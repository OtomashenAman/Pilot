# Technical Architecture

## System Components

### API Layer (FastAPI + Python 3.11+)
- AsyncIO endpoints with Pydantic v2 validation
- API versioning: /v1/rules, /v1/evaluate, /v1/ledger
- JWT + OAuth2 with fine-grained RBAC (Rule Admin, Auditor, Operator)
- Request correlation IDs for distributed tracing

### Deterministic Rule Engine
- Custom JSON-Logic implementation with frozen Python dictionaries
- Rules cached in Redis (read-only) to ensure consistency across workers
- Determinism enforced via: no random(), no datetime.now(), no external I/O
- Celery tasks execute rules in sandboxed subprocesses with resource limits

### Data Layer (PostgreSQL 15+)
**Schema Design:**
- `rule_sets`: id, version, jurisdiction_code, logic_jsonb, effective_from, effective_to, content_hash, created_by
- `decision_ledger`: id, subcontractor_id, rule_version, input_payload_hash, output_decision, evidence_refs[], ledger_hash, previous_hash, created_at (partitioned by month)
- `evidence_store`: id, decision_id, s3_uri, sha256_checksum, citation_paths[], retention_until, encryption_key_id
- `subcontractors`: id, profile_encrypted, jurisdiction, onboarding_status, foreign keys to latest decision

**Constraints:**
- Ledger table: INSERT only, no UPDATE/DELETE (enforced via RLS policies)
- Foreign key constraints ensure every decision references valid rule version
- JSONB GIN indexes on evidence citation paths for fast audit queries

### Async Processing (Celery + Redis)
- **high_priority**: Real-time rule evaluation, document virus scanning (ClamAV)
- **default**: Evidence OCR extraction, hash verification
- **low_priority**: Ledger compaction, compliance report generation
- Dead Letter Queues (DLQ) with 3-day retention for failed deterministic evaluations

### Evidence Management
- S3 with Object Lock (Compliance Mode) for immutable storage
- Pre-signed URLs for upload (15-minute expiry)
- Client-side encryption (AES-256-GCM) before transit
- Citation service maps extracted data points to specific document regions

### Security & Compliance
- Row-Level Security (RLS) enforces tenant isolation in Postgres
- Ledger integrity checks via background Celery beat job (hash chain verification)
- Automated backups: Daily snapshots (7 days), Weekly (4 weeks), Monthly (7 years)
- Audit logging: All rule version changes logged to separate immutable table

## Performance Targets
- Rule evaluation: p99 < 200ms
- Ledger write throughput: >1000 decisions/second
- Evidence retrieval: p99 < 500ms for documents <10MB