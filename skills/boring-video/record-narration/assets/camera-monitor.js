'use strict';
(() => {
  const monitor = document.getElementById('cameraMonitor');
  const video = document.getElementById('cameraPreview');
  const handle = document.getElementById('cameraDrag');
  const toggle = document.getElementById('toggleCameraPreview');
  const behind = document.getElementById('cameraBehind');
  const aspect = document.getElementById('cameraAspect');
  const ratios = {'16:9': 16/9, '4:3': 4/3, '1:1': 1, '9:16': 9/16};
  const key = 'narration-camera-layout';
  let position = null, drag = null, previewHidden = false, centered = false;
  try {
    const saved = JSON.parse(localStorage.getItem(key));
    if (typeof saved?.hidden === 'boolean') previewHidden = saved.hidden;
    if (typeof saved?.behind === 'boolean') behind.checked = saved.behind;
    centered = saved?.centered === true;
    if (saved && ratios[saved.aspect]) aspect.value = saved.aspect;
    if (Number.isFinite(saved?.x) && Number.isFinite(saved?.y)) position = {x: saved.x, y: saved.y};
  } catch (_) { /* Storage may be disabled. */ }
  function persist() {
    try { localStorage.setItem(key, JSON.stringify({...position, aspect: aspect.value, hidden: previewHidden, behind: behind.checked, centered})); } catch (_) {}
  }
  function place(x, y) {
    const bounds = monitor.getBoundingClientRect();
    const bar = document.getElementById('bar').getBoundingClientRect();
    position = {
      x: Math.max(8, Math.min(x, innerWidth - bounds.width - 8)),
      y: Math.max(8, Math.min(y, Math.min(innerHeight, bar.top) - bounds.height - 8)),
    };
    monitor.style.left = `${position.x}px`;
    monitor.style.top = `${position.y}px`;
    monitor.style.right = 'auto';
  }
  function layout() {
    const ratio = ratios[aspect.value];
    video.style.aspectRatio = String(ratio);
    if (monitor.hidden) return;
    const bar = document.getElementById('bar').getBoundingClientRect();
    const available = Math.max(100, Math.min(innerHeight, bar.top) - 90);
    monitor.style.width = `${Math.min(innerWidth <= 600 ? 160 : 240, innerWidth - 16, available * ratio)}px`;
    const bounds = monitor.getBoundingClientRect();
    place(centered ? (innerWidth - bounds.width)/2 : position?.x ?? bounds.x, centered ? 80 : position?.y ?? bounds.y);
  }
  monitor.addEventListener('pointerdown', event => {
    if (event.button !== 0 || event.target.closest('.camera-toolbar')) return;
    const bounds = monitor.getBoundingClientRect();
    centered = false;
    drag = {id: event.pointerId, x: event.clientX - bounds.x, y: event.clientY - bounds.y};
    monitor.setPointerCapture(event.pointerId);
    monitor.classList.add('is-dragging');
    event.preventDefault();
  });
  monitor.addEventListener('pointermove', event => {
    if (drag?.id === event.pointerId) place(event.clientX - drag.x, event.clientY - drag.y);
  });
  function finish(event) {
    if (drag?.id !== event.pointerId) return;
    drag = null;
    monitor.classList.remove('is-dragging');
    persist();
  }
  monitor.addEventListener('pointerup', finish);
  monitor.addEventListener('pointercancel', finish);
  monitor.addEventListener('lostpointercapture', finish);
  handle.addEventListener('keydown', event => {
    const delta = {ArrowLeft: [-10, 0], ArrowRight: [10, 0], ArrowUp: [0, -10], ArrowDown: [0, 10]}[event.key];
    if (!delta) return;
    event.preventDefault();
    centered = false;
    const bounds = monitor.getBoundingClientRect();
    place(bounds.x + delta[0], bounds.y + delta[1]); persist();
  });
  aspect.addEventListener('change', () => { layout(); persist(); });
  window.addEventListener('resize', layout);
  function visibility() {
    const active = !!video.srcObject;
    monitor.hidden = !active || previewHidden;
    toggle.hidden = !active;
    toggle.setAttribute('aria-pressed', String(!previewHidden));
    toggle.setAttribute('aria-label', previewHidden ? '显示摄像头预览' : '隐藏摄像头预览');
    layout();
  }
  function layering() { document.body.dataset.cameraBehind = String(behind.checked); }
  behind.addEventListener('change', () => { layering(); persist(); });
  toggle.addEventListener('click', () => { previewHidden = !previewHidden; visibility(); persist(); });
  document.getElementById('cameraCenter').addEventListener('click', () => { centered = true; layout(); persist(); });
  window.CameraMonitor = {show: visibility, stop: visibility};
  layering();
  visibility();
  layout();
})();
