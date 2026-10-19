from __future__ import annotations

import logging
from typing import Any, Protocol

from .errors import ProviderError

logger = logging.getLogger(__name__)


class ModelProvider(Protocol):
    async def generate_json(
        self,
        *,
        stage: str,
        model: str,
        instructions: str,
        input_text: str,
        json_schema: dict[str, Any],
        use_web_search: bool,
    ) -> str: ...


class OpenAIModelProvider:
    def __init__(self, *, api_key: str, timeout_seconds: float) -> None:
        if not api_key:
            raise ValueError("OPENAI API key is required")
        try:
            from openai import AsyncOpenAI
        except ImportError as exc:  # pragma: no cover - packaging protects this path
            raise RuntimeError("The openai package is not installed") from exc
        self._client = AsyncOpenAI(api_key=api_key, timeout=timeout_seconds, max_retries=0)

    async def generate_json(
        self,
        *,
        stage: str,
        model: str,
        instructions: str,
        input_text: str,
        json_schema: dict[str, Any],
        use_web_search: bool,
    ) -> str:
        request: dict[str, Any] = {
            "model": model,
            "instructions": instructions,
            "input": input_text,
            "store": False,
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": f"household_agent_{stage}",
                    "strict": True,
                    "schema": json_schema,
                }
            },
        }
        if use_web_search:
            request["tools"] = [{"type": "web_search", "search_context_size": "medium"}]
            request["tool_choice"] = "required"
        try:
            response = await self._client.responses.create(**request)
        except Exception as exc:
            logger.exception("provider_error stage=%s error_type=%s", stage, type(exc).__name__)
            raise ProviderError(stage=stage, detail=f"Provider request failed: {exc}") from exc
        if response.status != "completed" or not response.output_text:
            detail = getattr(response, "error", None) or getattr(
                response, "incomplete_details", None
            )
            logger.error(
                "provider_incomplete stage=%s status=%s detail=%s",
                stage,
                response.status,
                detail,
            )
            raise ProviderError(stage=stage, detail=f"Provider did not complete: {detail}")
        usage = getattr(response, "usage", None)
        logger.info(
            "provider_usage stage=%s input_tokens=%s output_tokens=%s total_tokens=%s",
            stage,
            getattr(usage, "input_tokens", None),
            getattr(usage, "output_tokens", None),
            getattr(usage, "total_tokens", None),
        )
        return response.output_text

