"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-white text-[#000000] border-t border-[#D9D9D9] relative overflow-hidden">
      {/* Large watermark wordmark matching Hanzo */}
      <div
        className="absolute bottom-0 right-0 font-display font-extrabold text-[160px] sm:text-[220px] leading-none text-black/[0.025] select-none pointer-events-none tracking-tight"
        aria-hidden
      >
        APEX
      </div>

      <div className="max-w-[1440px] mx-auto px-4 sm:px-8 pt-20 pb-12 relative z-10">

        {/* Top row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16 pb-16 border-b border-[#D9D9D9]">

          {/* Brand column */}
          <div className="md:col-span-1 space-y-5">
            {/* Logo */}
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-[#000000] flex items-center justify-center shadow-xs">
                <span className="font-display font-extrabold text-white text-xs">Ax</span>
                <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-[#0CB300] shadow-[0_0_4px_#0CB300]" />
              </div>
              <span className="font-display font-extrabold text-[#000000] text-xl tracking-tight">APEX</span>
            </div>

            <p className="text-[#545454] text-sm leading-relaxed">
              The 24-Layer Sovereign Agentic AI OS. Socratic reasoning gates, hybrid vector memory under 38ms, and 18.4× AST symbol context compression.
            </p>

            {/* Live status badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#FAFAF9] border border-[#D9D9D9] font-mono text-[11px] text-[#000000]">
              <span className="w-2 h-2 rounded-full bg-[#0CB300] animate-pulse" />
              <span className="font-semibold">All 24 Layers Operational</span>
            </div>
          </div>

          {/* Architecture column */}
          <div className="space-y-4">
            <h4 className="font-mono text-xs font-bold text-[#8C8C8C] uppercase tracking-wider">
              Architecture
            </h4>
            <ul className="space-y-3 font-medium text-sm text-[#545454]">
              {[
                { label: "Socratic Invariant Gate", href: "#process" },
                { label: "Code Compass AST Indexer", href: "#process" },
                { label: "ChromaDB + Redis Cache", href: "#telemetry" },
                { label: "Parallel TaskGroup Swarms", href: "#orchestrator" },
                { label: "Hardware Oscilloscope", href: "#telemetry" },
              ].map((item) => (
                <li key={item.label}>
                  <a href={item.href} className="hover:text-[#FF3700] transition-colors">
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Developers column */}
          <div className="space-y-4">
            <h4 className="font-mono text-xs font-bold text-[#8C8C8C] uppercase tracking-wider">
              Developers
            </h4>
            <ul className="space-y-3 font-medium text-sm text-[#545454]">
              {[
                { label: "Interactive DAG Playground", href: "#orchestrator" },
                { label: "Python SDK Reference", href: "#playground" },
                { label: "Real-time Telemetry Bridge", href: "#telemetry" },
                { label: "Cluster Pricing & Plans", href: "#pricing" },
                { label: "System FAQ", href: "#faq" },
              ].map((item) => (
                <li key={item.label}>
                  <a href={item.href} className="hover:text-[#FF3700] transition-colors">
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Connect column */}
          <div className="space-y-4">
            <h4 className="font-mono text-xs font-bold text-[#8C8C8C] uppercase tracking-wider">
              Connect
            </h4>
            <p className="text-sm text-[#545454]">
              Available for enterprise deployments and air-gapped cluster setups.
            </p>
            <div className="pt-2">
              <a
                href="mailto:team@apex-os.ai"
                className="font-display font-bold text-base text-[#000000] hover:text-[#FF3700] transition-colors block mb-4"
              >
                team@apex-os.ai ↗
              </a>
              <a
                href="https://github.com/Qambar-dev-0207/realjarvis"
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-[#D9D9D9] hover:border-[#000000] text-[#000000] text-xs font-semibold shadow-xs transition-all"
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                GitHub Repository
              </a>
            </div>
          </div>

        </div>

        {/* Bottom row */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 font-mono text-xs text-[#8C8C8C]">
          <div>
            © {new Date().getFullYear()} APEX Sovereign Intelligence. Built with zero hallucination.
          </div>
          <div className="flex items-center gap-6">
            <span className="flex items-center gap-1.5 text-[#000000] font-semibold">
              <span className="w-2 h-2 rounded-full bg-[#0CB300]" />
              Status: 99.99% Invariance
            </span>
            <a href="#overview" className="hover:text-[#000000] transition-colors">
              Back to top ↑
            </a>
          </div>
        </div>

      </div>
    </footer>
  );
}
