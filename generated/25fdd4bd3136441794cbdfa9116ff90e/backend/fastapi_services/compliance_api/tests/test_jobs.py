import importlib
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient


def _load_app():
    """Best-effort app loader to keep tests robust across minor layout changes."""
    candidates = [
        "backend.fastapi_services.compliance_api.app.main",
        "fastapi_services.compliance_api.app.main",
        "services.compliance_engine.app.main",
        "app.main",
        "main",
    ]
    for mod_name in candidates:
        try:
            mod = importlib.import_module(mod_name)
            app = getattr(mod, "app", None)
            if app is not None:
                return app, mod
        except Exception:
            continue
    raise RuntimeError("Unable to import FastAPI app from known module paths")


@pytest.fixture()
def client():
    app, _ = _load_app()
    with TestClient(app) as c:
        yield c


def _patch_first_available(monkeypatch, module, names, value):
    for name in names:
        if hasattr(module, name):
            monkeypatch.setattr(module, name, value)
            return name
    return None


def test_create_job_returns_accepted_and_job_id(client, monkeypatch):
    app, mod = _load_app()

    async def _fake_enqueue(payload: Dict[str, Any]):
        return {"job_id": "job_123", "status": "queued"}

    patched = _patch_first_available(
        monkeypatch,
        mod,
        ["enqueue_evaluation_job", "create_job", "submit_job", "enqueue_job"],
        _fake_enqueue,
    )
    if not patched:
        pytest.skip("No known job enqueue function found to patch")

    payload = {"entity_id": "entity-1", "rule_id": "aml-check", "input_payload": {"country": "US"}}
    resp = client.post("/jobs", json=payload)

    assert resp.status_code in (200, 201, 202)
    body = resp.json()
    assert "job_id" in body
    assert body["job_id"] == "job_123"
    assert body.get("status") in ("queued", "pending", "accepted")


def test_get_job_status_returns_terminal_state(client, monkeypatch):
    _, mod = _load_app()

    async def _fake_status(job_id: str):
        assert job_id == "job_done"
        return {
            "job_id": job_id,
            "status": "completed",
            "result": {"decision": "pass", "rule_version": "v1.0.0"},
        }

    patched = _patch_first_available(
        monkeypatch,
        mod,
        ["get_job_status", "fetch_job_status", "read_job_status"],
        _fake_status,
    )
    if not patched:
        pytest.skip("No known job status function found to patch")

    resp = client.get("/jobs/job_done")
    assert resp.status_code == 200
    body = resp.json()
    assert body["job_id"] == "job_done"
    assert body["status"] == "completed"
    assert body["result"]["decision"] == "pass"


def test_get_job_status_not_found(client, monkeypatch):
    _, mod = _load_app()

    async def _fake_status(job_id: str):
        return None

    patched = _patch_first_available(
        monkeypatch,
        mod,
        ["get_job_status", "fetch_job_status", "read_job_status"],
        _fake_status,
    )
    if not patched:
        pytest.skip("No known job status function found to patch")

    resp = client.get("/jobs/missing")
    assert resp.status_code in (404, 422)
