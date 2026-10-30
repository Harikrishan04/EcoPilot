"""
tests/test_flight_dynamics_3d.py — Unit & Integration Tests for 3D Flight Dynamics
===================================================================================

Phase 2 Verification Suite:
  - 3D continuous position, velocity, and heading tracking
  - Semi-implicit Euler kinematic integration
  - Dynamic wind drift vector displacement
  - Continuous bilinear terrain height and clearance calculation
  - Vehicle limits (max speed, climb/descent rates, altitude floor/ceiling)
  - Battery electrical power consumption and SoC depletion
  - Terminal outcomes (success, collision, depletion, timeout)
  - Fixed-seed determinism and reproducibility
"""

import math
import os
import sys
import unittest
import numpy as np

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drone_env import DroneEnv, MissionOutcome
from safety import SafetyEnvelope, FlightMode
from planner_baseline import RuleBasedPlanner


class TestFlightDynamics3D(unittest.TestCase):
    """Test suite covering Phase 2 3D flight state, kinematics, and energy dynamics."""

    def setUp(self):
        self.env = DroneEnv()

    def test_stationary_hover_consumes_energy_and_preserves_position(self):
        """
        Unit test: Stationary hover consumes baseline electrical power (avionics + lift)
        and preserves position within tight tolerance (<= 0.5 cells).
        """
        self.env.reset(seed=123)
        self.env.wind_speed = 3.0  # Mild breeze
        self.env.wind_dir_rad = 0.0

        r_start, c_start = self.env.drone_r, self.env.drone_c
        initial_battery = self.env.battery_soc_pct

        # Execute 3 consecutive hover steps (Action 8)
        for _ in range(3):
            next_state, reward, done, info = self.env.step(action=8)

        # 1. Energy consumption: battery has drained and power is positive (>150 W)
        self.assertLess(self.env.battery_soc_pct, initial_battery)
        self.assertGreater(info["power_w"], 150.0)
        self.assertGreater(self.env.energy_consumed_wh, 0.0)

        # 2. Position preservation: drift during station-keeping hover is bounded within 0.5 cells
        r_drift = abs(self.env.drone_r - r_start)
        c_drift = abs(self.env.drone_c - c_start)
        self.assertLess(r_drift, 0.5, f"Excessive row drift in hover: {r_drift:.3f}")
        self.assertLess(c_drift, 0.5, f"Excessive col drift in hover: {c_drift:.3f}")

    def test_climbing_increases_altitude_and_energy_use(self):
        """
        Unit test: Climbing increases altitude (z) and draws more power than level flight.
        """
        self.env.reset(seed=202)
        initial_z = self.env.drone_z
        initial_energy = self.env.energy_consumed_wh

        # Step climb action (Action 9)
        _, _, _, info_climb = self.env.step(action=9)
        z_after_climb = self.env.drone_z

        self.assertGreater(z_after_climb, initial_z, "Climb action did not increase altitude")
        self.assertGreater(self.env.vz_mps, 0.0, "Climb vertical velocity was not positive")

        # Compare power with level hover under identical atmospheric conditions
        power_climb = info_climb["power_w"]
        # Step hover action (Action 8)
        _, _, _, info_hover = self.env.step(action=8)
        power_hover = info_hover["power_w"]

        self.assertGreater(power_climb, power_hover, "Climbing power must exceed steady hover power")

    def test_descending_decreases_altitude_and_cannot_pass_through_terrain(self):
        """
        Unit test: Descending decreases altitude, and descending into ground elevation
        cannot pass through terrain; triggers COLLISION_TERRAIN.
        """
        self.env.reset(seed=303)
        initial_z = self.env.drone_z

        # Step descent action (Action 10)
        _, _, _, info_descend = self.env.step(action=10)
        self.assertLess(self.env.drone_z, initial_z, "Descent action did not decrease altitude")
        self.assertLess(self.env.vz_mps, 0.0, "Descent vertical velocity was not negative")

        # Force drone altitude directly to local terrain level on a mountain ridge away from landing zones
        self.env.drone_r, self.env.drone_c = 22.0, 1.0
        ground_elev = self.env.get_terrain_elevation(self.env.drone_r, self.env.drone_c)
        self.env.drone_z = ground_elev + 0.005  # 5mm above terrain

        # One more descent step command must contact terrain and detect collision
        _, _, done, info_crash = self.env.step(action=10)
        self.assertTrue(done, "Ground contact did not terminate episode")
        self.assertEqual(info_crash["outcome"], MissionOutcome.COLLISION_TERRAIN.value)
        self.assertEqual(info_crash["status"], "terrain_crash")

    def test_horizontal_motion_changes_position_in_expected_direction(self):
        """
        Unit test: Cardinal horizontal actions move position in the expected directions:
          - North (Action 0): row decreases
          - East  (Action 2): col increases
          - South (Action 4): row increases
          - West  (Action 6): col decreases
        """
        self.env.reset(seed=404)
        self.env.wind_speed = 0.0  # Zero wind to isolate pure command translation
        self.env.drone_r, self.env.drone_c = 10.0, 10.0

        # Step North (Action 0)
        self.env.step(action=0)
        self.assertLess(self.env.drone_r, 10.0, "North step did not decrease row coordinate")
        self.assertAlmostEqual(self.env.drone_c, 10.0, delta=0.05)

        # Step East (Action 2)
        r_before, c_before = self.env.drone_r, self.env.drone_c
        self.env.step(action=2)
        self.assertGreater(self.env.drone_c, c_before, "East step did not increase col coordinate")

        # Step South (Action 4)
        r_before = self.env.drone_r
        self.env.step(action=4)
        self.assertGreater(self.env.drone_r, r_before, "South step did not increase row coordinate")

        # Step West (Action 6)
        c_before = self.env.drone_c
        self.env.step(action=6)
        self.assertLess(self.env.drone_c, c_before, "West step did not decrease col coordinate")

    def test_wind_causes_measurable_downwind_drift(self):
        """
        Unit test: Ambient wind causes a measurable downwind displacement compared to calm air.
        """
        # Run identical North command under calm air vs strong West wind
        env_calm = DroneEnv()
        env_calm.reset(seed=505)
        env_calm.drone_r, env_calm.drone_c = 12.0, 12.0
        env_calm.wind_speed = 0.0
        env_calm.step(action=0)  # Move North

        env_windy = DroneEnv()
        env_windy.reset(seed=505)
        env_windy.drone_r, env_windy.drone_c = 12.0, 12.0
        env_windy.wind_speed = 10.0
        env_windy.wind_dir_rad = 1.5 * math.pi  # Wind FROM West (blows toward East)
        env_windy.step(action=0)  # Move North

        # West wind (blowing East) must displace col to the East (+c)
        drift_east = env_windy.drone_c - env_calm.drone_c
        self.assertGreater(drift_east, 0.03, f"Expected eastward wind drift, got {drift_east:.4f} cells")
        self.assertGreater(env_windy.vx_mps, 0.0, "Ground vx velocity must reflect eastward drift")

    def test_headwind_increases_energy_use_compared_with_no_wind(self):
        """
        Unit test: Flying into a headwind increases aerodynamic relative airspeed
        and produces higher power draw (due to v_rel^3 drag) than zero wind.
        """
        # Drone flying North (heading = 0)
        env_calm = DroneEnv()
        env_calm.reset(seed=606)
        env_calm.drone_r, env_calm.drone_c = 15.0, 15.0
        env_calm.wind_speed = 0.0
        _, _, _, info_calm = env_calm.step(action=0)

        env_headwind = DroneEnv()
        env_headwind.reset(seed=606)
        env_headwind.drone_r, env_headwind.drone_c = 15.0, 15.0
        env_headwind.wind_speed = 10.0
        env_headwind.wind_dir_rad = 0.0  # Wind FROM North -> direct headwind
        _, _, _, info_headwind = env_headwind.step(action=0)

        # Headwind relative airspeed must be higher
        self.assertGreater(info_headwind["airspeed_mps"], info_calm["airspeed_mps"])
        # Parasitic drag power increases with airspeed cubed
        self.assertGreater(info_headwind["power_w"], info_calm["power_w"])

    def test_speed_climb_rate_altitude_floor_and_ceiling_enforced(self):
        """
        Unit test: Enforces maximum horizontal speed, climb rate, descent rate,
        altitude ceiling (0.85), and altitude floor (0.15).
        """
        self.env.reset(seed=707)

        # 1. Climb rate ceiling
        self.env.drone_z = 0.82
        for _ in range(5):
            self.env.step(action=9)  # Climb
        self.assertLessEqual(self.env.drone_z, self.env.max_altitude, "Exceeded flight ceiling")
        self.assertLessEqual(self.env.vz_mps, self.env.max_climb_rate_mps, "Exceeded maximum climb velocity")

        # 2. Descent rate floor
        self.env.drone_z = 0.20
        # Place in deep valley to avoid terrain collision during test
        self.env.drone_r, self.env.drone_c = 2.0, 2.0
        for _ in range(5):
            self.env.step(action=10)  # Descend
        self.assertGreaterEqual(self.env.drone_z, self.env.min_altitude, "Breached flight floor")
        self.assertGreaterEqual(self.env.vz_mps, self.env.max_descent_rate_mps, "Exceeded maximum descent velocity")

        # 3. Horizontal ground speed limit
        self.env.wind_speed = 15.0
        self.env.wind_dir_rad = math.pi / 2.0
        self.env.step(action=2)  # East
        horiz_speed = math.hypot(self.env.vx_mps, self.env.vy_mps)
        self.assertLessEqual(horiz_speed, self.env.max_horizontal_speed_mps + 1e-3, "Exceeded max horizontal speed")

    def test_terrain_collision_yields_correct_terminal_outcome(self):
        """
        Unit test: Moving into high relief with negative clearance yields COLLISION_TERRAIN.
        """
        self.env.reset(seed=808)
        # Place drone adjacent to high ridge in south-east (row 22, col 2)
        self.env.drone_r = 21.0
        self.env.drone_c = 1.0
        self.env.drone_z = 0.20  # Below the mountain height at (22, 1)

        # Force step into the high mountain
        _, reward, done, info = self.env.step(action=4)  # South

        self.assertTrue(done, "Terrain crash did not terminate episode")
        self.assertEqual(info["outcome"], MissionOutcome.COLLISION_TERRAIN.value)
        self.assertEqual(info["status"], "terrain_crash")
        self.assertLess(reward, -30.0, "Expected large negative crash penalty")

    def test_battery_depletion_yields_correct_terminal_outcome(self):
        """
        Unit test: Battery draining to 0% yields BATTERY_DEPLETED terminal outcome.
        """
        self.env.reset(seed=909)
        self.env.drone_r, self.env.drone_c = 10.0, 10.0  # Center of terrain
        self.env.wind_speed = 0.0
        self.env.battery_soc_pct = 0.05  # Near zero

        _, reward, done, info = self.env.step(action=8)  # Hover step

        self.assertTrue(done, "Battery depletion did not terminate episode")
        self.assertEqual(info["outcome"], MissionOutcome.BATTERY_DEPLETED.value)
        self.assertEqual(info["status"], "battery_depleted")
        self.assertLessEqual(self.env.battery_soc_pct, 0.0)

    def test_calm_weather_mission_reaches_goal_with_positive_clearance_and_battery(self):
        """
        Integration test: A complete calm-weather mission executed by the Rule-Based Planner
        safely reaches the goal with positive clearance and substantial battery remaining.
        """
        state = self.env.reset(seed=5001)
        planner = RuleBasedPlanner(self.env.terrain)

        # Set calm conditions
        self.env.wind_speed = 2.0
        self.env.wind_dir_rad = 0.5
        done = False
        steps = 0

        while not done and steps < 80:
            action = planner.select_action(self.env.drone_pos, self.env.goal_pos)
            state, reward, done, info = self.env.step(action)
            steps += 1
            # Check continuous clearance remained safe
            elev = self.env.get_terrain_elevation(self.env.drone_r, self.env.drone_c)
            clearance = self.env.drone_z - elev
            self.assertGreater(clearance, 0.0, f"Step {steps}: Negative clearance {clearance:.4f}")

        self.assertTrue(done, "Mission did not terminate within budget")
        self.assertEqual(info["outcome"], MissionOutcome.SUCCESS.value)
        self.assertGreater(self.env.battery_soc_pct, 50.0, "Expected substantial battery remaining")
        self.assertGreater(len(self.env.telemetry_history), 5, "Telemetry history was not recorded")

    def test_unsafe_trajectory_intercepted_by_safety_layer(self):
        """
        Integration test: When policy commands an unsafe trajectory toward high relief,
        the SafetyEnvelope intercepts the candidate action before physical execution.
        """
        self.env.reset(seed=1010)
        envelope = SafetyEnvelope(r_critical=0.85, terrain_safety_margin=0.05)

        # Drone at cruise altitude near a ridge
        current_pos = (21, 2)
        unsafe_action = 4  # South (into high elevation)

        intervention = envelope.evaluate(
            policy_action=unsafe_action,
            current_pos=current_pos,
            home_pos=(self.env.home_r, self.env.home_c),
            r_env=0.20,
            dynamic_pressure_pa=30.0,
            terrain_grid=self.env.terrain,
            cruise_altitude=self.env.cruise_altitude,
            battery_soc_pct=100.0,
            consecutive_hover_steps=0,
            landing_zones=self.env.landing_zones,
        )

        self.assertTrue(intervention.is_overridden, "Safety layer failed to override unsafe action")
        self.assertIn("TERRAIN_COLLISION_RISK", intervention.trigger_reasons[0])
        # Executed action is altered from unsafe South (4) to a safe diversion
        self.assertNotEqual(intervention.executed_action, unsafe_action)

    def test_fixed_seed_reproducibility(self):
        """
        Regression test: Repeating a fixed-seed mission produces identical 3D trajectory
        and telemetry across runs.
        """
        def run_fixed_episode(seed_val: int):
            env = DroneEnv()
            env.reset(seed=seed_val)
            planner = RuleBasedPlanner(env.terrain)
            trajectory = []
            for _ in range(10):
                act = planner.select_action(env.drone_pos, env.goal_pos)
                _, _, done, info = env.step(act)
                trajectory.append((
                    round(env.drone_r, 5),
                    round(env.drone_c, 5),
                    round(env.drone_z, 5),
                    round(env.vx_mps, 5),
                    round(env.vy_mps, 5),
                    round(info["battery_soc"], 4),
                    round(info["energy_wh"], 5),
                ))
                if done:
                    break
            return trajectory

        run1 = run_fixed_episode(5050)
        run2 = run_fixed_episode(5050)

        self.assertEqual(run1, run2, "Telemetry and 3D trajectories differed on identical seed!")


if __name__ == "__main__":
    unittest.main()
