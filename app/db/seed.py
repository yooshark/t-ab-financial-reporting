import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal

from faker import Faker

from app.core.config import settings
from app.db.models import (
    TransactionStatus,
    TransactionType,
)
from app.db.session import sessionmaker
from app.db.uow import SaSessionUnitOfWork

fake = Faker()


async def random_date() -> datetime:
    now = datetime.now()
    start = now - timedelta(days=365 * 2)
    return start + timedelta(seconds=random.randint(0, int((now - start).total_seconds())))


async def seed_db(uow: SaSessionUnitOfWork) -> None:
    async with uow:
        user_count = await uow.user_repo.count()

    if user_count > 0:
        return

    users = [
        {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "email": fake.unique.email(),
            "registered_at": fake.date_time_between(
                start_date="-2y",
                end_date="now",
            ),
        }
        for _ in range(settings.seed.USERS_COUNT)
    ]
    async with uow:
        await uow.user_repo.bulk_insert(users)

    async with uow:
        user_ids = await uow.user_repo.get_all_ids()

    statuses = list(TransactionStatus)
    types = list(TransactionType)

    batch = []

    for i in range(settings.seed.TRANSACTIONS_COUNT):
        batch.append(
            {
                "user_id": random.choice(user_ids),
                "amount": Decimal(random.randint(1, 1000)),
                "status": statuses[i % 2],
                "type": types[(i // 2) % 2],
                "payment_date": await random_date(),
            }
        )

        if len(batch) == settings.seed.BATCH:
            async with uow:
                await uow.transaction_repo.bulk_insert(batch)
            batch.clear()

    if batch:
        async with uow:
            await uow.transaction_repo.bulk_insert(batch)


async def run_seed() -> None:
    uow = SaSessionUnitOfWork(sessionmaker)
    await seed_db(uow)


if __name__ == "__main__":
    if settings.seed.ENABLED:
        asyncio.run(run_seed())
