import ArtifactTabs from '@/components/ArtifactTabs';
import JobStatusCard from '@/components/JobStatusCard';
import { getArtifacts, getBuild } from '@/lib/api';

export default async function BuildDetailPage({ params }: { params: { jobId: string } }) {
  const job = await getBuild(params.jobId);
  const artifacts = await getArtifacts(params.jobId);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Build Details</h2>
      <JobStatusCard job={job} />
      <ArtifactTabs artifacts={artifacts} />
    </div>
  );
}
