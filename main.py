import os
import json
import uuid
import asyncio
import time
import sys
import re
import pyfiglet
from pathlib import Path
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
from src.core.hooks import HookManager
from src.core.harness import AgentHarness
from src.services.genius_mode import GeniusMode
from src.tools.resume_tool import ResumeTool
from src.core.api_security import validate_all_keys, leaked_key_warning
from src.core.animations import (
    pulse_banner, type_text, progress_trail, sparkle_panel,
    thinking_orb, matrix_rain, neural_pulse,
    thinking_cascade, response_reveal, stream_panel,
)


SLASH_HELP = """\
[bold cyan]APEX SLASH COMMANDS[/bold cyan]

[yellow]Session[/yellow]
  /help                    Show this menu
  /now                     Show current date, time, weekday
  /tools                   Show registered tools + per-tool success/fail stats
  /clear                   Clear console
  /clear-session           Wipe current session memory
  /clear-all               Wipe all memories (requires confirm)
  /exit                    Quit APEX
  /resume                  List recent sessions to resume
  /compact                 Summarize and trim long-term context

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

[yellow]Think Partner[/yellow]
  /think <prompt>          Cross-question — surface ambiguity before answering
  /architect <idea>        Design partner — propose + critique your architecture
  /architect <idea> | <yours>   Same, with your architecture after the |
  /debate <claim>          Adversarial pushback (steelman opposing view)
  /brainstorm <topic>      Divergent ideation — 6 distinct angles
  /teach <topic>           Layered explanation: intuition → mechanism → test
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

[yellow]Genius Critique[/yellow]
  /genius <prompt>         Full 5-stage critique: cross-question / right / wrong / blind spots / action / wit
  /critique <prompt>       What you're getting right vs wrong (terse)
  /blindspot <prompt>      Second-order consequences + suggested next steps

[yellow]Resume[/yellow]
  /resume <path>           Rewrite resume (PDF/DOCX/TXT/MD) → polished PDF + feedback
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

[yellow]Telemetry[/yellow]
  /cost                    Show daily spend
  /status                  System health summary
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

    async def load_system(self):
        from src.tools.mcp_client import MCPClient
        self.mcp_client = MCPClient()
        self.classifier = InputClassifier()
        self.router = SmartRouter()
        self.memory_manager = MemoryManager()
        self.workspace = WorkspaceManager()
        self.knowledge_visualizer = KnowledgeVisualizer(self.memory_manager, self.workspace)
        self.learning_manager = LearningManager(self.memory_manager)
        self.learning_manager.seed_skills()

        self.gemini_client = GeminiClient(model_name="gemini-2.5-flash", mcp_client=self.mcp_client) if os.getenv("GEMINI_API_KEY") else None
        self.provisioner = AutoProvisioner(self.learning_manager.skill_manager, self.mcp_client, self.workspace)
        self.parallel_executor = ParallelExecutor(console=self.console, primary_brain=self.gemini_client, mcp_client=self.mcp_client)
        self.assembler = ResponseAssembler(self.console)
        self.spend_tracker = SpendTracker()
        self.retina = RetinaTool()
        self.briefing_agent = BriefingAgent(self.workspace, self.spend_tracker)
        # forge is constructed below; will be back-attached after init
        self._briefing_forge_pending = True
        self.cognitive_core = EmotionalCore()
        self.sync_manager = SovereignSync()
        self.groq_client = GroqClient()
        self.hooks = HookManager(project_root=os.getcwd())
        self.code_compass = CodeCompass(root=os.getcwd())
        self.think_partner = ThinkPartner(console=self.console)
        self.auto_think_enabled = True  # auto-route ambiguous prompts to ThinkPartner
        self.swarm = Swarm(console=self.console)
        self.pending_clarification = None  # holds original prompt while waiting for user answer
        self.tool_selector = AutoToolSelector()
        self.auto_tool_enabled = True  # bypass full DAG planner for high-confidence single-tool intents
        # Wire optional tool collaborators into ParallelExecutor so plan steps
        # like vision/code_compass/swarm/etc are reachable.
        self.parallel_executor.retina = self.retina
        self.parallel_executor.code_compass = self.code_compass
        self.parallel_executor.think_partner = self.think_partner
        self.parallel_executor.agent_swarm = self.swarm
        self.knowledge_forge = KnowledgeForge(
            hw_monitor=self.parallel_executor.hw,
            console=self.console,
            hooks=self.hooks,
            project_root=os.getcwd(),
        )
        self.briefing_agent.forge = self.knowledge_forge
        self.parallel_executor.knowledge_forge = self.knowledge_forge
        # Genius critique layer + Resume PDF tool
        self.genius = GeniusMode(
            mimo_client=self.parallel_executor.coding_pipeline.mimo,
            groq_client=self.groq_client,
        )
        self.resume_tool = ResumeTool()
        # Autonomous tool-calling harness wired to FULL APEX surface.
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
            max_steps=30,
        )
        self.self_evolver = SelfEvolver(
            workspace=self.workspace,
            learning_manager=self.learning_manager,
            provisioner=self.provisioner,
            hw_monitor=self.parallel_executor.hw,
            console=self.console,
            forge=self.knowledge_forge,
        )

        self.ready = True


def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')


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
    # Matrix rain intro
    try:
        matrix_rain(console, duration=0.8)
    except Exception:
        pass
    # Animated pulsing wordmark
    try:
        pulse_banner("APEX", console=console, cycles=2, fps=16)
    except Exception:
        title = pyfiglet.figlet_format("APEX", font="slant")
        console.print(Align.center(_gradient(title)))
    tagline = Text(
        "SOVEREIGN OMEGA // 24-LAYER MULTI-PROVIDER OS",
        style="bold white on grey15",
    )
    console.print(Align.center(tagline))
    console.print()
    # Neural network visualization showing model topology
    try:
        neural_pulse(console, duration=1.4)
    except Exception:
        pass
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
    """
    active = engine.workspace.get_active()
    if not active:
        engine.console.print("[red]No active project.[/red]")
        return

    apex_md_path = os.path.join(active.root_dir, "APEX.md")
    if os.path.exists(apex_md_path):
        if not Confirm.ask(f"[yellow]APEX.md exists. Overwrite?[/yellow]"):
            return

    file_summary = "\n".join(active.file_tree[:50])
    template = f"""# APEX Project Directives — {active.name}

> Auto-generated by `/init`. Edit freely. APEX reads this on every request.

## Goals
{chr(10).join(f"- {g}" for g in active.goals)}

## Stack
_(detected from file tree)_

## Conventions
- Match existing code style
- Don't add features that weren't asked for
- Run tests before declaring done

## Files
{file_summary}

## Notes
_Add long-lived constraints, gotchas, and architectural decisions here._
"""
    with open(apex_md_path, "w", encoding="utf-8") as f:
        f.write(template)
    engine.console.print(f"[bold green]✓ APEX.md generated at {apex_md_path}[/bold green]")


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
        except ValueError:
            engine.console.print("[red]Usage: /todo done <number>[/red]")
        return
    if args:
        engine.workspace.add_todo(active.name, " ".join(args))
        engine.console.print("[green]✓ Todo added.[/green]")
        return
    if not active.todos:
        engine.console.print("[dim]No todos.[/dim]")
        return
    for i, t in enumerate(active.todos):
        mark = "[green]✓[/green]" if t.get("done") else "[yellow]○[/yellow]"
        engine.console.print(f" {mark} {i+1}. {t.get('task','')}")


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

    console.print(Panel(
        "\n\n".join(sections) or "(no analysis)",
        title="APEX GENIUS", border_style="bright_magenta", padding=(1, 2),
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
    if cmd == "/autothink":
        if args and args[0].lower() in ("on", "off"):
            engine.auto_think_enabled = args[0].lower() == "on"
        else:
            engine.auto_think_enabled = not engine.auto_think_enabled
        console.print(f"[bright_magenta]Auto-think → {engine.auto_think_enabled}[/bright_magenta]")
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
        full = " ".join(args)
        # parse rounds=N
        rounds = 1
        rounds_match = re.search(r"\brounds=(\d+)", full)
        if rounds_match:
            rounds = int(rounds_match.group(1))
            full = re.sub(r"\brounds=\d+", "", full).strip()
        # parse roster after |
        roster = None
        if "|" in full:
            goal, roster_str = (s.strip() for s in full.split("|", 1))
            roster = [r.strip().lower() for r in roster_str.split(",") if r.strip()]
        else:
            goal = full

        res = await thinking_cascade(
            engine.swarm.run(goal, rounds=rounds, roster=roster),
            phases=["Spawning agents", "Running specialist round", "Merging outputs", "Synthesizing"],
            console=console,
            style="bright_blue",
        )

        if not res.get("ok"):
            console.print(f"[red]Swarm failed: {res.get('error')}[/red]")
            return True

        # render transcript per agent
        for post in res["transcript"]:
            console.print(Panel(
                Markdown(post["content"][:2000]),
                title=f"{post['role'].upper()} — {post['agent']}",
                border_style="cyan",
            ))
        # final synthesis
        console.print(Panel(
            Markdown(res["artifact"]),
            title=f"SWARM SYNTHESIS — roster: {', '.join(res['roster'])}",
            border_style="bright_blue",
        ))
        await engine.memory_manager.store_interaction(engine.session_id, f"/swarm {goal}", res["artifact"])
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
        if not goal:
            console.print("[red]Empty goal.[/red]")
            return True
        engine.harness.max_steps = max_steps
        result = await engine.harness.run(goal)
        if result.get("success"):
            summary = result.get("summary", "(no summary)")
            touched = result.get("touched_files", []) or []
            body = f"[bold green]✓ DONE[/bold green]\n\n{summary}"
            if touched:
                body += f"\n\n[dim]Touched {len(touched)} file(s):[/dim]\n" + "\n".join(f"  • {p}" for p in touched[:20])
                if result.get("snapshot_dir"):
                    body += f"\n\n[dim]Snapshot:[/dim] {result['snapshot_dir']}  ([cyan]/harness rollback[/cyan] to revert)"
            console.print(Panel(body, title="HARNESS COMPLETE", border_style="green"))
        else:
            console.print(Panel(
                f"[red]{result.get('error','harness failed')}[/red]",
                title="HARNESS FAILED", border_style="red",
            ))
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

    console.print(f"[red]Unknown command: {cmd}. Type /help.[/red]")
    return True


async def main():
    engine = APEXEngine()
    console = engine.console
    await boot_sequence(console)

    loader_task = asyncio.create_task(engine.load_system())

    console.print(Panel(
        "[bold green]System Wake-up Initiated.[/bold green]\n"
        "Initializing [cyan]Gemini 2.5 Flash[/cyan], [gold1]Xiaomi MiMo v2.5-pro[/gold1], "
        "[magenta]Groq Llama[/magenta], [white]MiniMax 2.5[/white].\n"
        "[italic cyan]Good morning, Architect. All systems at 100%. Type /help for commands.[/italic cyan]",
        border_style="bright_black", title="GREETING"
    ))

    objective = Prompt.ask("\n[bold white]Objective[/bold white]")

    if not engine.ready:
        try:
            await thinking_cascade(
                loader_task,
                phases=[
                    "Waking kernel",
                    "Syncing memory layer",
                    "Loading tool registry",
                    "Connecting MCP servers",
                    "Calibrating Genius layer",
                ],
                console=console,
                style="gold1",
            )
        except Exception:
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
        console.print(f"[bold green]✓ ATTACHED: {existing.name}[/bold green]")
    else:
        engine.workspace.create_project(
            name=folder_name,
            description=f"Auto-detected project in {cwd}",
            root_dir=cwd,
            goals=["Autonomous Exploration"]
        )
        console.print(f"[bold blue]⚡ NEW WORKSPACE: {folder_name}[/bold blue]")

    engine.workspace.scan_local_files(folder_name)
    active = engine.workspace.get_active()
    console.print(f"[bold green]✓ CODEBASE MAPPED: {len(active.file_tree)} files.[/bold green]")

    home = os.path.expanduser("~")
    skills_dir = os.path.join(home, ".apex", "skills")
    engine.learning_manager.load_markdown_skills(skills_dir)

    await auto_load_mcp(engine)

    if engine.workspace.get_directives(folder_name):
        console.print("[bold green]✓ APEX.md / CLAUDE.md directives auto-loaded.[/bold green]")

    await engine.hooks.fire("SessionStart", {"session_id": engine.session_id, "project": folder_name})

    # Background self-evolution loop (idle-triggered, hardware-gated)
    evolve_task = asyncio.create_task(engine.self_evolver.background_loop(idle_threshold=300, sleep_interval=60))
    # Background knowledge forge loop (daily, idle-only, hardware-gated)
    forge_task = asyncio.create_task(engine.knowledge_forge.background_loop(idle_threshold=600, sleep_interval=120))

    if not os.getenv("GEMINI_API_KEY"):
        console.print("[yellow]⚠ GEMINI_API_KEY missing — Forge synth/applier will run in degraded heuristic mode.[/yellow]")
    console.print("[bold green]✓ SYSTEM SYNCED.[/bold green]\n")
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

            user_input = await session.prompt_async(HTML(f"\n{status_line}\n<b><cyan>❯</cyan></b> "))
            if not user_input.strip():
                continue

            await engine.hooks.fire("UserPromptSubmit", {"input": user_input, "session_id": engine.session_id})
            engine.self_evolver.mark_input()
            engine.knowledge_forge.mark_input()

            velocity = 1.0 / (time.time() - last_msg_time + 0.1)
            last_msg_time = time.time()

            # ! prefix: direct shell passthrough (like Claude Code's ! command)
            if user_input.startswith("!"):
                raw_cmd = user_input[1:].strip()
                if raw_cmd:
                    res = await engine.parallel_executor.shell.execute(raw_cmd)
                    if res["success"]:
                        console.print(res.get("output", ""))
                    else:
                        console.print(f"[red]{res.get('error', 'Command failed')}[/red]")
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
                await engine.memory_manager.store_interaction(engine.session_id, user_input, reply)
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
                    "APEX — Sovereign Agentic AI OS.\n\n"
                    "I am not a chatbot wrapper. I am a multi-tier orchestration engine "
                    "combining high-reasoning planning (Gemini 2.5 Flash), fast edge inference "
                    "(Groq), code implementation (Xiaomi MiMo v2.5-pro), and specialist agent swarms.\n\n"
                    "What I do:\n"
                    "  ● Plan and execute multi-step goals autonomously via DAG\n"
                    "  ● Select tools on my own — 17 registered tools, 35 harness tools\n"
                    "  ● Think WITH you — cross-question, architect, debate, brainstorm, teach\n"
                    "  ● Critique your thinking — GeniusMode: right/wrong/blind spots/action\n"
                    "  ● Improve your resume → output ATS-optimized PDF\n"
                    "  ● See, read, and hear — image OCR, video understanding, audio transcription\n"
                    "  ● Spawn specialist agent swarms for complex goals\n"
                    "  ● Learn from arxiv + ecosystem daily, propose and apply self-improvements\n"
                    "  ● Run autonomously as an agentic loop — goal in, done() out\n\n"
                    f"Built by: QambarOP | {TimeContext.now_human()}"
                )
                console.print(Panel(_identity, title="APEX — Identity", border_style="bright_cyan"))
                await engine.memory_manager.store_interaction(engine.session_id, user_input, _identity)
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
                    with Live(Spinner("dots", text=f"{rx_pick['tool']}...", style="cyan"),
                              refresh_per_second=10, transient=True):
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
                        engine.session_id, user_input, str(result.get("output", ""))[:1000]
                    )
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

            if engine.auto_think_enabled and engine.think_partner.client:
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
                    if res.get("questions"):
                        engine.pending_clarification = {"original_prompt": effective_input}
                        console.print("[dim]Type answers to continue (or any new prompt to abandon clarification).[/dim]")
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, json.dumps(res, default=str))
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
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, res.get("output", ""))
                    continue

            async def _core_analysis():
                nonlocal emotional_state, apex_state, classification, path, pruned_knowledge, valid_files
                emotional_state = await engine.cognitive_core.analyze_user(user_input, velocity)
                apex_state = engine.cognitive_core.synthesize_apex_state(emotional_state)
                if engine.gemini_client:
                    engine.gemini_client.apex_state_directive = engine.cognitive_core.style_directive(apex_state)
                classification = await engine.classifier.classify(user_input)
                path = engine.router.route(classification)
                pruned_knowledge = await engine.knowledge_visualizer.get_pruned_context(user_input)
                file_matches = re.findall(r"[\w\.\-/\\]+\.(?:pdf|png|jpg|jpeg|webp|md|py|txt|json)", user_input)
                valid_files = [f for f in file_matches if os.path.exists(f)]
                if classification.get('requires_vision') and not any(f.endswith(('.png', '.jpg', '.jpeg')) for f in valid_files):
                    valid_files.append(engine.retina.capture_screen())

            emotional_state = apex_state = classification = path = pruned_knowledge = None
            valid_files = []
            await thinking_cascade(
                _core_analysis(),
                phases=["Reading context", "Classifying intent", "Selecting path"],
                console=console,
                style="white",
            )

            plan = None
            if classification.get("autonomous_skill_id"):
                skill_id = classification["autonomous_skill_id"]
                console.print(f"[bold magenta]AUTONOMOUS TRIGGER: '{skill_id}'[/bold magenta]")
                skill = engine.learning_manager.skill_manager.find_matching_skill(skill_id, threshold=1.0)
                if skill:
                    plan = skill.plan_template

            if path == "fast_path" and not plan:
                context = await engine.memory_manager.get_relevant_context(user_input, engine.session_id)
                project_context = ""
                if active_proj:
                    project_context = f"--- WORKSPACE: {active_proj.name} ---\n{engine.workspace.get_project_context_summary(active_proj.name)}"
                directives = engine.workspace.get_directives(active_proj.name) if active_proj else ""
                directives_block = f"\n--- DIRECTIVES ---\n{directives}\n" if directives else ""

                full_context = f"{directives_block}{pruned_knowledge}\n\n{project_context}\n\n{context}"
                apex_directive = engine.cognitive_core.style_directive(apex_state)
                prompt = f"{full_context}\n{apex_directive}\n\nUser: {user_input}"

                # Stream response into animated live panel
                if apex_state and apex_state.flavor:
                    console.print(f"[italic dim]({apex_state.mood}) {apex_state.flavor}[/italic dim]")
                panel_title = f"APEX  ·  {active_proj.name}" if active_proj else "APEX"
                response = stream_panel(
                    engine.groq_client.stream_completion(prompt),
                    title=panel_title,
                    console=console,
                    border_style="bright_cyan",
                )

                # Track spend (approx tokens: 1 token ≈ 4 chars)
                engine.spend_tracker.log_interaction(
                    session_id=engine.session_id,
                    model=engine.groq_client.model,
                    tokens_in=len(prompt) // 4,
                    tokens_out=len(response) // 4,
                    compute_sec=time.time() - last_msg_time,
                )
                await engine.memory_manager.store_interaction(engine.session_id, user_input, response)
                asyncio.create_task(engine.knowledge_visualizer.extract_knowledge(user_input, response))

            elif (path == "thinking_path" or plan) and engine.gemini_client:
                if not plan:
                    if not engine.code_compass.index:
                        engine.code_compass.build()
                    compass_ctx = engine.code_compass.context_for_query(user_input, max_files=5)
                    compass_block = f"\n--- CODE COMPASS (compressed symbol map) ---\n{compass_ctx}\n" if compass_ctx else ""
                    plan = await thinking_cascade(
                        engine.gemini_client.generate_plan(
                            f"{pruned_knowledge}\n{compass_block}\n{user_input}",
                            engine.session_id,
                            file_paths=valid_files,
                            emotional_state=emotional_state,
                        ),
                        phases=["Mapping codebase", "Decomposing goal", "Building task DAG", "Selecting tools"],
                        console=console,
                        style="gold1",
                    )

                response_reveal(
                    engine.assembler.render_plan(plan),
                    title="Task DAG",
                    console=console,
                    final_border="yellow",
                    cycles=5,
                )
                if plan.socratic_insight:
                    console.print(Panel(f"[italic]{plan.socratic_insight}[/italic]", title="CRITIQUE", border_style="magenta"))

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
                    response = engine.groq_client.get_completion(synthesis_prompt)
                    engine.assembler.render_final_response(user_input, response, plan, results, active_proj, vitals)
                    engine.spend_tracker.log_interaction(
                        session_id=engine.session_id,
                        model="gemini-2.5-flash",
                        tokens_in=len(user_input) // 4,
                        tokens_out=len(response) // 4,
                        compute_sec=time.time() - t0,
                    )
                    await engine.memory_manager.store_interaction(engine.session_id, user_input, response)
                    asyncio.create_task(engine.learning_manager.learn(engine.session_id, user_input, response, plan))
                    asyncio.create_task(engine.knowledge_visualizer.extract_knowledge(user_input, response))
            elif path == "thinking_path" and not engine.gemini_client:
                console.print("[yellow]Gemini offline — falling back to Groq fast-path.[/yellow]")
                context = await engine.memory_manager.get_relevant_context(user_input, engine.session_id)
                response = engine.groq_client.get_completion(f"{context}\n\nUser: {user_input}")
                engine.assembler.render_final_response(user_input, response, project=active_proj, vitals=vitals)
                await engine.memory_manager.store_interaction(engine.session_id, user_input, response)

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]ERROR: {e}[/bold red]")

    await engine.hooks.fire("Stop", {"session_id": engine.session_id})
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
