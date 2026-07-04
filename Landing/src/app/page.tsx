"use client";

import Link from "next/link";
import styles from "./page.module.css";
import { useEffect, useState, useRef, useCallback } from "react";
import CanvasBackground from "../components/CanvasBackground";
import OrchestratorVisualizer from "../components/OrchestratorVisualizer";
import WireframeShapes from "../components/WireframeShapes";
import TelemetryCard from "../components/TelemetryCard";

interface DagNode {
  id: string;
  label: string;
  description: string;
  color: "cyan" | "violet" | "emerald" | "amber" | "orange";
  logs: string[];
  sourceCode: string;
}

const DAG_STEPS: DagNode[] = [
  {
    id: "router",
    label: "INTENT ROUTER",
    description: "Normalizes input query and matches active sovereign skills.",
    color: "cyan",
    logs: [
      "$ apex run router --input='tailor resume for Google SWE'",
      "⏳ [Strategy] Parsing intent signature using Gemini-2.0-Flash...",
      "🔍 [Router] Query intent resolved: 'RESUME_TAILORING'.",
      "🔋 [Vitals] Available RAM: 32.4GB, CPU temperature stable.",
      "🟢 [Router] Active skill compiled: 'resume_tailor_skill.json'. Stage 1 Complete."
    ],
    sourceCode: `# core/router.py
from pydantic import BaseModel
from typing import List, Optional

class IntentRouter(BaseModel):
    """
    Classifies raw queries and resolves Sovereign Skills.
    """
    intent_threshold: float = 0.85
    active_skills: List[str] = []

    async def route_intent(self, query: str) -> str:
        # Resolve target cognitive skill
        normalized = query.strip().lower()
        if "resume" in normalized:
            return "RESUME_TAILORING"
        return "UNKNOWN_INTENT"`
  },
  {
    id: "cache",
    label: "SEMANTIC CACHE",
    description: "Performs vector lookup in Chroma DB to bypass model latency.",
    color: "violet",
    logs: [
      "$ apex query --semantic='tailor resume for Google SWE'",
      "🔍 [Cache] Running cosine similarity lookup in Chroma DB vectors...",
      "⚠️ [Cache] Proximity score: 0.82 (threshold is 0.95).",
      "⚡ [Fastpath] Cache miss. Diverting task execution to strategic planning.",
      "🟢 [Cache] Bypassed. Direct model inference requested. Stage 2 Complete."
    ],
    sourceCode: `# memory/semantic_cache.py
import redis
from chromadb import Client

class SemanticCache:
    """
    Vector search caching to bypass inference models.
    """
    def __init__(self, host: str, port: int):
        self.r = redis.Redis(host=host, port=port)
        self.chroma = Client()

    def lookup(self, vector: list) -> Optional[dict]:
        # Perform cosine vector lookup in Chroma DB
        return self.chroma.query(vector, threshold=0.95)`
  },
  {
    id: "socratic",
    label: "SOCRATIC GATE",
    description: "Probes planning assumptions and forces Steelman critiques.",
    color: "orange",
    logs: [
      "$ apex run socratic-gate --verify-thesis='direct-rewrite'",
      "⏳ [Strategy] Activating Socratic Reasoning Gate...",
      "🧠 [Probing] Critique: Google values impact metrics (XYZ format) over list of skills.",
      "⚠️ [Steelman] Steelman Thesis: Emphasize direct latency reduction in past jobs.",
      "🟢 [Strategy] Plan updated with steelman reasoning rules. Stage 3 Complete."
    ],
    sourceCode: `# core/socratic_gate.py
from pydantic import BaseModel

class SocraticGate(BaseModel):
    """
    Probes assumptions and forces steelman critiques.
    """
    gate_active: bool = True
    deep_probing: bool = True

    def critique(self, plan: list) -> list:
        # Generate strongest counter-arguments
        return ["Google values metrics (XYZ format)"]`
  },
  {
    id: "swarm",
    label: "SWARM DISPATCH",
    description: "Allocates task groups to parallel specialist subagents.",
    color: "emerald",
    logs: [
      "$ apex swarm dispatch --roster=['writer-agent', 'verifier-agent']",
      "⚙️ [Dispatcher] Resolving dependencies: writer waits for verifier AST validation.",
      "📦 [Swarm] Worker 1 (Writer-Agent) spawned in sandbox environment.",
      "📦 [Swarm] Worker 2 (Verifier-Agent) listening on port 8002.",
      "🟢 [Swarm] Swarm fully operational. Tasks running in parallel. Stage 4 Complete."
    ],
    sourceCode: `# core/swarm.py
from typing import List, Dict

class SwarmDispatcher:
    """
    Dispatches task groups to specialist agents.
    """
    def __init__(self, roster: List[str]):
        self.agents = roster
        self.blackboard = {}

    def dispatch(self, tasks: list) -> Dict[str, Any]:
        # Execute parallel TaskGroups asynchronously
        return {"status": "dispatched", "count": len(tasks)}`
  },
  {
    id: "sandbox",
    label: "SANDBOX COMPILER",
    description: "Runs and compiles verified code blocks in isolated sandboxes.",
    color: "amber",
    logs: [
      "$ apex sandbox compile --language=typescript",
      "🛠️ [Harness] Connecting to local runner harness...",
      "⚙️ [Compiler] Parsing AST structure. 1 file generated.",
      "🧪 [Sandbox] Running unit tests: 'npm run test'...",
      "🟢 [Compiler] Tests: 12/12 PASS. Execution validated. Stage 5 Complete."
    ],
    sourceCode: `# core/sandbox.py
import subprocess

class SandboxEngine:
    """
    Compiles and executes code block files securely.
    """
    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def run_tests(self, file_path: str) -> bool:
        # Sandbox execution limits networking
        res = subprocess.run(["npm", "run", "test"])
        return res.returncode == 0`
  },
  {
    id: "verifier",
    label: "SYNC VERIFIER",
    description: "Performs self-healing checks and synchronizes memory loops.",
    color: "cyan",
    logs: [
      "$ apex sync verify --save-cache",
      "🔍 [Verifier] Performing self-healing assertion test...",
      "🧬 [Memory] Adding successful execution to Chroma DB vectors (+1 entry).",
      "💾 [Sync] Synchronized Redis session cache.",
      "🟢 [System] Verification complete. Runtime: 48ms. Cycle Ends."
    ],
    sourceCode: `# core/verifier.py
from .models import ExecutionPlan

class SyncVerifier:
    """
    Validates execution results and syncs vector logs.
    """
    def verify_plan(self, plan: ExecutionPlan) -> bool:
        # Check plan compliance and update cache
        if plan.requires_clarification:
            return False
        return True`
  }
];

