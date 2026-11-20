// Optional integration test: npm install playwright outside the repository, then
// PLAYWRIGHT_MODULE=/absolute/path/node_modules/playwright node tests/browser.cjs
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const { spawn, execFileSync } = require('node:child_process');
const { mkdtempSync, writeFileSync, readFileSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const path = require('node:path');
const python = process.env.NARRATION_PYTHON || 'python3';
const assert = require('node:assert/strict');
(async () => {
  const root = mkdtempSync(path.join(tmpdir(), 'narration-browser-'));
  const skill = path.resolve(__dirname, '..');
  const script = path.join(root, 'script.txt');
  writeFileSync(script, '今天测试口播录音。\n\n照着读，可以暂停和继续。\n<img src=x onerror=alert(1)>\n' + '这是需要慢慢朗读的口播内容。\n'.repeat(30));
  const server = spawn(python, [path.join(skill, 'scripts/recorder.py'), '--script', script, '--session', path.join(root, 'session'), '--port', '0', '--no-open']);
  let browser;
  try {
    const url = await new Promise((resolve, reject) => {
      const timer = setTimeout(() => reject(new Error('server startup timed out')), 10000);
      server.on('error', reject);
      server.stdout.on('data', data => {
        const match = data.toString().match(/Recorder: (http:\/\/\S+)/);
        if (match) { clearTimeout(timer); resolve(match[1]); }
      });
      server.stderr.on('data', data => process.stderr.write(data));
    });
    browser = await chromium.launch({channel: 'chrome', headless: true,
      args: ['--use-fake-device-for-media-stream', '--use-fake-ui-for-media-stream']});
    const page = await browser.newPage({viewport: {width: 1400, height: 1000}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    page.on('dialog', dialog => dialog.accept());
    page.setDefaultTimeout(15000);
    await page.goto(url);
    await page.waitForFunction(() => !document.querySelector('#record').disabled);
    assert.equal(await page.locator('#script img').count(), 0);
    assert.equal(await page.locator('#waveform').count(), 1);
    await page.locator('#font').fill('44');
    await page.locator('#font').dispatchEvent('input');
    assert.equal(await page.locator('#script').evaluate(el => getComputedStyle(el).fontSize), '44px');
    await page.locator('#scroll').click();
    await page.waitForFunction(() => document.querySelector('#script').scrollTop >= 10, null, {timeout: 2500});
    await page.locator('#scroll').click();
    await page.locator('#top').click();
    await page.locator('#record').click();
    await page.waitForFunction(() => !document.querySelector('#stop').disabled);
    await page.waitForFunction(() => document.querySelector('#timer').textContent === '00:03');
    await page.locator('#pause').click();
    assert.equal(await page.locator('#pause').textContent(), '继续');
    const paused = await page.locator('#timer').textContent();
    await page.waitForTimeout(1100);
    assert.equal(await page.locator('#timer').textContent(), paused);
    await page.locator('#pause').click();
    await page.locator('#stop').click();
    await page.waitForFunction(() => !document.querySelector('#finish').disabled);
    assert.equal(await page.locator('audio').evaluate(el => el.src.startsWith('blob:')), true);
    await page.waitForFunction(() => document.querySelector('#waveform').dataset.ready === 'true');
    const box = await page.locator('#waveform').boundingBox();
    await page.mouse.move(box.x + box.width * .2, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width * .6, box.y + box.height / 2, {steps: 8});
    await page.mouse.up();
    await page.waitForFunction(() => !document.querySelector('#playSelection').disabled);
    assert.match(await page.locator('#selection').textContent(), /秒/);
    await page.locator('#playSelection').click();
    await page.locator('audio').evaluate(el => el.pause());
    await page.locator('audio').evaluate(el => { el.currentTime = 0; return el.play(); });
    await page.waitForFunction(() => document.querySelector('audio').currentTime > .1);
    await page.locator('audio').evaluate(el => el.pause());
    await page.locator('#finish').click();
    await page.waitForFunction(() => document.querySelector('#message').textContent.includes('已交接'));
    let state = JSON.parse(readFileSync(path.join(root, 'session/session.json')));
    assert.equal(state.status, 'ready');
    assert.equal(state.takes[0].capture.autoGainControl, false);
    assert.equal(state.takes[0].capture.noiseSuppression, false);
    assert.equal(state.takes[0].capture.echoCancellation, false);
    const audio = path.join(root, 'session', state.audio);
    // Streaming WebM often has no duration header. Decode before measuring.
    execFileSync('ffprobe', ['-v', 'error', audio]);
    execFileSync(python, [path.join(skill, 'scripts/process_audio.py'), 'prepare', '--session', path.join(root, 'session'), '--output', path.join(root, 'processed')]);
    const duration = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', path.join(root, 'processed/narration.wav')]).toString());
    assert.ok(duration > 2 && duration < 5, `pause removed from audio duration: ${duration}`);
    // A failed upload must block later chunks so interrupted recovery has a valid prefix.
    await page.route('**/api/takes/*/chunks/1', route => route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({error: 'simulated upload failure'})}));
    await page.locator('#record').click();
    await page.waitForFunction(() => !document.querySelector('#stop').disabled);
    await page.waitForFunction(() => document.querySelector('#timer').textContent === '00:07');
    const interrupted = JSON.parse(readFileSync(path.join(root, 'session/session.json'))).takes[1];
    const { readdirSync } = require('node:fs');
    assert.deepEqual(readdirSync(path.join(root, 'session/takes', interrupted.id)).filter(name => name.endsWith('.chunk')), ['000000.chunk']);
    await page.reload();
    await page.waitForFunction(() => document.querySelectorAll('#takes button').length === 2);
    const recovery = page.locator('#takes button').filter({hasText: '恢复'});
    await recovery.click();
    await page.waitForFunction(() => document.querySelector('#message').textContent.includes('已恢复保存部分'));
    assert.equal(await page.locator('#takes button').count(), 2);
    await page.locator('#finish').click();
    await page.waitForFunction(() => document.querySelector('#message').textContent.includes('已交接'));
    state = JSON.parse(readFileSync(path.join(root, 'session/session.json')));
    assert.equal(state.takes.length, 2);
    assert.equal(state.takes.every(take => take.complete), true);
    execFileSync('ffprobe', ['-v', 'error', path.join(root, 'session', state.audio)]);
    assert.deepEqual(errors, []);
    if (process.env.SCREENSHOT) await page.screenshot({path: process.env.SCREENSHOT, fullPage: true});
    console.log('PASS: recording, pause/resume, playback, normalization, handoff, reload recovery, script escaping');
  } catch (error) {
    console.error('Session at failure:', readFileSync(path.join(root, 'session/session.json'), 'utf8'));
    for (const context of browser?.contexts() || []) for (const page of context.pages()) console.error('UI at failure:', await page.locator('#message').textContent(), await page.locator('#timer').textContent());
    throw error;
  } finally {
    await browser?.close(); server.kill('SIGTERM');
    rmSync(root, {recursive: true, force: true});
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
