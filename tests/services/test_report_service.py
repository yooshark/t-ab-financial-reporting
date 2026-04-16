import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
from decimal import Decimal
import pandas as pd

from app.services.report_service import ReportService
from app.schemas.report import ReportQueryParams
from app.core.enums import TransactionStatus, MetricSortByCountry


@pytest.mark.asyncio
async def test_get_report_total_calculation_positive(report_service, mock_tr_manager):
    """Verify correct calculation of total transaction amount."""
    params = ReportQueryParams()
    mock_metrics = {"amount_total": Decimal("1500.50")}
    mock_tr_manager.transaction_repo.get_base_metrics.return_value = mock_metrics

    result = await report_service.get_report(params)

    assert result["amount_total"] == Decimal("1500.50")


@pytest.mark.asyncio
async def test_get_report_average_calculation_positive(report_service, mock_tr_manager):
    """Verify correct calculation of average transaction amount."""
    params = ReportQueryParams(include_avg=True)
    mock_metrics = {"amount_total": Decimal("1000.00"), "amount_avg": Decimal("250.00")}
    mock_tr_manager.transaction_repo.get_base_metrics.return_value = mock_metrics

    result = await report_service.get_report(params)

    assert result["amount_avg"] == Decimal("250.00")


@pytest.mark.asyncio
async def test_get_report_min_max_calculation_positive(report_service, mock_tr_manager):
    """Verify correct calculation of minimum and maximum transaction amounts."""
    params = ReportQueryParams(include_min=True, include_max=True)
    mock_metrics = {"amount_total": Decimal("1000.00"), "amount_min": Decimal("5.00"), "amount_max": Decimal("500.00")}
    mock_tr_manager.transaction_repo.get_base_metrics.return_value = mock_metrics

    result = await report_service.get_report(params)

    assert result["amount_min"] == Decimal("5.00")
    assert result["amount_max"] == Decimal("500.00")


@pytest.mark.asyncio
async def test_get_report_daily_aggregations_positive(report_service, mock_tr_manager):
    """Verify correct daily aggregations with shift metrics."""
    params = ReportQueryParams(include_daily_shift=True, include_avg=True)
    base_metrics = {"amount_total": Decimal("1000.00")}
    daily_metrics = [
        {
            "date": date(2024, 1, 1),
            "amount_total_daily_shift": Decimal("100.00"),
            "amount_avg_daily_shift": Decimal("10.00"),
        },
        {
            "date": date(2024, 1, 2),
            "amount_total_daily_shift": Decimal("200.00"),
            "amount_avg_daily_shift": Decimal("20.00"),
        },
    ]

    mock_tr_manager.transaction_repo.get_base_metrics.return_value = base_metrics
    mock_tr_manager.transaction_repo.get_daily_metrics.return_value = daily_metrics

    result = await report_service.get_report(params)

    assert len(result["daily"]) == 2
    assert result["daily"][0]["date"] == date(2024, 1, 1)
    assert result["daily"][0]["amount_total"] == Decimal("100.00")


@pytest.mark.asyncio
async def test_get_report_by_country_positive(report_service, mock_tr_manager):
    """Verify correct country-based metrics calculation and aggregation."""
    mock_df = pd.DataFrame({"id": [1, 2, 3], "country": ["USA", "USA", "UK"]})

    with patch("app.services.report_service.read_csv", return_value=mock_df):
        mock_tr_manager.user_repo.get_user_transactions_by_external_ids.return_value = [
            (1, 2, Decimal("200.00"), Decimal("100.00")),
            (2, 3, Decimal("300.00"), Decimal("100.00")),
            (3, 1, Decimal("50.00"), Decimal("50.00")),
        ]

        result = await report_service.get_report_by_countries(sort_by=MetricSortByCountry.TOTAL, top_n=None)

        assert len(result) == 2
        usa_report = next(item for item in result if item["country"] == "USA")
        assert usa_report["count"] == 5
        assert usa_report["total"] == 500.0


# --- Negative and Edge Cases ---


@pytest.mark.asyncio
async def test_get_report_failed_status_edge_case(report_service):
    """Verify that 'failed' status returns empty report (per business logic)."""
    params = ReportQueryParams(tr_status=TransactionStatus.FAILED)
    result = await report_service.get_report(params)
    assert result == {}


@pytest.mark.asyncio
async def test_get_report_empty_repo_result(report_service, mock_tr_manager):
    """Handle empty transaction list (zero or null-safe values)."""
    params = ReportQueryParams()
    mock_tr_manager.transaction_repo.get_base_metrics.return_value = {
        "amount_total": Decimal("0.00"),
        "amount_avg": None,
        "amount_min": None,
        "amount_max": None,
    }

    result = await report_service.get_report(params)
    assert result["amount_total"] == Decimal("0.00")
    assert result["amount_avg"] is None


@pytest.mark.asyncio
async def test_get_report_by_countries_empty_csv(report_service, mock_tr_manager):
    """Handle empty CSV file gracefully."""
    mock_df = pd.DataFrame(columns=["id", "country"])

    with patch("app.services.report_service.read_csv", return_value=mock_df):
        result = await report_service.get_report_by_countries(sort_by=None, top_n=None)
        assert result == []


@pytest.mark.asyncio
async def test_get_report_by_countries_no_users_found(report_service, mock_tr_manager):
    """Handle case where users in CSV have no matching transactions in DB."""
    mock_df = pd.DataFrame({"id": [999], "country": ["Mars"]})

    with patch("app.services.report_service.read_csv", return_value=mock_df):
        mock_tr_manager.user_repo.get_user_transactions_by_external_ids.return_value = []

        result = await report_service.get_report_by_countries(sort_by=None, top_n=None)
        assert len(result) == 1
        assert result[0]["country"] == "Mars"
        assert result[0]["total"] == 0.0
        assert result[0]["count"] == 0
