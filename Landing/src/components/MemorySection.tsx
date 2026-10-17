"use client";

import { useState } from "react";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import ApexMascot from "./ApexMascot";
import { MOTION_EASE, MOTION_TIMING } from "../lib/motion";

export default function MemorySection() {
  const [activeLayer, setActiveLayer] = useState<"all" | "redis" | "chroma">("all");
  const shouldReduceMotion = useReducedMotion();

  const isRedisActive = activeLayer === "all" || activeLayer === "redis";
  const isChromaActive = activeLayer === "all" || activeLayer === "chroma";

  return (
    <section
      id="memory"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-28 sm:py-36 lg:py-44 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Hybrid Memory Architecture"
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
              HYBRID MEMORY
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
                Context should not end
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
                transition={{ duration: 0.82, delay: 0.1, ease: MOTION_EASE.enter }}
                className="block font-normal"
              >
                with the{" "}
                <span className="font-editorial italic font-normal text-[#E9D0AD]">
                  conversation.
                </span>
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
            APEX combines active working memory with semantic retrieval to make relevant context available across tasks and interactions.
          </motion.p>
        </div>

        {/* Memory Architecture Visual + Dual-Role Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch mb-10">
          {/* Left Column: Interactive Memory Lattice Network Diagram */}
          <div className="lg:col-span-7 bg-[#08090A] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-10 flex flex-col justify-between relative overflow-hidden min-h-[460px]">
            {/* Header / Mode Selector */}
            <div className="flex items-center justify-between pb-6 border-b border-[rgba(255,255,255,0.08)] font-code text-xs z-10">
              <span className="text-[#737575] uppercase tracking-wider">
                HYBRID TOPOLOGY
              </span>
              <div className="flex items-center gap-2" role="tablist">
                <button
                  role="tab"
                  aria-selected={activeLayer === "redis"}
                  type="button"
                  onClick={() => setActiveLayer("redis")}
                  className={`px-3 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer focus-visible:outline-[#FF4A16] ${
                    activeLayer === "redis"
                      ? "bg-[#FF4A16] text-white shadow-[0_0_12px_rgba(255,74,22,0.4)]"
                      : "bg-[#111315] text-[#737575] hover:text-[#B2B0AD]"
                  }`}
                >
                  REDIS
                </button>
                <button
                  role="tab"
                  aria-selected={activeLayer === "chroma"}
                  type="button"
                  onClick={() => setActiveLayer("chroma")}
                  className={`px-3 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer focus-visible:outline-[#FF4A16] ${
                    activeLayer === "chroma"
                      ? "bg-[#FF4A16] text-white shadow-[0_0_12px_rgba(255,74,22,0.4)]"
                      : "bg-[#111315] text-[#737575] hover:text-[#B2B0AD]"
                  }`}
                >
                  CHROMADB
                </button>
                <button
                  role="tab"
                  aria-selected={activeLayer === "all"}
                  type="button"
                  onClick={() => setActiveLayer("all")}
                  className={`px-3 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer focus-visible:outline-[#FF4A16] ${
                    activeLayer === "all"
                      ? "bg-[rgba(255,255,255,0.2)] text-white shadow-[0_0_12px_rgba(255,255,255,0.2)]"
                      : "bg-[#111315] text-[#737575] hover:text-[#B2B0AD]"
                  }`}
                >
                  ALL
                </button>
              </div>
            </div>

            {/* SVG Architectural Memory Lattice */}
            <div className="my-auto py-8 flex items-center justify-center relative">
              <svg viewBox="0 0 540 240" className="w-full max-w-[500px] h-auto text-white overflow-visible">
                {/* Connecting Bridge Rays between Redis & ChromaDB */}
                <line
                  x1="180"
                  y1="120"
                  x2="340"
                  y2="120"
                  stroke={activeLayer === "all" ? "#FF4A16" : "rgba(255,255,255,0.15)"}
                  strokeWidth="1.5"
                  strokeDasharray="4 4"
                  className="transition-colors duration-300"
                />

                {/* Left Cluster: REDIS Working Context (Sub-10ms) */}
                <g
                  className="transition-opacity duration-300"
                  style={{ opacity: isRedisActive ? 1 : 0.25 }}
                >
                  {/* Outer boundary circle */}
                  <circle cx="120" cy="120" r="70" fill="none" stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />

                  {/* Redis Central Hub */}
                  <rect x="85" y="100" width="70" height="40" rx="8" fill="#111315" stroke={isRedisActive ? "#FF4A16" : "rgba(255,255,255,0.2)"} strokeWidth="1.5" />
                  <text x="120" y="125" textAnchor="middle" fill="#F5F3EF" fontSize="11" fontFamily="monospace" fontWeight="bold">REDIS</text>

                  {/* Compact Peripheral Nodes */}
                  <circle cx="65" cy="80" r="6" fill="#111315" stroke={isRedisActive ? "#FF4A16" : "rgba(255,255,255,0.3)"} />
                  <line x1="85" y1="105" x2="71" y2="85" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <text x="65" y="70" textAnchor="middle" fill="#8C9295" fontSize="8" fontFamily="monospace">SESSION</text>

                  <circle cx="65" cy="160" r="6" fill="#111315" stroke={isRedisActive ? "#FF4A16" : "rgba(255,255,255,0.3)"} />
                  <line x1="85" y1="135" x2="71" y2="155" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <text x="65" y="178" textAnchor="middle" fill="#8C9295" fontSize="8" fontFamily="monospace">AST_CACHE</text>

                  <circle cx="175" cy="70" r="6" fill="#111315" stroke={isRedisActive ? "#FF4A16" : "rgba(255,255,255,0.3)"} />
                  <line x1="145" y1="100" x2="170" y2="75" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <text x="175" y="60" textAnchor="middle" fill="#8C9295" fontSize="8" fontFamily="monospace">DAG_STATE</text>

                  <text x="120" y="205" textAnchor="middle" fill="#FF4A16" fontSize="9" fontFamily="monospace" letterSpacing="0.1em">
                    WORKING CONTEXT (&lt;10ms)
                  </text>
                </g>

                {/* Right Cluster: CHROMADB Semantic Network (<38ms HNSW) */}
                <g
                  className="transition-opacity duration-300"
                  style={{ opacity: isChromaActive ? 1 : 0.25 }}
                >
                  {/* Outer boundary circle */}
                  <circle cx="400" cy="120" r="70" fill="none" stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />

                  {/* ChromaDB Central Hub */}
                  <rect x="360" y="100" width="80" height="40" rx="8" fill="#111315" stroke={isChromaActive ? "#FF4A16" : "rgba(255,255,255,0.2)"} strokeWidth="1.5" />
                  <text x="400" y="125" textAnchor="middle" fill="#F5F3EF" fontSize="11" fontFamily="monospace" fontWeight="bold">CHROMADB</text>

                  {/* Distributed Semantic Graph Nodes */}
                  <circle cx="455" cy="75" r="6" fill="#111315" stroke={isChromaActive ? "#FF4A16" : "rgba(255,255,255,0.3)"} />
                  <line x1="435" y1="105" x2="450" y2="80" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <text x="455" y="65" textAnchor="middle" fill="#8C9295" fontSize="8" fontFamily="monospace">INVARIANTS</text>

                  <circle cx="455" cy="165" r="6" fill="#111315" stroke={isChromaActive ? "#FF4A16" : "rgba(255,255,255,0.3)"} />
                  <line x1="435" y1="135" x2="450" y2="160" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <text x="455" y="182" textAnchor="middle" fill="#8C9295" fontSize="8" fontFamily="monospace">EMBEDDINGS</text>

                  <circle cx="345" cy="65" r="6" fill="#111315" stroke={isChromaActive ? "#FF4A16" : "rgba(255,255,255,0.3)"} />
                  <line x1="375" y1="100" x2="350" y2="70" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <text x="345" y="55" textAnchor="middle" fill="#8C9295" fontSize="8" fontFamily="monospace">RESEARCH</text>

                  <text x="400" y="205" textAnchor="middle" fill="#FF4A16" fontSize="9" fontFamily="monospace" letterSpacing="0.1em">
                    SEMANTIC RETRIEVAL (&lt;38ms)
                  </text>
                </g>
              </svg>
            </div>

            {/* Bottom Status / Mode Description */}
            <div className="pt-4 border-t border-[rgba(255,255,255,0.08)] flex flex-wrap items-center justify-between gap-4 font-code text-[11px] text-[#737575] z-10">
              <span className="uppercase">
                {activeLayer === "all"
                  ? "TOPOLOGY // INTEGRATED ACTIVE & PERSISTENT CONTEXT"
                  : activeLayer === "redis"
                  ? "TOPOLOGY // EPHEMERAL WORKING CACHE ONLY"
                  : "TOPOLOGY // PERSISTENT VECTOR LATTICE ONLY"}
              </span>
              <span className="text-[#FF4A16]">HNSW COSINE SIMILARITY</span>
            </div>
          </div>

          {/* Right Column: Dual-Role Cards */}
          <div className="lg:col-span-5 flex flex-col justify-between gap-6">
            {/* Redis Working Memory Card */}
            <div
              onClick={() => setActiveLayer("redis")}
              className={`p-6 sm:p-7 rounded-xl border transition-all duration-300 cursor-pointer ${
                isRedisActive
                  ? "bg-[#08090A] border-[rgba(255,255,255,0.22)] shadow-sm"
                  : "bg-transparent border-transparent opacity-40 hover:opacity-80"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="font-code text-xs font-semibold text-[#FF4A16]">
                  01 / ACTIVE
                </span>
                <span className="font-code text-[10px] text-[#8C9295] uppercase">
                  &lt;10ms LATENCY
                </span>
              </div>
              <h3 className="font-sans text-lg sm:text-xl font-medium text-[#F5F3EF] mb-2">
                Working Memory (Redis)
              </h3>
              <p className="text-[#B2B0AD] text-xs sm:text-sm leading-relaxed mb-4">
                Holds active conversation state, intermediate tool execution outputs, and ephemeral scratchpads needed during an unfolding task.
              </p>
              <div className="font-code text-[11px] text-[#E9D0AD]/90 flex items-center gap-2">
                <span className="text-[#FF4A16]">▸</span>
                <span>Fast in-memory key-value eviction & task rollback states.</span>
              </div>
            </div>

            {/* ChromaDB Semantic Memory Card */}
            <div
              onClick={() => setActiveLayer("chroma")}
              className={`p-6 sm:p-7 rounded-xl border transition-all duration-300 cursor-pointer ${
                isChromaActive
                  ? "bg-[#08090A] border-[rgba(255,255,255,0.22)] shadow-sm"
                  : "bg-transparent border-transparent opacity-40 hover:opacity-80"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="font-code text-xs font-semibold text-[#FF4A16]">
                  02 / PERSISTENT
                </span>
                <span className="font-code text-[10px] text-[#8C9295] uppercase">
                  &lt;38ms HNSW
                </span>
              </div>
              <h3 className="font-sans text-lg sm:text-xl font-medium text-[#F5F3EF] mb-2">
                Semantic Memory (ChromaDB)
              </h3>
              <p className="text-[#B2B0AD] text-xs sm:text-sm leading-relaxed mb-4">
                Indexes user project specifications, documentation, and historical problem-solving patterns into a persistent searchable vector space.
              </p>
              <div className="font-code text-[11px] text-[#E9D0AD]/90 flex items-center gap-2">
                <span className="text-[#FF4A16]">▸</span>
                <span>Cross-session knowledge graph and concept recall.</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Outside Area: Learning Mascot cleanly positioned outside the central diagram */}
        <div className="pt-6 border-t border-[rgba(255,255,255,0.06)] flex flex-wrap items-center justify-between gap-4">
          <span className="font-code text-[10px] tracking-[0.2em] text-[#737575] uppercase">
            EPHEMERAL-TO-SEMANTIC CONSOLIDATION PIPELINE
          </span>

          <div className="flex items-center gap-3 opacity-80 hover:opacity-100 transition-opacity">
            <span className="font-code text-[9px] text-[#8C9295] uppercase hidden sm:inline">INDEXING_MEMORY</span>
            <ApexMascot
              variant="learning"
              height={75}
              animateIdle={true}
              alt="APEX companion indexing hybrid memory context"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
