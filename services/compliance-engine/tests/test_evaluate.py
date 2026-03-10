from app.evaluator import evaluate, input_hash


def test_evaluator_deterministic_hash():
    payload_a = {"age": 21, "country": "US"}
    payload_b = {"country": "US", "age": 21}
    assert input_hash(payload_a) == input_hash(payload_b)


def test_rules_dsl_basic():
    logic = {
        "when": {
            "all": [
                {"eq": ["country", "US"]},
                {"in": ["state", ["CA", "NY"]]}
            ]
        },
        "reason": "geo_check"
    }
    out = evaluate(logic, {"country": "US", "state": "CA"})
    assert out["eligible"] is True
