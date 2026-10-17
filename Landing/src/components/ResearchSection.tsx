"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import ApexMascot from "./ApexMascot";
import { MOTION_EASE } from "../lib/motion";

interface ResearchStage {
  step: string;
  name: string;
  tag: string;
  body: string;
  spec: string;
}

const RESEARCH_STAGES: ResearchStage[] = [
  {
    step: "01",
    name: "SOURCE",
    tag: "Multi-Source Intake",
    body: "Gathers raw technical documentation, academic arXiv preprints, and local codebase files into an ingestion queue.",
    spec: "WebSearchAgent & CodeAnalyzerAgent intake streams.",
  },
  {
    step: "02",
    name: "INGEST",
    tag: "AST Context Compression",
    body: "Parses Abstract Syntax Trees to isolate signatures and structures, removing token bloat without losing structural precision.",
    spec: "Code Compass symbol traverser achieving 18.4× token compression.",
  },
  {
    step: "03",
    name: "CONNECT",
    tag: "Relational Knowledge Graph",
    body: "Links extracted concepts, classes, and architectural specifications into an interconnected semantic memory graph.",
    spec: "Embeds Knowledge Items directly into persistent ChromaDB collections.",
  },
  {
    step: "04",
    name: "RETRIEVE",
    tag: "Sub-38ms Zero-Loss Recall",
    body: "Injects relevant context directly into the planning and execution phases of autonomous tasks.",
    spec: "Hybrid vector search combining keyword indices with cosine similarity.",
  },
];

