"use client";

import { motion } from "motion/react";

const FEATURES = [
  {
    number: "01",
    tag: "REAL-TIME INTELLIGENCE",
    title: "Vector memory that thinks at hardware speed",
    description: "ChromaDB semantic search and Redis working memory work together under 38ms, providing real-time cognitive recall without LLM roundtrips for repeated context.",
    metric: "< 38ms",
    metricLabel: "ChromaDB latency",
    accent: "#65CC00",
    code: [
      { color: "#6B7280", text: "# Semantic memory lookup" },
      { color: "#65CC00", text: "results = await memory.search(" },
      { color: "#9CA3AF", text: '    query="Google SWE resume",' },
      { color: "#9CA3AF", text: "    top_k=5, threshold=0.82" },
      { color: "#65CC00", text: ")" },
      { color: "#6B7280", text: "# ✓ 12 results in 31ms" },
    ],
  },
  {
    number: "02",
    tag: "PATTERN RECOGNITION",
    title: "18.4× context compression via AST indexing",
    description: "Code Compass parses Python and TypeScript Abstract Syntax Trees — extracting only class definitions and function signatures, feeding the exact symbols needed into LLM context.",
    metric: "18.4×",
    metricLabel: "Token efficiency",
    accent: "#FF4500",
    code: [
      { color: "#6B7280", text: "# AST symbol extraction" },
      { color: "#FF4500", text: "compass = CodeCompass('./src')" },
      { color: "#9CA3AF", text: "symbols = compass.extract()" },
      { color: "#6B7280", text: "# 412 symbols • 24,100 tokens" },
      { color: "#FF4500", text: "# vs. 450,000 full injection" },
      { color: "#65CC00", text: "# → 18.6× compression" },
    ],
  },
  {
    number: "03",
    tag: "AUTONOMOUS DECISIONS",
    title: "Socratic gates that refuse to hallucinate",
    description: "Every high-stakes action passes through an assumption probing gate. The Steelman Critique engine generates and defeats counter-arguments before dispatching parallel agent swarms.",
    metric: "VERIFIED",
    metricLabel: "After Socratic gate",
    accent: "#2563EB",
    code: [
      { color: "#6B7280", text: "# Socratic verification" },
      { color: "#2563EB", text: "gate = SocraticGate()" },
      { color: "#9CA3AF", text: "result = gate.verify({" },
      { color: "#9CA3AF", text: '    "action": "rewrite router.py"' },
      { color: "#9CA3AF", text: "})" },
      { color: "#65CC00", text: "# ✓ Applied rollback strategy" },
    ],
  },
];

export default function FeatureRows() {
  return (
    <section className="py-20 bg-white">
      <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
          className="mb-12 max-w-xl"
        >
          <div className="font-mono text-xs font-semibold text-[#FF4500] uppercase tracking-widest mb-4">
            CORE CAPABILITIES
          </div>
          <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#0A0A0B] tracking-tight leading-[1.1]">
            Built different,<br />by design
          </h2>
        </motion.div>

        {/* Feature Rows */}
        <div className="space-y-12">
          {FEATURES.map((feature, idx) => (
            <motion.div
              key={feature.number}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-60px" }}
              transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
              className={`grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-20 items-center ${
                idx % 2 === 1 ? "lg:grid-flow-dense" : ""
              }`}
            >
              {/* Text Column */}
              <div className={`space-y-6 ${idx % 2 === 1 ? "lg:col-start-2" : ""}`}>
                {/* Number + Tag */}
                <div className="flex items-center gap-4">
                  <span className="font-mono text-6xl font-extrabold text-black/6 select-none leading-none">
                    {feature.number}
                  </span>
                  <span
                    className="font-mono text-[11px] font-bold uppercase tracking-widest px-3 py-1 rounded-full"
                    style={{
                      color: feature.accent,
                      background: `${feature.accent}14`,
                    }}
                  >
                    {feature.tag}
                  </span>
                </div>

                {/* Title */}
                <h3 className="font-display text-3xl sm:text-4xl font-extrabold text-[#0A0A0B] leading-tight tracking-tight">
                  {feature.title}
                </h3>

                {/* Description */}
                <p className="text-[#6B7280] text-base leading-relaxed max-w-md">
                  {feature.description}
                </p>

                {/* Metric callout */}
                <div className="flex items-center gap-4 pt-2">
                  <div
                    className="font-mono text-3xl font-extrabold tracking-tight"
                    style={{ color: feature.accent }}
                  >
                    {feature.metric}
                  </div>
                  <div className="text-xs font-mono text-[#6B7280] uppercase tracking-wider">
                    {feature.metricLabel}
                  </div>
                </div>
              </div>

              {/* Code Terminal Visual */}
              <div className={idx % 2 === 1 ? "lg:col-start-1 lg:row-start-1" : ""}>
                <div className="bg-[#0A0A0B] rounded-2xl overflow-hidden shadow-[0_32px_80px_-16px_rgba(0,0,0,0.28)]">
                  {/* Terminal chrome */}
                  <div className="flex items-center gap-2 px-5 py-4 border-b border-white/6">
                    <span className="w-3 h-3 rounded-full bg-[#FF5F57]" />
                    <span className="w-3 h-3 rounded-full bg-[#FEBC2E]" />
                    <span className="w-3 h-3 rounded-full bg-[#28C840]" />
                    <span className="ml-3 font-mono text-xs text-white/30">apex-core.py</span>
                  </div>

                  {/* Code lines */}
                  <div className="p-6 font-mono text-sm space-y-1.5">
                    {feature.code.map((line, lineIdx) => (
                      <motion.div
                        key={lineIdx}
                        initial={{ opacity: 0, x: -8 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ duration: 0.3, delay: lineIdx * 0.08 }}
                        style={{ color: line.color }}
                      >
                        {line.text}
                        {lineIdx === feature.code.length - 1 && (
                          <span className="cursor-blink ml-0.5 inline-block w-2 h-4 bg-white/40 align-middle" />
                        )}
                      </motion.div>
                    ))}
                  </div>

                  {/* Bottom bar */}
                  <div className="px-6 py-3 border-t border-white/6 flex items-center justify-between">
                    <span className="font-mono text-[10px] text-white/25 uppercase tracking-wider">
                      APEX ENGINE
                    </span>
                    <span
                      className="font-mono text-[10px] font-bold uppercase tracking-wider flex items-center gap-1.5"
                      style={{ color: feature.accent }}
                    >
                      <span className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ backgroundColor: feature.accent }} />
                      ACTIVE
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
