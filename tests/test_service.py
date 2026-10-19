from __future__ import annotations

import json

import pytest

from household_agent.contracts import ProductInput
from household_agent.errors import ContractValidationError, ResearchUnavailableError
from household_agent.service import RecommendationService


class StubStage:
    def __init__(self, output: str, events: list[str], name: str) -> None:
        self.output = output
        self.events = events
        self.name = name

    async def run(self, *args) -> str:
        self.events.append(self.name)
        return self.output


def research(*, status: str = "completed", evidence: list | None = None) -> str:
    return json.dumps(
        {
            "product_name": "pan",
            "research_status": status,
            "evidence": evidence or [],
            "retrieval_errors": [],
        }
    )


def insufficient_decision() -> str:
    return json.dumps(
        {
            "outcome": "Insufficient evidence",
            "explanation": "No reliable replacement guidance was established.",
            "uncertainty": "No defensible evidence was found.",
            "used_claim_ids": [],
            "source_basis": "none",
            "next_action": None,
        }
    )


@pytest.mark.asyncio
async def test_empty_evidence_reaches_decision_and_returns_outcome() -> None:
    events: list[str] = []
    service = RecommendationService(
        StubStage(research(), events, "research"),
        StubStage(insufficient_decision(), events, "decision"),
    )
    result = await service.recommend(ProductInput(product_name="pan"))
    assert result.outcome == "Insufficient evidence"
    assert events == ["research", "decision"]


@pytest.mark.asyncio
async def test_malformed_research_stops_before_decision() -> None:
    events: list[str] = []
    service = RecommendationService(
        StubStage("not-json", events, "research"),
        StubStage(insufficient_decision(), events, "decision"),
    )
    with pytest.raises(ContractValidationError):
        await service.recommend(ProductInput(product_name="pan"))
    assert events == ["research"]


@pytest.mark.asyncio
async def test_malformed_decision_fails_without_retry() -> None:
    events: list[str] = []
    service = RecommendationService(
        StubStage(research(), events, "research"), StubStage("{}", events, "decision")
    )
    with pytest.raises(ContractValidationError):
        await service.recommend(ProductInput(product_name="pan"))
    assert events == ["research", "decision"]


@pytest.mark.asyncio
async def test_failed_research_without_evidence_is_unavailable() -> None:
    events: list[str] = []
    service = RecommendationService(
        StubStage(research(status="failed"), events, "research"),
        StubStage(insufficient_decision(), events, "decision"),
    )
    with pytest.raises(ResearchUnavailableError):
        await service.recommend(ProductInput(product_name="pan"))
    assert events == ["research"]


@pytest.mark.asyncio
async def test_renderer_shows_exactly_cited_evidence_in_citation_order() -> None:
    claims = [
        {
            "claim_id": claim_id,
            "source_name": claim_id,
            "source_type": "general",
            "source_url": f"https://example.com/{claim_id}",
            "claim_text": "Replace when significantly worn.",
            "applicable_product": "ceramic pan",
            "conditions": ["significantly worn"],
            "summary": None,
        }
        for claim_id in ("a", "b", "unused")
    ]
    decision = json.dumps(
        {
            "outcome": "Replace",
            "explanation": "Two sources match known significant wear.",
            "uncertainty": None,
            "used_claim_ids": ["b", "a"],
            "source_basis": "general",
            "next_action": "Replace the pan.",
        }
    )
    service = RecommendationService(
        StubStage(research(evidence=claims), [], "research"),
        StubStage(decision, [], "decision"),
    )
    result = await service.recommend(ProductInput(product_name="ceramic pan"))
    assert [claim.claim_id for claim in result.evidence] == ["b", "a"]

