"""
Terminal animations — Rich-powered effects for APEX.

Effects:
  - type_text(text, console, cps=120)          — typewriter print
  - pulse_banner(title, console, cycles=3)     — gradient color pulse on figlet
  - sparkle_panel(text, console)               — animated dot-trail border panel
  - matrix_rain(console, duration=2.0)         — quick boot decoration
  - neural_pulse(console, duration=1.5)        — animated neural network graph
  - thinking_orb(console, label, task)         — async spinner while a coroutine runs
  - thinking_cascade(coro, phases, console)    — multi-phase thinking display
  - response_reveal(text, title, console)      — animated panel fade-in for responses
  - stream_panel(gen, title, console)          — live-updating streaming panel
  - progress_trail(steps, console, delay)      — boot checklist animation

All animations are tty-safe (`console.is_terminal`). Non-tty degrades to plain prints.
"""

import asyncio
import math
import random
import sys
import time
from typing import Awaitable, Generator, Iterable, List, Optional

import pyfiglet
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.rule import Rule
from rich.spinner import Spinner
from rich.text import Text


_PULSE_PALETTE = (
    "bright_cyan", "cyan", "bright_blue", "magenta",
    "bright_magenta", "gold1", "yellow",
)
_ORB_FRAMES = ("◐", "◓", "◑", "◒")

# Cinematic color sequences
_FIRE_PALETTE   = ("red", "bright_red", "yellow", "bright_yellow", "gold1")
_ICE_PALETTE    = ("bright_blue", "cyan", "bright_cyan", "white", "bright_white")
_NEON_PALETTE   = ("bright_magenta", "magenta", "bright_cyan", "cyan", "bright_green")

# Thinking phase glyphs — each stage gets a unique glyph
_PHASE_GLYPHS = {
    "plan":     "◈",
    "analyze":  "◉",
    "execute":  "◎",
    "think":    "⬡",
    "route":    "◆",
    "search":   "◇",
    "code":     "⊞",
    "write":    "⊟",
    "default":  "◌",
}


def _is_animatable(console: Console) -> bool:
    return bool(getattr(console, "is_terminal", False)) and "dumb" not in (sys.stdout.encoding or "").lower()


def _glyph_for(label: str) -> str:
    low = label.lower()
    for key, g in _PHASE_GLYPHS.items():
        if key in low:
            return g
    return _PHASE_GLYPHS["default"]


# ── typewriter ────────────────────────────────────────────────────────────────

def type_text(
    text: str,
    console: Optional[Console] = None,
    cps: int = 120,
    style: str = "",
    end: str = "\n",
) -> None:
    console = console or Console()
    if not _is_animatable(console) or cps <= 0:
        console.print(text, style=style, end=end)
        return
    delay = 1.0 / cps
    for ch in text:
        console.print(ch, style=style, end="")
        try:
            sys.stdout.flush()
        except Exception:
            pass
        time.sleep(delay)
    if end:
        console.print("", end=end)


# ── banner pulse ──────────────────────────────────────────────────────────────

def pulse_banner(
    title: str = "APEX",
    console: Optional[Console] = None,
    cycles: int = 3,
    fps: int = 18,
    font: str = "ansi_shadow",
) -> None:
    console = console or Console()
    try:
        art = pyfiglet.figlet_format(title, font=font)
    except Exception:
        art = pyfiglet.figlet_format(title)
    lines = art.rstrip("\n").splitlines()
    if not lines:
        return
    if not _is_animatable(console):
        console.print(Align.center(Text(art, style=f"bold {_PULSE_PALETTE[0]}")))
        return

    frame_total = cycles * len(_PULSE_PALETTE) * 2
    palette = list(_PULSE_PALETTE) + list(reversed(_PULSE_PALETTE))
    with Live("", console=console, refresh_per_second=fps, transient=False) as live:
        for f in range(frame_total):
            t = palette[f % len(palette)]
            rendered = Text()
            for idx, line in enumerate(lines):
                ci = (f + idx) % len(palette)
                rendered.append(line + "\n", style=f"bold {palette[ci]}")
            live.update(Align.center(rendered))
            time.sleep(1.0 / fps)


