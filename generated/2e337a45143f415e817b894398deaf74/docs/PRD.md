# EOR/AOR Subcontractor Onboarding Platform - PRD

## 1. Overview
Platform to automate compliance-heavy onboarding for subcontractors across jurisdictions, ensuring deterministic eligibility decisions with full audit trails for EOR/AOR liability protection.

## 2. Core Requirements

### 2.1 Deterministic Rule Engine
- DSL-based rule definitions (JSON/YAML) evaluating contractor classification, tax residency, and compliance eligibility
- Guaranteed deterministic execution: identical inputs + rule version = identical output
- Support for jurisdiction-specific rule sets (US 1099 vs UK IR35 vs EU AOR)
- Sub-100ms evaluation latency for real-time onboarding flows

### 2.2 Rule Versioning
- Immutable rule snapshots with semantic versioning (v1.0.0, v1.1.0)
- Git-like branching for rule staging (prod/staging/draft)
- Automatic migration paths for in-flight applications when rules update
- Rollback capability to previous versions within 24h

### 2.3 Decision Ledger
- Append-only ledger recording every rule evaluation (input hash, rule version, output, timestamp)
- Tamper-evident logging (SHA-256 chained hashes)
- Queryable audit trail by contractor ID, jurisdiction, date range
- 7-year retention with WORM (Write Once Read Many) storage

### 2.4 Evidence Citations
- Structured evidence linking (document UUIDs, API response hashes, third-party verification IDs)
- Auto-generated citation maps showing which evidence supported which decision nodes
- Evidence integrity verification (checksums on ingestion)
- Support for document expiration and re-verification triggers

## 3. User Flows

### Primary: Contractor Onboarding
1. Identity verification (KYC) → Evidence captured
2. Jurisdiction detection → Rule set selected
3. Classification questionnaire → Rule engine evaluation
4. Compliance check (background/tax) → Celery async processing
5. Deterministic decision render → Ledger entry created
6. Contract generation (if eligible) with decision citation

### Secondary: Compliance Review
1. Auditor queries decision ledger by contractor
2. System replays rule evaluation with original evidence
3. Full lineage: Input → Rules vX.Y.Z → Evidence IDs → Output

## 4. Technical Constraints
- **Stack**: Python 3.11+, FastAPI, PostgreSQL 15+, Celery with Redis
- **Determinism**: No randomness, no external API calls during rule eval (pre-fetch evidence)
- **Scalability**: 10,000 concurrent evaluations/hour
- **Compliance**: SOC2 Type II, GDPR Article 30, IRS Pub 15-A recordkeeping

## 5. Data Model (Key Entities)
- **RuleSet**: version, jurisdiction, AST representation, effective_date
- **Decision**: id, contractor_id, rule_version_id, input_payload_hash, output_payload, ledger_hash, created_at
- **Evidence**: id, type, source, content_hash, expires_at, citation_refs[]
- **EvaluationContext**: frozen dict of inputs (country, entity_type, answers[])

## 6. Success Metrics
- 99.99% decision reproducibility (same input/version = same output)
- <50ms p99 rule evaluation time
- Zero unexplainable decisions (100% evidence coverage)
- Audit query response <200ms for 5-year history
