"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

interface CodeTab {
  id: string;
  label: string;
  lang: string;
  code: string;
}

const TABS: CodeTab[] = [
  {
    id: "python",
    label: "PYTHON SDK",
    lang: "python",
    code: `from apex import SovereignOS, SocraticGate

# Initialize 24-Layer Agentic AI OS
os = SovereignOS(
    model="gemini-2.0-flash",
    socratic_gate=True,
    ast_compression=True
)

# Dispatch autonomous task with Socratic reflection
result = await os.dispatch(
    objective="Tailor resume for Staff SWE & verify AST symbols",
    token_budget_usd=0.05
)

print(f"Status: {result.status} | Latency: {result.vector_latency_ms}ms")`,
  },
  {
    id: "typescript",
    label: "TYPESCRIPT CLIENT",
    lang: "typescript",
    code: `import { ApexSovereign } from "@apex/sovereign-sdk";

const client = new ApexSovereign({
  apiKey: process.env.APEX_API_KEY,
  vectorCache: "chromadb",
  maxCostUsd: 0.10,
});

async function runSwarm() {
  const trace = await client.swarm.dispatch({
    task: "Build dependency AST graph for ./src",
    parallelThreads: 4
  });
  console.log(\`Compressed tokens by \${trace.compressionRatio}x\`);
}`,
  },
  {
    id: "curl",
    label: "REST API (cURL)",
    lang: "bash",
    code: `curl -X POST https://api.apex-sovereign.os/v2/dispatch \\
  -H "Authorization: Bearer $APEX_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "objective": "Execute Socratic Steelman verification",
    "router_threshold": 0.85,
    "isolated_sandbox": true
  }'`,
  },
  {
    id: "cli",
    label: "CLI DIRECTIVE",
    lang: "bash",
    code: `# Install APEX Sovereign CLI
npm install -g @apex/cli

# Run Socratic Gate with hardware vitals monitoring
apex socratic-gate --verify-thesis --max-ram-gb 32`,
  },
];

export default function CodePlayground() {
  const [activeTab, setActiveTab] = useState<string>("python");
  const [copied, setCopied] = useState<boolean>(false);

  const currentTab = TABS.find((t) => t.id === activeTab) || TABS[0];

  const handleCopy = () => {
    navigator.clipboard.writeText(currentTab.code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-[#000000] text-white rounded-3xl p-6 sm:p-8 shadow-xl overflow-hidden relative border border-[#262626]">
      {/* Header Bar Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 mb-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-[#262626] border border-white/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#262626] border border-white/20" />
          <span className="w-2.5 h-2.5 rounded-full bg-[#262626] border border-white/20" />
          <span className="font-mono text-xs text-[#8C8C8C] ml-3">
            apex://sdk/playground · v2.4
          </span>
        </div>

        {/* Tab Buttons */}
        <div className="flex flex-wrap items-center gap-1.5 font-mono text-xs p-1 bg-[#1A1A1A] rounded-xl border border-white/10">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3.5 py-1.5 rounded-lg transition-all cursor-pointer font-semibold ${
                activeTab === tab.id
                  ? "bg-[#FF3700] text-white shadow-xs"
                  : "text-[#8C8C8C] hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Code Editor Body */}
      <div className="relative font-mono text-xs sm:text-sm leading-relaxed overflow-x-auto min-h-[220px]">
        <button
          onClick={handleCopy}
          className="absolute top-0 right-0 px-4 py-1.5 rounded-full bg-[#1A1A1A] hover:bg-[#262626] text-white text-xs font-mono transition-colors border border-white/10 z-10 cursor-pointer flex items-center gap-2"
        >
          {copied ? (
            <>
              <span className="text-[#0CB300]">✓</span>
              <span>COPIED</span>
            </>
          ) : (
            <>
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span>COPY SPEC</span>
            </>
          )}
        </button>

        <AnimatePresence mode="wait">
          <motion.pre
            key={currentTab.id}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.2 }}
            className="text-white/85 pt-4"
          >
            <code>{currentTab.code}</code>
          </motion.pre>
        </AnimatePresence>
      </div>

      {/* Footer Status */}
      <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between font-mono text-[11px] text-[#8C8C8C]">
        <span>RUNTIME: {currentTab.lang.toUpperCase()} · VERIFIED DETERMINISM</span>
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-[#0CB300] animate-pulse" />
          <span className="text-[#0CB300] font-bold">SOCRATIC GATE READY</span>
        </div>
      </div>
    </div>
  );
}
