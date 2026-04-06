"""
Match event generator — produces structured events weighted by persona traits.
Sport-aware: generates soccer, basketball, or cricket events based on config.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

# ---------------------------------------------------------------------------
# Trait indices: 0=speed, 1=stamina, 2=positioning, 3=technical, 4=aerial,
# 5=decision_speed, 6=pressure_tolerance, 7=creativity, 8=work_rate,
# 9=leadership, 10=consistency, 11=injury_resilience, 12=form_momentum,
# 13=big_game_performance, 14=adaptability, 15=teamwork
# ---------------------------------------------------------------------------

SPORT_EVENTS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "soccer": {
        "events": {
            "pass":      {"traits": [3, 5, 15], "rating_impact": 0.05},
            "shot":      {"traits": [3, 0, 13], "rating_impact": 0.2},
            "goal":      {"traits": [2, 3, 12], "rating_impact": 1.0},
            "assist":    {"traits": [7, 3, 15], "rating_impact": 0.6},
            "dribble":   {"traits": [0, 3, 7],  "rating_impact": 0.15},
            "tackle":    {"traits": [8, 2, 6],  "rating_impact": 0.15},
            "intercept": {"traits": [2, 5, 8],  "rating_impact": 0.2},
            "foul":      {"traits": [6, 8, 14], "rating_impact": -0.2},
            "save":      {"traits": [5, 2, 6],  "rating_impact": 0.5},
            "cross":     {"traits": [3, 7, 0],  "rating_impact": 0.1},
            "header":    {"traits": [4, 2, 13], "rating_impact": 0.2},
            "key_pass":  {"traits": [7, 5, 15], "rating_impact": 0.3},
        },
        "base_events": 12,
        "match_minutes": 90,
    },
    "basketball": {
        "events": {
            "two_pointer":   {"traits": [3, 2, 12], "rating_impact": 0.4},
            "three_pointer": {"traits": [3, 7, 13], "rating_impact": 0.7},
            "free_throw":    {"traits": [3, 6, 10], "rating_impact": 0.2},
            "assist":        {"traits": [7, 5, 15], "rating_impact": 0.5},
            "rebound":       {"traits": [4, 2, 8],  "rating_impact": 0.3},
            "steal":         {"traits": [0, 5, 14], "rating_impact": 0.4},
            "block":         {"traits": [4, 5, 6],  "rating_impact": 0.5},
            "turnover":      {"traits": [5, 6, 10], "rating_impact": -0.4},
            "dunk":          {"traits": [0, 4, 13], "rating_impact": 0.6},
            "layup":         {"traits": [0, 3, 7],  "rating_impact": 0.3},
            "foul":          {"traits": [8, 6, 14], "rating_impact": -0.2},
        },
        "base_events": 18,
        "match_minutes": 48,
    },
    "cricket": {
        "events": {
            "single":       {"traits": [0, 8, 10], "rating_impact": 0.1},
            "boundary":     {"traits": [3, 7, 12], "rating_impact": 0.4},
            "six":          {"traits": [3, 13, 7], "rating_impact": 0.7},
            "dot_ball":     {"traits": [6, 10, 1], "rating_impact": -0.05},
            "wicket":       {"traits": [3, 6, 13], "rating_impact": 1.0},
            "catch":        {"traits": [2, 5, 14], "rating_impact": 0.5},
            "run_out":      {"traits": [0, 5, 8],  "rating_impact": 0.4},
            "stumping":     {"traits": [5, 3, 6],  "rating_impact": 0.5},
            "wide":         {"traits": [3, 10, 6], "rating_impact": -0.15},
            "no_ball":      {"traits": [10, 3, 8], "rating_impact": -0.2},
            "maiden_over":  {"traits": [10, 6, 8], "rating_impact": 0.6},
        },
        "base_events": 15,
        "match_minutes": 200,
    },
}


class EventEngine:
    """Generates match events for a single round based on persona traits and sport."""

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
        sport: str = "soccer",
    ) -> List[Dict[str, Any]]:
        pv = np.asarray(persona_vector, dtype=np.float64)
        if pv.sum() > 0:
            pv = pv / pv.sum()

        sport_cfg = SPORT_EVENTS.get(sport, SPORT_EVENTS["soccer"])
        event_defs = sport_cfg["events"]
        event_names = list(event_defs.keys())
        max_minutes = sport_cfg["match_minutes"]

        if num_events is None:
            base = self.rng.poisson(lam=sport_cfg["base_events"])
            num_events = max(5, min(base, 30))

        home_bonus = 0.05 if home_advantage else -0.02
        fatigue_penalty = fatigue * 0.15
        importance_boost = match_importance * 0.1

        events: List[Dict[str, Any]] = []
        for _ in range(num_events):
            event_type = self._sample_event_type(event_names, event_defs, pv, opponent_strength)
            success = self._compute_success(
                event_defs[event_type]["traits"], pv, opponent_strength,
                home_bonus, fatigue_penalty, importance_boost,
            )
            rating_impact = self._rating_impact(event_defs[event_type]["rating_impact"], success)

            events.append({
                "type": event_type,
                "success": success,
                "rating_impact": round(rating_impact, 2),
                "minute": int(self.rng.uniform(1, max_minutes)),
            })

        events.sort(key=lambda e: e["minute"])
        return events

    def _sample_event_type(
        self,
        event_names: List[str],
        event_defs: Dict[str, Dict[str, Any]],
        pv: np.ndarray,
        opponent_strength: float,
    ) -> str:
        weights = np.ones(len(event_names), dtype=np.float64)
        for i, ename in enumerate(event_names):
            for ti in event_defs[ename]["traits"]:
                if ti < len(pv):
                    weights[i] += pv[ti]
            if event_defs[ename]["rating_impact"] < 0:
                weights[i] += opponent_strength * 0.3
        weights = np.clip(weights, 0.01, None)
        weights /= weights.sum()
        idx = self.rng.choice(len(event_names), p=weights)
        return event_names[idx]

    def _compute_success(
        self,
        trait_indices: List[int],
        pv: np.ndarray,
        opponent_strength: float,
        home_bonus: float,
        fatigue_penalty: float,
        importance_boost: float,
    ) -> bool:
        skill = sum(pv[ti] for ti in trait_indices if ti < len(pv))
        prob = 0.3 + skill * 0.5 - opponent_strength * 0.2 + home_bonus - fatigue_penalty + importance_boost
        prob = np.clip(prob, 0.05, 0.95)
        return bool(self.rng.random() < prob)

    @staticmethod
    def _rating_impact(base_impact: float, success: bool) -> float:
        return base_impact if success else base_impact * -0.3

    def compute_round_stats(self, events: List[Dict[str, Any]], sport: str = "soccer") -> Dict[str, Any]:
        total_impact = sum(e["rating_impact"] for e in events)
        base_rating = 6.0 + total_impact
        rating = round(np.clip(base_rating, 1.0, 10.0), 1)

        if sport == "soccer":
            goals = sum(1 for e in events if e["type"] == "goal" and e["success"])
            assists = sum(1 for e in events if e["type"] == "assist" and e["success"])
            return {
                "goals": goals, "assists": assists, "rating": rating,
                "shots": sum(1 for e in events if e["type"] in ("shot", "goal")),
                "passes": sum(1 for e in events if e["type"] in ("pass", "key_pass", "assist")),
                "tackles": sum(1 for e in events if e["type"] == "tackle"),
                "total_events": len(events),
            }
        elif sport == "basketball":
            points = (
                sum(2 for e in events if e["type"] == "two_pointer" and e["success"])
                + sum(3 for e in events if e["type"] == "three_pointer" and e["success"])
                + sum(1 for e in events if e["type"] == "free_throw" and e["success"])
                + sum(2 for e in events if e["type"] in ("dunk", "layup") and e["success"])
            )
            return {
                "points": points, "rating": rating,
                "assists": sum(1 for e in events if e["type"] == "assist" and e["success"]),
                "rebounds": sum(1 for e in events if e["type"] == "rebound" and e["success"]),
                "steals": sum(1 for e in events if e["type"] == "steal" and e["success"]),
                "blocks": sum(1 for e in events if e["type"] == "block" and e["success"]),
                "turnovers": sum(1 for e in events if e["type"] == "turnover"),
                "total_events": len(events),
            }
        else:
            runs = (
                sum(1 for e in events if e["type"] == "single" and e["success"])
                + sum(4 for e in events if e["type"] == "boundary" and e["success"])
                + sum(6 for e in events if e["type"] == "six" and e["success"])
            )
            return {
                "runs": runs, "rating": rating,
                "wickets": sum(1 for e in events if e["type"] == "wicket" and e["success"]),
                "catches": sum(1 for e in events if e["type"] == "catch" and e["success"]),
                "boundaries": sum(1 for e in events if e["type"] in ("boundary", "six") and e["success"]),
                "dot_balls": sum(1 for e in events if e["type"] == "dot_ball"),
                "extras": sum(1 for e in events if e["type"] in ("wide", "no_ball")),
                "total_events": len(events),
            }
