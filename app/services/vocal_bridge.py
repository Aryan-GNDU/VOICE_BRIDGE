"""VocalBridge SDK integration."""

from collections.abc import Callable
from importlib import import_module
from typing import Any

from pydantic import SecretStr

from app.config.settings import get_settings
from app.schemas.response import VocalBridgeResponse
from app.utils.exceptions import ConfigurationError, LLMError


class VocalBridgeService:
    """Thin adapter around the VocalBridge Python SDK."""

    def __init__(self, client_factory: Callable[[], Any] | None = None) -> None:
        self._client_factory = client_factory or self._build_client

    async def create_voice_response(
        self,
        *,
        conversation_id: str,
        user_message: str,
        assistant_answer: str,
    ) -> VocalBridgeResponse:
        """Create a VocalBridge session/token for a chat answer."""
        settings = get_settings()
        if settings.vocal_bridge_api_key is None:
            raise ConfigurationError("VOCAL_BRIDGE_API_KEY is required when voice=true.")

        client = self._client_factory()
        payload = {
            "agent_id": settings.vocal_bridge_agent_id,
            "conversation_id": conversation_id,
            "input": user_message,
            "response": assistant_answer,
            "metadata": {"source": "chat_endpoint"},
        }
        payload = {key: value for key, value in payload.items() if value is not None}

        try:
            result = await self._call_sdk(client, payload)
        except ConfigurationError:
            raise
        except Exception as exc:
            raise LLMError("VocalBridge could not create a voice session.") from exc

        normalized = self._to_dict(result)
        session_id = (
            normalized.get("session_id")
            or normalized.get("id")
            or normalized.get("sid")
        )
        return VocalBridgeResponse(
            session_id=session_id,
            token=normalized.get("token"),
            livekit_url=normalized.get("livekit_url") or normalized.get("livekitUrl"),
            raw=normalized,
        )

    @staticmethod
    async def _call_sdk(client: Any, payload: dict[str, Any]) -> Any:
        candidates = [
            ("sessions", "create"),
            ("voice_sessions", "create"),
            ("voice", "create_session"),
            (None, "create_session"),
            (None, "create_voice_session"),
            ("tokens", "create"),
            ("voice_tokens", "create"),
        ]
        for namespace, method_name in candidates:
            target = getattr(client, namespace, None) if namespace else client
            if target is None:
                continue
            method = getattr(target, method_name, None)
            if method is None:
                continue
            result = method(**payload)
            if hasattr(result, "__await__"):
                result = await result
            return result

        raise ConfigurationError(
            "Installed VocalBridge SDK does not expose a supported session/token method."
        )

    @staticmethod
    def _build_client() -> Any:
        settings = get_settings()
        api_key = _secret_value(settings.vocal_bridge_api_key)
        if api_key is None:
            raise ConfigurationError("VOCAL_BRIDGE_API_KEY is required when voice=true.")

        for module_name in ("vocalbridge", "vocalbridgeai"):
            try:
                module = import_module(module_name)
            except ImportError:
                continue

            for class_name in ("VocalBridge", "VocalBridgeClient", "Client"):
                client_class = getattr(module, class_name, None)
                if client_class is None:
                    continue
                try:
                    return client_class(api_key=api_key)
                except TypeError:
                    return client_class(api_key)

        raise ConfigurationError(
            "Install the VocalBridge Python SDK package to use voice=true."
        )

    @staticmethod
    def _to_dict(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump()
        if hasattr(value, "dict"):
            return value.dict()
        return {
            key: getattr(value, key)
            for key in ("id", "sid", "session_id", "token", "livekit_url", "livekitUrl")
            if hasattr(value, key)
        }


def _secret_value(secret: SecretStr | None) -> str | None:
    return secret.get_secret_value() if secret is not None else None
