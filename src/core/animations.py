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
  - status_ticker(console)                     — live one-line ✶ doing X… (1.2s) updater
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


# ── decrypt-reveal banner (cinematic boot wordmark) ─────────────────────────

_GLITCH_CHARS = "█▓▒░╬╤╧╪╫╝╜╛┐┌╔╗▌▐▀▄■"


def decrypt_reveal_banner(
    title: str = "APEX",
    console: Optional[Console] = None,
    font: str = "ansi_shadow",
    reveal_speed: float = 0.018,    # seconds per column of reveal
    glitch_frames: int = 4,          # tail of garbled passes after full reveal
    fps: int = 60,
    final_palette: Iterable[str] = ("bright_cyan", "cyan", "magenta", "bright_magenta", "bright_cyan"),
) -> None:
    """
    Cinematic boot banner: figlet wordmark resolves column-by-column from
    glitch chars into the final colored ASCII. Then briefly shimmers and locks.

    Visually distinct from pulse_banner — this looks like a system *decrypting
    itself online* rather than a rainbow gradient.

    Non-tty falls back to a single colored figlet print.
    """
    console = console or Console()
    try:
        art = pyfiglet.figlet_format(title, font=font)
    except Exception:
        art = pyfiglet.figlet_format(title)
    lines = art.rstrip("\n").splitlines()
    if not lines:
        return

    width = max(len(ln) for ln in lines)
    height = len(lines)
    palette = list(final_palette)

    if not _is_animatable(console):
        out = Text()
        for idx, ln in enumerate(lines):
            out.append(ln + "\n", style=f"bold {palette[idx % len(palette)]}")
        console.print(Align.center(out))
        return

    rng = random.Random(0xA9EF)
    target_grid = [list(ln.ljust(width)) for ln in lines]

    def _build_frame(reveal_col: int, ghost_phase: int) -> Text:
        out = Text()
        for y in range(height):
            for x in range(width):
                tch = target_grid[y][x]
                if x < reveal_col and tch != " ":
                    # Settled column — render in palette color, varying per row
                    style = f"bold {palette[(y + ghost_phase) % len(palette)]}"
                    out.append(tch, style=style)
                elif tch != " " and x < reveal_col + 4:
                    # Edge of reveal wave — bright white scan beam
                    out.append(rng.choice(_GLITCH_CHARS), style="bold bright_white")
                elif tch != " ":
                    # Not yet resolved — flicker glitch char in deep cyan
                    if rng.random() < 0.85:
                        out.append(rng.choice(_GLITCH_CHARS), style="dim cyan")
                    else:
                        out.append(" ", style="dim")
                else:
                    out.append(" ")
            out.append("\n")
        return out

    delay = 1.0 / fps
    with Live("", console=console, refresh_per_second=fps, transient=False) as live:
        # Stage 1 — reveal from left to right
        col = 0
        ghost = 0
        steps_per_col = max(1, int(reveal_speed * fps))
        while col <= width:
            live.update(Align.center(_build_frame(col, ghost)))
            for _ in range(steps_per_col):
                time.sleep(delay)
            col += 1
            ghost = (ghost + 1) % len(palette)

        # Stage 2 — settled but shimmer the palette a few frames
        for f in range(glitch_frames * 6):
            shimmer = Text()
            for y in range(height):
                color = palette[(y + f) % len(palette)]
                shimmer.append("".join(target_grid[y]) + "\n", style=f"bold {color}")
            live.update(Align.center(shimmer))
            time.sleep(1.0 / 24)

        # Stage 3 — lock to a clean gradient and exit
        final = Text()
        for y in range(height):
            color = palette[y % len(palette)]
            final.append("".join(target_grid[y]) + "\n", style=f"bold {color}")
        live.update(Align.center(final))
        time.sleep(0.15)

    # Spectrum bar — animated audio-meter underneath
    _spectrum_bar(console, duration=0.7)


