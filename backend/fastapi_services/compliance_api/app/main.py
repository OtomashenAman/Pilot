from fastapi import FastAPI

from .db import check_db_ready
from .routes import builds, jobs

app = FastAPI(title="Compliance API", version="1.0.0")


@app.on_event("startup")
def startup_event() -> None:
    check_db_ready()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


app.include_router(builds.router, prefix="/builds", tags=["builds"])
app.include_router(jobs.router, prefix="/jobs", tags=["jobs"])
