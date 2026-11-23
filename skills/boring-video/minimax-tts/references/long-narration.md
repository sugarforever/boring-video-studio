# Long narration

When the script exceeds the synchronous CLI's length limit, split at coherent paragraph or beat boundaries into accepted parts. Keep the platform, model, voice and other settings consistent; synthesize each part into a separate directory.

Assemble the audio through the production workflow, or FFmpeg for standalone delivery. Offset each part's SRT by its actual start in the assembled timeline, including any inserted pauses, and renumber cues. Review joins, full audio and subtitle synchronization before applying the generation branch's completion condition. Retain the part-to-source mapping and original outputs as evidence.

The CLI does not automatically split or merge parts. Consult the [synchronous API](https://platform.minimax.io/docs/api-reference/speech-t2a-http) for service limits and pronunciation/pause controls.
