"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";

interface ModelEndpoint {
  id: string;
  name: string;
  role: string;
  latency: string;
  description: string;
  routingTrigger: string;
}

const MODEL_ENDPOINTS: ModelEndpoint[] = [
  {
    id: "gemini",
    name: "Gemini 2.0 Flash",
    role: "Strategic Planning & Intent Routing",
    latency: "High-reasoning tier",
    description: "Analyzes unstructured intent, normalizes query boundaries, and decomposes multi-step goals into dependency-ordered task graphs.",
    routingTrigger: "Activated on complex reasoning, schema compilation, and strategic planning goals.",
  },
  {
    id: "groq",
    name: "Groq LPU Inference",
    role: "Low-Latency Edge Tool Execution",
    latency: "Sub-100ms inference tier",
    description: "Executes deterministic function calling, atomic tool selection, and rapid code validation cycles with instantaneous response.",
    routingTrigger: "Activated for fast reflexive tool selection, parameter extraction, and status validation.",
  },
  {
    id: "ollama",
    name: "Ollama / Local Sovereignty",
    role: "Air-Gapped Private Execution",
    latency: "Zero external network tier",
    description: "Runs local DeepSeek and Qwen models directly on private hardware without sending sensitive code or credentials over the network.",
    routingTrigger: "Activated during air-gapped operations, offline failovers, or confidential token policies.",
  },
];

export default function ModelRoutingSection() {
  const [selectedEndpoint, setSelectedEndpoint] = useState<number>(0);
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="models"
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-32 sm:py-40 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Multi-Model Intelligence"
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
              MODEL ORCHESTRATION
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
                One objective.
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
                Multiple minds.
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
            APEX coordinates model access and specialized execution paths around the work that needs to be done.
          </motion.p>
        </div>

        {/* Branching Architectural Composition */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center bg-[#050607] border border-[rgba(255,255,255,0.1)] rounded-2xl p-8 sm:p-12">
          {/* Left Column: Central Architectural Router Node + Branching Paths */}
          <div className="lg:col-span-5 flex flex-col items-center justify-center p-6 border-b lg:border-b-0 lg:border-r border-[rgba(255,255,255,0.08)]">
            {/* Central Router Element */}
            <div className="w-20 h-20 rounded-2xl bg-[#111315] border border-[rgba(255,255,255,0.2)] flex items-center justify-center relative mb-6 shadow-md">
              <span className="w-2.5 h-2.5 rounded-full bg-[#FF4A16] animate-pulse" />
              <span className="absolute -top-3 font-code text-[9px] tracking-widest text-[#FF4A16] uppercase bg-[#08090A] px-2 py-0.5 rounded border border-[#FF4A16]/40">
                KERNEL ROUTER
              </span>
            </div>

            <span className="font-sans text-base font-medium text-[#F5F3EF] mb-1">
              APEX Model Router
            </span>
            <span className="font-code text-xs text-[#737575] text-center max-w-[260px] leading-relaxed mb-6">
              Classifies semantic bounds and dynamically routes execution streams
            </span>

            {/* Downward/Outward Branching Vector Indicators */}
            <div className="flex items-center gap-2 text-xs font-code text-[#737575]">
              <span>3 VERIFIED TIERS</span>
              <span>•</span>
              <span className="text-[#FF4A16]">0 LOCK-IN</span>
            </div>
          </div>

          {/* Right Column: Model Endpoint Cards / Selectors */}
          <div className="lg:col-span-7 flex flex-col gap-4">
            {MODEL_ENDPOINTS.map((endpoint, idx) => {
              const isSelected = selectedEndpoint === idx;
              return (
                <button
                  key={endpoint.id}
                  type="button"
                  onClick={() => setSelectedEndpoint(idx)}
                  className={`p-6 rounded-xl border text-left transition-all duration-300 cursor-pointer ${
                    isSelected
                      ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_20px_rgba(255,74,22,0.15)] -translate-x-1"
                      : "bg-[#08090A]/80 border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)] opacity-70 hover:opacity-100"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <span
                        className={`w-2 h-2 rounded-full transition-colors ${
                          isSelected ? "bg-[#FF4A16]" : "bg-[rgba(255,255,255,0.2)]"
                        }`}
                      />
                      <h3 className="font-sans text-base sm:text-lg font-medium text-[#F5F3EF]">
                        {endpoint.name}
                      </h3>
                    </div>
                    <span className="font-code text-[11px] text-[#737575]">
                      {endpoint.latency}
                    </span>
                  </div>

                  <p className="font-code text-xs text-[#FF4A16] mb-3">
                    {endpoint.role}
                  </p>

                  <p className="text-[#B2B0AD] text-xs sm:text-sm leading-relaxed mb-3">
                    {endpoint.description}
                  </p>

                  <AnimatePresence mode="wait">
                    {isSelected && (
                      <motion.div
                        key={endpoint.id}
                        initial={{ opacity: 0, y: -4 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -4 }}
                        transition={{ duration: 0.24, ease: [0.16, 1, 0.3, 1] }}
                        className="pt-3 border-t border-[rgba(255,255,255,0.08)] font-code text-[11px] text-[#E9D0AD]/90 overflow-hidden"
                      >
                        <span className="text-[#737575] mr-2">DISPATCH POLICY:</span>
                        {endpoint.routingTrigger}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </button>
              );
            })}
          </div>
        </div>

        {/* Factually Accurate Technical Boundary Note */}
        <div className="mt-8 pt-6 border-t border-[rgba(255,255,255,0.08)] flex flex-wrap items-center justify-between gap-4 text-[#737575] font-code text-[11px] tracking-[0.2em] uppercase">
          <span>ORCHESTRATION LAYER ≠ RAW LLM CALL</span>
          <span>MULTI-STEP CONTEXT MERGING</span>
        </div>
      </div>
    </section>
  );
}
