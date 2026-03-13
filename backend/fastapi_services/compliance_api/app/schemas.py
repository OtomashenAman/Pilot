from datetime import datetime
from pydantic import BaseModel, Field


class BuildCreate(BaseModel):
    rule_slug: str = Field(min_length=3, max_length=128)
    semantic_version: str
    dsl_snapshot: dict
    created_by: str


class BuildResponse(BaseModel):
    id: int
    rule_slug: str
    semantic_version: str
    hash_sha256: str
    created_at: datetime


class JobCreate(BaseModel):
    rule_version_id: int
    input_payload: dict
    correlation_id: str


class JobResponse(BaseModel):
    job_id: str
    status: str
    queued_at: datetime
