import pytest

from httpx import AsyncClient


class TestHealthCheck:
    @pytest.mark.anyio
    async def test_ping(self, client: AsyncClient):
        response = await client.get("/ping")
        assert response.status_code == 200
        assert response.json() == 'pong'
