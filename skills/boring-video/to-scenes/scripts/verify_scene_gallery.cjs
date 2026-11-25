#!/usr/bin/env node
// Supply a Playwright module path when it is not installed in the caller's environment.
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require(process.argv[2] || 'playwright');
const gallery = path.resolve(__dirname, '../assets/scene-patterns/gallery.html');

(async () => {
  const browser = await chromium.launch({headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1920, height: 1080}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(pathToFileURL(gallery).href);
    await page.evaluate(() => document.fonts.ready);
    const ids = await page.evaluate(() => SCENE_CATALOG.map(record => record.id));
    assert.equal(ids.length, 20);
    await page.evaluate(() => document.head.insertAdjacentHTML('beforeend',
      '<style>nav,aside,#info,details,#work>p{display:none}#layout{display:block}#work{padding:0}#viewport{width:1920px;height:1080px;overflow:visible}#stage{transform:none!important}</style>'));
    let variants = 0;
    for (const theme of ['blockframe', 'swiss-minimalism', 'raycast-dark', 'claude-warm']) {
      for (const id of ids) {
        const result = await page.evaluate(async ({id, theme}) => {
          const host = document.querySelector('#stage');
          const scene = ScenePatterns.render(host, id, {}, {theme, time: 4});
          await document.fonts.ready;
          await Promise.all([...host.querySelectorAll('img')].map(img => img.decode()));
          const state = time => {scene.setTime(time); return host.innerHTML;};
          const direct = state(4);
          state(0);
          for (let time = 0; time <= 4; time += .1) scene.setTime(time);
          const sequential = state(4);
          state(7.9);
          const backward = state(4);
          const main = host.querySelector('main').getBoundingClientRect();
          const overflow = [...host.querySelectorAll('main h2,main h3,main p,main small,main b,main pre,main .card,main .source-surface,main .demo,main .presenter')]
            .filter(el => {
              const rect = el.getBoundingClientRect();
              return rect.bottom > main.bottom + 1 || rect.right > main.right + 1 || rect.left < main.left - 1;
            }).map(el => el.textContent.slice(0, 40));
          return {seek: direct === sequential && direct === backward, overflow};
        }, {id, theme});
        assert.ok(result.seek, `${id}/${theme}: inconsistent seek`);
        assert.deepEqual(result.overflow, [], `${id}/${theme}: overflow`);
        variants++;
      }
    }
    await page.reload();
    await page.locator('#search').fill('盲测');
    await page.locator('#list button').click();
    await page.locator('#theme').selectOption('raycast-dark');
    for (const [time, opacity] of [['6', '1'], ['2', '0']]) {
      await page.locator('#time').fill(time);
      await page.locator('#time').dispatchEvent('input');
      assert.equal(await page.locator('.identity').first().evaluate(el => getComputedStyle(el).opacity), opacity);
    }
    await page.locator('summary').click();
    await page.locator('#props').fill(JSON.stringify({title: '替换后的项目标题'}));
    await page.locator('#apply').click();
    assert.equal(await page.locator('#stage h1').textContent(), '替换后的项目标题');
    assert.deepEqual(errors, []);
    console.log(`${variants} theme variants: fonts/images loaded, no default-content overflow, deterministic seek; gallery filtering/theme/reveal/edit checks passed`);
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
