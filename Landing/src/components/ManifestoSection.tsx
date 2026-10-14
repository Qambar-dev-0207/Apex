"use client";

import { motion, useScroll, useTransform, useReducedMotion } from "motion/react";
import { useRef } from "react";
import ScrollWordReveal from "./text/ScrollWordReveal";
import ApexMascot from "./ApexMascot";

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

  const progressionSteps = [
    {
      num: "01",
      title: "REASON",
      desc: "Probe assumptions with Socratic invariants before state mutation.",
    },
    {
      num: "02",
      title: "ORCHESTRATE",
      desc: "Decompose goals into deterministic, dependency-ordered Task DAGs.",
    },
    {
      num: "03",
      title: "EVOLVE",
      desc: "Continuous self-healing loops with automatic snapshot rollback.",
    },
  ];

  return (
    <section
      ref={containerRef}
      id="manifesto"
      className="relative w-full bg-[#050607] text-[#F5F3EF] py-28 sm:py-36 lg:py-48 overflow-hidden border-t border-[rgba(255,255,255,0.06)] select-none"
      aria-label="APEX Philosophy Manifesto"
    >
      <div className="max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16">
        {/* Subtle Horizontal Architectural Reveal Line that extends across the section */}
        <div className="w-full h-px bg-[rgba(255,255,255,0.08)] mb-16 sm:mb-20 relative overflow-hidden" aria-hidden="true">
          <motion.div
            style={{ width: shouldReduceMotion ? "100%" : lineWidth }}
            className="absolute left-0 top-0 bottom-0 bg-gradient-to-r from-[rgba(255,255,255,0.15)] via-[#FF4A16]/50 to-[rgba(255,255,255,0.1)]"
          />
        </div>

        {/* Asymmetrical Typography-Led Composition */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          {/* Left Column: Eyebrow + Mascot in Negative Space */}
          <div className="lg:col-span-3 flex flex-col justify-between h-full">
            <div>
              <motion.div
                initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                className="font-code text-[10px] sm:text-[11px] tracking-[0.28em] text-[#737575] uppercase font-medium flex items-center gap-2.5 mb-10"
              >
                <span className="w-3 h-px bg-[#FF4A16]" aria-hidden="true" />
                <span>A DIFFERENT KIND OF SYSTEM</span>
              </motion.div>

              {/* Thoughtful Mascot in Negative Space - Small and Secondary */}
              <div className="hidden lg:block pt-8 opacity-85 hover:opacity-100 transition-opacity">
                <ApexMascot
                  variant="thinking"
                  height={108}
                  animateIdle={true}
                  alt="APEX companion in thoughtful reflection"
                />
                <span className="block mt-3 font-code text-[9px] tracking-[0.2em] text-[#737575] uppercase">
                  PHILOSOPHY // REASONING
                </span>
              </div>
            </div>
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
                      : { opacity: 0, y: "110%" }
                  }
                  whileInView={{ opacity: 1, y: 0 }}
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
                      : { opacity: 0, y: "110%" }
                  }
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-60px" }}
                  transition={{ duration: 0.85, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                  className="block font-editorial italic font-normal text-[#FF7A45]"
                >
                  beginning.
                </motion.span>
              </span>
            </h2>

            {/* Word-By-Word Scroll-Linked Reading Emphasis */}
            <div className="mb-16 sm:mb-20 max-w-[840px]">
              <ScrollWordReveal
                tokens={manifestoTokens}
                className="text-[#B2B0AD] text-xl sm:text-2xl lg:text-[28px] font-normal leading-[1.52] tracking-wide"
              />
            </div>

            {/* Ordered Progression: 01 REASON → 02 ORCHESTRATE → 03 EVOLVE */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-8 pt-10 border-t border-[rgba(255,255,255,0.08)]">
              {progressionSteps.map((step, idx) => (
                <motion.div
                  key={step.num}
                  initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0, y: 14 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "-40px" }}
                  transition={{
                    duration: 0.65,
                    delay: idx * 0.15,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className={`flex flex-col gap-3 group ${
                    idx > 0 ? "sm:border-l sm:border-[rgba(255,255,255,0.08)] sm:pl-8" : ""
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span className="font-code text-[11px] text-[#FF4A16] font-semibold tracking-wider">
                      {step.num}
                    </span>
                    <span className="w-1.5 h-px bg-[#FF4A16]/50" />
                    <span className="font-code text-xs tracking-[0.24em] text-[#F5F3EF] uppercase font-semibold group-hover:text-[#FF7A45] transition-colors">
                      {step.title}
                    </span>
                  </div>
                  <span className="text-[#8C9295] text-xs font-normal leading-relaxed group-hover:text-[#B2B0AD] transition-colors">
                    {step.desc}
                  </span>
                </motion.div>
              ))}
            </div>

            {/* Mobile Mascot placement if screen is small */}
            <div className="block lg:hidden pt-12">
              <ApexMascot
                variant="thinking"
                height={90}
                animateIdle={true}
                alt="APEX companion in thoughtful reflection"
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
