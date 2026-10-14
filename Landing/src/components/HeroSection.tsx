"use client";

import { useState } from "react";
import Image from "next/image";
import { motion, useReducedMotion } from "motion/react";
import { ArrowRight, ArrowUpRight } from "lucide-react";

export default function HeroSection() {
  const [activeStage, setActiveStage] = useState(0);
  const shouldReduceMotion = useReducedMotion();

  const handleScrollDown = (e: React.MouseEvent) => {
    e.preventDefault();
    const target = document.getElementById("architecture");
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleStageClick = (stageIdx: number) => {
    setActiveStage(stageIdx);
    const targetIds = ["orchestration", "models", "memory"];
    const target = document.getElementById(targetIds[stageIdx]);
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  const headlineLines = [
    { text: "An operating", delay: 0.35, isItalic: false },
    { text: "system for", delay: 0.45, isItalic: false },
    { text: "autonomous", delay: 0.55, isItalic: true },
    { text: "intelligence.", delay: 0.65, isItalic: false },
  ];

  return (
    <section
      id="hero"
      className="relative w-full h-[100svh] min-h-[640px] bg-[#050607] flex flex-col justify-between overflow-hidden select-none"
      aria-label="APEX Sovereign Intelligence Hero"
    >
      {/* Background Architectural Canvas */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden" aria-hidden="true">
        <Image
          src="/apex-space-gateway.jpg"
          alt="APEX Sovereign Gateway"
          fill
          priority
          sizes="100vw"
          quality={90}
          className="object-cover object-center scale-[1.01] will-change-transform"
        />
        {/* Very subtle edge vignette to ensure complete immersion */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#08090A]/40 via-transparent to-[#08090A]/30 pointer-events-none" />
      </div>

      {/* Hero Foreground Content */}
      <div className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 flex flex-col justify-between h-full pt-28 sm:pt-32 pb-8 pointer-events-none">
        {/* Main Editorial Text Area (Left side) */}
        <div className="max-w-[760px] my-auto pointer-events-auto">
          {/* Eyebrow: Appears before the headline */}
          <motion.div
            initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="font-code text-[10px] sm:text-[11px] tracking-[0.26em] text-[#8C9295] uppercase font-medium mb-7 flex items-center gap-2"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16]/80 animate-pulse" aria-hidden="true" />
            <span>PERSONAL AI OS / 24-LAYER ORCHESTRATION</span>
          </motion.div>

          {/* 4-Line Architectural Headline with Masked Editorial Reveal */}
          <h1 className="font-editorial text-[46px] xs:text-[58px] sm:text-7xl lg:text-[86px] xl:text-[98px] leading-[0.98] tracking-[-0.015em] text-[#F3F4F2] mb-7 flex flex-col">
            {headlineLines.map((line, idx) => (
              <span
                key={idx}
                className="overflow-mask block relative py-0.5 sm:py-1"
                style={{ willChange: "transform, opacity, filter" }}
              >
                <motion.span
                  initial={
                    shouldReduceMotion
                      ? { opacity: 1, y: 0, filter: "none" }
                      : { opacity: 0, y: "115%", filter: "blur(3px)" }
                  }
                  animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
                  transition={{
                    duration: line.isItalic ? 0.9 : 0.82,
                    delay: line.delay,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className={`block ${
                    line.isItalic
                      ? "font-editorial italic font-normal text-[#F3F4F2]"
                      : "font-normal"
                  }`}
                >
                  {line.text}
                </motion.span>
              </span>
            ))}
          </h1>

          {/* Supporting Copy */}
          <motion.p
            initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.95, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#9A9FA1] text-sm sm:text-base font-normal leading-relaxed max-w-[460px] mb-10"
          >
            From intent to coordinated execution, APEX connects planning, memory, and action in one intelligent system.
          </motion.p>

          {/* Actions: White Pill CTA & Secondary Link */}
          <motion.div
            initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 1.15, ease: [0.16, 1, 0.3, 1] }}
            className="flex items-center gap-7"
          >
            {/* Primary Pill Button */}
            <a
              href="#architecture"
              onClick={handleScrollDown}
              className="group inline-flex items-center gap-3 px-7 py-3.5 rounded-full bg-[#F3F4F2] text-[#08090A] font-sans text-xs tracking-wider font-semibold transition-all duration-200 hover:bg-white hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-[#FF4A16] shadow-md cursor-pointer"
            >
              <span>Explore the architecture</span>
              <ArrowRight
                size={14}
                className="transition-transform duration-200 group-hover:translate-x-1.5"
                aria-hidden="true"
              />
            </a>

            {/* Secondary CTA */}
            <a
              href="https://github.com/Qambar-dev-0207/Apex"
              target="_blank"
              rel="noopener noreferrer"
              className="group link-underline inline-flex items-center gap-1.5 text-[#F3F4F2] hover:text-white font-sans text-xs tracking-wider transition-colors duration-200 py-1 font-medium focus-visible:outline-[#FF4A16]"
            >
              <span>View source</span>
              <ArrowUpRight
                size={13}
                className="transition-transform duration-200 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 text-[#9A9FA1] group-hover:text-white"
                aria-hidden="true"
              />
            </a>
          </motion.div>
        </div>

        {/* Right Side Vertical Stage Indicators (01, 02, 03) */}
        <div className="hidden lg:flex flex-col gap-4 absolute right-12 xl:right-16 top-1/2 -translate-y-1/2 pointer-events-auto font-code text-[11px] tracking-[0.24em] uppercase">
          {/* Stage 01 */}
          <button
            type="button"
            onClick={() => handleStageClick(0)}
            className={`flex items-center text-left transition-colors duration-200 py-1 cursor-pointer group ${
              activeStage === 0 ? "text-[#F3F4F2] font-semibold" : "text-[#737575] hover:text-[#B2B0AD]"
            }`}
          >
            <span
              className={`w-[2px] transition-all duration-300 mr-3 rounded-full ${
                activeStage === 0 ? "h-4 bg-[#FF4A16] opacity-100" : "h-2 bg-transparent opacity-0"
              }`}
              aria-hidden="true"
            />
            <span className="w-6 inline-block">01</span>
            <span>ORCHESTRATION</span>
          </button>

          {/* Stage 02 */}
          <button
            type="button"
            onClick={() => handleStageClick(1)}
            className={`flex items-center text-left transition-colors duration-200 py-1 cursor-pointer group ${
              activeStage === 1 ? "text-[#F3F4F2] font-semibold" : "text-[#737575] hover:text-[#B2B0AD]"
            }`}
          >
            <span
              className={`w-[2px] transition-all duration-300 mr-3 rounded-full ${
                activeStage === 1 ? "h-4 bg-[#FF4A16] opacity-100" : "h-2 bg-transparent opacity-0"
              }`}
              aria-hidden="true"
            />
            <span className="w-6 inline-block">02</span>
            <span>EXECUTION</span>
          </button>

          {/* Stage 03 */}
          <button
            type="button"
            onClick={() => handleStageClick(2)}
            className={`flex items-center text-left transition-colors duration-200 py-1 cursor-pointer group ${
              activeStage === 2 ? "text-[#F3F4F2] font-semibold" : "text-[#737575] hover:text-[#B2B0AD]"
            }`}
          >
            <span
              className={`w-[2px] transition-all duration-300 mr-3 rounded-full ${
                activeStage === 2 ? "h-4 bg-[#FF4A16] opacity-100" : "h-2 bg-transparent opacity-0"
              }`}
              aria-hidden="true"
            />
            <span className="w-6 inline-block">03</span>
            <span>MEMORY</span>
          </button>
        </div>

        {/* Bottom Bar: Left Metadata Line + Right Scroll Badge */}
        <div className="w-full flex items-center justify-between pt-6 border-t border-[rgba(235,240,238,0.08)] pointer-events-auto">
          {/* Metadata Line */}
          <motion.div
            initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 1.25 }}
            className="flex flex-wrap items-center gap-3 sm:gap-5 text-[#858B8E] font-code text-[10px] sm:text-[11px] tracking-[0.22em] uppercase font-normal"
          >
            <span>24 LAYERS</span>
            <span className="text-[#858B8E]/50 text-xs" aria-hidden="true">•</span>
            <span>TASK DAGs</span>
            <span className="text-[#858B8E]/50 text-xs" aria-hidden="true">•</span>
            <span>HYBRID MEMORY</span>
          </motion.div>

          {/* Circular SCROLL Badge on Bottom Right */}
          <motion.button
            type="button"
            onClick={handleScrollDown}
            initial={shouldReduceMotion ? { opacity: 1, scale: 1 } : { opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 1.35 }}
            className="w-14 h-14 rounded-full border border-[rgba(235,240,238,0.25)] hover:border-[rgba(235,240,238,0.6)] flex items-center justify-center transition-all duration-300 group cursor-pointer"
            aria-label="Scroll to architecture"
          >
            <span className="font-code text-[9px] tracking-[0.25em] text-[#9A9FA1] group-hover:text-[#F3F4F2] uppercase transition-colors">
              SCROLL
            </span>
          </motion.button>
        </div>
      </div>
    </section>
  );
}
