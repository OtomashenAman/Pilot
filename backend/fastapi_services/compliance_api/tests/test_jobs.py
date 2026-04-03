import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Adjust import path to actual FastAPI app location if needed
    from services.compliance_engine.app.main import app

    return TestClient(app)


def test_list_jobs_success(client, monkeypatch):
    expected = [
        {"id": "job_1", "status": "queued"},
        {"id": "job_2", "status": "running"},
    ]

    async def fake_list_jobs(*args, **kwargs):
        return expected

    monkeypatch.setattr(
        "services.compliance_engine.app.main.list_jobs",
        fake_list_jobs,
        raising=False,
    )

    res = client.get("/jobs")
    assert res.status_code == 200
    assert res.json() == expected


def test_get_job_not_found(client, monkeypatch):
    async def fake_get_job(*args, **kwargs):
        return None

    monkeypatch.setattr(
        "services.compliance_engine.app.main.get_job",
        fake_get_job,
        raising=False,
    )

    res = client.get("/jobs/missing-job")
    assert res.status_code in (404, 422)


def test_create_job_validation_error(client):
    # Intentionally invalid payload
    res = client.post("/jobs", json={"unexpected": True})
    assert res.status_code == 422
