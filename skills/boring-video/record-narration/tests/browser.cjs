// Optional integration test: npm install playwright outside the repository, then
// PLAYWRIGHT_MODULE=/absolute/path/node_modules/playwright node tests/browser.cjs
// RECORDER_ONLY=1 skips audio normalization for constant-level fake microphone input.
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
    assert.equal(await page.locator('#settings').isVisible(), false);
    await page.locator('#menu').click();
    assert.equal(await page.locator('#menu').getAttribute('aria-expanded'), 'true');
    await page.locator('#font').fill('44');
    await page.locator('#font').dispatchEvent('input');
    assert.equal(await page.locator('#scriptInner').evaluate(el => getComputedStyle(el).fontSize), '44px');
    await page.keyboard.press('Escape');
    await page.waitForFunction(() => document.querySelector('#menu').getAttribute('aria-expanded') === 'false');
    await page.locator('#scroll').click();
    await page.waitForFunction(() => document.querySelector('#script').scrollTop >= 10, null, {timeout: 2500});
    await page.locator('#scroll').click();
    await page.locator('#menu').click();
    await page.locator('#top').click();
    await page.locator('#closeMenu').click();
    if (process.env.CAMERA_TEST) {
      await page.locator('#menu').click();
      await page.locator('#cameraEnabled').check();
      await page.locator('#closeMenu').click();
    }
    await page.locator('#record').click();
    await page.waitForFunction(() => !document.querySelector('#stop').disabled);
    assert.equal(await page.locator('#record').isVisible(), false);
    if (process.env.CAMERA_TEST) {
      await page.waitForFunction(() => document.querySelector('#cameraPreview').videoWidth > 0);
      assert.equal(await page.locator('#cameraEnabled').isDisabled(), true);
    }
    await page.waitForFunction(() => document.querySelector('#timer').textContent === '00:03');
    await page.locator('#pause').click();
    assert.equal(await page.locator('#pause').textContent(), '继续录音');
    const paused = await page.locator('#timer').textContent();
    await page.waitForTimeout(1100);
    assert.equal(await page.locator('#timer').textContent(), paused);
    await page.locator('#pause').click();
    await page.route('**/api/takes/*/finalize', route => route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({error: 'simulated finalize failure'})}));
    await page.locator('#stop').click();
    await page.waitForFunction(() => document.body.dataset.error === 'save');
    assert.equal(await page.locator('#fallback').isVisible(), true);
    assert.equal(await page.locator('#notice').getAttribute('role'), 'alert');
    await page.unroute('**/api/takes/*/finalize');
    await page.locator('#retrySave').click();
    await page.waitForFunction(() => !document.querySelector('#finish').disabled);
    await page.locator('#menu').click();
    assert.equal(await page.locator('#player').evaluate(el => el.src.startsWith('blob:')), true);
    await page.waitForFunction(() => document.querySelector('#waveform').dataset.ready === 'true');
    await page.locator('#waveform').scrollIntoViewIfNeeded();
    const box = await page.locator('#waveform').boundingBox();
    await page.mouse.move(box.x + box.width * .2, box.y + box.height / 2);
    await page.mouse.down();
    await page.mouse.move(box.x + box.width * .6, box.y + box.height / 2, {steps: 8});
    await page.mouse.up();
    await page.waitForFunction(() => !document.querySelector('#playSelection').disabled);
    assert.match(await page.locator('#selection').textContent(), /秒/);
    await page.locator('#playSelection').click();
    await page.locator('#player').evaluate(el => el.pause());
    await page.locator('#player').evaluate(el => { el.currentTime = 0; return el.play(); });
    await page.waitForFunction(() => document.querySelector('#player').currentTime > .1);
    await page.locator('#player').evaluate(el => el.pause());
    await page.locator('#finish').click();
    await page.waitForFunction(() => document.querySelector('#message').textContent.includes('已交接'));
    let state = JSON.parse(readFileSync(path.join(root, 'session/session.json')));
    assert.equal(state.status, 'ready');
    assert.equal(state.takes[0].capture.autoGainControl, false);
    assert.equal(state.takes[0].capture.noiseSuppression, false);
    assert.equal(state.takes[0].capture.echoCancellation, false);
    const audio = path.join(root, 'session', state.audio);
    if (process.env.CAMERA_TEST) {
      const handoff = JSON.parse(readFileSync(path.join(root, 'session/handoff.json')));
      assert.equal(handoff.video, handoff.audio);
      assert.ok(state.takes[0].capture.width > 0);
      assert.equal(await page.locator('#cameraPreview').evaluate(el => el.srcObject), null);
      assert.ok(await page.locator('#player').evaluate(el => el.videoWidth > 0));
      const probe = JSON.parse(execFileSync('ffprobe', ['-v', 'error', '-show_streams', '-of', 'json', audio]));
      assert.deepEqual(probe.streams.map(s => s.codec_type).sort(), ['audio', 'video']);
      const decoded = path.join(root, 'camera-audio.wav');
      execFileSync('ffmpeg', ['-v', 'error', '-i', audio, '-vn', decoded]);
      const duration = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', decoded]));
      assert.ok(duration > 2 && duration < 5, `AV pause removed: ${duration}`);
      execFileSync(python, [path.join(skill, 'scripts/export_camera.py'), '--video', audio, '--audio', decoded, '--output', path.join(root, 'author.mp4')]);
    }
    // Streaming WebM often has no duration header. Decode before measuring.
    execFileSync('ffprobe', ['-v', 'error', audio]);
    if (!process.env.RECORDER_ONLY) {
    execFileSync(python, [path.join(skill, 'scripts/process_audio.py'), 'prepare', '--session', path.join(root, 'session'), '--output', path.join(root, 'processed')]);
    const duration = Number(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', path.join(root, 'processed/narration.wav')]).toString());
    assert.ok(duration > 2 && duration < 5, `pause removed from audio duration: ${duration}`);
    }
    // A failed upload must block later chunks so interrupted recovery has a valid prefix.
    await page.route('**/api/takes/*/chunks/1', route => route.fulfill({status: 503, contentType: 'application/json', body: JSON.stringify({error: 'simulated upload failure'})}));
    await page.locator('#record').click();
    await page.waitForFunction(() => !document.querySelector('#stop').disabled);
    await page.waitForFunction(() => document.querySelector('#timer').textContent === '00:07');
    const interrupted = JSON.parse(readFileSync(path.join(root, 'session/session.json'))).takes[1];
    const { readdirSync } = require('node:fs');
    assert.deepEqual(readdirSync(path.join(root, 'session/takes', interrupted.id)).filter(name => name.endsWith('.chunk')), ['000000.chunk']);
    await page.reload();
    await page.waitForFunction(() => document.querySelectorAll('#takes .take').length === 2);
    await page.locator('#menu').click();
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
    if (process.env.CAMERA_TEST) {
      assert.ok(state.takes[1].video);
      const handoff = JSON.parse(readFileSync(path.join(root, 'session/handoff.json')));
      assert.equal(handoff.video, handoff.audio);
      await page.locator('#cameraEnabled').uncheck();
    }
    await page.unroute('**/api/takes/*/chunks/1');
    // A zero-chunk emptyTake take must not trap draft revisions.
    const auth = new URL(url).hash.slice(1);
    const emptyTake = await page.evaluate(async token => {
      const response = await fetch('/api/takes', {method: 'POST',
        headers: {'X-Recorder-Token': token, 'Content-Type': 'application/json'},
        body: JSON.stringify({mime: 'audio/webm', script: document.querySelector('#scriptInner').dataset.source})});
      return response.json();
    }, auth);
    await page.reload();
    await page.waitForFunction(() => !document.querySelector('#record').disabled);
    await page.locator('#menu').click();
    assert.equal(await page.getByRole('button', {name: '恢复已保存部分'}).isDisabled(), true);
    await page.getByRole('button', {name: '放弃此版本'}).click();
    await page.waitForFunction(() => document.querySelector('#takes').textContent.includes('已放弃'));
    const oldSnapshot = readFileSync(path.join(root, 'session/takes', emptyTake.id, 'script.txt'), 'utf8');
    const revised = '修改后的稿件，在原页面继续录制。';
    writeFileSync(script, revised);
    const reused = execFileSync(python, [path.join(skill, 'scripts/recorder.py'),
      '--script', script, '--session', path.join(root, 'session'), '--update-script', '--no-open'], {encoding: 'utf8'});
    assert.ok(reused.includes(url));
    await page.waitForFunction(text => document.querySelector('#scriptInner').dataset.source === text, revised);
    assert.equal(readFileSync(path.join(root, 'session/takes', emptyTake.id, 'script.txt'), 'utf8'), oldSnapshot);
    await page.locator('#closeMenu').click();
    // Force a draft update between the displayed text and take creation.
    const latest = '刚更新的新稿，确认后才能重新开始。';
    await page.route('**/api/takes', async route => {
      await page.request.post(new URL('/api/script', url).href, {
        headers: {'X-Recorder-Token': auth}, data: {text: latest}});
      await route.continue();
    }, {times: 1});
    await page.locator('#record').click();
    await page.waitForFunction(() => document.querySelector('#notice').textContent.includes('请确认新稿'));
    assert.equal(await page.locator('#scriptInner').getAttribute('data-source'), latest);
    assert.equal(JSON.parse(readFileSync(path.join(root, 'session/session.json'))).takes.length, 3);
    assert.equal(await page.locator('#record').isEnabled(), true);
    if (process.env.CAMERA_TEST) {
      await page.locator('#menu').click();
      await page.locator('#cameraEnabled').check();
      await page.locator('#closeMenu').click();
      await page.evaluate(() => {
        window.realGetUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
        navigator.mediaDevices.getUserMedia = async () => { throw new DOMException('Camera permission denied', 'NotAllowedError'); };
      });
      await page.locator('#record').click();
      await page.waitForFunction(() => document.querySelector('#notice').textContent.includes('Camera permission denied'));
      assert.equal(await page.locator('#record').isEnabled(), true);
      assert.equal(JSON.parse(readFileSync(path.join(root, 'session/session.json'))).takes.length, 3);
      await page.evaluate(() => { navigator.mediaDevices.getUserMedia = window.realGetUserMedia; });
      await page.locator('#record').click();
      await page.waitForFunction(() => document.querySelector('#cameraPreview').videoWidth > 0);
      await page.waitForFunction(() => document.querySelector('#timer').textContent === '00:02');
      if (process.env.CAMERA_SCREENSHOT) await page.screenshot({path: process.env.CAMERA_SCREENSHOT});
      await page.evaluate(() => {
        window.interruptedTracks = document.querySelector('#cameraPreview').srcObject.getTracks();
        window.interruptedTracks.find(track => track.kind === 'video').dispatchEvent(new Event('ended'));
      });
      await page.waitForFunction(() => !document.querySelector('#finish').disabled);
      assert.equal(await page.evaluate(() => window.interruptedTracks.every(track => track.readyState === 'ended')), true);
      assert.equal(await page.locator('#notice').isVisible(), true);
      assert.match(await page.locator('#notice').textContent(), /设备已断开/);
    }
    assert.deepEqual(errors, []);
    if (process.env.SCREENSHOT) await page.screenshot({path: process.env.SCREENSHOT + '.desktop.png', fullPage: true});
    await page.setViewportSize({width: 390, height: 844});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.equal(await page.locator('#record').isVisible(), true);
    await page.locator('#menu').click();
    assert.equal(await page.locator('#mic').isVisible(), true);
    await page.locator('#closeMenu').click();
    if (process.env.SCREENSHOT) await page.screenshot({path: process.env.SCREENSHOT, fullPage: true});
    console.log('PASS: recording, pause/resume, playback, handoff, reload recovery, script escaping, abandoned take, live draft update' + (process.env.RECORDER_ONLY ? ' (normalization excluded)' : ', normalization'));
  } catch (error) {
    console.error('Session at failure:', readFileSync(path.join(root, 'session/session.json'), 'utf8'));
    for (const context of browser?.contexts() || []) for (const page of context.pages()) console.error('UI at failure:', await page.locator('#message').textContent(), await page.locator('#timer').textContent());
    throw error;
  } finally {
    await browser?.close(); server.kill('SIGTERM');
    rmSync(root, {recursive: true, force: true});
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
