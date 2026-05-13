# GeniusMode + ResumeTool + Critique System

---

## GeniusMode (`src/services/genius_mode.py`)

APEX's built-in high-cognition critic. Give it any prompt and it returns a structured 6-field analysis that cross-questions your thinking, surfaces what's right, calls out what's wrong, finds blind spots, and suggests concrete next actions — with a touch of wit.

### The 6-field JSON contract

```json
{
  "cross_question": "The one question that reveals the deepest assumption in your thinking",
  "right":          "What you're actually doing well — acknowledged honestly",
  "wrong":          "What's broken, wrong, or risky — no softening",
  "blind_spots":    "What you haven't considered that could change everything",
  "action":         "The single most valuable next step",
  "one_liner":      "Wit + truth compressed into one sentence"
}
```

### Brain cascade

```
Gemini 2.5 Flash (JSON mime-type forced)
    ↓ fails
Xiaomi MiMo v2.5-pro
    ↓ fails
Groq llama-3.1-8b
    ↓ fails
Offline stub (valid shape, witty one_liner)
```

Offline stub example:
```json
{
  "cross_question": "What assumption are you making that you haven't tested?",
  "right": "You're asking for critique — that alone puts you ahead of most.",
  "wrong": "All brains offline — but your problem is still real.",
  "blind_spots": "The thing you're most certain about is probably worth questioning.",
  "action": "Write down the one assumption that, if wrong, breaks everything.",
  "one_liner": "Running offline — but the truth doesn't need WiFi."
}
```

### Methods

| Method | Output |
|---|---|
| `analyze(prompt, context=None)` | Full 6-field analysis |
| `critique_only(prompt)` | `right` + `wrong` + `one_liner` |
| `blindspots_only(prompt)` | `blind_spots` + `action` |
| `pre_step_critique(goal, proposed_step)` | Cross-question before executing a step |

`pre_step_critique` is particularly useful in agentic harness runs: before each major action, APEX can critique its own proposed next step.

### Slash commands

| Command | What it does |
|---|---|
| `/genius <prompt>` | Full 5-stage analysis, rendered as a labeled panel |
| `/critique <prompt>` | Right/wrong only + one-liner — quick sanity check |
| `/blindspot <prompt>` | Blind spots + ranked actions — surfaces the unseen |

### Example output (`/genius Should I migrate to microservices?`)

```
╭─ GeniusMode Analysis ─────────────────────────────────────────────────╮
│ Cross-question: What problem are you actually solving — scalability,   │
│   team autonomy, or boredom with the monolith?                         │
│                                                                         │
│ Right: You're thinking about architecture before you hit the wall.      │
│                                                                         │
│ Wrong: Microservices don't solve organizational problems — they amplify │
│   them. If your team can't own a monolith, they won't own 12 services. │
│                                                                         │
│ Blind spots: Distributed systems failure modes (split-brain, latency   │
│   amplification, cascading failures) that your monolith hides for free. │
│                                                                         │
│ Action: Write a one-page document describing exactly what is broken     │
│   TODAY. If you can't, you don't need microservices yet.               │
│                                                                         │
│ One-liner: "Migrating to microservices to fix a slow team is like      │
│   buying a sports car to fix traffic."                                  │
╰─────────────────────────────────────────────────────────────────────────╯
```

---

## ResumeTool (`src/tools/resume_tool.py`)

Takes a resume in any format, rewrites it with AI, and returns a clean ATS-optimized PDF.

### Supported input formats

| Extension | Parser |
|---|---|
| `.pdf` | pypdf text extraction |
| `.docx` | python-docx paragraph extraction |
| `.txt` | direct read |
| `.md` | direct read (markdown accepted as-is) |

### Rewrite pipeline

```
load_resume(path)
    → raw text
    → rewrite_resume(text, target_role=None)  [Gemini 2.5 Flash, JSON-forced]
    → structured data dict
    → render_pdf(data, out_path, accent='#1f4e79')  [reportlab platypus]
    → returns PDF path
```

### JSON output structure

```json
{
  "name": "Jane Doe",
  "headline": "Senior Software Engineer",
  "contact": {"email": "...", "phone": "...", "location": "...", "linkedin": "..."},
  "summary": "...",
  "experience": [
    {
      "role": "...",
      "company": "...",
      "dates": "2022 – 2024",
      "bullets": ["achieved X by doing Y", "..."]
    }
  ],
  "projects": [{"name": "...", "description": "...", "tech": ["..."]}],
  "education": [{"degree": "...", "institution": "...", "year": "..."}],
  "skills": {"Languages": ["Python", "Go"], "Tools": ["Docker", "Redis"]},
  "feedback": "3 specific actionable improvements for this resume"
}
```

### PDF rendering

Built with **reportlab platypus**:
- One-column ATS-friendly layout
- Colored header rule (configurable `accent` hex color, default `#1f4e79`)
- `KeepTogether` per experience block — no awkward page splits
- Skills as `[tag]` style inline badges
- XML-safe: all user content escaped via `_e()` before rendering
- Contact info rendered as clickable links where applicable

### Slash command

```
/resume path/to/resume.pdf
/resume path/to/resume.pdf | Senior ML Engineer
```

APEX saves the output PDF alongside the input file with `_apex.pdf` suffix.

### Offline fallback

When Gemini is unreachable, `rewrite_resume()` returns a `_fallback_parse()` stub — a valid dict with the correct keys, populated with the raw input text in `summary` and empty structured fields. PDF render still works.
