export default function MarkdownViewer({ content }: { content: string }) {
  const lines = content.split("\n");
  return (
    <div className="rounded-md border border-slate-800 bg-slate-950 p-4 font-mono text-sm">
      {lines.map((line, i) => (
        <p key={i} className="whitespace-pre-wrap text-slate-200">
          {line}
        </p>
      ))}
    </div>
  );
}
