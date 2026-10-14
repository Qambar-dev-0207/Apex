"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";

interface LoopStage {
  id: string;
  step: string;
  title: string;
  role: string;
  description: string;
  telemetry: string;
}

const LOOP_STAGES: LoopStage[] = [
  {
    id: "observe",
    step: "01",
    title: "OBSERVE",
    role: "Sensory Telemetry Bridge",
    description: "Monitors tool executions, output streams, return codes, and system events in real time.",
    telemetry: "Real-time process stdout/stderr stream parsing with invariant pattern detectors.",
  },
  {
    id: "act",
    step: "02",
    title: "ACT",
    role: "Deterministic Agent Execution",
    description: "Applies tools, mutates local state, and completes atomic sub-tasks within isolated boundaries.",
    telemetry: "Scoped sub-process environments prevent uncontained state side-effects.",
  },
  {
    id: "verify",
    step: "03",
    title: "VERIFY",
    role: "Socratic Invariant Check",
    description: "Validates task output against expected schemas and invariant contracts before progressing.",
    telemetry: "Rigorous assertion gates fail fast if output violates logical consistency.",
  },
  {
    id: "recover",
    step: "04",
    title: "RECOVER",
    role: "AgentHarness Rollback",
    description: "On detected validation failures, reverts system state to the last clean snapshot checkpoint.",
    telemetry: "Git/filesystem state snapshot rollback prevents compounding hallucinated errors.",
  },
  {
    id: "continue",
    step: "05",
    title: "CONTINUE",
    role: "Replanning & Execution Resume",
    description: "Generates an alternate execution branch informed by failure telemetry and continues the goal.",
    telemetry: "Dynamic DAG recalculation with failure context appended to working memory.",
  },
];

export default function EvolutionSection() {
  const [selectedStage, setSelectedStage] = useState<number>(2); // Default to "VERIFY"
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="evolution"
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-32 sm:py-40 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Recovery & Continuous Improvement Loop"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[840px] mb-20">
          {/* Eyebrow with horizontal line draw */}
          <div className="flex items-center gap-3 mb-5">
            <motion.span
              initial={shouldReduceMotion ? { width: 24 } : { width: 0 }}
              whileInView={{ width: 24 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              className="h-px bg-[#FF4A16] block"
              aria-hidden="true"
            />
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, x: 0 } : { opacity: 0, x: -8 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.5, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium"
            >
              EXECUTION / FEEDBACK
            </motion.div>
          </div>

          {/* Masked Line Reveal Headline */}
          <h2 className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-6 flex flex-col">
            <span className="overflow-mask block relative py-0.5">
              <motion.span
                initial={
                  shouldReduceMotion
                    ? { opacity: 1, y: 0 }
                    : { opacity: 0, y: "110%", filter: "blur(3px)" }
                }
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                viewport={{ once: true }}
                transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
                className="block font-normal"
              >
                Built to recover.
              </motion.span>
            </span>
            <span className="overflow-mask block relative py-0.5">
              <motion.span
                initial={
                  shouldReduceMotion
                    ? { opacity: 1, y: 0 }
                    : { opacity: 0, y: "110%", filter: "blur(3px)" }
                }
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                viewport={{ once: true }}
                transition={{ duration: 0.85, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                className="block font-editorial italic font-normal text-[#E9D0AD]"
              >
                Designed to improve.
              </motion.span>
            </span>
          </h2>

          <motion.p
            initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
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
                  className={`flex flex-col items-start p-4 rounded-xl border text-left transition-all duration-200 cursor-pointer ${
                    isSelected
                      ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_16px_rgba(255,74,22,0.15)]"
                      : "bg-[#08090A] border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)]"
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-2">
                    <span
                      className={`font-code text-xs font-semibold ${
                        isSelected ? "text-[#FF4A16]" : "text-[#737575]"
                      }`}
                    >
                      {stg.step}
                    </span>
                    {isSelected && (
                      <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16] animate-pulse" />
                    )}
                  </div>
                  <span
                    className={`font-code text-xs tracking-wider uppercase font-semibold mb-1 ${
                      isSelected ? "text-[#F5F3EF]" : "text-[#B2B0AD]"
                    }`}
                  >
                    {stg.title}
                  </span>
                  <span className="text-[11px] text-[#737575] line-clamp-1">
                    {stg.role}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Detailed Stage Feedback Display */}
          <div className="min-h-[140px] flex items-center">
            <AnimatePresence mode="wait">
              <motion.div
                key={selectedStage}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
                className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center bg-[#08090A] border border-[rgba(255,255,255,0.08)] rounded-xl p-6 sm:p-8"
              >
                <div className="lg:col-span-7">
                  <div className="flex items-center gap-2 font-code text-xs text-[#FF4A16] uppercase font-semibold mb-2">
                    <span>STAGE {LOOP_STAGES[selectedStage].step} — {LOOP_STAGES[selectedStage].role}</span>
                  </div>
                  <h3 className="font-sans text-xl sm:text-2xl font-medium text-[#F5F3EF] mb-3">
                    {LOOP_STAGES[selectedStage].title} Pipeline
                  </h3>
                  <p className="text-[#B2B0AD] text-sm sm:text-base leading-relaxed mb-4">
                    {LOOP_STAGES[selectedStage].description}
                  </p>
                </div>

                <div className="lg:col-span-5 bg-[#111315] border border-[rgba(255,255,255,0.06)] rounded-lg p-5 font-code text-xs">
                  <span className="text-[#737575] text-[10px] tracking-wider uppercase block mb-2">
                    HARNESS TELEMETRY
                  </span>
                  <p className="text-[#E9D0AD] leading-relaxed">
                    {LOOP_STAGES[selectedStage].telemetry}
                  </p>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* Factually Accurate Disclaimer */}
        <div className="pt-6 border-t border-[rgba(255,255,255,0.08)] flex flex-wrap items-center justify-between gap-4 text-[#737575] font-code text-[11px] tracking-[0.2em] uppercase">
          <span>SELF-HEALING AGENT HARNESS</span>
          <span>DETERMINISTIC SNAPSHOT RESTORATION</span>
        </div>
      </div>
    </section>
  );
}
