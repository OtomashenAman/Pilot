from typing import Any, Dict


def _get_path(data: Dict[str, Any], path: str) -> Any:
    cur = data
    for part in path.split('.'):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def eval_rule(rule: Dict[str, Any], ctx: Dict[str, Any]) -> bool:
    if "all" in rule:
        return all(eval_rule(r, ctx) for r in rule["all"])
    if "any" in rule:
        return any(eval_rule(r, ctx) for r in rule["any"])
    if "not" in rule:
        return not eval_rule(rule["not"], ctx)
    if "eq" in rule:
        left = _get_path(ctx, rule["eq"][0])
        right = rule["eq"][1]
        return left == right
    if "in" in rule:
        left = _get_path(ctx, rule["in"][0])
        right = rule["in"][1]
        return left in right
    if "exists" in rule:
        return _get_path(ctx, rule["exists"]) is not None
    raise ValueError("Unsupported rule operator")
