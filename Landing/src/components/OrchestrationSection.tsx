"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

interface WorkflowStep {
  id: string;
  num: string;
  label: string;
  title: string;
  description: string;
  technicalNote: string;
}

const WORKFLOW_STEPS: WorkflowStep[] = [
  {
    id: "intent",
    num: "01",
    label: "INTENT",
    title: "Understand the objective",
    description: "Understand the objective and identify the appropriate approach.",
    technicalNote: "Gemini 2.0 Flash classifies prompt invariants and normalizes task scope.",
  },
  {
    id: "plan",
    num: "02",
    label: "PLAN",
    title: "Decompose into Task DAGs",
    description: "Decompose the work into dependency-ordered tasks.",
    technicalNote: "Constructs Directed Acyclic Graphs with topological sort order and failure boundaries.",
  },
  {
    id: "delegate",
    num: "03",
    label: "DELEGATE",
    title: "Route to specialized paths",
    description: "Route individual tasks to the appropriate agent or tool.",
    technicalNote: "Dispatches atomic subtasks across WebSearch, CodeEngine, and Sandbox agents.",
  },
  {
    id: "execute",
    num: "04",
    label: "EXECUTE",
    title: "Coordinate parallel paths",
    description: "Coordinate independent work while respecting dependencies.",
    technicalNote: "Non-blocking asyncio TaskGroups execute parallel streams under hardware thermal bounds.",
  },
  {
    id: "verify",
    num: "05",
    label: "VERIFY",
    title: "Check results & assert invariants",
    description: "Check results and follow the existing recovery workflow when needed.",
    technicalNote: "Socratic invariant gates validate outputs before committing state to working memory.",
  },
];

export default function OrchestrationSection() {
  const [activeStep, setActiveStep] = useState<number>(0);

  return (
    <section
      id="orchestration"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-32 sm:py-40 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)]"
      aria-label="APEX Orchestration Workflow Engine"
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
            THE ORCHESTRATION ENGINE
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-6"
          >
            Complexity, brought into{" "}
            <span className="font-editorial italic font-normal text-[#E9D0AD]">
              order.
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            A goal becomes a sequence of dependent tasks, coordinated toward a shared result.
          </motion.p>
        </div>

        {/* Continuous Line & Node Workflow Diagram (Interactive) */}
        <div className="bg-[#08090A] border border-[rgba(255,255,255,0.1)] rounded-2xl p-8 sm:p-12 mb-12">
          {/* Desktop Horizontal Workflow Navigation */}
          <div className="hidden lg:grid grid-cols-5 gap-4 relative mb-12 pb-8 border-b border-[rgba(255,255,255,0.08)]">
            {/* Connecting Track Line behind buttons */}
            <div className="absolute top-5 left-10 right-10 h-px bg-[rgba(255,255,255,0.12)] z-0" />

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
                        ? "bg-[#FF4A16] border-[#FF4A16] shadow-[0_0_16px_rgba(255,74,22,0.4)] scale-110"
                        : isPassed
                        ? "bg-[#111315] border-[#FF4A16]/60 text-[#FF4A16]"
                        : "bg-[#08090A] border-[rgba(255,255,255,0.2)] text-[#737575] hover:border-[rgba(255,255,255,0.4)]"
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
                    className={`font-code text-xs tracking-[0.2em] uppercase font-medium transition-colors mb-1.5 ${
                      isSelected ? "text-[#F5F3EF]" : "text-[#737575] group-hover:text-[#B2B0AD]"
                    }`}
                  >
                    {step.label}
                  </span>

                  {/* Short Title */}
                  <span className="font-sans text-xs text-[#B2B0AD] max-w-[140px] leading-snug">
                    {step.title}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Mobile Vertical Workflow Selector */}
          <div className="lg:hidden flex flex-col gap-3 mb-8">
            {WORKFLOW_STEPS.map((step, idx) => {
              const isSelected = activeStep === idx;
              return (
                <button
                  key={step.id}
                  type="button"
                  onClick={() => setActiveStep(idx)}
                  className={`flex items-center justify-between p-4 rounded-xl border text-left transition-all ${
                    isSelected
                      ? "bg-[#111315] border-[#FF4A16] text-[#F5F3EF]"
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

          {/* Selected Stage Explanation & Architectural Trace */}
          <AnimatePresence mode="wait">
            <motion.div
              key={activeStep}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center bg-[#050607] border border-[rgba(255,255,255,0.08)] rounded-xl p-6 sm:p-8"
            >
              <div className="lg:col-span-7">
                <div className="flex items-center gap-2.5 font-code text-[10px] tracking-[0.24em] text-[#FF4A16] uppercase font-semibold mb-2">
                  <span>STAGE {WORKFLOW_STEPS[activeStep].num} ARCHITECTURE</span>
                </div>
                <h3 className="font-sans text-xl sm:text-2xl font-medium text-[#F5F3EF] mb-3">
                  {WORKFLOW_STEPS[activeStep].title}
                </h3>
                <p className="text-[#B2B0AD] text-sm sm:text-base leading-relaxed mb-4">
                  {WORKFLOW_STEPS[activeStep].description}
                </p>
              </div>

              <div className="lg:col-span-5 bg-[#111315] border border-[rgba(255,255,255,0.06)] rounded-lg p-5 font-code text-xs">
                <span className="text-[#737575] text-[10px] tracking-wider uppercase block mb-2">
                  CORE SPECIFICATION
                </span>
                <p className="text-[#E9D0AD] leading-relaxed">
                  {WORKFLOW_STEPS[activeStep].technicalNote}
                </p>
              </div>
            </motion.div>
          </AnimatePresence>
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
