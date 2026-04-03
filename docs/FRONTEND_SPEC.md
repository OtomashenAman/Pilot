# Frontend Specification

## Tech Stack
- **Framework**: Next.js 14 (App Router)
- **State**: Zustand + React Query
- **UI Library**: Tailwind + Headless UI
- **Charts**: Recharts / Tremor
- **Forms**: React Hook Form + Zod
- **Monaco Editor**: For rule editing (YAML/JSON)

## Core Pages

### 1. Rule Studio (/rules)
**Purpose**: Author and manage compliance rules

**Layout**:
```
┌─────────────────────────────────────────────┐
│ Sidebar        │  Editor       │  Preview  │
│ - Rule tree    │  - Monaco     │  - Test   │
│ - Versions     │    Editor     │    input  │
│ - Git history  │  - Linting    │  - Output │
└─────────────────────────────────────────────┘
```

**Features**:
- Monaco Editor with custom rule DSL syntax highlighting
- Real-time validation against JSON Schema
- Version diff viewer (react-diff-viewer)
- "Test Rule" panel with sample data
- Publish workflow with approval gates

**State Management**:
- Draft auto-save to localStorage
- Optimistic updates for version switching

### 2. Decision Explorer (/decisions)
**Purpose**: Query and audit all compliance decisions

**Layout**:
```
┌─────────────────────────────────────────────┐
│ Filters        │  Decision List             │
│ - Date range   │  - Table with pagination   │
│ - Rule version │  - Expandable rows         │
│ - Outcome      │  - Evidence links          │
│ - Tenant       │                            │
└─────────────────────────────────────────────┘
```

**Features**:
- Advanced filtering (date, rule, outcome, evidence presence)
- Export to CSV/JSON (signed exports)
- Decision detail modal:
  - Input context (collapsed PII)
  - Rule version used
  - Execution trace (step-by-step)
  - Evidence gallery (thumbnails)
  - Ledger proof (hash chain)

**Performance**:
- Virtualized list (react-window)
- Debounced search (500ms)
- Cursor-based pagination

### 3. Evidence Vault (/evidence)
**Purpose**: Manage supporting documentation

**Features**:
- Drag-drop upload with virus scanning indicator
- Document viewer (PDF.js + image viewer)
- Evidence-to-decision linking interface
- Retention policy display
- OCR text extraction preview

### 4. Compliance Dashboard (/dashboard)
**Purpose**: High-level metrics and monitoring

**Widgets**:
- Decision volume (time series)
- Pass/fail rates by rule category
- Pending evidence citations
- Rule version adoption rates
- Ledger integrity status

**Real-time**:
- WebSocket connection for live decision stream
- Alert banner for rule execution failures

## Components Library

### RuleCard
```typescript
interface RuleCardProps {
  rule: {
    id: string;
    name: string;
    currentVersion: string;
    status: 'draft' | 'published' | 'deprecated';
    lastModified: Date;
    executionCount: number;
  };
  onPublish: () => void;
  onTest: () => void;
}
```

### DecisionTimeline
- Vertical timeline showing decision chain
- Color coding: Green (pass), Red (fail), Yellow (error)
- Hover reveals ledger hash

### EvidenceUploader
- Chunked upload for large files
- Progress indicator
- Automatic hash verification
- Virus scan status badge

## Security UI
- PII masking: Toggle to show/hide sensitive fields
- Role-based UI elements (RBAC checks)
- Session timeout warning
- Audit log of user actions

## API Integration

### React Query Hooks
```typescript
// hooks/useDecisions.ts
export const useDecisions = (filters: FilterParams) => {
  return useQuery({
    queryKey: ['decisions', filters],
    queryFn: () => fetchDecisions(filters),
    staleTime: 30000,
  });
};

// hooks/useRuleEvaluation.ts
export const useRuleEvaluation = () => {
  return useMutation({
    mutationFn: evaluateRule,
    onSuccess: (data) => {
      // Optimistically update decision list
    }
  });
};
```

## Error Handling
- Global error boundary with fallback UI
- Toast notifications for async operations
- Network status indicator (offline mode support)

## Accessibility
- WCAG 2.1 AA compliance
- Keyboard navigation for rule editor
- Screen reader support for decision tables
- High contrast mode support
