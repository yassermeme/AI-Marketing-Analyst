from fastapi.testclient import TestClient

from app.main import app


async def healthy_probe() -> None:
    return None


async def unavailable_probe() -> None:
    raise ConnectionError("unavailable")


def test_health_check_reports_healthy_dependencies() -> None:
    with TestClient(app) as client:
        app.state.database_probe = healthy_probe
        app.state.redis_probe = healthy_probe
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["dependencies"] == {"postgresql": {"status": "ok", "detail": None}, "redis": {"status": "ok", "detail": None}}


def test_health_check_returns_503_when_dependency_is_unavailable() -> None:
    with TestClient(app, raise_server_exceptions=False) as client:
        app.state.database_probe = unavailable_probe
        app.state.redis_probe = healthy_probe
        response = client.get("/api/v1/health")

    assert response.status_code == 503
    payload = response.json()["detail"]
    assert payload["status"] == "degraded"
    assert payload["dependencies"]["postgresql"]["status"] == "unavailable"
    assert payload["dependencies"]["redis"]["status"] == "ok"
