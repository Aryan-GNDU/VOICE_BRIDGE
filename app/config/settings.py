"""Runtime settings loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Validated application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Agentic AI Assistant"
    app_version: str = "1.0.0"
    environment: Literal["local", "dev", "staging", "prod"] = "local"

    groq_api_key: SecretStr | None = Field(default=None, alias="GROQ_API_KEY")
    google_api_key: SecretStr | None = Field(default=None, alias="GOOGLE_API_KEY")
    google_cse_id: str | None = Field(default=None, alias="GOOGLE_CSE_ID")
    langchain_api_key: SecretStr | None = Field(default=None, alias="LANGCHAIN_API_KEY")
    langsmith_api_key: SecretStr | None = Field(default=None, alias="LANGSMITH_API_KEY")

    model_name: str = Field(default="openai/gpt-oss-120b", alias="MODEL_NAME")
    temperature: float = Field(default=0.2, ge=0.0, le=2.0, alias="TEMPERATURE")
    max_tokens: int = Field(default=2048, ge=128, le=8192, alias="MAX_TOKENS")
    request_timeout_seconds: float = Field(default=60.0, ge=1.0, alias="REQUEST_TIMEOUT_SECONDS")
    max_retries: int = Field(default=2, ge=0, le=10, alias="MAX_RETRIES")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    langsmith_tracing: bool = Field(default=False, alias="LANGSMITH_TRACING")
    langsmith_project: str = Field(default="agentic-ai-assistant", alias="LANGSMITH_PROJECT")

    wikipedia_top_k: int = Field(default=3, ge=1, le=10, alias="WIKIPEDIA_TOP_K")
    arxiv_top_k: int = Field(default=5, ge=1, le=10, alias="ARXIV_TOP_K")
    google_top_k: int = Field(default=5, ge=1, le=10, alias="GOOGLE_TOP_K")

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        """Normalize and validate the logging level."""
        normalized = value.upper()
        valid = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in valid:
            msg = f"LOG_LEVEL must be one of {sorted(valid)}"
            raise ValueError(msg)
        return normalized


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings."""
    return Settings()
