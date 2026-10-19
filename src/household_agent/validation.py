from __future__ import annotations

import json
import logging
from typing import Any, Dict, TypeVar, Union

from pydantic import BaseModel, ValidationError

from .contracts import DecisionResult, ResearchResult, SourceBasis, SourceType
from .errors import ContractValidationError

ModelT = TypeVar("ModelT", bound=BaseModel)
logger = logging.getLogger(__name__)


def _parse_payload(
    payload: Union[str, bytes, Dict[str, Any]], model: type[ModelT], stage: str
) -> ModelT:
    try:
        if isinstance(payload, (str, bytes)):
            return model.model_validate_json(payload)
        return model.model_validate(payload)
    except (ValidationError, json.JSONDecodeError) as exc:
        logger.warning(
            "contract_validation_error stage=%s error_type=%s detail=%s",
            stage,
            type(exc).__name__,
            exc,
        )
        raise ContractValidationError(stage=stage, detail=str(exc)) from exc


def validate_research_result(payload: Union[str, bytes, Dict[str, Any]]) -> ResearchResult:
    return _parse_payload(payload, ResearchResult, "research_validation")


def validate_decision_result(
    payload: Union[str, bytes, Dict[str, Any]], research: ResearchResult
) -> DecisionResult:
    decision = _parse_payload(payload, DecisionResult, "decision_validation")
    available = {claim.claim_id: claim for claim in research.evidence}
    unknown = sorted(set(decision.used_claim_ids) - available.keys())
    if unknown:
        logger.warning(
            "contract_validation_error stage=decision_validation unknown_claim_ids=%s",
            unknown,
        )
        raise ContractValidationError(
            stage="decision_validation",
            detail=f"Decision references unknown claim IDs: {', '.join(unknown)}",
        )

    cited_types = {available[claim_id].source_type for claim_id in decision.used_claim_ids}
    expected_basis = _source_basis(cited_types)
    if decision.source_basis is not expected_basis:
        logger.warning(
            "contract_validation_error stage=decision_validation declared_basis=%s expected_basis=%s",
            decision.source_basis.value,
            expected_basis.value,
        )
        raise ContractValidationError(
            stage="decision_validation",
            detail=(
                f"source_basis is {decision.source_basis.value!r}; cited claims require "
                f"{expected_basis.value!r}"
            ),
        )
    return decision


def _source_basis(source_types: set[SourceType]) -> SourceBasis:
    relevant = source_types & {SourceType.MANUFACTURER, SourceType.GENERAL}
    if not relevant:
        return SourceBasis.NONE
    if relevant == {SourceType.MANUFACTURER}:
        return SourceBasis.MANUFACTURER
    if relevant == {SourceType.GENERAL}:
        return SourceBasis.GENERAL
    return SourceBasis.MIXED

