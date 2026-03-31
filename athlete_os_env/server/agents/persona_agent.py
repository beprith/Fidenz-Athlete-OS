"""
PersonaAgent — LLM-generates a PlayerPersona from seed data.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import numpy as np

from models import PlayerPersona
from server.utils.llm_client import get_llm_client
from server.utils.logger import get_logger
from server.utils.sports_data import get_sample_player

log = get_logger("persona_agent")

PERSONA_PROMPT = """You are a sports behavioral psychologist AI. Given the following player
data, generate a detailed behavioral persona.

Return valid JSON with these fields:
{
  "bio": "<2-sentence behavioral profile>",
  "mbti_tag": "<4-letter MBTI>",
  "decision_style": "<one of: instinctive, calculated, methodical, visionary, aggressive, predatory>",
  "pressure_response": "<one of: thrives, composed, steady, crumbles>",
  "speed": <0.0-1.0>, "stamina": <0.0-1.0>, "positioning": <0.0-1.0>,
  "technical": <0.0-1.0>, "aerial": <0.0-1.0>, "decision_speed": <0.0-1.0>,
  "pressure_tolerance": <0.0-1.0>, "creativity": <0.0-1.0>,
  "work_rate": <0.0-1.0>, "leadership": <0.0-1.0>, "consistency": <0.0-1.0>,
  "injury_resilience": <0.0-1.0>, "form_momentum": <0.0-1.0>,
  "big_game_performance": <0.0-1.0>, "adaptability": <0.0-1.0>, "teamwork": <0.0-1.0>
}

Player data:
"""


class PersonaAgent:
    """Generates or retrieves player personas."""

    def __init__(self):
        self._llm = get_llm_client()
        self._cache: Dict[str, PlayerPersona] = {}

    def generate(
        self,
        player_id: str,
        seed_data: Dict[str, Any] | None = None,
        use_cache: bool = True,
    ) -> PlayerPersona:
        if use_cache and player_id in self._cache:
            return self._cache[player_id]

        # Try mock DB first
        persona = get_sample_player(player_id)
        if persona:
            self._cache[player_id] = persona
            log.info(f"Loaded persona from sample DB: {persona.name}")
            return persona

        # Fall back to LLM generation
        persona = self._generate_via_llm(player_id, seed_data or {})
        self._cache[player_id] = persona
        return persona

    def _generate_via_llm(
        self, player_id: str, seed_data: Dict[str, Any]
    ) -> PlayerPersona:
        data_str = json.dumps(seed_data, indent=2, default=str)[:3000]
        try:
            messages = [
                {"role": "system", "content": PERSONA_PROMPT},
                {"role": "user", "content": data_str},
            ]
            result = self._llm.chat_json(messages)
            persona = PlayerPersona(
                player_id=player_id,
                name=seed_data.get("name", player_id),
                position=seed_data.get("position", ""),
                nationality=seed_data.get("nationality", ""),
                age=seed_data.get("age", 0),
                **{k: v for k, v in result.items() if hasattr(PlayerPersona, k)},
            )
            log.info(f"LLM-generated persona for {persona.name}")
            return persona
        except Exception as exc:
            log.warning(f"LLM persona generation failed: {exc}. Using defaults.")
            return PlayerPersona(
                player_id=player_id,
                name=seed_data.get("name", player_id),
                position=seed_data.get("position", ""),
                nationality=seed_data.get("nationality", ""),
                age=seed_data.get("age", 0),
            )

    def get_baseline_vector(self, player_id: str) -> list[float]:
        persona = self._cache.get(player_id)
        if persona:
            return persona.trait_vector()
        return [0.5] * 16

    def update_persona_traits(
        self, player_id: str, new_weights: list[float]
    ) -> None:
        """Update cached persona with PPO-adjusted weights."""
        persona = self._cache.get(player_id)
        if not persona:
            return
        names = persona.trait_names()
        for name, val in zip(names, new_weights):
            setattr(persona, name, float(np.clip(val, 0.0, 1.0)))

    def clear_cache(self) -> None:
        self._cache.clear()
