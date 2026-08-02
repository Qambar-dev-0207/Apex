# 🏆 Original Design Generator — Award-Tier UI/UX Framework

*Next.js + Python · Reusable — duplicate this file per project, and log the last one in Appendix A before you do.*

## 0. How This File Works

This replaces the old clone-a-URL workflow. There's no reference site to extract from — fill in **Section 1** with a one-line project brief and hand this file to Claude. Each time, Claude should:

1. Run the **Research Protocol** (Section 2) fresh, with live web search — never from memory or last project's notes. Trends move monthly; a cached mental picture is exactly how output starts looking the same across projects.
2. Generate a **Design Direction** (Section 3) by combining independent axes, not by picking one premade "style." Run it through the Cliché Check before moving on.
3. Fill in Sections 4–17 with concrete, original values derived from that direction.
4. Emit the **Starter Kit** (Section 18) as real, working Next.js + Python code.
5. Append one row to the **Direction Ledger** (Appendix A) so the next project doesn't repeat this one.

**The governing principle:** award-tier ≠ animation-maximalist. What actually separates Awwwards/FWA winners from generic output is restraint plus one or two extremely well-executed signature moments, not motion on every element. This file exists to help you choose fewer, better effects — not to justify adding more.

**Three defaults to actively steer away from**, unless the brief specifically calls for one of them — they're common enough in AI-generated design to read as a tell:
- Warm cream background (~`#F4F1EA`) + high-contrast serif + a terracotta/clay accent near `#D97757`
- Near-black background + a single acid-green or vermilion accent
- Broadsheet layout: hairline rules, zero border-radius, dense newspaper columns

None of these are bad taste on their own — they're just overused defaults. If Section 3 lands on one of them, that's the signal to revise, not ship.

**On `manus.im`:** it isn't a UI or animation library — it's a general autonomous browsing/research agent (Butterfly Effect / Monica). It doesn't belong in `package.json`. It's genuinely useful in Section 2 for running the multi-tab inspiration crawl and handing back a synthesized mood board — that's where it's placed below.

---

## 1. Project Brief & Novelty Anchor

| Field | Value |
|---|---|
| Project name / one-line pitch | APEX — Sovereign Agentic AI OS |
| Real subject, audience, and the page's single job | AI engineers, developers, and autonomous system builders; showcase the 24-Layer Sovereign AI OS through an award-winning narrative storyboard with interactive DAG orchestrator, live telemetry, and Socratic reasoning trace. |
| Brand personality (3–5 adjectives) | Sovereign, Editorial Quartz, High-Precision, Architectural, Storyboard |
| Fixed constraints (existing logo/colors, a11y requirements, deadline, hosting target) | Light theme primary (Quartz Sand), high contrast WCAG AA accessible, Framer Motion animations, responsive across mobile to 4K displays. |
| Light / dark / both | Light Mode Primary (Quartz Sand `#F8F7F4` + International Vermilion `#FF4500` + Royal Blue `#2563EB`) |
| Prior directions to avoid | Dark void themes without narrative flow, generic template cards |
| Deliberate constraint for this round (optional) | Editorial Quartz Storyboard theme: warm quartz canvas + international vermilion primary action + royal blue intelligence glow + Framer Motion narrative reveals |

---

## 2. Research Protocol

*Run this before Section 3, every time. Output 4–8 bullets on what's actually common right now vs. what's overdone — that's what feeds the Direction Generator.*

| Source | Good for |
|---|---|
| awwwards.com — Site of the Day / Month / Year, filterable by category | Current daily bar for craft + execution |
| thefwa.com — FWA of the Day, Hall of Fame | Longest-running award archive; now tracks an "AI" project category too |
| godly.website | Fast-moving, screenshot-first feed |
| lapa.ninja, siteinspire.com, land-book.com | Landing-page patterns by category/industry |
| onepagelove.com | Single-page / product-launch patterns |
| minimal.gallery | Restraint-first counterpoint to maximalist feeds |
| codrops.com (Tympanus) | Technique-level trend writeups, often with source |
| Dribbble, "web design" + current year tag | Early-stage direction before it hits production sites |

