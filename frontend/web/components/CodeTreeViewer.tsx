export default function CodeTreeViewer({ tree }: { tree: string }) {
  return (
    <pre className="overflow-x-auto rounded-md border border-slate-800 bg-slate-950 p-4 text-sm text-slate-200">
      {tree}
    </pre>
  );
}
