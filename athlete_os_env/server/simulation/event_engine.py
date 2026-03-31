"""
Match event generator — produces structured events weighted by persona traits.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np


EVENT_TYPES = [
    "pass", "shot", "goal", "assist", "dribble", "tackle",
    "intercept", "foul", "save", "cross", "header", "key_pass",
]

# Mapping from event type to the trait index that most influences it
# Trait indices: 0=speed, 1=stamina, 2=positioning, 3=technical, 4=aerial,
# 5=decision_speed, 6=pressure_tolerance, 7=creativity, 8=work_rate,
# 9=leadership, 10=consistency, 11=injury_resilience, 12=form_momentum,
# 13=big_game_performance, 14=adaptability, 15=teamwork
EVENT_TRAIT_MAP: Dict[str, List[int]] = {
    "pass":      [3, 5, 15],
    "shot":      [3, 0, 13],
    "goal":      [2, 3, 12],
    "assist":    [7, 3, 15],
    "dribble":   [0, 3, 7],
    "tackle":    [8, 2, 6],
    "intercept": [2, 5, 8],
    "foul":      [6, 8, 14],
    "save":      [5, 2, 6],
    "cross":     [3, 7, 0],
    "header":    [4, 2, 13],
    "key_pass":  [7, 5, 15],
}


class EventEngine:
    """Generates match events for a single round based on persona traits."""

    def __init__(self, seed: int = 42):
        self.rng = np.random.RandomState(seed)

    def generate_round_events(
        self,
        persona_vector: list[float] | np.ndarray,
        opponent_strength: float = 0.5,
        match_importance: float = 0.5,
        home_advantage: bool = True,
        fatigue: float = 0.0,
        num_events: int | None = None,
    ) -> List[Dict[str, Any]]:
        pv = np.asarray(persona_vector, dtype=np.float64)
        if pv.sum() > 0:
            pv = pv / pv.sum()

        if num_events is None:
            base = self.rng.poisson(lam=12)
            num_events = max(5, min(base, 25))

        home_bonus = 0.05 if home_advantage else -0.02
        fatigue_penalty = fatigue * 0.15
        importance_boost = match_importance * 0.1

        events: List[Dict[str, Any]] = []
        for _ in range(num_events):
            event_type = self._sample_event_type(pv, opponent_strength)
            success = self._compute_success(
                event_type, pv, opponent_strength,
                home_bonus, fatigue_penalty, importance_boost,
            )
            rating_impact = self._rating_impact(event_type, success)

            events.append({
                "type": event_type,
                "success": success,
                "rating_impact": round(rating_impact, 2),
                "minute": int(self.rng.uniform(1, 90)),
            })

        events.sort(key=lambda e: e["minute"])
        return events

    def _sample_event_type(
        self, pv: np.ndarray, opponent_strength: float
    ) -> str:
        weights = np.ones(len(EVENT_TYPES), dtype=np.float64)
        for i, etype in enumerate(EVENT_TYPES):
            trait_indices = EVENT_TRAIT_MAP.get(etype, [])
            for ti in trait_indices:
                if ti < len(pv):
                    weights[i] += pv[ti]
            if etype in ("tackle", "intercept"):
                weights[i] += opponent_strength * 0.3
        weights = np.clip(weights, 0.01, None)
        weights /= weights.sum()
        idx = self.rng.choice(len(EVENT_TYPES), p=weights)
        return EVENT_TYPES[idx]

    def _compute_success(
        self,
        event_type: str,
        pv: np.ndarray,
        opponent_strength: float,
        home_bonus: float,
        fatigue_penalty: float,
        importance_boost: float,
    ) -> bool:
        trait_indices = EVENT_TRAIT_MAP.get(event_type, [])
        skill = sum(pv[ti] for ti in trait_indices if ti < len(pv))
        prob = 0.3 + skill * 0.5 - opponent_strength * 0.2 + home_bonus - fatigue_penalty + importance_boost
        prob = np.clip(prob, 0.05, 0.95)
        return bool(self.rng.random() < prob)

    @staticmethod
    def _rating_impact(event_type: str, success: bool) -> float:
        base_impact = {
            "goal": 1.0, "assist": 0.6, "key_pass": 0.3, "shot": 0.2,
            "dribble": 0.15, "cross": 0.1, "header": 0.2,
            "pass": 0.05, "tackle": 0.15, "intercept": 0.2,
            "save": 0.5, "foul": -0.2,
        }
        impact = base_impact.get(event_type, 0.1)
        return impact if success else impact * -0.3

    def compute_round_stats(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        goals = sum(1 for e in events if e["type"] == "goal" and e["success"])
        assists = sum(1 for e in events if e["type"] == "assist" and e["success"])
        total_impact = sum(e["rating_impact"] for e in events)
        base_rating = 6.0 + total_impact
        rating = round(np.clip(base_rating, 1.0, 10.0), 1)

        return {
            "goals": goals,
            "assists": assists,
            "rating": rating,
            "shots": sum(1 for e in events if e["type"] in ("shot", "goal")),
            "passes": sum(1 for e in events if e["type"] in ("pass", "key_pass", "assist")),
            "tackles": sum(1 for e in events if e["type"] == "tackle"),
            "total_events": len(events),
        }
