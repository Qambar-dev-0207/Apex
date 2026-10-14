"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import ApexMascot, { MascotVariant } from "./ApexMascot";

interface WorkflowStep {
  id: string;
  num: string;
  label: string;
  title: string;
  description: string;
  technicalNote: string;
  mascotVariant: MascotVariant;
  mascotAlt: string;
  graphRole: string;
}

const WORKFLOW_STEPS: WorkflowStep[] = [
  {
    id: "intent",
    num: "01",
    label: "Intent",
    title: "Understand the objective",
    description: "Analyze the objective, detect boundaries, and identify the appropriate routing approach without assumptions.",
    technicalNote: "Gemini 2.0 Flash classifies intent into atomic tool schemas and invariant guardrails.",
    mascotVariant: "coding",
    mascotAlt: "APEX companion parsing system intent",
    graphRole: "Root Dispatcher",
  },
  {
    id: "plan",
    num: "02",
    label: "Plan",
    title: "Decompose into Task DAGs",
    description: "Break the overarching goal down into dependency-ordered, directed acyclic tasks.",
    technicalNote: "DAG compiler resolves step dependencies and isolates parallel sub-trees.",
    mascotVariant: "building",
    mascotAlt: "APEX companion assembling task DAG hierarchy",
    graphRole: "DAG Tree Assembly",
  },
  {
    id: "delegate",
    num: "03",
    label: "Delegate",
    title: "Route to specialized paths",
    description: "Direct individual tasks to the optimal model, local tool, or specialized execution agent.",
    technicalNote: "Groq LPU handles deterministic tools; local Ollama takes sovereign air-gapped tasks.",
    mascotVariant: "coding",
    mascotAlt: "APEX companion delegating to multi-model workers",
    graphRole: "Multi-Model Router",
  },
  {
    id: "execute",
    num: "04",
    label: "Execute",
    title: "Coordinate parallel work",
    description: "Execute independent tasks concurrently while strictly respecting upstream prerequisite outputs.",
    technicalNote: "Isolated sub-process sandboxes with real-time memory synchronization.",
    mascotVariant: "building",
    mascotAlt: "APEX companion running sandbox execution",
    graphRole: "Sandboxed Worker",
  },
  {
    id: "verify",
    num: "05",
    label: "Verify",
    title: "Check results & assert invariants",
    description: "Validate task output against safety rules and trigger self-healing recovery if an anomaly occurs.",
    technicalNote: "AgentHarness execution wrapper with automated snapshot rollbacks.",
    mascotVariant: "coding",
    mascotAlt: "APEX companion verifying invariant integrity",
    graphRole: "Invariant Guard",
  },
];

