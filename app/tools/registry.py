"""Central registry for all assistant tools."""

from langchain_core.tools import BaseTool

from app.tools.arxiv import ArxivTool
from app.tools.base import AssistantTool
from app.tools.google import GoogleSearchTool
from app.tools.wikipedia import WikipediaTool


class ToolRegistry:
    """Register and expose tools to the agent."""

    def __init__(self, tools: list[AssistantTool] | None = None) -> None:
        self._tools = tools or [
            GoogleSearchTool(),
            WikipediaTool(),
            ArxivTool(),
        ]

    def get_tools(self) -> list[BaseTool]:
        """Return LangChain tool objects."""
        return [tool.as_langchain_tool() for tool in self._tools]

    def tool_names(self) -> list[str]:
        """Return registered tool names."""
        return [tool.name for tool in self._tools]