export default function ResearchSection() {
  const [activeStage, setActiveStage] = useState<number>(0);
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="research"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-28 sm:py-36 lg:py-44 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Research and KnowledgeForge System"
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
              RESEARCH & KNOWLEDGE
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
                From research to
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
                usable knowledge.
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
            APEX explores a workflow in which research, structured context, and implementation can inform the next stage of development.
          </motion.p>
        </div>

        {/* Culminating Technical Visualization Canvas: Interactive Information Transformation Pipeline */}
        <div className="bg-[#08090A] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-10 lg:p-12 mb-10 relative overflow-hidden">
          {/* Subtle grid */}
          <div className="absolute inset-0 architectural-grid opacity-20 pointer-events-none" />

          {/* Interactive Stage Selector Tabs */}
          <div className="flex flex-wrap items-center justify-between gap-4 pb-6 border-b border-[rgba(255,255,255,0.08)] mb-8 relative z-10" role="tablist">
            <span className="font-code text-xs text-[#737575] tracking-wider uppercase">
              KNOWLEDGEFORGE // TRANSFORMATION PIPELINE
            </span>

            <div className="flex items-center gap-2">
              {RESEARCH_STAGES.map((stg, idx) => {
                const isActive = activeStage === idx;
                return (
                  <button
                    key={stg.step}
                    role="tab"
                    aria-selected={isActive}
                    type="button"
                    onClick={() => setActiveStage(idx)}
                    className={`px-3 sm:px-4 py-1.5 rounded-lg font-code text-xs font-semibold transition-all cursor-pointer focus-visible:outline-[#FF4A16] ${
                      isActive
                        ? "bg-[#FF4A16] text-white shadow-[0_0_14px_rgba(255,74,22,0.4)]"
                        : "bg-[#111315] text-[#8C9295] hover:text-[#F5F3EF]"
                    }`}
                  >
                    {stg.step} {stg.name}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Central Transformation Graphic */}
          <div className="my-6 py-8 flex flex-col items-center justify-center relative z-10">
            <svg viewBox="0 0 680 180" className="w-full max-w-[640px] h-auto text-white overflow-visible">
              {/* Connecting Conduit Ray */}
              <line x1="80" y1="90" x2="600" y2="90" stroke="rgba(255,255,255,0.15)" strokeWidth="1.5" strokeDasharray="4 4" />

              {/* Stage 1: SOURCE — Document Representations */}
              <g
                className="transition-opacity duration-300 cursor-pointer"
                onClick={() => setActiveStage(0)}
                style={{ opacity: activeStage === 0 ? 1 : 0.4 }}
              >
                <rect x="40" y="55" width="80" height="70" rx="6" fill="#111315" stroke={activeStage === 0 ? "#FF4A16" : "rgba(255,255,255,0.2)"} strokeWidth={activeStage === 0 ? "2" : "1"} />
                {/* Simulated document lines */}
                <line x1="52" y1="72" x2="108" y2="72" stroke="rgba(255,255,255,0.4)" strokeWidth="2" />
                <line x1="52" y1="84" x2="96" y2="84" stroke="rgba(255,255,255,0.4)" strokeWidth="2" />
                <line x1="52" y1="96" x2="104" y2="96" stroke="rgba(255,255,255,0.4)" strokeWidth="2" />
                <line x1="52" y1="108" x2="80" y2="108" stroke="#FF4A16" strokeWidth="2" />
                <text x="80" y="145" textAnchor="middle" fill={activeStage === 0 ? "#FF4A16" : "#8C9295"} fontSize="10" fontFamily="monospace" fontWeight="bold">01 SOURCE</text>
              </g>

              {/* Stage 2: INGEST — Structured AST Syntax Tree */}
              <g
                className="transition-opacity duration-300 cursor-pointer"
                onClick={() => setActiveStage(1)}
                style={{ opacity: activeStage === 1 ? 1 : 0.4 }}
              >
                <rect x="210" y="55" width="85" height="70" rx="6" fill="#111315" stroke={activeStage === 1 ? "#FF4A16" : "rgba(255,255,255,0.2)"} strokeWidth={activeStage === 1 ? "2" : "1"} />
                {/* Syntax tree nodes */}
                <circle cx="252" cy="74" r="5" fill="#FF4A16" />
                <line x1="252" y1="79" x2="234" y2="98" stroke="rgba(255,255,255,0.3)" />
                <line x1="252" y1="79" x2="270" y2="98" stroke="rgba(255,255,255,0.3)" />
                <circle cx="234" cy="98" r="4" fill="#E9D0AD" />
                <circle cx="270" cy="98" r="4" fill="#E9D0AD" />
                <text x="252" y="145" textAnchor="middle" fill={activeStage === 1 ? "#FF4A16" : "#8C9295"} fontSize="10" fontFamily="monospace" fontWeight="bold">02 INGEST (AST)</text>
              </g>

              {/* Stage 3: CONNECT — Relational Knowledge Graph */}
              <g
                className="transition-opacity duration-300 cursor-pointer"
                onClick={() => setActiveStage(2)}
                style={{ opacity: activeStage === 2 ? 1 : 0.4 }}
              >
                <rect x="385" y="55" width="85" height="70" rx="6" fill="#111315" stroke={activeStage === 2 ? "#FF4A16" : "rgba(255,255,255,0.2)"} strokeWidth={activeStage === 2 ? "2" : "1"} />
                {/* Graph network cluster */}
                <circle cx="410" cy="80" r="4" fill="#FF4A16" />
                <circle cx="445" cy="75" r="4" fill="#FF4A16" />
                <circle cx="428" cy="102" r="4" fill="#FF4A16" />
                <line x1="410" y1="80" x2="445" y2="75" stroke="#FF4A16" strokeWidth="1.2" />
                <line x1="410" y1="80" x2="428" y2="102" stroke="#FF4A16" strokeWidth="1.2" />
                <line x1="445" y1="75" x2="428" y2="102" stroke="#FF4A16" strokeWidth="1.2" />
                <text x="427" y="145" textAnchor="middle" fill={activeStage === 2 ? "#FF4A16" : "#8C9295"} fontSize="10" fontFamily="monospace" fontWeight="bold">03 CONNECT</text>
              </g>

              {/* Stage 4: RETRIEVE — Retrievable Context Group */}
              <g
                className="transition-opacity duration-300 cursor-pointer"
                onClick={() => setActiveStage(3)}
                style={{ opacity: activeStage === 3 ? 1 : 0.4 }}
              >
                <rect x="555" y="55" width="90" height="70" rx="6" fill="#111315" stroke={activeStage === 3 ? "#FF4A16" : "rgba(255,255,255,0.2)"} strokeWidth={activeStage === 3 ? "2" : "1"} />
                {/* Aperture vector beam */}
                <circle cx="600" cy="90" r="14" fill="none" stroke="#FF4A16" strokeWidth="1.5" strokeDasharray="3 3" />
                <circle cx="600" cy="90" r="4" fill="#FF4A16" />
                <text x="600" y="145" textAnchor="middle" fill={activeStage === 3 ? "#FF4A16" : "#8C9295"} fontSize="10" fontFamily="monospace" fontWeight="bold">04 RETRIEVE</text>
              </g>
            </svg>
          </div>

          {/* Synchronized Detail Drawer */}
          <div className="min-h-[100px] pt-6 border-t border-[rgba(255,255,255,0.08)] relative z-10">
            <AnimatePresence mode="wait">
              <motion.div
                key={activeStage}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4 }}
                transition={{ duration: 0.25, ease: MOTION_EASE.interface }}
                className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center"
              >
                <div className="md:col-span-8">
                  <div className="flex items-center gap-3 mb-1.5 font-code text-xs text-[#FF4A16]">
                    <span>STAGE {RESEARCH_STAGES[activeStage].step}</span>
                    <span className="text-[#8C9295]/40">·</span>
                    <span className="text-[#F5F3EF]">{RESEARCH_STAGES[activeStage].tag}</span>
                  </div>
                  <p className="text-[#B2B0AD] text-sm leading-relaxed">
                    {RESEARCH_STAGES[activeStage].body}
                  </p>
                </div>

                <div className="md:col-span-4 bg-[#111315] border border-[rgba(255,255,255,0.06)] rounded-lg p-4 font-code text-xs text-[#E9D0AD]/90">
                  <span className="text-[#737575] text-[10px] tracking-wider uppercase block mb-1">
                    SPECIFICATION
                  </span>
                  <span>{RESEARCH_STAGES[activeStage].spec}</span>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>
        </div>

        {/* 4 Sequential Stage Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-12">
          {RESEARCH_STAGES.map((stg, idx) => {
            const isActive = activeStage === idx;
            return (
              <button
                key={stg.step}
                type="button"
                onClick={() => setActiveStage(idx)}
                className={`p-6 sm:p-7 rounded-xl text-left border transition-all duration-300 cursor-pointer flex flex-col justify-between min-h-[260px] focus-visible:outline-[#FF4A16] ${
                  isActive
                    ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_16px_rgba(255,74,22,0.15)] translate-y-[-2px]"
                    : "bg-[#08090A] border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)] opacity-70 hover:opacity-100"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span
                      className={`font-code text-xs font-semibold ${
                        isActive ? "text-[#FF4A16]" : "text-[#737575]"
                      }`}
                    >
                      STAGE {stg.step}
                    </span>
                    <span className="w-1.5 h-1.5 rounded-full bg-[rgba(255,255,255,0.2)]" />
                  </div>
                  <h3 className="font-sans text-base sm:text-lg font-medium text-[#F5F3EF] mb-1">
                    {stg.name}
                  </h3>
                  <span className="font-code text-[11px] text-[#FF4A16]/80 block mb-3">
                    {stg.tag}
                  </span>
                  <p className="text-[#B2B0AD] text-xs leading-relaxed">
                    {stg.body}
                  </p>
                </div>

                <div className="pt-3 border-t border-[rgba(255,255,255,0.06)] font-code text-[10px] text-[#737575]">
                  {stg.spec}
                </div>
              </button>
            );
          })}
        </div>

        {/* Bottom Outside Area: Curious Mascot cleanly placed */}
        <div className="pt-6 border-t border-[rgba(255,255,255,0.08)] flex flex-wrap items-center justify-between gap-4">
          <span className="font-code text-[10px] tracking-[0.2em] text-[#737575] uppercase">
            GROUNDED TECHNICAL INGESTION // CHROMA HNSW
          </span>

          <div className="flex items-center gap-3 opacity-80 hover:opacity-100 transition-opacity">
            <span className="font-code text-[9px] text-[#8C9295] uppercase hidden sm:inline">KNOWLEDGE_EXPLORER</span>
            <ApexMascot
              variant="curious"
              height={70}
              animateIdle={true}
              alt="APEX companion exploring knowledge graph"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
