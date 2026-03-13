import uuid
from datetime import datetime, timezone
from fastapi import APIRouter

from ..schemas import JobCreate, JobResponse

router = APIRouter()

_JOBS = {}


@router.post("", response_model=JobResponse)
def create_job(payload: JobCreate) -> JobResponse:
    job_id = str(uuid.uuid4())
    _JOBS[job_id] = {
        "status": "queued",
        "payload": payload.model_dump(),
        "queued_at": datetime.now(timezone.utc),
    }
    return JobResponse(job_id=job_id, status="queued", queued_at=_JOBS[job_id]["queued_at"])


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str) -> JobResponse:
    job = _JOBS[job_id]
    return JobResponse(job_id=job_id, status=job["status"], queued_at=job["queued_at"])
