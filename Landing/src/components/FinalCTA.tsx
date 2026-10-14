"use client";

import { motion, useReducedMotion } from "motion/react";
import { ArrowUp, ArrowUpRight } from "lucide-react";

export default function FinalCTA() {
  const shouldReduceMotion = useReducedMotion();

  const scrollToTop = (e: React.MouseEvent) => {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <section
      id="final-cta"
      className="relative w-full min-h-[70vh] bg-[#050607] border-t border-[rgba(255,255,255,0.1)] flex items-center justify-center overflow-hidden py-32 px-6 sm:px-10 select-none"
      aria-label="Return to the Threshold"
    >
      {/* Background Architectural Monoliths & Warm Ambient Light Source */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden" aria-hidden="true">
        {/* Left Monolithic Pillar */}
        <div className="absolute top-0 bottom-0 left-0 w-[12%] sm:w-[18%] bg-gradient-to-r from-[#020303] via-[#08090A] to-transparent border-r border-[rgba(255,255,255,0.06)]" />

        {/* Right Monolithic Pillar */}
        <div className="absolute top-0 bottom-0 right-0 w-[12%] sm:w-[18%] bg-gradient-to-l from-[#020303] via-[#08090A] to-transparent border-l border-[rgba(255,255,255,0.06)]" />

        {/* Center Vertical Aperture of Warm Light */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-px h-full bg-gradient-to-b from-transparent via-[#E9D0AD]/25 to-transparent" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[340px] h-[340px] rounded-full bg-[#E9D0AD]/5 blur-[120px]" />

        {/* Subtle Horizon Ground Line */}
        <div className="absolute bottom-24 left-0 right-0 h-px bg-gradient-to-r from-transparent via-[rgba(255,255,255,0.12)] to-transparent" />
      </div>

      <div className="relative z-10 max-w-3xl mx-auto text-center flex flex-col items-center">
        {/* Architectural Emblem */}
        <motion.div
          initial={shouldReduceMotion ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="w-10 h-10 mb-8 rounded-full border border-[rgba(255,255,255,0.16)] flex items-center justify-center bg-[#08090A]/80 backdrop-blur-sm"
        >
          <div className="w-1.5 h-1.5 rounded-full bg-[#FF4A16] shadow-[0_0_8px_#FF4A16]" />
        </motion.div>

        {/* Masked Line Reveal Headline: Calm, quiet resolution */}
        <h2 className="font-editorial text-5xl sm:text-7xl lg:text-8xl text-[#F5F3EF] tracking-tight leading-[1.05] mb-6 flex flex-col items-center">
          <span className="overflow-mask block relative py-1">
            <motion.span
              initial={
                shouldReduceMotion
                  ? { opacity: 1, y: 0 }
                  : { opacity: 0, y: "110%", filter: "blur(3px)" }
              }
              whileInView={{ opacity: 1, y: 0, filter: "blur(0px)" }}
              viewport={{ once: true }}
              transition={{ duration: 0.88, ease: [0.16, 1, 0.3, 1] }}
              className="block font-normal"
            >
              Beyond the prompt.
            </motion.span>
          </span>
        </h2>

        {/* Supporting Copy */}
        <motion.p
          initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.65, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
          className="text-[#B2B0AD] text-base sm:text-lg font-light tracking-wide max-w-md mb-12"
        >
          Explore the architecture behind APEX.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 0.35, ease: [0.16, 1, 0.3, 1] }}
          className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6"
        >
          {/* Primary CTA */}
          <a
            href="https://github.com/Qambar-dev-0207/Apex"
            target="_blank"
            rel="noopener noreferrer"
            className="group relative inline-flex items-center gap-2.5 px-8 py-3.5 rounded-full bg-[#F5F3EF] text-[#050607] font-sans text-xs tracking-wider uppercase font-medium hover:bg-white transition-all duration-300 shadow-[0_0_30px_rgba(245,243,239,0.15)] hover:shadow-[0_0_40px_rgba(245,243,239,0.3)] hover:scale-[1.02] active:scale-[0.98] cursor-pointer"
          >
            <span>Explore APEX on GitHub</span>
            <ArrowUpRight
              size={14}
              className="transition-transform duration-300 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
              aria-hidden="true"
            />
          </a>

          {/* Secondary CTA: Return to beginning */}
          <button
            type="button"
            onClick={scrollToTop}
            className="group link-underline inline-flex items-center gap-2 px-6 py-3.5 rounded-full text-[#B2B0AD] hover:text-[#F5F3EF] font-sans text-xs tracking-wider uppercase transition-colors duration-200 border border-[rgba(255,255,255,0.14)] hover:border-[rgba(255,255,255,0.3)] cursor-pointer"
          >
            <span>Return to the beginning</span>
            <ArrowUp
              size={13}
              className="transition-transform duration-200 group-hover:-translate-y-0.5"
              aria-hidden="true"
            />
          </button>
        </motion.div>

        {/* Subordinate Monolithic Note */}
        <div className="mt-20 pt-8 border-t border-[rgba(255,255,255,0.06)] w-full flex justify-center">
          <span className="font-mono text-[10px] tracking-[0.28em] text-[#737575] uppercase">
            24 LAYERS · DETERMINISTIC GRAPHS · IMMUTABLE MEMORY
          </span>
        </div>
      </div>
    </section>
  );
}