def _spectrum_bar(console: Console, duration: float = 0.7, fps: int = 30,
                  width: int = 40, height: int = 3) -> None:
    """Quick animated bar-graph beneath the banner for cinematic effect."""
    if not _is_animatable(console):
        return
    rng = random.Random()
    end = time.time() + duration
    bars = [rng.randint(0, height) for _ in range(width)]
    with Live("", console=console, refresh_per_second=fps, transient=True) as live:
        while time.time() < end:
            # walk each bar up/down by 1 toward a new random target
            for i in range(width):
                tgt = rng.randint(0, height)
                if bars[i] < tgt:
                    bars[i] += 1
                elif bars[i] > tgt:
                    bars[i] -= 1
            txt = Text()
            glyphs = (" ", "▁", "▃", "▅", "▇")
            for y in range(height, 0, -1):
                line = ""
                for b in bars:
                    line += glyphs[min(b, len(glyphs) - 1)] if b >= y else " "
                style = "bright_cyan" if y == 1 else ("cyan" if y == 2 else "magenta")
                txt.append(line + "\n", style=f"bold {style}")
            live.update(Align.center(txt))
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


# ── status ticker (live one-line ephemeral status) ───────────────────────────

_STAR_FRAMES = ("✶", "✷", "✸", "✹", "✺", "✹", "✸", "✷")


class StatusTicker:
    """
    Live one-line ephemeral status display, Claude-Code style.

    Shows: `✶ <message>… (1.2s)`

    Usage (async context manager):

        async with status_ticker(console) as t:
            await t.set("Adding classify + intent cache")
            await do_thing_1()
            await t.set("Picking best tool")
            await do_thing_2()

    The line clears on exit (transient=True). Non-tty falls back to plain
    prints, one per `set()`.

    `t.tick()` is a no-op alias kept for symmetry — the underlying Rich Live
    refresh handles the animation frame internally.
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        style: str = "bright_cyan",
        fps: int = 12,
    ):
        self.console = console or Console()
        self.style = style
        self.fps = fps
        self._live: Optional[Live] = None
        self._message: str = "thinking"
        self._t_start: float = 0.0
        self._task: Optional[asyncio.Task] = None
        self._stop = asyncio.Event()
        self._animatable = _is_animatable(self.console)

    async def __aenter__(self):
        self._t_start = time.time()
        self._stop.clear()
        if self._animatable:
            self._live = Live(
                self._render(),
                console=self.console,
                refresh_per_second=self.fps,
                transient=True,
            )
            self._live.__enter__()
            self._task = asyncio.create_task(self._spin())
        else:
            # Non-tty: print initial message
            self.console.print(f"  ✶ {self._message}…")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self._stop.set()
        if self._task is not None:
            try:
                await self._task
            except Exception:
                pass
        if self._live is not None:
            try:
                self._live.__exit__(exc_type, exc, tb)
            except Exception:
                pass

    async def set(self, message: str) -> None:
        """Swap the active status message."""
        self._message = message
        if self._animatable and self._live is not None:
            self._live.update(self._render())
        else:
            elapsed = time.time() - self._t_start
            self.console.print(f"  ✶ {message}…  [dim]({elapsed:.1f}s)[/dim]")

    async def tick(self) -> None:
        """No-op alias — kept for API symmetry."""
        return None

    # ── internal ─────────────────────────────────────────────────────────────

    def _render(self) -> Text:
        elapsed = time.time() - self._t_start
        frame_idx = int(elapsed * self.fps) % len(_STAR_FRAMES)
        star = _STAR_FRAMES[frame_idx]
        out = Text()
        out.append(f"  {star} ", style=f"bold {self.style}")
        out.append(self._message, style=self.style)
        out.append("…  ", style=self.style)
        out.append(f"({elapsed:.1f}s)", style="dim white")
        return out

    async def _spin(self):
        try:
            while not self._stop.is_set():
                if self._live is not None:
                    self._live.update(self._render())
                await asyncio.sleep(1.0 / self.fps)
        except asyncio.CancelledError:
            pass


def status_ticker(
    console: Optional[Console] = None,
    style: str = "bright_cyan",
    fps: int = 12,
) -> StatusTicker:
    """Factory — returns a StatusTicker async context manager."""
    return StatusTicker(console=console, style=style, fps=fps)
