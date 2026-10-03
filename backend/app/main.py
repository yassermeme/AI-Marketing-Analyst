from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.api.router import api_router
from app.core.config import get_settings
from app.core.health import make_database_probe, make_redis_probe

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine: AsyncEngine = create_async_engine(settings.database_url, pool_pre_ping=True)
    redis_client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    app.state.database_probe = make_database_probe(engine)
    app.state.redis_probe = make_redis_probe(redis_client)
    yield
    await redis_client.aclose()
    await engine.dispose()


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip().rstrip("/") for origin in settings.cors_origins.split(",") if origin.strip()],
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Content-Type"],
)
app.include_router(api_router, prefix=settings.api_v1_prefix)
