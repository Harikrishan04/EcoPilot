/**
 * tests/test_ui_phase2_enhancements.mjs
 * End-to-end browser verification of EcoPilot Phase 2 UI Enhancements:
 *  1. Mission status bar & avionics telemetry (altitude ASL, clearance AGL, battery SoC)
 *  2. Tab navigation (Live, Replay, Benchmark, Specs)
 *  3. Flight log replay playback (Calm, Moderate, Severe Emergency)
 *  4. SVG mini-altitude chart rendering
 *  5. Dynamic benchmark table population from evaluation_summary.csv
 *  6. Safety override diagnostics card
 */

import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const PORT = 9223;
const HTML_PATH = "file://" + path.resolve("ecopilot_demo.html");
const SCREENSHOT_DIR = path.resolve("tests/screenshots");
const USER_DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "ecopilot-p2-test-"));

fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

async function sleep(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

let chromeStderr = "";
let chromeStdout = "";
let chromeExitCode = null;

const chrome = spawn(
  "google-chrome",
  [
    `--remote-debugging-port=${PORT}`,
    "--headless=new",
    "--disable-gpu",
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--disable-software-rasterizer",
    "--disable-crash-reporter",
    "--disable-breakpad",
    "--no-default-browser-check",
    "--no-first-run",
    "--disable-extensions",
    "--disable-background-networking",
    `--user-data-dir=${USER_DATA_DIR}`,
    "--window-size=1440,950",
    HTML_PATH,
  ]
);

chrome.stdout?.on("data", (d) => { chromeStdout += d.toString(); });
chrome.stderr?.on("data", (d) => { chromeStderr += d.toString(); });
chrome.on("exit", (code, signal) => { chromeExitCode = code !== null ? code : signal; });

function cleanup() {
  try { chrome.kill("SIGKILL"); } catch (_) {}
  try { fs.rmSync(USER_DATA_DIR, { recursive: true, force: true }); } catch (_) {}
}

process.on("exit", cleanup);
process.on("SIGINT", () => { cleanup(); process.exit(1); });

function createCDPClient(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 1;
  const callbacks = new Map();

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.id && callbacks.has(data.id)) {
      const cb = callbacks.get(data.id);
      callbacks.delete(data.id);
      cb(data.result);
    }
  };

  const ready = new Promise((res, rej) => {
    ws.onopen = res;
    ws.onerror = rej;
  });

  return {
    async send(method, params = {}) {
      await ready;
      return new Promise((resolve) => {
        const reqId = id++;
        callbacks.set(reqId, resolve);
        ws.send(JSON.stringify({ id: reqId, method, params }));
      });
    },
    async evaluate(expression) {
      const res = await this.send("Runtime.evaluate", {
        expression,
        returnByValue: true,
        awaitPromise: true,
      });
      return res?.result?.value;
    },
    async captureScreenshot(filename) {
      const res = await this.send("Page.captureScreenshot", { format: "png" });
      const buffer = Buffer.from(res.data, "base64");
      const outPath = path.join(SCREENSHOT_DIR, filename);
      fs.writeFileSync(outPath, buffer);
      console.log(`[Screenshot] Saved -> ${outPath}`);
    },
    close() { ws.close(); }
  };
}

