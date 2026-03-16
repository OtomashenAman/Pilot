import ArtifactTabs from '@/components/ArtifactTabs';
import { getBuildJob } from '@/lib/api';

export default async function BuildDetailPage({ params }: { params: { jobId: string } }) {
  const job = await getBuildJob(params.jobId);

  return (
    <div className="space-y-6">
      <section className="card">
        <div className="card-header">
          <h1 className="text-lg font-semibold">Build {job.id}</h1>
        </div>
        <div className="card-body grid gap-2 text-sm">
          <p><span className="font-medium">Rule Set:</span> {job.rule_set}</p>
          <p><span className="font-medium">Version:</span> {job.version}</p>
          <p><span className="font-medium">Status:</span> {job.status}</p>
          <p><span className="font-medium">Decision:</span> {job.decision ?? 'n/a'}</p>
          <p><span className="font-medium">Input Hash:</span> <code className="break-all text-xs">{job.input_hash}</code></p>
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Artifacts</h2>
        <ArtifactTabs artifacts={job.artifacts} />
      </section>
    </div>
  );
}
