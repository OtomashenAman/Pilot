import hashlib
import json
from typing import Any, Dict
from .rules_dsl import eval_rule


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def input_hash(payload: Dict[str, Any]) -> str:
    return sha256_hex(canonical_json(payload))


def evaluate(logic_blob: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    decision = bool(eval_rule(logic_blob["when"], payload))
    result = {
        "eligible": decision,
        "reason": logic_blob.get("reason", "rule_evaluated"),
    }
    return result


def output_signature(payload: Dict[str, Any], logic_blob: Dict[str, Any], version: str) -> str:
    material = canonical_json(payload) + canonical_json(logic_blob) + version
    return sha256_hex(material)


def chain_hash(prev_hash: str, content: Dict[str, Any]) -> str:
    return sha256_hex((prev_hash or "") + canonical_json(content))
