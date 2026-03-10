# Subcontractor Onboarding PRD (EOR/AOR)

## 1. Context
EOR/AOR platforms require compliant, auditable onboarding of subcontractors across jurisdictions. System must enforce deterministic eligibility rules with immutable audit trails.

## 2. Core Requirements

### 2.1 Deterministic Rule Engine
- DSL for compliance rules (tax residency, visa status, background checks)
- Rule execution must be pure functions: same inputs = same outputs
- Support boolean logic, date comparisons, entity lookups
- Execution context isolation per evaluation

### 2.2 Rule Versioning
- Semantic versioning for rule sets (v1.0.0, v1.1.0)
- Immutable rule snapshots (content-addressable storage)
- A/B testing capability for rule rollouts
- Rollback to previous versions within 24h

### 2.3 Decision Ledger
- Append-only log of all eligibility decisions
- Cryptographic chaining (hash of previous decision)
- Tamper-evident storage
- Decision ID, timestamp, rule version, inputs hash, output, confidence score

### 2.4 Evidence Citations
- Every decision must cite supporting evidence (doc IDs, API responses)
- Evidence integrity verification (checksums)
- Retention policies per jurisdiction (7 years default)
- Evidence binding to specific decision IDs

## 3. User Flows
1. Subcontractor submits application
2. System executes rule set against profile + documents
3. Async verification via Celery tasks (background checks, API validations)
4. Decision written to ledger with evidence citations
5. Human reviewer override capability (with mandatory justification)

## 4. Compliance
- GDPR/CCPA data handling
- SOC2 Type II audit requirements
- Immutable audit trails (WORM storage)
- Right to explanation (decision reasoning)

## 5. Success Metrics
- Decision latency <500ms (sync rules)
- 100% audit trail coverage
- Zero rule versioning conflicts
- Evidence retrieval <200ms