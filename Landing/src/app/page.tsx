"use client";

import { useState, useRef, useEffect } from "react";
import { motion, useMotionValue, useSpring, AnimatePresence } from "motion/react";
import SensiqHeader from "../components/SensiqHeader";
import LogoMarquee from "../components/LogoMarquee";
import FaqAccordion from "../components/FaqAccordion";
import Footer from "../components/Footer";
import TelemetryCard from "../components/TelemetryCard";
import OrchestratorVisualizer from "../components/OrchestratorVisualizer";
import CodePlayground from "../components/CodePlayground";

/* ─── Magnetic Button (Hanzo Pill Design) ───────────────── */
function MagneticCTA({
  children,
  href,
  variant = "primary",
  className = "",
}: {
  children: React.ReactNode;
  href: string;
  variant?: "primary" | "outline" | "dark";
  className?: string;
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
    x.set((e.clientX - rect.left - rect.width / 2) * 0.25);
    y.set((e.clientY - rect.top - rect.height / 2) * 0.25);
  };

  const handleLeave = () => {
    x.set(0);
    y.set(0);
  };

  const baseStyles =
    "px-8 py-4 rounded-full font-semibold text-sm tracking-wide inline-flex items-center justify-center gap-3 transition-all duration-300 cursor-pointer select-none";

  let variantStyles = "";
  if (variant === "primary") {
    variantStyles =
      "bg-[#FF3700] text-white shadow-[0_4px_16px_rgba(255,55,0,0.28)] hover:bg-[#E03000] hover:shadow-[0_8px_24px_rgba(255,55,0,0.4)] hover:-translate-y-0.5";
  } else if (variant === "dark") {
    variantStyles =
      "bg-[#000000] text-white shadow-[0_4px_16px_rgba(0,0,0,0.18)] hover:bg-[#262626] hover:-translate-y-0.5";
  } else {
    variantStyles =
      "bg-white border border-[#D9D9D9] text-[#000000] shadow-xs hover:border-[#000000] hover:shadow-sm hover:-translate-y-0.5";
  }

  return (
    <motion.a
      ref={ref}
      href={href}
      style={{ x: springX, y: springY }}
      onMouseMove={handleMouse}
      onMouseLeave={handleLeave}
      className={`${baseStyles} ${variantStyles} ${className}`}
    >
      {children}
    </motion.a>
  );
}

/* ─── Preset Data for Live Orchestrator ─────────────────── */
interface PresetSpec {
  id: string;
  name: string;
  tag: string;
  description: string;
  logs: string[];
  sourceCode: string;
}

