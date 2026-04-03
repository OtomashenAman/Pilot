import { getReviewQueue } from '@/lib/api';

const severityColor = {
  low: 'text-emerald-300',
  medium: 'text-amber-300',
  high: 'text-red-300'
};

export default async function ReviewPage() {
  const items = await getReviewQueue();

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-semibold">Evidence Review Queue</h2>
      <div className="space-y-3">
        {items.map((item) => (
          <article key={item.id} className="rounded-lg border border-slate-800 bg-slate-900 p-4">
            <div className="flex items-center justify-between">
              <h3 className="font-medium">{item.title}</h3>
              <span className={`text-sm ${severityColor[item.severity]}`}>{item.severity}</span>
            </div>
            <p className="mt-2 text-sm text-slate-400">Decision: {item.decision} · Evidence: {item.evidenceCount}</p>
          </article>
        ))}
      </div>
    </div>
  );
}
