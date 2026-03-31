"""
OntologyAgent — extracts entity types from uploaded stats data.
"""

from __future__ import annotations

from typing import Any, Dict, List

from server.graphrag.ontology import (
    ENTITY_TYPES,
    RELATION_TYPES,
    PlayerNode,
    TeamNode,
    LeagueNode,
    MatchNode,
    SkillNode,
    InjuryNode,
)
from server.utils.llm_client import get_llm_client
from server.utils.logger import get_logger

log = get_logger("ontology_agent")

ONTOLOGY_PROMPT = """You are an ontology extraction agent for a sports analytics platform.
Given the following player data, extract structured entities and relationships.

Return a JSON object with:
{
  "players": [{"id": str, "name": str, "position": str, "nationality": str, "age": int}],
  "teams": [{"id": str, "name": str, "league": str}],
  "leagues": [{"id": str, "name": str, "country": str}],
  "skills": [{"id": str, "name": str, "category": str}],
  "relationships": [{"source": str, "target": str, "type": str, "properties": {}}]
}

Player data:
"""


class OntologyAgent:
    """Parses seed data into typed entity/relationship records."""

    def __init__(self):
        self._llm = get_llm_client()

    def extract(self, raw_data: str | Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract entities from raw player data.
        Falls back to rule-based extraction if LLM is unavailable.
        """
        if isinstance(raw_data, dict):
            return self._extract_from_dict(raw_data)
        try:
            return self._extract_via_llm(str(raw_data))
        except Exception as exc:
            log.warning(f"LLM extraction failed, using rule-based fallback: {exc}")
            return self._extract_from_dict({"raw": raw_data})

    def _extract_via_llm(self, text: str) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": ONTOLOGY_PROMPT},
            {"role": "user", "content": text[:4000]},
        ]
        return self._llm.chat_json(messages)

    def _extract_from_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Rule-based extraction from structured dict."""
        result: Dict[str, Any] = {
            "players": [],
            "teams": [],
            "leagues": [],
            "skills": [],
            "relationships": [],
        }

        if "player_id" in data:
            result["players"].append({
                "id": data["player_id"],
                "name": data.get("name", "Unknown"),
                "position": data.get("position", ""),
                "nationality": data.get("nationality", ""),
                "age": data.get("age", 0),
            })

        if "team" in data:
            tid = data["team"].lower().replace(" ", "_")
            result["teams"].append({
                "id": tid,
                "name": data["team"],
                "league": data.get("league", ""),
            })
            if result["players"]:
                result["relationships"].append({
                    "source": result["players"][0]["id"],
                    "target": tid,
                    "type": "PLAYS_FOR",
                    "properties": {},
                })

        return result
