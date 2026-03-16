import { BuildJob } from '@/lib/types';

const statusStyles: Record<BuildJob['status'], string> = {
  queued: 'bg-slate-100 text-slate-700',
  running: 'bg-blue-100 text-blue-700',
  completed: 'bg-emerald-100 text-emerald-700',
  failed: 'bg-rose-100 text-rose-700'
};

export default function JobStatusCard({ job }: { job: BuildJob }) {
  return (
    <div className="card">
      <div className="card-body space-y-2">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold">{job.rule_set}</p>
          <span className={`rounded-full px-2 py-1 text-xs font-medium ${statusStyles[job.status]}`}>{job.status}</span>
        </div>
        <p className="text-xs text-slate-500">Job ID: {job.id}</p>
        <p className="text-xs text-slate-500">Version: {job.version}</p>
      </div>
    </div>
  );
}
