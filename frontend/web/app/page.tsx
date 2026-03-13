import Link from "next/link";
import BuildForm from "@/components/BuildForm";

export default function HomePage() {
  return (
    <div className="space-y-8">
      <section className="space-y-3">
        <h1 className="text-3xl font-bold">Compliance Platform UI</h1>
        <p className="max-w-2xl text-slate-300">
          Deterministic rules, immutable audit evidence, and review workflows for global workforce compliance.
        </p>
        <div className="flex gap-4 text-sm">
          <Link href="/builds">View Builds</Link>
          <Link href="/rules">View Rules</Link>
          <Link href="/review">Open Review Queue</Link>
        </div>
      </section>
      <BuildForm />
    </div>
  );
}
