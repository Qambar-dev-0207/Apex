"use client";

import { useState } from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "motion/react";

interface PhilosophyTab {
  id: string;
  label: string;
  desc: string;
}

const PHILOSOPHY_TABS: PhilosophyTab[] = [
  {
    id: "reason",
    label: "REASON",
    desc: "Probe assumptions with Socratic invariants before initiating state mutation.",
  },
  {
    id: "orchestrate",
    label: "ORCHESTRATE",
    desc: "Decompose goals into deterministic, dependency-ordered Task DAGs.",
  },
  {
    id: "evolve",
    label: "EVOLVE",
    desc: "Continuous self-healing loops with automated snapshot rollback.",
  },
];

export default function ManifestoSection() {
  const [activeTab, setActiveTab] = useState<number>(1); // Default to ORCHESTRATE matching reference
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="manifesto"
      className="relative w-full bg-[#050607] border-t border-[rgba(255,255,255,0.08)] select-none overflow-hidden"
      aria-label="A Different Kind of System"
    >
      {/* Main Wide Panoramic Banner Container matching exact reference */}
      <div className="relative w-full min-h-[480px] sm:min-h-[520px] lg:min-h-[560px] flex flex-col justify-between overflow-hidden">
        {/* Background Artwork: Brutalist Obsidian Architecture + APEX Robot in Thinking Pose */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          <Image
            src="/apex-manifesto-bg.jpg"
            alt="APEX — A Different Kind of System"
            fill
            priority
            sizes="100vw"
            quality={95}
            className="object-cover object-[center_42%] scale-[1.01]"
          />
          {/* Subtle directional gradient on far-left to ensure typography contrast */}
          <div className="absolute inset-y-0 left-0 w-full sm:w-[50%] lg:w-[44%] bg-gradient-to-r from-[#050607]/80 via-[#050607]/35 to-transparent pointer-events-none" />
        </div>

        {/* Top/Middle Area: Left Editorial Typography */}
        <div className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-14 pt-12 sm:pt-14 lg:pt-16 pb-4 flex-1 flex flex-col justify-between pointer-events-none">
          <div className="max-w-[520px] pointer-events-auto">
            {/* Eyebrow: - A DIFFERENT KIND OF SYSTEM */}
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 6 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
              className="flex items-center gap-2 mb-3.5 font-sans text-[11px] sm:text-xs tracking-[0.24em] text-[#8C9295] uppercase font-medium"
            >
              <span className="text-[#FF4A16] font-bold text-sm leading-none">—</span>
              <span>A DIFFERENT KIND OF SYSTEM</span>
            </motion.div>

            {/* Headline: A prompt is only the beginning. */}
            <h2 className="font-editorial text-4xl sm:text-5xl lg:text-[54px] xl:text-[60px] leading-[1.06] tracking-tight text-[#F5F3EF] mb-3.5">
              <span className="overflow-mask block relative py-0.5">
                <motion.span
                  initial={
                    shouldReduceMotion
                      ? { opacity: 1, y: 0 }
                      : { opacity: 0, y: "110%" }
                  }
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.75, ease: [0.16, 1, 0.3, 1] }}
                  className="block font-normal"
                >
                  A prompt is only
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
                  transition={{ duration: 0.85, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
                  className="block font-normal"
                >
                  the <span className="italic font-normal">beginning.</span>
                </motion.span>
              </span>
            </h2>

            {/* Subtitle Copy matching reference 3-line structure */}
            <motion.p
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="text-[#9A9FA1] text-[13px] sm:text-sm lg:text-[14.5px] font-normal leading-[1.55] max-w-[460px]"
            >
              The real work begins after understanding the intent —
              <br className="hidden sm:inline" /> planning the steps, coordinating execution, validating
              <br className="hidden sm:inline" /> results, and carrying useful context forward.
            </motion.p>
          </div>

          {/* Bottom Area: Segmented Tabs (REASON | ORCHESTRATE | EVOLVE) */}
          <div className="w-full pt-10 sm:pt-14 pb-4 pointer-events-auto">
            {/* Interactive Tabs */}
            <div className="flex items-center gap-6 sm:gap-10">
              {PHILOSOPHY_TABS.map((tab, idx) => {
                const isActive = activeTab === idx;

                return (
                  <button
                    key={tab.id}
                    type="button"
                    onClick={() => setActiveTab(idx)}
                    className="flex flex-col items-start gap-2 group cursor-pointer text-left focus-visible:outline-[#FF4A16] transition-transform hover:translate-y-[-1px]"
                  >
                    {/* Top Indicator Line */}
                    <div
                      className={`w-14 sm:w-20 h-[2px] rounded-full transition-all duration-300 ${
                        isActive
                          ? "bg-[#FF4A16] shadow-[0_0_10px_#FF4A16]"
                          : "bg-[rgba(255,255,255,0.18)] group-hover:bg-[rgba(255,255,255,0.4)]"
                      }`}
                    />
                    {/* Tab Label */}
                    <span
                      className={`font-code text-xs sm:text-[13px] tracking-[0.22em] uppercase font-bold transition-colors ${
                        isActive
                          ? "text-[#F5F3EF]"
                          : "text-[#8C9295] group-hover:text-[#D1D5D8]"
                      }`}
                    >
                      {tab.label}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Grounded Technical Specification Toast/Drawer on Click */}
            <div className="mt-5 pt-3 border-t border-[rgba(255,255,255,0.07)] flex flex-wrap items-center justify-between gap-2.5 font-code text-[11px] text-[#8C9295]">
              <div className="flex items-center gap-2">
                <span className="text-[#FF4A16] font-semibold">{PHILOSOPHY_TABS[activeTab].label} //</span>
                <span className="text-[#F5F3EF]">{PHILOSOPHY_TABS[activeTab].desc}</span>
              </div>
              <span className="text-[#8C9295]/60 uppercase tracking-widest text-[10px]">
                SOVEREIGN REASONING ENGINE
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

