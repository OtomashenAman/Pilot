import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.schemas import JobCreate, JobRead


router = APIRouter(prefix="/jobs", tags=["jobs"])
_JOBS = {}


def _canonical_hash(context: dict) -> str:
    canonical = json.dumps(context, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


@router.post("", response_model=JobRead)
def create_job(payload: JobCreate) -> JobRead:
    job_id = str(uuid4())
    input_hash = _canonical_hash(payload.context)
    record = JobRead(
        id=job_id,
        build_id=payload.build_id,
        input_hash=input_hash,
        status="queued",
        result=None,
        created_at=datetime.now(timezone.utc),
    )
    _JOBS[job_id] = record
    return record


@router.get("/{job_id}", response_model=JobRead)
def get_job(job_id: str) -> JobRead:
    if job_id not in _JOBS:
        raise HTTPException(status_code=404, detail="job not found")
    return _JOBS[job_id]
