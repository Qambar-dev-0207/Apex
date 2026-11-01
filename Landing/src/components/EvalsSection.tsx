"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import { Zap, Brain, ShieldCheck, Search, ArrowUpRight, CheckCircle2 } from "lucide-react";
import ApexMascot from "./ApexMascot";
import { MOTION_EASE } from "../lib/motion";

interface EvalPillar {
  id: string;
  num: string;
  title: string;
  headline: string;
  badge: string;
  accent: string;
  icon: typeof Zap;
  metrics: { label: string; value: string; detail: string }[];
  summary: string;
  technicalNote: string;
}

const EVAL_PILLARS: EvalPillar[] = [
  {
    id: "speed",
    num: "01",
    title: "Speed & Latency",
    headline: "Deterministic 0ms bypasses & sub-10µs routing",
    badge: "0.003ms Fast Path",
    accent: "#FF4A16",
    icon: Zap,
    metrics: [
      { label: "Deterministic Regex Skip", value: "0.003 ms", detail: "p95 latency (0ms LLM skip)" },
      { label: "Reflex Scout Intent", value: "0.008 ms", detail: "p95 sub-10µs decision" },
      { label: "Desktop AppLauncher", value: "1.08 ms", detail: "Mean execution (p95: 5.99ms)" },
      { label: "CodeCompass AST Query", value: "5.75 ms", detail: "Token-efficient symbol query" },
    ],
    summary:
      "Deterministic intent matching skips cloud LLM latency entirely, executing local commands in single-digit microseconds.",
    technicalNote:
      "Measured across 100 consecutive trials on Python 3.13 / Windows 11 host architecture.",
  },
  {
    id: "quality",
    num: "02",
    title: "Answer Quality & Reasoning",
    headline: "100% algorithmic synthesis & topological DAG plans",
    badge: "100% Pass Rate",
    accent: "#E9D0AD",
    icon: Brain,
    metrics: [
      { label: "HumanEval-Lite Synthesis", value: "5 / 5", detail: "22/22 unit assertions passed (100%)" },
      { label: "Task DAG Topological Order", value: "100%", detail: "Zero cyclic dependency failures" },
      { label: "Socratic Critique Gate", value: "Active", detail: "Hypothesis & blind-spot probing" },
      { label: "Supercomputer UI Formatting", value: "Verified", detail: "Zero-truncation multi-stream panels" },
    ],
    summary:
      "Autonomous code generation passes 100% of benchmark unit assertions with strict dependency ordering across multi-step goals.",
    technicalNote:
      "Evaluated against canonical algorithmic challenges (Two Sum, Palindrome, Longest Substring, Interval Merge, Binary Search).",
  },
  {
    id: "integrity",
    num: "03",
    title: "System Integrity & Safety",
    headline: "OS filesystem sandboxing & bit-for-bit SHA256 rollbacks",
    badge: "100% Defense",
    accent: "#10B981",
    icon: ShieldCheck,
    metrics: [
      { label: "Protected File Shield", value: "100%", detail: ".env, .git/config, and ../ traversal blocked" },
      { label: "Atomic Multi-Edit Rollback", value: "SHA256", detail: "Bit-for-bit exact file preservation" },
      { label: "Duplicate Collision Guard", value: "Enforced", detail: "Ambiguous edits aborted on 2x match" },
      { label: "Tool Schema Compliance", value: "57 / 57", detail: "22 DAG Tools + 35 AgentHarness Tools valid" },
    ],
    summary:
      "Guaranteed state integrity with pre-execution snapshots, sandbox isolation, and automatic rollback on partial failures.",
    technicalNote:
      "Verified via test_harness_atomic_multi_edit_rollback with automated sha256 checksum validation.",
  },
  {
    id: "retrieval",
    num: "04",
    title: "Semantic Retrieval & Memory",
    headline: "Zero-loss vector recall across sessions & AST trees",
    badge: "Recall@3 = 1.0",
    accent: "#38BDF8",
    icon: Search,
    metrics: [
      { label: "ChromaDB Vector Recall@3", value: "1.00", detail: "Perfect hit rate across semantic queries" },
      { label: "ChromaDB Precision@3 / MRR", value: "1.00", detail: "Mean reciprocal rank 1.0" },
      { label: "CodeCompass AST Symbol Recall", value: "5 / 5", detail: "100% symbol discovery across 39 modules" },
      { label: "Automated Pytest Suite", value: "473 / 473", detail: "100% operational test pass rate" },
    ],
    summary:
      "High-dimensional vector indexing ensures relevant directives, history, and codebase symbols are available at planning time.",
    technicalNote:
      "Tested via cosine similarity across 5 simulated project memories with ChromaDB PersistentClient.",
  },
];

