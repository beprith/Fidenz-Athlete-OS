"""
Lightweight PPO update on a 16-dim persona weight vector.
No neural network — operates directly on the trait simplex.
"""

from __future__ import annotations

import numpy as np

from models import TRAIT_COUNT


def softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum()


class PPOPolicy:
    """
    Proximal Policy Optimization on a low-dimensional persona vector.
    The 'policy' is a 16-dim logit vector whose softmax gives trait weights.
    """

    def __init__(
        self,
        dim: int = TRAIT_COUNT,
        lr: float = 3e-3,
        clip_eps: float = 0.2,
        entropy_coeff: float = 0.01,
        seed: int = 42,
    ):
        self.dim = dim
        self.lr = lr
        self.clip_eps = clip_eps
        self.entropy_coeff = entropy_coeff
        self.rng = np.random.RandomState(seed)

        self.logits = np.zeros(dim, dtype=np.float64)
        self._old_logits: np.ndarray | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_weights(self) -> np.ndarray:
        return softmax(self.logits)

    def initialize_from_persona(self, trait_vector: list[float]) -> None:
        arr = np.asarray(trait_vector, dtype=np.float64)
        arr = np.clip(arr, 1e-8, None)
        arr = arr / arr.sum()
        self.logits = np.log(arr + 1e-8)
        self._old_logits = self.logits.copy()

    def update(self, advantages: np.ndarray, old_probs: np.ndarray) -> dict:
        """
        Single PPO update step.
        Returns dict with diagnostics (policy_loss, entropy, clip_fraction).
        """
        if self._old_logits is None:
            self._old_logits = self.logits.copy()

        new_probs = softmax(self.logits)
        ratio = new_probs / (old_probs + 1e-8)

        clipped_ratio = np.clip(ratio, 1.0 - self.clip_eps, 1.0 + self.clip_eps)
        surrogate = np.minimum(ratio * advantages, clipped_ratio * advantages)
        policy_loss = -surrogate.mean()

        entropy = -np.sum(new_probs * np.log(new_probs + 1e-8))

        grad = -advantages * (1.0 - new_probs)  # simplified gradient
        grad -= self.entropy_coeff * (-np.log(new_probs + 1e-8) - 1.0)

        self.logits -= self.lr * grad
        self._old_logits = self.logits.copy()

        clip_fraction = float(np.mean(np.abs(ratio - 1.0) > self.clip_eps))

        return {
            "policy_loss": float(policy_loss),
            "entropy": float(entropy),
            "clip_fraction": clip_fraction,
        }

    def snapshot(self) -> dict:
        return {
            "logits": self.logits.tolist(),
            "weights": self.get_weights().tolist(),
        }

    def reset(self) -> None:
        self.logits = np.zeros(self.dim, dtype=np.float64)
        self._old_logits = None
