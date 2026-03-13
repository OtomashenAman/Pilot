import Link from "next/link";
import { BuildJob } from "@/lib/types";

const statusColor: Record<BuildJob["status"], string> = {
  queued: "text-yellow-300",
  running: "text-blue-300",
  succeeded: "text-success",
  failed: "text-danger"
};

export default function JobStatusCard({ job }: { job: BuildJob }) {
  return (
    <article className="rounded-xl border border-slate-800 bg-card p-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">{job.ruleSlug}</h3>
        <span className={`text-sm capitalize ${statusColor[job.status]}`}>{job.status}</span>
      </div>
      <p className="mt-1 text-sm text-slate-300">{job.jurisdiction} • {job.summary ?? "No summary"}</p>
      <p className="mt-1 text-xs text-slate-400">Updated {new Date(job.updatedAt).toLocaleString()}</p>
      <Link href={`/builds/${job.id}`} className="mt-3 inline-block text-sm">
        View job details →
      </Link>
    </article>
  );
}
