"use client";

import { useRef, useState, useEffect } from "react";
import { useScroll, motion, useTransform } from "motion/react";
import IntelligenceCore from "./IntelligenceCore";
import Image from "next/image";

interface StoryStep {
  label: string;
  headline: string;
  copy: string;
  stageNumber: string;
}

const STORY_STEPS: StoryStep[] = [
  {
    stageNumber: "01 / 03",
    label: "01 / ORCHESTRATION",
    headline: "Intent becomes a plan.",
    copy: "APEX turns a goal into a structured set of dependent tasks, coordinating the steps required to move the work forward.",
  },
  {
    stageNumber: "02 / 03",
    label: "02 / EXECUTION",
    headline: "Complexity moves in parallel.",
    copy: "Specialized agents and coordinated execution paths work through individual tasks before their outputs converge for validation.",
  },
  {
    stageNumber: "03 / 03",
    label: "03 / MEMORY",
    headline: "Context carries forward.",
    copy: "Redis supports active working memory, while ChromaDB provides a foundation for long-term semantic retrieval.",
  },
];

export default function ScrollStory() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [currentProgress, setCurrentProgress] = useState(0);

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end end"],
  });

  useEffect(() => {
    const unsubscribe = scrollYProgress.on("change", (latest) => {
      setCurrentProgress(latest);
    });
    return () => unsubscribe();
  }, [scrollYProgress]);

  // Non-overlapping, clean transitions with clear fade-out windows
  const opacity1 = useTransform(scrollYProgress, [0, 0.08, 0.22, 0.30], [0.2, 1, 1, 0]);
  const y1 = useTransform(scrollYProgress, [0, 0.08, 0.22, 0.30], [12, 0, 0, -12]);

  const opacity2 = useTransform(scrollYProgress, [0.34, 0.42, 0.56, 0.64], [0, 1, 1, 0]);
  const y2 = useTransform(scrollYProgress, [0.34, 0.42, 0.56, 0.64], [12, 0, 0, -12]);

  const opacity3 = useTransform(scrollYProgress, [0.68, 0.76, 0.95, 1], [0, 1, 1, 1]);
  const y3 = useTransform(scrollYProgress, [0.68, 0.76, 0.95, 1], [12, 0, 0, 0]);

  const activeStage = currentProgress < 0.33 ? 0 : currentProgress < 0.66 ? 1 : 2;

  const scrollToStage = (stageIdx: number) => {
    if (!containerRef.current) return;
    const targetScroll = containerRef.current.offsetTop + (stageIdx * 0.33) * containerRef.current.clientHeight;
    window.scrollTo({ top: targetScroll, behavior: "smooth" });
  };

  return (
    <section
      ref={containerRef}
      id="architecture"
      className="relative w-full h-[300vh] bg-[#08090A]"
      aria-label="APEX 24-Layer Architecture Walkthrough"
    >
      {/* Sticky Full-Viewport Scene Container */}
      <div className="sticky top-0 h-screen w-full overflow-hidden flex items-center bg-[#08090A]">
        {/* Subtle Atmospheric Backdrop matching Hero */}
        <div className="absolute inset-0 opacity-25 pointer-events-none -z-10">
          <Image
            src="/apex-space-gateway.jpg"
            alt="Atmospheric Backdrop"
            fill
            className="object-cover object-center filter blur-md"
          />
        </div>
        <div className="absolute inset-0 bg-[#08090A]/80 -z-10" />

        {/* Central 3D Core Visualizer Anchor */}
        <div className="absolute inset-0 pointer-events-none z-0">
          <IntelligenceCore isHeroMode={false} scrollProgress={currentProgress} />
        </div>

        {/* Foreground Content Container */}
        <div className="relative z-10 w-full max-w-[1600px] mx-auto px-6 sm:px-10 lg:px-16 flex flex-col justify-between h-full pt-28 sm:pt-32 pb-8 pointer-events-none">
          {/* Main Content Area */}
          <div className="flex items-center justify-between w-full my-auto">
            {/* Defined Reading Column (Left side) */}
            <div className="w-full max-w-[560px] pointer-events-auto">
              {/* Stage Headline Indicator */}
              <div className="flex items-center gap-3.5 mb-6">
                <span className="font-code text-xs font-semibold tracking-[0.25em] text-[#FF3700]">
                  {STORY_STEPS[activeStage].stageNumber}
                </span>

                <div className="w-20 h-px bg-[rgba(235,240,238,0.15)] relative overflow-hidden">
                  <div
                    className="absolute left-0 top-0 bottom-0 bg-[#FF3700] transition-all duration-150"
                    style={{ width: `${Math.min(100, Math.max(0, currentProgress * 100))}%` }}
                  />
                </div>

                <span className="font-code text-[11px] tracking-[0.2em] text-[#9A9FA1] uppercase">
                  {activeStage === 0 ? "Orchestration" : activeStage === 1 ? "Execution" : "Memory"}
                </span>
              </div>

              {/* Crossfading Narrative Stacks */}
              <div className="relative min-h-[240px]">
                {/* State 01: Orchestration */}
                <motion.div
                  style={{ opacity: opacity1, y: y1 }}
                  className={`absolute inset-0 transition-none ${
                    currentProgress < 0.33 ? "pointer-events-auto" : "pointer-events-none"
                  }`}
                >
                  <div className="font-code text-[11px] tracking-[0.24em] text-[#9A9FA1] uppercase font-medium mb-3">
                    {STORY_STEPS[0].label}
                  </div>
                  <h2 className="font-editorial text-4xl sm:text-6xl tracking-[-0.015em] leading-[1.04] text-[#F3F4F2] mb-5">
                    {STORY_STEPS[0].headline}
                  </h2>
                  <p className="text-[#9A9FA1] text-sm sm:text-base font-normal leading-relaxed max-w-[480px]">
                    {STORY_STEPS[0].copy}
                  </p>
                </motion.div>

                {/* State 02: Execution */}
                <motion.div
                  style={{ opacity: opacity2, y: y2 }}
                  className={`absolute inset-0 transition-none ${
                    currentProgress >= 0.33 && currentProgress < 0.66
                      ? "pointer-events-auto"
                      : "pointer-events-none"
                  }`}
                >
                  <div className="font-code text-[11px] tracking-[0.24em] text-[#9A9FA1] uppercase font-medium mb-3">
                    {STORY_STEPS[1].label}
                  </div>
                  <h2 className="font-editorial text-4xl sm:text-6xl tracking-[-0.015em] leading-[1.04] text-[#F3F4F2] mb-5">
                    {STORY_STEPS[1].headline}
                  </h2>
                  <p className="text-[#9A9FA1] text-sm sm:text-base font-normal leading-relaxed max-w-[480px]">
                    {STORY_STEPS[1].copy}
                  </p>
                </motion.div>

                {/* State 03: Memory */}
                <motion.div
                  style={{ opacity: opacity3, y: y3 }}
                  className={`absolute inset-0 transition-none ${
                    currentProgress >= 0.66 ? "pointer-events-auto" : "pointer-events-none"
                  }`}
                >
                  <div className="font-code text-[11px] tracking-[0.24em] text-[#9A9FA1] uppercase font-medium mb-3">
                    {STORY_STEPS[2].label}
                  </div>
                  <h2 className="font-editorial text-4xl sm:text-6xl tracking-[-0.015em] leading-[1.04] text-[#F3F4F2] mb-5">
                    {STORY_STEPS[2].headline}
                  </h2>
                  <p className="text-[#9A9FA1] text-sm sm:text-base font-normal leading-relaxed max-w-[480px]">
                    {STORY_STEPS[2].copy}
                  </p>
                </motion.div>
              </div>
            </div>

            {/* Right Side Vertical Stage Indicator */}
            <div className="hidden lg:flex flex-col gap-4 font-code text-[11px] tracking-[0.24em] uppercase pointer-events-auto">
              <button
                type="button"
                onClick={() => scrollToStage(0)}
                className={`flex items-center text-left transition-colors duration-300 py-1 cursor-pointer ${
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

              <button
                type="button"
                onClick={() => scrollToStage(1)}
                className={`flex items-center text-left transition-colors duration-300 py-1 cursor-pointer ${
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

              <button
                type="button"
                onClick={() => scrollToStage(2)}
                className={`flex items-center text-left transition-colors duration-300 py-1 cursor-pointer ${
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
          </div>

          {/* Bottom Bar: Metadata Line + Scroll Badge */}
          <div className="w-full flex items-center justify-between pt-6 border-t border-[rgba(235,240,238,0.08)] pointer-events-auto">
            <div className="flex flex-wrap items-center gap-3 sm:gap-5 text-[#858B8E] font-code text-[10px] sm:text-[11px] tracking-[0.22em] uppercase font-normal">
              <span>24 LAYERS</span>
              <span className="text-[#858B8E]/50 text-xs" aria-hidden="true">•</span>
              <span>TASK DAGs</span>
              <span className="text-[#858B8E]/50 text-xs" aria-hidden="true">•</span>
              <span>HYBRID MEMORY</span>
            </div>

            <div className="w-14 h-14 rounded-full border border-[rgba(235,240,238,0.25)] flex items-center justify-center">
              <span className="font-code text-[9px] tracking-[0.25em] text-[#9A9FA1] uppercase">
                {activeStage === 0 ? "01/03" : activeStage === 1 ? "02/03" : "03/03"}
              </span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
