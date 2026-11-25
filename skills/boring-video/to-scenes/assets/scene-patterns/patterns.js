/* Scene patterns v2. Review scaffolds; factual inputs must be supplied by a project. */
(function () {
  const E = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const clamp = n => Math.max(0, Math.min(1, n));
  const media = m => m?.src ? `<img class="evidence" src="${E(m.src)}" alt="${E(m.alt || '项目证据')}"/>` : '<div class="media-slot">接入真实截图 / 录屏 / 人物素材</div>';
  const item = (v, i) => `<div class="row reveal" data-step="${i}"><span class="ordinal">${String(i+1).padStart(2,'0')}</span><b>${E(v.label)}</b><span>${E(v.detail)}</span></div>`;
  function content(id,p){
    const items=p.items;
    switch(id){
      case 'release-timeline': return `<div class="timeline"><div class="axis"></div>${p.events.map((v,i)=>`<div class="event reveal" data-step="${i}" style="left:${6+clamp(v.position)*72}%"><div class="card"><b>${E(v.label)}</b><small>${E(v.date)}</small></div><i></i></div>`).join('')}</div><p class="takeaway">${E(p.rangeLabel)}</p>`;
      case 'duel-cards': return `<div class="duel"><div class="card reveal" data-step="0"><small>对象 A</small><h2>${E(p.left.label)}</h2><p>${E(p.left.detail)}</p></div><strong class="relation reveal" data-step="2">${E(p.relation)}</strong><div class="card reveal" data-step="1"><small>对象 B</small><h2>${E(p.right.label)}</h2><p>${E(p.right.detail)}</p></div></div>`;
      case 'chapter-agenda': return `<div class="agenda">${items.slice(0,4).map(item).join('')}</div>`;
      case 'model-map': return `<div class="map">${items.slice(0,4).map((v,i)=>`<div class="mapping reveal" data-step="${i}"><b class="tile">${E(v.label)}</b><span class="accent">≈</span><h3>${E(v.detail)}</h3></div>`).join('')}</div>`;
      case 'quote-evidence': return `<blockquote class="card reveal" data-step="0">“${E(p.quote)}”<small>${E(p.attribution)}</small></blockquote>`;
      case 'price-pair': return `<div class="pair">${items.slice(0,2).map((v,i)=>`<div class="card reveal" data-step="${i}"><small>${E(v.label)}</small><div class="figure">${E(v.value)}</div><p>${E(v.detail)}</p></div>`).join('')}</div><p>${E(p.unit)}</p>`;
      case 'source-table': return `<div class="source-surface reveal" data-step="0">${media(p.media)}</div><p class="takeaway">${E(p.caption || '指出证据行、列与脚注')}</p>`;
      case 'rank-bars': { if (!(p.max>0) || items.some(v=>v.value<0||v.value>p.max)) throw Error('rank-bars requires 0 ≤ value ≤ max'); return `<div class="bars">${items.slice(0,6).map((v,i)=>`<div class="bar-row reveal" data-step="${i}"><span>${E(v.label)}</span><div class="bar-track"><div class="bar" style="width:${v.value/p.max*100}%"></div></div><b>${E(v.value)}</b></div>`).join('')}</div><p>0 — ${E(p.max)} · ${E(p.unit)}</p>`; }
      case 'cost-time-map': {if(!(p.xMax>0&&p.yMax>0)||p.points.some(v=>v.x<0||v.y<0||v.x>p.xMax||v.y>p.yMax)) throw Error('Point outside linear axes');return `<div class="plot"><span class="y-label">${E(p.yLabel)} · 0–${E(p.yMax)}</span><span class="x-label">${E(p.xLabel)} · 0–${E(p.xMax)}</span>${p.points.map((v,i)=>`<div class="point reveal" data-step="${i}" style="left:${v.x/p.xMax*85}%;bottom:${v.y/p.yMax*80}%"><i></i><b>${E(v.label)}</b><small>${E(v.x)} / ${E(v.y)}</small></div>`).join('')}</div>`;}
      case 'test-matrix': return `<p class="protocol">${E(p.protocol)}</p><div class="matrix">${items.slice(0,6).map((v,i)=>`<div class="card reveal" data-step="${i}"><small>测试 ${String(i+1).padStart(2,'0')}</small><h3>${E(v.label)}</h3><p>${E(v.detail)}</p></div>`).join('')}</div>`;
      case 'task-brief': {const idx=p.prompt.indexOf(p.highlight);if(p.highlight&&idx<0)throw Error('Highlight must occur in prompt');return `<p class="protocol">${E(p.protocol)}</p><div class="prompt card reveal" data-step="0">${idx<0?E(p.prompt):E(p.prompt.slice(0,idx))+'<mark>'+E(p.highlight)+'</mark>'+E(p.prompt.slice(idx+p.highlight.length))}</div>`;}
      case 'demo-stage': return `<div class="demo reveal" data-step="0">${media(p.media)}</div><p>${E(p.caption || '操作 → 可见变化 → 结果停留')}</p>`;
      case 'blind-pair': return `<div class="pair">${items.slice(0,2).map((v,i)=>`<div class="reveal" data-step="${i}"><div class="card blind-media">${media(v.media)}</div><h2>${i?'B':'A'} <span class="identity">${E(v.label)}</span></h2><p class="identity">${E(v.detail)}</p></div>`).join('')}</div><p class="blind-note">先观察，后揭晓</p>`;
      case 'metric-scorecard': return `<div class="score"><div class="score-row score-head"><span>指标 / 单位</span>${p.columns.map(v=>`<h3>${E(v)}</h3>`).join('')}</div>${p.metrics.slice(0,4).map((v,i)=>`<div class="score-row reveal" data-step="${i}"><span>${E(v.label)}<small>${E(v.unit)}</small></span><b>${E(v.a)}</b><b>${E(v.b)}</b></div>`).join('')}</div>`;
      case 'elapsed-breakdown': {const total=p.segments.reduce((s,v)=>s+v.value,0);if(!(total>0)||p.segments.some(v=>v.value<0))throw Error('Segments require nonnegative durations and positive total');return `<div class="figure">${E(total)} <small>${E(p.unit)}</small></div><div class="segments">${p.segments.map((v,i)=>`<div class="segment reveal" data-step="${i}" style="flex:${v.value}"></div>`).join('')}</div><div class="segment-labels">${p.segments.map((v,i)=>`<p><b>${i+1}. ${E(v.label)}</b><br>${E(v.value)} ${E(p.unit)}</p>`).join('')}</div>`;}
      case 'terminal-evidence': return `<p class="protocol">${E(p.truthMode)} · ${E(p.source)}</p><pre class="card reveal" data-step="0"><code>$ ${E(p.command)}\n\n<span class="terminal-output">${E(p.output)}</span></code></pre>`;
      case 'results-ledger': return `<div class="ledger">${items.slice(0,6).map(item).join('')}</div><p class="takeaway reveal" data-step="4">${E(p.summary || '逐项核对，再得出总计')}</p>`;
      case 'presenter-focus': return `<div class="presenter reveal" data-step="0">${media(p.media)}</div><p>${E(p.caption || '一句判断，给观众消化的时间')}</p>`;
      case 'decision-statement': return `<div class="statement reveal" data-step="0"><h2>${E(p.statement)}</h2><p>${E(p.qualifier)}</p></div>`;
      case 'action-close': return `<div class="statement reveal" data-step="0"><h2>${E(p.statement)}</h2><p class="destination">${E(p.destination)}</p><small>${E(p.qualifier)}</small></div>`;
      default: throw Error('Unknown scene pattern: '+id);
    }
  }
  function render(host,id,props={},options={}){
    const record=window.SCENE_CATALOG.find(v=>v.id===id);if(!record)throw Error('Unknown pattern');
    const p={title:record.title,...record.example,...props};
    host.className='scene theme-'+(options.theme || 'blockframe');host.dataset.pattern=id;
    host.innerHTML=`<div class="scene-inner"><header><span class="kicker">${E(record.category)} / ${E(id)}</span><h1>${E(p.title)}</h1></header><main>${content(id,p)}</main><footer><span>${E(p.source)}</span><span>独立案例 · v${E(record.revision)} · ${E(window.SCENE_LIBRARY.preview.ratio)}</span></footer></div>`;
    const setTime=time=>{const t=Number(time);if(!Number.isFinite(t))throw Error('Time must be finite');host.querySelectorAll('.reveal').forEach(el=>{const start=.5+Number(el.dataset.step)*.55;const phase=clamp((t-start)/.4);el.style.opacity=phase;el.style.transform=`translateY(${(1-phase)*20}px)`;});host.querySelectorAll('.identity').forEach(el=>{el.style.opacity=t>=p.revealAt?'1':'0';});const note=host.querySelector('.blind-note');if(note)note.textContent=t>=p.revealAt?'身份揭晓 · 对照项目证据':'先观察，后揭晓';};
    setTime(options.time??4);return {setTime,record,props:p};
  }
  window.ScenePatterns={render,revision:'2'};
})();
