# EOR/AOR Onboarding Architecture

## 1. Component Diagram

```
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   FastAPI    │──────▶  Rule Engine │──────▶  PostgreSQL │
│   Gateway    │      │  (Python)    │      │   (Ledger)   │
└──────────────┘      └──────────────┘      └──────────────┘
        │                      │                      │
        ▼                      ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   Celery     │      │  Evidence    │      │   Rule       │
│   Workers    │      │   Store      │      │   Registry   │
└──────────────┘      │  (S3/MinIO)  │      │  (Postgres)  │
                      └──────────────┘      └──────────────┘
```

## 2. Rule Engine Design

### 2.1 Deterministic Execution
- **AST-based DSL**: Rules compiled to immutable Abstract Syntax Trees (nodes: AND, OR, COMPARE, LOOKUP)
- **Frozen Context**: EvaluationContext is Pydantic model with `frozen=True`, hashable
- **No Side Effects**: Rule engine is pure function: `evaluate(context: FrozenContext, ruleset: RuleVersion) -> DecisionResult`
- **Seeding**: Any randomness (if needed for sampling) uses deterministic seed from context hash

### 2.2 Versioning Implementation
- **RuleVersion Table**: `id`, `semantic_version`, `jurisdiction`, `ast_json`, `effective_from`, `effective_to`, `hash`
- **Immutable Storage**: Published rules marked `is_immutable=True`; updates create new versions
- **Migration Service**: Celery task re-evaluates in-flight applications against new rules, creates new Decision entries

## 3. Decision Ledger

### 3.1 Append-Only Schema
```sql
CREATE TABLE decisions (
    id UUID PRIMARY KEY,
    contractor_id UUID NOT NULL,
    rule_version_id UUID NOT NULL,
    input_hash VARCHAR(64) NOT NULL,  -- SHA256 of canonicalized inputs
    output JSONB NOT NULL,
    evidence_refs JSONB NOT NULL,     -- ['doc_123', 'api_response_456']
    previous_hash VARCHAR(64),        -- Chain hash for tamper evidence
    ledger_hash VARCHAR(64) NOT NULL, -- SHA256(prev_hash + current_row_data)
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_decisions_contractor ON decisions(contractor_id, created_at DESC);
```

### 3.2 Verification
- Background Celery task daily verifies hash chain integrity
- Exposes `/audit/verify/{decision_id}` endpoint for cryptographic proof

## 4. Evidence Citations

### 4.1 Evidence Ingestion
- **Evidence Service**: Handles uploads to S3 with SHA-256 checksums stored in Postgres
- **Citation Format**: `evidence://{type}/{id}/{hash_fragment}` (e.g., `evidence://tax_form/W9_123/abc123`)
- **Binding**: Evidence IDs injected into EvaluationContext before rule execution

### 4.2 Integrity
- Content-addressed storage: S3 key includes hash prefix `evidence/{hash_prefix}/{uuid}`
- Async Celery job validates evidence not expired before decision finalization

## 5. API Design (FastAPI)

### Key Endpoints
- `POST /evaluate`: Synchronous rule evaluation (returns Decision with ledger_id)
- `POST /evidence`: Async evidence ingestion (returns evidence_id)
- `GET /decisions/{id}/lineage`: Full replay data (inputs, rules version, evidence)
- `GET /rules/{jurisdiction}/versions`: List available rule versions
- `POST /rules/{id}/publish`: Immutable publication (admin only)

### Async Processing (Celery)
- `tasks.evaluate_async`: For complex evaluations requiring external API calls
- `tasks.generate_audit_report`: Compile decision + evidence package for legal
- `tasks.rule_migration`: Re-evaluate cohorts when rules update

## 6. Determinism Guarantees

### Input Freezing
- All inputs canonicalized to sorted JSON before hashing
- Time-sensitive rules use `evaluation_timestamp` from context, not `now()`
- External data pre-fetched into Evidence store, referenced by hash

### Testing
- Regression test suite: 10k historical evaluations must produce identical outputs when replayed
- Property-based testing (Hypothesis) to ensure pure functions

## 7. Deployment
- **Database**: PostgreSQL with `pgcrypto` for hashing, read replicas for audit queries
- **Caching**: Redis for rule ASTs (immutable, long TTL), not for decisions
- **Workers**: Celery with `task_always_eager=False`, acks_late=True for durability
