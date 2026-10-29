/**
 * tests/test_browser_demo.mjs — EcoPilot Automated Browser Testing Script
 *
 * Launches Google Chrome in headless mode with remote debugging (CDP),
 * loads ecopilot_demo.html, and executes 4 automated testing scenarios:
 *   1. Calm Conditions: Verifies physics telemetry, R_env < 0.25, and nominal envelope.
 *   2. Severe Weather: Injects extreme wind and pressure drop, verifies R_env > 0.85 and hard safety override triggers.
 *   3. Agent Switching & Mission Execution: Steps through greedy policy navigation, logs safety interventions.
 *   4. Policy Reset & Telemetry Verification.
 *
 * Complies with IMPROVEMENT_PLAN.md:
 *   - Fails with non-zero exit code on incorrect telemetry or missing interventions.
 *   - Captures and prints Chrome stderr and startup/connection errors in failure output.
 *   - Uses isolated user-data-dir to guarantee clean headless execution without profile conflicts.
 */

import { spawn } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const PORT = 9222;
const HTML_PATH = "file://" + path.resolve("ecopilot_demo.html");
const SCREENSHOT_DIR = path.resolve("tests/screenshots");
const USER_DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "ecopilot-chrome-"));

fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

async function sleep(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

console.log("=== Launching Google Chrome (Headless CDP) ===");
let chromeStderr = "";
let chromeStdout = "";
let chromeExitCode = null;
let chromeSpawnError = null;

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

chrome.stdout?.on("data", (data) => {
  chromeStdout += data.toString();
});

chrome.stderr?.on("data", (data) => {
  chromeStderr += data.toString();
});

chrome.on("error", (err) => {
  chromeSpawnError = err;
  console.error("[Chrome Process Error]", err);
});

chrome.on("exit", (code, signal) => {
  chromeExitCode = code !== null ? code : signal;
});

function cleanup() {
  try {
    chrome.kill("SIGKILL");
  } catch (_) {}
  try {
    fs.rmSync(USER_DATA_DIR, { recursive: true, force: true });
  } catch (_) {}
}

process.on("exit", cleanup);
process.on("SIGINT", () => {
  cleanup();
  process.exit(1);
});

// Helper to send CDP commands
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

  const ready = new Promise((resolve, reject) => {
    ws.onopen = resolve;
    ws.onerror = reject;
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
    close() {
      ws.close();
    },
  };
}

async function runBrowserTests() {
  let targets = null;
  let lastFetchError = null;

  for (let i = 0; i < 25; i++) {
    await sleep(400);
    if (chromeExitCode !== null) {
      break; // Chrome died early
    }
    try {
      const resp = await fetch(`http://127.0.0.1:${PORT}/json`);
      if (resp.ok) {
        targets = await resp.json();
        break;
      }
    } catch (err) {
      lastFetchError = err;
    }
  }

  if (!targets || targets.length === 0) {
    const errorDetails = [
      "Failed to connect to Chrome DevTools Protocol at http://127.0.0.1:" + PORT,
      `Chrome Process Exit Code: ${chromeExitCode}`,
      `Chrome Spawn Error: ${chromeSpawnError ? chromeSpawnError.message : "None"}`,
      `Last Network Fetch Error: ${lastFetchError ? lastFetchError.message : "None"}`,
      "--- Captured Chrome Stderr Output ---",
      chromeStderr.trim() || "(No stderr captured)",
      "--- Captured Chrome Stdout Output ---",
      chromeStdout.trim() || "(No stdout captured)",
    ].join("\n");
    throw new Error(errorDetails);
  }

  const pageTarget = targets.find((t) => t.type === "page") || targets[0];
  console.log(`Connected to page: ${pageTarget.title || pageTarget.url}`);

  const client = createCDPClient(pageTarget.webSocketDebuggerUrl);
  await client.send("Page.enable");
  await client.send("Runtime.enable");

  await sleep(1000); // Allow initial canvas draw

  console.log("\n--- TEST 1: Calm Conditions & Initial Telemetry ---");
  await client.evaluate(`
    document.getElementById('sliderWind').value = '2.0';
    document.getElementById('sliderRH').value = '45';
    document.getElementById('sliderDP').value = '0.0';
    updatePhysics();
  `);
  await sleep(300);

  const calmMetrics = await client.evaluate(`({
    r_env: parseFloat(document.getElementById('valREnv').innerText),
    rho: document.getElementById('valRho').innerText,
    q: document.getElementById('valQ').innerText,
    badge: document.getElementById('safetyBadge').innerText
  })`);
  console.log("Calm State Metrics:", calmMetrics);

  if (calmMetrics.r_env < 0.25 && calmMetrics.badge.includes("NOMINAL")) {
    console.log("✓ PASS: Calm telemetry within nominal flight limits.");
  } else {
    throw new Error(`TEST 1 FAILED: Unexpected calm telemetry values: ${JSON.stringify(calmMetrics)}`);
  }
  await client.captureScreenshot("1_calm_nominal.png");

  console.log("\n--- TEST 2: Severe Squall & Safety Override Trigger ---");
  await client.evaluate(`
    document.getElementById('sliderWind').value = '15.0';
    document.getElementById('sliderDP').value = '-2.8';
    document.getElementById('sliderRH').value = '90';
    updatePhysics();
  `);
  await sleep(300);

  const severeMetrics = await client.evaluate(`({
    r_env: parseFloat(document.getElementById('valREnv').innerText),
    rho: document.getElementById('valRho').innerText,
    q: document.getElementById('valQ').innerText,
    badge: document.getElementById('safetyBadge').innerText,
    lambda: document.getElementById('valLambda').innerText
  })`);
  console.log("Severe State Metrics:", severeMetrics);

  if (severeMetrics.r_env >= 0.85 && severeMetrics.badge.includes("OVERRIDE")) {
    console.log("✓ PASS: Critical safety override triggered in DOM (badge: OVERRIDE ACTIVE).");
  } else {
    throw new Error(`TEST 2 FAILED: Safety override did not trigger under severe squall: ${JSON.stringify(severeMetrics)}`);
  }
  await client.captureScreenshot("2_severe_override_triggered.png");

  console.log("\n--- TEST 3: Stepping Policy Under Extreme Risk ---");
  const flightResult = await client.evaluate(`
    (() => {
      isFlying = true;
      for (let i = 0; i < 5; i++) {
        stepSimulation();
      }
      isFlying = false;
      return {
        step: document.getElementById('stepCounter').innerText,
        dronePos: document.getElementById('valDronePos').innerText,
        overrides: parseInt(document.getElementById('valOverrides').innerText),
        recentLogs: Array.from(document.querySelectorAll('#logBox div')).slice(-5).map(d => d.innerText)
      };
    })()
  `);
  console.log("Flight Intervention Results:", flightResult);

  if (flightResult.overrides > 0) {
    console.log(`✓ PASS: Safety envelope successfully intercepted and executed safe maneuvers (${flightResult.overrides} overrides logged).`);
  } else {
    throw new Error("TEST 3 FAILED: No safety interventions were recorded during extreme squall weather.");
  }
  await client.captureScreenshot("3_policy_interventions_active.png");

  console.log("\n--- TEST 4: Agent Selection & Reset ---");
  await client.evaluate(`
    document.getElementById('agentSelect').value = 'baseline';
    updateAgentSelection();
    setWeatherPreset('calm');
    resetMission(false);
  `);
  await sleep(400);

  const baselineState = await client.evaluate(`({
    selectedAgent: document.getElementById('agentSelect').value,
    badge: document.getElementById('safetyBadge').innerText,
    dronePos: document.getElementById('valDronePos').innerText,
    r_env: document.getElementById('valREnv').innerText
  })`);
  console.log("Static Baseline State:", baselineState);

  if (baselineState.selectedAgent === "baseline" && baselineState.badge.includes("NOMINAL")) {
    console.log("✓ PASS: Agent dropdown toggled to baseline and mission reset cleanly.");
  } else {
    throw new Error(`TEST 4 FAILED: Agent selection reset failed: ${JSON.stringify(baselineState)}`);
  }
  await client.captureScreenshot("4_static_baseline_reset.png");

  console.log("\n=== All Browser Tests Completed Successfully ===");
  client.close();
  cleanup();
  process.exit(0);
}

runBrowserTests().catch((err) => {
  console.error("\n================ BROWSER INTEGRATION TEST FAILURE ================");
  console.error(err.message || err);
  console.error("==================================================================\n");
  cleanup();
  process.exit(1);
});
