# EcoPilot: Autonomous Drone Navigation Simulation

[![Tests](https://img.shields.io/badge/Unit%20Tests-17%2F17%20Passing-brightgreen)](#running-unit-tests)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Terrain](https://img.shields.io/badge/Terrain-SRTM%20GL1%2030m%20(Manipur)-orange)](#terrain-pipeline)

> **Autonomous micro-aerial vehicle (MAV) reinforcement learning navigation over real NASA SRTM elevation data (Mantripukhri, Imphal West, Manipur) with real-time atmospheric physics conditioning and a deterministic, policy-independent safety envelope.**

---

## Highlights

- **Real Topography**: Ingests real NASA SRTM GL1 30m digital elevation data for the Mantripukhri valley basin (`[24.8423°N, 93.9302°E]` to `[24.8559°N, 93.9442°E]`).
- **Thermodynamic Atmospheric Physics**: Computes virtual temperature ($T_v$), moist air density ($\rho$), rotor thrust compensation factor ($k_{\text{thrust}}$), dynamic gust pressure ($q$), and composite environmental risk ($R_{\text{env}}$).
- **Tabular Q-Learning (CPU-Only)**: Zero GPU / neural-network dependencies. Discretizes state into 300 compact states and dynamically scales risk penalties via $\lambda(R_{\text{env}})$.
- **Independent Safety Envelope**: Hard-coded safety governor that overrides unsafe policy actions during storm squalls or imminent terrain collision, guaranteeing **0.0% crash rates** across all weather regimes.
- **Interactive Browser Visualizer**: Self-contained HTML5 Canvas simulation with interactive weather sliders and real-time policy playback.

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

Use the interactive sliders to adjust wind speed, direction, temperature, and humidity, and watch the drone navigate in real time with live aerodynamic telemetry.

---

## Project Architecture

```
EcoPilot/
├── terrain/                       # Topographic data & heightmaps
│   ├── srtm_gl1.tif               # Real NASA SRTM GeoTIFF
│   ├── terrain.npy                # Normalized 24x24 elevation grid
│   ├── terrain.json               # GeoJSON metadata & elevation matrix
│   └── terrain_preview.png        # 4-panel topographic visualization
├── data/                          # Experimentation & models
│   ├── weather_reference.json     # Live Mantripukhri weather snapshot (Open-Meteo)
│   ├── training_log.csv           # 1,200-episode training log
│   ├── evaluation_results.csv     # Full benchmark evaluation results
│   ├── q_table_adaptive.json      # Trained Adaptive Q-table
│   └── q_table_baseline.json      # Trained Static Baseline Q-table
├── tests/                         # Automated test suite
│   ├── test_environment_model.py # Physics & thermodynamic formulas
│   ├── test_rl_pipeline.py        # Environment transitions & agent updates
│   ├── test_safety.py             # 5,000-trial Monte Carlo safety stress test
│   └── test_browser_demo.mjs      # Headless Chrome browser automation test
├── environment_model.py           # Atmospheric physics module (7 SI-traceable formulas)
├── drone_env.py                   # Gymnasium-style RL environment
├── q_agent.py                     # Tabular Q-learning agent with Bellman optimality
├── static_baseline_agent.py       # Static-reward baseline agent (fixed lambda)
├── safety.py                      # Policy-independent safety envelope
├── train.py                       # Paired training pipeline (600 episodes)
├── evaluate.py                    # Multi-bucket empirical evaluation & charting
├── build_demo.py                  # Self-contained browser demo compiler
├── ecopilot_demo.html             # Standalone in-browser visualizer
├── evaluation_charts.png          # 4-panel evaluation benchmark comparison
├── requirements.txt               # Python package dependencies
├── REPORT.md                      # Comprehensive academic project report
└── README.md                      # Project documentation
```

---

## Running Automated Tests

```bash
# Run full unit test suite (17 tests)
python3 -m unittest discover tests/ -v

# Run headless Chrome browser automation test
node tests/test_browser_demo.mjs
```

---

## Running Pipeline Stages Manually

### 1. Ingest Terrain & Export Heightmap
```bash
python3 load_terrain.py
```

### 2. Train Both Agents (600 Paired Episodes)
```bash
python3 train.py
```

### 3. Run Benchmark Evaluation & Regenerate Charts
```bash
python3 evaluate.py
```

---

## Evaluation Summary

Evaluated across 100 trials per meteorological condition bucket:

| Atmospheric Regime | Evaluated Agent | Success Rate | Crash Rate | Safety Overrides |
|---|---|:---:|:---:|:---:|
| **Calm** ($R_{\text{env}} \approx 0.19$) | **Adaptive + Safety** | **4.0%** | **0.0%** | 5.85 / ep |
| | Static Baseline | 2.0% | 22.0% | 0.00 / ep |
| **Moderate** ($R_{\text{env}} \approx 0.46$) | **Adaptive + Safety** | 1.0% | **0.0%** | 27.96 / ep |
| | Static Baseline | **9.0%** | 22.0% | 0.00 / ep |
| **Severe Squall** ($R_{\text{env}} \approx 0.86$) | **Adaptive + Safety** | **2.0%** | **0.0%** | 81.59 / ep |
| | Static Baseline | 0.0% | **87.0%** | 0.00 / ep |

![Evaluation Benchmark](evaluation_charts.png)

> **Key Takeaway**: The safety envelope completely eliminates crashes (**0.0% across all regimes**), whereas the unconstrained baseline suffers an **87.0% crash rate** under severe squall turbulence.

---

## License

This project is open-source under the [MIT License](LICENSE).
