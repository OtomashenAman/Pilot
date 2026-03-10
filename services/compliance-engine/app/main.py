from uuid import UUID
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from .models import RuleSet, DecisionLedger
from .evaluator import evaluate, input_hash, output_signature, chain_hash


app = FastAPI(title="compliance-engine")
Base.metadata.create_all(bind=engine)


class EvaluateRequest(BaseModel):
    contractor_id: UUID
    input: dict


@app.post("/evaluate/{jurisdiction}")
def evaluate_jurisdiction(jurisdiction: str, req: EvaluateRequest, db: Session = Depends(get_db)):
    rs = db.execute(
        select(RuleSet).where(RuleSet.jurisdiction == jurisdiction, RuleSet.active.is_(True)).order_by(RuleSet.created_at.desc())
    ).scalars().first()
    if not rs:
        raise HTTPException(status_code=404, detail="No active ruleset")

    result = evaluate(rs.logic_blob, req.input)
    ih = input_hash(req.input)
    oh = output_signature(req.input, rs.logic_blob, rs.version)

    last = db.execute(select(DecisionLedger).order_by(DecisionLedger.sequence.desc())).scalars().first()
    prev_hash = last.current_hash if last else None
    content = {
        "contractor_id": str(req.contractor_id),
        "jurisdiction": jurisdiction,
        "rule_version": rs.version,
        "input_hash": ih,
        "output": result,
        "output_hash": oh,
    }
    cur_hash = chain_hash(prev_hash or "", content)

    row = DecisionLedger(
        contractor_id=req.contractor_id,
        jurisdiction=jurisdiction,
        rule_version=rs.version,
        input_hash=ih,
        output=result,
        output_hash=oh,
        prev_hash=prev_hash,
        current_hash=cur_hash,
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return {"decision": result, "ledger_sequence": row.sequence, "hash": row.current_hash}
