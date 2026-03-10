# Classification Rule Engine - Architecture

## System Components

### FastAPI Services
- **API Layer**: Pydantic models for type safety, dependency injection for auth
- **Rule Engine Core**: Deterministic evaluator using topological sort for DAG execution
- **Ledger Service**: Write-once verification, hash chain validation

### Database (Postgres)
- **rules** table: id, version_id, jurisdiction, logic_jsonb, checksum, effective_dates
- **evaluations** table: id, contractor_id, rule_version_id, inputs_hash, outcome, score, created_at
- **ledger** table: id, evaluation_id, decision_hash, previous_hash, timestamp, merkle_root (partitioned by month)
- **evidence_citations** table: id, evaluation_id, factor_path, weight, source_ref (JSONB), created_at
- **GIN indexes** on logic_jsonb for rule querying; **BRIN indexes** on ledger timestamps

### Celery Workers
- **evaluator-worker**: CPU-bound rule execution (concurrency=4)
- **ledger-worker**: Sequential write to ensure hash chain integrity (concurrency=1, queue=ledger)
- **export-worker**: Compliance report generation, S3 upload

## Rule Engine Implementation

### Deterministic Execution
1. **Input Freezing**: Serialize inputs to canonical JSON (sorted keys) before evaluation
2. **Rule DAG**: Directed acyclic graph of factors; topological sort ensures consistent evaluation order
3. **No Non-determinism**: Random seeds fixed; no current_timestamp usage (use evaluation_request_time)
4. **Scoring**: Weighted sum with fixed-precision Decimal (28, 10) to avoid float errors

### Versioning Strategy
- **SCD Type 2** for rule metadata; **immutable snapshots** for logic_jsonb
- Version promotion: COPY from draft to active with transaction-level consistency
- Historical replay: Store input_snapshots (JSONB) to re-run old evaluations against new rules

### Decision Ledger
- **Hash Chain**: ledger[n].hash = SHA256(ledger[n-1].hash + evaluation_id + outcome + timestamp)
- **Merkle Trees**: Daily aggregation for efficient verification
- **Partitioning**: Monthly partitions; cold storage to S3 after 1 year

### Evidence Citations
- **Automated Capture**: Rule engine emits (factor_id, value, weight) tuples during execution
- **Source Tracking**: Foreign key references stored as JSONB to handle polymorphic sources (contracts, timesheets, invoices)
- **Tamper Evidence**: Citation hashes included in evaluation hash

## Data Flow

1. **Ingestion**: Contractor data → Postgres (normalized tables)
2. **Evaluation Trigger**: API call or Celery beat schedule
3. **Pre-computation**: Celery task fetches all required evidence into Redis cache (5min TTL)
4. **Rule Execution**: Deterministic engine processes DAG, emits score + citations
5. **Ledger Write**: Async task writes to ledger table with hash chaining (serial queue)
6. **Response**: Evaluation ID + outcome returned; citations available via GET

## Deployment Considerations
- **Migrations**: Alembic; rule version changes require manual promotion API call
- **Backup**: Ledger table requires point-in-time recovery; hash chain verification on restore
- **Scaling**: Read replicas for evaluation history; single writer for ledger
- **Monitoring**: Prometheus metrics on rule evaluation latency, hash chain integrity checks
