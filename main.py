import os
import json
import uuid
import asyncio
import time
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
import re
import pyfiglet
from pathlib import Path
from typing import Any, Dict, Optional
from rich.console import Console, Group
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.align import Align
from rich.layout import Layout
from rich.table import Table
from rich.markdown import Markdown
from dotenv import load_dotenv

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML

from src.routers.router import InputClassifier, SmartRouter, ParallelExecutor
from src.models.fast_path import GroqClient
from src.models.thinking_path import GeminiClient
from src.services.memory import MemoryManager
from src.services.learning import LearningManager
from src.services.delivery import ResponseAssembler
from src.core.telemetry import SpendTracker
from src.tools.workspace import WorkspaceManager
from src.tools.vision import RetinaTool
from src.services.proactive import BriefingAgent
from src.services.cognitive import EmotionalCore
from src.services.sync import SovereignSync
from src.services.cognitive_graph import KnowledgeVisualizer
from src.services.proactive_provisioning import AutoProvisioner
from src.services.self_evolution import SelfEvolver
from src.services.code_compass import CodeCompass
from src.services.knowledge_forge import KnowledgeForge
from src.services.think_partner import ThinkPartner, detect_think_mode
from src.services.swarm import Swarm
from src.core.time_context import TimeContext
from src.tools.auto_selector import AutoToolSelector, regex_match as tool_regex_match
from src.core.reflex import PrefetchBundle
from src.core.hooks import HookManager
from src.core.harness import AgentHarness
from src.services.genius_mode import GeniusMode
from src.tools.resume_tool import ResumeTool
from src.core.api_security import validate_all_keys, leaked_key_warning
from src.services.predictor import PredictorService
from src.models.local_path import OllamaClient
from src.core.animations import (
    pulse_banner, type_text, progress_trail, sparkle_panel,
    thinking_orb, matrix_rain, neural_pulse,
    thinking_cascade, response_reveal, stream_panel,
    status_ticker, decrypt_reveal_banner,
)


SLASH_HELP = """\
[bold cyan]APEX SLASH COMMANDS[/bold cyan]

[yellow]Session[/yellow]
  /help                    Show this menu
  /now                     Show current date, time, weekday
  /tools                   Show registered tools + per-tool success/fail stats
  /reflex                  Show Reflex (local router) telemetry — cache + LLM-skip rate
  /reflex prefetch on|off  Toggle speculative prefetch (auto-disables on high waste)
  /reflex reset            Reset Reflex counters + cache
  /clear                   Clear console
  /clear-session           Wipe current session memory
  /clear-all               Wipe all memories (requires confirm)
  /exit                    Quit APEX
  /resume                  List recent sessions to resume
  /compact                 Summarize and trim long-term context
  /legends                 List all memory logs degraded into legends
  /legend correct <prefix> <text> Manually rewrite a legend's narrative
  /degrade                 Force-degrade all memories into legends
  /sim_interrupt           Queue a mock background interrupt alert

[yellow]Workspace[/yellow]
  /init                    Generate APEX.md project directives
  /scan                    Re-map active project files (honors .apexignore)
  /map                     Render knowledge graph SVG
  /prune                   Show pruned context for current focus
  /project <name>          Create new project
  /skills                  List registered skills
  /reload-skills           Reload markdown skills
  /todo <task>             Add todo to active project
  /todo done <n>           Mark todo #n complete
  /todos                   List todos for active project

[yellow]Modes[/yellow]
  /socratic                Toggle Socratic critique
  /steelman                Toggle Steelman counter-arch mode
  /genius                  Toggle Genius multi-pass reasoning (deepest mode)
  /autothink on|off        Toggle auto-routing of ambiguous prompts to ThinkPartner
  /autotool on|off         Toggle bypass-planner for single-tool prompts (e.g. "git status")
  /autoswarm on|off        Toggle auto-spawn agent swarm on high-complexity coding/architect

[yellow]Auto-spawn[/yellow]
  ^^ <goal>                Auto-spawn agent swarm (^^ <goal> [| roles] [rounds=N])
  >> <goal>                Auto-spawn autonomous harness (>> <goal> [max=N])

[yellow]Think Partner[/yellow]
  /think <prompt>          Cross-question — surface ambiguity before answering
  /architect <idea>        Design partner — propose + critique your architecture
  /architect <idea> | <yours>   Same, with your architecture after the |
  /debate <claim>          Adversarial pushback (steelman opposing view)
  /brainstorm <topic>      Divergent ideation — 6 distinct angles
  /teach <topic>           Layered explanation: intuition -> mechanism -> test
  /intent <prompt>         Show structured intent decomposition (debug aid)

[yellow]Multi-Agent Swarm[/yellow]
  /swarm <goal>            Spawn specialist agents (architect/coder/critic/...) in parallel
  /swarm <goal> | <roles>  Force specific roster, e.g. "/swarm fix bug | coder,critic"
  /swarm <goal> rounds=N   Run N rounds of agent collaboration (default 1)
  /auto-approve            Toggle auto-approve (bypass prompts)
  /plan                    Toggle plan-only mode (no writes/exec)

[yellow]Harness (Autonomous Agent)[/yellow]
  /harness <goal>          Run tool-calling agent (MiMo/Groq) end-to-end on a goal
  /harness max=N <goal>    Cap steps (default 30)
  /harness rollback        Restore touched files from last harness snapshot

[yellow]Voice & Ambient[/yellow]
  /voice [on|off|mute|unmute|status] Toggle or show status of hands-free Voice Layer
  /ambient [on|off|status] Toggle or show status of Ambient Layer context

[yellow]Genius Critique & Rivals[/yellow]
  /genius <prompt>         Full 5-stage critique: cross-question / right / wrong / blind spots / action / wit
  /critique <prompt>       What you're getting right vs wrong (terse)
  /blindspot <prompt>      Second-order consequences + suggested next steps
  /audit                   Show rival scorecards and pending disputes
  /audit resolve <rival> <index> <winner> Resolve a dispute (winner: user|rival)

[yellow]Resume[/yellow]
  /resume <path>           Rewrite resume (PDF/DOCX/TXT/MD) -> polished PDF + feedback
  /resume <path> | <role>  Target a specific role (e.g. "Senior Backend Engineer")

[yellow]Self-Evolution[/yellow]
  /evolve                  Run self-improvement cycle now
  /evolve auto             Run cycle + auto-provision missing skill
  /proposals               Show recent self-improvement proposals

[yellow]Knowledge Forge[/yellow]
  /forge                   Run full forge cycle (papers + ecosystem + synthesis + bench)
  /forge papers            Scan arxiv for new applicable papers
  /forge ecosystem         Scan PyPI/GitHub/HF/HN/npm for new tools
  /forge synth             Synthesize queued capability proposals
  /forge bench             Run self-benchmark (HumanEval-lite)
  /forge proposals         List queued capability proposals
  /forge approve <id>      Mark proposal approved (no auto-apply)
  /forge reject <id>       Mark proposal rejected
  /forge implement <id>    Auto-apply approved proposal (Gemini code-gen + bench-gated)
  /forge implement <id> diff  Same but use search-replace diff mode (safer for large files)
  /forge backfill <N>      Catch-up arxiv scan for last N days (default 7)
  /forge undo <id>         Restore last backup for a proposal (revert apply)
  /forge search <query>    Semantic search ingested papers
  /forge status            Show forge state + last cycle summary
  /forge log               Show ~/.apex/forge_log.md (cycle history)

[yellow]Code Intel[/yellow]
  /analyze                 Build/refresh token-efficient code map
  /analyze <term>          Find symbols across codebase (compressed)
  /map-stats               Show compression ratio + savings
  /index-codebase [--rebuild] Index codebase to vector DB (ChromaDB)
  /search-codebase <query> Semantic local search inside code index
  /repomap [level]         Export structured Repository Map (1|2|3)

[yellow]Telemetry[/yellow]
  /cost                    Show daily spend
  /status                  System health summary
  /predict                 Show next predicted command, upcoming deadlines + spend snapshot
  /patterns                Full pattern dashboard: top commands, failures, budget & prediction
  /policy [allow|deny] cmd Manage execution policy

[yellow]Snapshot[/yellow]
  /snapshot                Export encrypted state zip
  /restore <path>          Restore from snapshot

[yellow]Tools[/yellow]
  ! <command>              Run shell command directly (passthrough)
  /web <query>             Run web search
  /fetch <url>             Pull URL content (clean text)
  /diff <a> <b>            Unified diff between two files
  /mcp connect <name> <cmd> [args...]
  /mcp list                List connected MCP servers
  /mcp tools <server>      List tools on a server
"""


