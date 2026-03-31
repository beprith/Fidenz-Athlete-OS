"""
GraphBuilderAgent — chunks player career into episodes, builds knowledge graph.
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from models import PlayerPersona
from server.graphrag.graph_builder import InMemoryGraph
from server.graphrag.ontology import (
    PLAYS_FOR, HAS_SKILL, PARTICIPATED_IN, COMPETES_IN,
    CHEMISTRY_WITH, COMPARED_TO,
)
from server.utils.logger import get_logger
from server.utils.sports_data import get_career_stats

log = get_logger("graph_builder_agent")


class GraphBuilderAgent:
    """Builds the in-memory knowledge graph from player data and career stats."""

    def __init__(self, graph: InMemoryGraph):
        self.graph = graph

    def build_player_graph(
        self,
        persona: PlayerPersona,
        team_context: Dict[str, Any] | None = None,
    ) -> str:
        """
        Create all graph nodes/edges for a player.
        Returns the player node ID.
        """
        pid = persona.player_id

        # Player node
        embedding = self._compute_embedding(persona)
        self.graph.add_node(
            pid,
            "Player",
            {
                "name": persona.name,
                "position": persona.position,
                "nationality": persona.nationality,
                "age": persona.age,
                "overall_rating": np.mean(persona.trait_vector()),
            },
            embedding=embedding,
        )

        # Skill nodes from trait vector
        for tname, tval in zip(persona.trait_names(), persona.trait_vector()):
            skill_id = f"{pid}_skill_{tname}"
            self.graph.add_node(skill_id, "Skill", {"name": tname, "category": "trait"})
            self.graph.add_edge(pid, skill_id, HAS_SKILL, {"level": round(tval, 3)})

        # Team context
        if team_context:
            team_id = team_context.get("team", "unknown").lower().replace(" ", "_")
            self.graph.add_node(team_id, "Team", {
                "name": team_context.get("team", "Unknown"),
                "formation": team_context.get("formation", "4-3-3"),
                "style": team_context.get("style", "balanced"),
            })
            self.graph.add_edge(pid, team_id, PLAYS_FOR, {
                "role": team_context.get("role", persona.position),
            })

            league_name = team_context.get("league", "Unknown League")
            league_id = league_name.lower().replace(" ", "_")
            self.graph.add_node(league_id, "League", {
                "name": league_name,
                "country": team_context.get("country", ""),
            })
            self.graph.add_edge(team_id, league_id, COMPETES_IN)

        # Career stats as match nodes
        career = get_career_stats(pid)
        for season_stats in career:
            match_id = f"{pid}_season_{season_stats['season']}"
            self.graph.add_node(match_id, "Match", {
                "season": season_stats["season"],
                "goals": season_stats["goals"],
                "assists": season_stats["assists"],
                "rating": season_stats["rating"],
                "appearances": season_stats["appearances"],
            })
            self.graph.add_edge(pid, match_id, PARTICIPATED_IN, {
                "goals": season_stats["goals"],
                "assists": season_stats["assists"],
                "rating": season_stats["rating"],
                "minutes": season_stats["minutes"],
            })

        log.info(f"Built graph for {persona.name}: {self.graph.summary()}")
        return pid

    def add_chemistry_edge(
        self, player_a_id: str, player_b_id: str, score: float
    ) -> None:
        self.graph.add_edge(player_a_id, player_b_id, CHEMISTRY_WITH, {"score": score})
        self.graph.add_edge(player_b_id, player_a_id, CHEMISTRY_WITH, {"score": score})

    def add_comparison_edge(
        self, player_a_id: str, player_b_id: str, similarity: float
    ) -> None:
        self.graph.add_edge(player_a_id, player_b_id, COMPARED_TO, {
            "similarity_score": similarity,
        })

    @staticmethod
    def _compute_embedding(persona: PlayerPersona) -> np.ndarray:
        """Simple embedding: normalized trait vector padded to 32 dims."""
        tv = np.asarray(persona.trait_vector(), dtype=np.float32)
        padded = np.zeros(32, dtype=np.float32)
        padded[:len(tv)] = tv
        norm = np.linalg.norm(padded)
        if norm > 1e-8:
            padded /= norm
        return padded
