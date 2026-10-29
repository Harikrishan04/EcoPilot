"""
q_agent.py — EcoPilot Phase 3: Tabular Q-Learning Agent
======================================================

Implements a tabular Q-learning agent for autonomous drone navigation.
Uses epsilon-greedy action selection, Bellman optimality update, and policy serialization.
"""

from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

import numpy as np


class QAgent:
    """Tabular Q-learning agent for discrete state and action spaces."""

    def __init__(
        self,
        num_actions: int = 8,
        learning_rate: float = 0.10,
        discount_factor: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
        name: str = "AdaptiveQAgent",
    ):
        """
        Initializes the Q-learning agent.

        Args:
            num_actions: Number of discrete actions (default 8).
            learning_rate: Learning rate alpha in [0.0, 1.0].
            discount_factor: Temporal discount factor gamma in [0.0, 1.0].
            epsilon_start: Initial exploration probability.
            epsilon_min: Minimum exploration floor.
            epsilon_decay: Multiplicative decay factor per episode.
            name: Agent identifier label.
        """
        self.num_actions = num_actions
        self.lr = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon_start
        self.eps_min = epsilon_min
        self.eps_decay = epsilon_decay
        self.name = name

        # Q-table: mapping from state tuple -> np.ndarray of shape (num_actions,)
        self.q_table: Dict[Tuple[int, ...], np.ndarray] = {}

    def get_q_values(self, state: Tuple[int, ...]) -> np.ndarray:
        """Retrieves or initializes the Q-values array for a given state."""
        if state not in self.q_table:
            self.q_table[state] = np.zeros(self.num_actions, dtype=np.float32)
        return self.q_table[state]

    def select_action(self, state: Tuple[int, ...], training: bool = True) -> int:
        """
        Selects an action using epsilon-greedy policy during training,
        or pure greedy policy during evaluation/inference.

        Args:
            state: Discretized state tuple.
            training: Whether exploration is enabled.

        Returns:
            Action integer in 0..(num_actions - 1).
        """
        if training and (np.random.random() < self.epsilon):
            return int(np.random.randint(0, self.num_actions))

        q_vals = self.get_q_values(state)
        # Random tie-breaking among maximum Q-values
        max_val = np.max(q_vals)
        best_actions = np.flatnonzero(q_vals == max_val)
        return int(np.random.choice(best_actions))

    def update(
        self,
        state: Tuple[int, ...],
        action: int,
        reward: float,
        next_state: Tuple[int, ...],
        done: bool,
    ) -> float:
        """
        Applies standard Bellman tabular Q-learning update.

        Formula:
            Q(s, a) <- Q(s, a) + alpha * [r + gamma * max_a' Q(s', a') - Q(s, a)]

        Returns:
            Temporal difference error.
        """
        current_q = self.get_q_values(state)[action]

        if done:
            target = reward
        else:
            next_max_q = np.max(self.get_q_values(next_state))
            target = reward + self.gamma * next_max_q

        td_error = float(target - current_q)
        self.q_table[state][action] += self.lr * td_error
        return td_error

    def decay_epsilon(self) -> float:
        """Decays epsilon by decay factor down to the minimum floor."""
        self.epsilon = max(self.eps_min, self.epsilon * self.eps_decay)
        return self.epsilon

    def save_policy_json(self, filepath: str) -> None:
        """Exports the Q-table as JSON for browser playback (Phase 6)."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        # Convert tuple keys to string "r_c_h_risk" for valid JSON format
        serializable_dict = {
            ",".join(map(str, state)): [round(float(v), 4) for v in q_vals]
            for state, q_vals in self.q_table.items()
        }
        meta = {
            "agent_name": self.name,
            "num_states_learned": len(self.q_table),
            "num_actions": self.num_actions,
            "q_table": serializable_dict,
        }
        with open(filepath, "w") as f:
            json.dump(meta, f, indent=2)
        print(f"[save] Exported {self.name} Q-table ({len(self.q_table)} states) → {filepath}")

    def load_policy_json(self, filepath: str) -> None:
        """Loads a pre-trained Q-table from JSON."""
        with open(filepath, "r") as f:
            meta = json.load(f)
        q_dict = meta.get("q_table", {})
        self.q_table = {}
        for state_str, vals in q_dict.items():
            state_tuple = tuple(int(x) for x in state_str.split(","))
            self.q_table[state_tuple] = np.array(vals, dtype=np.float32)
        print(f"[load] Loaded {self.name} Q-table ({len(self.q_table)} states) from {filepath}")

