"""API response models."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str


class VocalBridgeResponse(BaseModel):
    """Voice session details returned by VocalBridge."""

    session_id: str | None = None
    token: str | None = None
    livekit_url: str | None = None
    raw: dict = Field(default_factory=dict)


class ChatResponse(BaseModel):
    """Chat response returned by the assistant."""

    conversation_id: str
    answer: str
    tools_available: list[str] = Field(default_factory=list)
    voice: VocalBridgeResponse | None = None


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
