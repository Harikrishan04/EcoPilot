"""
train.py — EcoPilot Paired Multi-Agent Training Pipeline with PBRS Comparison
=============================================================================

Trains comparative RL agents under identical domain-randomized atmospheric trajectories
and 3D terrain corridor coordinates:
  1. Adaptive Q-Learning Agent (conditioned on dynamic R_env, unshaped)
  2. Adaptive Q-Learning Agent + PBRS (conditioned on R_env + A*-guided potential shaping)
  3. Static Baseline Agent (fixed unconditioned lambda = 1.0, unshaped)

Outputs:
  - data/training_log.csv: Full per-episode training trajectory log for all agents.
  - data/q_table_adaptive.json: Serialized policy for the Adaptive Agent.
  - data/q_table_adaptive_pbrs.json: Serialized policy for the Adaptive + PBRS Agent.
  - data/q_table_baseline.json: Serialized policy for the Static Baseline Agent.
  - data/training_learning_curves.png: Comparative 4-panel learning curves.
"""

from __future__ import annotations

import csv
import os
import time
from typing import Any, Dict, List

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from drone_env import DroneEnv, MissionOutcome
from q_agent import QAgent
from static_baseline_agent import StaticBaselineAgent


def plot_training_learning_curves(
    adaptive_history: List[Dict],
    pbrs_history: List[Dict],
    baseline_history: List[Dict],
    output_png: str = "data/training_learning_curves.png",
    window: int = 50,
) -> None:
    """Plots comparative 4-panel training learning curves across all agents."""
    os.makedirs(os.path.dirname(os.path.abspath(output_png)), exist_ok=True)
    n = len(adaptive_history)
    eps = np.arange(1, n + 1)

    def rolling_mean(arr: List[float], w: int) -> np.ndarray:
        s = np.cumsum(np.insert(arr, 0, 0.0))
        res = np.zeros(len(arr))
        for i in range(len(arr)):
            start_idx = max(0, i - w + 1)
            res[i] = (s[i + 1] - s[start_idx]) / (i + 1 - start_idx)
        return res

    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle(
        "EcoPilot — Multi-Agent Training Dynamics on SRTM Topography\n"
        "(Adaptive Agent vs Adaptive + PBRS (A*-Guided) vs Static Baseline)",
        fontsize=13, fontweight="bold"
    )

    agents = [
        ("Adaptive (Unshaped)", adaptive_history, "#2b8cbe", "-"),
        ("Adaptive + PBRS (A*-Guided)", pbrs_history, "#8856a7", "-"),
        ("Static Baseline", baseline_history, "#e34a33", "--"),
    ]

    # 1. Success Rate (%)
    ax1 = axs[0, 0]
    for lbl, hist, color, ls in agents:
        succ = [r["success"] * 100.0 for r in hist]
        ax1.plot(eps, rolling_mean(succ, window), label=lbl, color=color, linestyle=ls, linewidth=2.0)
    ax1.set_title(f"(1) Mission Success Rate (Rolling {window} Ep)")
    ax1.set_xlabel("Episode")
    ax1.set_ylabel("Success Rate (%)")
    ax1.set_ylim(-5, 105)
    ax1.grid(True, linestyle="--", alpha=0.5)
    ax1.legend(loc="lower right")

    # 2. Unshaped Return
    ax2 = axs[0, 1]
    for lbl, hist, color, ls in agents:
        rews = [r.get("unshaped_reward", r["reward"]) for r in hist]
        ax2.plot(eps, rolling_mean(rews, window), label=lbl, color=color, linestyle=ls, linewidth=2.0)
    ax2.set_title(f"(2) True Unshaped Return (Rolling {window} Ep)")
    ax2.set_xlabel("Episode")
    ax2.set_ylabel("Mean Return (Unshaped)")
    ax2.grid(True, linestyle="--", alpha=0.5)
    ax2.legend(loc="lower right")

    # 3. Episode Steps (Efficiency)
    ax3 = axs[1, 0]
    for lbl, hist, color, ls in agents:
        steps = [r["steps"] for r in hist]
        ax3.plot(eps, rolling_mean(steps, window), label=lbl, color=color, linestyle=ls, linewidth=2.0)
    ax3.set_title(f"(3) Flight Steps to Goal / Episode (Rolling {window} Ep)")
    ax3.set_xlabel("Episode")
    ax3.set_ylabel("Mean Steps")
    ax3.grid(True, linestyle="--", alpha=0.5)
    ax3.legend(loc="upper right")

    # 4. Battery SoC Remaining (%)
    ax4 = axs[1, 1]
    for lbl, hist, color, ls in agents:
        soc = [r["battery_soc"] for r in hist]
        ax4.plot(eps, rolling_mean(soc, window), label=lbl, color=color, linestyle=ls, linewidth=2.0)
    ax4.set_title(f"(4) Final Battery SoC (Rolling {window} Ep)")
    ax4.set_xlabel("Episode")
    ax4.set_ylabel("SoC Remaining (%)")
    ax4.grid(True, linestyle="--", alpha=0.5)
    ax4.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(output_png, dpi=200)
    plt.close()
    print(f"[save] Training learning curves figure saved → {output_png}")


