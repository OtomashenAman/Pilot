export default function MarkdownViewer({ content }: { content: string }) {
  return <pre className="whitespace-pre-wrap rounded border border-slate-800 bg-slate-950 p-4 text-sm text-slate-200">{content}</pre>;
}
