import re

import pytest
from fastapi.testclient import TestClient


SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")


@pytest.fixture
def client():
    from services.compliance_engine.app.main import app

    return TestClient(app)


def test_create_build_accepts_semver(client: TestClient):
    payload = {
        "rule_slug": "worker-classification-de",
        "semantic_version": "2.1.4",
        "dsl_logic": {"if": [{">": ["salary", 100000]}, "employee", "contractor"]},
    }

    res = client.post("/builds", json=payload)
    assert res.status_code in (200, 201, 202)
    body = res.json()
    assert "status" in body
    assert body["status"] in {"queued", "building", "created", "accepted", "success"}


def test_create_build_rejects_invalid_semver(client: TestClient):
    payload = {
        "rule_slug": "worker-classification-de",
        "semantic_version": "2.1",
        "dsl_logic": {"if": [True, "employee", "contractor"]},
    }
    assert not SEMVER_RE.match(payload["semantic_version"])

    res = client.post("/builds", json=payload)
    assert res.status_code in (400, 422)


def test_get_build_not_found(client: TestClient):
    res = client.get("/builds/non-existent-build")
    assert res.status_code in (404, 422)


def test_build_response_contains_hash_or_identifier(client: TestClient):
    create = client.post(
        "/builds",
        json={
            "rule_slug": "worker-classification-us",
            "semantic_version": "1.0.0",
            "dsl_logic": {"if": [{"==": ["country", "US"]}, "employee", "contractor"]},
        },
    )
    assert create.status_code in (200, 201, 202)
    body = create.json()
    build_id = body.get("id") or body.get("build_id")
    assert build_id

    get_res = client.get(f"/builds/{build_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data.get("hash") or data.get("compiled_hash") or data.get("id") or data.get("build_id")
