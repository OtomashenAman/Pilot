import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Adjust import path if app module differs in repository
    from compliance_api.main import app

    return TestClient(app)


def test_create_job_success(client):
    payload = {
        "job_type": "compliance_evaluation",
        "context": {"country": "DE", "effective_date": "2026-01-01"},
        "rule_set": "onboarding_compliance",
        "version": "2.1.0",
    }

    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code in (200, 201)
    data = resp.json()

    assert "id" in data
    assert data.get("status") in {"queued", "pending", "created", "running"}


def test_create_job_validation_error(client):
    payload = {
        # missing required fields intentionally
        "job_type": "compliance_evaluation",
    }
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 422


def test_get_job_not_found(client):
    resp = client.get("/api/v1/jobs/non-existent-id")
    assert resp.status_code in (404, 422)


def test_get_job_by_id_after_create(client):
    create_payload = {
        "job_type": "compliance_evaluation",
        "context": {"country": "US", "effective_date": "2026-01-01"},
        "rule_set": "onboarding_compliance",
        "version": "2.1.0",
    }
    create_resp = client.post("/api/v1/jobs", json=create_payload)
    assert create_resp.status_code in (200, 201)
    created = create_resp.json()
    job_id = created["id"]

    get_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert get_resp.status_code == 200
    fetched = get_resp.json()

    assert fetched["id"] == job_id
    assert "status" in fetched
