"use client";

import { motion, useScroll, useTransform, useReducedMotion } from "motion/react";
import { useRef } from "react";
import ScrollWordReveal from "./text/ScrollWordReveal";

export default function ManifestoSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const shouldReduceMotion = useReducedMotion();

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const lineWidth = useTransform(scrollYProgress, [0.08, 0.45], ["0%", "100%"]);

  const manifestoTokens = [
    { text: "The" },
    { text: "real" },
    { text: "work" },
    { text: "begins" },
    { text: "after" },
    { text: "understanding" },
    { text: "the" },
    { text: "intent" },
    { text: "—" },
    { text: "planning", isItalic: true },
    { text: "the", isItalic: true },
    { text: "steps,", isItalic: true },
    { text: "coordinating", isItalic: true },
    { text: "execution,", isItalic: true },
    { text: "validating", isItalic: true },
    { text: "results,", isItalic: true },
    { text: "and" },
    { text: "carrying" },
    { text: "useful" },
    { text: "context" },
    { text: "forward." },
  ];

  return (
    <section
      ref={containerRef}
      id="manifesto"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-32 sm:py-44 lg:py-52 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Philosophy Manifesto"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Subtle Horizontal Architectural Reveal Line that extends across the section */}
        <div className="w-full h-px bg-[rgba(255,255,255,0.08)] mb-20 relative overflow-hidden" aria-hidden="true">
          <motion.div
            style={{ width: shouldReduceMotion ? "100%" : lineWidth }}
            className="absolute left-0 top-0 bottom-0 bg-gradient-to-r from-[rgba(255,255,255,0.15)] via-[rgba(255,255,255,0.45)] to-[rgba(255,255,255,0.1)]"
          />
        </div>

        {/* Asymmetrical Typography-Led Composition */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          {/* Eyebrow Column */}
          <div className="lg:col-span-3">
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium sticky top-28 flex items-center gap-2.5"
            >
              <span className="w-3 h-px bg-[#737575]" aria-hidden="true" />
              <span>A DIFFERENT KIND OF SYSTEM</span>
            </motion.div>
          </div>

          {/* Core Manifesto Text Column */}
          <div className="lg:col-span-9 max-w-[960px]">
            {/* Monumental Headline with Masked Line Reveal */}
            <h2 className="font-editorial text-4xl sm:text-6xl lg:text-7xl xl:text-[80px] leading-[1.04] tracking-[-0.02em] text-[#F5F3EF] mb-12 flex flex-col">
              <span className="overflow-mask block relative py-0.5">
                <motion.span
                  initial={
                    shouldReduceMotion
                      ? { opacity: 1, y: 0 }
                      : { opacity: 0, y: "110%", filter: "blur(3px)" }
                  }
                  whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
                  className="block font-normal"
                >
                  A prompt is only the
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
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ duration: 0.85, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                  className="block font-editorial italic font-normal text-[#E9D0AD]"
                >
                  beginning.
                </motion.span>
              </span>
            </h2>

            {/* Word-By-Word Scroll-Linked Reading Emphasis */}
            <div className="mb-20 max-w-[840px]">
              <ScrollWordReveal
                tokens={manifestoTokens}
                className="text-[#B2B0AD] text-xl sm:text-2xl lg:text-[28px] font-normal leading-[1.52] tracking-wide"
              />
            </div>

            {/* Understated Philosophy Pillars: REASON / ORCHESTRATE / EVOLVE */}
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ duration: 0.75, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="grid grid-cols-1 sm:grid-cols-3 gap-8 pt-10 border-t border-[rgba(255,255,255,0.08)]"
            >
              <div className="flex flex-col gap-2.5">
                <span className="font-code text-xs tracking-[0.24em] text-[#F5F3EF] uppercase font-semibold">
                  REASON
                </span>
                <span className="text-[#737575] text-xs font-normal leading-relaxed">
                  Probe assumptions with Socratic invariants before state mutation.
                </span>
              </div>

              <div className="flex flex-col gap-2.5 sm:border-l sm:border-[rgba(255,255,255,0.08)] sm:pl-8">
                <span className="font-code text-xs tracking-[0.24em] text-[#F5F3EF] uppercase font-semibold">
                  ORCHESTRATE
                </span>
                <span className="text-[#737575] text-xs font-normal leading-relaxed">
                  Decompose goals into deterministic, dependency-ordered Task DAGs.
                </span>
              </div>

              <div className="flex flex-col gap-2.5 sm:border-l sm:border-[rgba(255,255,255,0.08)] sm:pl-8">
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
