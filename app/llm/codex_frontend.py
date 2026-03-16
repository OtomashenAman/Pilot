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
        raise ValueError("Azure Codex frontend returned empty content")

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


def codex_generate_frontend(repo_context: str, prd_pack: dict) -> dict:
    prompt = {
        "task": "Generate frontend UI for a compliance platform",
        "stack": {
            "frontend": "nextjs",
            "language": "typescript",
            "styling": "tailwind",
            "router": "app-router",
        },
        "required_outputs": [
            "frontend/web/app/layout.tsx",
            "frontend/web/app/page.tsx",
            "frontend/web/app/builds/page.tsx",
            "frontend/web/app/builds/[jobId]/page.tsx",
            "frontend/web/app/rules/page.tsx",
            "frontend/web/app/review/page.tsx",
            "frontend/web/components/BuildForm.tsx",
            "frontend/web/components/JobStatusCard.tsx",
            "frontend/web/components/ArtifactTabs.tsx",
            "frontend/web/components/MarkdownViewer.tsx",
            "frontend/web/components/CodeTreeViewer.tsx",
            "frontend/web/lib/api.ts",
            "frontend/web/lib/types.ts",
            "frontend/web/package.json",
            "frontend/web/next.config.js",
            "frontend/web/tsconfig.json",
            "frontend/web/postcss.config.js",
            "frontend/web/tailwind.config.ts",
            "frontend/web/app/globals.css",
            "frontend/web/Dockerfile",
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
        print("[codex-frontend] preparing request")
        response = client.responses.create(
            model=AZURE_OPENAI_CODEX_DEPLOYMENT,
            input=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior frontend engineer. "
                        "Generate production-style Next.js App Router code. "
                        "Return ONLY valid JSON with keys: plan, diffs, notes."
                    ),
                },
                {
                    "role": "user",
                    "content": json.dumps(prompt, ensure_ascii=False),
                },
            ],
        )
        print("[codex-frontend] response received")
        raw = response.output_text or ""
        print("[codex-frontend] raw response start")
        print(raw[:2000])
        print("[codex-frontend] raw response end")
        return _parse_json_response(raw)

    return retry_call(_call)