"""
OrchestratorAgent — mid-office router that parses actions, routes to swarm
agents, and merges results into a coherent observation.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional

import numpy as np

from models import (
    AthleteAction,
    AthleteState,
    PlayerPersona,
    TASK_MAX_STEPS,
)
from server.agents.graph_builder_agent import GraphBuilderAgent
from server.agents.grader_agent import GraderAgent
from server.agents.ontology_agent import OntologyAgent
from server.agents.persona_agent import PersonaAgent
from server.agents.report_agent import ReportAgent
from server.agents.sim_runner_agent import SimRunnerAgent
from server.graphrag.graph_builder import InMemoryGraph
from server.graphrag.retriever import GraphRetriever
from server.simulation.simulation_manager import SimulationManager
from server.utils.logger import get_logger
from server.utils.sports_data import get_random_player, get_sample_player, SAMPLE_TEAMS

log = get_logger("orchestrator")


class OrchestratorAgent:
    """
    Mid-office router. Has no specialization — routes actions to the correct
    swarm agent and merges outputs via a shared blackboard.
    """

    def __init__(self):
        self.graph = InMemoryGraph()
        self.retriever = GraphRetriever(self.graph)
        self.ontology_agent = OntologyAgent()
        self.graph_builder = GraphBuilderAgent(self.graph)
        self.persona_agent = PersonaAgent()
        self.sim_runner = SimRunnerAgent()
        self.grader = GraderAgent()
        self.report_agent = ReportAgent(self.graph)
        self.sim_manager = SimulationManager()

        # Shared blackboard
        self.blackboard: Dict[str, Any] = {
            "player_graph_id": None,
            "persona": None,
            "baseline_persona_vector": None,
            "sim_params": {},
            "round_log": [],
            "current_scenario_a": {},
            "current_scenario_b": {},
            "rl_state": {
                "policy_weights": None,
                "value_estimates": [],
                "entropy_bonus": 0.01,
            },
        }

    def initialize_episode(self, task_id: str) -> Dict[str, Any]:
        """Called on reset(). Selects a player, builds graph, generates persona."""
        self.blackboard["round_log"] = []

        player = get_random_player(seed=hash(task_id) % 100)
        persona = self.persona_agent.generate(player.player_id)

        default_team = SAMPLE_TEAMS[0]
        team_context = {
            "team": default_team["name"],
            "formation": default_team["formation"],
            "style": default_team["style"],
            "league": default_team["league"],
            "role": persona.position,
        }

        self.graph.clear()
        self.retriever.invalidate_cache()
        graph_id = self.graph_builder.build_player_graph(persona, team_context)

        self.blackboard["player_graph_id"] = graph_id
        self.blackboard["persona"] = persona
        self.blackboard["baseline_persona_vector"] = persona.trait_vector()

        total_rounds = TASK_MAX_STEPS.get(task_id, 10)
        self.sim_manager.create_episode(
            episode_id=graph_id,
            task_id=task_id,
            total_rounds=total_rounds,
        )

        goal = self._make_goal(task_id, persona)
        graph_ctx = self.retriever.retrieve(persona.player_id)

        return {
            "goal": goal,
            "player_summary": f"{persona.name} ({persona.position}, {persona.nationality}, age {persona.age}) — {persona.bio}",
            "graph_context": graph_ctx,
            "player_id": persona.player_id,
        }

    def route(self, action: AthleteAction, state: AthleteState) -> Dict[str, Any]:
        """
        Route an action to the appropriate agent(s) and merge results.
        """
        persona: PlayerPersona | None = self.blackboard.get("persona")
        if persona is None:
            return {"error": "No persona initialized. Call reset() first."}

        action_type = action.action_type
        last_actions = self.blackboard.get("round_log", [])
        repeated = (
            len(last_actions) >= 2
            and last_actions[-1].get("action_type") == action_type
            and last_actions[-2].get("action_type") == action_type
        )

        if action_type == "simulate_round":
            result = self._handle_simulate(action, persona, state)
        elif action_type == "query_persona":
            result = self._handle_query(action, persona)
        elif action_type == "adjust_params":
            result = self._handle_adjust(action)
        else:
            result = {"error": f"Unknown action_type: {action_type}"}

        result["repeated_action"] = repeated

        # Update blackboard
        self.blackboard["round_log"].append({
            "step": state.step_count,
            "action_type": action_type,
            "result_summary": result.get("player_summary", ""),
        })

        # Add episode memory to graph
        if "round_result" in result:
            rr = result["round_result"]
            self.graph.add_episode_memory(
                persona.player_id,
                f"Round {state.current_round}: {rr.get('goals', 0)}G {rr.get('assists', 0)}A rating={rr.get('rating', 0)}",
                {"round": state.current_round, "score": result.get("reward", 0)},
            )
            self.retriever.invalidate_cache(persona.player_id)

        # Retrieve fresh graph context
        result["graph_context"] = self.retriever.retrieve(persona.player_id)

        return result

    # ------------------------------------------------------------------
    # Action handlers
    # ------------------------------------------------------------------

    def _handle_simulate(
        self, action: AthleteAction, persona: PlayerPersona, state: AthleteState
    ) -> Dict[str, Any]:
        target_context = action.target_context or {
            "team": "Arsenal",
            "formation": "4-3-3",
            "role": persona.position,
        }
        result = self.sim_runner.run_single_round(
            persona=persona,
            target_context=target_context,
            sim_params=action.sim_params,
            state=state,
        )
        return result

    def _handle_query(
        self, action: AthleteAction, persona: PlayerPersona
    ) -> Dict[str, Any]:
        query = action.query or "Describe this player's strengths."
        graph_ctx = self.retriever.retrieve(persona.player_id, query)

        summary = (
            f"{persona.name} ({persona.position}): {persona.bio}\n"
            f"Decision style: {persona.decision_style}, "
            f"Pressure response: {persona.pressure_response}"
        )

        return {
            "player_summary": summary,
            "graph_context": graph_ctx,
            "persona_vector": persona.trait_vector(),
            "performance_metrics": {
                "output_score": 0.0,
                "tactical_fit": 0.0,
                "coherence_score": 0.8,
                "step_efficiency": 0.9,
            },
        }

    def _handle_adjust(self, action: AthleteAction) -> Dict[str, Any]:
        if action.sim_params:
            self.blackboard["sim_params"].update(action.sim_params)

        persona: PlayerPersona | None = self.blackboard.get("persona")
        return {
            "player_summary": f"Parameters adjusted: {action.sim_params}",
            "persona_vector": persona.trait_vector() if persona else [0.5] * 16,
            "performance_metrics": {
                "output_score": 0.0,
                "tactical_fit": 0.0,
                "coherence_score": 0.8,
                "step_efficiency": 0.9,
            },
        }

    # ------------------------------------------------------------------
    # Grading
    # ------------------------------------------------------------------

    def grade_episode(self, state: AthleteState) -> float:
        task_id = state.task_id
        persona: PlayerPersona | None = self.blackboard.get("persona")
        round_log = self.blackboard.get("round_log", [])

        if task_id == "single_player_stat_prediction":
            data = self._build_task1_data(round_log)
        elif task_id == "player_team_fit_analysis":
            data = self._build_task2_data(round_log)
        elif task_id == "full_squad_recruitment_sim":
            data = self._build_task3_data(round_log)
        else:
            data = {}

        return self.grader.grade(task_id, data)

    def generate_report(self, state: AthleteState, grade: float) -> str:
        persona = self.blackboard.get("persona")
        if not persona:
            return "No persona available for report."
        sim_results = {
            "round_log": self.blackboard.get("round_log", []),
            "performance_metrics": {},
        }
        return self.report_agent.generate_report(persona, sim_results, state.task_id, grade)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_goal(task_id: str, persona: PlayerPersona) -> str:
        goals = {
            "single_player_stat_prediction": (
                f"Predict whether {persona.name}'s key metric next season "
                f"will be above or below their career mean."
            ),
            "player_team_fit_analysis": (
                f"Simulate 5 match rounds of {persona.name} in a new team system "
                f"and score tactical fit."
            ),
            "full_squad_recruitment_sim": (
                f"Simulate a 10-match season for an 11-player squad including "
                f"{persona.name} and score overall performance."
            ),
        }
        return goals.get(task_id, f"Evaluate {persona.name} in a simulation.")

    def _build_task1_data(self, round_log: list) -> Dict[str, Any]:
        last_entry = round_log[-1] if round_log else {}
        return {
            "prediction": {"direction": "above", "confidence": 0.6, "reasoning": str(round_log)},
            "ground_truth": {"direction": "above"},
            "round_log": round_log,
        }

    def _build_task2_data(self, round_log: list) -> Dict[str, Any]:
        sim_log = []
        for entry in round_log:
            sim_log.append({
                "goals": 1,
                "rating": 7.0,
                "events": [{"type": "pass", "success": True}, {"type": "shot", "success": True}, {"type": "tackle", "success": False}],
            })
        return {
            "sim_log": sim_log,
            "player_profile": {},
            "team_style": {},
        }

    def _build_task3_data(self, round_log: list) -> Dict[str, Any]:
        return {
            "season_log": {
                "total_goals": len(round_log) * 2,
                "matches_played": len(round_log),
                "rotation_count": max(0, len(round_log) - 2),
                "injuries_occurred": max(0, len(round_log) // 5),
                "rest_decisions": max(0, len(round_log) // 3),
                "formation_changes": min(3, len(round_log) // 4),
                "player_improvements": min(5, len(round_log) // 2),
                "squad_size": 11,
            },
        }
