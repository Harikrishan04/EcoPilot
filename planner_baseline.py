"""
planner_baseline.py — EcoPilot Non-RL Rule-Based A* Planner Baseline
=====================================================================

Implements a deterministic A* / heuristic potential-field pathfinding planner
serving as an external non-RL baseline benchmark.

Operates with the exact same safety envelope and environmental constraints
as the RL agents to isolate policy decision quality from safety controller actions.
"""

from __future__ import annotations

import heapq
import math
from typing import List, Optional, Set, Tuple

import numpy as np


class RuleBasedPlanner:
    """
    Deterministic A* pathfinding planner for 3D terrain navigation.
    Computes shortest obstacle-clearing path and issues directional movement actions.
    """

    ACTION_DELTAS = [
        (-1, 0),   # 0: North
        (-1, 1),   # 1: North-East
        (0, 1),    # 2: East
        (1, 1),    # 3: South-East
        (1, 0),    # 4: South
        (1, -1),   # 5: South-West
        (0, -1),   # 6: West
        (-1, -1),  # 7: North-West
        (0, 0),    # 8: Hover
    ]

    def __init__(
        self,
        terrain_grid: np.ndarray,
        cruise_altitude: float = 0.40,
        safety_margin: float = 0.04,
        name: str = "RuleBasedAStarPlanner"
    ):
        self.terrain = np.array(terrain_grid, dtype=np.float32)
        self.grid_rows, self.grid_cols = self.terrain.shape
        self.cruise_altitude = cruise_altitude
        self.safety_margin = safety_margin
        self.name = name

    def select_action(
        self,
        current_pos: Tuple[int, int],
        goal_pos: Tuple[int, int],
        training: bool = False
    ) -> int:
        """
        Plans next step toward goal using A* shortest path over the elevation map.

        Args:
            current_pos: (row, col) integer coordinates.
            goal_pos: (row, col) goal coordinates.
            training: Dummy argument for interface compatibility with QAgent.

        Returns:
            Action integer in 0..7 (or 8 for hover if trapped/reached).
        """
        cur_r, cur_c = current_pos
        goal_r, goal_c = goal_pos

        if (cur_r, cur_c) == (goal_r, goal_c):
            return 8  # Reached -> Hover

        path = self._find_astar_path(current_pos, goal_pos)
        if path and len(path) > 1:
            next_r, next_c = path[1]
            dr = next_r - cur_r
            dc = next_c - cur_c
            for idx, (delta_r, delta_c) in enumerate(self.ACTION_DELTAS[:8]):
                if (delta_r, delta_c) == (dr, dc):
                    return idx

        # Fallback: greedy Euclidean direction minimizing elevation cost
        best_act = 8
        best_cost = float("inf")
        for idx, (dr, dc) in enumerate(self.ACTION_DELTAS[:8]):
            nr, nc = cur_r + dr, cur_c + dc
            if 0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols:
                elev = self.terrain[nr, nc]
                if elev < (self.cruise_altitude - self.safety_margin):
                    dist = math.hypot(goal_r - nr, goal_c - nc)
                    cost = dist + (elev * 5.0)
                    if cost < best_cost:
                        best_cost = cost
                        best_act = idx

        return best_act

    def _find_astar_path(
        self,
        start: Tuple[int, int],
        goal: Tuple[int, int]
    ) -> Optional[List[Tuple[int, int]]]:
        """Runs A* search from start to goal considering terrain elevation costs."""
        sr, sc = start
        gr, gc = goal

        h0 = math.hypot(gr - sr, gc - sc)
        # Priority queue: (f_score, g_cost, current_node, path)
        open_set = [(h0, 0.0, (sr, sc), [(sr, sc)])]
        visited: Set[Tuple[int, int]] = set()

        max_allowed_elev = self.cruise_altitude - self.safety_margin

        while open_set:
            _, g, (r, c), path = heapq.heappop(open_set)
            if (r, c) == (gr, gc):
                return path

            if (r, c) in visited:
                continue
            visited.add((r, c))

            for dr, dc in self.ACTION_DELTAS[:8]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < self.grid_rows and 0 <= nc < self.grid_cols:
                    if (nr, nc) in visited:
                        continue
                    elev = self.terrain[nr, nc]
                    if elev >= max_allowed_elev:
                        continue  # Impassable ridge

                    step_dist = math.hypot(dr, dc)
                    terrain_cost = elev * 4.0  # Prefer lower valley passes
                    new_g = g + step_dist + terrain_cost
                    h = math.hypot(gr - nr, gc - nc)
                    heapq.heappush(open_set, (new_g + h, new_g, (nr, nc), path + [(nr, nc)]))

        return None

