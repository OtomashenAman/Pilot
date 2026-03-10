# EOR/AOR Subcontractor Onboarding - Product Requirements

## 1. Overview
Platform to automate compliance, risk assessment, and onboarding for subcontractors across 150+ jurisdictions under Employer/Agent of Record models.

## 2. Goals
- Reduce onboarding time from 5 days to <4 hours for standard cases
- 100% audit trail for compliance investigations
- Zero-downtime rule updates for regulatory changes
- Deterministic eligibility decisions with full provenance

## 3. Non-Goals
- Payment processing (handled by external payroll)
- Contract negotiation (pre-signed templates only)
- Real-time video KYC (async document review)

## 4. Functional Requirements

### 4.1 Deterministic Rule Engine
- JSON/YAML rule definitions with strict schema validation
- Execution context isolation (no external calls during evaluation)
- Rule output hash for reproducibility verification
- Support for jurisdiction-specific rule sets (country/state/local)

### 4.2 Rule Versioning
- Semantic versioning (major.minor.patch) for all rule sets
- Immutable rule storage; updates create new versions
- Ability to replay historical decisions with original rule version
- A/B testing capability for rule changes (shadow mode)

### 4.3 Decision Ledger
- Append-only immutable log of every rule evaluation
- Tamper-evident cryptographic chaining (previous hash reference)
- Queryable by contractor_id, rule_version, timestamp, jurisdiction
- Retention: 7 years minimum for compliance

### 4.4 Evidence Citations
- Every decision field links to source evidence UUIDs
- Evidence types: Document scans, API responses, user inputs, third-party checks
- Confidence scoring (0.0-1.0) per evidence item
- Evidence expiration tracking (e.g., background check valid for 90 days)

## 5. Data Model (High Level)
- **Contractor**: PII, jurisdiction, onboarding_status
- **RuleSet**: version, jurisdiction_scope, logic_blob (JSONB), hash
- **Decision**: rule_version_id, input_hash, output, ledger_sequence
- **Evidence**: type, storage_uri, extracted_metadata, expiration_date
- **Citation**: decision_id, evidence_id, field_path, confidence

## 6. API Surface
- `POST /evaluate/{jurisdiction}`: Sync rule evaluation
- `POST /onboard`: Async onboarding initiation
- `GET /decisions/{contractor_id}`: Full decision history
- `GET /evidence/{evidence_id}`: Evidence retrieval with citations
- `POST /rules`: Deploy new rule version (admin)

## 7. Success Metrics
- Decision latency: p95 <200ms for rule evaluation
- Rule deployment time: <5 minutes global propagation
- Audit query response: <2s for 7-year history
- Evidence citation coverage: 100% of decision fields
