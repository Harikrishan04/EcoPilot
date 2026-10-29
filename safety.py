"""
safety.py — EcoPilot Phase 4: Independent Hard-Coded Safety Envelope
===================================================================

Implements an independent flight safety override layer that sits between the
learned RL policy (Q-table) and the drone flight controller.

Hard Constraints (from project specification):
  - Always implemented as logic INDEPENDENT of the Q-table.
  - Never let the learned policy be the only barrier between the drone and a crash.
  - If R_env > R_critical or q > q_max, forces Hover / Return-to-Base (RTB) regardless
    of the policy's chosen action.

Decision Logic:
  1. Check Environmental Risk: R_env > R_critical (default 0.85)
  2. Check Dynamic Pressure / Gust Load: q > q_max (default 120.0 Pa)
  3. Check Imminent Terrain Collision: Next cell elevation >= cruise_altitude
  4. If safe: Allow policy action through unchanged.
  5. If unsafe: Override action, switch flight mode to HOVER_HOLD or RETURN_TO_BASE.
"""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np


class FlightMode(enum.Enum):
    """Drone operational flight modes."""
    POLICY_DRIVEN = "POLICY_DRIVEN"   # Normal operation governed by Q-table
    HOVER_HOLD = "HOVER_HOLD"         # Maintain current coordinates in place
    RETURN_TO_BASE = "RETURN_TO_BASE" # Autonomously route back toward home spawn
    EMERGENCY_LAND = "EMERGENCY_LAND" # Controlled descent (severe envelope breach)


# Action indices matching DroneEnv (0..7) + Special Hover action (8)
ACTION_HOVER = 8
ACTION_CLIMB = 9
ACTION_DESCEND = 10
ACTION_RTH = 11
ACTION_DELTAS = [
    (-1, 0),   # 0: North
    (-1, 1),   # 1: North-East
    (0, 1),    # 2: East
    (1, 1),    # 3: South-East
    (1, 0),    # 4: South
    (1, -1),   # 5: South-West
    (0, -1),   # 6: West
    (-1, -1),  # 7: North-West
    (0, 0),    # 8: Hover (Hold Position)
]


@dataclass
class SafetyIntervention:
    """Detailed record of a safety envelope evaluation and potential intervention."""
    is_overridden: bool
    flight_mode: FlightMode
    executed_action: int
    original_policy_action: int
    trigger_reasons: List[str] = field(default_factory=list)
    r_env: float = 0.0
    dynamic_pressure_pa: float = 0.0
    terrain_clearance: float = 1.0


