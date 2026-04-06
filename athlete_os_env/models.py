"""
Fidenz Athlete OS Data Models — Typed Action, Observation, State for OpenEnv compliance.
Uses Pydantic BaseModel and inherits from openenv-core base classes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from openenv.core.env_server import Action, Observation, State


# ---------------------------------------------------------------------------
# Single-player models (OpenEnv-compliant)
# ---------------------------------------------------------------------------

class AthleteAction(Action):
    """Agent-issued action for a single-player simulation step or query."""

    action_type: str = "simulate_round"  # "simulate_round" | "query_persona" | "adjust_params"
    player_id: str = "default"
    target_context: Dict[str, Any] = Field(default_factory=dict)
    sim_params: Optional[Dict[str, Any]] = None
    query: Optional[str] = None


class AthleteObservation(Observation):
    """Observation returned after each environment step."""

    goal: str = ""
    player_summary: str = ""
    round_result: Optional[Dict[str, Any]] = None
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    persona_drift_score: float = 0.0
    last_action_error: Optional[str] = None
    graph_context: Optional[str] = None
    step_hint: Optional[str] = None
    screenshot_uri: Optional[str] = None


class AthleteState(State):
    """Full episode state exposed via the /state endpoint."""

    task_id: str = ""
    player_id: str = ""
    current_round: int = 0
    total_rounds: int = 0
    cumulative_reward: float = 0.0
    persona_initialized: bool = False
    graph_id: Optional[str] = None
    simulation_status: str = "idle"  # idle | building | simulating | grading | done
    kl_penalty_total: float = 0.0
    done: bool = False
    goal: str = ""
    baseline_persona_vector: Optional[List[float]] = None
    reward: float = 0.0


# ---------------------------------------------------------------------------
# Multi-player / squad models
# ---------------------------------------------------------------------------

class SquadAction(BaseModel):
    """Agent-issued action for multi-player squad simulation."""

    action_type: str = "simulate_squad_round"  # "simulate_squad_round" | "swap_player" | "query_chemistry"
    squad_id: str = ""
    player_roles: Dict[str, str] = Field(default_factory=dict)
    target_context: Dict[str, Any] = Field(default_factory=dict)
    substitution: Optional[Dict[str, str]] = None
    query: Optional[str] = None


class SquadObservation(BaseModel):
    """Observation for multi-player squad simulation."""

    goal: str = ""
    squad_summary: str = ""
    round_result: Optional[Dict[str, Any]] = None
    individual_ratings: Dict[str, float] = Field(default_factory=dict)
    chemistry_matrix: Optional[List[List[float]]] = None
    weakest_link: Optional[str] = None
    fatigue_map: Dict[str, float] = Field(default_factory=dict)
    persona_drift_scores: Dict[str, float] = Field(default_factory=dict)
    last_action_error: Optional[str] = None
    step_hint: Optional[str] = None


# ---------------------------------------------------------------------------
# Internal domain models
# ---------------------------------------------------------------------------

class PlayerPersona(BaseModel):
    """Behavioral persona generated from seed data + LLM."""

    player_id: str = ""
    name: str = ""
    sport: str = ""
    position: str = ""
    nationality: str = ""
    age: int = 0
    bio: str = ""
    mbti_tag: str = ""
    decision_style: str = ""
    pressure_response: str = ""

    # 16-dim trait vector (raw values, normalized to simplex at runtime)
    speed: float = 0.5
    stamina: float = 0.5
    positioning: float = 0.5
    technical: float = 0.5
    aerial: float = 0.5
    decision_speed: float = 0.5
    pressure_tolerance: float = 0.5
    creativity: float = 0.5
    work_rate: float = 0.5
    leadership: float = 0.5
    consistency: float = 0.5
    injury_resilience: float = 0.5
    form_momentum: float = 0.5
    big_game_performance: float = 0.5
    adaptability: float = 0.5
    teamwork: float = 0.5

    def trait_vector(self) -> List[float]:
        return [
            self.speed, self.stamina, self.positioning, self.technical,
            self.aerial, self.decision_speed, self.pressure_tolerance,
            self.creativity, self.work_rate, self.leadership,
            self.consistency, self.injury_resilience, self.form_momentum,
            self.big_game_performance, self.adaptability, self.teamwork,
        ]

    @staticmethod
    def trait_names() -> List[str]:
        return [
            "speed", "stamina", "positioning", "technical",
            "aerial", "decision_speed", "pressure_tolerance",
            "creativity", "work_rate", "leadership",
            "consistency", "injury_resilience", "form_momentum",
            "big_game_performance", "adaptability", "teamwork",
        ]


class RoundSummary(BaseModel):
    """Result of a single simulated match round."""

    round_num: int = 0
    goals: int = 0
    assists: int = 0
    rating: float = 0.0
    events: List[Dict[str, Any]] = Field(default_factory=list)
    minutes_played: int = 90
    fatigue_delta: float = 0.0
    context: str = ""


class SimulationResult(BaseModel):
    """Aggregated result from a simulation run."""

    player_id: str = ""
    scenario: str = ""
    rounds: List[RoundSummary] = Field(default_factory=list)
    persona_vector: List[float] = Field(default_factory=list)
    player_summary: str = ""
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    graph_context: str = ""
    error: Optional[str] = None


TASK_MAX_STEPS = {
    "single_player_stat_prediction": 10,
    "player_team_fit_analysis": 20,
    "full_squad_recruitment_sim": 50,
}

TRAIT_COUNT = 16
