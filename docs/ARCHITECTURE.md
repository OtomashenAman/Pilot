# Compliance Engine Architecture

## System Components

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Next.js UI    │────▶│   FastAPI GW     │────▶│  Django Admin   │
│  (Rule Editor)  │     │  (Rule Executor) │     │ (Rule Mgmt)     │
└─────────────────┘     └────────┬─────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
           ┌──────────────┐ ┌────────┐ ┌──────────────┐
           │   Celery     │ │Postgres│ │   S3/MinIO   │
           │   Workers    │ │        │ │  (Evidence)  │
           └──────────────┘ └────────┘ └──────────────┘
```

## Data Model

### Rule Engine (Django)
```python
class RuleVersion(models.Model):
    rule_id = models.UUIDField()
    version = models.CharField(max_length=20)  # semver
    definition = models.JSONField()  # AST representation
    bytecode = models.BinaryField()  # compiled
    hash = models.CharField(max_length=64)  # sha256
    status = models.CharField(choices=["draft","published","deprecated"])
    created_at = models.DateTimeField(auto_now_add=True)
    
class RuleSet(models.Model):
    name = models.CharField()
    rules = models.ManyToManyField(RuleVersion)
    version = models.CharField()
```

### Decision Ledger (PostgreSQL - partitioned by month)
```sql
CREATE TABLE decision_ledger (
    id UUID PRIMARY KEY,
    rule_version_id UUID REFERENCES rule_versions(id),
    input_hash VARCHAR(64),  -- deterministic input fingerprint
    output JSONB,
    evidence_refs UUID[],    -- links to evidence_store
    merkle_root VARCHAR(64),
    previous_hash VARCHAR(64),  -- chain linking
    signature BYTEA,         -- HSM signed
    created_at TIMESTAMPTZ,
    tenant_id UUID
) PARTITION BY RANGE (created_at);
```

### Evidence Store (S3 + Metadata in PG)
```python
class Evidence(models.Model):
    ledger_entry = models.ForeignKey(DecisionLedger)
    source_type = models.CharField()  # 'document','api','manual'
    storage_path = models.CharField()  # s3://bucket/key
    content_hash = models.CharField(max_length=64)
    metadata = models.JSONField()
    retention_until = models.DateTimeField()
```

## Deterministic Execution

### FastAPI Rule Executor
```python
@router.post("/evaluate")
async def evaluate_rule(
    rule_id: UUID,
    context: dict,
    evidence: list[EvidenceRef]
):
    # 1. Load compiled bytecode from cache (Redis)
    rule = await get_rule_bytecode(rule_id)
    
    # 2. Execute in sandboxed environment
    result = await execute_deterministic(rule, context)
    
    # 3. Write to ledger (async via Celery)
    ledger_id = await commit_to_ledger(
        rule_id=rule_id,
        input=context,
        output=result,
        evidence=evidence
    )
    
    return {"decision": result, "ledger_id": ledger_id}
```

### Sandboxing
- Restricted Python (RestrictedPython) or WASM runtime
- No I/O, no imports, pure functions only
- Timeout: 100ms per rule execution

## Versioning Strategy

1. **Draft Phase**: Rules editable in Django Admin
2. **Publish**: Immutable snapshot created, bytecode compiled
3. **Execution**: Only published versions executable
4. **Deprecation**: Soft delete, existing evaluations continue
5. **Migration**: Automated data migration scripts between versions

## Ledger Integrity

```
Block N:   [Data] + [Hash(N-1)] -> Hash(N) -> HSM Sign
Block N+1: [Data] + [Hash(N)]   -> Hash(N+1) -> HSM Sign
```

- Daily Merkle tree root published to external transparency log
- Tamper detection service runs hourly

## Scaling

- **Read Replicas**: Decision queries go to replicas
- **Sharding**: Partition ledger by tenant_id
- **Caching**: Rule bytecode cached in Redis (LRU)
- **Async**: Bulk evaluations via Celery + RabbitMQ
