from __future__ import annotations


class HouseholdAgentError(Exception):
    """Base class for controlled application failures."""


class ContractValidationError(HouseholdAgentError):
    def __init__(self, *, stage: str, detail: str) -> None:
        super().__init__(detail)
        self.stage = stage
        self.detail = detail


class ProviderError(HouseholdAgentError):
    def __init__(self, *, stage: str, detail: str) -> None:
        super().__init__(detail)
        self.stage = stage
        self.detail = detail


class ResearchUnavailableError(HouseholdAgentError):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)
        self.stage = "research"
        self.detail = detail

