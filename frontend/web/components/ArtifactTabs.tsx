'use client';

import { useState } from 'react';
import type { BuildArtifact } from '@/lib/types';
import MarkdownViewer from '@/components/MarkdownViewer';
import CodeTreeViewer from '@/components/CodeTreeViewer';

export default function ArtifactTabs({ artifacts }: { artifacts: BuildArtifact[] }) {
  const [active, setActive] = useState(artifacts[0]?.id);
  const selected = artifacts.find((a) => a.id === active) ?? artifacts[0];

  if (!selected) return <p className="text-sm text-slate-400">No artifacts yet.</p>;

  return (
    <div className="rounded-lg border border-slate-800 bg-slate-900">
      <div className="flex flex-wrap gap-2 border-b border-slate-800 p-3">
        {artifacts.map((a) => (
          <button key={a.id} onClick={() => setActive(a.id)} className={`rounded px-3 py-1 text-sm ${selected.id === a.id ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-300'}`}>
            {a.name}
          </button>
        ))}
      </div>
      <div className="p-4">
        {selected.type === 'markdown' ? <MarkdownViewer content={selected.content} /> : <CodeTreeViewer raw={selected.content} />}
      </div>
    </div>
  );
}
