"use client";

import { motion, useReducedMotion } from "motion/react";
import React from "react";

interface MaskedLineRevealProps {
  lines: Array<{
    text: string;
    isItalic?: boolean;
    className?: string;
  }>;
  className?: string;
  lineClassName?: string;
  staggerDelay?: number;
  baseDelay?: number;
  duration?: number;
  as?: "h1" | "h2" | "h3" | "h4" | "div";
}

export default function MaskedLineReveal({
  lines,
  className = "",
  lineClassName = "",
  staggerDelay = 0.1,
  baseDelay = 0,
  duration = 0.85,
  as: Component = "div",
}: MaskedLineRevealProps) {
  const shouldReduceMotion = useReducedMotion();

  return (
    <Component className={`flex flex-col ${className}`}>
      {lines.map((line, idx) => (
        <span
          key={idx}
          className="overflow-mask block relative leading-[1.08]"
          style={{ willChange: "transform, opacity, filter" }}
        >
          <motion.span
            initial={
              shouldReduceMotion
                ? { opacity: 1, y: 0, filter: "none" }
                : { opacity: 0, y: "112%", filter: "blur(3px)" }
            }
            animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
            transition={{
              duration: line.isItalic ? duration * 1.05 : duration,
              delay: baseDelay + idx * staggerDelay,
              ease: [0.16, 1, 0.3, 1],
            }}
            className={`block ${
              line.isItalic ? "font-editorial italic font-normal" : ""
            } ${line.className || ""} ${lineClassName}`}
          >
            {line.text}
          </motion.span>
        </span>
      ))}
    </Component>
  );
}
