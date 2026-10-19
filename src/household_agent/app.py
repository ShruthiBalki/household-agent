from __future__ import annotations

from functools import lru_cache
import logging

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse

from .agents import DecisionAgent, ResearchAgent
from .contracts import ErrorDetail, ErrorResponse, ProductInput, RecommendationResponse
from .errors import ContractValidationError, ProviderError, ResearchUnavailableError
from .logging import configure_logging
from .provider import OpenAIModelProvider
from .service import RecommendationService
from .settings import Settings, get_settings

configure_logging(get_settings().log_level)
logger = logging.getLogger(__name__)


def build_service(settings: Settings) -> RecommendationService:
    if settings.provider != "openai":
        raise ProviderError(stage="configuration", detail="Unsupported provider configuration")
    if not settings.openai_api_key:
        raise ProviderError(
            stage="configuration",
            detail="An OpenAI API key is required before requesting recommendations",
        )
    provider = OpenAIModelProvider(
        api_key=settings.openai_api_key,
        timeout_seconds=settings.provider_timeout_seconds,
    )
    return RecommendationService(
        ResearchAgent(
            provider,
            model=settings.research_model,
            max_search_queries=settings.max_search_queries,
            max_evidence_sources=settings.max_evidence_sources,
        ),
        DecisionAgent(provider, model=settings.decision_model),
    )


@lru_cache
def get_service() -> RecommendationService:
    return build_service(get_settings())


app = FastAPI(
    title="Household Agent",
    version="0.1.0",
    description="Evidence-backed household product replacement recommendations.",
)


@app.exception_handler(RequestValidationError)
async def input_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    del request
    logger.warning("request_failed code=invalid_input error_count=%d", len(exc.errors()))
    body = ErrorResponse(
        error=ErrorDetail(
            code="invalid_input",
            message="The request input is invalid.",
            stage="input_validation",
        )
    )
    return JSONResponse(status_code=422, content=body.model_dump(mode="json"))


@app.exception_handler(ContractValidationError)
async def contract_error_handler(
    request: Request, exc: ContractValidationError
) -> JSONResponse:
    del request
    logger.error("request_failed code=invalid_agent_output stage=%s", exc.stage)
    body = ErrorResponse(
        error=ErrorDetail(
            code="invalid_agent_output",
            message="An agent returned output that violated its contract.",
            stage=exc.stage,
        )
    )
    return JSONResponse(status_code=502, content=body.model_dump(mode="json"))


@app.exception_handler(ResearchUnavailableError)
async def research_unavailable_handler(
    request: Request, exc: ResearchUnavailableError
) -> JSONResponse:
    del request
    logger.error("request_failed code=research_unavailable stage=%s", exc.stage)
    body = ErrorResponse(
        error=ErrorDetail(code="research_unavailable", message=exc.detail, stage=exc.stage)
    )
    return JSONResponse(status_code=503, content=body.model_dump(mode="json"))


@app.exception_handler(ProviderError)
async def provider_error_handler(request: Request, exc: ProviderError) -> JSONResponse:
    del request
    logger.error("request_failed code=provider_unavailable stage=%s", exc.stage)
    body = ErrorResponse(
        error=ErrorDetail(
            code="provider_unavailable",
            message="The external provider could not complete the request.",
            stage=exc.stage,
        )
    )
    return JSONResponse(status_code=503, content=body.model_dump(mode="json"))


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    del request
    logger.exception("request_failed code=internal_error error_type=%s", type(exc).__name__)
    body = ErrorResponse(
        error=ErrorDetail(
            code="internal_error",
            message="An unexpected internal error occurred.",
            stage="internal",
        )
    )
    return JSONResponse(status_code=500, content=body.model_dump(mode="json"))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/v1/recommendations",
    response_model=RecommendationResponse,
    responses={502: {"model": ErrorResponse}, 503: {"model": ErrorResponse}},
)
async def recommend(
    product: ProductInput, service: RecommendationService = Depends(get_service)
) -> RecommendationResponse:
    return await service.recommend(product)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index() -> str:
    return _INDEX_HTML


_INDEX_HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Household Agent</title><style>
body{font:16px system-ui;max-width:760px;margin:3rem auto;padding:0 1rem;color:#17202a}form,article{display:grid;gap:.8rem}input,textarea,button{font:inherit;padding:.7rem}button{cursor:pointer;background:#173f5f;color:white;border:0;border-radius:4px}.muted{color:#59636e}a{color:#075b9a}li{margin:.6rem 0}
</style></head><body><h1>Household Agent</h1><p class="muted">Evidence-backed replacement guidance. Only product name is required.</p>
<form id="form"><input name="product_name" required placeholder="Product name"><input name="purchase_date" type="date"><input name="product_url" type="url" placeholder="Product URL"><textarea name="notes" placeholder="Condition or other notes"></textarea><button>Get recommendation</button></form><article id="result" aria-live="polite"></article>
<script>const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));document.querySelector('#form').addEventListener('submit',async e=>{e.preventDefault();const out=document.querySelector('#result');out.textContent='Researching…';const data=Object.fromEntries(new FormData(e.target));for(const k of Object.keys(data))if(!data[k])data[k]=null;try{const r=await fetch('/api/v1/recommendations',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(data)});const x=await r.json();if(!r.ok)throw new Error(x.error?.message||'Request failed');out.innerHTML=`<h2>${esc(x.outcome)}</h2><p>${esc(x.explanation)}</p>${x.uncertainty?`<p><strong>Uncertainty:</strong> ${esc(x.uncertainty)}</p>`:''}${x.next_action?`<p><strong>Next action:</strong> ${esc(x.next_action)}</p>`:''}<h3>Evidence (${esc(x.source_basis)})</h3><ul>${x.evidence.map(v=>`<li><a rel="noopener" target="_blank" href="${esc(v.source_url)}">${esc(v.source_name)}</a>: ${esc(v.claim_text)}</li>`).join('')}</ul>`}catch(err){out.textContent=err.message}});</script></body></html>"""

