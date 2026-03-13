import hashlib
import json
from datetime import datetime, timezone
from fastapi import APIRouter

from ..schemas import BuildCreate, BuildResponse

router = APIRouter()

_BUILDS = []


@router.post("", response_model=BuildResponse)
def create_build(payload: BuildCreate) -> BuildResponse:
    normalized = json.dumps(payload.dsl_snapshot, sort_keys=True, separators=(",", ":"))
    rule_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    build_id = len(_BUILDS) + 1
    item = {
        "id": build_id,
        "rule_slug": payload.rule_slug,
        "semantic_version": payload.semantic_version,
        "hash_sha256": rule_hash,
        "created_at": datetime.now(timezone.utc),
    }
    _BUILDS.append(item)
    return BuildResponse(**item)


@router.get("", response_model=list[BuildResponse])
def list_builds() -> list[BuildResponse]:
    return [BuildResponse(**b) for b in _BUILDS]
