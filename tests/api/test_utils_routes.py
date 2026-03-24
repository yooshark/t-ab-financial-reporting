from httpx import AsyncClient


async def test_health_check_endpoint(api_client: AsyncClient):
    response = await api_client.get("/api/utils/health-check/")

    assert response.status_code == 200
    assert response.json() is True
