"""Wikipedia lookup tool."""

import asyncio

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.config.logger import get_logger
from app.config.settings import get_settings
from app.tools.base import AssistantTool

logger = get_logger(__name__)


class WikipediaInput(BaseModel):
    """Input schema for Wikipedia lookups."""

    query: str = Field(
        ...,
        min_length=1,
        description="Topic, concept, person, or article to look up.",
    )


class WikipediaTool(AssistantTool):
    """Retrieve stable encyclopedic information from Wikipedia."""

    name = "wikipedia"
    description = (
        "Use for stable encyclopedic background, biographies, definitions, history, "
        "and general concepts. Mention the Wikipedia article used in the final answer."
    )

    def __init__(self) -> None:
        settings = get_settings()
        self.tool = WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(
                top_k_results=settings.wikipedia_top_k,
                doc_content_chars_max=3000,
            )
        )

    def as_langchain_tool(self) -> StructuredTool:
        """Return this tool as a LangChain structured tool."""
        return StructuredTool.from_function(
            name=self.name,
            description=self.description,
            args_schema=WikipediaInput,
            coroutine=self._arun,
        )

    async def _arun(self, query: str) -> str:
        """Run the Wikipedia query asynchronously."""
        try:
            logger.info("tool.wikipedia.start", extra={"query": query})
            result = await asyncio.to_thread(self.tool.run, query)
            logger.info("tool.wikipedia.complete", extra={"query": query})
            return (
                f"Source: Wikipedia\nQuery: {query}\n\n"
                f"{result or 'No Wikipedia results were found.'}"
            )
        except Exception as exc:
            return self.handle_error(exc)
