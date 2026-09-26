#!/usr/bin/env node
// Record a ttyd page viewport through the Chrome DevTools Protocol.
//
// Headless Chromium renders the page at the target resolution; Page.startScreencast
// streams lossless PNG frames, which are resampled to a constant frame rate and piped
// straight into ffmpeg. No screen-recording permission, no browser chrome, no pointer,
// and the host screen stays free while the take runs.
//
// usage: node cdp-record.mjs <shot.json>
//
// shot.json:
// {
//   "url": "http://127.0.0.1:7681/",
//   "out": "/abs/path/01-install-cdp-4k.mp4",
//   "width": 3840, "height": 2160, "fps": 30, "crf": 14,
//   "steps": [                       // everything before "start" is off-camera setup
//     { "do": "type", "text": "clear", "delay": 0 },
//     { "do": "press", "key": "Enter" },
//     { "do": "start" },
//     { "do": "wait", "ms": 1500 },
//     { "do": "type", "text": "pi list", "delay": 120 },
//     { "do": "wait", "ms": 2000 },
//     { "do": "press", "key": "Enter" },             // exactly one submission, never retried
//     { "do": "waitText", "text": "Installed", "timeout": 60000 },
//     { "do": "waitNoText", "text": "Working", "timeout": 120000 }, // must stay absent settleMs (default 1500)
//     { "do": "wait", "ms": 2500 },
//     { "do": "stop" }                            // "start" may take its own "out" to split a take
//   ]
// }
//
// Requires playwright-core (npm i playwright-core) and a Chromium build
// (npx playwright install chromium, or set CHROMIUM_PATH).

import { spawn } from "node:child_process";
import { readFileSync, existsSync, readdirSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { chromium } from "playwright-core";

const shot = JSON.parse(readFileSync(process.argv[2], "utf8"));
const { url, out, width = 3840, height = 2160, fps = 30, crf = 14 } = shot;

function chromiumPath() {
  if (process.env.CHROMIUM_PATH) return process.env.CHROMIUM_PATH;
  const cache = join(homedir(), "Library/Caches/ms-playwright");
  if (!existsSync(cache)) return undefined;
  const dir = readdirSync(cache).filter((d) => /^chromium-\d+$/.test(d)).sort().pop();
  const exe = dir && join(cache, dir, "chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing");
  return exe && existsSync(exe) ? exe : undefined;
}

const browser = await chromium.launch({ executablePath: chromiumPath(), headless: true });
const context = await browser.newContext({ viewport: { width, height }, deviceScaleFactor: 1 });
const page = await context.newPage();
await page.goto(url);
await page.waitForFunction(() => !!window.term, null, { timeout: 15000 });
await page.click("body");

// Visible terminal text, read from the xterm.js buffer that ttyd exposes as window.term.
const screenText = () =>
  page.evaluate(() => {
    const b = window.term.buffer.active;
    const lines = [];
    for (let i = b.viewportY; i < b.viewportY + window.term.rows; i++) lines.push(b.getLine(i)?.translateToString(true) ?? "");
    return lines.join("\n");
  });

async function waitFor(predicate, timeout, label) {
  const until = Date.now() + timeout;
  while (Date.now() < until) {
    if (predicate(await screenText())) return;
    await page.waitForTimeout(150);
  }
  throw new Error(`timed out waiting for ${label}`);
}

// Capture: keep the latest screencast frame, emit it at a constant rate into ffmpeg.
const cdp = await context.newCDPSession(page);
let latest;
let ffmpeg;
let ticker;
let started = 0;
let written = 0;
let current;

cdp.on("Page.screencastFrame", async (event) => {
  latest = Buffer.from(event.data, "base64");
  await cdp.send("Page.screencastFrameAck", { sessionId: event.sessionId }).catch(() => {});
});

async function start(target = out) {
  latest = undefined;
  written = 0;
  current = target;
  ffmpeg = spawn("ffmpeg", [
    "-v", "error", "-y",
    "-f", "image2pipe", "-framerate", String(fps), "-c:v", "png", "-i", "-",
    "-c:v", "libx264", "-preset", "slow", "-crf", String(crf), "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
    target,
  ], { stdio: ["pipe", "inherit", "inherit"] });
  await cdp.send("Page.startScreencast", { format: "png", maxWidth: width, maxHeight: height, everyNthFrame: 1 });
  while (!latest) await page.waitForTimeout(20);
  started = Date.now();
  ticker = setInterval(() => {
    const due = Math.floor(((Date.now() - started) * fps) / 1000) + 1;
    for (; written < due; written++) ffmpeg.stdin.write(latest);
  }, 1000 / fps / 2);
}

async function stop() {
  clearInterval(ticker);
  await cdp.send("Page.stopScreencast");
  ffmpeg.stdin.end();
  await new Promise((resolve, reject) => ffmpeg.on("close", (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}`)))));
  console.log(`wrote ${current}: ${written} frames, ${(written / fps).toFixed(1)} s`);
  ffmpeg = undefined;
}

try {
  for (const step of shot.steps) {
    switch (step.do) {
      case "type": await page.keyboard.type(step.text, { delay: step.delay ?? 120 }); break;
      case "paste": await page.keyboard.insertText(step.text); break;
      case "press": await page.keyboard.press(step.key); break;
      case "wait": await page.waitForTimeout(step.ms); break;
      case "waitText": await waitFor((t) => t.includes(step.text), step.timeout ?? 60000, `"${step.text}"`); break;
      case "waitNoText": {
        // A TUI can blank a busy indicator between steps (e.g. between two tool calls), so require
        // the text to stay absent for settleMs before treating the app as idle.
        const settle = step.settleMs ?? 1500;
        const until = Date.now() + (step.timeout ?? 60000);
        let quietSince;
        while (true) {
          if (Date.now() > until) throw new Error(`timed out waiting for no "${step.text}"`);
          if ((await screenText()).includes(step.text)) quietSince = undefined;
          else if ((quietSince ??= Date.now()) + settle <= Date.now()) break;
          await page.waitForTimeout(150);
        }
        break;
      }
      case "screenshot": await page.screenshot({ path: step.path }); break;
      case "start": await start(step.out); break;
      case "stop": await stop(); break;
      default: throw new Error(`unknown step ${step.do}`);
    }
  }
  if (ffmpeg) await stop();
} catch (error) {
  // Leave evidence of the failed state next to the output before tearing down.
  await page.screenshot({ path: `${out}.fail.png` }).catch(() => {});
  console.error(`step failed; screenshot at ${out}.fail.png`);
  throw error;
} finally {
  if (ffmpeg) { clearInterval(ticker); ffmpeg.stdin.end(); }
  await browser.close();
}
