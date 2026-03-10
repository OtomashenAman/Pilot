import os
import json
import re
from openai import OpenAI

MOONSHOT_API_KEY = os.environ["MOONSHOT_API_KEY"]
MOONSHOT_BASE_URL = os.getenv("MOONSHOT_BASE_URL", "https://api.moonshot.ai/v1")
KIMI_MODEL = os.getenv("KIMI_MODEL", "kimi-k2.5")

client = OpenAI(
    api_key=MOONSHOT_API_KEY,
    base_url=MOONSHOT_BASE_URL,
    timeout=60.0,
)


def extract_json_object(raw: str) -> str:
    raw = (raw or "").strip()
    if not raw:
        raise ValueError("Model returned empty content")

    if raw.startswith("```"):
        lines = raw.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw = "\n".join(lines).strip()

    start = raw.find("{")
    end = raw.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No complete JSON object found in model output")

    return raw[start:end + 1]


def try_repair_json(raw: str) -> str:
    raw = re.sub(r",(\s*[}\]])", r"\1", raw)
    raw = raw.replace("“", '"').replace("”", '"').replace("’", "'")
    return raw


def parse_json_response(raw: str) -> dict:
    candidate = extract_json_object(raw)
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        repaired = try_repair_json(candidate)
        return json.loads(repaired)


def kimi_generate_prd_pack(user_prompt: str, stack: str, db: str, queue: str) -> dict:
    system = """
You are a senior product architect.

Return ONLY one valid JSON object.
Do not use markdown fences.
Do not add explanations.
Do not add comments.

Schema:
{
  "files": [
    {"path":"docs/PRD.md","content":"..."},
    {"path":"docs/ARCHITECTURE.md","content":"..."}
  ],
  "decisions": {
    "language":"python",
    "framework":"fastapi",
    "db":"postgres",
    "queue":"celery"
  }
}

Keep content concise but useful.
"""

    user = {
        "request": user_prompt,
        "constraints": {
            "stack": stack,
            "db": db,
            "queue": queue,
            "must_have": [
                "deterministic rule engine",
                "rule versioning",
                "decision ledger",
                "evidence citations"
            ]
        }
    }

    print("[kimi] preparing request")
    resp = client.chat.completions.create(
        model=KIMI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
        ],
        temperature=1,
        max_tokens=5000,
        response_format={"type": "json_object"},
    )
    print("[kimi] response received")

    raw = resp.choices[0].message.content or ""
    print("[kimi] raw response start")
    print(raw)
    print("[kimi] raw response end")

    return parse_json_response(raw)