"""
Mock sports data provider with sample player profiles.
Provides seed data for demos without requiring external APIs.
"""

from __future__ import annotations

from typing import Any, Dict, List

from models import PlayerPersona


# ---------------------------------------------------------------------------
# Sample player database (soccer-biased but sport-agnostic concept)
# ---------------------------------------------------------------------------

SAMPLE_PLAYERS: List[Dict[str, Any]] = [
    {
        "player_id": "mbappe_01",
        "name": "Kylian Mbappé",
        "position": "CF",
        "nationality": "France",
        "age": 27,
        "bio": "Electric pace, lethal finishing, thrives in transition play.",
        "mbti_tag": "ESTP",
        "decision_style": "instinctive",
        "pressure_response": "thrives",
        "speed": 0.95, "stamina": 0.78, "positioning": 0.85, "technical": 0.90,
        "aerial": 0.55, "decision_speed": 0.88, "pressure_tolerance": 0.82,
        "creativity": 0.80, "work_rate": 0.65, "leadership": 0.60,
        "consistency": 0.75, "injury_resilience": 0.70, "form_momentum": 0.85,
        "big_game_performance": 0.90, "adaptability": 0.80, "teamwork": 0.70,
    },
    {
        "player_id": "saka_01",
        "name": "Bukayo Saka",
        "position": "RW",
        "nationality": "England",
        "age": 24,
        "bio": "Versatile winger with elite dribbling and end product.",
        "mbti_tag": "ENFJ",
        "decision_style": "calculated",
        "pressure_response": "composed",
        "speed": 0.85, "stamina": 0.82, "positioning": 0.78, "technical": 0.88,
        "aerial": 0.45, "decision_speed": 0.80, "pressure_tolerance": 0.78,
        "creativity": 0.85, "work_rate": 0.80, "leadership": 0.65,
        "consistency": 0.82, "injury_resilience": 0.75, "form_momentum": 0.80,
        "big_game_performance": 0.78, "adaptability": 0.85, "teamwork": 0.82,
    },
    {
        "player_id": "rice_01",
        "name": "Declan Rice",
        "position": "CDM",
        "nationality": "England",
        "age": 27,
        "bio": "Complete midfielder — dominant in duels, progressive passing range.",
        "mbti_tag": "ISTJ",
        "decision_style": "methodical",
        "pressure_response": "steady",
        "speed": 0.72, "stamina": 0.90, "positioning": 0.88, "technical": 0.75,
        "aerial": 0.80, "decision_speed": 0.78, "pressure_tolerance": 0.85,
        "creativity": 0.60, "work_rate": 0.92, "leadership": 0.85,
        "consistency": 0.88, "injury_resilience": 0.85, "form_momentum": 0.75,
        "big_game_performance": 0.82, "adaptability": 0.75, "teamwork": 0.90,
    },
    {
        "player_id": "debruyne_01",
        "name": "Kevin De Bruyne",
        "position": "CAM",
        "nationality": "Belgium",
        "age": 34,
        "bio": "World-class playmaker with unmatched passing vision.",
        "mbti_tag": "INTJ",
        "decision_style": "visionary",
        "pressure_response": "composed",
        "speed": 0.65, "stamina": 0.60, "positioning": 0.82, "technical": 0.92,
        "aerial": 0.55, "decision_speed": 0.90, "pressure_tolerance": 0.80,
        "creativity": 0.95, "work_rate": 0.70, "leadership": 0.82,
        "consistency": 0.70, "injury_resilience": 0.45, "form_momentum": 0.65,
        "big_game_performance": 0.88, "adaptability": 0.78, "teamwork": 0.85,
    },
    {
        "player_id": "haaland_01",
        "name": "Erling Haaland",
        "position": "ST",
        "nationality": "Norway",
        "age": 25,
        "bio": "Physically dominant striker with elite finishing and movement.",
        "mbti_tag": "ENTJ",
        "decision_style": "predatory",
        "pressure_response": "thrives",
        "speed": 0.88, "stamina": 0.75, "positioning": 0.92, "technical": 0.78,
        "aerial": 0.90, "decision_speed": 0.82, "pressure_tolerance": 0.80,
        "creativity": 0.55, "work_rate": 0.60, "leadership": 0.65,
        "consistency": 0.85, "injury_resilience": 0.72, "form_momentum": 0.90,
        "big_game_performance": 0.88, "adaptability": 0.68, "teamwork": 0.62,
    },
    {
        "player_id": "james_01",
        "name": "LeBron James",
        "position": "SF",
        "nationality": "USA",
        "age": 41,
        "bio": "All-time great — versatile scorer, passer, and defender.",
        "mbti_tag": "ENTJ",
        "decision_style": "strategic",
        "pressure_response": "thrives",
        "speed": 0.70, "stamina": 0.75, "positioning": 0.90, "technical": 0.88,
        "aerial": 0.85, "decision_speed": 0.92, "pressure_tolerance": 0.95,
        "creativity": 0.85, "work_rate": 0.72, "leadership": 0.98,
        "consistency": 0.90, "injury_resilience": 0.65, "form_momentum": 0.70,
        "big_game_performance": 0.95, "adaptability": 0.90, "teamwork": 0.88,
    },
    {
        "player_id": "kohli_01",
        "name": "Virat Kohli",
        "position": "Batsman",
        "nationality": "India",
        "age": 37,
        "bio": "Run-machine — aggressive batting, elite chase record.",
        "mbti_tag": "ESTP",
        "decision_style": "aggressive",
        "pressure_response": "thrives",
        "speed": 0.78, "stamina": 0.80, "positioning": 0.85, "technical": 0.92,
        "aerial": 0.50, "decision_speed": 0.85, "pressure_tolerance": 0.90,
        "creativity": 0.75, "work_rate": 0.88, "leadership": 0.90,
        "consistency": 0.82, "injury_resilience": 0.78, "form_momentum": 0.75,
        "big_game_performance": 0.92, "adaptability": 0.82, "teamwork": 0.80,
    },
]

