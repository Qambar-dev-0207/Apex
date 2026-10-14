"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

interface LoopStage {
  id: string;
  step: string;
  label: string;
  title: string;
  description: string;
  implementedFeature: string;
}

const LOOP_STAGES: LoopStage[] = [
  {
    id: "observe",
    step: "01",
    label: "OBSERVE",
    title: "Runtime Context & State Monitoring",
    description: "Inspects execution signals, AST syntax validity, and system resource limits before each action.",
    implementedFeature: "Hardware vitals bridge & subprocess status listener in AgentHarness.",
  },
  {
    id: "act",
    step: "02",
    label: "ACT",
    title: "Isolated Sandbox Execution",
    description: "Executes atomic tool calls, code modifications, or swarm research inside isolated timeout boundaries.",
    implementedFeature: "asyncio execution harness with enforced timeout limits and memory caps.",
  },
  {
    id: "verify",
    step: "03",
    label: "VERIFY",
    title: "Socratic Invariant Probing",
    description: "Forces assertion checks against generated outputs to catch hallucinated references or test regressions.",
    implementedFeature: "Socratic gate validating syntax and schema compliance prior to state commit.",
  },
  {
    id: "recover",
    step: "04",
    label: "RECOVER",
    title: "Defensive Checkpoint Rollback",
    description: "Reverts uncommitted state instantly when an assertion fails or a tool throws an unrecoverable exception.",
    implementedFeature: "Atomic rollback snapshots preserving system integrity on external failures.",
  },
  {
    id: "continue",
    step: "05",
    label: "CONTINUE",
    title: "Reflected Resumption",
    description: "Reflects upon error traces, adapts the DAG topology, and safely resumes forward progress.",
    implementedFeature: "Self-healing retry loop updating failure memories in ChromaDB.",
  },
];

export default function EvolutionSection() {
  const [selectedStage, setSelectedStage] = useState<number>(2); // Default to "VERIFY"

  return (
    <section
      id="evolution"
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-32 sm:py-40 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)]"
      aria-label="APEX Recovery & Continuous Improvement Loop"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[840px] mb-20">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium mb-5"
          >
            EXECUTION / FEEDBACK
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-6"
          >
            Built to recover.{" "}
            <span className="font-editorial italic font-normal text-[#E9D0AD]">
              Designed to improve.
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            A coordinated system needs more than execution. It needs a way to observe outcomes, validate work, and respond when something fails.
          </motion.p>
        </div>

        {/* Closed-Loop Structural Pipeline */}
        <div className="bg-[#050607] border border-[rgba(255,255,255,0.1)] rounded-2xl p-8 sm:p-12 mb-12">
          {/* Closed Loop Visual Track */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 relative mb-12 pb-8 border-b border-[rgba(255,255,255,0.08)]">
            {LOOP_STAGES.map((stg, idx) => {
              const isSelected = selectedStage === idx;
              return (
                <button
                  key={stg.id}
                  type="button"
                  onClick={() => setSelectedStage(idx)}
                  className={`p-4 rounded-xl border text-left transition-all cursor-pointer ${
                    isSelected
                      ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_16px_rgba(255,74,22,0.2)]"
                      : "bg-[#08090A] border-[rgba(255,255,255,0.06)] hover:border-[rgba(255,255,255,0.2)] text-[#737575]"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-code text-[11px] font-semibold text-[#FF4A16]">
                      {stg.step}
                    </span>
                    {isSelected && (
                      <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16] animate-pulse" />
                    )}
                  </div>
                  <span
                    className={`font-code text-xs tracking-wider uppercase block mb-1 ${
                      isSelected ? "text-[#F5F3EF]" : "text-[#B2B0AD]"
                    }`}
                  >
                    {stg.label}
                  </span>
                  <span className="text-[11px] text-[#737575] line-clamp-1">
                    {stg.title}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Detailed Selected Stage Breakdown */}
          <AnimatePresence mode="wait">
            <motion.div
              key={selectedStage}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center bg-[#08090A] border border-[rgba(255,255,255,0.08)] rounded-xl p-6 sm:p-8"
            >
              <div className="lg:col-span-7">
                <div className="font-code text-[11px] tracking-[0.24em] text-[#FF4A16] uppercase font-semibold mb-2">
                  FEEDBACK STAGE {LOOP_STAGES[selectedStage].step} — {LOOP_STAGES[selectedStage].label}
                </div>
                <h3 className="font-sans text-xl sm:text-2xl font-medium text-[#F5F3EF] mb-3">
                  {LOOP_STAGES[selectedStage].title}
                </h3>
                <p className="text-[#B2B0AD] text-sm sm:text-base leading-relaxed mb-4">
                  {LOOP_STAGES[selectedStage].description}
                </p>
              </div>

              <div className="lg:col-span-5 bg-[#111315] border border-[rgba(255,255,255,0.06)] rounded-lg p-5 font-code text-xs">
                <span className="text-[#737575] text-[10px] tracking-wider uppercase block mb-2">
                  VERIFIED IMPLEMENTATION
                </span>
                <p className="text-[#E9D0AD] leading-relaxed">
                  {LOOP_STAGES[selectedStage].implementedFeature}
                </p>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Bottom Notation */}
        <div className="flex flex-wrap items-center justify-between gap-4 text-[#737575] font-code text-[11px] tracking-[0.2em] uppercase pt-6 border-t border-[rgba(255,255,255,0.08)]">
          <span>OBSERVE → ACT → VERIFY → RECOVER → CONTINUE</span>
          <span>CLOSED-LOOP RECOVERY BOUNDS</span>
        </div>
      </div>
    </section>
  );
}
