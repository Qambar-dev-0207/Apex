"use client";

import { motion } from "motion/react";
import { useEffect, useRef, useState } from "react";

function TypedCode({ lines }: { lines: { text: string; color: string }[] }) {
  return (
    <div className="bg-[#0A0A0B] rounded-xl p-5 font-mono text-xs space-y-1.5 overflow-hidden">
      {lines.map((line, idx) => (
        <motion.div
          key={idx}
          initial={{ opacity: 0, x: -6 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.25, delay: idx * 0.1 }}
          style={{ color: line.color }}
        >
          {line.text}
        </motion.div>
      ))}
    </div>
  );
}

function MiniCounter({ value, suffix }: { value: number; suffix: string }) {
  const [display, setDisplay] = useState<string>("0");
  const ref = useRef<HTMLSpanElement>(null);
  const isDecimal = value % 1 !== 0;

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          const start = performance.now();
          const duration = 1500;
          const tick = (now: number) => {
            const progress = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            const current = eased * value;
            setDisplay(isDecimal ? current.toFixed(1) : Math.floor(current).toString());
            if (progress < 1) requestAnimationFrame(tick);
            else setDisplay(isDecimal ? value.toFixed(1) : value.toString());
          };
          requestAnimationFrame(tick);
          observer.disconnect();
        }
      },
      { threshold: 0.5 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [value, isDecimal]);

  return (
    <span ref={ref}>
      {display}{suffix}
    </span>
  );
}

