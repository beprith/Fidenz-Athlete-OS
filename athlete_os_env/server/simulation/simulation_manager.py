"""
Lifecycle management for simulation episodes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from models import PlayerPersona, RoundSummary, SimulationResult


@dataclass
class EpisodeContext:
    """All mutable state for a single simulation episode."""

    episode_id: str = ""
    task_id: str = ""
    status: str = "idle"  # idle | building | simulating | grading | done
    current_round: int = 0
    total_rounds: int = 0
    rounds: List[RoundSummary] = field(default_factory=list)
    scenario_a_result: Optional[SimulationResult] = None
    scenario_b_result: Optional[SimulationResult] = None
    last_error: Optional[str] = None


class SimulationManager:
    """Tracks active episode contexts and provides lifecycle helpers."""

    def __init__(self):
        self._episodes: Dict[str, EpisodeContext] = {}

    def create_episode(self, episode_id: str, task_id: str, total_rounds: int) -> EpisodeContext:
        ctx = EpisodeContext(
            episode_id=episode_id,
            task_id=task_id,
            total_rounds=total_rounds,
        )
        self._episodes[episode_id] = ctx
        return ctx

    def get_episode(self, episode_id: str) -> EpisodeContext | None:
        return self._episodes.get(episode_id)

    def update_status(self, episode_id: str, status: str) -> None:
        ctx = self._episodes.get(episode_id)
        if ctx:
            ctx.status = status

    def record_round(self, episode_id: str, summary: RoundSummary) -> None:
        ctx = self._episodes.get(episode_id)
        if ctx:
            ctx.rounds.append(summary)
            ctx.current_round = summary.round_num

    def record_result(
        self,
        episode_id: str,
        result: SimulationResult,
        scenario: str = "a",
    ) -> None:
        ctx = self._episodes.get(episode_id)
        if ctx:
            if scenario == "a":
                ctx.scenario_a_result = result
            else:
                ctx.scenario_b_result = result

    def is_done(self, episode_id: str) -> bool:
        ctx = self._episodes.get(episode_id)
        if not ctx:
            return True
        return ctx.status == "done" or ctx.current_round >= ctx.total_rounds

    def cleanup(self, episode_id: str) -> None:
        self._episodes.pop(episode_id, None)
