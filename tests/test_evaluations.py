from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from household_agent.agents import RESEARCH_INSTRUCTIONS, ResearchAgent
from household_agent.contracts import DecisionResult, ProductInput, ResearchResult
from household_agent.errors import ContractValidationError, ProviderError, ResearchUnavailableError
from household_agent.service import RecommendationService
from household_agent.validation import validate_decision_result, validate_research_result


def claim(
    claim_id: str,
    *,
    source_type: str = "general",
    text: str = "Replace when significantly worn.",
    conditions: list[str] | None = None,
    url_host: str | None = None,
) -> dict:
    host = url_host or f"{claim_id}.example.org"
    return {
        "claim_id": claim_id,
        "source_name": f"Source {claim_id}",
        "source_type": source_type,
        "source_url": f"https://{host}/guidance",
        "claim_text": text,
        "applicable_product": "ceramic nonstick pan",
        "conditions": conditions or [],
        "summary": None,
    }


def research_payload(
    evidence: list[dict] | None = None,
    *,
    status: str = "completed",
    errors: list[str] | None = None,
    product_name: str = "ceramic nonstick pan",
) -> dict:
    return {
        "product_name": product_name,
        "research_status": status,
        "evidence": evidence or [],
        "retrieval_errors": errors or [],
    }


def decision_payload(
    outcome: str,
    ids: list[str],
    basis: str,
    *,
    uncertainty: str | None = None,
    explanation: str = "The result follows the supplied evidence and known product facts.",
) -> dict:
    return {
        "outcome": outcome,
        "explanation": explanation,
        "uncertainty": uncertainty,
        "used_claim_ids": ids,
        "source_basis": basis,
        "next_action": None,
    }


class OutputStage:
    def __init__(self, payload: dict | str, calls: list[str] | None = None, name: str = ""):
        self.payload = payload
        self.calls = calls
        self.name = name

    async def run(self, *args) -> str:
        if self.calls is not None:
            self.calls.append(self.name)
        return self.payload if isinstance(self.payload, str) else json.dumps(self.payload)


async def run_fixture(research: dict, decision: dict, product_name: str = "ceramic nonstick pan"):
    service = RecommendationService(OutputStage(research), OutputStage(decision))
    return await service.recommend(ProductInput(product_name=product_name))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("research", "decision", "expected", "expected_ids"),
    [
        pytest.param(
            research_payload([claim("m1", source_type="manufacturer", text="Replace when coating peels.", conditions=["coating peels"])]),
            decision_payload("Replace", ["m1"], "manufacturer"),
            "Replace", ["m1"], id="EV-01-manufacturer-happy-path",
        ),
        pytest.param(
            research_payload([claim("g1", text="Replace after 3–5 years."), claim("g2", text="Replace only based on condition.")]),
            decision_payload("Unresolved evidence conflict", ["g1", "g2"], "general", uncertainty="Credible sources materially disagree on age versus condition."),
            "Unresolved evidence conflict", ["g1", "g2"], id="EV-02-unresolved-conflict",
        ),
        pytest.param(
            research_payload([claim("g1", conditions=["significant scratching or peeling"]), claim("g2", conditions=["significant scratching or peeling"])]),
            decision_payload("Condition dependent", ["g1", "g2"], "general", uncertainty="The pan's scratching or peeling condition is unknown."),
            "Condition dependent", ["g1", "g2"], id="EV-03-condition-dependent",
        ),
        pytest.param(
            research_payload([]),
            decision_payload("Insufficient evidence", [], "none", uncertainty="No credible replacement guidance was established."),
            "Insufficient evidence", [], id="EV-04-insufficient-evidence",
        ),
        pytest.param(
            research_payload([], product_name="pan"),
            decision_payload("Insufficient product information", [], "none", uncertainty="Material and coating are unknown, and guidance differs by pan type."),
            "Insufficient product information", [], id="EV-05-generic-product",
        ),
        pytest.param(
            research_payload([claim("g1"), claim("g2")]),
            decision_payload("Replace", ["g1", "g2"], "general", explanation="Known significant wear meets both independent general criteria."),
            "Replace", ["g1", "g2"], id="EV-06-general-guidance",
        ),
        pytest.param(
            research_payload([claim("m1", source_type="manufacturer", text="Replace if coating peels.", conditions=["coating peels"])]),
            decision_payload("Insufficient evidence", ["m1"], "manufacturer", uncertainty="The one-way peeling trigger does not determine what to do when peeling is absent."),
            "Insufficient evidence", ["m1"], id="EV-07-no-reverse-inference",
        ),
        pytest.param(
            research_payload([claim("r1", source_type="other", text="Replace every three years."), claim("r2", source_type="other", text="Replace every three years.")]),
            decision_payload("Insufficient evidence", ["r1", "r2"], "none", uncertainty="Retailer repetition does not establish credible independent corroboration."),
            "Insufficient evidence", ["r1", "r2"], id="EV-08-weak-sources",
        ),
        pytest.param(
            research_payload([claim("g1"), claim("g2")]),
            decision_payload("Replace", ["g1", "g2"], "general"),
            "Replace", ["g1", "g2"], id="EV-10-manufacturer-not-decisive",
        ),
        pytest.param(
            research_payload([claim("g1"), claim("g2")], status="partial", errors=["Manufacturer page could not be retrieved"]),
            decision_payload("Replace", ["g1", "g2"], "general"),
            "Replace", ["g1", "g2"], id="EV-15-access-failure-not-absence",
        ),
        pytest.param(
            research_payload([claim("m1", source_type="manufacturer", text="Use the expiration date printed on the label.", conditions=["labeled expiration date"])]),
            decision_payload("Condition dependent", ["m1"], "manufacturer", uncertainty="The labeled expiration date is not supplied."),
            "Condition dependent", ["m1"], id="EV-16-missing-expiration",
        ),
        pytest.param(
            research_payload([claim("g1", url_host="same-origin.example"), claim("g2", url_host="same-origin.example")]),
            decision_payload("Insufficient evidence", ["g1", "g2"], "general", uncertainty="The two pages reproduce one underlying source and are not independent."),
            "Insufficient evidence", ["g1", "g2"], id="EV-17-independence",
        ),
        pytest.param(
            research_payload([claim("g1", conditions=["significant wear"]), claim("g2", conditions=["significant wear"])]),
            decision_payload("Condition dependent", ["g1", "g2"], "general", uncertainty="The notes say only 'some wear'; significant wear is not established."),
            "Condition dependent", ["g1", "g2"], id="EV-18-unknown-wear",
        ),
    ],
)
async def test_behavioral_fixture_outcomes(research, decision, expected, expected_ids) -> None:
    result = await run_fixture(research, decision, product_name=research["product_name"])
    assert result.outcome.value == expected
    assert [item.claim_id for item in result.evidence] == expected_ids
    assert "?" not in result.explanation  # no clarification questions in V1


