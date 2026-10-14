"use client";

import { motion, useReducedMotion } from "motion/react";

interface ResearchStage {
  id?: string;
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
    id: "03",
    step: "03",
    name: "CONNECT",
    tag: "Relational Knowledge Graph",
    body: "Links extracted concepts, classes, and architectural specifications into an interconnected semantic memory graph.",
    spec: "Embeds Knowledge Items directly into persistent ChromaDB collections.",
  },
  {
    id: "04",
    step: "04",
    name: "RETRIEVE",
    tag: "Sub-38ms Zero-Loss Recall",
    body: "Injects relevant context directly into the planning and execution phases of autonomous tasks.",
    spec: "Hybrid vector search combining keyword indices with cosine similarity.",
  },
];

export default function ResearchSection() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="research"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-32 sm:py-40 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Research and KnowledgeForge System"
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
                    : { opacity: 0, y: "110%", filter: "blur(3px)" }
                }
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                viewport={{ once: true }}
                transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
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
                    : { opacity: 0, y: "110%", filter: "blur(3px)" }
                }
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                viewport={{ once: true }}
                transition={{ duration: 0.85, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
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
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            APEX explores a workflow in which research, structured context, and implementation can inform the next stage of development.
          </motion.p>
        </div>

        {/* Abstract Field of Fine Document Planes & 4 Sequential Stages */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {RESEARCH_STAGES.map((stg, idx) => (
            <motion.div
              key={stg.step}
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: idx * 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="p-8 rounded-xl bg-[#08090A] border border-[rgba(255,255,255,0.08)] hover:border-[rgba(255,255,255,0.22)] transition-all duration-300 flex flex-col justify-between min-h-[340px]"
            >
              <div>
                <div className="flex items-center justify-between mb-6">
                  <span className="font-code text-xs font-semibold text-[#FF4A16]">
                    STAGE {stg.step}
                  </span>
                  <span className="font-code text-[10px] tracking-wider text-[#737575] uppercase">
                    {stg.tag}
                  </span>
                </div>

                <h3 className="font-sans text-xl font-medium text-[#F5F3EF] mb-3">
                  {stg.name}
                </h3>

                <p className="text-[#B2B0AD] text-xs sm:text-sm leading-relaxed mb-6">
                  {stg.body}
                </p>
              </div>

              <div className="pt-4 border-t border-[rgba(255,255,255,0.06)] font-code text-[11px] text-[#E9D0AD]/85">
                ▸ {stg.spec}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Bottom Sequence Notation */}
        <div className="flex flex-wrap items-center justify-between gap-4 text-[#737575] font-code text-[11px] tracking-[0.2em] uppercase pt-6 border-t border-[rgba(255,255,255,0.08)]">
          <span>SOURCE → INGEST → CONNECT → RETRIEVE</span>
          <span>KNOWLEDGEFORGE SPECIFICATION</span>
        </div>
      </div>
    </section>
  );
}
