"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { motion, useScroll, useTransform, useReducedMotion } from "motion/react";
import {
  ArrowRight,
  ArrowUpRight,
  Database,
  Search,
} from "lucide-react";
import AtmosphericParticles from "./AtmosphericParticles";
import { MOTION_EASE } from "../lib/motion";

export default function HeroSection() {
  const [activeStage, setActiveStage] = useState(0);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [isDesktop, setIsDesktop] = useState(false);
  const heroRef = useRef<HTMLElement | null>(null);
  const shouldReduceMotion = useReducedMotion();

  // Scroll-linked camera push & text drift
  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
  });

  const bgScale = useTransform(scrollYProgress, [0, 1], [1, 1.05]);
  const bgTranslateY = useTransform(scrollYProgress, [0, 1], [0, 40]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.65], [1, 0]);
  const contentTranslateY = useTransform(scrollYProgress, [0, 0.65], [0, -28]);

  // Subtle pointer parallax listener for desktop
  useEffect(() => {
    const checkDesktop = () => {
      setIsDesktop(window.innerWidth >= 1024 && !("ontouchstart" in window));
    };
    checkDesktop();
    window.addEventListener("resize", checkDesktop);

    const handleMouseMove = (e: MouseEvent) => {
      if (!isDesktop || shouldReduceMotion) return;
      const { innerWidth, innerHeight } = window;
      const x = (e.clientX / innerWidth - 0.5) * 2; // -1 to 1
      const y = (e.clientY / innerHeight - 0.5) * 2;
      setMousePos({ x, y });
    };

    window.addEventListener("mousemove", handleMouseMove, { passive: true });
    return () => {
      window.removeEventListener("resize", checkDesktop);
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, [isDesktop, shouldReduceMotion]);

  const handleScrollDown = (e: React.MouseEvent) => {
    e.preventDefault();
    const target = document.getElementById("manifesto");
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  };

  const handleCapabilityClick = (targetId: string, idx: number) => {
    setActiveStage(idx);
    const target = document.getElementById(targetId);
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

  // Parallax offsets
  const bgParallaxX = isDesktop && !shouldReduceMotion ? mousePos.x * -5 : 0;
  const bgParallaxY = isDesktop && !shouldReduceMotion ? mousePos.y * -3 : 0;

  return (
    <section
      ref={heroRef}
      id="hero"
      className="relative w-full h-[100svh] min-h-[640px] max-h-[1080px] bg-[#050607] flex flex-col justify-between overflow-hidden select-none"
      aria-label="APEX Sovereign Intelligence Hero"
    >
      {/* Background Architectural Portal Canvas with Horizon, Sunlight Rays & Reflective Floor */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden" aria-hidden="true">
        <motion.div
          style={{
            scale: shouldReduceMotion ? 1 : bgScale,
            y: shouldReduceMotion ? 0 : bgTranslateY,
            x: bgParallaxX,
            transition: "transform 240ms cubic-bezier(0.2, 0, 0.2, 1)",
          }}
          className="relative w-full h-full will-change-transform"
        >
          <Image
            src="/apex-space-gateway-hero.jpg"
            alt=""
            fill
            priority
            sizes="100vw"
            quality={95}
            className="object-cover object-center will-change-transform"
          />

          {/* Atmospheric Particle Field over horizon */}
          <AtmosphericParticles />

          {/* Directional gradient overlays: Dark on left for high-contrast editorial typography, open on right for sunburst & planet */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#050607]/90 via-[#050607]/45 via-45% to-transparent pointer-events-none" />
          <div className="absolute inset-x-0 top-0 h-24 bg-gradient-to-b from-[#050607]/60 to-transparent pointer-events-none" />
          <div className="absolute inset-x-0 bottom-0 h-32 bg-gradient-to-t from-[#050607]/80 via-[#050607]/20 to-transparent pointer-events-none" />
        </motion.div>
      </div>

      {/* Hero Foreground Content */}
      <motion.div
        style={{
          opacity: shouldReduceMotion ? 1 : contentOpacity,
          y: shouldReduceMotion ? 0 : contentTranslateY,
        }}
        className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 flex flex-col justify-between flex-1 pt-24 sm:pt-28 pb-3 sm:pb-4 pointer-events-none"
      >
        {/* Main Content Area (Left-Aligned Editorial Typography) */}
        <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-6 items-center my-auto">
          {/* Left Editorial Copy Area */}
          <div className="lg:col-span-8 max-w-[760px] pointer-events-auto">
            {/* Eyebrow: Technical System Identifier */}
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.18, ease: MOTION_EASE.enter }}
              className="font-code text-[10px] sm:text-[11px] tracking-[0.24em] text-[#8C9295] uppercase font-medium mb-4 sm:mb-5 flex items-center gap-2.5"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16] shadow-[0_0_8px_#FF4A16] animate-pulse" aria-hidden="true" />
              <span>PERSONAL AI OS / 24-LAYER ORCHESTRATION</span>
            </motion.div>

            {/* 4-Line Architectural Headline with Masked Editorial Reveal */}
            <h1 className="font-editorial text-[48px] xs:text-[54px] sm:text-6xl lg:text-[76px] xl:text-[84px] leading-[0.96] tracking-[-0.015em] text-[#FFFFFF] mb-4 sm:mb-5 flex flex-col">
              {headlineLines.map((line, idx) => (
                <span
                  key={idx}
                  className="overflow-mask block relative py-0.5"
                  style={{ willChange: "transform, opacity" }}
                >
                  <motion.span
                    initial={
                      shouldReduceMotion
                        ? { opacity: 1, y: 0 }
                        : { opacity: 0, y: "115%" }
                    }
                    animate={{ opacity: 1, y: 0 }}
                    transition={{
                      duration: line.isItalic ? 0.88 : 0.8,
                      delay: line.delay,
                      ease: MOTION_EASE.enter,
                    }}
                    className={`block ${
                      line.isItalic
                        ? "font-editorial italic font-normal text-[#FF4A16]"
                        : "font-normal text-white"
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
              transition={{ duration: 0.6, delay: 0.82, ease: MOTION_EASE.enter }}
              className="text-[#9A9FA1] text-xs sm:text-sm lg:text-[15px] font-normal leading-relaxed max-w-[490px] mb-6 sm:mb-7"
            >
              From intent to coordinated execution, APEX connects planning, memory, and action in one intelligent system.
            </motion.p>

            {/* Actions: Brand Warm Orange Primary CTA & Secondary Link */}
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.98, ease: MOTION_EASE.enter }}
              className="flex flex-wrap items-center gap-5 sm:gap-6 mb-5 sm:mb-6"
            >
              {/* Primary Action Button */}
              <a
                href="#manifesto"
                onClick={handleScrollDown}
                className="group inline-flex items-center gap-2.5 px-6 sm:px-7 py-3 sm:py-3.5 rounded-full bg-[#FF4A16] hover:bg-[#ff5d2e] text-white font-sans text-xs tracking-wider font-semibold transition-all duration-200 hover:scale-[1.02] active:scale-[0.98] shadow-[0_0_24px_rgba(255,74,22,0.35)] focus-visible:outline-[#FF4A16] cursor-pointer"
              >
                <span>Enter the threshold</span>
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

            {/* Technical Metadata Row beneath CTAs */}
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.65, delay: 1.12 }}
              className="flex flex-wrap items-center gap-2.5 sm:gap-4 text-[#858B8E] font-code text-[10px] sm:text-[11px] tracking-[0.24em] uppercase font-normal"
            >
              <span>24 layers</span>
              <span className="text-[#858B8E]/40" aria-hidden="true">·</span>
              <span>Task DAGs</span>
              <span className="text-[#858B8E]/40" aria-hidden="true">·</span>
              <span>Hybrid memory</span>
              <span className="text-[#858B8E]/40" aria-hidden="true">·</span>
              <span>Multi-model execution</span>
            </motion.div>
          </div>

          {/* Right Column (Architecture & Companion Overview Area) */}
          <div className="hidden lg:block lg:col-span-4 h-full pointer-events-none" />
        </div>

        {/* Lower Hero Capability Rail matching reference layout 1:1 */}
        <motion.div
          initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 1.25, ease: MOTION_EASE.enter }}
          className="w-full pt-4 sm:pt-5 pb-2 border-t border-[rgba(255,255,255,0.08)] pointer-events-auto"
        >
          <div className="w-full flex items-center justify-between">
            {/* 4 Capability Groups */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 lg:gap-8 flex-1">
              {/* Item 1: ORCHESTRATION */}
              <button
                type="button"
                onClick={() => handleCapabilityClick("orchestration", 0)}
                className="group flex items-center text-left transition-colors duration-200 cursor-pointer"
              >
                <div className="w-[2px] h-6 bg-[#FF4A16] mr-3 sm:mr-3.5 shrink-0" />
                <div className="flex items-center gap-2.5 sm:gap-3">
                  <svg
                    viewBox="0 0 18 18"
                    className="w-4 h-4 text-[#FF4A16] shrink-0"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.75"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M5 4C3 6 3 12 5 14" />
                    <path d="M13 4C15 6 15 12 13 14" />
                    <circle cx="9" cy="9" r="1.5" fill="currentColor" />
                  </svg>
                  <div>
                    <div className="font-code text-[11px] sm:text-xs tracking-[0.18em] uppercase font-semibold">
                      <span className="text-[#FF4A16]">ORCH</span>
                      <span className="text-[#F3F4F2]">ESTRATION</span>
                    </div>
                    <p className="font-sans text-[11px] sm:text-xs text-[#8C9295] tracking-wide">
                      Intent → Plan → Execute
                    </p>
                  </div>
                </div>
              </button>

              {/* Item 2: MULTI-MODEL */}
              <button
                type="button"
                onClick={() => handleCapabilityClick("models", 1)}
                className="group flex items-center text-left transition-colors duration-200 cursor-pointer pl-0 md:pl-4 lg:pl-6 border-l-0 md:border-l border-[rgba(255,255,255,0.08)]"
              >
                <div className="flex items-center gap-2.5 sm:gap-3">
                  <svg
                    viewBox="0 0 24 24"
                    className="w-4 h-4 text-[#8C9295] group-hover:text-[#F3F4F2] transition-colors shrink-0"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="1.75"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    aria-hidden="true"
                  >
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z" />
                    <polyline points="3.27 6.96 12 12.01 20.73 6.96" />
                    <line x1="12" y1="22.08" x2="12" y2="12" />
                  </svg>
                  <div>
                    <div className="font-code text-[11px] sm:text-xs tracking-[0.18em] uppercase text-[#F3F4F2] font-semibold group-hover:text-white transition-colors">
                      MULTI-MODEL
                    </div>
                    <p className="font-sans text-[11px] sm:text-xs text-[#8C9295] tracking-wide group-hover:text-[#B2B0AD] transition-colors">
                      Gemini · Groq · Ollama
                    </p>
                  </div>
                </div>
              </button>

              {/* Item 3: HYBRID MEMORY */}
              <button
                type="button"
                onClick={() => handleCapabilityClick("memory", 2)}
                className="group flex items-center text-left transition-colors duration-200 cursor-pointer pl-0 md:pl-4 lg:pl-6 border-l-0 md:border-l border-[rgba(255,255,255,0.08)]"
              >
                <div className="flex items-center gap-2.5 sm:gap-3">
                  <Database
                    size={15}
                    className="text-[#8C9295] group-hover:text-[#F3F4F2] transition-colors shrink-0"
                    strokeWidth={1.75}
                    aria-hidden="true"
                  />
                  <div>
                    <div className="font-code text-[11px] sm:text-xs tracking-[0.18em] uppercase text-[#F3F4F2] font-semibold group-hover:text-white transition-colors">
                      HYBRID MEMORY
                    </div>
                    <p className="font-sans text-[11px] sm:text-xs text-[#8C9295] tracking-wide group-hover:text-[#B2B0AD] transition-colors">
                      Redis · ChromaDB
                    </p>
                  </div>
                </div>
              </button>

              {/* Item 4: RESEARCH */}
              <button
                type="button"
                onClick={() => handleCapabilityClick("research", 3)}
                className="group flex items-center text-left transition-colors duration-200 cursor-pointer pl-0 md:pl-4 lg:pl-6 border-l-0 md:border-l border-[rgba(255,255,255,0.08)]"
              >
                <div className="flex items-center gap-2.5 sm:gap-3">
                  <Search
                    size={15}
                    className="text-[#8C9295] group-hover:text-[#F3F4F2] transition-colors shrink-0"
                    strokeWidth={1.75}
                    aria-hidden="true"
                  />
                  <div>
                    <div className="font-code text-[11px] sm:text-xs tracking-[0.18em] uppercase text-[#F3F4F2] font-semibold group-hover:text-white transition-colors">
                      RESEARCH
                    </div>
                    <p className="font-sans text-[11px] sm:text-xs text-[#8C9295] tracking-wide group-hover:text-[#B2B0AD] transition-colors">
                      Ingest · Connect · Retrieve
                    </p>
                  </div>
                </div>
              </button>
            </div>

            {/* Circular Scroll Down Button */}
            <div className="hidden lg:flex items-center pl-6 border-l border-[rgba(255,255,255,0.08)] ml-6 shrink-0">
              <button
                type="button"
                onClick={handleScrollDown}
                className="w-10 h-10 rounded-full border border-[rgba(255,255,255,0.22)] hover:border-[rgba(255,255,255,0.6)] flex items-center justify-center transition-all duration-300 group cursor-pointer hover:scale-105 focus-visible:outline-[#FF4A16]"
                aria-label="Scroll to manifesto section"
              >
                <span className="font-code text-[8px] tracking-[0.25em] text-[#9A9FA1] group-hover:text-[#F3F4F2] uppercase transition-colors">
                  SCROLL
                </span>
              </button>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </section>
  );
}