def run_training(
    num_episodes: int = 700,
    eval_interval: int = 50,
    log_csv_path: str = "data/training_log.csv",
    save_dir: str = "data",
    include_pbrs: bool = True,
) -> Dict[str, Any]:
    """
    Executes paired training for comparative RL agents over num_episodes.

    Args:
        num_episodes: Total paired training episodes (default 700).
        eval_interval: Frequency of progress report logging.
        log_csv_path: Destination path for training log CSV.
        save_dir: Output directory for learned Q-tables.
        include_pbrs: Whether to include the A*-guided PBRS agent.

    Returns:
        Summary dictionary with learning statistics.
    """
    os.makedirs(save_dir, exist_ok=True)
    os.makedirs(os.path.dirname(os.path.abspath(log_csv_path)), exist_ok=True)

    print("=" * 72)
    print("EcoPilot — Paired Multi-Agent Tabular Q-Learning Training")
    print(f"Episodes : {num_episodes} paired episodes")
    print("Agents   : AdaptiveAgent vs AdaptiveAgent_PBRS vs StaticBaseline")
    print("Terrain  : SRTM GL1 30m Mantripukhri Valley, Manipur")
    print("=" * 72)

    env = DroneEnv()
    adaptive_agent = QAgent(num_actions=8, learning_rate=0.15, discount_factor=0.95, epsilon_decay=0.994, name="AdaptiveAgent")
    pbrs_agent = QAgent(num_actions=8, learning_rate=0.15, discount_factor=0.95, epsilon_decay=0.994, name="AdaptiveAgent_PBRS")
    baseline_agent = StaticBaselineAgent(num_actions=8, learning_rate=0.15, discount_factor=0.95, epsilon_decay=0.994)

    csv_file = open(log_csv_path, "w", newline="")
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow([
        "episode", "agent_type", "total_reward", "unshaped_reward", "steps",
        "status", "outcome", "success", "crash", "battery_soc", "energy_wh", "r_env", "epsilon"
    ])

    adaptive_history: List[Dict] = []
    pbrs_history: List[Dict] = []
    baseline_history: List[Dict] = []

    start_time = time.time()

    for ep in range(1, num_episodes + 1):
        ep_seed = 1000 + ep

        # ── 1. Train Adaptive Agent (Unshaped) ────────────────────────────────
        state = env.reset(seed=ep_seed)
        r_env_val = env.r_env
        total_reward_adapt = 0.0
        done = False
        steps_adapt = 0

        while not done:
            action = adaptive_agent.select_action(state, training=True)
            next_state, reward, done, info = env.step(action, use_adaptive_reward=True, use_pbrs=False)
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
            "unshaped_reward": total_reward_adapt, "steps": steps_adapt,
            "status": status_adapt, "outcome": outcome_adapt,
            "success": success_adapt, "crash": crash_adapt, "battery_soc": soc_adapt,
            "energy_wh": energy_adapt, "r_env": r_env_val, "eps": eps_adapt
        }
        adaptive_history.append(record_adapt)
        csv_writer.writerow([
            ep, "AdaptiveAgent", round(total_reward_adapt, 2), round(total_reward_adapt, 2),
            steps_adapt, status_adapt, outcome_adapt, success_adapt, crash_adapt,
            round(soc_adapt, 1), round(energy_adapt, 3), round(r_env_val, 4), round(eps_adapt, 4)
        ])

        # ── 2. Train Adaptive Agent + PBRS (A*-Guided Shaping) ─────────────────
        if include_pbrs:
            state_p = env.reset(seed=ep_seed)
            total_reward_pbrs = 0.0
            unshaped_reward_pbrs = 0.0
            done_p = False
            steps_pbrs = 0

            while not done_p:
                action_p = pbrs_agent.select_action(state_p, training=True)
                next_state_p, reward_p, done_p, info_p = env.step(action_p, use_adaptive_reward=True, use_pbrs=True)
                pbrs_agent.update(state_p, action_p, reward_p, next_state_p, done_p)
                state_p = next_state_p
                total_reward_pbrs += reward_p
                unshaped_reward_pbrs += info_p.get("unshaped_reward", reward_p)
                steps_pbrs += 1

            eps_pbrs = pbrs_agent.decay_epsilon()
            status_p = info_p.get("status", "unknown")
            outcome_p = info_p.get("outcome", "unknown")
            success_p = int(outcome_p == "success")
            crash_p = int("crash" in outcome_p)
            soc_p = info_p.get("battery_soc", 100.0)
            energy_p = info_p.get("energy_wh", 0.0)

            record_pbrs = {
                "episode": ep, "agent": "AdaptiveAgent_PBRS", "reward": total_reward_pbrs,
                "unshaped_reward": unshaped_reward_pbrs, "steps": steps_pbrs,
                "status": status_p, "outcome": outcome_p,
                "success": success_p, "crash": crash_p, "battery_soc": soc_p,
                "energy_wh": energy_p, "r_env": r_env_val, "eps": eps_pbrs
            }
            pbrs_history.append(record_pbrs)
            csv_writer.writerow([
                ep, "AdaptiveAgent_PBRS", round(total_reward_pbrs, 2), round(unshaped_reward_pbrs, 2),
                steps_pbrs, status_p, outcome_p, success_p, crash_p,
                round(soc_p, 1), round(energy_p, 3), round(r_env_val, 4), round(eps_pbrs, 4)
            ])

        # ── 3. Train Static Baseline Agent ────────────────────────────────────
        state_b = env.reset(seed=ep_seed)
        total_reward_base = 0.0
        done_b = False
        steps_base = 0

        while not done_b:
            action_b = baseline_agent.select_action(state_b, training=True)
            next_state_b, reward_b, done_b, info_b = env.step(action_b, use_adaptive_reward=False, use_pbrs=False)
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
            "unshaped_reward": total_reward_base, "steps": steps_base,
            "status": status_base, "outcome": outcome_base,
            "success": success_base, "crash": crash_base, "battery_soc": soc_base,
            "energy_wh": energy_base, "r_env": r_env_val, "eps": eps_base
        }
        baseline_history.append(record_base)
        csv_writer.writerow([
            ep, "StaticBaseline", round(total_reward_base, 2), round(total_reward_base, 2),
            steps_base, status_base, outcome_base, success_base, crash_base,
            round(soc_base, 1), round(energy_base, 3), round(r_env_val, 4), round(eps_base, 4)
        ])

        # Periodic progress report
        if ep % eval_interval == 0:
            w_a = adaptive_history[-eval_interval:]
            w_p = pbrs_history[-eval_interval:] if include_pbrs else []
            w_b = baseline_history[-eval_interval:]

            succ_a = sum(r["success"] for r in w_a) / eval_interval * 100.0
            succ_b = sum(r["success"] for r in w_b) / eval_interval * 100.0
            rew_a = sum(r["unshaped_reward"] for r in w_a) / eval_interval
            rew_b = sum(r["unshaped_reward"] for r in w_b) / eval_interval

            pbrs_str = ""
            if include_pbrs and w_p:
                succ_p = sum(r["success"] for r in w_p) / eval_interval * 100.0
                rew_p = sum(r["unshaped_reward"] for r in w_p) / eval_interval
                pbrs_str = f"PBRS: Succ={succ_p:4.1f}% | UnshapedRew={rew_p:6.1f}  ||  "

            print(
                f"[Ep {ep:03d}/{num_episodes}] "
                f"Adaptive: Succ={succ_a:4.1f}% | Rew={rew_a:6.1f}  ||  "
                f"{pbrs_str}"
                f"Baseline: Succ={succ_b:4.1f}% | Rew={rew_b:6.1f}  "
                f"(eps={eps_adapt:.2f})"
            )

    csv_file.close()
    elapsed = time.time() - start_time
    print(f"\n[Training Finished] Total elapsed time: {elapsed:.2f} s ({elapsed/num_episodes*1000:.1f} ms/ep)")

    # Done-Condition Verification
    first_50_succ_a = sum(r["success"] for r in adaptive_history[:50]) / 50.0 * 100.0
    last_50_succ_a = sum(r["success"] for r in adaptive_history[-50:]) / 50.0 * 100.0
    improvement_a = last_50_succ_a - first_50_succ_a

    print("\n" + "=" * 72)
    print("Learning Improvement Verification (First 50 -> Last 50 Episodes):")
    print(f"  Adaptive (Unshaped) : {first_50_succ_a:.1f}% -> {last_50_succ_a:.1f}% (Gain: {improvement_a:+.1f}%)")

    first_50_succ_p, last_50_succ_p, improvement_p = 0.0, 0.0, 0.0
    if include_pbrs:
        first_50_succ_p = sum(r["success"] for r in pbrs_history[:50]) / 50.0 * 100.0
        last_50_succ_p = sum(r["success"] for r in pbrs_history[-50:]) / 50.0 * 100.0
        improvement_p = last_50_succ_p - first_50_succ_p
        print(f"  Adaptive + PBRS (A*) : {first_50_succ_p:.1f}% -> {last_50_succ_p:.1f}% (Gain: {improvement_p:+.1f}%)")

    first_50_succ_b = sum(r["success"] for r in baseline_history[:50]) / 50.0 * 100.0
    last_50_succ_b = sum(r["success"] for r in baseline_history[-50:]) / 50.0 * 100.0
    improvement_b = last_50_succ_b - first_50_succ_b
    print(f"  Static Baseline      : {first_50_succ_b:.1f}% -> {last_50_succ_b:.1f}% (Gain: {improvement_b:+.1f}%)")
    print("=" * 72)

    # Save Q-tables
    q_adapt_path = os.path.join(save_dir, "q_table_adaptive.json")
    q_base_path = os.path.join(save_dir, "q_table_baseline.json")
    adaptive_agent.save_policy_json(q_adapt_path)
    baseline_agent.save_policy_json(q_base_path)

    if include_pbrs:
        q_pbrs_path = os.path.join(save_dir, "q_table_adaptive_pbrs.json")
        pbrs_agent.save_policy_json(q_pbrs_path)
        plot_training_learning_curves(
            adaptive_history, pbrs_history, baseline_history,
            output_png=os.path.join(save_dir, "training_learning_curves.png")
        )

    return {
        "num_episodes": num_episodes,
        "elapsed_seconds": round(elapsed, 2),
        "adaptive_first_50": first_50_succ_a,
        "adaptive_last_50": last_50_succ_a,
        "pbrs_first_50": first_50_succ_p,
        "pbrs_last_50": last_50_succ_p,
    }


if __name__ == "__main__":
    run_training(num_episodes=700, eval_interval=50, include_pbrs=True)