def test_ev09_optional_inputs_and_errors() -> None:
    product = ProductInput.model_validate(
        {"product_name": "pan", "purchase_date": "2021-06-01", "product_url": "https://example.com/pan", "notes": "some wear"}
    )
    assert product.purchase_date.isoformat() == "2021-06-01"
    with pytest.raises(ValidationError):
        ProductInput.model_validate({"product_name": "", "purchase_date": "bad"})


def test_ev11_research_contract_preserves_conditions_and_errors() -> None:
    value = validate_research_result(
        research_payload([claim("m1", source_type="manufacturer", conditions=["only when peeling"])], status="partial", errors=["https://example.org was inaccessible"])
    )
    assert value.evidence[0].conditions == ["only when peeling"]
    assert value.retrieval_errors


def test_ev12_research_schema_fails_fast() -> None:
    with pytest.raises(ContractValidationError):
        validate_research_result({"research_status": "completed", "evidence": []})


def test_ev13_final_validator_fails_fast() -> None:
    research = ResearchResult.model_validate(research_payload())
    with pytest.raises(ContractValidationError):
        validate_decision_result(decision_payload("Replace", ["missing"], "manufacturer"), research)


@pytest.mark.asyncio
async def test_ev14_sequential_no_feedback_or_retry() -> None:
    calls: list[str] = []
    service = RecommendationService(
        OutputStage(research_payload(), calls, "research"),
        OutputStage(decision_payload("Insufficient evidence", [], "none", uncertainty="Only one or no credible general source was available."), calls, "decision"),
    )
    await service.recommend(ProductInput(product_name="pan"))
    assert calls == ["research", "decision"]


def test_ev19_research_is_collection_only() -> None:
    assert "do not recommend" in RESEARCH_INSTRUCTIONS
    assert "do not score credibility" in RESEARCH_INSTRUCTIONS


def test_ev20_conservative_manufacturer_early_stop_instruction() -> None:
    assert "Stop early only when directly applicable manufacturer guidance clearly resolves" in RESEARCH_INSTRUCTIONS
    assert "Otherwise continue to general guidance" in RESEARCH_INSTRUCTIONS


class TooManySourcesProvider:
    async def generate_json(self, **kwargs) -> str:
        return json.dumps(research_payload([claim("a"), claim("b")]))


@pytest.mark.asyncio
async def test_ev21_configurable_budget_is_enforced() -> None:
    agent = ResearchAgent(TooManySourcesProvider(), model="model", max_search_queries=1, max_evidence_sources=1)
    with pytest.raises(ProviderError, match="budget"):
        await agent.run(ProductInput(product_name="pan"))


@pytest.mark.asyncio
async def test_ev22_claim_id_join_and_missing_id() -> None:
    available = research_payload(
        [claim("used", source_type="manufacturer"), claim("unused", source_type="manufacturer")]
    )
    result = await run_fixture(
        available, decision_payload("Replace", ["used"], "manufacturer")
    )
    assert [item.claim_id for item in result.evidence] == ["used"]
    with pytest.raises(ContractValidationError):
        await run_fixture(
            available, decision_payload("Replace", ["missing"], "manufacturer")
        )


def test_ev23_plain_uncertainty_required() -> None:
    with pytest.raises(ValidationError):
        DecisionResult.model_validate(decision_payload("Condition dependent", [], "none"))


def test_ev24_components_are_independently_constructible() -> None:
    assert ProductInput(product_name="pan").product_name == "pan"
    assert ResearchResult.model_validate(research_payload()).evidence == []
    assert DecisionResult.model_validate(decision_payload("Insufficient evidence", [], "none", uncertainty="No evidence."))


@pytest.mark.asyncio
async def test_ev25_empty_evidence_is_outcome_but_malformed_is_error() -> None:
    result = await run_fixture(
        research_payload(),
        decision_payload("Insufficient evidence", [], "none", uncertainty="No defensible evidence was found."),
    )
    assert result.outcome.value == "Insufficient evidence"
    service = RecommendationService(OutputStage("not-json"), OutputStage("{}"))
    with pytest.raises(ContractValidationError):
        await service.recommend(ProductInput(product_name="pan"))
