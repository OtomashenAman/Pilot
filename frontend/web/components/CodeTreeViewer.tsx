import { TreeNode } from '@/lib/types';

function Node({ node, depth = 0 }: { node: TreeNode; depth?: number }) {
  return (
    <div style={{ paddingLeft: `${depth * 12}px` }} className="py-1 text-sm">
      <span className="mr-2 text-slate-400">{node.type === 'folder' ? '📁' : '📄'}</span>
      <span>{node.name}</span>
      {node.children?.map((child) => (
        <Node key={`${node.name}-${child.name}`} node={child} depth={depth + 1} />
      ))}
    </div>
  );
}

export default function CodeTreeViewer({ nodes }: { nodes: TreeNode[] }) {
  return <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">{nodes.map((n) => <Node key={n.name} node={n} />)}</div>;
}
