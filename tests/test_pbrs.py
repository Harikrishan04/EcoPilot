"""
tests/test_pbrs.py — Unit Tests for Potential-Based Reward Shaping (PBRS)
========================================================================

Verifies strict compliance with the theoretical and implementation rules of PBRS
(Ng, Harada, & Russell, 1999):
  1. Default disabled: use_pbrs is False by default; output is numerically unshaped.
  2. Same discount factor gamma: pbrs_gamma matches the agent's discount factor (0.95).
  3. Phi(terminal) = 0: All terminal states (goal, crash, timeout, RTH, landing) enforce Phi=0.
  4. State-only dependency: Phi depends strictly on spatial terrain coordinates, not action or time.
  5. Telescoping sum invariance: sum_{t=0}^{T-1} gamma^t * F_t == -Phi(s_0).
  6. Unshaped metrics transparency: info['unshaped_reward'] and info['pbrs_shaping'] are recorded.
"""

import math
import os
import sys
import unittest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drone_env import DroneEnv, MissionOutcome
from q_agent import QAgent


class TestPBRS(unittest.TestCase):
    """Test suite for Potential-Based Reward Shaping in DroneEnv."""

    def setUp(self):
        self.env = DroneEnv(use_pbrs=False)

    def test_pbrs_disabled_by_default(self):
        """Verify that PBRS is disabled by default and reward equals unshaped_reward."""
        self.assertFalse(self.env.use_pbrs)
        self.env.reset(seed=42)
        _, reward, _, info = self.env.step(0)
        self.assertIn("unshaped_reward", info)
        self.assertIn("pbrs_shaping", info)
        self.assertEqual(reward, info["unshaped_reward"])

    def test_pbrs_same_gamma_as_agent(self):
        """Verify shaping gamma exactly matches QAgent discount factor."""
        agent = QAgent()
        self.assertEqual(self.env.pbrs_gamma, agent.gamma)
        self.assertEqual(self.env.pbrs_gamma, 0.95)

    def test_potential_depends_only_on_state(self):
        """Verify Phi(s) depends strictly on coordinates, not action or step count."""
        self.env.reset(seed=101)
        r, c = 5.5, 6.2
        phi1 = self.env.get_potential(r, c)

        # Advance step count and change internal environment states
        self.env.step_count = 50
        self.env.wind_speed = 15.0
        self.env.battery_soc_pct = 30.0
        phi2 = self.env.get_potential(r, c)

        self.assertEqual(phi1, phi2, "Phi changed when non-spatial state changed!")

    def test_potential_is_monotonic_towards_goal(self):
        """Verify that approaching the goal along valley increases potential towards zero."""
        self.env.reset(seed=101)
        gr, gc = self.env.goal_r, self.env.goal_c
        # Potential at the exact goal should be 0.0
        phi_goal = self.env.get_potential(float(gr), float(gc))
        self.assertAlmostEqual(phi_goal, 0.0, places=4)

        # Potential further away should be negative (since Phi = -scale * cost)
        phi_far = self.env.get_potential(float((gr + 5) % self.env.grid_rows), float(gc))
        self.assertLess(phi_far, phi_goal)

    def test_terminal_potential_zero_enforcement(self):
        """Verify that when done is True, Phi(curr) is set to 0.0 and F = -Phi(prev)."""
        env = DroneEnv(use_pbrs=True)
        env.reset(seed=202)
        # Force next step to trigger timeout terminal condition
        env.step_count = env.max_steps - 1
        phi_before = env.get_potential(env.drone_r, env.drone_c)

        _, reward, done, info = env.step(8)  # Hover at timeout threshold
        self.assertTrue(done)
        self.assertEqual(info["outcome"], MissionOutcome.TIMEOUT.value)

        # At terminal state: F = gamma * 0.0 - phi_before = -phi_before
        expected_f = -phi_before
        self.assertAlmostEqual(info["pbrs_shaping"], expected_f, places=4)
        self.assertAlmostEqual(reward, info["unshaped_reward"] + expected_f, places=4)

    def test_telescoping_discounted_sum_identity(self):
        """
        Verify the fundamental PBRS identity over a full episode trajectory:
          sum_{t=0}^{T-1} gamma^t * F(s_t, s_{t+1}) == gamma^T * Phi(s_T) - Phi(s_0) == -Phi(s_0)
        """
        env = DroneEnv(use_pbrs=True)
        env.reset(seed=303)
        phi_0 = env.get_potential(env.drone_r, env.drone_c)
        gamma = env.pbrs_gamma

        discounted_f_sum = 0.0
        step_idx = 0
        done = False

        while not done and step_idx < 150:
            _, _, done, info = env.step(np.random.randint(0, 8))
            f_t = info["pbrs_shaping"]
            discounted_f_sum += (gamma ** step_idx) * f_t
            step_idx += 1

        self.assertTrue(done, "Episode did not terminate within step budget.")
        # Theoretical identity: discounted sum of F must equal -Phi(s_0)
        expected_telescope = -phi_0
        self.assertAlmostEqual(discounted_f_sum, expected_telescope, places=3,
                               msg=f"Telescoping sum {discounted_f_sum} != -Phi(s_0) {-phi_0}")

    def test_unshaped_metrics_identical_regardless_of_pbrs_flag(self):
        """Verify unshaped reward and physical outcomes are identical under identical actions."""
        env_unshaped = DroneEnv(use_pbrs=False)
        env_shaped = DroneEnv(use_pbrs=True)

        env_unshaped.reset(seed=404)
        env_shaped.reset(seed=404)

        for act in [1, 2, 2, 0, 3]:
            _, rew_u, done_u, info_u = env_unshaped.step(act)
            _, rew_s, done_s, info_s = env_shaped.step(act)

            self.assertEqual(done_u, done_s)
            self.assertEqual(info_u["unshaped_reward"], info_s["unshaped_reward"])
            self.assertEqual(info_u["battery_soc"], info_s["battery_soc"])
            self.assertEqual(info_u["energy_wh"], info_s["energy_wh"])
            self.assertEqual(info_u["clearance"], info_s["clearance"])
            self.assertEqual(rew_u, info_s["unshaped_reward"])
            self.assertNotEqual(rew_s, rew_u)  # Shaped reward incorporates F_t


if __name__ == "__main__":
    unittest.main()
