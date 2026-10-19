from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, field_validator, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ProductInput(StrictModel):
    product_name: str = Field(min_length=1)
    purchase_date: Optional[date] = None
    product_url: Optional[AnyHttpUrl] = None
    notes: Optional[str] = None

    @field_validator("product_name")
    @classmethod
    def product_name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("product_name must not be blank")
        return value


class SourceType(str, Enum):
    MANUFACTURER = "manufacturer"
    GENERAL = "general"
    OTHER = "other"


class ResearchStatus(str, Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


class EvidenceClaim(StrictModel):
    claim_id: str = Field(min_length=1)
    source_name: str = Field(min_length=1)
    source_type: SourceType
    source_url: AnyHttpUrl
    claim_text: str = Field(min_length=1)
    applicable_product: str = Field(min_length=1)
    conditions: list[str]
    summary: Optional[str] = None

    @field_validator("claim_id", "source_name", "claim_text", "applicable_product")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("required text must not be blank")
        return value

    @field_validator("conditions")
    @classmethod
    def conditions_must_not_contain_blanks(cls, values: list[str]) -> list[str]:
        if any(not value.strip() for value in values):
            raise ValueError("conditions must not contain blank strings")
        return values


class ResearchResult(StrictModel):
    product_name: str = Field(min_length=1)
    research_status: ResearchStatus
    evidence: list[EvidenceClaim]
    retrieval_errors: list[str]

    @model_validator(mode="after")
    def claim_ids_are_unique(self) -> "ResearchResult":
        ids = [claim.claim_id for claim in self.evidence]
        if len(ids) != len(set(ids)):
            raise ValueError("claim_id values must be unique")
        return self


class Outcome(str, Enum):
    REPLACE = "Replace"
    NOT_YET = "Not yet"
    CONDITION_DEPENDENT = "Condition dependent"
    INSUFFICIENT_EVIDENCE = "Insufficient evidence"
    INSUFFICIENT_PRODUCT_INFORMATION = "Insufficient product information"
    UNRESOLVED_CONFLICT = "Unresolved evidence conflict"


class SourceBasis(str, Enum):
    MANUFACTURER = "manufacturer"
    GENERAL = "general"
    MIXED = "mixed"
    NONE = "none"


OUTCOMES_REQUIRING_UNCERTAINTY = {
    Outcome.CONDITION_DEPENDENT,
    Outcome.INSUFFICIENT_EVIDENCE,
    Outcome.INSUFFICIENT_PRODUCT_INFORMATION,
    Outcome.UNRESOLVED_CONFLICT,
}


class DecisionResult(StrictModel):
    outcome: Outcome
    explanation: str = Field(min_length=1)
    uncertainty: Optional[str]
    used_claim_ids: list[str]
    source_basis: SourceBasis
    next_action: Optional[str] = None

    @field_validator("explanation")
    @classmethod
    def explanation_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("explanation must not be blank")
        return value

    @model_validator(mode="after")
    def mechanical_consistency(self) -> "DecisionResult":
        if len(self.used_claim_ids) != len(set(self.used_claim_ids)):
            raise ValueError("used_claim_ids must be unique")
        if any(not claim_id.strip() for claim_id in self.used_claim_ids):
            raise ValueError("used_claim_ids must not contain blank strings")
        if self.outcome in OUTCOMES_REQUIRING_UNCERTAINTY:
            if self.uncertainty is None or not self.uncertainty.strip():
                raise ValueError(f"{self.outcome.value} requires a nonempty uncertainty")
        if self.source_basis is not SourceBasis.NONE and not self.used_claim_ids:
            raise ValueError("a non-none source_basis requires cited claims")
        return self


class RecommendationResponse(StrictModel):
    outcome: Outcome
    explanation: str
    source_basis: SourceBasis
    evidence: list[EvidenceClaim]
    uncertainty: Optional[str]
    next_action: Optional[str]


class ErrorDetail(StrictModel):
    code: str
    message: str
    stage: str


class ErrorResponse(StrictModel):
    error: ErrorDetail

