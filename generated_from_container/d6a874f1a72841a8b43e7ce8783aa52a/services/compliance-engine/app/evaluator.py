import hashlib
import json
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from .models import Rule, Decision
from .rules_dsl import evaluate


def canonical_hash(payload: Dict[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def compute_decision_hash(prev_hash: Optional[str], rule_id: int, input_hash: str, outcome: bool, evidence_ids: list) -> str:
    body = {
        "prev_hash": prev_hash or "",
        "rule_id": rule_id,
        "input_hash": input_hash,
        "outcome": outcome,
        "evidence_ids": evidence_ids,
    }
    return canonical_hash(body)


def get_active_rule(db: Session, jurisdiction: str, version_tag: Optional[str] = None) -> Rule:
    stmt = select(Rule).where(Rule.jurisdiction == jurisdiction)
    if version_tag:
        stmt = stmt.where(Rule.version_tag == version_tag)
    else:
        stmt = stmt.order_by(desc(Rule.effective_from))
    rule = db.execute(stmt).scalars().first()
    if not rule:
        raise ValueError("No matching rule")
    return rule


def evaluate_and_record(db: Session, rule: Rule, payload: Dict[str, Any]) -> Decision:
    outcome = bool(evaluate(rule.logic_jsonb.get("logic"), payload))
    evidence_ids = rule.logic_jsonb.get("evidence_ids", [])
    input_hash = canonical_hash(payload)
    prev = db.execute(select(Decision).order_by(desc(Decision.id))).scalars().first()
    prev_hash = prev.decision_hash if prev else None
    decision_hash = compute_decision_hash(prev_hash, rule.id, input_hash, outcome, evidence_ids)

    decision = Decision(
        rule_id=rule.id,
        input_hash=input_hash,
        outcome_bool=outcome,
        evidence_ids=evidence_ids,
        prev_decision_hash=prev_hash,
        decision_hash=decision_hash,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision
