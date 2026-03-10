# Architecture: Subcontractor Onboarding

## 1. System Components

### Rule Engine Service (FastAPI)
- **DSL Parser**: JSON-based rule definitions → AST
- **Execution Engine**: Deterministic sandbox (restricted Python/Lua)
- **Version Control**: Git-like storage for rules in PostgreSQL JSONB
- **Cache**: Redis for compiled rule ASTs

### Decision Ledger
- **Write Model**: PostgreSQL (partitioned by date)
- **Immutable Store**: S3/GCS with object lock (WORM)
- **Hash Chain**: Each decision includes SHA256(previous_decision_hash + payload)
- **API**: `/decisions/{id}` returns full chain of evidence

### Evidence Service
- **Document Store**: S3 with checksums (SHA256)
- **Metadata**: PostgreSQL (doc_id, decision_id, citation_type, retention_date)
- **Verification**: Async Celery tasks validate document authenticity

## 2. Data Model

```sql
-- Rule Versions
CREATE TABLE rule_sets (
    id UUID PRIMARY KEY,
    version VARCHAR(20) NOT NULL,
    hash VARCHAR(64) UNIQUE, -- content hash
    rules JSONB NOT NULL,
    effective_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Decision Ledger
CREATE TABLE decisions (
    id UUID PRIMARY KEY,
    application_id UUID,
    rule_set_version VARCHAR(20),
    rule_set_hash VARCHAR(64),
    input_hash VARCHAR(64), -- hash of normalized inputs
    result JSONB NOT NULL,
    previous_decision_hash VARCHAR(64),
    decision_hash VARCHAR(64), -- integrity check
    created_at TIMESTAMP DEFAULT NOW()
);

-- Evidence Citations
CREATE TABLE evidence (
    id UUID PRIMARY KEY,
    decision_id UUID REFERENCES decisions(id),
    document_id VARCHAR(255),
    document_hash VARCHAR(64),
    citation_type VARCHAR(50), -- 'passport', 'tax_record', 'api_response'
    storage_path VARCHAR(500),
    retention_until DATE
);
```

## 3. Async Processing (Celery)
- **verify_document**: OCR, forgery detection, checksum validation
- **external_api_check**: Tax status, sanctions lists, background checks
- **ledger_sync**: Batch write to cold storage (S3 WORM)
- **evidence_cleanup**: GDPR deletion post-retention

## 4. API Design

```python
# Deterministic evaluation endpoint
POST /v1/evaluate
{
  "application_id": "uuid",
  "rule_set_version": "v1.2.0", # optional, defaults to active
  "context": {...} # normalized inputs
}

Response:
{
  "decision_id": "uuid",
  "outcome": "approved|denied|manual_review",
  "rule_version": "v1.2.0",
  "citations": ["evidence_id_1", ...],
  "explanation": "Rule 3.2 failed: tax_residency_mismatch"
}
```

## 5. Determinism Guarantees
- Input normalization (sorted JSON keys, UTC timestamps)
- Fixed-point arithmetic for financial calculations
- No external calls during rule execution (pre-fetched context)
- Seedable random (if needed for sampling) stored in context
- Execution timeout: 5s max

## 6. Deployment
- FastAPI + Uvicorn (async workers)
- PostgreSQL 15+ (JSONB indexing)
- Celery workers (prefork for CPU-bound OCR, gevent for I/O)
- S3 Object Lock for compliance storage

## 7. Security
- mTLS between services
- Rule execution sandboxed (seccomp-bpf)
- Decision ledger write-once (DB user with INSERT only)
- Evidence encryption at rest (AES-256)