const PRESETS: PresetSpec[] = [
  {
    id: "resume",
    name: "Resume Tailoring Swarm",
    tag: "VECTOR REWRITE",
    description: "Resolves semantic intent, computes vector similarity in ChromaDB, and executes Socratic steelman rewrites.",
    logs: [
      "$ apex run router --input='tailor resume for Google SWE'",
      "⏳ [Strategy] Parsing intent using Gemini 3.8 Flash...",
      "🔍 [Router] Intent resolved: 'RESUME_TAILORING'.",
      "🔋 [Vitals] RAM: 32.4GB · Vector latency: 38ms.",
      "🟢 [Router] Skill compiled: 'resume_tailor_skill.json'.",
      "✨ [Steelman] Probed 14 career metrics · Rewrote bullet points.",
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
    name: "AST Code Compass",
    tag: "TOKEN COMPRESSION",
    description: "Parses Python & TypeScript AST symbols, slashing token payload by 18.4× without loss of structural context.",
    logs: [
      "$ apex code-compass --index='./src'",
      "🔍 [AST] Building symbol dependency graph...",
      "⚡ [Compass] Extracted 412 class & function signatures.",
      "📉 [Token Saver] 450,000 → 24,100 tokens (18.6× compression).",
      "🟢 Context ready for strategic zero-loss inference.",
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
    name: "Agent Swarm Harness",
    tag: "PARALLEL TASKGROUPS",
    description: "Spawns concurrent WebSearchAgent and CodeAnalyzerAgent in isolated asyncio TaskGroups with real-time hardware bounds.",
    logs: [
      "$ apex swarm --dispatch='Deep dive on AI OS architectures'",
      "🐝 [Swarm] Spawning WebSearchAgent & CodeAnalyzerAgent...",
      "⚡ [Parallel] Fetching 12 artifacts across arXiv & GitHub...",
      "📊 [Synthesis] Merging Knowledge Items into ChromaDB...",
      "🟢 Multi-agent synthesis complete in 1.42s.",
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
    name: "Socratic Invariant Gate",
    tag: "DEFENSIVE REASONING",
    description: "Forces assumption verification before dispatching irreversible autonomous state modifications.",
    logs: [
      "$ apex socratic-gate --probe-assumptions",
      "🧠 [Probing] Thesis: Direct state overwrite without backup.",
      "⚠️ [Critique] High probability of Redis connection lock.",
      "🛡️ [Guardrail] Invariant enforced: Applied rollback transaction.",
      "🟢 State modification verified & passed.",
    ],
    sourceCode: `# core/socratic_gate.py
class SocraticGate:
    def verify_assumptions(self, plan: dict) -> bool:
        if "rollback" not in plan:
            plan["rollback"] = True
        return True`,
  },
];

/* ─── Capability tags for the manifesto ─────────────────── */
interface CapabilityTag {
  label: string;
  highlight: string;
  detail: string;
}

const CAPABILITY_TAGS: CapabilityTag[] = [
  {
    label: "Socratic Reasoning Gates",
    highlight: "100% Invariant Probing",
    detail: "Forces assumption probing and Steelman critiques before any irreversible state mutation occurs.",
  },
  {
    label: "38ms Hybrid Vector Recall",
    highlight: "Redis + ChromaDB Tier",
    detail: "Combines in-memory working cache (<10ms) with persistent vector semantic search (<38ms).",
  },
  {
    label: "18.4× AST Token Compression",
    highlight: "AST Symbol Indexer",
    detail: "Parses abstract syntax trees to inject only live signatures, shrinking 450k contexts to 24k tokens.",
  },
  {
    label: "Parallel TaskGroup Swarms",
    highlight: "asyncio Concurrency",
    detail: "Dispatches concurrent web, file, and sandbox agents in parallel without blocking main loop.",
  },
  {
    label: "Hardware Oscilloscope Vitals",
    highlight: "RAM & Temp Telemetry",
    detail: "Real-time hardware bridge monitoring GPU thermals, system RAM, and live USD spend limits.",
  },
  {
    label: "Zero-State Rollback",
    highlight: "Defensive Checkpoints",
    detail: "Automated snapshot recovery that rolls back state instantly when external tool assertions fail.",
  },
];

/* ─── Process Pipeline Steps ────────────────────────────── */
const PIPELINE_STEPS = [
  {
    num: "01",
    title: "Intent Routing & Socratic Probing",
    subtitle: "Eliminating Hallucinated Premises",
    body: "Before any action or API dispatch occurs, the intent router verifies semantic boundaries and forces assumption probing to detect invalid propositions.",
    badge: "100% assumption verification across 400k production queries",
    metric: "0.00% Unchecked Actions",
  },
  {
    num: "02",
    title: "AST Symbol Context Compression",
    subtitle: "Code Compass Symbol Traverser",
    body: "Code Compass walks the Abstract Syntax Tree to extract only target class and function signatures, feeding razor-sharp context without token bloat.",
    badge: "Shrank context from 450,000 to 24,100 tokens in under 12ms",
    metric: "18.4× Token Savings",
  },
  {
    num: "03",
    title: "Parallel Swarm & Hardware Guardrails",
    subtitle: "Sandboxed Multi-Agent Execution",
    body: "Dispatches isolated agent swarms across Web, File, and Code environments while the hardware bridge monitors system thermals and hard spend limits.",
    badge: "Parallel speedup of 4.2× with sub-38ms vector cache recall",
    metric: "<38ms Vector Latency",
  },
];

/* ─── Autonomous Case Studies ───────────────────────────── */
const CASE_STUDIES = [
  {
    title: "Career OS & Resume Tailoring",
    category: "AUTONOMOUS SYNTHESIS",
    stat: "12 Artifacts Synthesized",
    description: "Vector-driven job description parsing, gap analysis, and Socratic steelman rewriting with verified Google ATS compatibility.",
    tag: "ChromaDB + Gemini 3.8 Flash",
  },
  {
    title: "AST Code Compass Refactor Engine",
    category: "CONTEXT OPTIMIZATION",
    stat: "412 Signatures Mapped",
    description: "Automated dependency graph construction across 85,000 lines of Python & TypeScript with zero hallucinated symbol references.",
    tag: "AST Parsing · 18.4×",
  },
  {
    title: "Socratic Rollback Gatekeeper",
    category: "DEFENSIVE EXECUTION",
    stat: "Zero Invariant Leaks",
    description: "Automatic detection of deadlocks and race conditions during high-concurrency Redis state synchronization.",
    tag: "Zero-Trust Guardrail",
  },
  {
    title: "Multi-Agent Research Swarm",
    category: "DISTRIBUTED INTELLIGENCE",
    stat: "1.42s Synthesis Latency",
    description: "Parallel discovery across arXiv, GitHub repos, and documentation sets with automatic Knowledge Item extraction.",
    tag: "asyncio TaskGroups",
  },
];

export default function Home() {
  /* Dynamic rotating keyword in hero */
  const ROTATING_WORDS = ["Reasoning", "Cognitive OS", "Agent Swarms", "Intelligence"];
  const [wordIndex, setWordIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setWordIndex((prev) => (prev + 1) % ROTATING_WORDS.length);
    }, 2800);
    return () => clearInterval(interval);
  }, [ROTATING_WORDS.length]);

  /* State for interactive capability tag in manifesto */
  const [activeCapability, setActiveCapability] = useState<number>(0);

  /* State for live orchestrator visualizer */
  const [activePresetIndex, setActivePresetIndex] = useState<number>(0);
  const [isSimulating, setIsSimulating] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<"logs" | "code">("logs");
  const currentPreset = PRESETS[activePresetIndex];

  /* State for pricing billing toggle */
  const [isAnnual, setIsAnnual] = useState(false);

  return (
    <div className="min-h-screen bg-white text-[#000000] font-body selection:bg-[#FF3700] selection:text-white relative overflow-x-hidden">
      {/* Floating minimalist navbar */}
      <SensiqHeader />

      {/* ══════════════════════════════════════════════════════════
          1. HERO SECTION — Hanzo Signature Ambient Gradient & Layout
          ══════════════════════════════════════════════════════════ */}
      <section id="overview" className="pt-36 sm:pt-44 pb-20 sm:pb-28 relative z-10 overflow-hidden">
        {/* Hanzo subtle ambient light streaks in background */}
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[550px] pointer-events-none opacity-40 -z-10"
          style={{
            background: "radial-gradient(ellipse at 50% 0%, #EAEAEA 0%, #F5F5F5 45%, transparent 70%)",
            filter: "blur(40px)",
          }}
        />

        <div className="max-w-[1440px] mx-auto px-4 sm:px-8">
          <div className="max-w-[1000px] mx-auto text-center">

            {/* Hanzo-style Status Pill */}
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-white border border-[#D9D9D9] shadow-xs mb-8"
            >
              <span className="w-2 h-2 rounded-full bg-[#0CB300] animate-pulse shadow-[0_0_8px_#0CB300]" />
              <span className="font-mono text-xs font-semibold text-[#000000] uppercase tracking-wider">
                Booking Open · 2 Spots Left
              </span>
            </motion.div>

            {/* Headline — Scaled to Hanzo's Exact ~84px Display Scale */}
            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.65, delay: 0.1, ease: [0.16, 1, 0.3, 1] }}
              className="font-display font-extrabold text-[#000000] tracking-[-0.035em] leading-[1.04] mb-8 text-5xl sm:text-7xl lg:text-[84px]"
            >
              Unlimited{" "}
              <span className="inline-block relative overflow-hidden align-baseline h-[1.15em] min-w-[280px] sm:min-w-[420px] text-left">
                <AnimatePresence mode="wait">
                  <motion.span
                    key={ROTATING_WORDS[wordIndex]}
                    initial={{ y: 50, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: -50, opacity: 0 }}
                    transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
                    className="absolute inset-0 text-[#FF3700] font-serif-accent italic font-normal tracking-normal"
                  >
                    {ROTATING_WORDS[wordIndex]}
                  </motion.span>
                </AnimatePresence>
              </span>
              <br />
              for Solid Systems.
            </motion.h1>

            {/* Subtext — Hanzo's #545454 Neutral Color & Generous Spacing */}
            <motion.p
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.55, delay: 0.2, ease: [0.16, 1, 0.3, 1] }}
              className="text-[#545454] text-lg sm:text-xl font-normal leading-relaxed max-w-[660px] mx-auto mb-10"
            >
              We help engineering teams replace fragile prompt chains with a 24-Layer
              Sovereign Operating System. Enforce Socratic gates, compress token context 18×,
              and execute deterministic multi-agent swarms — fast and hassle-free.
            </motion.p>

            {/* Action Buttons — Hanzo Primary Pill (#FF3700) + Secondary Pill */}
            <motion.div
              initial={{ opacity: 0, y: 14 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.28, ease: [0.16, 1, 0.3, 1] }}
              className="flex flex-wrap items-center justify-center gap-4 mb-14"
            >
              <MagneticCTA href="#pricing" variant="primary">
                Choose your plan
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </MagneticCTA>

              <MagneticCTA href="#work" variant="outline">
                <span className="font-mono text-xs font-semibold tracking-wider">
                  SEE RECENT WORK
                </span>
              </MagneticCTA>
            </motion.div>


            {/* ─── Hero Showcase Card (Hanzo Browser Container) ─── */}
            <motion.div
              initial={{ opacity: 0, y: 35 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.75, delay: 0.35, ease: [0.16, 1, 0.3, 1] }}
              className="relative mx-auto max-w-[1120px] rounded-3xl bg-white border border-[#D9D9D9] shadow-[0_16px_48px_-12px_rgba(0,0,0,0.06)] overflow-hidden"
            >
              {/* Chrome Header */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-[#D9D9D9] bg-[#FAFAFA]">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full bg-[#E5E5E5] inline-block border border-[#D9D9D9]" />
                  <span className="w-3 h-3 rounded-full bg-[#E5E5E5] inline-block border border-[#D9D9D9]" />
                  <span className="w-3 h-3 rounded-full bg-[#E5E5E5] inline-block border border-[#D9D9D9]" />
                </div>
                <div className="bg-white border border-[#D9D9D9] rounded-full px-5 py-1 text-xs font-mono text-[#545454]">
                  apex://live-kernel · socratic-swarm-v2.4
                </div>
                <div className="flex items-center gap-2 font-mono text-xs">
                  <span className="w-2 h-2 rounded-full bg-[#0CB300] animate-pulse" />
                  <span className="text-[#0CB300] font-bold text-[11px]">38ms LATENCY</span>
                </div>
              </div>

              {/* Grid content */}
              <div className="grid grid-cols-1 lg:grid-cols-12 min-h-[380px]">
                {/* Visualizer SVG */}
                <div className="lg:col-span-7 bg-[#FAFAFA] p-8 flex items-center justify-center border-b lg:border-b-0 lg:border-r border-[#D9D9D9]">
                  <div className="w-full h-[280px] relative">
                    <svg viewBox="0 0 500 280" className="w-full h-full">
                      {/* Grid Lines */}
                      <line x1="250" y1="140" x2="140" y2="70" stroke="#D9D9D9" strokeWidth="1.5" strokeDasharray="3 3" />
                      <line x1="250" y1="140" x2="360" y2="70" stroke="#D9D9D9" strokeWidth="1.5" strokeDasharray="3 3" />
                      <line x1="250" y1="140" x2="120" y2="210" stroke="#D9D9D9" strokeWidth="1.5" strokeDasharray="3 3" />
                      <line x1="250" y1="140" x2="380" y2="210" stroke="#D9D9D9" strokeWidth="1.5" strokeDasharray="3 3" />
                      <line x1="140" y1="70" x2="70" y2="140" stroke="#D9D9D9" strokeWidth="1.5" />
                      <line x1="360" y1="70" x2="430" y2="140" stroke="#D9D9D9" strokeWidth="1.5" />

                      {/* Core Node */}
                      <circle cx="250" cy="140" r="32" fill="#FF3700" />
                      <circle cx="250" cy="140" r="42" fill="none" stroke="#FF3700" strokeWidth="1.5" opacity="0.3" className="animate-ping" />
                      <text x="250" y="144" textAnchor="middle" fill="white" fontSize="10" fontFamily="var(--font-jetbrains)" fontWeight="bold">
                        APEX OS
                      </text>

                      {/* Surrounding Nodes */}
                      {[
                        { cx: 140, cy: 70, r: 16, fill: "#000000", label: "Intent Router" },
                        { cx: 360, cy: 70, r: 16, fill: "#000000", label: "Socratic Gate" },
                        { cx: 70, cy: 140, r: 14, fill: "#262626", label: "ChromaDB" },
                        { cx: 430, cy: 140, r: 14, fill: "#0CB300", label: "Hardware Bridge" },
                        { cx: 120, cy: 210, r: 16, fill: "#000000", label: "Agent Swarm" },
                        { cx: 380, cy: 210, r: 14, fill: "#FF3700", label: "Code Compass" },
                      ].map((n, i) => (
                        <g key={i}>
                          <circle cx={n.cx} cy={n.cy} r={n.r} fill={n.fill} />
                          <text x={n.cx} y={n.cy + n.r + 14} textAnchor="middle" fill="#000000" fontSize="9" fontFamily="var(--font-jetbrains)" fontWeight="600">
                            {n.label}
                          </text>
                        </g>
                      ))}
                    </svg>
                  </div>
                </div>

                {/* Reasoning Terminal Block (True Black #000000 Contrast) */}
                <div className="lg:col-span-5 bg-[#000000] p-6 font-mono text-xs flex flex-col justify-between">
                  <div>
                    <div className="flex items-center justify-between pb-3 mb-4 border-b border-white/10 text-white/40 text-[10px] uppercase tracking-wider">
                      <span>Live Invariant Probing</span>
                      <span className="text-[#0CB300]">100% INVARIANTS PASSED</span>
                    </div>

                    <div className="space-y-2">
                      <div className="text-[#FF3700]">$ apex run router --socratic</div>
                      <div className="text-white/60">⏳ Parsing semantic query bounds...</div>
                      <div className="text-white/80">🔍 Intent: SOVEREIGN_SWARM_ORCHESTRATION</div>
                      <div className="text-[#0CB300]">🛡️ Socratic Invariant Gate: PASSED</div>
                      <div className="text-white/60">⚡ Code Compass: 18.4× compression active</div>
                      <div className="text-white/80">📊 Vector Cache Latency: 38ms (ChromaDB)</div>
                      <div className="text-[#545454]">▶ Dispatching 3 parallel TaskGroups...</div>
                    </div>
                  </div>

                  <div className="pt-4 mt-6 border-t border-white/10 flex items-center justify-between text-[11px]">
                    <span className="text-white/40">MEMORY STATE</span>
                    <span className="text-[#0CB300] font-semibold">32.4 GB STABLE</span>
                  </div>
                </div>
              </div>
            </motion.div>

          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          2. LOGO MARQUEE — Hanzo Minimal Monochrome Ticker
          ══════════════════════════════════════════════════════════ */}
      <LogoMarquee />

      {/* ══════════════════════════════════════════════════════════
          3. MANIFESTO & CAPABILITIES — Hanzo's Signature Intro Section
          ══════════════════════════════════════════════════════════ */}
      <section className="py-24 sm:py-32 bg-white">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8">
          <div className="max-w-[1000px] mx-auto">

            {/* Overline */}
            <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest mb-6">
              Hello!
            </div>

            {/* Giant Editorial Statement */}
            <h2 className="font-display font-extrabold text-[#000000] text-3xl sm:text-5xl lg:text-6xl tracking-tight leading-[1.12] mb-12">
              We help startups and enterprise establish{" "}
              <span className="font-serif-accent italic font-normal text-[#FF3700]">mathematical certainty</span>{" "}
              between probabilistic LLMs and irreversible production workloads.
            </h2>

            {/* Interactive Capability Tags Row (Hanzo Service Tags) */}
            <div className="flex flex-wrap gap-2.5 mb-8">
              {CAPABILITY_TAGS.map((cap, idx) => {
                const isActive = activeCapability === idx;
                return (
                  <button
                    key={cap.label}
                    onClick={() => setActiveCapability(idx)}
                    className={`px-5 py-2.5 rounded-full text-xs font-mono font-semibold transition-all duration-200 cursor-pointer ${
                      isActive
                        ? "bg-[#000000] text-white shadow-xs scale-105"
                        : "bg-[#F0F0F0] border border-[#D9D9D9] text-[#000000] hover:border-[#000000]"
                    }`}
                  >
                    {cap.label}
                  </button>
                );
              })}
            </div>

            {/* Capability Detail Card */}
            <motion.div
              key={activeCapability}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="p-8 rounded-3xl bg-[#FAFAFA] border border-[#D9D9D9] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6"
            >
              <div>
                <span className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-wider block mb-2">
                  {CAPABILITY_TAGS[activeCapability].highlight}
                </span>
                <p className="text-[#000000] text-base sm:text-lg font-medium leading-relaxed">
                  {CAPABILITY_TAGS[activeCapability].detail}
                </p>
              </div>
              <div className="shrink-0">
                <span className="px-4 py-2 rounded-full bg-white border border-[#D9D9D9] font-mono text-xs text-[#000000] font-semibold">
                  KERNEL SPEC v2.4
                </span>
              </div>
            </motion.div>

          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          4. PROCESS PIPELINE — Hanzo's 3-Step Section
          ══════════════════════════════════════════════════════════ */}
      <section id="process" className="py-24 sm:py-32 bg-[#FAFAFA] border-y border-[#D9D9D9]">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8">

          {/* Section Header with Asymmetric Layout */}
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-16 pb-8 border-b border-[#D9D9D9]">
            <div>
              <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest mb-3">
                OUR PROCESS, EXPLAINED
              </div>
              <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#000000] tracking-tight">
                Here&apos;s <span className="font-serif-accent italic font-normal text-[#FF3700]">how it works</span>
              </h2>
            </div>
            <p className="text-[#545454] text-base max-w-md">
              A deterministic three-stage execution pipeline replacing unverified prompt chains with strict Socratic assertions.
            </p>
          </div>

          {/* 3 Step Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {PIPELINE_STEPS.map((step) => (
              <div
                key={step.num}
                className="p-8 sm:p-10 rounded-3xl bg-white border border-[#D9D9D9] flex flex-col justify-between min-h-[380px] hover:border-[#000000] transition-all duration-300 shadow-xs"
              >
                <div>
                  <div className="font-mono font-extrabold text-3xl text-[#FF3700] mb-6">
                    {step.num}
                  </div>
                  <h3 className="font-display font-bold text-xl sm:text-2xl text-[#000000] mb-2">
                    {step.title}
                  </h3>
                  <div className="font-mono text-xs font-semibold text-[#545454] uppercase tracking-wider mb-4">
                    {step.subtitle}
                  </div>
                  <p className="text-[#545454] text-sm leading-relaxed mb-6">
                    {step.body}
                  </p>
                </div>

                {/* Verified Metric Quote Box */}
                <div className="pt-6 border-t border-[#D9D9D9]">
                  <div className="font-serif-accent italic text-sm text-[#000000] bg-[#FAFAFA] px-4 py-2.5 rounded-xl border border-[#D9D9D9]">
                    &quot;{step.badge}&quot;
                  </div>
                </div>
              </div>
            ))}
          </div>

        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          5. AUTONOMOUS CASE STUDIES — Hanzo's Work Showcase
          ══════════════════════════════════════════════════════════ */}
      <section id="work" className="py-24 sm:py-32 bg-white">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8">

          {/* Section Header */}
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-16 pb-8 border-b border-[#D9D9D9]">
            <div>
              <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest mb-3">
                OUR PROJECTS
              </div>
              <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#000000] tracking-tight">
                Recent <span className="font-serif-accent italic font-normal text-[#FF3700]">Case Studies</span>
              </h2>
            </div>
            <p className="text-[#545454] text-base max-w-md">
              Real-world systems orchestrated by APEX without human intervention or catastrophic hallucination.
            </p>
          </div>

          {/* 4 Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-16">
            {CASE_STUDIES.map((study, idx) => (
              <div
                key={idx}
                className="group p-8 sm:p-10 rounded-3xl bg-[#FAFAFA] border border-[#D9D9D9] hover:border-[#000000] transition-all duration-300 shadow-xs flex flex-col justify-between min-h-[300px]"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <span className="font-mono text-[11px] font-bold text-[#FF3700] uppercase tracking-wider">
                      {study.category}
                    </span>
                    <span className="font-mono text-xs font-semibold px-3 py-1 rounded-full bg-white border border-[#D9D9D9] text-[#000000]">
                      {study.stat}
                    </span>
                  </div>

                  <h3 className="font-display font-bold text-2xl text-[#000000] mb-3 group-hover:text-[#FF3700] transition-colors">
                    {study.title}
                  </h3>

                  <p className="text-[#545454] text-sm sm:text-base leading-relaxed mb-6">
                    {study.description}
                  </p>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-[#D9D9D9] font-mono text-xs text-[#545454]">
                  <span>{study.tag}</span>
                  <span className="text-[#000000] font-bold group-hover:translate-x-1 transition-transform inline-flex items-center gap-1">
                    Inspect Trace →
                  </span>
                </div>
              </div>
            ))}
          </div>

          {/* ─── Embedded Interactive Orchestrator & Live DAG ─── */}
          <div id="orchestrator" className="rounded-3xl bg-white border border-[#D9D9D9] p-6 sm:p-10 shadow-sm">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8 pb-6 border-b border-[#D9D9D9]">
              <div>
                <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest mb-2">
                  INTERACTIVE HARNESS
                </div>
                <h3 className="font-display text-2xl sm:text-3xl font-extrabold text-[#000000]">
                  Live DAG &amp; <span className="font-serif-accent italic font-normal text-[#FF3700]">Reasoning Inspector</span>
                </h3>
              </div>

              {/* Preset Selector */}
              <div className="flex flex-wrap gap-2 p-1.5 bg-[#F0F0F0] border border-[#D9D9D9] rounded-2xl font-mono text-xs">
                {PRESETS.map((p, idx) => (
                  <button
                    key={p.id}
                    onClick={() => setActivePresetIndex(idx)}
                    className={`px-4 py-2 rounded-xl transition-all font-semibold cursor-pointer ${
                      activePresetIndex === idx
                        ? "bg-[#000000] text-white shadow-xs"
                        : "text-[#545454] hover:text-[#000000]"
                    }`}
                  >
                    {p.name}
                  </button>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              {/* DAG Canvas */}
              <div className="lg:col-span-7 bg-[#FAFAFA] rounded-2xl border border-[#D9D9D9] overflow-hidden flex flex-col">
                <div className="flex items-center justify-between px-5 py-3 border-b border-[#D9D9D9] font-mono text-xs">
                  <span className="text-[#545454] uppercase tracking-wider font-semibold">
                    DAG TOPOLOGY · {currentPreset.tag}
                  </span>
                  <button
                    onClick={() => setIsSimulating(!isSimulating)}
                    className="px-3 py-1 rounded-md bg-[#000000] text-white text-[11px] font-semibold hover:bg-black/80 transition-all cursor-pointer"
                  >
                    {isSimulating ? "PAUSE SIMULATION" : "RESUME"}
                  </button>
                </div>
                <div className="h-[340px] flex items-center justify-center">
                  <OrchestratorVisualizer activePreset={currentPreset.name} isSimulating={isSimulating} />
                </div>
              </div>

              {/* Terminal Code / Trace */}
              <div className="lg:col-span-5 bg-[#000000] rounded-2xl overflow-hidden flex flex-col h-[400px]">
                <div className="bg-[#1A1A1A] px-5 py-3 border-b border-white/10 flex items-center gap-3 font-mono text-xs">
                  <button
                    onClick={() => setActiveTab("logs")}
                    className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                      activeTab === "logs"
                        ? "bg-[#FF3700]/20 text-[#FF3700] font-bold"
                        : "text-white/40 hover:text-white"
                    }`}
                  >
                    REASONING TRACE
                  </button>
                  <button
                    onClick={() => setActiveTab("code")}
                    className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                      activeTab === "code"
                        ? "bg-white/10 text-white font-bold"
                        : "text-white/40 hover:text-white"
                    }`}
                  >
                    PYTHON SOURCE
                  </button>
                </div>

                <div className="p-5 font-mono text-xs overflow-y-auto flex-1 space-y-2">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={currentPreset.id + activeTab}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      exit={{ opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      {activeTab === "logs" ? (
                        currentPreset.logs.map((log, idx) => (
                          <div
                            key={idx}
                            className={`leading-relaxed ${
                              log.includes("🟢")
                                ? "text-[#0CB300] font-semibold"
                                : log.includes("⚠️")
                                ? "text-amber-400"
                                : log.includes("⚡")
                                ? "text-[#FF3700]"
                                : "text-white/70"
                            }`}
                          >
                            {log}
                          </div>
                        ))
                      ) : (
                        <pre className="text-white/70 whitespace-pre-wrap leading-relaxed">
                          {currentPreset.sourceCode}
                        </pre>
                      )}
                    </motion.div>
                  </AnimatePresence>
                </div>

                <div className="px-5 py-2.5 border-t border-white/10 font-mono text-[10px] flex justify-between text-white/40">
                  <span>ACTIVE REASONING NODE</span>
                  <span className="text-[#0CB300] font-bold">100% INVARIANTS PASSED</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          6. ARCHITECTURE & METRIC GRID — Hanzo's About Section
          ══════════════════════════════════════════════════════════ */}
      <section id="stack" className="py-24 sm:py-32 bg-[#FAFAFA] border-y border-[#D9D9D9]">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8">

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
            {/* Left Narrative */}
            <div className="lg:col-span-6 space-y-6">
              <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest">
                Pushing boundaries since 2024
              </div>
              <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#000000] tracking-tight leading-[1.1]">
                Engineering the <span className="font-serif-accent italic font-normal text-[#FF3700]">Post-Hallucination</span> Era
              </h2>
              <p className="text-[#545454] text-base sm:text-lg leading-relaxed">
                Most agentic frameworks treat LLMs like deterministic APIs: they send an unbounded string, hope the model follows instructions, and crash when hallucinations cascade into database writes.
              </p>
              <p className="text-[#545454] text-base leading-relaxed">
                APEX was engineered from the silicon up as a sovereign operating system. With an in-memory scheduler, strict Socratic gatekeeper, and hardware oscilloscope vitals, every autonomous state transition is bounded, verifiable, and recoverable.
              </p>
              <div className="pt-4">
                <MagneticCTA href="#pricing" variant="dark">
                  Explore Cluster Specs →
                </MagneticCTA>
              </div>
            </div>

            {/* Right Metric Boxes (Hanzo 4-Box Grid) */}
            <div className="lg:col-span-6 grid grid-cols-1 sm:grid-cols-2 gap-6">
              {[
                { value: "< 38ms", label: "Vector Cache Latency", note: "ChromaDB + Redis Hybrid" },
                { value: "18.4×", label: "AST Token Savings", note: "Code Compass symbol pruning" },
                { value: "24", label: "Sovereign OS Layers", note: "From kernel to multi-agent swarm" },
                { value: "0.00%", label: "Unchecked Mutations", note: "Guaranteed Socratic invariance" },
              ].map((m, idx) => (
                <div
                  key={idx}
                  className="p-8 rounded-3xl bg-white border border-[#D9D9D9] flex flex-col justify-between min-h-[190px] shadow-xs hover:border-[#000000] transition-all duration-300"
                >
                  <div className="font-display font-extrabold text-4xl sm:text-5xl text-[#000000]">
                    {m.value}
                  </div>
                  <div>
                    <div className="font-display font-bold text-base text-[#000000] mb-1">
                      {m.label}
                    </div>
                    <div className="font-mono text-xs text-[#545454]">
                      {m.note}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          7. HARDWARE OSCILLOSCOPE VITALS
          ══════════════════════════════════════════════════════════ */}
      <section id="telemetry" className="py-24 sm:py-32 bg-white">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8">

          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-16 pb-8 border-b border-[#D9D9D9]">
            <div>
              <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest mb-3">
                REAL-TIME MONITORING
              </div>
              <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#000000] tracking-tight">
                Hardware <span className="font-serif-accent italic font-normal text-[#FF3700]">Oscilloscope</span> Vitals
              </h2>
            </div>
            <p className="text-[#545454] text-base max-w-md">
              Live telemetry streamed directly from the hardware bridge to ensure compute, thermals, and API budgets remain strictly bounded.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <TelemetryCard title="AVAILABLE SYSTEM RAM" value={32.4} unit="GB" subtext="HARDWARE BRIDGE MONITOR" type="sine" color="emerald" />
            <TelemetryCard title="VECTOR CACHE LATENCY" value={38} unit="ms" subtext="CHROMADB SEMANTIC SEARCH" type="bars" color="amber" />
            <TelemetryCard title="CODE COMPASS SAVINGS" value={18.4} unit="x" subtext="AST SYMBOL EFFICIENCY" type="sine" color="cyan" />
            <TelemetryCard title="TOKEN SPEND CONTROL" value={0.042} unit="USD" subtext="REAL-TIME COST TRACKER" type="random" color="violet" />
          </div>

        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          8. DEVELOPER SDK PLAYGROUND
          ══════════════════════════════════════════════════════════ */}
      <section id="playground" className="py-24 sm:py-32 bg-[#FAFAFA] border-y border-[#D9D9D9]">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8 space-y-12">
          <div className="max-w-2xl">
            <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest mb-3">
              DEVELOPER SDK
            </div>
            <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#000000] tracking-tight">
              One Unified <span className="font-serif-accent italic font-normal text-[#FF3700]">Python SDK</span>.
            </h2>
            <p className="text-[#545454] text-base mt-4">
              Write typed agent pipelines with automated rollback, Socratic verification, and telemetry with two lines of code.
            </p>
          </div>
          <CodePlayground />
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          9. PRICING & LICENSING — Hanzo's "Fixed Price, Zero Limits"
          ══════════════════════════════════════════════════════════ */}
      <section id="pricing" className="py-24 sm:py-32 bg-white">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8">

          {/* Section Header */}
          <div className="text-center max-w-2xl mx-auto mb-14">
            <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest mb-3">
              PRICING
            </div>
            <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#000000] tracking-tight mb-4">
              Fixed Price, <span className="font-serif-accent italic font-normal text-[#FF3700]">Zero Limits</span>.
            </h2>
            <p className="text-[#545454] text-base">
              Predictable compute pricing with zero surprise token overages or per-agent penalties.
            </p>

            {/* Monthly / Annual Toggle */}
            <div className="mt-8 inline-flex items-center gap-2 p-1.5 rounded-full bg-[#F0F0F0] border border-[#D9D9D9] shadow-xs">
              <button
                onClick={() => setIsAnnual(false)}
                className={`px-5 py-2 rounded-full text-xs font-mono font-semibold transition-all cursor-pointer ${
                  !isAnnual ? "bg-[#000000] text-white shadow-xs" : "text-[#545454]"
                }`}
              >
                MONTHLY
              </button>
              <button
                onClick={() => setIsAnnual(true)}
                className={`px-5 py-2 rounded-full text-xs font-mono font-semibold transition-all cursor-pointer flex items-center gap-1.5 ${
                  isAnnual ? "bg-[#000000] text-white shadow-xs" : "text-[#545454]"
                }`}
              >
                <span>ANNUAL</span>
                <span className="px-2 py-0.5 rounded-full bg-[#0CB300]/20 text-[#0CB300] text-[10px] font-bold">
                  20% OFF
                </span>
              </button>
            </div>
          </div>

          {/* 3 Pricing Cards Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-stretch max-w-[1240px] mx-auto mb-16">
            {/* Tier 1: Developer Core */}
            <div className="p-8 sm:p-10 rounded-3xl bg-white border border-[#D9D9D9] flex flex-col justify-between shadow-xs hover:border-[#000000] transition-all duration-300">
              <div>
                <div className="font-mono text-xs font-bold text-[#545454] uppercase tracking-wider mb-2">
                  DEVELOPER CORE
                </div>
                <div className="font-display font-extrabold text-4xl sm:text-5xl text-[#000000] mb-2">
                  {isAnnual ? "$159" : "$199"}
                  <span className="text-sm font-normal text-[#545454]">/month</span>
                </div>
                <p className="text-[#545454] text-sm leading-relaxed mb-6">
                  For solo AI researchers and engineers deploying personal sovereign agents.
                </p>

                <div className="space-y-3 pt-6 border-t border-[#D9D9D9] text-sm text-[#000000]">
                  {[
                    "Single-Node APEX Runtime",
                    "Socratic Reasoning Gate",
                    "Local ChromaDB + Redis Tier",
                    "Up to 5 Parallel Agent Swarms",
                    "Community Discord Support",
                  ].map((feat, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-[#0CB300] font-bold">✓</span>
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-8">
                <MagneticCTA href="#orchestrator" variant="outline" className="w-full">
                  Deploy Core
                </MagneticCTA>
              </div>
            </div>

            {/* Tier 2: Production Swarm (Featured - Hanzo #FF3700 Accent) */}
            <div className="p-8 sm:p-10 rounded-3xl bg-white border-2 border-[#FF3700] relative flex flex-col justify-between shadow-md">
              <div className="absolute -top-3.5 left-1/2 -translate-x-1/2 bg-[#FF3700] text-white px-4 py-1 rounded-full font-mono text-[10px] font-bold uppercase tracking-wider">
                MOST POPULAR
              </div>

              <div>
                <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-wider mb-2">
                  PRODUCTION SWARM
                </div>
                <div className="font-display font-extrabold text-4xl sm:text-5xl text-[#000000] mb-2">
                  {isAnnual ? "$559" : "$699"}
                  <span className="text-sm font-normal text-[#545454]">/month</span>
                </div>
                <p className="text-[#545454] text-sm leading-relaxed mb-6">
                  For high-growth teams orchestrating mission-critical autonomous workloads.
                </p>

                <div className="space-y-3 pt-6 border-t border-[#D9D9D9] text-sm text-[#000000]">
                  {[
                    "Full 24-Layer Sovereign OS",
                    "Code Compass (18.4× AST Compression)",
                    "Unlimited Parallel Swarms",
                    "Hardware Oscilloscope & Spend Caps",
                    "Sub-38ms Vector Cache Guarantee",
                    "Dedicated Slack Channel Support",
                  ].map((feat, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-[#FF3700] font-bold">✓</span>
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-8">
                <MagneticCTA href="#orchestrator" variant="primary" className="w-full">
                  Deploy Production Cluster
                </MagneticCTA>
              </div>
            </div>

            {/* Tier 3: Enterprise Sovereign */}
            <div className="p-8 sm:p-10 rounded-3xl bg-white border border-[#D9D9D9] flex flex-col justify-between shadow-xs hover:border-[#000000] transition-all duration-300">
              <div>
                <div className="font-mono text-xs font-bold text-[#545454] uppercase tracking-wider mb-2">
                  CUSTOM
                </div>
                <div className="font-display font-extrabold text-4xl sm:text-5xl text-[#000000] mb-2">
                  {isAnnual ? "$1,999" : "$2,499"}
                  <span className="text-sm font-normal text-[#545454]">/month</span>
                </div>
                <p className="text-[#545454] text-sm leading-relaxed mb-6">
                  For fintech, defense, and air-gapped clusters requiring custom invariants.
                </p>

                <div className="space-y-3 pt-6 border-t border-[#D9D9D9] text-sm text-[#000000]">
                  {[
                    "Air-Gapped On-Premise Cluster",
                    "Custom Socratic Invariant Engine",
                    "Dedicated Hardware Bridge",
                    "99.99% Uptime Guarantee SLA",
                    "24/7 Dedicated Staff Engineer",
                  ].map((feat, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <span className="text-[#0CB300] font-bold">✓</span>
                      <span>{feat}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-8">
                <MagneticCTA href="mailto:team@apex-os.ai" variant="dark" className="w-full">
                  Contact Enterprise
                </MagneticCTA>
              </div>
            </div>
          </div>

        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          10. FAQ ACCORDION — Hanzo Clean Hairline Style
          ══════════════════════════════════════════════════════════ */}
      <section id="faq" className="py-24 sm:py-32 bg-[#FAFAFA] border-y border-[#D9D9D9]">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8">
          <div className="max-w-[1000px] mx-auto">

            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-6 mb-16 pb-8 border-b border-[#D9D9D9]">
              <div>
                <div className="font-mono text-xs font-bold text-[#FF3700] uppercase tracking-widest mb-3">
                  FAQ
                </div>
                <h2 className="font-display text-4xl sm:text-5xl font-extrabold text-[#000000] tracking-tight">
                  Your Questions, <span className="font-serif-accent italic font-normal text-[#FF3700]">Answered</span>
                </h2>
              </div>
              <p className="text-[#545454] text-sm font-mono">
                Have more questions? Book a free discovery call
              </p>
            </div>

            <FaqAccordion />

          </div>
        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          11. FINAL CTA & BOOKING — Hanzo "2 Spots Available" Section
          ══════════════════════════════════════════════════════════ */}
      <section className="py-28 sm:py-36 bg-white relative overflow-hidden">
        <div className="max-w-[1000px] mx-auto px-4 sm:px-8 text-center relative z-10">

          {/* Availability Pill */}
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-[#FAFAFA] border border-[#D9D9D9] shadow-xs mb-8">
            <span className="w-2 h-2 rounded-full bg-[#0CB300] animate-pulse" />
            <span className="font-mono text-xs font-semibold text-[#000000] uppercase tracking-wider">
              2 spots available
            </span>
          </div>

          <h2 className="font-display font-extrabold text-5xl sm:text-7xl text-[#000000] tracking-tight leading-[1.04] mb-8">
            Let&apos;s Connect.<br />
            <span className="font-serif-accent italic font-normal text-[#FF3700]">Zero Hallucinations.</span>
          </h2>

          <p className="text-[#545454] text-lg sm:text-xl font-normal leading-relaxed max-w-[620px] mx-auto mb-10">
            Feel free to contact us with any questions. We are available for enterprise cluster deployments or exploratory architecture deep dives.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <MagneticCTA href="#orchestrator" variant="primary">
              Choose your plan
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </MagneticCTA>

            <MagneticCTA href="https://github.com/Qambar-dev-0207/realjarvis" variant="outline">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
              </svg>
              View on GitHub
            </MagneticCTA>
          </div>

        </div>
      </section>

      {/* ══════════════════════════════════════════════════════════
          12. MINIMALIST FOOTER
          ══════════════════════════════════════════════════════════ */}
      <Footer />
    </div>
  );
}