# ── sparkle panel ─────────────────────────────────────────────────────────────

def sparkle_panel(
    text: str,
    console: Optional[Console] = None,
    title: str = "APEX",
    cycles: int = 12,
    fps: int = 12,
    border_palette: Iterable[str] = ("cyan", "bright_cyan", "magenta", "bright_magenta"),
) -> None:
    console = console or Console()
    if not _is_animatable(console):
        console.print(Panel(text, title=title, border_style="cyan"))
        return
    palette = list(border_palette)
    with Live("", console=console, refresh_per_second=fps, transient=False) as live:
        for i in range(cycles):
            live.update(Panel(
                text,
                title=title,
                border_style=palette[i % len(palette)],
                padding=(1, 2),
            ))
            time.sleep(1.0 / fps)


# ── matrix rain ───────────────────────────────────────────────────────────────

def matrix_rain(
    console: Optional[Console] = None,
    duration: float = 1.6,
    fps: int = 24,
    width: int = 80,
    height: int = 14,
) -> None:
    console = console or Console()
    if not _is_animatable(console):
        return
    chars = "01ΛΣΩαβγδ#@*+=-"
    cols = [random.randint(0, height - 1) for _ in range(width)]
    speeds = [random.choice((1, 1, 2)) for _ in range(width)]
    end = time.time() + duration
    with Live("", console=console, refresh_per_second=fps, transient=True) as live:
        while time.time() < end:
            grid = [[" "] * width for _ in range(height)]
            for x in range(width):
                head = cols[x]
                for trail in range(6):
                    y = head - trail
                    if 0 <= y < height:
                        grid[y][x] = random.choice(chars)
                cols[x] = (head + speeds[x]) % (height + 6)
            txt = Text()
            for y, row in enumerate(grid):
                line = "".join(row)
                style = "bright_green" if y % 3 == 0 else ("green" if y % 3 == 1 else "dark_green")
                txt.append(line + "\n", style=style)
            live.update(Align.center(txt))
            time.sleep(1.0 / fps)


# ── neural pulse (boot decor) ─────────────────────────────────────────────────

