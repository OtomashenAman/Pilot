import './globals.css';
import Link from 'next/link';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Compliance Platform',
  description: 'Deterministic compliance verification console'
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <header className="border-b border-slate-200 bg-white">
          <div className="container-page flex items-center justify-between py-4">
            <Link href="/" className="text-sm font-semibold text-slate-900">Compliance Console</Link>
            <nav className="flex items-center gap-4 text-sm text-slate-600">
              <Link href="/builds">Builds</Link>
              <Link href="/rules">Rules</Link>
              <Link href="/review">Review</Link>
            </nav>
          </div>
        </header>
        <main className="container-page">{children}</main>
      </body>
    </html>
  );
}
