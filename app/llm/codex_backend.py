import os
import json
from openai import OpenAI

AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
AZURE_OPENAI_CODEX_DEPLOYMENT = os.environ["AZURE_OPENAI_CODEX_DEPLOYMENT"]

client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=f"{AZURE_OPENAI_ENDPOINT}/openai/v1/",
    timeout=90.0,
)


def _parse_json_response(raw: str) -> dict:
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("Azure Codex returned empty content")

    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        raw = raw[start:end + 1]

    return json.loads(raw)


def codex_generate_backend(repo_context: str, prd_pack: dict) -> dict:
    prompt = {
        "task": "Generate backend code for a compliance platform",
        "stack": {
            "backend": ["django", "fastapi"],
            "database": "postgres",
            "queue": "celery",
        },
        "required_outputs": [
            "backend/django_app/config/settings.py",
            "backend/django_app/apps/compliance_core/models.py",
            "backend/django_app/apps/rules_registry/models.py",
            "backend/fastapi_services/compliance_api/app/main.py",
            "backend/fastapi_services/compliance_api/app/routes/builds.py",
            "backend/fastapi_services/compliance_api/app/routes/jobs.py",
            "backend/fastapi_services/compliance_api/app/schemas.py",
            "backend/fastapi_services/compliance_api/app/db.py",
        ],
        "repo_context": repo_context,
        "prd_pack": prd_pack,
        "output_schema": {
            "plan": ["string"],
            "diffs": [{"path": "string", "diff": "string"}],
            "notes": ["string"],
        },
    }

    response = client.responses.create(
        model=AZURE_OPENAI_CODEX_DEPLOYMENT,
        input=[
            {
                "role": "system",
                "content": (
                    "You are a senior backend engineer. "
                    "Generate modular production-style backend code. "
                    "Return ONLY valid JSON with keys: plan, diffs, notes."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(prompt, ensure_ascii=False),
            },
        ],
    )

    raw = response.output_text or ""
    return _parse_json_response(raw)