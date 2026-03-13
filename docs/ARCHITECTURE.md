# Technical Architecture

## System Topology

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│   Next.js   │──────│  API Gateway │──────│   Django    │
│   (Admin)   │      │   (Kong/AWS) │      │  (Core API) │
└─────────────┘      └──────────────┘      └──────┬──────┘
                                                   │
                         ┌─────────────────────────┼─────────────────────────┐
                         │                         │                         │
                   ┌─────▼─────┐          ┌───────▼────────┐       ┌────────▼──────┐
                   │  FastAPI  │          │     Celery     │       │   Postgres    │
                   │  (Rules   │          │   (Workers)    │       │  (Primary)    │
                   │  Engine)  │          └───────┬────────┘       └───────────────┘
                   └─────┬─────┘                  │
                         │              ┌─────────▼──────────┐
                         │              │   Redis (Broker)   │
                         │              └────────────────────┘
                   ┌─────▼─────┐
                   │  S3/MinIO │
                   │ (Evidence │
                   │  Storage) │
                   └───────────┘
```

## Service Boundaries

### Django (Monolith)
- User management, auth, permissions (RBAC)
- Rule CRUD and metadata management
- Decision ledger storage and querying
- Evidence document management
- Webhook management

### FastAPI (Microservice)
- Rule execution engine (deterministic sandbox)
- DSL parser and compiler
- Rule validation and dependency resolution
- High-throughput decision endpoint (/evaluate)
- Stateless, horizontal scaling

### Celery Workers
- Async rule compilation
- Evidence document OCR/indexing
- Ledger archival to cold storage
- Compliance report generation
- Rule version migration jobs

## Data Model

**Rule**
- id, slug, jurisdiction, category
- current_version_id, status (draft/active/deprecated)
- dsl_logic (JSON), compiled_hash
- created_at, updated_at

**RuleVersion**
- id, rule_id, version_number, semantic_version
- dsl_snapshot, compiled_bytecode
- hash_sha256, created_by, changelog
- effective_date, deprecated_date

**Decision**
- id, correlation_id, timestamp
- rule_version_id, input_hash, output_result
- execution_duration_ms, context (anonymized)
- ledger_sequence_number, merkle_hash

**Evidence**
- id, decision_id, citation_type (statute/case_law/contract)
- source_url, document_id, excerpt
- confidence_score, extracted_at

## Determinism Guarantees
1. Frozen rule version at evaluation time
2. Input normalization (sorted keys, UTC timestamps)
3. No external I/O during eval (pre-fetched data only)
4. Fixed-point arithmetic for currency calculations
5. Deterministic JSON serialization

## Security
- Row-level security (RLS) in Postgres for multi-tenant data
- Rule evaluation sandboxed (restricted Python, no network)
- Audit logs streamed to SIEM
- Evidence files encrypted client-side before upload
