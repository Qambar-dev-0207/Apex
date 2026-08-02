"use client";

import { useState } from "react";
import { motion } from "motion/react";

interface CommandSpec {
  cmd: string;
  label: string;
  output: string[];
}

const COMMANDS: CommandSpec[] = [
  {
    cmd: "python main.py --sovereign",
    label: "01. INITIALIZE OS",
    output: [
      "⚡ APEX Sovereign Operating System v2.4",
      "🔋 [Vitals] Hardware Bridge Active (CPU: 38°C, RAM: 32.4GB free)",
      "🧠 [Brain] Intent Router initialized with Gemini 2.0 Flash",
      "💾 [Memory] Redis working cache & ChromaDB semantic memory loaded",
      "🟢 System ready. Socratic reasoning gate enforced."
    ]
  },
  {
    cmd: "apex query --semantic='tailor resume for Google SWE'",
    label: "02. SEMANTIC CACHE LOOKUP",
    output: [
      "$ apex query --semantic='tailor resume for Google SWE'",
      "🔍 [Cache] Computing vector embedding cosine distance...",
      "⚡ [ChromaDB] Proximity score: 0.98. Cache hit!",
      "⏱️ [Performance] Retrieved past decision artifact in 38ms (bypassed LLM API cost)",
      "🟢 Artifact ready: 'google_swe_tailored_v2.json'"
    ]
  },
  {
    cmd: "apex run socratic-gate --verify-thesis",
    label: "03. SOCRATIC REASONING",
    output: [
      "$ apex run socratic-gate --verify-thesis",
      "⏳ [Socratic Gate] Probing user intent & assumption validity...",
      "🧠 [Steelman] Proposing alternative optimization path: AST code compression",
      "🛡️ [Guardrail] Applied safety boundary on sandbox execution",
      "🟢 Action verified and dispatched to parallel swarm."
    ]
  }
];

export default function TerminalSection() {
  const [activeTab, setActiveTab] = useState<number>(0);
  const [copied, setCopied] = useState<boolean>(false);

  const activeCmd = COMMANDS[activeTab];

  const handleCopy = () => {
    navigator.clipboard.writeText(activeCmd.cmd);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="terminal" className="py-20 relative z-10">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 md:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
          className="mb-12 text-center md:text-left"
        >
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-[#2563EB]/10 border border-[#2563EB]/20 text-[#2563EB] font-mono text-xs font-semibold uppercase tracking-wider mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-[#2563EB]"></span>
            CLI INTERACTIVE SANDBOX
          </div>
          <h2 className="font-display text-3xl md:text-4xl font-extrabold text-[#0C0C0E] tracking-tight mb-3">
            Command-First Autonomous Control
          </h2>
          <p className="font-sans text-[#52525B] max-w-xl text-sm leading-relaxed">
            Execute sovereign directives directly from your shell. APEX exposes high-speed CLI parameters for instant orchestration.
          </p>
        </motion.div>

        {/* Terminal Window */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-[#0C0C0E] border border-black/15 rounded-2xl overflow-hidden shadow-2xl"
        >
          {/* Header Bar */}
          <div className="bg-[#16161A] px-6 py-4 border-b border-white/10 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500/80 inline-block"></span>
              <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block"></span>
              <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block"></span>
              <span className="font-mono text-xs text-gray-400 ml-2">bash - apex-sovereign-cli</span>
            </div>

            {/* Command Tabs */}
            <div className="flex items-center gap-2 font-mono text-xs">
              {COMMANDS.map((c, idx) => (
                <button
                  key={c.label}
                  onClick={() => setActiveTab(idx)}
                  className={`px-3 py-1.5 rounded-md transition-colors ${
                    activeTab === idx
                      ? "bg-[#FF4500]/20 border border-[#FF4500]/50 text-[#FF4500] font-bold"
                      : "text-gray-400 hover:text-gray-200"
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {/* Terminal Body */}
          <div className="p-8 font-mono text-xs md:text-sm text-gray-200 space-y-4">
            <div className="flex items-center justify-between bg-[#050507] p-3 rounded-lg border border-white/10">
              <div className="flex items-center gap-2 text-[#FF4500]">
                <span className="text-gray-500">$</span>
                <span>{activeCmd.cmd}</span>
              </div>
              <button
                onClick={handleCopy}
                className="px-3 py-1 rounded bg-[#1C1F2B] hover:bg-[#2A2E3D] text-gray-300 text-xs font-mono transition-colors"
              >
                {copied ? "COPIED ✓" : "COPY CMD"}
              </button>
            </div>

            <div className="space-y-2 pt-2">
              {activeCmd.output.map((line, idx) => (
                <div key={idx} className="leading-relaxed flex items-start gap-2">
                  <span className="text-gray-600 select-none">&gt;</span>
                  <span className={line.includes("🟢") ? "text-[#059669]" : line.includes("⚠️") ? "text-amber-400" : "text-gray-300"}>
                    {line}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
