# Contractor Classification Rule Engine - PRD

## 1. Context
Latin American workforce management platform requiring deterministic contractor vs. employee classification to ensure labor law compliance across jurisdictions (MX, BR, AR, CL, CO).

## 2. Goals
- Automate contractor classification with 100% deterministic outcomes
- Maintain immutable audit trail for regulatory defense
- Support multi-jurisdiction rule sets with localization
- Enable compliance team self-service rule management

## 3. Functional Requirements

### 3.1 Rule Engine
- Deterministic evaluation: identical inputs produce identical outputs (no ML/AI)
- Rule types: boolean logic, threshold comparisons, date ranges, geographic checks
- Rule composition: AND/OR/NOT nesting with max depth 10
- Evaluation latency: p95 <200ms for rulesets up to 50 rules

### 3.2 Rule Versioning
- Semantic versioning for rule sets (major.minor.patch)
- Immutable rule snapshots post-publish
- Blue/green deployment of rule versions
- Automatic rollback on error thresholds
- Version comparison/diff visualization

### 3.3 Decision Ledger
- Append-only log of all classification decisions
- Fields: contractor_id, rule_version_id, input_hash, output, timestamp, correlation_id
- Tamper-evident hashing (SHA-256 chain)
- Retention: 7 years (regulatory requirement)
- Exportable to PDF/CSV for audits

### 3.4 Evidence Citations
- Every decision output must cite specific input fields as evidence
- Evidence mapping: rule_node_id -> [field_paths]
- Support for document references (contract_id, invoice_id)
- Confidence scoring (0-100) based on data completeness

## 4. Non-Functional Requirements
- Determinism: Same inputs + same rule version = identical output (verified by hash)
- Availability: 99.9% uptime
- Throughput: 1000 evaluations/minute
- Compliance: LGPD, GDPR, local labor codes
- Audit: Complete traceability from output to raw inputs

## 5. User Stories
- Compliance Manager: Draft and publish new rule versions without engineering
- Auditor: Export decision ledger for specific contractor across date range
- Ops: Debug why contractor X was classified as Y on date Z with full evidence
- Legal: Prove classification logic hasn't changed retroactively

## 6. Constraints
- No non-deterministic operations (random, current_time, external APIs) in rules
- All dates must be explicit parameters, not system time
- Rules must be serializable to JSON for versioning
- Celery workers must be stateless