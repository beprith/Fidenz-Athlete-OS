"""
AthleteEnvironment — core OpenEnv environment implementing reset/step/state.
Inherits from openenv.core.env_server.Environment.
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

import numpy as np

from openenv.core.env_server import Environment
from openenv.core.env_server.types import EnvironmentMetadata

from models import (
    AthleteAction,
    AthleteObservation,
    AthleteState,
    TASK_MAX_STEPS,
)
from server.agents.orchestrator import OrchestratorAgent
from server.rl.reward import RewardEngine
from server.rl.kl_constraint import KLConstraint
from server.rl.ppo_policy import PPOPolicy
from server.rl.experience_replay import ExperienceReplay, Transition
from server.utils.logger import EpisodeLogger, get_logger

log = get_logger("environment")


TASK_IDS = [
    "single_player_stat_prediction",
    "player_team_fit_analysis",
    "full_squad_recruitment_sim",
]


class AthleteEnvironment(Environment[AthleteObservation, AthleteAction, AthleteState]):
    """
    OpenEnv-compliant environment.
    Implements reset(), step(action), and state property.
    """

    def __init__(self):
        self._state = AthleteState()
        self.orchestrator = OrchestratorAgent()
        self.reward_engine = RewardEngine()
        self.kl_constraint = KLConstraint(beta=0.1)
        self.ppo = PPOPolicy()
        self.replay = ExperienceReplay()
        self._episode_logger = EpisodeLogger()
        self._ws_callbacks: list = []
        self._next_task_id: str | None = None
        self._task_index: int = 0

    # ------------------------------------------------------------------
    # OpenEnv API
    # ------------------------------------------------------------------

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **kwargs: Any,
    ) -> AthleteObservation:
        """Initialize a new episode and return the initial observation."""
        task_id = self._next_task_id or kwargs.get("task_id") or self._select_task()
        self._next_task_id = None

        self._state = AthleteState(
            episode_id=episode_id or str(uuid.uuid4()),
            task_id=task_id,
        )

        self.kl_constraint.reset()
        self.ppo.reset()
        self.replay.clear()

        self._episode_logger.set_context(self._state.episode_id)
        self._episode_logger.info(f"Reset — task={self._state.task_id}")

        obs_data = self.orchestrator.initialize_episode(self._state.task_id)

        self._state.player_id = obs_data.get("player_id", "")
        self._state.goal = obs_data.get("goal", "")
        self._state.persona_initialized = True
        self._state.simulation_status = "idle"
        self._state.total_rounds = TASK_MAX_STEPS.get(self._state.task_id, 10)
        self._state.baseline_persona_vector = self.orchestrator.blackboard.get(
            "baseline_persona_vector", [0.5] * 16
        )

        self.ppo.initialize_from_persona(self._state.baseline_persona_vector)

        self._emit_ws("phase_change", {"phase": "idle"})

        return AthleteObservation(
            goal=obs_data["goal"],
            player_summary=obs_data["player_summary"],
            graph_context=obs_data.get("graph_context"),
            step_hint="Start by simulating a round with target_context.",
            done=False,
            reward=0.0,
        )

    def step(
        self,
        action: AthleteAction,
        timeout_s: Optional[float] = None,
        **kwargs: Any,
    ) -> AthleteObservation:
        """Execute one step and return observation with reward and done flag."""
        self._state.step_count += 1
        self._state.current_round += 1
        self._state.simulation_status = "simulating"
        self._episode_logger.set_context(self._state.episode_id, self._state.step_count)

        self._emit_ws("phase_change", {"phase": "simulating"})

        result = self.orchestrator.route(action, self._state)

        if "error" in result and result["error"]:
            return AthleteObservation(
                goal=self._state.goal,
                player_summary=result.get("player_summary", ""),
                last_action_error=result["error"],
                step_hint="Fix the error and try again.",
                done=False,
                reward=0.0,
            )

        raw_reward = self.reward_engine.compute(result, self._state)

        persona_vector = result.get("persona_vector", [0.5] * 16)
        baseline = self._state.baseline_persona_vector or [0.5] * 16
        kl_penalty = self.kl_constraint.compute(persona_vector, baseline)

        shaped_reward = max(0.0, raw_reward - kl_penalty)
        self._state.cumulative_reward += shaped_reward
        self._state.kl_penalty_total += kl_penalty
        self._state.reward = shaped_reward

        self.replay.push(Transition(
            state={"step": self._state.step_count},
            action=action.model_dump(),
            reward=shaped_reward,
            next_state={"step": self._state.step_count + 1},
            done=False,
            persona_vector=persona_vector,
            advantage=0.0,
        ))

        if self._state.step_count % 5 == 0 and len(self.replay) >= 5:
            self._ppo_update()

        done = self._check_done(result)
        self._state.done = done

        if done:
            self._state.simulation_status = "grading"
            self._emit_ws("phase_change", {"phase": "grading"})
            grade = self.orchestrator.grade_episode(self._state)
            self._state.reward = grade
            shaped_reward = grade
            self._state.simulation_status = "done"
            self._emit_ws("phase_change", {"phase": "done"})

        hint = self.reward_engine.get_hint(shaped_reward)

        self._emit_ws("reward_update", {
            "step": self._state.step_count,
            "reward": shaped_reward,
            "kl_penalty": kl_penalty,
            "net": shaped_reward,
        })

        if result.get("round_result"):
            self._emit_ws("round_event", {
                "round": self._state.current_round,
                "player": self._state.player_id,
                "action": action.action_type,
                "rating": result["round_result"].get("rating", 0),
            })

        self._episode_logger.info(
            f"Step {self._state.step_count}: reward={shaped_reward:.3f} "
            f"kl={kl_penalty:.3f} done={done}"
        )

        return AthleteObservation(
            goal=self._state.goal,
            player_summary=result.get("player_summary", ""),
            round_result=result.get("round_result"),
            performance_metrics=result.get("performance_metrics", {}),
            persona_drift_score=kl_penalty,
            last_action_error=result.get("error"),
            graph_context=result.get("graph_context"),
            step_hint=hint,
            done=done,
            reward=shaped_reward,
        )

    @property
    def state(self) -> AthleteState:
        return self._state

    def close(self) -> None:
        pass

    def get_metadata(self) -> EnvironmentMetadata:
        return EnvironmentMetadata(
            name="Fidenz Athlete OS",
            description="Multi-sport player simulation platform — OpenEnv-compliant RL environment",
            version="0.1.0",
        )

    # ------------------------------------------------------------------
    # Task management
    # ------------------------------------------------------------------

    def set_next_task(self, task_id: str) -> None:
        """Pre-select a task for the next reset() call."""
        self._next_task_id = task_id

    def _select_task(self) -> str:
        task = TASK_IDS[self._task_index % len(TASK_IDS)]
        self._task_index += 1
        return task

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _check_done(self, result: dict[str, Any]) -> bool:
        max_steps = TASK_MAX_STEPS.get(self._state.task_id, 10)
        if self._state.step_count >= max_steps:
            return True
        if result.get("done"):
            return True
        return False

    def _ppo_update(self) -> None:
        self.replay.compute_advantages()
        batch = self.replay.sample(min(len(self.replay), 16))
        if not batch:
            return

        mean_advantage = float(np.mean([t.advantage for t in batch]))
        advantages = np.full(self.ppo.dim, mean_advantage, dtype=np.float64)
        old_probs = self.ppo.get_weights()

        self.ppo.update(advantages, old_probs)

        new_weights = self.ppo.get_weights().tolist()
        self.orchestrator.persona_agent.update_persona_traits(
            self._state.player_id, new_weights
        )

    # ------------------------------------------------------------------
    # WebSocket event emission
    # ------------------------------------------------------------------

    def register_ws_callback(self, callback) -> None:
        self._ws_callbacks.append(callback)

    def _emit_ws(self, event_type: str, data: dict[str, Any]) -> None:
        payload = {"type": event_type, **data}
        for cb in self._ws_callbacks:
            try:
                cb(payload)
            except Exception:
                pass
