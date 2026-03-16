from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.schemas import BuildCreate, BuildRead


router = APIRouter(prefix="/builds", tags=["builds"])
_BUILDS = {}


@router.post("", response_model=BuildRead)
def create_build(payload: BuildCreate) -> BuildRead:
    build_id = str(uuid4())
    record = BuildRead(
        id=build_id,
        rule_key=payload.rule_key,
        version=payload.version,
        git_commit_hash=payload.git_commit_hash,
        status="created",
        created_at=datetime.now(timezone.utc),
    )
    _BUILDS[build_id] = record
    return record


@router.get("/{build_id}", response_model=BuildRead)
def get_build(build_id: str) -> BuildRead:
    if build_id not in _BUILDS:
        raise HTTPException(status_code=404, detail="build not found")
    return _BUILDS[build_id]
