from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="HOUSEHOLD_AGENT_", env_file=".env", extra="ignore"
    )

    provider: str = "openai"
    openai_api_key: Optional[str] = Field(
        default=None,
        repr=False,
        validation_alias=AliasChoices("HOUSEHOLD_AGENT_OPENAI_API_KEY", "OPENAI_API_KEY"),
    )
    research_model: str = "gpt-5.5"
    decision_model: str = "gpt-5.5"
    provider_timeout_seconds: float = Field(default=45.0, gt=0, le=180)
    max_search_queries: int = Field(default=4, ge=1, le=10)
    max_evidence_sources: int = Field(default=8, ge=1, le=20)
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()

