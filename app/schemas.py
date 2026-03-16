from pydantic import BaseModel
from typing import Any, Literal


JobStatus = Literal[
    "created",
    "generating_prd",
    "prd_done",
    "generating_backend",
    "generating_frontend",
    "generating_tests",
    "generating_infra",
    "writing_files",
    "validating_output",
    "code_done",
    "failed",
]


class BuildRequest(BaseModel):
    prompt: str
    stack: str = "django-fastapi-nextjs"
    db: str = "postgres"
    queue: str = "celery"


class BuildResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobDetail(BaseModel):
    job_id: str
    status: JobStatus
    prompt: str
    prd_pack: dict[str, Any] | None = None
    codex_plan: dict[str, Any] | None = None
    codex_diffs: dict[str, Any] | None = None
    validation: dict[str, Any] | None = None
    pr_status: str | None = None
    pr_url: str | None = None
    branch_name: str | None = None
    error: str | None = None