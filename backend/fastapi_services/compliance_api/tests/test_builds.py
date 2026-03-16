import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Adjust import path if app module differs in repository
    from compliance_api.main import app

    return TestClient(app)


def test_create_build_success(client):
    payload = {
        "rule_key": "onboarding_compliance",
        "version": "2.1.0",
        "git_commit_hash": "a" * 40,
        "effective_from": "2026-01-01T00:00:00Z",
    }
    resp = client.post("/api/v1/builds", json=payload)
    assert resp.status_code in (200, 201)
    data = resp.json()
    assert "id" in data
    assert data.get("version") == "2.1.0"


def test_create_build_invalid_semver(client):
    payload = {
        "rule_key": "onboarding_compliance",
        "version": "v2",  # invalid semver expected by PRD
        "git_commit_hash": "b" * 40,
        "effective_from": "2026-01-01T00:00:00Z",
    }
    resp = client.post("/api/v1/builds", json=payload)
    assert resp.status_code in (400, 422)


def test_list_builds(client):
    resp = client.get("/api/v1/builds")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) or "items" in data


def test_get_build_not_found(client):
    resp = client.get("/api/v1/builds/non-existent-id")
    assert resp.status_code in (404, 422)
