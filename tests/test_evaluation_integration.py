"""
tests/test_evaluation_integration.py — Integration Tests for EcoPilot Evaluation Pipeline
========================================================================================

Verifies that evaluate_all() runs cleanly end-to-end from a versioned JSON config,
generates per-episode and aggregate CSVs with complete weather and path-length data,
and renders the comparison charts.
"""

import csv
import os
import shutil
import tempfile
import unittest

from evaluate import evaluate_all, load_evaluation_config
from drone_env import DroneEnv, MissionOutcome
from safety import SafetyEnvelope, FlightMode


class TestEvaluationIntegration(unittest.TestCase):
    """Integration test suite for the empirical evaluation pipeline."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="ecopilot_eval_test_")
        self.episodes_csv = os.path.join(self.temp_dir, "test_episodes.csv")
        self.summary_csv = os.path.join(self.temp_dir, "test_summary.csv")
        self.charts_png = os.path.join(self.temp_dir, "test_charts.png")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_load_config_structure(self):
        """Verify baseline evaluation configuration loads and contains all required sections."""
        cfg = load_evaluation_config("configs/baseline_evaluation.json")
        self.assertIn("evaluation", cfg)
        self.assertIn("condition_buckets", cfg)
        self.assertIn("models", cfg)
        self.assertIn("outputs", cfg)

        buckets = cfg["condition_buckets"]
        self.assertIn("Calm", buckets)
        self.assertIn("Moderate", buckets)
        self.assertIn("Severe", buckets)

    def test_evaluate_all_integration_small_run(self):
        """
        Runs evaluate_all() with 2 episodes per bucket to temporary files,
        verifying per-episode CSV schema, summary metrics, and chart generation.
        """
        results = evaluate_all(
            config_path="configs/baseline_evaluation.json",
            override_episodes_per_bucket=2,
            override_episodes_csv=self.episodes_csv,
            override_summary_csv=self.summary_csv,
            override_charts_png=self.charts_png,
        )

        # 1. Verify Per-Episode CSV
        self.assertTrue(os.path.isfile(self.episodes_csv), f"Missing {self.episodes_csv}")
        with open(self.episodes_csv, "r") as f:
            reader = csv.DictReader(f)
            ep_rows = list(reader)

        # 3 buckets * 3 models * 2 episodes = 18 episode rows
        self.assertEqual(len(ep_rows), 18)

        sample = ep_rows[0]
        required_episode_cols = [
            "episode_id", "seed", "bucket", "agent", "outcome", "status",
            "success", "safe_rth", "controlled_landing", "timeout", "crash", "battery_depleted",
            "steps", "path_length_cells", "path_length_m", "energy_consumed_wh",
            "battery_end_pct", "total_reward", "interventions", "override_reasons",
            "wind_speed_mps", "wind_dir_deg", "gust_variance", "temp_k", "pressure_pa",
            "relative_humidity", "pressure_trend_hpa_h", "air_density_kg_m3", "r_env"
        ]
        for col in required_episode_cols:
            self.assertIn(col, sample, f"Missing required column in episode CSV: {col}")

        # Verify path length is recorded and non-zero for active flights
        self.assertTrue(any(float(r["path_length_m"]) > 0.0 for r in ep_rows))

        # 2. Verify Aggregate Summary CSV
        self.assertTrue(os.path.isfile(self.summary_csv), f"Missing {self.summary_csv}")
        with open(self.summary_csv, "r") as f:
            sum_reader = csv.DictReader(f)
            sum_rows = list(sum_reader)

        # 3 buckets * 3 models = 9 summary rows
        self.assertEqual(len(sum_rows), 9)

        required_summary_cols = [
            "bucket", "agent", "trials", "success_rate_pct", "ci_95_pct",
            "safe_rth_rate_pct", "controlled_landing_rate_pct", "timeout_rate_pct",
            "crash_rate_pct", "battery_depletion_rate_pct", "mean_flight_steps",
            "mean_path_length_m", "mean_energy_wh", "mean_interventions",
            "mean_reward", "mean_wind_speed_mps", "mean_r_env"
        ]
        for col in required_summary_cols:
            self.assertIn(col, sum_rows[0], f"Missing required column in summary CSV: {col}")

        # 3. Verify Chart Generation
        self.assertTrue(os.path.isfile(self.charts_png), f"Missing {self.charts_png}")
        self.assertGreater(os.path.getsize(self.charts_png), 10000, "Generated chart is too small or empty")

    def test_evaluation_byte_for_byte_reproducibility(self):
        """
        Verify that evaluation is strictly deterministic: running evaluation twice
        on identical seeds produces byte-for-byte identical episode and summary CSV files.
        """
        dir1 = tempfile.mkdtemp(prefix="repro1_")
        dir2 = tempfile.mkdtemp(prefix="repro2_")
        try:
            ep1 = os.path.join(dir1, "episodes.csv")
            sum1 = os.path.join(dir1, "summary.csv")
            ch1 = os.path.join(dir1, "chart.png")

            ep2 = os.path.join(dir2, "episodes.csv")
            sum2 = os.path.join(dir2, "summary.csv")
            ch2 = os.path.join(dir2, "chart.png")

            evaluate_all(
                config_path="configs/baseline_evaluation.json",
                override_episodes_per_bucket=2,
                override_episodes_csv=ep1,
                override_summary_csv=sum1,
                override_charts_png=ch1,
            )
            evaluate_all(
                config_path="configs/baseline_evaluation.json",
                override_episodes_per_bucket=2,
                override_episodes_csv=ep2,
                override_summary_csv=sum2,
                override_charts_png=ch2,
            )

            with open(ep1, "rb") as f1, open(ep2, "rb") as f2:
                self.assertEqual(f1.read(), f2.read(), "Episode CSVs are not byte-for-byte identical across runs!")

            with open(sum1, "rb") as f1, open(sum2, "rb") as f2:
                self.assertEqual(f1.read(), f2.read(), "Summary CSVs are not byte-for-byte identical across runs!")
        finally:
            shutil.rmtree(dir1, ignore_errors=True)
            shutil.rmtree(dir2, ignore_errors=True)

    def test_controlled_landing_end_to_end(self):
        """
        Verify that when battery reaches critical threshold (< 8%), the safety envelope
        overrides the policy with EMERGENCY_LAND and directs the drone to complete
        a safe controlled descent at an approved flat landing site.
        """
        env = DroneEnv()
        env.reset(seed=42)

        # Place drone directly at an approved emergency landing zone
        target_lz = env.landing_zones[0]
        env.drone_r = float(target_lz[0])
        env.drone_c = float(target_lz[1])
        env.battery_soc_pct = 7.0  # Below 8.0% critical threshold
        env.step_count = 1

        envelope = SafetyEnvelope(battery_critical_pct=8.0)
        policy_action = 0  # Policy attempts to move North

        intervention = envelope.evaluate(
            policy_action=policy_action,
            current_pos=(int(round(env.drone_r)), int(round(env.drone_c))),
            home_pos=(env.home_r, env.home_c),
            r_env=env.r_env,
            dynamic_pressure_pa=10.0,
            terrain_grid=env.terrain,
            cruise_altitude=env.cruise_altitude,
            battery_soc_pct=env.battery_soc_pct,
            landing_zones=env.landing_zones,
        )

        self.assertTrue(intervention.is_overridden)
        self.assertEqual(intervention.flight_mode, FlightMode.EMERGENCY_LAND)
        self.assertEqual(intervention.executed_action, 10)  # ACTION_DESCEND

        next_state, reward, done, info = env.step(intervention.executed_action)

        self.assertTrue(done)
        self.assertEqual(info.get("outcome"), MissionOutcome.CONTROLLED_LANDING.value)
        self.assertEqual(info.get("status"), "controlled_landing")
        self.assertGreater(reward, 0.0)


if __name__ == "__main__":
    unittest.main()

