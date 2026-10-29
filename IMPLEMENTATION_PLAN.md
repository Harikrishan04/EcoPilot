# EcoPilot Implementation Plan

## Objective

Evolve EcoPilot from a 2D grid-navigation prototype into a reproducible drone-navigation simulation that evaluates mission completion, safety, energy use, and robustness under changing weather.

## Scope and outcome definitions

Every episode must end in one of these mutually exclusive outcomes:

| Outcome | Definition | Counts as mission success? |
|---|---|---|
| `success` | Drone reaches the goal within time, energy, and safety limits. | Yes |
| `safe_return` | Safety controller returns the drone to home. | No; report as safe abort. |
| `safe_land` | Safety controller reaches a designated landing zone. | No; report as safe abort. |
| `timeout` | Maximum episode duration is reached. | No |
| `collision` | Terrain, obstacle, or boundary collision occurs. | No |
| `constraint_violation` | Geofence, altitude, speed, or battery constraint is violated. | No |

## Phase 1: Establish a reproducible baseline

**Goal:** Make present behavior measurable before redesigning the simulator.

### Tasks

1. Add a single experiment configuration file containing random seed, terrain, weather bucket, agent, safety settings, and max episode length.
2. Update `evaluate.py` to return separate counts for all episode outcomes.
3. Evaluate Adaptive RL, Static RL, and a simple greedy route-planning baseline with identical safety settings.
4. Store one row per episode with seed, outcome, reward, steps, path length, interventions, and weather values.
5. Change browser test warnings into failed assertions and save Chrome startup errors.

### Files expected to change

- `evaluate.py`
- `tests/test_browser_demo.mjs`
- `data/evaluation_results.csv`
- New: `configs/baseline_evaluation.json`
- New: `baseline_agent.py`

### Acceptance checks

- [ ] One command produces a CSV and chart from a documented seed.
- [ ] All policies use the same episodes and safety configuration.
- [ ] Timeout, crash, safe return, and success are distinct outcomes.
- [ ] Browser tests fail when a required telemetry condition is false.

## Phase 2: Extend the environment to 3D flight state

**Goal:** Replace one-cell moves with simplified but continuous flight dynamics.

### State model

```text
position:       x, y, z
velocity:       vx, vy, vz
attitude:       heading/yaw
mission:        goal vector, elapsed time, home position
environment:    wind vector, gust value, terrain clearance
vehicle:        battery, energy used, maximum speed and climb rate
```

### Tasks

1. Create `flight_dynamics.py` with timestep-based position, velocity, drag, gravity, and energy updates.
2. Add an interpolated terrain-height query from the existing terrain grid.
3. Represent clearance as `altitude - terrain_height`.
4. Add battery consumption based on time, speed, climb rate, and wind compensation.
5. Preserve a compatibility mode so the existing grid environment can still be tested during migration.

### Files expected to change

- New: `flight_dynamics.py`
- `drone_env.py`
- `environment_model.py`
- New: `tests/test_flight_dynamics.py`

### Acceptance checks

- [ ] A stationary drone consumes energy while hovering.
- [ ] Climbing, faster flight, and stronger headwind increase energy use.
- [ ] Motion respects configured maximum speed, climb rate, and altitude range.
- [ ] Collision occurs when terrain clearance is zero or below.
- [ ] Existing physics tests continue to pass.

## Phase 3: Add dynamic weather and uncertainty

**Goal:** Make wind, weather, sensing, and command execution change throughout a mission.

### Tasks

1. Create `weather_profile.py` for calm, moderate, severe, and randomized weather trajectories.
2. Update wind every simulation timestep using a base vector plus bounded gust process.
3. Add configurable GPS, altitude, wind-estimation, and terrain-measurement noise.
4. Add configurable observation and control-command latency.
5. Include weather and fault parameters in the experiment record.

### Files expected to change

- New: `weather_profile.py`
- `drone_env.py`
- `environment_model.py`
- New: `tests/test_weather_profile.py`

