#!/usr/bin/env node
// Validate a selection without creating a preview. Exit 2 requires user adjustment.
const fs=require('node:fs'),path=require('node:path');
const {pathToFileURL}=require('node:url');
if(!process.argv[2]||process.argv[2]==='--help'){
 console.log('Usage: node validate_scene_selection.cjs selection.json [playwright-module-path]');process.exit(process.argv[2]?0:1);
}
(async()=>{
 const selection=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
 const {chromium}=require(process.argv[3]||'playwright'),browser=await chromium.launch({headless:true});
 try{
  const page=await browser.newPage();
  await page.goto(pathToFileURL(path.resolve(__dirname,'../assets/scene-patterns/gallery.html')).href+'?preflight=1');
  const report=await page.evaluate(s=>ScenePatterns.validate(s.id,s.props||{},{theme:s.theme,mode:s.mode,revision:s.revision}),selection);
  console.log(JSON.stringify(report,null,2));process.exitCode=report.ok?0:2;
 }finally{await browser.close()}
})().catch(error=>{console.error(error.message);process.exitCode=1});
