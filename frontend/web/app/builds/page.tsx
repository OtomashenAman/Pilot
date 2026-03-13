import JobStatusCard from "@/components/JobStatusCard";
import { listBuilds } from "@/lib/api";

export default async function BuildsPage() {
  const builds = await listBuilds();

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Build Jobs</h1>
      <div className="grid gap-3">
        {builds.map((job) => (
          <JobStatusCard key={job.id} job={job} />
        ))}
      </div>
    </div>
  );
}
