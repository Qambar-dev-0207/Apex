"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { Layers, ShieldCheck, Cpu, HardDrive } from "lucide-react";

interface ArchitectureTier {
  id: string;
  num: string;
  name: string;
  headline: string;
  summary: string;
  details: string[];
  icon: typeof Layers;
}

const ARCHITECTURE_TIERS: ArchitectureTier[] = [
  {
    id: "strategy",
    num: "01",
    name: "Intelligence & Strategy",
    headline: "Intent routing and cognitive orchestration.",
    summary:
      "Intent understanding, routing, orchestration, and dependency-ordered task planning.",
    details: [
      "Gemini 2.0 Flash intent classification & sovereign skill routing",
      "Directed Acyclic Graph (Task DAG) decomposition engine",
      "Socratic Invariant Gate with Steelman assumption probing",
    ],
    icon: ShieldCheck,
  },
  {
    id: "memory",
    num: "02",
    name: "Memory & Context",
    headline: "Hybrid working cache and semantic retrieval.",
    summary:
      "Working memory, long-term semantic retrieval, and contextual relationships.",
    details: [
      "Redis in-memory working cache for active state (<10ms latency)",
      "ChromaDB persistent vector embeddings for long-term semantic search",
      "AST Code Compass symbol indexer with 18.4× context compression",
    ],
    icon: HardDrive,
  },
  {
    id: "execution",
    num: "03",
    name: "Execution & Validation",
    headline: "Parallel dispatch and defensive validation.",
    summary:
      "Specialized agents, task coordination, execution, and result verification.",
    details: [
      "asyncio TaskGroup concurrent worker pool with timeout boundaries",
      "Specialized research and coding agent harnesses",
      "Multi-stage pipeline: Spec → Implementation → Automated Validation",
    ],
    icon: Cpu,
  },
  {
    id: "interface",
    num: "04",
    name: "Interface & Telemetry",
    headline: "Sensory awareness and hardware guardrails.",
    summary:
      "User interaction, environmental context, and operational signals where supported.",
    details: [
      "Real-time hardware monitoring (CPU, RAM, thermals, token spend)",
      "Ambient sensory awareness and multi-modal screen context",
      "Proactive throttling based on system load and budget gates",
    ],
    icon: Layers,
  },
];

