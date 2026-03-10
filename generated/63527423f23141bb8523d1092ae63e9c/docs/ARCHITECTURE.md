# Classification Rule Engine Architecture

## 1. System Components

### 1.1 API Layer (FastAPI)
- **Endpoints**:
  - POST /evaluate - Synchronous classification
  - POST /evaluate/async - Celery-backed async evaluation
  - GET /rules/versions - List rule versions
  - POST /rules/versions - Create new version (draft)
  - POST /rules/publish - Publish version (immutable)
  - GET /ledger/{contractor_id} - Decision history
  - GET /evidence/{decision_id} - Evidence citations

### 1.2 Rule Engine Core (Python)
- **Parser**: JSON rule AST -> executable graph
- **Evaluator**: Depth-first traversal with memoization
- **Determinism Guard**: Pre-execution validation (no banned ops)
- **Hash Service**: SHA-256 of (inputs + rule_version) for caching

### 1.3 Versioning System
- **Storage**: Postgres JSONB (rulesets) + S3 (artifacts)
- **State Machine**: Draft -> Published -> Deprecated -> Archived
- **Migration**: Blue/green routing via version tags
- **Schema**: rule_sets(id, version, jurisdiction, rules_json, hash, status, created_at)

### 1.4 Decision Ledger
- **Storage**: Postgres partitioned by month
- **Schema**: decisions(id, contractor_id, rule_version_id, inputs_hash, result, confidence, evidence_refs, created_at)
- **Integrity**: Previous hash stored for chain verification
- **Async Write**: Celery task for ledger append (fire-and-forget)

### 1.5 Evidence Collector
- **Citations**: Maps rule nodes to input field paths
- **Documents**: Links to contract/invoice tables via foreign keys
- **Aggregation**: Real-time evidence bundle generation

## 2. Data Models

```python
# Rule Set (Versioned)
class RuleSet:
    id: UUID
    version: str  # semver
    jurisdiction: str  # 'MX', 'BR', etc.
    rules: List[RuleNode]  # JSONB
    hash: str  # content hash
    status: Enum[DRAFT, PUBLISHED, DEPRECATED]
    effective_date: date
    created_by: user_id

# Decision (Ledger)
class Decision:
    id: UUID
    contractor_id: UUID
    rule_version_id: UUID
    input_snapshot: JSONB  # frozen input state
    input_hash: str
    output: ClassificationResult
    confidence_score: int
    evidence_citations: List[EvidenceRef]
    previous_decision_hash: Optional[str]  # chain
    created_at: timestamp

# Evidence Reference
class EvidenceRef:
    rule_node_id: str
    field_path: str
    value: Any
    document_id: Optional[UUID]
    confidence: int  # 0-100 data quality
```

## 3. Processing Flow

### 3.1 Synchronous Evaluation
1. Client POST /evaluate with contractor_id + context
2. Fetch active RuleSet for jurisdiction
3. Validate determinism (no forbidden ops)
4. Execute rule graph -> ClassificationResult
5. Collect evidence citations during traversal
6. Calculate confidence score
7. Return result + evidence + decision_id
8. Async Celery task: write to ledger

### 3.2 Async Evaluation (High Volume)
1. Client POST /evaluate/async
2. Celery task queued with priority routing
3. Worker processes: same flow as sync
4. Webhook callback on completion
5. Ledger write within same transaction

### 3.3 Rule Publishing
1. Compliance uploads new rule JSON
2. Validation: schema, determinism, cycles
3. Hash calculation
4. Insert as DRAFT
5. Review workflow -> PUBLISHED
6. Cache invalidation (Redis)
7. Previous version marked DEPRECATED (grace period)

## 4. Determinism Guarantees

### 4.1 Forbidden Operations
- datetime.now() (use explicit effective_date param)
- random(), uuid4() (use deterministic IDs)
- External API calls (pre-fetch to input_snapshot)
- Database queries during evaluation (all data in input_snapshot)

### 4.2 Validation
- Static analysis of rule AST pre-publish
- Sandbox execution with mock data
- Hash verification: re-run historical decisions, verify match

## 5. Infrastructure

### 5.1 Postgres Schema
- **Tables**: rule_sets, decisions, evidence_refs, contractors, input_snapshots
- **Indexes**: decisions(contractor_id, created_at), rule_sets(jurisdiction, status)
- **Partitioning**: decisions by month (retention 7 years)

### 5.2 Celery Configuration
- **Queues**: classification.high, classification.low, ledger.write
- **Retries**: 3 attempts with exponential backoff
- **DLQ**: Dead letter queue for failed ledger writes (critical)
- **Workers**: 4 pods min, HPA based on queue depth

### 5.3 Caching (Redis)
- Rule sets: Cache published versions (TTL 1h)
- Input hashes: Cache evaluation results (TTL 24h)
- Deterministic: same inputs = same output, safe to cache

## 6. Audit & Compliance

### 6.1 Ledger Integrity
- Daily batch job: Verify hash chain continuity
- Monthly export: Compressed decision logs to cold storage
- Tamper detection: Alert if hash mismatch detected

### 6.2 Evidence Requirements
- Every boolean result must have >=1 supporting evidence
- Geographic rules: cite address verification source
- Financial rules: cite invoice/payment document IDs
- Time-based rules: cite contract dates with source

## 7. Deployment Strategy

### 7.1 Rule Versions
- Blue/Green: New version published alongside old
- Canary: 5% traffic to new version, monitor error rates
- Rollback: Instant revert to previous version via status change

### 7.2 Database Migrations
- Rule schema changes: Additive only (no rewrites)
- Ledger: Append-only, never update historical decisions
- Evidence: Separate table to avoid decision bloat