from typing import Any, Dict, Optional
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .evaluator import get_active_rule, evaluate_and_record


app = FastAPI(title="compliance-engine")


class EvaluateRequest(BaseModel):
    jurisdiction: str
    version_tag: Optional[str] = None
    attributes: Dict[str, Any]


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.post("/evaluate")
def evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    try:
        rule = get_active_rule(db, req.jurisdiction, req.version_tag)
        decision = evaluate_and_record(db, rule, req.attributes)
        return {
            "decision_id": decision.id,
            "compliance_status": decision.outcome_bool,
            "evidence_links": decision.evidence_ids,
            "decision_hash": decision.decision_hash,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
