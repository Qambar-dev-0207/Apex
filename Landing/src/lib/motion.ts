/**
 * APEX Sovereign OS — Centralized Motion System & Animation Tokens
 * 
 * Defines consistent timing, easing, depth, and interaction state primitives.
 * Creative principle: The environment establishes the world, motion explains
 * the system, and interaction gives the user control.
 */

import { Variants, Transition } from "motion/react";

/* ─── Timing Tokens (in seconds) ─── */
export const MOTION_TIMING = {
  micro: 0.18,       // Micro-interactions (140–220 ms)
  standard: 0.32,    // Standard UI transitions (220–400 ms)
  textReveal: 0.65,  // Text line reveals (450–750 ms)
  section: 0.75,     // Section transitions (500–900 ms)
  slow: 0.95,        // Atmospheric & monumental shifts
} as const;

/* ─── Easing Curves ─── */
export const MOTION_EASE = {
  // Restrained ease-out for entrances
  enter: [0.16, 1, 0.3, 1] as const,
  // Smooth ease-in-out for spatial transitions
  spatial: [0.65, 0, 0.35, 1] as const,
  // Standard responsive UI easing
  interface: [0.22, 0.61, 0.36, 1] as const,
  // Gentle exit curve
  exit: [0.4, 0, 1, 1] as const,
} as const;

/* ─── Damped Spring Presets ─── */
export const MOTION_SPRING = {
  interactive: {
    type: "spring" as const,
    stiffness: 300,
    damping: 25,
    mass: 0.8,
  },
  subtle: {
    type: "spring" as const,
    stiffness: 200,
    damping: 30,
  },
} as const;

/* ─── Reusable Transitions ─── */
export const transitions = {
  enter: (delay = 0): Transition => ({
    duration: MOTION_TIMING.section,
    delay,
    ease: MOTION_EASE.enter,
  }),
  text: (delay = 0): Transition => ({
    duration: MOTION_TIMING.textReveal,
    delay,
    ease: MOTION_EASE.enter,
  }),
  micro: (delay = 0): Transition => ({
    duration: MOTION_TIMING.micro,
    delay,
    ease: MOTION_EASE.interface,
  }),
  spatial: (delay = 0): Transition => ({
    duration: MOTION_TIMING.slow,
    delay,
    ease: MOTION_EASE.spatial,
  }),
};

/* ─── Reusable Framer Motion Variants ─── */

/** Section Entrance Variant */
export const sectionVariants: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: MOTION_TIMING.section,
      ease: MOTION_EASE.enter,
    },
  },
};

/** Masked Line Text Reveal Variant */
export const maskedLineVariants: Variants = {
  hidden: { y: "115%", opacity: 0 },
  visible: (custom = 0) => ({
    y: 0,
    opacity: 1,
    transition: {
      duration: MOTION_TIMING.textReveal,
      delay: custom,
      ease: MOTION_EASE.enter,
    },
  }),
};

/** Eyebrow Technical Line Draw Variant */
export const lineDrawVariants: Variants = {
  hidden: { width: 0 },
  visible: {
    width: 24,
    transition: {
      duration: 0.5,
      ease: MOTION_EASE.enter,
    },
  },
};

/** Architectural Plate Unfolding Variant */
export const plateVariants: Variants = {
  hidden: { opacity: 0, y: 16, scale: 0.98 },
  visible: (i = 0) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: MOTION_TIMING.standard + i * 0.08,
      delay: i * 0.08,
      ease: MOTION_EASE.enter,
    },
  }),
};

/** SVG Path Draw Variant */
export const pathDrawVariants: Variants = {
  hidden: { pathLength: 0, opacity: 0 },
  visible: (delay = 0) => ({
    pathLength: 1,
    opacity: 1,
    transition: {
      pathLength: { duration: 0.9, delay, ease: MOTION_EASE.enter },
      opacity: { duration: 0.3, delay },
    },
  }),
};

/** Node Pulsing / Revealing Variant */
export const nodeRevealVariants: Variants = {
  hidden: { scale: 0.8, opacity: 0 },
  visible: (delay = 0) => ({
    scale: 1,
    opacity: 1,
    transition: {
      duration: MOTION_TIMING.standard,
      delay,
      ease: MOTION_EASE.enter,
    },
  }),
};

/** Mascot Restrained Entrance Variant */
export const mascotEntranceVariants: Variants = {
  hidden: { opacity: 0, y: 10 },
  visible: (delay = 0) => ({
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.65,
      delay,
      ease: MOTION_EASE.enter,
    },
  }),
};

/** Static Reduced Motion Fallback Variants */
export const reducedMotionVariants: Variants = {
  hidden: { opacity: 1, y: 0, scale: 1 },
  visible: { opacity: 1, y: 0, scale: 1, transition: { duration: 0.01 } },
};
