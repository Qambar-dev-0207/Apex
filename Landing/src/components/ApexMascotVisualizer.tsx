"use client";

import { useState, useEffect } from "react";
import Image from "next/image";

interface MascotStateInfo {
  id: string;
  label: string;
  action: string;
  color: string;
  icon: string;
}

const MASCOT_STATES: MascotStateInfo[] = [
  { id: "focus", label: "FOCUS MODE", action: "Scanning system vitals", color: "from-cyan-500 to-blue-600", icon: "👁️" },
  { id: "coding", label: "CODING", action: "Writing clean TypeScript & Python", color: "from-emerald-500 to-teal-600", icon: "💻" },
  { id: "thinking", label: "THINKING", action: "Evaluating multi-model graph reasoning", color: "from-purple-500 to-indigo-600", icon: "💭" },
  { id: "learning", label: "LEARNING", action: "Indexing research papers & AST maps", color: "from-amber-500 to-yellow-600", icon: "📖" },
  { id: "building", label: "BUILDING", action: "Assembling sovereign OS modules", color: "from-orange-500 to-red-600", icon: "🔧" },
  { id: "analyzing", label: "ANALYZING", action: "Profiling telemetry & latency metrics", color: "from-blue-500 to-cyan-600", icon: "📊" },
  { id: "deploying", label: "DEPLOYING", action: "Launching parallel worker swarms", color: "from-rose-500 to-pink-600", icon: "🚀" },
  { id: "connected", label: "CONNECTED", action: "Synchronized with local MCP bridge", color: "from-emerald-400 to-green-600", icon: "📡" },
  { id: "happy", label: "HAPPY", action: "All tests passing cleanly", color: "from-yellow-400 to-amber-500", icon: "✨" },
  { id: "excited", label: "EXCITED", action: "New capability evolved!", color: "from-yellow-300 to-orange-500", icon: "⚡" },
  { id: "focused", label: "FOCUSED", action: "Eliminating architectural debt", color: "from-blue-600 to-indigo-700", icon: "🎯" },
  { id: "determined", label: "DETERMINED", action: "Refactor path locked in", color: "from-red-600 to-rose-700", icon: "🔥" },
  { id: "curious", label: "CURIOUS", action: "Exploring new model weights", color: "from-violet-500 to-purple-600", icon: "❓" },
  { id: "proud", label: "PROUD", action: "APEX Sovereign OS v3.0 fully online", color: "from-amber-400 to-yellow-500", icon: "🏆" }
];

export default function ApexMascotVisualizer() {
  const [activeState, setActiveState] = useState<MascotStateInfo>(MASCOT_STATES[1]);
  const [autoRotate, setAutoRotate] = useState(true);

  useEffect(() => {
    if (!autoRotate) return;
    const interval = setInterval(() => {
      setActiveState((prev) => {
        const nextIdx = (MASCOT_STATES.findIndex((s) => s.id === prev.id) + 1) % MASCOT_STATES.length;
        return MASCOT_STATES[nextIdx];
      });
    }, 4000);
    return () => clearInterval(interval);
  }, [autoRotate]);

  return (
    <div className="relative w-full max-w-4xl mx-auto rounded-2xl border border-white/10 bg-slate-950/80 p-6 backdrop-blur-xl shadow-2xl overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between pb-4 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 rounded-full bg-cyan-400 animate-ping" />
          <h3 className="font-mono text-sm font-bold tracking-wider text-cyan-300 uppercase">
            &lt;APEX MASCOT&gt; // ACTIVE STATE MATRIX
          </h3>
        </div>
        <button
          onClick={() => setAutoRotate(!autoRotate)}
          className={`px-3 py-1 text-xs font-mono rounded-lg transition-all border ${
            autoRotate
              ? "bg-cyan-500/20 text-cyan-300 border-cyan-500/40"
              : "bg-white/5 text-slate-400 border-white/10"
          }`}
        >
          {autoRotate ? "AUTO-CYCLING: ON" : "PAUSED"}
        </button>
      </div>

      {/* Main Mascot Visual */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center my-6">
        {/* Image Card */}
        <div className="md:col-span-5 relative group flex flex-col items-center justify-center p-4 rounded-xl border border-white/10 bg-black/40 overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/10 via-transparent to-purple-500/10 opacity-50 group-hover:opacity-100 transition-opacity" />
          <div className="relative w-64 h-64 rounded-lg overflow-hidden border border-white/10 shadow-lg">
            <Image
              src="/apex-mascot.jpg"
              alt="APEX Official Robot Mascot"
              fill
              className="object-contain p-2 hover:scale-105 transition-transform duration-300"
            />
          </div>
          <p className="font-mono text-[10px] text-slate-400 mt-2 tracking-widest uppercase">
            Official APEX System Mascot
          </p>
        </div>

        {/* State Information */}
        <div className="md:col-span-7 flex flex-col justify-center space-y-4">
          <div className="flex items-center gap-3">
            <span className="text-3xl">{activeState.icon}</span>
            <div>
              <span className="text-xs font-mono text-cyan-400 uppercase tracking-widest">
                Current Agent State
              </span>
              <h2 className="text-2xl font-bold font-mono text-white flex items-center gap-2">
                {activeState.label}
              </h2>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-white/5 border border-white/10">
            <p className="font-mono text-sm text-slate-300">
              <span className="text-cyan-400 font-bold">▶ ACTION:</span> {activeState.action}
            </p>
          </div>

          {/* Selector Grid */}
          <div>
            <p className="font-mono text-xs text-slate-400 mb-2">Select State to Test:</p>
            <div className="flex flex-wrap gap-2">
              {MASCOT_STATES.map((state) => (
                <button
                  key={state.id}
                  onClick={() => {
                    setActiveState(state);
                    setAutoRotate(false);
                  }}
                  className={`px-2.5 py-1 text-xs font-mono rounded-md transition-all border ${
                    activeState.id === state.id
                      ? "bg-cyan-500/30 text-cyan-200 border-cyan-400 shadow-md scale-105"
                      : "bg-white/5 text-slate-400 border-white/5 hover:bg-white/10 hover:text-white"
                  }`}
                >
                  {state.icon} {state.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Footer Tagline */}
      <div className="pt-3 border-t border-white/10 flex items-center justify-between text-xs font-mono text-slate-400">
        <span>Think. Build. Evolve.</span>
        <span className="text-cyan-400">APEX Sovereign OS v3.0</span>
      </div>
    </div>
  );
}
