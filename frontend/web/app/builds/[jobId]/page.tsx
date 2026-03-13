import { notFound } from "next/navigation";
import ArtifactTabs from "@/components/ArtifactTabs";
import { getArtifacts, getBuild } from "@/lib/api";

export default async function BuildDetailPage({ params }: { params: { jobId: string } }) {
  const job = await getBuild(params.jobId);
  if (!job) return notFound();
  const artifacts = await getArtifacts(params.jobId);

  return (
    <div className="space-y-5">
      <header>
        <h1 className="text-2xl font-bold">Build {job.id}</h1>
        <p className="text-slate-300">{job.ruleSlug} • {job.jurisdiction} • {job.status}</p>
      </header>
      <ArtifactTabs artifacts={artifacts} />
    </div>
  );
}
