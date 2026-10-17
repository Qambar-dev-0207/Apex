"use client";

import { useState } from "react";
import Image from "next/image";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import ApexMascot from "./ApexMascot";
import { MOTION_EASE } from "../lib/motion";

interface WorkflowStage {
  id: string;
  title: string;
  line1: string;
  line2: string;
  summary: string;
  technicalNote: string;
  nodePos: { x: number; y: number };
}

const ORCHESTRATION_STAGES: WorkflowStage[] = [
  {
    id: "intent",
    title: "INTENT",
    line1: "Understand",
    line2: "the objective.",
    summary: "Parses natural human language into formal goal specifications and validates pre-execution invariant bounds.",
    technicalNote: "Gemini 2.0 Flash intent classification & sovereign invariant guardrails.",
    nodePos: { x: 80, y: 110 },
  },
  {
    id: "plan",
    title: "PLAN",
    line1: "Decompose",
    line2: "into tasks.",
    summary: "Builds a Directed Acyclic Graph (DAG) with topologically sorted sub-tasks and dependency contracts.",
    technicalNote: "Task DAG decomposition engine with parallelizable branch analysis.",
    nodePos: { x: 230, y: 110 },
  },
  {
    id: "delegate",
    title: "DELEGATE",
    line1: "Route to the",
    line2: "right agents.",
    summary: "Assigns each atomic task to specialized model providers (Gemini, Groq LPU, or local Ollama).",
    technicalNote: "Groq LPU handles deterministic tools; local Ollama runs air-gapped tasks.",
    nodePos: { x: 380, y: 110 },
  },
  {
    id: "execute",
    title: "EXECUTE",
    line1: "Coordinate",
    line2: "execution.",
    summary: "Executes tool calls in isolated Python sandboxes with memory synchronization.",
    technicalNote: "Isolated sub-process sandboxes with real-time memory synchronization.",
    nodePos: { x: 530, y: 110 },
  },
  {
    id: "verify",
    title: "VERIFY",
    line1: "Validate",
    line2: "and recover.",
    summary: "Validates execution outputs against invariants, triggering automated rollback if deviations occur.",
    technicalNote: "AgentHarness execution wrapper with automated snapshot rollbacks.",
    nodePos: { x: 680, y: 110 },
  },
];

/* SVG Icons for Stages */
function IntentIcon({ isActive }: { isActive: boolean }) {
  return (
    <div
      className={`relative w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-all duration-300 shrink-0 ${
        isActive
          ? "border border-[#FF4A16] bg-[#FF4A16]/20 shadow-[0_0_18px_rgba(255,74,22,0.8),inset_0_0_8px_rgba(255,74,22,0.5)]"
          : "border border-[rgba(255,255,255,0.22)] bg-[#0C0E10] text-[#8C9295]"
      }`}
    >
      <svg viewBox="0 0 24 24" className="w-4 h-4 sm:w-4.5 sm:h-4.5" fill="none">
        <circle cx="12" cy="12" r="9.5" stroke={isActive ? "#FF4A16" : "rgba(255,255,255,0.3)"} strokeWidth="1.2" />
        <circle cx="12" cy="12" r="4.5" fill={isActive ? "#FF4A16" : "rgba(255,255,255,0.6)"} />
        <circle cx="10.5" cy="10.5" r="1.8" fill={isActive ? "#FFF0EB" : "rgba(255,255,255,0.9)"} />
      </svg>
    </div>
  );
}

function PlanIcon({ isActive }: { isActive: boolean }) {
  return (
    <div
      className={`relative w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-all duration-300 shrink-0 ${
        isActive
          ? "border border-[#FF4A16] bg-[#FF4A16]/20 shadow-[0_0_18px_rgba(255,74,22,0.8)]"
          : "border border-[rgba(255,255,255,0.22)] bg-[#0C0E10] text-[#9A9FA1]"
      }`}
    >
      <svg viewBox="0 0 24 24" className="w-4 h-4 sm:w-4.5 sm:h-4.5" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" strokeOpacity="0.4" />
        <polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76" fill="currentColor" fillOpacity="0.15" />
      </svg>
    </div>
  );
}

