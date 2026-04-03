import type { BuildJob } from '@/lib/types';

const statusStyles: Record<BuildJob['status'], string> = {
  queued: 'bg-amber-500/20 text-amber-300',
  running: 'bg-blue-500/20 text-blue-300',
  success: 'bg-emerald-500/20 text-emerald-300',
  failed: 'bg-red-500/20 text-red-300'
};

export default function JobStatusCard({ job }: { job: BuildJob }) {
  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900 p-4">
      <div className="flex items-center justify-between">
        <p className="font-medium">{job.repository}</p>
        <span className={`rounded px-2 py-1 text-xs ${statusStyles[job.status]}`}>{job.status}</span>
      </div>
      <p className="mt-2 text-sm text-slate-400">{job.branch} · {job.commitSha}</p>
      {job.summary ? <p className="mt-3 text-sm text-slate-300">{job.summary}</p> : null}
    </div>
  );
}
