from unittest.mock import MagicMock
from decimal import Decimal
from datetime import date

import pytest

from app.schemas.report import ReportQueryParams


async def test_set_params(transaction_repo):
    params = ReportQueryParams(start_date=date(2024, 1, 1))
    await transaction_repo.set_params(params)
    assert transaction_repo.params == params


async def test_get_base_metrics_positive(transaction_repo, mock_session):
    params = ReportQueryParams(include_avg=True)
    await transaction_repo.set_params(params)

    mock_result = MagicMock()
    mock_mapping = MagicMock()
    mock_mapping.all.return_value = [{"amount_total": Decimal("100.00"), "amount_avg": Decimal("50.00")}]
    mock_result.mappings.return_value = mock_mapping
    mock_session.execute.return_value = mock_result

    metrics = await transaction_repo.get_base_metrics()

    assert metrics["amount_total"] == Decimal("100.00")
    assert metrics["amount_avg"] == Decimal("50.00")
    mock_session.execute.assert_called_once()


async def test_get_daily_metrics_positive(transaction_repo, mock_session):
    params = ReportQueryParams(include_daily_shift=True)
    await transaction_repo.set_params(params)

    mock_result = MagicMock()
    mock_mapping = MagicMock()
    mock_data = [{"date": date(2024, 1, 1), "amount_total_daily_shift": Decimal("10.00")}]
    mock_mapping.all.return_value = mock_data
    mock_result.mappings.return_value = mock_mapping
    mock_session.execute.return_value = mock_result

    metrics = await transaction_repo.get_daily_metrics()

    assert len(metrics) == 1
    assert metrics[0]["date"] == date(2024, 1, 1)
    mock_session.execute.assert_called_once()


async def test_get_base_metrics_db_error_propagation(transaction_repo, mock_session):
    params = ReportQueryParams()
    await transaction_repo.set_params(params)

    mock_session.execute.side_effect = Exception("Database connection lost")

    with pytest.raises(Exception, match="Database connection lost"):
        await transaction_repo.get_base_metrics()


async def test_get_base_metrics_empty_db(transaction_repo, mock_session):
    params = ReportQueryParams()
    await transaction_repo.set_params(params)

    mock_result = MagicMock()
    mock_mapping = MagicMock()
    mock_mapping.all.return_value = [{"amount_total": None, "amount_avg": None}]
    mock_result.mappings.return_value = mock_mapping
    mock_session.execute.return_value = mock_result

    metrics = await transaction_repo.get_base_metrics()
    assert metrics["amount_total"] is None
    assert metrics["amount_avg"] is None
