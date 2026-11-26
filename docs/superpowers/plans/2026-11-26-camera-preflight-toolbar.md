# Camera preflight and visible device controls

- Move microphone/camera selection, camera enable, ratio, centering, layering and preview visibility to a responsive bottom toolbar. Keep reading preferences and takes in the drawer.
- Camera enable acquires a video-only preview stream. Idle preview, device switching and framing produce no takes, chunks, microphone stream or MediaRecorder.
- Start recording acquires the selected microphone and clones the preview video track into one AV recorder. Stop releases recording tracks but retains the independent preview until camera-off. Permission/device failures leave a recoverable UI and preserve captured chunks.
- Test preview-before-record with zero take/files, stream reuse, hide/show, camera selection/off/disconnect, permission denial, toolbar interaction and mobile bounds. Adapt prior capture/reading regressions, run Python checks and request code review before opening a follow-up PR.