class SafetyEnvelope:
    """
    Deterministic, fail-safe safety governor that inspects and overrides
    RL policy actions before physical actuator execution.
    """

    def __init__(
        self,
        r_critical: float = 0.85,            # Maximum tolerable environmental risk score [0, 1]
        q_max_pa: float = 120.0,             # Maximum allowable dynamic pressure [Pa]
        terrain_safety_margin: float = 0.02, # Altitude buffer above terrain [0, 1]
        max_hover_steps: int = 4,            # Maximum allowable consecutive hover steps
        battery_reserve_pct: float = 20.0,   # Minimum battery reserve before forced RTH [%]
        battery_critical_pct: float = 8.0,   # Critical battery threshold before emergency landing [%]
        **kwargs,
    ):
        """
        Initializes the enhanced safety envelope.

        Args:
            r_critical: Threshold of composite risk R_env triggering abort/hover.
            q_max_pa: Dynamic pressure limit above which gust loading is unsafe.
            terrain_safety_margin: Buffer between cruise altitude and terrain elevation.
            max_hover_steps: Duration limit for hover station-keeping before forced abort.
            battery_reserve_pct: Battery State of Charge triggering Return-to-Home.
            battery_critical_pct: Battery State of Charge forcing Emergency Landing.
        """
        if "low_battery_soc" in kwargs:
            battery_reserve_pct = kwargs.pop("low_battery_soc")
        self.r_critical = r_critical
        self.q_max_pa = q_max_pa
        self.terrain_safety_margin = terrain_safety_margin
        self.max_hover_steps = max_hover_steps
        self.battery_reserve_pct = battery_reserve_pct
        self.battery_critical_pct = battery_critical_pct

    def evaluate(
        self,
        policy_action: int,
        current_pos: Tuple[int, int],
        home_pos: Tuple[int, int],
        r_env: float,
        dynamic_pressure_pa: float,
        terrain_grid: np.ndarray,
        cruise_altitude: float = 0.40,
        battery_soc_pct: float = 100.0,
        consecutive_hover_steps: int = 0,
        landing_zones: Optional[List[Tuple[int, int]]] = None,
    ) -> SafetyIntervention:
        """
        Evaluates the current state against the hard safety envelope.

        If any safety constraint is violated, the policy action is strictly
        bypassed and replaced with an autonomous safe maneuver (Hover, RTB, or Land).

        Args:
            policy_action: Action integer in 0..7 (or hover 8) chosen by Q-table.
            current_pos: Drone current coordinate (row, col).
            home_pos: Drone home/spawn base coordinate (row, col).
            r_env: Composite environmental risk score in [0.0, 1.0].
            dynamic_pressure_pa: Instantaneous dynamic pressure q [Pa].
            terrain_grid: 2D numpy array of normalized terrain heights.
            cruise_altitude: Normalized flight altitude plane.
            battery_soc_pct: Remaining battery State of Charge [%].
            consecutive_hover_steps: Number of continuous steps spent in hover.
            landing_zones: Optional list of precomputed emergency landing coordinates.

        Returns:
            SafetyIntervention record containing executed action and flight mode.
        """
        triggers: List[str] = []
        rows, cols = terrain_grid.shape
        cur_r = int(np.clip(round(current_pos[0]), 0, rows - 1))
        cur_c = int(np.clip(round(current_pos[1]), 0, cols - 1))

        # ── Check 1: Critical Battery Depletion ───────────────────────────────
        if battery_soc_pct <= self.battery_critical_pct:
            triggers.append(f"CRITICAL_BATTERY ({battery_soc_pct:.1f}% <= {self.battery_critical_pct:.1f}%)")
        elif battery_soc_pct <= self.battery_reserve_pct:
            triggers.append(f"LOW_BATTERY_RESERVE ({battery_soc_pct:.1f}% <= {self.battery_reserve_pct:.1f}%)")

        # ── Check 2: Environmental Storm Risk Breach ──────────────────────────
        if r_env > self.r_critical:
            triggers.append(f"CRITICAL_R_ENV ({r_env:.3f} > {self.r_critical:.3f})")

        # ── Check 3: Aerodynamic Gust / Dynamic Pressure Overload ─────────────
        if dynamic_pressure_pa > self.q_max_pa:
            triggers.append(f"EXCESSIVE_DYNAMIC_PRESSURE ({dynamic_pressure_pa:.1f} Pa > {self.q_max_pa:.1f} Pa)")

        # ── Check 4: Imminent Terrain Obstacle or Boundary Breach ──────────────
        dr, dc = ACTION_DELTAS[policy_action] if policy_action < len(ACTION_DELTAS) else (0, 0)
        next_r, next_c = cur_r + dr, cur_c + dc

        out_of_bounds = not (0 <= next_r < rows and 0 <= next_c < cols)
        if out_of_bounds:
            triggers.append(f"BOUNDARY_BREACH (Target ({next_r},{next_c}) outside {rows}x{cols})")
        else:
            predicted_height = terrain_grid[next_r, next_c]
            clearance = cruise_altitude - predicted_height
            if clearance < self.terrain_safety_margin:
                triggers.append(f"TERRAIN_COLLISION_RISK (Clearance {clearance:.3f} < {self.terrain_safety_margin:.3f})")

        # ── Decision Logic ────────────────────────────────────────────────────
        current_clearance = cruise_altitude - terrain_grid[cur_r, cur_c]
        if not triggers:
            # All safety criteria satisfied: execute policy action as intended
            return SafetyIntervention(
                is_overridden=False,
                flight_mode=FlightMode.POLICY_DRIVEN,
                executed_action=policy_action,
                original_policy_action=policy_action,
                r_env=r_env,
                dynamic_pressure_pa=dynamic_pressure_pa,
                terrain_clearance=current_clearance,
            )

        # ── Override Triggered: Formulate Safe Action ─────────────────────────
        # Rule: Hover has a strict maximum duration. If exceeded, force RTH or Landing!
        hover_exhausted = (consecutive_hover_steps >= self.max_hover_steps)

        if battery_soc_pct <= self.battery_critical_pct:
            # Emergency landing at nearest valley zone
            safe_action = self._calculate_landing_action(current_pos, landing_zones, terrain_grid, cruise_altitude)
            chosen_mode = FlightMode.EMERGENCY_LAND

        elif (r_env > 0.95 or dynamic_pressure_pa > (self.q_max_pa * 1.3)) and not hover_exhausted:
            # Brief emergency station-keeping (max 4 steps)
            safe_action = ACTION_HOVER
            chosen_mode = FlightMode.HOVER_HOLD

        else:
            # Orderly Return-To-Base (RTB): select retreat action routing toward home_pos
            safe_action = self._calculate_rtb_action(current_pos, home_pos, terrain_grid, cruise_altitude)
            chosen_mode = FlightMode.RETURN_TO_BASE

        current_clearance = cruise_altitude - terrain_grid[cur_r, cur_c]
        return SafetyIntervention(
            is_overridden=True,
            flight_mode=chosen_mode,
            executed_action=safe_action,
            original_policy_action=policy_action,
            trigger_reasons=triggers,
            r_env=r_env,
            dynamic_pressure_pa=dynamic_pressure_pa,
            terrain_clearance=current_clearance,
        )

    def _calculate_landing_action(
        self,
        current_pos: Tuple[int, int],
        landing_zones: Optional[List[Tuple[int, int]]],
        terrain_grid: np.ndarray,
        cruise_altitude: float,
    ) -> int:
        """Determines best vector toward nearest flat landing zone."""
        if not landing_zones:
            return ACTION_HOVER
        cur_r, cur_c = current_pos
        # Find nearest landing zone
        best_lz = min(landing_zones, key=lambda lz: math.hypot(lz[0] - cur_r, lz[1] - cur_c))
        if math.hypot(best_lz[0] - cur_r, best_lz[1] - cur_c) <= 1.0:
            return ACTION_DESCEND
        return self._calculate_rtb_action(current_pos, best_lz, terrain_grid, cruise_altitude)

    def _calculate_rtb_action(
        self,
        current_pos: Tuple[int, int],
        home_pos: Tuple[int, int],
        terrain_grid: np.ndarray,
        cruise_altitude: float,
    ) -> int:
        """
        Determines the safest adjacent action directing the drone toward home_pos
        while avoiding high-relief terrain cells.
        """
        rows, cols = terrain_grid.shape
        cur_r, cur_c = current_pos
        home_r, home_c = home_pos

        if math.hypot(home_r - cur_r, home_c - cur_c) <= 0.8:
            return ACTION_HOVER

        best_action = ACTION_HOVER
        best_cost = float("inf")

        for action_idx in range(8):
            dr, dc = ACTION_DELTAS[action_idx]
            cand_r, cand_c = cur_r + dr, cur_c + dc

            # Must be inside bounds
            if not (0 <= cand_r < rows and 0 <= cand_c < cols):
                continue

            # Must not hit terrain
            cand_height = terrain_grid[cand_r, cand_c]
            if cand_height >= (cruise_altitude - self.terrain_safety_margin):
                continue

            # Distance toward home base
            dist_home = math.hypot(home_r - cand_r, home_c - cand_c)
            # Route cost penalizes terrain height along the retreat path
            cost = dist_home + (cand_height * 4.0)

            if cost < best_cost:
                best_cost = cost
                best_action = action_idx

        return best_action


# Convenience standalone function matching project specification
def safety_override(
    chosen_action: int,
    current_pos: Tuple[int, int],
    home_pos: Tuple[int, int],
    r_env: float,
    dynamic_pressure_pa: float,
    terrain_grid: np.ndarray,
    r_critical: float = 0.85,
    q_max_pa: float = 120.0,
    cruise_altitude: float = 0.40,
) -> Tuple[int, bool, str]:
    """
    Hard safety override function independent of the Q-table.

    Returns:
        Tuple of (executed_action, is_overridden, reason_string)
    """
    envelope = SafetyEnvelope(r_critical=r_critical, q_max_pa=q_max_pa)
    intervention = envelope.evaluate(
        policy_action=chosen_action,
        current_pos=current_pos,
        home_pos=home_pos,
        r_env=r_env,
        dynamic_pressure_pa=dynamic_pressure_pa,
        terrain_grid=terrain_grid,
        cruise_altitude=cruise_altitude,
    )
    reason = "; ".join(intervention.trigger_reasons) if intervention.is_overridden else "NOMINAL"
    return intervention.executed_action, intervention.is_overridden, reason

