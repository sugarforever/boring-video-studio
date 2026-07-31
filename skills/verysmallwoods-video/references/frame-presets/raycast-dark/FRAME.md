---
version: alpha
name: Raycast Dark — Frame (video / frame layer)
description: >
  Video-first design preset inspired by the Raycast design system — the dark interior of a
  precision instrument, a Swiss watch case carved from obsidian. The unit is the frame
  (1920×1080). Atoms are sacred — a near-black blue-tinted ground (#07080a, never pure black),
  near-white ink (#f9f9f9), ONE saturated Raycast Red (#FF6363) used as sparse punctuation, a
  single humanist family (Inter display + body, with POSITIVE letter-spacing) and JetBrains
  Mono for code, macOS-native multi-layer elevation (box-shadow + inset top highlight),
  barely-visible rgba(255,255,255,0.06–0.1) hairline borders, gradient keycaps, and the
  signature diagonal red-stripe motif. Depth is the identity here — real shadows, not a flat
  plane. Composition, frame scale, and aspect-ratio behavior are written for the frame.
  Restraint governs the red; motion is out of scope.
unit: the frame — 1920×1080 primary; 9:16 and 1:1 documented
principle: atoms are sacred · composition is free · numbers come from the script

colors:
  canvas: "#07080a"                    # DARKEST — near-black blue-tinted ground (never pure black)
  surface: "#101111"                   # elevated surface / standard card background
  card: "#1b1c1e"                      # raised container / badge & tag fill
  key-cap: "#121212"                   # keycap gradient start (→ #0d0d0d bottom)
  ink: "#f9f9f9"                       # LIGHTEST — primary text, high-emphasis
  ink-soft: "#cdcdce"                  # secondary body text, descriptions
  ink-dim: "#9c9c9d"                   # tertiary labels, nav, captions
  ink-mute: "#6a6b6c"                  # disabled / placeholder / low-emphasis
  accent: "#FF6363"                    # Raycast Red — the ONE punctuation (most chromatic)
  border: "#252829"                    # opaque card / divider border (cool gray)
  hairline: "rgba(255,255,255,0.08)"   # live white hairline border on dark surfaces
  highlight: "rgba(255,255,255,0.10)"  # inset top highlight — the macOS light-from-above
  glow: "rgba(215,201,175,0.05)"       # warm ambient glow behind featured elements

typography:
  # — reading ramp (Inter, POSITIVE tracking, weight 500 baseline) —
  body:        { fontFamily: "Inter", cqw: 0.85, weight: 500, lineHeight: 1.6, tracking: "0.012em", color: "ink-soft" }
  body-lede:   { fontFamily: "Inter", cqw: 1.0,  weight: 400, lineHeight: 1.6, tracking: "0.012em", color: "ink" }
  body-sm:     { fontFamily: "Inter", cqw: 0.75, weight: 500, lineHeight: 1.6, tracking: "0.012em", color: "ink-dim" }
  label:       { fontFamily: "Inter", px: 13, weight: 600, tracking: "0.02em", upper: false, color: "ink-dim" }
  kicker:      { fontFamily: "Inter", px: 14, weight: 600, tracking: "0.14em", upper: true, color: "accent" }
  # — chrome / code ramp (JetBrains Mono) —
  mono-chrome: { fontFamily: "JetBrains Mono", px: 13, weight: 500, tracking: "0.02em", upper: true, color: "ink-dim" }
  keycap:      { fontFamily: "JetBrains Mono", px: 13, weight: 600, tracking: "0.02em", color: "ink-soft" }
  code:        { fontFamily: "JetBrains Mono", cqw: 0.78, weight: 500, tracking: "0.018em", color: "ink-soft" }
  # — display ramp (Inter, weight 600, near-zero → slight-negative tracking, tight leading) —
  h3:          { fontFamily: "Inter", cqw: 1.6, weight: 600, lineHeight: 1.2,  tracking: "0.004em" }
  h2:          { fontFamily: "Inter", cqw: 2.6, weight: 600, lineHeight: 1.12, tracking: "0em" }
  headline:    { fontFamily: "Inter", cqw: 3.6, weight: 600, lineHeight: 1.08, tracking: "-0.005em" }
  stat-figure: { fontFamily: "Inter", cqw: 6.6, weight: 600, lineHeight: 0.95, tracking: "-0.012em" }
  display:     { fontFamily: "Inter", cqw: 5.2, weight: 600, lineHeight: 1.05, tracking: "-0.006em" }
  display-hero:{ fontFamily: "Inter", cqw: 6.4, weight: 600, lineHeight: 1.02, tracking: "-0.008em" }

spacing:
  edge: "5cqw"           # standard frame edge inset (~96px@1920) — the safe line
  gutter: "1.25cqw"      # 12-column gutter (~24px@1920)
  unit: "0.417cqw"       # 8px base unit — every spacing step is a multiple
  pad-card: "1.67cqw"    # 32px internal card padding
  pad-top: "5cqw"
  pad-bottom: "5cqw"
  gap-lg: "3cqw"
  gap-md: "1.5cqw"
  radius-card: "0.83cqw" # 16px — standard card / product-window radius
  radius-btn: "0.31cqw"  # 6px — the workhorse button/badge radius
  radius-pill: "4.5cqw"  # 86px+ — full pill for primary CTAs

components:
  elevated-card:
    backgroundColor: "{colors.surface}"
    border: "1px solid {colors.hairline}"
    rounded: "{spacing.radius-card}"
    shadow: "outer ring {colors.card} 0 0 0 1px + inset {colors.canvas} 0 0 0 1px + inset {colors.highlight} 0 1px 0 0 (top light) + drop rgba(0,0,0,0.28) 0 1.2cqw 2.4cqw"
    description: "The macOS-native elevation card — the signature move. Depth is REAL: an outer containment ring, an inset top highlight simulating a light source from above, and a soft drop shadow. Shadows always come in pairs (outer + inset); never a single flat shadow. This is the identity — do not flatten it."
  hairline-border:
    rule: "1px solid {colors.hairline}"
    description: "The barely-visible white rgba border (0.06–0.10) that contains a surface on the dark ground — structurally essential, almost invisible. The opaque {colors.border} (~#252829) cool-gray is its solid-divider cousin. Never a thick or warm border."
  keycap:
    backgroundColor: "linear-gradient({colors.key-cap} → #0d0d0d)"
    border: "1px solid {colors.hairline}"
    rounded: "{spacing.radius-btn}"
    shadow: "5-layer stack — inset {colors.highlight} top + rgba(0,0,0,0.4) drop below — physical 3D key"
    typography: "{typography.keycap}"
    description: "The keyboard shortcut key cap — a gradient-filled physical key with heavy multi-layer shadow. ⌘ K, ⌥ Space. Reinforces the developer-tool identity; use for shortcut chips, never as decoration."
  red-stripe:
    backgroundColor: "{colors.accent}"
    size: "a set of parallel diagonal bars at a fixed 45°/135° angle — from a thin corner motif to a hero field"
    rounded: "0"
    description: "The iconic Raycast diagonal red-stripe pattern — the brand's abstract, geometric signature. Generated by rule (even bars, one angle), one cluster per frame, red only. The atmosphere device, standing in for Swiss's arcs/dots."
  red-accent:
    backgroundColor: "{colors.accent}"
    size: "a kicker tick (0.4cqw × 2.4cqw), a left-border rail (~0.2cqw), a single flagged word, or one stripe field"
    description: "Raycast Red as PUNCTUATION — never pervasive. A flat red tick before a kicker, a red left-rail on an alert card, one red word in a headline, or the stripe motif. Reserve red for hero moments and danger/critical states. Blue is for interactive/info; red is the brand."
  pill-button:
    backgroundColor: "hsla(0,0%,100%,0.815) (primary CTA) or transparent (ghost)"
    color: "{colors.canvas} (on CTA) / {colors.ink}"
    rounded: "{spacing.radius-pill}"
    shadow: "inset {colors.highlight} 0 1px 0 0"
    description: "The primary CTA is a semi-transparent-white pill with dark text and an inset top highlight; secondary is a transparent 6px-radius button with a hairline border. Hover is an OPACITY change (0.6), never a color swap — a signature Raycast interaction."
  badge:
    backgroundColor: "{colors.card}"
    color: "{colors.ink}"
    rounded: "{spacing.radius-btn}"
    typography: "{typography.label}"
    description: "A compact #1b1c1e pill for categorization / status tags. 14px, weight 500, tight 0 6px padding."
  command-row:
    layout: "grid: icon · Inter label · optional keycap / mono meta, right-aligned"
    borderRadius: "{spacing.radius-btn}"
    hover: "{colors.card} fill + hairline"
    typography: "{typography.body} label + {typography.keycap} shortcut"
    description: "The Raycast command-palette list item — an icon, a flush-left label, and a trailing keycap or mono meta. The product-as-content atom (agenda / index / feature list). One row may carry a red accent."
  stat-card:
    backgroundColor: "{colors.surface}"
    border: "1px solid {colors.hairline}"
    rounded: "{spacing.radius-card}"
    typography: "{typography.stat-figure} figure + {typography.label} caption"
    description: "An elevated metric card — big Inter figure over a dim label, on the layered card. Figure in ink (or one figure in red). The KPI atom; the number IS the data, never invented."
  code-block:
    backgroundColor: "{colors.surface}"
    border: "1px solid {colors.hairline}"
    rounded: "{spacing.radius-btn}"
    typography: "{typography.code}"
    description: "A JetBrains Mono code / terminal block on an elevated surface — GeistMono in spirit. Syntax stays low-contrast; the red is reserved for a single flagged token, never rainbow highlighting."
  window-chrome:
    layout: "three 12px dots (traffic lights, rendered gray not colored) top-left of a rounded product window"
    rounded: "{spacing.radius-card}"
    shadow: "elevated-card stack, heavier drop for a floating window"
    description: "The macOS product-window frame — rounded corners, subtle traffic-light dots, deep floating shadow. The image / screenshot slot; imagery sits inside real window chrome, grid-locked."
  page-chrome:
    typography: "{typography.mono-chrome}"
    placement: "section code top-left (e.g. S04 / 06), date or vol. top-right; topic label bottom-left, page № bottom-right — all on the {spacing.edge} safe line"
    description: "The systematic technical annotation. JetBrains Mono, uppercase, tracked, in {colors.ink-dim} — the only persistent chrome. Sits directly on the dark ground, no border."
---

# Raycast Dark — Frame (video / frame layer)

## Overview

Raycast Dark at frame scale is the **Raycast design system rebuilt for 1920×1080** — the dark
interior of a precision instrument, a Swiss watch case carved from obsidian. The background isn't
just dark, it's an almost-black **blue-tinted** void (`#07080a`, never pure black) that makes the
frame feel like the inside of a native macOS application rather than a website. The message is
served on a stage of confident darkness: fast, minimal, trustworthy. Every surface, border, and
shadow is calibrated to evoke a high-performance desktop utility.

The palette is absolute restraint: a near-black **canvas**, near-white **ink**, cool-gray text
steps, and **one saturated Raycast Red** used as sparse punctuation — a kicker tick, a single
flagged word, an alert rail, or the diagonal stripe motif. The red never dominates; it _punctuates_.
The voice is a single humanist family: **Inter** carries every display line and every body line with
**positive letter-spacing** (+0.2px in spirit) — unusual for a dark UI, giving the type an airy,
breathable quality against dense dark surfaces; **JetBrains Mono** carries code and the systematic
chrome. Weight **500** is the body baseline (not 400) — a subtle extra heft that keeps dark-mode text
from feeling thin.

Unlike a flat Swiss plane, **depth is the identity here**. The signature move is the macOS-native
layered shadow: multi-layer box-shadows with inset top highlights that simulate physical depth, as if
cards and keys are pressed or raised glass on a dark desk. Shadows always come in pairs — an outer
containment ring plus an inset highlight. Honor that; it is what makes this read as Raycast and not a
generic dark theme.

**Key characteristics at frame scale:**

- **Near-black blue-tinted ground** — `#07080a`, never pure black; the cold blue tint is essential.
- **Near-white ink + cool-gray steps + ONE red** — `#f9f9f9` ink, `#cdcdce`/`#9c9c9d` secondary; Raycast Red punctuates.
- **One humanist family, positive tracking** — Inter display + body (weight 500 baseline, +tracking); JetBrains Mono for code/chrome.
- **macOS-native multi-layer elevation** — every card/key gets an outer ring + inset top highlight + drop shadow; shadows come in pairs.
- **Barely-visible white hairline borders** — `rgba(255,255,255,0.06–0.10)` containment, structurally essential and almost invisible.
- **Gradient keycaps** — physical 3D key caps for shortcuts; the developer-tool signature.
- **Diagonal red-stripe motif** — the abstract geometric brand mark, generated by rule, one cluster per frame.
- **Rounded, not sharp** — 6px workhorse radius, 16px cards, 86px+ pills; soft corners are correct here.

## The Frame

### Frame Craft Bar

Five eyeball tests gate every frame before any structural check:

- **Squint** — exactly one Inter element dominates as the focal (`display`/`display-hero`/`stat-figure`) against near-white ink on the dark void; hierarchy is size + weight + elevation, red is punctuation only.
- **Silence** — declarative frames read **generously empty**; sections float in a vast dark void, cinematic pacing between elements — dense product, sparse marketing copy.
- **Depth** — every card, key, and product window carries the **paired shadow** (outer ring + inset top highlight + drop); a single flat shadow or a borderless flat rectangle reads as broken.
- **Restraint** — **canvas + ink + ONE red**; the red flags a single element or the stripe motif; borders are barely-visible white hairlines; never a second saturated hue as the primary accent.
- **Reference** — aim at the **Raycast marketing site** — the command palette floating on `#07080a`, keycaps, the hero red stripes; failure looks like a **pure-black flat card deck with harsh borders and no inset light**.

- **Primary:** 1920×1080 (16:9). Display authored in **`cqw`** (`px ÷ 1920 × 100 = cqw`).
- **Vertical:** 1080×1920 (9:16). **Square:** 1080×1080 (1:1).
- **Safe area:** `edge` (5cqw) generous gutters; content and the ~1200px-equivalent container hang from the `edge` line; the stripe motif may bleed off an edge.

**The container law (load-bearing).** Every frame ground sets `container-type: size`; ALL frame-relative
units are `cqw`/`cqh` against it — never `vw`. Card radii, hairline widths, shadow spreads, keycap
sizes, and the stripe geometry all hold their proportion against the frame at any render size.

## Colors

Tokens are the identity. `{colors.canvas}` (`#07080a`) is the near-black blue-tinted ground — the
darkest surface and the stage; `{colors.ink}` (`#f9f9f9`) near-white is headlines and high-emphasis
text; `{colors.ink-soft}` / `{colors.ink-dim}` / `{colors.ink-mute}` are the cool-gray text steps for
secondary, tertiary, and disabled copy. `{colors.surface}` (`#101111`) and `{colors.card}` (`#1b1c1e`)
are the two elevated surfaces — standard cards and raised fills. `{colors.accent}` Raycast Red
(`#FF6363`) is the ONE accent — a kicker tick, a flagged word, an alert rail, or the stripe motif, used
sparingly. `{colors.border}` (`#252829`) is the opaque cool-gray divider; `{colors.hairline}` /
`{colors.highlight}` are the live white rgba borders and the inset top light; `{colors.glow}` is the
subtle warm ambient aura behind featured elements.

**Blue is for interactive/info, red is the brand.** When emphasis is needed: raise the type, add an
elevated card, or add ONE red element. Red never becomes a palette — it is a signal. Never use pure
black (`#000000`) — the blue tint differentiates Raycast from a generic dark theme. Headlines are ink
or (rarely) red; body is a cool-gray step; the ground is the near-black canvas.

## Typography

One humanist family carries the whole voice. The **display ramp** (Inter `h3` 1.6cqw → `display-hero`
6.4cqw, weight **600**, near-zero to slight-negative tracking) carries every headline — confident but
not oversized; Raycast avoids typographic spectacle in favor of functional elegance. The **reading
ramp** (Inter body 0.85cqw, weight **500** baseline, **positive** tracking) carries copy + labels. The
**chrome/code ramp** (JetBrains Mono) carries section codes, keycaps, and code.

- **Legibility floor:** any load-bearing line ≥ **1.4cqw**; px labels/mono are chrome only.
- **Positive tracking on dark:** body carries +0.012em (+0.2px in spirit) — deliberately airy, unlike most dark UIs; display tightens to near-zero / slight-negative optically at the largest sizes only.
- **Weight 500 baseline:** body uses medium (500), not regular (400) — the extra heft keeps dark-mode text from feeling thin. Display is **600**, never 800/900 — Raycast is restrained, not shouty.
- **Fit-to-measure:** size the headline to its length. ≤3 words → `display`/`display-hero`; 4–6 → `headline`/`h2`; 7+ → `h3`. Hero stats use `stat-figure`.
- **Case:** headlines sentence case; ALL-CAPS reserved for short `kicker`/`mono-chrome`; keycaps and code in JetBrains Mono. Enable OpenType `calt`, `kern`, `liga`, `ss03` on Inter where available.

## Depth & Surface

**Depth is real here — this is the one place Raycast departs from a flat plane.** Hierarchy comes from:

- **Elevation** — the macOS-native paired shadow (outer containment ring + inset top highlight + soft drop); cards and keys read as raised or pressed glass.
- **Scale contrast** — the 6.4cqw → 0.75cqw span; one focal element against precise small type.
- **Weight** — Inter 600 display vs Inter 500 body.
- **The one red** — a single red block, word, rail, or the stripe motif draws the eye.
- **The dark void** — generous negative space; content floats on `#07080a`.

**Shadow law:** shadows always come in **pairs** — an outer ring for containment plus an inset top
highlight (`rgba(255,255,255,0.05–0.25)`) simulating light from above, often with an inset bottom dark.
Never a single flat drop shadow. **Ceiling:** no colorful gradients (except the subtle keycap gradient
and warm glow), no second saturated hue as the primary accent, no harsh solid borders where a hairline
belongs. The blue-tinted void is the stage; content is the performer.

## Shapes

- **6px (radius-btn)** — buttons, badges, keycaps, small interactive elements. The workhorse.
- **16px (radius-card)** — standard cards, product windows, feature panels.
- **86px+ (radius-pill)** — primary CTAs, nav pills — full pill shape.
- **0 (right angle)** — the diagonal stripe bars and full-bleed fields only.
- Soft-rounded rectangles are correct — Raycast is not a sharp-cornered system.

## Components

- **elevated-card** — the macOS-native depth card (outer ring + inset top highlight + drop); the signature surface everything sits on.
- **hairline-border** — the barely-visible white rgba border. **keycap** — gradient physical shortcut keys.
- **red-stripe** / **red-accent** — the diagonal brand motif and red-as-punctuation (tick, rail, one word), one cluster per frame.
- **command-row** — the Raycast command-palette list item (icon · label · trailing keycap). **stat-card** — elevated metric card where the figure IS the data.
- **pill-button** / **badge** — the opacity-hover CTA pill and the compact status tag. **code-block** — JetBrains Mono terminal on an elevated surface.
- **window-chrome** — the macOS product-window image slot. **page-chrome** — mono section code / date / topic / № on the safe line.

## Frame Treatments

> Recipe: ground · anchor · composes · focal · chrome · accent · silence · Fixed/Free · density.
> Every frame sits on `{colors.canvas}`, floats content in a generous dark void, carries paired
> elevation on its cards/keys, and spends the red as sparse punctuation — one accent or stripe cluster max.

### 1 · Cover (identity · move: elevated wordmark + diagonal stripes · center-left)

**Ground** `{colors.canvas}`, content hangs from `edge`. **Composes** page-chrome (S01 / date),
red-stripe cluster (upper-right, bleeding off), kicker (red tick + label), display-hero, an optional
keycap chip. **Focal** a 1–2 line Inter `display-hero` headline in near-white ink, driven center-left,
with a red kicker above and a short Inter lede below; a keycap or CTA pill anchors it. **Chrome** mono
section code / date top; topic / № bottom, in ink-dim. **Accent** the diagonal red stripes + the kicker
tick (optionally one red word). **Silence** vast dark void upper-right behind the stripes. **Fixed** dark
ground, one red cluster, positive-tracked ink. **Free** headline, stripe scale/placement, lede, keycap.
**Density** sparse.

### 2 · Feature / Index (index · move: command-palette rows · left)

**Ground** `{colors.canvas}`, `edge`. **Composes** kicker + h2, an elevated-card holding 4–6
command-rows (icon · Inter label · trailing keycap/mono meta). **Focal** an Inter `h2` over the command
palette — each row an icon, a flush-left label, and a trailing keycap; one row optionally highlighted
with a red rail or red label. **Chrome** page-chrome. **Accent** one red row / red keycap. **Silence**
the card floats in the void with generous margin. **Fixed** paired-shadow card, hairline row dividers,
trailing keycaps. **Free** items, count, which row is red, icons. **Density** standard.

### 3 · Statement / Pull Quote (statement · move: large ink line + one red word · center-left)

**Ground** `{colors.canvas}`, `edge`. **Composes** kicker, display/display-hero, attribution, optional
faint stripe motif (corner). **Focal** a 1–3 line Inter statement in near-white ink, driven center-left,
**one key word set in Raycast Red**; a small mono/`label` attribution beneath a hairline. **Chrome**
page-chrome. **Accent** the single red word (or a short red rail under the line). **Silence** deliberately
open right into the void. **Fixed** positive tracking, one red word, dark ground. **Free** statement,
which word is red, attribution. **Density** sparse.

### 4 · Data / Metrics (data · move: elevated stat cards · grid)

**Ground** `{colors.canvas}`, `edge`. **Composes** kicker + h3, a row of 3–4 elevated stat-cards (Inter
`stat-figure` figure over a `label` caption on the layered card) or a single hero figure. **Focal** either
a row of stat-cards (each a raised card with its figure) or one dominant `stat-figure`; one figure may run
red. **Chrome** page-chrome + a mono SOURCE line. **Accent** one red figure (or a red rail on the leader
card). **Silence** cards float with even gutters; the void frames them. **Fixed** paired-shadow cards,
figures = real data, hairline borders. **Free** figures, card count, which is red. **Density** standard.

### 5 · Two-Panel (content · move: product window + text · split)

**Ground** `{colors.canvas}`, `edge`, split (e.g. text left, product window right). **Composes** kicker
+ h2 + Inter body in the text field; a window-chrome (macOS product window with traffic-light dots, deep
floating shadow) opposite, or a code-block. **Focal** an Inter `h2` + flush-left Inter body, balanced
against the elevated product window / code-block. **Chrome** page-chrome + a mono caption under the
window. **Accent** a red kicker tick or one red word / one flagged code token. **Silence** the gutter
between fields; no filler. **Fixed** window-chrome elevation, hairline borders, positive-tracked body.
**Free** which side is text, split ratio, window vs code. **Density** standard.

### 6 · Closing (closer · move: diagonal stripe field + sign-off · left)

**Ground** `{colors.canvas}`, `edge`. **Composes** a diagonal red-stripe field (a corner or a left rail)
or a single keycap CTA, display, a short mono sign-off, page-chrome. **Focal** a 1–2 line Inter sign-off
in near-white ink flush-left, anchored beside the red-stripe field or above a keycap CTA; a mono URL/`label`
beneath a hairline. **Chrome** page-chrome. **Accent** the red stripes (or one red word). **Silence**
generous void. **Fixed** dark ground, one red cluster, paired elevation. **Free** sign-off, stripes vs
keycap, meta. **Density** sparse.

## Composition Rules

### Do

- Sit **every** frame on `#07080a` (never pure black); float content in a generous dark void — dense product, sparse copy.
- Give every card, key, and product window the **paired shadow** — outer containment ring + inset top highlight + soft drop; shadows come in pairs.
- Set body **positive-tracked** (+0.012em), weight 500; keep display at weight 600 with near-zero tracking — confident, not shouty.
- Use the **one red** sparingly — a kicker tick, a single flagged word, an alert rail, or the diagonal stripe motif (one cluster per frame).
- Contain surfaces with **barely-visible white hairline borders** (rgba 0.06–0.10); use the opaque cool-gray `#252829` for solid dividers.
- Hover / emphasis is an **opacity or elevation** shift, never a color swap; keep interactions macOS-native.

### Don't

- Don't use pure black (`#000000`) as the ground, and don't make red pervasive — blue is for interactive/info, red is the brand punctuation.
- Don't create single-layer flat shadows or borderless flat rectangles — the paired inset-highlight depth is core.
- Don't apply negative tracking to body text — Raycast deliberately uses positive spacing for readability on dark.
- Don't mix typefaces outside Inter / JetBrains Mono; no serifs, no scripts, no decorative faces.
- Don't add a second saturated accent hue, colorful gradient backgrounds, or decorative ornament — the dark void is the stage.
- Don't mix warm and cool borders — stick to the cool-gray / white-rgba border family; keep the warm glow subtle and rare.

## Aspect-Ratio Behavior

| Treatment              | 16:9                                | 9:16                                    | 1:1                          |
| ---------------------- | ----------------------------------- | --------------------------------------- | ---------------------------- |
| Cover                  | wordmark center-left, stripes upper-right | wordmark lower, stripes top          | wordmark center, stripes behind |
| Feature / Index        | card cols left, void right          | full-width card, tighter rows           | card centered, fewer rows    |
| Statement / Quote      | large line center-left, one red word | line stacked taller, red word kept     | line centered block          |
| Data / Metrics         | 3–4 stat-cards in a row             | stat-cards stacked vertically           | 2×2 stat-card grid           |
| Two-Panel              | window + text side-by-side          | stacked (text over window)              | stacked                      |
| Closing                | stripe field left, sign-off right   | stripe field top, sign-off below        | stripes behind, centered block |

Keep the `edge` inset and the paired elevation in every ratio. Re-step display per ratio above the
1.4cqw floor. Stat-card ROWS stack to a column on 9:16 (or a 2×2 grid on 1:1). The keycap and hairline
proportions hold via `cqw`. Positive body tracking holds in every ratio.

## Approved Entities

No real customers, logos, or vendors are defined here — render any such mark as a placeholder (a
window-chrome product slot, or a mono wordmark set in `label`). The Raycast red-stripe motif and keycaps
are CSS-only brand furniture. Screenshot / product slots stay as window-chrome frames until real imagery
is wired.

## Numerals & Claims (hard rule)

Never invent figures, dates, or counts at frame scale. Render slots as `— figure —`, `{metric}`. **Stat
figures must equal real data** — a number is a lie if it doesn't trace to a script figure. Section codes
(S01, S02…) and keycap glyphs are decorative chrome and may be sequential. The `SOURCE —` mono line
carries the citation when the script supplies one.

## Pre-Render Self-Audit

- **Squint** — one Inter focal (display/stat) dominates in near-white ink on `#07080a`; hierarchy is size + weight + elevation.
- **Silence** — content floats in a generous dark void; dense product, sparse marketing copy, nothing crowded.
- **Depth** — every card / key / window carries the paired shadow (outer ring + inset top highlight + drop); no flat rectangles.
- **Palette** — canvas + ink + cool-gray steps + ONE red; red is punctuation (tick / word / rail / stripes), never pervasive; never pure black.
- **Type** — Inter display 600 (near-zero tracking) / Inter body 500 (positive tracking) / JetBrains Mono chrome; ≥1.4cqw floor; caps only on short kickers.
- **Borders** — barely-visible white hairlines (rgba 0.06–0.10) or cool-gray `#252829`; no warm or harsh borders.
- **Motif** — at most one red-stripe / keycap cluster, generated by rule, red only.
- **Anchor** — content weighted to left/center-left, asymmetric; no 3 frames in a row with the same anchor.
- **Fabrication** — every numeral traces to the script, else a placeholder slot.

## Known Gaps

- **Motion intentionally out of scope.** frame.md specifies composition only; entrances/transitions are the animation layer's job (soft `power3.out` / `power4.out` snaps and gentle fades suit the macOS-native feel — nothing bounces garishly).
- **Fonts via Google Fonts.** **Inter** (display + body) ships on Google Fonts and is Raycast's real face. **JetBrains Mono** substitutes for Raycast's **GeistMono** (Vercel's Geist Mono is not reliably on Google Fonts; JetBrains Mono is the safe monospace stand-in, same tool-like character). `SF Pro Text` (Apple system) is unavailable free and falls back to Inter. A CJK pairing (Noto Sans SC 400/600) carries the humanist voice for Hanzi; keep positive tracking and the weight-500 baseline.
- **9:16 / 1:1 are guidance** — verify the 1.4cqw legibility floor, that stat-card rows stack, and that the paired elevation still reads at the smaller container size.
- **Depth is CSS-only** — the macOS multi-layer shadows, gradient keycaps, diagonal red stripes, and window-chrome are all box-shadow / gradient / SVG; no external imagery is required to render the identity.
- **OpenType `ss03`** and the exact Raycast key-cap 5-layer shadow are approximated — Inter on Google Fonts carries `ss03`; the keycap shadow is a faithful multi-layer stand-in, not the pixel-exact original.
