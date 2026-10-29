"""
evaluate.py — EcoPilot Phase 5: Empirical Policy Evaluation
==========================================================

Evaluates the trained Adaptive Q-Learning Agent vs the Static Baseline Agent
across a matrix of controlled atmospheric condition buckets:
  1. Calm Bucket     (R_env < 0.30)
  2. Moderate Bucket (0.30 <= R_env <= 0.65)
  3. Severe Bucket   (R_env > 0.65)

Generates:
  - data/evaluation_results.csv : Detailed statistical metrics per bucket
  - evaluation_charts.png        : Comparative multi-panel performance visualization
"""

from __future__ import annotations

import csv
import json
import math
import os
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from drone_env import DroneEnv
from environment_model import air_density, calculate_R_env
from q_agent import QAgent
from safety import SafetyEnvelope, FlightMode


def configure_bucket_environment(
    env: DroneEnv,
    bucket_name: str,
    rng: np.random.Generator
) -> float:
    """
    Sets deterministic environmental parameters on the environment matching
    the targeted atmospheric severity bucket.
    """
    if bucket_name == "Calm":
        env.wind_speed = float(rng.uniform(1.0, 3.5))
        env.wind_dir_rad = float(rng.uniform(0.0, 2.0 * math.pi))
        env.gust_variance = float(rng.uniform(0.1, 0.4))
        env.temp_k = float(rng.uniform(293.15, 296.15)) # 20-23C
        env.pressure_pa = float(rng.uniform(92400.0, 92800.0))
        env.rh = float(rng.uniform(0.40, 0.55))
        env.dP_dt = float(rng.uniform(-0.2, 0.2))

    elif bucket_name == "Moderate":
        env.wind_speed = float(rng.uniform(5.0, 8.5))
        env.wind_dir_rad = float(rng.uniform(0.0, 2.0 * math.pi))
        env.gust_variance = float(rng.uniform(1.2, 2.5))
        env.temp_k = float(rng.uniform(298.15, 303.15)) # 25-30C
        env.pressure_pa = float(rng.uniform(92000.0, 92400.0))
        env.rh = float(rng.uniform(0.60, 0.75))
        env.dP_dt = float(rng.uniform(-1.0, -0.4))

    elif bucket_name == "Severe":
        env.wind_speed = float(rng.uniform(11.0, 14.5))
        env.wind_dir_rad = float(rng.uniform(0.0, 2.0 * math.pi))
        env.gust_variance = float(rng.uniform(3.5, 4.8))
        env.temp_k = float(rng.uniform(303.15, 308.15)) # 30-35C
        env.pressure_pa = float(rng.uniform(91000.0, 91800.0)) # Rapid barometric drop
        env.rh = float(rng.uniform(0.80, 0.95))
        env.dP_dt = float(rng.uniform(-2.8, -1.8))

    else:
        raise ValueError(f"Unknown bucket: {bucket_name}")

    # Recompute atmospheric physics
    env.air_density_val = air_density(env.temp_k, env.pressure_pa, env.rh)
    env.r_env = calculate_R_env(
        wind_speed=env.wind_speed,
        gust_variance=env.gust_variance,
        dP_dt_hpa_h=env.dP_dt,
        rho=env.air_density_val
    )
    return env.r_env


def run_evaluation_episode(
    env: DroneEnv,
    agent: QAgent,
    bucket_name: str,
    use_adaptive_reward: bool,
    use_safety_envelope: bool = True,
    seed: int = 42
) -> Dict[str, Any]:
    """Runs a single greedy evaluation episode under targeted bucket weather."""
    # 1. Reset spawn and terrain coordinates with fixed episode seed
    env.reset(seed=seed)

    # 2. Apply targeted bucket weather AFTER reset so it is not overwritten
    rng_weather = np.random.default_rng(seed + 10000)
    configure_bucket_environment(env, bucket_name, rng_weather)
    state = env._get_discretized_state()

    envelope = SafetyEnvelope(r_critical=0.85, q_max_pa=120.0) if use_safety_envelope else None
    home_pos = env.drone_pos

    done = False
    total_reward = 0.0
    steps = 0
    interventions_count = 0

    while not done:
        # Greedy action (training=False)
        policy_action = agent.select_action(state, training=False)

        executed_action = policy_action
        if envelope is not None:
            # Estimate dynamic pressure for current planned action
            heading = env.ACTION_HEADINGS[policy_action]
            w_along, w_cross = env.wind_speed * math.cos(env.wind_dir_rad - heading), env.wind_speed * math.sin(env.wind_dir_rad - heading)
            v_rel = math.hypot(env.drone_speed_mps - w_along, w_cross)
            q_dyn = 0.5 * env.air_density_val * (v_rel ** 2)

            intervention = envelope.evaluate(
                policy_action=policy_action,
                current_pos=env.drone_pos,
                home_pos=home_pos,
                r_env=env.r_env,
                dynamic_pressure_pa=q_dyn,
                terrain_grid=env.terrain,
                cruise_altitude=env.cruise_altitude
            )
            if intervention.is_overridden:
                executed_action = intervention.executed_action
                interventions_count += 1
                if intervention.flight_mode == FlightMode.HOVER_HOLD:
                    # Hover in place: step without changing position, penalty for emergency hold
                    env.step_count += 1
                    total_reward -= 1.0
                    if env.step_count >= env.max_steps:
                        done = True
                        status = "timeout"
                    continue

        next_state, reward, done, info = env.step(executed_action, use_adaptive_reward=use_adaptive_reward)
        state = next_state
        total_reward += reward
        steps += 1

    status = info.get("status", "unknown")
    return {
        "reward": total_reward,
        "steps": steps,
        "status": status,
        "success": int(status == "success"),
        "crash": int("crash" in status),
        "interventions": interventions_count,
        "r_env": env.r_env,
    }


