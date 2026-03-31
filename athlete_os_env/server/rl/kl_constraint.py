"""
KL-divergence penalty — prevents persona drift from seed baseline.
"""

from __future__ import annotations

import numpy as np


class KLConstraint:
    """
    Computes KL(current || baseline) and adapts the penalty coefficient
    when drift is consistently high.
    """

    def __init__(self, beta: float = 0.1, max_beta: float = 1.0):
        self.beta = beta
        self.max_beta = max_beta
        self._drift_history: list[float] = []

    def compute(
        self,
        current_persona: np.ndarray | list[float],
        baseline_persona: np.ndarray | list[float],
    ) -> float:
        eps = 1e-8
        p = np.clip(np.asarray(current_persona, dtype=np.float64), eps, 1.0)
        q = np.clip(np.asarray(baseline_persona, dtype=np.float64), eps, 1.0)

        # Normalize to probability distributions
        p = p / p.sum()
        q = q / q.sum()

        kl = float(np.sum(p * np.log(p / q)))
        penalty = self.beta * kl

        self._drift_history.append(kl)
        self.adapt_beta()

        return penalty

    def adapt_beta(self) -> None:
        if len(self._drift_history) >= 5:
            avg_drift = float(np.mean(self._drift_history[-5:]))
            if avg_drift > 0.3:
                self.beta = min(self.beta * 1.5, self.max_beta)
            elif avg_drift < 0.05:
                self.beta = max(self.beta * 0.8, 0.01)

    def reset(self) -> None:
        self._drift_history.clear()
        self.beta = 0.1
