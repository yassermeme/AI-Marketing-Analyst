from collections.abc import Awaitable, Callable

from fastapi import Request

HealthProbe = Callable[[], Awaitable[None]]


def get_database_probe(request: Request) -> HealthProbe:
    return request.app.state.database_probe


def get_redis_probe(request: Request) -> HealthProbe:
    return request.app.state.redis_probe
