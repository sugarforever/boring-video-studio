# Camera-friendly reading layout

Goal: Keep the author's reading position near the lens while preserving optional live framing feedback.

- Add a default top-centered three-line reading viewport with adjustable text width and a full-script fallback. Existing manual/automatic scrolling and pause behavior stay authoritative.
- Let the camera preview sit below the text, with theme-colored translucent backing to maintain legibility. A settings action centers the camera under the lens; users can bring it back above text for unrestricted repositioning.
- Add an accessible preview toggle to the recording bar. Hiding the preview changes visibility only; it must retain the same live media tracks and continue recording. Save reading/layout preferences locally.
- Test fixed viewport geometry while scrolling, width/full-view changes, hit-tested layering, centering, track identity and live state across hide/show, stop cleanup, persistence and mobile bounds. Run existing camera and audio regressions and Python suite before updating the existing PR.

The live reading layout does not alter the saved camera footage or final picture-in-picture composition. Preview lifetime is subsequently revised by [camera preflight and toolbar](2026-11-26-camera-preflight-toolbar.md).
