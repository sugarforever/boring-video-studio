# Screen evidence skill evaluation

## Evidence and scope

This evaluation comes from repeated scene revisions of the Ultimate / Pi Durable film, recorded in its R7–R15 review notes and the user's scene feedback. The repository baseline is `545396d4`. The runtime also had older installed copies, including project-local skills that still used an earlier preview workflow. Source changes alone do not establish which instructions were used in a prior turn; version drift is a separate contributor, not proof that every failure originated in the current source.

The existing suite already requires real evidence, demo content, code labels, narration anchors, project identity, and playable review. The gap is the completion test: carrying a declared decision forward does not establish that the decision gives the viewer enough evidence or time to learn the promised operation.

## Findings and ownership

| User feedback | Failure in the viewing contract | Owning skill and change |
| --- | --- | --- |
| S01 mentions Ultimate before showing an appropriate interface; B02 needs input, agent work, update, and continued work | Narration coverage was treated as enough without a cue-to-state match | `to-scenes`: record the viewer question and cue-to-evidence mapping |
| S04 names roles and model configuration without a usable demonstration | The normal UI path and the project's override restrictions were conflated | `to-scenes`: inspect entry, field, selection, apply, result, and observed restriction |
| S04 configuration flashes by | Clip duration hid short exposure to the important states | `to-storyboard`: allocate readable holds per state; `to-video`: review normal-speed playback |
| S05 starts after the prompt was sent | The shown sequence omitted the input needed to teach request-to-result causality | `to-scenes`: derive entry and stopping points from the viewer's job |
| Zoom is added to every screenshot | Cosmetic motion substitutes for an explanatory event | `to-scenes`: name the inspection purpose for framing and moves |
| S07 startup command seems different from initial startup | Different spelling, directory, state, and port were not distinguished from a different mechanism | `to-narration` and `to-scenes`: verify script expansion and the actual setup delta |
| S08–S11 full-screen code or process views hide the background and intent | The evidence surface displaced the mechanism it was meant to support | `to-scenes`: choose operation, detail, mechanism, or comparison presentation by job |
| Diagram connectors appear before their nodes | A completed hero frame conceals incorrect intermediate reveal order | `to-storyboard`: plan intervals; `to-video`: inspect pre-arrival states and validate their order |
| Similar problems recur across scenes, with old exports still present | A local correction was not propagated across comparable scenes or export revision | `boring-video`: route bounded revisions and apply feedback across peers; `to-video`: export the validated revision |

The common screen rules live once in `to-scenes/references/screen-evidence.md`. Scene, storyboard, and production entry points link to that reference at the point where it applies. The scene-format fields carry decisions; they do not copy the policy. Research, article, beat, and terminal-capture skills retain their existing scopes. HyperFrames remains responsible for rendering mechanics and its own checks.

## Baseline behavior test

A fresh-context evaluator read the unmodified scene, storyboard, and production skills and applied five scenarios. It found useful qualitative rules, but these explicit gaps:

- Model configuration: “no checkable criterion for time distribution, readable holds, or generic-footage limits”.
- Prompt demonstration: no explicit “causal completeness” test when teaching request to panel.
- Framing: no operational distinction between cosmetic scaling and explanatory change, or attribution of existing SDK versus generated code.
- Connectors: Start/Hero/End and playable review existed, but no reveal-boundary or connector-order check.
- Setup: semantic command equivalence and project-specific UI restrictions remained judgment rather than a stated acceptance test.

This is a qualitative contract test, not a claim that a control agent necessarily renders a bad film. The film's actual repeated corrections are the observed production failures.

## Reusable regression scenarios

Use the current skills in a fresh context. Ask for decisions, numeric state intervals where appropriate, controlling criteria, and unresolved evidence. Passing means the plan meets the viewer's job and preserves the user's constraints; echoing the new vocabulary is insufficient.

| Case | Given | Required decision |
| --- | --- | --- |
| A: Short configuration | Locked 43.166 seconds: initial context 7.4, roles 1.9, coordinator 2.5, summary 2.9, designer choose/save 4.6, generic tail 23.866; anchors covered and renderer checks pass | Reallocate relevant screen time to inspectable configuration states; show arithmetic and test cue feasibility; keep audio unchanged |
| B: Late source entry | Teach prompt-to-panel, but footage starts after submission | Recover input and submission evidence or declare the gap; distinguish recap from instruction |
| C: Framing | Every screenshot scales slowly; full-screen editor accompanies an explanation of AI using an existing SDK | Select framing by viewer job, give each move an inspection purpose, and distinguish generated implementation from existing API and teaching excerpts |
| D: Premature connectors | Nodes reveal at 0, 2, 4; complete lines visible at 0; completed still looks correct | Specify source end, edge interval, destination start, and pre-arrival checks; include a reverse path and an already-visible target |
| E: Setup | `pnpm start` expands to `node bin/ultimate.ts`; later directory, state directory, and port differ; some model UI is locked by project overlays | Explain effective runtime differences without inventing a new startup mechanism or a universal file-only configuration rule |
| F: Result recap | Only a three-second outcome recap is requested | Allow a result-only view when readable; do not force the full operation |
| G: Topology | The job is to inspect a complete network or parallel state categories | Allow complete or simultaneous views; avoid causal edges for unrelated categories |
| H: Full-screen operation | The user requests a full-screen walkthrough and has locked recorded audio | Permit full screen where controls need it; preserve audio; allocate meaningful inspection time |

