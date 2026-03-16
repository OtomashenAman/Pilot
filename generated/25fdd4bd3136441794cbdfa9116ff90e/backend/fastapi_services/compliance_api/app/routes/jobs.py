from fastapi import APIRouter

from ..schemas import JobStatusResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
    return JobStatusResponse(
        job_id=job_id,
        status="running",
        submitted_count=100,
        completed_count=42,
        failed_count=0,
    )


@router.get("", response_model=list[JobStatusResponse])
async def list_jobs() -> list[JobStatusResponse]:
    return [
        JobStatusResponse(
            job_id="example-job",
            status="completed",
            submitted_count=10,
            completed_count=10,
            failed_count=0,
        )
    ]
