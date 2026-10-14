"use client";

import { useState } from "react";
import { motion, useReducedMotion } from "motion/react";
import ApexMascot from "./ApexMascot";

export default function MemorySection() {
  const [activeLayer, setActiveLayer] = useState<"all" | "redis" | "chroma">("all");
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="memory"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-32 sm:py-40 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Hybrid Memory Architecture"
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
                    : { opacity: 0, y: "110%", filter: "blur(3px)" }
                }
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                viewport={{ once: true }}
                transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
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
                    : { opacity: 0, y: "110%", filter: "blur(3px)" }
                }
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                viewport={{ once: true }}
                transition={{ duration: 0.82, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
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
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            APEX combines active working memory with semantic retrieval to make relevant context available across tasks and interactions.
          </motion.p>
        </div>

        {/* Memory Architecture Visual + Dual-Role Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch mb-12">
          {/* Left Column: Interactive Memory Lattice Diagram */}
          <div className="lg:col-span-7 bg-[#08090A] border border-[rgba(255,255,255,0.1)] rounded-2xl p-6 sm:p-10 flex flex-col justify-between relative overflow-hidden min-h-[420px]">
            {/* Header / Mode Selector */}
            <div className="flex items-center justify-between pb-6 border-b border-[rgba(255,255,255,0.08)] font-code text-xs z-10">
              <span className="text-[#737575] uppercase tracking-wider">
                HYBRID TOPOLOGY
              </span>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => setActiveLayer("redis")}
                  className={`px-3 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                    activeLayer === "redis"
                      ? "bg-[#FF4A16] text-white"
                      : "bg-[#111315] text-[#737575] hover:text-[#B2B0AD]"
                  }`}
                >
                  REDIS
                </button>
                <button
                  type="button"
                  onClick={() => setActiveLayer("chroma")}
                  className={`px-3 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                    activeLayer === "chroma"
                      ? "bg-[#FF4A16] text-white"
                      : "bg-[#111315] text-[#737575] hover:text-[#B2B0AD]"
                  }`}
                >
                  CHROMADB
                </button>
                <button
                  type="button"
                  onClick={() => setActiveLayer("all")}
                  className={`px-3 py-1 rounded text-[11px] font-semibold transition-all cursor-pointer ${
                    activeLayer === "all"
                      ? "bg-[rgba(255,255,255,0.2)] text-white"
                      : "bg-[#111315] text-[#737575] hover:text-[#B2B0AD]"
                  }`}
                >
                  ALL
                </button>
              </div>
            </div>

            {/* SVG Architectural Memory Lattice */}
            <div className="my-auto py-8 flex items-center justify-center">
              <svg viewBox="0 0 540 220" className="w-full max-w-[500px] h-auto text-white">
                {/* Connecting Bridge Rays between Redis & ChromaDB */}
                <line
                  x1="160"
                  y1="110"
                  x2="380"
                  y2="110"
                  stroke={activeLayer === "all" ? "rgba(255,74,22,0.6)" : "rgba(255,255,255,0.15)"}
                  strokeWidth="1.5"
                  strokeDasharray="4 4"
                />

                {/* Left Cluster: Redis Working State */}
                <g
                  className={`transition-opacity duration-300 ${
                    activeLayer === "chroma" ? "opacity-30" : "opacity-100"
                  }`}
                >
                  <circle cx="160" cy="110" r="42" fill="#111315" stroke={activeLayer === "redis" ? "#FF4A16" : "rgba(255,255,255,0.2)"} strokeWidth="1.5" />
                  <circle cx="160" cy="110" r="6" fill="#FF4A16" />
                  <text x="160" y="142" textAnchor="middle" fill="#F5F3EF" fontSize="10" fontFamily="var(--font-jetbrains)" fontWeight="600">
                    REDIS
                  </text>
                  <text x="160" y="156" textAnchor="middle" fill="#737575" fontSize="8" fontFamily="var(--font-jetbrains)">
                    WORKING CACHE
                  </text>

                  {/* Satellite nodes for active tasks */}
                  <circle cx="100" cy="70" r="14" fill="#08090A" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <line x1="160" y1="110" x2="100" y2="70" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
                  <circle cx="100" cy="150" r="14" fill="#08090A" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <line x1="160" y1="110" x2="100" y2="150" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
                  <circle cx="190" cy="50" r="12" fill="#08090A" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <line x1="160" y1="110" x2="190" y2="50" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
                </g>

                {/* Right Cluster: ChromaDB Semantic Memory */}
                <g
                  className={`transition-opacity duration-300 ${
                    activeLayer === "redis" ? "opacity-30" : "opacity-100"
                  }`}
                >
                  <circle cx="380" cy="110" r="42" fill="#111315" stroke={activeLayer === "chroma" ? "#FF4A16" : "rgba(255,255,255,0.2)"} strokeWidth="1.5" />
                  <circle cx="380" cy="110" r="6" fill="#FF4A16" />
                  <text x="380" y="142" textAnchor="middle" fill="#F5F3EF" fontSize="10" fontFamily="var(--font-jetbrains)" fontWeight="600">
                    CHROMADB
                  </text>
                  <text x="380" y="156" textAnchor="middle" fill="#737575" fontSize="8" fontFamily="var(--font-jetbrains)">
                    VECTOR STORE
                  </text>

                  {/* Satellite nodes for persistent embeddings */}
                  <circle cx="440" cy="70" r="14" fill="#08090A" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <line x1="380" y1="110" x2="440" y2="70" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
                  <circle cx="440" cy="150" r="14" fill="#08090A" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <line x1="380" y1="110" x2="440" y2="150" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
                  <circle cx="350" cy="50" r="12" fill="#08090A" stroke="rgba(255,255,255,0.2)" strokeWidth="1" />
                  <line x1="380" y1="110" x2="350" y2="50" stroke="rgba(255,255,255,0.15)" strokeWidth="1" />
                </g>
              </svg>
            </div>

            {/* Micro Caption */}
            <div className="pt-4 border-t border-[rgba(255,255,255,0.06)] flex items-center justify-between text-[#737575] font-code text-[10px]">
              <span>EPHEMERAL EXECUTION CONTEXT</span>
              <span>INDEXED SEMANTIC EMBEDDINGS</span>
            </div>
          </div>

          {/* Right Column: Explanatory Role Cards */}
          <div className="lg:col-span-5 flex flex-col justify-between gap-6">
            {/* Redis Role Card */}
            <div
              onClick={() => setActiveLayer("redis")}
              className={`p-7 rounded-xl border transition-all cursor-pointer ${
                activeLayer === "redis"
                  ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_20px_rgba(255,74,22,0.15)]"
                  : "bg-[#08090A] border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)]"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="font-code text-xs font-semibold text-[#FF4A16] tracking-wider">
                  TIER 01 / WORKING MEMORY
                </span>
                <span className="font-code text-[11px] text-[#737575]">IN-MEMORY</span>
              </div>
              <h3 className="font-sans text-xl font-medium text-[#F5F3EF] mb-2">
                Redis Working Context
              </h3>
              <p className="text-[#B2B0AD] text-sm leading-relaxed mb-4">
                A foundation for short-term working context, active execution locks, and intermediate task outputs with sub-10ms access.
              </p>
              <div className="font-code text-[11px] text-[#E9D0AD]/90">
                ▸ Session state, active task DAG payloads, fast deduplication
              </div>
            </div>

            {/* ChromaDB Role Card */}
            <div
              onClick={() => setActiveLayer("chroma")}
              className={`p-7 rounded-xl border transition-all cursor-pointer ${
                activeLayer === "chroma"
                  ? "bg-[#111315] border-[#FF4A16] shadow-[0_0_20px_rgba(255,74,22,0.15)]"
                  : "bg-[#08090A] border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.2)]"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="font-code text-xs font-semibold text-[#FF4A16] tracking-wider">
                  TIER 02 / SEMANTIC RETRIEVAL
                </span>
                <span className="font-code text-[11px] text-[#737575]">VECTOR STORE</span>
              </div>
              <h3 className="font-sans text-xl font-medium text-[#F5F3EF] mb-2">
                ChromaDB Long-Term Knowledge
              </h3>
              <p className="text-[#B2B0AD] text-sm leading-relaxed mb-4">
                A vector-backed retrieval layer indexing past interaction graphs, codebase symbol maps, and research artifacts for semantic recall.
              </p>
              <div className="font-code text-[11px] text-[#E9D0AD]/90">
                ▸ Cross-interaction learning, AST code embeddings, research documents
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Technical Notation + Learning Mascot at Secondary Edge */}
        <div className="pt-6 border-t border-[rgba(255,255,255,0.08)] flex flex-wrap items-center justify-between gap-4 text-[#737575] font-code text-[11px] tracking-[0.2em] uppercase">
          <div className="flex items-center gap-4">
            <span>WORKING CACHE ↔ SEMANTIC VECTOR MANIFOLD</span>
            <span className="text-[#737575]/40">·</span>
            <span>DETERMINISTIC RETRIEVAL BOUNDS</span>
          </div>

          <div className="flex items-center gap-3 opacity-80 hover:opacity-100 transition-opacity">
            <span className="text-[9px] text-[#8C9295] tracking-widest hidden sm:inline">MEMORY::CONSOLIDATE</span>
            <ApexMascot
              variant="learning"
              height={74}
              animateIdle={true}
              alt="APEX companion indexing memory context"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
