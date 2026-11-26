'use strict';
const $ = id => document.getElementById(id);
const UI = window.RecorderUI;
let sessionTakes = [], handed = null;
const key = `recorder-token:${location.host}`;
const token = location.hash.slice(1) || sessionStorage.getItem(key) || '';
sessionStorage.setItem(key, token);
history.replaceState(null, '', location.pathname);
let recorder, stream, context, analyser, levelData, takeId, chunks = [], nextUpload = 0, uploadQueue = Promise.resolve();
let busy = false, selected = null, started = 0, elapsed = 0, scrollOn = false, lastFrame = 0, scrollCarry = 0;
let playerURL, backupURL, activeRegion, captureWarning;
const regions = WaveSurfer.Regions.create();
const waveform = WaveSurfer.create({container: '#waveform', media: $('player'),
  height: 76, waveColor: '#ABA496', progressColor: '#57534A', cursorColor: '#26251F',
  plugins: [regions]});
regions.enableDragSelection({color: 'rgba(47,94,140,.13)'});
function selection(region) {
  activeRegion = region;
  regions.getRegions().filter(item => item !== region).forEach(item => item.remove());
  $('selection').textContent = `${region.start.toFixed(2)} - ${region.end.toFixed(2)} 秒`;
  $('playSelection').disabled = busy || recorder?.state === 'recording' || recorder?.state === 'paused';
}
regions.on('region-created', selection);
regions.on('region-updated', selection);
$('playSelection').addEventListener('click', () => activeRegion?.play(true));
const message = text => { UI.say(text); UI.showNotice({kind: 'warn', title: text}); };
function phase(next, info = {}) { UI.setPhase(next, {chunks: nextUpload, total: chunks.length, ...info}); }
function savedPhase() {
  const take = sessionTakes.find(take => take.id === selected);
  phase(take ? 'saved' : 'idle', {take});
}
async function api(path, body) {
  const headers = {'X-Recorder-Token': token};
  if (body !== undefined && !(body instanceof Blob)) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(body);
  }
  const response = await fetch(path, {method: body === undefined ? 'GET' : 'POST', headers, body});
  if (!response.ok) {
    const data = await response.json();
    const error = new Error(data.error || `请求失败 (${response.status})`);
    error.status = response.status;
    throw error;
  }
  return response.json();
}
function controls() {
  const active = recorder && recorder.state !== 'inactive';
  $('record').disabled = busy || active;
  $('retrySave').disabled = busy || active;
  $('review').disabled = busy || active;
  $('lock').hidden = !busy && !active;
  $('pause').disabled = busy || !active;
  $('stop').disabled = busy || !active;
  $('mic').disabled = busy || active;
  $('cameraEnabled').disabled = busy || active;
  $('camera').disabled = busy || active || !$('cameraEnabled').checked;
  waveform.setOptions({interact: !busy && !active});
  $('playSelection').disabled = busy || active || !activeRegion;
  $('finish').disabled = busy || active || !selected;
  document.querySelectorAll('#takes button').forEach(button => { button.disabled = busy || active || button.dataset.unavailable === 'true'; });
}
async function preview(take) {
  const response = await fetch(`/api/takes/${take.id}/audio`, {headers: {'X-Recorder-Token': token}});
  if (!response.ok) throw new Error('试听加载失败');
  const blob = await response.blob();
  if (playerURL) URL.revokeObjectURL(playerURL);
  playerURL = URL.createObjectURL(blob);
  $('player').pause();
  activeRegion = null; regions.clearRegions(); $('playSelection').disabled = true;
  $('selection').textContent = '拖动波形选择试听范围';
  $('waveform').dataset.ready = 'false';
  UI.setPreview(take);
  $('player').classList.toggle('audio-only', !take.video);
  $('player').src = playerURL;
  try {
    await waveform.loadBlob(blob);
    $('waveform').dataset.ready = 'true';
  } catch (error) { message(`波形加载失败，仍可用播放器试听：${error.message}`); }
  selected = take.id;
  document.querySelectorAll('[data-take]').forEach(button => {
    button.setAttribute('aria-pressed', String(button.dataset.take === selected));
    button.classList.toggle('is-sel', button.dataset.take === selected);
    button.querySelector('.radio')?.classList.toggle('is-on', button.dataset.take === selected);
    const tag = button.querySelector('.tag');
    if (tag) tag.textContent = button.dataset.take === handed ? '已交接' : button.dataset.take === selected ? '已选中' : '完整';
  });
  controls();
}
async function refresh() {
  const state = await api('/api/state');
  if ($('scriptInner').dataset.source !== state.script) {
    UI.renderScript(state.script);
    $('scriptInner').dataset.source = state.script;
  }
  selected = state.selected;
  handed = state.status === 'ready' ? selected : null;
  sessionTakes = state.takes.map((take, index) => ({...take, n: index + 1,
    duration: take.id === takeId ? elapsed : undefined}));
  const handle = recover => async take => {
    busy = true; controls();
    try {
      if (recover) {
        await api(`/api/takes/${take.id}/finalize`, {chunks: take.chunks});
        await refresh(); savedPhase();
        message('已恢复保存部分。中断录音请试听确认，尾部可能缺失。');
      } else { await preview(take); savedPhase(); UI.clearNotice(); }
    } catch (error) { message(error.message); }
    finally { busy = false; controls(); }
  };
  UI.renderTakes(sessionTakes, {selected, handed, locked: busy || !!(recorder && recorder.state !== 'inactive'),
    onPick: handle(false), onRecover: handle(true), onAbandon: async take => {
      busy = true; controls();
      try {
        await api(`/api/takes/${take.id}/abandon`, {});
        await refresh(); savedPhase();
        message('已放弃此版本，已保存的文件仍保留。可以改稿或重新录制。');
      } catch (error) { message(error.message); }
      finally { busy = false; controls(); }
    }});
  const current = sessionTakes.find(take => take.id === selected && take.complete);
  if (current) await preview(current);
  controls();
  return state;
}
async function microphones() {
  const devices = await navigator.mediaDevices.enumerateDevices();
  const previous = $('mic').value;
  $('mic').replaceChildren(new Option('系统默认麦克风', ''));
  devices.filter(device => device.kind === 'audioinput').forEach((device, index) => {
    $('mic').add(new Option(device.label || `麦克风 ${index + 1}`, device.deviceId));
  });
  $('mic').value = previous;
  const camera = $('camera').value;
  $('camera').replaceChildren(new Option('系统默认摄像头', ''));
  devices.filter(device => device.kind === 'videoinput').forEach((device, index) => {
    $('camera').add(new Option(device.label || `摄像头 ${index + 1}`, device.deviceId));
  });
  $('camera').value = camera;
}
async function upload(index) {
  const item = chunks[index];
  if (item.saved) return;
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      await api(`/api/takes/${takeId}/chunks/${index}`, item.blob);
      item.saved = true; return;
    } catch (error) {
      if (attempt === 2) throw error;
      await new Promise(resolve => setTimeout(resolve, 500 * (attempt + 1)));
    }
  }
}
async function flushChunks() {
  // Preserve a contiguous prefix on disk, even when a request fails.
  while (nextUpload < chunks.length) {
    await upload(nextUpload);
    nextUpload++;
    if (UI.phase === 'saving') phase('saving');
    else if (recorder?.state === 'recording' || recorder?.state === 'paused') {
      phase(recorder.state === 'paused' ? 'paused' : 'recording');
      if ($('notice').dataset.upload === 'pending') { UI.clearNotice(); delete $('notice').dataset.upload; }
    }
  }
}
function release() {
  stream?.getTracks().forEach(track => track.stop());
  $('cameraPreview').srcObject = null;
  window.CameraMonitor.stop();
  if (context) context.close().catch(() => {});
  analyser = null; context = null; UI.setLevel(0);
}
$('cameraEnabled').addEventListener('change', controls);
$('record').addEventListener('click', async () => {
  busy = true; captureWarning = null; $('player').pause(); controls();
  try {
    const mic = $('mic').value;
    const camera = $('cameraEnabled').checked;
    const cameraId = $('camera').value;
    stream = await navigator.mediaDevices.getUserMedia({video: camera ? {width: {ideal: 1280}, height: {ideal: 720}, frameRate: {ideal: 30}, ...(cameraId ? {deviceId: {exact: cameraId}} : {})} : false, audio: {echoCancellation: false, noiseSuppression: false, autoGainControl: false, channelCount: 1, ...(mic ? {deviceId: {exact: mic}} : {})}});
    await microphones();
    const mime = (camera ? ['video/webm;codecs=vp8,opus', 'video/webm;codecs=vp9,opus', 'video/mp4'] : ['audio/webm;codecs=opus', 'audio/mp4', 'audio/ogg;codecs=opus']).find(type => MediaRecorder.isTypeSupported(type));
    if (!mime) throw new Error('此浏览器不支持可保存的录音格式，请使用 Chrome 或 Safari。');
    recorder = new MediaRecorder(stream, {mimeType: mime});
    context = new AudioContext();
    await context.resume();
    analyser = context.createAnalyser(); analyser.fftSize = 256;
    context.createMediaStreamSource(stream).connect(analyser);
    levelData = new Uint8Array(analyser.fftSize);
    const settings = stream.getAudioTracks()[0].getSettings();
    const capture = Object.fromEntries(['sampleRate', 'channelCount', 'echoCancellation', 'noiseSuppression', 'autoGainControl'].filter(key => key in settings).map(key => [key, settings[key]]));
    if (camera) Object.assign(capture, Object.fromEntries(['width', 'height', 'frameRate'].map(key => [key, stream.getVideoTracks()[0].getSettings()[key]])));
    const take = await api('/api/takes', {mime, capture, script: $('scriptInner').dataset.source}); takeId = take.id;
    chunks = []; nextUpload = 0; elapsed = 0; started = performance.now(); uploadQueue = Promise.resolve();
    recorder.addEventListener('dataavailable', event => {
      if (!event.data.size) return;
      chunks.push({blob: event.data, saved: false});
      uploadQueue = uploadQueue.then(flushChunks).catch(error => {
        $('notice').dataset.upload = 'pending';
        message(`暂未保存到本地服务：${error.message}。停止时将重试，请勿关闭页面。`);
      });
    });
    recorder.addEventListener('error', event => {
      phase('error', {error: 'mic'});
      message(`录音发生错误：${event.error?.message || '设备不可用'}。请保存或恢复已有录音。`);
    });
    recorder.addEventListener('stop', saveRecording, {once: true});
    stream.getTracks().forEach(track => track.addEventListener('ended', () => {
      captureWarning = '录制设备已断开，已保存的部分需要试听确认。请检查设备并重新录制。';
      if (recorder.state === 'inactive') return;
      if (recorder.state === 'recording') elapsed += performance.now() - started;
      busy = true; recorder.stop(); controls();
      phase('saving');
      message('录制设备已断开，正在保存已录部分。请检查设备并试听后重录。');
    }, {once: true}));
    recorder.start(2000);
    if (camera) {
      $('cameraPreview').srcObject = stream;
      $('cameraMonitor').hidden = false;
      window.CameraMonitor.show();
    }
    $('fallback').hidden = true;
    phase('recording'); UI.clearNotice();
    await refresh();
  } catch (error) {
    release();
    if (error.status === 409) {
      await refresh(); savedPhase();
      UI.showNotice({kind: 'warn', title: '口播稿已更新', detail: '请确认新稿，再点击开始录音。'});
    } else { phase('error', {error: 'perm'}); UI.showNotice({kind: 'error', title: '无法开始录音', detail: error.message}); }
  }
  finally { busy = false; controls(); }
});
$('pause').addEventListener('click', () => {
  if (recorder.state === 'recording') {
    elapsed += performance.now() - started; recorder.pause();
    phase('paused');
  } else {
    started = performance.now(); recorder.resume();
    phase('recording');
  }
});
$('stop').addEventListener('click', () => {
  if (recorder.state === 'recording') elapsed += performance.now() - started;
  busy = true; recorder.stop(); controls(); scrollOn = false;
  UI.setScrolling(false); phase('saving'); UI.clearNotice();
});
async function saveRecording() {
  release();
  busy = true; controls();
  try {
    if (backupURL) URL.revokeObjectURL(backupURL);
    const blob = new Blob(chunks.map(item => item.blob), {type: recorder.mimeType});
    backupURL = URL.createObjectURL(blob);
    $('fallback').href = backupURL;
    $('fallback').download = `narration-${takeId}.${recorder.mimeType.includes('mp4') ? (recorder.mimeType.startsWith('video/') ? 'mp4' : 'm4a') : recorder.mimeType.includes('ogg') ? 'ogg' : 'webm'}`;
    $('fallback').hidden = true;
    await uploadQueue;
    await flushChunks();
    await api(`/api/takes/${takeId}/finalize`, {chunks: chunks.length});
    await refresh(); savedPhase(); UI.clearNotice();
    if (captureWarning) message(captureWarning);
  } catch (error) { phase('error', {error: 'save'}); UI.showNotice({kind: 'error', title: '自动保存失败', detail: `${error.message}。请先下载原始录音备份，保持页面开启后重试。`, fallback: true}); }
  finally { busy = false; controls(); }
}
$('retrySave').addEventListener('click', () => { phase('saving'); UI.clearNotice(); saveRecording(); });
$('finish').addEventListener('click', async () => {
  busy = true; controls();
  try { await api('/api/ready', {take: selected}); UI.closeMenu(); UI.showNotice({kind: 'ok', title: '已交接', detail: '回到 Codex 聊天，发送「录好了，继续处理」。', copy: true, dismissable: true}); }
  catch (error) { message(error.message); }
  finally { busy = false; controls(); }
});
$('top').addEventListener('click', () => { $('script').scrollTop = 0; });
$('scroll').addEventListener('click', () => {
  scrollOn = !scrollOn; UI.setScrolling(scrollOn, Number($('speed').value));
});
function frame(now) {
  if (scrollOn && recorder?.state !== 'paused') {
    const movement = scrollCarry + Math.min(now - lastFrame, 100) / 1000 * Number($('speed').value);
    const pixels = Math.floor(movement);
    scrollCarry = movement - pixels;
    $('script').scrollTop += pixels;
    if ($('script').scrollTop + $('script').clientHeight >= $('script').scrollHeight - 1) { scrollOn = false; UI.setScrolling(false); }
  }
  lastFrame = now;
  if (analyser) {
    analyser.getByteTimeDomainData(levelData);
    UI.setLevel(Math.min(1, Math.sqrt(levelData.reduce((sum, value) => sum + ((value - 128) / 128) ** 2, 0) / levelData.length) * 3));
  }
  const seconds = Math.floor((elapsed + (recorder?.state === 'recording' ? now - started : 0)) / 1000);
  $('timer').textContent = `${String(Math.floor(seconds / 60)).padStart(2, '0')}:${String(seconds % 60).padStart(2, '0')}`;
  requestAnimationFrame(frame);
}
window.addEventListener('beforeunload', event => {
  if (busy || (recorder && recorder.state !== 'inactive')) { event.preventDefault(); event.returnValue = ''; }
});
(async () => {
  try {
    const state = await refresh();
    if (!navigator.mediaDevices?.getUserMedia || !window.MediaRecorder) throw new Error('当前页面无法访问麦克风，请用 Chrome 或 Safari 打开本地链接。');
    await microphones();
    savedPhase();
    if (state.takes.some(take => !take.complete && !take.abandoned)) UI.showNotice({kind: 'warn', title: '发现未完成的录音', detail: '可在菜单恢复已保存部分，恢复后请试听确认。', recover: true});
    controls(); requestAnimationFrame(frame);
  } catch (error) { $('record').disabled = true; UI.showNotice({kind: 'error', title: '无法准备录音', detail: error.message}); }
})();

// Follow draft changes in the existing tab, leaving active capture untouched.
let checkingDraft = false;
setInterval(async () => {
  if (checkingDraft || busy || (recorder && recorder.state !== 'inactive')) return;
  checkingDraft = true;
  try {
    const state = await api('/api/state');
    if (!busy && (!recorder || recorder.state === 'inactive') && $('scriptInner').dataset.source !== state.script) {
      await refresh();
      $('script').scrollTop = 0;
      savedPhase(); controls();
    }
  } catch (_) { /* Keep the current draft visible during a service restart. */ }
  finally { checkingDraft = false; }
}, 2000);
