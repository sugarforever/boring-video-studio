#!/usr/bin/env node
const assert=require('node:assert/strict'),path=require('node:path'),fs=require('node:fs'),os=require('node:os');
const {spawnSync}=require('node:child_process'),{pathToFileURL}=require('node:url');
const modulePath=process.argv[2]||'playwright',{chromium}=require(modulePath);
(async()=>{const browser=await chromium.launch();try{
 const page=await browser.newPage({viewport:{width:1920,height:1080}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const url=pathToFileURL(path.resolve(__dirname,'../assets/scene-patterns/gallery.html')).href;
 await page.goto(url+'?preflight=1');await page.addStyleTag({content:'nav,aside,#info,details,#work>p{display:none}#layout{display:block}#work{padding:0}#viewport{width:1920px;height:1080px}#stage{transform:none!important}'});
 const result=await page.evaluate(async()=>{
  const host=document.querySelector('#stage'),empty=host.childElementCount===0;
  const props={data:{source:JSON.stringify({payload:Array(5).fill('A'.repeat(36))},null,2),focusPath:['payload'],highlightLine:3}};
  const original=JSON.stringify(props),report=ScenePatterns.validate('json-data',props),noPreview=host.childElementCount===0;
  ScenePatterns.render(host,'json-data');const before=host.outerHTML;
  let blocked=false;try{ScenePatterns.render(host,'json-data',props)}catch(e){blocked=e.name==='SceneValidationError'&&e.report.issues.length>0}
  const unchanged=before===host.outerHTML;
  const proposal=report.issues.find(v=>v.path==='data.focusValue').suggestions.find(v=>v.action==='excerpt');
  const adjusted={data:{...props.data,focusPreview:proposal.changes[0].value}},approved=ScenePatterns.validate('json-data',adjusted);
  const variants=[];
  for(const theme of SceneThemes.ids)for(const mode of ['light','dark']){
   ScenePatterns.render(host,'json-data',adjusted,{theme,mode,time:4});await document.fonts.ready;
   const bounds=host.getBoundingClientRect(),walker=document.createTreeWalker(host,NodeFilter.SHOW_TEXT);let fits=true;
   while(walker.nextNode()){const node=walker.currentNode;if(!node.textContent.trim())continue;const range=document.createRange();range.selectNodeContents(node);const r=range.getBoundingClientRect();if(r.bottom>bounds.top+920||r.right>bounds.right)fits=false;}
   variants.push(fits&&host.textContent.includes('节选'));
  }
  const sourcePreserved=[...host.querySelectorAll('.code-text')].map(el=>el.textContent).join('\n')===props.data.source;
  const cases=[
   ['code-block',{data:{source:'中'.repeat(29),highlightLine:1}},'data.source.line[1]'],
   ['terminal-session',{data:{source:'x'.repeat(65),highlightLine:1}},'data.source.line[1]'],
   ['source-table',{data:{rows:[['A',1,2],['B',1,2],['C',1,2],['D',1,2]]}},'data.rows'],
   ['rank-bars',{data:{items:[['名称'.repeat(8),20]]}},'data.items.0.0'],
   ['vscode-editor',{data:{fileName:'a-very-long-active-file.js',files:['a-very-long-active-file.js']}},'data.files.0'],
   ['xml-data',{data:{source:'<r>\n'+Array(5).fill('<v>'+'A'.repeat(36)+'</v>').join('\n')+'\n</r>',focusTag:'r',highlightLine:2}},'data.focusValue'],
   ['json-data',{data:{source:'"moisture": 41,',highlightLine:1}},'data.source'],
   ['json-data',{data:{...props.data,focusPreview:'invented…'}},'data.focusPreview'],
   ['code-block',{title:'长'.repeat(50)},'title'],
   ['code-block',{copy:{'当前高亮':'长'.repeat(20)}},'copy.当前高亮'],
   ['elapsed-breakdown',{data:{segments:[['A',1],['B',999]]}},'data.segments.0'],
   ['cost-time-map',{data:{points:[['A',10,10],['B',11,11]]}},'data.points.1']
  ];
  const checks=cases.map(([id,p,path])=>{const r=ScenePatterns.validate(id,p);return !r.ok&&r.requiresConfirmation&&r.issues.some(v=>v.path===path&&v.suggestions.every(s=>s.requiresConfirmation));});
  const revision=ScenePatterns.validate('json-data',{}, {revision:'2'}).ok===false;
  return {empty,noPreview,blocked,unchanged,inputUnchanged:original===JSON.stringify(props),requiresConfirmation:report.requiresConfirmation,approved:approved.ok,sourcePreserved,variants,checks,revision,props,adjusted};
 });
 for(const name of ['empty','noPreview','blocked','unchanged','inputUnchanged','requiresConfirmation','approved','sourcePreserved','revision'])assert.equal(result[name],true,name);
 assert.ok(result.variants.every(Boolean),'Approved excerpt fits all style/mode variants');assert.ok(result.checks.every(Boolean),JSON.stringify(result.checks));
 await page.goto(url+'?pattern=json-data');await page.locator('summary').click();
 const before=await page.locator('#stage').evaluate(el=>el.outerHTML);
 await page.locator('#props').fill(JSON.stringify(result.props));await page.locator('#validate').click();
 assert.ok((await page.locator('#error').textContent()).includes('data.focusValue'));
 await page.locator('#apply').click();assert.equal(await page.locator('#stage').evaluate(el=>el.outerHTML),before);assert.ok(await page.locator('#copy').isDisabled());
 await page.locator('#props').fill(JSON.stringify(result.adjusted));await page.locator('#validate').click();
 assert.equal(await page.locator('#stage').evaluate(el=>el.outerHTML),before);assert.ok(await page.locator('#copy').isDisabled());
 await page.locator('#apply').click();assert.equal(await page.locator('#error').textContent(),'');assert.ok(await page.locator('#copy').isEnabled());assert.ok((await page.locator('#stage').textContent()).includes('节选'));
 assert.deepEqual(errors,[]);
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'scene-preflight-'));
 try{for(const [props,status]of [[result.props,2],[result.adjusted,0],[null,2],[false,2]]){
  const input=path.join(temp,'selection.json');fs.writeFileSync(input,JSON.stringify({id:'json-data',revision:'3',props}));
  const run=spawnSync(process.execPath,[path.join(__dirname,'validate_scene_selection.cjs'),input,modulePath],{encoding:'utf8'});
  assert.equal(run.status,status,run.stderr);assert.equal(JSON.parse(run.stdout).ok,status===0);
 }}finally{fs.rmSync(temp,{recursive:true,force:true})}
 console.log('Preflight passed: format-specific budgets, unchanged rejected inputs/previews, reviewed excerpt, UI confirmation, and CLI exit codes');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
