export default function CodeTreeViewer({ raw }: { raw: string }) {
  let formatted = raw;
  try {
    formatted = JSON.stringify(JSON.parse(raw), null, 2);
  } catch {}

  return <pre className="overflow-x-auto rounded border border-slate-800 bg-slate-950 p-4 text-xs">{formatted}</pre>;
}
