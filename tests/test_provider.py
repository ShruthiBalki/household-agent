from __future__ import annotations

from types import SimpleNamespace
import logging

import pytest

from household_agent.errors import ProviderError
from household_agent.provider import OpenAIModelProvider


class FakeResponses:
    def __init__(self, response=None, error=None) -> None:
        self.response = response
        self.error = error
        self.requests = []

    async def create(self, **kwargs):
        self.requests.append(kwargs)
        if self.error:
            raise self.error
        return self.response


@pytest.mark.asyncio
async def test_openai_provider_uses_strict_schema_search_and_no_storage(caplog) -> None:
    provider = OpenAIModelProvider(api_key="test-key", timeout_seconds=1)
    responses = FakeResponses(
        SimpleNamespace(
            status="completed",
            output_text="{}",
            usage=SimpleNamespace(input_tokens=12, output_tokens=7, total_tokens=19),
        )
    )
    provider._client = SimpleNamespace(responses=responses)
    with caplog.at_level(logging.INFO, logger="household_agent.provider"):
        result = await provider.generate_json(
            stage="research",
            model="test-model",
            instructions="instructions",
            input_text="input",
            json_schema={"type": "object", "properties": {}, "additionalProperties": False},
            use_web_search=True,
        )
    assert result == "{}"
    request = responses.requests[0]
    assert request["store"] is False
    assert request["tools"] == [{"type": "web_search", "search_context_size": "medium"}]
    assert request["tool_choice"] == "required"
    assert request["text"]["format"]["strict"] is True
    assert "input_tokens=12 output_tokens=7 total_tokens=19" in caplog.text


@pytest.mark.asyncio
async def test_openai_provider_maps_failures_without_retrying(caplog) -> None:
    provider = OpenAIModelProvider(api_key="test-key", timeout_seconds=1)
    responses = FakeResponses(error=TimeoutError("timed out"))
    provider._client = SimpleNamespace(responses=responses)
    with caplog.at_level(logging.ERROR, logger="household_agent.provider"):
        with pytest.raises(ProviderError, match="Provider request failed"):
            await provider.generate_json(
                stage="decision",
                model="test-model",
                instructions="instructions",
                input_text="input",
                json_schema={"type": "object"},
                use_web_search=False,
            )
    assert len(responses.requests) == 1
    assert "provider_error stage=decision error_type=TimeoutError" in caplog.text
