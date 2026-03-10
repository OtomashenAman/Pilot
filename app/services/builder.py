from sqlalchemy.orm import Session
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
import os
from ..models import BuildJob
from ..llm.kimi import kimi_generate_prd_pack
from ..llm.codex import codex_generate_diffs
from .repo_context import build_repo_context
from .exporter import write_codex_diffs, write_prd_files

PACK_SCHEMA = {
    "type": "object",
    "required": ["files", "decisions"],
    "properties": {
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["path", "content"],
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"}
                }
            }
        },
        "decisions": {"type": "object"}
    }
}

_pack_validator = Draft202012Validator(PACK_SCHEMA)


def create_job(db: Session, prompt: str) -> BuildJob:
    import uuid
    job = BuildJob(job_id=uuid.uuid4().hex, prompt=prompt, status="created")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def run_build_pipeline(db: Session, job_id: str, stack: str, dbtype: str, queue: str) -> BuildJob:
    print(f"[builder] starting pipeline for {job_id}")
    job = db.query(BuildJob).filter(BuildJob.job_id == job_id).one()

    try:
        job.status = "generating_prd"
        db.commit()
        db.refresh(job)

        print(f"[builder] calling Kimi for {job_id}")
        pack = kimi_generate_prd_pack(job.prompt, stack=stack, db=dbtype, queue=queue)
        print(f"[builder] Kimi returned for {job_id}")

        errors = sorted(_pack_validator.iter_errors(pack), key=lambda e: e.path)
        if errors:
            raise ValidationError(errors[0].message)

        job.prd_pack = pack
        job.status = "prd_done"
        db.commit()
        db.refresh(job)

        job.status = "generating_code"
        db.commit()
        db.refresh(job)

        repo_context = build_repo_context()

        print(f"[builder] calling Codex for {job_id}")
        codex_out = codex_generate_diffs(repo_context=repo_context, prd_pack=pack)
        print(f"[builder] Codex returned for {job_id}")

        job.codex_plan = {
            "plan": codex_out.get("plan", []),
            "notes": codex_out.get("notes", []),
        }
        job.codex_diffs = {
            "diffs": codex_out.get("diffs", []),
        }
        db.commit()
        db.refresh(job)

        # WRITE TO FILESYSTEM
        generated_dir = os.path.join("/app/generated", job.job_id)
        prd_written = write_prd_files(job.prd_pack, base_dir=generated_dir)
        code_written = write_codex_diffs(job.codex_diffs, base_dir=generated_dir)

        print(f"[builder] writing output to {generated_dir}")
        print(f"[builder] wrote PRD files: {prd_written}")
        print(f"[builder] wrote code files: {code_written}")

        job.status = "code_done"
        db.commit()
        db.refresh(job)

        print(f"[builder] completed pipeline for {job_id}")
        return job

    except Exception as e:
        print(f"[builder] pipeline failed for {job_id}: {type(e).__name__}: {e}")
        job.status = "failed"
        job.error = f"{type(e).__name__}: {e}"
        db.commit()
        db.refresh(job)
        return job