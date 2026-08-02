"use client";

import { motion } from "motion/react";
import OrchestratorVisualizer from "./OrchestratorVisualizer";

export default function DarkShowcase() {
  return (
    <section className="bg-[#0A0A0B] py-16 relative overflow-hidden">
      {/* Ambient glow */}
      <div
        className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] opacity-20 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse at 50% 0%, rgba(255,69,0,0.6) 0%, rgba(37,99,235,0.3) 50%, transparent 70%)",
          filter: "blur(60px)",
        }}
      />

      <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8 relative z-10">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">

          {/* Left: Quote / Copy */}
          <motion.div
            initial={{ opacity: 0, x: -30 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-8"
          >
            <div className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest">
              LIVE DAG ORCHESTRATOR
            </div>

            <blockquote className="font-display text-3xl sm:text-4xl lg:text-5xl font-extrabold text-white leading-[1.1] tracking-tight">
              The OS that{" "}
              <span className="text-[#FF4500]">refuses</span>{" "}
              to hallucinate.
            </blockquote>

            <p className="text-white/50 text-base leading-relaxed max-w-md">
              Watch the live DAG orchestration graph as APEX routes intent, probes assumptions through the Socratic Gate, and dispatches verified agent swarms — all in real time.
            </p>

            {/* Stats row */}
            <div className="grid grid-cols-3 gap-6 pt-4">
              {[
                { value: "24", label: "Layers" },
                { value: "38ms", label: "Latency" },
                { value: "0", label: "Hallucinations" },
              ].map((stat) => (
                <div key={stat.label} className="space-y-1">
                  <div className="font-display text-2xl font-extrabold text-white">{stat.value}</div>
                  <div className="font-mono text-[10px] text-white/35 uppercase tracking-wider">{stat.label}</div>
                </div>
              ))}
            </div>

            <a
              href="#orchestrator"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-white/8 border border-white/12 text-white text-sm font-semibold hover:bg-white/14 hover:border-white/20 transition-all duration-200"
            >
              Explore orchestrator
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </a>
          </motion.div>

          {/* Right: Live DAG visualizer on dark */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.15, ease: [0.16, 1, 0.3, 1] }}
            className="relative"
          >
            {/* Card wrapper */}
            <div className="bg-white/4 border border-white/8 rounded-2xl p-1 shadow-[0_0_80px_rgba(255,69,0,0.08)]">
              <div className="bg-[#0F0F12] rounded-xl overflow-hidden">
                {/* Terminal chrome */}
                <div className="flex items-center justify-between px-5 py-3.5 border-b border-white/6">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#FF5F57]" />
                    <span className="w-2.5 h-2.5 rounded-full bg-[#FEBC2E]" />
                    <span className="w-2.5 h-2.5 rounded-full bg-[#28C840]" />
                  </div>
                  <div className="font-mono text-[10px] text-white/25 uppercase tracking-wider">LIVE DAG · RESUME TAILORING</div>
                  <div className="flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#65CC00] animate-pulse" />
                    <span className="font-mono text-[10px] text-[#65CC00] font-semibold">LIVE</span>
                  </div>
                </div>

                {/* Visualizer */}
                <div className="h-[380px]">
                  <OrchestratorVisualizer activePreset="Resume Tailoring DAG" isSimulating={true} />
                </div>

                {/* Metric overlays */}
                <div className="px-5 py-3.5 border-t border-white/6 flex items-center justify-between font-mono text-xs">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1.5">
                      <span className="text-white/40">AVG LATENCY</span>
                      <span className="text-[#65CC00] font-bold">38ms</span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className="text-white/40">NODES ACTIVE</span>
                      <span className="text-[#2563EB] font-bold">11</span>
                    </div>
                  </div>
                  <span className="text-[#FF4500] font-semibold">PASSED SOCRATIC GATE</span>
                </div>
              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
