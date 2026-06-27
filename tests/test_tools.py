"""Tool registry and tool behavior tests."""

import pytest

from app.tools.google import GoogleSearchTool
from app.tools.registry import ToolRegistry


def test_registry_exposes_expected_tools() -> None:
    registry = ToolRegistry()
    assert registry.tool_names() == ["google_search", "wikipedia", "arxiv"]


@pytest.mark.asyncio
async def test_google_tool_handles_missing_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_CSE_ID", raising=False)
    tool = GoogleSearchTool()
    result = await tool._arun("latest AI news")
    assert "GOOGLE_API_KEY" in result