**Queries worth running directly** (swap in the current month/year): `site:awwwards.com site of the day`, `web design trends [year]`, `[industry] landing page inspiration [year]`, `codrops scroll animation [year]`.

**Optional — delegate the crawl:** an autonomous browsing agent (e.g. Manus) can run the multi-tab research pass and return a synthesized mood board faster than doing it query by query. Feed its output into Section 3 the same way — it's a research step, not a dependency.

---

## 3. Design Direction Generator

Don't pick one named "style" — pick one option from *each* axis below and combine them. That combinatorial step is what keeps output from converging on the same two or three looks. Mutate or invent beyond this bank once Section 2 has surfaced something more specific than what's listed here; treat it as a starting vocabulary, not a menu you're confined to.

### Axis 1 — Structural Philosophy
Swiss/editorial grid · brutalist raw · asymmetric split-screen · full-bleed cinematic · modular bento grid · infinite canvas/freeform · single-column narrative scroll · layered editorial overlap · terminal/CLI-inspired · maximalist collage

### Axis 2 — Color Philosophy
| Direction | Illustrative starting point | Note |
|---|---|---|
| Monochrome + single accent | `#111111`/`#FAFAFA` + `#2E5EFF` | |
| Duotone gradient wash | `#4C1D95` → `#DB2777` | |
| Dark-luxury | `#0B0B0C` + `#B8935F` bronze | |
| Y2K/dopamine saturated pop | `#FF2E63` / `#08D9D6` / `#FFDE59` | current 2026 comeback per trend research |
| Muted earth/organic | `#6B5B4E` / `#A69076` / `#E8DFD3` | |
| Neon-on-void | `#050505` + `#00E5FF` | overlaps a known AI-default (near-black + acid-green/vermilion) — differentiate the accent hue hard, or pair with an unexpected structural axis choice |
| Paper/cream editorial | `#EDE6D6` + `#1A1A1A` + `#1E3A5F` | avoid the exact `#F4F1EA` + `~#D97757` combo — see Section 0 |
| Gradient mesh maximal | `#6366F1` → `#EC4899` → `#F59E0B` | |
| Pastel soft-UI | `#FFE5EC` / `#E0F4FF` / `#FFF4E0` + `#FF8FA3` | |
| Data-viz semantic palette | `#2563EB` `#16A34A` `#DC2626` `#D97706` `#7C3AED` | function over vibe — dashboards, explainable-AI surfaces |

### Axis 3 — Typographic Voice
Oversized kinetic display · editorial serif+sans pairing · mono-everything · condensed impact · variable-font micro-interactions · custom display + system body · all-lowercase minimal · expressive italic accents · grotesk neutral workhorse · full serif (display+body)

*Pull the actual typefaces from this round's Research Protocol pass — don't default to the same two families project after project.*

### Axis 4 — Motion Character
| Direction | Library |
|---|---|
| Scroll-scrubbed cinematic | GSAP + ScrollTrigger |
| Micro-interaction precision | Motion |
| Staggered reveal choreography | anime.js |
| Physics spring / drag | Motion |
| Cursor-reactive / magnetic | Motion + custom |
| Continuous ambient motion | anime.js `onScroll`/WAAPI, or CSS only |
| Native view-transition driven | Motion `animateView()` |
| 3D parallax depth | React Three Fiber |
| Text-morph / split-char | anime.js `splitText` or GSAP `SplitText` |
| Minimal / restrained | — deliberately, as a contrast choice, not an oversight |

