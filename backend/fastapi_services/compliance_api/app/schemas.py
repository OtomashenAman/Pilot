from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class BuildStatus(str, Enum):
    queued = "queued"
    running = "running"
    succeeded = "succeeded"
    failed = "failed"


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    errored = "errored"


class BuildCreate(BaseModel):
    rule_set_id: str
    trigger: str = Field(default="manual")


class BuildResponse(BaseModel):
    id: str
    rule_set_id: str
    status: BuildStatus
    created_at: datetime


class JobCreate(BaseModel):
    tenant_id: str
    rule_version_id: str
    payload: dict


class JobResponse(BaseModel):
    id: str
    tenant_id: str
    rule_version_id: str
    status: JobStatus
    created_at: datetime
