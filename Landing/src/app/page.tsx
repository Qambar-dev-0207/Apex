"use client";

import { useState, useRef } from "react";
import { motion, useMotionValue, useSpring, AnimatePresence } from "motion/react";
import SensiqHeader from "../components/SensiqHeader";
import LogoMarquee from "../components/LogoMarquee";
import NumberGrid from "../components/NumberGrid";
import ScrollPinnedShowcase from "../components/ScrollPinnedShowcase";
import DarkShowcase from "../components/DarkShowcase";
import CodePlayground from "../components/CodePlayground";
import ScrollPinnedQuotes from "../components/ScrollPinnedQuotes";
import FaqAccordion from "../components/FaqAccordion";
import Footer from "../components/Footer";
import CanvasBackground from "../components/CanvasBackground";
import TelemetryCard from "../components/TelemetryCard";
import BentoGrid from "../components/BentoGrid";
import TerminalSection from "../components/TerminalSection";
import ComparisonSection from "../components/ComparisonSection";
import OrchestratorVisualizer from "../components/OrchestratorVisualizer";

/* ─── Magnetic Button ──────────────────────────────────── */
function MagneticCTA({
  children,
  href,
  variant = "primary",
}: {
  children: React.ReactNode;
  href: string;
  variant?: "primary" | "outline";
}) {
  const ref = useRef<HTMLAnchorElement>(null);
  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const springX = useSpring(x, { stiffness: 280, damping: 22 });
  const springY = useSpring(y, { stiffness: 280, damping: 22 });

  const handleMouse = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    x.set((e.clientX - rect.left - rect.width / 2) * 0.3);
    y.set((e.clientY - rect.top - rect.height / 2) * 0.3);
  };

  const handleLeave = () => { x.set(0); y.set(0); };

  const base = "px-8 py-4 rounded-2xl font-semibold text-sm tracking-wide inline-flex items-center gap-3 transition-all duration-200 cursor-pointer";
  const styles = variant === "primary"
    ? `${base} bg-[#FF4500] text-white shadow-[0_6px_24px_rgba(255,69,0,0.35)] hover:bg-[#E03E00] hover:shadow-[0_8px_30px_rgba(255,69,0,0.45)]`
    : `${base} bg-white border border-black/12 text-[#0A0A0B] shadow-sm hover:border-black/20 hover:shadow-md`;

  return (
    <motion.a
      ref={ref}
      href={href}
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      className={styles}
    >
      {children}
    </motion.a>
  );
}

/* ─── Preset data for orchestrator section ─────────────── */
interface PresetSpec {
  id: string;
  name: string;
  description: string;
  logs: string[];
  sourceCode: string;
}

