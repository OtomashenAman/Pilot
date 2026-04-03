from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter

from app.schemas import BuildCreate, BuildResponse, BuildStatus

router = APIRouter(prefix="/builds", tags=["builds"])

_BUILDS = []


@router.post("", response_model=BuildResponse)
async def create_build(payload: BuildCreate):
    build = BuildResponse(
        id=str(uuid4()),
        rule_set_id=payload.rule_set_id,
        status=BuildStatus.queued,
        created_at=datetime.now(timezone.utc),
    )
    _BUILDS.append(build)
    return build


@router.get("", response_model=list[BuildResponse])
async def list_builds():
    return _BUILDS
