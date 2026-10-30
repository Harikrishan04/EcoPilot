# Phase 2 Checklist: 3D Flight State and Dynamics

## Goal

Replace grid-only movement with a simplified, timestep-based flight model that tracks 3D position, velocity, terrain clearance, wind effects, and battery use.

## Design decisions

- [x] Define the coordinate system and units for horizontal position, altitude, velocity, acceleration, time, terrain elevation, and energy.
- [x] Document the timestep duration and explain how one terrain-grid cell maps to metres.
- [x] Define vehicle limits: maximum horizontal speed, climb and descent rate, altitude floor and ceiling, battery capacity, and minimum terrain clearance.
- [x] State which effects are modelled and which are intentionally simplified, including drag, wind drift, gravity, motor response, and terrain interpolation.
- [x] Preserve compatibility with the current grid-navigation interface during the migration, or document the replacement interface.

## Flight-state implementation

- [x] Track position as `(x, y, z)` or equivalent continuous coordinates.
- [x] Track velocity as `(vx, vy, vz)`.
- [x] Track heading or yaw separately from position.
- [x] Track elapsed simulation time and timestep count.
- [x] Track battery state of charge and total energy consumed.
- [x] Include terrain clearance in observation and telemetry.
- [x] Record a timestamped flight-history entry for each control step.

## Dynamics implementation

- [x] Apply the control action over one fixed timestep.
- [x] Update velocity before position using a documented integration method.
- [x] Enforce maximum horizontal speed, climb rate, descent rate, altitude floor, and altitude ceiling.
- [x] Apply wind vector effects to ground velocity and position drift.
- [x] Apply a simplified drag or damping term so velocity remains physically bounded.
- [x] Apply hovering, climb, descend, horizontal movement, return-to-home, and landing actions consistently.
- [x] Return a clear terminal outcome when terrain, boundary, altitude, or battery constraints are violated.

## Terrain and clearance

- [x] Implement terrain-height lookup for every simulated position.
- [x] Use interpolation when the drone is between terrain-grid cells, or explicitly document nearest-cell sampling.
- [x] Compute clearance as drone altitude minus terrain height.
- [x] Detect terrain collision when clearance is zero or below.
- [x] Detect unsafe flight when clearance is below the configured safety margin.
- [x] Verify that valid spawn, goal, return, and landing locations have adequate clearance.

## Energy model

- [x] Define the battery capacity in watt-hours.
- [x] Calculate energy use from elapsed time and power draw.
- [x] Make hovering consume energy.
- [x] Make climbing consume more energy than level flight.
- [x] Make higher speed and strong headwind increase energy use.
- [x] End the episode with `battery_depleted` if energy reaches zero before a safe terminal outcome.
- [x] Export battery state and energy consumed in episode telemetry.

## Observation and telemetry

- [x] Include altitude, velocity, heading, clearance, wind, battery, goal direction, and distance-to-goal in the environment observation or documented state interface.
- [x] Include position, velocity, clearance, airspeed, power, energy, environmental risk, and outcome in telemetry.
- [x] Ensure telemetry values are calculated from the same state used for the dynamics step.
- [x] Export flight path length and total simulated flight time in evaluation records.

## Test checklist

- [x] Unit test: stationary hover consumes energy and preserves position within tolerance.
- [x] Unit test: climbing increases altitude and energy use.
- [x] Unit test: descending decreases altitude and cannot pass through terrain.
- [x] Unit test: horizontal motion changes position in the expected direction.
- [x] Unit test: wind causes measurable downwind drift.
- [x] Unit test: headwind increases energy use compared with no wind for the same command.
- [x] Unit test: speed, climb rate, altitude floor, and altitude ceiling are enforced.
- [x] Unit test: terrain collision yields the correct terminal outcome.
- [x] Unit test: battery depletion yields the correct terminal outcome.
- [x] Integration test: a complete calm-weather mission reaches the goal with positive clearance and remaining battery.
- [x] Integration test: an unsafe trajectory is intercepted by the safety layer before collision.
- [x] Regression test: fixed seed produces the same trajectory and telemetry on repeated runs.

## Acceptance rules

| Requirement | Acceptance evidence |
|---|---|
| Continuous 3D state | Telemetry includes changing position, velocity, and altitude over several steps. |
| Terrain safety | Collision and low-clearance tests pass for flat terrain, slopes, and ridges. |
| Wind response | The same command under opposing wind directions produces different ground tracks. |
| Energy realism | Hover, climb, speed, and headwind tests show the expected ordering of energy consumption. |
| Constraint enforcement | No evaluated step exceeds configured speed, altitude, climb, or clearance constraints. |
| Terminal outcomes | Collision, battery depletion, success, safe return, controlled landing, and timeout are distinguishable. |
| Reproducibility | Repeating a fixed-seed mission produces byte-identical or tolerance-defined telemetry. |
| Integration | A calm mission completes safely; an emergency case ends in safe return or controlled landing. |

## Required evidence before Phase 2 completion

- [x] Updated environment and dynamics source files.
- [x] Tests covering every acceptance rule above.
- [x] A documented configuration for timestep, vehicle limits, and energy parameters.
- [x] A reproducible sample flight log for calm, moderate-wind, and emergency scenarios.
- [x] Updated evaluation output with path length, simulated flight time, energy, minimum clearance, and terminal outcome.
- [x] Updated README and report that describe the 3D model as a simplified simulation, including its limits.
