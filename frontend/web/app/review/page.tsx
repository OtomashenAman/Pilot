import { listReviewItems } from "@/lib/api";

export default async function ReviewPage() {
  const items = await listReviewItems();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Decision Review Queue</h1>
      <div className="grid gap-3">
        {items.map((item) => (
          <article key={item.id} className="rounded-xl border border-slate-800 bg-card p-4">
            <div className="flex items-center justify-between">
              <p className="font-medium">Decision {item.decisionId}</p>
              <p className="text-sm text-slate-300">Rule v{item.ruleVersion}</p>
            </div>
            <p className="mt-2 text-sm text-slate-200">Outcome: {item.outcome}</p>
            <p className="text-sm text-slate-300">
              Confidence: {(item.confidence * 100).toFixed(1)}% • Citations: {item.citations}
            </p>
          </article>
        ))}
      </div>
    </div>
  );
}
