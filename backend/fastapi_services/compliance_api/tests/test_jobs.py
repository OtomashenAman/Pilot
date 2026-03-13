import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Import lazily so tests fail clearly if app path changes.
    from services.compliance_engine.app.main import app

    return TestClient(app)


def test_create_job_returns_accepted_or_created(client: TestClient):
    payload = {
        "jurisdiction": "DE",
        "rule_version": "2.1.4",
        "input": {"country": "DE", "role": "Contractor", "salary": 120000},
    }

    res = client.post("/jobs", json=payload)

    assert res.status_code in (200, 201, 202)
    body = res.json()
    assert "id" in body or "job_id" in body
    assert "status" in body
    assert body["status"] in {"queued", "pending", "running", "accepted", "created"}


def test_get_job_not_found(client: TestClient):
    res = client.get("/jobs/non-existent-job-id")
    assert res.status_code in (404, 422)


def test_get_job_status_happy_path(client: TestClient):
    create_res = client.post(
        "/jobs",
        json={
            "jurisdiction": "US",
            "rule_version": "1.0.0",
            "input": {"country": "US", "role": "Employee", "salary": 90000},
        },
    )
    assert create_res.status_code in (200, 201, 202)
    body = create_res.json()
    job_id = body.get("id") or body.get("job_id")
    assert job_id

    res = client.get(f"/jobs/{job_id}")
    assert res.status_code == 200
    data = res.json()
    assert (data.get("id") or data.get("job_id")) == job_id
    assert data.get("status") in {"queued", "pending", "running", "succeeded", "failed", "completed"}


def test_create_job_validation_error(client: TestClient):
    # Missing required fields on purpose
    res = client.post("/jobs", json={"input": {}})
    assert res.status_code in (400, 422)
