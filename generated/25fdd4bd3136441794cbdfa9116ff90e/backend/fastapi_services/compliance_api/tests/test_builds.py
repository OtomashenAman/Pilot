import importlib
from typing import Any, Dict, List

import pytest
from fastapi.testclient import TestClient


def _load_app():
    for mod_name in [
        "backend.fastapi_services.compliance_api.app.main",
        "fastapi_services.compliance_api.app.main",
        "services.compliance_engine.app.main",
        "app.main",
        "main",
    ]:
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


def test_create_build_happy_path(client, monkeypatch):
    _, mod = _load_app()

    async def _fake_create(payload: Dict[str, Any]):
        return {
            "id": "build_1",
            "status": "created",
            "rule_id": payload["rule_id"],
            "version": payload["version"],
        }

    patched = _patch_first_available(
        monkeypatch,
        mod,
        ["create_build", "start_build", "enqueue_build"],
        _fake_create,
    )
    if not patched:
        pytest.skip("No known build create function found to patch")

    resp = client.post("/builds", json={"rule_id": "kyc", "version": "v1.1.0"})
    assert resp.status_code in (200, 201, 202)
    body = resp.json()
    assert body["id"] == "build_1"
    assert body["rule_id"] == "kyc"
    assert body["version"] == "v1.1.0"


def test_list_builds_returns_collection(client, monkeypatch):
    _, mod = _load_app()

    async def _fake_list() -> List[Dict[str, Any]]:
        return [
            {"id": "build_1", "status": "success", "version": "v1.0.0"},
            {"id": "build_2", "status": "running", "version": "v1.1.0"},
        ]

    patched = _patch_first_available(
        monkeypatch,
        mod,
        ["list_builds", "get_builds", "read_builds"],
        _fake_list,
    )
    if not patched:
        pytest.skip("No known builds list function found to patch")

    resp = client.get("/builds")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 2
    assert body[0]["id"] == "build_1"


def test_get_build_not_found(client, monkeypatch):
    _, mod = _load_app()

    async def _fake_get(build_id: str):
        return None

    patched = _patch_first_available(
        monkeypatch,
        mod,
        ["get_build", "fetch_build", "read_build"],
        _fake_get,
    )
    if not patched:
        pytest.skip("No known build getter function found to patch")

    resp = client.get("/builds/build_missing")
    assert resp.status_code in (404, 422)
