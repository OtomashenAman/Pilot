import { listRules } from "@/lib/api";

export default async function RulesPage() {
  const rules = await listRules();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Rules Registry</h1>
      <div className="overflow-hidden rounded-xl border border-slate-800">
        <table className="min-w-full divide-y divide-slate-800 text-sm">
          <thead className="bg-card text-slate-300">
            <tr>
              <th className="px-4 py-2 text-left">Slug</th>
              <th className="px-4 py-2 text-left">Jurisdiction</th>
              <th className="px-4 py-2 text-left">Version</th>
              <th className="px-4 py-2 text-left">Hash</th>
              <th className="px-4 py-2 text-left">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 bg-slate-950/30">
            {rules.map((r) => (
              <tr key={r.id}>
                <td className="px-4 py-2">{r.slug}</td>
                <td className="px-4 py-2">{r.jurisdiction}</td>
                <td className="px-4 py-2">{r.currentVersion}</td>
                <td className="px-4 py-2 font-mono">{r.hashSha256}</td>
                <td className="px-4 py-2 capitalize">{r.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