SAMPLE_TEAMS: List[Dict[str, Any]] = [
    {"id": "arsenal", "name": "Arsenal", "league": "Premier League", "formation": "4-3-3", "style": "possession_press"},
    {"id": "real_madrid", "name": "Real Madrid", "league": "La Liga", "formation": "4-3-3", "style": "counter_attack"},
    {"id": "man_city", "name": "Manchester City", "league": "Premier League", "formation": "4-2-3-1", "style": "possession"},
    {"id": "barcelona", "name": "FC Barcelona", "league": "La Liga", "formation": "4-3-3", "style": "tiki_taka"},
    {"id": "lakers", "name": "LA Lakers", "league": "NBA", "formation": "small_ball", "style": "fast_break"},
    {"id": "rcb", "name": "Royal Challengers Bengaluru", "league": "IPL", "formation": "batting_heavy", "style": "aggressive"},
]


def get_sample_player(player_id: str) -> PlayerPersona | None:
    for p in SAMPLE_PLAYERS:
        if p["player_id"] == player_id:
            return PlayerPersona(**{k: v for k, v in p.items()})
    return None


def get_random_player(seed: int = 0) -> PlayerPersona:
    idx = seed % len(SAMPLE_PLAYERS)
    return PlayerPersona(**{k: v for k, v in SAMPLE_PLAYERS[idx].items()})


def get_sample_team(team_id: str) -> Dict[str, Any] | None:
    for t in SAMPLE_TEAMS:
        if t["id"] == team_id:
            return t
    return None


def list_player_ids() -> List[str]:
    return [p["player_id"] for p in SAMPLE_PLAYERS]


def get_career_stats(player_id: str) -> List[Dict[str, Any]]:
    """Return mock career stats for a player — used by ontology/graph agents."""
    import numpy as np
    rng = np.random.RandomState(hash(player_id) % (2**31))

    seasons = []
    for year in range(2020, 2026):
        seasons.append({
            "season": f"{year}-{year+1}",
            "appearances": int(rng.randint(20, 40)),
            "goals": int(rng.randint(0, 25)),
            "assists": int(rng.randint(0, 15)),
            "rating": round(float(rng.uniform(6.0, 8.5)), 1),
            "minutes": int(rng.randint(1500, 3400)),
        })
    return seasons