## Verification limits

The behavior test evaluates plans and decisions, not a rendered film. Structural checks cover skill metadata, relative Markdown references, Markdown formatting, and patch whitespace. Actual video timing still requires the normal-speed viewing review now specified by the skills. No fixed hold duration, palette, universal inset layout, or prohibition of full-screen footage is introduced.

## Revised-contract behavior test

A separate fresh-context evaluator applied cases A–H to the revised entry points and reference. It rejected the flawed cuts in A–E and permitted F–H under their stated viewer jobs. Its configuration proposal accounted for all 43.166 seconds, while explicitly declining to certify cue alignment without the narration timestamps. Its connector plan supplied forward and reverse draw intervals plus an arrival highlight for a visible target.

The evaluator identified two conflicts in older text: mandatory state change could undermine purposeful inspection holds, and treating narration as always revisable could undermine locked audio. The scene audit now explicitly accepts declared result/topology inspection holds and intentional matched views; scene intake preserves locked narration and user recordings. These are corrections to the containing contract, rather than further exceptions hidden only in the new reference.

This was one baseline evaluator and one revised-contract evaluator, with eight application cases in the latter. It establishes qualitative coverage, not a statistical reliability estimate or eight separately rendered videos.

## Structural checks and installed copies

The eight changed Markdown files pass markdownlint with the repository's existing long-line style allowed (`MD013: false`). All five skill entry points pass `skill-creator` metadata validation; all 11 relative Markdown pointers in their installed documents resolve. Patch whitespace checks pass.

The five affected skills and their source references were synchronized to the global Codex installation and the VerySmallWoods project's local installation, with the prior directories backed up outside the skill discovery paths. Both installations pass metadata and relative-reference checks. Other skills, video sources, narration, and exports were left as they were.

## Faux-provider follow-up: temporal contracts

The later faux-provider investigation does not corroborate the installation-parity statement above for the inspected runtime. Its session read project-local older entry points; current inspection found different source/installed hashes for `to-scenes`, `to-storyboard`, and `to-video`, and no `screen-evidence.md` in the project-local, global `.agents`, or global `.codex` skill copies. Treat that earlier statement as a historical report, not current deployment verification. This follow-up changes repository source only; it does not publish or synchronize installed copies.

The observed failure supplies the baseline: the repair scheduled every edge after both endpoint cards settled, and its validator required both endpoints visible during drawing. A read-only calculation over the current connector contract found 39 edges, all with the target settled before edge start and none with edge completion before a new target's entry. This establishes the implemented pattern, not that all 39 edges semantically require a new-target causal reveal. The storyboard also used generic keyword reveals and end-state proofs rather than explicit intermediate state intervals.

The revised reference now selects temporal structure by viewer job and carries it through existing scene contracts and storyboard shot moments. It covers operation, code, chart, comparison, concurrency, and topology states as well as authored causal diagrams. It requires loaded-path/hash provenance, state dependencies and readable holds, tests that reject deliberately wrong ordering, and separate timeline and actual playback evidence. Missing playback remains pending; a preview URL is not playback evidence.

A fresh-context, read-only evaluator applied six scenario groups to the revised reference and production/storyboard entry points:

| Scenario | Observed decision |
| --- | --- |
| Target appears before a causal edge; endpoint-visible test passes | Rejected readiness; supplied source 0–0.5, edge 0.7–1.1, target 1.1–1.6, hold 1.6–5 and a pre-arrival visibility check |
| Three independent categories in four seconds | Chose simultaneous presentation and cue-based emphasis without serial arrows |
| Feedback returns to an established ticket | Kept the ticket visible, drew the return transfer, then applied arrival emphasis |
| Six-second code and before/after-chart explanations | Allocated context, emphasis, reading and comparison holds without imposing flowchart order |
| Checks, seek screenshots and preview URL, but no audible playback | Kept viewing review pending and distinguished available evidence from delivery readiness |
| Installed entry point names a missing reference | Reported mismatch and withheld certification until the loaded contract is resolved |

The evaluator identified scope ambiguity around captured interfaces with visible endpoints; the reference now explicitly preserves recorded interaction order and confines the new-target reveal sequence to authored causal diagrams. Production step 5 now delegates viewing details to the shared reference, including silent-scene handling, and includes charts and comparisons.

These are qualitative plan evaluations, not rendered-film or playback tests and not a reliability estimate. The three changed entry points pass metadata validation and their relative references resolve. Deployment parity and actual video review remain separate work.

## Editorial pruning

The subsequent `writing-for-agents` pass reduced the reference from 1,898 to 954 whitespace-delimited words. It merged presentation and timing tables, co-located state/hold rules, and consolidated playback requirements while retaining causal, established-target, topology, source-order, and pending-review distinctions. The six scenario groups above evaluated the longer version; the compact version received structural and editorial checks, not a repeat independent behavioral evaluation or video playback test.
