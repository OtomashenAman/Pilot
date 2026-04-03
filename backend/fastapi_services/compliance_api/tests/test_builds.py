import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Adjust import path to actual FastAPI app location if needed
    from services.compliance_engine.app.main import app

    return TestClient(app)


def test_list_builds_success(client, monkeypatch):
    expected = [
        {"id": "build_1", "status": "success"},
        {"id": "build_2", "status": "failed"},
    ]

    async def fake_list_builds(*args, **kwargs):
        return expected

    monkeypatch.setattr(
        "services.compliance_engine.app.main.list_builds",
        fake_list_builds,
        raising=False,
    )

    res = client.get("/builds")
    assert res.status_code == 200
    assert res.json() == expected


def test_get_build_success(client, monkeypatch):
    expected = {"id": "build_1", "status": "success", "artifact": "s3://x/y"}

    async def fake_get_build(*args, **kwargs):
        return expected

    monkeypatch.setattr(
        "services.compliance_engine.app.main.get_build",
        fake_get_build,
        raising=False,
    )

    res = client.get("/builds/build_1")
    assert res.status_code == 200
    assert res.json()["id"] == "build_1"


def test_create_build_validation_error(client):
    res = client.post("/builds", json={})
    assert res.status_code == 422
