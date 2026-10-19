from __future__ import annotations

import logging
from typing import Protocol

from .contracts import (
    DecisionResult,
    ProductInput,
    RecommendationResponse,
    ResearchResult,
    ResearchStatus,
)
from .errors import ResearchUnavailableError
from .validation import validate_decision_result, validate_research_result

logger = logging.getLogger(__name__)


class Researcher(Protocol):
    async def run(self, product: ProductInput) -> str: ...


class Decider(Protocol):
    async def run(self, product: ProductInput, research: ResearchResult) -> str: ...


class RecommendationService:
    def __init__(self, researcher: Researcher, decider: Decider) -> None:
        self._researcher = researcher
        self._decider = decider

    async def recommend(self, product: ProductInput) -> RecommendationResponse:
        raw_research = await self._researcher.run(product)
        research = validate_research_result(raw_research)
        logger.info(
            "research_validated status=%s evidence_count=%d retrieval_error_count=%d",
            research.research_status.value,
            len(research.evidence),
            len(research.retrieval_errors),
        )
        if research.research_status is ResearchStatus.FAILED and not research.evidence:
            detail = "Research could not retrieve enough information to evaluate the product."
            if research.retrieval_errors:
                detail += " Retrieval access failed for the attempted sources."
            logger.error(
                "research_unavailable retrieval_error_count=%d",
                len(research.retrieval_errors),
            )
            raise ResearchUnavailableError(detail)

        raw_decision = await self._decider.run(product, research)
        decision = validate_decision_result(raw_decision, research)
        logger.info(
            "decision_validated outcome=%s cited_claim_count=%d source_basis=%s",
            decision.outcome.value,
            len(decision.used_claim_ids),
            decision.source_basis.value,
        )
        return _render(decision, research)


def _render(decision: DecisionResult, research: ResearchResult) -> RecommendationResponse:
    by_id = {claim.claim_id: claim for claim in research.evidence}
    evidence = [by_id[claim_id] for claim_id in decision.used_claim_ids]
    return RecommendationResponse(
        outcome=decision.outcome,
        explanation=decision.explanation,
        source_basis=decision.source_basis,
        evidence=evidence,
        uncertainty=decision.uncertainty,
        next_action=decision.next_action,
    )

