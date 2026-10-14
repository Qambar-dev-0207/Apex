"use client";

import Image from "next/image";
import { motion, useReducedMotion } from "motion/react";
import { ArrowUpRight } from "lucide-react";

export default function FinalCTA() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <section
      id="final-cta"
      className="relative w-full bg-[#050607] border-t border-[rgba(255,255,255,0.08)] select-none overflow-hidden"
      aria-label="Beyond the prompt"
    >
      {/* Wide Panoramic Landscape Banner Container */}
      <div className="relative w-full min-h-[380px] sm:min-h-[440px] lg:min-h-[500px] flex items-center overflow-hidden">
        {/* Panoramic Landscape Background Artwork */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          <Image
            src="/apex-beyond-prompt.jpg"
            alt="APEX companion overlooking the planetary horizon"
            fill
            priority
            sizes="100vw"
            quality={92}
            className="object-cover object-center scale-[1.01]"
          />
          {/* Subtle Right-Side Gradient to guarantee crisp readability of headline and button */}
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-[#050607]/20 to-[#050607]/75 sm:to-[#050607]/60 pointer-events-none" />
          <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-[#050607] to-transparent pointer-events-none" />
        </div>

        {/* Foreground Content: Right-Aligned Composition matching exact reference */}
        <div className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 flex items-center justify-end py-16 sm:py-20 lg:py-24">
          <div className="max-w-[540px] text-left">
            {/* Masked Editorial Headline: Beyond the prompt. */}
            <h2 className="font-editorial text-4xl sm:text-5xl lg:text-6xl text-[#F5F3EF] tracking-tight leading-[1.08] mb-3">
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
                  Beyond the prompt.
                </motion.span>
              </span>
            </h2>

            {/* Supporting Copy */}
            <motion.p
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.6, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
              className="text-[#D8D6D2] text-sm sm:text-base font-normal leading-relaxed mb-6"
            >
              Explore the architecture behind APEX.
            </motion.p>

            {/* Orange Pill Action Button: Explore APEX on GitHub ↗ */}
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.55, delay: 0.28, ease: [0.16, 1, 0.3, 1] }}
            >
              <a
                href="https://github.com/Qambar-dev-0207/Apex"
                target="_blank"
                rel="noopener noreferrer"
                className="group inline-flex items-center gap-2.5 px-6 sm:px-8 py-3 sm:py-3.5 rounded-full bg-[#FF4A16] hover:bg-[#ff5d2e] text-white font-sans text-xs sm:text-sm font-semibold tracking-wide transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_24px_rgba(255,74,22,0.4)] cursor-pointer"
              >
                <span>Explore APEX on GitHub</span>
                <ArrowUpRight
                  size={15}
                  className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                  aria-hidden="true"
                />
              </a>
            </motion.div>
          </div>
        </div>
      </div>
    </section>
  );
}
