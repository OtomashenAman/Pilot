# EOR/AOR Onboarding Architecture

## 1. System Overview
Async-first architecture separating synchronous rule evaluation from long-running compliance checks.

## 2. Component Diagram
```
[Client] → FastAPI (Sync Rules) → PostgreSQL (Ledger/State)
              ↓
          Celery Workers → Background Checks (KYC/Tax)
              ↓
        Document Store (S3/MinIO) ← Evidence
```

## 3. Rule Engine Design
### 3.1 Deterministic Execution
- Pure functions only: no DB queries, no RNG, no timestamps during eval
- Input normalization: canonical JSON ordering, decimal quantization
- Docker sandbox for Python rule execution (restricted imports)
- Output signature: `SHA256(input_json + rule_logic + version)`

### 3.2 Versioning Strategy
- Git-backed rule storage with PostgreSQL JSONB cache
- RuleSet table: `id, version, effective_date, logic_hash, created_at`
- Migration path: blue/green deployment with traffic cutover
- Rollback capability: immediate revert to previous version via `active` flag

## 4. Decision Ledger
### 4.1 Schema
```sql
CREATE TABLE decision_ledger (
    sequence BIGSERIAL PRIMARY KEY,
    contractor_id UUID NOT NULL,
    rule_version VARCHAR NOT NULL,
    input_hash VARCHAR(64) NOT NULL,
    output JSONB NOT NULL,
    prev_hash VARCHAR(64),
    current_hash VARCHAR(64) GENERATED ALWAYS AS (SHA256(...)),
    created_at TIMESTAMP DEFAULT NOW()
);
```
### 4.2 Integrity
- Hash chain links decisions: `current_hash = SHA256(prev_hash + content)`
- Async replication to cold storage (compliance vault)
- Partitioning by created_date (monthly)

## 5. Evidence Citations
- Evidence stored with `source_type` (upload, api, derived)
- Citation table links specific JSON paths in decisions to evidence UUIDs
- Extraction pipeline (Celery): OCR for docs, structured extraction for APIs
- Confidence scores via ML models (document authenticity) or API metadata

## 6. Database Schema (PostgreSQL)
- **rules**: Versioned rule logic with GIN index on jurisdiction JSONB
- **contractors**: Core entity with status enum (pending, approved, rejected, suspended)
- **evidence**: Foreign key to contractors, metadata JSONB, TTL for auto-expiry
- **citations**: Composite index on (decision_sequence, evidence_id)
- **ledger**: Append-only, no updates/deletes allowed (DB-level policy)

## 7. Async Processing (Celery)
### 7.1 Task Flow
1. `onboard_initiate` → Create contractor record
2. `collect_evidence` → Fetch external data (background check APIs)
3. `evaluate_rules` → Deterministic engine execution
4. `record_decision` → Write to ledger + citations
5. `notify_stakeholders` → Webhooks/email

### 7.2 Reliability
- Task idempotency via contractor_id + task_name deduplication
- Dead letter queue for failed evidence collection
- Retry with exponential backoff (API rate limits)

## 8. API Implementation (FastAPI)
- Pydantic models for strict input validation (determinism prerequisite)
- Dependency injection for rule engine versioning
- Asyncpg for high-concurrency ledger writes
- Middleware for request hashing (evidence for API call itself)

## 9. Security & Compliance
- Field-level encryption for PII in PostgreSQL (pgsodium)
- Evidence immutability: WORM storage (Write Once Read Many)
- Audit endpoints: Read-only replicas for ledger queries
- GDPR: Evidence hard delete after retention (ledger keeps hash only)
