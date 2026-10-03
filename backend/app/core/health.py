from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio import Redis


@dataclass(frozen=True)
class DependencyProbes:
    database: callable
    redis: callable


def make_database_probe(engine: AsyncEngine):
    async def probe() -> None:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))

    return probe


def make_redis_probe(client: Redis):
    async def probe() -> None:
        if not await client.ping():
            raise ConnectionError("Redis ping returned false")

    return probe