const PRESETS: PresetSpec[] = [
  {
    id: "resume",
    name: "Resume Tailoring",
    description: "Normalizes intent, computes vector similarity in ChromaDB, executes Socratic steelman rewrite.",
    logs: [
      "$ apex run router --input='tailor resume for Google SWE'",
      "⏳ [Strategy] Parsing intent using Gemini 2.0 Flash...",
      "🔍 [Router] Intent resolved: 'RESUME_TAILORING'.",
      "🔋 [Vitals] RAM: 32.4GB stable.",
      "🟢 [Router] Skill compiled: 'resume_tailor_skill.json'.",
    ],
    sourceCode: `# core/router.py
from pydantic import BaseModel
from typing import List

class IntentRouter(BaseModel):
    intent_threshold: float = 0.85
    active_skills: List[str] = []

    async def route_intent(self, query: str) -> str:
        normalized = query.strip().lower()
        if "resume" in normalized:
            return "RESUME_TAILORING"
        return "UNKNOWN_INTENT"`,
  },
  {
    id: "compass",
    name: "Code Compass",
    description: "Parses Python & TypeScript AST symbols, providing 18.4x token savings.",
    logs: [
      "$ apex code-compass --index='./src'",
      "🔍 [AST] Building symbol dependency graph...",
      "⚡ [Compass] Extracted 412 class & function signatures.",
      "📉 [Token Saver] 450,000 → 24,100 tokens (18.6×).",
      "🟢 Context ready for strategic inference.",
    ],
    sourceCode: `# services/code_compass.py
import ast

class CodeCompass:
    def extract_symbols(self, file_path: str) -> dict:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())
        return {
            "classes": [n.name for n in ast.walk(tree)
                        if isinstance(n, ast.ClassDef)],
            "functions": [n.name for n in ast.walk(tree)
                          if isinstance(n, ast.FunctionDef)]
        }`,
  },
  {
    id: "swarm",
    name: "Agent Swarm",
    description: "Spawns concurrent Web, File, Code agents in parallel TaskGroups.",
    logs: [
      "$ apex swarm --dispatch='Deep dive on AI OS architectures'",
      "🐝 [Swarm] Spawning WebSearchAgent & CodeAnalyzerAgent...",
      "⚡ [Parallel] Fetching 12 artifacts across arXiv & GitHub...",
      "📊 [Synthesis] Merging Knowledge Items into ChromaDB...",
      "🟢 Multi-agent synthesis complete.",
    ],
    sourceCode: `# core/harness.py
import asyncio

async def dispatch_swarm(task_list: list):
    async with asyncio.TaskGroup() as tg:
        for task in task_list:
            tg.create_task(task.execute())`,
  },
  {
    id: "socratic",
    name: "Socratic Gate",
    description: "Forces assumption probing before dispatching autonomous state changes.",
    logs: [
      "$ apex socratic-gate --probe-assumptions",
      "🧠 [Probing] Thesis: Direct state overwrite without backup.",
      "⚠️ [Critique] High probability of Redis disconnect lock.",
      "🛡️ [Guardrail] Applied rollback strategy.",
      "🟢 Action verified.",
    ],
    sourceCode: `# core/socratic_gate.py
class SocraticGate:
    def verify_assumptions(self, plan: dict) -> bool:
        if "rollback" not in plan:
            plan["rollback"] = True
        return True`,
  },
];

