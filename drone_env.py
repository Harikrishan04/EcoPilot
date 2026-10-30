"""
drone_env.py — EcoPilot 3D Flight Navigation Environment
=========================================================

Gymnasium-style 3D flight simulation environment for an autonomous micro-aerial
vehicle (MAV) navigating real SRTM elevation terrain (Mantripukhri, Manipur) under
dynamic atmospheric physics, battery energy constraints, and wind drift.

Mission Outcomes (explicitly separated per IMPROVEMENT_PLAN.md):
  - SUCCESS: Reached goal with adequate clearance and battery reserve.
  - SAFE_RTH: Autonomously returned to base safely under severe weather/low battery.
  - CONTROLLED_LANDING: Completed safe descent at an approved flat landing site.
  - TIMEOUT: Exceeded maximum mission step budget.
  - COLLISION_TERRAIN: Contacted terrain relief / ridge.
  - COLLISION_BOUNDARY: Breached geofenced bounding perimeter.
  - BATTERY_DEPLETED: Battery drained to 0% before reaching goal or home.
"""

from __future__ import annotations

import collections
import enum
import heapq
import json
import math
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

from environment_model import (
    air_density,
    calculate_R_env,
    adaptive_lambda,
    wind_components,
    dynamic_pressure,
    battery_power_consumption,
    compute_soc_drain,
    compute_3d_kinematic_drift,
    compute_relative_airspeed,
    KELVIN_OFFSET,
    RHO_0_STANDARD,
    BATTERY_CAPACITY_WH,
)


class MissionOutcome(enum.Enum):
    """Explicit terminal outcomes for flight missions."""
    IN_FLIGHT = "in_flight"
    SUCCESS = "success"
    SAFE_RTH = "safe_rth"
    CONTROLLED_LANDING = "controlled_landing"
    TIMEOUT = "timeout"
    COLLISION_TERRAIN = "terrain_crash"
    COLLISION_BOUNDARY = "boundary_crash"
    ALTITUDE_VIOLATION = "altitude_violation"
    BATTERY_DEPLETED = "battery_depleted"


@dataclass
class FlightTelemetry:
    """Instantaneous 3D flight telemetry snapshot."""
    step: int
    position_3d: Tuple[float, float, float]  # (row, col, altitude_norm)
    velocity_mps: Tuple[float, float, float]  # (vx, vy, vz)
    airspeed_mps: float
    heading_rad: float
    terrain_clearance_norm: float
    battery_soc_pct: float
    power_watts: float
    energy_consumed_wh: float
    r_env: float
    dynamic_pressure_pa: float
    outcome: MissionOutcome = MissionOutcome.IN_FLIGHT
    elapsed_time_s: float = 0.0
    ground_speed_mps: float = 0.0
    position_meters: Tuple[float, float, float] = (0.0, 0.0, 0.0)


