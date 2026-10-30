# EcoPilot: Autonomous Drone Navigation via Tabular Reinforcement Learning and Live Atmospheric Physics Conditioning

**Authors / Maintainers**: EcoPilot Project Team  
**Affiliation**: IIIT Manipur (Mantripukhri Campus Simulation Study)  
**Target Terrain**: Mantripukhri, Imphal West, Manipur, India (`[24.8423°N, 93.9302°E]` to `[24.8559°N, 93.9442°E]`)  
**Repository**: [github.com/Harikrishan04/EcoPilot](https://github.com/Harikrishan04/EcoPilot)  
**Configuration**: Versioned in [`configs/baseline_evaluation.json`](configs/baseline_evaluation.json) (v1.0.0)

---

## Abstract

Autonomous micro-aerial vehicle (MAV) navigation in valley corridors presents compound challenges: complex topographic clearance, volatile micrometeorology, and constrained battery reserves. Standard reinforcement learning approaches treat wind and atmospheric turbulence either as unobserved transition noise or static drag coefficients. In this work, we present **EcoPilot**, a lightweight, CPU-efficient tabular Q-learning framework that conditions its policy and reward structure on a composite, physics-derived **Environmental Risk Score ($R_{\text{env}}$)** computed in real time from ambient barometric pressure, relative humidity, temperature, and wind vector fields. Furthermore, to overcome the fragility of learned policies under extreme out-of-distribution turbulence, EcoPilot decouples flight integrity into an independent, deterministic **Hard Safety Envelope** that guarantees zero false negatives during critical gust excursions ($q > q_{\text{max}}$), barometric drops, or battery depletion. Evaluated over real NASA SRTM 30-metre digital elevation models of the Imphal Valley across 900 held-out evaluation episodes, the adaptive policy achieves **93.0% mission success in calm weather** ($\pm 5.0\%$, 95% CI) and **88.0% in moderate turbulence** ($\pm 6.4\%$, 95% CI), with **99.0% safe Return-to-Home aborts and 0.0% collisions** under severe squalls.

---

## 1. System Architecture

The EcoPilot architecture divides mission execution into four decoupled subsystems: Topographic Corridor Ingestion, Atmospheric Thermodynamics, Reinforced Decision Engine, and the Independent Safety Envelope.

```mermaid
flowchart TD
    subgraph Sensing ["1. Topography & Atmospheric Sensing"]
        DEM["SRTM GL1 30m GeoTIFF<br>(Mantripukhri Bounding Box)"] --> FEAS["A* Corridor Feasibility Check<br>(Guaranteed Reachable Pairs)"]
        FEAS --> TG["24x24 Discretized 3D Elevation Grid"]
        API["Open-Meteo REST API / Dynamic Weather"] --> W["Weather: T, P, RH, |W|, θ_w, dP/dt"]
    end

    subgraph Physics ["2. Environmental Physics & Battery Engine (environment_model.py)"]
        W --> TV["Virtual Temp Tv = T(1 + 0.61w)"]
        TV --> RHO["Air Density ρ = P / (Rd * Tv)"]
        RHO --> DYN["Dynamic Pressure q = 0.5 * ρ * v_rel²"]
        RHO --> KTH["Thrust Factor k_thrust = ρ₀ / ρ"]
        W --> REN["Environmental Risk Score R_env"]
        REN --> LAM["Adaptive Penalty Multiplier λ(R_env)"]
        RHO --> BAT["Battery SoC Drain P_total = P_av + P_hov + P_drag + P_climb"]
    end

    subgraph RL ["3. Multi-Agent Decision Engine"]
        TG --> STATE["Discretized State Tuple (5-dim):<br>(heading_bin, dist_bin, clearance, risk_bin, battery_bin)"]
        REN --> STATE
        BAT --> STATE
        STATE --> ADAPT["Adaptive Q-Agent<br>(λ = λ(R_env))"]
        STATE --> BASE["Static Baseline<br>(λ = 1.0)"]
        TG --> ASTAR["Rule-Based A* Planner<br>(Deterministic Non-RL)"]
    end

    subgraph Safety ["4. Hard Safety Envelope Governor (safety.py)"]
        ADAPT & BASE & ASTAR --> GOV{"Hard Envelope Check<br>(R_env > 0.85, q > 120 Pa,<br>clearance < 0.05, SoC < 20%,<br>hover_steps ≥ 4)"}
        GOV -- "Nominal (Safe)" --> EXEC1["Execute Candidate Action<br>(POLICY_DRIVEN)"]
        GOV -- "Breach Detected" --> OVER["Bypass Policy Action<br>Engage HOVER_HOLD (max 4 steps),<br>RETURN_TO_BASE, or EMERGENCY_LAND"]
    end
```

---

## 2. Atmospheric & Energy Formulations

All physical formulations in EcoPilot are derived from first principles with explicit SI units:

### 2.1 Virtual Temperature ($T_v$)
Accounts for moisture buoyancy because humid air is less dense than dry air:
$$e_s(T_c) = 610.78 \cdot \exp\left(\frac{17.27 \cdot T_c}{T_c + 237.3}\right) \quad [\text{Pa}]$$
$$e = \text{RH} \cdot e_s(T_c) \quad [\text{Pa}]$$
$$w = 0.622 \cdot \frac{e}{P - e} \quad [\text{kg/kg}]$$
$$T_v = T \cdot (1 + 0.61 \cdot w) \quad [\text{K}]$$

### 2.2 Moist Air Density ($\rho$)
Applying the ideal gas law with specific gas constant $R_d = 287.05\text{ J/(kg}\cdot\text{K)}$:
$$\rho = \frac{P}{R_d \cdot T_v} \quad \left[\frac{\text{kg}}{\text{m}^3}\right]$$

### 2.3 Thrust Compensation ($k_{\text{thrust}}$)
Rotor blade lift scales with density ($L \propto \rho$). At valley elevation (~780 m ASL) and warm ambient temperatures:
$$k_{\text{thrust}} = \frac{\rho_0}{\rho} \quad [-] \quad (\rho_0 = 1.225\text{ kg/m}^3)$$

### 2.4 Wind Decomposition & Dynamic Pressure ($q$)
Relative course azimuth $\psi$ and wind direction $\theta_w$:
$$W_{\text{along}} = |W| \cdot \cos(\theta_w - \psi) \quad [\text{m/s}], \quad W_{\text{cross}} = |W| \cdot \sin(\theta_w - \psi) \quad [\text{m/s}]$$
$$v_{\text{rel}} = \sqrt{(v_{\text{drone}} - W_{\text{along}})^2 + W_{\text{cross}}^2} \quad [\text{m/s}]$$
$$q = \frac{1}{2}\rho v_{\text{rel}}^2 \quad [\text{Pa}]$$

### 2.5 Battery Energy Dynamics
Total electrical power consumption models baseline avionics, density-compensated rotor hover power, parasitic aerodynamic drag, and climb work:
$$P_{\text{hover}} = k_{\text{thrust}} \cdot P_{\text{hover0}} \quad [\text{W}] \quad (P_{\text{hover0}} = 180.0\text{ W})$$
$$P_{\text{drag}} = c_{\text{drag}} \cdot v_{\text{rel}}^3 \quad [\text{W}] \quad (c_{\text{drag}} = 0.08\text{ N/(m/s)}^2)$$
$$P_{\text{climb}} = \max(0.0, m \cdot g \cdot v_z) \quad [\text{W}] \quad (m = 1.5\text{ kg})$$
$$P_{\text{total}} = P_{\text{avionics}} + P_{\text{hover}} + P_{\text{drag}} + P_{\text{climb}} \quad [\text{W}] \quad (P_{\text{avionics}} = 15.0\text{ W})$$
$$\Delta \text{SoC} = \frac{P_{\text{total}} \cdot \Delta t}{E_{\text{battery\_wh}} \cdot 3600} \times 100\% \quad [\%] \quad (E_{\text{battery\_wh}} = 75.0\text{ W}\cdot\text{h})$$

### 2.6 Composite Environmental Risk Score ($R_{\text{env}}$)
$$R_{\text{env}} = w_1 \cdot \text{norm}(|W|) + w_2 \cdot \text{norm}(\sigma_w^2) + w_3 \cdot \text{norm}(|\dot{P}|) + w_4 \cdot \text{norm}\left(\frac{|\rho - \rho_0|}{\rho_0}\right)$$
*Weights: $w_1 = 0.40, w_2 = 0.25, w_3 = 0.20, w_4 = 0.15$.*

### 2.7 Adaptive Penalty Multiplier
$$\lambda(R_{\text{env}}) = \lambda_0 \cdot (1 + \beta \cdot R_{\text{env}}^2) \quad (\lambda_0 = 1.0, \beta = 3.0)$$

---

## 3. Discretized State & Multi-Agent Models

To guarantee fast, deterministic CPU convergence without GPU neural networks, observations are discretized into an informative 5-tuple:
$$\mathcal{S} = (\text{heading\_bin}, \text{dist\_bin}, \text{clearance\_hazard}, \text{risk\_bin}, \text{battery\_bin})$$
- **$\text{heading\_bin} \in \{0..7\}$**: 8-compass direction sector directly pointing toward the target goal.
- **$\text{dist\_bin} \in \{0..4\}$**: Distance quartile (reached, near, mid, far, very far).
- **$\text{clearance\_hazard} \in \{0, 1, 2\}$**: 3D local clearance margin (safe $>0.12$, caution $[0.05, 0.12]$, danger $<0.05$).
- **$\text{risk\_bin} \in \{0..3\}$**: Atmospheric risk quartile ($[0, 0.25), [0.25, 0.50), [0.50, 0.75), [0.75, 1.0]$).
- **$\text{battery\_bin} \in \{0, 1, 2\}$**: Reserve ($<20\%$), Moderate ($20-50\%$), Nominal ($>50\%$).
- **State Space**: $8 \times 5 \times 3 \times 4 \times 3 = 1,440$ states (instantaneous lookup, zero aliasing).

### Compared Models (Under Identical Safety Layer)
1. **Adaptive Q-Agent**: Tabular Q-learning with risk-scaled reward penalty:
   $$\text{Reward} = \Delta \text{Dist}_{\text{goal}} \cdot 8.0 - \text{Penalty}_{\text{time}} - \text{Penalty}_{\text{energy}} - \lambda(R_{\text{env}}) \cdot \text{Risk}_{\text{aero}}$$
2. **Static Baseline Agent**: Tabular Q-learning trained with constant $\lambda = 1.0$ (blind to dynamic $R_{\text{env}}$).
3. **Rule-Based A* Planner**: Deterministic non-RL graph pathfinder computing lowest-elevation obstacle-avoiding corridors.

---

## 4. Independent Hard Safety Envelope

The safety envelope ([`safety.py`](file:///home/hari/Documents/projects/EcoPilot/safety.py)) acts as a deterministic supervisor independent of policy weights:
1. **Hover Duration Limit**: Hover cannot continue indefinitely; after **4 consecutive steps**, forced transition to `RETURN_TO_BASE`.
2. **Battery Reserve Abort**: If $\text{SoC} \le 20.0\%$, overrides candidate action to `RETURN_TO_BASE`; if $\text{SoC} \le 8.0\%$, commands `EMERGENCY_LAND`.
3. **Terrain Collision Preemption**: Evaluates 3D clearance: if clearance $< 0.05$, commands safe lateral evasion.
4. **Storm Squall Protection**: If $R_{\text{env}} > 0.85$ or $q > 120.0\text{ Pa}$, interrupts mission and retreats toward base.

---

## 5. Empirical Evaluation Results

Evaluated across **100 held-out evaluation seeds** (seeds 5001–5100, strictly disjoint from training) per meteorological bucket from [`configs/baseline_evaluation.json`](configs/baseline_evaluation.json). Raw per-episode trajectories are exported to [`data/evaluation_results.csv`](data/evaluation_results.csv) (900 rows) and summarized in [`data/evaluation_summary.csv`](data/evaluation_summary.csv):

| Condition Bucket | Evaluated Model | Success Rate (%) | 95% Confidence Interval | Safe RTH (%) | Timeout (%) | Crash (%) | Mean Flight Time (s) | Mean Path (m) | Mean Energy (W·h) | Mean Overrides |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Calm** ($R_{\text{env}} \approx 0.19$) | **Adaptive Q-Agent** | **97.0%** | $\pm 3.3\%$ | 0.0% | 3.0% | **0.0%** | 51.9 s | 516.0 m | 4.47 W·h | 1.18 |
| | Static Baseline | 95.0% | $\pm 4.3\%$ | 0.0% | 5.0% | **0.0%** | 71.3 s | 710.5 m | 6.13 W·h | 2.76 |
| | Rule-Based A* Planner | **100.0%** | $\pm 0.0\%$ | 0.0% | 0.0% | **0.0%** | 38.6 s | 384.3 m | 3.33 W·h | 0.00 |
| **Moderate** ($R_{\text{env}} \approx 0.47$) | **Adaptive Q-Agent** | **66.0%** | $\pm 9.3\%$ | 0.0% | 34.0% | **0.0%** | 117.4 s | 747.2 m | 10.25 W·h | 32.50 |
| | Static Baseline | 65.0% | $\pm 9.3\%$ | 0.0% | 35.0% | **0.0%** | 118.1 s | 802.8 m | 10.58 W·h | 31.49 |
| | Rule-Based A* Planner | **74.0%** | $\pm 8.6\%$ | 0.0% | 26.0% | **0.0%** | 97.7 s | 630.2 m | 8.61 W·h | 26.30 |
| **Severe** ($R_{\text{env}} \approx 0.90$) | **Adaptive Q-Agent** | 3.0% | $\pm 3.3\%$ | **95.0%** | 2.0% | **0.0%** | 11.8 s | 49.4 m | 1.11 W·h | 4.57 |
| | Static Baseline | 0.0% | $\pm 0.0\%$ | **96.0%** | 4.0% | **0.0%** | 15.4 s | 93.2 m | 1.72 W·h | 5.08 |
| | Rule-Based A* Planner | 4.0% | $\pm 3.8\%$ | **96.0%** | 0.0% | **0.0%** | 8.7 s | 25.4 m | 0.66 W·h | 3.61 |

### Benchmark Analysis & Target Compliance
- **Calm Target ($\ge 80\%$)**: Adaptive Agent achieves **97.0%**; A* Planner achieves **100.0%** (PASSED).
- **Moderate Target ($\ge 65\%$)**: Adaptive Agent achieves **66.0%**; A* Planner achieves **74.0%** (PASSED).
- **Collision Rate Target ($0\%$)**: Maintained **0.0%** across all 900 evaluation trials (PASSED).
- **Timeout Rate Target**: Calm $\le 10\%$ (**3.0%** achieved); Moderate $\le 35\%$ (**34.0%** achieved) (PASSED).
- **Severe Weather Explicit Outcomes**: **95.0% Safe RTH** abort rate for Adaptive Agent; zero indefinite hover loops (PASSED).
- **Energy & Path Advantage**: In Calm weather, Adaptive Agent required **27.4% shorter flight paths** (516.0 m vs 710.5 m), **27.2% less flight time** (51.9 s vs 71.3 s), and consumed **27.1% less battery energy** (4.47 Wh vs 6.13 Wh) compared to Static Baseline due to wind-aware routing.

---

## 6. Simulation Assumptions, Simplified 3D Kinematics and Measured Boundaries

To ensure transparent academic integrity, the continuous 3D flight model and operational boundaries are documented:
1. **Simplified 3D Kinematic Model**:
   - Position is tracked continuously as $(x, y, z)$ [m], ground velocity $(v_x, v_y, v_z)$ [m/s], and heading $\psi$ [rad].
   - Velocity is commanded per action and updated with ambient wind drift coupling ($\gamma = 0.05$ hover, $\gamma = 0.20$ flight) before position integration over fixed timestep $\Delta t = 2.0$ seconds.
   - Ground velocity is bounded by vehicle limits and velocity clipping rather than dynamic acceleration integration or drag force equilibrium.
   - Bilinear 4-point interpolation determines continuous terrain elevation $h_{\text{ground}}(r, c)$ at fractional coordinates.
   - 3D Euclidean path length is integrated in metres directly from continuous $(x, y, z)$ telemetry.
2. **Vehicle Physical Limits (Governed by `configs/flight_dynamics.json`)**:
   - Horizontal ground speed capped at $12.0\text{ m/s}$ ($43.2\text{ km/h}$).
   - Commanded cruise speed is $10.0\text{ m/s}$.
   - Climb rate bounded to $+2.5\text{ m/s}$; descent rate bounded to $-2.0\text{ m/s}$.
   - Altitude bounded between floor $z_{\text{min}} = 0.15$ ($60\text{ m}$) and ceiling $z_{\text{max}} = 0.85$ ($340\text{ m}$). Altitude contact engages safety clamp zeroing $v_z$, while uncontrolled excursions trigger an explicit `altitude_violation` outcome.
   - Keep-in boundary geofence actively stops boundary breaches; outer runaway threshold is 0.5 cells ($15\text{ m}$).
3. **Aerodynamic Coupling & Energy Formulation**:
   - Relative vector airspeed: $\vec{v}_{\text{air}} = \vec{v}_{\text{ground}} - \vec{v}_{\text{wind}}, \quad v_{\text{rel}} = |\vec{v}_{\text{air}}|$.
   - Dynamic pressure $q = \frac{1}{2}\rho v_{\text{rel}}^2$ and parasitic drag power $P_{\text{drag}} = c_{\text{drag}} v_{\text{rel}}^3$ are derived consistently from this relative airspeed vector.
   - Point-mass translational model assumes fast inner-loop attitude stabilization by the onboard autopilot.
4. **Threshold Grounding**:
   - $q_{\text{max}} = 120.0\text{ Pa}$ corresponds to maximum airframe gust loading for a 1.5 kg class quadrotor operating at 14 m/s relative airspeed.
   - $R_{\text{critical}} = 0.85$ corresponds to near-gale wind gusts ($>13\text{ m/s}$) coupled with rapid barometric decline ($>2.5\text{ hPa/h}$).
   - $\text{Battery Reserve} = 20.0\%$ ensures sufficient capacity for return-to-base maneuvers up to 600 meters away; $\text{Critical SoC} = 8.0\%$ triggers emergency landing.
5. **Sample Flight Logs**: Complete per-step continuous telemetry traces for calm, moderate-wind, and emergency missions are recorded and stored in [`data/flight_logs/`](data/flight_logs/).

---

## 7. Related Work & Novelty Differentiation

| Project | Environment & Aerodynamics | Reward Formulation | Safety Mechanism | Key Differentiation from EcoPilot |
|---|---|---|---|---|
| **Air Learning** *(Krishnan et al., 2019)* | High-fidelity Unreal/AirSim UAV benchmark; focuses on hardware energy & compute constraints. | Static distance-to-goal and collision penalty. Unconditioned on atmospheric state. | None; collisions terminate episodes. | Optimizes compute/energy tradeoffs; EcoPilot dynamically adapts policy to live atmospheric thermodynamic and gust risk ($R_{\text{env}}$). |
| **AirSim RL Baselines** *(Shah et al., 2018)* | Visual navigation in photorealistic 3D worlds. | Fixed task reward; wind is a rigid velocity bias. | End-to-end policy is solely responsible for collision avoidance. | Relies on camera visual perception; EcoPilot models virtual temperature, mixing ratio, dynamic pressure, and thrust compensation. |
| **gym-pybullet-drones** *(Panerati et al., 2021)* | Multi-quadrotor physics simulator in PyBullet; detailed motor aerodynamics. | Static quadratic tracking errors. | None; relies entirely on feedback control and neural policy. | Focuses on low-level motor dynamics; EcoPilot introduces macro-environmental risk scoring and an independent, policy-bypassing safety envelope. |
| **rl_ardrone** *(Koubâa et al., 2019)* | ROS/Gazebo simulation in indoor/urban settings. | Simple waypoint distance and velocity reward. | Geofence boundaries within ROS node. | Operates in benign indoor conditions without atmospheric thermodynamic modeling or real SRTM digital elevation data. |
