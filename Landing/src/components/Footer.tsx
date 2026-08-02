"use client";

import Link from "next/link";

export default function Footer() {
  return (
    <footer className="bg-[#0A0A0B] text-white relative overflow-hidden">
      {/* Large watermark wordmark */}
      <div
        className="absolute bottom-0 right-0 font-display font-extrabold text-[180px] sm:text-[240px] leading-none text-white/[0.025] select-none pointer-events-none tracking-tight"
        aria-hidden
      >
        APEX
      </div>

      <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8 pt-20 pb-12 relative z-10">

        {/* Top row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-16">

          {/* Brand column */}
          <div className="md:col-span-1 space-y-6">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-[#FF4500] flex items-center justify-center">
                <span className="font-display font-extrabold text-white text-xs">Ax</span>
              </div>
              <span className="font-display font-extrabold text-white text-xl tracking-tight">APEX</span>
            </div>

            <p className="text-white/40 text-sm leading-relaxed">
              The 24-Layer Sovereign Agentic AI OS. Cognitive supremacy through Socratic reasoning, hybrid memory, and hardware-native execution.
            </p>

            {/* Live status */}
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#65CC00] animate-pulse shadow-[0_0_6px_#65CC00]" />
              <span className="font-mono text-[11px] text-[#65CC00] font-semibold tracking-wide">
                All 24 Tiers Operational
              </span>
            </div>

            {/* GitHub link */}
            <a
              href="https://github.com/Qambar-dev-0207/realjarvis"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white/6 border border-white/10 text-white/60 text-xs font-medium hover:text-white hover:bg-white/10 hover:border-white/20 transition-all duration-200"
            >
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              View on GitHub
            </a>
          </div>

          {/* Sovereign Architecture */}
          <div className="space-y-5">
            <h4 className="font-mono text-[10px] font-bold text-white/35 uppercase tracking-widest">
              Architecture
            </h4>
            <ul className="space-y-3.5">
              {[
                "Tier 1: Intent Router & Socratic Gate",
                "Tier 2: Code Compass AST Indexer",
                "Tier 3: ChromaDB + Redis Memory",
                "Tier 4: Parallel TaskGroup Swarm",
              ].map((item) => (
                <li key={item}>
                  <a href="#stack" className="text-sm text-white/45 hover:text-white transition-colors duration-200">
                    {item}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Developer */}
          <div className="space-y-5">
            <h4 className="font-mono text-[10px] font-bold text-white/35 uppercase tracking-widest">
              Developer
            </h4>
            <ul className="space-y-3.5">
              {[
                { label: "DAG Orchestrator Playground", href: "#orchestrator" },
                { label: "SDK Playground", href: "#playground" },
                { label: "Hardware Telemetry", href: "#telemetry" },
                { label: "CLI Sandbox", href: "#terminal" },
              ].map((item) => (
                <li key={item.label}>
                  <a href={item.href} className="text-sm text-white/45 hover:text-white transition-colors duration-200">
                    {item.label}
                  </a>
                </li>
              ))}
            </ul>
          </div>

          {/* Live vitals widget */}
          <div className="space-y-5">
            <h4 className="font-mono text-[10px] font-bold text-white/35 uppercase tracking-widest">
              System Vitals
            </h4>
            <div className="space-y-3 bg-white/4 border border-white/8 rounded-xl p-4">
              {[
                { label: "ChromaDB Latency", value: "< 38ms", color: "#65CC00" },
                { label: "Token Efficiency", value: "18.4×", color: "#FF4500" },
                { label: "Agent Swarms", value: "Parallel", color: "#2563EB" },
                { label: "System RAM", value: "32.4 GB", color: "#A78BFA" },
              ].map((item) => (
                <div key={item.label} className="flex justify-between items-center text-xs font-mono">
                  <span className="text-white/35">{item.label}</span>
                  <span className="font-bold" style={{ color: item.color }}>{item.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-8 border-t border-white/6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="font-mono text-[11px] text-white/25">
            © 2026 APEX Sovereign OS. Built for Autonomous Cognitive Supremacy.
          </div>
          <div className="flex items-center gap-6 font-mono text-[11px] text-white/25">
            <span className="hover:text-white/60 cursor-pointer transition-colors">Privacy</span>
            <span className="hover:text-white/60 cursor-pointer transition-colors">Terms of Sovereignty</span>
            <span className="hover:text-white/60 cursor-pointer transition-colors">MIT License</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
