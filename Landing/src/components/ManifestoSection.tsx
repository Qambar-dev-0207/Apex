"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { motion, AnimatePresence, useReducedMotion } from "motion/react";
import ApexMascot from "./ApexMascot";
import { MOTION_EASE } from "../lib/motion";

interface PhilosophyConcept {
  id: string;
  label: string;
  tagline: string;
  desc: string;
  technicalPrinciple: string;
}

const PHILOSOPHY_CONCEPTS: PhilosophyConcept[] = [
  {
    id: "reason",
    label: "REASON",
    tagline: "Probe assumptions before mutation",
    desc: "Autonomous execution without assumption checking creates compounding error loops. APEX validates goals against Socratic invariants before changing state.",
    technicalPrinciple: "Socratic Invariant Gate with pre-execution boundary validation.",
  },
  {
    id: "orchestrate",
    label: "ORCHESTRATE",
    tagline: "Decompose complexity into order",
    desc: "Complex human intent is broken down into structured, dependency-ordered Task DAGs, routed to specialized models, and executed with deterministic coordination.",
    technicalPrinciple: "Directed Acyclic Graph (Task DAG) execution engine with isolated parallel sub-trees.",
  },
  {
    id: "evolve",
    label: "EVOLVE",
    tagline: "Self-healing through continuous feedback",
    desc: "Execution failures trigger automated snapshot rollbacks rather than cascading errors. Feedback telemetry informs dynamic replanning and long-term memory.",
    technicalPrinciple: "AgentHarness snapshot checkpointing with automated rollback recovery.",
  },
];

