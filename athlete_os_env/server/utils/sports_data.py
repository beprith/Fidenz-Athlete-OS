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

SPORT_SOCCER = "soccer"
SPORT_BASKETBALL = "basketball"
SPORT_CRICKET = "cricket"

SAMPLE_PLAYERS: List[Dict[str, Any]] = [
    {
        "player_id": "mbappe_01",
        "name": "Kylian Mbappé",
        "sport": SPORT_SOCCER,
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
        "sport": SPORT_SOCCER,
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
        "sport": SPORT_SOCCER,
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
        "sport": SPORT_SOCCER,
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
        "sport": SPORT_SOCCER,
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
    # ── Basketball ────────────────────────────────
    {
        "player_id": "james_01",
        "name": "LeBron James",
        "sport": SPORT_BASKETBALL,
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
        "player_id": "curry_01",
        "name": "Stephen Curry",
        "sport": SPORT_BASKETBALL,
        "position": "PG",
        "nationality": "USA",
        "age": 38,
        "bio": "Greatest shooter ever — gravity-bending off-ball movement, elite handles.",
        "mbti_tag": "ENFP",
        "decision_style": "instinctive",
        "pressure_response": "thrives",
        "speed": 0.80, "stamina": 0.78, "positioning": 0.88, "technical": 0.96,
        "aerial": 0.55, "decision_speed": 0.92, "pressure_tolerance": 0.90,
        "creativity": 0.92, "work_rate": 0.82, "leadership": 0.88,
        "consistency": 0.85, "injury_resilience": 0.62, "form_momentum": 0.80,
        "big_game_performance": 0.90, "adaptability": 0.85, "teamwork": 0.90,
    },
    {
        "player_id": "giannis_01",
        "name": "Giannis Antetokounmpo",
        "sport": SPORT_BASKETBALL,
        "position": "PF",
        "nationality": "Greece",
        "age": 31,
        "bio": "Freak athlete — unstoppable transition game, dominant interior force.",
        "mbti_tag": "ISFP",
        "decision_style": "instinctive",
        "pressure_response": "composed",
        "speed": 0.90, "stamina": 0.88, "positioning": 0.82, "technical": 0.72,
        "aerial": 0.92, "decision_speed": 0.80, "pressure_tolerance": 0.82,
        "creativity": 0.68, "work_rate": 0.90, "leadership": 0.80,
        "consistency": 0.85, "injury_resilience": 0.75, "form_momentum": 0.85,
        "big_game_performance": 0.88, "adaptability": 0.78, "teamwork": 0.82,
    },
    {
        "player_id": "jokic_01",
        "name": "Nikola Jokić",
        "sport": SPORT_BASKETBALL,
        "position": "C",
        "nationality": "Serbia",
        "age": 31,
        "bio": "Cerebral center — all-time playmaking big man, triple-double machine.",
        "mbti_tag": "INTP",
        "decision_style": "visionary",
        "pressure_response": "composed",
        "speed": 0.50, "stamina": 0.72, "positioning": 0.92, "technical": 0.90,
        "aerial": 0.78, "decision_speed": 0.95, "pressure_tolerance": 0.88,
        "creativity": 0.95, "work_rate": 0.65, "leadership": 0.82,
        "consistency": 0.92, "injury_resilience": 0.80, "form_momentum": 0.88,
        "big_game_performance": 0.90, "adaptability": 0.88, "teamwork": 0.95,
    },
    # ── Cricket ─────────────────────────────────
    {
        "player_id": "kohli_01",
        "name": "Virat Kohli",
        "sport": SPORT_CRICKET,
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
    {
        "player_id": "bumrah_01",
        "name": "Jasprit Bumrah",
        "sport": SPORT_CRICKET,
        "position": "Bowler",
        "nationality": "India",
        "age": 32,
        "bio": "Death-overs specialist — unplayable yorkers, deceptive pace variation.",
        "mbti_tag": "ISTJ",
        "decision_style": "calculated",
        "pressure_response": "thrives",
        "speed": 0.92, "stamina": 0.70, "positioning": 0.75, "technical": 0.95,
        "aerial": 0.40, "decision_speed": 0.88, "pressure_tolerance": 0.92,
        "creativity": 0.80, "work_rate": 0.85, "leadership": 0.72,
        "consistency": 0.88, "injury_resilience": 0.55, "form_momentum": 0.78,
        "big_game_performance": 0.94, "adaptability": 0.85, "teamwork": 0.78,
    },
    {
        "player_id": "rashid_01",
        "name": "Rashid Khan",
        "sport": SPORT_CRICKET,
        "position": "All-Rounder",
        "nationality": "Afghanistan",
        "age": 27,
        "bio": "Spin wizard — relentless accuracy, lethal leg breaks, handy lower-order bat.",
        "mbti_tag": "ENFJ",
        "decision_style": "instinctive",
        "pressure_response": "composed",
        "speed": 0.65, "stamina": 0.82, "positioning": 0.78, "technical": 0.90,
        "aerial": 0.45, "decision_speed": 0.85, "pressure_tolerance": 0.85,
        "creativity": 0.88, "work_rate": 0.90, "leadership": 0.75,
        "consistency": 0.85, "injury_resilience": 0.80, "form_momentum": 0.82,
        "big_game_performance": 0.85, "adaptability": 0.82, "teamwork": 0.85,
    },
    {
        "player_id": "dhoni_01",
        "name": "MS Dhoni",
        "sport": SPORT_CRICKET,
        "position": "Wicket-Keeper",
        "nationality": "India",
        "age": 44,
        "bio": "Captain Cool — ice-cold finisher, lightning-fast stumpings, tactical genius.",
        "mbti_tag": "ISTP",
        "decision_style": "calculated",
        "pressure_response": "thrives",
        "speed": 0.60, "stamina": 0.68, "positioning": 0.90, "technical": 0.88,
        "aerial": 0.50, "decision_speed": 0.95, "pressure_tolerance": 0.98,
        "creativity": 0.82, "work_rate": 0.75, "leadership": 0.98,
        "consistency": 0.85, "injury_resilience": 0.72, "form_momentum": 0.65,
        "big_game_performance": 0.96, "adaptability": 0.90, "teamwork": 0.92,
    },
]

SAMPLE_TEAMS: List[Dict[str, Any]] = [
    # Soccer
    {"id": "arsenal", "name": "Arsenal", "sport": SPORT_SOCCER, "league": "Premier League", "formation": "4-3-3", "style": "possession_press"},
    {"id": "real_madrid", "name": "Real Madrid", "sport": SPORT_SOCCER, "league": "La Liga", "formation": "4-3-3", "style": "counter_attack"},
    {"id": "man_city", "name": "Manchester City", "sport": SPORT_SOCCER, "league": "Premier League", "formation": "4-2-3-1", "style": "possession"},
    {"id": "barcelona", "name": "FC Barcelona", "sport": SPORT_SOCCER, "league": "La Liga", "formation": "4-3-3", "style": "tiki_taka"},
    {"id": "bayern", "name": "Bayern Munich", "sport": SPORT_SOCCER, "league": "Bundesliga", "formation": "4-2-3-1", "style": "high_press"},
    # Basketball
    {"id": "lakers", "name": "LA Lakers", "sport": SPORT_BASKETBALL, "league": "NBA", "formation": "small_ball", "style": "fast_break"},
    {"id": "warriors", "name": "Golden State Warriors", "sport": SPORT_BASKETBALL, "league": "NBA", "formation": "motion_offense", "style": "three_point"},
    {"id": "bucks", "name": "Milwaukee Bucks", "sport": SPORT_BASKETBALL, "league": "NBA", "formation": "paint_dominant", "style": "transition"},
    {"id": "nuggets", "name": "Denver Nuggets", "sport": SPORT_BASKETBALL, "league": "NBA", "formation": "pick_and_roll", "style": "half_court"},
    # Cricket
    {"id": "rcb", "name": "Royal Challengers Bengaluru", "sport": SPORT_CRICKET, "league": "IPL", "formation": "batting_heavy", "style": "aggressive"},
    {"id": "csk", "name": "Chennai Super Kings", "sport": SPORT_CRICKET, "league": "IPL", "formation": "spin_heavy", "style": "strategic"},
    {"id": "mi", "name": "Mumbai Indians", "sport": SPORT_CRICKET, "league": "IPL", "formation": "balanced", "style": "pace_dominant"},
    {"id": "india", "name": "India National Team", "sport": SPORT_CRICKET, "league": "International", "formation": "balanced", "style": "all_round"},
]


def get_player_sport(player_id: str) -> str | None:
    for p in SAMPLE_PLAYERS:
        if p["player_id"] == player_id:
            return p["sport"]
    return None


def get_compatible_teams(player_id: str) -> List[Dict[str, Any]]:
    sport = get_player_sport(player_id)
    if sport is None:
        return SAMPLE_TEAMS
    return [t for t in SAMPLE_TEAMS if t["sport"] == sport]


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
