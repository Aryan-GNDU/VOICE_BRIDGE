"""Google Custom Search tool."""

import asyncio
from typing import Any

from langchain_community.utilities.google_search import GoogleSearchAPIWrapper
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.config.logger import get_logger
from app.config.settings import get_settings
from app.tools.base import AssistantTool, ToolResult
from app.utils.exceptions import ConfigurationError

logger = get_logger(__name__)


class GoogleSearchInput(BaseModel):
    """Input schema for Google Search."""

    query: str = Field(..., min_length=1, description="Search query for current web information.")


class GoogleSearchTool(AssistantTool):
    """Search the public web through Google Custom Search."""

    name = "google_search"
    description = (
        "Use for current events, latest announcements, recent facts, news, URLs, "
        "and broad web discovery. Returns concise snippets with source URLs."
    )

    def __init__(self) -> None:
        settings = get_settings()
        if not settings.google_api_key or not settings.google_cse_id:
            self.wrapper: GoogleSearchAPIWrapper | None = None
        else:
            self.wrapper = GoogleSearchAPIWrapper(
                google_api_key=settings.google_api_key.get_secret_value(),
                google_cse_id=settings.google_cse_id,
                k=settings.google_top_k,
            )

    def as_langchain_tool(self) -> StructuredTool:
        """Return this tool as a LangChain structured tool."""
        return StructuredTool.from_function(
            name=self.name,
            description=self.description,
            args_schema=GoogleSearchInput,
            coroutine=self._arun,
        )

    async def _arun(self, query: str) -> str:
        """Execute Google Search asynchronously."""
        try:
            if self.wrapper is None:
                raise ConfigurationError(
                    "GOOGLE_API_KEY and GOOGLE_CSE_ID are required for Google Search."
                )
            logger.info("tool.google_search.start", extra={"query": query})
            raw_results = await asyncio.to_thread(
                self.wrapper.results,
                query,
                get_settings().google_top_k,
            )
            results = [self._to_tool_result(item) for item in raw_results]
            logger.info(
                "tool.google_search.complete",
                extra={"query": query, "result_count": len(results)},
            )
            return self.format_results(results)
        except Exception as exc:
            return self.handle_error(exc)

    @staticmethod
    def _to_tool_result(item: dict[str, Any]) -> ToolResult:
        return ToolResult(
            source="Google Search",
            title=item.get("title", "Untitled result"),
            content=item.get("snippet", "No snippet available."),
            url=item.get("link"),
        )
