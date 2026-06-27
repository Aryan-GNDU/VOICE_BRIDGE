"""HTTP routes for the assistant service."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_chat_service
from app.config.settings import Settings, get_settings
from app.schemas.request import ChatRequest, ResetMemoryRequest
from app.schemas.response import (
    ChatResponse,
    ConfigResponse,
    HealthResponse,
    ResetMemoryResponse,
    ToolInfo,
)
from app.services.chat import ChatService

router = APIRouter()
ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Return service health."""
    return HealthResponse(status="ok")


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    service: ChatServiceDep,
) -> ChatResponse:
    """Send a user message to the agent."""
    return await service.chat(request)


@router.post(
    "/reset-memory",
    response_model=ResetMemoryResponse,
    status_code=status.HTTP_200_OK,
)
async def reset_memory(
    request: ResetMemoryRequest,
    service: ChatServiceDep,
) -> ResetMemoryResponse:
    """Reset conversation memory for a thread."""
    service.reset_memory(request.conversation_id)
    return ResetMemoryResponse(conversation_id=request.conversation_id, reset=True)


@router.get("/tools", response_model=list[ToolInfo])
async def tools(service: ChatServiceDep) -> list[ToolInfo]:
    """Return the registered tools and their descriptions."""
    return service.list_tools()


@router.get("/config", response_model=ConfigResponse)
async def config(settings: SettingsDep) -> ConfigResponse:
    """Return non-secret runtime configuration."""
    return ConfigResponse(
        app_name=settings.app_name,
        app_version=settings.app_version,
        model_name=settings.model_name,
        temperature=settings.temperature,
        max_tokens=settings.max_tokens,
        langsmith_enabled=settings.langsmith_tracing,
    )
