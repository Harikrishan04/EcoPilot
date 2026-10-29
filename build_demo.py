"""
build_demo.py — Compiles self-contained EcoPilot in-browser simulation demo.
"""

import json
import os

with open("terrain/terrain.json") as f:
    terrain_data = json.load(f)

with open("data/q_table_adaptive.json") as f:
    q_adaptive_data = json.load(f)

with open("data/q_table_baseline.json") as f:
    q_baseline_data = json.load(f)

html_template = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>EcoPilot — Autonomous Drone RL Simulation (Mantripukhri, Manipur)</title>
  <style>
    :root {
      --bg-dark: #0f172a;
      --bg-card: #1e293b;
      --border: #334155;
      --accent-blue: #38bdf8;
      --accent-green: #22c55e;
      --accent-yellow: #eab308;
      --accent-red: #ef4444;
      --text-main: #f8fafc;
      --text-dim: #94a3b8;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      padding: 16px;
      line-height: 1.4;
    }
    header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      margin-bottom: 16px;
      border-bottom: 1px solid var(--border);
    }
    .title-group h1 {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--accent-blue);
      letter-spacing: -0.5px;
    }
    .title-group p {
      font-size: 0.85rem;
      color: var(--text-dim);
    }
    .badge-bar {
      display: flex;
      gap: 8px;
    }
    .badge {
      font-size: 0.75rem;
      padding: 4px 8px;
      border-radius: 4px;
      background: #0284c722;
      color: var(--accent-blue);
      border: 1px solid #0284c744;
    }
    .layout-grid {
      display: grid;
      grid-template-columns: 320px 1fr 340px;
      gap: 16px;
      min-height: calc(100vh - 100px);
    }
    @media (max-width: 1200px) {
      .layout-grid { grid-template-columns: 1fr; }
    }
    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    .card h2 {
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--text-main);
      border-bottom: 1px solid var(--border);
      padding-bottom: 6px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .slider-group {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }
    .slider-label {
      display: flex;
      justify-content: space-between;
      font-size: 0.8rem;
      color: var(--text-dim);
    }
    .slider-label span.val {
      color: var(--accent-blue);
      font-weight: 600;
    }
    input[type=range] {
      width: 100%;
      accent-color: var(--accent-blue);
    }
    .btn-row {
      display: flex;
      gap: 8px;
    }
    button {
      flex: 1;
      padding: 8px 12px;
      background: #334155;
      color: var(--text-main);
      border: 1px solid #475569;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    button:hover { background: #475569; }
    button.primary {
      background: #0284c7;
      border-color: #38bdf8;
    }
    button.primary:hover { background: #0369a1; }
    button.danger {
      background: #dc2626;
      border-color: #f87171;
    }
    .metric-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
    .metric-box {
      background: #0f172a88;
      border: 1px solid var(--border);
      padding: 8px;
      border-radius: 6px;
    }
    .metric-box .label {
      font-size: 0.7rem;
      color: var(--text-dim);
    }
    .metric-box .value {
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--text-main);
    }
    .risk-meter {
      height: 8px;
      border-radius: 4px;
      background: #334155;
      overflow: hidden;
      margin-top: 4px;
    }
    .risk-bar {
      height: 100%;
      width: 0%;
      background: var(--accent-green);
      transition: width 0.2s, background 0.2s;
    }
    .canvas-container {
      position: relative;
      background: #000;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      justify-content: center;
      align-items: center;
      border: 1px solid var(--border);
      flex: 1;
      min-height: 520px;
    }
    canvas {
      display: block;
      cursor: crosshair;
    }
    .overlay-info {
      position: absolute;
      top: 12px;
      left: 12px;
      background: #0f172acc;
      backdrop-filter: blur(4px);
      border: 1px solid var(--border);
      padding: 6px 12px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-family: monospace;
      pointer-events: none;
    }
    .legend {
      position: absolute;
      bottom: 12px;
      right: 12px;
      background: #0f172acc;
      border: 1px solid var(--border);
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 0.7rem;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .ramp {
      width: 80px;
      height: 8px;
      border-radius: 2px;
      background: linear-gradient(to right, #4d8050, #96b464, #c8b482, #b48c5a, #dcd2c8);
    }
    .log-box {
      background: #0f172a;
      border: 1px solid var(--border);
      border-radius: 6px;
      height: 180px;
      overflow-y: auto;
      padding: 8px;
      font-family: monospace;
      font-size: 0.75rem;
      color: #cbd5e1;
      display: flex;
      flex-direction: column-reverse;
    }
    .log-entry { margin-bottom: 2px; }
    .log-warn { color: var(--accent-yellow); }
    .log-crit { color: var(--accent-red); font-weight: bold; }
    .log-success { color: var(--accent-green); font-weight: bold; }
    .status-badge {
      display: inline-block;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 0.7rem;
      font-weight: 600;
    }
    .status-nominal { background: #14532d; color: #86efac; border: 1px solid #22c55e44; }
    .status-override { background: #7f1d1d; color: #fca5a5; border: 1px solid #ef444444; }
  </style>
</head>
<body>

  <header>
    <div class="title-group">
      <h1>EcoPilot — Autonomous Drone Simulation</h1>
      <p>Tabular Q-Learning Navigation with Live Atmospheric Physics · Mantripukhri (IIIT Manipur Campus)</p>
    </div>
    <div class="badge-bar">
      <span class="badge">SRTM GL1 (30m) Real Terrain</span>
      <span class="badge">Discretized R_env Risk</span>
      <span class="badge">Independent Safety Envelope</span>
    </div>
  </header>

  <div class="layout-grid">

    <!-- LEFT PANEL: Atmospheric Physics & Sliders -->
    <div class="card">
      <h2>
        <span>Atmospheric Controls</span>
        <span id="safetyBadge" class="status-badge status-nominal">ENVELOPE: NOMINAL</span>
      </h2>

      <!-- Presets -->
      <div class="btn-row">
        <button onclick="setWeatherPreset('calm')">Calm Morning</button>
        <button onclick="setWeatherPreset('moderate')">Mod. Breeze</button>
        <button onclick="setWeatherPreset('severe')">Severe Squall</button>
      </div>

      <!-- Sliders -->
      <div class="slider-group">
        <div class="slider-label"><span>Wind Speed (|W|)</span><span class="val" id="valWind">3.0 m/s</span></div>
        <input type="range" id="sliderWind" min="0" max="15" step="0.5" value="3.0" oninput="updatePhysics()">
      </div>

      <div class="slider-group">
        <div class="slider-label"><span>Wind Azimuth (θ_w)</span><span class="val" id="valDir">140° (SE)</span></div>
        <input type="range" id="sliderDir" min="0" max="360" step="10" value="140" oninput="updatePhysics()">
      </div>

      <div class="slider-group">
        <div class="slider-label"><span>Relative Humidity (RH)</span><span class="val" id="valRH">55%</span></div>
        <input type="range" id="sliderRH" min="20" max="100" step="5" value="55" oninput="updatePhysics()">
      </div>

      <div class="slider-group">
        <div class="slider-label"><span>Barometric Trend (dP/dt)</span><span class="val" id="valDP">0.0 hPa/h</span></div>
        <input type="range" id="sliderDP" min="-3" max="3" step="0.2" value="0.0" oninput="updatePhysics()">
      </div>

      <!-- Live Physics Metrics -->
      <div class="metric-grid">
        <div class="metric-box">
          <div class="label">Air Density (ρ)</div>
          <div class="value" id="valRho">1.06 kg/m³</div>
        </div>
        <div class="metric-box">
          <div class="label">Thrust Factor (k_th)</div>
          <div class="value" id="valKThrust">1.15×</div>
        </div>
        <div class="metric-box">
          <div class="label">Dyn Pressure (q)</div>
          <div class="value" id="valQ">48.2 Pa</div>
        </div>
        <div class="metric-box">
          <div class="label">Adaptive Penalty (λ)</div>
          <div class="value" id="valLambda">1.25×</div>
        </div>
      </div>

      <!-- Environmental Risk Score Gauge -->
      <div class="metric-box" style="margin-top: 4px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
          <span class="label">Composite Risk (R_env)</span>
          <span class="value" id="valREnv" style="font-size:1.1rem; color:var(--accent-green);">0.18</span>
        </div>
        <div class="risk-meter">
          <div id="riskBar" class="risk-bar" style="width: 18%;"></div>
        </div>
      </div>

      <!-- Live Ground Reference Info -->
      <div style="font-size: 0.72rem; color: var(--text-dim); line-height: 1.3; border-top: 1px solid var(--border); padding-top: 8px;">
        📍 <strong>Local Reference</strong>: Mantripukhri Valley Floor (~780m ASL). Dry air is heavier than humid air (T_v correction active). Hard safety override triggers if R_env > 0.85 or q > 120 Pa.
      </div>
    </div>

    <!-- CENTER PANEL: Real Terrain Simulation Canvas -->
    <div class="card" style="padding: 12px;">
      <h2>
        <span>Real Terrain Simulation (24×24 Grid)</span>
        <span style="font-size:0.75rem; color:var(--text-dim);" id="stepCounter">Step: 0 / 100</span>
      </h2>

      <div class="canvas-container">
        <canvas id="simCanvas" width="576" height="576"></canvas>
        <div id="coordOverlay" class="overlay-info">Hover over terrain cell...</div>
        <div class="legend">
          <span>780m</span>
          <div class="ramp"></div>
          <span>828m</span>
        </div>
      </div>

      <div class="btn-row" style="margin-top: 4px;">
        <button id="btnPlay" class="primary" onclick="toggleFlight()">▶ Start Mission</button>
        <button onclick="resetMission(true)">🎲 New Random Route</button>
        <button onclick="resetMission(false)">⏹ Reset Current</button>
      </div>
    </div>

    <!-- RIGHT PANEL: Agent Settings, Policy Playback & Log -->
    <div class="card">
      <h2>Policy & Safety Controls</h2>

      <div class="slider-group">
        <label class="slider-label"><span>Active Agent</span></label>
        <select id="agentSelect" style="background:#334155; color:white; padding:6px; border-radius:4px; border:1px solid #475569;" onchange="updateAgentSelection()">
          <option value="adaptive">Adaptive Q-Agent (R_env-Aware Policy)</option>
          <option value="baseline">Static Baseline Agent (Unconditioned)</option>
        </select>
      </div>

      <div style="display:flex; justify-content:space-between; align-items:center; background:#0f172a; padding:8px 12px; border-radius:6px; border:1px solid var(--border);">
        <span style="font-size:0.8rem; font-weight:600;">Hard Safety Envelope</span>
        <input type="checkbox" id="checkSafety" checked style="width:18px; height:18px; accent-color:var(--accent-blue);" onchange="updatePhysics()">
      </div>

      <!-- Telemetry Box -->
      <div class="metric-grid">
        <div class="metric-box">
          <div class="label">Drone Position</div>
          <div class="value" id="valDronePos" style="font-size:0.95rem;">(2, 2)</div>
        </div>
        <div class="metric-box">
          <div class="label">Goal Target</div>
          <div class="value" id="valGoalPos" style="font-size:0.95rem;">(20, 20)</div>
        </div>
        <div class="metric-box">
          <div class="label">Distance to Goal</div>
          <div class="value" id="valDist" style="font-size:0.95rem;">25.4 cells</div>
        </div>
        <div class="metric-box">
          <div class="label">Safety Overrides</div>
          <div class="value" id="valOverrides" style="font-size:0.95rem; color:var(--accent-yellow);">0</div>
        </div>
      </div>

      <!-- Live Flight Event Log -->
      <div style="font-size:0.8rem; font-weight:600; margin-top:2px;">Mission Event Log</div>
      <div id="logBox" class="log-box"></div>

      <!-- Phase 5 Evaluation Benchmark Reference -->
      <div style="border-top: 1px solid var(--border); padding-top: 8px;">
        <div style="font-size:0.75rem; color:var(--text-dim); margin-bottom:4px;">Benchmark Crash Rate in Severe Weather:</div>
        <div style="display:flex; justify-content:space-between; font-size:0.8rem;">
          <span style="color:var(--accent-blue); font-weight:600;">Adaptive + Safety: 0.0%</span>
          <span style="color:var(--accent-red); font-weight:600;">Static Baseline: 87.0%</span>
        </div>
      </div>
    </div>

  </div>

  <script>
    // Embedded Data from Phase 1 and Phase 3
    const TERRAIN_DATA = __TERRAIN_DATA_PLACEHOLDER__;
    const Q_ADAPTIVE = __Q_ADAPTIVE_PLACEHOLDER__;
    const Q_BASELINE = __Q_BASELINE_PLACEHOLDER__;

    // Physical Constants
    const RD = 287.05;
    const RHO_0 = 1.225;
    const KELVIN_OFFSET = 273.15;
    const Q_CRITICAL = 120.0;
    const R_CRITICAL = 0.85;
    const CRUISE_ALTITUDE = 0.40;

    // Grid Dimensions
    const GRID_SIZE = TERRAIN_DATA.grid_size;
    const ELEV_MATRIX = TERRAIN_DATA.values;
    const CANVAS = document.getElementById("simCanvas");
    const CTX = CANVAS.getContext("2d");
    const CELL_PX = CANVAS.width / GRID_SIZE;

    // 8-Directional Movements
    const ACTIONS = [
      [-1, 0],   // 0: N
      [-1, 1],   // 1: NE
      [0, 1],    // 2: E
      [1, 1],    // 3: SE
      [1, 0],    // 4: S
      [1, -1],   // 5: SW
      [0, -1],   // 6: W
      [-1, -1]   // 7: NW
    ];
    const ACTION_NAMES = ["North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"];

    // Flight State
    let dronePos = { r: 2, c: 2 };
    let homePos = { r: 2, c: 2 };
    let goalPos = { r: 20, c: 20 };
    let flightTrail = [];
    let overrideMarkers = [];
    let isFlying = false;
    let stepCount = 0;
    let overrideCount = 0;
    let flightTimer = null;

    // Physics State
    let currentREnv = 0.2;
    let currentRho = 1.06;
    let currentLambda = 1.25;
    let currentQ = 45.0;

    // ── 1. Terrain Colormap Ramping ──────────────────────────────────────────
    function getElevationColor(normH) {
      // 0.0 (valley green) -> 0.3 (tan) -> 0.7 (mountain brown) -> 1.0 (ridge cream)
      if (normH < 0.25) {
        const t = normH / 0.25;
        const r = Math.round(77 + t * (150 - 77));
        const g = Math.round(128 + t * (180 - 128));
        const b = Math.round(80 + t * (100 - 80));
        return `rgb(${r}, ${g}, ${b})`;
      } else if (normH < 0.60) {
        const t = (normH - 0.25) / 0.35;
        const r = Math.round(150 + t * (180 - 150));
        const g = Math.round(180 + t * (140 - 180));
        const b = Math.round(100 + t * (90 - 100));
        return `rgb(${r}, ${g}, ${b})`;
      } else {
        const t = (normH - 0.60) / 0.40;
        const r = Math.round(180 + t * (220 - 180));
        const g = Math.round(140 + t * (210 - 140));
        const b = Math.round(90 + t * (200 - 90));
        return `rgb(${r}, ${g}, ${b})`;
      }
    }

    // ── 2. Atmospheric Physics Calculations ─────────────────────────────────
    function updatePhysics() {
      const windSpeed = parseFloat(document.getElementById("sliderWind").value);
      const windDirDeg = parseFloat(document.getElementById("sliderDir").value);
      const rhPct = parseFloat(document.getElementById("sliderRH").value);
      const dpDt = parseFloat(document.getElementById("sliderDP").value);

      document.getElementById("valWind").textContent = `${windSpeed.toFixed(1)} m/s`;
      document.getElementById("valDir").textContent = `${windDirDeg}°`;
      document.getElementById("valRH").textContent = `${rhPct}%`;
      document.getElementById("valDP").textContent = `${dpDt.toFixed(1)} hPa/h`;

      // Air Density with virtual temperature correction
      const tempC = 25.0;
      const tempK = tempC + KELVIN_OFFSET;
      const pressPa = 92500.0; // Mantripukhri valley pressure
      const rhFrac = rhPct / 100.0;

      // Magnus-Tetens vapor pressure
      const eSat = 610.78 * Math.exp((17.27 * tempC) / (tempC + 237.3));
      const e = rhFrac * eSat;
      const w = 0.622 * (e / (pressPa - e));
      const tv = tempK * (1.0 + 0.61 * w);
      currentRho = pressPa / (RD * tv);

      // Thrust compensation
      const kThrust = RHO_0 / currentRho;

      // Dynamic pressure (at nominal 8 m/s airspeed)
      const vRel = Math.hypot(8.0 + windSpeed * 0.7, windSpeed * 0.5);
      currentQ = 0.5 * currentRho * (vRel ** 2);

      // Composite R_env
      const normWind = Math.min(1.0, windSpeed / 15.0);
      const gustVar = (windSpeed * 0.3) ** 2;
      const normGust = Math.min(1.0, gustVar / 5.0);
      const normDP = Math.min(1.0, Math.abs(dpDt) / 3.0);
      const normRho = Math.min(1.0, Math.abs(currentRho - RHO_0) / (RHO_0 * 0.15));

      currentREnv = 0.40 * normWind + 0.25 * normGust + 0.20 * normDP + 0.15 * normRho;
      currentLambda = 1.0 * (1.0 + 3.0 * (currentREnv ** 2));

      // Update UI displays
      document.getElementById("valRho").textContent = `${currentRho.toFixed(3)} kg/m³`;
      document.getElementById("valKThrust").textContent = `${kThrust.toFixed(2)}×`;
      document.getElementById("valQ").textContent = `${currentQ.toFixed(1)} Pa`;
      document.getElementById("valLambda").textContent = `${currentLambda.toFixed(2)}×`;
      document.getElementById("valREnv").textContent = currentREnv.toFixed(3);

      const rBar = document.getElementById("riskBar");
      const rPct = Math.min(100, Math.round(currentREnv * 100));
      rBar.style.width = `${rPct}%`;
      if (currentREnv < 0.35) {
        rBar.style.background = "var(--accent-green)";
        document.getElementById("valREnv").style.color = "var(--accent-green)";
      } else if (currentREnv < 0.70) {
        rBar.style.background = "var(--accent-yellow)";
        document.getElementById("valREnv").style.color = "var(--accent-yellow)";
      } else {
        rBar.style.background = "var(--accent-red)";
        document.getElementById("valREnv").style.color = "var(--accent-red)";
      }

      // Safety Envelope Indicator
      const safetyEnabled = document.getElementById("checkSafety").checked;
      const isUnsafe = safetyEnabled && (currentREnv > R_CRITICAL || currentQ > Q_CRITICAL);
      const sBadge = document.getElementById("safetyBadge");
      if (isUnsafe) {
        sBadge.className = "status-badge status-override";
        sBadge.textContent = "OVERRIDE ACTIVE";
      } else {
        sBadge.className = "status-badge status-nominal";
        sBadge.textContent = "ENVELOPE: NOMINAL";
      }

      drawScene();
    }

    function setWeatherPreset(type) {
      if (type === 'calm') {
        document.getElementById("sliderWind").value = 2.0;
        document.getElementById("sliderDir").value = 90;
        document.getElementById("sliderRH").value = 45;
        document.getElementById("sliderDP").value = 0.1;
      } else if (type === 'moderate') {
        document.getElementById("sliderWind").value = 6.5;
        document.getElementById("sliderDir").value = 140;
        document.getElementById("sliderRH").value = 65;
        document.getElementById("sliderDP").value = -0.8;
      } else if (type === 'severe') {
        document.getElementById("sliderWind").value = 13.5;
        document.getElementById("sliderDir").value = 220;
        document.getElementById("sliderRH").value = 88;
        document.getElementById("sliderDP").value = -2.6;
      }
      updatePhysics();
    }

    // ── 3. Canvas Scene Rendering ───────────────────────────────────────────
    function drawScene() {
      CTX.clearRect(0, 0, CANVAS.width, CANVAS.height);

      // Draw Terrain Cells
      for (let r = 0; r < GRID_SIZE; r++) {
        for (let c = 0; c < GRID_SIZE; c++) {
          const elev = ELEV_MATRIX[r][c];
          CTX.fillStyle = getElevationColor(elev);
          CTX.fillRect(c * CELL_PX, r * CELL_PX, CELL_PX, CELL_PX);

          // Subtle cell gridlines
          CTX.strokeStyle = "#ffffff08";
          CTX.strokeRect(c * CELL_PX, r * CELL_PX, CELL_PX, CELL_PX);
        }
      }

      // Draw Flight Trail
      if (flightTrail.length > 1) {
        CTX.beginPath();
        CTX.strokeStyle = "#38bdf8";
        CTX.lineWidth = 3;
        CTX.lineCap = "round";
        CTX.lineJoin = "round";
        for (let i = 0; i < flightTrail.length; i++) {
          const pt = flightTrail[i];
          const px = pt.c * CELL_PX + CELL_PX / 2;
          const py = pt.r * CELL_PX + CELL_PX / 2;
          if (i === 0) CTX.moveTo(px, py);
          else CTX.lineTo(px, py);
        }
        CTX.stroke();
      }

      // Draw Override Markers
      for (const m of overrideMarkers) {
        const mx = m.c * CELL_PX + CELL_PX / 2;
        const my = m.r * CELL_PX + CELL_PX / 2;
        CTX.fillStyle = "#ef4444";
        CTX.beginPath();
        CTX.arc(mx, my, 4, 0, 2 * Math.PI);
        CTX.fill();
      }

      // Draw Goal Beacon (Target)
      const gx = goalPos.c * CELL_PX + CELL_PX / 2;
      const gy = goalPos.r * CELL_PX + CELL_PX / 2;
      CTX.strokeStyle = "#22c55e";
      CTX.lineWidth = 2;
      CTX.beginPath();
      CTX.arc(gx, gy, 10, 0, 2 * Math.PI);
      CTX.stroke();
      CTX.beginPath();
      CTX.arc(gx, gy, 4, 0, 2 * Math.PI);
      CTX.fillStyle = "#22c55e";
      CTX.fill();

      // Draw Drone Position (Icon / Diamond)
      const dx = dronePos.c * CELL_PX + CELL_PX / 2;
      const dy = dronePos.r * CELL_PX + CELL_PX / 2;
      CTX.save();
      CTX.translate(dx, dy);

      // Pulsing outer halo
      CTX.beginPath();
      CTX.arc(0, 0, 12, 0, 2 * Math.PI);
      CTX.fillStyle = "#38bdf833";
      CTX.fill();

      // Drone quadcopter shape
      CTX.fillStyle = "#38bdf8";
      CTX.beginPath();
      CTX.arc(0, 0, 5, 0, 2 * Math.PI);
      CTX.fill();
      CTX.strokeStyle = "#ffffff";
      CTX.lineWidth = 1.5;
      CTX.stroke();
      CTX.restore();

      // Draw Wind Direction Indicator (Top Right Corner)
      drawWindIndicator();
    }

    function drawWindIndicator() {
      const windSpeed = parseFloat(document.getElementById("sliderWind").value);
      const windDirDeg = parseFloat(document.getElementById("sliderDir").value);
      const cx = CANVAS.width - 36;
      const cy = 36;

      CTX.save();
      CTX.translate(cx, cy);
      CTX.beginPath();
      CTX.arc(0, 0, 22, 0, 2 * Math.PI);
      CTX.fillStyle = "#0f172acc";
      CTX.fill();
      CTX.strokeStyle = "#475569";
      CTX.stroke();

      // Wind Arrow pointing in direction wind is blowing toward (Dir + 180)
      const rad = (windDirDeg - 90) * Math.PI / 180.0;
      CTX.rotate(rad);
      CTX.strokeStyle = "#38bdf8";
      CTX.lineWidth = 2.5;
      CTX.beginPath();
      CTX.moveTo(-12, 0);
      CTX.lineTo(12, 0);
      CTX.lineTo(6, -5);
      CTX.moveTo(12, 0);
      CTX.lineTo(6, 5);
      CTX.stroke();
      CTX.restore();
    }

    // ── 4. Policy Execution & Safety Override Engine ────────────────────────
    function getDiscretizedState() {
      const dr = goalPos.r - dronePos.r;
      const dc = goalPos.c - dronePos.c;
      const drBin = Math.max(-2, Math.min(2, Math.round(dr / 4.0)));
      const dcBin = Math.max(-2, Math.min(2, Math.round(dc / 4.0)));

      // 8-neighbor hazard detection
      let maxH = ELEV_MATRIX[dronePos.r][dronePos.c];
      for (let drStep = -1; drStep <= 1; drStep++) {
        for (let dcStep = -1; dcStep <= 1; dcStep++) {
          const nr = dronePos.r + drStep;
          const nc = dronePos.c + dcStep;
          if (nr >= 0 && nr < GRID_SIZE && nc >= 0 && nc < GRID_SIZE) {
            maxH = Math.max(maxH, ELEV_MATRIX[nr][nc]);
          }
        }
      }
      let hazard = 0;
      if (maxH >= CRUISE_ALTITUDE) hazard = 2;
      else if (maxH >= CRUISE_ALTITUDE * 0.65) hazard = 1;

      // Risk Bin
      const riskBin = Math.max(0, Math.min(3, Math.floor(currentREnv * 4.0)));
      return `${drBin},${dcBin},${hazard},${riskBin}`;
    }

    function selectAction(stateKey) {
      const agentType = document.getElementById("agentSelect").value;
      const policyTable = (agentType === "adaptive") ? Q_ADAPTIVE.q_table : Q_BASELINE.q_table;
      const qVals = policyTable[stateKey];

      if (!qVals) {
        // Fallback: direct vector toward goal
        const dr = goalPos.r - dronePos.r;
        const dc = goalPos.c - dronePos.c;
        if (Math.abs(dr) > Math.abs(dc)) return (dr > 0) ? 4 : 0;
        return (dc > 0) ? 2 : 6;
      }

      let bestAction = 0;
      let maxQ = -Infinity;
      for (let a = 0; a < 8; a++) {
        if (qVals[a] > maxQ) {
          maxQ = qVals[a];
          bestAction = a;
        }
      }
      return bestAction;
    }

    function stepSimulation() {
      if (!isFlying) return;
      stepCount++;
      document.getElementById("stepCounter").textContent = `Step: ${stepCount} / 100`;

      const stateKey = getDiscretizedState();
      let action = selectAction(stateKey);
      const safetyEnabled = document.getElementById("checkSafety").checked;

      let isOverridden = false;
      let overrideReason = "";

      // ── Safety Envelope Check ──────────────────────────────────────────────
      if (safetyEnabled) {
        if (currentREnv > R_CRITICAL) {
          isOverridden = true;
          overrideReason = `Critical Environmental Risk (R_env = ${currentREnv.toFixed(2)})`;
        } else if (currentQ > Q_CRITICAL) {
          isOverridden = true;
          overrideReason = `Gust Dynamic Pressure Limit (q = ${currentQ.toFixed(1)} Pa)`;
        } else {
          // Check collision
          const nextR = dronePos.r + ACTIONS[action][0];
          const nextC = dronePos.c + ACTIONS[action][1];
          if (nextR < 0 || nextR >= GRID_SIZE || nextC < 0 || nextC >= GRID_SIZE || ELEV_MATRIX[nextR][nextC] >= CRUISE_ALTITUDE) {
            isOverridden = true;
            overrideReason = "Imminent Terrain Ridge / Boundary Hazard";
          }
        }
      }

      if (isOverridden) {
        overrideCount++;
        overrideMarkers.push({ ...dronePos });
        document.getElementById("valOverrides").textContent = overrideCount;

        if (currentREnv > 0.95 || currentQ > Q_CRITICAL * 1.3) {
          // Hover in place
          log(`⚠️ SAFETY OVERRIDE: ${overrideReason} -> Hovering in place`, "log-warn");
          drawScene();
          checkTermination();
          return;
        } else {
          // Route safely toward home base
          log(`⚠️ SAFETY OVERRIDE: ${overrideReason} -> Routing to Base`, "log-warn");
          action = calculateSafeRetreatAction();
        }
      }

      // Execute Action Move
      const delta = ACTIONS[action];
      const newR = dronePos.r + delta[0];
      const newC = dronePos.c + delta[1];

      // Terrain crash check (if safety is disabled)
      if (newR < 0 || newR >= GRID_SIZE || newC < 0 || newC >= GRID_SIZE || ELEV_MATRIX[newR][newC] >= CRUISE_ALTITUDE) {
        log(`💥 CRASH! Drone collided with mountain ridge at (${newR}, ${newC})`, "log-crit");
        stopFlight();
        drawScene();
        return;
      }

      dronePos = { r: newR, c: newC };
      flightTrail.push({ ...dronePos });

      // Update Telemetry
      const dist = Math.hypot(goalPos.r - dronePos.r, goalPos.c - dronePos.c);
      document.getElementById("valDronePos").textContent = `(${dronePos.r}, ${dronePos.c})`;
      document.getElementById("valDist").textContent = `${dist.toFixed(1)} cells`;

      checkTermination();
      drawScene();
    }

    function calculateSafeRetreatAction() {
      let bestAct = 0;
      let minCost = Infinity;
      for (let a = 0; a < 8; a++) {
        const nr = dronePos.r + ACTIONS[a][0];
        const nc = dronePos.c + ACTIONS[a][1];
        if (nr >= 0 && nr < GRID_SIZE && nc >= 0 && nc < GRID_SIZE && ELEV_MATRIX[nr][nc] < CRUISE_ALTITUDE) {
          const dHome = Math.hypot(homePos.r - nr, homePos.c - nc);
          const cost = dHome + ELEV_MATRIX[nr][nc] * 4.0;
          if (cost < minCost) {
            minCost = cost;
            bestAct = a;
          }
        }
      }
      return bestAct;
    }

    function checkTermination() {
      if (dronePos.r === goalPos.r && dronePos.c === goalPos.c) {
        log(`🎯 SUCCESS! Drone reached target goal at (${goalPos.r}, ${goalPos.c})!`, "log-success");
        stopFlight();
      } else if (stepCount >= 100) {
        log(`⏱️ TIMEOUT: Mission step limit (100) reached.`, "log-warn");
        stopFlight();
      }
    }

    function toggleFlight() {
      if (isFlying) {
        stopFlight();
      } else {
        startFlight();
      }
    }

    function startFlight() {
      isFlying = true;
      document.getElementById("btnPlay").textContent = "⏸ Pause Mission";
      document.getElementById("btnPlay").className = "danger";
      log(`🚀 Mission Started. Navigating toward (${goalPos.r}, ${goalPos.c})`);
      flightTimer = setInterval(stepSimulation, 200);
    }

    function stopFlight() {
      isFlying = false;
      document.getElementById("btnPlay").textContent = "▶ Resume Mission";
      document.getElementById("btnPlay").className = "primary";
      clearInterval(flightTimer);
    }

    function resetMission(randomize = false) {
      stopFlight();
      stepCount = 0;
      overrideCount = 0;
      overrideMarkers = [];
      document.getElementById("stepCounter").textContent = "Step: 0 / 100";
      document.getElementById("valOverrides").textContent = "0";

      if (randomize) {
        // Pick new valid valley spawn & goal
        let found = false;
        for (let tries = 0; tries < 100; tries++) {
          const sr = Math.floor(Math.random() * (GRID_SIZE - 4)) + 2;
          const sc = Math.floor(Math.random() * (GRID_SIZE - 4)) + 2;
          const gr = Math.floor(Math.random() * (GRID_SIZE - 4)) + 2;
          const gc = Math.floor(Math.random() * (GRID_SIZE - 4)) + 2;
          if (ELEV_MATRIX[sr][sc] < 0.25 && ELEV_MATRIX[gr][gc] < 0.25 && Math.hypot(gr - sr, gc - sc) > 10) {
            dronePos = { r: sr, c: sc };
            homePos = { r: sr, c: sc };
            goalPos = { r: gr, c: gc };
            found = true;
            break;
          }
        }
      } else {
        dronePos = { ...homePos };
      }

      flightTrail = [{ ...dronePos }];
      document.getElementById("valDronePos").textContent = `(${dronePos.r}, ${dronePos.c})`;
      document.getElementById("valGoalPos").textContent = `(${goalPos.r}, ${goalPos.c})`;
      const dist = Math.hypot(goalPos.r - dronePos.r, goalPos.c - dronePos.c);
      document.getElementById("valDist").textContent = `${dist.toFixed(1)} cells`;
      document.getElementById("btnPlay").textContent = "▶ Start Mission";

      log(`🔄 Mission Reset. Drone at (${dronePos.r}, ${dronePos.c}), Goal at (${goalPos.r}, ${goalPos.c})`);
      drawScene();
    }

    function updateAgentSelection() {
      const agentType = document.getElementById("agentSelect").value;
      log(`Switched to: ${agentType === 'adaptive' ? 'Adaptive Q-Agent' : 'Static Baseline Agent'}`);
    }

    function log(msg, className = "") {
      const box = document.getElementById("logBox");
      const div = document.createElement("div");
      div.className = `log-entry ${className}`;
      div.textContent = `[T+${stepCount}] ${msg}`;
      box.appendChild(div);
    }

    // Interactive Canvas Mouse Hover (Cell Elevation & Coordinates)
    CANVAS.addEventListener("mousemove", (e) => {
      const rect = CANVAS.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const c = Math.floor(x / (CANVAS.width / GRID_SIZE));
      const r = Math.floor(y / (CANVAS.height / GRID_SIZE));

      if (r >= 0 && r < GRID_SIZE && c >= 0 && c < GRID_SIZE) {
        const normH = ELEV_MATRIX[r][c];
        const minM = TERRAIN_DATA.min_elevation_m || 780.8;
        const maxM = TERRAIN_DATA.max_elevation_m || 827.5;
        const meters = (minM + normH * (maxM - minM)).toFixed(1);
        const lat = (TERRAIN_DATA.north - (r / (GRID_SIZE - 1)) * (TERRAIN_DATA.north - TERRAIN_DATA.south)).toFixed(4);
        const lon = (TERRAIN_DATA.west + (c / (GRID_SIZE - 1)) * (TERRAIN_DATA.east - TERRAIN_DATA.west)).toFixed(4);

        document.getElementById("coordOverlay").innerHTML =
          `Cell [${r}, ${c}] | ${lat}°N, ${lon}°E | Elevation: <strong>${meters} m</strong> (norm: ${normH.toFixed(3)})`;
      }
    });

    // Initial Setup
    resetMission(false);
    updatePhysics();
    log("Simulation Environment Ready. Initialized with SRTM GL1 Mantripukhri Terrain.");
  </script>
</body>
</html>
"""

# Embed the real JSON data directly
html_final = html_template.replace("__TERRAIN_DATA_PLACEHOLDER__", json.dumps(terrain_data))
html_final = html_final.replace("__Q_ADAPTIVE_PLACEHOLDER__", json.dumps(q_adaptive_data))
html_final = html_final.replace("__Q_BASELINE_PLACEHOLDER__", json.dumps(q_baseline_data))

output_path = "ecopilot_demo.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_final)

print(f"[build] Created self-contained {output_path} ({len(html_final)/1024:.1f} KB)")