### Acceptance checks

- [ ] Identical seeds reproduce identical weather trajectories.
- [ ] Different seeds produce meaningfully different trajectories within configured bounds.
- [ ] Wind produces measurable drift when no compensation is applied.
- [ ] Sensor noise and latency can be enabled independently.

## Phase 4: Redesign the policy interface

**Goal:** Give the navigation policy enough state and actions for 3D flight.

### Observation

Use a normalized observation vector containing:

```text
relative goal position, velocity, heading,
altitude, terrain clearance, local terrain samples,
wind estimate, gust estimate, battery reserve,
distance to home, time remaining, safety mode
```

### Actions

Start with high-level velocity commands:

```text
forward/backward velocity, lateral velocity, vertical velocity, yaw-rate,
hover, return-to-home, controlled-land
```

### Tasks

1. Add an observation encoder and action validator.
2. Keep tabular Q-learning only for a small discrete prototype.
3. Introduce a policy interface so tabular, rule-based, and future neural policies share one evaluation path.
4. Add a greedy goal-seeking baseline and a wind-compensated rule-based baseline.

### Files expected to change

- `q_agent.py`
- New: `policy_interface.py`
- New: `rule_based_agent.py`
- `drone_env.py`
- New: `tests/test_policy_interface.py`

### Acceptance checks

- [ ] Every agent accepts the same observation and returns a valid action.
- [ ] Invalid actions are rejected before dynamics execution.
- [ ] Rule-based agent reaches easy calm-weather goals consistently.
- [ ] Evaluation can switch policies without changing environment code.

## Phase 5: Implement layered safety and recovery

**Goal:** Convert emergency behavior from indefinite hovering into verified recovery behavior.

### Safety constraints

1. Minimum terrain clearance.
2. Geofence boundary.
3. Maximum horizontal and vertical speed.
4. Maximum acceleration and turn rate.
5. Minimum battery reserve for return or landing.
6. Wind and gust operating limits.
7. Observation-health and control-latency limits.

### Tasks

1. Refactor `SafetyEnvelope` into a safety filter that receives the proposed high-level action and returns a safe action.
2. Add safety modes: `POLICY`, `HOVER`, `RETURN_HOME`, `LAND`, and `TERMINATE`.
3. Define landing zones from low-risk, low-slope terrain cells.
4. Add a maximum hover duration followed by return or land.
5. Record each intervention, constraint, original action, safe action, and final result.

### Files expected to change

- `safety.py`
- New: `recovery_planner.py`
- `drone_env.py`
- `evaluate.py`
- `tests/test_safety.py`
- New: `tests/test_recovery_planner.py`

### Acceptance checks

- [ ] A safety violation never sends an unsafe action to the dynamics model.
- [ ] Return-to-home and landing finish in a terminal safe outcome.
- [ ] Hover cannot continue indefinitely.
- [ ] Every safety event is traceable in the episode record.
- [ ] Safety tests cover every constraint independently and in combinations.

## Phase 6: Train and compare policies

**Goal:** Demonstrate whether wind-aware adaptation improves navigation beyond safety rules alone.

### Experiment matrix

| Policy | Wind in observation | Adaptive risk reward | Safety filter |
|---|---:|---:|---:|
| Greedy baseline | No | No | Yes |
| Wind-compensated baseline | Yes | No | Yes |
| Static RL | Optional | No | Yes |
| Adaptive RL | Yes | Yes | Yes |

### Tasks

1. Train using multiple terrain maps, starts, goals, weather sequences, vehicle parameters, sensor-noise levels, and latencies.
2. Reserve terrain maps, seeds, and wind profiles for testing only.
3. Save training configuration and policy version with every model.
4. Run at least five independent training seeds per policy.
5. Report means and 95% confidence intervals.

### Acceptance checks

