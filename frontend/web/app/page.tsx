import BuildForm from '@/components/BuildForm';
import { listBuildJobs } from '@/lib/api';
import JobStatusCard from '@/components/JobStatusCard';

export default async function HomePage() {
  const jobs = await listBuildJobs();

  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
      <BuildForm />
      <section className="space-y-3">
        <h2 className="text-sm font-semibold text-slate-700">Recent Jobs</h2>
        {jobs.map((job) => (
          <JobStatusCard key={job.id} job={job} />
        ))}
      </section>
    </div>
  );
}
