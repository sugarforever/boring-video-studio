# Scene presets (v1)

This reference defines a small first set of three reusable scene presets for explanatory videos. It is intentionally bounded — not a complete visual catalog. Every preset inherits and must preserve all existing contracts in [`screen-evidence.md`](screen-evidence.md), [`scene-format.md`](scene-format.md), and [`hyperframes-capability-envelope.md`](hyperframes-capability-envelope.md).

## Shared rules

- **Narration alignment**: State reveals, highlights, and transitions follow spoken cues in `NARRATION.md` (or declared silent beats). Never run decorative choreography that fights the narration.
- **Readable holds**: A readable hold begins only after motion settles. Budget separate time for entry, edge drawing, or state shifts before counting hold duration.
- **Truthfulness and evidence**: Presets do not replace `screen_contract` or `demo_contract`. Always label illustrative teaching diagrams, real excerpts, or measured outcomes honestly; never disguise an illustrative preset as captured runtime output.
- **Theme and content variation**: Presets standardize spatial grammar, temporal dependencies, and input bounds — not a single visual skin. Vary palette, typography, surface tokens (CSS custom properties), and domain copy to match the episode's visual world while preserving legibility and WCAG contrast at 1920x1080.
- **Feasibility**: All three presets default to `native` browser composition in HyperFrames (`HTML + CSS + SVG`). If a specific scene adds external media, recorded clips, or heavy 3D, reclassify per `hyperframes-capability-envelope.md`.

---

## 1. `relationship-causal-diagram`

### Selection conditions

- **Use when**: The beat explains how components relate structurally (`topology` mode) or how a trigger, request, or state propagates step-by-step across components (`causal` mode).
- **Do not use when**: Items have no meaningful edges/dependencies (use `structured-list-cards`), or the core job is a matched A/B state diff across shared axes (use `matched-comparison`).

### Explicit mode distinction

Every scene using this preset **must** declare `mode: topology` or `mode: causal`:

| Mode | Viewer job | Temporal contract |
| --- | --- | --- |
| `topology` | Inspect system structure, boundaries, or parallel connections | Complete or simultaneous node/edge view is valid. Guide attention with highlight rings or dimming; do not animate directional arrival that falsely implies execution order. |
| `causal` | Follow execution order, data flow, or cause-and-effect propagation | Enforce `screen-evidence.md` causal ordering: `source reveal end <= edge draw start` and `edge draw end <= new destination reveal start`. New destinations must remain hidden while the incoming edge draws. Previously established destinations stay visible and receive arrival emphasis/state update only after the edge finishes drawing. |

### Bounded inputs

- **Nodes**: 3–5 primary nodes (hard max 6).
- **Edges**: 2–6 connectors; in `causal` mode, at most 1 active causal transfer per narration cue (unless explicitly declaring a parallel branch).
- **Text budgets**:
  - Node title: <= 18 CJK chars or <= 28 Latin chars.
  - Node subtitle/state: optional 1 line, <= 24 CJK chars or <= 40 Latin chars.
  - Edge label: <= 10 CJK chars or <= 18 Latin chars.
- **Required metadata**: `mode` (`topology` | `causal`), `evidence_label` (e.g., `Illustrative Architecture`, `Observed Execution Trace`), and theme CSS tokens (`--bg`, `--surface`, `--ink`, `--muted`, `--accent`, `--edge`, `--edge-active`).

### Layout and timing guidance

- **Canvas**: 16:9 (`1920x1080`), outer padding >= 72px, reserve >= 120px bottom clearance for captions/subtitles.
- **Geometry**:
  - `causal`: left-to-right or top-to-bottom reading spine with explicit directional arrowheads.
  - `topology`: balanced layered or hub-and-spoke layout with clean non-crossing connectors and clear boundary labels.
- **Timing**:
  - Context header & title settle: `0.4s–0.6s`.
  - Per `causal` hop: source reveal `0.4s` → edge draw `0.5s–0.7s` → destination reveal or arrival emphasis `0.4s`.
  - Final readable hold: `>= 1.5s` after the last node/state settles (longer for dense labels).
  - Verify pre-arrival state during `causal` edge draw: a newly introduced destination must not be visible before the edge reaches it.

### Fallbacks

- **Input exceeds 6 nodes or connectors cross**: Split into two scenes — a high-level `topology` overview followed by a focused 3–4 node `causal` path — or simplify into a 3-step `structured-list-cards` (`ordered`) scene.
- **Locked narration too short for full hop-by-hop reveal**: Switch to `topology` mode with pre-established nodes and cue-synced focus highlights, and record the timing tradeoff in `SCENES.md`.
- **Complex interactive/3D graph risk**: Fall back to flat 2D SVG native nodes and paths preserving the exact same dependency story.

### Playable minimal sample

- [`../samples/relationship-causal-diagram/index.html`](../samples/relationship-causal-diagram/index.html)

---

## 2. `matched-comparison`

### Selection conditions

- **Use when**: The beat compares a `before-after` transformation of the same subject or two `parallel` alternatives evaluated across shared dimensions.
- **Do not use when**: The two sides do not share comparable axes (use `structured-list-cards`), or the core job is tracing a multi-step flow (use `relationship-causal-diagram`).

