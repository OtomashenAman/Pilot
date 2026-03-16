# System Architecture

## Stack
- **Django**: Admin panel, ORM, migrations, user management, rule CRUD
- **FastAPI**: High-performance evaluation API, async rule execution
- **Next.js**: React frontend, SSR dashboard
- **Postgres**: Primary DB (JSONB for DSL, temporal tables for versioning)
- **Celery + Redis**: Background jobs, batch evaluations, audit aggregation

## Service Boundaries

### Django Monolith (Port 8000)
- Authentication/Authorization (JWT issuance)
- Rule management REST API (versioning logic)
- Admin interface for compliance officers
- Database migrations and model definitions
- Celery task orchestration

### FastAPI Service (Port 8001)
- Stateless evaluation engine
- DSL interpreter (Python-based, sandboxed)
- Decision ledger write-ahead logging
- High-concurrency async endpoints
- Direct Postgres read replicas for lookups

## Data Flow
1. Client POST /evaluate → FastAPI
2. FastAPI fetches rule version from Postgres (cached in Redis)
3. DSL interpreter executes against input payload
4. Evidence citations extracted from input metadata
5. Decision + Evidence written to Postgres (transactional)
6. Ledger hash computed and stored (linked to previous hash)
7. Async Celery task archives to cold storage (S3)

## Database Schema
```sql
-- Rules table with temporal versioning
CREATE TABLE rules (
    id UUID PRIMARY KEY,
    slug VARCHAR(255) UNIQUE,
    current_version VARCHAR(20),
    jurisdiction VARCHAR(50),
    created_at TIMESTAMP
);

CREATE TABLE rule_versions (
    id UUID PRIMARY KEY,
    rule_id UUID REFERENCES rules(id),
    version VARCHAR(20),
    dsl JSONB NOT NULL,
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP,
    hash VARCHAR(64) UNIQUE,
    created_by UUID,
    created_at TIMESTAMP
);

-- Decision ledger (append-only)
CREATE TABLE decisions (
    id UUID PRIMARY KEY,
    entity_id VARCHAR(255) NOT NULL,
    rule_version_id UUID REFERENCES rule_versions(id),
    input_hash VARCHAR(64),
    output_decision JSONB NOT NULL,
    ledger_hash VARCHAR(64) NOT NULL,
    previous_hash VARCHAR(64),
    evaluated_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_entity_time (entity_id, evaluated_at)
) PARTITION BY RANGE (evaluated_at);

-- Evidence citations
CREATE TABLE evidence (
    id UUID PRIMARY KEY,
    decision_id UUID REFERENCES decisions(id),
    source_type VARCHAR(50), -- 'api', 'document', 'manual'
    reference_id VARCHAR(255),
    field_path VARCHAR(255),
    data_hash VARCHAR(64),
    confidence FLOAT,
    captured_at TIMESTAMP
);
```

## Docker Setup
- **db**: Postgres 15 with pg_partman for time-series partitioning
- **redis**: Celery broker and FastAPI cache
- **django**: Gunicorn + Django, handles admin and rule management
- **fastapi**: Uvicorn workers, auto-scaled based on evaluation queue depth
- **celery-worker**: Background task processing
- **celery-beat**: Scheduled rule expiration checks
- **frontend**: Next.js standalone output

## Security
- Rule DSL execution in restricted Python sandbox (restrictedpython lib)
- Input validation via Pydantic schemas
- Row-level security (RLS) on decisions table per tenant
- Ledger hashes signed with HMAC for tamper detection