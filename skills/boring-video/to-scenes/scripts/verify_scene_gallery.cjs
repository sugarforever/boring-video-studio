#!/usr/bin/env node
const assert=require('node:assert/strict');
const path=require('node:path');
const {pathToFileURL}=require('node:url');
const {chromium}=require(process.argv[2]||'playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage({viewport:{width:1920,height:1080}}),errors=[];
  page.on('pageerror',e=>errors.push(e.message));
  await page.goto(pathToFileURL(path.resolve(__dirname,'../assets/scene-patterns/gallery.html')).href);
  await page.addStyleTag({content:'nav,aside,#info,details,#work>p{display:none}#layout{display:block}#work{padding:0}#viewport{width:1920px;height:1080px}#stage{transform:none!important}'});
  const ids=await page.evaluate(()=>SCENE_CATALOG.map(r=>r.id));assert.equal(ids.length,20);
  let count=0;
  for(const theme of ['blockframe','swiss-minimalism','raycast-dark','claude-warm'])for(const mode of ['light','dark'])for(const id of ids){
   const result=await page.evaluate(async({id,theme,mode})=>{
    const host=document.querySelector('#stage'),scene=ScenePatterns.render(host,id,{}, {theme,mode,time:4});await document.fonts.ready;
    const state=time=>{scene.setTime(time);return host.innerHTML},direct=state(4);state(0);for(let time=0;time<=4;time+=.1)scene.setTime(time);const sequential=state(4);state(7.9);const backward=state(4);
    const bounds=host.getBoundingClientRect(),overflow=[],walker=document.createTreeWalker(host,NodeFilter.SHOW_TEXT);
    while(walker.nextNode()){const node=walker.currentNode;if(!node.textContent.trim())continue;const range=document.createRange();range.selectNodeContents(node);for(const r of range.getClientRects())if(r.left<bounds.left-1||r.right>bounds.right+1||r.top<bounds.top-1||r.bottom>bounds.top+920)overflow.push(node.textContent.slice(0,40));}
    return {seek:direct===sequential&&direct===backward,overflow,headline:!!host.querySelector('[data-headline]'),unbound:host.textContent.includes('{{')};
   },{id,theme,mode});
   assert.deepEqual(result,{seek:true,overflow:[],headline:true,unbound:false},`${id}/${theme}/${mode}`);count++;
  }
  const dataChecks=await page.evaluate(()=>{
   const host=document.querySelector('#stage'),render=(id,data,time=7)=>{ScenePatterns.render(host,id,{data},{time});return host.textContent};
   const votes=render('blind-pair',{votes:[3,1]});const hidden=render('blind-pair',{votes:[3,1]},2);
   const elapsed=render('elapsed-breakdown',{segments:[['准备',10],['制作',20],['完成',30]]});
   const metrics=render('metric-scorecard',{metrics:[['耗时','秒',20,30]]});
   const demo=render('demo-stage',{temperatures:Array(12).fill(22)});
   let rejects=0;for(const [id,data]of [['rank-bars',{max:0}],['blind-pair',{votes:[-1,2]}],['demo-stage',{temperatures:[22]}]])try{render(id,data)}catch{rejects++}
   return {votes:votes.includes('75%')&&votes.includes('3 票')&&votes.includes('4'),hidden:!hidden.includes('社区设计组'),elapsed:elapsed.includes('60'),metrics:metrics.includes('+50%'),demo:demo.includes('现在 22 ℃'),rejects};
  });assert.deepEqual(dataChecks,{votes:true,hidden:true,elapsed:true,metrics:true,demo:true,rejects:3});
  const mediaCheck=await page.evaluate(async()=>{
   const host=document.querySelector('#stage'),asset={src:'data:image/svg+xml,'+encodeURIComponent('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="450"><rect width="800" height="450" fill="orange"/></svg>'),alt:'测试图片'};
   for(const id of ['source-table','demo-stage','presenter-focus','blind-pair']){
    const media=id==='blind-pair'?{a:asset,b:asset}:{primary:asset};const scene=ScenePatterns.render(host,id,{media},{time:7});
    await Promise.all([...host.querySelectorAll('img')].map(img=>img.decode()));
    if(host.querySelectorAll('img').length!==Object.keys(media).length)return false;
    scene.setTime(2);await Promise.all([...host.querySelectorAll('img')].map(img=>img.decode()));
   }return true;
  });assert.ok(mediaCheck,'Image replacement slots');
  await page.reload();await page.locator('#search').fill('盲测');await page.locator('#list button').click();await page.locator('#theme').selectOption('raycast-dark');await page.locator('#mode').selectOption('dark');
  assert.equal(await page.locator('#stage').getAttribute('data-mode'),'dark');
  await page.locator('summary').click();await page.locator('#props').fill(JSON.stringify({title:'替换后的项目标题',copy:{'作者已隐藏':'尚未揭晓'}}));await page.locator('#apply').click();
  assert.equal(await page.locator('[data-headline]').textContent(),'替换后的项目标题');assert.ok((await page.locator('#stage').textContent()).includes('尚未揭晓'));assert.equal(await page.locator('#error').textContent(),'');
  assert.deepEqual(errors,[]);console.log(`${count} variants passed: text bounds, resolved bindings, deterministic seeking; data geometry/labels, reveal, mode and editing checks passed`);
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
