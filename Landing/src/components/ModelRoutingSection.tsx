"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import ApexMascot from "./ApexMascot";
import { MOTION_EASE, MOTION_TIMING } from "../lib/motion";

interface ModelEndpoint {
  id: string;
  name: string;
  role: string;
  tier: string;
  description: string;
  routingTrigger: string;
}

const MODEL_ENDPOINTS: ModelEndpoint[] = [
  {
    id: "gemini",
    name: "Gemini 2.0 Flash",
    role: "Strategic Planning & Intent Routing",
    tier: "High-reasoning tier",
    description: "Analyzes unstructured intent, normalizes query boundaries, and decomposes multi-step goals into dependency-ordered task graphs.",
    routingTrigger: "Activated on complex reasoning, schema compilation, and strategic planning goals.",
  },
  {
    id: "groq",
    name: "Groq LPU Inference",
    role: "Low-Latency Edge Tool Execution",
    tier: "Sub-100ms inference tier",
    description: "Executes deterministic function calling, atomic tool selection, and rapid code validation cycles with instantaneous response.",
    routingTrigger: "Activated for fast reflexive tool selection, parameter extraction, and status validation.",
  },
  {
    id: "ollama",
    name: "Ollama / Local Sovereignty",
    role: "Air-Gapped Private Execution",
    tier: "Zero external network tier",
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
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-28 sm:py-36 lg:py-44 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Multi-Model Intelligence"
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
                    : { opacity: 0, y: "110%" }
                }
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.75, ease: MOTION_EASE.enter }}
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
                    : { opacity: 0, y: "110%" }
                }
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.85, delay: 0.1, ease: MOTION_EASE.enter }}
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
            transition={{ duration: 0.6, delay: 0.2, ease: MOTION_EASE.enter }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            APEX coordinates model access and specialized execution paths around the work that needs to be done.
          </motion.p>
        </div>

        {/* Branching Architectural Composition */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 lg:gap-14 items-center bg-[#050607] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-10 lg:p-12 relative overflow-hidden">
          {/* Subtle grid background */}
          <div className="absolute inset-0 architectural-grid opacity-20 pointer-events-none" />

          {/* Left Column: Central Architectural Router Node + SVG Radiating Conduits */}
          <div className="lg:col-span-5 flex flex-col items-center justify-center p-6 border-b lg:border-b-0 lg:border-r border-[rgba(255,255,255,0.08)] relative z-10">
            {/* Central Kernel Router Element */}
            <motion.div
              initial={shouldReduceMotion ? { scale: 1, opacity: 1 } : { scale: 0.9, opacity: 0 }}
              whileInView={{ scale: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, ease: MOTION_EASE.enter }}
              className="w-24 h-24 rounded-2xl bg-[#111315] border border-[rgba(255,255,255,0.2)] flex flex-col items-center justify-center relative mb-5 shadow-lg group"
            >
              <div className="w-3 h-3 rounded-full bg-[#FF4A16] shadow-[0_0_12px_#FF4A16] animate-pulse mb-1.5" />
              <span className="font-code text-[9px] tracking-widest text-[#FF4A16] uppercase font-bold">
                KERNEL
              </span>
              <span className="font-code text-[8px] tracking-widest text-[#8C9295] uppercase">
                ROUTER
              </span>

              {/* Corner marks */}
              <span className="absolute top-0 right-0 w-2 h-2 border-t border-r border-[#FF4A16]/60" />
              <span className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-[#FF4A16]/60" />
            </motion.div>

            <span className="font-sans text-base font-medium text-[#F5F3EF] mb-1">
              APEX Model Router
            </span>
            <span className="font-code text-xs text-[#737575] text-center max-w-[280px] leading-relaxed mb-6">
              Classifies semantic bounds and dynamically routes execution streams
            </span>

            {/* Visual SVG Branching Conduits */}
            <svg viewBox="0 0 320 120" className="w-full max-w-[300px] h-auto text-white overflow-visible">
              {/* Route Path 1 (Top / Gemini) */}
              <path
                d="M 160 10 C 160 30, 60 40, 60 90"
                fill="none"
                stroke={selectedEndpoint === 0 ? "#FF4A16" : "rgba(255,255,255,0.15)"}
                strokeWidth={selectedEndpoint === 0 ? "2" : "1.2"}
                strokeDasharray={selectedEndpoint === 0 ? "4 4" : "none"}
                className="transition-colors duration-300"
              />
              {/* Route Path 2 (Middle / Groq) */}
              <path
                d="M 160 10 L 160 90"
                fill="none"
                stroke={selectedEndpoint === 1 ? "#FF4A16" : "rgba(255,255,255,0.15)"}
                strokeWidth={selectedEndpoint === 1 ? "2" : "1.2"}
                strokeDasharray={selectedEndpoint === 1 ? "4 4" : "none"}
                className="transition-colors duration-300"
              />
              {/* Route Path 3 (Bottom / Ollama) */}
              <path
                d="M 160 10 C 160 30, 260 40, 260 90"
                fill="none"
                stroke={selectedEndpoint === 2 ? "#FF4A16" : "rgba(255,255,255,0.15)"}
                strokeWidth={selectedEndpoint === 2 ? "2" : "1.2"}
                strokeDasharray={selectedEndpoint === 2 ? "4 4" : "none"}
                className="transition-colors duration-300"
              />

              {/* Endpoint Nodes */}
              <circle cx="60" cy="90" r="4" fill={selectedEndpoint === 0 ? "#FF4A16" : "rgba(255,255,255,0.4)"} />
              <circle cx="160" cy="90" r="4" fill={selectedEndpoint === 1 ? "#FF4A16" : "rgba(255,255,255,0.4)"} />
              <circle cx="260" cy="90" r="4" fill={selectedEndpoint === 2 ? "#FF4A16" : "rgba(255,255,255,0.4)"} />
            </svg>
          </div>

          {/* Right Column: Interactive Provider Cards + Dynamic Detail Drawer */}
          <div className="lg:col-span-7 flex flex-col justify-between relative z-10" role="tablist">
            <div className="space-y-3.5 mb-6">
              {MODEL_ENDPOINTS.map((endpoint, idx) => {
                const isSelected = selectedEndpoint === idx;
                return (
                  <button
                    key={endpoint.id}
                    role="tab"
                    aria-selected={isSelected}
                    type="button"
                    onClick={() => setSelectedEndpoint(idx)}
                    className={`w-full text-left p-5 rounded-xl border transition-all duration-300 cursor-pointer focus-visible:outline-[#FF4A16] ${
                      isSelected
                        ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_24px_rgba(255,74,22,0.18)] translate-x-1"
                        : "bg-[#08090A]/90 border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)] opacity-70 hover:opacity-100"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-sans text-sm sm:text-base font-semibold text-[#F5F3EF]">
                        {endpoint.name}
                      </span>
                      <span
                        className={`font-code text-[10px] tracking-wider uppercase font-medium ${
                          isSelected ? "text-[#FF4A16]" : "text-[#737575]"
                        }`}
                      >
                        {endpoint.tier}
                      </span>
                    </div>

                    <div className="font-code text-xs text-[#8C9295] mb-2.5">
                      {endpoint.role}
                    </div>

                    <p className="text-[#B2B0AD] text-xs sm:text-[13px] leading-relaxed">
                      {endpoint.description}
                    </p>

                    {isSelected && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        transition={{ duration: 0.24, ease: MOTION_EASE.interface }}
                        className="mt-3 pt-3 border-t border-[rgba(255,255,255,0.08)] font-code text-[11px] text-[#E9D0AD]/90 flex items-center gap-2"
                      >
                        <span className="text-[#FF4A16]">TRIGGER //</span>
                        <span>{endpoint.routingTrigger}</span>
                      </motion.div>
                    )}
                  </button>
                );
              })}
            </div>

            {/* Bottom Notation Bar + Connected Mascot */}
            <div className="pt-4 border-t border-[rgba(255,255,255,0.08)] flex items-center justify-between gap-4">
              <span className="font-code text-[10px] text-[#737575] tracking-widest uppercase">
                ZERO VENDOR LOCK-IN // ADAPTIVE MODEL ARBITRAGE
              </span>

              <div className="flex items-center gap-2 opacity-85 hover:opacity-100 transition-opacity">
                <span className="font-code text-[9px] text-[#8C9295] uppercase hidden sm:inline">MULTI_MODEL</span>
                <ApexMascot
                  variant="connected"
                  height={65}
                  animateIdle={true}
                  alt="APEX companion linked across multi-model providers"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
