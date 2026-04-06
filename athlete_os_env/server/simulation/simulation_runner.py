"""
Dual-context async simulation runner.
Runs Scenario A (current team) vs Scenario B (target team) in parallel.
Sport-aware: passes sport context to event engine for correct event generation.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Tuple

import numpy as np

from models import PlayerPersona, RoundSummary, SimulationResult
from server.simulation.event_engine import EventEngine
from server.simulation.persona_config import SimConfig, adjust_fatigue

SPORT_MATCH_MINUTES = {
    "soccer": 90,
    "basketball": 48,
    "cricket": 200,
}


class SimulationRunner:
    """Runs match simulations for a player persona under a given config."""

    def __init__(self, seed: int = 42):
        self.engine = EventEngine(seed=seed)

    def run_round(self, config: SimConfig, round_num: int) -> RoundSummary:
        sport = config.sport or "soccer"
        events = self.engine.generate_round_events(
            persona_vector=config.persona_vector,
            opponent_strength=config.opponent_strength,
            match_importance=config.match_importance,
            home_advantage=(config.home_away == "home"),
            fatigue=config.fatigue,
            sport=sport,
        )
        stats = self.engine.compute_round_stats(events, sport=sport)

        fatigue_delta = 0.03 + config.fatigue * 0.02
        config.fatigue = min(1.0, config.fatigue + fatigue_delta)

        goals = stats.get("goals", 0)
        assists = stats.get("assists", 0)
        if sport == "basketball":
            goals = stats.get("points", 0)
        elif sport == "cricket":
            goals = stats.get("runs", 0)
            assists = stats.get("wickets", 0)

        return RoundSummary(
            round_num=round_num,
            goals=goals,
            assists=assists,
            rating=stats["rating"],
            events=events,
            minutes_played=SPORT_MATCH_MINUTES.get(sport, 90),
            fatigue_delta=round(fatigue_delta, 4),
            context=f"{config.team} ({config.formation}) as {config.role}",
        )

    def run_scenario(
        self,
        persona: PlayerPersona,
        config: SimConfig,
        num_rounds: int = 5,
    ) -> SimulationResult:
        sport = config.sport or "soccer"
        rounds: list[RoundSummary] = []
        for r in range(1, num_rounds + 1):
            summary = self.run_round(config, r)
            rounds.append(summary)

        avg_rating = np.mean([r.rating for r in rounds]) if rounds else 0.0

        if sport == "soccer":
            total_goals = sum(r.goals for r in rounds)
            total_assists = sum(r.assists for r in rounds)
            output_score = min(1.0, (total_goals + total_assists * 0.7) / max(num_rounds * 0.8, 1))
            summary_text = f"{persona.name} at {config.team} ({config.role}): {total_goals}G {total_assists}A, avg {avg_rating:.1f}"
        elif sport == "basketball":
            total_points = sum(r.goals for r in rounds)
            total_assists = sum(r.assists for r in rounds)
            output_score = min(1.0, (total_points / max(num_rounds * 15, 1)))
            summary_text = f"{persona.name} at {config.team} ({config.role}): {total_points}PTS {total_assists}AST, avg {avg_rating:.1f}"
        else:
            total_runs = sum(r.goals for r in rounds)
            total_wickets = sum(r.assists for r in rounds)
            output_score = min(1.0, (total_runs / max(num_rounds * 30, 1)) + total_wickets * 0.1)
            summary_text = f"{persona.name} at {config.team} ({config.role}): {total_runs}R {total_wickets}W, avg {avg_rating:.1f}"

        metrics = {
            "output_score": float(np.clip(output_score, 0.0, 1.0)),
            "tactical_fit": float(np.clip(avg_rating / 10.0, 0.0, 1.0)),
            "coherence_score": 0.7,
            "step_efficiency": max(0.0, 1.0 - len(rounds) / (num_rounds * 1.5)),
        }

        return SimulationResult(
            player_id=persona.player_id,
            scenario=config.team,
            rounds=rounds,
            persona_vector=persona.trait_vector(),
            player_summary=summary_text,
            performance_metrics=metrics,
        )


async def run_dual_simulation(
    persona: PlayerPersona,
    config_a: SimConfig,
    config_b: SimConfig,
    num_rounds: int = 5,
    seed: int = 42,
) -> Tuple[SimulationResult, SimulationResult]:
    """Run two scenarios in parallel using asyncio."""
    loop = asyncio.get_event_loop()
    runner_a = SimulationRunner(seed=seed)
    runner_b = SimulationRunner(seed=seed + 1)

    result_a, result_b = await asyncio.gather(
        loop.run_in_executor(None, runner_a.run_scenario, persona, config_a, num_rounds),
        loop.run_in_executor(None, runner_b.run_scenario, persona, config_b, num_rounds),
    )
    return result_a, result_b
