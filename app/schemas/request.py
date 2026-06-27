"""API request models."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""

    message: str = Field(..., min_length=1, max_length=8000)
    conversation_id: str = Field(default="default", min_length=1, max_length=200)


class ResetMemoryRequest(BaseModel):
    """Request body for resetting memory."""

    conversation_id: str = Field(default="default", min_length=1, max_length=200)
