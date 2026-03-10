from pydantic import BaseModel, Field
from typing import Any, Literal

JobStatus = Literal[
    "created",
    "generating_prd",
    "prd_done",
    "generating_code",
    "code_done",
    "failed",
]

class BuildRequest(BaseModel):
    prompt: str = Field(..., min_length=10)
    # Optional hints
    stack: str = Field("python-fastapi", description="e.g., python-fastapi")
    db: str = Field("postgres", description="e.g., postgres")
    queue: str = Field("celery", description="e.g., celery/temporal/none")

class BuildResponse(BaseModel):
    job_id: str
    status: JobStatus

class JobDetail(BaseModel):
    job_id: str
    status: JobStatus
    prompt: str
    prd_pack: dict | None = None
    codex_plan: dict | None = None
    codex_diffs: dict | None = None
    error: str | None = None

# Expected structured pack from Kimi
class PackFile(BaseModel):
    path: str
    content: str

class PRDPack(BaseModel):
    files: list[PackFile]
    decisions: dict[str, Any] = {}