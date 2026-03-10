# Subcontractor Onboarding PRD

## Overview
EOR/AOR platform for deterministic subcontractor eligibility validation with full audit trails and compliance evidence management.

## Core Requirements

### Deterministic Rule Engine
- JSON-Logic based rule definitions with 100% reproducible outputs given identical inputs
- Stateless evaluation, no external API calls during execution (pre-fetched data only)
- Support for jurisdiction-specific compliance matrices (tax, labor law, AML/KYC)
- Sub-100ms evaluation time per rule set

### Rule Versioning
- Immutable semantic versioning (MAJOR.MINOR.PATCH) for all compliance rules
- Historical preservation enabling retroactive audit simulations
- Effective dating with overlapping rule sets for jurisdiction transitions
- Git-like branching for proposed regulation changes

### Decision Ledger
- Append-only cryptographically chained records (SHA-256: prev_hash + payload)
- Tamper-evident storage with hash verification endpoints
- Immutable WORM (Write Once Read Many) backup strategy
- Queryable by subcontractor_id, rule_version, jurisdiction, timestamp

### Evidence Citations
- Mandatory citation requirements: every decision factor must link to source evidence
- Document integrity via SHA-256 checksums stored in ledger
- Granular citation mapping (JSON path → evidence_id → byte range)
- Support for multi-source evidence aggregation (single decision, multiple docs)

## User Flows
1. **Intake**: Subcontractor submits PII, tax forms, certifications via secure upload
2. **Validation**: Async Celery pipeline extracts data, verifies document authenticity
3. **Evaluation**: Rule engine processes against active jurisdiction-specific rule set
4. **Decision**: Binary (Approve/Reject) or tertiary (+Manual Review) with full rationale
5. **Audit**: Compliance officers query decision chains with full evidence trails

## Compliance
- GDPR Article 30 (Record of Processing Activities)
- SOC2 Type II (Security & Availability)
- ISO 27001 (Information Security Management)
- Multi-jurisdictional labor law retention requirements (3-7 years)