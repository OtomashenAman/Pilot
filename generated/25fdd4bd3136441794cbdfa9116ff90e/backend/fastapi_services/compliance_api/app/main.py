from fastapi import FastAPI

from .routes.builds import router as builds_router
from .routes.jobs import router as jobs_router

app = FastAPI(title="Compliance API", version="1.0.0")

app.include_router(builds_router, prefix="/api/v2")
app.include_router(jobs_router, prefix="/api/v2")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
