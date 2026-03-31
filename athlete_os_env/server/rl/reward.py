"""
Bounded sigmoid reward with partial credit signals.
"""

from __future__ import annotations

import numpy as np

from models import AthleteState


def _sigmoid(x: float, steepness: float = 6.0, midpoint: float = 0.5) -> float:
    return float(1.0 / (1.0 + np.exp(-steepness * (x - midpoint))))


class RewardEngine:
    """Computes shaped reward for each simulation step."""

    WEIGHTS = [0.40, 0.30, 0.20, 0.10]  # output, tactical, coherence, efficiency

    HALLUCINATION_PENALTY = -0.3
    REPEAT_PENALTY = -0.2

    def compute(self, result: dict, state: AthleteState) -> float:
        metrics = result.get("performance_metrics", {})
        components = [
            metrics.get("output_score", 0.0),
            metrics.get("tactical_fit", 0.0),
            metrics.get("coherence_score", 0.0),
            metrics.get("step_efficiency", 0.0),
        ]
        raw = sum(w * c for w, c in zip(self.WEIGHTS, components))

        penalty = 0.0
        if result.get("hallucination_detected"):
            penalty += self.HALLUCINATION_PENALTY
        if result.get("repeated_action"):
            penalty += self.REPEAT_PENALTY

        shaped = _sigmoid(raw + penalty)
        return float(np.clip(shaped, 0.0, 1.0))

    @staticmethod
    def get_hint(shaped_reward: float) -> str:
        if shaped_reward >= 0.8:
            return "Excellent — maintain current strategy."
        if shaped_reward >= 0.5:
            return "Good progress. Consider adjusting sim_params for edge cases."
        if shaped_reward >= 0.3:
            return "Below average — try varying the target_context."
        return "Poor fit detected — reconsider formation or player role."
