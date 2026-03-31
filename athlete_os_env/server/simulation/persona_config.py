"""
Translates PlayerPersona into SimConfig parameters for the event engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

import numpy as np

from models import PlayerPersona


@dataclass
class SimConfig:
    """Configuration that drives a single simulation context."""

    player_id: str = ""
    team: str = "Unknown"
    formation: str = "4-3-3"
    role: str = "CM"
    opponent_strength: float = 0.5
    home_away: str = "home"
    match_importance: float = 0.5
    weather: str = "clear"
    injury_risk_weight: float = 0.1
    fatigue: float = 0.0
    persona_vector: list[float] = field(default_factory=list)
    extra: Dict[str, Any] = field(default_factory=dict)


def persona_to_sim_config(
    persona: PlayerPersona,
    target_context: Dict[str, Any],
    sim_params: Dict[str, Any] | None = None,
) -> SimConfig:
    """Build a SimConfig from a persona + target context + optional overrides."""
    params = sim_params or {}
    pv = persona.trait_vector()

    # Position-based fatigue baseline
    position_fatigue = {
        "GK": 0.02, "CB": 0.05, "LB": 0.08, "RB": 0.08,
        "CM": 0.07, "CDM": 0.06, "CAM": 0.07,
        "LW": 0.09, "RW": 0.09, "CF": 0.08, "ST": 0.07,
    }
    role = target_context.get("role", persona.position)
    base_fatigue = position_fatigue.get(role, 0.06)
    stamina_factor = max(0.01, 1.0 - persona.stamina)
    fatigue = base_fatigue * stamina_factor

    return SimConfig(
        player_id=persona.player_id,
        team=target_context.get("team", "Unknown"),
        formation=target_context.get("formation", "4-3-3"),
        role=role,
        opponent_strength=params.get("opponent_strength", 0.5),
        home_away=params.get("home_away", "home"),
        match_importance=params.get("match_importance", 0.5),
        weather=params.get("weather", "clear"),
        injury_risk_weight=params.get("injury_risk_weight", 0.1),
        fatigue=fatigue,
        persona_vector=pv,
        extra=params.get("extra", {}),
    )


def adjust_fatigue(config: SimConfig, rounds_played: int) -> SimConfig:
    """Increment fatigue based on rounds played and injury resilience."""
    config.fatigue = min(1.0, config.fatigue + 0.03 * rounds_played)
    return config
