from datetime import datetime
from decimal import Decimal

from app.db.models import User, Transaction, TransactionStatus, TransactionType


def test_user_model_fields():
    user = User(first_name="John", last_name="Doe", email="john@example.com", registered_at=datetime.now())
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john@example.com"
    assert isinstance(user.registered_at, datetime)


def test_transaction_model_fields():
    transaction = Transaction(
        amount=Decimal("100.50"),
        status=TransactionStatus.SUCCESSFUL,
        type=TransactionType.PAYMENT,
        payment_date=datetime.now(),
    )
    assert transaction.amount == Decimal("100.50")
    assert transaction.status == TransactionStatus.SUCCESSFUL
    assert transaction.type == TransactionType.PAYMENT
    assert isinstance(transaction.payment_date, datetime)


def test_user_transaction_relationship():
    user = User(id=1, first_name="John")
    transaction = Transaction(id=1, user_id=1, user=user)
    user.transactions = [transaction]

    assert transaction.user == user
    assert transaction.user_id == 1
    assert user.transactions == [transaction]
