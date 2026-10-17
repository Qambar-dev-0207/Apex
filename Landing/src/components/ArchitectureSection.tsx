"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import ApexMascot from "./ApexMascot";
import { MOTION_EASE, MOTION_TIMING } from "../lib/motion";

interface ArchitectureTier {
  id: string;
  num: string;
  name: string;
  summary: string;
  details: string[];
  specs: string;
}

const ARCHITECTURE_TIERS: ArchitectureTier[] = [
  {
    id: "strategy",
    num: "01",
    name: "Intelligence & Strategy",
    summary: "Intent understanding, routing, orchestration, and dependency-ordered task planning.",
    specs: "Task DAGs · Socratic Gate · Gemini 2.0 Flash",
    details: [
      "Gemini 2.0 Flash intent classification & sovereign skill routing",
      "Directed Acyclic Graph (Task DAG) decomposition engine",
      "Socratic Invariant Gate with Steelman assumption probing",
    ],
  },
  {
    id: "memory",
    num: "02",
    name: "Memory & Context",
    summary: "Working memory, long-term semantic retrieval, and contextual relationships.",
    specs: "Redis Cache · ChromaDB HNSW · Context Consolidation",
    details: [
      "Redis sub-10ms active state working memory cache",
      "ChromaDB persistent vector database with HNSW index (<38ms)",
      "Automated ephemeral-to-semantic consolidation pipelines",
    ],
  },
  {
    id: "execution",
    num: "03",
    name: "Execution & Validation",
    summary: "Specialized agents, task coordination, execution, and result verification.",
    specs: "Groq LPU (<100ms) · AgentHarness · Sandbox Isolation",
    details: [
      "Groq LPU low-latency deterministic tool execution dispatch",
      "AgentHarness execution wrapper with automated snapshot rollbacks",
      "Isolated Python sub-process sandboxes with safety guardrails",
    ],
  },
  {
    id: "interface",
    num: "04",
    name: "Interface & Telemetry",
    summary: "User interaction, environmental context, and operational signals.",
    specs: "Full Sensory Bridge · Code Compass AST (18.4×) · Ollama Failover",
    details: [
      "Full sensory bridge: mouse, keyboard, and display telemetry",
      "Adaptive real-time token compression via Code Compass AST (18.4×)",
      "Local sovereignty offline failover: Ollama DeepSeek & Qwen models",
    ],
  },
];

