import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock
from decimal import Decimal

from app.core.dependencies import get_report_service


async def test_get_report_endpoint(api_client: AsyncClient, mock_report_service, override_dependency):
    mock_report_service.get_report.return_value = {"amount_total": Decimal("1000.00"), "amount_avg": Decimal("100.00")}

    with override_dependency(get_report_service, mock_report_service):
        response = await api_client.get("/api/report/", params={"include_avg": "true"})

    assert response.status_code == 200
    data = response.json()
    assert data["amount_total"] == "1000.00"
    assert data["amount_avg"] == "100.00"

    mock_report_service.get_report.assert_called_once()


async def test_get_report_by_country_endpoint(api_client: AsyncClient, mock_report_service, override_dependency):

    mock_report_service.get_report_by_countries.return_value = [
        {"country": "USA", "count": 10, "total": 1000.0, "avg": 100.0}
    ]

    with override_dependency(get_report_service, mock_report_service):
        response = await api_client.get("/api/report/by-country", params={"top_n": 5})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["country"] == "USA"

    mock_report_service.get_report_by_countries.assert_called_once()
