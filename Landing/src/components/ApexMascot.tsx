"use client";

import Image from "next/image";
import { motion, useReducedMotion } from "motion/react";
import React from "react";

export const MASCOT_METADATA = {
  hero: { src: "/mascot/apex-mascot-hero.png", width: 239, height: 216, defaultAlt: "APEX companion overlooking the gateway" },
  thinking: { src: "/mascot/apex-mascot-thinking.png", width: 190, height: 153, defaultAlt: "APEX companion pondering system architecture" },
  analyzing: { src: "/mascot/apex-mascot-analyzing.png", width: 194, height: 142, defaultAlt: "APEX companion analyzing runtime telemetry" },
  coding: { src: "/mascot/apex-mascot-coding.png", width: 177, height: 143, defaultAlt: "APEX companion synthesizing code and task DAGs" },
  building: { src: "/mascot/apex-mascot-building.png", width: 185, height: 142, defaultAlt: "APEX companion assembling execution modules" },
  connected: { src: "/mascot/apex-mascot-connected.png", width: 144, height: 142, defaultAlt: "APEX companion linked across multi-model providers" },
  learning: { src: "/mascot/apex-mascot-learning.png", width: 145, height: 145, defaultAlt: "APEX companion indexing hybrid memory context" },
  focused: { src: "/mascot/apex-mascot-focused.png", width: 124, height: 116, defaultAlt: "APEX companion monitoring execution loop" },
  focus: { src: "/mascot/apex-mascot-focus.png", width: 147, height: 150, defaultAlt: "APEX companion focusing on agent harness" },
  determined: { src: "/mascot/apex-mascot-determined.png", width: 128, height: 116, defaultAlt: "APEX companion recovering state deterministically" },
  curious: { src: "/mascot/apex-mascot-curious.png", width: 127, height: 116, defaultAlt: "APEX companion exploring knowledge graph" },
  excited: { src: "/mascot/apex-mascot-excited.png", width: 124, height: 116, defaultAlt: "APEX companion celebrating verified output" },
  happy: { src: "/mascot/apex-mascot-happy.png", width: 128, height: 115, defaultAlt: "APEX companion operating peacefully" },
  proud: { src: "/mascot/apex-mascot-proud.png", width: 118, height: 116, defaultAlt: "APEX companion standing by sovereign system" },
  deploying: { src: "/mascot/apex-mascot-deploying.png", width: 190, height: 142, defaultAlt: "APEX companion deploying autonomous workflows" },
} as const;

export type MascotVariant = keyof typeof MASCOT_METADATA;

export interface ApexMascotProps {
  variant: MascotVariant;
  className?: string;
  width?: number;
  height?: number;
  alt?: string;
  animateIdle?: boolean;
  entranceDelay?: number;
  priority?: boolean;
  style?: React.CSSProperties;
}

export default function ApexMascot({
  variant,
  className = "",
  width,
  height,
  alt,
  animateIdle = false,
  entranceDelay = 0,
  priority = false,
  style = {},
}: ApexMascotProps) {
  const meta = MASCOT_METADATA[variant];
  const shouldReduceMotion = useReducedMotion();

  // Compute dimensions preserving exact aspect ratio
  const intrinsicRatio = meta.width / meta.height;
  let finalWidth: number = meta.width;
  let finalHeight: number = meta.height;

  if (height && !width) {
    finalHeight = height;
    finalWidth = Math.round(height * intrinsicRatio);
  } else if (width && !height) {
    finalWidth = width;
    finalHeight = Math.round(width / intrinsicRatio);
  } else if (width && height) {
    finalWidth = width;
    finalHeight = height;
  }

  const isDecorative = !alt;
  const computedAlt = isDecorative ? "" : alt;

  return (
    <motion.div
      initial={
        shouldReduceMotion
          ? { opacity: 1, y: 0 }
          : { opacity: 0, y: 8 }
      }
      animate={
        shouldReduceMotion
          ? { opacity: 1, y: 0 }
          : animateIdle
          ? { opacity: 1, y: [0, -3.5, 0] }
          : { opacity: 1, y: 0 }
      }
      transition={
        shouldReduceMotion
          ? { duration: 0.2 }
          : {
              opacity: { duration: 0.6, delay: entranceDelay, ease: [0.16, 1, 0.3, 1] },
              y: animateIdle
                ? {
                    duration: 5.2,
                    repeat: Infinity,
                    repeatType: "reverse",
                    ease: "easeInOut",
                    delay: entranceDelay + 0.6,
                  }
                : { duration: 0.6, delay: entranceDelay, ease: [0.16, 1, 0.3, 1] },
            }
      }
      className={`inline-block select-none pointer-events-none ${className}`}
      style={{
        ...style,
        willChange: animateIdle && !shouldReduceMotion ? "transform" : "auto",
      }}
      aria-hidden={isDecorative ? "true" : undefined}
    >
      <Image
        src={meta.src}
        alt={computedAlt}
        width={finalWidth}
        height={finalHeight}
        priority={priority}
        className="block max-w-full h-auto object-contain"
        style={{
          imageRendering: "pixelated",
        }}
      />
    </motion.div>
  );
}