export default function BentoGrid() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-5 sm:gap-6">

      {/* Card 1: Socratic Gate — span 8, tall */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.05 }}
        className="md:col-span-8 apex-card p-8 sm:p-10 flex flex-col justify-between gap-8 min-h-[360px]"
      >
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <span className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest bg-[#FF4500]/8 px-3 py-1.5 rounded-full">
              TIER 1 · INTELLIGENCE
            </span>
            <span className="font-mono text-[10px] text-[#9CA3AF] font-medium">01 / SOCRATIC</span>
          </div>

          <div>
            <h3 className="font-display text-2xl sm:text-3xl font-extrabold text-[#0A0A0B] leading-tight">
              Intent Normalizer &amp; Socratic Gate
            </h3>
            <p className="text-[#6B7280] text-sm leading-relaxed mt-3 max-w-lg">
              Classifies objectives using Gemini 2.0 Flash, activates sovereign skills automatically, and forces Steelman critiques before execution.
            </p>
          </div>
        </div>

        <TypedCode lines={[
          { text: "$ apex socratic-gate --verify-thesis", color: "#FF4500" },
          { text: '🔍 Probing: "Execute direct rewrite without tests"', color: "#9CA3AF" },
          { text: "⚠️  Steelman: Risk of silent side-effects in router.py", color: "#F59E0B" },
          { text: "🟢 Guardrails applied. Plan verified & approved.", color: "#65CC00" },
        ]} />
      </motion.div>

      {/* Card 2: Code Compass stat — span 4 */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.15 }}
        className="md:col-span-4 apex-card p-8 sm:p-10 flex flex-col justify-between min-h-[360px]"
      >
        <div className="space-y-3">
          <span className="font-mono text-[11px] font-bold text-[#2563EB] uppercase tracking-widest bg-[#2563EB]/8 px-3 py-1.5 rounded-full inline-block">
            TIER 2 · MEMORY
          </span>
          <h3 className="font-display text-xl font-extrabold text-[#0A0A0B]">
            Code Compass AST
          </h3>
          <p className="text-[#6B7280] text-sm leading-relaxed">
            Parses Python &amp; TypeScript symbols, giving you massive token savings over full file injection.
          </p>
        </div>

        <div>
          <div className="font-display text-6xl font-extrabold text-[#2563EB] tracking-tight leading-none mb-2">
            18.4×
          </div>
          <div className="flex items-center gap-2">
            <div className="flex-1 h-1.5 bg-[#F5F4F0] rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width: "88%" }}
                viewport={{ once: true }}
                transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
                className="h-full bg-[#2563EB] rounded-full"
              />
            </div>
            <span className="font-mono text-[10px] text-[#6B7280]">88%</span>
          </div>
          <div className="font-mono text-[10px] text-[#9CA3AF] uppercase tracking-wider mt-1">Average token efficiency</div>
        </div>
      </motion.div>

      {/* Card 3: ChromaDB Memory — span 4 */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.25 }}
        className="md:col-span-4 apex-card p-8 sm:p-10 flex flex-col justify-between"
      >
        <div className="space-y-3">
          <span className="font-mono text-[11px] font-bold text-[#65CC00] uppercase tracking-widest bg-[#65CC00]/8 px-3 py-1.5 rounded-full inline-block">
            TIER 2 · CONTEXT CACHE
          </span>
          <h3 className="font-display text-xl font-extrabold text-[#0A0A0B]">
            ChromaDB + Redis Memory
          </h3>
          <p className="text-[#6B7280] text-sm leading-relaxed">
            Sub-100ms vector proximity lookups bypass repetitive LLM calls with instant recall.
          </p>
        </div>

        <div className="space-y-4">
          {/* Live status bar */}
          {[
            { label: "ChromaDB", val: 92, color: "#65CC00" },
            { label: "Redis Cache", val: 78, color: "#2563EB" },
          ].map((item) => (
            <div key={item.label}>
              <div className="flex justify-between font-mono text-[10px] text-[#6B7280] mb-1">
                <span>{item.label}</span>
                <span className="font-semibold" style={{ color: item.color }}>{item.val}%</span>
              </div>
              <div className="h-1.5 bg-[#F5F4F0] rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  whileInView={{ width: `${item.val}%` }}
                  viewport={{ once: true }}
                  transition={{ duration: 1, ease: "easeOut", delay: 0.4 }}
                  className="h-full rounded-full"
                  style={{ backgroundColor: item.color }}
                />
              </div>
            </div>
          ))}

          <div className="flex items-center gap-2 pt-1">
            <span className="w-2 h-2 rounded-full bg-[#65CC00] animate-pulse shadow-[0_0_6px_#65CC00]" />
            <span className="font-mono text-[10px] text-[#65CC00] font-semibold">Semantic Cache Active · &lt;38ms</span>
          </div>
        </div>
      </motion.div>

      {/* Card 4: Parallel Swarm — span 8 */}
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, delay: 0.35 }}
        className="md:col-span-8 apex-card p-8 sm:p-10 flex flex-col justify-between gap-8"
      >
        <div className="space-y-4">
          <div className="flex items-start justify-between gap-4">
            <span className="font-mono text-[11px] font-bold text-[#7C3AED] uppercase tracking-widest bg-[#7C3AED]/8 px-3 py-1.5 rounded-full">
              TIER 3 · EXECUTION &amp; SWARM
            </span>
            <span className="font-mono text-[10px] text-[#9CA3AF] font-medium">04 / PARALLEL</span>
          </div>

          <div>
            <h3 className="font-display text-2xl sm:text-3xl font-extrabold text-[#0A0A0B] leading-tight">
              Parallel TaskGroup Dispatcher &amp; Sandbox
            </h3>
            <p className="text-[#6B7280] text-sm leading-relaxed mt-3 max-w-xl">
              Orchestrates concurrent multi-agent research swarms across isolated sandboxes with atomic error handling.
            </p>
          </div>
        </div>

        {/* Swarm visualizer */}
        <div className="grid grid-cols-3 gap-4 font-mono text-xs">
          {[
            { label: "TASKGROUP SWARM", value: "Parallel", color: "#7C3AED", sub: "3 agents active" },
            { label: "SANDBOX ENGINE", value: "Isolated", color: "#65CC00", sub: "Docker containers" },
            { label: "HARDWARE BRIDGE", value: "32.4 GB", color: "#FF4500", sub: "System RAM available" },
          ].map((item) => (
            <div key={item.label} className="bg-[#F5F4F0] border border-black/6 p-4 rounded-xl">
              <div className="text-[10px] text-[#9CA3AF] uppercase tracking-wider mb-2">{item.label}</div>
              <div className="font-display text-base font-extrabold" style={{ color: item.color }}>
                {item.value}
              </div>
              <div className="text-[10px] text-[#6B7280] mt-1">{item.sub}</div>
            </div>
          ))}
        </div>
      </motion.div>

    </div>
  );
}
