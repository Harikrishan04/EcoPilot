"""
tests/test_rl_pipeline.py — Unit Tests for EcoPilot Phase 3 RL Pipeline
======================================================================
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drone_env import DroneEnv, MissionOutcome
from q_agent import QAgent
from static_baseline_agent import StaticBaselineAgent


class TestRLPipeline(unittest.TestCase):
    """Test suite for DroneEnv and Tabular Q-learning agents."""

    def setUp(self):
        self.env = DroneEnv()

    def test_env_reset_state_shape_and_types(self):
        """Verify environment reset yields valid 5-element state tuple within bounds."""
        state = self.env.reset(seed=42)
        self.assertIsInstance(state, tuple)
        self.assertEqual(len(state), 5)

        heading_bin, dist_bin, hazard, risk_bin, battery_bin = state
        self.assertIn(heading_bin, range(8))
        self.assertIn(dist_bin, range(5))
        self.assertIn(hazard, {0, 1, 2})
        self.assertIn(risk_bin, {0, 1, 2, 3})
        self.assertIn(battery_bin, {0, 1, 2})

    def test_env_step_transition_and_reward(self):
        """Verify stepping produces valid transition tuple and telemetry info."""
        state = self.env.reset(seed=101)
        next_state, reward, done, info = self.env.step(action=0, use_adaptive_reward=True)

        self.assertIsInstance(next_state, tuple)
        self.assertEqual(len(next_state), 5)
        self.assertIsInstance(reward, float)
        self.assertIsInstance(done, bool)
        self.assertIn("status", info)
        self.assertIn("r_env", info)
        self.assertIn("battery_soc", info)
        self.assertIn("energy_wh", info)
        self.assertIn("outcome", info)


    def test_q_agent_selection_and_update(self):
        """Verify QAgent Q-table initialization, Bellman update, and greedy choice."""
        agent = QAgent(learning_rate=0.5, discount_factor=0.90)
        state_a = (1, 1, 0, 1)
        state_b = (0, 0, 0, 1)

        # Initially all Q-values are 0
        init_q = agent.get_q_values(state_a)
        self.assertEqual(len(init_q), 8)
        self.assertTrue((init_q == 0.0).all())

        # Update action 2 with reward +10
        agent.update(state=state_a, action=2, reward=10.0, next_state=state_b, done=False)

        # After update, Q(s_a, 2) should be 0.5 * 10 = 5.0
        updated_q = agent.get_q_values(state_a)
        self.assertAlmostEqual(updated_q[2], 5.0, places=3)

        # Greedy action choice should now pick action 2
        best_act = agent.select_action(state_a, training=False)
        self.assertEqual(best_act, 2)

    def test_saved_q_table_files_exist_and_load(self):
        """Verify exported Q-tables can be loaded cleanly."""
        q_adapt_file = "data/q_table_adaptive.json"
        q_base_file = "data/q_table_baseline.json"

        self.assertTrue(os.path.isfile(q_adapt_file), f"Missing {q_adapt_file}")
        self.assertTrue(os.path.isfile(q_base_file), f"Missing {q_base_file}")

        agent = QAgent()
        agent.load_policy_json(q_adapt_file)
        self.assertGreater(len(agent.q_table), 50)


if __name__ == "__main__":
    unittest.main()

