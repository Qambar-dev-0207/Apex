"use client";

import { motion } from "motion/react";

const BEFORE_ITEMS = [
  "Direct un-routed prompt submission to API",
  "High hallucination rate with no guardrails",
  "Full codebase dumped into context window",
  "Sequential single-thread tool execution",
  "Zero hardware vitals or spend monitoring",
];

const AFTER_ITEMS = [
  "Intent Normalizer & Sovereign Skill Router",
  "Socratic Gate with Steelman critiques",
  "Code Compass AST — 18.4× token savings",
  "Parallel TaskGroup multi-agent swarm",
  "Hardware Bridge + real-time spend control",
];

export default function ComparisonSection() {
  return (
    <section className="py-16 bg-[#F5F4F0]">
      <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="mb-16 text-center"
        >
          <div className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest mb-4">
            PARADIGM SHIFT
          </div>
          <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#0A0A0B] tracking-tight leading-tight">
            Generic wrapper<br />vs. sovereign OS
          </h2>
        </motion.div>

        {/* Comparison grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">

          {/* BEFORE */}
          <motion.div
            initial={{ opacity: 0, x: -24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="bg-white border border-black/8 rounded-2xl overflow-hidden"
          >
            {/* Header */}
            <div className="px-8 py-5 border-b border-black/6 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <h3 className="font-display text-base font-extrabold text-[#0A0A0B]">
                  Single-Prompt Wrapper
                </h3>
              </div>
              <span className="font-mono text-[10px] font-bold bg-red-50 text-red-500 border border-red-100 px-2.5 py-1 rounded-full uppercase tracking-wide">
                Before APEX
              </span>
            </div>

            {/* Items */}
            <div className="px-8 py-6 space-y-0">
              {BEFORE_ITEMS.map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -12 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: idx * 0.08 }}
                  className="flex items-start gap-4 py-4 border-b border-black/5 last:border-0"
                >
                  <span className="w-5 h-5 rounded-full border-2 border-red-200 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-red-400 text-xs font-bold leading-none">✕</span>
                  </span>
                  <span className="font-mono text-[13px] text-[#9CA3AF] line-through decoration-red-200">
                    {item}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* AFTER */}
          <motion.div
            initial={{ opacity: 0, x: 24 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-[#0A0A0B] rounded-2xl overflow-hidden shadow-[0_32px_80px_-16px_rgba(0,0,0,0.25)]"
          >
            {/* Header */}
            <div className="px-8 py-5 border-b border-white/8 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-[#65CC00] shadow-[0_0_8px_#65CC00]" />
                <h3 className="font-display text-base font-extrabold text-white">
                  APEX 24-Layer Sovereign OS
                </h3>
              </div>
              <span className="font-mono text-[10px] font-bold bg-[#65CC00]/12 text-[#65CC00] border border-[#65CC00]/20 px-2.5 py-1 rounded-full uppercase tracking-wide">
                After APEX
              </span>
            </div>

            {/* Items */}
            <div className="px-8 py-6 space-y-0">
              {AFTER_ITEMS.map((item, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: 12 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: idx * 0.08 }}
                  className="flex items-start gap-4 py-4 border-b border-white/6 last:border-0"
                >
                  <span className="w-5 h-5 rounded-full bg-[#65CC00]/15 border border-[#65CC00]/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-[#65CC00] text-xs font-bold leading-none">✓</span>
                  </span>
                  <span className="font-mono text-[13px] text-white/80 font-medium">
                    {item}
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
