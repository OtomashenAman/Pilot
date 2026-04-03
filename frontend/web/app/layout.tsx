import './globals.css';
import Link from 'next/link';
import type { ReactNode } from 'react';

export const metadata = {
  title: 'Compliance Platform',
  description: 'Deterministic compliance verification and audit UI'
};

const nav = [
  { href: '/', label: 'Dashboard' },
  { href: '/builds', label: 'Builds' },
  { href: '/rules', label: 'Rules' },
  { href: '/review', label: 'Review' }
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-slate-800 bg-slate-900/60 backdrop-blur">
            <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
              <h1 className="text-lg font-semibold">Compliance Engine</h1>
              <nav className="flex gap-4 text-sm">
                {nav.map((item) => (
                  <Link key={item.href} href={item.href} className="rounded px-2 py-1 hover:bg-slate-800">
                    {item.label}
                  </Link>
                ))}
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-7xl px-6 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
