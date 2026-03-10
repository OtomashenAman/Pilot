from typing import Any, Dict, List


def _resolve_var(ctx: Dict[str, Any], path: str) -> Any:
    cur = ctx
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def evaluate(expr: Any, ctx: Dict[str, Any]) -> bool:
    if isinstance(expr, bool):
        return expr
    if not isinstance(expr, dict) or len(expr) != 1:
        raise ValueError("Invalid expression")

    op, args = next(iter(expr.items()))

    if op == "var":
        return _resolve_var(ctx, args)
    if op == "not":
        return not bool(evaluate(args, ctx))
    if op == "and":
        return all(bool(evaluate(a, ctx)) for a in args)
    if op == "or":
        return any(bool(evaluate(a, ctx)) for a in args)

    if op in {"==", "!=", ">", ">=", "<", "<="}:
        left = _value(args[0], ctx)
        right = _value(args[1], ctx)
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == ">":
            return left > right
        if op == ">=":
            return left >= right
        if op == "<":
            return left < right
        return left <= right

    raise ValueError(f"Unsupported op: {op}")


def _value(node: Any, ctx: Dict[str, Any]) -> Any:
    if isinstance(node, dict) and "var" in node:
        return _resolve_var(ctx, node["var"])
    if isinstance(node, dict):
        return evaluate(node, ctx)
    if isinstance(node, List):
        return [_value(n, ctx) for n in node]
    return node
