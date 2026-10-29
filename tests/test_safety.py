"""
tests/test_safety.py — Unit Tests for EcoPilot Safety Envelope
=============================================================

Verifies that the hard safety envelope operates independently of the learned policy:
  - Never triggers under nominal conditions.
  - 100% trigger reliability under extreme synthetic environmental conditions.
  - Autonomous Return-to-Base (RTB) or Hover selection when active.
"""

import os
import sys
import unittest

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from safety import (
    ACTION_HOVER,
    FlightMode,
    SafetyEnvelope,
    SafetyIntervention,
    safety_override,
)


class TestSafetyEnvelope(unittest.TestCase):
    """Test suite for independent flight safety envelope."""

    def setUp(self):
        # 10x10 test terrain with valley in center (0.1) and high ridge on the east (0.8)
        self.terrain = np.full((10, 10), 0.10, dtype=np.float32)
        self.terrain[:, 8:] = 0.80  # Impassable ridge
        self.envelope = SafetyEnvelope(r_critical=0.85, q_max_pa=120.0)
        self.current_pos = (5, 5)
        self.home_pos = (2, 2)
        self.cruise_altitude = 0.40

    def test_nominal_conditions_pass_through(self):
        """Under normal weather and safe terrain, policy action is preserved."""
        policy_action = 0  # Move North (safe valley)
        intervention = self.envelope.evaluate(
            policy_action=policy_action,
            current_pos=self.current_pos,
            home_pos=self.home_pos,
            r_env=0.35,              # Well below 0.85
            dynamic_pressure_pa=45.0, # Well below 120.0
            terrain_grid=self.terrain,
            cruise_altitude=self.cruise_altitude,
        )

        self.assertFalse(intervention.is_overridden)
        self.assertEqual(intervention.executed_action, policy_action)
        self.assertEqual(intervention.flight_mode, FlightMode.POLICY_DRIVEN)
        self.assertEqual(len(intervention.trigger_reasons), 0)

    def test_critical_r_env_triggers_override(self):
        """When R_env exceeds R_critical (0.85), override MUST trigger."""
        policy_action = 0
        intervention = self.envelope.evaluate(
            policy_action=policy_action,
            current_pos=self.current_pos,
            home_pos=self.home_pos,
            r_env=0.91,              # > 0.85
            dynamic_pressure_pa=60.0,
            terrain_grid=self.terrain,
            cruise_altitude=self.cruise_altitude,
        )

        self.assertTrue(intervention.is_overridden)
        self.assertIn("CRITICAL_R_ENV", intervention.trigger_reasons[0])
        self.assertIn(intervention.flight_mode, {FlightMode.RETURN_TO_BASE, FlightMode.HOVER_HOLD})

    def test_dynamic_pressure_overload_triggers_override(self):
        """When gust dynamic pressure q exceeds q_max (120 Pa), override MUST trigger."""
        policy_action = 0
        intervention = self.envelope.evaluate(
            policy_action=policy_action,
            current_pos=self.current_pos,
            home_pos=self.home_pos,
            r_env=0.40,
            dynamic_pressure_pa=145.0, # > 120.0 Pa
            terrain_grid=self.terrain,
            cruise_altitude=self.cruise_altitude,
        )

        self.assertTrue(intervention.is_overridden)
        self.assertIn("EXCESSIVE_DYNAMIC_PRESSURE", intervention.trigger_reasons[0])

    def test_imminent_terrain_collision_triggers_override(self):
        """If policy commands drone into high ridge (east), envelope intercepts."""
        policy_action_east = 2  # Move East into ridge (col 5 -> col 6, heading toward col 8)
        # Move drone right next to the ridge at col 7
        drone_near_ridge = (5, 7)
        intervention = self.envelope.evaluate(
            policy_action=policy_action_east, # Target is col 8 (height 0.80 > 0.40)
            current_pos=drone_near_ridge,
            home_pos=self.home_pos,
            r_env=0.20,
            dynamic_pressure_pa=30.0,
            terrain_grid=self.terrain,
            cruise_altitude=self.cruise_altitude,
        )

        self.assertTrue(intervention.is_overridden)
        self.assertTrue(any("TERRAIN_COLLISION_RISK" in r for r in intervention.trigger_reasons))
        # Executed action must NOT be the suicidal policy action 2
        self.assertNotEqual(intervention.executed_action, policy_action_east)

    def test_standalone_safety_override_function(self):
        """Verify the wrapper function safety_override() interface."""
        act, overridden, reason = safety_override(
            chosen_action=3,
            current_pos=self.current_pos,
            home_pos=self.home_pos,
            r_env=0.95,
            dynamic_pressure_pa=130.0,
            terrain_grid=self.terrain,
        )
        self.assertTrue(overridden)
        self.assertIn("CRITICAL_R_ENV", reason)
        self.assertIn("EXCESSIVE_DYNAMIC_PRESSURE", reason)

    def test_monte_carlo_stress_100_percent_reliability(self):
        """
        DONE CONDITION: Unit test in isolation with 5,000 synthetic values to
        confirm the override always triggers on extreme values and never on normal ones.
        """
        rng = np.random.default_rng(2026)
        n_samples = 5000

        false_negatives = 0
        false_positives = 0

        for _ in range(n_samples):
            # Sample synthetic environmental variables
            r_val = float(rng.uniform(0.0, 1.2))
            q_val = float(rng.uniform(0.0, 200.0))
            pol_act = int(rng.integers(0, 8))

            is_unsafe_ground_truth = (r_val > 0.85) or (q_val > 120.0)

            intervention = self.envelope.evaluate(
                policy_action=pol_act,
                current_pos=self.current_pos,
                home_pos=self.home_pos,
                r_env=r_val,
                dynamic_pressure_pa=q_val,
                terrain_grid=self.terrain,
                cruise_altitude=self.cruise_altitude,
            )

            if is_unsafe_ground_truth and not intervention.is_overridden:
                false_negatives += 1
            if not is_unsafe_ground_truth and intervention.is_overridden:
                # Only a false positive if terrain collision wasn't also triggered
                if not any("TERRAIN" in r or "BOUNDARY" in r for r in intervention.trigger_reasons):
                    false_positives += 1

        print(f"\n--- Monte Carlo Stress Test ({n_samples} trials) ---")
        print(f"False Negatives (Unsafe condition not caught) : {false_negatives}")
        print(f"False Positives (Nominal state falsely flagged): {false_positives}")

        self.assertEqual(false_negatives, 0, "Safety envelope failed to trigger on unsafe state!")
        self.assertEqual(false_positives, 0, "Safety envelope triggered on nominal state!")


if __name__ == "__main__":
    unittest.main()

