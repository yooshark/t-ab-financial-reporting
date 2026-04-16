import pytest
from unittest.mock import MagicMock
from decimal import Decimal


async def test_get_all_ids(user_repo, mock_session):
    mock_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [1, 2, 3]
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    ids = await user_repo.get_all_ids()

    assert ids == [1, 2, 3]
    mock_session.execute.assert_called_once()


async def test_get_user_transactions_by_ids(user_repo, mock_session):
    mock_result = MagicMock()
    mock_data = [(1, 10, Decimal("1000.00"), Decimal("100.00")), (2, 5, Decimal("500.00"), Decimal("100.00"))]
    mock_result.all.return_value = mock_data
    mock_session.execute.return_value = mock_result

    result = await user_repo.get_user_transactions_by_external_ids([1, 2])

    assert result == mock_data
    mock_session.execute.assert_called_once()
