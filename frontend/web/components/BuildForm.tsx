'use client';

import { useState } from 'react';

export default function BuildForm() {
  const [repo, setRepo] = useState('acme/risk-rules');
  const [branch, setBranch] = useState('main');
  const [submitted, setSubmitted] = useState(false);

  return (
    <form
      className="rounded-lg border border-slate-800 bg-slate-900 p-4"
      onSubmit={(e) => {
        e.preventDefault();
        setSubmitted(true);
      }}
    >
      <h3 className="mb-3 font-medium">Start New Build</h3>
      <div className="grid gap-3 md:grid-cols-2">
        <input className="rounded border border-slate-700 bg-slate-950 px-3 py-2" value={repo} onChange={(e) => setRepo(e.target.value)} />
        <input className="rounded border border-slate-700 bg-slate-950 px-3 py-2" value={branch} onChange={(e) => setBranch(e.target.value)} />
      </div>
      <button className="mt-4 rounded bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500" type="submit">
        Queue Build
      </button>
      {submitted ? <p className="mt-2 text-sm text-emerald-400">Build queued for {repo}@{branch}</p> : null}
    </form>
  );
}
