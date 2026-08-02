"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "motion/react";

const STATS = [
  { value: 38, suffix: "ms", label: "Vector Cache Latency", description: "Sub-100ms semantic memory recall" },
  { value: 18.4, suffix: "×", label: "Token Efficiency", description: "Code Compass AST compression" },
  { value: 24, suffix: "", label: "Sovereign Layers", description: "Full architectural depth" },
  { value: 99.9, suffix: "%", label: "Socratic Accuracy", description: "Assumption validation rate" },
];

function AnimatedNumber({ target, suffix, duration = 1500 }: { target: number; suffix: string; duration?: number }) {
  const [display, setDisplay] = useState<number>(0);
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true });
  const started = useRef(false);

  useEffect(() => {
    if (!inView || started.current) return;
    started.current = true;
    const start = performance.now();
    const isDecimal = target % 1 !== 0;

    const tick = (now: number) => {
      const progress = Math.min((now - start) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = eased * target;
      setDisplay(isDecimal ? parseFloat(current.toFixed(1)) : Math.floor(current));
      if (progress < 1) requestAnimationFrame(tick);
      else setDisplay(target);
    };
    requestAnimationFrame(tick);
  }, [inView, target, duration]);

  return (
    <span ref={ref}>
      {target % 1 !== 0 ? display.toFixed(1) : display}
      {suffix}
    </span>
  );
}

export default function NumberGrid() {
  return (
    <section className="bg-[#F5F4F0] py-12 border-y border-black/6 relative z-10">
      <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
          {STATS.map((stat, idx) => (
            <div
              key={idx}
              className="bg-white border border-black/8 rounded-2xl p-6 sm:p-8 flex flex-col justify-between gap-4 shadow-sm hover:shadow-md hover:border-black/16 transition-all"
            >
              {/* Top Accent Pill */}
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] font-bold text-[#FF4500] uppercase tracking-wider bg-[#FF4500]/10 px-2.5 py-1 rounded-full">
                  METRIC 0{idx + 1}
                </span>
                <span className="w-2 h-2 rounded-full bg-[#65CC00]" />
              </div>

              {/* Giant number */}
              <div className="font-display text-4xl sm:text-5xl font-extrabold text-[#0A0A0B] tracking-tight leading-none my-1">
                <AnimatedNumber target={stat.value} suffix={stat.suffix} />
              </div>

              {/* Label & Description */}
              <div className="space-y-1">
                <div className="text-sm font-bold text-[#0A0A0B]">{stat.label}</div>
                <div className="text-xs text-[#6B7280] font-mono leading-relaxed">{stat.description}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
