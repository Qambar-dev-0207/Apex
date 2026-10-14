"use client";

import React, { useRef } from "react";
import { useScroll, useTransform, motion, MotionValue, useReducedMotion } from "motion/react";

interface WordToken {
  text: string;
  isItalic?: boolean;
}

interface ScrollWordRevealProps {
  tokens: WordToken[];
  className?: string;
}

function WordItem({
  token,
  progress,
  start,
  end,
  shouldReduceMotion,
}: {
  token: WordToken;
  progress: MotionValue<number>;
  start: number;
  end: number;
  shouldReduceMotion: boolean | null;
}) {
  const opacity = useTransform(progress, [start, end], [0.22, 1]);

  if (shouldReduceMotion) {
    return (
      <span
        className={`inline-block ${
          token.isItalic ? "font-editorial italic text-[#F5F3EF] text-[1.14em]" : ""
        }`}
        style={{ opacity: 1 }}
      >
        {token.text}
      </span>
    );
  }

  return (
    <motion.span
      style={{ opacity }}
      className={`inline-block transition-colors duration-150 ${
        token.isItalic ? "font-editorial italic text-[#F5F3EF] text-[1.14em]" : ""
      }`}
    >
      {token.text}
    </motion.span>
  );
}

export default function ScrollWordReveal({
  tokens,
  className = "",
}: ScrollWordRevealProps) {
  const containerRef = useRef<HTMLParagraphElement>(null);
  const shouldReduceMotion = useReducedMotion();

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start 0.85", "end 0.30"],
  });

  const totalWords = tokens.length;

  return (
    <p
      ref={containerRef}
      className={`select-text ${className}`}
      aria-label={tokens.map((t) => t.text).join(" ")}
    >
      {tokens.map((token, i) => {
        // Distribute word intervals smoothly across the reading scroll range
        const step = 0.85 / totalWords;
        const start = i * step;
        const end = Math.min(start + step * 1.5, 1);

        return (
          <React.Fragment key={i}>
            <WordItem
              token={token}
              progress={scrollYProgress}
              start={start}
              end={end}
              shouldReduceMotion={shouldReduceMotion}
            />
            {i < totalWords - 1 && " "}
          </React.Fragment>
        );
      })}
    </p>
  );
}