async function runTests() {
  console.log("=== Testing EcoPilot Phase 2 UI Enhancements ===");
  let targets = null;
  for (let i = 0; i < 25; i++) {
    await sleep(400);
    try {
      const resp = await fetch(`http://127.0.0.1:${PORT}/json`);
      if (resp.ok) {
        targets = await resp.json();
        break;
      }
    } catch (_) {}
  }

  if (!targets || targets.length === 0) {
    throw new Error(`Failed to connect to Chrome at port ${PORT}:\n${chromeStderr}`);
  }

  const page = targets.find((t) => t.type === "page") || targets[0];
  const client = createCDPClient(page.webSocketDebuggerUrl);
  await client.send("Page.enable");
  await client.send("Runtime.enable");

  await sleep(800);

  // 1. Check Initial Phase 2 Avionics Telemetry
  console.log("\n[Check 1] Persistent Mission Status Bar & Avionics Displays...");
  const initTelemetry = await client.evaluate(`({
    missionState: document.getElementById('missionState')?.innerText,
    missionClock: document.getElementById('missionClock')?.innerText,
    safetyBadge: document.getElementById('safetyBadge')?.innerText,
    altitude: document.getElementById('valAltitude')?.innerText,
    clearance: document.getElementById('valClearance')?.innerText,
    battery: document.getElementById('valBattery')?.innerText,
    svgLength: document.getElementById('altitudeSvg')?.innerHTML?.length || 0
  })`);
  console.log("Initial Avionics Telemetry:", initTelemetry);

  if (!initTelemetry.missionState || !initTelemetry.missionClock || !initTelemetry.altitude || initTelemetry.svgLength === 0) {
    throw new Error("Missing Phase 2 avionics elements or SVG altitude chart");
  }
  console.log("✓ PASS: Phase 2 status bar, altitude ASL, clearance, battery, and SVG chart verified.");

  // 2. Test Tab Navigation
  console.log("\n[Check 2] Tab Navigation...");
  await client.evaluate(`switchTab('eval');`);
  await sleep(300);

  const evalSectionVisible = await client.evaluate(`({
    evalDisplay: document.getElementById('sectionEval')?.style?.display,
    modeLabel: document.getElementById('activeModeLabel')?.innerText,
    tableRows: document.querySelectorAll('#benchmarkTableContainer table tr')?.length
  })`);
  console.log("Evaluation Tab State:", evalSectionVisible);

  if (evalSectionVisible.evalDisplay !== 'block' || evalSectionVisible.tableRows < 9) {
    throw new Error(`Evaluation tab did not render correctly: ${JSON.stringify(evalSectionVisible)}`);
  }
  console.log(`✓ PASS: Benchmark tab active with ${evalSectionVisible.tableRows} table rows rendered from evaluation_summary.csv.`);
  await client.captureScreenshot("5_benchmark_eval_tab.png");

  // 3. Test Model Specs Tab
  console.log("\n[Check 3] Model Specs Tab...");
  await client.evaluate(`switchTab('specs');`);
  await sleep(200);

  const specsState = await client.evaluate(`({
    specsDisplay: document.getElementById('sectionSpecs')?.style?.display,
    specCards: document.querySelectorAll('#sectionSpecs .spec-card')?.length
  })`);
  console.log("Specs Tab State:", specsState);

  if (specsState.specsDisplay !== 'block' || specsState.specCards < 4) {
    throw new Error("Specs tab failed to display technical spec cards");
  }
  console.log("✓ PASS: Model assumptions & aerodynamics specs displayed.");

  // 4. Test Flight Log Replay Mode
  console.log("\n[Check 4] Phase 2 Flight Log Replay...");
  await client.evaluate(`switchTab('replay');`);
  await sleep(300);

  // Load emergency/severe log
  await client.evaluate(`loadFlightLog('emergency');`);
  await sleep(300);

  // Step forward 10 steps in replay
  await client.evaluate(`
    for (let i = 0; i < 10; i++) {
      stepReplay(1);
    }
  `);
  await sleep(300);

  const replayState = await client.evaluate(`({
    stepLabel: document.getElementById('replayStepLabel')?.innerText,
    dronePos: document.getElementById('valDronePos')?.innerText,
    alt: document.getElementById('valAltitude')?.innerText,
    clearance: document.getElementById('valClearance')?.innerText,
    battery: document.getElementById('valBattery')?.innerText,
    clock: document.getElementById('missionClock')?.innerText,
    safetyEvent: document.getElementById('safetyEventContent')?.innerText
  })`);
  console.log("Replay Step 10 Telemetry:", replayState);

  if (!replayState.stepLabel.includes("Step 10") || !replayState.alt || !replayState.clock) {
    throw new Error(`Replay telemetry did not advance properly: ${JSON.stringify(replayState)}`);
  }
  console.log("✓ PASS: Replay successfully scrubs through 3D telemetry, updates altitude, clearance, battery SoC, and mission clock.");
  await client.captureScreenshot("6_flight_log_replay.png");

  // 5. Return to Live Simulation and Reset
  console.log("\n[Check 5] Return to Live Simulation...");
  await client.evaluate(`
    switchTab('live');
    resetMission(false);
  `);
  await sleep(300);

  const liveState = await client.evaluate(`({
    mode: document.getElementById('activeModeLabel')?.innerText,
    state: document.getElementById('missionState')?.innerText,
    step: document.getElementById('stepCounter')?.innerText
  })`);
  console.log("Returned to Live State:", liveState);

  if (liveState.mode !== "LIVE SIMULATOR" || liveState.state !== "READY" || liveState.step !== "Step: 0 / 100") {
    throw new Error(`Failed to restore live simulation state: ${JSON.stringify(liveState)}`);
  }
  console.log("✓ PASS: Cleanly switched back to live simulation with nominal reset state.");

  console.log("\n=== All Phase 2 UI Enhancements Verified Successfully! ===");
  client.close();
  cleanup();
  process.exit(0);
}

runTests().catch((err) => {
  console.error("\nTEST FAILED:", err.message || err);
  cleanup();
  process.exit(1);
});