class DroneEnv:
    """
    3D Aerodynamic Flight Simulation Environment with real SRTM terrain,
    live atmospheric thermodynamics, wind drift, and battery energy depletion.
    """

    # 12 Discrete Flight Actions:
    # 0..7: 8 Horizontal Cardinal & Intercardinal translations
    # 8: Hover (Station-Keeping)
    # 9: Climb (+ altitude)
    # 10: Descend (- altitude)
    # 11: Return-to-Home (RTH retreat vector)
    ACTION_NAMES = [
        "N", "NE", "E", "SE", "S", "SW", "W", "NW",
        "HOVER", "CLIMB", "DESCEND", "RTH"
    ]

    # Horizontal coordinate deltas for actions 0..7
    ACTION_DELTAS = [
        (-1, 0),   # 0: North
        (-1, 1),   # 1: North-East
        (0, 1),    # 2: East
        (1, 1),    # 3: South-East
        (1, 0),    # 4: South
        (1, -1),   # 5: South-West
        (0, -1),   # 6: West
        (-1, -1),  # 7: North-West
    ]

    ACTION_HEADINGS = [
        0.0,                  # 0: North (0 deg)
        math.pi / 4.0,        # 1: North-East (45 deg)
        math.pi / 2.0,        # 2: East (90 deg)
        3.0 * math.pi / 4.0,  # 3: South-East (135 deg)
        math.pi,              # 4: South (180 deg)
        5.0 * math.pi / 4.0,  # 5: South-West (225 deg)
        3.0 * math.pi / 2.0,  # 6: West (270 deg)
        7.0 * math.pi / 4.0,  # 7: North-West (315 deg)
    ]

    def __init__(
        self,
        terrain_path: Optional[str] = None,
        terrain_grid: Optional[np.ndarray] = None,
        max_steps: Optional[int] = None,
        cruise_altitude: Optional[float] = None,
        drone_speed_mps: Optional[float] = None,
        dt_seconds: Optional[float] = None,
        battery_capacity_wh: Optional[float] = None,
        dynamics_config_path: Optional[str] = "configs/flight_dynamics.json",
    ):
        """
        Initializes the 3D Drone Flight Environment.

        Configuration is loaded from configs/flight_dynamics.json as the single
        source of truth for physical vehicle limits, units, and simulation parameters.

        Args:
            terrain_path: Path to terrain.npy. If None, loads from 'terrain/terrain.npy'.
            terrain_grid: Direct numpy array for terrain elevation.
            max_steps: Maximum step budget per mission episode (overrides config if provided).
            cruise_altitude: Nominal normalized flight plane altitude [0, 1].
            drone_speed_mps: Commanded drone cruise airspeed [m/s].
            dt_seconds: Real-world elapsed seconds represented by one control step.
            battery_capacity_wh: Battery energy capacity in Watt-hours.
            dynamics_config_path: Path to flight dynamics JSON specification.
        """
        if terrain_grid is not None:
            self.terrain = np.array(terrain_grid, dtype=np.float32)
        else:
            if terrain_path is None:
                default_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terrain", "terrain.npy")
                terrain_path = default_path
            if not os.path.isfile(terrain_path):
                raise FileNotFoundError(f"Terrain file not found: {terrain_path}. Run Phase 1 pipeline first.")
            self.terrain = np.load(terrain_path).astype(np.float32)

        self.grid_rows, self.grid_cols = self.terrain.shape

        # ── Load Single Source of Truth for Dynamics & Vehicle Limits ─────────
        self.dynamics_config_path = dynamics_config_path
        self.dynamics_config: Dict[str, Any] = {}
        if dynamics_config_path:
            cfg_p = dynamics_config_path
            if not os.path.isfile(cfg_p):
                alt_p = os.path.join(os.path.dirname(os.path.abspath(__file__)), dynamics_config_path)
                if os.path.isfile(alt_p):
                    cfg_p = alt_p
            if os.path.isfile(cfg_p):
                with open(cfg_p, "r", encoding="utf-8") as f:
                    self.dynamics_config = json.load(f)

        coord_cfg = self.dynamics_config.get("coordinate_system", {})
        sim_cfg = self.dynamics_config.get("simulation", {})
        limits_cfg = self.dynamics_config.get("vehicle_limits", {})

        # Spatial resolution and vertical relief scale
        self.grid_cell_size_m: float = float(coord_cfg.get("spatial_resolution_m_per_cell", 30.0))
        self.vertical_scale_m: float = float(coord_cfg.get("vertical_scale_m", 400.0))

        # Simulation timestep and maximum steps
        self.dt_seconds: float = dt_seconds if dt_seconds is not None else float(sim_cfg.get("dt_seconds", 2.0))
        self.max_steps: int = max_steps if max_steps is not None else int(sim_cfg.get("max_steps", 120))

        # Velocity limits and cruise speed
        self.max_horizontal_speed_mps: float = float(limits_cfg.get("max_horizontal_speed_mps", 12.0))
        self.commanded_cruise_speed_mps: float = (
            drone_speed_mps if drone_speed_mps is not None else float(limits_cfg.get("commanded_cruise_speed_mps", 10.0))
        )
        self.drone_speed_mps: float = self.commanded_cruise_speed_mps

        self.max_climb_rate_mps: float = float(limits_cfg.get("max_climb_rate_mps", 2.5))
        self.commanded_climb_rate_mps: float = float(limits_cfg.get("commanded_climb_rate_mps", 1.5))
        self.max_descent_rate_mps: float = float(limits_cfg.get("max_descent_rate_mps", -2.0))
        self.commanded_descent_rate_mps: float = float(limits_cfg.get("commanded_descent_rate_mps", -1.5))

        # Altitude bounds and safety margins
        self.cruise_altitude: float = (
            cruise_altitude if cruise_altitude is not None else float(limits_cfg.get("cruise_altitude_norm", 0.40))
        )
        self.min_altitude: float = float(limits_cfg.get("min_altitude_norm", 0.15))
        self.max_altitude: float = float(limits_cfg.get("max_altitude_norm", 0.85))
        self.min_clearance_margin: float = float(limits_cfg.get("min_clearance_margin_norm", 0.05))
        self.altitude_limit_behavior: str = str(limits_cfg.get("altitude_limit_behavior", "safety_clamp"))
        self.altitude_excursion_tolerance: float = float(limits_cfg.get("altitude_excursion_tolerance", 0.05))
        self.q_max_pa: float = float(limits_cfg.get("q_max_pa", 120.0))

        # Battery thresholds
        self.battery_capacity_wh: float = (
            battery_capacity_wh if battery_capacity_wh is not None else float(limits_cfg.get("battery_capacity_wh", BATTERY_CAPACITY_WH))
        )
        self.low_battery_soc: float = float(limits_cfg.get("low_battery_soc_pct", 20.0))
        self.critical_battery_soc: float = float(limits_cfg.get("critical_battery_soc_pct", 8.0))

        # Wind drift coupling factors
        self.wind_drift_coupling: float = float(sim_cfg.get("wind_drift_coupling", 0.20))
        self.wind_drift_coupling_hover: float = float(sim_cfg.get("wind_drift_coupling_hover", 0.05))
        self.rng = np.random.default_rng(42)

        # Precompute safe valley cells (elevation well below cruise altitude, inside flight volume)
        self.valley_mask = self.terrain < (self.cruise_altitude - self.min_clearance_margin)
        self.valley_coords: List[Tuple[int, int]] = [
            (r, c) for r in range(1, self.grid_rows - 1) for c in range(1, self.grid_cols - 1) if self.valley_mask[r, c]
        ]
        if not self.valley_coords:
            self.valley_coords = [(2, 2), (self.grid_rows - 3, self.grid_cols - 3)]

        # Precompute safe emergency landing zones (flat valley basins with slope < 0.03)
        self.landing_zones = self._identify_landing_zones()

        # Dynamic continuous 3D state variables
        self.drone_r: float = 2.0
        self.drone_c: float = 2.0
        self.drone_z: float = cruise_altitude
        self.vx_mps: float = 0.0
        self.vy_mps: float = 0.0
        self.vz_mps: float = 0.0
        self.airspeed_mps: float = 0.0
        self.home_r: int = 2
        self.home_c: int = 2
        self.goal_r: int = 20
        self.goal_c: int = 20
        self.heading_rad: float = 0.0
        self.step_count: int = 0
        self.hover_consecutive_steps: int = 0

        # Battery state
        self.battery_soc_pct: float = 100.0
        self.energy_consumed_wh: float = 0.0

        # Atmospheric state variables
        self.wind_speed: float = 0.0
        self.wind_dir_rad: float = 0.0
        self.gust_variance: float = 0.0
        self.temp_k: float = 298.15
        self.pressure_pa: float = 92500.0
        self.rh: float = 0.60
        self.dP_dt: float = 0.0
        self.air_density_val: float = RHO_0_STANDARD
        self.r_env: float = 0.0

        # Mission outcome & telemetry histories
        self.outcome = MissionOutcome.IN_FLIGHT
        self.flight_history: List[Tuple[int, int]] = []
        self.telemetry_history: List[FlightTelemetry] = []

    @property
    def drone_pos(self) -> Tuple[int, int]:
        """Convenience rounded (row, col) integer coordinates."""
        return int(round(self.drone_r)), int(round(self.drone_c))

    @property
    def goal_pos(self) -> Tuple[int, int]:
        """Convenience goal (row, col) coordinates."""
        return self.goal_r, self.goal_c

    def get_terrain_elevation(self, r: float, c: float, method: str = "bilinear") -> float:
        """
        Computes terrain elevation at continuous coordinates (r, c).
        Supports bilinear 4-point surface interpolation (default) and nearest-neighbor sampling.

        Args:
            r: Continuous row coordinate [0, grid_rows - 1].
            c: Continuous column coordinate [0, grid_cols - 1].
            method: 'bilinear' (default) or 'nearest'.

        Returns:
            Normalized terrain elevation in [0.0, 1.0].
        """
        r_clamped = max(0.0, min(float(self.grid_rows - 1), float(r)))
        c_clamped = max(0.0, min(float(self.grid_cols - 1), float(c)))

        if method == "nearest":
            return float(self.terrain[int(round(r_clamped)), int(round(c_clamped))])

        r0 = int(math.floor(r_clamped))
        r1 = min(self.grid_rows - 1, r0 + 1)
        c0 = int(math.floor(c_clamped))
        c1 = min(self.grid_cols - 1, c0 + 1)

        wr = r_clamped - float(r0)
        wc = c_clamped - float(c0)

        h00 = float(self.terrain[r0, c0])
        h10 = float(self.terrain[r1, c0])
        h01 = float(self.terrain[r0, c1])
        h11 = float(self.terrain[r1, c1])

        elev = (1.0 - wr) * (1.0 - wc) * h00 + wr * (1.0 - wc) * h10 + (1.0 - wr) * wc * h01 + wr * wc * h11
        return float(elev)

    def get_continuous_state(self) -> Dict[str, Any]:
        """
        Returns continuous 3D state telemetry dictionary matching Phase 2 interface.
        """
        elev = self.get_terrain_elevation(self.drone_r, self.drone_c)
        clearance = self.drone_z - elev
        ground_speed = math.hypot(self.vx_mps, self.vy_mps)
        return {
            "position_3d": (float(self.drone_r), float(self.drone_c), float(self.drone_z)),
            "position_meters": (
                float(self.drone_c * self.grid_cell_size_m),
                float((self.grid_rows - 1 - self.drone_r) * self.grid_cell_size_m),
                float(self.drone_z * self.vertical_scale_m),
            ),
            "velocity_mps": (float(self.vx_mps), float(self.vy_mps), float(self.vz_mps)),
            "ground_speed_mps": float(ground_speed),
            "airspeed_mps": float(self.airspeed_mps),
            "heading_rad": float(self.heading_rad),
            "terrain_elevation_norm": float(elev),
            "terrain_clearance_norm": float(clearance),
            "battery_soc_pct": float(self.battery_soc_pct),
            "energy_consumed_wh": float(self.energy_consumed_wh),
            "step_count": int(self.step_count),
            "elapsed_time_s": float(self.step_count * self.dt_seconds),
            "r_env": float(self.r_env),
            "outcome": self.outcome.value,
        }

    def compute_continuous_path_length_meters(self) -> float:
        """
        Calculates exact three-dimensional Euclidean path length in metres from continuous telemetry.
        Integrates continuous horizontal displacement, wind drift, and vertical movements.
        """
        if len(self.telemetry_history) < 2:
            return 0.0
        total_m = 0.0
        for t1, t2 in zip(self.telemetry_history[:-1], self.telemetry_history[1:]):
            x1, y1, z1 = t1.position_meters
            x2, y2, z2 = t2.position_meters
            total_m += math.hypot(math.hypot(x2 - x1, y2 - y1), z2 - z1)
        return float(total_m)

    def _identify_landing_zones(self) -> List[Tuple[int, int]]:
        """Identifies flat valley cells suitable for controlled emergency landing."""
        zones = []
        for r, c in self.valley_coords:
            # Check local elevation variance across 3x3 patch
            r_min, r_max = max(0, r - 1), min(self.grid_rows, r + 2)
            c_min, c_max = max(0, c - 1), min(self.grid_cols, c + 2)
            patch = self.terrain[r_min:r_max, c_min:c_max]
            if (np.max(patch) - np.min(patch)) < 0.04 and self.terrain[r, c] < 0.20:
                zones.append((r, c))
        return zones if zones else self.valley_coords[:5]

    def _is_route_feasible(self, start: Tuple[int, int], goal: Tuple[int, int]) -> bool:
        """
        Uses A* graph search over the 3D elevation map to guarantee that a safe,
        clear corridor exists between start and goal before episode launch.
        """
        sr, sc = start
        gr, gc = goal
        if (sr, sc) == (gr, gc):
            return False

        # Priority queue for A*: (f_score, cost, (r, c))
        h_start = math.hypot(gr - sr, gc - sc)
        open_set = [(h_start, 0.0, (sr, sc))]
        visited: Set[Tuple[int, int]] = set()

        while open_set:
            _, g, (curr_r, curr_c) = heapq.heappop(open_set)
            if (curr_r, curr_c) == (gr, gc):
                return True

            if (curr_r, curr_c) in visited:
                continue
            visited.add((curr_r, curr_c))

            for dr, dc in self.ACTION_DELTAS:
                nr, nc = curr_r + dr, curr_c + dc
                if 0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols:
                    if (nr, nc) in visited:
                        continue
                    # Obstacle check: must have clearance beneath cruise altitude
                    if self.terrain[nr, nc] >= (self.cruise_altitude - self.min_clearance_margin):
                        continue
                    new_g = g + math.hypot(dr, dc)
                    h = math.hypot(gr - nr, gc - nc)
                    heapq.heappush(open_set, (new_g + h, new_g, (nr, nc)))

        return False

    def reset(self, seed: Optional[int] = None) -> Tuple[int, int, int, int, int]:
        """
        Resets environment with guaranteed route reachability and domain randomization.

        Returns:
            Discretized observation state tuple.
        """
        self.rng = np.random.default_rng(seed)
        rng = self.rng
        self.step_count = 0
        self.hover_consecutive_steps = 0
        self.battery_soc_pct = 100.0
        self.energy_consumed_wh = 0.0
        self.outcome = MissionOutcome.IN_FLIGHT

        # 1. Randomize start and goal with verified corridor feasibility
        found_feasible = False
        for _ in range(60):
            idx_start = rng.integers(0, len(self.valley_coords))
            idx_goal = rng.integers(0, len(self.valley_coords))
            s_pos = self.valley_coords[idx_start]
            g_pos = self.valley_coords[idx_goal]
            dist = math.hypot(g_pos[0] - s_pos[0], g_pos[1] - s_pos[1])
            if dist >= 7.0 and self._is_route_feasible(s_pos, g_pos):
                self.home_r, self.home_c = s_pos
                self.drone_r, self.drone_c = float(s_pos[0]), float(s_pos[1])
                self.goal_r, self.goal_c = g_pos
                found_feasible = True
                break

        if not found_feasible:
            # Fallback to guaranteed open valley coordinates
            self.home_r, self.home_c = 2, 2
            self.drone_r, self.drone_c = 2.0, 2.0
            self.goal_r, self.goal_c = 14, 18

        self.drone_z = self.cruise_altitude
        self.vx_mps = 0.0
        self.vy_mps = 0.0
        self.vz_mps = 0.0
        self.airspeed_mps = 0.0
        self.heading_rad = math.atan2(self.goal_c - self.drone_c, self.goal_r - self.drone_r)
        self.flight_history = [(int(self.drone_r), int(self.drone_c))]
        self.telemetry_history = []

        # 2. Domain Randomization (Mantripukhri seasonal atmospheric distribution)
        self.wind_speed = float(rng.rayleigh(scale=3.5))
        self.wind_dir_rad = float(rng.uniform(0.0, 2.0 * math.pi))
        self.gust_variance = float(np.clip((self.wind_speed * 0.3) ** 2 + rng.normal(0.2, 0.1), 0.0, 5.0))
        self.temp_k = float(rng.normal(298.15, 3.5))
        self.pressure_pa = float(rng.normal(92500.0, 400.0))
        self.rh = float(rng.uniform(0.40, 0.90))
        self.dP_dt = float(rng.normal(0.0, 1.0))

        # 3. Physics metrics
        self.air_density_val = air_density(self.temp_k, self.pressure_pa, self.rh)
        self.r_env = calculate_R_env(
            wind_speed=self.wind_speed,
            gust_variance=self.gust_variance,
            dP_dt_hpa_h=self.dP_dt,
            rho=self.air_density_val,
        )

        elev0 = self.get_terrain_elevation(self.drone_r, self.drone_c)
        clearance0 = self.drone_z - elev0
        self.telemetry_history.append(
            FlightTelemetry(
                step=0,
                position_3d=(float(self.drone_r), float(self.drone_c), float(self.drone_z)),
                velocity_mps=(0.0, 0.0, 0.0),
                airspeed_mps=0.0,
                heading_rad=float(self.heading_rad),
                terrain_clearance_norm=float(clearance0),
                battery_soc_pct=100.0,
                power_watts=0.0,
                energy_consumed_wh=0.0,
                r_env=float(self.r_env),
                dynamic_pressure_pa=0.0,
                outcome=MissionOutcome.IN_FLIGHT,
                elapsed_time_s=0.0,
                ground_speed_mps=0.0,
                position_meters=(
                    float(self.drone_c * self.grid_cell_size_m),
                    float((self.grid_rows - 1 - self.drone_r) * self.grid_cell_size_m),
                    float(self.drone_z * self.vertical_scale_m),
                ),
            )
        )

        return self.get_state()

    def get_state(self) -> Tuple[int, int, int, int, int]:
        """
        Discretizes continuous 3D state into a compact, informative observation tuple:
          (goal_heading_bin, goal_dist_bin, terrain_clearance_hazard, risk_bin, battery_bin)

        Observation Components:
          - goal_heading_bin (0..7): Which 45-deg compass direction points toward the goal.
          - goal_dist_bin (0..4): Distance quartile (0: reached, 1: near, 2: mid, 3: far, 4: very far).
          - terrain_clearance_hazard (0..2): Vertical obstacle proximity (0: safe, 1: caution, 2: critical).
          - risk_bin (0..3): Atmospheric severity quartile.
          - battery_bin (0..2): Battery charge status (0: reserve <20%, 1: mid 20-50%, 2: nominal >50%).

        Total State Space: 8 x 5 x 3 x 4 x 3 = 1,440 discrete states (lightweight tabular CPU learning).
        """
        dr = self.goal_r - self.drone_r
        dc = self.goal_c - self.drone_c
        dist = math.hypot(dr, dc)

        # 1. Goal Heading Direction (0..7 compass sectors)
        if dist < 0.5:
            goal_heading_bin = 0
        else:
            angle = math.atan2(dc, -dr)  # 0 = North, pi/2 = East
            if angle < 0:
                angle += 2.0 * math.pi
            goal_heading_bin = int(round(angle / (math.pi / 4.0))) % 8

        # 2. Goal Distance Quartile
        if dist < 1.0:
            goal_dist_bin = 0
        elif dist <= 4.0:
            goal_dist_bin = 1
        elif dist <= 8.0:
            goal_dist_bin = 2
        elif dist <= 14.0:
            goal_dist_bin = 3
        else:
            goal_dist_bin = 4

        # 3. 3D Terrain Clearance Hazard
        cur_r = int(np.clip(round(self.drone_r), 0, self.grid_rows - 1))
        cur_c = int(np.clip(round(self.drone_c), 0, self.grid_cols - 1))

        # Check local 3x3 patch clearance
        r_min, r_max = max(0, cur_r - 1), min(self.grid_rows, cur_r + 2)
        c_min, c_max = max(0, cur_c - 1), min(self.grid_cols, cur_c + 2)
        max_local_terrain = float(np.max(self.terrain[r_min:r_max, c_min:c_max]))
        clearance = self.drone_z - max_local_terrain

        if clearance < self.min_clearance_margin:
            clearance_hazard = 2  # Critical obstacle
        elif clearance < (self.min_clearance_margin * 2.5):
            clearance_hazard = 1  # Caution
        else:
            clearance_hazard = 0  # Clear

        # 4. Environmental Risk Quartile
        risk_bin = int(np.clip(math.floor(self.r_env * 4.0), 0, 3))

        # 5. Battery State of Charge Quartile
        if self.battery_soc_pct < self.low_battery_soc:
            battery_bin = 0  # Reserve critical (<20%)
        elif self.battery_soc_pct < 50.0:
            battery_bin = 1  # Moderate (20-50%)
        else:
            battery_bin = 2  # Nominal (>50%)

        return (goal_heading_bin, goal_dist_bin, clearance_hazard, risk_bin, battery_bin)

    def _get_discretized_state(self) -> Tuple[int, int, int, int]:
        """Legacy 4-tuple adapter for backward compatibility with Phase 3 tests."""
        s = self.get_state()
        # Returns (dr_bin, dc_bin, clearance_hazard, risk_bin)
        dr = int(np.clip(round((self.goal_r - self.drone_r) / 4.0), -2, 2))
        dc = int(np.clip(round((self.goal_c - self.drone_c) / 4.0), -2, 2))
        return (dr, dc, s[2], s[3])

    def _record_telemetry(
        self,
        clearance: float,
        power_w: float,
        v_rel: float,
        q_dyn: float,
    ) -> None:
        """Appends an instantaneous FlightTelemetry snapshot to history."""
        ground_speed = math.hypot(self.vx_mps, self.vy_mps)
        self.telemetry_history.append(
            FlightTelemetry(
                step=self.step_count,
                position_3d=(float(self.drone_r), float(self.drone_c), float(self.drone_z)),
                velocity_mps=(float(self.vx_mps), float(self.vy_mps), float(self.vz_mps)),
                airspeed_mps=float(v_rel),
                heading_rad=float(self.heading_rad),
                terrain_clearance_norm=float(clearance),
                battery_soc_pct=float(self.battery_soc_pct),
                power_watts=float(power_w),
                energy_consumed_wh=float(self.energy_consumed_wh),
                r_env=float(self.r_env),
                dynamic_pressure_pa=float(q_dyn),
                outcome=self.outcome,
                elapsed_time_s=float(self.step_count * self.dt_seconds),
                ground_speed_mps=float(ground_speed),
                position_meters=(
                    float(self.drone_c * self.grid_cell_size_m),
                    float((self.grid_rows - 1 - self.drone_r) * self.grid_cell_size_m),
                    float(self.drone_z * self.vertical_scale_m),
                ),
            )
        )

    def step(
        self,
        action: int,
        use_adaptive_reward: bool = True
    ) -> Tuple[Any, float, bool, Dict[str, Any]]:
        """
        Executes one 3D simulation step with kinematics, wind drift, and battery drain.

        Integration method: Semi-implicit Euler / discrete kinematics.
        Velocity is updated from commanded action and wind vector coupling before position update.

        Args:
            action: Action index (0..7 directional, 8: Hover, 9: Climb, 10: Descend, 11: RTH).
            use_adaptive_reward: Whether to weight risk by lambda(R_env).

        Returns:
            Tuple of (next_state, reward, done, info_dict)
        """
        self.step_count += 1
        prev_dist = math.hypot(self.goal_r - self.drone_r, self.goal_c - self.drone_c)

        # Dynamic atmospheric micro-perturbations during flight
        self.wind_speed = max(0.0, self.wind_speed + float(self.rng.normal(0.0, 0.15)))
        self.r_env = calculate_R_env(
            wind_speed=self.wind_speed,
            gust_variance=self.gust_variance,
            dP_dt_hpa_h=self.dP_dt,
            rho=self.air_density_val,
        )

        is_hover = (action == 8)
        vz_cmd = 0.0
        v_cmd_x, v_cmd_y = 0.0, 0.0

        if action < 8:
            # Standard 8-directional movement with commanded cruise speed
            self.heading_rad = self.ACTION_HEADINGS[action]
            v_cmd_x = self.commanded_cruise_speed_mps * math.sin(self.heading_rad)
            v_cmd_y = self.commanded_cruise_speed_mps * math.cos(self.heading_rad)
            self.hover_consecutive_steps = 0

        elif action == 8:
            # Hover (Station-Keeping)
            v_cmd_x = 0.0
            v_cmd_y = 0.0
            vz_cmd = 0.0
            self.hover_consecutive_steps += 1

        elif action == 9:
            # Climb (+ altitude)
            v_cmd_x = 0.0
            v_cmd_y = 0.0
            vz_cmd = self.commanded_climb_rate_mps
            self.hover_consecutive_steps = 0

        elif action == 10:
            # Descend (- altitude)
            v_cmd_x = 0.0
            v_cmd_y = 0.0
            vz_cmd = self.commanded_descent_rate_mps
            self.hover_consecutive_steps = 0

        elif action == 11:
            # Return-to-Home (route towards base)
            dr_home = self.home_r - self.drone_r
            dc_home = self.home_c - self.drone_c
            d_len = math.hypot(dr_home, dc_home)
            if d_len > 0.01:
                self.heading_rad = math.atan2(dc_home, -dr_home)
                v_cmd_x = self.commanded_cruise_speed_mps * math.sin(self.heading_rad)
                v_cmd_y = self.commanded_cruise_speed_mps * math.cos(self.heading_rad)
            self.hover_consecutive_steps = 0

        # ── 1. Simplified 3D Kinematics with Wind Coupling ───────────────────
        # Wind vector components in world frame (from origin azimuth theta_w)
        # theta_w = 0 (from North) -> blows South (-y)
        # theta_w = pi/2 (from East) -> blows West (-x)
        w_x = -self.wind_speed * math.sin(self.wind_dir_rad)
        w_y = -self.wind_speed * math.cos(self.wind_dir_rad)

        # Drift coupling: hover active station-keeping compensates 75% of drift; forward flight couples 20%
        gamma_drift = self.wind_drift_coupling_hover if is_hover else self.wind_drift_coupling

        vx_g = v_cmd_x + (gamma_drift * w_x)
        vy_g = v_cmd_y + (gamma_drift * w_y)
        vz_g = float(np.clip(vz_cmd, self.max_descent_rate_mps, self.max_climb_rate_mps))

        # Enforce maximum horizontal speed limit from flight dynamics configuration
        horiz_speed = math.hypot(vx_g, vy_g)
        if horiz_speed > self.max_horizontal_speed_mps:
            scale = self.max_horizontal_speed_mps / horiz_speed
            vx_g *= scale
            vy_g *= scale

        self.vx_mps = vx_g
        self.vy_mps = vy_g
        self.vz_mps = vz_g

        # ── 2. Position Integration & Altitude Limit Enforcement ──────────────
        step_dc = (vx_g * self.dt_seconds) / self.grid_cell_size_m
        step_dr = -(vy_g * self.dt_seconds) / self.grid_cell_size_m
        step_dz = (vz_g * self.dt_seconds) / self.vertical_scale_m

        next_r = self.drone_r + step_dr
        next_c = self.drone_c + step_dc
        cand_z = self.drone_z + step_dz

        altitude_clamped = False
        altitude_status = "nominal"

        if cand_z > self.max_altitude:
            next_z = self.max_altitude
            self.vz_mps = 0.0
            altitude_clamped = True
            altitude_status = "ceiling_clamped"
            if self.altitude_limit_behavior == "terminal_violation" or cand_z > (self.max_altitude + self.altitude_excursion_tolerance):
                # Uncontrolled altitude excursion beyond allowable tolerance
                self.drone_z = next_z
                self.outcome = MissionOutcome.ALTITUDE_VIOLATION
                ground_elev = self.get_terrain_elevation(next_r, next_c, method="bilinear")
                clearance = self.drone_z - ground_elev
                v_rel = compute_relative_airspeed((self.vx_mps, self.vy_mps, self.vz_mps), self.wind_speed, self.wind_dir_rad)
                q_dyn, _ = dynamic_pressure(self.air_density_val, v_rel, self.q_max_pa)
                power_w = battery_power_consumption(self.air_density_val, v_rel, 0.0, is_hover)
                info = {
                    "r_env": self.r_env,
                    "wind_speed": self.wind_speed,
                    "battery_soc": self.battery_soc_pct,
                    "energy_wh": self.energy_consumed_wh,
                    "power_w": power_w,
                    "dynamic_pressure_pa": q_dyn,
                    "altitude": self.drone_z,
                    "clearance": clearance,
                    "airspeed_mps": v_rel,
                    "ground_speed_mps": horiz_speed,
                    "velocity_mps": (self.vx_mps, self.vy_mps, self.vz_mps),
                    "position_3d": (next_r, next_c, self.drone_z),
                    "elapsed_time_s": self.step_count * self.dt_seconds,
                    "altitude_clamped": True,
                    "altitude_status": altitude_status,
                    "outcome": self.outcome.value,
                    "status": "altitude_violation",
                }
                self._record_telemetry(clearance, power_w, v_rel, q_dyn)
                return self.get_state(), -50.0, True, info
        elif cand_z < self.min_altitude:
            # Check terrain first: if descending into terrain, let terrain collision handler process it
            ground_elev_cand = self.get_terrain_elevation(next_r, next_c, method="bilinear")
            if cand_z <= ground_elev_cand:
                next_z = cand_z
            else:
                next_z = self.min_altitude
                self.vz_mps = 0.0
                altitude_clamped = True
                altitude_status = "floor_clamped"
                if self.altitude_limit_behavior == "terminal_violation" or cand_z < (self.min_altitude - self.altitude_excursion_tolerance):
                    # Uncontrolled altitude excursion below allowable floor
                    self.drone_z = next_z
                    self.outcome = MissionOutcome.ALTITUDE_VIOLATION
                    clearance = self.drone_z - ground_elev_cand
                    v_rel = compute_relative_airspeed((self.vx_mps, self.vy_mps, self.vz_mps), self.wind_speed, self.wind_dir_rad)
                    q_dyn, _ = dynamic_pressure(self.air_density_val, v_rel, self.q_max_pa)
                    power_w = battery_power_consumption(self.air_density_val, v_rel, 0.0, is_hover)
                    info = {
                        "r_env": self.r_env,
                        "wind_speed": self.wind_speed,
                        "battery_soc": self.battery_soc_pct,
                        "energy_wh": self.energy_consumed_wh,
                        "power_w": power_w,
                        "dynamic_pressure_pa": q_dyn,
                        "altitude": self.drone_z,
                        "clearance": clearance,
                        "airspeed_mps": v_rel,
                        "ground_speed_mps": horiz_speed,
                        "velocity_mps": (self.vx_mps, self.vy_mps, self.vz_mps),
                        "position_3d": (next_r, next_c, self.drone_z),
                        "elapsed_time_s": self.step_count * self.dt_seconds,
                        "altitude_clamped": True,
                        "altitude_status": altitude_status,
                        "outcome": self.outcome.value,
                        "status": "altitude_violation",
                    }
                    self._record_telemetry(clearance, power_w, v_rel, q_dyn)
                    return self.get_state(), -50.0, True, info
        else:
            next_z = cand_z

        self.drone_z = float(next_z)

        # ── 3. Aerodynamics & Dynamic Pressure via Vector Air Velocity ────────
        # air_velocity = ground_velocity - wind_velocity
        # airspeed = |air_velocity|
        v_rel = compute_relative_airspeed((self.vx_mps, self.vy_mps, self.vz_mps), self.wind_speed, self.wind_dir_rad)
        self.airspeed_mps = float(v_rel)
        q_dyn, is_gust_crit = dynamic_pressure(self.air_density_val, v_rel, self.q_max_pa)

        # ── 4. Battery Power & Energy Depletion ───────────────────────────────
        power_w = battery_power_consumption(
            rho=self.air_density_val,
            airspeed_mps=v_rel,
            vertical_speed_mps=max(0.0, vz_g),
            is_hover=is_hover,
        )
        soc_drain = compute_soc_drain(power_w, self.dt_seconds, self.battery_capacity_wh)
        self.battery_soc_pct = max(0.0, self.battery_soc_pct - soc_drain)
        self.energy_consumed_wh += power_w * (self.dt_seconds / 3600.0)

        # Continuous bilinear terrain elevation and clearance lookup
        ground_elev = self.get_terrain_elevation(next_r, next_c, method="bilinear")
        clearance = self.drone_z - ground_elev

        # Telemetry snapshot
        ground_speed = math.hypot(self.vx_mps, self.vy_mps)
        info: Dict[str, Any] = {
            "r_env": self.r_env,
            "wind_speed": self.wind_speed,
            "battery_soc": self.battery_soc_pct,
            "energy_wh": self.energy_consumed_wh,
            "power_w": power_w,
            "dynamic_pressure_pa": q_dyn,
            "altitude": self.drone_z,
            "clearance": clearance,
            "airspeed_mps": v_rel,
            "ground_speed_mps": ground_speed,
            "velocity_mps": (self.vx_mps, self.vy_mps, self.vz_mps),
            "position_3d": (next_r, next_c, self.drone_z),
            "elapsed_time_s": self.step_count * self.dt_seconds,
            "altitude_clamped": altitude_clamped,
            "altitude_status": altitude_status,
            "outcome": MissionOutcome.IN_FLIGHT.value,
            "status": "in_flight",
        }

        # ── 5. Boundary Geofence Keep-In Enforcement ──────────────────────────
        if next_r < 0.0 or next_r > (self.grid_rows - 1.0) or next_c < 0.0 or next_c > (self.grid_cols - 1.0):
            # Uncontrolled flyaway beyond outer buffer (> 0.5 cells / 15m)
            if next_r < -0.5 or next_r > (self.grid_rows - 0.5) or next_c < -0.5 or next_c > (self.grid_cols - 0.5):
                self.outcome = MissionOutcome.COLLISION_BOUNDARY
                info["outcome"] = self.outcome.value
                info["status"] = "boundary_crash"
                self._record_telemetry(clearance, power_w, v_rel, q_dyn)
                return self.get_state(), -60.0, True, info

            # Keep-in geofence barrier: clamp within physical flight boundary
            next_r = float(np.clip(next_r, 0.0, self.grid_rows - 1.0))
            next_c = float(np.clip(next_c, 0.0, self.grid_cols - 1.0))
            if next_r <= 0.0 and self.vy_mps > 0:
                self.vy_mps = 0.0
            elif next_r >= (self.grid_rows - 1.0) and self.vy_mps < 0:
                self.vy_mps = 0.0
            if next_c <= 0.0 and self.vx_mps < 0:
                self.vx_mps = 0.0
            elif next_c >= (self.grid_cols - 1.0) and self.vx_mps > 0:
                self.vx_mps = 0.0

            ground_elev = self.get_terrain_elevation(next_r, next_c, method="bilinear")
            clearance = self.drone_z - ground_elev
            info["clearance"] = clearance
            info["position_3d"] = (next_r, next_c, self.drone_z)

        # ── 6. Terrain Clearance / Collision Check ────────────────────────────
        if clearance <= 0.0:
            # Physical collision into terrain relief
            self.drone_r, self.drone_c = next_r, next_c
            self.outcome = MissionOutcome.COLLISION_TERRAIN
            info["outcome"] = self.outcome.value
            info["status"] = "terrain_crash"
            self._record_telemetry(clearance, power_w, v_rel, q_dyn)
            return self.get_state(), -60.0, True, info

        # Update valid drone coordinates
        self.drone_r, self.drone_c = next_r, next_c
        cell_r = int(np.clip(round(next_r), 0, self.grid_rows - 1))
        cell_c = int(np.clip(round(next_c), 0, self.grid_cols - 1))
        self.flight_history.append((cell_r, cell_c))
        curr_dist = math.hypot(self.goal_r - self.drone_r, self.goal_c - self.drone_c)

        # ── 7. Battery Depletion Check ────────────────────────────────────────
        if self.battery_soc_pct <= 0.0:
            self.outcome = MissionOutcome.BATTERY_DEPLETED
            info["outcome"] = self.outcome.value
            info["status"] = "battery_depleted"
            self._record_telemetry(clearance, power_w, v_rel, q_dyn)
            return self.get_state(), -40.0, True, info

        # ── 8. Goal Reached Check ─────────────────────────────────────────────
        if curr_dist <= 1.2:
            self.outcome = MissionOutcome.SUCCESS
            info["outcome"] = self.outcome.value
            info["status"] = "success"
            success_reward = 80.0 + (self.battery_soc_pct * 0.2)  # Bonus for battery efficiency
            self._record_telemetry(clearance, power_w, v_rel, q_dyn)
            return self.get_state(), float(success_reward), True, info

        # ── 9. Safe Return-to-Home & Controlled Landing Check ─────────────────
        dist_home = math.hypot(self.home_r - self.drone_r, self.home_c - self.drone_c)
        is_emergency_condition = (self.r_env > 0.80 or self.battery_soc_pct < self.low_battery_soc)

        # Check controlled emergency landing in nearest flat landing zone (prioritized if battery critical)
        if (self.battery_soc_pct <= 10.0 or action == 10) and self.step_count > 0:
            nearest_lz_dist = min(math.hypot(lz[0] - self.drone_r, lz[1] - self.drone_c) for lz in self.landing_zones)
            if nearest_lz_dist <= 1.2:
                self.outcome = MissionOutcome.CONTROLLED_LANDING
                info["outcome"] = self.outcome.value
                info["status"] = "controlled_landing"
                land_reward = 30.0
                self._record_telemetry(clearance, power_w, v_rel, q_dyn)
                return self.get_state(), float(land_reward), True, info

        if dist_home <= 1.2 and (action == 11 or is_emergency_condition) and self.step_count > 2:
            self.outcome = MissionOutcome.SAFE_RTH
            info["outcome"] = self.outcome.value
            info["status"] = "safe_rth"
            rth_reward = 35.0  # Safe recovery reward
            self._record_telemetry(clearance, power_w, v_rel, q_dyn)
            return self.get_state(), float(rth_reward), True, info

        # ── 10. Timeout Check ─────────────────────────────────────────────────
        if self.step_count >= self.max_steps:
            self.outcome = MissionOutcome.TIMEOUT
            info["outcome"] = self.outcome.value
            info["status"] = "timeout"
            self._record_telemetry(clearance, power_w, v_rel, q_dyn)
            return self.get_state(), -15.0, True, info

        # ── 11. Continuous Reward Function ────────────────────────────────────
        w_along, w_cross = wind_components(self.wind_speed, self.wind_dir_rad, self.heading_rad)
        progress = (prev_dist - curr_dist) * 8.0
        time_penalty = 0.15
        clearance_penalty = max(0.0, (self.min_clearance_margin * 2.0 - clearance) * 20.0)
        energy_penalty = (power_w / 300.0) * 0.10
        gust_penalty = (q_dyn / 120.0) * 1.5 if is_gust_crit else (q_dyn / 120.0) * 0.4
        total_risk = (abs(w_cross) / 10.0) + clearance_penalty + gust_penalty

        if use_adaptive_reward:
            lambda_weight = adaptive_lambda(self.r_env, lambda0=1.0, beta=3.0)
        else:
            lambda_weight = 1.0

        step_reward = progress - time_penalty - energy_penalty - (lambda_weight * total_risk)
        self._record_telemetry(clearance, power_w, v_rel, q_dyn)

        return self.get_state(), float(step_reward), False, info
