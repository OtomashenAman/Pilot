# Frontend Specification

## Tech Stack
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui components
- **State**: Zustand (client), React Query (server)
- **Forms**: React Hook Form + Zod validation

## Core Pages

### 1. Rule Editor (/rules/[id]/edit)
- Visual DSL builder (drag-drop logic nodes)
- JSON editor mode for advanced users
- Version timeline sidebar (compare versions side-by-side)
- Test evaluator (mock payload input → instant result)
- Effective date picker with timezone support
- "Publish New Version" button (creates immutable version)

### 2. Decision Ledger (/ledger)
- Filterable table: Entity ID, Rule, Version, Outcome, Date
- Expandable rows showing Evidence Citations
- "View Input Payload" modal (hashed view for privacy)
- Export to CSV/JSON
- Ledger integrity indicator (hash verification status)

### 3. Compliance Dashboard (/dashboard)
- KPI Cards: Evaluations/sec, Pass Rate %, Active Rules
- Time-series chart: Decision volume by jurisdiction
- Recent violations list (failed compliance checks)
- Rule expiration alerts (<30 days)

### 4. Entity Compliance Profile (/entities/[id])
- Timeline of all evaluations for specific entity
- Current compliance status per rule category
- Evidence document viewer (iframe integration)
- "Re-evaluate" button (triggers new check with latest rules)

## Key Components

### VisualRuleBuilder
- Node types: Condition, And/Or, Comparison, Calculation
- Real-time validation (no circular deps)
- Auto-save drafts to localStorage

### EvidenceBadge
- Icon indicating source type (API, Upload, System)
- Hover tooltip: confidence score + timestamp
- Link to source document (if available)

### VersionDiff
- Side-by-side DSL JSON diff
- Highlight effective date changes
- "Rollback" action (creates new version reverting to old DSL)

## API Integration
- Django API: `/api/v1/rules/*` (management)
- FastAPI: `/api/v2/evaluate/*` (evaluation)
- WebSocket: `/ws/ledger` for real-time decision streaming

## Authentication
- JWT stored in httpOnly cookies
- Role-based access: Admin, Compliance Officer, Auditor (read-only ledger)
- MFA required for rule publishing

## Performance
- Virtualized lists for ledger (>10k rows)
- Debounced search (200ms)
- SWR caching for rule definitions (immutable, cache forever)