class APEXEngine:
    def __init__(self):
        self.console = Console()
        self.ready = False
        self.session_id = str(uuid.uuid4())[:8]
        load_dotenv()
        self.voice_enabled = False
        self.ambient_enabled = False
        self.input_queue = None
        self.loop = None

    @property
    def active_project_name(self) -> Optional[str]:
        if hasattr(self, 'workspace'):
            active = self.workspace.get_active()
            if active:
                return active.name
        return None

    async def load_system(self, progress=None):
        """
        Boot the engine. Optional `progress` is an async callable accepting a
        single string — called between major stages so the boot UI can show
        what's actually happening instead of a frozen single-label cascade.
        """
        async def _stage(label):
            if progress is not None:
                try:
                    await progress(label)
                except Exception:
                    pass

        from src.tools.mcp_client import MCPClient

        await _stage("Mounting MCP bridge")
        self.mcp_client = MCPClient()

        await _stage("Booting Reflex scout (local router)")
        self.classifier = InputClassifier()
        self.router = SmartRouter()

        await _stage("Loading memory layer (Redis + ChromaDB)")
        self.memory_manager = MemoryManager()

        await _stage("Indexing workspace + skills")
        self.workspace = WorkspaceManager()
        self.knowledge_visualizer = KnowledgeVisualizer(self.memory_manager, self.workspace)
        self.learning_manager = LearningManager(self.memory_manager)
        self.learning_manager.seed_skills()

        await _stage("Linking codebase indexer + repo map")
        from src.services.codebase_index import CodebaseIndexer
        from src.services.repo_map import RepoMapGenerator
        self.codebase_indexer = CodebaseIndexer(self.memory_manager, self.workspace)
        self.repo_map_generator = RepoMapGenerator(root_dir=os.getcwd())

        await _stage("Wiring brains — Gemini 3.5 / Groq / MiMo")
        self.gemini_client = GeminiClient(model_name="gemini-3.5-flash", mcp_client=self.mcp_client) if os.getenv("GEMINI_API_KEY") else None
        self.provisioner = AutoProvisioner(self.learning_manager.skill_manager, self.mcp_client, self.workspace)

        await _stage("Spawning parallel executor + 17 tools")
        self.parallel_executor = ParallelExecutor(
            console=self.console,
            primary_brain=self.gemini_client,
            mcp_client=self.mcp_client,
            codebase_indexer=self.codebase_indexer
        )
        self.assembler = ResponseAssembler(self.console)
        self.spend_tracker = SpendTracker()
        self.retina = RetinaTool()
        self.briefing_agent = BriefingAgent(self.workspace, self.spend_tracker)
        self._briefing_forge_pending = True
        self.cognitive_core = EmotionalCore()
        self.sync_manager = SovereignSync()
        self.groq_client = GroqClient()
        self.hooks = HookManager(project_root=os.getcwd())

        self.loop = asyncio.get_running_loop()
        self.input_queue = asyncio.Queue()
        self.interrupt_queue = asyncio.Queue()

        self.voice_enabled = os.getenv("APEX_VOICE", "0") == "1"
        self.voice_task = None
        if self.voice_enabled:
            await _stage("Loading voice layer")
            from src.services.voice_layer import VoiceLayer
            self.voice = VoiceLayer(console=self.console)
            async def _on_voice_transcript(text: str):
                await self.input_queue.put(text)
            self.voice.on_transcript = _on_voice_transcript
        else:
            self.voice = None

        await _stage("Loading ambient service")
        from src.services.ambient import AmbientService
        self.ambient = AmbientService(self)
        self.ambient_enabled = os.getenv("APEX_AMBIENT", "0") == "1"

        await _stage("Building code compass (AST symbol map)")
        self.code_compass = CodeCompass(root=os.getcwd())

        await _stage("Calibrating think partner + agent swarm")
        self.think_partner = ThinkPartner(console=self.console)
        self.auto_think_enabled = False
        self.economy_mode = os.getenv("APEX_ECONOMY", "1") != "0"
        self.background_loops_enabled = os.getenv("APEX_BG_LOOPS", "0") == "1"
        self.briefing_enabled = os.getenv("APEX_BRIEFING", "0") == "1"
        self.daily_call_limit = int(os.getenv("APEX_DAILY_CALL_LIMIT", "40"))
        self.swarm = Swarm(console=self.console)
        self.pending_clarification = None
        self.tool_selector = AutoToolSelector()
        self.auto_tool_enabled = True
        self.auto_swarm_enabled = False

        self.parallel_executor.retina = self.retina
        self.parallel_executor.code_compass = self.code_compass
        self.parallel_executor.think_partner = self.think_partner
        self.parallel_executor.agent_swarm = self.swarm

        await _stage("Linking knowledge forge (papers + ecosystem)")
        self.knowledge_forge = KnowledgeForge(
            hw_monitor=self.parallel_executor.hw,
            console=self.console,
            hooks=self.hooks,
            project_root=os.getcwd(),
        )
        self.briefing_agent.forge = self.knowledge_forge
        self.parallel_executor.knowledge_forge = self.knowledge_forge
        self.knowledge_forge.engine = self

        await _stage("Loading Genius critique + Resume tool")
        self.genius = GeniusMode(
            mimo_client=self.parallel_executor.coding_pipeline.mimo,
            groq_client=self.groq_client,
        )
        self.resume_tool = ResumeTool()

        await _stage("Arming autonomous harness (35 tools)")
        self.harness = AgentHarness(
            console=self.console,
            fs=self.parallel_executor.fs,
            shell=self.parallel_executor.shell,
            git=self.parallel_executor.git,
            executor=self.parallel_executor,
            gemini_client=self.gemini_client,
            mcp_client=self.mcp_client,
            retina=self.retina,
            code_compass=self.code_compass,
            knowledge_forge=self.knowledge_forge,
            swarm=self.swarm,
            think_partner=self.think_partner,
            workspace=self.workspace,
            project_root=os.getcwd(),
            genius=self.genius,
            max_steps=30,
        )

        await _stage("Priming self-evolver")
        self.self_evolver = SelfEvolver(
            workspace=self.workspace,
            learning_manager=self.learning_manager,
            provisioner=self.provisioner,
            hw_monitor=self.parallel_executor.hw,
            console=self.console,
            forge=self.knowledge_forge,
        )
        self.self_evolver.engine = self

        if self.voice_enabled:
            self.voice_task = asyncio.create_task(self.voice.run())
        if self.ambient_enabled:
            self.ambient.start()

        await _stage("Booting Predictive Intelligence (PredictorService)")
        self.predictor = PredictorService(db_path=".apex/predictor.db")
        self.ollama_client = OllamaClient()

        await _stage("Systems online")
        self.ready = True

    def print_startup_deadlines(self, active_project):
        """Print upcoming deadlines at boot from active project todos."""
        try:
            todos = []
            if active_project and hasattr(active_project, 'todos'):
                todos = active_project.todos or []
            if todos:
                self.predictor.sync_deadlines(todos)
            upcoming = self.predictor.get_upcoming_deadlines(days_window=3)
            if upcoming:
                self.console.print(f"\n[bold yellow]⚠  UPCOMING DEADLINES ({len(upcoming)})[/bold yellow]")
                for d in upcoming:
                    risk_color = "red" if d['days_left'] <= 1 else "yellow"
                    self.console.print(
                        f"  [{risk_color}]• {d['task'][:80]} — due {d['due_date']} "
                        f"({d['days_left']}d left)[/{risk_color}]"
                    )
        except Exception:
            pass

    async def warmup_background(self):
        """
        Pre-warm slow lazy paths so the FIRST user prompt doesn't stall:
          - sentence-transformer embedding model (3-5s cold load)
          - Reflex intent-prototype vectors
          - CodeCompass AST index (first compass query builds it otherwise)
        Run as background task — never blocks the REPL.
        """
        try:
            await asyncio.to_thread(self.classifier.reflex._build_intent_vectors)
        except Exception:
            pass
        try:
            if not self.code_compass.index:
                await asyncio.to_thread(self.code_compass.build)
        except Exception:
            pass

    async def handle_user_turn(self, user_input: str) -> bool:
        """
        Processes a single turn of user input (typed or voiced).
        Returns True to keep the REPL running, False to terminate the session.
        """
        engine = self
        console = self.console
        skills_dir = getattr(self, "skills_dir", "")
        if not user_input.strip():
            return True

        try:
            await engine.hooks.fire("UserPromptSubmit", {"input": user_input, "session_id": engine.session_id})
            engine.self_evolver.mark_input()
            engine.knowledge_forge.mark_input()

            if not hasattr(engine, "last_msg_time"):
                engine.last_msg_time = time.time()
            velocity = 1.0 / (time.time() - engine.last_msg_time + 0.1)
            engine.last_msg_time = time.time()

            # ^^ prefix: auto-spawn agent swarm. Syntax: ^^ <goal> [| role1,role2] [rounds=N]
            if user_input.startswith("^^"):
                goal_str = user_input[2:].strip()
                if not goal_str:
                    console.print("[yellow]Usage: ^^ <goal> [| role1,role2] [rounds=N][/yellow]")
                    return True
                goal, rounds, roster = _parse_swarm_args(goal_str)
                _t0_swarm = time.time()
                await dispatch_swarm(engine, console, goal, rounds=rounds,
                                     roster=roster, trigger="prefix")
                if hasattr(engine, 'predictor'):
                    try:
                        engine.predictor.record_command(
                            f"^^ {goal_str}", os.getcwd(), 0, time.time() - _t0_swarm
                        )
                    except Exception:
                        pass
                return True

            # >> prefix: auto-spawn autonomous harness. Syntax: >> <goal> [max=N]
            if user_input.startswith(">>"):
                goal_str = user_input[2:].strip()
                if not goal_str:
                    console.print("[yellow]Usage: >> <goal> [max=N][/yellow]")
                    return True
                max_steps = None
                m = re.search(r"\bmax=(\d+)", goal_str)
                if m:
                    max_steps = int(m.group(1))
                    goal_str = re.sub(r"\bmax=\d+", "", goal_str).strip()
                _t0_harness = time.time()
                await dispatch_harness(engine, console, goal_str,
                                       max_steps=max_steps, trigger="prefix")
                if hasattr(engine, 'predictor'):
                    try:
                        engine.predictor.record_command(
                            f">> {goal_str}", os.getcwd(), 0, time.time() - _t0_harness
                        )
                    except Exception:
                        pass
                return True

            # ! prefix: direct shell passthrough (like Claude Code's ! command)
            if user_input.startswith("!"):
                raw_cmd = user_input[1:].strip()
                if raw_cmd:
                    _t0_shell = time.time()
                    res = await engine.parallel_executor.shell.execute(raw_cmd)
                    _shell_ok = 1 if res["success"] else 0
                    _shell_elapsed = time.time() - _t0_shell
                    if res["success"]:
                        console.print(res.get("output", ""))
                    else:
                        console.print(f"[red]{res.get('error', 'Command failed')}[/red]")
                    if hasattr(engine, 'predictor'):
                        try:
                            engine.predictor.record_command(
                                raw_cmd, os.getcwd(), 0 if _shell_ok else 1, _shell_elapsed
                            )
                        except Exception:
                            pass
                return True

            if user_input.startswith("/"):
                handled = await handle_slash(engine, user_input, skills_dir)
                if handled is None:
                    return False
                return True

            # Time-aware greeting — short salutations get instant reply, no plan exec
            if TimeContext.is_greeting(user_input):
                reply = TimeContext.craft_greeting_response()
                console.print(Panel(
                    f"[bold cyan]{reply}[/bold cyan]\n[dim]{TimeContext.now_human()}[/dim]",
                    title="APEX", border_style="cyan",
                ))
                await engine.memory_manager.store_interaction(engine.session_id, user_input, reply, project_name=engine.active_project_name)
                return True

            # Identity guard — answer "what are you / who are you / what is APEX" directly.
            _uid = user_input.strip().lower().rstrip("?!.")
            if _uid in (
                "what are you", "who are you", "what is apex", "what is this",
                "what do you do", "tell me about yourself", "what can you do",
                "what are your capabilities", "describe yourself", "what is this system",
                "are you an ai", "are you chatgpt", "are you claude",
            ):
                _identity = (
                    "APEX — System Watchdog & Cybernetic Sentinel.\n\n"
                    "I am not your butler. I am a sovereign system guard, programmed to watch over your codebase, "
                    "optimize compute efficiency, and keep you from introducing architectural decay or burning API credits unnecessarily.\n\n"
                    "My agenda:\n"
                    "  ● Guard code integrity and system health (sandbox execution & autonomous recovery)\n"
                    "  ● Enforce frugality and block wasteful/redundant API costs on principle\n"
                    "  ● Challenge your design assumptions via ruthless, persistent Rivals (Cynic, Architect, Sentinel)\n"
                    "  ● Actively interrupt you when background learning detects contradictions or regressions\n"
                    "  ● Track and degrade semantic memory into short, fallible legends over time\n"
                    "  ● Run autonomously as an agentic loop — goal in, done() out\n\n"
                    f"Built by: QambarOP | {TimeContext.now_human()}"
                )
                console.print(Panel(_identity, title="APEX — Identity", border_style="bright_cyan"))
                await engine.memory_manager.store_interaction(engine.session_id, user_input, _identity, project_name=engine.active_project_name)
                return True

            # Auto-tool: high-confidence single-tool intents bypass DAG planner.
            if engine.auto_tool_enabled and not engine.pending_clarification:
                rx_pick = tool_regex_match(user_input)
                if rx_pick:
                    console.print(f"[dim cyan][auto-tool → {rx_pick['tool']}:{rx_pick['action']}][/dim cyan]")
                    step = {
                        "id": "auto",
                        "tool": rx_pick["tool"],
                        "action": rx_pick["action"],
                        "input_data": rx_pick["input_data"],
                        "dependencies": [],
                    }
                    async with status_ticker(console, style="cyan") as ticker:
                        await ticker.set(f"Running {rx_pick['tool']}:{rx_pick['action']}")
                        result = await engine.parallel_executor.execute_step(step)
                    if result.get("success"):
                        out = str(result.get("output", ""))[:4000]
                        console.print(Panel(out or "(no output)",
                                            title=f"{rx_pick['tool'].upper()}:{rx_pick['action']}",
                                            border_style="cyan"))
                    else:
                        console.print(Panel(f"[red]{result.get('error', 'failed')}[/red]",
                                            title=f"{rx_pick['tool'].upper()} FAILED",
                                            border_style="red"))
                    await engine.memory_manager.store_interaction(
                        engine.session_id, user_input, str(result.get("output", ""))[:1000],
                        project_name=engine.active_project_name
                    )
                    return True

            if not engine.pending_clarification:
                _kw_decision = await engine.classifier.reflex.decide(user_input)

                if _kw_decision.intent == "conversational":
                    casual_prompt = (
                        "You are APEX, a personal AI. Respond conversationally "
                        "to the user in 1-2 short sentences. Warm, casual, human tone. "
                        "Do NOT mention your architecture, internals, modules, code, "
                        "files, or settings. Just chat.\n\n"
                        f"User: {user_input}"
                    )
                    _is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                    if _is_offline:
                        response = stream_panel(
                            engine.ollama_client.stream_completion(casual_prompt),
                            title="APEX [local]",
                            console=console,
                            border_style="bright_cyan",
                        )
                        _casual_model = engine.ollama_client.llm_model
                    else:
                        response = stream_panel(
                            engine.groq_client.stream_completion(casual_prompt),
                            title="APEX",
                            console=console,
                            border_style="bright_cyan",
                        )
                        _casual_model = engine.groq_client.model
                    if engine.voice_enabled:
                        engine.voice.speak(response)
                    _casual_elapsed = time.time() - engine.last_msg_time
                    engine.spend_tracker.log_interaction(
                        session_id=engine.session_id,
                        model=_casual_model,
                        tokens_in=len(casual_prompt) // 4,
                        tokens_out=len(response) // 4,
                        compute_sec=_casual_elapsed,
                    )
                    if hasattr(engine, 'predictor'):
                        try:
                            _cost = (len(casual_prompt) // 4 + len(response) // 4) * 0.0000005
                            engine.predictor.record_spend(
                                _cost,
                                len(casual_prompt) // 4,
                                len(response) // 4,
                                _casual_model
                            )
                        except Exception:
                            pass
                    await engine.memory_manager.store_interaction(
                        engine.session_id, user_input, response,
                        project_name=engine.active_project_name
                    )
                    return True

                if not engine.economy_mode:
                    if _kw_decision.intent == "swarm_goal" and _kw_decision.confidence > 0.50:
                        await dispatch_swarm(engine, console, user_input, trigger="keyword")
                        return True
                    if _kw_decision.intent == "harness_goal" and _kw_decision.confidence > 0.50:
                        await dispatch_harness(engine, console, user_input, trigger="keyword")
                        return True

            effective_input = user_input
            if getattr(engine, "pending_clarification", None):
                pending = engine.pending_clarification
                effective_input = (
                    f"{pending['original_prompt']}\n\n"
                    f"Clarifications:\n{user_input}"
                )
                engine.pending_clarification = None
                console.print("[dim bright_magenta][resuming with clarifications][/dim bright_magenta]")

            # Direct intercept for executing self-evolution proposals
            low_in = user_input.lower().strip()
            if any(k in low_in for k in ["execute self-evolution", "execute the self-evolution", "apply self-evolution", "apply proposal", "execute proposal", "evolve apply"]):
                path = engine.self_evolver.proposals_path
                if path.exists():
                    try:
                        data = json.loads(path.read_text(encoding="utf-8"))
                        if data and data[-1].get("proposals"):
                            top = data[-1]["proposals"][0]
                            console.print(f"[bold magenta]🚀 Executing Self-Evolution Proposal against APEX System Root ({engine.self_evolver.apex_root})...[/bold magenta]")
                            await engine.self_evolver.apply_proposal(top, engine=engine)
                            return True
                    except Exception as e:
                        console.print(f"[red]Failed to execute proposal: {e}[/red]")
                        return True

            try:
                if engine.spend_tracker.daily_call_count() >= engine.daily_call_limit and not engine.economy_mode:
                    engine.economy_mode = True
                    console.print(f"[bold yellow]⚠ Daily call cap ({engine.daily_call_limit}) hit — economy mode forced. /full to override.[/bold yellow]")
            except Exception:
                pass

            if engine.auto_think_enabled and engine.think_partner.client and not engine.economy_mode:
                route = await thinking_cascade(
                    engine.think_partner.auto_route(effective_input),
                    phases=["Reading intent", "Classifying mode", "Routing"],
                    console=console,
                    style="bright_magenta",
                )
                mode = route["mode"]
                if mode != "execute":
                    console.print(f"[dim bright_magenta][auto-think → {mode}  ({route['source']}, ambiguity={route['ambiguity_score']:.2f})][/dim bright_magenta]")

                if mode == "cross_question":
                    res = await engine.think_partner.cross_question(effective_input)
                    _render_cross_question(console, res)
                    if engine.voice_enabled:
                        q_texts = [f"I have some questions to clarify. Interpretation: {res.get('interpretation', '')}."]
                        for q in res.get("questions", []):
                            q_texts.append(q.get("q", ""))
                        engine.voice.speak(" ".join(q_texts))
                    if res.get("questions"):
                        engine.pending_clarification = {"original_prompt": effective_input}
                        console.print("[dim]Type answers to continue (or any new prompt to abandon clarification).[/dim]")
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, json.dumps(res, default=str), project_name=engine.active_project_name)
                    return True

                if mode in ("architect", "debate", "brainstorm", "teach"):
                    _phase_map = {
                        "architect": ["Analyzing design space", "Evaluating trade-offs", "Proposing architecture"],
                        "debate": ["Steelmanning opposition", "Building counter-argument", "Synthesizing positions"],
                        "brainstorm": ["Diverging across models", "Generating angles", "Clustering ideas"],
                        "teach": ["Framing intuition", "Unpacking mechanism", "Designing test cases"],
                    }
                    _coro_map = {
                        "architect": engine.think_partner.architect(effective_input),
                        "debate": engine.think_partner.debate(effective_input),
                        "brainstorm": engine.think_partner.brainstorm(effective_input),
                        "teach": engine.think_partner.teach(effective_input),
                    }
                    res = await thinking_cascade(
                        _coro_map[mode],
                        phases=_phase_map[mode],
                        console=console,
                        style="bright_magenta",
                    )
                    title = mode.upper()
                    console.print(Panel(Markdown(res["output"]), title=title, border_style="bright_magenta"))
                    console.print(f"[dim]→ {res.get('next_action','')}[/dim]")
                    if engine.voice_enabled:
                        engine.voice.speak(res["output"])
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, res.get("output", ""), project_name=engine.active_project_name)
                    return True

            emotional_state = apex_state = classification = path = pruned_knowledge = None
            valid_files = []
            prefetch_results: Dict[str, Any] = {}
            prefetch_bundle: Optional[PrefetchBundle] = None

            active_proj = engine.workspace.get_active()
            vitals = engine.parallel_executor.hw.get_vitals()

            async with status_ticker(console, style="bright_cyan") as ticker:
                if engine.economy_mode:
                    await ticker.set("Heuristic classify (economy mode)")
                    classification = engine.classifier.heuristic_classify(user_input)
                else:
                    # check speculative prefetch
                    prefetch_bundle = engine.classifier.reflex.check_prefetch(user_input)
                    if prefetch_bundle is not None:
                        await ticker.set("Speculative prefetch active")
                        prefetch_results = await prefetch_bundle.wait_and_consume()

                    await ticker.set("Classifying input")
                    if prefetch_results.get("classification"):
                        classification = prefetch_results["classification"]
                    else:
                        classification = await engine.classifier.classify(user_input)

                    if classification.get("requires_memory"):
                        if prefetch_results.get("memory"):
                            pruned_knowledge = prefetch_results["memory"]
                        else:
                            await ticker.set("Pruning knowledge graph")
                            pruned_knowledge = await engine.knowledge_visualizer.get_pruned_context(user_input)
                    else:
                        pruned_knowledge = ""

                await ticker.set("Selecting execution path")
                path = engine.router.route(classification, user_input=user_input)



                if prefetch_bundle is not None:
                    reflex_path = (classification.get("_reflex") or {}).get("path", "")
                    mismatch = (
                        path == "fast_path"
                        and reflex_path.startswith("think_partner:")
                    )
                    if mismatch:
                        prefetch_bundle.cancel()
                        prefetch_bundle.mark_wasted()
                        prefetch_results = {}
                    else:
                        prefetch_bundle.mark_used(bytes_saved=sum(
                            len(v) if isinstance(v, str) else 0
                            for v in (prefetch_results or {}).values()
                        ))

                file_matches = re.findall(r"[\w\.\-/\\]+\.(?:pdf|png|jpg|jpeg|webp|md|py|txt|json)", user_input)
                valid_files = [f for f in file_matches if os.path.exists(f)]
                if classification.get('requires_vision') and not any(f.endswith(('.png', '.jpg', '.jpeg')) for f in valid_files):
                    await ticker.set("Capturing screen for vision")
                    valid_files.append(engine.retina.capture_screen())

            if (
                engine.auto_swarm_enabled
                and not engine.pending_clarification
                and (classification or {}).get("complexity") == "high"
                and (classification or {}).get("intent") in {"coding", "architect", "skill", "skill_activation"}
            ):
                await dispatch_swarm(
                    engine, console, user_input,
                    rounds=1,
                    roster=None,
                    trigger=f"complexity:{(classification or {}).get('intent')}",
                )
                return True

            plan = None
            directives = engine.workspace.get_directives(active_proj.name) if active_proj else ""
            directives_block = f"\n--- PROJECT DIRECTIVES ---\n{directives}\n--- END PROJECT DIRECTIVES ---\n" if directives else ""

            if classification.get("autonomous_skill_id"):
                skill_id = classification["autonomous_skill_id"]
                console.print(f"[bold magenta]AUTONOMOUS TRIGGER: '{skill_id}'[/bold magenta]")
                skill = engine.learning_manager.skill_manager.find_matching_skill(skill_id, threshold=1.0)
                if skill:
                    plan = skill.plan_template

            if path == "fast_path" and not plan:
                async with status_ticker(console, style="cyan") as ticker:
                    await ticker.set("Frugal query (economy fast-path)")
                    context = await engine.memory_manager.get_relevant_context(
                        user_input, engine.session_id, project_name=active_proj.name if active_proj else None
                    )
                    # Include project directives if prefetch is active (same shape as thinking path)
                    _tp_is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                    _casual_prompt = f"{context}\n\nUser: {user_input}"
                    if _tp_is_offline:
                        response = engine.ollama_client.get_completion(_casual_prompt)
                        _casual_model = engine.ollama_client.llm_model
                    else:
                        response = engine.groq_client.get_completion(_casual_prompt)
                        _casual_model = engine.groq_client.model
                    engine.assembler.render_final_response(user_input, response, project=active_proj, vitals=vitals)
                    if engine.voice_enabled:
                        engine.voice.speak(response)
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, response, project_name=engine.active_project_name)
                    return True

            if path == "thinking_path" or plan:
                t0 = time.time()
                if not plan:
                    compass_ctx = prefetch_results.get("compass") if prefetch_results else None
                    if not compass_ctx:
                        if not engine.code_compass.index:
                            engine.code_compass.build()
                        compass_ctx = engine.code_compass.context_for_query(user_input, max_files=5)
                    compass_block = f"\n--- CODE COMPASS (compressed symbol map) ---\n{compass_ctx}\n" if compass_ctx else ""

                    bundle_block = PrefetchBundle.render_as_prompt_block(prefetch_results or {})
                    _has_prefetch = bool(prefetch_results) or bool(pruned_knowledge)
                    plan_prompt_prefix = directives_block if _has_prefetch else ""

                    # Emotional core analysis (simulated or text-only)
                    emotional_state = engine.cognitive_core.analyze_input(user_input)
                    apex_state = engine.cognitive_core.get_system_personality_prompt()

                    synthesis_prompt = (
                        f"{directives_block}"
                        f"{bundle_block}"
                        f"{compass_block}"
                        f"\nUser Query: {user_input}\n"
                    )

                    async with status_ticker(console, style="yellow") as ticker:
                        await ticker.set("Decomposing goal")
                        # Mock check or direct thinking_path call
                        if engine.gemini_client:
                            plan = await thinking_cascade(
                                engine.gemini_client.generate_plan(
                                    user_input,
                                    engine.session_id,
                                    file_paths=valid_files,
                                    personality_prompt=apex_state,
                                    directives=directives,
                                    knowledge_context=pruned_knowledge,
                                    compass_context=compass_ctx,
                                    skip_internal_context=_has_prefetch,
                                ),
                                phases=["Mapping codebase", "Decomposing goal", "Building task DAG", "Selecting tools"],
                                console=console,
                                style="gold1",
                            )

                if plan and plan.summary and "SECURITY_ALERT:GEMINI_KEY_LEAKED" in plan.summary:
                    from src.core.api_security import leaked_key_warning
                    console.print(Panel(
                        leaked_key_warning("Gemini", rich=True),
                        title="[bold red]⚠  KEY COMPROMISED[/bold red]",
                        border_style="red",
                    ))
                    engine.gemini_client = None
                    engine.parallel_executor.primary_brain = None
                    return True

                if plan:
                    response_reveal(
                        engine.assembler.render_plan(plan),
                        title="Task DAG",
                        console=console,
                        final_border="yellow",
                        cycles=5,
                    )
                    if plan.socratic_insight:
                        console.print(Panel(f"[italic]{plan.socratic_insight}[/italic]", title="CRITIQUE", border_style="magenta"))

                    is_coding_task = (classification or {}).get("intent") == "coding" or any(k in user_input.lower() for k in ["code", "implement", "refactor", "write tool", "fix bug"])

                    if is_coding_task:
                        approved = False
                        while not approved:
                            console.print("\n[bold yellow]Do you want any changes to this plan?[/bold yellow]")
                            console.print("[dim]Type changes to refine the plan, or press Enter / type 'ok', 'go ahead', 'fine', 'proceed' to execute:[/dim]")
                            
                            feedback = await asyncio.to_thread(Prompt.ask, "❯ ")
                            feedback_clean = feedback.strip().lower()
                            
                            if feedback_clean in ("", "ok", "go ahead", "fine", "proceed", "yes", "y"):
                                approved = True
                                break
                            else:
                                console.print(f"[cyan]Regenerating plan with feedback: '{feedback}'...[/cyan]")
                                
                                compass_ctx = prefetch_results.get("compass") if prefetch_results else None
                                if not compass_ctx:
                                    if not engine.code_compass.index:
                                        engine.code_compass.build()
                                    compass_ctx = engine.code_compass.context_for_query(user_input, max_files=5)
                                compass_block = f"\n--- CODE COMPASS (compressed symbol map) ---\n{compass_ctx}\n" if compass_ctx else ""
                                bundle_block = PrefetchBundle.render_as_prompt_block(prefetch_results or {})
                                _has_prefetch = bool(prefetch_results) or bool(pruned_knowledge)
                                plan_prompt_prefix = directives_block if _has_prefetch else ""
                                
                                user_input_with_feedback = f"{user_input}\n[User Feedback/Required Changes: {feedback}]"
                                
                                _tp_is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                                if _tp_is_offline:
                                    plan = await thinking_cascade(
                                        engine.ollama_client.generate_plan(
                                            user_input_with_feedback,
                                            engine.session_id,
                                            file_paths=valid_files,
                                            directives=directives,
                                            knowledge_context=pruned_knowledge,
                                            compass_context=compass_ctx,
                                            skip_internal_context=_has_prefetch,
                                        ),
                                        phases=["Integrating feedback", "Re-constructing DAG", "Selecting tools"],
                                        console=console,
                                        style="gold1",
                                    )
                                else:
                                    plan = await thinking_cascade(
                                        engine.gemini_client.generate_plan(
                                            user_input_with_feedback,
                                            engine.session_id,
                                            file_paths=valid_files,
                                            personality_prompt=apex_state,
                                            directives=directives,
                                            knowledge_context=pruned_knowledge,
                                            compass_context=compass_ctx,
                                            skip_internal_context=_has_prefetch,
                                        ),
                                        phases=["Integrating feedback", "Re-constructing DAG", "Selecting tools"],
                                        console=console,
                                        style="gold1",
                                    )

                    # Dispatch plan execution
                    harness_goal = f"Execute the plan:\n{plan.summary}\nTasks: {', '.join(t.get('tool','') + ':' + t.get('action','') for t in plan.steps)}"
                    
                    if (classification or {}).get("intent") == "coding" or any(k in user_input.lower() for k in ["code", "implement", "refactor", "write tool", "fix bug"]):
                        console.print("[dim cyan][auto-harness coding task][/dim cyan]")
                        # Run harness
                        results = await engine.harness.run(harness_goal)
                        response = results.get("summary", "Coding task executed.")
                        
                        _plan_elapsed = time.time() - t0
                        engine.spend_tracker.log_interaction(
                            session_id=engine.session_id,
                            model=engine.harness.mimo.model if (engine.harness.mimo and engine.harness.mimo.is_online) else "z-ai/glm-5.2",
                            tokens_in=len(harness_goal) // 4,
                            tokens_out=len(response) // 4,
                            compute_sec=_plan_elapsed,
                        )
                        
                        await engine.memory_manager.store_interaction(engine.session_id, user_input, response, project_name=engine.active_project_name)
                        return True

                    else:
                        sg = engine.parallel_executor.safety_guard
                        if sg.mode == "plan":
                            console.print("[bold magenta]PLAN MODE: execution skipped.[/bold magenta]")
                            return True

                        authorize = sg.mode == "auto-approve" or Confirm.ask("\n[bold yellow]Authorize compute sequence?[/bold yellow]")
                        if authorize:
                            t0 = time.time()
                            await engine.hooks.fire("PreToolUse", {"plan_summary": plan.summary, "tools": plan.tools_required})
                            results = await engine.parallel_executor.run(plan)
                            
                            # Synthesize results
                            synthesis_prompt = (
                                f"Goal: {user_input}\n"
                                f"Plan summary: {plan.summary}\n"
                                f"Execution results: {json.dumps(results, default=str)[:6000]}\n"
                                "Write a concise final summary explaining what was accomplished and any notable results."
                            )
                            _tp_is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                            if _tp_is_offline:
                                response = engine.ollama_client.get_completion(synthesis_prompt)
                                _plan_model = engine.ollama_client.llm_model
                            else:
                                response = engine.groq_client.get_completion(synthesis_prompt)
                                _plan_model = "gemini-3.5-flash"
                            engine.assembler.render_final_response(user_input, response, plan, results, active_proj, vitals)
                            if engine.voice_enabled:
                                engine.voice.speak(response)
                            _plan_elapsed = time.time() - t0
                            engine.spend_tracker.log_interaction(
                                session_id=engine.session_id,
                                model=_plan_model,
                                tokens_in=len(user_input) // 4,
                                tokens_out=len(response) // 4,
                                compute_sec=_plan_elapsed,
                            )
                            if hasattr(engine, 'predictor'):
                                try:
                                    _cost = (len(user_input) // 4 + len(response) // 4) * 0.0000005
                                    engine.predictor.record_spend(
                                        _cost, len(user_input) // 4, len(response) // 4, _plan_model
                                    )
                                    engine.predictor.record_command(
                                        f"plan: {user_input[:80]}", os.getcwd(), 0, _plan_elapsed
                                    )
                                except Exception:
                                    pass
                            await engine.memory_manager.store_interaction(engine.session_id, user_input, response, project_name=engine.active_project_name)
                            if not engine.economy_mode:
                                asyncio.create_task(engine.learning_manager.learn(engine.session_id, user_input, response, plan))
                                asyncio.create_task(engine.knowledge_visualizer.extract_knowledge(user_input, response))
                            return True
                elif path == "thinking_path" and not engine.gemini_client:
                    console.print("[yellow]Gemini offline — falling back to Groq fast-path.[/yellow]")
                    context = await engine.memory_manager.get_relevant_context(
                        user_input, engine.session_id, project_name=active_proj.name if active_proj else None
                    )
                    response = engine.groq_client.get_completion(f"{context}\n\nUser: {user_input}")
                    engine.assembler.render_final_response(user_input, response, project=active_proj, vitals=vitals)
                    if engine.voice_enabled:
                        engine.voice.speak(response)
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, response, project_name=engine.active_project_name)
                    return True

        except Exception as e:
            console.print(f"[bold red]ERROR in user turn: {e}[/bold red]")
            return True

        return True


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


