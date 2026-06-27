"""VocalBridge integration tests."""

import pytest

from app.config.settings import get_settings
from app.services.vocal_bridge import VocalBridgeService
from app.utils.exceptions import ConfigurationError


class FakeSessions:
    def __init__(self) -> None:
        self.payload: dict | None = None

    async def create(self, **payload: object) -> dict:
        self.payload = payload
        return {
            "id": "vb_session_123",
            "token": "vb_voice_token",
            "livekit_url": "wss://livekit.example",
        }


class FakeClient:
    def __init__(self) -> None:
        self.sessions = FakeSessions()


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


async def test_create_voice_response_uses_sdk_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VOCAL_BRIDGE_API_KEY", "vb_test")
    monkeypatch.setenv("VOCAL_BRIDGE_AGENT_ID", "agent_123")
    fake_client = FakeClient()
    service = VocalBridgeService(client_factory=lambda: fake_client)

    response = await service.create_voice_response(
        conversation_id="demo",
        user_message="hello",
        assistant_answer="hi",
    )

    assert response.session_id == "vb_session_123"
    assert response.token == "vb_voice_token"  # noqa: S105 - fake SDK response.
    assert response.livekit_url == "wss://livekit.example"
    assert fake_client.sessions.payload == {
        "agent_id": "agent_123",
        "conversation_id": "demo",
        "input": "hello",
        "response": "hi",
        "metadata": {"source": "chat_endpoint"},
    }


async def test_create_voice_response_requires_api_key() -> None:
    service = VocalBridgeService(client_factory=FakeClient)

    with pytest.raises(ConfigurationError):
        await service.create_voice_response(
            conversation_id="demo",
            user_message="hello",
            assistant_answer="hi",
        )
