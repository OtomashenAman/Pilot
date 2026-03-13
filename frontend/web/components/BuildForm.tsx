"use client";

import { FormEvent, useState } from "react";
import { createBuild } from "@/lib/api";

export default function BuildForm() {
  const [ruleSlug, setRuleSlug] = useState("");
  const [jurisdiction, setJurisdiction] = useState("");
  const [message, setMessage] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const job = await createBuild({ ruleSlug, jurisdiction });
    setMessage(`Created ${job.id} (${job.status})`);
    setRuleSlug("");
    setJurisdiction("");
  }

  return (
    <form onSubmit={onSubmit} className="space-y-4 rounded-xl border border-slate-800 bg-card p-4">
      <h2 className="text-lg font-semibold">Start Rule Build</h2>
      <div className="grid gap-3 sm:grid-cols-2">
        <input
          required
          value={ruleSlug}
          onChange={(e) => setRuleSlug(e.target.value)}
          placeholder="rule slug"
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2"
        />
        <input
          required
          value={jurisdiction}
          onChange={(e) => setJurisdiction(e.target.value)}
          placeholder="jurisdiction (e.g. DE)"
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-2"
        />
      </div>
      <button className="rounded-md bg-accent px-4 py-2 font-medium text-slate-900">Create Build</button>
      {message ? <p className="text-sm text-slate-300">{message}</p> : null}
    </form>
  );
}
