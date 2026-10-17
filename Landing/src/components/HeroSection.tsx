"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { motion, useScroll, useTransform, useReducedMotion } from "motion/react";
import {
  ArrowRight,
  ArrowUpRight,
  GitBranch,
  Cpu,
  Database,
  Search,
} from "lucide-react";
import ApexMascot from "./ApexMascot";
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

  const bgScale = useTransform(scrollYProgress, [0, 1], [1, 1.06]);
  const bgTranslateY = useTransform(scrollYProgress, [0, 1], [0, 48]);
  const contentOpacity = useTransform(scrollYProgress, [0, 0.65], [1, 0]);
  const contentTranslateY = useTransform(scrollYProgress, [0, 0.65], [0, -32]);

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

  const capabilityGroups = [
    {
      id: "orchestration",
      title: "Orchestration",
      descriptor: "Intent → Plan → Execute",
      icon: GitBranch,
    },
    {
      id: "models",
      title: "Multi-model",
      descriptor: "Gemini · Groq · Ollama",
      icon: Cpu,
    },
    {
      id: "memory",
      title: "Hybrid memory",
      descriptor: "Redis · ChromaDB",
      icon: Database,
    },
    {
      id: "research",
      title: "Research",
      descriptor: "Ingest · Connect · Retrieve",
      icon: Search,
    },
  ];

  // Parallax offsets
  const bgParallaxX = isDesktop && !shouldReduceMotion ? mousePos.x * -6 : 0;
  const bgParallaxY = isDesktop && !shouldReduceMotion ? mousePos.y * -4 : 0;
  const mascotParallaxX = isDesktop && !shouldReduceMotion ? mousePos.x * 10 : 0;
  const mascotParallaxY = isDesktop && !shouldReduceMotion ? mousePos.y * 6 : 0;

  return (
    <section
      ref={heroRef}
      id="hero"
      className="relative w-full h-[100svh] min-h-[680px] max-h-[1080px] bg-[#050607] flex flex-col justify-between overflow-hidden select-none"
      aria-label="APEX Sovereign Intelligence Hero"
    >
      {/* Background Architectural Portal Canvas with Horizon & Reflective Floor */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden" aria-hidden="true">
        <motion.div
          style={{
            scale: shouldReduceMotion ? 1 : bgScale,
            y: shouldReduceMotion ? 0 : bgTranslateY,
            x: bgParallaxX,
            rotateY: bgParallaxX * 0.05,
            transition: "transform 200ms cubic-bezier(0.2, 0, 0.2, 1)",
          }}
          className="relative w-full h-full will-change-transform"
        >
          <Image
            src="/apex-space-gateway.jpg"
            alt=""
            fill
            priority
            sizes="100vw"
            quality={95}
            className="object-cover object-center will-change-transform"
          />

          {/* Atmospheric Particle Field over horizon */}
          <AtmosphericParticles />

          {/* Directional gradient overlays for crisp editorial readability */}
          <div className="absolute inset-0 bg-gradient-to-r from-[#050607]/85 via-[#050607]/40 to-transparent pointer-events-none" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#050607] via-transparent to-[#050607]/60 pointer-events-none" />

          {/* Warm atmospheric light wash from horizon */}
          <div className="absolute inset-x-0 bottom-0 h-44 bg-gradient-to-t from-[#050607] via-[#050607]/50 to-transparent pointer-events-none" />

          {/* Reflective floor sheen hairline */}
          <div className="absolute inset-x-0 bottom-24 h-px bg-gradient-to-r from-transparent via-[rgba(233,208,173,0.18)] to-transparent pointer-events-none" />
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
        {/* Main Content Area (Split: Left Editorial, Right Foreground Mascot) */}
        <div className="w-full grid grid-cols-1 lg:grid-cols-12 gap-6 items-center my-auto">
          {/* Left Editorial Copy Area (Span 8 cols) */}
          <div className="lg:col-span-8 max-w-[760px] pointer-events-auto">
            {/* Eyebrow: Technical System Identifier */}
            <motion.div
              initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.45, delay: 0.18, ease: MOTION_EASE.enter }}
              className="font-code text-[10px] sm:text-[11px] tracking-[0.26em] text-[#8C9295] uppercase font-medium mb-4 sm:mb-5 flex items-center gap-2.5"
            >
              <span className="w-1.5 h-1.5 rounded-full bg-[#FF4A16] shadow-[0_0_8px_#FF4A16] animate-pulse" aria-hidden="true" />
              <span>PERSONAL AI OS / 24-LAYER ORCHESTRATION</span>
            </motion.div>

            {/* 4-Line Architectural Headline with Masked Editorial Reveal */}
            <h1 className="font-editorial text-[42px] xs:text-[50px] sm:text-6xl lg:text-[74px] xl:text-[84px] leading-[0.98] tracking-[-0.015em] text-[#F3F4F2] mb-4 sm:mb-5 flex flex-col">
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
                        ? "font-editorial italic font-normal text-[#FF7A45]"
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
              transition={{ duration: 0.6, delay: 0.82, ease: MOTION_EASE.enter }}
              className="text-[#9A9FA1] text-xs sm:text-sm lg:text-base font-normal leading-relaxed max-w-[480px] mb-6 sm:mb-7"
            >
              From intent to coordinated execution, APEX connects planning, memory, and action in one intelligent system.
            </motion.p>

            {/* Actions: Brand Warm Orange Primary CTA & Understated Secondary Link */}
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
              className="flex flex-wrap items-center gap-2.5 sm:gap-4 text-[#858B8E] font-code text-[10px] sm:text-[11px] tracking-[0.22em] uppercase font-normal"
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

          {/* Right Side Foreground Mascot with Subtle Desktop Parallax */}
          <div className="lg:col-span-4 flex items-end justify-start lg:justify-end pointer-events-auto">
            <motion.div
              style={{
                x: mascotParallaxX,
                y: mascotParallaxY,
                transition: "transform 240ms cubic-bezier(0.2, 0, 0.2, 1)",
              }}
              className="relative flex flex-col items-start lg:items-end will-change-transform"
            >
              <ApexMascot
                variant="hero"
                height={122}
                animateIdle={true}
                entranceDelay={1.15}
                priority={true}
                alt="APEX companion overlooking the architectural gateway"
                className="drop-shadow-[0_12px_24px_rgba(0,0,0,0.8)] filter opacity-95 hover:opacity-100 transition-opacity"
              />
              <span className="mt-2 font-code text-[9px] tracking-[0.22em] text-[#8C9295]/70 uppercase hidden sm:inline-block">
                SYS::AGENT_01 // READY
              </span>
            </motion.div>
          </div>
        </div>

        {/* Lower Hero Capability Rail */}
        <motion.div
          initial={shouldReduceMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 1.25, ease: MOTION_EASE.enter }}
          className="w-full pt-5 pb-2 border-t border-[rgba(235,240,238,0.08)] pointer-events-auto"
        >
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            {/* 4 Capability Groups */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-6 flex-1">
              {capabilityGroups.map((group, idx) => {
                const Icon = group.icon;
                const isActive = activeStage === idx;
                return (
                  <button
                    key={group.id}
                    type="button"
                    onClick={() => handleCapabilityClick(group.id, idx)}
                    className={`group text-left p-2 sm:p-2.5 rounded-lg border transition-all duration-200 cursor-pointer ${
                      isActive
                        ? "border-[#FF4A16]/50 bg-[#FF4A16]/5"
                        : "border-transparent hover:border-[rgba(235,240,238,0.12)] hover:bg-[#08090A]/40"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <Icon
                        size={13}
                        className={`transition-colors duration-200 ${
                          isActive
                            ? "text-[#FF4A16]"
                            : "text-[#8C9295] group-hover:text-[#F3F4F2]"
                        }`}
                        aria-hidden="true"
                      />
                      <span className="font-code text-[11px] sm:text-xs tracking-[0.16em] uppercase text-[#F3F4F2] font-medium">
                        {group.title}
                      </span>
                    </div>
                    <p className="font-sans text-[11px] sm:text-xs text-[#8C9295] tracking-wide truncate group-hover:text-[#B2B0AD] transition-colors">
                      {group.descriptor}
                    </p>
                  </button>
                );
              })}
            </div>

            {/* Circular Scroll Down Button */}
            <div className="hidden xl:flex items-center pl-6 border-l border-[rgba(235,240,238,0.08)]">
              <button
                type="button"
                onClick={handleScrollDown}
                className="w-11 h-11 rounded-full border border-[rgba(235,240,238,0.2)] hover:border-[rgba(235,240,238,0.6)] flex items-center justify-center transition-all duration-300 group cursor-pointer hover:scale-105 focus-visible:outline-[#FF4A16]"
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