export default function ArchitectureSection() {
  const [selectedTier, setSelectedTier] = useState<number>(0);

  return (
    <section
      id="architecture"
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-32 sm:py-40 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)]"
      aria-label="APEX 24-Layer System Architecture"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[840px] mb-20 lg:mb-28">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium mb-5"
          >
            SYSTEM ARCHITECTURE
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-6"
          >
            Structure beneath the{" "}
            <span className="font-editorial italic font-normal text-[#E9D0AD]">
              intelligence.
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            APEX brings orchestration, context, execution, and interface into a layered system designed to coordinate complex work.
          </motion.p>
        </div>

        {/* 2-Column Architectural Layout: Interactive Stack Diagram + Tier Explanations */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-center">
          {/* Left Column: Stacked Architectural Planes Visualization */}
          <div className="lg:col-span-6 bg-[#050607] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-10 relative overflow-hidden min-h-[460px] flex items-center justify-center">
            {/* Subtle Perspective Coordinate Grid Background */}
            <div className="absolute inset-0 architectural-grid opacity-20 pointer-events-none" />

            {/* Central Vertical Architectural Axis Line */}
            <div className="absolute top-10 bottom-10 left-1/2 -translate-x-1/2 w-px bg-[rgba(255,255,255,0.12)] pointer-events-none" />

            {/* Exploded Architectural Monolithic Planes */}
            <div className="relative w-full max-w-[420px] flex flex-col gap-6 sm:gap-7 z-10 py-4">
              {ARCHITECTURE_TIERS.map((tier, idx) => {
                const isSelected = selectedTier === idx;
                return (
                  <button
                    key={tier.id}
                    type="button"
                    onClick={() => setSelectedTier(idx)}
                    onMouseEnter={() => setSelectedTier(idx)}
                    className={`group w-full relative text-left p-4 sm:p-5 rounded-xl border transition-all duration-300 cursor-pointer ${
                      isSelected
                        ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_24px_rgba(255,74,22,0.15)] -translate-y-1"
                        : "bg-[#08090A]/90 border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.22)]"
                    }`}
                  >
                    {/* Layer Header */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span
                          className={`font-code text-xs font-semibold tracking-wider ${
                            isSelected ? "text-[#FF4A16]" : "text-[#737575]"
                          }`}
                        >
                          TIER {tier.num}
                        </span>
                        <span className="w-1.5 h-1.5 rounded-full bg-[rgba(255,255,255,0.15)]" />
                        <span className="font-sans text-xs sm:text-sm font-semibold text-[#F5F3EF]">
                          {tier.name}
                        </span>
                      </div>

                      {/* Small Active Orange Beacon */}
                      {isSelected && (
                        <div className="flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16] animate-pulse" />
                          <span className="font-code text-[9px] tracking-widest text-[#FF4A16] uppercase">
                            ACTIVE
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Short Descriptor */}
                    <p className="text-[#B2B0AD] text-xs font-normal leading-relaxed line-clamp-1">
                      {tier.headline}
                    </p>

                    {/* Structural Corner Marks */}
                    <span
                      className={`absolute top-0 right-0 w-2 h-2 border-t border-r transition-colors ${
                        isSelected ? "border-[#FF4A16]" : "border-[rgba(255,255,255,0.15)]"
                      }`}
                    />
                    <span
                      className={`absolute bottom-0 left-0 w-2 h-2 border-b border-l transition-colors ${
                        isSelected ? "border-[#FF4A16]" : "border-[rgba(255,255,255,0.15)]"
                      }`}
                    />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Column: Explanatory Groups with Interactive Reveal */}
          <div className="lg:col-span-6 flex flex-col justify-between">
            <div className="space-y-4 mb-8">
              {ARCHITECTURE_TIERS.map((tier, idx) => {
                const isSelected = selectedTier === idx;
                return (
                  <div
                    key={tier.id}
                    onClick={() => setSelectedTier(idx)}
                    onMouseEnter={() => setSelectedTier(idx)}
                    className={`p-6 sm:p-7 rounded-xl border transition-all duration-300 cursor-pointer ${
                      isSelected
                        ? "bg-[#111315]/80 border-[rgba(255,255,255,0.2)] shadow-sm"
                        : "bg-transparent border-transparent hover:border-[rgba(255,255,255,0.06)] opacity-60 hover:opacity-100"
                    }`}
                  >
                    <div className="flex items-center gap-4 mb-2">
                      <span className="font-code text-xs font-semibold tracking-wider text-[#FF4A16]">
                        {tier.num} —
                      </span>
                      <h3 className="font-sans text-lg sm:text-xl font-medium text-[#F5F3EF]">
                        {tier.name}
                      </h3>
                    </div>

                    <p className="text-[#B2B0AD] text-sm leading-relaxed mb-4">
                      {tier.summary}
                    </p>

                    <AnimatePresence>
                      {isSelected && (
                        <motion.ul
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.3 }}
                          className="pt-4 border-t border-[rgba(255,255,255,0.08)] space-y-2 overflow-hidden"
                        >
                          {tier.details.map((detail, dIdx) => (
                            <li
                              key={dIdx}
                              className="flex items-start gap-2.5 font-code text-xs text-[#E9D0AD]/90"
                            >
                              <span className="text-[#FF4A16] select-none">▸</span>
                              <span>{detail}</span>
                            </li>
                          ))}
                        </motion.ul>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })}
            </div>

            {/* Bottom Clarifying Notation */}
            <div className="pt-6 border-t border-[rgba(255,255,255,0.08)] flex items-center justify-between text-[#737575] font-code text-[10px] tracking-[0.2em] uppercase">
              <span>FOUR ARCHITECTURAL TIERS</span>
              <span>24 DEEP INTERNAL LAYERS</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
