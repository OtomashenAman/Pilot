from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from .db import Base, SessionLocal, engine, get_db
from .schemas import BuildRequest, BuildResponse, JobDetail
from .services.builder import create_job, run_build_pipeline
from .models import BuildJob

app = FastAPI(title="Compliance AI Builder", version="1.0.0")


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


@app.post("/v1/build", response_model=BuildResponse)
def build(req: BuildRequest, db: Session = Depends(get_db)):
    job = create_job(db, prompt=req.prompt)
    print(f"[main] created job {job.job_id}")

    run_build_pipeline(
        db=db,
        job_id=job.job_id,
        stack=req.stack,
        dbtype=req.db,
        queue=req.queue,
    )

    db.refresh(job)
    print(f"[main] finished job {job.job_id} with status {job.status}")
    return BuildResponse(job_id=job.job_id, status=job.status)


@app.get("/v1/jobs/{job_id}", response_model=JobDetail)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job: BuildJob | None = db.query(BuildJob).filter(BuildJob.job_id == job_id).first()
    if not job:
        raise HTTPException(404, "job not found")

    return JobDetail(
        job_id=job.job_id,
        status=job.status,  # type: ignore
        prompt=job.prompt,
        prd_pack=job.prd_pack,
        codex_plan=job.codex_plan,
        codex_diffs=job.codex_diffs,
        error=job.error,
    )


from .llm.kimi import client as kimi_client
import os

@app.get("/v1/test-kimi")
def test_kimi():
    import json
    resp = kimi_client.chat.completions.create(
        model=os.environ["KIMI_MODEL"],
        messages=[
            {"role": "user", "content": "Reply with exactly: OK"}
        ],
        temperature=1
    )
    return {"content": resp.choices[0].message.content}