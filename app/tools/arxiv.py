"""arXiv research paper search tool."""

import asyncio
from typing import Any

from langchain_community.tools import ArxivQueryRun
from langchain_community.utilities import ArxivAPIWrapper
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.config.logger import get_logger
from app.config.settings import get_settings
from app.tools.base import AssistantTool

logger = get_logger(__name__)


class ArxivInput(BaseModel):
    """Input schema for arXiv search."""

    query: str = Field(
        ...,
        min_length=1,
        description="Research topic, paper title, author, or arXiv ID.",
    )


class ArxivTool(AssistantTool):
    """Search scholarly papers on arXiv."""

    name = "arxiv"
    description = (
        "Use for research papers, technical paper explanations, scholarly comparisons, "
        "authors, arXiv IDs, and publication years."
    )

    def __init__(self) -> None:
        settings = get_settings()
        self.tool = ArxivQueryRun(
            api_wrapper=ArxivAPIWrapper(
                top_k_results=settings.arxiv_top_k,
                doc_content_chars_max=4000,
                load_max_docs=settings.arxiv_top_k,
            )
        )

    def as_langchain_tool(self) -> StructuredTool:
        """Return this tool as a LangChain structured tool."""
        return StructuredTool.from_function(
            name=self.name,
            description=self.description,
            args_schema=ArxivInput,
            coroutine=self._arun,
        )

    async def _arun(self, query: str) -> str:
        """Run arXiv lookup asynchronously."""
        try:
            logger.info("tool.arxiv.start", extra={"query": query})
            result = await asyncio.to_thread(self.tool.run, query)
            logger.info("tool.arxiv.complete", extra={"query": query})
            return self._format_raw_result(query, result)
        except Exception as exc:
            return self.handle_error(exc)

    @staticmethod
    def _format_raw_result(query: str, result: Any) -> str:
        if not result:
            return "No arXiv papers were found."
        return (
            "Source: arXiv\n"
            f"Query: {query}\n\n"
            "The final answer must cite paper title, authors, arXiv ID, and year when present.\n\n"
            f"{result}"
        )
