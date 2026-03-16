# System Architecture

## 1. Tech Stack
- **API Layer**: FastAPI (rule evaluation), Django (admin/ORM)
- **Frontend**: Next.js 14 (App Router, Server Components)
- **Database**: PostgreSQL 15 (primary), Read Replicas
- **Queue**: Celery + Redis
- **Storage**: S3 (documents), IPFS (ledger integrity hashes)
- **Infra**: AWS EKS, Terraform, Istio

## 2. Service Architecture

### 2.1 Rule Engine Service (FastAPI)
```
POST /api/v1/evaluate
{
  "context": {...},
  "rule_set": "onboarding_compliance",
  "version": "2.1.0",
  "evidence": [...]
}
```
- Stateless, horizontally scalable
- Pydantic models for type safety
- Deterministic execution environment (frozen Python deps, no network calls)

### 2.2 Ledger Service (Django)
- Append-only DecisionLedger model
- Cryptographic chaining: `current_hash = sha256(prev_hash + data)`
- Partitioned by month (performance)
- Read replica for audit queries

### 2.3 Document Processor (Celery Workers)
- OCR pipeline (Tesseract/AWS Textract)
- Virus scanning (ClamAV)
- Metadata extraction
- Evidence hashing

## 3. Data Model

### 3.1 Rule Versioning
```sql
CREATE TABLE rule_versions (
    id UUID PRIMARY KEY,
    rule_key VARCHAR(100),
    version VARCHAR(20),
    ast_json JSONB,           -- Abstract Syntax Tree
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    created_by VARCHAR(100),
    git_commit_hash VARCHAR(40)
);
```

### 3.2 Decision Ledger
```sql
CREATE TABLE decision_ledger (
    id BIGSERIAL,
    decision_id UUID PRIMARY KEY,
    rule_version_id UUID REFERENCES rule_versions(id),
    input_hash VARCHAR(64),   -- SHA-256 of canonicalized inputs
    output_result JSONB,
    evidence_refs UUID[],
    previous_hash VARCHAR(64),
    current_hash VARCHAR(64),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_previous FOREIGN KEY (previous_hash) REFERENCES decision_ledger(current_hash)
);
```

### 3.3 Evidence Citations
```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY,
    evidence_type VARCHAR(50), -- document, api, calculation
    source_uri VARCHAR(500),
    content_hash VARCHAR(64),
    metadata JSONB,
    created_at TIMESTAMP
);
```

## 4. Determinism Guarantees
1. **Frozen Dependencies**: Docker images with locked pip hashes
2. **No External Calls**: All external data pre-fetched into context
3. **Canonical Serialization**: JSON with sorted keys for input hashing
4. **Time Handling**: Rules use `effective_date` from context, not system time

## 5. Infrastructure

### 5.1 Deployment
- EKS with Karpenter autoscaling
- Separate node pools: web (spot), workers (on-demand), db (reserved)
- Blue/green deployments for rule engine

### 5.2 Security
- mTLS between services (Istio)
- HashiCorp Vault for secrets
- KMS for database encryption
- WAF rules for document upload endpoints

### 5.3 Observability
- OpenTelemetry tracing (rule evaluation spans)
- Prometheus metrics: `rule_evaluations_total`, `decision_ledger_size_bytes`
- Loki for structured logging
- Ledger integrity monitoring (hash verification jobs)

## 6. Scaling Strategy
- Rule evaluations: Cache compiled ASTs in Redis
- Ledger writes: Batch inserts (1000/decision), async replication
- Document processing: SQS dead-letter queues for failures