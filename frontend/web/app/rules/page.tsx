import { getRules } from '@/lib/api';

export default async function RulesPage() {
  const rules = await getRules();

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Rule Studio</h2>
      <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
        <p className="mb-3 text-sm text-slate-400">Rule inventory and versions</p>
        <ul className="space-y-2">
          {rules.map((rule) => (
            <li key={rule.id} className="flex items-center justify-between rounded border border-slate-800 bg-slate-950 p-3">
              <span>{rule.name}</span>
              <span className="text-sm text-slate-400">v{rule.version} · {rule.status}</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