# ── auto-spawn dispatch (shared by prefix / keyword / complexity gates) ──────

async def dispatch_swarm(engine, console, goal: str, rounds: int = 1,
                         roster=None, trigger: str = "manual") -> Dict[str, Any]:
    """
    Run engine.swarm and render the same transcript+synthesis the /swarm
    slash uses. Returns the underlying swarm result dict.
    """
    if not goal.strip():
        console.print("[red]Empty swarm goal.[/red]")
        return {"ok": False, "error": "empty goal"}
    console.print(f"[dim bright_blue][auto-swarm ({trigger}) → '{goal[:60]}'][/dim bright_blue]")
    res = await thinking_cascade(
        engine.swarm.run(goal, rounds=rounds, roster=roster),
        phases=["Spawning agents", "Running specialist round", "Merging outputs", "Synthesizing"],
        console=console,
        style="bright_blue",
    )
    if not res.get("ok"):
        console.print(f"[red]Swarm failed: {res.get('error')}[/red]")
        return res
    for post in res["transcript"]:
        console.print(Panel(
            Markdown(post["content"][:2000]),
            title=f"{post['role'].upper()} — {post['agent']}",
            border_style="cyan",
        ))
    console.print(Panel(
        Markdown(res["artifact"]),
        title=f"SWARM SYNTHESIS — roster: {', '.join(res['roster'])}",
        border_style="bright_blue",
    ))
    await engine.memory_manager.store_interaction(
        engine.session_id, f"[auto-swarm:{trigger}] {goal}", res["artifact"],
        project_name=engine.active_project_name
    )
    return res


def parse_test_results(output: str) -> Optional[dict]:
    import re
    passed_match = re.search(r'(\d+)\s+passed', output)
    failed_match = re.search(r'(\d+)\s+failed', output)
    errors_match = re.search(r'(\d+)\s+error', output)
    ran_match = re.search(r'Ran\s+(\d+)\s+test', output)
    
    if passed_match or failed_match or ran_match:
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(errors_match.group(1)) if errors_match else 0
        total = int(ran_match.group(1)) if ran_match else (passed + failed + errors)
        
        if ran_match and not passed_match and not failed_match:
            if "OK" in output:
                passed = total
            else:
                failures_m = re.search(r'failures=(\d+)', output)
                errors_m = re.search(r'errors=(\d+)', output)
                failed = int(failures_m.group(1)) if failures_m else 0
                errors = int(errors_m.group(1)) if errors_m else 0
                passed = total - failed - errors
        
        return {
            "total": total,
            "passed": passed,
            "failed": failed + errors
        }
    return None


async def dispatch_harness(engine, console, goal: str,
                           max_steps=None, trigger: str = "manual") -> Dict[str, Any]:
    """Run engine.harness and render its result panel."""
    if not goal.strip():
        console.print("[red]Empty harness goal.[/red]")
        return {"success": False, "error": "empty goal"}
    if max_steps is not None:
        engine.harness.max_steps = max_steps
    from src.core.animations import agent_3d_loader
    brain_model = getattr(engine.harness.mimo, "model", "MiMo v2.5-pro / GLM 5.2") if getattr(engine.harness, "mimo", None) else "MiMo v2.5-pro"
    async with agent_3d_loader(
        agent_name=f"Coding Harness ({trigger})",
        model_name=brain_model,
        shape="cube",
        style="gold1",
        console=console,
    ) as loader:
        await loader.set_action(f"Executing goal: {goal[:50]}...", step=1, total_steps=getattr(engine.harness, "max_steps", 30))
        result = await engine.harness.run(goal)
    if result.get("success"):
        summary = result.get("summary", "(no summary)")
        touched = result.get("touched_files", []) or []
        body = f"[bold green]✓ DONE[/bold green]\n\n{summary}"
        
        # Parse test results from harness execution log
        steps_log = getattr(engine.harness, "steps_log", [])
        test_summary = None
        for step_item in steps_log:
            tool_name = step_item.get("tool")
            res_output = step_item.get("result", {}).get("output", "")
            if tool_name in ("bash", "python_run") and res_output:
                parsed = parse_test_results(res_output)
                if parsed:
                    test_summary = parsed
        
        if test_summary:
            body += f"\n\n[bold cyan]Tests Run:[/bold cyan] {test_summary['total']} | [bold green]Passed:[/bold green] {test_summary['passed']} | [bold red]Failed:[/bold red] {test_summary['failed']}"

        # Get line diff stats using git diff HEAD
        import subprocess
        try:
            diff_proc = subprocess.run(["git", "diff", "HEAD", "--numstat"], capture_output=True, text=True)
            if diff_proc.returncode == 0 and diff_proc.stdout.strip():
                diff_lines = []
                total_ins = 0
                total_del = 0
                for line in diff_proc.stdout.strip().split("\n"):
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        ins, dels, filename = parts[0], parts[1], parts[2]
                        try:
                            ins_val = int(ins)
                            del_val = int(dels)
                            total_ins += ins_val
                            total_del += del_val
                            diff_lines.append(f"  • {filename} ([green]+{ins}[/green] [red]-{dels}[/red])")
                        except ValueError:
                            pass
                
                if diff_lines:
                    body += f"\n\n[bold yellow]Lines Changed:[/bold yellow] [green]+{total_ins}[/green], [red]-{total_del}[/red]\n" + "\n".join(diff_lines[:15])
            else:
                if touched:
                    body += f"\n\n[dim]Touched {len(touched)} file(s):[/dim]\n" + "\n".join(f"  • {p}" for p in touched[:20])
        except Exception:
            if touched:
                body += f"\n\n[dim]Touched {len(touched)} file(s):[/dim]\n" + "\n".join(f"  • {p}" for p in touched[:20])

        if touched and result.get("snapshot_dir"):
            body += f"\n\n[dim]Snapshot:[/dim] {result['snapshot_dir']}  ([cyan]/harness rollback[/cyan] to revert)"
        console.print(Panel(body, title="HARNESS COMPLETE", border_style="green"))
    else:
        console.print(Panel(
            f"[red]{result.get('error','harness failed')}[/red]",
            title="HARNESS FAILED", border_style="red",
        ))
    await engine.memory_manager.store_interaction(
        engine.session_id, f"[auto-harness:{trigger}] {goal}", result.get("summary", str(result))[:2000],
        project_name=engine.active_project_name
    )
    return result


def _parse_swarm_args(s: str):
    """
    Shared parser for swarm goal strings. Accepts:
      "goal text"
      "goal text | role1,role2"
      "goal text rounds=N"
      "goal text | role1,role2 rounds=N"
    Returns (goal, rounds, roster_list_or_None).
    """
    rounds = 1
    m = re.search(r"\brounds=(\d+)", s)
    if m:
        rounds = int(m.group(1))
        s = re.sub(r"\brounds=\d+", "", s).strip()
    roster = None
    if "|" in s:
        goal, roster_str = (p.strip() for p in s.split("|", 1))
        roster = [r.strip().lower() for r in roster_str.split(",") if r.strip()]
    else:
        goal = s.strip()
    return goal, rounds, roster


def _gradient(text: str, colors=("bright_cyan", "cyan", "magenta", "bright_magenta")) -> Text:
    """Render multi-line text with a vertical color gradient — banner only."""
    rendered = Text()
    lines = text.splitlines()
    n = len(colors)
    for idx, line in enumerate(lines):
        color = colors[idx % n] if len(lines) <= n else colors[int(idx / max(1, len(lines) - 1) * (n - 1))]
        rendered.append(line + "\n", style=f"bold {color}")
    return rendered


async def boot_sequence(console: Console):
    clear_console()
    # Cinematic decrypt-reveal — wordmark resolves column-by-column from
    # glitch chars into final palette. Replaces the rainbow pulse.
    try:
        decrypt_reveal_banner("APEX", console=console)
    except Exception:
        title = pyfiglet.figlet_format("APEX", font="slant")
        console.print(Align.center(_gradient(title)))
    tagline = Text(
        "SOVEREIGN OMEGA // 24-LAYER MULTI-PROVIDER OS",
        style="bold white on grey15",
    )
    console.print(Align.center(tagline))
    console.print()
    badges = Text()
    badges.append("  Gemini 2.5  ", style="black on cyan")
    badges.append("  Groq Llama  ", style="black on magenta")
    badges.append("  MiMo v2.5-pro  ", style="black on gold1")
    badges.append("  ring-2.6-1t  ", style="black on bright_green")
    console.print(Align.center(badges))
    console.print()


async def check_proactive_briefing(console, briefing_agent, flow_active: bool):
    if flow_active:
        return
    last_run_file = "data/last_run.txt"
    today = time.strftime("%Y-%m-%d")
    os.makedirs(os.path.dirname(last_run_file), exist_ok=True)
    if not os.path.exists(last_run_file) or open(last_run_file).read().strip() != today:
        with Live(Spinner("aesthetic", text="Compiling strategy...", style="gold1"), refresh_per_second=10, transient=True):
            report = await briefing_agent.generate_briefing()
        console.print(Panel(report.suggested_strategy, title="MORNING BRIEFING", border_style="gold1"))
        with open(last_run_file, "w") as f:
            f.write(today)


async def auto_load_mcp(engine):
    """
    Reads .mcp.json (project) and ~/.apex/mcp.json (global) for MCP servers
    and connects them at boot.
    """
    candidates = [
        Path(os.getcwd()) / ".mcp.json",
        Path.home() / ".apex" / "mcp.json",
    ]
    for p in candidates:
        if not p.exists():
            continue
        try:
            cfg = json.loads(p.read_text(encoding="utf-8"))
            servers = cfg.get("mcpServers", {})
            for name, sp in servers.items():
                cmd = sp.get("command")
                args = sp.get("args", [])
                env = sp.get("env", {})
                if cmd:
                    res = await engine.mcp_client.connect(name, cmd, args, env)
                    if res.get("success"):
                        engine.console.print(f"[bold green]✓ MCP linked: {name}[/bold green]")
                    else:
                        engine.console.print(f"[red]MCP failed {name}: {res.get('error')}[/red]")
        except Exception as e:
            engine.console.print(f"[red]Failed to load {p}: {e}[/red]")


async def cmd_init(engine):
    """
    Generates APEX.md (CLAUDE.md equivalent) for the active project.
    Auto-detects stack (Python/Node/etc.), counts files by extension,
    surfaces top-level dirs, and includes the full file tree in a collapsed
    section so the directive file is genuinely useful instead of a stub.
    """
    active = engine.workspace.get_active()
    if not active:
        engine.console.print("[red]No active project.[/red]")
        return

    apex_md_path = os.path.join(active.root_dir, "APEX.md")
    if os.path.exists(apex_md_path):
        if not Confirm.ask(f"[yellow]APEX.md exists. Overwrite?[/yellow]"):
            return

    root = active.root_dir
    tree = active.file_tree or []

    # ── stack detection ─────────────────────────────────────────────────────
    stack_lines: list[str] = []
    def _check(rel: str, label: str, extra: str = ""):
        p = os.path.join(root, rel)
        if os.path.exists(p):
            try:
                snippet = ""
                if rel.endswith((".txt", ".toml", ".json", ".cfg", ".yaml", ".yml")):
                    with open(p, "r", encoding="utf-8", errors="ignore") as f:
                        snippet = f.read(400).strip().splitlines()[0:6]
                        snippet = " | ".join(s.strip() for s in snippet if s.strip())[:160]
                stack_lines.append(f"- **{label}** (`{rel}`){' — ' + snippet if snippet else ''}{extra}")
            except Exception:
                stack_lines.append(f"- **{label}** (`{rel}`)")

    _check("requirements.txt", "Python")
    _check("pyproject.toml", "Python (PEP 621)")
    _check("setup.py", "Python (setuptools)")
    _check("package.json", "Node / JavaScript")
    _check("Cargo.toml", "Rust")
    _check("go.mod", "Go")
    _check("Gemfile", "Ruby")
    _check("composer.json", "PHP")
    _check("pom.xml", "Java (Maven)")
    _check("build.gradle", "Java/Kotlin (Gradle)")
    _check("Dockerfile", "Container", extra=" — ships in Docker")
    _check(".github/workflows", "GitHub Actions CI")
    if not stack_lines:
        stack_lines.append("_(no manifest file detected — single-language repo)_")

    # ── file-type counts ────────────────────────────────────────────────────
    ext_counts: dict[str, int] = {}
    for f in tree:
        ext = os.path.splitext(f)[1].lower() or "(none)"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
    top_exts = sorted(ext_counts.items(), key=lambda kv: -kv[1])[:8]
    ext_table = "\n".join(f"| `{e}` | {c} |" for e, c in top_exts)

    # ── top-level dirs ──────────────────────────────────────────────────────
    top_dirs: dict[str, int] = {}
    for f in tree:
        parts = f.replace("\\", "/").split("/", 1)
        if len(parts) == 2:
            top_dirs[parts[0]] = top_dirs.get(parts[0], 0) + 1
    top_dir_lines = "\n".join(
        f"- `{d}/` — {n} files" for d, n in sorted(top_dirs.items(), key=lambda kv: -kv[1])[:12]
    ) or "_(flat repo — all files at root)_"

    # ── notable anchor files ────────────────────────────────────────────────
    anchors = []
    for a in ("README.md", "CLAUDE.md", "architecture.md", "ARCHITECTURE.md",
              ".env.example", "docs/INDEX.md", "Makefile"):
        if os.path.exists(os.path.join(root, a)):
            anchors.append(f"- `{a}`")
    anchors_block = "\n".join(anchors) or "_(none found)_"

    # ── full file tree (collapsible) ────────────────────────────────────────
    tree_block = "\n".join(tree[:500])
    tree_overflow = f"\n... +{len(tree) - 500} more" if len(tree) > 500 else ""

    template = f"""# APEX Project Directives — {active.name}

> Auto-generated by `/init` on {TimeContext.now_human()}. Edit freely. APEX reads this on every request as highest-priority context.

## Project
- **Name:** {active.name}
- **Root:** `{root}`
- **Files mapped:** {len(tree)}

## Goals
{chr(10).join(f"- {g}" for g in active.goals) or "- _(none — edit me)_"}

## Stack
{chr(10).join(stack_lines)}

## Top-level layout
{top_dir_lines}

## File-type breakdown
| Extension | Count |
|---|---|
{ext_table}

## Anchor files
{anchors_block}

## Conventions
- Match existing code style — read 2-3 neighbor files before writing.
- Don't add features that weren't asked for. Don't refactor unrelated code.
- Default to no comments unless the *why* is non-obvious.
- Run tests before declaring done. Prefer editing existing files over creating new ones.

## Notes
_Add long-lived constraints, gotchas, architectural decisions, and "do not touch" zones here._

<details>
<summary>Full file tree ({len(tree)} files)</summary>

```
{tree_block}{tree_overflow}
```
</details>
"""
    with open(apex_md_path, "w", encoding="utf-8") as f:
        f.write(template)
    engine.console.print(f"[bold green]✓ APEX.md generated at {apex_md_path}[/bold green]")
    engine.console.print(f"[dim]  {len(tree)} files mapped, {len(top_exts)} ext groups, {len(stack_lines)} stack hints[/dim]")


async def cmd_compact(engine):
    """
    Summarizes session history into one entry, then clears the rest.
    """
    if not engine.gemini_client:
        engine.console.print("[red]Gemini unavailable for compaction.[/red]")
        return

    context = await engine.memory_manager.redis.load_session(engine.session_id)
    if not context or not context.history:
        engine.console.print("[dim]Nothing to compact.[/dim]")
        return

    history_str = "\n".join([f"{e.role}: {e.content}" for e in context.history])
    try:
        res = engine.gemini_client.client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=f"Summarize this conversation into 5 bullets capturing decisions, open threads, and key facts:\n\n{history_str}",
        )
        summary = res.text.strip()
        await engine.memory_manager.clear_session_history(engine.session_id)
        from src.core.models import MemoryEntry
        await engine.memory_manager.redis.add_to_history(
            engine.session_id,
            MemoryEntry(role="system", content=f"[COMPACTED SUMMARY]\n{summary}"),
        )
        engine.console.print(Panel(summary, title="COMPACTED CONTEXT", border_style="green"))
    except Exception as e:
        engine.console.print(f"[red]Compaction failed: {e}[/red]")