export default function ManifestoSection() {
  const [activeConcept, setActiveConcept] = useState<number>(1); // Default to ORCHESTRATE
  const [hasAutoProgressed, setHasAutoProgressed] = useState(false);
  const shouldReduceMotion = useReducedMotion();

  // Subtle initial progression REASON -> ORCHESTRATE on initial view if motion enabled
  useEffect(() => {
    if (shouldReduceMotion || hasAutoProgressed) return;

    const timer1 = setTimeout(() => {
      setActiveConcept(0); // REASON
    }, 1200);

    const timer2 = setTimeout(() => {
      setActiveConcept(1); // ORCHESTRATE
      setHasAutoProgressed(true);
    }, 3200);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, [shouldReduceMotion, hasAutoProgressed]);

  return (
    <section
      id="manifesto"
      className="relative w-full bg-[#050607] border-t border-[rgba(255,255,255,0.08)] select-none overflow-hidden"
      aria-label="A Different Kind of System"
    >
      {/* Main Wide Panoramic Banner Container */}
      <div className="relative w-full min-h-[520px] sm:min-h-[580px] lg:min-h-[640px] flex flex-col justify-between overflow-hidden">
        {/* Background Artwork: Brutalist Obsidian Architecture */}
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
          {/* Subtle directional gradient on left to ensure typography contrast */}
          <div className="absolute inset-y-0 left-0 w-full sm:w-[55%] lg:w-[48%] bg-gradient-to-r from-[#050607]/90 via-[#050607]/45 to-transparent pointer-events-none" />
          <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[#050607] to-transparent pointer-events-none" />
        </div>

        {/* Top/Middle Area: Left Editorial Typography & Right Thinking Mascot */}
        <div className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-14 pt-12 sm:pt-16 lg:pt-20 pb-4 flex-1 flex flex-col justify-between pointer-events-none">
            {/* Left Editorial Copy Area (Span 8 cols) */}
            <div className="lg:col-span-8 max-w-[560px]">
              {/* Eyebrow: - A DIFFERENT KIND OF SYSTEM */}
              <motion.div
                initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 6 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.45, ease: MOTION_EASE.enter }}
                className="flex items-center gap-2 mb-3.5 font-sans text-[11px] sm:text-xs tracking-[0.24em] text-[#8C9295] uppercase font-medium"
              >
                <span className="text-[#FF4A16] font-bold text-sm leading-none">—</span>
                <span>A DIFFERENT KIND OF SYSTEM</span>
              </motion.div>

              {/* Headline: A prompt is only the beginning. */}
              <h2 className="font-editorial text-4xl sm:text-5xl lg:text-[56px] xl:text-[64px] leading-[1.04] tracking-tight text-[#F5F3EF] mb-4">
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
                    transition={{ duration: 0.85, delay: 0.1, ease: MOTION_EASE.enter }}
                    className="block font-normal"
                  >
                    the <span className="font-editorial italic font-normal text-[#FF7A45]">beginning.</span>
                  </motion.span>
                </span>
              </h2>

              {/* Subtitle Copy */}
              <motion.p
                initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.6, delay: 0.2, ease: MOTION_EASE.enter }}
                className="text-[#9A9FA1] text-[13px] sm:text-sm lg:text-[15px] font-normal leading-[1.6] max-w-[480px]"
              >
                The real work begins after understanding the intent —
                <br className="hidden sm:inline" /> planning the steps, coordinating execution, validating
                <br className="hidden sm:inline" /> results, and carrying useful context forward.
              </motion.p>
            </div>

          {/* Bottom Area: Segmented Interactive Concepts (REASON | ORCHESTRATE | EVOLVE) */}
          <div className="w-full pt-10 sm:pt-14 pb-4 pointer-events-auto">
            {/* Interactive Concept Controls */}
            <div className="flex flex-wrap items-center gap-6 sm:gap-10 mb-4" role="tablist">
              {PHILOSOPHY_CONCEPTS.map((concept, idx) => {
                const isActive = activeConcept === idx;

                return (
                  <button
                    key={concept.id}
                    role="tab"
                    aria-selected={isActive}
                    type="button"
                    onClick={() => {
                      setActiveConcept(idx);
                      setHasAutoProgressed(true);
                    }}
                    className="flex flex-col items-start gap-2 group cursor-pointer text-left focus-visible:outline-[#FF4A16] transition-transform hover:translate-y-[-1px]"
                  >
                    {/* Top Indicator Line */}
                    <div
                      className={`w-14 sm:w-24 h-[2px] rounded-full transition-all duration-300 ${
                        isActive
                          ? "bg-[#FF4A16] shadow-[0_0_12px_#FF4A16]"
                          : "bg-[rgba(255,255,255,0.18)] group-hover:bg-[rgba(255,255,255,0.4)]"
                      }`}
                    />

                    {/* Concept Label */}
                    <span
                      className={`font-code text-xs sm:text-[13px] tracking-[0.22em] uppercase font-bold transition-colors duration-200 ${
                        isActive
                          ? "text-[#FF4A16]"
                          : "text-[#8C9295] group-hover:text-white"
                      }`}
                    >
                      {concept.label}
                    </span>
                  </button>
                );
              })}
            </div>

            {/* Concept Detail Transition Panel */}
            <div className="min-h-[56px] pt-2 border-t border-[rgba(255,255,255,0.06)] flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <AnimatePresence mode="wait">
                <motion.div
                  key={PHILOSOPHY_CONCEPTS[activeConcept].id}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  transition={{ duration: 0.26, ease: MOTION_EASE.interface }}
                  className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4"
                >
                  <span className="font-sans text-xs sm:text-sm text-[#F5F3EF] font-medium">
                    {PHILOSOPHY_CONCEPTS[activeConcept].tagline}
                  </span>
                  <span className="hidden sm:inline text-[#8C9295]/40">—</span>
                  <span className="text-[11px] sm:text-xs text-[#8C9295] max-w-[620px]">
                    {PHILOSOPHY_CONCEPTS[activeConcept].desc}
                  </span>
                </motion.div>
              </AnimatePresence>

              <span className="font-code text-[10px] tracking-widest text-[#FF4A16]/80 uppercase hidden md:inline">
                {PHILOSOPHY_CONCEPTS[activeConcept].technicalPrinciple}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
