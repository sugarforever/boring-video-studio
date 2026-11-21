'use strict';
const $ = id => document.getElementById(id);
$('menu').addEventListener('click', () => {
  $('settings').showModal();
  $('menu').setAttribute('aria-expanded', 'true');
});
$('closeMenu').addEventListener('click', () => $('settings').close());
$('settings').addEventListener('close', () => $('menu').setAttribute('aria-expanded', 'false'));
const key = `recorder-token:${location.host}`;
const token = location.hash.slice(1) || sessionStorage.getItem(key) || '';
sessionStorage.setItem(key, token);
history.replaceState(null, '', location.pathname);
let recorder, stream, context, analyser, levelData, takeId, chunks = [], nextUpload = 0, uploadQueue = Promise.resolve();
let busy = false, selected = null, started = 0, elapsed = 0, scrollOn = false, lastFrame = 0, scrollCarry = 0;
let playerURL, backupURL, activeRegion;
const regions = WaveSurfer.Regions.create();
const waveform = WaveSurfer.create({container: '#waveform', media: $('player'),
  height: 90, waveColor: '#a1b0a0', progressColor: '#3e6154', cursorColor: '#30332f',
  plugins: [regions]});
regions.enableDragSelection({color: 'rgba(62,97,84,.18)'});
function selection(region) {
  activeRegion = region;
  regions.getRegions().filter(item => item !== region).forEach(item => item.remove());
  $('selection').textContent = `${region.start.toFixed(2)} - ${region.end.toFixed(2)} 秒`;
  $('playSelection').disabled = busy || recorder?.state === 'recording' || recorder?.state === 'paused';
}
regions.on('region-created', selection);
regions.on('region-updated', selection);
$('playSelection').addEventListener('click', () => activeRegion?.play(true));
const message = text => { $('message').textContent = text; };
async function api(path, body) {
  const headers = {'X-Recorder-Token': token};
  if (body !== undefined && !(body instanceof Blob)) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(body);
  }
  const response = await fetch(path, {method: body === undefined ? 'GET' : 'POST', headers, body});
  if (!response.ok) {
    const data = await response.json();
    throw new Error(data.error || `请求失败 (${response.status})`);
  }
  return response.json();
}
function controls() {
  const active = recorder && recorder.state !== 'inactive';
  $('record').disabled = busy || active;
  $('pause').disabled = busy || !active;
  $('stop').disabled = busy || !active;
  $('mic').disabled = busy || active;
  waveform.setOptions({interact: !busy && !active});
  $('playSelection').disabled = busy || active || !activeRegion;
  $('finish').disabled = busy || active || !selected;
  document.querySelectorAll('#takes button').forEach(button => { button.disabled = busy || active; });
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
  $('player').src = playerURL;
  try {
    await waveform.loadBlob(blob);
    $('waveform').dataset.ready = 'true';
  } catch (error) { message(`波形加载失败，仍可用播放器试听：${error.message}`); }
  selected = take.id;
  document.querySelectorAll('[data-take]').forEach(button => {
    button.setAttribute('aria-pressed', String(button.dataset.take === selected));
    button.classList.toggle('primary', button.dataset.take === selected);
  });
  controls();
}
async function refresh() {
  const state = await api('/api/state');
  $('script').textContent = state.script;
  selected = state.selected;
  $('takes').replaceChildren();
  for (const [index, take] of state.takes.entries()) {
    const row = document.createElement('div'); row.className = 'take';
    const button = document.createElement('button');
    button.textContent = take.complete ? `版本 ${index + 1} · 选择 / 试听` : `版本 ${index + 1} · 恢复 ${take.chunks} 个已保存块`;
    button.dataset.take = take.id;
    button.classList.toggle('primary', selected === take.id);
    button.setAttribute('aria-pressed', String(selected === take.id));
    button.addEventListener('click', async () => {
      busy = true; controls();
      try {
        if (!take.complete) {
          await api(`/api/takes/${take.id}/finalize`, {chunks: take.chunks});
          await refresh();
          message('已恢复保存部分。中断录音请试听确认，尾部可能缺失。');
        } else { await preview(take); message(`已选择版本 ${index + 1}`); }
      } catch (error) { message(error.message); }
      finally { busy = false; controls(); }
    });
    row.append(button); $('takes').append(row);
  }
  const current = state.takes.find(take => take.id === selected && take.complete);
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
  }
}
function release() {
  stream?.getTracks().forEach(track => track.stop());
  if (context) context.close().catch(() => {});
  analyser = null; context = null; $('level').value = 0;
}
$('record').addEventListener('click', async () => {
  busy = true; $('player').pause(); controls();
  try {
    const mic = $('mic').value;
    stream = await navigator.mediaDevices.getUserMedia({audio: {echoCancellation: false, noiseSuppression: false, autoGainControl: false, channelCount: 1, ...(mic ? {deviceId: {exact: mic}} : {})}});
    await microphones();
    const mime = ['audio/webm;codecs=opus', 'audio/mp4', 'audio/ogg;codecs=opus'].find(type => MediaRecorder.isTypeSupported(type));
    if (!mime) throw new Error('此浏览器不支持可保存的录音格式，请使用 Chrome 或 Safari。');
    recorder = new MediaRecorder(stream, {mimeType: mime});
    context = new AudioContext();
    await context.resume();
    analyser = context.createAnalyser(); analyser.fftSize = 256;
    context.createMediaStreamSource(stream).connect(analyser);
    levelData = new Uint8Array(analyser.fftSize);
    const settings = stream.getAudioTracks()[0].getSettings();
    const capture = Object.fromEntries(['sampleRate', 'channelCount', 'echoCancellation', 'noiseSuppression', 'autoGainControl'].filter(key => key in settings).map(key => [key, settings[key]]));
    const take = await api('/api/takes', {mime, capture}); takeId = take.id;
    chunks = []; nextUpload = 0; elapsed = 0; started = performance.now(); uploadQueue = Promise.resolve();
    recorder.addEventListener('dataavailable', event => {
      if (!event.data.size) return;
      chunks.push({blob: event.data, saved: false});
      uploadQueue = uploadQueue.then(flushChunks).catch(error => {
        message(`暂未保存到本地服务：${error.message}。停止时将重试，请勿关闭页面。`);
      });
    });
    recorder.addEventListener('error', event => {
      message(`录音发生错误：${event.error?.message || '设备不可用'}。请保存或恢复已有录音。`);
    });
    recorder.addEventListener('stop', saveRecording, {once: true});
    recorder.start(2000);
    $('fallback').style.display = 'none';
    $('pause').textContent = '暂停'; message('录音中 · 每隔约 2 秒保存');
    await refresh();
  } catch (error) { release(); message(`无法开始录音：${error.message}`); }
  finally { busy = false; controls(); }
});
$('pause').addEventListener('click', () => {
  if (recorder.state === 'recording') {
    elapsed += performance.now() - started; recorder.pause();
    $('pause').textContent = '继续'; message('已暂停');
  } else {
    started = performance.now(); recorder.resume();
    $('pause').textContent = '暂停'; message('录音中');
  }
});
$('stop').addEventListener('click', () => {
  if (recorder.state === 'recording') elapsed += performance.now() - started;
  busy = true; recorder.stop(); controls(); scrollOn = false;
  $('scroll').textContent = '开始滚动'; message('正在保存，请稍候…');
});
async function saveRecording() {
  release();
  busy = true; controls();
  try {
    if (backupURL) URL.revokeObjectURL(backupURL);
    const blob = new Blob(chunks.map(item => item.blob), {type: recorder.mimeType});
    backupURL = URL.createObjectURL(blob);
    $('fallback').href = backupURL;
    $('fallback').download = `narration-${takeId}.${recorder.mimeType.includes('mp4') ? 'm4a' : recorder.mimeType.includes('ogg') ? 'ogg' : 'webm'}`;
    $('fallback').style.display = 'block';
    await uploadQueue;
    await flushChunks();
    await api(`/api/takes/${takeId}/finalize`, {chunks: chunks.length});
    await refresh(); message('录音已保存。试听后可以交给 Codex，或另录一版。');
  } catch (error) { message(`自动保存失败：${error.message}。请立即下载原始录音备份，或保持页面并重启服务后恢复已保存块。`); }
  finally { busy = false; controls(); }
}
$('finish').addEventListener('click', async () => {
  busy = true; controls();
  try { await api('/api/ready', {take: selected}); $('settings').close(); message('已交接。在 Codex 聊天中说“录好了，继续处理”。'); }
  catch (error) { message(error.message); }
  finally { busy = false; controls(); }
});
$('font').addEventListener('input', () => { $('script').style.fontSize = `${$('font').value}px`; });
$('top').addEventListener('click', () => { $('script').scrollTop = 0; });
$('scroll').addEventListener('click', () => {
  scrollOn = !scrollOn; $('scroll').textContent = scrollOn ? '暂停滚动' : '开始滚动';
});
function frame(now) {
  if (scrollOn && recorder?.state !== 'paused') {
    const movement = scrollCarry + Math.min(now - lastFrame, 100) / 1000 * Number($('speed').value);
    const pixels = Math.floor(movement);
    scrollCarry = movement - pixels;
    $('script').scrollTop += pixels;
  }
  lastFrame = now;
  if (analyser) {
    analyser.getByteTimeDomainData(levelData);
    $('level').value = Math.min(1, Math.sqrt(levelData.reduce((sum, value) => sum + ((value - 128) / 128) ** 2, 0) / levelData.length) * 3);
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
    message(state.status === 'ready' ? '当前版本已交给 Codex，也可以再录一版。' : '准备好了。点击开始录音。');
    controls(); requestAnimationFrame(frame);
  } catch (error) { $('record').disabled = true; message(error.message); }
})();
