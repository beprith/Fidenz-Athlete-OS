"""
Sports entity schema definitions for the in-memory property graph.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Node types
# ---------------------------------------------------------------------------

@dataclass
class PlayerNode:
    id: str
    name: str
    position: str
    nationality: str = ""
    age: int = 0
    overall_rating: float = 0.0
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TeamNode:
    id: str
    name: str
    league_id: str = ""
    formation: str = "4-3-3"
    style: str = "balanced"
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LeagueNode:
    id: str
    name: str
    country: str = ""
    strength: float = 0.5
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchNode:
    id: str
    home_team_id: str = ""
    away_team_id: str = ""
    season: str = ""
    matchday: int = 0
    result: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillNode:
    id: str
    name: str
    category: str = "technical"
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InjuryNode:
    id: str
    type: str
    severity: str = "minor"
    games_missed: int = 0
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FormationNode:
    id: str
    name: str  # e.g. "4-3-3", "3-5-2"
    properties: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Edge types
# ---------------------------------------------------------------------------

@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relation: str
    properties: Dict[str, Any] = field(default_factory=dict)


# Relation type constants
PLAYS_FOR = "PLAYS_FOR"
COMPETES_IN = "COMPETES_IN"
PARTICIPATED_IN = "PARTICIPATED_IN"
PART_OF = "PART_OF"
HAS_SKILL = "HAS_SKILL"
SUFFERED = "SUFFERED"
COMPARED_TO = "COMPARED_TO"
USES_FORMATION = "USES_FORMATION"
CHEMISTRY_WITH = "CHEMISTRY_WITH"
PREFERS_PASS_TO = "PREFERS_PASS_TO"
POSITIONAL_CONFLICT = "POSITIONAL_CONFLICT"
SAME_NATIONALITY_AS = "SAME_NATIONALITY_AS"
FORMER_TEAMMATE_OF = "FORMER_TEAMMATE_OF"
MANAGED_BY = "MANAGED_BY"


# Entity type registry for the ontology agent
ENTITY_TYPES = {
    "Player": PlayerNode,
    "Team": TeamNode,
    "League": LeagueNode,
    "Match": MatchNode,
    "Skill": SkillNode,
    "Injury": InjuryNode,
    "Formation": FormationNode,
}

RELATION_TYPES = [
    PLAYS_FOR, COMPETES_IN, PARTICIPATED_IN, PART_OF,
    HAS_SKILL, SUFFERED, COMPARED_TO, USES_FORMATION,
    CHEMISTRY_WITH, PREFERS_PASS_TO, POSITIONAL_CONFLICT,
    SAME_NATIONALITY_AS, FORMER_TEAMMATE_OF, MANAGED_BY,
]
