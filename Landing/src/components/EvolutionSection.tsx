"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import ApexMascot from "./ApexMascot";
import { MOTION_EASE } from "../lib/motion";

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
  const [selectedStage, setSelectedStage] = useState<number>(3); // Default to "RECOVER" to highlight the recovery capability
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="evolution"
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-16 sm:py-20 lg:py-24 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Recovery & Continuous Improvement Loop"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[840px] mb-10 lg:mb-14">
          {/* Eyebrow with horizontal line draw */}
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
              className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium"
            >
              EXECUTION / FEEDBACK
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
                Built to recover.
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
                Designed to improve.
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
            A coordinated system needs more than execution. It needs a way to observe outcomes, validate work, and respond when something fails.
          </motion.p>
        </div>

        {/* Closed-Loop Structural Pipeline Container */}
        <div className="bg-[#050607] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-10 lg:p-12 mb-8 relative overflow-hidden">
          {/* Subtle architectural grid */}
          <div className="absolute inset-0 architectural-grid opacity-15 pointer-events-none" />

          {/* Top Stage Control Strip */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 relative mb-8 pb-6 border-b border-[rgba(255,255,255,0.08)] z-10" role="tablist">
            {LOOP_STAGES.map((stg, idx) => {
              const isSelected = selectedStage === idx;
              const isRecovery = stg.id === "recover";
              return (
                <button
                  key={stg.id}
                  role="tab"
                  aria-selected={isSelected}
                  type="button"
                  onClick={() => setSelectedStage(idx)}
                  className={`flex flex-col items-start p-3.5 sm:p-4 rounded-xl border text-left transition-all duration-200 cursor-pointer focus-visible:outline-[#FF4A16] ${
                    isSelected
                      ? isRecovery
                        ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_20px_rgba(255,74,22,0.3)] translate-y-[-2px]"
                        : "bg-[#111315] border-[#FF4A16] shadow-[0_0_16px_rgba(255,74,22,0.2)] translate-y-[-2px]"
                      : "bg-[#08090A] border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)]"
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-1.5">
                    <span
                      className={`font-code text-xs font-semibold ${
                        isSelected ? "text-[#FF4A16]" : "text-[#737575]"
                      }`}
                    >
                      {stg.step}
                    </span>
                    {isSelected ? (
                      <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16] animate-pulse" />
                    ) : isRecovery ? (
                      <span className="font-code text-[9px] text-[#FF4A16]/70 uppercase tracking-widest">
                        FAILOVER
                      </span>
                    ) : null}
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

          {/* Expansive Architectural Curved Workflow Schematic */}
          <div className="w-full py-6 mb-8 flex justify-center items-center overflow-x-auto z-10 relative">
            <svg
              viewBox="0 0 880 200"
              className="w-full max-w-[840px] h-auto text-white overflow-visible select-none"
            >
              {/* Background Reference Track Lines */}
              <line
                x1="80"
                y1="60"
                x2="800"
                y2="60"
                stroke="rgba(255,255,255,0.12)"
                strokeWidth="1.5"
              />

              {/* Progressive Main Forward Execution Path */}
              <motion.path
                d="M 80 60 L 260 60 L 440 60 L 800 60"
                fill="none"
                stroke={selectedStage !== 3 ? "#FF4A16" : "rgba(255,255,255,0.25)"}
                strokeWidth="2"
                initial={shouldReduceMotion ? { pathLength: 1 } : { pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.2, ease: [0.16, 1, 0.3, 1] }}
              />

              {/* Curved Distinct Recovery Failover Branch: From VERIFY (440,60) -> down to RECOVER (620,140) -> up to CONTINUE (800,60) */}
              <motion.path
                d="M 440 60 C 440 140, 520 140, 620 140 C 720 140, 800 140, 800 60"
                fill="none"
                stroke={selectedStage === 3 ? "#FF4A16" : "rgba(255,74,22,0.4)"}
                strokeWidth={selectedStage === 3 ? "2.5" : "1.5"}
                strokeDasharray="6 4"
                initial={shouldReduceMotion ? { pathLength: 1 } : { pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.4, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
                className="transition-colors duration-300"
              />

              {/* Rollback Reconnect Branch to ACT (State Restoration Loop): From RECOVER (620, 140) back to ACT (260, 60) */}
              <motion.path
                d="M 620 140 C 500 180, 320 180, 260 70"
                fill="none"
                stroke={selectedStage === 3 ? "rgba(255,74,22,0.7)" : "rgba(255,255,255,0.1)"}
                strokeWidth="1.2"
                strokeDasharray="4 4"
                initial={shouldReduceMotion ? { pathLength: 1 } : { pathLength: 0 }}
                whileInView={{ pathLength: 1 }}
                viewport={{ once: true }}
                transition={{ duration: 1.6, delay: 0.5, ease: [0.16, 1, 0.3, 1] }}
              />

              {/* Recovery Branch Label Badge */}
              <g transform="translate(620, 168)">
                <rect
                  x="-120"
                  y="-10"
                  width="240"
                  height="20"
                  rx="4"
                  fill="#08090A"
                  stroke={selectedStage === 3 ? "#FF4A16" : "rgba(255,74,22,0.3)"}
                  strokeWidth="1"
                />
                <text
                  x="0"
                  y="3"
                  textAnchor="middle"
                  fill={selectedStage === 3 ? "#FF4A16" : "#E9D0AD"}
                  fontSize="9"
                  fontFamily="monospace"
                  letterSpacing="0.12em"
                  fontWeight="600"
                >
                  AGENTHARNESS SNAPSHOT ROLLBACK GATE
                </text>
              </g>

              {/* State Restored Loop Annotation */}
              <text
                x="410"
                y="185"
                textAnchor="middle"
                fill={selectedStage === 3 ? "#FF4A16" : "#737575"}
                fontSize="8"
                fontFamily="monospace"
                letterSpacing="0.1em"
              >
                ↺ REVERTS UNVERIFIED MUTATIONS TO CHECKPOINT
              </text>

              {/* Node 01: OBSERVE */}
              <g
                className="cursor-pointer"
                onClick={() => setSelectedStage(0)}
              >
                <circle
                  cx="80"
                  cy="60"
                  r={selectedStage === 0 ? "10" : "7"}
                  fill={selectedStage === 0 ? "#FF4A16" : "#111315"}
                  stroke={selectedStage === 0 ? "#FFF0EB" : "rgba(255,255,255,0.4)"}
                  strokeWidth="2"
                />
                {selectedStage === 0 && (
                  <circle cx="80" cy="60" r="15" fill="none" stroke="#FF4A16" strokeWidth="1" opacity="0.6" className="animate-ping" />
                )}
                <text x="80" y="38" textAnchor="middle" fill={selectedStage === 0 ? "#FF4A16" : "#B2B0AD"} fontSize="11" fontFamily="monospace" fontWeight="bold">01 OBSERVE</text>
                <text x="80" y="85" textAnchor="middle" fill="#737575" fontSize="8" fontFamily="monospace">STDOUT / TELEMETRY</text>
              </g>

              {/* Node 02: ACT */}
              <g
                className="cursor-pointer"
                onClick={() => setSelectedStage(1)}
              >
                <circle
                  cx="260"
                  cy="60"
                  r={selectedStage === 1 ? "10" : "7"}
                  fill={selectedStage === 1 ? "#FF4A16" : "#111315"}
                  stroke={selectedStage === 1 ? "#FFF0EB" : "rgba(255,255,255,0.4)"}
                  strokeWidth="2"
                />
                {selectedStage === 1 && (
                  <circle cx="260" cy="60" r="15" fill="none" stroke="#FF4A16" strokeWidth="1" opacity="0.6" className="animate-ping" />
                )}
                <text x="260" y="38" textAnchor="middle" fill={selectedStage === 1 ? "#FF4A16" : "#B2B0AD"} fontSize="11" fontFamily="monospace" fontWeight="bold">02 ACT</text>
                <text x="260" y="85" textAnchor="middle" fill="#737575" fontSize="8" fontFamily="monospace">ATOMIC EXECUTION</text>
              </g>

              {/* Node 03: VERIFY */}
              <g
                className="cursor-pointer"
                onClick={() => setSelectedStage(2)}
              >
                <circle
                  cx="440"
                  cy="60"
                  r={selectedStage === 2 ? "10" : "7"}
                  fill={selectedStage === 2 ? "#FF4A16" : "#111315"}
                  stroke={selectedStage === 2 ? "#FFF0EB" : "rgba(255,255,255,0.4)"}
                  strokeWidth="2"
                />
                {selectedStage === 2 && (
                  <circle cx="440" cy="60" r="15" fill="none" stroke="#FF4A16" strokeWidth="1" opacity="0.6" className="animate-ping" />
                )}
                <text x="440" y="38" textAnchor="middle" fill={selectedStage === 2 ? "#FF4A16" : "#B2B0AD"} fontSize="11" fontFamily="monospace" fontWeight="bold">03 VERIFY</text>
                <text x="440" y="85" textAnchor="middle" fill="#737575" fontSize="8" fontFamily="monospace">INVARIANT GATE</text>
              </g>

              {/* Node 04: RECOVER (On Distinct Lower Branch) */}
              <g
                className="cursor-pointer"
                onClick={() => setSelectedStage(3)}
              >
                <circle
                  cx="620"
                  cy="140"
                  r={selectedStage === 3 ? "12" : "8"}
                  fill={selectedStage === 3 ? "#FF4A16" : "#111315"}
                  stroke="#FF4A16"
                  strokeWidth="2"
                />
                {selectedStage === 3 && (
                  <circle cx="620" cy="140" r="18" fill="none" stroke="#FF4A16" strokeWidth="1.5" opacity="0.7" className="animate-ping" />
                )}
                <text x="620" y="122" textAnchor="middle" fill="#FF4A16" fontSize="11" fontFamily="monospace" fontWeight="bold">04 RECOVER</text>
              </g>

              {/* Node 05: CONTINUE */}
              <g
                className="cursor-pointer"
                onClick={() => setSelectedStage(4)}
              >
                <circle
                  cx="800"
                  cy="60"
                  r={selectedStage === 4 ? "10" : "7"}
                  fill={selectedStage === 4 ? "#FF4A16" : "#111315"}
                  stroke={selectedStage === 4 ? "#FFF0EB" : "rgba(255,255,255,0.4)"}
                  strokeWidth="2"
                />
                {selectedStage === 4 && (
                  <circle cx="800" cy="60" r="15" fill="none" stroke="#FF4A16" strokeWidth="1" opacity="0.6" className="animate-ping" />
                )}
                <text x="800" y="38" textAnchor="middle" fill={selectedStage === 4 ? "#FF4A16" : "#B2B0AD"} fontSize="11" fontFamily="monospace" fontWeight="bold">05 CONTINUE</text>
                <text x="800" y="85" textAnchor="middle" fill="#737575" fontSize="8" fontFamily="monospace">REPLAN & ADVANCE</text>
              </g>

              {/* Controlled Amber Path Progression Pulse */}
              {!shouldReduceMotion && (
                <motion.circle
                  r="3.5"
                  fill="#FF4A16"
                  initial={{ cx: 80, cy: 60, opacity: 0 }}
                  animate={{
                    cx: [80, 260, 440, 620, 800],
                    cy: [60, 60, 60, 140, 60],
                    opacity: [0, 1, 1, 1, 0],
                  }}
                  transition={{
                    duration: 4,
                    repeat: 2, // Composed resting state: runs twice then settles
                    ease: "easeInOut",
                  }}
                />
              )}
            </svg>
          </div>

          {/* Synchronized Detail Drawer */}
          <div className="min-h-[140px] flex items-center z-10 relative">
            <AnimatePresence mode="wait">
              <motion.div
                key={selectedStage}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.25, ease: MOTION_EASE.enter }}
                className="w-full grid grid-cols-1 lg:grid-cols-12 gap-6 lg:gap-8 items-center bg-[#08090A] border border-[rgba(255,255,255,0.08)] rounded-xl p-5 sm:p-8"
              >
                <div className="lg:col-span-6">
                  <div className="flex items-center gap-2 font-code text-xs text-[#FF4A16] uppercase font-semibold mb-2">
                    <span>STAGE {LOOP_STAGES[selectedStage].step} — {LOOP_STAGES[selectedStage].role}</span>
                  </div>
                  <h3 className="font-sans text-xl sm:text-2xl font-medium text-[#F5F3EF] mb-2.5">
                    {LOOP_STAGES[selectedStage].title} Pipeline
                  </h3>
                  <p className="text-[#B2B0AD] text-sm sm:text-base leading-relaxed">
                    {LOOP_STAGES[selectedStage].description}
                  </p>
                </div>

                <div className="lg:col-span-4 bg-[#111315] border border-[rgba(255,255,255,0.06)] rounded-lg p-4 sm:p-5 font-code text-xs">
                  <span className="text-[#737575] text-[10px] tracking-wider uppercase block mb-1.5">
                    HARNESS TELEMETRY
                  </span>
                  <p className="text-[#E9D0AD] leading-relaxed">
                    {LOOP_STAGES[selectedStage].telemetry}
                  </p>
                </div>

                {/* Companion Mascot */}
                <div className="lg:col-span-2 flex flex-col items-center justify-center pt-2 lg:pt-0">
                  <ApexMascot
                    variant={LOOP_STAGES[selectedStage].id === "recover" ? "determined" : "focused"}
                    height={76}
                    animateIdle={true}
                    alt={
                      LOOP_STAGES[selectedStage].id === "recover"
                        ? "APEX companion determined to rollback state"
                        : "APEX companion monitoring loop execution"
                    }
                  />
                  <span className="font-code text-[9px] text-[#737575] tracking-widest mt-2 uppercase">
                    HARNESS::{LOOP_STAGES[selectedStage].id.toUpperCase()}
                  </span>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* Factually Accurate Disclaimer */}
        <div className="pt-4 border-t border-[rgba(255,255,255,0.08)] flex flex-wrap items-center justify-between gap-4 text-[#737575] font-code text-[11px] tracking-[0.2em] uppercase">
          <span>SELF-HEALING AGENT HARNESS</span>
          <span>DETERMINISTIC SNAPSHOT RESTORATION // ILLUSTRATIVE WORKFLOW</span>
        </div>
      </div>
    </section>
  );
}