- [ ] Adaptive and static policies are evaluated on exactly the same episodes.
- [ ] Test seeds and terrain are absent from training.
- [ ] Results include confidence intervals from independent runs.
- [ ] A claimed adaptive-policy benefit is supported by a positive confidence interval relative to static RL.

## Phase 7: Evaluate and report results

**Goal:** Produce evidence that supports only the project claims justified by experiments.

### Evaluation conditions

| Bucket | Wind | Faults | Main expected behavior |
|---|---|---|---|
| Calm | 0–3 m/s | None | Complete mission efficiently. |
| Moderate | 3–8 m/s plus gusts | Optional noise and latency | Complete mission safely with limited intervention. |
| Severe | 8–15 m/s plus gusts | Noise and latency enabled | Complete mission when feasible; otherwise return or land safely. |
| Held-out | Unseen terrain and weather combinations | Varying faults | Demonstrate generalization. |

### Required metrics

| Metric | Rule |
|---|---|
| Mission success rate | Reached goal before time or energy limit, without a safety violation. |
| Collision rate | Terrain, obstacle, or boundary collisions divided by episodes. |
| Timeout rate | Timed-out episodes divided by episodes. |
| Safe-abort rate | Safe return plus safe landing divided by episodes. |
| Unsafe-abort rate | Failed return or landing divided by aborts. |
| Return success rate | Safe home arrival divided by return commands. |
| Intervention rate | Safety interventions divided by control steps. |
| Energy use | Energy consumed per episode and per completed mission. |
| Path efficiency | Shortest feasible path length divided by flown path length. |
| Dynamic violations | Rate of speed, acceleration, jerk, altitude, and clearance violations. |
| Generalization gap | Difference in held-out and standard evaluation success rates. |

### Minimum acceptance rules

- [ ] Calm mission success is at least 80%.
- [ ] Moderate mission success is at least 65%.
- [ ] Simulator collision rate is 0% when the safety filter is enabled.
- [ ] Calm timeout rate is at most 10%.
- [ ] Moderate timeout rate is at most 20%.
- [ ] Return-to-home success is at least 95%.
- [ ] Severe outcomes are reported as mission success, safe return, safe land, timeout, collision, or violation; they must not be combined.
- [ ] Held-out success is within 10 percentage points of standard test success, or the gap is explained as a limitation.

## Phase 8: Testing and automation

**Goal:** Make correctness and reproducibility automatic.

### Test layers

| Layer | Coverage |
|---|---|
| Unit | Atmospheric formulas, dynamics, battery, terrain query, observation encoding, action validation, and safety constraints. |
| Integration | Reset-to-terminal missions across each weather bucket, including return and land recovery. |
| Regression | Fixed seeds retain expected outcomes and metric ranges. |
| Browser | Telemetry, agent selection, weather controls, override display, and mission reset. |
| Reproducibility | Evaluation recreates results from a saved configuration and seed. |

### Acceptance checks

- [ ] Test commands have documented prerequisites and return nonzero on failure.
- [ ] Browser launch logs are captured on failure.
- [ ] Tests do not overwrite committed evaluation artifacts by default.
- [ ] CI runs unit and integration tests for every change.

## Suggested delivery milestones

| Milestone | Deliverable |
|---|---|
| M1 | Reproducible baseline report and reliable browser test. |
| M2 | 3D dynamics, terrain clearance, battery, and dynamic weather. |
| M3 | Shared policy interface and wind-compensated rule-based baseline. |
| M4 | Safety filter, return-to-home, controlled landing, and recovery tests. |
| M5 | Multi-seed training and fair policy comparison. |
| M6 | Held-out evaluation, final charts, report, and documented limitations. |

## Contributor responsibilities

Your primary contribution can be documented as:

> Design and evaluate a wind-aware drone-navigation simulator that separates learned navigation policy, deterministic safety filtering, and low-level flight dynamics. The evaluation compares adaptive, static, and rule-based policies under matched terrain, weather, random seeds, and safety constraints, using mission completion, safe aborts, energy use, trajectory efficiency, and constraint compliance.
