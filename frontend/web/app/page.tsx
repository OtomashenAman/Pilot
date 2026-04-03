import Link from 'next/link';
import { getBuilds, getRules, getReviewQueue } from '@/lib/api';

export default async function HomePage() {
  const [builds, rules, review] = await Promise.all([getBuilds(), getRules(), getReviewQueue()]);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Compliance Dashboard</h2>
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4"><p className="text-sm text-slate-400">Active Builds</p><p className="text-2xl font-bold">{builds.length}</p></div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4"><p className="text-sm text-slate-400">Published Rules</p><p className="text-2xl font-bold">{rules.filter((r) => r.status === 'published').length}</p></div>
        <div className="rounded-lg border border-slate-800 bg-slate-900 p-4"><p className="text-sm text-slate-400">Review Queue</p><p className="text-2xl font-bold">{review.length}</p></div>
      </div>
      <Link className="inline-block rounded bg-indigo-600 px-4 py-2 text-sm font-medium" href="/builds">Go to Builds</Link>
    </div>
  );
}