export default function EvalsSection() {
  const [selectedPillar, setSelectedPillar] = useState<number>(0);
  const shouldReduceMotion = useReducedMotion();
  const current = EVAL_PILLARS[selectedPillar];

  return (
    <section
      id="evals"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-20 sm:py-28 lg:py-32 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Empirical Benchmark Evaluations"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[880px] mb-12 lg:mb-16">
          {/* Eyebrow */}
          <div className="flex items-center gap-3 mb-4">
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
              className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium flex items-center gap-2"
            >
              <span>EMPIRICAL BENCHMARKS</span>
              <span className="text-[#FF4A16]/70">·</span>
              <span className="text-[#FF4A16]">473 TESTS VERIFIED</span>
            </motion.div>
          </div>

          {/* Masked Line Reveal Headline */}
          <h2 className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-5 flex flex-col">
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
                Four sovereign pillars.
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
                Empirically validated.
              </motion.span>
            </span>
          </h2>

          <motion.p
            initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: MOTION_EASE.enter }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[660px]"
          >
            APEX is rigorously measured across speed, answer quality, filesystem integrity, and semantic retrieval to guarantee deterministic performance under production load.
          </motion.p>
        </div>

        {/* 4-Pillar Interactive Telemetry Dashboard */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start mb-8">
          {/* Left Column: 4 Pillar Selection Tabs */}
          <div className="lg:col-span-5 flex flex-col gap-3" role="tablist" aria-label="Evaluation Pillars">
            {EVAL_PILLARS.map((pillar, idx) => {
              const isSelected = selectedPillar === idx;
              const Icon = pillar.icon;

              return (
                <button
                  key={pillar.id}
                  role="tab"
                  aria-selected={isSelected}
                  type="button"
                  onClick={() => setSelectedPillar(idx)}
                  className={`p-5 rounded-xl border text-left transition-all duration-300 cursor-pointer focus-visible:outline-[#FF4A16] relative overflow-hidden group ${
                    isSelected
                      ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_24px_rgba(255,74,22,0.2)] translate-x-1"
                      : "bg-[#08090A]/80 border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)] opacity-70 hover:opacity-100"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2.5">
                      <span className="font-code text-xs font-semibold text-[#FF4A16]">
                        {pillar.num}
                      </span>
                      <span className="w-1 h-1 rounded-full bg-[rgba(255,255,255,0.2)]" />
                      <span className="font-sans text-sm sm:text-base font-semibold text-[#F5F3EF]">
                        {pillar.title}
                      </span>
                    </div>

                    <span
                      className={`font-code text-[10px] tracking-wider uppercase px-2 py-0.5 rounded ${
                        isSelected
                          ? "bg-[#FF4A16]/20 text-[#FF4A16] border border-[#FF4A16]/40"
                          : "bg-white/5 text-[#8C9295]"
                      }`}
                    >
                      {pillar.badge}
                    </span>
                  </div>

                  <p className="text-[#8C9295] text-xs leading-relaxed mb-3">
                    {pillar.headline}
                  </p>

                  <div className="flex items-center justify-between pt-2 border-t border-[rgba(255,255,255,0.06)] font-code text-[10px]">
                    <span className="text-[#737575] uppercase tracking-wider">
                      {isSelected ? "ACTIVE INSPECTION" : "SELECT TO VIEW"}
                    </span>
                    <Icon size={14} className={isSelected ? "text-[#FF4A16]" : "text-[#737575]"} />
                  </div>

                  {/* Corner Accent */}
                  {isSelected && (
                    <span className="absolute top-0 right-0 w-2 h-2 border-t border-r border-[#FF4A16]" />
                  )}
                </button>
              );
            })}
          </div>

          {/* Right Column: Detailed Metric Telemetry View */}
          <div className="lg:col-span-7 bg-[#08090A] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-8 lg:p-10 relative overflow-hidden flex flex-col justify-between min-h-[480px]">
            {/* Subtle background grid */}
            <div className="absolute inset-0 architectural-grid opacity-20 pointer-events-none" />

            {/* Top Bar */}
            <div className="relative z-10 flex items-center justify-between pb-4 border-b border-[rgba(255,255,255,0.08)] mb-6 font-code text-xs">
              <div className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full bg-[#10B981] shadow-[0_0_8px_#10B981] animate-pulse" />
                <span className="text-[#F5F3EF] uppercase tracking-wider font-semibold">
                  TELEMETRY MATRIX // PILLAR 0{selectedPillar + 1}
                </span>
              </div>
              <span className="text-[#8C9295] text-[10px] tracking-widest uppercase">
                PYTEST & HARNESS BENCH
              </span>
            </div>

            {/* Main Content Area */}
            <AnimatePresence mode="wait">
              <motion.div
                key={current.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                transition={{ duration: 0.35, ease: MOTION_EASE.enter }}
                className="relative z-10 flex-1 flex flex-col justify-between"
              >
                <div>
                  <div className="mb-6">
                    <span className="font-code text-[11px] text-[#FF4A16] tracking-widest uppercase font-semibold block mb-1">
                      {current.title} SPECIFICATION
                    </span>
                    <h3 className="font-editorial text-2xl sm:text-3xl text-[#F5F3EF] mb-2 font-normal">
                      {current.headline}
                    </h3>
                    <p className="text-[#B2B0AD] text-xs sm:text-sm leading-relaxed">
                      {current.summary}
                    </p>
                  </div>

                  {/* 4 Metric Telemetry Tiles */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 mb-6">
                    {current.metrics.map((metric, mIdx) => (
                      <div
                        key={mIdx}
                        className="bg-[#111315]/90 border border-[rgba(255,255,255,0.08)] rounded-xl p-4 flex flex-col justify-between hover:border-[rgba(255,255,255,0.18)] transition-all"
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-code text-[10px] text-[#8C9295] uppercase tracking-wider truncate">
                            {metric.label}
                          </span>
                          <CheckCircle2 size={13} className="text-[#10B981] shrink-0" />
                        </div>
                        <div className="font-code text-xl sm:text-2xl font-bold text-[#F5F3EF] tracking-tight mb-1">
                          {metric.value}
                        </div>
                        <span className="text-[10px] font-code text-[#E9D0AD]/80">
                          {metric.detail}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Technical Note & Link to Full Documentation */}
                <div className="pt-4 border-t border-[rgba(255,255,255,0.08)] flex flex-wrap items-center justify-between gap-3 text-[11px] font-code text-[#8C9295]">
                  <span className="text-[10px] text-[#737575] leading-relaxed max-w-[460px]">
                    ▸ {current.technicalNote}
                  </span>

                  <a
                    href="https://github.com/Qambar-dev-0207/Apex/blob/main/docs/EVALUATIONS.md"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 text-[#FF4A16] hover:text-white transition-colors uppercase tracking-wider text-[10px] font-semibold"
                  >
                    <span>Read EVALUATIONS.md</span>
                    <ArrowUpRight size={12} />
                  </a>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* Section Footer Bar with Companion */}
        <div className="pt-6 border-t border-[rgba(255,255,255,0.06)] flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4 text-[#737575] font-code text-[10px] tracking-[0.2em] uppercase">
            <span>AUTOMATED EVALUATION HARNESS</span>
            <span className="text-[#737575]/40">·</span>
            <span>22 CANONICAL DAG TOOLS</span>
            <span className="text-[#737575]/40">·</span>
            <span>35 AGENTHARNESS TOOLS</span>
            <span className="text-[#737575]/40">·</span>
            <span className="text-[#10B981]">100% PASS RATE</span>
          </div>

          <div className="flex items-center gap-3 opacity-80 hover:opacity-100 transition-opacity">
            <span className="font-code text-[9px] text-[#8C9295] uppercase hidden sm:inline">EVALS::VERIFIED</span>
            <ApexMascot
              variant="proud"
              height={70}
              animateIdle={true}
              alt="APEX companion verifying empirical benchmarks"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