export default function OrchestrationSection() {
  const [activeStep, setActiveStep] = useState<number>(0);
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="orchestration"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-28 sm:py-36 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Orchestration Workflow Engine"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[840px] mb-16 sm:mb-20">
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
              THE ORCHESTRATION ENGINE
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
                transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
                className="block font-normal"
              >
                Complexity, brought into
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
                className="block font-editorial italic font-normal text-[#FF7A45]"
              >
                order.
              </motion.span>
            </span>
          </h2>

          <motion.p
            initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#9A9FA1] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            A goal becomes a sequence of dependent tasks, coordinated toward a shared result.
          </motion.p>
        </div>

        {/* Continuous Line & Node Workflow Diagram (Interactive DAG Model) */}
        <div className="bg-[#08090A] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-10 lg:p-12 mb-12 relative overflow-hidden">
          {/* Subtle Technical Architectural Grid Backdrop */}
          <div className="absolute inset-0 architectural-grid opacity-15 pointer-events-none" />

          {/* Illustrative Label in corner */}
          <div className="flex items-center justify-between pb-6 mb-8 border-b border-[rgba(255,255,255,0.08)]">
            <span className="font-code text-[10px] tracking-[0.24em] text-[#737575] uppercase">
              WORKFLOW PIPELINE // TASK DAG VISUALIZATION
            </span>
            <span className="font-code text-[10px] tracking-[0.2em] text-[#FF4A16] uppercase">
              STAGE {WORKFLOW_STEPS[activeStep].num} OF 05
            </span>
          </div>

          {/* Desktop Horizontal Workflow Navigation with SVG DAG Connector Track */}
          <div className="hidden lg:grid grid-cols-5 gap-4 relative mb-12 pb-6">
            {/* SVG Connecting Track Line */}
            <svg
              className="absolute top-5 left-12 right-12 w-[calc(100%-6rem)] h-2 z-0 pointer-events-none"
              preserveAspectRatio="none"
              aria-hidden="true"
            >
              <line
                x1="0%"
                y1="50%"
                x2="100%"
                y2="50%"
                stroke="rgba(255,255,255,0.14)"
                strokeWidth="1.5"
                strokeDasharray="4 4"
              />
              <motion.line
                x1="0%"
                y1="50%"
                x2={`${(activeStep / 4) * 100}%`}
                y2="50%"
                stroke="#FF4A16"
                strokeWidth="2"
                transition={{ duration: 0.4 }}
              />
            </svg>

            {WORKFLOW_STEPS.map((step, idx) => {
              const isSelected = activeStep === idx;
              const isPassed = activeStep > idx;
              return (
                <button
                  key={step.id}
                  type="button"
                  onClick={() => setActiveStep(idx)}
                  className="group relative flex flex-col items-center text-center cursor-pointer z-10 focus-visible:outline-[#FF4A16] py-1"
                >
                  {/* Node Dot / Marker */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center border transition-all duration-300 mb-4 ${
                      isSelected
                        ? "bg-[#FF4A16] border-[#FF4A16] shadow-[0_0_20px_rgba(255,74,22,0.5)] scale-110"
                        : isPassed
                        ? "bg-[#111315] border-[#FF4A16]/70 text-[#FF4A16]"
                        : "bg-[#08090A] border-[rgba(255,255,255,0.2)] text-[#737575] group-hover:border-[rgba(255,255,255,0.45)]"
                    }`}
                  >
                    <span
                      className={`font-code text-xs font-semibold ${
                        isSelected ? "text-white" : isPassed ? "text-[#FF4A16]" : "text-[#737575]"
                      }`}
                    >
                      {step.num}
                    </span>
                  </div>

                  {/* Stage Name */}
                  <span
                    className={`font-code text-xs tracking-[0.2em] uppercase font-semibold transition-colors duration-200 mb-1 ${
                      isSelected ? "text-[#F5F3EF]" : "text-[#737575] group-hover:text-[#B2B0AD]"
                    }`}
                  >
                    {step.label}
                  </span>

                  <span className="font-sans text-xs text-[#737575] max-w-[140px] truncate">
                    {step.title}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Mobile Vertical Connected Flow */}
          <div className="lg:hidden flex flex-col gap-3 mb-8">
            {WORKFLOW_STEPS.map((step, idx) => {
              const isSelected = activeStep === idx;
              return (
                <button
                  key={step.id}
                  type="button"
                  onClick={() => setActiveStep(idx)}
                  className={`w-full flex items-center justify-between p-4 rounded-xl border text-left transition-all duration-200 cursor-pointer ${
                    isSelected
                      ? "bg-[#111315] border-[#FF4A16] text-[#F5F3EF] shadow-[0_0_12px_rgba(255,74,22,0.15)]"
                      : "bg-[#08090A] border-[rgba(255,255,255,0.08)] text-[#737575]"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="font-code text-xs font-semibold text-[#FF4A16]">
                      {step.num}
                    </span>
                    <span className="font-code text-xs tracking-wider uppercase">
                      {step.label}
                    </span>
                  </div>
                  <span className="font-sans text-xs text-[#B2B0AD]">{step.title}</span>
                </button>
              );
            })}
          </div>

          {/* Selected Stage Explanation + Companion Mascot with clean crossfade */}
          <div className="min-h-[170px] flex items-center">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeStep}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -6 }}
                transition={{ duration: 0.26, ease: [0.16, 1, 0.3, 1] }}
                className="w-full grid grid-cols-1 lg:grid-cols-12 gap-8 items-center bg-[#050607] border border-[rgba(255,255,255,0.08)] rounded-xl p-6 sm:p-8"
              >
                <div className="lg:col-span-6">
                  <div className="flex items-center gap-2.5 font-code text-[10px] tracking-[0.24em] text-[#FF4A16] uppercase font-semibold mb-2">
                    <span>STAGE {WORKFLOW_STEPS[activeStep].num} // {WORKFLOW_STEPS[activeStep].graphRole}</span>
                  </div>
                  <h3 className="font-sans text-xl sm:text-2xl font-medium text-[#F5F3EF] mb-3">
                    {WORKFLOW_STEPS[activeStep].title}
                  </h3>
                  <p className="text-[#9A9FA1] text-sm sm:text-base leading-relaxed mb-4">
                    {WORKFLOW_STEPS[activeStep].description}
                  </p>
                </div>

                <div className="lg:col-span-4 bg-[#111315] border border-[rgba(255,255,255,0.06)] rounded-lg p-5 font-code text-xs">
                  <span className="text-[#737575] text-[10px] tracking-wider uppercase block mb-2">
                    CORE SPECIFICATION
                  </span>
                  <p className="text-[#F3F4F2] leading-relaxed">
                    {WORKFLOW_STEPS[activeStep].technicalNote}
                  </p>
                </div>

                {/* Companion Mascot at edge of orchestration card */}
                <div className="lg:col-span-2 flex flex-col items-center justify-center pt-2 lg:pt-0">
                  <ApexMascot
                    variant={WORKFLOW_STEPS[activeStep].mascotVariant}
                    height={86}
                    animateIdle={true}
                    alt={WORKFLOW_STEPS[activeStep].mascotAlt}
                  />
                  <span className="font-code text-[9px] text-[#737575] tracking-widest mt-2 uppercase">
                    SYS::{WORKFLOW_STEPS[activeStep].id.toUpperCase()}
                  </span>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* Bottom Sequence Notation */}
        <div className="flex flex-wrap items-center justify-between gap-4 text-[#737575] font-code text-[11px] tracking-[0.22em] uppercase pt-6 border-t border-[rgba(255,255,255,0.08)]">
          <span>INTENT → PLAN → DELEGATE → EXECUTE → VERIFY</span>
          <span>DETERMINISTIC DAG DISPATCH</span>
        </div>
      </div>
    </section>
  );
}
