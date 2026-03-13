# Frontend Specification

## Stack
- **Framework**: Next.js 14 (App Router, Server Components)
- **Language**: TypeScript 5.3
- **Styling**: Tailwind CSS + shadcn/ui
- **State**: Zustand (client) + React Server Components (server)
- **Forms**: React Hook Form + Zod validation

## Core Pages

### 1. Rule Editor (`/rules/[id]/edit`)
- **DSL IDE**: Monaco Editor with custom syntax highlighting
- **Visual Builder**: Node-based DAG editor for rule dependencies
- **Version Timeline**: Git-style visualization of rule history
- **Test Panel**: Input JSON editor + Expected Output comparison
- **Actions**: Draft, Publish, Rollback, Compare versions

### 2. Decision Explorer (`/decisions`)
- **Search**: Filter by date, jurisdiction, rule version, outcome
- **Table**: Correlation ID, Timestamp, Rule, Version, Result, Evidence count
- **Detail View**: 
  - Input/Output JSON trees
  - Execution trace (step-by-step rule evaluation)
  - Evidence citations with document preview
  - Ledger proof verification badge

### 3. Audit Dashboard (`/audit`)
- **Compliance Overview**: Risk heatmap by jurisdiction
- **Drift Detection**: Rules modified vs. baseline
- **Report Generator**: Export PDF/CSV for auditors
- **Real-time Stream**: Recent decisions with confidence alerts

## Component Architecture

```
src/
├── app/
│   ├── (dashboard)/
│   ├── rules/
│   └── decisions/
├── components/
│   ├── rules/
│   │   ├── DslEditor.tsx
│   │   ├── VersionGraph.tsx
│   │   └── RuleTester.tsx
│   ├── decisions/
│   │   ├── DecisionTable.tsx
│   │   ├── EvidencePanel.tsx
│   │   └── ExecutionTrace.tsx
│   └── ui/ (shadcn components)
├── lib/
│   ├── api/ (Django/FastAPI clients)
│   └── dsl/ (parser utilities)
└── types/
    ├── rule.ts
    └── decision.ts
```

## Key Interactions

### Rule Evaluation Flow
1. User inputs contractor data (country, role, salary)
2. Frontend calls FastAPI `/evaluate` endpoint
3. Displays loading state with progress (streaming SSE for complex rules)
4. Result card shows: Classification, Confidence, Citations
5. One-click "Add to Ledger" creates immutable record

### Evidence Management
- Drag-drop document upload to S3 (presigned URLs)
- Automatic citation extraction highlights relevant text
- Side-by-side comparison: Rule requirement vs. Evidence

## Performance Requirements
- Time to Interactive (TTI) < 1.5s
- Editor load < 3s for 10k line rules
- Virtualized lists for >1000 decisions
- Optimistic UI for rule publishing

## Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation for DAG editor
- Screen reader support for decision trace visualization