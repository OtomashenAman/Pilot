import os

MAX_CHARS_DEFAULT = 60000

def build_repo_context(root: str = ".", max_chars: int | None = None) -> str:
    max_chars = max_chars or int(os.getenv("MAX_REPO_CONTEXT_CHARS", str(MAX_CHARS_DEFAULT)))

    # For first run, we assume empty/new repo; provide target structure only
    tree = [
        "services/compliance-engine/app/main.py",
        "services/compliance-engine/app/db.py",
        "services/compliance-engine/app/models.py",
        "services/compliance-engine/app/evaluator.py",
        "services/compliance-engine/app/rules_dsl.py",
        "services/compliance-engine/tests/test_evaluate.py",
        "services/compliance-engine/Dockerfile",
        "infra/docker-compose.yml",
    ]
    context = "REPO_TREE (desired):\n" + "\n".join(tree) + "\n"
    return context[:max_chars]