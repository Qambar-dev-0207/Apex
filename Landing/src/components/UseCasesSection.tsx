"use client";

import { motion } from "motion/react";

interface CapabilityBlock {
  num: string;
  title: string;
  copy: string;
  context: string;
}

const CAPABILITY_BLOCKS: CapabilityBlock[] = [
  {
    num: "01",
    title: "Build",
    copy: "Move from a complex engineering objective to a structured, coordinated sequence of work.",
    context: "Architecture specifications, AST symbol parsing, test-driven validation.",
  },
  {
    num: "02",
    title: "Research",
    copy: "Bring models, research workflows, and relevant context into a more coherent working process.",
    context: "arXiv literature synthesis, structured extraction, persistent vector collections.",
  },
  {
    num: "03",
    title: "Orchestrate",
    copy: "Coordinate specialized agents and tools across tasks that benefit from structured execution.",
    context: "Parallel TaskGroup concurrency, Socratic verification, automated rollback gates.",
  },
];

export default function UseCasesSection() {
  return (
    <section
      id="applications"
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-32 sm:py-40 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)]"
      aria-label="What APEX is Built For"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[840px] mb-20 lg:mb-28">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium mb-5"
          >
            SYSTEM CAPABILITIES
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-6"
          >
            What APEX is{" "}
            <span className="font-editorial italic font-normal text-[#E9D0AD]">
              built for.
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#B2B0AD] text-base sm:text-lg font-normal leading-relaxed max-w-[620px]"
          >
            Designed for engineering workflows where probabilistic text outputs are insufficient and verified execution is required.
          </motion.p>
        </div>

        {/* Three Asymmetric Large Text Blocks with Hairline Separators */}
        <div className="divide-y divide-[rgba(255,255,255,0.08)] border-y border-[rgba(255,255,255,0.08)]">
          {CAPABILITY_BLOCKS.map((block) => (
            <div
              key={block.num}
              className="py-16 sm:py-20 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start group"
            >
              {/* Large Typographic Marker */}
              <div className="lg:col-span-2 flex items-center gap-4">
                <span className="font-editorial text-5xl sm:text-7xl text-[#737575] group-hover:text-[#FF4A16] transition-colors duration-300">
                  {block.num}
                </span>
              </div>

              {/* Title & Statement */}
              <div className="lg:col-span-6">
                <h3 className="font-editorial text-3xl sm:text-5xl text-[#F5F3EF] mb-4">
                  {block.title}
                </h3>
                <p className="text-[#B2B0AD] text-base sm:text-xl font-normal leading-relaxed max-w-[560px]">
                  {block.copy}
                </p>
              </div>

              {/* Context / Application Details */}
              <div className="lg:col-span-4 lg:text-right pt-2">
                <span className="font-code text-xs text-[#E9D0AD]/80 leading-relaxed block">
                  {block.context}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
