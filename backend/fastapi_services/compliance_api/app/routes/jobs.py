from datetime import datetime, timezone
from uuid import uuid4
from fastapi import APIRouter

from app.schemas import JobCreate, JobResponse, JobStatus

router = APIRouter(prefix="/jobs", tags=["jobs"])

_JOBS = []


@router.post("", response_model=JobResponse)
async def create_job(payload: JobCreate):
    job = JobResponse(
        id=str(uuid4()),
        tenant_id=payload.tenant_id,
        rule_version_id=payload.rule_version_id,
        status=JobStatus.pending,
        created_at=datetime.now(timezone.utc),
    )
    _JOBS.append(job)
    return job


@router.get("", response_model=list[JobResponse])
async def list_jobs():
    return _JOBS
