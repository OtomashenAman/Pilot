from typing import Any, Dict


def _lookup(context: Dict[str, Any], path: str) -> Any:
    cur: Any = context
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def evaluate_ast(node: Dict[str, Any], context: Dict[str, Any]) -> bool:
    op = node.get("op")
    if op == "AND":
        return all(evaluate_ast(child, context) for child in node.get("args", []))
    if op == "OR":
        return any(evaluate_ast(child, context) for child in node.get("args", []))
    if op == "NOT":
        return not evaluate_ast(node["arg"], context)
    if op == "LOOKUP":
        return bool(_lookup(context, node["path"]))
    if op == "COMPARE":
        left = _lookup(context, node["left"])
        right = node.get("right")
        cmp_op = node.get("cmp")
        if cmp_op == "eq":
            return left == right
        if cmp_op == "ne":
            return left != right
        if cmp_op == "gt":
            return left > right
        if cmp_op == "gte":
            return left >= right
        if cmp_op == "lt":
            return left < right
        if cmp_op == "lte":
            return left <= right
        if cmp_op == "in":
            return left in right
        raise ValueError(f"Unsupported compare operator: {cmp_op}")
    raise ValueError(f"Unsupported AST op: {op}")
