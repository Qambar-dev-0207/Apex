# APEX — Terminal Animation System

`src/core/animations.py`

---

## Overview

APEX uses Rich-powered terminal animations for a premium CLI experience. Every animation is **tty-safe**: when stdout is piped, redirected, or in a dumb terminal, it degrades to a plain static print — no hangs, no broken escape codes, no test failures.

---

## tty detection

```python
def _is_animatable(console: Console) -> bool:
    return bool(getattr(console, "is_terminal", False)) and \
           "dumb" not in (sys.stdout.encoding or "").lower()
```

All animation functions check this before entering `Live` or `sleep` loops. When `False`, they print a plain equivalent and return immediately.

---

## Functions

### `type_text(text, console, cps=120, style="", end="\n")`

Types text character by character at `cps` characters per second.

```python
type_text("Initializing APEX...", cps=80, style="bold cyan")
```

- Non-tty: `console.print(text, style=style)` immediately
- `cps=0`: also prints immediately (explicit static mode)

---

### `pulse_banner(title="APEX", console, cycles=3, fps=18, font="ansi_shadow")`

Renders a figlet ASCII art banner with an animated diagonal color wave using Rich `Live`.

```python
pulse_banner("APEX", cycles=2, fps=18)
```

**How it works:**
1. `pyfiglet.figlet_format(title, font=font)` → ASCII art lines
2. For each frame, each line gets a phase-shifted color from `_PULSE_PALETTE`
3. The phase shift creates a diagonal wave across the banner
4. `Live` updates the display each frame at `fps` rate

Palette: `bright_cyan → cyan → bright_blue → magenta → bright_magenta → gold1 → yellow` (reversed for back half of cycle).

Non-tty: renders banner once in first palette color.

---

### `matrix_rain(console, duration=1.6, fps=24, width=80, height=14)`

Classic green character rain for boot decoration. Uses `Rich Live` with `transient=True` (clears after run).

```python
matrix_rain(duration=2.0)
```

Characters: `01ΛΣΩαβγδ#@*+=-`

Three-tone green gradient (bright_green / green / dark_green) for depth effect.

Non-tty: `return` immediately (no print — purely decorative).

---

### `progress_trail(steps, console, delay=0.18)`

Animated vertical checklist. Each step spins through `◐◓◑◒` frames then locks in green `✓`.

```python
progress_trail([
    "Memory system",
    "Tool registry",
    "AgentHarness",
    "KnowledgeForge",
])
```

Used in APEX boot sequence after modules load. Shows all modules coming online visually.

Non-tty: prints `  ✓ <step>` for each step immediately.

---

### `sparkle_panel(text, console, title="APEX", cycles=12, fps=12, border_palette=(...))`

Renders a Rich `Panel` with an animated cycling border color.

```python
sparkle_panel("Analysis complete.", title="GeniusMode")
```

Default border palette: `cyan → bright_cyan → magenta → bright_magenta`.

Non-tty: renders panel once in first border color.

---

### `thinking_orb(coro, label="thinking", console, spinner="aesthetic", style="bright_cyan")`

**Async wrapper** — runs an awaitable while showing an animated spinner. Returns the coroutine's result.

```python
result = await thinking_orb(some_long_async_task(), label="Loading APEX")
```

Used in boot sequence to wrap the module loader:
```python
await thinking_orb(loader_task, label="Initializing subsystems")
```

Non-tty: `return await coro` directly — no spinner, no overhead.

---

## ApexMascot & Block-Art Renderer

`ApexMascot` handles visual rendering for the official APEX pixel robot mascot.

### 14 Mascot States
- `focus`: Hero mascot pose (scratches head / idle standing)
- `coding`: Holds laptop with `</>` code on screen
- `thinking`: Thought bubble `...` floating right
- `learning`: Reads open book with `A` badge
- `building`: Wrench + stacked green/blue blocks
- `analyzing`: Holds bar graph + pie chart screen
- `deploying`: Rocket ship blasting off next to body
- `connected`: WiFi signal arcs radiating above antenna
- `happy`: Star eyes + wide smile + sparkles
- `excited`: Wide open eyes + `:D` mouth
- `focused`: Squinted horizontal eyes `-- --`
- `determined`: Angry angled brows `\\ //`
- `curious`: One small eye, one wide eye, floating `?`
- `proud`: Floating gold trophy `[T]` above head

### `ApexMascot.render_blockart(state="focus") -> Text`

Renders the mascot as crisp full-color terminal block art (Claude Code style):
- Uses upper/lower half-block characters (`▀`/`▄`)
- Each cell encodes 2 vertical pixel rows (2x vertical resolution in terminal)
- Exact RGB Palette: `(255, 215, 0)` gold eyes, `#141419` black screen, `#D7C6B2` beige body, status dots, and vibrant tool accents
- Hand-crafted 16x16 pixel sprite matrices eliminate all JPEG downsampling blur

```python
from src.core.animations import ApexMascot

# Returns a Rich Text object ready for console.print()
block_art = ApexMascot.render_blockart("coding")
console.print(block_art)
```

---

## Boot sequence

```python
# main.py boot_sequence()
matrix_rain(duration=1.2)          # 1. Green character rain
pulse_banner("APEX")               # 2. Animated APEX wordmark
ApexMascot.render_blockart("focus")# 3. Full-color hero APEX mascot
type_text(tagline, style="...")    # 4. Tagline types out
console.print(model_badges_row)    # 5. Brain badges (Gemini / MiMo / Groq)
# ... after loader:
progress_trail(module_checklist)   # 6. Module checklist animates in
```

---

## Adding a new effect

1. Add function to `src/core/animations.py`
2. Check `_is_animatable(console)` at the top
3. Provide static fallback for non-tty
4. Optionally add a test in `tests/test_e2e_full_apex.py::test_animations_safe_on_non_tty`

---

## Dependencies

| Package | Purpose |
|---|---|
| `rich` | Live display, Panel, Text, Spinner, Align |
| `pyfiglet` | ASCII art font rendering |
