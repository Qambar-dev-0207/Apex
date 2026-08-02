"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

const TESTIMONIALS = [
  {
    id: "martha",
    name: "Martha Hooper",
    role: "Lead AI Architect, Quantum Labs",
    quote: "APEX completely eliminated hallucinated code edits. The Socratic Gate intercepts bad thesis proposals before they reach our codebase.",
    metricTitle: "SOCRATIC REASONING",
    metricVal: "100%",
    metricSub: "Zero hallucinated edits in production",
  },
  {
    id: "anthony",
    name: "Anthony Edwards",
    role: "Principal Systems Engineer",
    quote: "Code Compass token savings are insane. Our context costs dropped by 18.4x while maintaining full symbol AST accuracy across 90+ modules.",
    metricTitle: "TOKEN EFFICIENCY",
    metricVal: "18.4x",
    metricSub: "Context compressed from 450k to 24k tokens",
  },
  {
    id: "sophia",
    name: "Sophia Raynolds",
    role: "Autonomous Swarm Researcher",
    quote: "Parallel TaskGroup swarms execute complex multi-agent research in seconds. Sub-38ms ChromaDB cache hits save us thousands in API spend.",
    metricTitle: "CHROMA LATENCY",
    metricVal: "38 ms",
    metricSub: "Sub-100ms vector search hit rate",
  },
];

export default function ScrollPinnedQuotes() {
  const [activeQuote, setActiveQuote] = useState<number>(0);
  const current = TESTIMONIALS[activeQuote];

  return (
    <section className="py-12 relative z-10">
      <div className="max-w-[1280px] mx-auto px-4 sm:px-6 md:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">

          {/* Left Column: Title & Controls */}
          <div className="lg:col-span-5 space-y-6">
            <div className="font-mono text-xs text-[#84CC16] font-bold uppercase tracking-widest bg-[#84CC16]/10 px-3.5 py-1.5 rounded-full inline-block">
              DEVELOPER STORIES
            </div>

            <h2 className="font-display text-3xl sm:text-5xl font-extrabold text-[#111111] leading-tight tracking-tight">
              What APEX Sovereign Developers Say
            </h2>

            <p className="font-sans text-[#666666] text-sm sm:text-base leading-relaxed">
              Real feedback from engineers building autonomous multi-agent systems with APEX 24-Layer OS.
            </p>

            {/* Testimonial Nav Stepper */}
            <div className="flex items-center gap-3 pt-2">
              {TESTIMONIALS.map((t, idx) => (
                <button
                  key={t.id}
                  onClick={() => setActiveQuote(idx)}
                  className={`px-4 py-2 rounded-xl font-mono text-xs font-bold transition-all ${
                    activeQuote === idx
                      ? "bg-[#111111] text-white shadow-md"
                      : "bg-white text-[#666666] border border-black/8 hover:text-[#111111]"
                  }`}
                >
                  0{idx + 1}. {t.name.split(" ")[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Right Column: Quote & Metric Card */}
          <div className="lg:col-span-7 flex flex-col justify-center">
            <AnimatePresence mode="wait">
              <motion.div
                key={current.id}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                transition={{ duration: 0.4 }}
                className="sensiq-card p-8 sm:p-10 space-y-6 bg-white shadow-xl border border-black/8"
              >
                <p className="font-display text-xl sm:text-2xl font-semibold text-[#111111] leading-relaxed">
                  "{current.quote}"
                </p>

                <div className="flex items-center justify-between border-t border-black/8 pt-6">
                  <div>
                    <div className="font-display font-bold text-base text-[#111111]">
                      {current.name}
                    </div>
                    <div className="font-mono text-xs text-[#666666] mt-0.5">
                      {current.role}
                    </div>
                  </div>

                  <div className="bg-[#EBEAE5] px-4 py-2 rounded-xl text-right font-mono">
                    <div className="text-[#84CC16] font-extrabold text-lg leading-none">
                      {current.metricVal}
                    </div>
                    <div className="text-[10px] text-[#666666] font-semibold uppercase tracking-wider mt-1">
                      {current.metricTitle}
                    </div>
                  </div>
                </div>
              </motion.div>
            </AnimatePresence>
          </div>

        </div>
      </div>
    </section>
  );
}
