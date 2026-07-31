---
version: alpha
name: Claude Warm — Frame (video / frame layer)
description: >
  Video-first design preset in the warm literary-editorial idiom, inspired by the Claude (Anthropic)
  design system. The unit is the frame (1920×1080). Atoms are sacred — a warm parchment ground
  (#f5f4ed) that reads like high-quality paper, a warm near-black ink (#141413), ONE earthy terracotta
  accent (#c96442) used warmly and sparingly, a muted olive-green as a quiet secondary mark, exclusively
  warm-toned neutrals (every grey has a yellow-brown undertone), a medium-weight editorial serif for
  display (Newsreader, weight 500, sentence case), a humanist sans for body (Inter), and JetBrains Mono
  for chrome/data. Comfortable serif line-heights (1.10–1.30 display, 1.50–1.60 body), soft warm-cream
  hairlines, gentle rounded editorial cards with a whisper of shadow, and generous magazine pacing.
  Warm and human, the opposite of clinical — organic warmth over tech-cold. Composition, frame scale,
  and aspect-ratio behavior are written for the frame; motion is out of scope.
unit: the frame — 1920×1080 primary; 9:16 and 1:1 documented
principle: atoms are sacred · composition is warm & editorial · numbers come from the script

colors:
  canvas: "#f5f4ed"     # parchment ground — the LIGHTEST value, warm cream, the emotional foundation
  panel: "#faf9f5"      # ivory — the lightest card/elevated surface on parchment
  sand: "#e8e6dc"       # warm sand — button + prominent interactive surfaces
  ink: "#141413"        # warm near-black — the DARKEST value, primary type + dark surface
  ink-2: "#30302e"      # warm charcoal — dark containers / nav / secondary dark surface
  ink-soft: "#5e5d59"   # olive grey — secondary body text
  ink-faint: "#87867f"  # stone grey — tertiary text, footnotes, mono ticks
  accent: "#c96442"     # terracotta — the ONE brand accent, most CHROMATIC value, used warmly
  accent-soft: "#d97757" # coral — a lighter, warmer terracotta variant for smaller accents / on-dark
  sage: "#6a6f4e"       # muted olive-green — a quiet, low-saturation secondary mark (never competes)
  line: "#e8e6dc"       # border warm — the soft cream hairline for rules, dividers, card edges
  line-soft: "#f0eee6"  # border cream — the gentlest containment, barely-there card border
  grid: "rgba(20,20,19,0.05)"  # optional editorial construction grid — revealed as chrome only

typography:
  # — reading ramp (Inter, humanist sans, relaxed literary line-height) —
  body:        { fontFamily: "Inter", cqw: 0.92, weight: 400, lineHeight: 1.6, color: "ink-soft" }
  body-lede:   { fontFamily: "Inter", cqw: 1.08, weight: 400, lineHeight: 1.6, color: "ink" }
  body-sm:     { fontFamily: "Inter", cqw: 0.8,  weight: 400, lineHeight: 1.55, color: "ink-soft" }
  label:       { fontFamily: "Inter", px: 13, weight: 500, tracking: "0.02em", color: "ink" }
  kicker:      { fontFamily: "JetBrains Mono", px: 14, weight: 500, tracking: "0.16em", upper: true, color: "accent" }
  # — chrome / data ramp (JetBrains Mono) —
  mono-chrome: { fontFamily: "JetBrains Mono", px: 13, weight: 400, tracking: "0.08em", upper: true, color: "ink-soft" }
  mono-tag:    { fontFamily: "JetBrains Mono", cqw: 0.78, weight: 500, tracking: "0.04em" }
  mono-tick:   { fontFamily: "JetBrains Mono", px: 12, weight: 400, tracking: "0.04em", color: "ink-faint" }
  # — display ramp (Newsreader, editorial serif, single medium weight 500, sentence case) —
  h3:          { fontFamily: "Newsreader", cqw: 2.0, weight: 500, lineHeight: 1.3,  tracking: "0" }
  h2:          { fontFamily: "Newsreader", cqw: 3.2, weight: 500, lineHeight: 1.2,  tracking: "-0.005em" }
  headline:    { fontFamily: "Newsreader", cqw: 4.6, weight: 500, lineHeight: 1.15, tracking: "-0.008em" }
  stat-figure: { fontFamily: "Newsreader", cqw: 8.0, weight: 500, lineHeight: 1.0,  tracking: "-0.01em" }
  display:     { fontFamily: "Newsreader", cqw: 6.4, weight: 500, lineHeight: 1.12, tracking: "-0.01em" }
  display-hero:{ fontFamily: "Newsreader", cqw: 8.4, weight: 500, lineHeight: 1.1,  tracking: "-0.012em" }
  vbig-numeral:{ fontFamily: "Newsreader", cqw: 12.0, weight: 500, lineHeight: 0.95, tracking: "-0.015em" }

spacing:
  edge: "6cqw"          # generous editorial frame margin (~115px@1920) — content breathes from here
  gutter: "1.5cqw"      # column gutter (~29px@1920)
  baseline: "0.42cqw"   # 8px base rhythm — vertical positions step on the 8px unit
  pad-top: "6cqw"
  pad-bottom: "6cqw"
  gap-lg: "3.5cqw"
  gap-md: "1.75cqw"

components:
  measure-grid:
    layout: "grid: repeat(12, 1fr); column-gap: {spacing.gutter}; inset: {spacing.edge}"
    overlay: "optional faint {colors.grid} column rules — construction lines, off by default, revealed as chrome"
    description: "The quiet editorial measure. Blocks hang on a generous 12-column field over the 8px rhythm, but placement is warm and literary — a comfortable text measure and generous margins, not a rigid Swiss lock. Composition breathes; the grid guides rather than commands."
  hairline:
    rule: "0.06cqw solid {colors.line}"
    description: "The soft warm-cream 1px rule — section dividers, index rows, card edges, chart baselines. Cream-tinted and gentle (never harsh ink), it is the lightest possible containment. Occasionally a terracotta rule flags one element."
  accent-underline:
    color: "{colors.accent}"
    size: "a 0.16cqw–0.28cqw terracotta rule beneath one word, one kicker, or a short phrase"
    rounded: "1cqw (soft, organic ends)"
    description: "Terracotta used warmly — a hand-drawn-feeling underline under a single accent word or a kicker. The signature emphasis device; warm, editorial, never a hard knockout block."
  accent-block:
    backgroundColor: "{colors.accent}"
    size: "a small solid mark — from a 0.3cqw × 2.4cqw kicker tab to a slim column rule"
    rounded: "0.3cqw (softened corners)"
    description: "A small, softly-cornered terracotta fill used as a warm compositional mark or to flag the single most important element. Earthy, un-tech — a block with gently rounded corners, never a sharp signal bar and never a gradient or glow."
  kicker:
    typography: "{typography.kicker}"
    marker: "a short {colors.accent} tab or {colors.sage} dot set before the label"
    description: "A small mono overline in terracotta, tracked and uppercase — the quiet editorial section marker. Optionally preceded by a soft terracotta tab or a muted-green dot."
  sage-mark:
    fill: "{colors.sage} soft dots, a small organic cluster, or a single quiet mark"
    size: "4–14cqw block, corner-set"
    rounded: "50% (dots) or soft"
    description: "The muted olive-green secondary — a quiet, hand-drawn-feeling cluster of soft dots or a single organic mark. Decorative punctuation, low saturation, always subordinate to the terracotta accent. One per frame at most."
  editorial-card:
    backgroundColor: "{colors.panel}"
    border: "0.06cqw solid {colors.line-soft}"
    rounded: "1.4cqw (comfortably rounded, ~16px@1920)"
    shadow: "0 0.2cqw 1.2cqw rgba(20,20,19,0.05) — a whisper only"
    description: "A gentle ivory card on parchment: soft cream border, comfortably rounded corners, a whisper-soft shadow (0.05 opacity). Warm and approachable — NOT a harsh clinical card. Depth is a barely-perceptible lift, never a heavy drop shadow."
  index-row:
    layout: "grid: mono ordinal · Newsreader serif label · optional mono meta"
    borderBottom: "0.06cqw solid {colors.line}"
    typography: "{typography.mono-tag} ordinal + {typography.h3} serif label"
    description: "A numbered contents row on a soft cream rule — the agenda/index atom. Serif label, mono ordinal; one row may carry a terracotta accent word or underline."
  h-bar:
    backgroundColor: "{colors.accent} (or {colors.sand} for context bars)"
    size: "height ~1.6cqw, width = value ÷ max × available field"
    rounded: "0.4cqw (softly rounded ends)"
    description: "A warm horizontal ranking bar with softly rounded ends; width IS the data. Terracotta for the leader, warm sand for the context bars. End-labelled with a {typography.mono-tick} figure over a soft hairline."
  kpi-figure:
    typography: "{typography.stat-figure} serif figure in ink, {typography.label} caption beneath a hairline"
    accent: "one figure may be set in {colors.accent}"
    description: "A big serif numeral (stat-figure / vbig-numeral) is the warm-editorial way to show a stat — a book-title-scale figure over a quiet label, not a chart. One figure may run terracotta."
  image-field:
    backgroundColor: "{colors.panel}"
    border: "0.06cqw solid {colors.line-soft}"
    rounded: "1.4cqw (comfortably rounded, ~16px; hero media up to 2.6cqw ~32px)"
    mark: "a soft {colors.sage} organic mark or a diagonal — the editorial-photo slot, generously rounded"
    typography: "{typography.mono-tick} caption below the field, flush-left"
    description: "The place a warm, editorial photograph or organic illustration goes — an ivory panel with generously rounded corners. Until wired, a soft sage placeholder mark. Imagery is human and editorial, never cold documentary."
  page-chrome:
    typography: "{typography.mono-chrome}"
    placement: "section code top-left (e.g. S04 / 12), date or vol. top-right; topic label bottom-left, page № bottom-right — all on the {spacing.edge} safe line"
    description: "The quiet technical annotation. Mono, uppercase, tracked, in stone-grey — the only persistent chrome, kept whisper-light so the editorial calm holds."
---

# Claude Warm — Frame (video / frame layer)

## Overview

Claude Warm at frame scale is a **warm literary salon rebuilt for 1920×1080** — the unhurried, quietly
intellectual editorial language inspired by the Claude (Anthropic) design system. Where most AI/product
frames lean cold and futuristic, this one radiates human warmth: the entire frame sits on a **parchment
ground (`#f5f4ed`)** that deliberately evokes high-quality paper rather than a screen. The message is
served with good taste and comfortable pacing — clarity through calm, not through austerity.

Hierarchy comes from a **medium-weight editorial serif** (Newsreader at weight 500, sentence case) that
gives every headline the gravitas of a book title, set against a **humanist sans** (Inter) for body and
**JetBrains Mono** for the systematic chrome. The palette is warm restraint: parchment ground, a **warm
near-black ink (`#141413`)** with a barely-perceptible olive undertone, exclusively **warm-toned neutrals**
(every grey has a yellow-brown cast — no cool blue-greys anywhere), **ONE earthy terracotta accent
(`#c96442`)** used sparingly and warmly, and a **muted olive-green** as a quiet secondary mark. Atmosphere,
when any, is **organic and hand-drawn-feeling**: soft cream hairlines, a whisper of shadow on gentle
rounded cards, small sage dot clusters — never geometric tech ornament.

**Key characteristics at frame scale:**

- **Parchment paper ground** — `#f5f4ed` warm cream reads as premium paper, not a screen; it IS the personality.
- **Warm neutrals only** — every grey carries a yellow-brown undertone; the darkest ink (`#141413`) is warm, never cool black.
- **Serif display / sans body / mono chrome** — Newsreader medium (500, sentence case) headlines · Inter body · JetBrains Mono chrome.
- **ONE terracotta accent, used warmly** — a soft underline, a small softly-cornered block, or a single accent word; earthy and un-tech.
- **Muted-green secondary** — a quiet olive-green mark, low saturation, always subordinate to terracotta.
- **Comfortable serif line-heights** — 1.10–1.30 for display (tight but never cramped), a relaxed 1.50–1.60 for body.
- **Soft, organic warmth** — cream hairlines, gently rounded cards (16–32px), whisper shadows; the opposite of clinical.
- **Generous magazine pacing** — editorial whitespace and light/dark section alternation give a book-like reading rhythm.

## The Frame

### Frame Craft Bar

Five eyeball tests gate every frame before any structural check:

- **Warmth** — the ground is parchment (`#f5f4ed`) or a warm dark (`#141413`), never pure white or cool grey; every neutral has a yellow-brown undertone. If it feels cold or screen-like, it's broken.
- **Voice** — exactly one Newsreader serif element carries the frame at book-title scale (`display`/`display-hero`/`vbig-numeral`), sentence case, weight 500; the serif/sans split (serif headline, sans body) is intact.
- **Calm** — declarative frames read **40–55% open**; whitespace is generous and editorial, an active compositional element — unhurried, never crowded, never austere.
- **Restraint** — parchment + warm ink + ONE terracotta; terracotta flags a single element warmly; the muted green stays quiet and subordinate; **no** cool blue-grey, no second saturated hue, no hard drop shadow.
- **Reference** — aim at a **fine literary magazine spread or a well-set essay page** — warm, lived-in, thoughtful; failure looks like a **cold, blue-grey, hard-shadowed clinical SaaS deck**.

- **Primary:** 1920×1080 (16:9). Display authored in **`cqw`** (`px ÷ 1920 × 100 = cqw`).
- **Vertical:** 1080×1920 (9:16). **Square:** 1080×1080 (1:1).
- **Safe area:** `edge` (6cqw) generous editorial margins; content hangs from the `edge` line, organic marks may bleed softly off an edge.

**The container law (load-bearing).** Every frame ground sets `container-type: size`; ALL frame-relative
units are `cqw`/`cqh` against it — never `vw`. The editorial measure, the 8px rhythm, the soft 1px
hairlines, and the rounded-corner radii all hold their proportion against the frame at any render size.

## Colors

Tokens are the identity. `{colors.canvas}` parchment is the warm paper ground; `{colors.panel}` ivory and
`{colors.sand}` warm sand are the elevated surfaces; `{colors.ink}` warm near-black is headlines,
body-in-ink, and dark surfaces; `{colors.ink-2}` warm charcoal is dark containers; `{colors.ink-soft}`
olive-grey is secondary body and `{colors.ink-faint}` stone-grey is tertiary/mono ticks. `{colors.accent}`
terracotta is the ONE brand accent — a soft underline, a small softly-cornered block, a chart leader, or a
single flagged word, used sparingly and warmly; `{colors.accent-soft}` coral is its lighter variant for
smaller accents and on-dark text. `{colors.sage}` muted olive-green is the quiet secondary mark.
`{colors.line}` / `{colors.line-soft}` are the warm cream hairlines. `{colors.grid}` is the optional
editorial construction overlay, revealed as chrome only.

**Every grey is warm; terracotta is the only voice.** When emphasis is needed: grow the serif, warm the
underline, or add ONE terracotta element. The muted green may punctuate but never competes — keep it
low-saturation and subordinate. Never introduce a cool blue-grey or a second saturated hue. Headlines are
ink or (rarely) one terracotta word; body is ink or warm grey; the ground is parchment or warm dark.

## Typography

Three faces, a warm editorial voice. The **display ramp** (Newsreader serif, `h3` 2.0cqw → `display-hero`
8.4cqw and `vbig-numeral` 12cqw, single medium weight **500**, sentence case, gentle negative tracking)
carries every headline. The **reading ramp** (Inter body 0.92cqw grey / lede in ink at a relaxed 1.6
line-height, labels in px) carries copy + labels. The **chrome/data ramp** (JetBrains Mono) carries section
codes, kickers, ticks, and data figures.

- **Legibility floor:** any load-bearing line ≥ **1.4cqw**; px labels/mono are chrome only.
- **Fit-to-measure:** size the headline to its length. Cap the block at a comfortable measure (headlines
  hang from the left margin or center for a title). ≤3 words → `display`/`display-hero`; 4–7 → `headline`/`h2`;
  8+ → `h3`. Hero stats use `vbig-numeral`/`stat-figure`.
- **Single serif weight (500).** All Newsreader display uses weight 500 — no bold, no light. The single-weight
  consistency is the voice, as if one author set every heading. Contrast comes from SIZE, not weight.
- **Comfortable line-heights.** Display sits at **1.10–1.30** — tight but never cramped; the serif needs the
  breathing room. Body sits at a relaxed **1.50–1.60** for a literary, book-like read (never below 1.4).
- **Case & tracking.** Headlines are sentence case (never ALL-CAPS). Gentle negative tracking on large serif
  display; near-zero on body. Uppercase + wide tracking reserved for short mono `kicker`/`label`/chrome only.

## Depth & Surface

Warmth and softness carry depth — there is no hard elevation. Hierarchy comes from:

- **Scale contrast** — the 12cqw → 0.8cqw span; one book-title serif element against quiet precise type.
- **Serif vs sans** — Newsreader 500 display vs Inter 400 body; the editorial split reads as hierarchy.
- **Warm surface layering** — parchment → ivory → sand → charcoal → ink; the eye reads a gentle "gradient" through warm tones.
- **The one terracotta** — a single warm underline, block, or word draws the eye.
- **Generous whitespace** — 40–55% open; editorial calm carries as much as ink.
- **Whisper shadow** — at most a `0 0.2cqw 1.2cqw rgba(20,20,19,0.05)` lift on a gentle rounded card; a barely-perceptible float, never a cast.

**Ceiling:** no heavy drop shadow, no gradient, no blur, no cool blue-grey, no second saturated hue, no
sharp corner on a card (softness is core). Depth is warm, soft, and gently layered — never harsh.

## Shapes

- **Comfortably rounded (1.4cqw ~16px)** — the default for cards, image fields, containers; softness is the identity.
- **Generously rounded (2.6cqw ~32px)** — hero media, large featured containers.
- **Soft small radii (0.3–0.4cqw)** — the terracotta accent block and bar ends carry gently softened corners.
- **50% (circle)** — sage dots and organic marks.
- Hard right-angle SaaS corners and sharp signal bars **do not exist** — every edge is at least gently softened.

## Components

- **measure-grid** — the quiet 12-column editorial measure over the 8px rhythm; guides warmly, never a rigid lock (optional faint overlay as chrome).
- **hairline** — the soft warm-cream 1px rule (occasionally terracotta). **accent-underline** / **accent-block** — warm terracotta emphasis: a soft underline, a small softly-cornered mark.
- **kicker** — the mono terracotta overline marker. **sage-mark** — the quiet muted-green organic secondary (soft dot cluster / single mark), one per frame.
- **index-row** — a numbered serif contents row on a cream rule. **h-bar** / **kpi-figure** — warm data: softly-rounded terracotta/sand bars, or a big serif figure.
- **editorial-card** — a gentle ivory card, cream border, rounded, whisper shadow. **image-field** — the warm editorial-photo slot (soft sage mark until wired). **page-chrome** — mono section code / date / topic / № in stone-grey on the safe line.

## Frame Treatments

> Recipe: ground · measure anchor · composes · focal · chrome · accent · calm · Fixed/Free · density.
> Every frame is warm parchment (or warm dark), 40–55% open, ONE terracotta accent used warmly, serif headline / sans body, at most one sage mark.

### 1 · Cover (identity · move: serif title + soft sage cluster · left or centered)

**Ground** `{colors.canvas}`, content hangs from `edge`. **Composes** page-chrome (S01 / date), a soft
`{colors.sage}` dot cluster (upper-right, bleeding gently off), kicker, display-hero. **Focal** a 1–3 line
Newsreader `display-hero` title in ink, driven to the **lower-left** and hung from the left margin (or
centered as a title page), with a terracotta `kicker` above and a short Inter lede below — **one word of the
title may carry a terracotta underline**. **Chrome** mono section code / date top; topic / № bottom.
**Accent** the terracotta kicker + one underlined word; the sage cluster stays quiet. **Calm** ~50% open —
the counter-space is intentional editorial air. **Fixed** parchment ground, serif title 500, one terracotta,
warm neutrals. **Free** title, sage cluster scale/placement, lede, left vs centered. **Density** sparse.

### 2 · Index / Contents (index · move: numbered serif rows on cream rules · left)

**Ground** `{colors.canvas}`, `edge`. **Composes** kicker, h2, 4–6 index-rows spanning a comfortable
measure. **Focal** a Newsreader `h2` over numbered index-rows (mono ordinal + Newsreader serif label, each
on a soft cream rule), one row optionally carrying a terracotta accent word or underline. **Chrome**
page-chrome. **Accent** one terracotta row-word or ordinal; optional sage dot beside the active row.
**Calm** the right counter-margin held open. **Fixed** soft cream rules, serif labels, mono ordinals.
**Free** items, count, which row is accented. **Density** standard (generously spaced rows).

### 3 · Pull-Quote / Statement (statement · move: large serif quote · left)

**Ground** `{colors.canvas}`, `edge`. **Composes** kicker, display/display-hero serif quote, attribution,
optional soft sage mark (corner). **Focal** a 1–3 line Newsreader statement hung from the left margin at
book-title scale, **one key word underlined or set in terracotta**; a small mono/`label` attribution beneath
a cream hairline. **Chrome** page-chrome. **Accent** the single terracotta word or underline (or a slim
terracotta rule beside the quote). **Calm** ~50–55% — deliberately open to the right, editorial air.
**Fixed** serif 500, sentence case, one terracotta emphasis. **Free** statement, which word is accented,
attribution. **Density** sparse.

### 4 · Data / Stats (data · move: big serif figure or warm bars · left)

**Ground** `{colors.canvas}`, `edge`. **Composes** kicker + h3, a `vbig-numeral`/`stat-figure` hero figure
OR a warm h-bar stack (3–4 rows), mono ticks. **Focal** either a book-title-scale serif **figure** in ink
(one accent figure may run terracotta) over a quiet `label`, or a horizontal h-bar ranking (softly-rounded
terracotta leader among warm-sand bars, bar width = value, end-labelled); baselines on a soft cream rule.
**Chrome** page-chrome + a mono SOURCE line. **Accent** the one terracotta figure or leader bar. **Calm**
moderate — the figure/chart occupies the lower field, kicker + headline the upper-left. **Fixed** figures/bar
lengths = real data, soft hairline baseline, warm bars with softened ends. **Free** figures, bar count,
figure-vs-bars. **Density** standard.

### 5 · Two-Column Editorial (content · move: soft image + serif text · split)

**Ground** `{colors.canvas}`, `edge`, editorial split (e.g. text left ~5 cols, image-field right ~6 cols).
**Composes** kicker + h2 + Inter body in the text field; an image-field (ivory, generously rounded, soft
sage mark until wired) opposite. **Focal** a Newsreader `h2` + relaxed Inter body, balanced against the
gently-rounded image-field. **Chrome** page-chrome + a mono caption under the image. **Accent** a terracotta
kicker or one underlined word. **Calm** the gutter between fields; unhurried, no filler. **Fixed** cream
field edges, serif heading / sans body, comfortable measure. **Free** which side is text, split ratio, copy.
**Density** standard.

### 6 · Closing (closer · move: soft terracotta mark + serif sign-off · left or centered)

**Ground** `{colors.canvas}` (or a warm dark `{colors.ink}` section for a chapter close), `edge`. **Composes**
a soft sage cluster or a slim terracotta accent-block, a Newsreader `display` sign-off, a short mono sign-off
line, page-chrome. **Focal** a 1–2 line serif sign-off in ink (or ivory on dark) hung flush-left or centered,
with **one terracotta word or underline**; a mono URL/`label` beneath a cream hairline. **Chrome** page-chrome.
**Accent** the terracotta word / slim block; the sage mark stays quiet. **Calm** ~50%. **Fixed** serif 500,
one terracotta, warm ground. **Free** sign-off, mark vs block, dark vs light close, meta. **Density** sparse.

## Composition Rules

### Do

- Keep the ground **warm** — parchment (`#f5f4ed`) or warm dark (`#141413`); keep every neutral yellow-brown-toned.
- Set headlines in **Newsreader serif at weight 500, sentence case**; body in **Inter** at a relaxed 1.5–1.6 line-height.
- Hold **40–55% open** editorial whitespace as an active counter-weight; let the frame breathe like a magazine spread.
- Make **one** serif element carry the frame at book-title scale; build contrast from **size**, not weight.
- Use the **one terracotta** warmly and sparingly — a soft underline, a small softly-cornered block, or a single flagged word.
- Keep the muted **sage green** quiet and subordinate; soften every corner (cards 16–32px); use at most a whisper shadow.
- Alternate warm light and warm dark sections for a book-like chapter rhythm when the sequence allows.

### Don't

- Don't use pure white or any cool blue-grey — the whole palette is warm; a cold neutral breaks the identity.
- Don't set headlines in a sans, in ALL-CAPS, or in bold (700+); Newsreader weight 500 sentence case is the ceiling.
- Don't introduce a second saturated hue or let the muted green out-shout terracotta; terracotta is the only accent voice.
- Don't use sharp corners on cards/containers, hard drop shadows, gradients, or blur — softness and warmth are core.
- Don't crowd the frame or reduce body line-height below 1.4; the generous spacing IS the editorial personality.
- Don't use cold, clinical, or geometric tech ornament; marks are organic and hand-drawn-feeling (soft sage dots, warm underlines).

## Aspect-Ratio Behavior

| Treatment              | 16:9                              | 9:16                                   | 1:1                             |
| ---------------------- | --------------------------------- | -------------------------------------- | ------------------------------- |
| Cover                  | serif title lower-left, sage upper-right | title lower, sage top, taller measure | title centered, sage behind     |
| Index / Contents       | rows left, margin right           | full-width rows, comfortable leading   | rows on a 6-col measure         |
| Pull-Quote / Statement | large serif quote flush-left      | quote stacked, taller, accent word kept| quote flush-left, centered block|
| Data / Stats           | serif figure / h-bar horizontal   | serif figure stacked, h-bars vertical  | compact figure or bars          |
| Two-Column Editorial   | text + image side-by-side         | stacked (text over image)              | stacked                         |
| Closing                | mark left, sign-off right/centered| mark top, sign-off below               | mark behind, centered block     |

Collapse the editorial measure to **6 columns on 9:16** and **6 on 1:1**; keep the `edge` inset and the 8px
rhythm. Re-step display per ratio above the 1.4cqw floor. A wide h-bar row stays horizontal but shortens on
9:16; a hero serif figure scales and stays centered. The serif/sans voice and warm ground hold in every ratio.

## Approved Entities

No real customers, logos, or vendors are defined here — render any such mark as a placeholder (the soft
image-field with a sage mark, or a mono/`label` wordmark). Photography and illustration slots stay as
image-fields until real warm, editorial imagery (or a hand-drawn-feeling illustration) is wired.

## Numerals & Claims (hard rule)

Never invent figures, dates, or counts at frame scale. Render slots as `— figure —`, `{metric}`. **Bar
widths and figure emphasis must equal real data scaled proportionally** — a bar is a lie if its length
doesn't trace to a script number. Index ordinals (01, 02…) are decorative and may be sequential. The
`SOURCE —` mono line carries the citation when the script supplies one.

## Pre-Render Self-Audit

- **Warmth** — parchment or warm-dark ground; every neutral yellow-brown-toned; no pure white, no cool blue-grey.
- **Voice** — exactly one Newsreader serif element at book-title scale, weight 500, sentence case; serif headline / sans body split intact.
- **Calm** — declarative frames 40–55% open; editorial air is intentional, nothing crowded, nothing austere.
- **Palette** — parchment + warm ink + ONE terracotta; terracotta flags a single element warmly; sage quiet and subordinate; body ink/warm-grey.
- **Type** — Newsreader display (500, sentence case) / Inter body (1.5–1.6) / JetBrains Mono chrome; ≥1.4cqw floor; caps only on short mono labels.
- **Depth** — no hard drop shadow, no gradient, no blur, no cool grey; cards/containers softly rounded (16–32px); at most a whisper shadow.
- **Marks** — at most one sage cluster or organic mark, quiet and low-saturation; emphasis is a warm terracotta underline/word/block.
- **Anchor** — left-hung or editorially centered; no 3 frames in a row with the identical anchor.
- **Fabrication** — every numeral and every bar length traces to the script, else a placeholder slot.

## Known Gaps

- **Fonts are Google-Fonts substitutes.** Claude's real display face is the custom **Anthropic Serif** (unavailable); **Newsreader** (weight 500, sentence case) stands in as a warm medium-weight editorial serif — Fraunces or Source Serif 4 are acceptable alternates. **Anthropic Sans** → **Inter** (humanist sans); **Anthropic Mono** → **JetBrains Mono**. All three ship on Google Fonts. A CJK pairing (Noto Serif SC 500 display / Noto Sans SC 400 body) carries the warm editorial voice for Hanzi; keep the serif/sans split and the comfortable line-heights.
- **Motion intentionally out of scope.** frame.md specifies composition only; entrances/transitions are the animation layer's job (gentle `power2.out` / `power3.out` fades and soft rises suit the warm editorial calm — nothing snaps hard, nothing floats mechanically).
- **9:16 / 1:1 are guidance** — verify the 1.4cqw legibility floor, the measure collapse to 6 columns, and that the serif title and warm bars re-step and stay legible.
- **Marks, bars, figures, hairlines, and the soft image-field are CSS/SVG-only** — no external imagery is required to render the identity; wire warm editorial photography or a hand-drawn illustration when available.
</content>
</invoke>
