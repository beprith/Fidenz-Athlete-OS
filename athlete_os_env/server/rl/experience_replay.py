"""
Circular buffer for off-policy correction between episodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

import numpy as np


@dataclass
class Transition:
    state: Dict[str, Any]
    action: Dict[str, Any]
    reward: float
    next_state: Dict[str, Any]
    done: bool
    persona_vector: List[float] = field(default_factory=list)
    advantage: float = 0.0


class ExperienceReplay:
    """Fixed-capacity circular buffer storing RL transitions."""

    def __init__(self, capacity: int = 500, seed: int = 42):
        self.capacity = capacity
        self._buffer: list[Transition] = []
        self._position = 0
        self._rng = np.random.RandomState(seed)

    def push(self, transition: Transition) -> None:
        if len(self._buffer) < self.capacity:
            self._buffer.append(transition)
        else:
            self._buffer[self._position] = transition
        self._position = (self._position + 1) % self.capacity

    def sample(self, batch_size: int) -> list[Transition]:
        batch_size = min(batch_size, len(self._buffer))
        indices = self._rng.choice(len(self._buffer), size=batch_size, replace=False)
        return [self._buffer[i] for i in indices]

    def compute_advantages(self, gamma: float = 0.99, lam: float = 0.95) -> None:
        """GAE-style advantage estimation over the buffer."""
        n = len(self._buffer)
        if n == 0:
            return

        advantages = np.zeros(n, dtype=np.float64)
        last_adv = 0.0

        for t in reversed(range(n)):
            if self._buffer[t].done:
                last_adv = 0.0
            next_reward = self._buffer[t + 1].reward if t + 1 < n else 0.0
            delta = self._buffer[t].reward + gamma * next_reward * (1 - int(self._buffer[t].done)) - self._buffer[t].reward
            last_adv = delta + gamma * lam * (1 - int(self._buffer[t].done)) * last_adv
            advantages[t] = last_adv

        for t in range(n):
            self._buffer[t].advantage = float(advantages[t])

    def __len__(self) -> int:
        return len(self._buffer)

    def clear(self) -> None:
        self._buffer.clear()
        self._position = 0
