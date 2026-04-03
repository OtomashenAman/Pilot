from fastapi import FastAPI

from app.routes.builds import router as builds_router
from app.routes.jobs import router as jobs_router


def create_app() -> FastAPI:
    app = FastAPI(title="Compliance API", version="1.0.0")

    @app.get("/healthz")
    async def healthz():
        return {"status": "ok"}

    app.include_router(builds_router, prefix="/api/v1")
    app.include_router(jobs_router, prefix="/api/v1")
    return app


app = create_app()
