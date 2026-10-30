# EcoPilot: Autonomous Drone Navigation Simulation

[![Tests](https://img.shields.io/badge/Unit%20Tests-37%2F37%20Passing-brightgreen)](#running-automated-tests)
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
| **Calm** ($R_{\text{env}} \approx 0.19$) | **Adaptive Q-Agent** | **98.0%** | $\pm 2.7\%$ | 0.0% | 2.0% | **0.0%** | 33.9 s | 602.9 m | 2.54 W·h |
| | Static Baseline | 96.0% | $\pm 3.8\%$ | 0.0% | 4.0% | **0.0%** | 48.5 s | 865.7 m | 3.63 W·h |
| | Rule-Based A* Planner | **100.0%** | $\pm 0.0\%$ | 0.0% | 0.0% | **0.0%** | 24.0 s | 402.5 m | 1.81 W·h |
| **Moderate** ($R_{\text{env}} \approx 0.47$) | **Adaptive Q-Agent** | **90.0%** | $\pm 5.9\%$ | 0.0% | 10.0% | **0.0%** | 53.9 s | 739.7 m | 5.02 W·h |
| | Static Baseline | 89.0% | $\pm 6.1\%$ | 0.0% | 11.0% | **0.0%** | 56.0 s | 722.1 m | 5.05 W·h |
| | Rule-Based A* Planner | **94.0%** | $\pm 4.7\%$ | 0.0% | 6.0% | **0.0%** | 43.1 s | 459.9 m | 3.80 W·h |
| **Severe** ($R_{\text{env}} \approx 0.90$) | **Adaptive Q-Agent** | 0.0% | $\pm 0.0\%$ | **100.0%** | 0.0% | **0.0%** | 6.0 s | 1.5 m | 0.40 W·h |
| | Static Baseline | 1.0% | $\pm 2.0\%$ | **99.0%** | 0.0% | **0.0%** | 7.8 s | 18.7 m | 0.58 W·h |
| | Rule-Based A* Planner | 2.0% | $\pm 2.7\%$ | **98.0%** | 0.0% | **0.0%** | 6.6 s | 11.8 m | 0.54 W·h |

![Evaluation Benchmark](evaluation_charts.png)

---

## 3D Flight State, Kinematics & Energy Model (Phase 2)

EcoPilot models continuous 3D flight state, kinematics, and energy consumption under real meteorological constraints:
- **Continuous 3D State**: Position $(x, y, z)$ [m], 3D ground velocity $(v_x, v_y, v_z)$ [m/s], relative airspeed $v_{\text{rel}}$ [m/s], heading $\psi$ [rad], terrain clearance $h_{\text{clear}}$ [m], and battery state-of-charge $\text{SoC}$ [%].
- **Semi-Implicit Euler Dynamics**: At each timestep ($\Delta t = 2.0$ s), velocity updates incorporate vehicle thrust commands and ambient wind drift coupling ($\gamma = 0.05$ hover, $\gamma = 0.20$ flight) before position integration.
- **Bilinear Continuous Elevation Lookup**: Interpolates 4-point SRTM elevation grid nodes so terrain clearance is continuously evaluated between discrete grid points.
- **Physical Vehicle Constraints**: Enforces maximum horizontal ground speed ($18.0\text{ m/s}$), maximum climb ($+2.5\text{ m/s}$), maximum descent ($-2.0\text{ m/s}$), altitude floor ($z_{\text{min}} = 0.15 \equiv 60\text{ m}$), and ceiling ($z_{\text{max}} = 0.85 \equiv 340\text{ m}$).
- **Energy Model**: Total electrical power $P_{\text{total}} = P_{\text{avionics}} + P_{\text{hover}} + P_{\text{drag}} + P_{\text{climb}}$ draws from a 75 W·h battery pack. Parasitic drag scales with $v_{\text{rel}}^3$, while climb requires vertical potential work $mgv_z$.
- **Sample Flight Logs**: Complete, timestamped JSON flight logs containing per-step continuous telemetry are automatically exported to [`data/flight_logs/`](data/flight_logs/) for calm, moderate, and emergency weather scenarios.
- **Simulation Scope & Simplifications**: Documented in [`configs/flight_dynamics.json`](configs/flight_dynamics.json). The simulation assumes point-mass translational kinematics with attitude stabilized by an underlying flight controller. High-frequency rotor vortex shedding and aerodynamic ground effect are simplified to lumped dynamic pressure and density-compensated thrust factors.

---

## Running Automated Tests

```bash
# Run full unit and integration test suite (25 tests covering physics, RL, safety, and evaluation)
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
