/* Original Claude Design layouts, rendered without its editor runtime. */
(function () {
  const value = (path, context) => {
    const key=path.trim();
    if (key==='true'||key==='false') return key==='true';
    return key.split('.').reduce((o,k)=>o?.[k],context);
  };
  // Templates are repository-authored; bindings accept property paths, never code.
  function expand(html, context) {
    const template=document.createElement('template');template.innerHTML=html;
    function visit(node,scope){
      if(node.nodeType===Node.TEXT_NODE){node.textContent=node.textContent.replace(/{{(.*?)}}/g,(_,p)=>String(value(p,scope)??''));return;}
      if(node.nodeType!==Node.ELEMENT_NODE)return;
      const tag=node.tagName.toLowerCase();
      if(tag==='sc-if'){
        if(!value(node.getAttribute('value').replace(/[{}]/g,''),scope)){node.remove();return;}
        for(const child of [...node.childNodes])visit(child,scope);
        node.replaceWith(...node.childNodes);return;
      }
      if(tag==='sc-for'){
        const rows=value(node.getAttribute('list').replace(/[{}]/g,''),scope);
        if(!Array.isArray(rows))throw Error('Missing list binding');
        const fragment=document.createDocumentFragment();
        for(const row of rows){const local={...scope,[node.getAttribute('as')]:row};for(const child of [...node.childNodes]){const copy=child.cloneNode(true);fragment.append(copy);visit(copy,local);}}
        node.replaceWith(fragment);return;
      }
      for(const attr of [...node.attributes]){
        if(attr.name.startsWith('on')||attr.name.startsWith('hint-')){node.removeAttribute(attr.name);continue;}
        node.setAttribute(attr.name,attr.value.replace(/{{(.*?)}}/g,(_,p)=>String(value(p,scope)??'')));
      }
      for(const child of [...node.childNodes])visit(child,scope);
    }
    for(const child of [...template.content.childNodes])visit(child,context);
    return template.content;
  }
  const codePatterns=new Set(['terminal-session','code-block','json-data','xml-data','vscode-editor']);
  function codeData(n,t,id){
    if(typeof n.source!=='string')throw Error('source must be text');
    const source=n.source.replace(/\r\n?/g,'\n'),lines=source.split('\n');
    const language={ 'terminal-session':'shell','code-block':n.language,'json-data':'json','xml-data':'xml','vscode-editor':n.language }[id];
    if(!['javascript','text','json','xml','shell'].includes(language))throw Error('Unsupported code language');
    if(!Number.isInteger(n.highlightLine)||n.highlightLine<1||n.highlightLine>lines.length)throw Error('highlightLine must identify an existing line');
    let focusLabel='当前高亮',focusValue=lines[n.highlightLine-1].trim()||'（空行）';
    if(language==='json'){
      const data=JSON.parse(source);
      if(id==='json-data'){
        if(!Array.isArray(n.focusPath)||!n.focusPath.length)throw Error('Provide a JSON focusPath');
        let target=data;for(const key of n.focusPath){if(target===null||typeof target!=='object'||!Object.hasOwn(target,key))throw Error('JSON focusPath does not exist');target=target[key];}
        focusLabel=n.focusPath.join('.');focusValue=JSON.stringify(target);
      }
    }
    if(language==='xml'){
      const doc=new DOMParser().parseFromString(source,'application/xml');
      if(doc.getElementsByTagNameNS('http://www.mozilla.org/newlayout/xml/parsererror.xml','parsererror').length)throw Error('Invalid XML source');
      if(id==='xml-data'){
        const node=doc.getElementsByTagName(n.focusTag)[0];if(!node)throw Error('XML focusTag does not exist');
        focusLabel='<'+n.focusTag+'>';focusValue=node.textContent;
      }
    }
    const tokens=line=>{
      if(language==='text')return [{text:line,color:t.ink}];
      const re=/("(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\/\/.*$|#[^\n]*|\b(?:export|function|const|let|return|if|else|true|false|null)\b|\b\d+(?:\.\d+)?\b|[<>/=])/g;
      const out=[];let offset=0;
      for(const match of line.matchAll(re)){
        if(match.index>offset)out.push({text:line.slice(offset,match.index),color:t.ink});
        const text=match[0],color=/^["']/.test(text)?t.ac2:/^\d/.test(text)?t.ac3:/^(\/\/|#)/.test(text)?t.mu:t.ac;
        out.push({text,color});offset=match.index+text.length;
      }
      if(offset<line.length)out.push({text:line.slice(offset),color:t.ink});return out;
    };
    let excerpt=false;
    if(n.focusPreview!==undefined){
      const original=focusValue.replace(/\s+/g,' ').trim();
      if(typeof n.focusPreview!=='string'||!/(?:…|\.\.\.)$/.test(n.focusPreview))throw Error('focusPreview must be a prefix ending with an ellipsis');
      const prefix=n.focusPreview.replace(/(?:…|\.\.\.)$/,'');
      if(!prefix||!original.startsWith(prefix))throw Error('focusPreview must preserve the beginning of the original value');
      focusValue=n.focusPreview;excerpt=true;
    }
    const code={excerpt,fileName:n.fileName,language,count:lines.length,highlight:String(n.highlightLine).padStart(2,'0'),focusLabel,focusValue,
      lines:lines.map((line,k)=>({n:k+1,tokens:tokens(line),bg:k+1===n.highlightLine?t.s2:'transparent',edge:k+1===n.highlightLine?t.ac:'transparent'}))};
    if(id==='vscode-editor'){
      if(!n.files.includes(n.fileName))throw Error('files must include the active file');
      code.files=n.files.map(name=>({name,bg:name===n.fileName?t.sf:'transparent',color:name===n.fileName?t.ac:t.mu,edge:name===n.fileName?t.ac:'transparent'}));
    }
    return code;
  }
  function dataFor(id,p,t,revealed){
    const d={},n=p.data||{};
    const finite=x=>typeof x==='number'&&Number.isFinite(x);
    const positive=x=>{if(!finite(x)||x<=0)throw Error('Scale maximum must be positive');return x;};
    const range=(x,max)=>{if(!finite(x)||x<0||x>max)throw Error('Value outside declared scale');return x;};
    if(id==='release-timeline')d.days=Array.from({length:29},(_,k)=>({l:k/28*100+'%',h:(k%7===0?22:11)+'px'}));
    if(id==='price-pair'){if(n.plans.length!==2)throw Error('Provide two plans');d.breakEven=+(n.plans[1].price/(positive(n.plans[0].price)/positive(n.plans[0].hours))).toFixed(1);d.price=n.plans.map((v,i)=>({...v,ph:(v.price/positive(v.hours)).toFixed(1),w:range(v.price/v.hours,positive(n.hourlyMax))/n.hourlyMax*100+'%',col:i?t.ac:t.ink,bar:i?t.b1:t.bN}));}
    if(id==='source-table'){d.ordersMax=positive(n.ordersMax);d.table=n.rows.map(([name,orders,percent])=>({n:name,o:orders,p:range(percent,100),ow:range(orders,n.ordersMax)/n.ordersMax*100+'%',pw:percent+'%',c:name===n.highlight?t.b1:t.bN,vc:name===n.highlight?t.ac:t.ink}));}
    if(id==='rank-bars'){
      positive(n.max);d.rank=n.items.map(([name,v],k)=>({r:k+1,n:name,v,w:range(v,n.max)/n.max*100+'%',lx:'calc('+v/n.max*100+'% + 24px)',c:k?t.bN:t.b1,rc:k?t.mu:t.ac}));
      d.rankAxis=[0,.25,.5,.75,1].map(v=>({v:v*n.max,l:v*100+'%'}));
    }
    if(id==='cost-time-map'){
      const W=960,H=500;positive(n.xMax);positive(n.yMax);
      d.pts=n.points.map(([name,x,y],i)=>{const px=range(x,n.xMax)/n.xMax*W,py=H-range(y,n.yMax)/n.yMax*H,left=px>W*.7;return {n:name,c:[t.c4,t.c2,t.c1,t.c3][i%4],meta:'¥'+x+' · '+y+' 分钟',x:px+'px',y:py+'px',lx:(left?px-34:px+34)+'px',tx:left?'translate(-100%,-50%)':'translate(0,-50%)',ta:left?'right':'left'};});
      d.xt=[0,.25,.5,.75,1].map(v=>({v:v*n.xMax,l:v*W+'px'}));d.yt=[0,.25,.5,.75,1].map(v=>({v:v*n.yMax,tp:H-v*H+'px'}));
    }
    if(id==='test-matrix'){d.scales=n.tests.map(r=>r.name+' '+r.max+' '+r.u).join(' / ');d.matrix=n.tests.map(r=>{positive(r.max);if(r.vals.length!==3||!['min','max'].includes(r.best))throw Error('Provide three results and min/max direction');const best=r.best==='min'?Math.min(...r.vals):Math.max(...r.vals);return {...r,cells:r.vals.map(v=>({v,u:r.u,w:range(v,r.max)/r.max*100+'%',best:v===best,vc:v===best?t.ac:t.ink,bc:v===best?t.b1:t.bN}))};});}
    if(id==='demo-stage'){
      const W=1060,H=300;positive(n.max-n.min);if(n.temperatures.length!==12)throw Error('Provide twelve two-hour temperature samples');n.temperatures.forEach(v=>range(v-n.min,n.max-n.min));d.current=n.temperatures.at(-1);
      const points=n.temperatures.map((v,k)=>[+(k/(n.temperatures.length-1)*W).toFixed(1),+(H-(v-n.min)/(n.max-n.min)*H).toFixed(1)]);
      d.tr={line:points.map(p=>p.join(',')).join(' '),area:'0,'+H+' '+points.map(p=>p.join(',')).join(' ')+' '+W+','+H,lx:points.at(-1)[0],ly:points.at(-1)[1],lxp:points.at(-1)[0]+'px',lyp:points.at(-1)[1]+'px'};
      d.tyt=[0,1/3,2/3,1].map(v=>({v:+(n.min+v*(n.max-n.min)).toFixed(1),tp:H-v*H+'px'}));d.txt=[0,2,4,6,8,10].map(k=>({lab:String(k*2).padStart(2,'0')+':00',l:k/11*W+'px'}));
    }
    if(id==='blind-pair'){if(n.votes.length!==2)throw Error('Provide two vote counts');const sum=positive(n.votes.reduce((s,v)=>s+range(v,Number.MAX_SAFE_INTEGER),0));const vote=v=>({v,w:v/sum*100+'%',pct:Math.round(v/sum*100)+'%'});d.blind={rev:revealed,hide:!revealed,total:sum,a:vote(n.votes[0]),b:vote(n.votes[1])};}
    if(id==='metric-scorecard')d.metrics=n.metrics.map(([name,u,a,b])=>{positive(a);range(b,Number.MAX_SAFE_INTEGER);const max=Math.max(a,b),delta=(b/a-1)*100;return {n:name,u,a,b,dl:(delta>0?'+':'')+delta.toFixed(0)+'%',aw:a/max*100+'%',bw:b/max*100+'%',bl:'calc('+b/max*100+'% + 20px)'};});
    if(id==='elapsed-breakdown'){
      const sum=positive(n.segments.reduce((s,v)=>s+v[1],0));d.total=sum;
      d.segs=n.segments.map(([name,v],k)=>({k:String(k+1).padStart(2,'0'),n:name,v:range(v,sum),c:[t.c2,t.c1,t.c3][k%3],f:v,pct:Math.round(v/sum*100)+'%'}));
      let offset=0;d.ruler=[{lab:'0',l:'0%',tx:'none'},...n.segments.map((v,k)=>{offset+=v[1];return {lab:offset+(k===n.segments.length-1?' 分钟':''),l:offset/sum*100+'%',tx:k===n.segments.length-1?'translateX(-100%)':'translateX(-50%)'};})];
    }
    if(codePatterns.has(id))d.code=codeData(n,t,id);
    return d;
  }
  function validate(id,props={},options={}){return SceneValidation.validate(id,props,options,dataFor);}
  function render(host,id,props={},options={}){
    const report=validate(id,props,options);
    if(!report.ok){const error=new Error('Scene content requires adjustment before rendering');error.name='SceneValidationError';error.report=report;throw error;}

    const record=window.SCENE_CATALOG.find(v=>v.id===id);
    const theme=options.theme||'blockframe',mode=options.mode||'light';
    const p={...record.example,...props,data:{...record.example.data,...props.data}};
    const t=SceneThemes.resolve(SceneThemes.keys[theme],mode);
    host.className='scene theme-'+theme;host.dataset.pattern=id;host.dataset.mode=mode;
    Object.assign(host.style,{backgroundColor:t.bg,color:t.ink,fontFamily:t.fb});
    let revealed,copySlots={};
    const draw=show=>{
      host.replaceChildren();
      const bg=document.createElement('div');bg.className='scene-backdrop';bg.style.backgroundImage=t.deco;host.append(bg);
      const dots=document.createElement('div');dots.className='scene-dots';Object.assign(dots.style,{backgroundImage:t.dots,backgroundSize:'28px 28px'});host.append(dots);
      const grid=document.createElement('div');grid.className='scene-grid';grid.style.backgroundImage=`repeating-linear-gradient(90deg, ${t.grid} 0 1px, transparent 1px 138.666px)`;host.append(grid);
      host.append(expand(SCENE_LAYOUTS[id],{t,d:dataFor(id,p,t,show)}));
      const root=host.querySelector('[data-scene]');
      for(const slot of root.querySelectorAll('[data-media]')){
        const asset=p.media?.[slot.dataset.media];if(!asset)continue;
        const img=document.createElement('img');img.src=asset.src;img.alt=asset.alt||'项目证据';
        Object.assign(img.style,{position:'absolute',inset:'0',width:'100%',height:'100%',objectFit:'contain'});
        Object.assign(slot.style,{position:'relative',minHeight:'0'});
        if(!slot.style.height&&slot.style.flex!=='1 1 0%')slot.style.height='520px';
        slot.replaceChildren(img);
      }

      copySlots={};
      const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
      while(walker.nextNode()){
        const text=walker.currentNode,key=text.textContent.trim();if(!key||text.parentElement.closest('[data-code-source]'))continue;
        const replacement=Object.hasOwn(p.copy||{},key)?p.copy[key]:key;
        copySlots[key]=replacement;
        text.textContent=text.textContent.replace(key,()=>replacement);
      }
      const headline=root.querySelector('[data-headline]');
      if(headline){headline.dataset.headline='';if(p.title!==undefined)headline.textContent=p.title;}
      revealed=show;
    };
    const setTime=time=>{
      if(typeof time!=='number'||!Number.isFinite(time))throw Error('Time must be finite');
      const show=id==='blind-pair'&&time>=(p.data.revealAt??5);if(revealed!==show)draw(show);
      const root=host.querySelector('[data-scene]');
      const phase=(start,duration)=>Math.max(0,Math.min(1,(time-start)/duration));
      [...root.children].forEach((el,k)=>{const q=phase(.08+k*.11,.62);el.style.opacity=q;el.style.translate=`0 ${(1-q)*28}px`;});
      root.querySelectorAll('[data-grow]').forEach((el,k)=>{el.style.scale=`${phase(.36+k*.07,.9)} 1`;el.style.transformOrigin='left center';});
      root.querySelectorAll('[data-rise]').forEach((el,k)=>{el.style.scale=`1 ${phase(.36+k*.12,.8)}`;el.style.transformOrigin='center bottom';});
      root.querySelectorAll('[data-pop]').forEach((el,k)=>{const q=phase(.5+k*.09,.5);el.style.opacity=q;el.style.scale=.4+.6*q;});
      root.querySelectorAll('[data-draw]').forEach(el=>{const length=el.getTotalLength?.()||0;if(length){el.style.strokeDasharray=length;el.style.strokeDashoffset=length*(1-phase(.4,1.4));}});
    };
    setTime(options.time??4);return {setTime,getCopySlots:()=>({...copySlots}),record,props:p,theme,mode};
  }
  window.ScenePatterns={render,validate,revision:'3'};
})();
