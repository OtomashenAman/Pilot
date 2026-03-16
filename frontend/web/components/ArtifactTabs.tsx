import { BuildArtifact } from '@/lib/types';
import MarkdownViewer from '@/components/MarkdownViewer';
import CodeTreeViewer from '@/components/CodeTreeViewer';

export default function ArtifactTabs({ artifacts }: { artifacts: BuildArtifact[] }) {
  if (!artifacts.length) return <p className="text-sm text-slate-500">No artifacts available.</p>;

  return (
    <div className="space-y-4">
      {artifacts.map((artifact) => (
        <section key={artifact.key} className="card">
          <div className="card-header">
            <h3 className="text-sm font-semibold">{artifact.title}</h3>
          </div>
          <div className="card-body">
            {artifact.type === 'markdown' ? <MarkdownViewer markdown={String(artifact.content)} /> : null}
            {artifact.type === 'json' ? <pre className="overflow-x-auto rounded-lg bg-slate-900 p-3 text-xs text-slate-100">{JSON.stringify(artifact.content, null, 2)}</pre> : null}
            {artifact.type === 'tree' ? <CodeTreeViewer nodes={artifact.content as any} /> : null}
          </div>
        </section>
      ))}
    </div>
  );
}
