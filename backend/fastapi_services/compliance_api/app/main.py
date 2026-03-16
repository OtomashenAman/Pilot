from fastapi import FastAPI

from app.routes import builds, jobs


app = FastAPI(title="Compliance API", version="1.0.0")


@app.get("/health", tags=["system"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(builds.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
