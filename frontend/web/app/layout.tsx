import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Compliance Platform",
  description: "Deterministic, auditable compliance workflow UI"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="border-b border-slate-800 bg-card/80 backdrop-blur">
            <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
              <Link href="/" className="text-lg font-semibold text-white">
                Compliance Console
              </Link>
              <nav className="flex items-center gap-5 text-sm text-slate-300">
                <Link href="/builds">Builds</Link>
                <Link href="/rules">Rules</Link>
                <Link href="/review">Review</Link>
              </nav>
            </div>
          </header>
          <main className="mx-auto max-w-6xl px-4 py-8">{children}</main>
        </div>
      </body>
    </html>
  );
}
