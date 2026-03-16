import { listRuleVersions } from '@/lib/api';

export default async function RulesPage() {
  const versions = await listRuleVersions();

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Rule Versions</h1>
      <div className="grid gap-3">
        {versions.map((v) => (
          <div key={v.id} className="card">
            <div className="card-body grid gap-1 text-sm">
              <p className="font-semibold">{v.rule_key} <span className="font-normal text-slate-500">v{v.version}</span></p>
              <p>Effective: {v.effective_from}{v.effective_to ? ` → ${v.effective_to}` : ''}</p>
              <p>Created by: {v.created_by}</p>
              <p className="text-xs text-slate-500">Commit: {v.git_commit_hash}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
