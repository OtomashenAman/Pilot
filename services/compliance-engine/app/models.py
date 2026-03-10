import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from .db import Base


class RuleSet(Base):
    __tablename__ = "rulesets"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version = Column(String(32), nullable=False)
    jurisdiction = Column(String(64), nullable=False, index=True)
    logic_blob = Column(JSONB, nullable=False)
    logic_hash = Column(String(64), nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DecisionLedger(Base):
    __tablename__ = "decision_ledger"
    sequence = Column(BigInteger, primary_key=True, autoincrement=True)
    contractor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    jurisdiction = Column(String(64), nullable=False, index=True)
    rule_version = Column(String(32), nullable=False, index=True)
    input_hash = Column(String(64), nullable=False)
    output = Column(JSONB, nullable=False)
    output_hash = Column(String(64), nullable=False)
    prev_hash = Column(String(64), nullable=True)
    current_hash = Column(String(64), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contractor_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source_type = Column(String(32), nullable=False)
    storage_uri = Column(String(512), nullable=False)
    extracted_metadata = Column(JSONB, nullable=False, default=dict)
    expiration_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Citation(Base):
    __tablename__ = "citations"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    decision_sequence = Column(BigInteger, ForeignKey("decision_ledger.sequence"), nullable=False, index=True)
    evidence_id = Column(UUID(as_uuid=True), ForeignKey("evidence.id"), nullable=False, index=True)
    field_path = Column(String(256), nullable=False)
    confidence = Column(Float, nullable=False)
