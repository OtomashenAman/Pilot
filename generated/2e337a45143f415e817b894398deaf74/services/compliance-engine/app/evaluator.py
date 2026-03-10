import hashlib
import json
from sqlalchemy import select
from .models import Decision
from .rules_dsl import evaluate_ast


def canonical_json(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def evaluate_and_record(db, contractor_id: str, ruleset, context: dict, evidence_refs=None):
    evidence_refs = evidence_refs or []
    input_hash = sha256_hex(canonical_json(context))
    eligible = evaluate_ast(ruleset.ast_json, context)
    output = {"eligible": bool(eligible), "jurisdiction": ruleset.jurisdiction, "version": ruleset.semantic_version}

    prev = db.execute(select(Decision).order_by(Decision.created_at.desc())).scalars().first()
    previous_hash = prev.ledger_hash if prev else ""

    row_material = canonical_json(
        {
            "contractor_id": contractor_id,
            "rule_version_id": str(ruleset.id),
            "input_hash": input_hash,
            "output": output,
            "evidence_refs": evidence_refs,
        }
    )
    ledger_hash = sha256_hex(previous_hash + row_material)

    decision = Decision(
        contractor_id=contractor_id,
        rule_version_id=ruleset.id,
        input_hash=input_hash,
        output=output,
        evidence_refs=evidence_refs,
        previous_hash=previous_hash or None,
        ledger_hash=ledger_hash,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision
