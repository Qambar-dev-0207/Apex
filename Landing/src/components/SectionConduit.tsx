"use client";

import { motion, useReducedMotion } from "motion/react";
import { MOTION_EASE } from "../lib/motion";

interface SectionConduitProps {
  label?: string;
  height?: number; // Height in px, defaults to 64
  className?: string;
}

export default function SectionConduit({
  label,
  height = 56,
  className = "",
}: SectionConduitProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div
      className={`relative w-full flex flex-col items-center justify-center pointer-events-none select-none z-10 ${className}`}
      aria-hidden="true"
    >
      {/* Upper Hairline */}
      <div
        className="w-px bg-gradient-to-b from-transparent via-[rgba(255,255,255,0.15)] to-[rgba(255,255,255,0.25)] relative overflow-hidden"
        style={{ height: `${height / 2}px` }}
      >
        {!shouldReduceMotion && (
          <motion.div
            animate={{ y: ["-100%", "200%"] }}
            transition={{
              duration: 3.2,
              repeat: Infinity,
              ease: "linear",
            }}
            className="w-full h-8 bg-gradient-to-b from-transparent via-[#FF4A16] to-transparent shadow-[0_0_8px_#FF4A16]"
          />
        )}
      </div>

      {/* Central Architectural Node or Glyph */}
      <div className="flex items-center gap-2.5 my-1.5">
        <div className="w-1.5 h-1.5 rounded-full border border-[#FF4A16]/60 bg-[#FF4A16]/20 shadow-[0_0_8px_rgba(255,74,22,0.6)] flex items-center justify-center">
          <div className="w-0.5 h-0.5 rounded-full bg-[#FF4A16]" />
        </div>
        {label && (
          <motion.span
            initial={shouldReduceMotion ? { opacity: 1 } : { opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, ease: MOTION_EASE.enter }}
            className="font-code text-[9px] tracking-[0.28em] text-[#737575] uppercase"
          >
            {label}
          </motion.span>
        )}
      </div>

      {/* Lower Hairline */}
      <div
        className="w-px bg-gradient-to-b from-[rgba(255,255,255,0.25)] via-[rgba(255,255,255,0.15)] to-transparent relative overflow-hidden"
        style={{ height: `${height / 2}px` }}
      >
        {!shouldReduceMotion && (
          <motion.div
            animate={{ y: ["-100%", "200%"] }}
            transition={{
              duration: 3.2,
              repeat: Infinity,
              ease: "linear",
              delay: 1.6,
            }}
            className="w-full h-8 bg-gradient-to-b from-transparent via-[#FF4A16] to-transparent shadow-[0_0_8px_#FF4A16]"
          />
        )}
      </div>
    </div>
  );
}
