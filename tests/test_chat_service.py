"""Chat service unit tests."""

import pytest
from langchain_core.messages import AIMessage

from app.services.chat import ChatService
from app.utils.exceptions import LLMError


def test_extract_answer_from_ai_message() -> None:
    result = {"messages": [AIMessage(content="Hello there")]}
    assert ChatService._extract_answer(result) == "Hello there"


def test_extract_answer_raises_when_missing() -> None:
    with pytest.raises(LLMError):
        ChatService._extract_answer({"messages": []})