### Modes

- `before-after`: Baseline state on the left, changed state on the right, with explicit delta callouts.
- `parallel`: Two peer options side-by-side with neutral framing and matched criteria rows.

### Bounded inputs

- **Panels**: Exactly 2 matched columns (`left` and `right`).
- **Aligned rows**: 2–4 shared evaluation rows (hard max 4). Every row must align horizontally across both panels.
- **Text budgets**:
  - Panel heading: <= 16 CJK chars or <= 24 Latin chars.
  - Row label: <= 12 CJK chars or <= 20 Latin chars.
  - Row value: <= 20 CJK chars or <= 34 Latin chars.
  - Delta summary bar (optional): 1 line, <= 28 CJK chars or <= 48 Latin chars.
- **Required metadata**: `mode` (`before-after` | `parallel`), per-side `evidence_label` (e.g., `Illustrative Teaching Model`, `Measured Local Run`), and theme tokens (`--bg`, `--panel-a`, `--panel-b`, `--ink`, `--delta-accent`, `--border`).

### Layout and timing guidance

- **Canvas**: 16:9 (`1920x1080`), symmetric 2-column grid (`1fr 1fr`, center gutter `40px–64px`), locked row heights so matching rows share the exact same vertical band.
- **Retention**: Keep both states visible simultaneously during inspection; never swap away the baseline before the viewer can inspect the contrast.
- **Timing**:
  - Establish scene header and left baseline panel: `0.5s`, then hold `1.0s–1.2s` so the baseline registers.
  - Reveal matched right panel: `0.5s`.
  - Shift emphasis onto the key delta row(s) and optional summary bar on the narration cue: `0.4s` per highlight.
  - Final side-by-side readable hold: `>= 2.0s` after all highlights settle.

### Fallbacks

- **>4 comparison rows or wide code/terminal diffs**: Do not cram tiny text side-by-side. Split into two consecutive 2–3 row comparison scenes, or use full-width sequential views with a pinned comparison summary header.
- **Single-state inspection dominates**: Drop the split layout and use standard `screen-evidence.md` full-view framing with a compact status badge.

### Playable minimal sample

- [`../samples/matched-comparison/index.html`](../samples/matched-comparison/index.html)

---

## 3. `structured-list-cards`

### Selection conditions

- **Use when**: The beat presents 2–4 discrete items whose spatial layout directly communicates **order** (`ordered` mode: sequence, pipeline stages, priority) or **grouping** (`grouped` mode: parallel categories, attributes, or checklist clusters).
- **Do not use when**: The scene is an unstructured bullet dump with no spatial meaning, or when explicit inter-node links are the point (use `relationship-causal-diagram`).

### Explicit mode distinction

| Mode | Spatial encoding | Temporal contract |
| --- | --- | --- |
| `ordered` | Explicit ordinal indices (`01`, `02`, `03`), left-to-right or stepped progression | Reveal cards in strict spoken order; emphasize the active card during its cue while retaining prior cards as context. |
| `grouped` | Shared category headers, balanced columns or 2x2 grid, no directional arrows | Reveal simultaneously or by group without implying causal sequence; move a subtle focus frame on each spoken cue. |

### Bounded inputs

- **Cards**: 2–4 cards (hard max 4 simultaneously at 1080p).
- **Per-card content**:
  - Badge/index: ordinal (`01`..`04`) for `ordered` or group tag for `grouped`.
  - Card title: <= 14 CJK chars or <= 22 Latin chars.
  - Supporting lines: 1–2 concise lines, each <= 24 CJK chars or <= 38 Latin chars.
- **Required metadata**: `mode` (`ordered` | `grouped`), `evidence_label`, and theme tokens (`--bg`, `--card-bg`, `--ink`, `--accent-1`, `--accent-2`, `--accent-3`, `--border`).

### Layout and timing guidance

- **Canvas**: 16:9 (`1920x1080`), equal-width card grid (`repeat(N, 1fr)`, gap `28px–36px`) with generous internal padding (`28px–36px`) and minimum body font size `26px` for delivery-size legibility.
- **Timing**:
  - Header settle: `0.4s`.
  - `ordered`: reveal each card on its narration cue (`0.4s` entry + `>= 1.0s` focus hold per card), keeping completed cards readable.
  - `grouped`: reveal all cards together (`0.5s`) or per group, then shift focus frame on spoken cues (`0.35s` shift + `>= 1.0s` hold).
  - Final overview readable hold: `>= 1.8s` with all cards settled.

### Fallbacks

- **>4 items**: Group into 2–3 higher-level categories or split across consecutive scenes; never shrink typography below legible delivery size.
- **Tight locked narration**: Do not convert an `ordered` list into an unordered `grouped` layout just to save time. Preserve explicit ordinal markers (`01`, `02`, `03`) and either render all ordered cards simultaneously with a sequential highlight cue in spoken order, or reduce items / split across consecutive scenes; record the timing tradeoff in `SCENES.md`.

### Playable minimal sample

- [`../samples/structured-list-cards/index.html`](../samples/structured-list-cards/index.html)