*(Full rationale + risk notes in Section 11's Library Selection Matrix.)*

### Axis 5 — Surface Treatment
Glassmorphic layering · flat/no-shadow · soft neumorphic · grainy texture overlay · hard-edge bordered · elevated soft-shadow cards · mesh-gradient blobs · photographic full-bleed · line-art/wireframe overlay · duotone image treatment

### Axis 6 — Depth & Dimensionality
Flat 2D · subtle parallax layers · full 3D/WebGL hero · isometric illustration · layered z-index collage · video backgrounds · interactive particle fields · skeuomorphic realism · scroll-linked camera movement · static/deliberate flatness

### Axis 7 — AI-Native Interaction Layer (optional, for agentic/AI-facing products)
Streaming typewriter reveal · expressive state avatar (idle/thinking/speaking) · live reasoning trace · voice waveform/audio-reactive UI · tool-call/action timeline · confidence/uncertainty visual language · command-palette/terminal-first interaction · none — conventional chat bubble

### Constraint Injection (optional — pick one per project)
No rounded corners anywhere · one accent color, used in exactly one place per screen · type-only hero, zero imagery · motion budget of 3 animated elements, everything else static · no stock photography · the grid must break at least once, deliberately · every CTA follows the same verb-first pattern · dark mode is the only mode · pair two axis choices that shouldn't work together and make it work

### Cliché Check (run before Section 4)
- Does this combination match one of the three defaults in Section 0? → revise.
- Would this exact combination come out of a completely different brief? → it's a default, not a choice — revise.
- Are numbered markers, eyebrows, or dividers encoding real structure, or just decorating? → cut if decorative.
- Is the type pairing specific to this brief, or the same two families as last time? → check Appendix A.
- Name the ONE signature element (Section 16) now — everything else in Sections 4–17 stays disciplined around it.

**→ Direction Statement:** An award-winning Light-Editorial Quartz Storyboard experience (`#F8F7F4` Warm Quartz canvas, `#FFFFFF` Frosted Glass cards, `#0C0C0E` Deep Mineral Obsidian typography, `#FF4500` International Vermilion primary action accent, and `#2563EB` Royal Blue intelligence glow). Anchored by `Space Grotesk` display typography paired with `Plus Jakarta Sans` body and `JetBrains Mono` code, orchestrated with Framer Motion (`motion/react`) scroll reveals, spring tab transitions, and interactive 3D DAG node physics.

---

## 4. Design Tokens

### 4a. Color Palette
| Token | Hex | Usage | Notes |
|---|---|---|---|
| `primary` | `#FF4500` | International Vermilion — Primary CTAs, active DAG nodes | High-energy editorial accent |
| `primary-hover` | `#E03E00` | Hover state for primary buttons | Smooth spring transition |
| `secondary` / `accent` | `#2563EB` | Royal Blue — Intelligence layer glow, active links | Signal status |
| `background` | `#F8F7F4` / `#F3F1EC` | Warm Quartz — Core background | Pristine editorial canvas |
| `surface` | `#FFFFFF` | Frosted Glass — Story cards, cockpit panels | Soft hairline glass borders |
| `text-primary` | `#0C0C0E` | Deep Mineral Obsidian — Display headings & body | High-contrast editorial readability |
| `text-muted` | `#52525B` / `#71717A` | Slate Graphite — Subtext & captions | Clean legibility |
| `border` | `rgba(12, 12, 14, 0.08)` / `#E4E4E7` | Hairline border dividers | Subtle structure |
| `success` / `warning` / `error` | `#059669` / `#D97706` / `#DC2626` | System state indicator lights | Live telemetry |
| gradients | `linear-gradient(180deg, rgba(255,69,0,0.08) 0%, rgba(248,247,244,0) 100%)` | Hero ambient warmth glow | Elegant editorial lighting |

### 4b. Typography Scale
| Element | Family | Size | Weight | Line-height | Letter-spacing |
|---|---|---|---|---|---|
| Display / H1 | Space Grotesk / Syne | 3.5rem (56px) - 4.5rem (72px) | 700 / 800 | 1.1 | -0.03em |
| H2 | Space Grotesk | 2.25rem (36px) - 2.75rem (44px) | 700 | 1.2 | -0.02em |
| H3 | Space Grotesk / Plus Jakarta Sans | 1.35rem (22px) - 1.5rem (24px) | 600 | 1.3 | -0.01em |
| Body | Plus Jakarta Sans / Inter | 1.0rem (16px) | 400 / 500 | 1.6 | 0em |
| Small / Caption | JetBrains Mono | 0.8125rem (13px) | 400 | 1.5 | 0.02em |
| Button / Label | JetBrains Mono | 0.875rem (14px) | 600 | 1.0 | 0.05em UPPERCASE |

- Display face source: Google Fonts (`Space Grotesk`)
- Body face source: Google Fonts (`Plus Jakarta Sans`)
- Mono face: Google Fonts (`JetBrains Mono`)
- Text-transform usage: Labels & Eyebrows uppercase with tracking
- Link styling: Hover underline glow in Royal Blue `#2563EB`

### 4c. Spacing, Radius & Shadow Scale
| Token | Value | Where used |
|---|---|---|
| Base unit | 4px / 8px | Grid alignment |
| `space-xs … space-3xl` | 8px, 16px, 24px, 48px, 96px | Container section gaps |
| `radius-sm / md / lg / full` | 6px, 12px, 16px, 9999px | Storycards, buttons, badges |
| `shadow-sm / md / lg / xl` | `0 10px 40px rgba(0, 0, 0, 0.04)` | Multi-layered soft card shadows |

### 4d. Breakpoints
| Name | Min-width | Layout notes |
|---|---|---|
| Mobile | 320px | Single column stacked layout |
| Tablet | 768px | 2-column bento & split code viewer |
| Desktop | 1024px | 3-column telemetry & 4-tier bento grid |
| Wide | 1440px | Full container max 1320px centered |
| Desktop | | |
| Wide | | |

Tailwind v4 ships native container-query variants (`@sm`, `@lg`, `@min-*`, `@max-*`) — decide per component whether it should respond to the viewport or to its own container.

---

## 5. Aesthetic & Voice
- Style category (the Section 3 combination, not a single word)
- Mood & tone (3–5 adjectives)
- Reference points surfaced by *this round's* Research Protocol pass — not a static "comparable sites" list
- Copywriting tone (style only — see Voice & Microcopy for the actual approach)

**Voice & Microcopy**
- Name things by what the person controls, not by how the system is built — "notifications," not "webhook config"
- Active voice, and a verb stays the same verb through a flow: a button that says "Publish" produces a toast that says "Published," not "Success"
- Errors state what happened and how to fix it, in the interface's voice — never "Oops!" and never vague
- Empty states are an invitation to act, not a dead end
- One job per element: a label labels, an example demonstrates, nothing does double duty

---

## 6. Information Architecture
- Full page/route inventory
- **Header:** logo placement, nav items, CTA, sticky/transparent behavior, scroll-state change
- **Footer:** column layout, link groups, socials, legal, newsletter

---

## 7. Page-by-Page Breakdown
*Duplicate per page from Section 6.*

**Page:**
- Section order top → bottom
- Hero: what's the single most characteristic thing in this subject's world? Lead with that — not a big-number-plus-gradient template unless it's genuinely the strongest option for this brief
- Layout notes per section (grid, alignment, max-width)
- Components unique to this page

---

## 8. Layout & Grid
- Max content width / container size
- Grid system (CSS grid columns, flex, 12-col)
- Section vertical padding — desktop vs. mobile
- Horizontal padding/margins
- Alignment patterns
- Reflow per breakpoint — and per-container, where Tailwind v4 container queries apply

---

## 9. Component Inventory
| Component | Variants | Key styles | States | Library |
|---|---|---|---|---|
| Button | primary/secondary/ghost/outline | | hover/active/focus/disabled | Kokonut UI or custom + Motion |
| Card / Panel | | | | Kokonut UI |
| Input / Form field | | | | shadcn/ui primitive |
| Nav (desktop) | | | | custom |
| Nav (mobile) | drawer/overlay/dropdown | | | Motion layout animation |
| Badge / Tag / Pill | | | | shadcn/ui |
| Modal / Dialog | | | | shadcn/ui (Radix/Base UI/Aria) |
| Tooltip / Popover | | | | shadcn/ui |
| Accordion | | | | shadcn/ui |
| Tabs | | | | shadcn/ui |
| Chart / Data viz | line/area/ring/radar/bar/sankey | | | Bklit UI |
| Table | | | | shadcn/ui |
| Avatar | | | | Kokonut UI |
| Progress / Loader | | | | anime.js or Motion |

Swap the Library column per project — this is a starting assignment, not a rule.

---

## 10. Backgrounds & Surface Effects
- Section background variety (solid / gradient / image / pattern / video)
- Glassmorphism / backdrop-blur usage
- Border weight & color conventions
- Noise / grain / texture overlays
- Mesh gradients / blobs / orbs
- Native CSS entry animations (`@starting-style`) for cases that don't need a JS library at all

---

## 11. Motion, Animation & 3D

### Choreography
| Element | Trigger | Effect | Duration / Easing | Library |
|---|---|---|---|---|
| | scroll/hover/load | fade/slide/parallax | | |

One orchestrated moment usually lands harder than scattered effects on every element. If it's tempting to animate everything, that's often a sign it's compensating for a weaker structural or typographic choice upstream.

### Library Selection Matrix
| Need | Library | Why | Risk / cost |
|---|---|---|---|
| Component-level UI motion, gestures, layout animations | **Motion** (`motion/react`; `motion/react-client` for RSC-safe usage) | Native React API, hybrid WAAPI+JS engine, 120fps GPU-accelerated, tree-shakable | Needs a `'use client'` boundary — push it as deep/late in the tree as possible |
| Timeline choreography, SVG morph/draw, canvas/hero sequences outside React's render cycle | **anime.js v4** | ESM subpath imports (`animate`, `stagger`, `createTimeline`, `createDraggable`, `onScroll`, `waapi`, `utils`) keep bundles small; native TS types; built-in spring/bounce easing | Clean up in a `useEffect` return, or it leaks outside React's lifecycle |
| Scroll-scrubbed cinematic sequences, pinning | **GSAP + ScrollTrigger** (`@gsap/react`'s `useGSAP()` hook) | The standard for this specific job; 100% free including every former Club plugin (SplitText, MorphSVG, DrawSVG, ScrollSmoother) since Webflow's 2025 acquisition of GreenSock | Heaviest of the three JS animation libraries — lazy-load, scope to routes that need it |
| Buttery smooth scroll | **Lenis** | Pairs with GSAP/Motion, low overhead | Disable under `prefers-reduced-motion` |
| Literal 3D/WebGL | **React Three Fiber + drei** | Declarative Three.js in React | Heaviest bundle on the page — `next/dynamic(..., { ssr: false })`, ship a 2D/poster fallback |
| Pre-built animated primitives (hero/pricing/testimonial blocks) | **Kokonut UI** | 100+ components on shadcn/ui + Motion, MIT-licensed, installed via the shadcn CLI | Free tier plus an optional paid "Pro" template tier — treat any copied component as a starting point, not final |
| Charts / data-viz | **Bklit UI** | Composable line/area/ring/radar/bar/sankey/candlestick components on shadcn/ui | Newer, smaller project than the others — check current component coverage before committing |
| Accessible primitives underneath everything | **shadcn/ui** | CLI v4 lets you pick Radix, Base UI, or React Aria as the base (`--base`); "presets" pack a whole token set into one portable string, which pairs neatly with Section 3's Direction Statement | — |
| Trend research, not runtime code | **Manus** (or similar browsing agent) | Autonomous multi-tab research/crawl for Section 2 | Not a UI library — see Section 0 |

---

## 12. Imagery & Icons
- Photography vs. illustration vs. 3D render vs. icon-only
- Image framing (radius, border, shadow, overlay/gradient masks)
- Icon style (outline/filled/duotone, stroke width, size)
- Avatar/logo treatment

---

## 13. Next.js Architecture
- Next.js 16, App Router only — the Pages Router is in maintenance mode. Confirm the installed version's exact APIs before relying on any of this; patch releases move fast
- Turbopack is the default bundler for both `next dev` and `next build`
- Caching is opt-in by default (Cache Components) — explicitly mark what should be cached rather than assuming Next.js will cache it for you
- Every component in `app/` is a Server Component by default — keep animated leaf components small and pushed deep in the tree. Import Motion from `motion/react-client` where it needs to sit inside an otherwise-server tree, `motion/react` for fully client-side files
- Streaming AI responses: the Vercel AI SDK (`ai` package) has first-class streaming support for OpenAI/Claude/Gemini, integrates directly with App Router streaming — pair with a typewriter-reveal micro-animation for Axis 7
- Fonts via `next/font` (self-hosted, zero layout shift) instead of a manual Google Fonts `<link>`
- SEO via the Metadata API / `generateMetadata`, even on animation-heavy pages — critical content still needs to be server-rendered, not hidden behind client-only JS
- Page-to-page transitions: Motion's `animateView()`, or the native View Transitions API directly
- CSS specificity gotcha: a type-selector (`.section`) and an element/class-based one can silently cancel each other's padding/margin — keep layout classes and animation classes in deliberately ordered layers
- Route Handlers are the boundary to the Python backend in production (see Section 14)

---

## 14. Python Backend Architecture
- **FastAPI** as the default — async, auto-generated OpenAPI docs, and the natural fit for the AI/ML endpoints most of these projects end up needing
- Communication pattern:
  - **Production:** Next.js Route Handlers or Server Actions proxy to FastAPI — keeps API keys/secrets server-side, avoids CORS, lets Next.js caching sit in front
  - **Prototype/hackathon speed:** direct client → FastAPI fetch is fine; tighten it up before it needs to survive contact with real users
- Streaming: a FastAPI `StreamingResponse`/SSE endpoint feeding the Vercel AI SDK on the Next.js side for token-by-token reveal
- Data layer: pick per project — Mongo/ChromaDB/Redis/Supabase are all reasonable defaults if there's no reason to start from zero
- Optional: a small Python + Playwright script to automate the cross-breakpoint screenshot QA pass (desktop hero, mobile hero, nav open/closed, footer, hover/active states) instead of doing it by hand each time

---

## 15. Performance, Accessibility & Risk Register
- Bundle budget: keep core-route JS to roughly 300–500KB gzipped; anything heavier (GSAP, R3F/Three.js) stays lazy-loaded and route-scoped, not in the global bundle
- Hydration mismatch: any library mutating the DOM outside React (anime.js, GSAP) must be scoped to refs and cleaned up in an effect's return function
- CLS: animate `transform`/`opacity` only — never properties that trigger layout (`width`, `height`, `top`, `left`)
- INP: `IntersectionObserver` over scroll-event listeners; rAF-throttle anything that must listen to scroll directly
- LCP: a poster image or 2D fallback for any hero video/3D canvas; defer 3D mount until after first paint
- SEO: critical content must be server-rendered even when it's visually animated in — don't gate meaningful copy behind client-only rendering
- `prefers-reduced-motion` respected everywhere motion is used, without exception
- Tailwind v4 dark-mode gotcha: colors defined with `@theme inline` are baked in at build time and break runtime dark-mode switching — keep raw color channels in `:root`/`.dark` and map them with a non-inline `@theme` instead
- Tailwind v4's modern-CSS baseline (Safari 16.4+, Chrome 111+, Firefox 128+) is a support-matrix decision — make it on purpose, not by accident
- Visible keyboard focus states, including on custom-cursor or magnetic-button treatments
- Concrete tools to actually run before calling it done: Lighthouse/PageSpeed Insights, Motion's own MotionScore animation-performance audit, WebPageTest
- Target bar even for an animation-heavy page: LCP < 2.5s, INP < 200ms, CLS < 0.1

---

## 16. Signature Moment & Misc
Pick ONE from this list and execute it at the highest craft level the timeline allows. Resist doing more than one — that's what "spend your boldness in one place" means in practice.
- Custom cursor
- Load/intro sequence
- Sound design toggle
- Unusual 404
- Custom scrollbar
- Favicon/tab-title animation
- A genuine easter egg

Anything not chosen here stays quiet and disciplined for the rest of the build.

---

## 17. Project File Structure
- Next.js: proposed `/app`, `/components`, `/lib`, `/styles` layout matching Section 9's component breakdown
- Python: proposed service layout (`/app` or `/src`, `/routers`, `/models`, `/services`)
- Where tokens live: `app/globals.css` (`@theme` block — see Section 18), not `tailwind.config.ts`

---

## 18. Ready-to-Paste Starter Kit

**`app/globals.css`** — Tailwind v4, CSS-first config, no `tailwind.config.ts`
```css
@import "tailwindcss";

@theme {
  --color-primary: ;
  --color-secondary: ;
  --color-background: ;
  --color-surface: ;
  --color-text-primary: ;
  --color-text-muted: ;
  --color-border: ;

  --font-display: ;
  --font-body: ;

  --spacing-xs: ;
  --spacing-sm: ;
  --spacing-md: ;
  --spacing-lg: ;
  --spacing-xl: ;

  --radius-sm: ;
  --radius-md: ;
  --radius-lg: ;

  --shadow-sm: ;
  --shadow-md: ;
  --shadow-lg: ;
}

/* Dark mode: raw channels + a non-inline mapping, so runtime toggling keeps working */
:root {
  --bg-channel: 255 255 255;
}
.dark {
  --bg-channel: 10 10 11;
}
@theme {
  --color-background: rgb(var(--bg-channel));
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
*Still on Tailwind v3? Use the equivalent `tailwind.config.ts` `theme.extend` block instead — same tokens, JS-first syntax.*

**`package.json` — dependency notes**
```jsonc
{
  "dependencies": {
    "next": "^16",
    "react": "^19",
    "react-dom": "^19",
    "motion": "^12"           // import from "motion/react" or "motion/react-client"
    // "animejs": "^4"         — add only if this project's Direction uses timeline/SVG choreography
    // "gsap", "@gsap/react"   — add only if it uses scroll-scrubbed cinematic sequences
    // "lenis"                 — add only alongside GSAP/Motion for smooth-scroll feel
    // "three", "@react-three/fiber", "@react-three/drei" — add only for a literal 3D hero
  }
}
```
*Kokonut UI, Bklit UI, and shadcn/ui primitives are copied in via the shadcn CLI (`npx shadcn@latest add ...`), not installed as blanket dependencies — pull only the components Section 9 actually calls for.*

**`main.py` — FastAPI skeleton**
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI(title="")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/stream")
async def stream_response():
    async def event_generator():
        # yield tokens as they arrive from your LLM provider of choice
        yield "data: \n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## ✅ Implementation Checklist
- [ ] Section 2 research run fresh — not reused from a prior project
- [ ] Section 3 direction generated by combining axes, passed the Cliché Check
- [ ] Section 4 tokens defined → exported to Section 18
- [ ] Layout grid & breakpoints set (Section 8)
- [ ] Header & footer built
- [ ] Components built from Section 9, each mapped to its library
- [ ] Backgrounds/surfaces/shadows matched (Section 10)
- [ ] Motion assigned per the Library Selection Matrix (Section 11) — one orchestrated moment, not scattered effects
- [ ] Next.js client/server boundaries deliberate, not accidental (Section 13)
- [ ] Python backend streaming wired to the AI-native axis, if used (Section 14)
- [ ] Performance/accessibility/risk pass complete (Section 15) — reduced-motion, focus states, Core Web Vitals targets
- [ ] Signature moment (Section 16) chosen, and it's exactly one
- [ ] Responsive QA across breakpoints — Playwright script or by hand
- [ ] Direction Ledger updated (Appendix A) before duplicating this file for the next project

---

## Appendix A — Direction Ledger
*Append one row after every project. Feed the last 2–3 rows into Section 1 next time.*

| Date | Project | Axis picks (short) | Signature element | Note |
|---|---|---|---|---|
| 2026-07-30 | APEX Sovereign AI OS | Swiss Grid + Dark Void Tech + JetBrains Mono + Motion + Interactive DAG | Interactive 3D Projected DAG Task Orchestrator | Tactical Amber + Cyber Cyan theme overhaul |