function DelegateIcon({ isActive }: { isActive: boolean }) {
  return (
    <div
      className={`relative w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-all duration-300 shrink-0 ${
        isActive
          ? "border border-[#FF4A16] bg-[#FF4A16]/20 shadow-[0_0_18px_rgba(255,74,22,0.8)]"
          : "border border-[rgba(255,255,255,0.22)] bg-[#0C0E10] text-[#9A9FA1]"
      }`}
    >
      <svg viewBox="0 0 24 24" className="w-4 h-4 sm:w-4.5 sm:h-4.5" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="18" cy="6" r="2.5" />
        <circle cx="6" cy="12" r="2.5" />
        <circle cx="18" cy="18" r="2.5" />
        <path d="M8.5 12h3a4 4 0 0 0 4-4V6" />
        <path d="M11.5 12a4 4 0 0 1 4 4v2" />
      </svg>
    </div>
  );
}

function ExecuteIcon({ isActive }: { isActive: boolean }) {
  return (
    <div
      className={`relative w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-all duration-300 shrink-0 ${
        isActive
          ? "border border-[#FF4A16] bg-[#FF4A16]/20 shadow-[0_0_18px_rgba(255,74,22,0.8)]"
          : "border border-[rgba(255,255,255,0.22)] bg-[#0C0E10] text-[#9A9FA1]"
      }`}
    >
      <svg viewBox="0 0 24 24" className="w-4 h-4 sm:w-4.5 sm:h-4.5" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" strokeOpacity="0.4" />
        <polygon points="10 8 16 12 10 16 10 8" fill="currentColor" fillOpacity="0.7" />
      </svg>
    </div>
  );
}

function VerifyIcon({ isActive }: { isActive: boolean }) {
  return (
    <div
      className={`relative w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-all duration-300 shrink-0 ${
        isActive
          ? "border border-[#FF4A16] bg-[#FF4A16]/20 shadow-[0_0_18px_rgba(255,74,22,0.8)]"
          : "border border-[rgba(255,255,255,0.22)] bg-[#0C0E10] text-[#9A9FA1]"
      }`}
    >
      <svg viewBox="0 0 24 24" className="w-4 h-4 sm:w-4.5 sm:h-4.5" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="9" strokeOpacity="0.4" />
        <polyline points="8.5 12 11 14.5 15.5 9.5" />
      </svg>
    </div>
  );
}

