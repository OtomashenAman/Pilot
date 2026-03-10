# EOR/AOR Onboarding Architecture

## 1. System Components

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│  FastAPI    │────▶│  Rule Engine │────▶│ Decision Ledger │
│   Gateway   │     │   Service    │     │   (Postgres)    │
└─────────────┘     └──────────────┘     └─────────────────┘
        │                    │                     │
        ▼                    ▼                     ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Celery    │     │   Postgres   │     │   Object Store  │
│   Workers   │     │   (JSONB)    │     │   (Evidence)    │
└─────────────┘     └──────────────┘     └─────────────────┘
```

## 2. Rule Engine Design

### Deterministic Execution
- **Engine**: Custom JSON Logic evaluator (no external dependencies)
- **Determinism**: Fixed iteration order, no timestamps in logic, no random()
- **Trace**: Every evaluation node returns `{result, path, timestamp, evidence_refs}`

### Versioning Schema
```sql
CREATE TABLE rules (
    rule_id UUID,
    version SEMVER, -- custom type
    effective_from TIMESTAMPTZ,
    effective_to TIMESTAMPTZ,
    logic JSONB NOT NULL, -- deterministic AST
    jurisdiction VARCHAR(10),
    PRIMARY KEY (rule_id, version)
);
```
- Immutable updates only (new version insertion)
- Composite foreign keys in Decision Ledger reference specific versions

## 3. Decision Ledger Implementation

### Cryptographic Chain
```sql
CREATE TABLE decisions (
    decision_id UUID PRIMARY KEY,
    previous_hash VARCHAR(64), -- SHA-256 of previous row
    current_hash VARCHAR(64), -- SHA-256 of this row's content
    rule_id UUID,
    rule_version SEMVER,
    input_payload JSONB,
    output_result JSONB,
    evidence_refs UUID[], -- links to evidence table
    evaluated_at TIMESTAMPTZ DEFAULT NOW(),
    FOREIGN KEY (rule_id, rule_version) REFERENCES rules(rule_id, version)
);
```
- Trigger-based hash generation on insert
- Partitioned by month for performance
- Read replica for audit queries

## 4. Evidence Citations

### Data Model
```sql
CREATE TABLE evidence (
    evidence_id UUID PRIMARY KEY,
    decision_id UUID REFERENCES decisions(decision_id),
    document_hash VARCHAR(64), -- SHA-256 of file content
    storage_path VARCHAR(255), -- S3 URI
    extracted_data JSONB, -- OCR/structured data
    citation_path TEXT, -- e.g., "tax_form.line_3"
    uploaded_at TIMESTAMPTZ
);
```
- Pre-signed URLs for document access (5min expiry)
- Async Celery tasks for: OCR, data extraction, hash verification

## 5. Async Processing (Celery)

### Task Flow
1. **document_processing**: OCR, validation, hash computation → stores evidence
2. **background_check**: Third-party API calls (criminal, credit) → stores results
3. **rule_evaluation**: Triggered after evidence collection → writes to Decision Ledger
4. **audit_export**: Scheduled jobs for compliance report generation

### Queue Separation
- `high`: Rule evaluation (blocking onboarding)
- `normal`: Document processing
- `low`: Audit exports, analytics

## 6. API Design Patterns

### Determinism Guarantees
- `POST /evaluate`: Returns decision_id + full trace
- `GET /decisions/{id}/audit`: Full evidence + rule version + input hash
- `POST /rules/test`: Dry-run against historical data without ledger write

### Concurrency
- Advisory locks on rule evaluation per subcontractor (prevent race conditions)
- Optimistic locking on rule version updates

## 7. Deployment Considerations
- Postgres: Enable `pgcrypto` for hashing, partition decisions table by range
- Celery: Redis backend for result storage, visibility timeout 1hr for long checks
- FastAPI: Stateless, horizontally scalable, JWT auth with RBAC