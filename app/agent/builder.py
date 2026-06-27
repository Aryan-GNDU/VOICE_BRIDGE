"""Build the LangChain agent graph."""

from langchain.agents import create_agent
from langgraph.graph.state import CompiledStateGraph

from app.agent.memory import AgentMemory
from app.agent.prompts import SYSTEM_PROMPT
from app.config.llm import build_groq_chat_model
from app.config.logger import get_logger
from app.tools.registry import ToolRegistry

logger = get_logger(__name__)


class AgentBuilder:
    """Factory responsible for composing LLM, tools, prompt, and memory."""

    def __init__(
        self,
        tool_registry: ToolRegistry | None = None,
        memory: AgentMemory | None = None,
    ) -> None:
        self.tool_registry = tool_registry or ToolRegistry()
        self.memory = memory or AgentMemory()

    def build(self) -> CompiledStateGraph:
        """Create a LangChain v1 agent using the current tool registry."""
        tools = self.tool_registry.get_tools()
        logger.info("agent.build", extra={"tool_count": len(tools)})
        return create_agent(
            model=build_groq_chat_model(),
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
            checkpointer=self.memory.checkpointer,
        )
