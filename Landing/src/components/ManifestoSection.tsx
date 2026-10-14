"use client";

import { motion, useScroll, useTransform } from "motion/react";
import { useRef } from "react";

export default function ManifestoSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const lineWidth = useTransform(scrollYProgress, [0.1, 0.6], ["0%", "100%"]);

  return (
    <section
      ref={containerRef}
      id="manifesto"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-32 sm:py-44 lg:py-52 overflow-hidden border-t border-[rgba(255,255,255,0.06)]"
      aria-label="APEX Philosophy Manifesto"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Subtle Horizontal Architectural Reveal Line */}
        <div className="w-full h-px bg-[rgba(255,255,255,0.08)] mb-20 relative overflow-hidden">
          <motion.div
            style={{ width: lineWidth }}
            className="absolute left-0 top-0 bottom-0 bg-[rgba(255,255,255,0.4)]"
          />
        </div>

        {/* Asymmetrical Typography-Led Composition */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          {/* Eyebrow Column */}
          <div className="lg:col-span-3">
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium sticky top-28"
            >
              A DIFFERENT KIND OF SYSTEM
            </motion.div>
          </div>

          {/* Core Manifesto Text Column */}
          <div className="lg:col-span-9 max-w-[960px]">
            {/* Monumental Headline */}
            <motion.h2
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="font-editorial text-4xl sm:text-6xl lg:text-7xl xl:text-[80px] leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-12"
            >
              A prompt is only the{" "}
              <span className="font-editorial italic font-normal text-[#E9D0AD]">
                beginning.
              </span>
            </motion.h2>

            {/* Core Philosophy Statement */}
            <motion.p
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.7, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="text-[#B2B0AD] text-lg sm:text-2xl lg:text-[26px] font-normal leading-[1.5] mb-20 max-w-[820px]"
            >
              The real work begins after understanding the intent —{" "}
              <span className="font-editorial italic text-[#F5F3EF] text-[1.12em] tracking-normal">
                planning the steps, coordinating execution, validating results,
              </span>{" "}
              and carrying useful context forward.
            </motion.p>

            {/* Understated Philosophy Pillars */}
            <motion.div
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-8 pt-10 border-t border-[rgba(255,255,255,0.08)]"
            >
              <div className="flex flex-col gap-2">
                <span className="font-code text-xs tracking-[0.24em] text-[#F5F3EF] uppercase font-semibold">
                  REASON
                </span>
                <span className="text-[#737575] text-xs font-normal leading-relaxed">
                  Probe assumptions with Socratic invariants before state mutation.
                </span>
              </div>

              <div className="flex flex-col gap-2 sm:border-l sm:border-[rgba(255,255,255,0.08)] sm:pl-8">
                <span className="font-code text-xs tracking-[0.24em] text-[#F5F3EF] uppercase font-semibold">
                  ORCHESTRATE
                </span>
                <span className="text-[#737575] text-xs font-normal leading-relaxed">
                  Decompose goals into deterministic, dependency-ordered Task DAGs.
                </span>
              </div>

              <div className="flex flex-col gap-2 sm:border-l sm:border-[rgba(255,255,255,0.08)] sm:pl-8">
                <span className="font-code text-xs tracking-[0.24em] text-[#F5F3EF] uppercase font-semibold">
                  EVOLVE
                </span>
                <span className="text-[#737575] text-xs font-normal leading-relaxed">
                  Continuous self-healing loops with automatic snapshot rollback.
                </span>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