export default function OrchestrationSection() {
  const [activeStage, setActiveStage] = useState<number>(0);
  const shouldReduceMotion = useReducedMotion();

  const getStageIcon = (idx: number, isActive: boolean) => {
    switch (idx) {
      case 0:
        return <IntentIcon isActive={isActive} />;
      case 1:
        return <PlanIcon isActive={isActive} />;
      case 2:
        return <DelegateIcon isActive={isActive} />;
      case 3:
        return <ExecuteIcon isActive={isActive} />;
      case 4:
        return <VerifyIcon isActive={isActive} />;
      default:
        return null;
    }
  };

  return (
    <section
      id="orchestration"
      className="relative w-full bg-[#050607] border-t border-[rgba(255,255,255,0.08)] select-none overflow-hidden"
      aria-label="The Orchestration Engine"
    >
      {/* Main Wide Panoramic Banner Container */}
      <div className="relative w-full min-h-[520px] sm:min-h-[580px] lg:min-h-[640px] flex flex-col justify-between overflow-hidden">
        {/* Background Artwork Canvas: Neural Branching DAG + APEX Robot Mascot at Laptop */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          <Image
            src="/apex-orchestration-bg.jpg"
            alt="APEX Orchestration Engine"
            fill
            priority
            sizes="100vw"
            quality={95}
            className="object-cover object-[center_42%] scale-[1.01]"
          />
          {/* Subtle directional gradient on left to ensure typography contrast */}
          <div className="absolute inset-y-0 left-0 w-full sm:w-[55%] lg:w-[45%] bg-gradient-to-r from-[#050607]/90 via-[#050607]/45 to-transparent pointer-events-none" />
          <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[#050607] to-transparent pointer-events-none" />
        </div>

        {/* Top/Middle Area: Left Editorial Typography & Right Coding Mascot */}
        <div className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-14 pt-12 sm:pt-16 lg:pt-20 pb-4 flex-1 flex flex-col justify-between pointer-events-none">
            {/* Left Editorial Copy Area (Span 8 cols) */}
            <div className="lg:col-span-8 max-w-[560px]">
              {/* Eyebrow: - THE ORCHESTRATION ENGINE */}
              <motion.div
                initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 6 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.45, ease: MOTION_EASE.enter }}
                className="flex items-center gap-2 mb-3.5 font-sans text-[11px] sm:text-xs tracking-[0.24em] text-[#8C9295] uppercase font-medium"
              >
                <span className="text-[#FF4A16] font-bold text-sm leading-none">—</span>
                <span>THE ORCHESTRATION ENGINE</span>
              </motion.div>

              {/* Headline: Complexity, brought into order. */}
              <h2 className="font-editorial text-4xl sm:text-5xl lg:text-[56px] xl:text-[64px] leading-[1.04] tracking-tight text-[#F5F3EF] mb-4">
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
                    Complexity,
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
                    className="block font-normal"
                  >
                    brought into <span className="font-editorial italic font-normal text-[#FF7A45]">order.</span>
                  </motion.span>
                </span>
              </h2>

              {/* Subtitle Copy */}
              <motion.p
                initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2, ease: MOTION_EASE.enter }}
                className="text-[#9A9FA1] text-[13px] sm:text-sm lg:text-[15px] font-normal leading-[1.6] max-w-[460px]"
              >
                A goal becomes a sequence of dependent
                <br className="hidden sm:inline" /> tasks, coordinated toward a shared result.
              </motion.p>
            </div>

          {/* Bottom Area: Connected 5-Stage Horizontal Workflow Track */}
          <div className="w-full pt-8 sm:pt-12 pb-4 pointer-events-auto">
            {/* Desktop Horizontal Connecting Track */}
            <div className="hidden md:flex items-start justify-between w-full relative" role="tablist">
              {ORCHESTRATION_STAGES.map((stage, idx) => {
                const isActive = activeStage === idx;
                const isPassed = activeStage > idx;
                const isLast = idx === ORCHESTRATION_STAGES.length - 1;

                return (
                  <div key={stage.id} className="flex-1 flex items-start">
                    {/* Stage Item Container */}
                    <div className="flex flex-col items-start group">
                      {/* Top Row: Icon + Title */}
                      <button
                        role="tab"
                        aria-selected={isActive}
                        type="button"
                        onClick={() => setActiveStage(idx)}
                        className="flex items-center gap-2.5 cursor-pointer text-left focus-visible:outline-[#FF4A16] rounded-md transition-transform hover:translate-y-[-1px]"
                      >
                        {/* Custom Stage Icon */}
                        {getStageIcon(idx, isActive)}

                        {/* Stage Name */}
                        <span
                          className={`font-code text-xs lg:text-[13px] tracking-[0.18em] uppercase font-bold transition-colors ${
                            isActive
                              ? "text-white"
                              : isPassed
                              ? "text-[#E0DFDC]"
                              : "text-[#B0B4B7] group-hover:text-white"
                          }`}
                        >
                          {stage.title}
                        </span>
                      </button>

                      {/* 2-line Sub-label description */}
                      <div className="mt-2 text-[11px] lg:text-[12px] text-[#8C9295] tracking-normal leading-[1.35] pl-[38px] sm:pl-[42px]">
                        <span className="block">{stage.line1}</span>
                        <span className="block">{stage.line2}</span>
                      </div>
                    </div>

                    {/* Connecting Line with Arrowhead in gap */}
                    {!isLast && (
                      <div
                        className="flex-1 flex items-center min-w-[24px] max-w-[120px] mx-2 lg:mx-4 mt-3.5 sm:mt-4 pointer-events-none"
                        aria-hidden="true"
                      >
                        {/* Thin horizontal line */}
                        <div
                          className={`flex-1 h-[1px] relative overflow-hidden transition-colors duration-300 ${
                            isPassed
                              ? "bg-[#FF4A16]"
                              : "bg-[rgba(255,255,255,0.22)]"
                          }`}
                        >
                          {isActive && !shouldReduceMotion && (
                            <motion.div
                              animate={{ x: ["-100%", "200%"] }}
                              transition={{ duration: 1.8, repeat: Infinity, ease: "linear" }}
                              className="w-8 h-full bg-gradient-to-r from-transparent via-[#FF4A16] to-transparent shadow-[0_0_8px_#FF4A16]"
                            />
                          )}
                        </div>
                        {/* Clean Arrowhead */}
                        <svg
                          viewBox="0 0 8 10"
                          className={`w-2 h-2.5 -ml-[1px] shrink-0 transition-colors duration-300 ${
                            isPassed || isActive
                              ? "text-[#FF4A16] fill-[#FF4A16]"
                              : "text-[rgba(255,255,255,0.35)] fill-[rgba(255,255,255,0.35)]"
                          }`}
                        >
                          <polygon points="0,0 8,5 0,10" />
                        </svg>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Mobile Vertical Connected Track */}
            <div className="md:hidden flex flex-col gap-2.5" role="tablist">
              {ORCHESTRATION_STAGES.map((stage, idx) => {
                const isActive = activeStage === idx;

                return (
                  <button
                    key={stage.id}
                    role="tab"
                    aria-selected={isActive}
                    type="button"
                    onClick={() => setActiveStage(idx)}
                    className={`w-full flex items-start gap-3 p-3 rounded-lg border text-left transition-all cursor-pointer focus-visible:outline-[#FF4A16] ${
                      isActive
                        ? "bg-[#111315]/95 border-[#FF4A16] shadow-[0_0_14px_rgba(255,74,22,0.25)]"
                        : "bg-[#08090A]/85 border-[rgba(255,255,255,0.08)]"
                    }`}
                  >
                    <div className="mt-0.5">{getStageIcon(idx, isActive)}</div>
                    <div>
                      <span className="font-code text-xs tracking-wider uppercase font-bold text-[#F5F3EF] block">
                        {stage.title}
                      </span>
                      <span className="text-[11px] text-[#8C9295] block mt-0.5 leading-tight">
                        {stage.line1} {stage.line2}
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Grounded Technical Specification Toast/Drawer on Click */}
            <div className="mt-5 pt-3 border-t border-[rgba(255,255,255,0.07)] flex flex-wrap items-center justify-between gap-2.5 font-code text-[11px] text-[#8C9295]">
              <div className="flex items-center gap-2">
                <span className="text-[#FF4A16] font-semibold">STAGE 0{activeStage + 1} //</span>
                <AnimatePresence mode="wait">
                  <motion.span
                    key={activeStage}
                    initial={{ opacity: 0, x: -4 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: 4 }}
                    transition={{ duration: 0.22 }}
                    className="text-[#F5F3EF]"
                  >
                    {ORCHESTRATION_STAGES[activeStage].technicalNote}
                  </motion.span>
                </AnimatePresence>
              </div>
              <span className="text-[#8C9295]/60 uppercase tracking-widest text-[10px]">
                DETERMINISTIC DAG DISPATCH
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
