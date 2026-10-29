"""
train.py — EcoPilot Paired Dual-Agent Training Pipeline
=======================================================

Trains both the Adaptive Q-Learning Agent (conditioned on dynamic R_env) and the
Static Baseline Agent (fixed lambda = 1.0) under identical domain-randomized
atmospheric trajectories and 3D terrain corridor coordinates.

Outputs:
  - data/training_log.csv: Full per-episode training trajectory log.
  - data/q_table_adaptive.json: Serialized policy for the Adaptive Agent.
  - data/q_table_baseline.json: Serialized policy for the Static Baseline Agent.
"""

from __future__ import annotations

import csv
import os
import time
from typing import Any, Dict, List

import numpy as np

from drone_env import DroneEnv, MissionOutcome
from q_agent import QAgent
from static_baseline_agent import StaticBaselineAgent


def run_training(
    num_episodes: int = 700,
    eval_interval: int = 50,
    log_csv_path: str = "data/training_log.csv",
    save_dir: str = "data"
) -> Dict[str, Any]:
    """
    Executes paired training for both RL agents over num_episodes.

    Args:
        num_episodes: Total paired training episodes (default 700 >= 500).
        eval_interval: Frequency of progress report logging.
        log_csv_path: Destination path for training log CSV.
        save_dir: Output directory for learned Q-tables.

    Returns:
        Summary dictionary with learning statistics.
    """
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(log_csv_path)), exist_ok=True)

    print("=" * 68)
    print("EcoPilot — Paired Tabular Q-Learning Training (3D Flight Simulation)")
    print(f"Episodes : {num_episodes} paired episodes")
    print("Agents   : AdaptiveAgent (R_env-conditioned) vs StaticBaseline (fixed lambda)")
    print("Terrain  : SRTM GL1 30m Mantripukhri Valley, Manipur")
    print("=" * 68)

    env = DroneEnv()
    adaptive_agent = QAgent(num_actions=8, learning_rate=0.15, discount_factor=0.95, epsilon_decay=0.994, name="AdaptiveAgent")
    baseline_agent = StaticBaselineAgent(num_actions=8, learning_rate=0.15, discount_factor=0.95, epsilon_decay=0.994)

    csv_file = open(log_csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "episode", "agent_type", "total_reward", "steps",
        "status", "outcome", "success", "crash", "battery_soc", "energy_wh", "r_env", "epsilon"
    ])

    adaptive_history: List[Dict] = []
    baseline_history: List[Dict] = []

    start_time = time.time()

    for ep in range(1, num_episodes + 1):
        # Identical episode seed so both agents face the exact same corridor & weather
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
        outcome_adapt = info.get("outcome", "unknown")
        success_adapt = int(outcome_adapt == "success")
        crash_adapt = int("crash" in outcome_adapt)
        soc_adapt = info.get("battery_soc", 100.0)
        energy_adapt = info.get("energy_wh", 0.0)

        record_adapt = {
            "episode": ep, "agent": "AdaptiveAgent", "reward": total_reward_adapt,
            "steps": steps_adapt, "status": status_adapt, "outcome": outcome_adapt,
            "success": success_adapt, "crash": crash_adapt, "battery_soc": soc_adapt,
            "energy_wh": energy_adapt, "r_env": r_env_val, "eps": eps_adapt
        }
        adaptive_history.append(record_adapt)
        csv_writer.writerow([
            ep, "AdaptiveAgent", round(total_reward_adapt, 2), steps_adapt,
            status_adapt, outcome_adapt, success_adapt, crash_adapt,
            round(soc_adapt, 1), round(energy_adapt, 3), round(r_env_val, 4), round(eps_adapt, 4)
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
        outcome_base = info_b.get("outcome", "unknown")
        success_base = int(outcome_base == "success")
        crash_base = int("crash" in outcome_base)
        soc_base = info_b.get("battery_soc", 100.0)
        energy_base = info_b.get("energy_wh", 0.0)

        record_base = {
            "episode": ep, "agent": "StaticBaseline", "reward": total_reward_base,
            "steps": steps_base, "status": status_base, "outcome": outcome_base,
            "success": success_base, "crash": crash_base, "battery_soc": soc_base,
            "energy_wh": energy_base, "r_env": r_env_val, "eps": eps_base
        }
        baseline_history.append(record_base)
        csv_writer.writerow([
            ep, "StaticBaseline", round(total_reward_base, 2), steps_base,
            status_base, outcome_base, success_base, crash_base,
            round(soc_base, 1), round(energy_base, 3), round(r_env_val, 4), round(eps_base, 4)
        ])

        # Periodic progress report
        if ep % eval_interval == 0:
            w_a = adaptive_history[-eval_interval:]
            w_b = baseline_history[-eval_interval:]

            succ_a = sum(r["success"] for r in w_a) / eval_interval * 100.0
            succ_b = sum(r["success"] for r in w_b) / eval_interval * 100.0
            rew_a = sum(r["reward"] for r in w_a) / eval_interval
            rew_b = sum(r["reward"] for r in w_b) / eval_interval

            print(
                f"[Ep {ep:03d}/{num_episodes}] "
                f"Adaptive: Succ={succ_a:4.1f}% | Rew={rew_a:6.1f}  ||  "
                f"Baseline: Succ={succ_b:4.1f}% | Rew={rew_b:6.1f}  "
                f"(eps={eps_adapt:.2f})"
            )

    csv_file.close()
    elapsed = time.time() - start_time
    print(f"\n[Training Finished] Total elapsed time: {elapsed:.2f} s ({elapsed/num_episodes*1000:.1f} ms/ep)")

    # Done-Condition Verification
    first_50_succ = sum(r["success"] for r in adaptive_history[:50]) / 50.0 * 100.0
    last_50_succ = sum(r["success"] for r in adaptive_history[-50:]) / 50.0 * 100.0
    improvement = last_50_succ - first_50_succ

    print("\n" + "=" * 68)
    print("Learning Improvement Verification:")
    print(f"  First 50 Episodes Success Rate: {first_50_succ:.1f}%")
    print(f"  Last  50 Episodes Success Rate: {last_50_succ:.1f}%")
    print(f"  Absolute Learning Gain        : {improvement:+.1f}%")
    print("=" * 68)

    # Save Q-tables
    q_adapt_path = os.path.join(save_dir, "q_table_adaptive.json")
    q_base_path = os.path.join(save_dir, "q_table_baseline.json")
    adaptive_agent.save_policy_json(q_adapt_path)
    baseline_agent.save_policy_json(q_base_path)

    return {
        "num_episodes": num_episodes,
        "elapsed_seconds": round(elapsed, 2),
        "first_50_success": first_50_succ,
        "last_50_success": last_50_succ,
        "improvement": round(improvement, 2),
    }


if __name__ == "__main__":
    run_training(num_episodes=700, eval_interval=50)
