"use client";

import { useMemo, useState } from "react";
import { Artifact } from "@/lib/types";
import MarkdownViewer from "@/components/MarkdownViewer";
import CodeTreeViewer from "@/components/CodeTreeViewer";

export default function ArtifactTabs({ artifacts }: { artifacts: Artifact[] }) {
  const [activeId, setActiveId] = useState(artifacts[0]?.id);
  const active = useMemo(() => artifacts.find((a) => a.id === activeId) ?? artifacts[0], [artifacts, activeId]);

  if (!active) return <p className="text-sm text-slate-400">No artifacts available.</p>;

  return (
    <section className="space-y-3 rounded-xl border border-slate-800 bg-card p-4">
      <div className="flex flex-wrap gap-2">
        {artifacts.map((a) => (
          <button
            key={a.id}
            onClick={() => setActiveId(a.id)}
            className={`rounded-md px-3 py-1 text-sm ${a.id === active.id ? "bg-accent text-slate-900" : "bg-slate-800 text-slate-200"}`}
          >
            {a.title}
          </button>
        ))}
      </div>
      {active.type === "bundle" ? <CodeTreeViewer tree={active.content} /> : <MarkdownViewer content={active.content} />}
    </section>
  );
}
