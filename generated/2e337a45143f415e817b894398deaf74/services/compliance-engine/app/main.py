from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .evaluator import evaluate_and_record
from .models import RuleSet


app = FastAPI(title="compliance-engine")


class EvaluateRequest(BaseModel):
    contractor_id: str
    jurisdiction: str
    semantic_version: str | None = None
    context: dict
    evidence_refs: list[str] = []


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.post("/evaluate")
def evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    stmt = select(RuleSet).where(RuleSet.jurisdiction == req.jurisdiction)
    if req.semantic_version:
        stmt = stmt.where(RuleSet.semantic_version == req.semantic_version)
    stmt = stmt.order_by(RuleSet.effective_from.desc())
    ruleset = db.execute(stmt).scalars().first()
    if not ruleset:
        raise HTTPException(status_code=404, detail="No ruleset found")

    decision = evaluate_and_record(
        db=db,
        contractor_id=req.contractor_id,
        ruleset=ruleset,
        context=req.context,
        evidence_refs=req.evidence_refs,
    )
    return {
        "decision_id": str(decision.id),
        "input_hash": decision.input_hash,
        "ledger_hash": decision.ledger_hash,
        "output": decision.output,
    }
