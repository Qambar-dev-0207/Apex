# Design Specification: Hanzo Framer Template

> **Reference URL:** [Hanzo Framer Project](https://framer.com/projects/Hanzo-copy--J583LQ6lVHAWb7Sw9Ohf-giEsZ?id=16a8e905-1c01-4116-941d-d548dcc493f5&reason=web-signup&node=RTbM5kfhR)  
> **Live Site:** [https://hanzo.framer.website/](https://hanzo.framer.website/)  
> **Designer:** Nick Stepuk  
> **Archetype:** Minimalist Luxury / Swiss Modernist Agency & Portfolio

---

## 1. Aesthetic Philosophy & Visual Identity

Hanzo is characterized by an ultra-clean, high-contrast, editorial Swiss design language:
* **Gallery-Grade Whitespace**: Generous macro-padding (`120px` to `180px`) gives every element commanding visual presence without clutter.
* **1px Hairline Structural Discipline**: Elevation is communicated through razor-sharp `#D9D9D9` 1px borders rather than diffuse drop shadows.
* **Typographic Contrast**: Combines geometric grotesque display headers (`Inter Display`) with italicized serif accents (`Instrument Serif`) and technical code tags (`Fragment Mono`).
* **Singular Punctuation Accent**: A monochromatic black-and-white canvas punctuated exclusively by an electric red-orange (`#FF3700`) for primary calls to action and a live status green (`#0CB300`).

---

## 2. Color System & Design Tokens

### Primary Palette

| Token | Hex Value | RGBA Equivalent | Role |
| :--- | :--- | :--- | :--- |
| `canvas-bg` | `#FFFFFF` | `rgb(255, 255, 255)` | Pure white page background |
| `surface-subtle` | `#FAFAFA` | `rgb(250, 250, 250)` | Secondary section background |
| `surface-card` | `#F5F5F5` | `rgb(245, 245, 245)` | Subtle card fill & preview containers |
| `chip-bg` | `#F0F0F0` | `rgb(240, 240, 240)` | Feature tags, badges, and toggle tracks |
| `hairline-border` | `#D9D9D9` | `rgba(0, 0, 0, 0.15)` | Primary structural borders and dividers |
| `border-subtle` | `#EBEBEB` | `rgba(0, 0, 0, 0.08)` | Inner container dividers |
| `text-primary` | `#000000` | `rgb(0, 0, 0)` | Headings, primary labels, active chips |
| `text-secondary` | `#545454` | `rgba(0, 0, 0, 0.67)` | Body copy, secondary descriptions |
| `text-muted` | `#8C8C8C` | `rgba(0, 0, 0, 0.45)` | Captions, metadata, inactive links |
| `accent-primary` | `#FF3700` | `rgb(255, 55, 0)` | Primary CTA buttons, pricing highlights |
| `accent-hover` | `#E03000` | `rgb(224, 48, 0)` | Hover state for primary buttons |
| `status-green` | `#0CB300` | `rgb(12, 179, 0)` | Live availability pulse dot |
| `dark-surface` | `#000000` | `rgb(0, 0, 0)` | Terminal block & high-contrast panels |
| `dark-card` | `#262626` | `rgb(38, 38, 38)` | Elevated dark chips |

### Alpha & Overlay Tokens
* `overlay-light`: `rgba(255, 255, 255, 0.85)` (backdrop blur header)
* `mask-gradient`: `linear-gradient(225deg, #FFFFFF 0%, #E8E8E8 100%)`
* `radial-mask`: `radial-gradient(125% 100% at 0 0, #000000 0%, rgba(0, 0, 0, 0.22) 88%, transparent 100%)`

---

## 3. Typography System

### Typeface Stack
1. **Primary Display & Headings**: `Inter Display`, sans-serif
2. **Body & UI**: `Inter`, sans-serif
3. **Editorial Accent / Quotes**: `Instrument Serif` (italic & normal)
4. **Technical / Metadata**: `Fragment Mono` or `JetBrains Mono`

### Type Scale & Hierarchy

| Level | Size (Desktop) | Size (Mobile) | Weight | Line Height | Tracking | Usage |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Hero Display (H1)** | `84px` | `44px` | 800 (ExtraBold) | `1.04` | `-0.035em` | Hero main headline |
| **Section Title (H2)**| `48px – 56px` | `32px` | 800 (ExtraBold) | `1.08` | `-0.03em` | Major section headings |
| **Card Title (H3)** | `28px – 32px` | `22px` | 700 (Bold) | `1.15` | `-0.02em` | Project cards, pricing tiers |
| **Subhead / Lead** | `20px – 24px` | `18px` | 400 (Regular) | `1.50` | `-0.01em` | Manifesto, hero subtext |
| **Body Standard** | `15px – 16px` | `14px` | 400 (Regular) | `1.60` | `0` | Paragraphs, feature lists |
| **Buttons & Nav** | `14px` | `13px` | 600 (SemiBold) | `1.00` | `0` | Navbar links, pill actions |
| **Badges & Overlines**| `11px – 12px`| `10px` | 600 (SemiBold) | `1.00` | `+0.05em` | Mono tags, step numbers |

---

## 4. Layout, Grids & Whitespace Hierarchy

### Breakpoints
* **Desktop Wide**: `1440px` (Stage Canvas)
* **Desktop Standard**: `1200px` (Inner Grid Boundary)
* **Content Column**: `1000px` (Focused Reading Width)
* **Tablet**: `810px` (2-column collapse)
* **Mobile**: `390px` (Single column stack)

### Spacing Scale
* **Section Vertical Padding (Macro)**: `120px` to `180px` (`pt-36 pb-28` to `py-32`)
* **Container Gaps (Meso)**: `48px`, `64px`, `80px` between title rows and card grids
* **Card Internal Padding**: `32px` to `48px` (`p-8 sm:p-10`)
* **Micro Spacing**: `8px` to `16px` between badges, titles, and metadata tags

### Border Radius Hierarchy
* **Pill Elements**: `9999px` (Buttons, status tags, toggle containers)
* **Cards & Containers**: `24px – 32px` (`rounded-3xl` for projects, pricing, and showcase)
* **Inner Badges & Chips**: `8px – 12px` (`rounded-xl` for code blocks and inner pills)

---

## 5. Section-by-Section Deconstruction

### 1. Navigation Header
* **Layout**: Centered floating pill bar (`rounded-2xl`, ~`64px` height).
* **Styling**: `bg-white/95` backdrop-blur with 1px `#D9D9D9` border.
* **Elements**:
  * Brand wordmark on the left with live status green pulse dot.
  * Nav links with active hover pills and dropdown chevron.
  * Mega-menu dropdown: 3-quadrant technical blueprint (Guides with contour illustration, Tools with monospace bit-stream, Case studies with bell curve, and API Docs footer banner).
  * Right: `Sign in` link + `#FF3700` primary pill CTA.

### 2. Hero Section
* **Layout**: Centered single-column layout within `1000px` max-width.
* **Elements**:
  * Status Pill: `Booking Open · 2 Spots Left` with `#0CB300` pulse dot.
  * Headline: Massive 84px typography with rotating keyword transition.
  * Subtitle: `#545454` neutral text constrained to `660px`.
  * CTA Group: Dual pill buttons (`#FF3700` primary + white outline secondary).
  * Social Proof: Avatar cluster with 5-star rating and "Trusted by Leaders".
  * Browser Showcase: Browser chrome (`apex://live-kernel`) split into SVG visualizer and deep-black (`#000000`) reasoning trace terminal.

### 3. Logo Marquee (Social Proof Ticker)
* **Layout**: Full-width infinite ticker band with vertical edge masks.
* **Styling**: `#FFFFFF` background with top and bottom `#D9D9D9` hairlines.
* **Elements**: Monospace brand chips (`#F0F0F0` background) separated by muted dots (`·`).

### 4. Manifesto Statement & Interactive Service Tags
* **Layout**: Left-aligned or centered `1000px` container.
* **Headline**: Oversized editorial typography (`48px – 60px`) stating the core mission.
* **Service Tags**: Horizontal flex-wrap row of `#F0F0F0` pill chips that scale and invert to black when active, updating a detail card below.

### 5. Process Pipeline ("Our Process, Explained")
* **Layout**: Asymmetric header (left title, right description) over a 3-column card grid.
* **Card Anatomy**:
  * Step number in bold `#FF3700` (`01`, `02`, `03`).
  * Step title and uppercase mono subline.
  * Description paragraph in `#545454`.
  * Bottom quote card with verified metric badges.

### 6. Projects & Case Studies
* **Layout**: 2×2 card grid with hover-zoom micro-interactions.
* **Card Anatomy**:
  * Category badge + stat tag in top row.
  * Large H3 card title with hover color transition.
  * Description copy + bottom link with trailing arrow (`Inspect Trace →`).
  * Embedded live interactive harness (DAG visualizer + tabbed terminal).

### 7. About & Metric Grid ("Pushing Boundaries")
* **Layout**: 2-column split (12-column grid: 6 cols narrative, 6 cols metrics).
* **Left**: Manifesto narrative detailing engineering philosophy.
* **Right**: 4-box grid of large stat cards (`<38ms`, `18.4×`, `24`, `0.00%`) with titles and technical subtitles.

### 8. Hardware Telemetry & Oscilloscope
* **Layout**: 4-column card row.
* **Cards**: Real-time waveform canvas/SVG displays (sine, bars, random) monitoring RAM, cache latency, AST compression, and cost.

### 9. Developer SDK Playground
* **Layout**: Integrated code editor container with syntax highlighting and copy-to-clipboard actions.

### 10. Pricing & Licensing ("Fixed Price, Zero Limits")
* **Layout**: Centered header with Monthly / Annual pill toggle (featuring a green `20% OFF` badge) over 3 cards.
* **Tiers**:
  * Developer Core (Standard card, outline button).
  * Production Swarm (Featured card with 2px `#FF3700` border, `MOST POPULAR` pill, primary `#FF3700` button).
  * Custom / Enterprise (Dark button, air-gapped specs).
* **Card Anatomy**: Tier name, price per month, description, checkmark feature list, full-width CTA button.

### 11. FAQ Accordion
* **Layout**: Single-column container (`1000px` max-width) with clean hairline dividers.
* **Accordion Item**: Question title with hover underline, tag badge, plus/minus or chevron toggle, and smooth expandable answer body.

### 12. Final Booking CTA & Footer
* **CTA Banner**: Centered `2 spots available` pill, giant H2 with `#FF3700` highlight, dual action buttons.
* **Footer**: Light `#FFFFFF` surface with `#D9D9D9` top border, large watermark wordmark in low opacity (`0.025`), 4-column link directory, and live status ping.

---

## 6. Motion & Interaction Rules

| Interaction | Duration | Easing | Implementation |
| :--- | :--- | :--- | :--- |
| **Button Hover** | `250ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `translateY(-2px)`, shadow bloom |
| **Card Hover** | `300ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | Border turns `#000000`, `translateY(-2px)` |
| **Mega-Menu Dropdown**| `240ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | `opacity: 0 -> 1`, `scale: 0.98 -> 1`, `y: 12px -> 0` |
| **Rotating Keyword** | `450ms` | `cubic-bezier(0.16, 1, 0.3, 1)` | Slide up out, slide up in (`y: 50 -> 0 -> -50`) |
| **Infinite Marquee** | `32s` | `linear` | Seamless `translateX(-50%)` loop |

---

## 7. What is Deliberately NOT There (Anti-Patterns)

* **No Saturated Multi-Color Glows**: No purple/cyan neon blobs or colored blur gradients.
* **No Heavy Drop Shadows**: Elevation is communicated through flat hairlines (`#D9D9D9`).
* **No Generic Stock Photography**: All visual content consists of live UI mockups, terminal windows, and vector blueprints.
* **No Multi-Level Submenus**: Mega-menu content is structured in flat, visible quadrants.
* **No Cluttered Badges**: Every badge uses minimal padding, uppercase mono typography, and neutral fills.