def evaluate_all(
    episodes_per_bucket: int = 100,
    q_table_adaptive_path: str = "data/q_table_adaptive.json",
    q_table_baseline_path: str = "data/q_table_baseline.json",
    output_csv_path: str = "data/evaluation_results.csv",
    output_chart_path: str = "evaluation_charts.png"
) -> Dict[str, Dict]:
    """
    Runs full factorial evaluation across Calm, Moderate, and Severe buckets.
    """
    print("=" * 64)
    print("EcoPilot — Phase 5: Empirical Policy Evaluation")
    print(f"Buckets  : Calm | Moderate | Severe")
    print(f"Trials   : {episodes_per_bucket} episodes per bucket")
    print("=" * 64)

    env = DroneEnv()

    # Load trained policies
    adaptive_agent = QAgent(name="AdaptiveAgent")
    adaptive_agent.load_policy_json(q_table_adaptive_path)

    baseline_agent = QAgent(name="StaticBaseline")
    baseline_agent.load_policy_json(q_table_baseline_path)

    buckets = ["Calm", "Moderate", "Severe"]
    results_summary: Dict[str, Dict] = {}

    csv_rows = []

    for bucket in buckets:
        print(f"\nEvaluating Condition Bucket: {bucket} …")
        rng = np.random.default_rng(42)

        adapt_records = []
        base_records = []

        for trial in range(1, episodes_per_bucket + 1):
            seed = 5000 + trial

            # Evaluate Adaptive Agent (with safety envelope)
            rec_adapt = run_evaluation_episode(
                env=env,
                agent=adaptive_agent,
                bucket_name=bucket,
                use_adaptive_reward=True,
                use_safety_envelope=True,
                seed=seed
            )
            adapt_records.append(rec_adapt)

            # Evaluate Baseline Agent (unconditioned, no safety override)
            rec_base = run_evaluation_episode(
                env=env,
                agent=baseline_agent,
                bucket_name=bucket,
                use_adaptive_reward=False,
                use_safety_envelope=False,
                seed=seed
            )
            base_records.append(rec_base)

        # Aggregate metrics
        def _aggregate(records: List[Dict]) -> Dict[str, float]:
            n = len(records)
            return {
                "success_rate_pct": round(sum(r["success"] for r in records) / n * 100.0, 1),
                "crash_rate_pct": round(sum(r["crash"] for r in records) / n * 100.0, 1),
                "mean_reward": round(sum(r["reward"] for r in records) / n, 2),
                "mean_steps": round(sum(r["steps"] for r in records) / n, 1),
                "mean_interventions": round(sum(r["interventions"] for r in records) / n, 2),
                "mean_r_env": round(sum(r["r_env"] for r in records) / n, 3),
            }

        stats_adapt = _aggregate(adapt_records)
        stats_base = _aggregate(base_records)

        results_summary[bucket] = {
            "AdaptiveAgent": stats_adapt,
            "StaticBaseline": stats_base
        }

        print(f"  [Adaptive]  Succ: {stats_adapt['success_rate_pct']:4.1f}% | Crash: {stats_adapt['crash_rate_pct']:4.1f}% | Rew: {stats_adapt['mean_reward']:6.1f} | Mean R_env: {stats_adapt['mean_r_env']:.3f}")
        print(f"  [Baseline]  Succ: {stats_base['success_rate_pct']:4.1f}% | Crash: {stats_base['crash_rate_pct']:4.1f}% | Rew: {stats_base['mean_reward']:6.1f}")

        # CSV Logging
        csv_rows.append({
            "bucket": bucket,
            "agent": "AdaptiveAgent",
            **stats_adapt
        })
        csv_rows.append({
            "bucket": bucket,
            "agent": "StaticBaseline",
            **stats_base
        })

    # Save CSV
    os.makedirs(os.path.dirname(os.path.abspath(output_csv_path)), exist_ok=True)
    with open(output_csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "bucket", "agent", "success_rate_pct", "crash_rate_pct",
            "mean_reward", "mean_steps", "mean_interventions", "mean_r_env"
        ])
        writer.writeheader()
        writer.writerows(csv_rows)
    print(f"\n[save] Evaluation table saved → {output_csv_path}")

    # Generate Chart
    generate_charts(results_summary, output_chart_path)

    return results_summary


