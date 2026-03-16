# Contractor Onboarding Platform PRD

## 1. Overview
Build a global contractor onboarding system with deterministic compliance verification, immutable audit trails, and automated document collection.

## 2. Goals
- Reduce onboarding time from 5 days to 2 hours
- 100% compliance coverage across 150+ countries
- Zero non-deterministic decision paths
- Full auditability for regulators

## 3. User Flows

### 3.1 Contractor Flow
1. Identity verification (KYC)
2. Tax form collection (W-9/W-8BEN)
3. Compliance questionnaire
4. Contract e-signature
5. Payment method setup

### 3.2 Admin Flow
1. Review decision ledger
2. Override rules (with mandatory justification)
3. Export compliance reports
4. Manage rule versions

## 4. Core Requirements

### 4.1 Deterministic Rule Engine
- All eligibility/compliance decisions via rule evaluation
- Rules defined as deterministic functions: f(context) → {pass|fail|review}
- No randomness, timestamps (use effective dates), or external calls without caching
- Rule execution must be reproducible with identical context hash

### 4.2 Rule Versioning
- Semantic versioning (MAJOR.MINOR.PATCH)
- Effective date ranges for each version
- Git-like diff visualization between versions
- Automatic migration paths for in-flight applications
- Rollback capability within 24h window

### 4.3 Decision Ledger
- Append-only immutable log (blockchain-inspired integrity)
- Schema: `decision_id`, `rule_version_id`, `input_hash`, `output`, `timestamp`, `evidence_refs[]`
- Cryptographic chaining (previous_hash field)
- Retention: 7 years minimum

### 4.4 Evidence Citations
- Every decision point links to supporting evidence
- Evidence types: uploaded_document, api_response, calculated_field, manual_review
- SHA-256 hashing of all evidence
- Tamper-evident seals on documents

## 5. Compliance Modules

### 5.1 KYC Verification
- Document OCR with confidence scoring
- Sanctions list screening (OFAC, UN, EU)
- PEP (Politically Exposed Persons) screening

### 5.2 Tax Compliance
- FATCA/CRS classification
- VAT/GST registration validation
- Tax residency determination

### 5.3 Employment Risk
- Misclassification scoring (AB5, IR35)
- Local labor law checklist
- Conflict of interest detection

## 6. Non-Functional Requirements
- Availability: 99.9% SLA
- Rule evaluation: <500ms p99
- Document processing: <30s async
- GDPR/CCPA compliant data retention

## 7. Success Metrics
- Decision accuracy: >99.5%
- False positive rate: <2%
- Rule deployment frequency: 10/day
- Audit query response time: <2s