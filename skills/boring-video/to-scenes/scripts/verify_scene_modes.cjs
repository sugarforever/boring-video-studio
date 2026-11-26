const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(process.argv[2] || 'playwright');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1920,height:1080}});
  await page.goto(pathToFileURL(path.resolve(__dirname,'../assets/scene-patterns/gallery.html')).href);
  const result=await page.evaluate(async()=>{
   const host=document.querySelector('#stage');
   ScenePatterns.render(host,'release-timeline',{}, {theme:'blockframe',mode:'light',time:4});
   const light=getComputedStyle(host).backgroundColor;
   ScenePatterns.render(host,'release-timeline',{}, {theme:'blockframe',mode:'dark',time:4});
   return {light,dark:getComputedStyle(host).backgroundColor};
  });
  assert.notEqual(result.light,result.dark,'light and dark must have independently resolved palettes');
  console.log('Light/dark palettes are distinct');
 } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
