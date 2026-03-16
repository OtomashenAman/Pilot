import { listReviewQueue } from '@/lib/api';

export default async function ReviewPage() {
  const items = await listReviewQueue();

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Manual Review Queue</h1>
      <div className="card overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3">Decision ID</th>
              <th className="px-4 py-3">Version</th>
              <th className="px-4 py-3">Output</th>
              <th className="px-4 py-3">Evidence</th>
              <th className="px-4 py-3">Prev Hash</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.decision_id} className="border-t border-slate-100">
                <td className="px-4 py-3">{item.decision_id}</td>
                <td className="px-4 py-3">{item.rule_version}</td>
                <td className="px-4 py-3">{item.output}</td>
                <td className="px-4 py-3">{item.evidence_count}</td>
                <td className="px-4 py-3 text-xs text-slate-500">{item.previous_hash}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
