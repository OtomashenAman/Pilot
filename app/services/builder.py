from sqlalchemy.orm import Session
from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
import os

from .validators import validate_backend_imports, validate_frontend
from .frontend_template import write_starter_frontend
from ..models import BuildJob
from ..llm.kimi import kimi_generate_prd_pack, retry_call
from ..llm.codex_backend import codex_generate_backend
from ..llm.codex_frontend import codex_generate_frontend
from ..llm.codex_tests import codex_generate_tests
from ..llm.codex_infra import codex_generate_infra
from .repo_context import build_repo_context
from .exporter import write_codex_diffs, write_prd_files
from .file_ops import copy_tree
from .git_ops import (
    ensure_git_identity,
    set_authenticated_remote,
    checkout_base_branch,
    create_branch,
    add_commit_push,
)
from .github_pr import create_github_pr

PACK_SCHEMA = {
    "type": "object",
    "required": ["files", "decisions"],
    "properties": {
        "files": {
            "type": "array",
            "minItems": 2,
            "items": {
                "type": "object",
                "required": ["path", "content"],
                "properties": {
                    "path": {"type": "string"},
                    "content": {"type": "string"},
                },
            },
        },
        "decisions": {
            "type": "object",
            "required": ["backend", "frontend", "db", "queue"],
            "properties": {
                "backend": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "frontend": {"type": "string"},
                "db": {"type": "string"},
                "queue": {"type": "string"},
            },
        },
    },
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
        pack = retry_call(lambda: kimi_generate_prd_pack(job.prompt, stack=stack, db=dbtype, queue=queue))
        print(f"[builder] Kimi returned for {job_id}")

        errors = sorted(_pack_validator.iter_errors(pack), key=lambda e: e.path)
        if errors:
            raise ValidationError(errors[0].message)

        job.prd_pack = pack
        job.status = "prd_done"
        db.commit()
        db.refresh(job)

        repo_context = build_repo_context()

        job.status = "generating_backend"
        db.commit()
        db.refresh(job)
        print(f"[builder] calling Codex backend for {job_id}")
        backend_out = retry_call(lambda: codex_generate_backend(repo_context=repo_context, prd_pack=pack))
        print(f"[builder] Codex backend returned for {job_id}")

        job.status = "generating_frontend"
        db.commit()
        db.refresh(job)
        print(f"[builder] calling Codex frontend for {job_id}")
        frontend_out = retry_call(lambda: codex_generate_frontend(repo_context=repo_context, prd_pack=pack))
        print(f"[builder] Codex frontend returned for {job_id}")

        job.status = "generating_tests"
        db.commit()
        db.refresh(job)
        print(f"[builder] calling Codex tests for {job_id}")
        tests_out = retry_call(lambda: codex_generate_tests(repo_context=repo_context, prd_pack=pack))
        print(f"[builder] Codex tests returned for {job_id}")

        job.status = "generating_infra"
        db.commit()
        db.refresh(job)
        print(f"[builder] calling Codex infra for {job_id}")
        infra_out = retry_call(lambda: codex_generate_infra(repo_context=repo_context, prd_pack=pack))
        print(f"[builder] Codex infra returned for {job_id}")

        merged_plan = []
        merged_notes = []
        merged_diffs = []

        for part in [backend_out, frontend_out, tests_out, infra_out]:
            merged_plan.extend(part.get("plan", []))
            merged_notes.extend(part.get("notes", []))
            merged_diffs.extend(part.get("diffs", []))

        job.codex_plan = {
            "plan": merged_plan,
            "notes": merged_notes,
        }
        job.codex_diffs = {
            "diffs": merged_diffs,
        }
        db.commit()
        db.refresh(job)

        job.status = "writing_files"
        db.commit()
        db.refresh(job)

        generated_dir = os.path.join("/app/generated", job.job_id)
        prd_written = write_prd_files(job.prd_pack, base_dir=generated_dir)
        code_written = write_codex_diffs(job.codex_diffs, base_dir=generated_dir)

        print(f"[builder] writing output to {generated_dir}")
        print(f"[builder] wrote PRD files: {prd_written}")
        print(f"[builder] wrote code files: {code_written}")

        frontend_package = os.path.join(generated_dir, "frontend", "web", "package.json")
        if not os.path.exists(frontend_package):
            print("[builder] frontend package.json missing, writing starter frontend template")
            write_starter_frontend(generated_dir)

        job.status = "validating_output"
        db.commit()
        db.refresh(job)

        backend_dir = os.path.join(generated_dir, "backend")
        frontend_dir = os.path.join(generated_dir, "frontend", "web")

        backend_validation = validate_backend_imports(backend_dir)

        if os.path.exists(frontend_dir) and os.path.exists(os.path.join(frontend_dir, "package.json")):
            frontend_validation = validate_frontend(frontend_dir)
        else:
            frontend_validation = {
                "ok": False,
                "step": "frontend_validation_skipped",
                "reason": "frontend package.json not found",
            }

        job.validation = {
            "backend": backend_validation,
            "frontend": frontend_validation,
        }
        job.status = "code_done"
        job.pr_status = "not_started"
        db.commit()
        db.refresh(job)

        auto_git_pr = os.getenv("AUTO_GIT_PR", "false").lower() == "true"

        if auto_git_pr:
            try:
                repo_path = os.environ["LOCAL_REPO_PATH"]
                base_branch = os.getenv("GITHUB_BASE_BRANCH", "main")
                branch_name = f"ai/{job.job_id}"

                job.pr_status = "creating"
                job.branch_name = branch_name
                db.commit()
                db.refresh(job)

                print("[builder] configuring git")
                ensure_git_identity(repo_path)
                set_authenticated_remote(repo_path)

                print(f"[builder] checking out base branch: {base_branch}")
                checkout_base_branch(repo_path, base_branch)

                print(f"[builder] creating branch: {branch_name}")
                create_branch(repo_path, branch_name)

                print(f"[builder] copying generated files into repo: {repo_path}")
                copy_tree(generated_dir, repo_path)

                print(f"[builder] committing and pushing branch: {branch_name}")
                push_result = add_commit_push(
                    repo_path=repo_path,
                    commit_message=f"AI-generated compliance platform scaffold for job {job.job_id}",
                    branch_name=branch_name,
                )

                if push_result == "no_changes":
                    job.pr_status = "failed"
                    job.error = "git/pr step failed: no changes detected for PR creation"
                    db.commit()
                    db.refresh(job)
                else:
                    pr = create_github_pr(
                        branch_name=branch_name,
                        title=f"AI: Compliance platform scaffold ({job.job_id})",
                        body=(
                            "This PR was generated automatically from the Kimi PRD pack "
                            "and Azure Codex implementation pipeline."
                        ),
                    )
                    job.pr_status = "created"
                    job.pr_url = pr.get("html_url")
                    db.commit()
                    db.refresh(job)
                    print(f"[builder] PR created: {job.pr_url}")

            except Exception as git_err:
                print(f"[builder] git/pr step failed: {git_err}")
                job.pr_status = "failed"
                job.error = f"git/pr step failed: {git_err}"
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