# HyperFrames capability envelope

Read this reference while directing scenes. It defines feasibility classes, not implementation recipes. HyperFrames' installed skills remain authoritative for current APIs, components, providers, and workflow behavior.

## Native browser expression

Treat these as normal scene-design territory:

- typography, shapes, diagrams, charts, interfaces, and data visualization;
- 2D staging, depth layers, parallax, masks, paths, and virtual camera motion;
- SVG, Canvas, WebGL, and Three.js scenes;
- deterministic animation, transformations, and transitions;
- local images, video, audio, captions, screen capture, and brand assets.

## Media or provider dependency

Mark the dependency when a scene requires:

- a real person, place, event, product, or recorded performance;
- copyrighted, brand-specific, or otherwise unavailable source material;
- generated image, generated video, voice, music, or sound effects;
- an authenticated site, browser session, or external provider.

## High-cost or uncertain treatment

Mark both the risk and a simpler fallback for:

- long or complex 3D sequences;
- detailed character acting or crowd animation;
- precise physical simulation;
- photoreal generative-video continuity across shots;
- exact reconstruction of an event without source media;
- any essential treatment whose provider, credentials, or assets are unconfirmed.

## Feasibility notation

Use one of these values in each scene:

- `native`: feasible with normal browser composition;
- `media`: feasible after named media is resolved;
- `provider`: feasible after the named external capability is available;
- `high-cost`: feasible but materially expensive in time or rendering;
- `uncertain`: needs a proof before storyboard approval.

For every value except `native`, name the dependency. Also name a fallback when that dependency is essential to the scene. Classify browser-native work as `uncertain` when its performance or interaction complexity needs a proof before approval. Every fallback preserves the scene's cognitive job.
