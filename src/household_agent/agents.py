from __future__ import annotations

import json
import logging
from typing import Any

from .contracts import DecisionResult, ProductInput, ResearchResult
from .errors import ProviderError
from .provider import ModelProvider

logger = logging.getLogger(__name__)


RESEARCH_INSTRUCTIONS = """You are the Research Agent for Household Agent V1.
Collect only replacement-relevant evidence; do not recommend whether to replace the item and do not score credibility.
Search verified manufacturer guidance first. Stop early only when directly applicable manufacturer guidance clearly resolves the question using supplied facts. Otherwise continue to general guidance.
Preserve every claim's direction, exact scope, conditions, limitations, applicable product, publisher, and canonical source URL. Never invent facts, URLs, product identity, or guidance. An inaccessible source is a retrieval error, not proof no guidance exists.
Use unique stable claim IDs. Empty evidence is valid. Mark status partial when access failures or budgets materially limit research and failed only when research could not meaningfully run.
Return only JSON matching the supplied schema."""


DECISION_INSTRUCTIONS = """You are the Decision Agent for Household Agent V1.
Use only the supplied product facts and validated research claims. Assess provenance, claim authority, transparency, applicability, incentives, currency, traceability, fidelity, corroboration, and genuine independence without numeric scoring.
A directly applicable manufacturer claim may be sufficient. An actionable recommendation based only on general guidance requires two credible independent sources with compatible applicable claims. Reposts and weak retailer/blog repetitions do not count. Reconcile scope differences; if credible material conflict remains, abstain.
Never reverse a conditional claim: 'replace if peeling' does not establish 'Not yet' when peeling is absent. Never upgrade vague wear to significant wear. Preserve purchase date as purchase date, not first-use date. Do not request more research or ask the user questions.
Choose exactly one supported outcome. Limited outcomes require concrete uncertainty. Cite only claim IDs actually used and make source_basis match those claims. Return only JSON matching the supplied schema."""


class ResearchAgent:
    def __init__(
        self,
        provider: ModelProvider,
        *,
        model: str,
        max_search_queries: int,
        max_evidence_sources: int,
    ) -> None:
        self._provider = provider
        self._model = model
        self._max_search_queries = max_search_queries
        self._max_evidence_sources = max_evidence_sources

    async def run(self, product: ProductInput) -> str:
        prompt = {
            "product": product.model_dump(mode="json"),
            "research_limits": {
                "maximum_search_queries": self._max_search_queries,
                "maximum_evidence_sources": self._max_evidence_sources,
            },
        }
        output = await self._provider.generate_json(
            stage="research",
            model=self._model,
            instructions=RESEARCH_INSTRUCTIONS,
            input_text=json.dumps(prompt, separators=(",", ":")),
            json_schema=_strict_schema(ResearchResult.model_json_schema()),
            use_web_search=True,
        )
        logger.info("agent_output stage=research output=%s", output)
        self._enforce_evidence_budget(output)
        return output

    def _enforce_evidence_budget(self, output: str) -> None:
        try:
            parsed = json.loads(output)
            evidence = parsed.get("evidence")
        except (json.JSONDecodeError, AttributeError):
            return  # The deterministic research validator reports malformed output.
        if isinstance(evidence, list) and len(evidence) > self._max_evidence_sources:
            raise ProviderError(
                stage="research",
                detail="Research output exceeded the configured evidence-source budget",
            )


class DecisionAgent:
    def __init__(self, provider: ModelProvider, *, model: str) -> None:
        self._provider = provider
        self._model = model

    async def run(self, product: ProductInput, research: ResearchResult) -> str:
        prompt = {
            "product": product.model_dump(mode="json"),
            "research": research.model_dump(mode="json"),
        }
        output = await self._provider.generate_json(
            stage="decision",
            model=self._model,
            instructions=DECISION_INSTRUCTIONS,
            input_text=json.dumps(prompt, separators=(",", ":")),
            json_schema=_strict_schema(DecisionResult.model_json_schema()),
            use_web_search=False,
        )
        logger.info("agent_output stage=decision output=%s", output)
        return output


def _strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Make optional Pydantic fields explicitly required for strict structured output."""
    schema = json.loads(json.dumps(schema))

    def visit(node: Any) -> None:
        if isinstance(node, dict):
            # Responses API Structured Outputs supports a strict JSON Schema
            # subset and rejects Pydantic's `format: uri` (and some other
            # format annotations). Runtime Pydantic validation still enforces
            # URL/date formats after generation.
            node.pop("format", None)
            properties = node.get("properties")
            if isinstance(properties, dict):
                node["required"] = list(properties)
                node["additionalProperties"] = False
            for value in node.values():
                visit(value)
        elif isinstance(node, list):
            for value in node:
                visit(value)

    visit(schema)
    return schema