def generate_charts(results: Dict[str, Dict], output_path: str) -> None:
    """Generates a 4-panel comparison figure."""
    buckets = list(results.keys())
    x = np.arange(len(buckets))
    width = 0.35

    fig, axs = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(
        "EcoPilot Phase 5 — Policy Evaluation: Adaptive Agent vs Static Baseline\n"
        "(SRTM Mantripukhri Terrain | Calm, Moderate, Severe Atmospheric Buckets)",
        fontsize=12, fontweight="bold"
    )

    adapt_succ = [results[b]["AdaptiveAgent"]["success_rate_pct"] for b in buckets]
    base_succ  = [results[b]["StaticBaseline"]["success_rate_pct"] for b in buckets]

    adapt_crash = [results[b]["AdaptiveAgent"]["crash_rate_pct"] for b in buckets]
    base_crash  = [results[b]["StaticBaseline"]["crash_rate_pct"] for b in buckets]

    adapt_rew = [results[b]["AdaptiveAgent"]["mean_reward"] for b in buckets]
    base_rew  = [results[b]["StaticBaseline"]["mean_reward"] for b in buckets]

    adapt_steps = [results[b]["AdaptiveAgent"]["mean_steps"] for b in buckets]
    base_steps  = [results[b]["StaticBaseline"]["mean_steps"] for b in buckets]

    colors_adapt = "#2b8cbe"
    colors_base  = "#e34a33"

    # ── Panel 1: Success Rate ─────────────────────────────────────────────────
    axs[0, 0].bar(x - width/2, adapt_succ, width, label="Adaptive Agent", color=colors_adapt)
    axs[0, 0].bar(x + width/2, base_succ, width, label="Static Baseline", color=colors_base)
    axs[0, 0].set_ylabel("Success Rate (%)")
    axs[0, 0].set_title("(1) Mission Success Rate")
    axs[0, 0].set_xticks(x)
    axs[0, 0].set_xticklabels(buckets)
    axs[0, 0].set_ylim(0, 100)
    axs[0, 0].grid(axis="y", linestyle="--", alpha=0.5)
    axs[0, 0].legend()

    # ── Panel 2: Crash Rate ───────────────────────────────────────────────────
    axs[0, 1].bar(x - width/2, adapt_crash, width, label="Adaptive Agent", color=colors_adapt)
    axs[0, 1].bar(x + width/2, base_crash, width, label="Static Baseline", color=colors_base)
    axs[0, 1].set_ylabel("Crash Rate (%)")
    axs[0, 1].set_title("(2) Crash Rate (Lower is Safer)")
    axs[0, 1].set_xticks(x)
    axs[0, 1].set_xticklabels(buckets)
    axs[0, 1].set_ylim(0, 100)
    axs[0, 1].grid(axis="y", linestyle="--", alpha=0.5)
    axs[0, 1].legend()

    # ── Panel 3: Mean Reward ──────────────────────────────────────────────────
    axs[1, 0].bar(x - width/2, adapt_rew, width, label="Adaptive Agent", color=colors_adapt)
    axs[1, 0].bar(x + width/2, base_rew, width, label="Static Baseline", color=colors_base)
    axs[1, 0].set_ylabel("Mean Episode Reward")
    axs[1, 0].set_title("(3) Mean Cumulative Reward")
    axs[1, 0].set_xticks(x)
    axs[1, 0].set_xticklabels(buckets)
    axs[1, 0].grid(axis="y", linestyle="--", alpha=0.5)
    axs[1, 0].legend()

    # ── Panel 4: Trajectory Steps ─────────────────────────────────────────────
    axs[1, 1].bar(x - width/2, adapt_steps, width, label="Adaptive Agent", color=colors_adapt)
    axs[1, 1].bar(x + width/2, base_steps, width, label="Static Baseline", color=colors_base)
    axs[1, 1].set_ylabel("Mean Flight Steps")
    axs[1, 1].set_title("(4) Path Efficiency (Mean Steps)")
    axs[1, 1].set_xticks(x)
    axs[1, 1].set_xticklabels(buckets)
    axs[1, 1].grid(axis="y", linestyle="--", alpha=0.5)
    axs[1, 1].legend()

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[save] Evaluation charts saved → {output_path}")


if __name__ == "__main__":
    evaluate_all(episodes_per_bucket=100)
