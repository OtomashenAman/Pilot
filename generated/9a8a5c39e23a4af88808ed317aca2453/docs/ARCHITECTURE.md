# Subcontractor Onboarding Architecture

## 1. System Components

### 1.1 API Gateway (FastAPI)
- `/onboarding/submit` - Async ingestion
- `/onboarding/{id}/status` - Status polling
- `/decisions/{id}/explain` - Decision reconstruction
- `/rules/deploy` - Versioned rule deployment

### 1.2 Rule Engine Service (Python)
- **Parser**: ANTLR4-based DSL compiler → Python bytecode
- **Executor**: Stateless, deterministic sandbox (restricted builtins only)
- **Cache**: Redis for compiled rule artifacts (version → compiled_fn)
- **Validation**: JSON Schema validation for inputs/outputs

### 1.3 Decision Ledger (Postgres)
- Table: `decisions` (partitioned by month)
- Columns: `id`, `rule_version`, `input_hash`, `output`, `prev_hash`, `signed_digest`
- Constraints: EXCLUDE to prevent hash collisions, immutable via RLS policies
- Index: BRIN on created_at, GIN on evidence_refs

### 1.4 Evidence Store (S3 + Postgres)
- S3: Original documents (encrypted at rest)
- Postgres: `evidence_extractions` - structured data with bounding boxes
- OCR Pipeline: Celery tasks using AWS Textract/Azure Form Recognizer

### 1.5 Async Processing (Celery)
- Queues:
  - `default`: Document processing, notifications
  - `rules`: Rule evaluation (priority based on risk score)
  - `compliance`: Sanctions screening, background checks

## 2. Rule Versioning Strategy

### Schema
```sql
CREATE TABLE rule_versions (
    rule_id UUID,
    version semver NOT NULL,
    dsl JSONB NOT NULL,
    checksum TEXT NOT NULL,
    effective_from TIMESTAMPTZ NOT NULL,
    effective_until TIMESTAMPTZ,
    created_by TEXT,
    PRIMARY KEY (rule_id, version)
);
```

### Deployment Flow
1. Upload DSL → Validation → Checksum calculation
2. Staging evaluation against synthetic test cases
3. Canary: 1% traffic → Monitor error rates
4. Promote: Update `effective_from`, previous version `effective_until`
5. Rollback: Update timestamps, cache invalidation

## 3. Decision Ledger Implementation

### Immutable Logging
```python
# Pseudocode
def append_decision(contractor_id, rule_version, inputs, output, evidence):
    prev_hash = get_last_hash()
    payload = serialize(contractor_id, rule_version, inputs, output, evidence, prev_hash)
    digest = sha256(payload)
    signature = hsm_sign(digest)
    
    db.execute(
        "INSERT INTO decisions (...) VALUES (...) "
        "ON CONFLICT DO NOTHING"  # Idempotency
    )
```

### Reconstruction API
- Accept `decision_id` → Retrieve original rule version → Re-execute with stored inputs
- Verify: Current output matches stored output (determinism check)

## 4. Evidence Citations

### Extraction Pipeline
1. Document upload → S3 → Celery task
2. OCR → Structured JSON → Validation against schemas
3. Store extraction with coordinates (page, bbox)
4. Link to decisions via `evidence_refs` JSONB array

### Citation Format
```json
{
  "evidence_id": "uuid",
  "document_id": "uuid",
  "extraction_id": "uuid",
  "field_path": "tax_id.value",
  "confidence": 0.98,
  "hash": "sha256:abc123...",
  "retrieved_at": "2024-01-15T10:00:00Z"
}
```

## 5. Data Flow

### Happy Path
1. Contractor submits application + documents
2. API persists docs → Triggers Celery workflow
3. Evidence extraction → Stores structured data
4. Rule evaluation (Risk rules → Tax rules → Sanctions)
5. Decision appended to ledger with evidence citations
6. Notification sent with decision explanation

### Audit Flow
1. Auditor requests decision explanation
2. System retrieves: rule_version(v1.2.0) + input_snapshot + evidence_refs
3. Re-executes rule in read-only mode
4. Returns: Original output, execution trace, cited evidence snippets

## 6. Database Schema Highlights

### Partitioning
- `decisions`: Range partitioned by `created_at` (monthly)
- `evidence_extractions`: Hash partitioned by `contractor_id`

### Constraints
- `rule_versions`: EXCLUDE USING gist (rule_id WITH =, effective_period WITH &&)
- `decisions`: Foreign key to specific rule version (enforces referential integrity)

## 7. Deployment

### Infrastructure
- K8s: FastAPI pods (HPA based on CPU/RPS)
- Postgres: Primary + 2 read replicas (synchronous replication for ledger)
- Redis: Cluster mode for rule cache
- Celery: 10 workers default, burst to 50 for batch processing

### Monitoring
- Prometheus: Rule evaluation latency p99, ledger append errors
- Alerting: Mismatch between stored and recomputed decisions (determinism failure)