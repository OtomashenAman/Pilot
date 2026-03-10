from app.evaluator import canonical_hash
from app.rules_dsl import evaluate


def test_canonical_hash_deterministic():
    a = {"b": 1, "a": {"x": 2, "y": 3}}
    b = {"a": {"y": 3, "x": 2}, "b": 1}
    assert canonical_hash(a) == canonical_hash(b)


def test_rules_dsl_evaluate_boolean_logic():
    expr = {
        "and": [
            {">=": [{"var": "age"}, 18]},
            {"==": [{"var": "country"}, "DE"]}
        ]
    }
    assert evaluate(expr, {"age": 20, "country": "DE"}) is True
    assert evaluate(expr, {"age": 17, "country": "DE"}) is False
