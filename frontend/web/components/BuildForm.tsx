'use client';

import { useState } from 'react';
import { createBuildJob } from '@/lib/api';

export default function BuildForm() {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  async function onSubmit(formData: FormData) {
    setLoading(true);
    setMessage(null);

    try {
      const contextRaw = String(formData.get('context') || '{}');
      const payload = {
        rule_set: String(formData.get('rule_set') || ''),
        version: String(formData.get('version') || ''),
        effective_date: String(formData.get('effective_date') || ''),
        trace: true,
        context: JSON.parse(contextRaw)
      };

      const result = await createBuildJob(payload);
      setMessage(`Build submitted: ${result.id}`);
    } catch (err) {
      setMessage('Failed to submit build. Verify JSON context and API connectivity.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <form action={onSubmit} className="card">
      <div className="card-header">
        <h2 className="text-base font-semibold">Start Compliance Evaluation</h2>
      </div>
      <div className="card-body grid gap-4">
        <input name="rule_set" placeholder="Rule set (e.g. onboarding_compliance)" className="rounded-lg border border-slate-300 px-3 py-2 text-sm" required />
        <input name="version" placeholder="Version (e.g. 2.1.0)" className="rounded-lg border border-slate-300 px-3 py-2 text-sm" required />
        <input name="effective_date" type="date" className="rounded-lg border border-slate-300 px-3 py-2 text-sm" required />
        <textarea name="context" rows={8} defaultValue={'{\n  "country": "US",\n  "contractor_type": "individual"\n}'} className="rounded-lg border border-slate-300 px-3 py-2 font-mono text-xs" />
        <button disabled={loading} className="inline-flex items-center justify-center rounded-lg bg-brand-700 px-4 py-2 text-sm font-medium text-white hover:bg-brand-900 disabled:opacity-50">
          {loading ? 'Submitting...' : 'Run Evaluation'}
        </button>
        {message ? <p className="text-xs text-slate-600">{message}</p> : null}
      </div>
    </form>
  );
}
