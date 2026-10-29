# EcoPilot Improvement Plan and Evaluation Rules

## Target outcome

EcoPilot should complete autonomous navigation missions from valid start positions to valid goals while avoiding terrain and safety-limit violations under controlled weather conditions.

A zero crash rate is not sufficient when a mission times out or remains in hover. Report mission success, safe aborts, and timeouts as separate outcomes.

## Features to implement

| Area | Improvement | Purpose |
|---|---|---|
| Flight environment | Model position, velocity, heading, altitude, acceleration, and battery state. | Turn grid movement into a flight simulation. |
| Wind model | Apply wind and gusts to motion, drift, and energy use; vary weather during each mission. | Make atmospheric conditions affect flight behaviour. |
| Terrain | Add 3D terrain clearance, slopes, no-fly zones, and route-feasibility checks. | Evaluate meaningful obstacle avoidance. |
| Safety | Add geofencing, battery reserve, action-rate limits, emergency landing zones, and sensor-failure handling. | Cover safety states beyond weather thresholds. |
| RL observation | Include velocity, heading, altitude, goal distance, local terrain, wind vector, battery, and safety state. | Give the agent enough context to choose safe actions. |
| RL actions | Support climb, descend, turn, speed reduction, hover, return-to-home, and land. | Allow realistic flight decisions. |
| Training | Train across many random seeds and weather trajectories; reward progress, energy efficiency, clearance, and smooth control. | Improve policy coverage and mission completion. |
| Baselines | Compare adaptive RL, static RL, and a rule-based planner with the same safety layer. | Separate policy performance from safety-controller performance. |
| Browser demo | Turn incorrect telemetry or missing overrides into test failures and retain Chrome startup errors. | Make the browser test a reliable integration check. |
| Documentation | State simulation assumptions and measured limits; remove unqualified safety guarantees. | Keep project claims aligned with evidence. |

## Implementation order

1. Define mission outcomes: success, safe return, controlled landing, timeout, and crash.
2. Build the 3D flight and weather environment.
3. Expand the observation and action spaces.
4. Implement safety and emergency-state handling.
5. Train policies and comparable baselines.
6. Run reproducible multi-seed evaluations.
7. Repair and run browser end-to-end tests.
8. Update reports, charts, and project claims.

## Completion checklist

### Mission capability

- [ ] Start and goal positions are valid and reachable.
- [ ] Calm-weather missions achieve at least 80% success on unseen seeds.
- [ ] Moderate-weather missions achieve at least 65% success on unseen seeds.
- [ ] Severe-weather missions have an explicit outcome: success, return-to-home, or controlled landing.
- [ ] Timeouts are counted as mission failures.
- [ ] Safe aborts are reported separately from mission success.

### Safety

- [ ] No collision, geofence breach, unsafe terrain clearance, or battery depletion occurs during evaluation.
- [ ] Each override records its reason, selected safe action, and final outcome.
- [ ] Return-to-home reaches home or transitions to a safe landing state.
- [ ] Hover has a maximum duration and then transitions to return, landing, or abort.
- [ ] Safety tests cover terrain, boundaries, wind, sensors, battery, and controller faults.
- [ ] Safety thresholds are justified by drone specifications or clearly marked as simulation assumptions.

### Learning and evaluation quality

- [ ] Training and evaluation use separate random seeds.
- [ ] Evaluation includes weather sequences not seen during training.
- [ ] Adaptive and static agents use identical safety settings during comparison.
- [ ] A non-RL planner is included as a baseline.
- [ ] Results include confidence intervals across multiple seeds.
- [ ] Results report success, crash, timeout, abort, path length, energy use, reward, and intervention count.

### Test quality

- [ ] Unit tests cover physics, rewards, state conversion, safety decisions, and policy loading.
- [ ] Integration tests run full missions from reset to terminal outcome.
- [ ] Browser tests fail with a nonzero exit code for incorrect telemetry or missing safety intervention.
- [ ] Browser test output includes Chrome launch and connection errors.
- [ ] One documented command runs tests in a clean environment.
- [ ] Evaluation artifacts can be reproduced from documented inputs and seeds.

## Evaluation rules

Evaluate every policy in Calm, Moderate, and Severe weather buckets. Use held-out seeds and report results separately for each bucket.

| Metric | Calculation | Acceptance rule |
|---|---|---|
| Mission success | Reached the goal before timeout with no safety violation. | Calm: at least 80%; Moderate: at least 65%; Severe: report separately. |
| Collision rate | Terrain, boundary, or clearance violations divided by total episodes. | 0% in the simulator. |
| Timeout rate | Timed-out episodes divided by total episodes. | Calm: at most 10%; Moderate: at most 20%. |
| Safe abort rate | Successful return-to-home or controlled landing divided by severe episodes. | Report separately from mission success. |
| Unsafe abort rate | Aborts that collide or deplete battery divided by aborts. | 0%. |
| Safety intervention rate | Safety overrides divided by total control steps. | Report for every bucket; investigate high values. |
| Return-to-home success | Safe home arrival divided by return commands. | At least 95%. |
| Generalization | Difference between held-out and training-distribution metrics. | No more than 10 percentage points for success rate. |
| Adaptive-policy gain | Adaptive result minus static result using identical safety settings. | Report the difference with a confidence interval. |
| Reproducibility | Same code, inputs, seed, and environment regenerate equivalent results. | Document tolerance and verify it in CI. |

## Reporting requirements

Each evaluation report must state:

- Number of episodes, random seeds, terrain maps, and weather trajectories.
- Whether the safety envelope was enabled for each compared policy.
- Mission-success, crash, timeout, safe-abort, and unsafe-abort rates.
- Mean and distribution of energy use, path length, reward, and interventions.
- Known simulation limits and any thresholds based on assumptions rather than vehicle specifications.
