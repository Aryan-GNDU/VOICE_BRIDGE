"""FastAPI integration tests."""

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_config_does_not_expose_secrets(client: AsyncClient) -> None:
    response = await client.get("/config")
    assert response.status_code == 200
    body = response.json()
    assert "groq_api_key" not in body
    assert body["model_name"]
