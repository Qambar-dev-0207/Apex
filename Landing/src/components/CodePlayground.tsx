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

print(f"Status: {result.status} | Latency: {result.vector_latency_ms}ms")`
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
}`
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
  }'`
  },
  {
    id: "cli",
    label: "CLI DIRECTIVE",
    lang: "bash",
    code: `# Install APEX Sovereign CLI
npm install -g @apex/cli

# Run Socratic Gate with hardware vitals monitoring
apex socratic-gate --verify-thesis --max-ram-gb 32`
  }
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
    <div className="bg-[#111111] text-[#F9FAFB] rounded-3xl p-6 sm:p-8 shadow-2xl overflow-hidden relative border border-white/10">
      {/* Header Bar Controls */}
      <div className="flex flex-wrap items-center justify-between gap-4 pb-6 mb-4 border-b border-white/10">
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-red-500/80"></span>
          <span className="w-3 h-3 rounded-full bg-amber-500/80"></span>
          <span className="w-3 h-3 rounded-full bg-emerald-500/80"></span>
          <span className="font-mono text-xs text-gray-400 ml-2">apex-sdk-playground</span>
        </div>

        {/* Tab Buttons */}
        <div className="flex items-center gap-1.5 font-mono text-xs">
          {TABS.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg transition-all ${
                activeTab === tab.id
                  ? "bg-[#84CC16] text-[#111111] font-bold shadow-md"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Code Editor Body */}
      <div className="relative font-mono text-xs sm:text-sm leading-relaxed overflow-x-auto min-h-[240px]">
        <button
          onClick={handleCopy}
          className="absolute top-0 right-0 px-3 py-1 rounded bg-[#222222] hover:bg-[#333333] text-gray-300 text-xs font-mono transition-colors border border-white/10 z-10"
        >
          {copied ? "COPIED ✓" : "COPY CODE"}
        </button>

        <AnimatePresence mode="wait">
          <motion.pre
            key={currentTab.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className="text-emerald-400 pt-4"
          >
            <code>{currentTab.code}</code>
          </motion.pre>
        </AnimatePresence>
      </div>

      {/* Footer Status */}
      <div className="mt-4 pt-4 border-t border-white/10 flex items-center justify-between font-mono text-[10px] text-gray-400">
        <span>LANGUAGE: {currentTab.lang.toUpperCase()}</span>
        <span className="text-[#84CC16] font-semibold">SOCRATIC GATE READY</span>
      </div>
    </div>
  );
}
