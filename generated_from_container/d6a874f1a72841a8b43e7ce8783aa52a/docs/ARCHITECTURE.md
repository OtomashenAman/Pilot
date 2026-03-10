# Architecture

## Components
- **API Layer**: FastAPI + Pydantic v2 for sync endpoints; JWT + mTLS auth
- **Rule Engine**: Python DSL interpreter (JSON logic: AND/OR/NOT/comparisons); pure functions only
- **Version Store**: Postgres JSONB with git-like DAG; rules immutable (insert-only)
- **Ledger**: Postgres append-only table with hash chain (prev_hash + data → current_hash)
- **Queue**: Celery + Redis for evidence collection and batch processing
- **Evidence Service**: Structured citations linking legal corpus IDs and policy versions

## Data Model
**rules** (id, jurisdiction, version_tag, logic_jsonb, effective_from, sha256_hash)
**decisions** (id, rule_id, input_hash, outcome_bool, evidence_ids[], timestamp, prev_decision_hash, signature)
**evidence** (id, citation_type [statute|policy|data], source_ref, excerpt, retrieved_at, checksum)

## Execution Flow
1. Client POSTs workforce entity (attributes + jurisdiction)
2. Engine loads active rule version (immutable snapshot)
3. Deterministic evaluation against entity (no DB calls, no RNG)
4. Evidence service maps triggered clauses to citations
5. Ledger writes decision with cryptographic chaining
6. Returns {decision_id, compliance_status, evidence_links}

## Determinism Guarantees
- Frozen dataclasses for inputs
- No network calls during eval
- Reproducible hashing (canonical JSON)