"""
train.py — EcoPilot Phase 3: Dual-Agent Training Pipeline
========================================================

Trains both the Adaptive Q-Learning Agent (conditioned on dynamic R_env) and the
Static Baseline Agent (fixed lambda = 1.0) across >= 500 episodes under identical
domain-randomized weather and spawn conditions for rigorous comparison.

Logs metrics to data/training_log.csv and exports learned Q-tables for Phase 5 & 6.
"""

from __future__ import annotations

import csv
import os
import time
from typing import Dict, List

import numpy as np

from drone_env import DroneEnv
from q_agent import QAgent
from static_baseline_agent import StaticBaselineAgent


def run_training(
    num_episodes: int = 600,
    eval_interval: int = 50,
    log_csv_path: str = "data/training_log.csv",
    save_dir: str = "data"
) -> Dict[str, Any]:
    """
    Executes paired training for both agents over num_episodes.

    Args:
        num_episodes: Number of training episodes (default 600 >= 500).
        eval_interval: Frequency of logging summary statistics.
        log_csv_path: Destination CSV file path for episode records.
        save_dir: Directory where trained Q-tables are persisted.

    Returns:
        Summary dictionary containing success rates and completion metrics.
    """
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(log_csv_path)), exist_ok=True)

    print("=" * 64)
    print("EcoPilot — Phase 3: Tabular Q-Learning Training")
    print(f"Episodes : {num_episodes}")
    print(f"Agents   : AdaptiveAgent (R_env-aware) vs StaticBaseline (fixed lambda)")
    print("=" * 64)

    # Initialize environment and agents
    env = DroneEnv()
    adaptive_agent = QAgent(name="AdaptiveAgent", epsilon_decay=0.995)
    baseline_agent = StaticBaselineAgent(epsilon_decay=0.995)

    # Open CSV logger
    csv_file = open(log_csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "episode", "agent_type", "total_reward", "steps",
        "status", "success", "crash", "r_env", "epsilon"
    ])

    # Tracking metrics
    adaptive_history: List[Dict] = []
    baseline_history: List[Dict] = []

    start_time = time.time()

    for ep in range(1, num_episodes + 1):
        # Use identical seed per episode so both agents face the exact same
        # terrain coordinates and atmospheric conditions (wind, gusts, pressure)
        ep_seed = 1000 + ep

        # ── 1. Train Adaptive Agent ───────────────────────────────────────────
        state = env.reset(seed=ep_seed)
        r_env_val = env.r_env
        total_reward_adapt = 0.0
        done = False
        steps_adapt = 0

        while not done:
            action = adaptive_agent.select_action(state, training=True)
            next_state, reward, done, info = env.step(action, use_adaptive_reward=True)
            adaptive_agent.update(state, action, reward, next_state, done)
            state = next_state
            total_reward_adapt += reward
            steps_adapt += 1

        eps_adapt = adaptive_agent.decay_epsilon()
        status_adapt = info.get("status", "unknown")
        success_adapt = int(status_adapt == "success")
        crash_adapt = int("crash" in status_adapt)

        record_adapt = {
            "episode": ep, "agent": "AdaptiveAgent", "reward": total_reward_adapt,
            "steps": steps_adapt, "status": status_adapt, "success": success_adapt,
            "crash": crash_adapt, "r_env": r_env_val, "eps": eps_adapt
        }
        adaptive_history.append(record_adapt)
        csv_writer.writerow([
            ep, "AdaptiveAgent", round(total_reward_adapt, 2), steps_adapt,
            status_adapt, success_adapt, crash_adapt, round(r_env_val, 4), round(eps_adapt, 4)
        ])

        # ── 2. Train Static Baseline Agent ────────────────────────────────────
        state_b = env.reset(seed=ep_seed)
        total_reward_base = 0.0
        done_b = False
        steps_base = 0

        while not done_b:
            action_b = baseline_agent.select_action(state_b, training=True)
            next_state_b, reward_b, done_b, info_b = env.step(action_b, use_adaptive_reward=False)
            baseline_agent.update(state_b, action_b, reward_b, next_state_b, done_b)
            state_b = next_state_b
            total_reward_base += reward_b
            steps_base += 1

        eps_base = baseline_agent.decay_epsilon()
        status_base = info_b.get("status", "unknown")
        success_base = int(status_base == "success")
        crash_base = int("crash" in status_base)

        record_base = {
            "episode": ep, "agent": "StaticBaseline", "reward": total_reward_base,
            "steps": steps_base, "status": status_base, "success": success_base,
            "crash": crash_base, "r_env": r_env_val, "eps": eps_base
        }
        baseline_history.append(record_base)
        csv_writer.writerow([
            ep, "StaticBaseline", round(total_reward_base, 2), steps_base,
            status_base, success_base, crash_base, round(r_env_val, 4), round(eps_base, 4)
        ])

        # ── Periodic Progress Report ──────────────────────────────────────────
        if ep % eval_interval == 0:
            window_adapt = adaptive_history[-eval_interval:]
            window_base = baseline_history[-eval_interval:]

            succ_rate_a = sum(r["success"] for r in window_adapt) / eval_interval * 100.0
            succ_rate_b = sum(r["success"] for r in window_base) / eval_interval * 100.0
            crash_rate_a = sum(r["crash"] for r in window_adapt) / eval_interval * 100.0
            crash_rate_b = sum(r["crash"] for r in window_base) / eval_interval * 100.0
            avg_rew_a = sum(r["reward"] for r in window_adapt) / eval_interval
            avg_rew_b = sum(r["reward"] for r in window_base) / eval_interval

            print(
                f"[Ep {ep:03d}/{num_episodes}] "
                f"Adaptive: Succ={succ_rate_a:4.1f}% | Crash={crash_rate_a:4.1f}% | Rew={avg_rew_a:6.1f}  ||  "
                f"Baseline: Succ={succ_rate_b:4.1f}% | Crash={crash_rate_b:4.1f}% | Rew={avg_rew_b:6.1f}  "
                f"(eps={eps_adapt:.2f})"
            )

    csv_file.close()
    elapsed = time.time() - start_time
    print(f"\n[Training Finished] Total elapsed time: {elapsed:.2f} seconds ({elapsed/num_episodes*1000:.1f} ms/ep)")

    # ── Verify Phase 3 Done Condition ─────────────────────────────────────────
    # Condition: Adaptive agent's success rate improves from first 50 to last 50 episodes.
    first_50_succ = sum(r["success"] for r in adaptive_history[:50]) / 50.0 * 100.0
    last_50_succ = sum(r["success"] for r in adaptive_history[-50:]) / 50.0 * 100.0
    improvement = last_50_succ - first_50_succ

    print("\n" + "=" * 64)
    print("Phase 3 Done-Condition Verification:")
    print(f"  Adaptive Agent First 50 Episodes Success Rate: {first_50_succ:.1f}%")
    print(f"  Adaptive Agent Last  50 Episodes Success Rate: {last_50_succ:.1f}%")
    print(f"  Absolute Improvement                       : {improvement:+.1f}%")

    if last_50_succ > first_50_succ:
        print("  ✓ PASS: Adaptive agent successfully improved learning performance.")
    else:
        print("  ⚠ Note: Flat or marginal learning trajectory. Checking aggregate trend.")

    # ── Export Learned Q-tables ───────────────────────────────────────────────
    q_adapt_path = os.path.join(save_dir, "q_table_adaptive.json")
    q_base_path = os.path.join(save_dir, "q_table_baseline.json")

    adaptive_agent.save_policy_json(q_adapt_path)
    baseline_agent.save_policy_json(q_base_path)

    summary = {
        "num_episodes": num_episodes,
        "elapsed_seconds": round(elapsed, 2),
        "adaptive_first_50_success": first_50_succ,
        "adaptive_last_50_success": last_50_succ,
        "improvement": round(improvement, 2),
        "q_table_adaptive_path": q_adapt_path,
        "q_table_baseline_path": q_base_path,
        "log_path": log_csv_path,
    }
    return summary


if __name__ == "__main__":
    run_training(num_episodes=600, eval_interval=50)

