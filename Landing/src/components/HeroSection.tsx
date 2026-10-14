"use client";

import { motion } from "motion/react";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import Image from "next/image";

interface HeroSectionProps {
  activeStage?: number;
  onSelectStage?: (stage: number) => void;
}

export default function HeroSection({
  activeStage = 0,
  onSelectStage,
}: HeroSectionProps) {
  const handleScrollDown = (e: React.MouseEvent) => {
    e.preventDefault();
    const target = document.getElementById("architecture");
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleStageClick = (stageIndex: number) => {
    if (onSelectStage) {
      onSelectStage(stageIndex);
    }
    const target = document.getElementById("architecture");
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <section
      id="hero"
      className="relative w-full min-h-[100svh] h-[100svh] min-h-[720px] flex items-center bg-[#08090A] overflow-hidden select-none"
      aria-label="APEX Sovereign Intelligence Hero"
    >
      {/* Clean Monumental Space Background Image */}
      <div className="absolute inset-0 z-0">
        <Image
          src="/apex-space-gateway.jpg"
          alt="APEX Sovereign Intelligence Monumental Gateway"
          fill
          priority
          quality={100}
          className="object-cover object-center pointer-events-none"
        />
        {/* Very subtle edge vignette to ensure complete immersion */}
        <div className="absolute inset-0 bg-gradient-to-r from-[#08090A]/40 via-transparent to-[#08090A]/30 pointer-events-none" />
      </div>

      {/* Hero Foreground Content */}
      <div className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 flex flex-col justify-between h-full pt-28 sm:pt-32 pb-8 pointer-events-none">
        {/* Main Editorial Text Area (Left side) */}
        <div className="max-w-[760px] my-auto pointer-events-auto">
          {/* Eyebrow */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
            className="font-code text-[10px] sm:text-[11px] tracking-[0.26em] text-[#8C9295] uppercase font-medium mb-7"
          >
            PERSONAL AI OS / 24-LAYER ORCHESTRATION
          </motion.div>

          {/* 4-Line Architectural Headline */}
          <motion.h1
            initial={{ opacity: 0, y: 22 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
            className="font-editorial text-[46px] xs:text-[58px] sm:text-7xl lg:text-[86px] xl:text-[98px] leading-[0.98] tracking-[-0.015em] text-[#F3F4F2] mb-7 flex flex-col"
          >
            <span className="font-normal block">An operating</span>
            <span className="font-normal block">system for</span>
            <span className="font-editorial italic font-normal block text-[#F3F4F2]">
              autonomous
            </span>
            <span className="font-editorial italic font-normal block text-[#F3F4F2]">
              intelligence.
            </span>
          </motion.h1>

          {/* Supporting Copy */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.22, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#9A9FA1] text-sm sm:text-base font-normal leading-relaxed max-w-[460px] mb-10"
          >
            From intent to coordinated execution, APEX connects planning, memory, and action in one intelligent system.
          </motion.p>

          {/* Actions: White Pill CTA & Secondary Link */}
          <motion.div
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="flex items-center gap-7"
          >
            {/* Primary Pill Button */}
            <a
              href="#architecture"
              onClick={handleScrollDown}
              className="group inline-flex items-center gap-3 px-7 py-3.5 rounded-full bg-[#F3F4F2] text-[#08090A] font-sans text-xs tracking-wider font-semibold transition-all duration-200 hover:bg-white hover:scale-[1.02] active:scale-[0.98] focus-visible:outline-[#FF3700] shadow-md"
            >
              <span>Explore the architecture</span>
              <ArrowRight
                size={14}
                className="transition-transform duration-200 group-hover:translate-x-1"
                aria-hidden="true"
              />
            </a>

            {/* Secondary CTA */}
            <a
              href="https://github.com/Qambar-dev-0207/Apex"
              target="_blank"
              rel="noopener noreferrer"
              className="group inline-flex items-center gap-1.5 text-[#F3F4F2] hover:text-white font-sans text-xs tracking-wider transition-colors duration-200 py-1 font-medium focus-visible:outline-[#FF3700]"
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
            className={`flex items-center text-left transition-colors duration-300 py-1 cursor-pointer group ${
              activeStage === 0 ? "text-[#F3F4F2] font-semibold" : "text-[#676D70] hover:text-[#9A9FA1]"
            }`}
          >
            <span
              className={`w-[2px] h-3.5 transition-all duration-300 mr-3 rounded-full ${
                activeStage === 0 ? "bg-[#F3F4F2] opacity-100 scale-y-100" : "bg-transparent opacity-0 scale-y-0"
              }`}
            />
            <span className="w-6 inline-block">01</span>
            <span>ORCHESTRATION</span>
          </button>

          {/* Stage 02 */}
          <button
            type="button"
            onClick={() => handleStageClick(1)}
            className={`flex items-center text-left transition-colors duration-300 py-1 cursor-pointer group ${
              activeStage === 1 ? "text-[#F3F4F2] font-semibold" : "text-[#676D70] hover:text-[#9A9FA1]"
            }`}
          >
            <span
              className={`w-[2px] h-3.5 transition-all duration-300 mr-3 rounded-full ${
                activeStage === 1 ? "bg-[#F3F4F2] opacity-100 scale-y-100" : "bg-transparent opacity-0 scale-y-0"
              }`}
            />
            <span className="w-6 inline-block">02</span>
            <span>EXECUTION</span>
          </button>

          {/* Stage 03 */}
          <button
            type="button"
            onClick={() => handleStageClick(2)}
            className={`flex items-center text-left transition-colors duration-300 py-1 cursor-pointer group ${
              activeStage === 2 ? "text-[#F3F4F2] font-semibold" : "text-[#676D70] hover:text-[#9A9FA1]"
            }`}
          >
            <span
              className={`w-[2px] h-3.5 transition-all duration-300 mr-3 rounded-full ${
                activeStage === 2 ? "bg-[#F3F4F2] opacity-100 scale-y-100" : "bg-transparent opacity-0 scale-y-0"
              }`}
            />
            <span className="w-6 inline-block">03</span>
            <span>MEMORY</span>
          </button>
        </div>

        {/* Bottom Bar: Left Metadata Line + Right Scroll Badge */}
        <div className="w-full flex items-center justify-between pt-6 border-t border-[rgba(235,240,238,0.08)] pointer-events-auto">
          {/* Metadata Line */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.4 }}
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
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.5 }}
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
