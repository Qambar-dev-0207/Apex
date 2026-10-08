"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

interface FaqItem {
  q: string;
  a: string;
  tag: string;
}

const FAQS: FaqItem[] = [
  {
    q: "How does the Socratic Friction Gate eliminate AI hallucinations?",
    a: "Before dispatching code modifications or state updates, APEX routes your query through a Socratic reasoning layer that probes hidden assumptions and executes Steelman critiques. If a proposed plan lacks rollback assertions, guardrails automatically modify the strategy.",
    tag: "REASONING GATE",
  },
  {
    q: "What is Code Compass AST and how does it achieve 18.4x token savings?",
    a: "Standard LLM wrappers dump entire source code files into context windows, burning tokens rapidly. Code Compass parses your project's Abstract Syntax Tree (AST) to index only target class definitions and function signatures, feeding precise symbols to the model.",
    tag: "TOKEN EFFICIENCY",
  },
  {
    q: "How does the hybrid ChromaDB + Redis memory cache work?",
    a: "APEX uses Redis for instant working memory (<10ms) during active execution sessions, paired with ChromaDB vector store for long-term semantic history (<38ms). Similar queries bypass repetitive LLM API costs entirely.",
    tag: "VECTOR MEMORY",
  },
  {
    q: "Can I enforce hard GPU/CPU temperature & USD spend limits?",
    a: "Yes. APEX features a real-time Hardware Bridge that monitors system RAM, CPU temperature, and active token spend. If a swarm exceeds configured budget thresholds (e.g. $0.05 per task), execution pauses safely.",
    tag: "HARDWARE VITALS",
  },
];

export default function FaqAccordion() {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  const toggle = (idx: number) => {
    setOpenIdx(openIdx === idx ? null : idx);
  };

  return (
    <div className="space-y-4 max-w-[1000px] mx-auto">
      {FAQS.map((faq, idx) => {
        const isOpen = openIdx === idx;
        return (
          <div
            key={idx}
            className="rounded-2xl bg-white border border-[#D9D9D9] hover:border-[#000000] transition-colors duration-300 overflow-hidden shadow-xs"
          >
            <button
              onClick={() => toggle(idx)}
              className="w-full p-6 sm:p-7 text-left flex items-center justify-between gap-4 font-display font-bold text-lg text-[#000000] focus:outline-none cursor-pointer group"
            >
              <div className="flex flex-wrap items-center gap-3">
                <span className="font-mono text-[10px] font-bold text-[#FF3700] bg-[#FF3700]/10 px-3 py-1 rounded-full uppercase tracking-wider">
                  {faq.tag}
                </span>
                <span className="group-hover:text-[#FF3700] transition-colors">
                  {faq.q}
                </span>
              </div>
              <span
                className={`shrink-0 w-8 h-8 rounded-full border border-[#D9D9D9] flex items-center justify-center font-mono text-base transition-all duration-300 ${
                  isOpen
                    ? "bg-[#000000] text-white border-[#000000] rotate-45"
                    : "text-[#545454] bg-[#FAFAF9]"
                }`}
              >
                +
              </span>
            </button>

            <AnimatePresence>
              {isOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
                >
                  <div className="px-6 sm:px-7 pb-6 pt-1 text-sm sm:text-base text-[#545454] leading-relaxed border-t border-[#D9D9D9]/60">
                    {faq.a}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        );
      })}
    </div>
  );
}
