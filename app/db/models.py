from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Index, Numeric, String, func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.core.enums import TransactionStatus, TransactionType


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=True,
        server_default=func.now(),
        onupdate=func.now(),
    )


class User(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
    )

    registered_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user",
    )
    external_id: Mapped[int]


class Transaction(Base):
    __tablename__ = "transactions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
        ),
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    status: Mapped[TransactionStatus] = mapped_column(
        SQLEnum(
            TransactionStatus,
            name="transaction_status",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    type: Mapped[TransactionType] = mapped_column(
        SQLEnum(
            TransactionType,
            name="transaction_type",
            values_callable=lambda enum: [e.value for e in enum],
        ),
        nullable=False,
    )

    payment_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
    )

    user: Mapped["User"] = relationship(
        back_populates="transactions",
    )

    __table_args__ = (
        Index(
            "ix_transactions_status_type_payment_date",
            "status",
            "type",
            "payment_date",
        ),
        Index(
            "ix_transactions_successful_payment_date",
            "payment_date",
            postgresql_where=(status == TransactionStatus.SUCCESSFUL),
        ),
    )