export default function ArchitectureSection() {
  const [selectedTier, setSelectedTier] = useState<number>(0);
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="architecture"
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-28 sm:py-36 lg:py-44 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX 24-Layer System Architecture"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[840px] mb-16 lg:mb-24">
          {/* Eyebrow with horizontal line draw */}
          <div className="flex items-center gap-3 mb-5">
            <motion.span
              initial={shouldReduceMotion ? { width: 24 } : { width: 0 }}
              whileInView={{ width: 24 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, ease: MOTION_EASE.enter }}
              className="h-px bg-[#FF4A16] block"
              aria-hidden="true"
            />
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: -8 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1, ease: MOTION_EASE.enter }}
              className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium"
            >
              SYSTEM ARCHITECTURE
            </motion.div>
          </div>

          {/* Masked Line Reveal Headline */}
          <h2 className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-6 flex flex-col">
            <span className="overflow-mask block relative py-0.5">
              <motion.span
                initial={
                  shouldReduceMotion
                    ? { opacity: 1, y: 0 }
                    : { opacity: 0, y: "110%" }
                }
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.75, ease: MOTION_EASE.enter }}
                className="block font-normal"
              >
                Structure beneath the
              </motion.span>
            </span>
            <span className="overflow-mask block relative py-0.5">
              <motion.span
                initial={
                  shouldReduceMotion
                    ? { opacity: 1, y: 0 }
                    : { opacity: 0, y: "110%" }
                }
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.85, delay: 0.1, ease: MOTION_EASE.enter }}
                className="block font-editorial italic font-normal text-[#E9D0AD]"
              >
                intelligence.
              </motion.span>
            </span>
          </h2>

          <motion.p
            initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: MOTION_EASE.enter }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            APEX brings orchestration, context, execution, and interface into a layered system designed to coordinate complex work.
          </motion.p>
        </div>

        {/* 2-Column Architectural Layout: Suspended Plate Visualization + Interactive Exploration */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center">
          {/* Left Column: Suspended Architectural Plate Stack */}
          <div className="lg:col-span-6 bg-[#050607] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-10 relative overflow-hidden min-h-[480px] flex items-center justify-center">
            {/* Perspective Architectural Coordinate Grid Background */}
            <div className="absolute inset-0 architectural-grid opacity-25 pointer-events-none" />

            {/* Central Vertical Architectural Axis Line with illuminated pulse */}
            <div className="absolute top-8 bottom-8 left-1/2 -translate-x-1/2 w-px bg-[rgba(255,255,255,0.12)] pointer-events-none overflow-hidden">
              {!shouldReduceMotion && (
                <motion.div
                  animate={{ y: ["-100%", "200%"] }}
                  transition={{ duration: 3.6, repeat: Infinity, ease: "linear" }}
                  className="w-full h-20 bg-gradient-to-b from-transparent via-[#FF4A16] to-transparent shadow-[0_0_12px_#FF4A16]"
                />
              )}
            </div>

            {/* Exploded Architectural Monolithic Plates */}
            <div className="relative w-full max-w-[440px] flex flex-col gap-5 sm:gap-6 z-10 py-3">
              {ARCHITECTURE_TIERS.map((tier, idx) => {
                const isSelected = selectedTier === idx;
                return (
                  <motion.button
                    key={tier.id}
                    type="button"
                    onClick={() => setSelectedTier(idx)}
                    onMouseEnter={() => setSelectedTier(idx)}
                    initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 14 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{
                      duration: MOTION_TIMING.standard + idx * 0.08,
                      delay: idx * 0.09,
                      ease: MOTION_EASE.enter,
                    }}
                    className={`group w-full relative text-left p-4 sm:p-5 rounded-xl border transition-all duration-300 cursor-pointer focus-visible:outline-[#FF4A16] ${
                      isSelected
                        ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_28px_rgba(255,74,22,0.2)] -translate-y-1.5 scale-[1.01]"
                        : "bg-[#08090A]/90 border-[rgba(255,255,255,0.08)] opacity-60 hover:opacity-90 hover:border-[rgba(255,255,255,0.22)]"
                    }`}
                  >
                    {/* Layer Header */}
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span
                          className={`font-code text-xs font-semibold tracking-wider transition-colors duration-200 ${
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

                      {/* Active Status Beacon */}
                      {isSelected ? (
                        <div className="flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16] animate-pulse" />
                          <span className="font-code text-[10px] tracking-widest text-[#FF4A16] uppercase font-medium">
                            ACTIVE
                          </span>
                        </div>
                      ) : (
                        <span className="font-code text-[9px] tracking-widest text-[#737575] uppercase">
                          SUSPENDED
                        </span>
                      )}
                    </div>

                    <p className="text-[#B2B0AD] text-xs font-normal leading-relaxed mb-2">
                      {tier.summary}
                    </p>

                    <div className="font-code text-[10px] text-[#FF4A16]/80 tracking-wide">
                      {tier.specs}
                    </div>

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
                  </motion.button>
                );
              })}
            </div>
          </div>

          {/* Right Column: Explanatory Groups with Shared State Synchronized Selection */}
          <div className="lg:col-span-6 flex flex-col justify-between">
            <div className="space-y-3.5 mb-8" role="tablist">
              {ARCHITECTURE_TIERS.map((tier, idx) => {
                const isSelected = selectedTier === idx;
                return (
                  <div
                    key={tier.id}
                    role="tab"
                    tabIndex={0}
                    aria-selected={isSelected}
                    onClick={() => setSelectedTier(idx)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        setSelectedTier(idx);
                      }
                    }}
                    className={`p-5 sm:p-6 rounded-xl border transition-all duration-300 cursor-pointer focus-visible:outline-[#FF4A16] ${
                      isSelected
                        ? "bg-[#111315]/95 border-[rgba(255,255,255,0.22)] shadow-md"
                        : "bg-transparent border-transparent hover:border-[rgba(255,255,255,0.06)] opacity-50 hover:opacity-100"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="font-code text-xs font-semibold tracking-wider text-[#FF4A16]">
                          {tier.num} —
                        </span>
                        <h3 className="font-sans text-base sm:text-lg font-medium text-[#F5F3EF]">
                          {tier.name}
                        </h3>
                      </div>
                      <span className="font-code text-[10px] text-[#737575] tracking-widest uppercase">
                        {isSelected ? "EXPANDED" : "SELECT"}
                      </span>
                    </div>

                    <p className="text-[#B2B0AD] text-xs sm:text-sm leading-relaxed mb-3">
                      {tier.summary}
                    </p>

                    <AnimatePresence mode="wait">
                      {isSelected && (
                        <motion.ul
                          key={tier.id}
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          transition={{ duration: 0.28, ease: MOTION_EASE.enter }}
                          className="pt-3.5 border-t border-[rgba(255,255,255,0.08)] space-y-2 overflow-hidden"
                        >
                          {tier.details.map((detail, dIdx) => (
                            <li
                              key={dIdx}
                              className="flex items-start gap-2.5 font-code text-xs text-[#E9D0AD]/95"
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

            {/* Bottom Clarifying Notation + Analyzing Mascot at outer edge */}
            <div className="pt-6 border-t border-[rgba(255,255,255,0.08)] flex flex-wrap items-center justify-between gap-4 text-[#737575] font-code text-[10px] tracking-[0.2em] uppercase">
              <div className="flex items-center gap-4">
                <span>FOUR ARCHITECTURAL TIERS</span>
                <span className="text-[#737575]/40">·</span>
                <span>24 DEEP INTERNAL LAYERS</span>
              </div>

              {/* Analyzing Companion at outer edge */}
              <div className="flex items-center gap-3 opacity-80 hover:opacity-100 transition-opacity">
                <span className="text-[9px] text-[#8C9295] tracking-widest hidden sm:inline">TELEMETRY::INSPECT</span>
                <ApexMascot
                  variant="analyzing"
                  height={80}
                  animateIdle={true}
                  alt="APEX companion analyzing system architecture"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
