"""
Tool registry — single source of truth for what tools APEX can use.

Each tool entry declares:
  - canonical name
  - aliases (fuzzy match — Gemini might say "fs" instead of "filesystem")
  - actions (verb subset)
  - input schema
  - one-line "when to use"
  - 1-2 examples

`get_prompt_block()` auto-generates the AVAILABLE TOOLS section that goes into
Gemini's system prompt, so adding a tool here updates planner behavior
without editing the system prompt by hand.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ToolSpec:
    name: str
    aliases: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    input_schema: str = ""
    when_to_use: str = ""
    examples: List[str] = field(default_factory=list)


REGISTRY: Dict[str, ToolSpec] = {
    "filesystem": ToolSpec(
        name="filesystem",
        aliases=["fs", "files", "file"],
        actions=["read", "write", "delete", "list", "search", "glob"],
        input_schema='write: JSON {"path": str, "content": str}; others: path string or pattern',
        when_to_use="Read source, write code edits, search/glob across project, list dirs.",
        examples=[
            'filesystem:write input_data={"path":"src/foo.py","content":"def x(): return 1"}',
            "filesystem:search input_data='def main' (uses ripgrep)",
            "filesystem:glob input_data='**/*.py'",
        ],
    ),
    "shell": ToolSpec(
        name="shell",
        aliases=["sh", "bash", "exec", "cmd"],
        actions=["execute"],
        input_schema="command string",
        when_to_use="Run system commands, package installs, build steps.",
        examples=["shell:execute input_data='pytest tests/'"],
    ),
    "git": ToolSpec(
        name="git",
        aliases=["vcs"],
        actions=["commit", "status", "diff", "add", "push", "pull", "log", "checkout"],
        input_schema="commit msg / branch name / file path",
        when_to_use="Source control operations.",
        examples=["git:commit input_data='feat: add auth'", "git:diff input_data=''"],
    ),
    "python_executor": ToolSpec(
        name="python_executor",
        aliases=["python", "py", "code"],
        actions=["write", "run"],
        input_schema="code string or task description",
        when_to_use="Generate validated Python code (write) or execute snippet (run).",
        examples=["python_executor:write input_data='function to parse CSV'"],
    ),
    "research_swarm": ToolSpec(
        name="research_swarm",
        aliases=["research", "rs"],
        actions=["search"],
        input_schema="query string",
        when_to_use="Multi-agent web/file/code research for unknowns. Slower than web_search but deeper.",
        examples=["research_swarm:search input_data='best Python async ORM 2026'"],
    ),
    "web_search": ToolSpec(
        name="web_search",
        aliases=["web", "google", "search"],
        actions=["search"],
        input_schema="query string",
        when_to_use="Quick web lookup. Faster but shallower than research_swarm.",
        examples=["web_search:search input_data='FastAPI middleware example'"],
    ),
    "workspace": ToolSpec(
        name="workspace",
        aliases=["ws", "project"],
        actions=["scan", "summarize", "directives", "list_projects"],
        input_schema="empty or project name",
        when_to_use="Get project context, list projects, read APEX.md/CLAUDE.md directives.",
        examples=["workspace:summarize input_data=''", "workspace:directives input_data=''"],
    ),
    "mcp": ToolSpec(
        name="mcp",
        aliases=["model-context-protocol"],
        actions=["connect", "call"],
        input_schema='JSON {"server": str, "tool": str, "args": {...}}',
        when_to_use="Invoke external MCP servers (Playwright, Supabase, Canva, etc).",
        examples=['mcp:call input_data=\'{"server":"playwright","tool":"navigate","args":{"url":"..."}}\''],
    ),
    "vision": ToolSpec(
        name="vision",
        aliases=["screen", "retina", "see", "media"],
        actions=["capture", "ocr", "describe", "describe_video", "transcribe_audio", "understand_media"],
        input_schema="empty (capture full screen) or path to image/video/audio file",
        when_to_use="See screen, OCR/describe images, summarize videos (frame-sampled multimodal), transcribe audio.",
        examples=[
            "vision:capture input_data=''",
            "vision:describe input_data='./screenshot.png'",
            "vision:describe_video input_data='./demo.mp4'",
            "vision:transcribe_audio input_data='./call.m4a'",
        ],
    ),
    "hardware": ToolSpec(
        name="hardware",
        aliases=["hw", "vitals", "system"],
        actions=["vitals", "load"],
        input_schema="empty",
        when_to_use="Check CPU/GPU/RAM — gate heavy ops, surface throttling.",
        examples=["hardware:vitals input_data=''"],
    ),
    "code_compass": ToolSpec(
        name="code_compass",
        aliases=["compass", "symbols", "ast"],
        actions=["search", "stats", "context"],
        input_schema="symbol/term string or empty",
        when_to_use="Token-efficient symbol search across project AST. Use BEFORE filesystem:search for code lookups.",
        examples=["code_compass:search input_data='MemoryManager'", "code_compass:context input_data='auth flow'"],
    ),
    "knowledge_forge": ToolSpec(
        name="knowledge_forge",
        aliases=["forge", "papers", "kf"],
        actions=["search_papers", "list_proposals", "status", "digest"],
        input_schema="query string for search; empty for others",
        when_to_use="Query ingested arxiv papers, ecosystem feed, capability proposals.",
        examples=["knowledge_forge:search_papers input_data='LLM agent memory'"],
    ),
    "swarm": ToolSpec(
        name="swarm",
        aliases=["multi_agent", "agents"],
        actions=["run"],
        input_schema='goal string or JSON {"goal": str, "roster": [str], "rounds": int}',
        when_to_use="Spawn specialist agents (architect/coder/critic/...) for high-complexity goals.",
        examples=['swarm:run input_data=\'{"goal":"design auth system","roster":["architect","critic"]}\''],
    ),
    "think_partner": ToolSpec(
        name="think_partner",
        aliases=["think", "tp"],
        actions=["cross_question", "architect", "debate", "brainstorm", "teach"],
        input_schema="prompt string",
        when_to_use="Cognitive collaboration — clarify vague goals, design review, adversarial pushback.",
        examples=["think_partner:architect input_data='build a billing service'"],
    ),
    "web_fetch": ToolSpec(
        name="web_fetch",
        aliases=["fetch", "url", "wf", "get_url"],
        actions=["fetch"],
        input_schema="URL string",
        when_to_use="Pull a SPECIFIC URL's text content. Use after web_search picks the target page.",
        examples=["web_fetch:fetch input_data='https://docs.python.org/3/library/asyncio.html'"],
    ),
    "todo": ToolSpec(
        name="todo",
        aliases=["todos", "tasks", "tl"],
        actions=["add", "list", "update", "remove", "clear_completed"],
        input_schema='add: task string; list: empty; update: JSON {"id":"...","status":"pending|in_progress|completed"}; remove: id string',
        when_to_use="Persistent per-project task list. Track multi-step work across sessions.",
        examples=[
            "todo:add input_data='wire MiMo into coding pipeline'",
            "todo:list input_data=''",
            'todo:update input_data=\'{"id":"a1b2","status":"completed"}\'',
        ],
    ),
    "diff": ToolSpec(
        name="diff",
        aliases=["compare", "patch"],
        actions=["run", "files", "content"],
        input_schema='JSON {"a": "<path>", "b": "<path>"} OR {"path": "<path>", "content": "<text>"}',
        when_to_use="Unified diff between two files or between disk and proposed content. Use BEFORE filesystem:write to preview changes.",
        examples=[
            'diff:run input_data=\'{"a":"src/foo.py","b":"src/foo.py.bak"}\'',
            'diff:run input_data=\'{"path":"README.md","content":"# new content\\n"}\'',
        ],
    ),
    "desktop_control": ToolSpec(
        name="desktop_control",
        aliases=["desktop", "ui", "automation", "win_automation"],
        actions=["click", "type", "read", "list_elements", "navigate", "powershell"],
        input_schema='JSON containing action details (e.g. {"selector": "...", "text": "..."})',
        when_to_use="Control Windows UI elements via UI Automation, run PowerShell scripts, or automate browser tasks using Playwright.",
        examples=[
            'desktop_control:click input_data=\'{"text": "Start"}\'',
            'desktop_control:type input_data=\'{"text": "notepad", "selector": "Search"}\'',
            'desktop_control:navigate input_data=\'{"url": "https://google.com"}\'',
        ],
    ),
}


# ── alias resolver ───────────────────────────────────────────────────────────

_ALIAS_INDEX: Dict[str, str] = {}
for _spec in REGISTRY.values():
    _ALIAS_INDEX[_spec.name] = _spec.name
    for _alias in _spec.aliases:
        _ALIAS_INDEX[_alias.lower()] = _spec.name


def resolve_tool_name(raw: str) -> Optional[str]:
    """Map raw tool name (possibly an alias) to canonical name. None if unknown."""
    if not raw:
        return None
    return _ALIAS_INDEX.get(raw.strip().lower())


def list_tools() -> List[str]:
    return sorted(REGISTRY.keys())


def get_spec(name: str) -> Optional[ToolSpec]:
    canonical = resolve_tool_name(name)
    if canonical is None:
        return None
    return REGISTRY[canonical]


def get_prompt_block() -> str:
    """
    Returns markdown block for AVAILABLE TOOLS section of Gemini system prompt.
    Auto-derived from REGISTRY — single source of truth.
    """
    lines = ["AVAILABLE TOOLS (use exact tool name in plans):"]
    for spec in REGISTRY.values():
        lines.append(
            f"- {spec.name}: actions=[{','.join(spec.actions)}] "
            f"input={spec.input_schema}"
        )
        lines.append(f"    when: {spec.when_to_use}")
        if spec.examples:
            lines.append(f"    e.g. {spec.examples[0]}")
    return "\n".join(lines)


# ── telemetry ────────────────────────────────────────────────────────────────

class ToolTelemetry:
    """Per-tool success/fail counter. Lives on ParallelExecutor."""

    def __init__(self):
        self.calls: Dict[str, Dict[str, int]] = {}

    def record(self, tool: str, success: bool, error: str = ""):
        canonical = resolve_tool_name(tool) or tool
        if canonical not in self.calls:
            self.calls[canonical] = {"ok": 0, "fail": 0, "last_error": ""}
        if success:
            self.calls[canonical]["ok"] += 1
        else:
            self.calls[canonical]["fail"] += 1
            self.calls[canonical]["last_error"] = error[:200]

    def summary(self) -> Dict[str, Dict[str, int]]:
        return dict(self.calls)

    def reset(self):
        self.calls.clear()