def neural_pulse(
    console: Optional[Console] = None,
    duration: float = 1.8,
    fps: int = 20,
) -> None:
    """
    Animated neural network visualization — 5 nodes connected by dynamic edges.
    Nodes 'fire' in sequence with a traveling pulse effect. Boot decoration.
    """
    console = console or Console()
    if not _is_animatable(console):
        return

    # Node layout (label, x, y) — rendered as a text grid
    nodes = [
        ("G", 8,  1),
        ("M", 28, 1),
        ("A", 18, 3),
        ("Q", 8,  5),
        ("R", 28, 5),
    ]
    node_styles = ["bright_cyan", "gold1", "bright_magenta", "cyan", "bright_green"]
    edges = [(0, 2), (1, 2), (2, 3), (2, 4), (0, 3), (1, 4)]

    # Edge label meanings
    node_labels = {
        "G": "Gemini",
        "M": "MiMo",
        "A": "APEX",
        "Q": "Groq",
        "R": "ring-2.6-1t",
    }

    W, H = 38, 7
    fire_seq = [0, 1, 2, 3, 4]
    end_t = time.time() + duration
    frame = 0

    with Live("", console=console, refresh_per_second=fps, transient=True) as live:
        while time.time() < end_t:
            grid = [[" "] * W for _ in range(H)]

            # Draw edges as dashes/dots
            for (a, b) in edges:
                lx, ly = nodes[a][1], nodes[a][2]
                rx, ry = nodes[b][1], nodes[b][2]
                steps = max(abs(rx - lx), abs(ry - ly))
                for step in range(1, steps):
                    px = lx + round((rx - lx) * step / steps)
                    py = ly + round((ry - ly) * step / steps)
                    if 0 <= px < W and 0 <= py < H:
                        pulse_pos = (frame // 2 + step) % (steps + 1)
                        grid[py][px] = "·" if pulse_pos != step else "●"

            # Draw nodes
            for i, (label, nx, ny) in enumerate(nodes):
                fire_idx = fire_seq[(frame // 3) % len(fire_seq)]
                char = f"[{label}]" if i == fire_idx else f" {label} "
                for ci, ch in enumerate(char):
                    px = nx + ci - 1
                    if 0 <= px < W and 0 <= ny < H:
                        grid[ny][px] = ch

            # Render
            out = Text()
            for row in grid:
                line = "".join(row)
                # Color fired node differently
                out.append(line + "\n", style="dim cyan")
            out.append("\n  ", style="")
            for label, style in zip(["G=Gemini", "M=MiMo", "A=APEX", "Q=Groq", "R=ring"], node_styles):
                out.append(f" {label} ", style=f"bold {style}")

            live.update(Align.center(out))
            frame += 1
            time.sleep(1.0 / fps)


# ── thinking orb (async, single label) ───────────────────────────────────────

async def thinking_orb(
    coro: Awaitable,
    label: str = "thinking",
    console: Optional[Console] = None,
    spinner: str = "aesthetic",
    style: str = "bright_cyan",
):
    """
    Run an awaitable while showing a labeled animated spinner.
    Returns the coroutine's result. Falls back to direct await on non-tty.
    """
    console = console or Console()
    if not _is_animatable(console):
        return await coro
    glyph = _glyph_for(label)
    spin = Spinner(spinner, text=Text(f" {glyph}  {label}", style=f"bold {style}"))
    task = asyncio.ensure_future(coro)
    with Live(spin, console=console, refresh_per_second=20, transient=True):
        while not task.done():
            await asyncio.sleep(0.05)
    return task.result()


# ── thinking cascade (multi-phase async) ─────────────────────────────────────

async def thinking_cascade(
    coro: Awaitable,
    phases: List[str],
    console: Optional[Console] = None,
    style: str = "bright_cyan",
    fps: int = 8,
):
    """
    Run `coro` while cycling through labeled thinking phases.
    Phases rotate every ~0.7s. Shows animated glyph + phase label + elapsed timer.

    Example:
        result = await thinking_cascade(
            gen_plan(prompt),
            ["Analyzing intent", "Building plan", "Selecting tools"],
        )
    """
    console = console or Console()
    if not _is_animatable(console):
        return await coro

    task = asyncio.ensure_future(coro)
    phase_idx = 0
    phase_duration = 0.75
    phase_start = time.time()
    t_start = time.time()
    orb_frames = ("⠋", "⠙", "⠸", "⠴", "⠦", "⠇")
    frame = 0

    def _build_display(phase: str, elapsed: float) -> Text:
        orb = orb_frames[frame % len(orb_frames)]
        glyph = _glyph_for(phase)
        out = Text()
        out.append(f"  {orb} ", style=f"bold {style}")
        out.append(f"{glyph}  ", style=f"dim {style}")
        out.append(phase, style=f"bold {style}")
        out.append(f"  [{elapsed:.1f}s]", style="dim white")
        # Dot trail
        dots = "." * (int(elapsed * 3) % 4)
        out.append(dots, style=f"dim {style}")
        return out

    with Live("", console=console, refresh_per_second=fps * 4, transient=True) as live:
        while not task.done():
            now = time.time()
            elapsed = now - t_start

            # Advance phase
            if now - phase_start >= phase_duration and phase_idx < len(phases) - 1:
                phase_idx += 1
                phase_start = now

            live.update(_build_display(phases[phase_idx], elapsed))
            frame += 1
            await asyncio.sleep(1.0 / (fps * 4))

    return task.result()


# ── response reveal (animated panel fade-in) ─────────────────────────────────

def response_reveal(
    text: str,
    title: str = "APEX",
    console: Optional[Console] = None,
    final_border: str = "bright_cyan",
    cycles: int = 6,
    fps: int = 18,
) -> None:
    """
    Reveal a response panel with a brief border-color animation before settling.
    Non-tty: plain panel print.
    """
    console = console or Console()
    if not _is_animatable(console):
        console.print(Panel(text, title=title, border_style=final_border, padding=(1, 2)))
        return

    # Sweep: dark → vibrant → settle
    sweep = ["grey50", "cyan", "bright_cyan", "magenta", "bright_cyan", final_border]
    # Clamp cycles to sweep length
    sequence = (sweep * ((cycles // len(sweep)) + 1))[:cycles] + [final_border]
    with Live("", console=console, refresh_per_second=fps, transient=False) as live:
        for border in sequence:
            live.update(Panel(text, title=f"[bold {border}]{title}[/bold {border}]",
                              border_style=border, padding=(1, 2)))
            time.sleep(1.0 / fps)


# ── stream panel (live token streaming) ──────────────────────────────────────

def stream_panel(
    generator: Generator,
    title: str = "APEX",
    console: Optional[Console] = None,
    border_style: str = "bright_cyan",
    max_chars: int = 8000,
) -> str:
    """
    Display a streaming generator inside an auto-updating Live panel.
    Returns the full accumulated text. Non-tty: prints tokens as they arrive.
    """
    console = console or Console()
    accumulated = []

    if not _is_animatable(console):
        console.print(f"\n[bold cyan]{title} //[/bold cyan] ", end="")
        for chunk in generator:
            console.print(chunk, end="")
            accumulated.append(chunk)
        console.print()
        return "".join(accumulated)

    cursor_frames = ("▋", " ")
    cf = 0

    with Live("", console=console, refresh_per_second=24, transient=False) as live:
        for chunk in generator:
            accumulated.append(chunk)
            cf = (cf + 1) % 2
            full = "".join(accumulated)
            if len(full) > max_chars:
                full = "…" + full[-max_chars:]
            cursor = cursor_frames[cf]
            live.update(Panel(
                full + f"[blink]{cursor}[/blink]",
                title=f"[bold bright_cyan]{title}[/bold bright_cyan]",
                border_style=border_style,
                padding=(1, 2),
            ))
        # Final — no cursor
        live.update(Panel(
            "".join(accumulated),
            title=f"[bold bright_cyan]{title}[/bold bright_cyan]",
            border_style=border_style,
            padding=(1, 2),
        ))

    return "".join(accumulated)


# ── progress trail (multi-step boot) ─────────────────────────────────────────

def progress_trail(
    steps: Iterable[str],
    console: Optional[Console] = None,
    delay: float = 0.18,
) -> None:
    """
    Render a vertical animated checklist: each step appears, animates, then
    locks in green. Useful for boot sequences.
    """
    console = console or Console()
    steps = list(steps)
    if not _is_animatable(console):
        for s in steps:
            console.print(f"  ✓ {s}")
        return
    state = ["○"] * len(steps)
    with Live("", console=console, refresh_per_second=20, transient=False) as live:
        for i, _ in enumerate(steps):
            for f in _ORB_FRAMES:
                state[i] = f
                live.update(_render_trail(steps, state))
                time.sleep(delay / len(_ORB_FRAMES))
            state[i] = "✓"
            live.update(_render_trail(steps, state))
            time.sleep(0.05)


def _render_trail(steps, state):
    out = Text()
    for s, marker in zip(steps, state):
        color = "green" if marker == "✓" else ("cyan" if marker in _ORB_FRAMES else "grey50")
        out.append(f"  {marker}  ", style=f"bold {color}")
        out.append(s + "\n")
    return out
