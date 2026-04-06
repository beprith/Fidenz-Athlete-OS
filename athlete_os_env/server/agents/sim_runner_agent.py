"""
SimRunnerAgent — drives dual-context parallel simulation.
"""

from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from models import PlayerPersona, SimulationResult, AthleteState
from server.simulation.persona_config import SimConfig, persona_to_sim_config
from server.simulation.simulation_runner import SimulationRunner, run_dual_simulation
from server.utils.logger import get_logger

log = get_logger("sim_runner_agent")


class SimRunnerAgent:
    """Manages running simulations for the orchestrator."""

    def __init__(self, seed: int = 42):
        self._runner = SimulationRunner(seed=seed)
        self._seed = seed

    def run_single_round(
        self,
        persona: PlayerPersona,
        target_context: Dict[str, Any],
        sim_params: Dict[str, Any] | None = None,
        state: AthleteState | None = None,
    ) -> Dict[str, Any]:
        config = persona_to_sim_config(persona, target_context, sim_params)

        round_num = state.current_round if state else 1
        summary = self._runner.run_round(config, round_num)

        sport = persona.sport or "soccer"
        if sport == "basketball":
            output_score = min(1.0, summary.goals / 15.0)
            stat_line = f"{summary.goals}PTS {summary.assists}AST"
        elif sport == "cricket":
            output_score = min(1.0, summary.goals / 30.0 + summary.assists * 0.1)
            stat_line = f"{summary.goals}R {summary.assists}W"
        else:
            output_score = min(1.0, (summary.goals + summary.assists * 0.7) / 1.5)
            stat_line = f"{summary.goals}G {summary.assists}A"

        result = {
            "round_result": {
                "goals": summary.goals,
                "assists": summary.assists,
                "rating": summary.rating,
                "events": summary.events,
                "context": summary.context,
            },
            "performance_metrics": {
                "output_score": output_score,
                "tactical_fit": float(min(1.0, summary.rating / 10.0)),
                "coherence_score": 0.7,
                "step_efficiency": 0.6,
            },
            "persona_vector": persona.trait_vector(),
            "player_summary": f"{persona.name}: {stat_line} rating={summary.rating}",
            "fatigue_delta": summary.fatigue_delta,
        }

        log.info(
            f"Round {round_num} for {persona.name}: "
            f"{stat_line} rating={summary.rating}"
        )
        return result

    async def run_dual_scenario(
        self,
        persona: PlayerPersona,
        context_a: Dict[str, Any],
        context_b: Dict[str, Any],
        sim_params: Dict[str, Any] | None = None,
        num_rounds: int = 5,
    ) -> Dict[str, Any]:
        config_a = persona_to_sim_config(persona, context_a, sim_params)
        config_b = persona_to_sim_config(persona, context_b, sim_params)

        result_a, result_b = await run_dual_simulation(
            persona, config_a, config_b, num_rounds, self._seed,
        )

        return {
            "scenario_a": {
                "team": context_a.get("team", "Current"),
                "rounds": [{"goals": r.goals, "assists": r.assists, "rating": r.rating} for r in result_a.rounds],
                "summary": result_a.player_summary,
                "metrics": result_a.performance_metrics,
            },
            "scenario_b": {
                "team": context_b.get("team", "Target"),
                "rounds": [{"goals": r.goals, "assists": r.assists, "rating": r.rating} for r in result_b.rounds],
                "summary": result_b.player_summary,
                "metrics": result_b.performance_metrics,
            },
            "persona_vector": persona.trait_vector(),
            "player_summary": result_b.player_summary,
            "performance_metrics": result_b.performance_metrics,
        }
