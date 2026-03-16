# EOR/AOR Subcontractor Onboarding Platform - PRD

## 1. Objective
Automate subcontractor eligibility determination for Employer/Agent of Record services with 100% auditability and deterministic compliance logic.

## 2. Core Requirements

### 2.1 Deterministic Rule Engine
- JSON-based logical operators (AND/OR/NOT/IN/COMPARE) only
- No ML or probabilistic scoring
- Same input payload must produce identical output across time
- Execution trace capture for every node evaluation

### 2.2 Rule Versioning
- Immutable rule artifacts (WORM - Write Once Read Many)
- Semantic versioning (major.minor.patch)
- Effective date ranges for rule applicability
- Automatic rollback capabilities for jurisdiction law changes
- Version diff visualization for compliance officers

### 2.3 Decision Ledger
- Append-only cryptographic log of all eligibility determinations
- Tamper-evident hashing (previous decision hash included in current record)
- Immutable storage with 7-year retention minimum
- Exportable audit trails (JSON/CSV) for regulatory review

### 2.4 Evidence Citations
- Auto-linking of source documents to specific rule nodes
- Document integrity verification (SHA-256 hashes)
- Source attribution (e.g., "Tax Form W-9 v2023, Line 3")
- Missing evidence blocking rules from evaluation

## 3. User Flows

### Subcontractor Onboarding
1. Identity verification (KYC) via Celery async task
2. Document upload (Contracts, Tax forms, Certifications)
3. Jurisdiction detection (auto or manual)
4. Rule engine evaluation with real-time feedback
5. Decision generation with cited evidence
6. Appeal workflow for rejected determinations

### Compliance Officer
1. Rule authoring via JSON DSL or UI builder
2. Version testing against historical cases
3. Activation/deactivation of rule sets by jurisdiction
4. Audit query interface (search by subcontractor, date, rule version)

## 4. Data Requirements
- Subcontractor PII (encrypted at rest)
- Jurisdiction-specific labor laws (200+ countries/states)
- Document templates and validation schemas
- Audit logs (immutable, partitioned by month)

## 5. Non-Functional Requirements
- Latency: <500ms for rule evaluation (p95)
- Availability: 99.9% (compliance critical)
- Audit query: <2s for 1M decision records
- Compliance: SOC2 Type II, GDPR, CCPA