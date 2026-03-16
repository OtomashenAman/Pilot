import os
import json
import time
from openai import OpenAI

AZURE_OPENAI_API_KEY = os.environ["AZURE_OPENAI_API_KEY"]
AZURE_OPENAI_ENDPOINT = os.environ["AZURE_OPENAI_ENDPOINT"].rstrip("/")
AZURE_OPENAI_CODEX_DEPLOYMENT = os.environ["AZURE_OPENAI_CODEX_DEPLOYMENT"]

client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=f"{AZURE_OPENAI_ENDPOINT}/openai/v1/",
    timeout=120.0,
)


def retry_call(fn, retries=3, delay=3):
    last_err = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(delay)
    raise last_err


def _parse_json_response(raw: str) -> dict:
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("Azure Codex infra returned empty content")

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


def codex_generate_infra(repo_context: str, prd_pack: dict) -> dict:
    prompt = {
        "task": "Generate infra and docker setup for a compliance platform",
        "required_outputs": [
            "infra/docker-compose.yml",
            "backend/fastapi_services/compliance_api/Dockerfile",
            "frontend/web/Dockerfile",
            ".env.example",
        ],
        "repo_context": repo_context,
        "prd_pack": prd_pack,
        "output_schema": {
            "plan": ["string"],
            "diffs": [{"path": "string", "diff": "string"}],
            "notes": ["string"],
        },
    }

    def _call():
        print("[codex-infra] preparing request")
        response = client.responses.create(
            model=AZURE_OPENAI_CODEX_DEPLOYMENT,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a DevOps engineer. "
                        "Generate minimal runnable Docker and infra files. "
                        "Return ONLY valid JSON with keys: plan, diffs, notes."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt, ensure_ascii=False),
                },
            ],
        )
        print("[codex-infra] response received")
        raw = response.output_text or ""
        print("[codex-infra] raw response start")
        print(raw[:2000])
        print("[codex-infra] raw response end")
        return _parse_json_response(raw)

    return retry_call(_call)