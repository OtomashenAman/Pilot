from django.db import models
from sqlalchemy import String, Integer, DateTime, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

class BuildJob(Base):
    __tablename__ = "build_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32), index=True, default="created")  # created|prd_done|code_done|failed
    prompt: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Artifacts produced by Kimi
    prd_pack: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Codex outputs
    codex_plan: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    codex_diffs: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Errors
    error: Mapped[str | None] = mapped_column(Text, nullable=True)