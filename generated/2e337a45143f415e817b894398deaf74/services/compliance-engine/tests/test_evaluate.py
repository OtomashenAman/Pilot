from app.evaluator import canonical_json, sha256_hex
from app.rules_dsl import evaluate_ast


def test_ast_deterministic_result():
    ast = {
        "op": "AND",
        "args": [
            {"op": "COMPARE", "left": "country", "cmp": "eq", "right": "US"},
            {"op": "COMPARE", "left": "answers.has_w9", "cmp": "eq", "right": True},
        ],
    }
    ctx = {"country": "US", "answers": {"has_w9": True}}
    assert evaluate_ast(ast, ctx) is True
    assert evaluate_ast(ast, ctx) is True


def test_canonical_hash_stable():
    p1 = {"b": 2, "a": 1}
    p2 = {"a": 1, "b": 2}
    assert canonical_json(p1) == canonical_json(p2)
    assert sha256_hex(canonical_json(p1)) == sha256_hex(canonical_json(p2))
