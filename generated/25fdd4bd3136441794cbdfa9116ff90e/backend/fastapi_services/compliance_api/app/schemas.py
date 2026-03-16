from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    source_type: Literal["api", "document", "manual", "system"]
    reference_id: str
    field_path: str | None = None
    data_hash: str
    confidence_score: float = Field(ge=0.0, le=1.0)


class EvaluateRequest(BaseModel):
    entity_id: str
    rule_slug: str
    jurisdiction: str
    input_payload: dict[str, Any]
    as_of: datetime | None = None


class EvaluateResponse(BaseModel):
    decision_id: str
    entity_id: str
    rule_version: str
    outcome: dict[str, Any]
    ledger_hash: str
    evidence: list[EvidenceItem] = []
    evaluated_at: datetime


class BatchEvaluateRequest(BaseModel):
    jobs: list[EvaluateRequest]


class BatchEvaluateResponse(BaseModel):
    job_id: str
    status: Literal["queued"]
    submitted_count: int


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    submitted_count: int | None = None
    completed_count: int | None = None
    failed_count: int | None = None