/* ═══════════════════════════════════════════════════════
   MAIN PAGE
═══════════════════════════════════════════════════════ */
export default function Home() {
  const [activePresetIndex, setActivePresetIndex] = useState<number>(0);
  const [isSimulating, setIsSimulating] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<"logs" | "code">("logs");

  const currentPreset = PRESETS[activePresetIndex];

  return (
    <div className="min-h-screen bg-[#F5F4F0] text-[#0A0A0B] font-sans selection:bg-[#FF4500] selection:text-white relative overflow-x-hidden">
      {/* Subtle canvas dots */}
      <CanvasBackground />

      {/* Header */}
      <SensiqHeader />

      {/* ══════════════════════════════════════
          HERO — Centered, commanding, minimal
          ══════════════════════════════════════ */}
      <section id="overview" className="pt-28 pb-12 relative z-10 hero-glow">
        <div className="max-w-[1100px] mx-auto px-4 sm:px-6 text-center">

          {/* Eyebrow */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
            className="flex items-center justify-center gap-3 mb-5"
          >
            <div className="flex items-center gap-2 bg-white/80 border border-black/8 px-4 py-2 rounded-full shadow-sm backdrop-blur-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-[#65CC00] animate-pulse shadow-[0_0_6px_#65CC00]" />
              <span className="font-mono text-[11px] font-semibold text-[#6B7280] uppercase tracking-widest">
                Sovereign Agentic AI · 24 Layers · Est. 2026
              </span>
            </div>
          </motion.div>

          {/* Headline — 96px, screen-commanding */}
          <motion.h1
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.08, ease: [0.16, 1, 0.3, 1] }}
            className="font-display font-extrabold text-[#0A0A0B] leading-[1.0] tracking-[-0.04em] mb-5"
            style={{ fontSize: "clamp(3rem, 7vw, 6rem)" }}
          >
            Intelligence that{" "}
            <span className="relative inline-block">
              <span className="relative z-10">doesn&apos;t</span>
              <span
                className="absolute -bottom-1 left-0 right-0 h-3 opacity-30 rounded-sm -z-10"
                style={{ background: "linear-gradient(90deg, #FF4500, #FF8C00)" }}
              />
            </span>
            <br />
            hallucinate.
          </motion.h1>

          {/* Subtext */}
          <motion.p
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, delay: 0.18, ease: [0.16, 1, 0.3, 1] }}
            className="text-[#6B7280] text-lg sm:text-xl leading-relaxed max-w-[560px] mx-auto mb-8"
          >
            A 24-Layer Agentic AI OS that enforces Socratic guardrails,
            compresses token context 18×, and executes parallel agent swarms.
          </motion.p>

          {/* CTAs */}
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.28, ease: [0.16, 1, 0.3, 1] }}
            className="flex flex-wrap items-center justify-center gap-4 mb-8"
          >
            <MagneticCTA href="#stack" variant="primary">
              Explore the OS
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </MagneticCTA>

            <MagneticCTA href="#playground" variant="outline">
              <span className="font-mono text-xs tracking-wider">SDK PLAYGROUND [ $ ]</span>
            </MagneticCTA>
          </motion.div>

          {/* Social proof strip */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="flex items-center justify-center gap-2 text-xs text-[#9CA3AF] font-mono mb-8"
          >
            <div className="flex -space-x-2">
              {["#6366F1", "#EC4899", "#F59E0B", "#10B981"].map((c, i) => (
                <div
                  key={i}
                  className="w-7 h-7 rounded-full border-2 border-[#F5F4F0]"
                  style={{ background: c }}
                />
              ))}
            </div>
            <span>Trusted by AI architects worldwide</span>
            <span className="text-[#FF4500] font-semibold">★★★★★</span>
          </motion.div>

          {/* Hero preview — DAG floats below */}
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.35, ease: [0.16, 1, 0.3, 1] }}
            className="relative"
          >
            {/* Glow underneath */}
            <div
              className="absolute -inset-x-20 top-16 h-40 opacity-30 pointer-events-none blur-3xl"
              style={{ background: "linear-gradient(90deg, #FF4500, #2563EB, #FF4500)" }}
            />

            <div className="relative apex-card overflow-hidden shadow-[0_40px_100px_-20px_rgba(0,0,0,0.14)]">
              {/* Browser chrome */}
              <div className="flex items-center gap-2 px-6 py-4 border-b border-black/6 bg-[#F9F9F8]">
                <span className="w-3 h-3 rounded-full bg-[#FF5F57]" />
                <span className="w-3 h-3 rounded-full bg-[#FEBC2E]" />
                <span className="w-3 h-3 rounded-full bg-[#28C840]" />
                <div className="flex-1 mx-4 bg-white border border-black/8 rounded-lg px-4 py-1.5 text-xs font-mono text-[#9CA3AF] text-left">
                  apex:// live-dag · resume-tailoring-swarm
                </div>
                <div className="flex items-center gap-1.5">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#65CC00] animate-pulse" />
                  <span className="font-mono text-[10px] text-[#65CC00] font-semibold">LIVE</span>
                </div>
              </div>

              {/* Metrics bar */}
              <div className="flex items-center gap-6 px-6 py-3 bg-[#FAFAF9] border-b border-black/4 font-mono text-xs">
                {[
                  { label: "AVG LATENCY", value: "38ms", color: "#65CC00" },
                  { label: "NODES", value: "11 ACTIVE", color: "#2563EB" },
                  { label: "SOCRATIC GATE", value: "PASSED", color: "#FF4500" },
                ].map((m) => (
                  <div key={m.label} className="flex items-center gap-2">
                    <span className="text-[#9CA3AF]">{m.label}</span>
                    <span className="font-bold" style={{ color: m.color }}>{m.value}</span>
                  </div>
                ))}
              </div>

              {/* Content area */}
              <div className="grid grid-cols-1 lg:grid-cols-5 min-h-[340px]">
                {/* DAG Placeholder with branded look */}
                <div className="lg:col-span-3 bg-[#FAFAF9] flex items-center justify-center p-8 border-r border-black/4">
                  <div className="w-full h-[280px] relative">
                    {/* Stylized node graph placeholder */}
                    <svg viewBox="0 0 480 280" className="w-full h-full opacity-90">
                      {/* Connections */}
                      <line x1="240" y1="140" x2="140" y2="80" stroke="#E5E7EB" strokeWidth="1.5" />
                      <line x1="240" y1="140" x2="340" y2="80" stroke="#E5E7EB" strokeWidth="1.5" />
                      <line x1="240" y1="140" x2="120" y2="200" stroke="#E5E7EB" strokeWidth="1.5" />
                      <line x1="240" y1="140" x2="360" y2="200" stroke="#E5E7EB" strokeWidth="1.5" />
                      <line x1="140" y1="80" x2="80" y2="140" stroke="#E5E7EB" strokeWidth="1" />
                      <line x1="340" y1="80" x2="400" y2="140" stroke="#E5E7EB" strokeWidth="1" />
                      {/* Core node */}
                      <circle cx="240" cy="140" r="28" fill="#FF4500" opacity="0.9" />
                      <text x="240" y="145" textAnchor="middle" fill="white" fontSize="9" fontFamily="monospace" fontWeight="bold">APEX CORE</text>
                      {/* Surrounding nodes */}
                      {[
                        { cx: 140, cy: 80, r: 16, fill: "#7C3AED", label: "Intent Router" },
                        { cx: 340, cy: 80, r: 14, fill: "#2563EB", label: "Socratic Gate" },
                        { cx: 80, cy: 140, r: 12, fill: "#059669", label: "ChromaDB" },
                        { cx: 400, cy: 140, r: 12, fill: "#F59E0B", label: "Redis" },
                        { cx: 120, cy: 200, r: 14, fill: "#EC4899", label: "Agent Swarm" },
                        { cx: 360, cy: 200, r: 12, fill: "#0EA5E9", label: "Sandbox" },
                        { cx: 240, cy: 60, r: 10, fill: "#65CC00", label: "Code Compass" },
                      ].map((node, i) => (
                        <g key={i}>
                          <circle cx={node.cx} cy={node.cy} r={node.r} fill={node.fill} opacity="0.85" />
                          <text x={node.cx} y={node.cy + node.r + 12} textAnchor="middle" fill="#6B7280" fontSize="8" fontFamily="monospace">{node.label}</text>
                        </g>
                      ))}
                    </svg>
                  </div>
                </div>

                {/* Right: Reasoning trace */}
                <div className="lg:col-span-2 bg-[#0A0A0B] p-6 font-mono text-xs space-y-2.5 overflow-hidden">
                  <div className="text-white/30 text-[10px] uppercase tracking-widest mb-4">REASONING TRACE</div>
                  {[
                    { text: "$ apex run router --resume", color: "#FF4500" },
                    { text: "⏳ Parsing intent signature...", color: "#6B7280" },
                    { text: "🔍 Intent: RESUME_TAILORING", color: "#9CA3AF" },
                    { text: "🔋 RAM: 32.4GB · CPU stable", color: "#6B7280" },
                    { text: "⚡ Skill: resume_tailor_skill", color: "#9CA3AF" },
                    { text: "🟢 Socratic gate: PASSED", color: "#65CC00" },
                    { text: "▶ Dispatching agent swarm...", color: "#2563EB" },
                  ].map((line, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.6 + i * 0.12, duration: 0.3 }}
                      style={{ color: line.color }}
                    >
                      {line.text}
                    </motion.div>
                  ))}
                  <div className="flex items-center gap-1.5 mt-4 pt-4 border-t border-white/8">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#65CC00] animate-pulse" />
                    <span className="text-[#65CC00] font-semibold text-[10px]">STAGE: ACTIVE REASONING</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating metric badges */}
            <div className="absolute -top-4 -right-4 hidden lg:block bg-white border border-black/8 px-4 py-2.5 rounded-xl shadow-lg font-mono text-xs space-y-1">
              <div className="flex items-center gap-2 text-[#9CA3AF]">AVG LATENCY <span className="text-[#65CC00] font-bold">38ms</span></div>
              <div className="w-24 h-1 bg-gray-100 rounded-full"><div className="w-4/5 h-full bg-[#65CC00] rounded-full" /></div>
            </div>

            <div className="absolute -bottom-4 -left-4 hidden lg:block bg-white border border-black/8 px-4 py-2.5 rounded-xl shadow-lg font-mono text-xs space-y-1">
              <div className="flex items-center gap-2 text-[#9CA3AF]">CODE COMPASS <span className="text-[#FF4500] font-bold">18.4×</span></div>
              <div className="w-24 h-1 bg-gray-100 rounded-full"><div className="w-11/12 h-full bg-[#FF4500] rounded-full" /></div>
            </div>
          </motion.div>

        </div>
      </section>

      {/* ══════════════════════════════════════
          LOGO MARQUEE — Dark band
          ══════════════════════════════════════ */}
      <LogoMarquee />

      {/* ══════════════════════════════════════
          NUMBER GRID — Editorial stats
          ══════════════════════════════════════ */}
      <NumberGrid />

      {/* ══════════════════════════════════════
          FEATURE ROWS — Alternating
          ══════════════════════════════════════ */}
      <ScrollPinnedShowcase />

      {/* ══════════════════════════════════════
          STACK BENTO GRID
          ══════════════════════════════════════ */}
      <section id="stack" className="py-16 bg-[#F5F4F0]">
        <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-14 max-w-xl"
          >
            <div className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest mb-4">
              SOVEREIGN ARCHITECTURE
            </div>
            <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#0A0A0B] tracking-tight leading-tight">
              The 24-Layer<br />Sovereign Stack
            </h2>
          </motion.div>
          <BentoGrid />
        </div>
      </section>

      {/* ══════════════════════════════════════
          DARK SHOWCASE — DAG on dark
          ══════════════════════════════════════ */}
      <DarkShowcase />

      {/* ══════════════════════════════════════
          SDK PLAYGROUND
          ══════════════════════════════════════ */}
      <section id="playground" className="py-16 bg-white">
        <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8 space-y-14">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="max-w-xl"
          >
            <div className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest mb-4">
              DEVELOPER SDK
            </div>
            <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#0A0A0B] tracking-tight">
              One unified API.<br />Infinite capability.
            </h2>
          </motion.div>
          <CodePlayground />
        </div>
      </section>

      {/* ══════════════════════════════════════
          ORCHESTRATOR — Interactive
          ══════════════════════════════════════ */}
      <section id="orchestrator" className="py-16 bg-[#F5F4F0] border-y border-black/6">
        <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-8"
          >
            <div>
              <div className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest mb-4">
                SOCRATIC GATE &amp; DAG
              </div>
              <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#0A0A0B] tracking-tight">
                Task Orchestrator<br />&amp; Reasoning Trace
              </h2>
            </div>

            {/* Preset tabs */}
            <div className="flex flex-wrap gap-2 p-1.5 bg-white border border-black/8 rounded-2xl font-mono text-xs shadow-sm">
              {PRESETS.map((p, idx) => (
                <button
                  key={p.id}
                  onClick={() => setActivePresetIndex(idx)}
                  className={`px-4 py-2 rounded-xl transition-all ${
                    activePresetIndex === idx
                      ? "bg-[#0A0A0B] text-white font-bold shadow-sm"
                      : "text-[#6B7280] hover:text-[#0A0A0B]"
                  }`}
                >
                  {p.name}
                </button>
              ))}
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
            <div className="lg:col-span-7 flex flex-col gap-4">
              <div className="apex-card overflow-hidden flex-1">
                <div className="flex items-center justify-between px-5 py-3 border-b border-black/6 font-mono text-xs bg-[#FAFAF9]">
                  <span className="text-[#9CA3AF] uppercase tracking-wider">LIVE DAG · {currentPreset.name.toUpperCase()}</span>
                  <button
                    onClick={() => setIsSimulating(!isSimulating)}
                    className="px-3 py-1 rounded-lg bg-[#0A0A0B] text-white font-semibold text-[11px] hover:bg-black/80 transition-all"
                  >
                    {isSimulating ? "⏸ PAUSE" : "▶ RESUME"}
                  </button>
                </div>
                <div className="h-[360px] bg-[#FAFAF9]">
                  <OrchestratorVisualizer activePreset={currentPreset.name} isSimulating={isSimulating} />
                </div>
              </div>
            </div>

            {/* Reasoning / Code panel */}
            <div className="lg:col-span-5 bg-[#0A0A0B] rounded-2xl overflow-hidden shadow-[0_20px_60px_rgba(0,0,0,0.2)] flex flex-col h-[440px]">
              <div className="bg-[#111115] px-5 py-3.5 border-b border-white/8 flex items-center gap-3 font-mono text-xs">
                <button
                  onClick={() => setActiveTab("logs")}
                  className={`px-3 py-1.5 rounded-lg transition-all ${
                    activeTab === "logs"
                      ? "bg-[#FF4500]/20 text-[#FF4500] font-bold"
                      : "text-white/30 hover:text-white/60"
                  }`}
                >
                  REASONING TRACE
                </button>
                <button
                  onClick={() => setActiveTab("code")}
                  className={`px-3 py-1.5 rounded-lg transition-all ${
                    activeTab === "code"
                      ? "bg-[#2563EB]/20 text-[#2563EB] font-bold"
                      : "text-white/30 hover:text-white/60"
                  }`}
                >
                  PYTHON SOURCE
                </button>
                <span className="ml-auto text-white/20 text-[10px]">APEX ENGINE</span>
              </div>

              <div className="p-5 font-mono text-xs overflow-y-auto flex-1 space-y-2.5">
                <AnimatePresence mode="wait">
                  <motion.div
                    key={currentPreset.id + activeTab}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.25 }}
                  >
                    {activeTab === "logs"
                      ? currentPreset.logs.map((log, idx) => (
                          <div
                            key={idx}
                            className={`leading-relaxed ${
                              log.includes("🟢") ? "text-[#65CC00] font-semibold"
                              : log.includes("⚠️") ? "text-amber-400"
                              : log.includes("⚡") ? "text-[#2563EB]"
                              : "text-white/50"
                            }`}
                          >
                            {log}
                          </div>
                        ))
                      : (
                          <pre className="text-white/50 whitespace-pre-wrap leading-relaxed">
                            {currentPreset.sourceCode}
                          </pre>
                        )
                    }
                  </motion.div>
                </AnimatePresence>
              </div>

              <div className="px-5 py-3 border-t border-white/6 font-mono text-[10px] flex justify-between">
                <span className="text-white/25">STAGE: ACTIVE REASONING</span>
                <span className="text-[#65CC00] font-semibold">PASSED SOCRATIC GATE</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════
          TELEMETRY CARDS
          ══════════════════════════════════════ */}
      <section id="telemetry" className="py-16 bg-white">
        <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8 space-y-14">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="max-w-xl"
          >
            <div className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest mb-4">
              REAL-TIME MONITORING
            </div>
            <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#0A0A0B] tracking-tight">
              Hardware oscilloscope<br />vitals
            </h2>
          </motion.div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
            <TelemetryCard title="AVAILABLE SYSTEM RAM" value={32.4} unit="GB" subtext="HARDWARE BRIDGE MONITOR" type="sine" color="emerald" />
            <TelemetryCard title="VECTOR CACHE LATENCY" value={38} unit="ms" subtext="CHROMADB SEMANTIC SEARCH" type="bars" color="cyan" />
            <TelemetryCard title="CODE COMPASS SAVINGS" value={18.4} unit="x" subtext="AST SYMBOL EFFICIENCY" type="sine" color="amber" />
            <TelemetryCard title="TOKEN SPEND CONTROL" value={0.042} unit="USD" subtext="REAL-TIME COST TRACKER" type="random" color="violet" />
          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════
          COMPARISON — Before / After
          ══════════════════════════════════════ */}
      <ComparisonSection />

      {/* ══════════════════════════════════════
          CLI TERMINAL
          ══════════════════════════════════════ */}
      <section id="terminal" className="py-16 bg-white border-t border-black/6">
        <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8">
          <TerminalSection />
        </div>
      </section>

      {/* ══════════════════════════════════════
          TESTIMONIALS
          ══════════════════════════════════════ */}
      <ScrollPinnedQuotes />

      {/* ══════════════════════════════════════
          FAQ
          ══════════════════════════════════════ */}
      <section className="py-16 bg-[#F5F4F0] border-y border-black/6">
        <div className="max-w-[1340px] mx-auto px-4 sm:px-6 md:px-8 space-y-14">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
            className="max-w-xl"
          >
            <div className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest mb-4">
              FAQ
            </div>
            <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#0A0A0B] tracking-tight">
              Sovereign OS<br />specifications
            </h2>
          </motion.div>
          <FaqAccordion />
        </div>
      </section>

      {/* ══════════════════════════════════════
          FINAL CTA — Mesh gradient, magnetic
          ══════════════════════════════════════ */}
      <section className="py-20 bg-[#F5F4F0] relative overflow-hidden">
        {/* Mesh gradient orbs */}
        <div className="absolute inset-0 pointer-events-none">
          <div
            className="absolute top-0 left-1/4 w-[600px] h-[400px] opacity-40"
            style={{
              background: "radial-gradient(ellipse, rgba(255,69,0,0.15) 0%, transparent 70%)",
              filter: "blur(80px)",
            }}
          />
          <div
            className="absolute bottom-0 right-1/4 w-[500px] h-[300px] opacity-30"
            style={{
              background: "radial-gradient(ellipse, rgba(37,99,235,0.12) 0%, transparent 70%)",
              filter: "blur(80px)",
            }}
          />
        </div>

        <div className="max-w-[900px] mx-auto px-4 sm:px-6 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, ease: [0.16, 1, 0.3, 1] }}
            className="space-y-8"
          >
            <div className="font-mono text-[11px] font-bold text-[#FF4500] uppercase tracking-widest">
              GET STARTED
            </div>

            <h2 className="font-display font-extrabold text-[#0A0A0B] tracking-[-0.03em] leading-[1.0]"
              style={{ fontSize: "clamp(2.5rem, 6vw, 5rem)" }}>
              Ready to build<br />
              <span className="text-[#FF4500]">sovereign</span> intelligence?
            </h2>

            <p className="text-[#6B7280] text-lg max-w-lg mx-auto leading-relaxed">
              Deploy autonomous Socratic agent swarms with full hardware-native memory and spend controls.
            </p>

            <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
              <MagneticCTA href="#orchestrator" variant="primary">
                Launch HUD now
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </MagneticCTA>

              <MagneticCTA href="https://github.com/Qambar-dev-0207/realjarvis" variant="outline">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
                </svg>
                View on GitHub
              </MagneticCTA>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <Footer />
    </div>
  );
}
