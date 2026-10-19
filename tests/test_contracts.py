from __future__ import annotations

import pytest
from pydantic import ValidationError

from household_agent.contracts import DecisionResult, ProductInput, ResearchResult
from household_agent.errors import ContractValidationError
from household_agent.validation import validate_decision_result, validate_research_result


def research_payload() -> dict:
    return {
        "product_name": "ceramic pan",
        "research_status": "completed",
        "evidence": [
            {
                "claim_id": "mfr-1",
                "source_name": "Example Manufacturer",
                "source_type": "manufacturer",
                "source_url": "https://example.com/care",
                "claim_text": "Replace if the coating peels.",
                "applicable_product": "Example ceramic pan",
                "conditions": ["The coating is peeling"],
                "summary": None,
            }
        ],
        "retrieval_errors": [],
    }


def test_input_accepts_only_product_name_and_preserves_unknowns() -> None:
    value = ProductInput(product_name=" pan ")
    assert value.product_name == "pan"
    assert value.purchase_date is None
    assert value.product_url is None
    assert value.notes is None


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"product_name": "   "},
        {"product_name": "pan", "purchase_date": "yesterday"},
        {"product_name": "pan", "product_url": "not a URL"},
        {"product_name": "pan", "unknown": "value"},
    ],
)
def test_invalid_inputs_are_rejected(payload: dict) -> None:
    with pytest.raises(ValidationError):
        ProductInput.model_validate(payload)


def test_empty_evidence_is_valid() -> None:
    result = ResearchResult.model_validate(
        {
            "product_name": "silicone pouch",
            "research_status": "completed",
            "evidence": [],
            "retrieval_errors": [],
        }
    )
    assert result.evidence == []


def test_duplicate_claim_ids_fail_fast() -> None:
    payload = research_payload()
    payload["evidence"].append(dict(payload["evidence"][0]))
    with pytest.raises(ContractValidationError, match="unique"):
        validate_research_result(payload)


def test_malformed_json_fails_fast() -> None:
    with pytest.raises(ContractValidationError):
        validate_research_result("{not-json")


def test_decision_requires_known_claim_ids_and_matching_basis() -> None:
    research = ResearchResult.model_validate(research_payload())
    decision = validate_decision_result(
        {
            "outcome": "Replace",
            "explanation": "The known condition matches the manufacturer's trigger.",
            "uncertainty": None,
            "used_claim_ids": ["mfr-1"],
            "source_basis": "manufacturer",
            "next_action": "Replace the pan.",
        },
        research,
    )
    assert isinstance(decision, DecisionResult)


def test_unknown_claim_id_is_rejected() -> None:
    with pytest.raises(ContractValidationError, match="unknown claim"):
        validate_decision_result(
            {
                "outcome": "Replace",
                "explanation": "Unsupported.",
                "uncertainty": None,
                "used_claim_ids": ["missing"],
                "source_basis": "manufacturer",
                "next_action": None,
            },
            ResearchResult.model_validate(research_payload()),
        )


@pytest.mark.parametrize(
    "outcome",
    [
        "Condition dependent",
        "Insufficient evidence",
        "Insufficient product information",
        "Unresolved evidence conflict",
    ],
)
def test_limited_outcomes_require_specific_uncertainty(outcome: str) -> None:
    with pytest.raises(ValidationError, match="requires a nonempty uncertainty"):
        DecisionResult.model_validate(
            {
                "outcome": outcome,
                "explanation": "Limited result.",
                "uncertainty": None,
                "used_claim_ids": [],
                "source_basis": "none",
                "next_action": None,
            }
        )


def test_source_basis_is_derived_from_cited_claim_types() -> None:
    research = ResearchResult.model_validate(research_payload())
    with pytest.raises(ContractValidationError, match="source_basis"):
        validate_decision_result(
            {
                "outcome": "Replace",
                "explanation": "The trigger is met.",
                "uncertainty": None,
                "used_claim_ids": ["mfr-1"],
                "source_basis": "general",
                "next_action": None,
            },
            research,
        )
