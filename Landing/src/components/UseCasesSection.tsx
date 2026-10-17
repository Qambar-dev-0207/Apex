"use client";

import { motion, useReducedMotion } from "motion/react";
import { MOTION_EASE } from "../lib/motion";

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
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="applications"
      className="relative w-full bg-[#08090A] text-[#F5F3EF] py-20 sm:py-28 lg:py-32 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="What APEX is Built For"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Section Header */}
        <div className="max-w-[840px] mb-12 lg:mb-16">
          {/* Eyebrow with horizontal line draw */}
          <div className="flex items-center gap-3 mb-4">
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
              SYSTEM CAPABILITIES
            </motion.div>
          </div>

          {/* Masked Line Reveal Headline */}
          <h2 className="font-editorial text-4xl sm:text-6xl lg:text-7xl leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-5 flex flex-col">
            <span className="overflow-mask block relative py-0.5">
              <motion.span
                initial={
                  shouldReduceMotion
                    ? { opacity: 1, y: 0 }
                    : { opacity: 0, y: "110%", filter: "blur(3px)" }
                }
                whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                viewport={{ once: true }}
                transition={{ duration: 0.75, ease: MOTION_EASE.enter }}
                className="block font-normal"
              >
                What APEX is
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
                transition={{ duration: 0.85, delay: 0.1, ease: MOTION_EASE.enter }}
                className="block font-editorial italic font-normal text-[#E9D0AD]"
              >
                built for.
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
            Designed for engineering workflows where probabilistic text outputs are insufficient and verified execution is required.
          </motion.p>
        </div>

        {/* Three Editorial Rows with Animated Hairline Dividers & Sequential Entrance */}
        <div className="border-t border-[rgba(255,255,255,0.08)]">
          {CAPABILITY_BLOCKS.map((block, idx) => (
            <motion.div
              key={block.num}
              tabIndex={0}
              className="py-12 sm:py-16 grid grid-cols-1 lg:grid-cols-12 gap-8 items-start group border-b border-[rgba(255,255,255,0.08)] hover:border-[#FF4A16]/40 focus:border-[#FF4A16]/60 focus:outline-none transition-colors duration-400 relative"
            >
              {/* Subtle accent hairline marker on left */}
              <div className="absolute left-0 top-0 bottom-0 w-0.5 bg-transparent group-hover:bg-[#FF4A16] group-focus:bg-[#FF4A16] transition-colors duration-300" />

              {/* Large Typographic Marker - Sequenced Reveal 1 */}
              <motion.div
                initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, x: -12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: idx * 0.1, ease: MOTION_EASE.enter }}
                className="lg:col-span-2 flex items-center gap-4 pl-3"
              >
                <span className="font-editorial text-5xl sm:text-7xl text-[#737575] group-hover:text-[#FF4A16] group-focus:text-[#FF4A16] transition-colors duration-300">
                  {block.num}
                </span>
              </motion.div>

              {/* Title & Statement - Sequenced Reveal 2 */}
              <motion.div
                initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.65, delay: idx * 0.1 + 0.08, ease: MOTION_EASE.enter }}
                className="lg:col-span-6"
              >
                <h3 className="font-editorial text-3xl sm:text-5xl text-[#F5F3EF] mb-3 group-hover:text-[#FFF] transition-colors">
                  {block.title}
                </h3>
                <p className="text-[#B2B0AD] text-base sm:text-xl font-normal leading-relaxed max-w-[560px]">
                  {block.copy}
                </p>
              </motion.div>

              {/* Context / Application Details - Sequenced Reveal 3 */}
              <motion.div
                initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.65, delay: idx * 0.1 + 0.16, ease: MOTION_EASE.enter }}
                className="lg:col-span-4 lg:text-right pt-2"
              >
                <span className="font-code text-xs text-[#E9D0AD]/80 leading-relaxed block group-hover:text-[#E9D0AD] transition-colors">
                  {block.context}
                </span>
              </motion.div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
