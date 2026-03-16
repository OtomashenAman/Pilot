# Compliance Engine PRD

## Overview
Deterministic compliance evaluation platform ensuring regulatory adherence through versioned rules, immutable decision ledgers, and evidence-backed citations.

## Core Requirements

### 1. Deterministic Rule Engine
- JSON-based DSL for rule definitions (conditions, operators, thresholds)
- Idempotent evaluations: same inputs always produce same outputs
- Support for boolean logic, arithmetic comparisons, date ranges, and regex patterns
- Sandbox execution environment with timeout guards
- Rule dependency graph resolution (DAG validation)

### 2. Rule Versioning
- Immutable rule storage (never update, only supersede)
- Semantic versioning (v1.0.0 → v1.1.0)
- Effective date ranges with automatic activation/expiration
- Branching support for jurisdiction-specific variants
- Diff visualization between versions

### 3. Decision Ledger
- Append-only log of all evaluation results
- Tamper-evident hashing (SHA-256 chain linking)
- Queryable by entity_id, rule_version, timestamp, outcome
- Exportable audit trails (CSV/JSON)
- Retention policies per jurisdiction

### 4. Evidence Citations
- Auto-capture source data references (field paths, document IDs)
- Confidence scoring per evidence item
- Support for external document URLs and hash verification
- Evidence lineage tracking (upstream data sources)
- Citation validity checking (stale data detection)

## Data Models
- **Rule**: id, version, dsl_definition, effective_from, effective_to, jurisdiction, hash
- **Evaluation**: id, entity_id, rule_id, version, input_payload, output_decision, evidence_map, ledger_hash, timestamp
- **Evidence**: id, evaluation_id, source_type, reference_id, data_hash, confidence_score, captured_at

## API Requirements
- POST /evaluate (sync, <200ms p99)
- POST /evaluate/batch (async via Celery)
- GET /rules/:id/versions
- GET /ledger/:entity_id
- POST /rules/:id/versions (create new version)

## Non-Functional
- 99.9% uptime SLA
- Evaluation latency <100ms (p95)
- Support 10M+ ledger entries with time-series partitioning
- GDPR/CCPA data deletion support (anonymization, not hard delete)