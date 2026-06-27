"""Chat orchestration service."""

from time import perf_counter

from langchain_core.messages import AIMessage

from app.agent.builder import AgentBuilder
from app.config.logger import get_logger
from app.schemas.request import ChatRequest
from app.schemas.response import ChatResponse, ToolInfo
from app.tools.registry import ToolRegistry
from app.utils.exceptions import LLMError

logger = get_logger(__name__)


class ChatService:
    """Application service that invokes the agent graph."""

    def __init__(self) -> None:
        self.tool_registry = ToolRegistry()
        self.builder = AgentBuilder(tool_registry=self.tool_registry)
        self.agent = self.builder.build()

    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Invoke the conversational agent for a user message."""
        start = perf_counter()
        config = {"configurable": {"thread_id": request.conversation_id}}
        try:
            result = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": request.message}]},
                config=config,
            )
        except Exception as exc:
            logger.exception("chat.llm_error", extra={"conversation_id": request.conversation_id})
            raise LLMError("The assistant could not complete the request.") from exc

        answer = self._extract_answer(result)
        elapsed_ms = round((perf_counter() - start) * 1000, 2)
        logger.info(
            "chat.completed",
            extra={
                "conversation_id": request.conversation_id,
                "elapsed_ms": elapsed_ms,
                "tools_available": self.tool_registry.tool_names(),
            },
        )
        return ChatResponse(
            conversation_id=request.conversation_id,
            answer=answer,
            tools_available=self.tool_registry.tool_names(),
        )

    def reset_memory(self, conversation_id: str) -> None:
        """Reset memory for a conversation thread."""
        self.builder.memory.reset_thread(conversation_id)
        logger.info("chat.memory_reset", extra={"conversation_id": conversation_id})

    def list_tools(self) -> list[ToolInfo]:
        """Return metadata for registered tools."""
        return [
            ToolInfo(name=tool.name, description=tool.description or "")
            for tool in self.tool_registry.get_tools()
        ]

    @staticmethod
    def _extract_answer(result: dict) -> str:
        """Extract final AI message content from a LangChain agent result."""
        messages = result.get("messages", [])
        for message in reversed(messages):
            if isinstance(message, AIMessage):
                return str(message.content)
            if isinstance(message, dict) and message.get("role") == "assistant":
                return str(message.get("content", ""))
        raise LLMError("The assistant returned no answer.")
