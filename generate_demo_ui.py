import json, csv

calm = json.load(open('data/flight_logs/calm_flight_log.json'))
mod = json.load(open('data/flight_logs/moderate_flight_log.json'))
emerg = json.load(open('data/flight_logs/emergency_flight_log.json'))

with open('data/evaluation_summary.csv') as f:
    eval_rows = list(csv.DictReader(f))

js_header = """/**
 * demo_ui.js — EcoPilot Phase 2 Avionics & Flight Log Replay Telemetry
 * Provides flight log data replay, altitude chart rendering, mission status tracking,
 * and dynamic benchmark visualization from empirical evaluation results.
 */

// Embedded Phase 2 Telemetry Flight Logs
const FLIGHT_LOGS = {
  calm: """ + json.dumps(calm) + """,
  moderate: """ + json.dumps(mod) + """,
  emergency: """ + json.dumps(emerg) + """
};

// Embedded Empirical Benchmark Summary from evaluation_summary.csv
const EVALUATION_SUMMARY = """ + json.dumps(eval_rows) + """;

// Replay State
let activeMode = 'live'; // 'live' | 'replay' | 'eval' | 'specs'
let activeLogKey = 'calm';
let replayStep = 0;
let isReplayPlaying = false;
let replayTimer = null;
let replaySpeed = 1;

// Latest Safety Intervention State
let lastSafetyEvent = {
  step: 0,
  trigger: 'None (Nominal Flight)',
  originalAction: 'None',
  overriddenAction: 'None',
  recoveryMode: 'None',
  active: false
};

// ── Tab Management ──────────────────────────────────────────────────────────
function switchTab(mode) {
  activeMode = mode;
  const tabs = ['live', 'replay', 'eval', 'specs'];
  tabs.forEach(t => {
    const btn = document.getElementById('tabBtn' + t.charAt(0).toUpperCase() + t.slice(1));
    const section = document.getElementById('section' + t.charAt(0).toUpperCase() + t.slice(1));
    if (btn) {
      if (t === mode) {
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
      } else {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
      }
    }
    if (section) {
      section.style.display = (t === mode) ? 'block' : 'none';
    }
  });

  const modeLabel = document.getElementById('activeModeLabel');
  if (modeLabel) {
    if (mode === 'live') modeLabel.textContent = 'LIVE SIMULATOR';
    else if (mode === 'replay') modeLabel.textContent = 'LOG REPLAY';
    else if (mode === 'eval') modeLabel.textContent = 'BENCHMARK EVAL';
    else if (mode === 'specs') modeLabel.textContent = 'MODEL SPECS';
  }

  // Adjust center/left layout visibility
  const liveControls = document.getElementById('liveAtmosphericControls');
  const replayControls = document.getElementById('replayScenarioControls');
  const liveBtnRow = document.getElementById('liveBtnRow');
  const replayBtnRow = document.getElementById('replayBtnRow');
  const canvasCard = document.getElementById('canvasCard');
  const rightTelemetryCard = document.getElementById('rightTelemetryCard');

  if (mode === 'live') {
    if (liveControls) liveControls.style.display = 'block';
    if (replayControls) replayControls.style.display = 'none';
    if (liveBtnRow) liveBtnRow.style.display = 'flex';
    if (replayBtnRow) replayBtnRow.style.display = 'none';
    if (canvasCard) canvasCard.style.display = 'flex';
    if (rightTelemetryCard) rightTelemetryCard.style.display = 'flex';
    pauseReplay();
    if (typeof drawScene === 'function') drawScene();
  } else if (mode === 'replay') {
    if (liveControls) liveControls.style.display = 'none';
    if (replayControls) replayControls.style.display = 'block';
    if (liveBtnRow) liveBtnRow.style.display = 'none';
    if (replayBtnRow) replayBtnRow.style.display = 'flex';
    if (canvasCard) canvasCard.style.display = 'flex';
    if (rightTelemetryCard) rightTelemetryCard.style.display = 'flex';
    if (typeof stopFlight === 'function') stopFlight();
    loadFlightLog(activeLogKey);
  } else {
    // Benchmark or Specs view
    if (canvasCard) canvasCard.style.display = 'none';
    if (rightTelemetryCard) rightTelemetryCard.style.display = 'none';
    if (liveControls) liveControls.style.display = 'none';
    if (replayControls) replayControls.style.display = 'none';
    pauseReplay();
    if (typeof stopFlight === 'function') stopFlight();
  }
}

// ── Flight Log Replay Engine ────────────────────────────────────────────────
function loadFlightLog(logKey) {
  activeLogKey = logKey;
  const logData = FLIGHT_LOGS[logKey];
  if (!logData) return;

  replayStep = 0;
  pauseReplay();

  // Update scenario selector buttons styling
  ['calm', 'moderate', 'emergency'].forEach(k => {
    const b = document.getElementById('btnLog_' + k);
    if (b) {
      if (k === logKey) {
        b.classList.add('primary');
      } else {
        b.classList.remove('primary');
      }
    }
  });

  // Metadata card
  const metaBox = document.getElementById('replayMetaBox');
  if (metaBox) {
    metaBox.innerHTML = `
      <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; font-size:0.75rem;">
        <div><strong>Scenario:</strong> ${logData.scenario} (Seed ${logData.seed})</div>
        <div><strong>Outcome:</strong> <span class="status-badge ${getOutcomeClass(logData.terminal_outcome)}">${logData.terminal_outcome.toUpperCase()}</span></div>
        <div><strong>Steps:</strong> ${logData.total_steps} (${logData.simulated_flight_time_s}s)</div>
        <div><strong>Energy:</strong> ${logData.energy_consumed_wh.toFixed(2)} Wh</div>
        <div><strong>End SoC:</strong> ${logData.battery_end_soc_pct.toFixed(1)}%</div>
        <div><strong>Start:</strong> (${logData.telemetry_history[0].position_3d[0].toFixed(1)}, ${logData.telemetry_history[0].position_3d[1].toFixed(1)})</div>
      </div>
    `;
  }

  // Scrubber setup
  const scrubber = document.getElementById('replayScrubber');
  if (scrubber) {
    scrubber.min = 0;
    scrubber.max = logData.telemetry_history.length - 1;
    scrubber.value = 0;
  }

  applyReplayStep(0);
}

function getOutcomeClass(outcome) {
  if (outcome === 'success') return 'status-nominal';
  if (outcome === 'safe_rth') return 'status-override';
  if (outcome === 'controlled_landing') return 'status-warn';
  if (outcome === 'timeout') return 'status-warn';
  return 'status-override';
}

function applyReplayStep(idx) {
  const logData = FLIGHT_LOGS[activeLogKey];
  if (!logData || !logData.telemetry_history[idx]) return;

  replayStep = idx;
  const rec = logData.telemetry_history[idx];

  // Update scrubber and step counters
  const scrubber = document.getElementById('replayScrubber');
  if (scrubber) scrubber.value = idx;

  const stepCountEl = document.getElementById('stepCounter');
  if (stepCountEl) stepCountEl.textContent = `Step: ${rec.step} / ${logData.total_steps}`;

  const replayStepLabel = document.getElementById('replayStepLabel');
  if (replayStepLabel) replayStepLabel.textContent = `Step ${rec.step} / ${logData.total_steps} (${rec.elapsed_time_s.toFixed(1)}s)`;

  // Clock
  const clockEl = document.getElementById('missionClock');
  if (clockEl) clockEl.textContent = `T+${rec.elapsed_time_s.toFixed(1)}s`;

  // Continuous drone coordinates
  const r = rec.position_3d[0];
  const c = rec.position_3d[1];
  const altNorm = rec.position_3d[2];

  const posEl = document.getElementById('valDronePos');
  if (posEl) posEl.textContent = `(${r.toFixed(1)}, ${c.toFixed(1)})`;

  // Flight dynamics metrics
  const altMeters = 780.8 + altNorm * (827.5 - 780.8);
  const clearanceM = rec.terrain_clearance_norm * (827.5 - 780.8);

  const altEl = document.getElementById('valAltitude');
  if (altEl) altEl.textContent = `${altMeters.toFixed(1)} m ASL`;

  const clearEl = document.getElementById('valClearance');
  if (clearEl) {
    let tag = 'SAFE';
    let color = 'var(--accent-green)';
    if (clearanceM < 15.0) {
      tag = 'CRITICAL';
      color = 'var(--accent-red)';
    } else if (clearanceM < 25.0) {
      tag = 'CAUTION';
      color = 'var(--accent-yellow)';
    }
    clearEl.innerHTML = `<span style="color:${color}">${clearanceM.toFixed(1)} m [${tag}]</span>`;
  }

  const airEl = document.getElementById('valAirspeed');
  if (airEl) airEl.textContent = `${rec.airspeed_mps.toFixed(1)} m/s`;

  const gndEl = document.getElementById('valGroundSpeed');
  if (gndEl) gndEl.textContent = `${rec.ground_speed_mps.toFixed(1)} m/s`;

  // Battery & Energy
  const batEl = document.getElementById('valBattery');
  if (batEl) batEl.textContent = `${rec.battery_soc_pct.toFixed(1)}%`;

  const batBar = document.getElementById('batteryBar');
  if (batBar) {
    batBar.style.width = `${rec.battery_soc_pct}%`;
    if (rec.battery_soc_pct > 50) batBar.style.background = 'var(--accent-green)';
    else if (rec.battery_soc_pct > 20) batBar.style.background = 'var(--accent-yellow)';
    else batBar.style.background = 'var(--accent-red)';
  }

  const nrgEl = document.getElementById('valEnergy');
  if (nrgEl) nrgEl.textContent = `${rec.energy_consumed_wh.toFixed(2)} Wh`;

  const pwrEl = document.getElementById('valPower');
  if (pwrEl) pwrEl.textContent = `${rec.power_watts.toFixed(0)} W`;

  // Physics display updates
  const rEnvEl = document.getElementById('valREnv');
  if (rEnvEl) {
    rEnvEl.textContent = rec.r_env.toFixed(3);
    if (rec.r_env > 0.85) rEnvEl.style.color = 'var(--accent-red)';
    else if (rec.r_env > 0.45) rEnvEl.style.color = 'var(--accent-yellow)';
    else rEnvEl.style.color = 'var(--accent-green)';
  }

  const riskBar = document.getElementById('riskBar');
  if (riskBar) {
    const pct = Math.min(100, Math.round(rec.r_env * 100));
    riskBar.style.width = `${pct}%`;
    if (rec.r_env > 0.85) riskBar.style.background = 'var(--accent-red)';
    else if (rec.r_env > 0.45) riskBar.style.background = 'var(--accent-yellow)';
    else riskBar.style.background = 'var(--accent-green)';
  }

  const qEl = document.getElementById('valQ');
  if (qEl) qEl.textContent = `${rec.dynamic_pressure_pa.toFixed(1)} Pa`;

  // Mission State & Safety Badge
  const stateBadge = document.getElementById('missionState');
  const safetyBadge = document.getElementById('safetyBadge');
  const isSafetyIntervention = rec.r_env > 0.85 || rec.dynamic_pressure_pa > 120.0 || rec.outcome === 'safe_rth';

  if (isSafetyIntervention) {
    if (safetyBadge) {
      safetyBadge.className = 'status-badge status-override';
      safetyBadge.textContent = 'OVERRIDE ACTIVE';
    }
    recordSafetyEvent(rec.step, `High Risk (R_env=${rec.r_env.toFixed(2)}, q=${rec.dynamic_pressure_pa.toFixed(1)}Pa)`, 'Route to Goal', 'Execute Safe Return-to-Home', 'Safety Intercept Active');
  } else {
    if (safetyBadge) {
      safetyBadge.className = 'status-badge status-nominal';
      safetyBadge.textContent = 'ENVELOPE: NOMINAL';
    }
  }

  if (stateBadge) {
    if (rec.outcome === 'success') {
      stateBadge.className = 'chip-val status-success';
      stateBadge.textContent = 'MISSION SUCCESS';
    } else if (rec.outcome === 'safe_rth') {
      stateBadge.className = 'chip-val status-rth';
      stateBadge.textContent = 'RETURNING TO BASE';
    } else if (rec.outcome === 'timeout') {
      stateBadge.className = 'chip-val status-warn';
      stateBadge.textContent = 'MISSION TIMEOUT';
    } else if (rec.outcome === 'controlled_landing') {
      stateBadge.className = 'chip-val status-land';
      stateBadge.textContent = 'CONTROLLED LANDING';
    } else if (isSafetyIntervention) {
      stateBadge.className = 'chip-val status-hold';
      stateBadge.textContent = 'SAFETY HOLD / RTH';
    } else {
      stateBadge.className = 'chip-val status-flying';
      stateBadge.textContent = 'FLYING (NOMINAL)';
    }
  }

  // Draw Replay on Canvas
  drawReplayScene(logData, idx);

  // Render Altitude Mini-Chart
  renderAltitudeChart(logData.telemetry_history, idx);
}

function drawReplayScene(logData, currentIdx) {
  if (typeof CTX === 'undefined' || !CTX) return;

  CTX.clearRect(0, 0, CANVAS.width, CANVAS.height);

  // Draw Terrain Cells
  for (let r = 0; r < GRID_SIZE; r++) {
    for (let c = 0; c < GRID_SIZE; c++) {
      const elev = ELEV_MATRIX[r][c];
      CTX.fillStyle = getElevationColor(elev);
      CTX.fillRect(c * CELL_PX, r * CELL_PX, CELL_PX, CELL_PX);
      CTX.strokeStyle = '#ffffff08';
      CTX.strokeRect(c * CELL_PX, r * CELL_PX, CELL_PX, CELL_PX);
    }
  }

  const hist = logData.telemetry_history;

  // Planned / Full Trail (faint dashed cyan)
  CTX.beginPath();
  CTX.strokeStyle = '#38bdf844';
  CTX.lineWidth = 2;
  CTX.setLineDash([4, 4]);
  for (let i = 0; i < hist.length; i++) {
    const pt = hist[i].position_3d;
    const px = pt[1] * CELL_PX + CELL_PX / 2;
    const py = pt[0] * CELL_PX + CELL_PX / 2;
    if (i === 0) CTX.moveTo(px, py);
    else CTX.lineTo(px, py);
  }
  CTX.stroke();
  CTX.setLineDash([]);

  // Elapsed Travelled Trail (Solid cyan glow)
  CTX.beginPath();
  CTX.strokeStyle = '#38bdf8';
  CTX.lineWidth = 3;
  CTX.lineCap = 'round';
  for (let i = 0; i <= currentIdx; i++) {
    const pt = hist[i].position_3d;
    const px = pt[1] * CELL_PX + CELL_PX / 2;
    const py = pt[0] * CELL_PX + CELL_PX / 2;
    if (i === 0) CTX.moveTo(px, py);
    else CTX.lineTo(px, py);
  }
  CTX.stroke();

  // Draw Override / High Risk Markers
  for (let i = 0; i <= currentIdx; i++) {
    if (hist[i].r_env > 0.85 || hist[i].outcome === 'safe_rth') {
      const pt = hist[i].position_3d;
      const px = pt[1] * CELL_PX + CELL_PX / 2;
      const py = pt[0] * CELL_PX + CELL_PX / 2;
      CTX.fillStyle = '#ef4444';
      CTX.beginPath();
      CTX.arc(px, py, 4, 0, 2 * Math.PI);
      CTX.fill();
    }
  }

  // Draw Home / Start Beacon
  const startPt = hist[0].position_3d;
  const sx = startPt[1] * CELL_PX + CELL_PX / 2;
  const sy = startPt[0] * CELL_PX + CELL_PX / 2;
  CTX.strokeStyle = '#38bdf8';
  CTX.lineWidth = 2;
  CTX.beginPath();
  CTX.arc(sx, sy, 8, 0, 2 * Math.PI);
  CTX.stroke();

  // Draw Goal Beacon (Target)
  const lastPt = hist[hist.length - 1].position_3d;
  const gx = lastPt[1] * CELL_PX + CELL_PX / 2;
  const gy = lastPt[0] * CELL_PX + CELL_PX / 2;
  CTX.strokeStyle = '#22c55e';
  CTX.lineWidth = 2;
  CTX.beginPath();
  CTX.arc(gx, gy, 10, 0, 2 * Math.PI);
  CTX.stroke();
  CTX.beginPath();
  CTX.arc(gx, gy, 4, 0, 2 * Math.PI);
  CTX.fillStyle = '#22c55e';
  CTX.fill();

  // Draw Current Drone Position & Heading
  const curr = hist[currentIdx];
  const dx = curr.position_3d[1] * CELL_PX + CELL_PX / 2;
  const dy = curr.position_3d[0] * CELL_PX + CELL_PX / 2;

  CTX.save();
  CTX.translate(dx, dy);

  // Pulsing halo
  CTX.beginPath();
  CTX.arc(0, 0, 14, 0, 2 * Math.PI);
  CTX.fillStyle = '#38bdf833';
  CTX.fill();

  // Heading vector arrow
  if (curr.heading_rad !== undefined) {
    CTX.rotate(curr.heading_rad);
    CTX.strokeStyle = '#ffffff';
    CTX.lineWidth = 2;
    CTX.beginPath();
    CTX.moveTo(0, 0);
    CTX.lineTo(14, 0);
    CTX.lineTo(10, -4);
    CTX.moveTo(14, 0);
    CTX.lineTo(10, 4);
    CTX.stroke();
  }

  // Drone quadcopter body
  CTX.fillStyle = '#38bdf8';
  CTX.beginPath();
  CTX.arc(0, 0, 5, 0, 2 * Math.PI);
  CTX.fill();
  CTX.strokeStyle = '#ffffff';
  CTX.lineWidth = 1.5;
  CTX.stroke();

  CTX.restore();

  // Wind direction compass in top-right
  if (typeof drawWindIndicator === 'function') drawWindIndicator();
}

// ── Replay Playback Controls ────────────────────────────────────────────────
function toggleReplayPlay() {
  if (isReplayPlaying) {
    pauseReplay();
  } else {
    playReplay();
  }
}

function playReplay() {
  const logData = FLIGHT_LOGS[activeLogKey];
  if (!logData) return;

  if (replayStep >= logData.telemetry_history.length - 1) {
    replayStep = 0;
  }

  isReplayPlaying = true;
  const btn = document.getElementById('btnReplayPlay');
  if (btn) {
    btn.textContent = '⏸ Pause';
    btn.classList.add('danger');
    btn.classList.remove('primary');
  }

  clearInterval(replayTimer);
  const intervalMs = Math.max(50, 200 / replaySpeed);
  replayTimer = setInterval(() => {
    if (replayStep < logData.telemetry_history.length - 1) {
      applyReplayStep(replayStep + 1);
    } else {
      pauseReplay();
    }
  }, intervalMs);
}

function pauseReplay() {
  isReplayPlaying = false;
  clearInterval(replayTimer);
  const btn = document.getElementById('btnReplayPlay');
  if (btn) {
    btn.textContent = '▶ Play';
    btn.classList.remove('danger');
    btn.classList.add('primary');
  }
}

function stepReplay(delta) {
  pauseReplay();
  const logData = FLIGHT_LOGS[activeLogKey];
  if (!logData) return;
  const next = Math.max(0, Math.min(logData.telemetry_history.length - 1, replayStep + delta));
  applyReplayStep(next);
}

function setReplaySpeed(spd) {
  replaySpeed = spd;
  ['1', '2', '5'].forEach(s => {
    const b = document.getElementById('btnSpeed_' + s);
    if (b) {
      if (parseInt(s) === spd) b.classList.add('primary');
      else b.classList.remove('primary');
    }
  });
  if (isReplayPlaying) {
    playReplay();
  }
}

// ── SVG Mini Altitude Profile Chart ─────────────────────────────────────────
function renderAltitudeChart(history, currentStepIdx) {
  const svg = document.getElementById('altitudeSvg');
  if (!svg || !history || history.length === 0) return;

  const width = 576;
  const height = 90;
  const padding = { top: 10, bottom: 20, left: 38, right: 15 };
  const plotW = width - padding.left - padding.right;
  const plotH = height - padding.top - padding.bottom;

  const totalSteps = history.length - 1 || 1;

  const minASL = 775.0;
  const maxASL = 835.0;

  let altPath = '';
  let groundPath = '';
  let groundArea = `M ${padding.left} ${height - padding.bottom} `;

  history.forEach((h, i) => {
    const x = padding.left + (i / totalSteps) * plotW;

    // Drone Altitude ASL
    const alt = 780.8 + h.position_3d[2] * (827.5 - 780.8);
    const yAlt = padding.top + plotH * (1 - (alt - minASL) / (maxASL - minASL));

    // Ground elevation under drone
    const groundAlt = alt - (h.terrain_clearance_norm * (827.5 - 780.8));
    const yGround = padding.top + plotH * (1 - (groundAlt - minASL) / (maxASL - minASL));

    if (i === 0) {
      altPath += `M ${x.toFixed(1)} ${yAlt.toFixed(1)} `;
      groundPath += `M ${x.toFixed(1)} ${yGround.toFixed(1)} `;
    } else {
      altPath += `L ${x.toFixed(1)} ${yAlt.toFixed(1)} `;
      groundPath += `L ${x.toFixed(1)} ${yGround.toFixed(1)} `;
    }
    groundArea += `L ${x.toFixed(1)} ${yGround.toFixed(1)} `;
  });

  groundArea += `L ${padding.left + plotW} ${height - padding.bottom} Z`;

  const cursorX = padding.left + (currentStepIdx / totalSteps) * plotW;
  const currH = history[currentStepIdx];
  const currAlt = 780.8 + currH.position_3d[2] * (827.5 - 780.8);
  const cursorY = padding.top + plotH * (1 - (currAlt - minASL) / (maxASL - minASL));

  svg.innerHTML = `
    <!-- Background Guidelines -->
    <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left + plotW}" y2="${padding.top}" stroke="#334155" stroke-dasharray="2,4" />
    <line x1="${padding.left}" y1="${padding.top + plotH/2}" x2="${padding.left + plotW}" y2="${padding.top + plotH/2}" stroke="#334155" stroke-dasharray="2,4" />
    <line x1="${padding.left}" y1="${height - padding.bottom}" x2="${padding.left + plotW}" y2="${height - padding.bottom}" stroke="#475569" />

    <!-- Y-Axis Labels -->
    <text x="${padding.left - 4}" y="${padding.top + 4}" fill="#94a3b8" font-size="8" text-anchor="end">835m</text>
    <text x="${padding.left - 4}" y="${padding.top + plotH/2 + 3}" fill="#94a3b8" font-size="8" text-anchor="end">805m</text>
    <text x="${padding.left - 4}" y="${height - padding.bottom}" fill="#94a3b8" font-size="8" text-anchor="end">775m</text>

    <!-- Ground Terrain Silhouette Area -->
    <path d="${groundArea}" fill="#1e293b" />
    <path d="${groundPath}" fill="none" stroke="#a16207" stroke-width="1.5" />

    <!-- Drone Flight Altitude Line -->
    <path d="${altPath}" fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" />

    <!-- Scrub Cursor -->
    <line x1="${cursorX.toFixed(1)}" y1="${padding.top}" x2="${cursorX.toFixed(1)}" y2="${height - padding.bottom}" stroke="#f59e0b" stroke-width="1.5" />
    <circle cx="${cursorX.toFixed(1)}" cy="${cursorY.toFixed(1)}" r="4" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />

    <!-- Legend & Labels -->
    <text x="${padding.left + 5}" y="${padding.top + 10}" fill="#38bdf8" font-size="8" font-weight="bold">Altitude: ${currAlt.toFixed(1)}m</text>
    <text x="${padding.left + 110}" y="${padding.top + 10}" fill="#a16207" font-size="8">Ground: ${(currAlt - currH.terrain_clearance_norm * (827.5 - 780.8)).toFixed(1)}m</text>
    <text x="${padding.left}" y="${height - 4}" fill="#64748b" font-size="8">T=0s</text>
    <text x="${padding.left + plotW}" y="${height - 4}" fill="#64748b" font-size="8" text-anchor="end">T=${currH.elapsed_time_s.toFixed(0)}s</text>
    <text x="${padding.left + plotW/2}" y="${height - 4}" fill="#64748b" font-size="8" text-anchor="middle">Altitude & Terrain Profile (ASL)</text>
  `;
}

// ── Safety Event Card ───────────────────────────────────────────────────────
function recordSafetyEvent(step, trigger, originalAction, overriddenAction, recoveryMode) {
  lastSafetyEvent = { step, trigger, originalAction, overriddenAction, recoveryMode, active: true };
  const card = document.getElementById('safetyEventCard');
  if (!card) return;

  const content = document.getElementById('safetyEventContent');
  if (content) {
    content.innerHTML = `
      <div style="font-size:0.75rem; line-height:1.4;">
        <div style="color:var(--accent-red); font-weight:600; margin-bottom:2px;">⚠️ Step T+${step}: ${trigger}</div>
        <div style="color:var(--text-dim);"><strong>Intended Action:</strong> ${originalAction}</div>
        <div style="color:var(--accent-yellow);"><strong>Overridden To:</strong> ${overriddenAction}</div>
        <div style="color:var(--accent-blue);"><strong>Failsafe Mode:</strong> ${recoveryMode}</div>
      </div>
    `;
  }
}

// ── Multi-Agent Evaluation Benchmark Table & Charts ─────────────────────────
function renderBenchmarkTable() {
  const container = document.getElementById('benchmarkTableContainer');
  if (!container) return;

  let html = `
    <table class="eval-table" role="table" aria-label="Empirical Evaluation Results">
      <thead>
        <tr>
          <th>Condition</th>
          <th>Agent Architecture</th>
          <th>Trials</th>
          <th>Success</th>
          <th>Safe RTH</th>
          <th>Controlled Land</th>
          <th>Crash</th>
          <th>Timeout</th>
          <th>Mean Energy</th>
          <th>Interventions</th>
        </tr>
      </thead>
      <tbody>
  `;

  EVALUATION_SUMMARY.forEach(row => {
    const isAdaptive = row.agent === 'AdaptiveAgent';
    const rowClass = isAdaptive ? 'row-adaptive' : '';

    html += `
      <tr class="${rowClass}">
        <td><strong>${row.bucket}</strong></td>
        <td>${row.agent}</td>
        <td>${row.trials}</td>
        <td><span class="badge-rate ${parseFloat(row.success_rate_pct) > 50 ? 'rate-good' : 'rate-low'}">${row.success_rate_pct}%</span></td>
        <td><span class="badge-rate ${parseFloat(row.safe_rth_rate_pct) > 0 ? 'rate-rth' : ''}">${row.safe_rth_rate_pct}%</span></td>
        <td>${row.controlled_landing_rate_pct}%</td>
        <td><span class="badge-rate rate-zero-crash">${row.crash_rate_pct}%</span></td>
        <td>${row.timeout_rate_pct}%</td>
        <td><strong>${parseFloat(row.mean_energy_wh).toFixed(2)} Wh</strong></td>
        <td>${parseFloat(row.mean_interventions).toFixed(1)}</td>
      </tr>
    `;
  });

  html += `
      </tbody>
    </table>
  `;

  container.innerHTML = html;
}

// Populate UI on load
document.addEventListener('DOMContentLoaded', () => {
  renderBenchmarkTable();
  // Also populate initial altitude chart with calm log
  if (FLIGHT_LOGS.calm) {
    renderAltitudeChart(FLIGHT_LOGS.calm.telemetry_history, 0);
  }
});
"""

with open('demo_ui.js', 'w') as f:
    f.write(js_header)

print('demo_ui.js generated successfully!')
