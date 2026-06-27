"""Base utilities for assistant tools."""

from abc import ABC, abstractmethod
from typing import Any

from langchain_core.tools import BaseTool
from pydantic import BaseModel

from app.config.logger import get_logger
from app.utils.exceptions import AppError

logger = get_logger(__name__)


class ToolResult(BaseModel):
    """Normalized output from search and research tools."""

    source: str
    title: str
    content: str
    url: str | None = None
    metadata: dict[str, Any] = {}


class AssistantTool(ABC):
    """Contract for all application-owned tools."""

    name: str
    description: str

    @abstractmethod
    def as_langchain_tool(self) -> BaseTool:
        """Return the LangChain tool object."""

    def format_results(self, results: list[ToolResult]) -> str:
        """Format normalized results for the LLM."""
        if not results:
            return "No results were found."
        lines: list[str] = []
        for index, result in enumerate(results, start=1):
            url = f"\nURL: {result.url}" if result.url else ""
            metadata = f"\nMetadata: {result.metadata}" if result.metadata else ""
            lines.append(
                f"{index}. Source: {result.source}\n"
                f"Title: {result.title}{url}{metadata}\n"
                f"Summary: {result.content}"
            )
        return "\n\n".join(lines)

    def handle_error(self, error: Exception) -> str:
        """Log and return a safe tool error string for the model."""
        logger.exception("tool.error", extra={"tool": self.name, "error": str(error)})
        if isinstance(error, AppError):
            return error.detail
        return f"{self.name} failed temporarily. Try another tool or answer with uncertainty."
