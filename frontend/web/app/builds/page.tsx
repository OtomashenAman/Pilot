import Link from 'next/link';
import BuildForm from '@/components/BuildForm';
import JobStatusCard from '@/components/JobStatusCard';
import { getBuilds } from '@/lib/api';

export default async function BuildsPage() {
  const builds = await getBuilds();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold">Build Pipeline</h2>
      <BuildForm />
      <div className="grid gap-4 md:grid-cols-2">
        {builds.map((job) => (
          <Link key={job.id} href={`/builds/${job.id}`}>
            <JobStatusCard job={job} />
          </Link>
        ))}
      </div>
    </div>
  );
}
