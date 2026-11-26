// PLAYWRIGHT_MODULE=/absolute/path/node_modules/playwright node tests/reading.cjs
const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const {spawn, execFileSync} = require('node:child_process');
const {mkdtempSync, writeFileSync, readFileSync, rmSync} = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
(async () => {
  const root = mkdtempSync(path.join(require('node:os').tmpdir(), 'narration-reading-'));
  const skill = path.resolve(__dirname, '..');
  const script = path.join(root, 'script.txt');
  writeFileSync(script, '这是一段固定阅读区测试，文字保持在镜头下方，让视线尽量看向正前方。\n\n'.repeat(30));
  const server = spawn(process.env.NARRATION_PYTHON || 'python3', [path.join(skill, 'scripts/recorder.py'), '--script', script, '--session', path.join(root, 'session'), '--port', '0', '--no-open']);
  let browser;
  try {
    const url = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(Error('startup timeout')), 10000);
      server.on('error', reject);
      server.stdout.on('data', data => { const match = String(data).match(/Recorder: (http:\/\/\S+)/); if (match) {clearTimeout(timer); resolve(match[1]);} });
    });
    browser = await chromium.launch({channel: 'chrome', headless: true, args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']});
    const page = await browser.newPage({viewport: {width: 1400, height: 1000}});
    page.setDefaultTimeout(10000);
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(url);
    await page.waitForFunction(() => !document.querySelector('#record').disabled);
    assert.equal(await page.locator('#cameraEnabled').isVisible(), true);
    assert.equal(await page.locator('#cameraEnabled').evaluate(el => !!el.closest('#bar')), true);
    assert.equal(await page.locator('#readingFocus').isChecked(), true);
    const reading = await page.locator('#script').boundingBox();
    assert.ok(reading.y < 100 && reading.height < 300);
    assert.ok(Math.abs(reading.x + reading.width/2 - 700) < 2);
    await page.locator('#scroll').click();
    await page.waitForFunction(() => document.querySelector('#script').scrollTop > 10);
    await page.locator('#scroll').click();
    assert.deepEqual(await page.locator('#script').boundingBox(), reading);
    await page.locator('#menu').click();
    await page.locator('#readingWidth').fill('10');
    await page.locator('#readingWidth').dispatchEvent('input');
    assert.ok((await page.locator('#script').boundingBox()).width < reading.width);
    await page.locator('#readingFocus').uncheck();
    assert.ok((await page.locator('#script').boundingBox()).height > 500);
    await page.locator('#readingFocus').check();
    await page.locator('#closeMenu').click();
    await page.evaluate(() => {
      window.realMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
      navigator.mediaDevices.getUserMedia = async () => {throw new DOMException('Camera permission denied', 'NotAllowedError');};
    });
    await page.locator('#cameraEnabled').click();
    await page.waitForFunction(() => !document.querySelector('#cameraEnabled').checked && !document.querySelector('#record').disabled);
    assert.match(await page.locator('#notice').textContent(), /Camera permission denied/);
    assert.equal(JSON.parse(readFileSync(path.join(root, 'session/session.json'))).takes.length, 0);
    await page.evaluate(() => {navigator.mediaDevices.getUserMedia = async constraints => {
      const media = await window.realMedia(constraints);
      if (constraints.audio) window.micTracks = media.getAudioTracks();
      return media;
    };});
    await page.locator('#cameraEnabled').check();
    await page.waitForFunction(() => document.querySelector('#cameraPreview').videoWidth > 0);
    await page.evaluate(() => {window.firstPreview = document.querySelector('#cameraPreview').srcObject;});
    const device = await page.locator('#camera option').last().getAttribute('value');
    await page.locator('#camera').selectOption(device);
    await page.waitForFunction(() => document.querySelector('#cameraPreview').srcObject && document.querySelector('#cameraPreview').srcObject !== window.firstPreview);
    assert.equal(await page.evaluate(() => window.firstPreview.getTracks().every(t => t.readyState === 'ended')), true);
    for (const id of ['camera', 'cameraAspect', 'cameraCenter', 'cameraBehind', 'mic']) {
      assert.equal(await page.locator('#' + id).evaluate(el => !!el.closest('#bar')), true);
    }

    await page.waitForTimeout(1100);
    const idle = JSON.parse(readFileSync(path.join(root, 'session/session.json')));
    assert.equal(idle.takes.length, 0, 'preview does not create takes');
    assert.equal(require('node:fs').existsSync(path.join(root, 'session/takes')), false);
    assert.equal(await page.locator('#cameraPreview').evaluate(el => el.srcObject.getAudioTracks().length), 0);
    await page.evaluate(() => {window.preflightStream = document.querySelector('#cameraPreview').srcObject;});
    if (process.env.PREFLIGHT_SCREENSHOT) await page.screenshot({path: process.env.PREFLIGHT_SCREENSHOT});
    await page.locator('#record').click();
    await page.waitForFunction(() => !document.querySelector('#stop').disabled);
    assert.equal(await page.evaluate(() => document.querySelector('#cameraPreview').srcObject === window.preflightStream), true);

    await page.evaluate(() => {window.originalStream = document.querySelector('#cameraPreview').srcObject;});
    await page.locator('#toggleCameraPreview').click();
    assert.equal(await page.locator('#cameraMonitor').isVisible(), false);
    assert.equal(await page.evaluate(() => window.originalStream.getTracks().every(t => t.readyState === 'live')), true);
    await page.locator('#toggleCameraPreview').click();
    assert.equal(await page.locator('#cameraMonitor').isVisible(), true);
    assert.equal(await page.evaluate(() => document.querySelector('#cameraPreview').srcObject === window.originalStream), true);
    await page.locator('#cameraCenter').click();
    await page.locator('#cameraBehind').check();
    const monitor = await page.locator('#cameraMonitor').boundingBox();
    assert.ok(Math.abs(monitor.x + monitor.width/2 - 700) < 2);
    const onTop = await page.evaluate(() => {
      const box = document.querySelector('#cameraMonitor').getBoundingClientRect();
      return !!document.elementFromPoint(box.x + box.width/2, box.y + 30)?.closest('#script');
    });
    assert.equal(onTop, true, 'reading text stays above centered camera');
    if (process.env.READING_SCREENSHOT) await page.screenshot({path: process.env.READING_SCREENSHOT});
    await page.locator('#cameraBehind').uncheck();
    assert.equal(await page.evaluate(() => {
      const box = document.querySelector('#cameraMonitor').getBoundingClientRect();
      return !!document.elementFromPoint(box.x + 10, box.y + 20)?.closest('#cameraMonitor');
    }), true);
    await page.locator('#toggleCameraPreview').click();
    await page.locator('#stop').click();
    await page.waitForFunction(() => !document.querySelector('#finish').disabled);
    assert.equal(await page.evaluate(() => window.originalStream.getTracks().every(t => t.readyState === 'live')), true);
    assert.equal(await page.evaluate(() => window.micTracks.every(t => t.readyState === 'ended')), true);
    await page.locator('#cameraEnabled').uncheck();
    assert.equal(await page.evaluate(() => window.originalStream.getTracks().every(t => t.readyState === 'ended')), true);
    const state = JSON.parse(readFileSync(path.join(root, 'session/session.json')));
    const source = path.join(root, 'session', state.takes[0].video);
    const streams = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_streams', '-of', 'json', source])).streams;
    assert.deepEqual(streams.map(s => s.codec_type).sort(), ['audio', 'video']);
    await page.reload();
    await page.waitForFunction(() => !document.querySelector('#record').disabled);
    assert.equal(await page.locator('#readingWidth').inputValue(), '10');
    assert.equal(await page.locator('#readingFocus').isChecked(), true);
    assert.equal(await page.locator('#cameraBehind').isChecked(), false);
    await page.locator('#cameraEnabled').check();
    await page.waitForFunction(() => !document.querySelector('#toggleCameraPreview').hidden);
    assert.equal(await page.locator('#cameraMonitor').isVisible(), true, 'explicit camera-on reveals preview');
    await page.locator('#toggleCameraPreview').click();
    await page.locator('#record').click();
    await page.waitForFunction(() => !document.querySelector('#stop').disabled);
    assert.equal(await page.locator('#cameraMonitor').isVisible(), false);
    await page.locator('#toggleCameraPreview').click();
    await page.setViewportSize({width: 390, height: 844});
    const mobile = await page.locator('#script').boundingBox();
    assert.ok(mobile.x >= 0 && mobile.x + mobile.width <= 390);
    if (process.env.PREFLIGHT_MOBILE_SCREENSHOT) await page.screenshot({path: process.env.PREFLIGHT_MOBILE_SCREENSHOT});
    await page.setViewportSize({width: 844, height: 390});
    await page.waitForTimeout(100);
    assert.equal(await page.evaluate(() => document.querySelector('#script').getBoundingClientRect().bottom <= document.querySelector('#bar').getBoundingClientRect().top), true);
    await page.setViewportSize({width: 390, height: 844});
    await page.locator('#stop').click();
    await page.waitForFunction(() => !document.querySelector('#finish').disabled);
    await page.evaluate(() => {
      window.idleTracks = document.querySelector('#cameraPreview').srcObject.getTracks();
      window.idleTracks[0].dispatchEvent(new Event('ended'));
    });
    assert.equal(await page.locator('#cameraEnabled').isChecked(), false);
    assert.equal(await page.locator('#cameraMonitor').isVisible(), false);
    assert.equal(await page.evaluate(() => window.idleTracks.every(t => t.readyState === 'ended')), true);
    assert.equal(JSON.parse(readFileSync(path.join(root, 'session/session.json'))).takes.length, 2);
    // A device can disappear while the take-creation request is still pending.
    await page.locator('#cameraEnabled').check();
    await page.waitForFunction(() => !document.querySelector('#record').disabled);
    let releaseStart, createdTake;
    const startGate = new Promise(resolve => {releaseStart = resolve;});
    const takeCreated = new Promise(resolve => {createdTake = resolve;});
    await page.route('**/api/takes', async route => {
      const response = await route.fetch();
      createdTake(await response.json());
      await startGate;
      await route.fulfill({response});
    }, {times: 1});
    await page.locator('#record').click();
    const pendingTake = await takeCreated;
    await page.locator('#cameraPreview').evaluate(el => el.srcObject.getVideoTracks()[0].dispatchEvent(new Event('ended')));
    releaseStart();
    await page.waitForFunction(() => !document.querySelector('#record').disabled && document.body.dataset.error === 'perm');
    const stoppedStart = JSON.parse(readFileSync(path.join(root, 'session/session.json'))).takes.find(t => t.id === pendingTake.id);
    assert.equal(stoppedStart.complete, false);
    assert.equal(stoppedStart.abandoned, true, 'failed startup abandons its empty take');
    assert.equal(require('node:fs').readdirSync(path.join(root, 'session/takes', pendingTake.id)).filter(n => n.endsWith('.chunk')).length, 0);
    assert.equal(await page.locator('#cameraMonitor').isVisible(), false);
    assert.deepEqual(errors, []);
    console.log('PASS: fixed reading area, width, full view, camera layering, preview visibility without stopping capture, persistence and mobile layout');
  } finally { await browser?.close(); server.kill('SIGTERM'); rmSync(root, {recursive: true, force: true}); }
})().catch(error => {console.error(error); process.exitCode = 1;});
