"""
drone_env.py — EcoPilot Phase 3: Drone Navigation Environment
=============================================================

Gymnasium-style reinforcement learning environment simulating an autonomous drone
navigating real elevation terrain (Mantripukhri, Imphal West, Manipur) under
dynamic atmospheric conditions (wind, humidity, barometric pressure).

State Space (Discretized for Tabular Q-Learning):
  Tuple: (delta_row_bin, delta_col_bin, terrain_hazard, risk_bin)
    - delta_row_bin: Target goal relative row bucket in {-2, -1, 0, 1, 2}
    - delta_col_bin: Target goal relative col bucket in {-2, -1, 0, 1, 2}
    - terrain_hazard: Local terrain obstacle hazard in {0: Clear, 1: Foothill, 2: Ridge}
    - risk_bin: Discretized environmental risk R_env in {0: Calm, 1: Moderate, 2: Windy, 3: Severe}

Action Space:
  8 Discrete horizontal directions on the 24x24 grid:
    0: N (-1, 0)   1: NE (-1, 1)  2: E (0, 1)    3: SE (1, 1)
    4: S (1, 0)    5: SW (1, -1)  6: W (0, -1)   7: NW (-1, -1)
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict, Optional, Tuple

import numpy as np

from environment_model import (
    air_density,
    calculate_R_env,
    adaptive_lambda,
    wind_components,
    dynamic_pressure,
    KELVIN_OFFSET,
    RHO_0_STANDARD,
)


class DroneEnv:
    """
    RL Environment for drone navigation over real SRTM elevation terrain with
    atmospheric risk conditioning.
    """

    # 8-directional movement deltas and corresponding heading angles (radians)
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
        0.0,                # 0: North (0 deg)
        math.pi / 4.0,      # 1: North-East (45 deg)
        math.pi / 2.0,      # 2: East (90 deg)
        3.0 * math.pi / 4.0,# 3: South-East (135 deg)
        math.pi,            # 4: South (180 deg)
        5.0 * math.pi / 4.0,# 5: South-West (225 deg)
        3.0 * math.pi / 2.0,# 6: West (270 deg)
        7.0 * math.pi / 4.0,# 7: North-West (315 deg)
    ]

    def __init__(
        self,
        terrain_path: Optional[str] = None,
        terrain_grid: Optional[np.ndarray] = None,
        max_steps: int = 100,
        cruise_altitude: float = 0.40,  # Normalized flight plane altitude
        drone_speed_mps: float = 8.0,   # Nominal drone cruise speed [m/s]
    ):
        """
        Initializes the drone environment.

        Args:
            terrain_path: Path to terrain.npy. If None, loads from 'terrain/terrain.npy'.
            terrain_grid: Direct numpy array for terrain.
            max_steps: Maximum steps allowed before episode termination.
            cruise_altitude: Normalised flight altitude [0.0, 1.0].
            drone_speed_mps: Drone nominal speed relative to air [m/s].
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
        self.max_steps = max_steps
        self.cruise_altitude = cruise_altitude
        self.drone_speed_mps = drone_speed_mps

        # Precompute low-elevation (valley floor) spawn cells for safe mission start/goal
        valley_mask = self.terrain < (self.cruise_altitude * 0.75)
        self.valley_coords = [
            (r, c) for r in range(self.grid_rows) for c in range(self.grid_cols) if valley_mask[r, c]
        ]
        if not self.valley_coords:
            self.valley_coords = [(0, 0), (self.grid_rows - 1, self.grid_cols - 1)]

        # Episode state variables
        self.drone_pos = (0, 0)
        self.goal_pos = (0, 0)
        self.step_count = 0

        # Atmospheric episode variables
        self.wind_speed: float = 0.0
        self.wind_dir_rad: float = 0.0
        self.gust_variance: float = 0.0
        self.temp_k: float = 298.15
        self.pressure_pa: float = 92500.0
        self.rh: float = 0.60
        self.dP_dt: float = 0.0
        self.air_density_val: float = RHO_0_STANDARD
        self.r_env: float = 0.0

    def reset(self, seed: Optional[int] = None) -> Tuple[int, int, int, int]:
        """
        Resets environment for a new episode with domain randomization.

        Returns:
            Initial discretized state tuple.
        """
        rng = np.random.default_rng(seed)
        self.step_count = 0

        # 1. Randomize spawn and goal positions with guaranteed separation
        for _ in range(50):
            idx_start = rng.integers(0, len(self.valley_coords))
            idx_goal = rng.integers(0, len(self.valley_coords))
            s_pos = self.valley_coords[idx_start]
            g_pos = self.valley_coords[idx_goal]
            dist = math.hypot(g_pos[0] - s_pos[0], g_pos[1] - s_pos[1])
            if dist >= 8.0:  # Minimum distance to learn meaningful path
                self.drone_pos = s_pos
                self.goal_pos = g_pos
                break
        else:
            self.drone_pos = (2, 2)
            self.goal_pos = (self.grid_rows - 4, self.grid_cols - 4)

        # 2. Domain Randomization (Mantripukhri seasonal meteorological distribution)
        # Wind magnitude follows a Rayleigh distribution (mode ~ 3.5 m/s)
        self.wind_speed = float(rng.rayleigh(scale=3.5))
        self.wind_dir_rad = float(rng.uniform(0.0, 2.0 * math.pi))
        # Gust variance proportional to wind speed with noise
        self.gust_variance = float(np.clip((self.wind_speed * 0.3) ** 2 + rng.normal(0.2, 0.1), 0.0, 5.0))
        # Ambient temperature centered at 25C (298.15K) +/- 5C
        self.temp_k = float(rng.normal(298.15, 3.5))
        # Atmospheric pressure centered at 925 hPa (~780m valley elevation)
        self.pressure_pa = float(rng.normal(92500.0, 400.0))
        # Relative humidity [40%, 90%]
        self.rh = float(rng.uniform(0.40, 0.90))
        # Pressure rate of change [hPa/h]
        self.dP_dt = float(rng.normal(0.0, 1.0))

        # 3. Calculate physics metrics for this episode
        self.air_density_val = air_density(self.temp_k, self.pressure_pa, self.rh)
        self.r_env = calculate_R_env(
            wind_speed=self.wind_speed,
            gust_variance=self.gust_variance,
            dP_dt_hpa_h=self.dP_dt,
            rho=self.air_density_val
        )

        return self._get_discretized_state()

    def _get_discretized_state(self) -> Tuple[int, int, int, int]:
        """
        Discretizes continuous coordinates and environment metrics into a compact,
        hashable state tuple for tabular Q-learning.

        State format: (dr_bin, dc_bin, terrain_hazard, risk_bin)
        """
        dr = self.goal_pos[0] - self.drone_pos[0]
        dc = self.goal_pos[1] - self.drone_pos[1]

        # Discretize relative goal distance into 5 bins {-2, -1, 0, 1, 2}
        # Step of 4 cells across the 24x24 grid
        dr_bin = int(np.clip(round(dr / 4.0), -2, 2))
        dc_bin = int(np.clip(round(dc / 4.0), -2, 2))

        # Terrain clearance & neighbor sensing:
        # Check current cell and 8 adjacent neighbors for high relief
        r, c = self.drone_pos
        current_elevation = self.terrain[r, c]

        # Scan 8 neighbors for maximum relief
        max_neighbor_elevation = current_elevation
        for dr_step in (-1, 0, 1):
            for dc_step in (-1, 0, 1):
                nr, nc = r + dr_step, c + dc_step
                if 0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols:
                    max_neighbor_elevation = max(max_neighbor_elevation, self.terrain[nr, nc])

        # Hazard classification:
        # 0: Low flat terrain (clear valley)
        # 1: Moderate foothill slope
        # 2: Severe ridge / terrain obstacle near or above cruise altitude
        if max_neighbor_elevation >= self.cruise_altitude:
            terrain_hazard = 2
        elif max_neighbor_elevation >= (self.cruise_altitude * 0.65):
            terrain_hazard = 1
        else:
            terrain_hazard = 0

        # Discretize continuous R_env in [0, 1] into 4 bins:
        # 0: Calm [0, 0.25), 1: Moderate [0.25, 0.50), 2: Windy [0.50, 0.75), 3: Severe [0.75, 1.0]
        risk_bin = int(np.clip(math.floor(self.r_env * 4.0), 0, 3))

        return (dr_bin, dc_bin, terrain_hazard, risk_bin)

    def step(
        self,
        action: int,
        use_adaptive_reward: bool = True
    ) -> Tuple[Tuple[int, int, int, int], float, bool, Dict[str, Any]]:
        """
        Executes one transition step in the environment.

        Args:
            action: Integer in 0..7 representing 8-directional movement.
            use_adaptive_reward: If True, scales risk penalty by lambda(R_env).
                                 If False (static baseline), uses fixed lambda0 = 1.0.

        Returns:
            Tuple of (next_state, reward, done, info_dict)
        """
        self.step_count += 1
        prev_dist = math.hypot(self.goal_pos[0] - self.drone_pos[0], self.goal_pos[1] - self.drone_pos[1])

        delta_r, delta_c = self.ACTION_DELTAS[action]
        next_r = self.drone_pos[0] + delta_r
        next_c = self.drone_pos[1] + delta_c

        info: Dict[str, Any] = {
            "r_env": self.r_env,
            "wind_speed": self.wind_speed,
            "status": "in_flight"
        }

        # ── 1. Boundary Check ─────────────────────────────────────────────────
        if not (0 <= next_r < self.grid_rows and 0 <= next_c < self.grid_cols):
            # Crashed into boundary
            info["status"] = "boundary_crash"
            crash_penalty = -50.0
            return self._get_discretized_state(), crash_penalty, True, info

        # ── 2. Terrain Collision Check ────────────────────────────────────────
        terrain_height = self.terrain[next_r, next_c]
        if terrain_height >= self.cruise_altitude:
            # Drone collided with ridge
            self.drone_pos = (next_r, next_c)
            info["status"] = "terrain_crash"
            crash_penalty = -50.0
            return self._get_discretized_state(), crash_penalty, True, info

        # Move drone to valid coordinate
        self.drone_pos = (next_r, next_c)
        curr_dist = math.hypot(self.goal_pos[0] - self.drone_pos[0], self.goal_pos[1] - self.drone_pos[1])

        # ── 3. Goal Check ─────────────────────────────────────────────────────
        if self.drone_pos == self.goal_pos:
            info["status"] = "success"
            goal_reward = 50.0
            return self._get_discretized_state(), goal_reward, True, info

        # ── 4. Timeout Check ──────────────────────────────────────────────────
        if self.step_count >= self.max_steps:
            info["status"] = "timeout"
            timeout_penalty = -10.0
            return self._get_discretized_state(), timeout_penalty, True, info

        # ── 5. Continuous Reward Formulation ──────────────────────────────────
        # Progress component (Euclidean distance reduction)
        progress = (prev_dist - curr_dist) * 5.0

        # Step time penalty (encourages direct, efficient routes)
        time_penalty = 0.10

        # Aerodynamic Risk Penalty:
        # Heading vs wind decomposition
        heading = self.ACTION_HEADINGS[action]
        w_along, w_cross = wind_components(self.wind_speed, self.wind_dir_rad, heading)

        # Dynamic pressure relative airspeed
        v_rel = math.hypot(self.drone_speed_mps - w_along, w_cross)
        q_dyn, is_gust_crit = dynamic_pressure(self.air_density_val, v_rel)

        # Risk penalty components:
        # Crosswind lateral drift strain + terrain proximity + dynamic pressure load
        crosswind_penalty = abs(w_cross) / 10.0
        terrain_proximity_penalty = (terrain_height / self.cruise_altitude) * 2.0
        gust_penalty = (q_dyn / 120.0) * 1.5 if is_gust_crit else (q_dyn / 120.0) * 0.5
        total_risk_penalty = crosswind_penalty + terrain_proximity_penalty + gust_penalty

        # Compute adaptive lambda vs static baseline lambda
        if use_adaptive_reward:
            lambda_weight = adaptive_lambda(self.r_env, lambda0=1.0, beta=3.0)
        else:
            lambda_weight = 1.0  # Static baseline ignores dynamic R_env

        reward = progress - time_penalty - (lambda_weight * total_risk_penalty)

        return self._get_discretized_state(), float(reward), False, info

