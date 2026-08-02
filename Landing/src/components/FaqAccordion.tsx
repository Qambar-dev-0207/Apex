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
    tag: "REASONING GATE"
  },
  {
    q: "What is Code Compass AST and how does it achieve 18.4x token savings?",
    a: "Standard LLM wrappers dump entire source code files into context windows, burning tokens rapidly. Code Compass parses your project's Abstract Syntax Tree (AST) to index only target class definitions and function signatures, feeding precise symbols to the model.",
    tag: "TOKEN EFFICIENCY"
  },
  {
    q: "How does the hybrid ChromaDB + Redis memory cache work?",
    a: "APEX uses Redis for instant working memory (<10ms) during active execution sessions, paired with ChromaDB vector store for long-term semantic history (<38ms). Similar queries bypass repetitive LLM API costs entirely.",
    tag: "VECTOR MEMORY"
  },
  {
    q: "Can I enforce hard GPU/CPU temperature & USD spend limits?",
    a: "Yes. APEX features a real-time Hardware Bridge that monitors system RAM, CPU temperature, and active token spend. If a swarm exceeds configured budget thresholds (e.g. $0.05 per task), execution pauses safely.",
    tag: "HARDWARE VITALS"
  }
];

export default function FaqAccordion() {
  const [openIdx, setOpenIdx] = useState<number | null>(0);

  const toggle = (idx: number) => {
    setOpenIdx(openIdx === idx ? null : idx);
  };

  return (
    <div className="space-y-4 max-w-3xl mx-auto">
      {FAQS.map((faq, idx) => {
        const isOpen = openIdx === idx;
        return (
          <div
            key={idx}
            className="sensiq-card overflow-hidden bg-white transition-all border border-black/8"
          >
            <button
              onClick={() => toggle(idx)}
              className="w-full p-6 text-left flex items-center justify-between gap-4 font-display font-bold text-base text-[#111111] focus:outline-none"
            >
              <div className="flex items-center gap-3">
                <span className="font-mono text-[10px] font-bold text-[#84CC16] bg-[#84CC16]/10 px-2.5 py-1 rounded-md">
                  {faq.tag}
                </span>
                <span>{faq.q}</span>
              </div>
              <span className={`font-mono text-xl font-light text-[#666666] transition-transform duration-200 ${isOpen ? "rotate-45" : ""}`}>
                +
              </span>
            </button>

            <AnimatePresence>
              {isOpen && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <div className="px-6 pb-6 pt-2 font-sans text-sm text-[#666666] leading-relaxed border-t border-black/5">
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
