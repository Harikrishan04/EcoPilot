"""
static_baseline_agent.py — EcoPilot Phase 3: Static-Reward Baseline Agent
========================================================================

Implements the baseline tabular Q-learning agent.
Has identical state discretization and update logic as QAgent, but is trained
strictly with a static (unconditioned) penalty weight (lambda = 1.0), remaining
blind to live environmental risk score R_env.
"""

from __future__ import annotations

from q_agent import QAgent


class StaticBaselineAgent(QAgent):
    """
    Baseline agent with identical tabular Q-learning mechanics, trained with
    fixed non-adaptive rewards (blind to dynamic R_env).
    """

    def __init__(
        self,
        num_actions: int = 8,
        learning_rate: float = 0.10,
        discount_factor: float = 0.95,
        epsilon_start: float = 1.0,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
    ):
        super().__init__(
            num_actions=num_actions,
            learning_rate=learning_rate,
            discount_factor=discount_factor,
            epsilon_start=epsilon_start,
            epsilon_min=epsilon_min,
            epsilon_decay=epsilon_decay,
            name="StaticBaselineAgent",
        )

