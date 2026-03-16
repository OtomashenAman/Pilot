interface MarkdownViewerProps {
  markdown: string;
}

export default function MarkdownViewer({ markdown }: MarkdownViewerProps) {
  const html = markdown
    .replace(/^###\s(.+)$/gm, '<h3 class="text-base font-semibold mt-4 mb-2">$1</h3>')
    .replace(/^##\s(.+)$/gm, '<h2 class="text-lg font-semibold mt-4 mb-2">$1</h2>')
    .replace(/^#\s(.+)$/gm, '<h1 class="text-xl font-bold mt-4 mb-2">$1</h1>')
    .replace(/^-\s(.+)$/gm, '<li class="ml-5 list-disc">$1</li>')
    .replace(/\n/g, '<br/>');

  return <div className="prose prose-slate max-w-none text-sm" dangerouslySetInnerHTML={{ __html: html }} />;
}
