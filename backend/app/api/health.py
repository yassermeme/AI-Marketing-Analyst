import asyncio
from datetime import UTC, datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.core.dependencies import HealthProbe, get_database_probe, get_redis_probe

router = APIRouter(tags=["health"])


class DependencyStatus(BaseModel):
    status: Literal["ok", "unavailable"]
    detail: str | None = None


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    timestamp: datetime
    dependencies: dict[str, DependencyStatus]


async def probe_dependency(name: str, probe: HealthProbe) -> tuple[str, DependencyStatus]:
    try:
        await probe()
    except Exception:
        return name, DependencyStatus(status="unavailable", detail="Connection unavailable")
    return name, DependencyStatus(status="ok")


@router.get("/health", response_model=HealthResponse, summary="Check API and dependency health")
async def health_check(
    database_probe: HealthProbe = Depends(get_database_probe),
    redis_probe: HealthProbe = Depends(get_redis_probe),
) -> HealthResponse:
    results = await asyncio.gather(
        probe_dependency("postgresql", database_probe),
        probe_dependency("redis", redis_probe),
    )
    dependencies = dict(results)
    overall_status: Literal["ok", "degraded"] = (
        "ok" if all(item.status == "ok" for item in dependencies.values()) else "degraded"
    )
    payload = HealthResponse(status=overall_status, timestamp=datetime.now(UTC), dependencies=dependencies)
    if overall_status != "ok":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=payload.model_dump(mode="json"))
    return payload
