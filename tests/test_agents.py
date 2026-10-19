from __future__ import annotations

import json
import logging

import pytest

from household_agent.agents import DecisionAgent, ResearchAgent
from household_agent.contracts import ProductInput, ResearchResult
from household_agent.errors import ProviderError


class RecordingProvider:
    def __init__(self, outputs: dict[str, str]) -> None:
        self.outputs = outputs
        self.calls: list[dict] = []

    async def generate_json(self, **kwargs) -> str:
        self.calls.append(kwargs)
        return self.outputs[kwargs["stage"]]


def valid_research() -> dict:
    return {
        "product_name": "pan",
        "research_status": "completed",
        "evidence": [],
        "retrieval_errors": [],
    }


@pytest.mark.asyncio
async def test_research_uses_web_search_and_passes_budgets(caplog) -> None:
    provider = RecordingProvider({"research": json.dumps(valid_research())})
    agent = ResearchAgent(
        provider, model="research-model", max_search_queries=3, max_evidence_sources=5
    )
    with caplog.at_level(logging.INFO, logger="household_agent.agents"):
        output = await agent.run(ProductInput(product_name="pan"))
    assert json.loads(output) == valid_research()
    call = provider.calls[0]
    assert call["stage"] == "research"
    assert call["use_web_search"] is True
    payload = json.loads(call["input_text"])
    assert payload["research_limits"] == {
        "maximum_search_queries": 3,
        "maximum_evidence_sources": 5,
    }
    assert "recommend" in call["instructions"]
    assert "agent_output stage=research" in caplog.text
    assert '"product_name": "pan"' in caplog.text


@pytest.mark.asyncio
async def test_research_rejects_output_over_source_budget() -> None:
    payload = valid_research()
    payload["evidence"] = [{"claim_id": str(index)} for index in range(2)]
    provider = RecordingProvider({"research": json.dumps(payload)})
    agent = ResearchAgent(
        provider, model="research-model", max_search_queries=1, max_evidence_sources=1
    )
    with pytest.raises(ProviderError, match="budget"):
        await agent.run(ProductInput(product_name="pan"))


@pytest.mark.asyncio
async def test_decision_has_no_search_or_research_callback() -> None:
    decision = {
        "outcome": "Insufficient evidence",
        "explanation": "No replacement guidance was found.",
        "uncertainty": "No defensible replacement evidence was available.",
        "used_claim_ids": [],
        "source_basis": "none",
        "next_action": None,
    }
    provider = RecordingProvider({"decision": json.dumps(decision)})
    agent = DecisionAgent(provider, model="decision-model")
    await agent.run(
        ProductInput(product_name="pan"), ResearchResult.model_validate(valid_research())
    )
    assert len(provider.calls) == 1
    assert provider.calls[0]["stage"] == "decision"
    assert provider.calls[0]["use_web_search"] is False
    assert "Never reverse" in provider.calls[0]["instructions"]


def test_strict_schema_requires_nullable_optional_fields() -> None:
    provider = RecordingProvider({})
    agent = DecisionAgent(provider, model="decision-model")
    del agent
    from household_agent.agents import _strict_schema

    schema = _strict_schema(ProductInput.model_json_schema())
    assert set(schema["required"]) == {
        "product_name",
        "purchase_date",
        "product_url",
        "notes",
    }
    assert "format" not in schema["properties"]["purchase_date"]["anyOf"][0]
    assert "format" not in schema["properties"]["product_url"]["anyOf"][0]


def test_research_provider_schema_removes_unsupported_uri_format() -> None:
    from household_agent.agents import _strict_schema

    schema = _strict_schema(ResearchResult.model_json_schema())
    claim_schema = schema["$defs"]["EvidenceClaim"]
    assert "format" not in claim_schema["properties"]["source_url"]
