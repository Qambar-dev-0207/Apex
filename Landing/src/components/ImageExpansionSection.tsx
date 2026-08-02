"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "motion/react";

export default function ImageExpansionSection() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });

  const scale = useTransform(scrollYProgress, [0, 0.5], [0.88, 1]);
  const borderRadius = useTransform(scrollYProgress, [0, 0.5], [32, 0]);

  return (
    <div ref={containerRef} className="py-24 relative z-10 overflow-hidden">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 md:px-8 text-center mb-12">
        <h2 className="font-display text-3xl sm:text-5xl font-extrabold text-[#111111] tracking-tight mb-4">
          Built for Peak Accuracy, Trusted by AI Architects
        </h2>
        <p className="font-sans text-[#666666] text-base max-w-xl mx-auto">
          Hardware-native execution, Socratic friction gates, and sub-38ms vector cache performance engineered for sovereign autonomy.
        </p>
      </div>

      <motion.div
        style={{ scale, borderRadius }}
        className="max-w-[1280px] mx-auto bg-[#111111] text-white p-10 sm:p-20 shadow-2xl relative overflow-hidden"
      >
        <div className="relative z-10 max-w-2xl space-y-6">
          <div className="font-mono text-xs text-[#84CC16] font-bold uppercase tracking-widest">
            ENGINEERED FOR SUPREMACY
          </div>
          <h3 className="font-display text-3xl sm:text-4xl font-extrabold leading-tight">
            The 24-Layer Agentic AI Operating System
          </h3>
          <p className="text-gray-400 text-sm sm:text-base leading-relaxed">
            Eliminate repetitive LLM costs, reduce hallucinated state updates, and execute multi-agent research swarms in isolated sandboxes.
          </p>
          <div className="pt-4">
            <a
              href="#orchestrator"
              className="px-6 py-3 rounded-full bg-white text-[#111111] font-mono text-xs font-bold uppercase tracking-wider hover:bg-gray-100 transition-all inline-block shadow-md"
            >
              EXPLORE ARCHITECTURE ›
            </a>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
