"""Groq LLM configuration."""

from langchain_groq import ChatGroq

from app.config.settings import get_settings
from app.utils.exceptions import ConfigurationError


def build_groq_chat_model() -> ChatGroq:
    """Create the Groq chat model used by the agent."""
    settings = get_settings()
    if settings.groq_api_key is None:
        raise ConfigurationError("GROQ_API_KEY is required to initialize the Groq model.")

    return ChatGroq(
        api_key=settings.groq_api_key.get_secret_value(),
        model=settings.model_name,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        timeout=settings.request_timeout_seconds,
        max_retries=settings.max_retries,
    )
