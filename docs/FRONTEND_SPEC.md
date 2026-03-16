# Frontend Specification

## 1. Tech Stack
- **Framework**: Next.js 14 (App Router)
- **State**: Zustand (client), React Query (server)
- **UI**: Tailwind CSS + Radix UI primitives
- **Forms**: React Hook Form + Zod validation
- **E-sign**: Embedded DocuSign/HelloSign SDK

## 2. Page Structure

### 2.1 Onboarding Wizard (`/onboarding/[step]`)
Multi-step form with deterministic progress calculation:
```typescript
interface Step {
  id: string;
  rule_validation: string; // Rule key to check completion
  evidence_required: string[];
}
```

Steps:
1. Personal Info (auto-save draft)
2. Tax Forms (dynamic based on residency rules)
3. Document Upload (drag-drop with virus scan status)
4. Compliance Questions (conditional logic from rule engine)
5. Review (evidence citations displayed)
6. Signature

### 2.2 Admin Dashboard (`/admin`)
- **Rule Manager**: Monaco Editor for rule DSL, diff viewer, version timeline
- **Decision Explorer**: Filterable ledger table, evidence chain visualization
- **Override Interface**: Mandatory justification field, links to parent decision

### 2.3 Audit Viewer (`/audit/[decision_id]`)
- Decision tree visualization (which rules fired)
- Evidence gallery with verification hashes
- Tamper-check status indicators

## 3. Key Components

### 3.1 RuleVisualizer
```typescript
interface RuleVisualizerProps {
  ruleVersionId: string;
  inputContext: Record<string, any>;
  showEvidence: boolean;
}
```
- Displays AST as flowchart
- Highlights executed branches
- Shows evidence citations per node

### 3.2 EvidenceUploader
- Chunked upload with checksum verification
- Real-time virus scan progress
- Automatic evidence hash generation
- Citation linking on successful upload

### 3.3 DecisionBadge
- Visual indicator: `PASS` | `FAIL` | `REVIEW` | `OVERRIDE`
- Hover reveals rule version and evidence count
- Click navigates to audit trail

## 4. API Integration

### 4.1 Rule Evaluation
```typescript
const evaluateRule = async (context: Context) => {
  const response = await fetch('/api/rules/evaluate', {
    method: 'POST',
    body: JSON.stringify({
      context,
      trace: true // Request execution trace for visualization
    })
  });
  return response.json(); // Includes decision_id, evidence_refs
};
```

### 4.2 Ledger Queries
- Cursor-based pagination for large audit logs
- Real-time WebSocket updates for decision status changes
- Export to CSV/PDF with embedded evidence hashes

## 5. State Management

### 5.1 Onboarding Store
```typescript
interface OnboardingState {
  draftId: string;
  formData: Record<string, any>;
  evidenceMap: Map<string, Evidence>;
  decisions: Decision[]; // Local cache of rule evaluations
  
  saveDraft: () => Promise<void>;
  evaluateCurrentStep: () => Promise<Decision>;
  attachEvidence: (field: string, file: File) => Promise<void>;
}
```

### 5.2 Optimistic Updates
- Immediate UI updates on form changes
- Background rule evaluation
- Rollback on validation failure

## 6. Security & Privacy
- Client-side encryption for sensitive fields (SSN, tax IDs) before transmission
- Automatic session timeout after 15min inactivity
- Secure document preview (signed URLs, 5min expiry)
- Redaction of PII in non-prod environments

## 7. Responsive Design
- Mobile-first for contractor flow (often on mobile)
- Desktop-optimized for admin/audit views
- Offline support for form filling (sync on reconnect)