import Link from 'next/link';
import { listBuildJobs } from '@/lib/api';

export default async function BuildsPage() {
  const jobs = await listBuildJobs();

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Build Jobs</h1>
      <div className="card overflow-hidden">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-50 text-left text-slate-600">
            <tr>
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Rule Set</th>
              <th className="px-4 py-3">Version</th>
              <th className="px-4 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id} className="border-t border-slate-100">
                <td className="px-4 py-3"><Link href={`/builds/${job.id}`} className="text-brand-700 hover:underline">{job.id}</Link></td>
                <td className="px-4 py-3">{job.rule_set}</td>
                <td className="px-4 py-3">{job.version}</td>
                <td className="px-4 py-3">{job.status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
