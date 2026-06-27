"""FastAPI dependency providers."""

from functools import lru_cache

from app.services.chat import ChatService


@lru_cache(maxsize=1)
def get_chat_service() -> ChatService:
    """Return a process-wide chat service instance."""
    return ChatService()
