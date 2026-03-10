# Subcontractor Onboarding Platform - PRD

## 1. Overview
EOR/AOR onboarding platform for compliant subcontractor engagement with deterministic eligibility verification, audit trails, and automated compliance checks.

## 2. Objectives
- Reduce onboarding time from 5 days to <24hrs for compliant subcontractors
- 100% auditability of eligibility decisions
- Zero-downtime rule updates with instant rollback capability

## 3. Core Features

### 3.1 Deterministic Rule Engine
- JSON-based rule DSL with strict schema validation
- Support for: boolean logic, numerical comparisons, date ranges, geographic restrictions
- Deterministic execution: same inputs + rule version = identical output
- Rule precompilation for performance (<100ms evaluation latency)

### 3.2 Rule Versioning
- Immutable rule snapshots with semantic versioning (v1.0.0, v1.1.0)
- Temporal validity (effective_from, effective_until)
- A/B testing capability via rule branches
- Automatic migration detection between versions

### 3.3 Decision Ledger
- Append-only ledger storing: rule_version, input_hash, output, timestamp, correlation_id
- Cryptographic chaining (previous_hash) for tamper detection
- GDPR-compliant right-to-erasure via redaction markers (preserving ledger integrity)
- Real-time decision streaming to data warehouse

### 3.4 Evidence Citations
- Auto-extraction of evidence from uploaded docs (tax forms, certifications, ID)
- Evidence fingerprinting (SHA-256) linked to specific rule evaluations
- Citation chains: Decision X cites Evidence Y from Document Z at Page P
- Evidence expiry tracking with proactive re-collection

## 4. Data Model

### Contractor Profile
- id, legal_entity_id, jurisdiction, tax_classification
- compliance_status: [pending, eligible, rejected, suspended]
- risk_score: 0-100

### Rules Registry
- rule_id, version, dsl_definition, checksum, created_at, deprecated_at
- rule_type: [eligibility, tax_compliance, background_check, sanction_screening]

### Decision Log
- decision_id, contractor_id, rule_id, rule_version, input_payload_hash
- output_result, confidence_score, executed_at, execution_duration_ms
- evidence_refs: [{document_id, extraction_id, hash}]

## 5. Compliance Requirements
- SOC2 Type II: Immutable audit trails, access controls
- GDPR: Data minimization, consent tracking, right to portability
- IRS/Tax: Document retention (7 years), W-9/W-8 validation logic
- Sanctions: OFAC, EU, UN list screening with daily delta checks

## 6. User Stories
1. As Compliance Officer, I want to deploy new tax rules instantly with rollback capability
2. As Auditor, I want to reproduce any decision from 2 years ago using original rules+data
3. As Contractor, I want to see exactly which documents were used to approve my eligibility
4. As Risk Manager, I want to see real-time breakdown of rejections by rule category

## 7. Non-Functional Requirements
- Throughput: 1000 evaluations/minute
- Availability: 99.99% (rule engine), 99.9% (onboarding API)
- RPO: 0 (synchronous ledger replication)
- RTO: <5 minutes

## 8. Security
- Field-level encryption for PII (AES-256)
- HSM-backed signing of decision ledger entries
- RBAC: rule_admin, auditor, onboarding_ops, contractor
- Data residency controls (EU data stays in EU)