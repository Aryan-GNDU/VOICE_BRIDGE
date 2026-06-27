"""API response models."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class ChatResponse(BaseModel):
    """Chat response returned by the assistant."""

    conversation_id: str
    answer: str
    tools_available: list[str] = Field(default_factory=list)


class ResetMemoryResponse(BaseModel):
    """Memory reset response."""

    conversation_id: str
    reset: bool


class ToolInfo(BaseModel):
    """Tool metadata response."""

    name: str
    description: str


class ConfigResponse(BaseModel):
    """Non-secret runtime configuration."""

    app_name: str
    app_version: str
    model_name: str
    temperature: float
    max_tokens: int
    langsmith_enabled: bool