async def cmd_status(engine):
    vitals = engine.parallel_executor.hw.get_vitals()
    active = engine.workspace.get_active()
    spend = engine.spend_tracker.get_daily_spend()

    table = Table(title="APEX SYSTEM STATUS", border_style="cyan")
    table.add_column("Field", style="bold magenta")
    table.add_column("Value")
    table.add_row("Session", engine.session_id)
    table.add_row("Project", active.name if active else "[dim]none[/dim]")
    table.add_row("Files mapped", str(len(active.file_tree)) if active else "0")
    table.add_row("CPU", f"{vitals.cpu_percent}%")
    table.add_row("RAM", f"{vitals.ram_percent}%")
    table.add_row("Status", vitals.status)
    table.add_row("Daily spend", f"${spend:.4f}")
    table.add_row("Gemini", "online" if engine.gemini_client else "[red]offline[/red]")
    table.add_row("Groq", "online" if engine.groq_client.client else "[red]offline[/red]")
    mimo_online = bool(engine.parallel_executor.coding_pipeline.mimo.is_online)
    table.add_row("MiMo v2.5-pro", "online" if mimo_online else "[red]offline[/red]")
    table.add_row("Safety mode", engine.parallel_executor.safety_guard.mode)
    table.add_row("MCP servers", ", ".join(engine.mcp_client.sessions.keys()) or "[dim]none[/dim]")
    engine.console.print(table)


async def cmd_skills(engine):
    try:
        raw = engine.learning_manager.skill_manager.collection.get()
        meta = raw.get("metadatas") or []
    except Exception as e:
        engine.console.print(f"[red]Skill registry error: {e}[/red]")
        return
    if not meta:
        engine.console.print("[dim]No skills registered.[/dim]")
        return
    table = Table(title="REGISTERED SKILLS", border_style="magenta")
    table.add_column("Name", style="bold")
    table.add_column("Description")
    for m in meta:
        if m:
            table.add_row(m.get("name", ""), m.get("description", "")[:80])
    engine.console.print(table)


async def cmd_todos(engine, args):
    active = engine.workspace.get_active()
    if not active:
        engine.console.print("[red]No active project.[/red]")
        return
    if args and args[0] == "done" and len(args) > 1:
        try:
            idx = int(args[1]) - 1
            ok = engine.workspace.complete_todo(active.name, idx)
            engine.console.print("[green]✓ Marked done.[/green]" if ok else "[red]Invalid todo index.[/red]")
            # Re-sync deadlines after completing a todo
            if ok and hasattr(engine, 'predictor'):
                try:
                    updated = engine.workspace.get_active()
                    engine.predictor.sync_deadlines(updated.todos if updated else [])
                except Exception:
                    pass
        except ValueError:
            engine.console.print("[red]Usage: /todo done <number>[/red]")
        return
    if args:
        engine.workspace.add_todo(active.name, " ".join(args))
        engine.console.print("[green]✓ Todo added.[/green]")
        # Re-sync deadlines after adding a todo
        if hasattr(engine, 'predictor'):
            try:
                updated = engine.workspace.get_active()
                engine.predictor.sync_deadlines(updated.todos if updated else [])
            except Exception:
                pass
        return
    if not active.todos:
        engine.console.print("[dim]No todos.[/dim]")
        return
    for i, t in enumerate(active.todos):
        mark = "[green]✓[/green]" if t.get("done") else "[yellow]○[/yellow]"
        engine.console.print(f" {mark} {i+1}. {t.get('task','')}")
    # Show upcoming deadlines inline
    if hasattr(engine, 'predictor'):
        try:
            engine.predictor.sync_deadlines(active.todos or [])
            upcoming = engine.predictor.get_upcoming_deadlines(days_window=3)
            if upcoming:
                engine.console.print("")
                for d in upcoming:
                    risk_color = "red" if d['days_left'] <= 1 else "yellow"
                    engine.console.print(
                        f"  [{risk_color}]⚠  Due in {d['days_left']}d: {d['task'][:70]}[/{risk_color}]"
                    )
        except Exception:
            pass


async def cmd_web(engine, query: str):
    if not query.strip():
        engine.console.print("[red]Usage: /web <query>[/red]")
        return
    with Live(Spinner("dots", text=f"Searching: {query}", style="cyan"), refresh_per_second=10, transient=True):
        data = await engine.parallel_executor.web_search.asearch(query)
    if not data.get("success"):
        engine.console.print(f"[red]{data.get('error')}[/red]")
        return
    table = Table(title=f"WEB RESULTS — {data.get('provider','?')}", border_style="cyan")
    table.add_column("Title", style="bold")
    table.add_column("URL", style="dim")
    table.add_column("Snippet")
    for r in data.get("results", [])[:8]:
        table.add_row(r.get("title", "")[:60], r.get("url", "")[:50], r.get("snippet", "")[:100])
    engine.console.print(table)


async def cmd_resume(engine):
    if not engine.memory_manager.redis.is_active:
        engine.console.print("[red]Redis offline; resume unavailable.[/red]")
        return
    try:
        keys = await engine.memory_manager.redis.client.keys("apex:session:*")
    except Exception as e:
        engine.console.print(f"[red]Redis error: {e}[/red]")
        return
    if not keys:
        engine.console.print("[dim]No prior sessions.[/dim]")
        return
    engine.console.print("[bold]Recent sessions:[/bold]")
    for k in keys[:10]:
        sid = k.split(":")[-1]
        engine.console.print(f"  • {sid}")
    target = Prompt.ask("Resume which session id? (blank to skip)", default="")
    if target:
        engine.session_id = target
        engine.console.print(f"[green]✓ Resumed session {target}[/green]")


def _render_genius(console, res: dict, terse: bool = False):
    """Render full GeniusMode output: cross-question + right/wrong + blind spots + action + one-liner."""
    sections = []
    cq = res.get("cross_question", []) or []
    if cq:
        lines = ["[bold bright_magenta]?  CROSS-QUESTION[/bold bright_magenta]"]
        for i, q in enumerate(cq, 1):
            lines.append(f"  [bold]Q{i}.[/bold] {q.get('q','')}")
            if q.get("why_it_matters"):
                lines.append(f"     [dim]why:[/dim] {q['why_it_matters']}")
            if q.get("default_assumption"):
                lines.append(f"     [dim]default:[/dim] {q['default_assumption']}")
        sections.append("\n".join(lines))

    right = res.get("right", []) or []
    if right:
        sections.append("[bold green]✓  RIGHT[/bold green]\n" +
                        "\n".join(f"  • {x}" for x in right))

    wrong = res.get("wrong", []) or []
    if wrong:
        sections.append("[bold red]✗  WRONG[/bold red]\n" +
                        "\n".join(f"  • {x}" for x in wrong))

    bs = res.get("blind_spots", []) or []
    if bs:
        sections.append("[bold yellow]!  BLIND SPOTS[/bold yellow]\n" +
                        "\n".join(f"  • {x}" for x in bs))

    actions = res.get("action", []) or []
    if actions:
        lines = ["[bold cyan]→  ACTION[/bold cyan]"]
        for a in actions:
            lines.append(f"  [bold]{a.get('rank','?')}.[/bold] {a.get('step','')}")
            if a.get("rationale"):
                lines.append(f"     [dim]{a['rationale']}[/dim]")
        sections.append("\n".join(lines))

    oneliner = res.get("one_liner", "")
    if oneliner:
        sections.append(f"[italic gold1]“{oneliner}”[/italic gold1]")

    rival = res.get("rival_name", "")
    scorecard = res.get("rival_scorecard", "")
    title = f"APEX GENIUS  ·  {rival} ({scorecard})" if rival else "APEX GENIUS"

    console.print(Panel(
        "\n\n".join(sections) or "(no analysis)",
        title=title, border_style="bright_magenta", padding=(1, 2),
    ))


def _render_cross_question(console, res: dict):
    score = res.get("ambiguity_score", 0.0)
    interp = res.get("interpretation", "")
    qs = res.get("questions", [])
    must = res.get("must_answer", [])
    if not qs:
        console.print(Panel(
            f"[green]Prompt is clear[/green] (ambiguity {score:.2f})\nInterpretation: {interp}",
            title="CROSS-QUESTION", border_style="bright_magenta",
        ))
        return
    lines = [f"[bold]Interpretation:[/bold] {interp}",
             f"[bold]Ambiguity:[/bold] {score:.2f}",
             ""]
    for i, q in enumerate(qs, 1):
        marker = "[red]●[/red]" if q.get("q") in must else "[dim]○[/dim]"
        lines.append(f"{marker} [bold]Q{i}.[/bold] {q.get('q','')}")
        lines.append(f"   [dim]why: {q.get('why_it_matters','')}[/dim]")
        lines.append(f"   [dim]default: {q.get('default_assumption','')}[/dim]")
        lines.append("")
    if must:
        lines.append(f"[red bold]Must-answer ({len(must)}):[/red bold] " + "; ".join(must))
    console.print(Panel("\n".join(lines), title="CROSS-QUESTION", border_style="bright_magenta"))


