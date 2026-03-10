import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from .db import Base


class RuleSet(Base):
    __tablename__ = "rule_sets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    semantic_version = Column(String(32), nullable=False)
    jurisdiction = Column(String(16), nullable=False, index=True)
    ast_json = Column(JSONB, nullable=False)
    effective_from = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    hash = Column(String(64), nullable=False)
    is_immutable = Column(Boolean, nullable=False, default=True)


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = Column(String(64), nullable=False, index=True)
    rule_version_id = Column(UUID(as_uuid=True), ForeignKey("rule_sets.id"), nullable=False)
    input_hash = Column(String(64), nullable=False)
    output = Column(JSONB, nullable=False)
    evidence_refs = Column(JSONB, nullable=False, default=list)
    previous_hash = Column(String(64), nullable=True)
    ledger_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