// Interactive Sequential Typewriter Text component (Declarative State-Slice based)
function TypewriterText({ text, delay = 0, speed = 80 }: { text: string; delay?: number; speed?: number }) {
  const [charCount, setCharCount] = useState(0);
  const [started, setStarted] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setStarted(true), delay);
    return () => clearTimeout(timer);
  }, [delay]);

  useEffect(() => {
    if (!started) return;
    if (charCount >= text.length) return;

    const timer = setTimeout(() => {
      setCharCount((prev) => prev + 1);
    }, speed);

    return () => clearTimeout(timer);
  }, [started, charCount, text, speed]);

  const displayedText = text.slice(0, charCount);
  const isDone = charCount >= text.length;

  return (
    <span className={styles.typewriterWrapper}>
      {displayedText}
      {started && !isDone && (
        <span className={styles.typewriterCursor}></span>
      )}
    </span>
  );
}

// Reusable L-Shaped HUD corner notches helper component
function HUDNotches() {
  return (
    <div className={styles.hudNotches}>
      <span className={styles.notchTL}></span>
      <span className={styles.notchTR}></span>
      <span className={styles.notchBL}></span>
      <span className={styles.notchBR}></span>
    </div>
  );
}

export default function Home() {
  const cockpitRef = useRef<HTMLDivElement>(null);
  const visualizerContainerRef = useRef<HTMLDivElement>(null);
  const [activeStep, setActiveStep] = useState<string>("router");
  const [terminalLines, setTerminalLines] = useState<string[]>(DAG_STEPS[0].logs);
  const [isSimulating, setIsSimulating] = useState(false);
  const [coords, setCoords] = useState({ x: 0, y: 0 });
  const [consoleMode, setConsoleMode] = useState<"monitor" | "source">("monitor");
  const [guideCoords, setGuideCoords] = useState({ x: 0, y: 0, active: false });
  
  // CLI Command Sandbox input states
  const [userPrompt, setUserPrompt] = useState("apex run resume --tailor='Google SWE'");

  // Select active node based on step
  const activeNode = DAG_STEPS.find(s => s.id === activeStep) || DAG_STEPS[0];

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (cockpitRef.current) {
        const rect = cockpitRef.current.getBoundingClientRect();
        const x = Math.round(e.clientX - rect.left);
        const y = Math.round(e.clientY - rect.top);
        setCoords({ x, y });
      }
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  // Chain pipeline simulation
  const runEndToEndPipeline = useCallback(() => {
    if (isSimulating) return;
    setIsSimulating(true);
    setConsoleMode("monitor");
    setTerminalLines(["$ apex pipeline --run-all"]);

    let currentStepIdx = 0;
    let currentLineIdx = 0;

    const interval = setInterval(() => {
      const stepData = DAG_STEPS[currentStepIdx];
      if (!stepData) {
        clearInterval(interval);
        setIsSimulating(false);
        return;
      }

      setActiveStep(stepData.id);

      if (currentLineIdx < stepData.logs.length) {
        const nextLine = stepData.logs[currentLineIdx];
        if (nextLine) {
          setTerminalLines((prev) => [...prev, nextLine]);
        }
        currentLineIdx++;
      } else {
        currentStepIdx++;
        currentLineIdx = 0;
      }
    }, 280);
  }, [isSimulating]);

  // Execute Sandbox prompt input from Hero
  const executeSandboxPrompt = () => {
    if (isSimulating) return;
    
    const cmdLower = userPrompt.toLowerCase();
    if (cmdLower.includes("cache") || cmdLower.includes("query")) {
      setActiveStep("cache");
      setTerminalLines(DAG_STEPS[1].logs);
    } else if (cmdLower.includes("sandbox") || cmdLower.includes("compile")) {
      setActiveStep("sandbox");
      setTerminalLines(DAG_STEPS[4].logs);
    } else if (cmdLower.includes("socratic") || cmdLower.includes("gate")) {
      setActiveStep("socratic");
      setTerminalLines(DAG_STEPS[2].logs);
    } else {
      runEndToEndPipeline();
    }

    setConsoleMode("monitor");
    
    setTimeout(() => {
      document.getElementById("cockpit")?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  };

  // Handle guidelines movements relative to visualizer container
  const handleVisualizerMouseMove = (e: React.MouseEvent) => {
    if (visualizerContainerRef.current) {
      const rect = visualizerContainerRef.current.getBoundingClientRect();
      const x = Math.round(e.clientX - rect.left);
      const y = Math.round(e.clientY - rect.top);
      setGuideCoords({ x, y, active: true });
    }
  };

  const handleVisualizerMouseLeave = () => {
    setGuideCoords((prev) => ({ ...prev, active: false }));
  };

  // Custom Python Syntax Highlighter
  const renderSyntaxHighlighting = (code: string) => {
    const lines = code.split("\n");
    return lines.map((line, idx) => {
      const trimmed = line.trim();
      
      if (trimmed.startsWith("#") || trimmed.startsWith('"""') || trimmed.endsWith('"""')) {
        return (
          <div key={idx} className={styles.codeComment}>
            {line}
          </div>
        );
      }

      const words = line.split(/(\s+|\(|\)|\:)/);
      const elements = words.map((word, wIdx) => {
        const tWord = word.trim();
        
        if (["from", "import", "class", "def", "return", "async", "await", "if", "else", "elif", "in"].includes(tWord)) {
          return <span key={wIdx} className={styles.codeKeyword}>{word}</span>;
        }
        if (["str", "int", "float", "bool", "list", "dict", "List", "Optional", "Dict", "Any", "BaseModel", "None", "ExecutionPlan"].includes(tWord)) {
          return <span key={wIdx} className={styles.codeClass}>{word}</span>;
        }
        if (tWord === "self") {
          return <span key={wIdx} className={styles.codeSelf}>{word}</span>;
        }
        if ((tWord.startsWith('"') && tWord.endsWith('"')) || (tWord.startsWith("'") && tWord.endsWith("'"))) {
          return <span key={wIdx} className={styles.codeString}>{word}</span>;
        }
        return word;
      });

      return (
        <div key={idx} className={styles.codeLine}>
          {elements}
        </div>
      );
    });
  };

  return (
    <div ref={cockpitRef} className={`${styles.pageWrapper} tech-dots`}>
      {/* Background Interactive Particles */}
      <CanvasBackground />

      {/* Floating System Param Ticker */}
      <div className={styles.systemTicker}>
        <div className={styles.tickerTrack}>
          <span>APEX // COGNITIVE LABS v1.0.0</span>
          <span className={styles.tickerDivider}></span>
          <span>LATENCY: 1.2MS (FAST-PATH)</span>
          <span className={styles.tickerDivider}></span>
          <span>CHROMA DB MEMORY VECTORS: 1,240</span>
          <span className={styles.tickerDivider}></span>
          <span>SOCRATIC AGENT PORT: 8002</span>
          <span className={styles.tickerDivider}></span>
          <span>ACTIVE COORDS: X: {coords.x} | Y: {coords.y}</span>
        </div>
      </div>

      {/* Organic claymorphic gradient background waves matching screenshot */}
      <div className={styles.waveBackgroundContainer}>
        <svg viewBox="0 0 1440 900" fill="none" className={styles.waveSvg}>
          <g filter="url(#blur-mesh)">
            <path d="M-100 200 C300 400, 600 100, 1000 350 C1300 500, 1500 250, 1600 400 L1600 900 L-100 900 Z" fill="rgba(224, 222, 218, 0.65)" />
            <path d="M-50 450 C400 300, 800 600, 1100 400 C1350 250, 1500 500, 1550 550 L1550 900 L-50 900 Z" fill="rgba(232, 230, 226, 0.75)" />
            <path d="M-200 600 C200 500, 500 700, 900 550 C1200 450, 1400 650, 1600 700 L1600 900 L-200 900 Z" fill="rgba(240, 238, 234, 0.9)" />
          </g>
          <defs>
            <filter id="blur-mesh" x="-20%" y="-20%" width="140%" height="140%" filterUnits="userSpaceOnUse" colorInterpolationFilters="sRGB">
              <feGaussianBlur stdDeviation="80" />
            </filter>
          </defs>
        </svg>
      </div>

      {/* Redesigned Minimal Navbar */}
      <header className={styles.header}>
        <HUDNotches />
        <div className={styles.headerLeft}>
          <svg width="40" height="24" viewBox="0 0 100 50" fill="none" className={styles.signatureLogo}>
            <path d="M10 28 C22 15, 32 38, 42 16 C52 0, 58 45, 85 24" stroke="var(--text-primary)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M40 32 L46 38" stroke="var(--text-primary)" strokeWidth="2.5" strokeLinecap="round" />
          </svg>
          <div className={styles.headerDivider}></div>
          <div className={styles.systemStatus}>
            <span className={styles.systemStatusText}>APEX COGNITIVE OS</span>
            <span className={styles.pulsingDot}></span>
          </div>
        </div>
        
        <nav className={styles.navRow}>
          <Link href="#cockpit" className={styles.navLinkItem}>About</Link>
          <span className={styles.navSlash}>/</span>
          <Link href="#telemetry" className={styles.navLinkItem}>Domain</Link>
          <span className={styles.navSlash}>/</span>
          <a 
            href="https://github.com/Qambar-dev-0207/PathOS.git" 
            target="_blank" 
            rel="noreferrer" 
            className={styles.navLinkItem}
          >
            Works
          </a>
          <span className={styles.navSlash}>/</span>
          <a 
            href="https://github.com/Qambar-dev-0207/PathOS.git" 
            target="_blank" 
            rel="noreferrer" 
            className={styles.navLinkItem}
          >
            Contact
          </a>
        </nav>
      </header>

      {/* Hero Section styled exactly like the screenshot but tailored to APEX */}
      <section className={styles.heroSection}>
        <div className={styles.heroGrid}>
          {/* Left technical description text block */}
          <div className={styles.heroLeftCol}>
            <div className={styles.jaLabel}>自律型エージェント。</div>
            <div className={styles.jaLabel}>意思決定の自動化。</div>
            <div className={styles.enLabelSub}>APEX SOVEREIGN OS // COGNITIVE ORCHESTRATION</div>

            {/* Pulsing server status LED stack */}
            <div className={styles.heroStatusStack}>
              <div className={styles.heroStatusRow}>
                <span className={`${styles.statusDot} ${styles.statusDotCyan}`}></span>
                <span className={styles.heroStatusText}>KERNEL : SYS_ACTIVE</span>
              </div>
              <div className={styles.heroStatusRow}>
                <span className={`${styles.statusDot} ${styles.statusDotEmerald}`}></span>
                <span className={styles.heroStatusText}>VECTOR_MEM : SYNCED</span>
              </div>
              <div className={styles.heroStatusRow}>
                <span className={`${styles.statusDot} ${styles.statusDotOrange}`}></span>
                <span className={styles.heroStatusText}>SANDBOX : SECURE_RUN</span>
              </div>
            </div>
          </div>

          {/* Right technical description text block */}
          <div className={styles.heroRightCol}>
            <p className={styles.heroDescPara}>
              意図を解析し、計画を構造化し、自律実行する。
              コグニティブレイヤーとローカル実行エンジンの交差点でつくる知的OS。
            </p>
            <p className={styles.heroDescParaEn}>
              Parsing intent, structuring execution DAGs, compiling parallel sandboxes.
              At the intersection of cognitive intelligence and hardware runtimes, a sovereign orchestrator.
            </p>
          </div>
        </div>

        {/* Massive Serif Headings exactly matching screenshot but tailored to APEX with typewriter animation */}
        <div className={styles.heroTitleContainer}>
          <h1 className={styles.serifTitleLine1}>
            <TypewriterText text="SOVEREIGN" delay={200} speed={100} />
          </h1>
          <h1 className={styles.serifTitleLine2}>
            <TypewriterText text="ORCHESTRATOR" delay={1200} speed={90} />
          </h1>
        </div>

        {/* Interactive CLI Prompt Executor Sandbox - Floating elegantly */}
        <div className={styles.promptSandbox}>
          <div className={styles.promptInputWrapper}>
            <span className={styles.promptPrefix}>&gt;</span>
            <input 
              type="text" 
              value={userPrompt}
              onChange={(e) => setUserPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") executeSandboxPrompt();
              }}
              className={styles.promptInputField}
              placeholder="Type sandbox command..."
            />
            <button className={styles.promptExecuteBtn} onClick={executeSandboxPrompt}>
              <span>EXECUTE</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
              </svg>
            </button>
          </div>

          {/* Quick Preset tags */}
          <div className={styles.promptPresets}>
            <span className={styles.presetLabel}>Presets //</span>
            <button 
              className={styles.presetPill}
              onClick={() => setUserPrompt("apex run resume --tailor='Google SWE'")}
            >
              Resume Tailor
            </button>
            <button 
              className={styles.presetPill}
              onClick={() => setUserPrompt("apex query --semantic='model lookup'")}
            >
              Vector Cache Check
            </button>
            <button 
              className={styles.presetPill}
              onClick={() => setUserPrompt("apex sandbox compile --lang=ts")}
            >
              Sandbox Verify
            </button>
          </div>
        </div>
      </section>

      {/* Cognitive Pipeline Timeline execution bar */}
      <section className={styles.timelineSection}>
        <div className={`${styles.timelineContainer} cockpit-panel`}>
          <HUDNotches />
          <span className={styles.timelineLabel}>{"ACTIVE EXECUTION TIMELINE //"}</span>
          <div className={styles.timelineSteps}>
            {DAG_STEPS.map((step, idx) => {
              const isActive = step.id === activeStep;
              return (
                <div key={step.id} className={styles.timelineStepWrapper}>
                  <div className={`${styles.timelineStep} ${isActive ? styles.timelineStepActive : ""}`}>
                    <span className={styles.timelineIndex}>0{idx + 1}</span>
                    <span className={styles.timelineName}>{step.id.toUpperCase()}</span>
                  </div>
                  {idx < DAG_STEPS.length - 1 && (
                    <div className={styles.timelineDivider}>──</div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Advanced Cockpit Panel */}
      <section id="cockpit" className={styles.cockpitSection}>
        <div className={`${styles.cockpitGrid} cockpit-panel`}>
          <HUDNotches />
          
          {/* Panel 1: Execution Planner (DAG Steps) */}
          <div className={styles.dagPanel}>
            <div className={styles.panelHeader}>
              <span>PLANNER : DECOMPOSED_DAG</span>
            </div>
            
            <div className={styles.dagFlow}>
              {DAG_STEPS.map((step, idx) => {
                const isActive = step.id === activeStep;
                return (
                  <div key={step.id} className={styles.dagStepContainer}>
                    <button 
                      className={`${styles.dagNode} ${isActive ? styles.dagNodeActive : ""}`}
                      onClick={() => {
                        if (!isSimulating) {
                          setActiveStep(step.id);
                          setTerminalLines(step.logs);
                        }
                      }}
                    >
                      <span className={styles.stepIndex}>0{idx + 1}</span>
                      <span className={styles.stepLabel}>{step.label}</span>
                      {isActive && <span className={styles.stepPulse}></span>}
                    </button>
                    {idx < DAG_STEPS.length - 1 && (
                      <div className={styles.dagConnector}></div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Panel 2: 3D Programmatic Visualizer Core with cursor guidelines */}
          <div className={styles.visualizerPanel}>
            <div className={styles.panelHeader}>
              <span>CORE_ORB : ROTATION_STAGE</span>
            </div>
            
            <div 
              ref={visualizerContainerRef}
              className={styles.canvasArea}
              onMouseMove={handleVisualizerMouseMove}
              onMouseLeave={handleVisualizerMouseLeave}
            >
              <OrchestratorVisualizer activePreset={activeStep} isSimulating={isSimulating} />
              
              {/* Dynamic Coordinate Guidelines */}
              {guideCoords.active && (
                <>
                  <div 
                    className={styles.dynamicLineX} 
                    style={{ top: `${guideCoords.y}px` }}
                  />
                  <div 
                    className={styles.dynamicLineY} 
                    style={{ left: `${guideCoords.x}px` }}
                  />
                  <div 
                    className={styles.coordsTooltip}
                    style={{ left: `${guideCoords.x + 12}px`, top: `${guideCoords.y + 12}px` }}
                  >
                    <span>TX: {guideCoords.x - 170}px</span>
                    <span>TY: {180 - guideCoords.y}px</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Panel 3: Dual-Mode Terminal Console */}
          <div className={styles.terminalPanel}>
            <div className={styles.consoleTabSelector}>
              <button 
                className={`${styles.tabBtn} ${consoleMode === "monitor" ? styles.tabBtnActive : ""}`}
                onClick={() => setConsoleMode("monitor")}
              >
                [ MONITOR ]
              </button>
              <button 
                className={`${styles.tabBtn} ${consoleMode === "source" ? styles.tabBtnActive : ""}`}
                onClick={() => setConsoleMode("source")}
              >
                [ SOURCE_CODE ]
              </button>
            </div>

            {consoleMode === "monitor" ? (
              <div className={styles.terminalBody}>
                {terminalLines.map((line, idx) => {
                  if (!line) return null;
                  const isCmd = line.startsWith("$");
                  const isErr = line.includes("⚠️") || line.includes("bypassed");
                  const isSuccess = line.includes("🟢") || line.includes("PASS") || line.includes("successfully");
                  
                  let textClass = "";
                  if (isCmd) textClass = styles.termCmd;
                  else if (isErr) textClass = styles.termErr;
                  else if (isSuccess) textClass = styles.termSuccess;

                  return (
                    <div key={idx} className={`${styles.terminalLine} ${textClass}`}>
                      {line}
                    </div>
                  );
                })}
                {isSimulating && (
                  <div className={styles.terminalCursorLine}>
                    <span className={styles.termCursor}>▋</span>
                  </div>
                )}
              </div>
            ) : (
              <div className={styles.codeBody}>
                {renderSyntaxHighlighting(activeNode.sourceCode)}
              </div>
            )}

            <div className={styles.terminalFooter}>
              <span>ACTIVE: {activeNode.id.toUpperCase()}</span>
              <span>PORT: 8002</span>
            </div>
          </div>

        </div>

        {/* Node description card */}
        <div className={styles.stepDetailsCard}>
          <HUDNotches />
          <span className={styles.detailsLabel}>{"// ACTIVE MODULE DETAILS"}</span>
          <h4 className={styles.detailsTitle}>{activeNode.label}</h4>
          <p className={styles.detailsText}>{activeNode.description}</p>
        </div>
      </section>

      {/* Telemetry Bento Grid */}
      <section id="telemetry" className={styles.telemetrySection}>
        <div className={styles.sectionHeader}>
          <span className={styles.sectionTag}>{"// VITAL STATISTICS"}</span>
          <h2 className={styles.sectionTitle}>System Telemetry</h2>
        </div>

        <div className={styles.bentoGrid}>
          {/* Sparkline Cache Rate */}
          <TelemetryCard 
            title="Semantic Cache Hit Rate" 
            value={98.6} 
            unit="%" 
            subtext="Redis fastpath vector hit ratio"
            type="random"
            color="cyan"
          />

          {/* Sparkline Latency */}
          <TelemetryCard 
            title="Average System Latency" 
            value={1.2} 
            unit="ms" 
            subtext="Cache bypass processing index"
            type="sine"
            color="amber"
          />

          {/* Sparkline CPU thread dispatch */}
          <TelemetryCard 
            title="CPU Thread Allocated" 
            value={34.2} 
            unit="%" 
            subtext="Hardware bridge dispatch cycles"
            type="bars"
            color="emerald"
          />

          {/* Interactive wireframe shapes bento block */}
          <div className={`${styles.wireframeBentoCard} cockpit-panel`}>
            <HUDNotches />
            <div className={styles.wireframeHeader}>
              <span className={styles.wireframeLabel}>TIER 4 // GEOMETRICAL WIREFRAME</span>
              <h3 className={styles.wireframeTitle}>Interactive Clay Gyroscope</h3>
            </div>
            
            <div className={styles.shapesArea}>
              <WireframeShapes />
            </div>
            
            <div className={styles.wireframeFooter}>
              <span>TILT COORDINATES MAP IN REALTIME</span>
            </div>
          </div>
        </div>
      </section>

      {/* Footer structured exactly like the multi-column header */}
      <footer className={styles.footer}>
        <div className={styles.footerGrid}>
          <HUDNotches />
          <div className={styles.footerBrand}>
            <svg width="40" height="24" viewBox="0 0 100 50" fill="none" className={styles.signatureLogo}>
              <path d="M10 28 C22 15, 32 38, 42 16 C52 0, 58 45, 85 24" stroke="var(--text-primary)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M40 32 L46 38" stroke="var(--text-primary)" strokeWidth="2.5" strokeLinecap="round" />
            </svg>
            <span className={styles.footerCopyright}>© 2026 APEX AI. MIT LICENSE.</span>
          </div>
          
          <div className={styles.footerCol}>
            <Link href="#cockpit" className={styles.footerLink}>About</Link>
            <Link href="#telemetry" className={styles.footerLink}>Domain</Link>
            <a 
              href="https://github.com/Qambar-dev-0207/PathOS.git" 
              target="_blank" 
              rel="noreferrer" 
              className={styles.footerLink}
            >
              Works
            </a>
          </div>

          <div className={styles.footerCol}>
            <span className={styles.footerLinkDisabled}>Package</span>
            <span className={styles.footerLinkDisabled}>Member</span>
          </div>

          <div className={styles.footerColRight}>
            <a 
              href="https://github.com/Qambar-dev-0207/PathOS.git" 
              target="_blank" 
              rel="noreferrer" 
              className={styles.footerLink}
            >
              Contact
            </a>
            <span className={styles.footerPortStatus}>PORT DEFAULT: 8002</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
