from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from .db import Base


class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True)
    jurisdiction = Column(String, nullable=False, index=True)
    version_tag = Column(String, nullable=False, index=True)
    logic_jsonb = Column(JSON, nullable=False)
    effective_from = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    sha256_hash = Column(String(64), nullable=False)


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(Integer, primary_key=True)
    citation_type = Column(String, nullable=False)
    source_ref = Column(String, nullable=False)
    excerpt = Column(String, nullable=True)
    checksum = Column(String(64), nullable=False)
    retrieved_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False, index=True)
    input_hash = Column(String(64), nullable=False, index=True)
    outcome_bool = Column(Boolean, nullable=False)
    evidence_ids = Column(JSON, nullable=False, default=list)
    prev_decision_hash = Column(String(64), nullable=True)
    decision_hash = Column(String(64), nullable=False, unique=True)
    signature = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    rule = relationship("Rule")
