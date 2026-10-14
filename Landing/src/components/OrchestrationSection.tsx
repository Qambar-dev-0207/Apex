"use client";

import { useState } from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "motion/react";

interface WorkflowStage {
  id: string;
  title: string;
  line1: string;
  line2: string;
  technicalNote: string;
}

const ORCHESTRATION_STAGES: WorkflowStage[] = [
  {
    id: "intent",
    title: "INTENT",
    line1: "Understand",
    line2: "the objective.",
    technicalNote: "Gemini 2.0 Flash intent classification & sovereign invariant guardrails.",
  },
  {
    id: "plan",
    title: "PLAN",
    line1: "Decompose",
    line2: "into tasks.",
    technicalNote: "Directed Acyclic Graph (Task DAG) decomposition engine with isolated parallel sub-trees.",
  },
  {
    id: "delegate",
    title: "DELEGATE",
    line1: "Route to the",
    line2: "right agents.",
    technicalNote: "Groq LPU handles deterministic tools; local Ollama runs air-gapped tasks.",
  },
  {
    id: "execute",
    title: "EXECUTE",
    line1: "Coordinate",
    line2: "execution.",
    technicalNote: "Isolated sub-process sandboxes with real-time memory synchronization.",
  },
  {
    id: "verify",
    title: "VERIFY",
    line1: "Validate",
    line2: "and recover.",
    technicalNote: "AgentHarness execution wrapper with automated snapshot rollbacks.",
  },
];

/* Custom SVG Icons matching exact reference visual styling */
function IntentIcon({ isActive }: { isActive: boolean }) {
  return (
    <div
      className={`relative w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center transition-all duration-300 shrink-0 ${
        isActive
          ? "border border-[#FF4A16] bg-[#FF4A16]/20 shadow-[0_0_18px_rgba(255,74,22,0.8),inset_0_0_8px_rgba(255,74,22,0.5)]"
          : "border border-[rgba(255,255,255,0.22)] bg-[#0C0E10] text-[#8C9295]"
      }`}
    >
      <svg
        viewBox="0 0 24 24"
        className="w-4 h-4 sm:w-4.5 sm:h-4.5"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Outer subtle ring */}
        <circle
          cx="12"
          cy="12"
          r="9.5"
          stroke={isActive ? "#FF4A16" : "rgba(255,255,255,0.3)"}
          strokeWidth="1.2"
        />
        {/* Inner glowing crescent / aperture node */}
        <circle
          cx="12"
          cy="12"
          r="4.5"
          fill={isActive ? "#FF4A16" : "rgba(255,255,255,0.6)"}
        />
        <circle
          cx="10.5"
          cy="10.5"
          r="1.8"
          fill={isActive ? "#FFF0EB" : "rgba(255,255,255,0.9)"}
        />
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
      <svg
        viewBox="0 0 24 24"
        className="w-4 h-4 sm:w-4.5 sm:h-4.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Compass / drafting node */}
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
      <svg
        viewBox="0 0 24 24"
        className="w-4 h-4 sm:w-4.5 sm:h-4.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Branching routing node */}
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
      <svg
        viewBox="0 0 24 24"
        className="w-4 h-4 sm:w-4.5 sm:h-4.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Execution play triangle */}
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
      <svg
        viewBox="0 0 24 24"
        className="w-4 h-4 sm:w-4.5 sm:h-4.5"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        {/* Verification checkmark */}
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
      {/* Main Wide Panoramic Banner Container matching exact reference */}
      <div className="relative w-full min-h-[480px] sm:min-h-[520px] lg:min-h-[560px] flex flex-col justify-between overflow-hidden">
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
          {/* Subtle directional gradient on far-left to ensure typography contrast */}
          <div className="absolute inset-y-0 left-0 w-full sm:w-[50%] lg:w-[42%] bg-gradient-to-r from-[#050607]/85 via-[#050607]/40 to-transparent pointer-events-none" />
        </div>

        {/* Top/Middle Area: Left Editorial Typography */}
        <div className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-14 pt-12 sm:pt-14 lg:pt-16 pb-4 flex-1 flex flex-col justify-between pointer-events-none">
          <div className="max-w-[520px] pointer-events-auto">
            {/* Eyebrow: - THE ORCHESTRATION ENGINE */}
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 6 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
              className="flex items-center gap-2 mb-3.5 font-sans text-[11px] sm:text-xs tracking-[0.24em] text-[#8C9295] uppercase font-medium"
            >
              <span className="text-[#FF4A16] font-bold text-sm leading-none">—</span>
              <span>THE ORCHESTRATION ENGINE</span>
            </motion.div>

            {/* Headline: Complexity, brought into order. */}
            <h2 className="font-editorial text-4xl sm:text-5xl lg:text-[54px] xl:text-[60px] leading-[1.06] tracking-tight text-[#F5F3EF] mb-3.5">
              <span className="overflow-mask block relative py-0.5">
                <motion.span
                  initial={
                    shouldReduceMotion
                      ? { opacity: 1, y: 0 }
                      : { opacity: 0, y: "110%" }
                  }
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
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
                  transition={{ duration: 0.85, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                  className="block font-normal"
                >
                  brought into order.
                </motion.span>
              </span>
            </h2>

            {/* Subtitle Copy matching reference 2-line structure */}
            <motion.p
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="text-[#9A9FA1] text-[13px] sm:text-sm lg:text-[14.5px] font-normal leading-[1.5] max-w-[440px]"
            >
              A goal becomes a sequence of dependent
              <br className="hidden sm:inline" /> tasks, coordinated toward a shared result.
            </motion.p>
          </div>

          {/* Bottom Area: Connected 5-Stage Horizontal Workflow Track */}
          <div className="w-full pt-10 sm:pt-14 pb-4 pointer-events-auto">
            {/* Desktop Horizontal Connecting Track matching reference layout */}
            <div className="hidden md:flex items-start justify-between w-full relative">
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

                      {/* 2-line Sub-label description aligned under the stage title */}
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
                          className={`flex-1 h-[1px] transition-colors duration-300 ${
                            isPassed
                              ? "bg-[#FF4A16]"
                              : "bg-[rgba(255,255,255,0.22)]"
                          }`}
                        />
                        {/* Clean Arrowhead */}
                        <svg
                          viewBox="0 0 8 10"
                          className={`w-2 h-2.5 -ml-[1px] shrink-0 transition-colors duration-300 ${
                            isPassed
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
            <div className="md:hidden flex flex-col gap-2.5">
              {ORCHESTRATION_STAGES.map((stage, idx) => {
                const isActive = activeStage === idx;

                return (
                  <button
                    key={stage.id}
                    type="button"
                    onClick={() => setActiveStage(idx)}
                    className={`w-full flex items-start gap-3 p-3 rounded-lg border text-left transition-all cursor-pointer ${
                      isActive
                        ? "bg-[#111315]/90 border-[#FF4A16] shadow-[0_0_14px_rgba(255,74,22,0.25)]"
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
                <span className="text-[#F5F3EF]">{ORCHESTRATION_STAGES[activeStage].technicalNote}</span>
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
