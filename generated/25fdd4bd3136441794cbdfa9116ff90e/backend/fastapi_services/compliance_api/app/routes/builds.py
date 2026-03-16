import hashlib
import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas import BatchEvaluateRequest, BatchEvaluateResponse, EvaluateRequest, EvaluateResponse

router = APIRouter(prefix="/evaluate", tags=["builds"])


@router.post("", response_model=EvaluateResponse)
async def evaluate(payload: EvaluateRequest, db: AsyncSession = Depends(get_db)) -> EvaluateResponse:
    evaluated_at = datetime.now(timezone.utc)
    outcome = {"compliant": True, "reasons": [], "score": 1.0}
    hash_input = {
        "entity_id": payload.entity_id,
        "rule_slug": payload.rule_slug,
        "jurisdiction": payload.jurisdiction,
        "input_payload": payload.input_payload,
        "outcome": outcome,
        "evaluated_at": evaluated_at.isoformat(),
    }
    ledger_hash = hashlib.sha256(json.dumps(hash_input, sort_keys=True).encode("utf-8")).hexdigest()
    return EvaluateResponse(
        decision_id=str(uuid.uuid4()),
        entity_id=payload.entity_id,
        rule_version="v1.0.0",
        outcome=outcome,
        ledger_hash=ledger_hash,
        evidence=[],
        evaluated_at=evaluated_at,
    )


@router.post("/batch", response_model=BatchEvaluateResponse)
async def evaluate_batch(payload: BatchEvaluateRequest, db: AsyncSession = Depends(get_db)) -> BatchEvaluateResponse:
    return BatchEvaluateResponse(
        job_id=str(uuid.uuid4()),
        status="queued",
        submitted_count=len(payload.jobs),
    )