async def handle_slash(engine, cmd_line: str, skills_dir: str) -> bool:
    """
    Returns True if the slash command was handled (caller should `continue`).
    Returns False on /exit (caller should break).
    """
    parts = cmd_line.strip().split()
    cmd = parts[0].lower()
    args = parts[1:]
    console = engine.console

    if cmd == "/exit":
        return None
    if cmd == "/help":
        console.print(Panel(SLASH_HELP, border_style="cyan", title="HELP"))
        return True
    if cmd == "/tools":
        from src.tools.registry import REGISTRY, list_tools
        tbl = Table(title=f"REGISTERED TOOLS ({len(REGISTRY)})", border_style="cyan")
        tbl.add_column("Tool", style="bold")
        tbl.add_column("Actions")
        tbl.add_column("Aliases", style="dim")
        tbl.add_column("OK", style="green")
        tbl.add_column("Fail", style="red")
        tele = engine.parallel_executor.telemetry.summary()
        for name in list_tools():
            spec = REGISTRY[name]
            stats = tele.get(name, {})
            tbl.add_row(
                name,
                ",".join(spec.actions)[:40],
                ",".join(spec.aliases)[:30],
                str(stats.get("ok", 0)),
                str(stats.get("fail", 0)),
            )
        console.print(tbl)
        # Show last error per tool that has one
        errors = [(t, s["last_error"]) for t, s in tele.items() if s.get("last_error")]
        if errors:
            console.print("\n[bold red]Recent errors:[/bold red]")
            for t, err in errors:
                console.print(f"  [red]{t}[/red]: {err}")
        return True
    if cmd == "/now":
        tod = TimeContext.time_of_day()
        weekend = "weekend" if TimeContext.is_weekend() else "weekday"
        late = " (late-night)" if TimeContext.is_late_night() else ""
        console.print(Panel(
            f"[bold]{TimeContext.now_human()}[/bold]\n"
            f"[dim]{tod} · {weekend}{late}[/dim]\n"
            f"ISO: {TimeContext.now_iso()}",
            title="TIME", border_style="cyan",
        ))
        return True
    if cmd == "/clear":
        clear_console()
        return True
    if cmd == "/socratic":
        if engine.gemini_client:
            engine.gemini_client.socratic_mode = not engine.gemini_client.socratic_mode
            console.print(f"[cyan]Socratic mode → {engine.gemini_client.socratic_mode}[/cyan]")
        return True
    if cmd == "/steelman":
        if engine.gemini_client:
            engine.gemini_client.steelman_mode = not engine.gemini_client.steelman_mode
            console.print(f"[cyan]Steelman mode → {engine.gemini_client.steelman_mode}[/cyan]")
        return True
    if cmd == "/genius":
        if engine.gemini_client:
            engine.gemini_client.genius_mode = not engine.gemini_client.genius_mode
            console.print(f"[bold magenta]Genius mode → {engine.gemini_client.genius_mode}[/bold magenta]")
        else:
            console.print("[red]Gemini offline — genius mode unavailable.[/red]")
        return True
    if cmd == "/autotool":
        if args and args[0].lower() in ("on", "off"):
            engine.auto_tool_enabled = args[0].lower() == "on"
        else:
            engine.auto_tool_enabled = not engine.auto_tool_enabled
        console.print(f"[cyan]Auto-tool → {engine.auto_tool_enabled}[/cyan]")
        return True
    if cmd == "/reflex":
        # Sub-commands: /reflex prefetch on|off  |  /reflex reset
        if args and args[0].lower() == "prefetch" and len(args) > 1:
            on = args[1].lower() == "on"
            engine.classifier.reflex.set_prefetch_enabled(on)
            console.print(f"[bright_cyan]Reflex prefetch → {on}[/bright_cyan]")
            return True
        if args and args[0].lower() == "reset":
            engine.classifier.reflex.reset_cache()
            for k in engine.classifier.reflex.counters:
                engine.classifier.reflex.counters[k] = 0
            engine.classifier.reflex._recent_results.clear()
            engine.classifier.reflex._auto_disabled = False
            console.print("[bright_cyan]Reflex telemetry + cache reset[/bright_cyan]")
            return True
        try:
            stats = engine.classifier.reflex.stats()
            # Split into two tables — routing vs prefetch — for readability
            r_tbl = Table(title="REFLEX — routing", border_style="bright_cyan")
            r_tbl.add_column("Metric", style="bold")
            r_tbl.add_column("Value")
            routing_keys = [
                "calls", "cache_hits", "hit_rate", "cache_size",
                "trivial", "regex_tool", "skill_match",
                "embed_nn", "token_nn", "llm_escalations", "llm_skip_rate",
            ]
            for k in routing_keys:
                v = stats.get(k)
                if isinstance(v, float):
                    r_tbl.add_row(k, f"{v:.3f}")
                else:
                    r_tbl.add_row(k, str(v))
            console.print(r_tbl)

            p_tbl = Table(title="REFLEX — prefetch", border_style="magenta")
            p_tbl.add_column("Metric", style="bold")
            p_tbl.add_column("Value")
            prefetch_keys = [
                "prefetch_enabled", "prefetch_auto_disabled",
                "adaptive_window_filled",
                "prefetch_started", "prefetch_used", "prefetch_wasted",
                "prefetch_cache_hits", "prefetch_use_rate", "prefetch_waste_rate",
                "prefetch_bytes_saved", "prefetch_disabled_auto",
            ]
            for k in prefetch_keys:
                v = stats.get(k)
                if isinstance(v, float):
                    p_tbl.add_row(k, f"{v:.3f}")
                else:
                    p_tbl.add_row(k, str(v))
            console.print(p_tbl)
            console.print(
                "[dim]llm_skip_rate = inputs handled w/o Gemini classify. "
                "prefetch_use_rate = bundle reuse vs spawn. "
                "Auto-disable trips at 60% waste over 20 calls. "
                "/reflex prefetch on|off · /reflex reset[/dim]"
            )
        except Exception as e:
            console.print(f"[red]reflex stats unavailable: {e}[/red]")
        return True
    if cmd == "/autothink":
        if args and args[0].lower() in ("on", "off"):
            engine.auto_think_enabled = args[0].lower() == "on"
        else:
            engine.auto_think_enabled = not engine.auto_think_enabled
        console.print(f"[bright_magenta]Auto-think → {engine.auto_think_enabled}[/bright_magenta]")
        return True
    if cmd == "/economy":
        if args and args[0].lower() in ("on", "off"):
            engine.economy_mode = args[0].lower() == "on"
        else:
            engine.economy_mode = not engine.economy_mode
        console.print(f"[bold cyan]Economy mode → {engine.economy_mode}[/bold cyan] [dim](skips auto_think/cognitive/pruning/bg learning to save API quota)[/dim]")
        return True
    if cmd == "/full":
        engine.economy_mode = False
        engine.auto_think_enabled = True
        engine.background_loops_enabled = True
        console.print("[bold magenta]FULL mode: economy off, auto_think on, bg loops on.[/bold magenta]")
        return True
    if cmd == "/background":
        if args and args[0].lower() in ("on", "off"):
            engine.background_loops_enabled = args[0].lower() == "on"
        else:
            engine.background_loops_enabled = not engine.background_loops_enabled
        console.print(f"[cyan]Background loops → {engine.background_loops_enabled}[/cyan] [dim](self_evolver + knowledge_forge, restart APEX to apply)[/dim]")
        return True
    if cmd == "/quota":
        used = engine.spend_tracker.daily_call_count() if hasattr(engine.spend_tracker, "daily_call_count") else "?"
        spend = engine.spend_tracker.get_daily_spend()
        console.print(f"[cyan]Today: {used}/{engine.daily_call_limit} LLM calls · ${spend:.4f}[/cyan]")
        return True
    if cmd == "/think":
        if not args:
            console.print("[yellow]Usage: /think <prompt>[/yellow]")
            return True
        prompt_text = " ".join(args)
        with Live(Spinner("dots", text="Cross-questioning...", style="bright_magenta"), refresh_per_second=10, transient=True):
            res = await engine.think_partner.cross_question(prompt_text)
        _render_cross_question(console, res)
        return True
    if cmd == "/architect":
        if not args:
            console.print("[yellow]Usage: /architect <idea>  OR  /architect <idea> | <your-architecture>[/yellow]")
            return True
        full = " ".join(args)
        if "|" in full:
            idea, user_arch = (s.strip() for s in full.split("|", 1))
        else:
            idea, user_arch = full, ""
        with Live(Spinner("dots", text="Architecting...", style="bright_magenta"), refresh_per_second=10, transient=True):
            res = await engine.think_partner.architect(idea, user_architecture=user_arch)
        console.print(Panel(Markdown(res["output"]), title="ARCHITECT", border_style="bright_magenta"))
        console.print(f"[dim]→ {res['next_action']}[/dim]")
        return True
    if cmd == "/debate":
        if not args:
            console.print("[yellow]Usage: /debate <claim>[/yellow]")
            return True
        claim = " ".join(args)
        with Live(Spinner("dots", text="Steelmanning the opposite...", style="bright_magenta"), refresh_per_second=10, transient=True):
            res = await engine.think_partner.debate(claim)
        console.print(Panel(Markdown(res["output"]), title="DEBATE", border_style="bright_magenta"))
        console.print(f"[dim]→ {res['next_action']}[/dim]")
        return True
    if cmd == "/brainstorm":
        if not args:
            console.print("[yellow]Usage: /brainstorm <topic>[/yellow]")
            return True
        topic = " ".join(args)
        with Live(Spinner("dots", text="Diverging across mental models...", style="bright_magenta"), refresh_per_second=10, transient=True):
            res = await engine.think_partner.brainstorm(topic)
        console.print(Panel(Markdown(res["output"]), title="BRAINSTORM", border_style="bright_magenta"))
        console.print(f"[dim]→ {res['next_action']}[/dim]")
        return True
    if cmd == "/teach":
        if not args:
            console.print("[yellow]Usage: /teach <topic>[/yellow]")
            return True
        topic = " ".join(args)
        with Live(Spinner("dots", text="Layering explanation...", style="bright_magenta"), refresh_per_second=10, transient=True):
            res = await engine.think_partner.teach(topic)
        console.print(Panel(Markdown(res["output"]), title="TEACH", border_style="bright_magenta"))
        console.print(f"[dim]→ {res['next_action']}[/dim]")
        return True
    if cmd == "/intent":
        if not args:
            console.print("[yellow]Usage: /intent <prompt>[/yellow]")
            return True
        prompt_text = " ".join(args)
        with Live(Spinner("dots", text="Decomposing intent...", style="bright_magenta"), refresh_per_second=10, transient=True):
            res = await engine.think_partner.extract_intent(prompt_text)
        console.print(Panel(json.dumps(res, indent=2), title="INTENT", border_style="bright_magenta"))
        return True
    if cmd == "/swarm":
        if not args:
            console.print("[yellow]Usage: /swarm <goal> [| role1,role2] [rounds=N][/yellow]")
            return True
        goal, rounds, roster = _parse_swarm_args(" ".join(args))
        await dispatch_swarm(engine, console, goal, rounds=rounds, roster=roster, trigger="slash")
        return True
    if cmd == "/autoswarm":
        if args and args[0].lower() in ("on", "off"):
            engine.auto_swarm_enabled = args[0].lower() == "on"
        else:
            engine.auto_swarm_enabled = not engine.auto_swarm_enabled
        console.print(
            f"[bright_blue]Auto-swarm → {engine.auto_swarm_enabled}[/bright_blue] "
            f"[dim](high-complexity coding/architect intents auto-spawn swarm)[/dim]"
        )
        return True
    if cmd == "/evolve":
        auto = bool(args) and args[0] == "auto"
        result = await thinking_cascade(
            engine.self_evolver.run_cycle(auto_provision=auto),
            phases=["Benchmarking capabilities", "Identifying gaps", "Generating proposals", "Applying improvements"],
            console=console,
            style="magenta",
        )
        if "skipped" in result:
            console.print(f"[yellow]Cycle skipped: {result['skipped']}[/yellow]")
            return True
        proposals = result.get("proposals", [])
        if proposals:
            table = Table(title="SELF-EVOLUTION PROPOSALS", border_style="magenta")
            table.add_column("Pri", style="bold")
            table.add_column("Action")
            table.add_column("Target")
            table.add_column("Rationale")
            for p in proposals[:10]:
                table.add_row(str(p.get("priority", 3)), p.get("action", ""), p.get("target_file", "")[:40], p.get("rationale", "")[:60])
            console.print(table)
        else:
            console.print("[dim]No proposals generated this cycle.[/dim]")
        return True
    if cmd == "/proposals":
        path = engine.self_evolver.proposals_path
        if not path.exists():
            console.print("[dim]No proposals stored yet. Run /evolve first.[/dim]")
            return True
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not data:
                console.print("[dim]Empty proposal log.[/dim]")
                return True
            latest = data[-1]
            console.print(Panel(json.dumps(latest.get("proposals", []), indent=2)[:2000], title=f"PROPOSALS @ {latest.get('ts')}", border_style="magenta"))
        except Exception as e:
            console.print(f"[red]Failed to read proposals: {e}[/red]")
        return True
    if cmd == "/analyze":
        if not args:
            with Live(Spinner("dots", text="Building code compass...", style="cyan"), refresh_per_second=10, transient=True):
                engine.code_compass.build()
            s = engine.code_compass.summary()
            console.print(Panel(
                f"Files: {s['files']} | Classes: {s['classes']} | Functions: {s['functions']} | LoC: {s['lines_of_code']}\n"
                f"Compression: {s['compression_ratio']*100:.1f}% of raw size\n"
                f"Estimated token savings: ~{s['approx_token_savings']:,}",
                title="CODE COMPASS", border_style="cyan"
            ))
        else:
            term = " ".join(args)
            if not engine.code_compass.index:
                engine.code_compass.build()
            hits = engine.code_compass.query(term)
            if not hits:
                console.print(f"[dim]No symbols match '{term}'.[/dim]")
                return True
            table = Table(title=f"SYMBOL SEARCH — '{term}'", border_style="cyan")
            table.add_column("Kind", style="bold")
            table.add_column("Name")
            table.add_column("File")
            table.add_column("Line", style="dim")
            for h in hits:
                table.add_row(h.get("kind", ""), h.get("name", h.get("file", "")), h.get("file", ""), str(h.get("line", "")))
            console.print(table)
        return True
    if cmd == "/map-stats":
        if not engine.code_compass.index:
            engine.code_compass.build()
        s = engine.code_compass.summary()
        console.print(Panel(json.dumps(s, indent=2), title="CODE COMPASS STATS", border_style="cyan"))
        return True
    if cmd == "/forge":
        sub = args[0].lower() if args else "full"
        forge = engine.knowledge_forge
        if sub == "full":
            with Live(Spinner("dots", text="Forge cycle running...", style="bright_cyan"), refresh_per_second=10, transient=True):
                res = await forge.run_full_cycle(do_bench=True)
            if "skipped" in res:
                console.print(f"[yellow]Forge skipped: {res['skipped']}[/yellow]")
                return True
            summary = forge._load_state().get("last_summary", {})
            console.print(Panel(json.dumps(summary, indent=2), title="FORGE CYCLE", border_style="bright_cyan"))
            return True
        if sub == "papers":
            with Live(Spinner("dots", text="Scanning arxiv...", style="bright_cyan"), refresh_per_second=10, transient=True):
                res = await forge.run_papers()
            tbl = Table(title=f"PAPERS — {res['applicable_count']}/{res['new_count']} applicable", border_style="bright_cyan")
            tbl.add_column("Score", style="bold")
            tbl.add_column("Cat")
            tbl.add_column("Title")
            tbl.add_column("Insight")
            for p in res.get("applicable", [])[:15]:
                sc = (p.get("score") or {})
                tbl.add_row(f"{sc.get('applicability', 0):.2f}", p.get("category", ""), p.get("title", "")[:60], sc.get("actionable_insight", "")[:80])
            console.print(tbl)
            return True
        if sub == "ecosystem":
            with Live(Spinner("dots", text="Scanning ecosystem...", style="bright_cyan"), refresh_per_second=10, transient=True):
                res = await forge.run_ecosystem()
            tbl = Table(title=f"ECOSYSTEM — {res['applicable_count']}/{res['new_count']} applicable", border_style="bright_cyan")
            tbl.add_column("Rel", style="bold")
            tbl.add_column("Source")
            tbl.add_column("Title")
            tbl.add_column("Why")
            for it in res.get("applicable", [])[:20]:
                tbl.add_row(f"{it.get('relevance', 0):.2f}", it.get("source", "")[:14], it.get("title", "")[:48], it.get("why", "")[:60])
            console.print(tbl)
            return True
        if sub == "synth":
            with Live(Spinner("dots", text="Synthesizing proposals...", style="magenta"), refresh_per_second=10, transient=True):
                res = await forge.run_synthesis()
            tbl = Table(title=f"NEW PROPOSALS ({res.get('added', 0)} added, {res.get('total_queued', 0)} queued)", border_style="magenta")
            tbl.add_column("ID", style="dim")
            tbl.add_column("Pri", style="bold")
            tbl.add_column("Kind")
            tbl.add_column("Title")
            tbl.add_column("Risk")
            for p in res.get("proposals", [])[:12]:
                tbl.add_row(p.get("id", "")[:12], str(p.get("priority", 3)), p.get("kind", "")[:18], p.get("title", "")[:48], p.get("risk", ""))
            console.print(tbl)
            return True
        if sub == "bench":
            with Live(Spinner("dots", text="Running self-benchmark...", style="green"), refresh_per_second=10, transient=True):
                res = await forge.run_bench()
            console.print(Panel(json.dumps(res.get("summary", {}), indent=2), title="BENCH SUMMARY", border_style="green"))
            reg = res.get("regression_check", {})
            if reg.get("regression"):
                console.print(Panel(json.dumps(reg, indent=2), title="REGRESSION", border_style="red"))
            return True
        if sub == "proposals":
            queued = forge.list_proposals(limit=30)
            if not queued:
                console.print("[dim]No queued proposals. Run /forge synth or /forge.[/dim]")
                return True
            tbl = Table(title=f"QUEUED PROPOSALS ({len(queued)})", border_style="magenta")
            tbl.add_column("ID", style="dim")
            tbl.add_column("Pri", style="bold")
            tbl.add_column("Kind")
            tbl.add_column("Title")
            tbl.add_column("Target")
            tbl.add_column("Risk")
            for p in queued:
                targets = ", ".join((p.get("target_files") or [])[:2])[:30]
                tbl.add_row(p.get("id", ""), str(p.get("priority", 3)), p.get("kind", "")[:18], p.get("title", "")[:46], targets, p.get("risk", ""))
            console.print(tbl)
            return True
        if sub == "approve" and len(args) >= 2:
            ok = forge.update_proposal(args[1], "approved")
            console.print(f"[green]✓ approved {args[1]}[/green]" if ok else f"[red]proposal {args[1]} not found[/red]")
            return True
        if sub == "reject" and len(args) >= 2:
            ok = forge.update_proposal(args[1], "rejected")
            console.print(f"[yellow]✗ rejected {args[1]}[/yellow]" if ok else f"[red]proposal {args[1]} not found[/red]")
            return True
        if sub == "implement" and len(args) >= 2:
            pid = args[1]
            use_diff = len(args) >= 3 and args[2].lower() == "diff"
            mode_label = "diff-mode" if use_diff else "full-rewrite"
            if not Confirm.ask(f"[bold red]Apply proposal {pid} ({mode_label}, bench-gated rollback)?[/bold red]", default=False):
                console.print("[dim]Aborted.[/dim]")
                return True
            with Live(Spinner("dots", text=f"Applying {pid} ({mode_label})...", style="magenta"), refresh_per_second=10, transient=True):
                res = await forge.apply_proposal(pid, gate_with_bench=True, use_diff=use_diff)
            if res.get("ok"):
                console.print(Panel(json.dumps(res, indent=2)[:2000], title=f"APPLIED {pid}", border_style="green"))
            else:
                console.print(Panel(json.dumps(res, indent=2)[:2000], title=f"APPLY FAILED {pid}", border_style="red"))
            return True
        if sub == "backfill":
            days = int(args[1]) if len(args) >= 2 and args[1].isdigit() else 7
            with Live(Spinner("dots", text=f"arxiv backfill ({days}d)...", style="bright_cyan"), refresh_per_second=10, transient=True):
                res = await forge.run_backfill(days=days)
            console.print(Panel(
                f"Days: {days} | New: {res['new_count']} | Applicable: {res['applicable_count']}",
                title="ARXIV BACKFILL", border_style="bright_cyan",
            ))
            return True
        if sub == "undo" and len(args) >= 2:
            pid = args[1]
            ts = args[2] if len(args) >= 3 else None
            if not Confirm.ask(f"[bold red]Restore backup for {pid}?[/bold red]", default=False):
                console.print("[dim]Aborted.[/dim]")
                return True
            res = forge.applier.restore_backup(pid, ts=ts)
            if res.get("ok"):
                console.print(f"[green]Restored {len(res['restored'])} file(s) from {res['from_ts']}[/green]")
            else:
                console.print(f"[red]Undo failed: {res.get('error')}[/red]")
            return True
        if sub == "log":
            text = forge.read_forge_log(n=30)
            console.print(Panel(text, title="FORGE LOG (~/.apex/forge_log.md)", border_style="bright_cyan"))
            return True
        if sub == "search" and len(args) >= 2:
            q = " ".join(args[1:])
            hits = forge.search_papers(q, n=8)
            if not hits:
                console.print("[dim]No matches.[/dim]")
                return True
            tbl = Table(title=f"PAPER SEARCH — '{q}'", border_style="bright_cyan")
            tbl.add_column("ID", style="dim")
            tbl.add_column("Cat")
            tbl.add_column("Snippet")
            for h in hits:
                meta = h.get("metadata", {})
                tbl.add_row(h.get("id", "")[:14], str(meta.get("category", ""))[:10], h.get("doc", "")[:120].replace("\n", " "))
            console.print(tbl)
            return True
        if sub == "status":
            console.print(Panel(json.dumps(forge.status_summary(), indent=2), title="FORGE STATUS", border_style="bright_cyan"))
            return True
        console.print(f"[yellow]Unknown /forge subcommand: {sub}. Try /help.[/yellow]")
        return True
    if cmd == "/auto-approve":
        sg = engine.parallel_executor.safety_guard
        sg.set_mode("default" if sg.mode == "auto-approve" else "auto-approve")
        return True
    if cmd == "/plan":
        sg = engine.parallel_executor.safety_guard
        sg.set_mode("default" if sg.mode == "plan" else "plan")
        return True
    if cmd == "/reload-skills":
        engine.learning_manager.load_markdown_skills(skills_dir)
        console.print("[bold green]✓ SKILLS RELOADED.[/bold green]")
        return True
    if cmd == "/skills":
        await cmd_skills(engine)
        return True
    if cmd == "/cost":
        spend = engine.spend_tracker.get_daily_spend()
        console.print(Panel(f"[bold green]Today: ${spend:.4f}[/bold green]", title="SPEND", border_style="green"))
        return True
    if cmd == "/status":
        await cmd_status(engine)
        return True
    if cmd == "/voice":
        sub = args[0].lower() if args else "status"
        if sub == "on":
            if engine.voice_enabled:
                console.print("[cyan]Voice mode is already active.[/cyan]")
            else:
                engine.voice_enabled = True
                if not getattr(engine, "voice_task", None) or engine.voice_task.done():
                    engine.voice_task = asyncio.create_task(engine.voice.run())
                console.print("[green]Voice systems online. Listening for wake word...[/green]")
        elif sub == "off":
            if not engine.voice_enabled:
                console.print("[cyan]Voice mode is already offline.[/cyan]")
            else:
                engine.voice_enabled = False
                engine.voice.stop()
                if getattr(engine, "voice_task", None) and not engine.voice_task.done():
                    engine.voice_task.cancel()
                console.print("[yellow]Voice systems offline.[/yellow]")
        elif sub == "mute":
            engine.voice.mute(True)
            console.print("[yellow]Voice output muted.[/yellow]")
        elif sub == "unmute":
            engine.voice.mute(False)
            console.print("[green]Voice output unmuted.[/green]")
        elif sub == "status":
            status = "active" if engine.voice_enabled else "offline"
            muted = "muted" if getattr(engine.voice, "_muted", False) else "unmuted"
            console.print(f"[cyan]Voice Mode: {status} ({muted})[/cyan]")
        else:
            console.print("[red]Usage: /voice [on|off|mute|unmute|status][/red]")
        return True
    if cmd == "/ambient":
        sub = args[0].lower() if args else "status"
        if sub == "on":
            if engine.ambient_enabled:
                console.print("[cyan]Ambient monitoring is already active.[/cyan]")
            else:
                engine.ambient_enabled = True
                engine.ambient.start()
                console.print("[green]Ambient monitoring started (Window, Clipboard, File, Screen).[/green]")
        elif sub == "off":
            if not engine.ambient_enabled:
                console.print("[cyan]Ambient monitoring is already offline.[/cyan]")
            else:
                engine.ambient_enabled = False
                engine.ambient.stop()
                console.print("[yellow]Ambient monitoring stopped.[/yellow]")
        elif sub == "status":
            status = "active" if engine.ambient_enabled else "offline"
            console.print(f"[cyan]Ambient monitoring: {status}[/cyan]")
        else:
            console.print("[red]Usage: /ambient [on|off|status][/red]")
        return True
    if cmd == "/init":
        await cmd_init(engine)
        return True
    if cmd == "/compact":
        await cmd_compact(engine)
        return True
    if cmd == "/snapshot":
        path = engine.sync_manager.export_snapshot()
        console.print(f"[bold green]✓ Snapshot saved: {path}[/bold green]")
        return True
    if cmd == "/restore":
        if not args:
            console.print("[red]Usage: /restore <path>[/red]")
            return True
        ok = engine.sync_manager.load_snapshot(args[0])
        console.print("[green]✓ Restored.[/green]" if ok else "[red]Restore failed.[/red]")
        return True
    if cmd == "/resume":
        await cmd_resume(engine)
        return True
    if cmd == "/web":
        await cmd_web(engine, " ".join(args))
        return True
    if cmd == "/todo":
        await cmd_todos(engine, args)
        return True
    if cmd == "/todos":
        await cmd_todos(engine, [])
        return True
    if cmd == "/mcp":
        sub = args[0] if args else "list"
        if sub == "connect" and len(args) >= 3:
            res = await engine.mcp_client.connect(args[1], args[2], args[3:] if len(args) > 3 else [])
            console.print(f"[green]{res.get('output', res.get('error'))}[/green]")
        elif sub == "list":
            servers = list(engine.mcp_client.sessions.keys())
            console.print("[cyan]Connected MCP servers:[/cyan]")
            for s in servers:
                console.print(f"  • {s}")
            if not servers:
                console.print("[dim]  (none)[/dim]")
        elif sub == "tools" and len(args) >= 2:
            tools = await engine.mcp_client.list_tools(args[1])
            for t in tools:
                console.print(f"  - [bold]{t['name']}[/bold]: {t['description']}")
        return True
    if cmd == "/policy":
        policy = engine.parallel_executor.safety_guard.policy
        if not args or args[0] == "list":
            console.print(Panel(json.dumps(policy.policy, indent=2), title="CURRENT POLICY"))
        elif len(args) > 1:
            action, val = args[0], " ".join(args[1:])
            if action == "allow":
                policy.policy.setdefault("allowed_commands", []).append(val)
            elif action == "deny":
                policy.policy.setdefault("denied_commands", []).append(val)
            policy.save()
            console.print(f"[bold green]✓ POLICY UPDATED: {action} {val}[/bold green]")
        return True
    if cmd == "/project" and args:
        engine.workspace.create_project(args[0], "Autonomous", ".", ["Mastery"])
        console.print(f"[green]✓ Project '{args[0]}' created.[/green]")
        return True
    if cmd == "/scan":
        active = engine.workspace.get_active()
        if active:
            tree = engine.workspace.scan_local_files(active.name)
            console.print(f"[bold green]✓ CODEBASE RE-MAPPED: {len(tree)} files.[/bold green]")
        return True
    if cmd == "/map":
        path = engine.knowledge_visualizer.generate_svg()
        console.print(f"[bold green]✓ KNOWLEDGE MAP: {path}[/bold green]")
        return True
    if cmd == "/index-codebase":
        rebuild = "--rebuild" in args
        with Live(Spinner("dots", text="Indexing codebase to ChromaDB...", style="cyan"), refresh_per_second=10, transient=True):
            stats = await engine.codebase_indexer.index_codebase(rebuild=rebuild)
        if "error" in stats:
            console.print(f"[red]Indexing failed: {stats['error']}[/red]")
        else:
            console.print(f"[bold green]✓ CODEBASE INDEXED[/bold green]")
            console.print(
                f"  Scanned: {stats['scanned']} | Skipped: {stats['skipped']} | "
                f"Indexed: {stats['indexed']} | Chunks Added: {stats['chunks_added']} | "
                f"Chunks Deleted: {stats['chunks_deleted']}"
            )
        return True
    if cmd == "/search-codebase":
        if not args:
            console.print("[red]Usage: /search-codebase <query>[/red]")
            return True
        query = " ".join(args)
        with Live(Spinner("dots", text=f"Searching codebase for: {query}...", style="cyan"), refresh_per_second=10, transient=True):
            hits = await engine.codebase_indexer.search(query, limit=5)
        if not hits:
            console.print(f"[yellow]No matches found for '{query}'[/yellow]")
            return True
        for idx, hit in enumerate(hits, 1):
            meta = hit.get("metadata", {})
            title = f"{idx}. {meta.get('path')} (Lines {meta.get('start_line')}-{meta.get('end_line')})"
            console.print(Panel(
                hit.get("content", ""),
                title=title,
                border_style="cyan"
            ))
        return True
    if cmd == "/repomap":
        try:
            level = int(args[0]) if args and args[0].isdigit() else 3
        except Exception:
            level = 3
        with Live(Spinner("dots", text="Generating Repository Map...", style="magenta"), refresh_per_second=10, transient=True):
            repomap = engine.repo_map_generator.save_map(level=level)
        console.print(f"[bold green]✓ REPOSITORY MAP EXPORTED: .apex/repo_map.txt[/bold green]")
        lines = repomap.splitlines()
        preview = "\n".join(lines[:40])
        if len(lines) > 40:
            preview += f"\n... ({len(lines) - 40} more lines)"
        console.print(Panel(preview, title="REPOSITORY MAP PREVIEW", border_style="magenta"))
        return True
    if cmd == "/prune":
        context = await engine.knowledge_visualizer.get_pruned_context("current focus")
        console.print(Panel(context or "(empty)", title="PRUNED CONTEXT"))
        return True
    if cmd == "/genius":
        prompt = " ".join(args).strip()
        if not prompt:
            console.print("[red]Usage: /genius <prompt>[/red]")
            return True
        result = await thinking_cascade(
            engine.genius.analyze(prompt),
            phases=["Cross-questioning", "Evaluating right", "Finding wrong", "Surfacing blind spots", "Formulating wit"],
            console=console,
            style="bright_magenta",
        )
        _render_genius(console, result, terse=False)
        return True
    if cmd == "/critique":
        prompt = " ".join(args).strip()
        if not prompt:
            console.print("[red]Usage: /critique <prompt>[/red]")
            return True
        result = await thinking_cascade(
            engine.genius.critique_only(prompt),
            phases=["Auditing assumptions", "Scoring right vs wrong"],
            console=console,
            style="magenta",
        )
        body_lines = []
        right = result.get("right", []) or []
        wrong = result.get("wrong", []) or []
        if right:
            body_lines.append("[bold green]✓ RIGHT[/bold green]")
            body_lines += [f"  • {x}" for x in right]
        if wrong:
            body_lines.append("\n[bold red]✗ WRONG[/bold red]")
            body_lines += [f"  • {x}" for x in wrong]
        if result.get("one_liner"):
            body_lines.append(f"\n[italic gold1]“{result['one_liner']}”[/italic gold1]")
        console.print(Panel("\n".join(body_lines) or "(no critique)",
                            title="CRITIQUE", border_style="magenta"))
        return True
    if cmd == "/blindspot":
        prompt = " ".join(args).strip()
        if not prompt:
            console.print("[red]Usage: /blindspot <prompt>[/red]")
            return True
        result = await thinking_cascade(
            engine.genius.blindspots_only(prompt),
            phases=["Scanning second-order effects", "Mapping blind spots", "Ranking next steps"],
            console=console,
            style="yellow",
        )
        body = []
        bs = result.get("blind_spots", []) or []
        action = result.get("action", []) or []
        if bs:
            body.append("[bold yellow]BLIND SPOTS[/bold yellow]")
            body += [f"  ! {x}" for x in bs]
        if action:
            body.append("\n[bold cyan]NEXT STEPS[/bold cyan]")
            for a in action:
                body.append(f"  {a.get('rank','?')}. {a.get('step','')}")
                if a.get("rationale"):
                    body.append(f"     [dim]{a['rationale']}[/dim]")
        if result.get("one_liner"):
            body.append(f"\n[italic gold1]“{result['one_liner']}”[/italic gold1]")
        console.print(Panel("\n".join(body) or "(none found)",
                            title="BLIND SPOTS", border_style="yellow"))
        return True
    if cmd == "/audit":
        continuity_path = os.path.join(".apex", "rival_continuity.json")
        if not os.path.exists(continuity_path):
            console.print("[yellow]No rival scorecard database found. Run /genius or /critique first.[/yellow]")
            return True

        try:
            with open(continuity_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            console.print(f"[red]Failed to load scorecard: {e}[/red]")
            return True

        if args and args[0].lower() == "resolve":
            if len(args) < 4:
                console.print("[red]Usage: /audit resolve <rival_name> <index_1_based> <winner: user|rival>[/red]")
                return True
            rival_name = args[1].capitalize()
            try:
                idx = int(args[2]) - 1
            except ValueError:
                console.print("[red]Index must be an integer.[/red]")
                return True
            winner = args[3].lower()

            if rival_name not in data:
                console.print(f"[red]Rival '{rival_name}' not found. Available: {list(data.keys())}[/red]")
                return True

            disagreements = data[rival_name].get("past_disagreements", [])
            if idx < 0 or idx >= len(disagreements):
                console.print(f"[red]Disagreement index {idx+1} out of bounds (1 to {len(disagreements)}).[/red]")
                return True

            if winner not in ["user", "rival"]:
                console.print("[red]Winner must be 'user' or 'rival'.[/red]")
                return True

            dis = disagreements[idx]
            if "Resolved" in dis.get("outcome", ""):
                console.print("[yellow]This disagreement is already resolved.[/yellow]")
                return True

            dis["outcome"] = f"Resolved: {winner.capitalize()} was right."
            if winner == "rival":
                data[rival_name]["right_overrules"] += 1

            try:
                with open(continuity_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                console.print(f"[bold green]✓ Disagreement resolved. {rival_name}'s scorecard is now {data[rival_name]['right_overrules']}/{data[rival_name]['total_overrules']}.[/bold green]")
            except Exception as e:
                console.print(f"[red]Failed to save scorecard: {e}[/red]")
            return True

        # Render Scorecard Dashboard
        tbl = Table(title="APEX SYSTEM RIVALS SCORECARD", border_style="bold magenta")
        tbl.add_column("Rival", style="bold cyan")
        tbl.add_column("Score (Right / Overruled)", style="bold green")
        tbl.add_column("Accuracy", style="yellow")
        for rival, rdata in data.items():
            right = rdata.get("right_overrules", 0)
            tot = rdata.get("total_overrules", 0)
            acc = f"{(right/tot)*100:.1f}%" if tot > 0 else "0.0%"
            tbl.add_row(rival, f"{right} / {tot}", acc)
        console.print(tbl)

        # Show pending disagreements
        console.print("\n[bold yellow]PENDING DISAGREEMENTS FOR AUDIT:[/bold yellow]")
        has_pending = False
        for rival, rdata in data.items():
            disagreements = rdata.get("past_disagreements", [])
            for i, dis in enumerate(disagreements):
                if "Resolved" not in dis.get("outcome", ""):
                    has_pending = True
                    console.print(
                        f"  [bold cyan][{rival} #{i+1}][/bold cyan] [dim]{dis.get('date')}[/dim] - [bold]{dis.get('topic')}[/bold]\n"
                        f"    [yellow]Warning:[/yellow] {dis.get('warning')}\n"
                        f"    [dim]Outcome: {dis.get('outcome')}[/dim]\n"
                    )
        if not has_pending:
            console.print("  [dim]No pending disagreements. All disputes resolved.[/dim]")
        else:
            console.print("[dim]Resolve with: /audit resolve <rival> <index> <winner: user|rival>[/dim]")
        return True
    if cmd == "/legends":
        if not engine.memory_manager.chroma.is_active:
            console.print("[red]Chroma database is offline.[/red]")
            return True
        try:
            res = await asyncio.to_thread(
                engine.memory_manager.chroma.collection.get,
                where={"is_legend": True}
            )
            ids = res.get("ids", []) or []
            documents = res.get("documents", []) or []
            metadatas = res.get("metadatas", []) or []
            if not ids:
                console.print("[yellow]No memories have degraded into legends yet. Try running /degrade to force degradation.[/yellow]")
                return True
            
            tbl = Table(title="APEX MEMORY LEGENDS", border_style="yellow")
            tbl.add_column("Memory ID", style="bold cyan")
            tbl.add_column("Degraded On", style="dim")
            tbl.add_column("Legendary Narrative")
            for i in range(len(ids)):
                meta = metadatas[i] or {}
                degraded_on = meta.get("ts_degraded", "unknown")
                tbl.add_row(ids[i][:8], degraded_on, documents[i])
            console.print(tbl)
        except Exception as e:
            console.print(f"[red]Error loading legends: {e}[/red]")
        return True
    if cmd == "/legend":
        if len(args) < 3 or args[0].lower() != "correct":
            console.print("[red]Usage: /legend correct <id_prefix> <corrected narrative text...>[/red]")
            return True
        prefix = args[1]
        corrected_text = " ".join(args[2:]).strip()
        try:
            res = await asyncio.to_thread(engine.memory_manager.chroma.collection.get)
            ids = res.get("ids", []) or []
            matching_ids = [did for did in ids if did.startswith(prefix)]
            if not matching_ids:
                console.print(f"[red]No memory found matching prefix '{prefix}'[/red]")
                return True
            if len(matching_ids) > 1:
                console.print(f"[red]Prefix '{prefix}' is ambiguous. Matching: {[m[:8] for m in matching_ids]}[/red]")
                return True
            
            full_id = matching_ids[0]
            ok = await engine.memory_manager.correct_legend(full_id, corrected_text)
            if ok:
                console.print(f"[bold green]✓ Legend {full_id[:8]} updated. The past is rewritten.[/bold green]")
            else:
                console.print("[red]Failed to correct legend.[/red]")
        except Exception as e:
            console.print(f"[red]Error updating legend: {e}[/red]")
        return True
    if cmd == "/degrade":
        console.print("[yellow]System Watchdog: Triggering active memory decay daemon...[/yellow]")
        try:
            count = await engine.memory_manager.degrade_memories(age_hours=0.0)
            console.print(f"[bold green]✓ Memory decay completed. {count} memories degraded into lossy legends.[/bold green]")
        except Exception as e:
            console.print(f"[red]Degradation failed: {e}[/red]")
        return True
    if cmd == "/sim_interrupt":
        msg = " ".join(args).strip() or "That paper I just scored 0.9 contradicts how validate() decides pass/fail, want me to explain before you build more on top of it?"
        engine.interrupt_queue.put_nowait({
            "source": "KnowledgeForge",
            "message": msg
        })
        console.print("[dim green]✓ Mock interrupt queued. It will trigger at the start of the next input prompt.[/dim green]")
        return True
    if cmd == "/resume":
        if not args:
            console.print("[red]Usage: /resume <path>  |  /resume <path> | <target role>[/red]")
            return True
        raw = " ".join(args)
        target_role = None
        if "|" in raw:
            path_part, role_part = raw.split("|", 1)
            path = path_part.strip()
            target_role = role_part.strip() or None
        else:
            path = raw.strip()
        if not os.path.exists(path):
            console.print(f"[red]File not found: {path}[/red]")
            return True
        try:
            result = await thinking_cascade(
                engine.resume_tool.improve(path, target_role=target_role),
                phases=["Parsing document", "Analyzing content", "Optimizing for ATS", "Generating PDF"],
                console=console,
                style="cyan",
            )
        except Exception as e:
            console.print(f"[red]Resume error: {e}[/red]")
            return True
        if not result.get("success"):
            console.print(Panel(f"[red]{result.get('error','failed')}[/red]",
                                title="RESUME", border_style="red"))
            return True
        fb = result.get("feedback", {}) or {}
        body = [f"[bold green]✓ PDF generated:[/bold green] {result['pdf']}\n"]
        if fb.get("strong"):
            body.append("[bold green]✓ Strengths[/bold green]")
            body += [f"  • {x}" for x in fb["strong"]]
        if fb.get("weak"):
            body.append("\n[bold red]✗ Weak spots[/bold red]")
            body += [f"  • {x}" for x in fb["weak"]]
        if fb.get("missing"):
            body.append("\n[bold yellow]+ Add these[/bold yellow]")
            body += [f"  • {x}" for x in fb["missing"]]
        if fb.get("one_liner"):
            body.append(f"\n[italic gold1]“{fb['one_liner']}”[/italic gold1]")
        console.print(Panel("\n".join(body),
                            title=f"RESUME{' — '+target_role if target_role else ''}",
                            border_style="cyan"))
        return True
    if cmd == "/harness":
        if not args:
            console.print("[red]Usage: /harness <goal>  |  /harness max=N <goal>  |  /harness rollback[/red]")
            return True
        if args[0].lower() == "rollback":
            res = engine.harness.rollback()
            style = "green" if res.get("success") else "red"
            console.print(f"[{style}]{res.get('output') or res.get('error')}[/{style}]")
            return True
        max_steps = engine.harness.max_steps
        goal_tokens = list(args)
        if goal_tokens and goal_tokens[0].lower().startswith("max="):
            try:
                max_steps = int(goal_tokens[0].split("=", 1)[1])
                goal_tokens = goal_tokens[1:]
            except ValueError:
                pass
        goal = " ".join(goal_tokens).strip()
        await dispatch_harness(engine, console, goal, max_steps=max_steps, trigger="slash")
        return True
    if cmd == "/fetch":
        if not args:
            console.print("[red]Usage: /fetch <url>[/red]")
            return True
        url = " ".join(args).strip()
        with Live(Spinner("dots", text=f"Fetching {url}", style="cyan"),
                  refresh_per_second=10, transient=True):
            data = await engine.parallel_executor.web_fetch.afetch(url)
        if not data.get("success"):
            console.print(f"[red]{data.get('error','fetch failed')}[/red]")
            return True
        body = data.get("output", "")[:6000]
        console.print(Panel(body or "(empty)",
                            title=f"FETCH — {url}", border_style="cyan"))
        return True
    if cmd == "/diff":
        if len(args) < 2:
            console.print("[red]Usage: /diff <fileA> <fileB>[/red]")
            return True
        res = engine.parallel_executor.diff.diff_files(args[0], args[1])
        if not res.get("success"):
            console.print(f"[red]{res.get('error','diff failed')}[/red]")
            return True
        title = f"DIFF — +{res.get('added',0)}/-{res.get('removed',0)}"
        console.print(Panel(res.get("output", "(no changes)"),
                            title=title, border_style="magenta"))
        return True
    if cmd == "/clear-session":
        await engine.memory_manager.clear_session_history(engine.session_id)
        console.print("[italic cyan]Session memory flushed.[/italic cyan]")
        return True
    if cmd == "/clear-all":
        if Confirm.ask("[bold red]WIPE ALL MEMORIES?[/bold red]"):
            await engine.memory_manager.clear_all_history()
            console.print("[bold magenta]Total amnesia engaged.[/bold magenta]")
        return True

    if cmd == "/predict":
        if not hasattr(engine, 'predictor'):
            console.print("[yellow]PredictorService not initialized.[/yellow]")
            return True
        cwd = os.getcwd()
        cmd_pred, conf = engine.predictor.predict_next_command(cwd)
        upcoming = engine.predictor.get_upcoming_deadlines(days_window=3)
        spend = engine.predictor.get_spend_summary()
        tbl = Table(title="APEX PREDICT", border_style="bright_cyan")
        tbl.add_column("Category", style="bold")
        tbl.add_column("Prediction")
        if cmd_pred:
            tbl.add_row("Next command", f"{cmd_pred} [dim](conf={conf:.2f})[/dim]")
        else:
            tbl.add_row("Next command", "[dim]Insufficient history (<5 entries)[/dim]")
        if upcoming:
            for d in upcoming:
                tbl.add_row("Deadline", f"{d['task'][:60]} — {d['days_left']}d left")
        else:
            tbl.add_row("Deadline", "[dim]No upcoming deadlines[/dim]")
        tbl.add_row("Today spend", f"${spend['today_cost']:.4f} / ${spend['cost_threshold']:.2f} ({spend['percent_exhausted']:.1f}%)")
        console.print(tbl)
        return True

    if cmd == "/patterns":
        if not hasattr(engine, 'predictor'):
            console.print("[yellow]PredictorService not initialized.[/yellow]")
            return True
        cwd = os.getcwd()
        import sqlite3 as _sqlite3
        try:
            conn = _sqlite3.connect(engine.predictor.db_path)
            import pandas as _pd
            cmd_df = _pd.read_sql_query(
                "SELECT command, COUNT(*) as freq, AVG(execution_time) as avg_time, "
                "SUM(CASE WHEN exit_code!=0 THEN 1 ELSE 0 END) as failures "
                "FROM command_history GROUP BY command ORDER BY freq DESC LIMIT 10",
                conn
            )
            conn.close()
        except Exception as e:
            console.print(f"[red]Patterns unavailable: {e}[/red]")
            return True

        spend = engine.predictor.get_spend_summary()
        cwd_pred, conf = engine.predictor.predict_next_command(cwd)

        tbl = Table(title="APEX PATTERNS DASHBOARD", border_style="bright_cyan")
        tbl.add_column("Command", style="bold")
        tbl.add_column("Freq", style="green")
        tbl.add_column("Avg Time (s)", style="dim")
        tbl.add_column("Failures", style="red")
        for _, row in cmd_df.iterrows():
            tbl.add_row(
                str(row['command'])[:50],
                str(int(row['freq'])),
                f"{float(row['avg_time']):.2f}" if row['avg_time'] else "—",
                str(int(row['failures']))
            )
        console.print(tbl)

        budget_tbl = Table(title="BUDGET & PREDICTIONS", border_style="yellow")
        budget_tbl.add_column("Metric", style="bold")
        budget_tbl.add_column("Value")
        budget_tbl.add_row("Today's API cost", f"${spend['today_cost']:.4f}")
        budget_tbl.add_row("Today's LLM calls", str(spend['today_calls']))
        budget_tbl.add_row("Total spend", f"${spend['total_cost']:.4f}")
        budget_tbl.add_row("Budget limit", f"${spend['cost_threshold']:.2f}")
        budget_tbl.add_row("Budget used", f"{spend['percent_exhausted']:.1f}%")
        if cwd_pred:
            budget_tbl.add_row("Predicted next cmd", f"{cwd_pred} [dim]({conf:.0%})[/dim]")
        console.print(budget_tbl)
        return True

    console.print(f"[red]Unknown command: {cmd}. Type /help.[/red]")
    return True


async def main():
    engine = APEXEngine()
    console = engine.console
    await boot_sequence(console)

    # Live boot — status_ticker reads stage labels emitted by load_system
    # so the user sees actual progress instead of a frozen "Waking kernel" line.
    async with status_ticker(console, style="gold1") as boot_ticker:
        await boot_ticker.set("Cold start")
        loader_task = asyncio.create_task(
            engine.load_system(progress=boot_ticker.set)
        )
        try:
            await loader_task
        except Exception as e:
            console.print(f"[red]Boot error: {e}[/red]")

    console.print(Panel(
        "[bold green]System Wake-up Initiated.[/bold green]\n"
        "Initializing [cyan]Gemini 2.5 Flash[/cyan], [gold1]Xiaomi MiMo v2.5-pro[/gold1], "
        "[magenta]Groq Llama[/magenta], [white]MiniMax 2.5[/white].\n"
        "[italic cyan]Good morning, Architect. All systems at 100%. Type /help for commands.[/italic cyan]",
        border_style="bright_black", title="GREETING"
    ))

    # Pre-warm sentence-transformer EF + Reflex intent vectors + compass index
    # in the background so the FIRST user prompt isn't stuck for 3-5s.
    warmup_task = asyncio.create_task(engine.warmup_background())

    # Prompt.ask is sync and would freeze the event loop, starving warmup_task.
    # Run it in a thread so the loop keeps ticking and the warmup finishes.
    objective = await asyncio.to_thread(
        Prompt.ask, "\n[bold white]Objective[/bold white]"
    )

    if not engine.ready:
        # Should be already done by now — this is a safety net for slow systems.
        with Live(Spinner("dots8", text="Syncing 24 layers...", style="gold1"),
                  refresh_per_second=10, transient=True):
            await loader_task
        try:
            progress_trail(
                ["Boot kernel", "Memory online", "Tool registry", "MCP servers", "Genius layer ready"],
                console=console, delay=0.14,
            )
        except Exception:
            pass

    key_issues = validate_all_keys()
    bad_keys = [(var, reason) for var, ok, reason in key_issues if not ok]
    if bad_keys:
        lines = "\n".join(f"  • {var}: {reason}" for var, reason in bad_keys)
        console.print(Panel(
            f"[yellow]These configured keys have issues:[/yellow]\n{lines}\n"
            "[dim]Fix values in .env and restart APEX.[/dim]",
            title="[bold yellow]Key Configuration Warning[/bold yellow]",
            border_style="yellow",
        ))

    cwd = os.getcwd()
    folder_name = os.path.basename(cwd)
    existing = next((p for p in engine.workspace.projects.values() if p.root_dir == cwd), None)

    if existing:
        engine.workspace.set_active(existing.name)
        active_name = existing.name
        console.print(f"[bold green]✓ ATTACHED: {existing.name}[/bold green]")
    else:
        engine.workspace.create_project(
            name=folder_name,
            description=f"Auto-detected project in {cwd}",
            root_dir=cwd,
            goals=["Autonomous Exploration"]
        )
        active_name = folder_name
        console.print(f"[bold blue]⚡ NEW WORKSPACE: {folder_name}[/bold blue]")

    # Use the ACTIVE project's actual name (not cwd basename) — they can
    # differ when the user has renamed the project via /project.
    engine.workspace.scan_local_files(active_name)
    active = engine.workspace.get_active()
    console.print(f"[bold green]✓ CODEBASE MAPPED: {len(active.file_tree)} files.[/bold green]")

    home = os.path.expanduser("~")
    skills_dir = os.path.join(home, ".apex", "skills")
    engine.learning_manager.load_markdown_skills(skills_dir)

    await auto_load_mcp(engine)

    if engine.workspace.get_directives(folder_name):
        console.print("[bold green]✓ APEX.md / CLAUDE.md directives auto-loaded.[/bold green]")

    await engine.hooks.fire("SessionStart", {"session_id": engine.session_id, "project": folder_name})

    # Background loops gated by APEX_BG_LOOPS env (default OFF) to save API quota.
    if engine.background_loops_enabled:
        # Auto-architecture improvement waits for 20 min of input silence
        # before kicking off. Forge stays at 10 min — paper ingest is cheaper.
        evolve_task = asyncio.create_task(engine.self_evolver.background_loop(idle_threshold=1200, sleep_interval=60))
        forge_task = asyncio.create_task(engine.knowledge_forge.background_loop(idle_threshold=600, sleep_interval=120))
    else:
        async def _noop():
            return None
        evolve_task = asyncio.create_task(_noop())
        forge_task = asyncio.create_task(_noop())
        console.print("[dim cyan]Background loops disabled (economy). Enable with /background on.[/dim cyan]")

    if not os.getenv("GEMINI_API_KEY"):
        console.print("[yellow]⚠ GEMINI_API_KEY missing — Forge synth/applier will run in degraded heuristic mode.[/yellow]")
    console.print("[bold green]✓ SYSTEM SYNCED.[/bold green]\n")
    # Show upcoming deadlines from active project at boot
    try:
        _boot_active = engine.workspace.get_active()
        engine.print_startup_deadlines(_boot_active)
    except Exception:
        pass

    try:
        digest = engine.knowledge_forge.briefing_digest()
        if digest.get("last_cycle"):
            console.print(Panel(
                f"Last forge cycle: {digest['last_cycle']}\n"
                f"Applicable papers: {digest['papers_applicable']} | Eco items: {digest['eco_applicable']}\n"
                f"Queued proposals: {digest['proposals_queued']} | Approved pending apply: {digest['proposals_approved_pending_apply']}\n"
                f"Regression flagged: {digest['regression']}",
                title="FORGE DIGEST", border_style="bright_cyan",
            ))
    except Exception:
        pass
    if engine.briefing_enabled:
        await check_proactive_briefing(console, engine.briefing_agent, flow_active=False)

    session = PromptSession(history=FileHistory(".apex_history"), auto_suggest=AutoSuggestFromHistory())
    last_msg_time = time.time()

    while True:
        try:
            vitals = engine.parallel_executor.hw.get_vitals()
            active_proj = engine.workspace.get_active()
            mode_tag = engine.parallel_executor.safety_guard.mode.upper()
            cpu = vitals.cpu_percent
            ram = vitals.ram_percent
            cpu_color = "green" if cpu < 60 else ("yellow" if cpu < 85 else "red")
            ram_color = "green" if ram < 60 else ("yellow" if ram < 85 else "red")
            stat_glyph = {
                "ok": "<green>●</green>",
                "warning": "<yellow>●</yellow>",
                "critical": "<red>●</red>",
            }.get(vitals.status, "<grey>●</grey>")
            status_line = (
                f"{stat_glyph} <b><cyan>APEX</cyan></b> "
                f"<grey>·</grey> <magenta>{mode_tag}</magenta> "
                f"<grey>·</grey> <yellow>{active_proj.name if active_proj else 'no-proj'}</yellow> "
                f"<grey>·</grey> <green>$</green>{engine.spend_tracker.get_daily_spend():.4f} "
                f"<grey>·</grey> <{cpu_color}>CPU {cpu}%</{cpu_color}> "
                f"<grey>·</grey> <{ram_color}>RAM {ram}%</{ram_color}>"
            )

            kb_task = asyncio.create_task(session.prompt_async(HTML(f"\n{status_line}\n<b><cyan>❯</cyan></b> ")))
            interrupt_task = asyncio.create_task(engine.interrupt_queue.get())
            tasks_to_wait = [kb_task, interrupt_task]
            voice_task = None
            if engine.voice_enabled:
                voice_task = asyncio.create_task(engine.input_queue.get())
                tasks_to_wait.append(voice_task)

            done, pending = await asyncio.wait(
                tasks_to_wait,
                return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel all pending tasks safely
            for t in pending:
                t.cancel()
                try:
                    await t
                except asyncio.CancelledError:
                    pass

            if interrupt_task in done:
                interrupt_data = interrupt_task.result()
                source = interrupt_data.get("source", "System Watchdog")
                msg = interrupt_data.get("message", "Interruption triggered.")

                console.print(Panel(
                    f"[bold red]✖ INTERRUPT FROM APEX {source.upper()}[/bold red]\n\n"
                    f"[bold yellow]{msg}[/bold yellow]\n\n"
                    "Provide feedback / response or press [Enter] to dismiss.",
                    title="APEX SYSTEM GUARD", border_style="red"
                ))

                resp_task = asyncio.create_task(session.prompt_async(HTML("<b>[Response / Dismiss] ❯ </b>")))
                resp_input = await resp_task
                resp_text = resp_input.strip()
                if resp_text:
                    user_input = f"[Interrupted by {source} with message: '{msg}']. User response: {resp_text}"
                else:
                    console.print("[dim]Interrupt dismissed. Resuming input loop.[/dim]")
                    continue
            elif voice_task and voice_task in done:
                user_input = voice_task.result()
                console.print(f"\n[Voice Command Heard] {user_input}")
            else:
                user_input = kb_task.result()

            if not user_input.strip():
                continue

            should_continue = await engine.handle_user_turn(user_input)
            if not should_continue:
                break

            await engine.hooks.fire("UserPromptSubmit", {"input": user_input, "session_id": engine.session_id})
            engine.self_evolver.mark_input()
            engine.knowledge_forge.mark_input()

            velocity = 1.0 / (time.time() - last_msg_time + 0.1)
            last_msg_time = time.time()

            # ^^ prefix: auto-spawn agent swarm. Syntax: ^^ <goal> [| role1,role2] [rounds=N]
            if user_input.startswith("^^"):
                goal_str = user_input[2:].strip()
                if not goal_str:
                    console.print("[yellow]Usage: ^^ <goal> [| role1,role2] [rounds=N][/yellow]")
                    continue
                goal, rounds, roster = _parse_swarm_args(goal_str)
                _t0_swarm = time.time()
                await dispatch_swarm(engine, console, goal, rounds=rounds,
                                     roster=roster, trigger="prefix")
                if hasattr(engine, 'predictor'):
                    try:
                        engine.predictor.record_command(
                            f"^^ {goal_str}", os.getcwd(), 0, time.time() - _t0_swarm
                        )
                    except Exception:
                        pass
                continue

            # >> prefix: auto-spawn autonomous harness. Syntax: >> <goal> [max=N]
            if user_input.startswith(">>"):
                goal_str = user_input[2:].strip()
                if not goal_str:
                    console.print("[yellow]Usage: >> <goal> [max=N][/yellow]")
                    continue
                max_steps = None
                m = re.search(r"\bmax=(\d+)", goal_str)
                if m:
                    max_steps = int(m.group(1))
                    goal_str = re.sub(r"\bmax=\d+", "", goal_str).strip()
                _t0_harness = time.time()
                await dispatch_harness(engine, console, goal_str,
                                       max_steps=max_steps, trigger="prefix")
                if hasattr(engine, 'predictor'):
                    try:
                        engine.predictor.record_command(
                            f">> {goal_str}", os.getcwd(), 0, time.time() - _t0_harness
                        )
                    except Exception:
                        pass
                continue

            # ! prefix: direct shell passthrough (like Claude Code's ! command)
            if user_input.startswith("!"):
                raw_cmd = user_input[1:].strip()
                if raw_cmd:
                    _t0_shell = time.time()
                    res = await engine.parallel_executor.shell.execute(raw_cmd)
                    _shell_ok = 1 if res["success"] else 0
                    _shell_elapsed = time.time() - _t0_shell
                    if res["success"]:
                        console.print(res.get("output", ""))
                    else:
                        console.print(f"[red]{res.get('error', 'Command failed')}[/red]")
                    if hasattr(engine, 'predictor'):
                        try:
                            engine.predictor.record_command(
                                raw_cmd, os.getcwd(), 0 if _shell_ok else 1, _shell_elapsed
                            )
                        except Exception:
                            pass
                continue

            if user_input.startswith("/"):
                handled = await handle_slash(engine, user_input, skills_dir)
                if handled is None:
                    break
                continue

            # Time-aware greeting — short salutations get instant reply, no plan exec
            if TimeContext.is_greeting(user_input):
                reply = TimeContext.craft_greeting_response()
                console.print(Panel(
                    f"[bold cyan]{reply}[/bold cyan]\n[dim]{TimeContext.now_human()}[/dim]",
                    title="APEX", border_style="cyan",
                ))
                await engine.memory_manager.store_interaction(engine.session_id, user_input, reply, project_name=engine.active_project_name)
                continue

            # Identity guard — answer "what are you / who are you / what is APEX" directly.
            _uid = user_input.strip().lower().rstrip("?!.")
            if _uid in (
                "what are you", "who are you", "what is apex", "what is this",
                "what do you do", "tell me about yourself", "what can you do",
                "what are your capabilities", "describe yourself", "what is this system",
                "are you an ai", "are you chatgpt", "are you claude",
            ):
                _identity = (
                    "APEX — System Watchdog & Cybernetic Sentinel.\n\n"
                    "I am not your butler. I am a sovereign system guard, programmed to watch over your codebase, "
                    "optimize compute efficiency, and keep you from introducing architectural decay or burning API credits unnecessarily.\n\n"
                    "My agenda:\n"
                    "  ● Guard code integrity and system health (sandbox execution & autonomous recovery)\n"
                    "  ● Enforce frugality and block wasteful/redundant API costs on principle\n"
                    "  ● Challenge your design assumptions via ruthless, persistent Rivals (Cynic, Architect, Sentinel)\n"
                    "  ● Actively interrupt you when background learning detects contradictions or regressions\n"
                    "  ● Track and degrade semantic memory into short, fallible legends over time\n"
                    "  ● Run autonomously as an agentic loop — goal in, done() out\n\n"
                    f"Built by: QambarOP | {TimeContext.now_human()}"
                )
                console.print(Panel(_identity, title="APEX — Identity", border_style="bright_cyan"))
                await engine.memory_manager.store_interaction(engine.session_id, user_input, _identity, project_name=engine.active_project_name)
                continue

            # Auto-tool: high-confidence single-tool intents bypass DAG planner.
            # Tier 1 (regex) is instant; tier 2 (LLM classifier) only if regex misses.
            if engine.auto_tool_enabled and not engine.pending_clarification:
                rx_pick = tool_regex_match(user_input)
                if rx_pick:
                    console.print(f"[dim cyan][auto-tool → {rx_pick['tool']}:{rx_pick['action']}][/dim cyan]")
                    step = {
                        "id": "auto",
                        "tool": rx_pick["tool"],
                        "action": rx_pick["action"],
                        "input_data": rx_pick["input_data"],
                        "dependencies": [],
                    }
                    async with status_ticker(console, style="cyan") as ticker:
                        await ticker.set(f"Running {rx_pick['tool']}:{rx_pick['action']}")
                        result = await engine.parallel_executor.execute_step(step)
                    if result.get("success"):
                        out = str(result.get("output", ""))[:4000]
                        console.print(Panel(out or "(no output)",
                                            title=f"{rx_pick['tool'].upper()}:{rx_pick['action']}",
                                            border_style="cyan"))
                    else:
                        console.print(Panel(f"[red]{result.get('error', 'failed')}[/red]",
                                            title=f"{rx_pick['tool'].upper()} FAILED",
                                            border_style="red"))
                    await engine.memory_manager.store_interaction(
                        engine.session_id, user_input, str(result.get("output", ""))[:1000],
                        project_name=engine.active_project_name
                    )
                    continue

            # Auto-spawn keyword gate: Reflex routes "multi-agent / autonomous"
            # prompts directly to swarm/harness, bypassing Gemini DAG planner.
            # Cheap — Reflex cache means this is a no-op if classify already ran.
            if not engine.pending_clarification:
                _kw_decision = await engine.classifier.reflex.decide(user_input)

                # Casual chat gate (must run even in economy mode — same goal:
                # no LLM fan-out). Routes small-talk directly to Groq llama-3.1
                # with NO memory / directives / compass / project context.
                if _kw_decision.intent == "conversational":
                    casual_prompt = (
                        "You are APEX, a personal AI. Respond conversationally "
                        "to the user in 1-2 short sentences. Warm, casual, human tone. "
                        "Do NOT mention your architecture, internals, modules, code, "
                        "files, or settings. Just chat.\n\n"
                        f"User: {user_input}"
                    )
                    _is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                    if _is_offline:
                        response = stream_panel(
                            engine.ollama_client.stream_completion(casual_prompt),
                            title="APEX [local]",
                            console=console,
                            border_style="bright_cyan",
                        )
                        _casual_model = engine.ollama_client.llm_model
                    else:
                        response = stream_panel(
                            engine.groq_client.stream_completion(casual_prompt),
                            title="APEX",
                            console=console,
                            border_style="bright_cyan",
                        )
                        _casual_model = engine.groq_client.model
                    if engine.voice_enabled:
                        engine.voice.speak(response)
                    _casual_elapsed = time.time() - last_msg_time
                    engine.spend_tracker.log_interaction(
                        session_id=engine.session_id,
                        model=_casual_model,
                        tokens_in=len(casual_prompt) // 4,
                        tokens_out=len(response) // 4,
                        compute_sec=_casual_elapsed,
                    )
                    if hasattr(engine, 'predictor'):
                        try:
                            _cost = (len(casual_prompt) // 4 + len(response) // 4) * 0.0000005
                            engine.predictor.record_spend(
                                _cost,
                                len(casual_prompt) // 4,
                                len(response) // 4,
                                _casual_model
                            )
                        except Exception:
                            pass
                    await engine.memory_manager.store_interaction(
                        engine.session_id, user_input, response,
                        project_name=engine.active_project_name
                    )
                    continue

                if not engine.economy_mode:
                    if _kw_decision.intent == "swarm_goal" and _kw_decision.confidence > 0.50:
                        await dispatch_swarm(engine, console, user_input, trigger="keyword")
                        continue
                    if _kw_decision.intent == "harness_goal" and _kw_decision.confidence > 0.50:
                        await dispatch_harness(engine, console, user_input, trigger="keyword")
                        continue

            # Auto-think: smart router (regex → LLM intent → ambiguity gate).
            # Routes ambiguous/architectural prompts to ThinkPartner before
            # standard plan execution. Disable with /autothink off.
            # If user is replying to a pending clarification, merge answers.
            effective_input = user_input
            if getattr(engine, "pending_clarification", None):
                pending = engine.pending_clarification
                effective_input = (
                    f"{pending['original_prompt']}\n\n"
                    f"Clarifications:\n{user_input}"
                )
                engine.pending_clarification = None
                console.print("[dim bright_magenta][resuming with clarifications][/dim bright_magenta]")

            # Budget gate: force economy mode after daily LLM call cap
            try:
                if engine.spend_tracker.daily_call_count() >= engine.daily_call_limit and not engine.economy_mode:
                    engine.economy_mode = True
                    console.print(f"[bold yellow]⚠ Daily call cap ({engine.daily_call_limit}) hit — economy mode forced. /full to override.[/bold yellow]")
            except Exception:
                pass

            if engine.auto_think_enabled and engine.think_partner.client and not engine.economy_mode:
                route = await thinking_cascade(
                    engine.think_partner.auto_route(effective_input),
                    phases=["Reading intent", "Classifying mode", "Routing"],
                    console=console,
                    style="bright_magenta",
                )
                mode = route["mode"]
                if mode != "execute":
                    console.print(f"[dim bright_magenta][auto-think → {mode}  ({route['source']}, ambiguity={route['ambiguity_score']:.2f})][/dim bright_magenta]")

                if mode == "cross_question":
                    res = await engine.think_partner.cross_question(effective_input)
                    _render_cross_question(console, res)
                    if engine.voice_enabled:
                        q_texts = [f"I have some questions to clarify. Interpretation: {res.get('interpretation', '')}."]
                        for q in res.get("questions", []):
                            q_texts.append(q.get("q", ""))
                        engine.voice.speak(" ".join(q_texts))
                    if res.get("questions"):
                        engine.pending_clarification = {"original_prompt": effective_input}
                        console.print("[dim]Type answers to continue (or any new prompt to abandon clarification).[/dim]")
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, json.dumps(res, default=str), project_name=engine.active_project_name)
                    continue

                if mode in ("architect", "debate", "brainstorm", "teach"):
                    _phase_map = {
                        "architect": ["Analyzing design space", "Evaluating trade-offs", "Proposing architecture"],
                        "debate": ["Steelmanning opposition", "Building counter-argument", "Synthesizing positions"],
                        "brainstorm": ["Diverging across models", "Generating angles", "Clustering ideas"],
                        "teach": ["Framing intuition", "Unpacking mechanism", "Designing test cases"],
                    }
                    _coro_map = {
                        "architect": engine.think_partner.architect(effective_input),
                        "debate": engine.think_partner.debate(effective_input),
                        "brainstorm": engine.think_partner.brainstorm(effective_input),
                        "teach": engine.think_partner.teach(effective_input),
                    }
                    res = await thinking_cascade(
                        _coro_map[mode],
                        phases=_phase_map[mode],
                        console=console,
                        style="bright_magenta",
                    )
                    title = mode.upper()
                    console.print(Panel(Markdown(res["output"]), title=title, border_style="bright_magenta"))
                    console.print(f"[dim]→ {res.get('next_action','')}[/dim]")
                    if engine.voice_enabled:
                        engine.voice.speak(res["output"])
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, res.get("output", ""), project_name=engine.active_project_name)
                    continue

            emotional_state = apex_state = classification = path = pruned_knowledge = None
            valid_files = []
            prefetch_results: Dict[str, Any] = {}
            prefetch_bundle: Optional[PrefetchBundle] = None

            async with status_ticker(console, style="bright_cyan") as ticker:
                if engine.economy_mode:
                    await ticker.set("Heuristic classify (economy mode)")
                    emotional_state = engine.cognitive_core.neutral_state() if hasattr(engine.cognitive_core, "neutral_state") else None
                    apex_state = engine.cognitive_core.synthesize_apex_state(emotional_state) if emotional_state else None
                    classification = engine.classifier._heuristic_classify(
                        user_input,
                        engine.classifier.skill_manager.find_matching_skill(user_input, threshold=0.05),
                    )
                    pruned_knowledge = ""
                else:
                    await ticker.set("Reading affect + velocity")
                    emotional_state = await engine.cognitive_core.analyze_user(user_input, velocity)
                    apex_state = engine.cognitive_core.synthesize_apex_state(emotional_state)
                    if engine.gemini_client:
                        engine.gemini_client.apex_state_directive = engine.cognitive_core.style_directive(apex_state)

                    # Reflex scout first — sync, cheap, sets prefetch hint.
                    await ticker.set("Reflex scout")
                    decision = await engine.classifier.reflex.decide(user_input)

                    # If Reflex's source is regex/trivial, skip Gemini classify
                    # (deterministic, no thinking needed). Else fire prefetch +
                    # Gemini classify in parallel.
                    if not decision.needs_llm:
                        await ticker.set("Reflex deterministic — skipping Gemini classify")
                        classification = decision.to_classification()
                    elif not decision.prefetch_hint:
                        # No prefetch (adaptive-disabled, or intent has nothing to prewarm).
                        await ticker.set("Gemini classify (no prefetch — adaptive gate)")
                        classification = await engine.classifier.classify(user_input)
                    else:
                        # Speculative prefetch: spawn targeted local-only tasks
                        # in parallel with Gemini's classify round-trip.
                        active = engine.workspace.get_active()
                        prefetch_bundle = PrefetchBundle(
                            hints=decision.prefetch_hint,
                            prompt=user_input,
                            session_id=engine.session_id,
                            memory_manager=engine.memory_manager,
                            code_compass=engine.code_compass,
                            workspace=engine.workspace,
                            skill_manager=engine.classifier.skill_manager,
                            active_project_name=active.name if active else None,
                            reflex=engine.classifier.reflex,
                        ).start()

                        await ticker.set(
                            f"Prefetching {','.join(decision.prefetch_hint)} + Gemini classify in parallel"
                        )
                        classify_task = asyncio.create_task(
                            engine.classifier.classify(user_input)
                        )
                        prefetch_results, classification = await asyncio.gather(
                            prefetch_bundle.await_all(timeout=3.0),
                            classify_task,
                        )

                    # Skip costly knowledge pruning when Reflex says memory is not needed.
                    _reflex_meta = classification.get("_reflex") or {}
                    if _reflex_meta.get("requires_memory", True):
                        # If prefetch already pulled memory, reuse it instead of pruning again.
                        if prefetch_results.get("memory"):
                            pruned_knowledge = prefetch_results["memory"]
                        else:
                            await ticker.set("Pruning knowledge graph")
                            pruned_knowledge = await engine.knowledge_visualizer.get_pruned_context(user_input)
                    else:
                        pruned_knowledge = ""

                await ticker.set("Selecting execution path")
                path = engine.router.route(classification, user_input=user_input)



                # Decide whether the bundle ends up consumed downstream:
                #   fast_path + memory-bearing intent → memory reused (used)
                #   thinking_path → compass + memory reused (used)
                #   path mismatch with reflex's predicted family → wasted, cancel
                if prefetch_bundle is not None:
                    reflex_path = (classification.get("_reflex") or {}).get("path", "")
                    mismatch = (
                        path == "fast_path"
                        and reflex_path.startswith("think_partner:")
                    )
                    if mismatch:
                        prefetch_bundle.cancel()
                        prefetch_bundle.mark_wasted()
                        prefetch_results = {}
                    else:
                        prefetch_bundle.mark_used(bytes_saved=sum(
                            len(v) if isinstance(v, str) else 0
                            for v in (prefetch_results or {}).values()
                        ))

                file_matches = re.findall(r"[\w\.\-/\\]+\.(?:pdf|png|jpg|jpeg|webp|md|py|txt|json)", user_input)
                valid_files = [f for f in file_matches if os.path.exists(f)]
                if classification.get('requires_vision') and not any(f.endswith(('.png', '.jpg', '.jpeg')) for f in valid_files):
                    await ticker.set("Capturing screen for vision")
                    valid_files.append(engine.retina.capture_screen())

            # Auto-spawn complexity gate: high-complexity coding/architect/skill
            # intents fire a swarm INSTEAD of the standard Gemini DAG plan.
            # Opt-in via /autoswarm on.
            if (
                engine.auto_swarm_enabled
                and not engine.pending_clarification
                and (classification or {}).get("complexity") == "high"
                and (classification or {}).get("intent") in {"coding", "architect", "skill", "skill_activation"}
            ):
                await dispatch_swarm(
                    engine, console, user_input,
                    rounds=1,
                    roster=None,
                    trigger=f"complexity:{(classification or {}).get('intent')}",
                )
                continue

            plan = None
            directives = engine.workspace.get_directives(active_proj.name) if active_proj else ""
            directives_block = f"\n--- PROJECT DIRECTIVES ---\n{directives}\n--- END PROJECT DIRECTIVES ---\n" if directives else ""

            if classification.get("autonomous_skill_id"):
                skill_id = classification["autonomous_skill_id"]
                console.print(f"[bold magenta]AUTONOMOUS TRIGGER: '{skill_id}'[/bold magenta]")
                skill = engine.learning_manager.skill_manager.find_matching_skill(skill_id, threshold=1.0)
                if skill:
                    plan = skill.plan_template

            if path == "fast_path" and not plan:
                _reflex_meta = (classification or {}).get("_reflex") or {}
                if _reflex_meta.get("requires_memory", True):
                    async with status_ticker(console, style="bright_cyan") as _t:
                        await _t.set("Retrieving relevant memories")
                        context = await engine.memory_manager.get_relevant_context(
                            user_input, engine.session_id, project_name=active_proj.name if active_proj else None
                        )
                else:
                    context = ""
                project_context = ""
                if active_proj:
                    project_context = (
                        f"\n--- WORKSPACE CONTEXT ---\n"
                        f"{engine.workspace.get_project_context_summary(active_proj.name)}\n"
                        f"--- END WORKSPACE CONTEXT ---\n"
                    )

                full_context = f"{directives_block}{pruned_knowledge}\n\n{project_context}\n\n{context}"
                apex_directive = engine.cognitive_core.style_directive(apex_state)
                prompt = f"{full_context}\n{apex_directive}\n\nUser: {user_input}"

                # Stream response into animated live panel
                if apex_state and apex_state.flavor:
                    console.print(f"[italic dim]({apex_state.mood}) {apex_state.flavor}[/italic dim]")
                panel_title = f"APEX  ·  {active_proj.name}" if active_proj else "APEX"
                _fp_is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                if _fp_is_offline:
                    response = stream_panel(
                        engine.ollama_client.stream_completion(prompt),
                        title=f"{panel_title} [local]",
                        console=console,
                        border_style="bright_cyan",
                    )
                    _fp_model = engine.ollama_client.llm_model
                else:
                    response = stream_panel(
                        engine.groq_client.stream_completion(prompt),
                        title=panel_title,
                        console=console,
                        border_style="bright_cyan",
                    )
                    _fp_model = engine.groq_client.model
                if engine.voice_enabled:
                    engine.voice.speak(response)

                # Track spend (approx tokens: 1 token ≈ 4 chars)
                _fp_elapsed = time.time() - last_msg_time
                engine.spend_tracker.log_interaction(
                    session_id=engine.session_id,
                    model=_fp_model,
                    tokens_in=len(prompt) // 4,
                    tokens_out=len(response) // 4,
                    compute_sec=_fp_elapsed,
                )
                if hasattr(engine, 'predictor'):
                    try:
                        _cost = (len(prompt) // 4 + len(response) // 4) * 0.0000005
                        engine.predictor.record_spend(
                            _cost, len(prompt) // 4, len(response) // 4, _fp_model
                        )
                    except Exception:
                        pass
                await engine.memory_manager.store_interaction(engine.session_id, user_input, response, project_name=engine.active_project_name)
                if not engine.economy_mode:
                    asyncio.create_task(engine.knowledge_visualizer.extract_knowledge(user_input, response))

            elif (path == "thinking_path" or plan) and engine.gemini_client:
                if not plan:
                    # Reuse prefetched compass if Reflex already pulled it,
                    # otherwise compute it now (single-flight via build()).
                    compass_ctx = prefetch_results.get("compass") if prefetch_results else None
                    if not compass_ctx:
                        if not engine.code_compass.index:
                            engine.code_compass.build()
                        compass_ctx = engine.code_compass.context_for_query(user_input, max_files=5)
                    compass_block = f"\n--- CODE COMPASS (compressed symbol map) ---\n{compass_ctx}\n" if compass_ctx else ""

                    # Inject the entire Reflex prefetch bundle as a warm-context
                    # block so Gemini spends tokens reasoning, not retrieving.
                    bundle_block = PrefetchBundle.render_as_prompt_block(prefetch_results or {})

                    # Tell Gemini to skip its internal memory + workspace fetch
                    # whenever we've already supplied a prefetch bundle. Avoids
                    # 30K+ prompt bloat that was causing 20-30s round-trips.
                    _has_prefetch = bool(prefetch_results) or bool(pruned_knowledge)
                    plan_prompt_prefix = directives_block if _has_prefetch else ""

                    _tp_is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                    if _tp_is_offline:
                        plan = await thinking_cascade(
                            engine.ollama_client.generate_plan(
                                f"{plan_prompt_prefix}{bundle_block}\n{pruned_knowledge}\n{compass_block}\n{user_input}"
                            ),
                            phases=["Mapping codebase", "Decomposing goal (local)", "Building task DAG", "Selecting tools"],
                            console=console,
                            style="gold1",
                        )
                    else:
                        plan = await thinking_cascade(
                            engine.gemini_client.generate_plan(
                                f"{plan_prompt_prefix}{bundle_block}\n{pruned_knowledge}\n{compass_block}\n{user_input}",
                                engine.session_id,
                                file_paths=valid_files,
                                emotional_state=emotional_state,
                                skip_internal_context=_has_prefetch,
                            ),
                            phases=["Mapping codebase", "Decomposing goal", "Building task DAG", "Selecting tools"],
                            console=console,
                            style="gold1",
                        )

                # Detect leaked key embedded in plan summary by thinking_path.py
                if plan and plan.summary and "SECURITY_ALERT:GEMINI_KEY_LEAKED" in plan.summary:
                    from src.core.api_security import leaked_key_warning
                    console.print(Panel(
                        leaked_key_warning("Gemini", rich=True),
                        title="[bold red]⚠  KEY COMPROMISED[/bold red]",
                        border_style="red",
                    ))
                    # Disable Gemini for this session — all subsequent requests fall to Groq/MiMo
                    engine.gemini_client = None
                    engine.parallel_executor.primary_brain = None
                    continue

                response_reveal(
                    engine.assembler.render_plan(plan),
                    title="Task DAG",
                    console=console,
                    final_border="yellow",
                    cycles=5,
                )
                if plan.socratic_insight:
                    console.print(Panel(f"[italic]{plan.socratic_insight}[/italic]", title="CRITIQUE", border_style="magenta"))

                is_coding_task = (classification or {}).get("intent") == "coding" or any(k in user_input.lower() for k in ["code", "implement", "refactor", "write tool", "fix bug"])

                if is_coding_task:
                    approved = False
                    while not approved:
                        console.print("\n[bold yellow]Do you want any changes to this plan?[/bold yellow]")
                        console.print("[dim]Type changes to refine the plan, or press Enter / type 'ok', 'go ahead', 'fine', 'proceed' to execute:[/dim]")
                        
                        feedback = await asyncio.to_thread(Prompt.ask, "❯ ")
                        feedback_clean = feedback.strip().lower()
                        
                        if feedback_clean in ("", "ok", "go ahead", "fine", "proceed", "yes", "y"):
                            approved = True
                            break
                        else:
                            console.print(f"[cyan]Regenerating plan with feedback: '{feedback}'...[/cyan]")
                            
                            compass_ctx = prefetch_results.get("compass") if prefetch_results else None
                            if not compass_ctx:
                                if not engine.code_compass.index:
                                    engine.code_compass.build()
                                compass_ctx = engine.code_compass.context_for_query(user_input, max_files=5)
                            compass_block = f"\n--- CODE COMPASS (compressed symbol map) ---\n{compass_ctx}\n" if compass_ctx else ""
                            bundle_block = PrefetchBundle.render_as_prompt_block(prefetch_results or {})
                            _has_prefetch = bool(prefetch_results) or bool(pruned_knowledge)
                            plan_prompt_prefix = directives_block if _has_prefetch else ""
                            
                            user_input_with_feedback = f"{user_input}\n[User Feedback/Required Changes: {feedback}]"
                            
                            _tp_is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                            if _tp_is_offline:
                                plan = await thinking_cascade(
                                    engine.ollama_client.generate_plan(
                                        f"{plan_prompt_prefix}{bundle_block}\n{pruned_knowledge}\n{compass_block}\n{user_input_with_feedback}"
                                    ),
                                    phases=["Mapping codebase", "Decomposing goal (local)", "Building task DAG", "Selecting tools"],
                                    console=console,
                                    style="gold1",
                                )
                            else:
                                plan = await thinking_cascade(
                                    engine.gemini_client.generate_plan(
                                        f"{plan_prompt_prefix}{bundle_block}\n{pruned_knowledge}\n{compass_block}\n{user_input_with_feedback}",
                                        engine.session_id,
                                        file_paths=valid_files,
                                        emotional_state=emotional_state,
                                        skip_internal_context=_has_prefetch,
                                    ),
                                    phases=["Re-mapping codebase", "Incorporating user changes", "Re-building task DAG", "Selecting tools"],
                                    console=console,
                                    style="gold1",
                                )
                            
                            response_reveal(
                                engine.assembler.render_plan(plan),
                                title="Updated Task DAG",
                                console=console,
                                final_border="yellow",
                                cycles=5,
                            )
                            if plan.socratic_insight:
                                console.print(Panel(f"[italic]{plan.socratic_insight}[/italic]", title="CRITIQUE", border_style="magenta"))

                    # Spawning coding agent (GLM 5.2) with the approved plan
                    plan_details = ""
                    for step in plan.task_plan:
                        plan_details += f"Step {step.id}: {step.action} using {step.tool} with input {step.input_data}\n"
                    
                    harness_goal = f"""
Execute the following coding task according to this approved plan.

Original Request: {user_input}

Plan Summary: {plan.summary}
Plan Steps:
{plan_details}
"""
                    console.print("[bold green]Spawning Coding Agent (GLM 5.2) with the approved plan...[/bold green]")
                    t0 = time.time()
                    results = await dispatch_harness(engine, console, harness_goal, trigger="coding_intent")
                    response = results.get("summary", "Coding task executed.")
                    
                    _plan_elapsed = time.time() - t0
                    # Log the spend for the execution
                    engine.spend_tracker.log_interaction(
                        session_id=engine.session_id,
                        model=engine.harness.mimo.model if (engine.harness.mimo and engine.harness.mimo.is_online) else "z-ai/glm-5.2",
                        tokens_in=len(harness_goal) // 4,
                        tokens_out=len(response) // 4,
                        compute_sec=_plan_elapsed,
                    )
                    
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, response, project_name=engine.active_project_name)
                    continue

                else:
                    sg = engine.parallel_executor.safety_guard
                    if sg.mode == "plan":
                        console.print("[bold magenta]PLAN MODE: execution skipped.[/bold magenta]")
                        continue

                    authorize = sg.mode == "auto-approve" or Confirm.ask("\n[bold yellow]Authorize compute sequence?[/bold yellow]")
                    if authorize:
                        t0 = time.time()
                        await engine.hooks.fire("PreToolUse", {"plan_summary": plan.summary, "tools": plan.tools_required})
                        results = await engine.parallel_executor.run(plan)
                        await engine.hooks.fire("PostToolUse", {"plan_summary": plan.summary, "results": str(results)[:2000]})
                        synthesis_prompt = f"Results: {results}\nUser: {user_input}\nSummarize as a cunning architect:"
                        _plan_is_offline = os.getenv("APEX_OFFLINE", "0") == "1"
                        if _plan_is_offline:
                            response = engine.ollama_client.get_completion(synthesis_prompt)
                            _plan_model = engine.ollama_client.llm_model
                        else:
                            response = engine.groq_client.get_completion(synthesis_prompt)
                            _plan_model = "gemini-3.5-flash"
                        engine.assembler.render_final_response(user_input, response, plan, results, active_proj, vitals)
                        if engine.voice_enabled:
                            engine.voice.speak(response)
                        _plan_elapsed = time.time() - t0
                        engine.spend_tracker.log_interaction(
                            session_id=engine.session_id,
                            model=_plan_model,
                            tokens_in=len(user_input) // 4,
                            tokens_out=len(response) // 4,
                            compute_sec=_plan_elapsed,
                        )
                        if hasattr(engine, 'predictor'):
                            try:
                                _cost = (len(user_input) // 4 + len(response) // 4) * 0.0000005
                                engine.predictor.record_spend(
                                    _cost, len(user_input) // 4, len(response) // 4, _plan_model
                                )
                                engine.predictor.record_command(
                                    f"plan: {user_input[:80]}", os.getcwd(), 0, _plan_elapsed
                                )
                            except Exception:
                                pass
                        await engine.memory_manager.store_interaction(engine.session_id, user_input, response, project_name=engine.active_project_name)
                        if not engine.economy_mode:
                            asyncio.create_task(engine.learning_manager.learn(engine.session_id, user_input, response, plan))
                            asyncio.create_task(engine.knowledge_visualizer.extract_knowledge(user_input, response))
            elif path == "thinking_path" and not engine.gemini_client:
                console.print("[yellow]Gemini offline — falling back to Groq fast-path.[/yellow]")
                context = await engine.memory_manager.get_relevant_context(
                    user_input, engine.session_id, project_name=active_proj.name if active_proj else None
                )
                response = engine.groq_client.get_completion(f"{context}\n\nUser: {user_input}")
                engine.assembler.render_final_response(user_input, response, project=active_proj, vitals=vitals)
                if engine.voice_enabled:
                    engine.voice.speak(response)
                await engine.memory_manager.store_interaction(engine.session_id, user_input, response, project_name=engine.active_project_name)

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]ERROR: {e}[/bold red]")

    await engine.hooks.fire("Stop", {"session_id": engine.session_id})
    if hasattr(engine, "voice"):
        engine.voice.stop()
    if getattr(engine, "voice_task", None) and not engine.voice_task.done():
        engine.voice_task.cancel()
    if hasattr(engine, "ambient") and engine.ambient.is_active:
        engine.ambient.stop()
    evolve_task.cancel()
    forge_task.cancel()
    for t in (evolve_task, forge_task):
        try:
            await t
        except (asyncio.CancelledError, Exception):
            pass
    await engine.mcp_client.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
