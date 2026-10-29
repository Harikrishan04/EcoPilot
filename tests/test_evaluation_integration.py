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


if __name__ == "__main__":
    unittest.main()
