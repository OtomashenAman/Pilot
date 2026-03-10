# Contractor Classification Rule Engine - PRD

## Objective
Deterministic classification system for contractor vs. employee status across Latam jurisdictions (BR, MX, AR, CL, CO, PE) to mitigate misclassification risk and ensure labor law compliance.

## Functional Requirements

### 1. Deterministic Rule Engine
- Idempotent evaluations: identical inputs produce identical outputs
- Rule execution order: factor weights → threshold comparison → classification
- Supported logic: boolean logic, weighted scoring, range checks, temporal rules
- Determinism enforcement: no external API calls during evaluation; all data pre-fetched

### 2. Multi-Jurisdiction Support
- Country-specific rule packs (CLT Brazil, LFT Mexico, etc.)
- Jurisdiction hierarchy: Federal → State/Provincial → Industry-specific
- Configurable factor weights per jurisdiction

### 3. Rule Versioning
- Immutable rule definitions; updates create new versions
- Version metadata: effective_date, deprecated_date, change_reason, author
- A/B testing support: parallel rule versions with traffic allocation
- Rollback capability: re-evaluate historical cases against previous rule versions

### 4. Decision Ledger
- Append-only audit log of every classification decision
- Immutable records: cryptographic hash chaining (previous_hash stored per record)
- Retention: 7 years minimum (Latam labor audit requirements)
- Fields: evaluation_id, contractor_id, rule_version_id, outcome, confidence_score, timestamp, hash

### 5. Evidence Citations
- Traceable reasoning: every decision cites specific evidence factors
- Evidence types: contract_clauses, payment_history, schedule_logs, tool_provided_flags
- Citation structure: factor_id, weight_applied, source_data_ref, excerpt
- Exportable justification reports for legal defense

## Data Model

### Core Entities
- **ContractorProfile**: id, jurisdiction_code, engagement_history, attributes_json
- **RuleSet**: id, jurisdiction_code, version_tag, effective_date, logic_json (DAG)
- **Evaluation**: id, contractor_id, rule_version_id, input_snapshot, outcome (EMPLOYEE|CONTRACTOR|REVIEW), score
- **LedgerEntry**: id, evaluation_id, timestamp, decision_hash, previous_hash
- **EvidenceCitation**: id, evaluation_id, factor_code, weight, source_table, source_id, value_at_time

## API Surface

### Synchronous
- `POST /evaluate` - Run classification (idempotent)
- `GET /evaluations/{id}` - Retrieve decision with evidence citations
- `GET /rules/{jurisdiction}/versions` - List rule versions

### Asynchronous (Celery)
- `POST /batch-evaluate` - Bulk classification jobs
- `POST /rules/{id}/promote` - Deploy new rule version with canary
- `POST /ledger/export` - Compliance audit package generation

## Compliance & Security
- LGPD/GDPR: PII encryption at rest, data retention policies
- Tamper-evident ledger: SHA-256 hashing with periodic notarization
- Access control: RBAC for rule authoring vs. evaluation execution
- Audit: All rule changes require dual approval in ledger

## Success Metrics
- Classification accuracy vs. legal review: >95% agreement
- Decision latency: p99 <200ms (sync), throughput >1000 evals/min (async)
- Audit query latency: <5s for 7-year history
