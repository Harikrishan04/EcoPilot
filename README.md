# EcoPilot: Autonomous Drone Navigation Simulation

[![Tests](https://img.shields.io/badge/Unit%20Tests-41%2F41%20Passing-brightgreen)](#running-automated-tests)
[![Browser Tests](https://img.shields.io/badge/Browser%20CDP-Passing-brightgreen)](#automated-browser-testing)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Terrain](https://img.shields.io/badge/Terrain-SRTM%20GL1%2030m%20(Manipur)-orange)](#terrain-pipeline)

> **Autonomous micro-aerial vehicle (MAV) reinforcement learning navigation over real NASA SRTM elevation data (Mantripukhri, Imphal West, Manipur) with real-time atmospheric thermodynamics, battery energy dynamics, and a deterministic, policy-independent safety envelope.**

---

## Highlights

- **Real Topography**: Ingests real NASA SRTM GL1 30m digital elevation data for the Mantripukhri valley basin (`[24.8423°N, 93.9302°E]` to `[24.8559°N, 93.9442°E]`) with guaranteed reachable A* valley corridors.
- **Thermodynamic Atmospheric Physics**: Computes virtual temperature ($T_v$), moist air density ($\rho$), rotor thrust compensation factor ($k_{\text{thrust}}$), dynamic gust pressure ($q$), and composite environmental risk ($R_{\text{env}}$).
- **Battery Energy Depletion**: Physical power draw model integrating avionics base load ($15\text{ W}$), thrust-compensated rotor hover power ($180\text{ W}$), parasitic aerodynamic drag, and vertical climb work from a 4S 75 W·h battery pack.
- **Tabular Q-Learning (CPU-Only)**: Zero GPU / neural-network dependencies. Discretizes state into 1,440 compact states and dynamically scales risk penalties via $\lambda(R_{\text{env}})$.
- **Independent Safety Envelope**: Hard-coded safety governor with duration-capped hover (max 4 steps), low-battery reserve aborts ($<20\%$), emergency landing zones, and storm protection, guaranteeing **0.0% crash rates** across all weather regimes.
- **Multi-Agent Benchmarking**: Compares the Adaptive Q-Agent against a Static Baseline Agent and an external Rule-Based A* Planner under identical safety layers.
- **Versioned & Reproducible**: Fully reproducible evaluation configured in [`configs/baseline_evaluation.json`](configs/baseline_evaluation.json), exporting per-episode logs (`data/evaluation_results.csv`) and aggregate summaries (`data/evaluation_summary.csv`).

---

## Visual Demonstration

![EcoPilot Interactive Visualizer](demo_screenshot.png)

---

## Quick Start

### 1. Prerequisites & Installation

```bash
git clone https://github.com/Harikrishan04/EcoPilot.git
cd EcoPilot

# Install dependencies (system packages or pip)
pip install -r requirements.txt
```

### 2. Launch the Interactive Browser Demo

Open [`ecopilot_demo.html`](ecopilot_demo.html) directly in any modern browser:

```bash
# On Linux
xdg-open ecopilot_demo.html

# Or serve locally
python3 -m http.server 8000
# Navigate to http://localhost:8000/ecopilot_demo.html
```

---

## Empirical Benchmark Evaluation

Evaluated across **100 held-out evaluation seeds** (seeds 5001–5100, strictly disjoint from training) per meteorological bucket:

| Condition Bucket | Evaluated Model | Success Rate (%) | 95% Confidence Interval | Safe RTH (%) | Timeout (%) | Crash (%) | Mean Flight Time (s) | Mean Path (m) | Mean Energy (W·h) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Calm** ($R_{\text{env}} \approx 0.19$) | **Adaptive Q-Agent** | **97.0%** | $\pm 3.3\%$ | 0.0% | 3.0% | **0.0%** | 51.9 s | 516.0 m | 4.47 W·h |
| | Static Baseline | 95.0% | $\pm 4.3\%$ | 0.0% | 5.0% | **0.0%** | 71.3 s | 710.5 m | 6.13 W·h |
| | Rule-Based A* Planner | **100.0%** | $\pm 0.0\%$ | 0.0% | 0.0% | **0.0%** | 38.6 s | 384.3 m | 3.33 W·h |
| **Moderate** ($R_{\text{env}} \approx 0.47$) | **Adaptive Q-Agent** | **66.0%** | $\pm 9.3\%$ | 0.0% | 34.0% | **0.0%** | 117.4 s | 747.2 m | 10.25 W·h |
| | Static Baseline | 65.0% | $\pm 9.3\%$ | 0.0% | 35.0% | **0.0%** | 118.1 s | 802.8 m | 10.58 W·h |
| | Rule-Based A* Planner | **74.0%** | $\pm 8.6\%$ | 0.0% | 26.0% | **0.0%** | 97.7 s | 630.2 m | 8.61 W·h |
| **Severe** ($R_{\text{env}} \approx 0.90$) | **Adaptive Q-Agent** | 3.0% | $\pm 3.3\%$ | **95.0%** | 2.0% | **0.0%** | 11.8 s | 49.4 m | 1.11 W·h |
| | Static Baseline | 0.0% | $\pm 0.0\%$ | **96.0%** | 4.0% | **0.0%** | 15.4 s | 93.2 m | 1.72 W·h |
| | Rule-Based A* Planner | 4.0% | $\pm 3.8\%$ | **96.0%** | 0.0% | **0.0%** | 8.7 s | 25.4 m | 0.66 W·h |

![Evaluation Benchmark](evaluation_charts.png)

---

## Simplified 3D Kinematic Model & Physical Limits (Phase 2)

EcoPilot models continuous 3D flight state, kinematics, and energy consumption under real meteorological constraints:
- **Continuous 3D State**: Position $(x, y, z)$ [m], 3D ground velocity $(v_x, v_y, v_z)$ [m/s], relative aerodynamic airspeed $v_{\text{rel}}$ [m/s], heading $\psi$ [rad], terrain clearance $h_{\text{clear}}$ [m], and battery state-of-charge $\text{SoC}$ [%].
- **Simplified 3D Kinematics**: At each timestep ($\Delta t = 2.0$ s), velocity updates incorporate commanded action velocity and ambient wind drift coupling ($\gamma = 0.05$ hover, $\gamma = 0.20$ flight) before advancing continuous position.
- **Single Source of Truth**: All limits are loaded directly from [`configs/flight_dynamics.json`](configs/flight_dynamics.json), enforcing maximum horizontal speed ($12.0\text{ m/s}$), maximum climb ($+2.5\text{ m/s}$), maximum descent ($-2.0\text{ m/s}$), altitude floor ($z_{\text{min}} = 0.15 \equiv 60\text{ m}$), and ceiling ($z_{\text{max}} = 0.85 \equiv 340\text{ m}$).
- **Vector Relative Airspeed**: Relative airspeed is computed directly from actual ground velocity and wind vector:
  $$\vec{v}_{\text{air}} = \vec{v}_{\text{ground}} - \vec{v}_{\text{wind}}, \quad v_{\text{rel}} = |\vec{v}_{\text{air}}|$$
  This exact relative airspeed is used for dynamic pressure $q = 0.5 \rho v_{\text{rel}}^2$ and parasitic drag power $P_{\text{drag}} = c_{\text{drag}} v_{\text{rel}}^3$.
- **Continuous 3D Path Length**: Calculated in metres from consecutive 3D continuous telemetry entries $(x, y, z)$, capturing horizontal wind drift and vertical climbs without integer grid rounding.
- **Altitude Geofence Clamp & Safety Outcome**: Altitude is clamped at the flight ceiling and floor with $v_z$ zeroed, while uncontrolled excursions trigger an explicit `altitude_violation` outcome.
- **Bilinear Elevation Lookup**: 4-point bilinear interpolation across SRTM GL1 30m digital elevation data.
- **Energy Model**: Total electrical power $P_{\text{total}} = P_{\text{avionics}} + P_{\text{hover}} + P_{\text{drag}} + P_{\text{climb}}$ from a 75 W·h battery pack.
- **Sample Flight Logs**: Complete, timestamped JSON flight logs exported to [`data/flight_logs/`](data/flight_logs/) for calm, moderate, and emergency scenarios.
- **Model Classification & Boundaries**: Characterized as a simplified 3D kinematic simulation. Translational ground speed is bounded by vehicle limits and velocity clipping rather than dynamic drag force equilibrium; attitude dynamics are assumed to be instantaneously stabilized by the inner-loop autopilot.

---

## Running Automated Tests

```bash
# Run full unit and integration test suite (41 tests covering physics, RL, safety, 3D dynamics, and evaluation)
python3 -m unittest discover tests/ -v

# Run hardened headless Chrome browser automation test (strict assertions and stderr diagnostics)
node tests/test_browser_demo.mjs
```

---

## Running Pipeline Stages Manually

### 1. Ingest Terrain & Export Heightmap
```bash
python3 load_terrain.py
```

### 2. Train Both Agents (700 Paired Episodes)
```bash
python3 train.py
```

### 3. Run Benchmark Evaluation from Versioned Configuration
```bash
python3 evaluate.py --config configs/baseline_evaluation.json
```

---

## License

This project is open-source under the [MIT License](LICENSE).
