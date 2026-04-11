"""
GraderAgent — deterministic task graders producing scores in (0, 1) (strict, no 0.0/1.0).
"""

from __future__ import annotations

from typing import Any, Dict, List

import numpy as np

from server.utils.logger import get_logger
from server.utils.score_bounds import clip_open_unit_interval

log = get_logger("grader_agent")


class GraderAgent:
    """Deterministic graders for all three OpenEnv tasks."""

    def grade(self, task_id: str, data: Dict[str, Any]) -> float:
        graders = {
            "single_player_stat_prediction": self.grade_task1,
            "player_team_fit_analysis": self.grade_task2,
            "full_squad_recruitment_sim": self.grade_task3,
        }
        grader = graders.get(task_id)
        if not grader:
            log.warning(f"Unknown task_id: {task_id}")
            return clip_open_unit_interval(0.5)
        score = grader(data)
        return clip_open_unit_interval(float(np.clip(score, 0.0, 1.0)))

    # ------------------------------------------------------------------
    # Task 1 — Easy: Single Player Stat Prediction
    # ------------------------------------------------------------------

    def grade_task1(self, data: Dict[str, Any]) -> float:
        prediction = data.get("prediction", {})
        ground_truth = data.get("ground_truth", {})
        round_log = data.get("round_log", [])

        pred_direction = prediction.get("direction", "above")
        true_direction = ground_truth.get("direction", "above")
        correct = int(pred_direction == true_direction)

        base = 0.5 * correct

        confidence = prediction.get("confidence", 0.5)
        calibration = 0.3 * (1.0 - abs(confidence - float(correct)))

        reasoning_score = self._grade_reasoning(round_log)

        return min(1.0, base + calibration + 0.2 * reasoning_score)

    # ------------------------------------------------------------------
    # Task 2 — Medium: Player-Team Tactical Fit Analysis
    # ------------------------------------------------------------------

    def grade_task2(self, data: Dict[str, Any]) -> float:
        sim_log = data.get("sim_log", [])
        player_profile = data.get("player_profile", {})
        team_style = data.get("team_style", {})

        if not sim_log:
            return clip_open_unit_interval(0.0)

        round_scores = []
        for round_data in sim_log:
            output_plausibility = self._score_output_plausibility(round_data, player_profile)
            tactical_alignment = self._score_tactical_alignment(round_data, team_style)
            narrative_coherence = self._score_narrative_coherence(round_data)

            score = 0.4 * output_plausibility + 0.4 * tactical_alignment + 0.2 * narrative_coherence
            round_scores.append(score)

        return float(np.mean(round_scores))

    # ------------------------------------------------------------------
    # Task 3 — Hard: Full Squad Recruitment Simulation
    # ------------------------------------------------------------------

    def grade_task3(self, data: Dict[str, Any]) -> float:
        season_log = data.get("season_log", {})
        if not season_log:
            return clip_open_unit_interval(0.0)

        scores = [
            0.30 * self._grade_squad_output(season_log),
            0.25 * self._grade_rotation(season_log),
            0.20 * self._grade_injury_mgmt(season_log),
            0.15 * self._grade_tactical_evolution(season_log),
            0.10 * self._grade_individual_dev(season_log),
        ]
        return float(sum(scores))

    # ------------------------------------------------------------------
    # Sub-graders
    # ------------------------------------------------------------------

    @staticmethod
    def _grade_reasoning(round_log: list) -> float:
        if not round_log:
            return 0.3
        log_text = " ".join(str(entry) for entry in round_log)
        word_count = len(log_text.split())
        if word_count < 10:
            return 0.2
        if word_count < 50:
            return 0.5
        return 0.8

    @staticmethod
    def _score_output_plausibility(
        round_data: Dict[str, Any], player_profile: Dict[str, Any]
    ) -> float:
        goals = round_data.get("goals", 0)
        rating = round_data.get("rating", 6.0)
        if goals > 5:
            return 0.1  # implausible
        if 4.0 <= rating <= 10.0:
            return 0.8
        return 0.4

    @staticmethod
    def _score_tactical_alignment(
        round_data: Dict[str, Any], team_style: Dict[str, Any]
    ) -> float:
        events = round_data.get("events", [])
        if not events:
            return 0.3
        successful = sum(1 for e in events if e.get("success"))
        ratio = successful / len(events) if events else 0
        return float(np.clip(ratio, 0.0, 1.0))

    @staticmethod
    def _score_narrative_coherence(round_data: Dict[str, Any]) -> float:
        events = round_data.get("events", [])
        if not events:
            return 0.3
        has_varied_types = len(set(e.get("type") for e in events)) >= 3
        return 0.8 if has_varied_types else 0.5

    @staticmethod
    def _grade_squad_output(season_log: Dict[str, Any]) -> float:
        total_goals = season_log.get("total_goals", 0)
        matches = season_log.get("matches_played", 1)
        gpg = total_goals / max(matches, 1)
        return float(np.clip(gpg / 2.0, 0.0, 1.0))

    @staticmethod
    def _grade_rotation(season_log: Dict[str, Any]) -> float:
        rotations = season_log.get("rotation_count", 0)
        matches = season_log.get("matches_played", 1)
        ratio = rotations / max(matches, 1)
        return float(np.clip(ratio / 0.5, 0.0, 1.0))

    @staticmethod
    def _grade_injury_mgmt(season_log: Dict[str, Any]) -> float:
        injuries = season_log.get("injuries_occurred", 0)
        rest_decisions = season_log.get("rest_decisions", 0)
        if injuries == 0:
            return 0.8
        prevention_ratio = rest_decisions / max(injuries, 1)
        return float(np.clip(prevention_ratio, 0.0, 1.0))

    @staticmethod
    def _grade_tactical_evolution(season_log: Dict[str, Any]) -> float:
        changes = season_log.get("formation_changes", 0)
        if changes == 0:
            return 0.3
        return float(np.clip(changes / 3.0, 0.0, 1.0))

    @staticmethod
    def _grade_individual_dev(season_log: Dict[str, Any]) -> float:
        improvements = season_log.get("player_improvements", 0)
        squad_size = season_log.get("squad_size", 11)
        ratio = improvements / max(squad_size, 1)
        return float(np.clip(ratio, 0.0, 1.0))
