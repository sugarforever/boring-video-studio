'use strict';
// 界面状态层：只负责显示，不触碰 MediaRecorder / 分块上传 / 交接 API。
// recorder.js 在原有流程的关键点调用 RecorderUI.*，录音与保存逻辑保持不变。
(function () {
  const $ = id => document.getElementById(id);
  const PHRASE = '录好了，继续处理';
  const LEVEL_BARS = Array.from(document.querySelectorAll('#level .lv'));
  const ERROR_META = {save: '部分分块未写入本地', mic: '录音已中断', perm: '麦克风未授权'};
  let phase = 'idle';
  let scrollState = {on: false, speed: 24};

  function show(el, on) { el.hidden = !on; }
  function say(text) { $('message').textContent = text; }

  function button(el, {label, primary, icon, disabled = false}) {
    el.className = 'btn' + (primary ? ' btn-primary' : '');
    el.disabled = disabled;
    el.replaceChildren();
    if (icon === 'rec') el.append(Object.assign(document.createElement('span'), {className: 'recdot'}));
    if (icon === 'stop') el.append(Object.assign(document.createElement('span'), {className: 'stopsq'}));
    el.append(document.createTextNode(label));
  }

  // phase: idle | recording | paused | saving | saved | error
  // info: {chunks, pending, total, take: {n, duration}, mic, error: 'save'|'mic'|'perm'}
  function setPhase(next, info = {}) {
    phase = next;
    const err = next === 'error' ? info.error : null;
    document.body.dataset.state = next;
    document.body.dataset.error = err || '';
    const dot = $('dot'), label = $('statusLabel'), meta = $('statusMeta');
    dot.className = 'dot' + ({recording: ' is-rec', paused: ' is-paused', saving: ' is-saving', saved: ' is-saved', error: ' is-error'}[next] || '');
    label.className = 'status-label' + (next === 'recording' || next === 'error' ? ' is-rec' : '');
    $('bar').classList.toggle('is-rec', next === 'recording');
    $('timer').classList.toggle('is-dim', next === 'idle' || err === 'perm');

    const text = {
      idle: ['未录制', info.mic || $('mic').selectedOptions[0]?.textContent || ''],
      recording: ['录音中', info.pending ? `${info.pending} 块待保存 · 正在重试` : `已自动保存 ${info.chunks || 0} 块 · 每约 2 秒`],
      paused: ['已暂停', `已保存 ${info.chunks || 0} 块 · 可继续或停止`],
      saving: ['正在保存', `${info.chunks || 0} / ${info.total || 0} 块 · 请勿关闭页面`],
      saved: [`已保存为版本 ${info.take?.n ?? ''}`, `在菜单中试听与交接`],
      error: [err === 'perm' ? '无法开始' : '需要处理', ERROR_META[err] || '']
    }[next];
    label.textContent = text[0];
    meta.textContent = text[1];

    const record = $('record'), pause = $('pause'), stop = $('stop');
    show(record, next === 'idle' || next === 'saved' || err === 'perm');
    record.querySelector('.lbl').textContent = next === 'saved' ? '录新版本' : err === 'perm' ? '重试' : '开始录音';
    show(pause, next === 'recording' || next === 'paused');
    if (next === 'recording') button(pause, {label: '暂停'});
    if (next === 'paused') button(pause, {label: '继续录音', primary: true, icon: 'rec'});
    show(stop, next === 'recording' || next === 'paused' || next === 'saving' || err === 'mic');
    if (!stop.hidden) button(stop, {
      label: next === 'saving' ? '正在保存…' : err === 'mic' ? '保存已录部分' : '停止并保存',
      primary: next !== 'paused', icon: next === 'saving' ? null : 'stop', disabled: next === 'saving'
    });
    show($('review'), next === 'saved');
    show($('retrySave'), err === 'save');
    show($('progress'), next === 'saving');
    if (next === 'saving') $('progress').style.width = `${Math.round(100 * (info.chunks || 0) / Math.max(1, info.total || 1))}%`;

    const locked = next === 'recording' || next === 'paused' || next === 'saving' || err === 'mic';
    show($('lock'), locked);
    setScrolling(scrollState.on);
    setBadge();
    if (next !== 'recording' && next !== 'paused') setLevel(0);
    return locked;
  }

  function fmt(ms) {
    const s = Math.max(0, Math.floor(ms / 1000));
    return `${String(Math.floor(s / 60)).padStart(2, '0')}:${String(s % 60).padStart(2, '0')}`;
  }

  // kind: error | warn | ok；error 用 role=alert，其余 role=status
  function showNotice({kind, title, detail, fallback = false, recover = false, copy = false, dismissable = false}) {
    const n = $('notice');
    n.className = `notice is-${kind}`;
    n.setAttribute('role', kind === 'error' ? 'alert' : 'status');
    $('noticeTitle').textContent = title;
    $('noticeDetail').textContent = detail || '';
    show($('fallback'), fallback && !!$('fallback').getAttribute('href'));
    show($('openRecover'), recover);
    show($('copyPhrase'), copy);
    $('copyPhrase').textContent = '复制这句话';
    show($('dismissNotice'), dismissable);
    n.hidden = false;
    say(title);
  }
  function clearNotice() { $('notice').hidden = true; }

  function renderScript(text) {
    const paras = String(text).split(/\n\s*\n|\n/).map(s => s.trim()).filter(Boolean);
    $('scriptInner').replaceChildren(...paras.map(t => {
      const p = document.createElement('p');
      p.className = 'para';
      p.textContent = t; // 稿件一律 textContent，避免注入
      return p;
    }));
  }

  function setLevel(value) {
    const on = Math.round(Math.max(0, Math.min(1, value)) * LEVEL_BARS.length);
    LEVEL_BARS.forEach((bar, i) => bar.classList.toggle('on', i < on));
    $('level').setAttribute('aria-label', phase === 'recording' || phase === 'paused'
      ? `输入电平：${value > .82 ? '偏高' : value > .2 ? '正常' : value > .01 ? '很低' : '无输入'}`
      : '输入电平：未在录音');
  }

  function setScrolling(on, speed = scrollState.speed) {
    scrollState = {on, speed};
    const btn = $('scroll');
    btn.setAttribute('aria-pressed', String(on));
    btn.querySelector('.lbl-long').textContent = on ? '暂停滚动' : '自动滚动';
    btn.querySelector('.lbl-short').textContent = on ? '暂停' : '滚动';
    $('scrollMeta').textContent = on && phase === 'paused' ? '随录音暂停' : `${speed} px/秒`;
    btn.setAttribute('aria-label', `${on ? '暂停滚动' : '自动滚动'}，速度 ${speed} 像素每秒`);
  }

  function setBadge() {
    const partial = !!document.querySelector('#takes .is-partial');
    show($('menuBadge'), partial || phase === 'error');
    $('menu').setAttribute('aria-label', '打开设置与录音版本' + (partial ? '（有未完成录音可恢复）' : ''));
  }

  // takes: [{id, n, complete, duration, chunks, at, recovered}]
  // handlers: {onPick(take), onRecover(take)}；返回 Map(id -> element)
  function renderTakes(takes, {selected, handed, locked, onPick, onRecover, onAbandon}) {
    const box = $('takes'), map = new Map();
    $('takeCount').textContent = takes.length ? `${takes.length} 个` : '';
    if (!takes.length) {
      box.innerHTML = '<div class="empty">还没有录音版本。关闭菜单，点击「开始录音」。</div>';
    } else {
      box.replaceChildren(...takes.map(take => {
        const tpl = $(take.complete ? 'takeTpl' : 'partialTpl').content.firstElementChild.cloneNode(true);
        tpl.querySelector('.take-t').textContent = `版本 ${take.n}${take.complete ? '' : take.abandoned ? ' · 已放弃' : ' · 未完成'}`;
        tpl.querySelector('.take-m').textContent = take.complete
          ? `${Number.isFinite(take.duration) ? fmt(take.duration) : '时长待读取'}${take.at ? ' · ' + take.at : ''}`
          : `已保存 ${take.chunks} 块 ≈ ${fmt(take.chunks * 2000)}`;
        if (take.complete) {
          const sel = take.id === selected;
          tpl.classList.toggle('is-sel', sel);
          tpl.setAttribute('aria-pressed', String(sel));
          tpl.dataset.take = take.id;
          tpl.querySelector('.radio').classList.toggle('is-on', sel);
          const tag = tpl.querySelector('.tag');
          tag.textContent = take.recovered ? '已恢复 · 尾部可能缺失' : take.id === handed ? '已交接' : sel ? '已选中' : '完整';
          tag.className = 'tag' + (take.recovered ? ' is-warn' : (sel || take.id === handed) ? ' is-ok' : '');
          tpl.disabled = locked;
          tpl.addEventListener('click', () => onPick(take));
        } else {
          const b = tpl.querySelector('button');
          b.dataset.unavailable = String(!!take.abandoned || !take.chunks);
          b.disabled = locked || b.dataset.unavailable === 'true';
          b.addEventListener('click', () => { b.textContent = '正在恢复…'; onRecover(take); });
          const abandon = tpl.querySelector('.abandon');
          abandon.dataset.unavailable = String(!!take.abandoned);
          abandon.disabled = locked || take.abandoned;
          abandon.addEventListener('click', () => onAbandon(take));
        }
        map.set(take.id, tpl);
        return tpl;
      }));
    }
    setBadge();
    return map;
  }

  function setPreview(take) {
    show($('previewSec'), !!take);
    $('previewTitle').textContent = take ? `版本 ${take.n}${Number.isFinite(take.duration) ? ' · ' + fmt(take.duration) : ''}` : '';
  }

  function setFinish({enabled, note, sending = false}) {
    $('finish').disabled = !enabled;
    $('finish').textContent = sending ? '正在交接…' : '使用选中版本，交给 Codex';
    if (note) $('finishNote').textContent = note;
  }

  // 菜单：原生 <dialog>.showModal() 提供 Esc 关闭与焦点隔离；关闭后焦点回到 burger。
  function openMenu(section) {
    const d = $('settings');
    if (!d.open) d.showModal();
    $('menu').setAttribute('aria-expanded', 'true');
    $('closeMenu').focus();
    if (section === 'takes') $('takesSec').scrollIntoView({block: 'start'});
  }
  function closeMenu() { if ($('settings').open) $('settings').close(); }
  $('menu').addEventListener('click', () => openMenu());
  $('closeMenu').addEventListener('click', closeMenu);
  $('review').addEventListener('click', () => openMenu('takes'));
  $('openRecover').addEventListener('click', () => openMenu('takes'));
  $('settings').addEventListener('close', () => { $('menu').setAttribute('aria-expanded', 'false'); $('menu').focus(); });
  $('settings').addEventListener('click', e => { const r = $('settings').getBoundingClientRect(); if (e.target === $('settings') && (e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom)) closeMenu(); }); // 点遮罩关闭
  $('dismissNotice').addEventListener('click', clearNotice);
  $('copyPhrase').addEventListener('click', async () => {
    try { await navigator.clipboard.writeText(PHRASE); $('copyPhrase').textContent = '已复制'; } catch { $('copyPhrase').textContent = `请手动输入：${PHRASE}`; }
  });
  $('font').addEventListener('input', () => {
    $('scriptInner').style.fontSize = `${$('font').value}px`;
    $('fontOut').textContent = `${$('font').value} px`;
  });
  $('speed').addEventListener('input', () => {
    $('speedOut').textContent = `${$('speed').value} px/秒`;
    setScrolling(scrollState.on, Number($('speed').value));
  });
  if (matchMedia('(max-width: 640px)').matches) { $('font').value = 24; $('font').dispatchEvent(new Event('input')); }

  window.RecorderUI = {setPhase, showNotice, clearNotice, renderScript, setLevel, setScrolling, renderTakes, setPreview, setFinish, openMenu, closeMenu, say, fmt, PHRASE, get phase() { return phase; }};
})();
