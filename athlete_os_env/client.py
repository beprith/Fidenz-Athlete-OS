"""
AthleteOSEnv — OpenEnv-compliant WebSocket client for the Fidenz Athlete OS environment.
Inherits from openenv.core.env_client.EnvClient for full SDK compatibility
including from_docker_image() and from_env() class methods.
"""

from __future__ import annotations

from typing import Any, Dict

from openenv.core.env_client import EnvClient, StepResult

from models import AthleteAction, AthleteObservation, AthleteState


class AthleteOSEnv(EnvClient[AthleteAction, AthleteObservation, AthleteState]):
    """
    Async WebSocket client for the Fidenz Athlete OS environment.

    Usage (async):
        async with AthleteOSEnv(base_url="http://localhost:7860") as env:
            result = await env.reset()
            result = await env.step(AthleteAction(action_type="simulate_round", ...))

    Usage (sync wrapper):
        env = AthleteOSEnv(base_url="http://localhost:7860").sync()
        with env:
            result = env.reset()
            result = env.step(AthleteAction(...))

    Usage (from Docker image — used by evaluators):
        env = await AthleteOSEnv.from_docker_image("fidenz-athlete-os:latest")
        result = await env.reset()
        await env.close()
    """

    def _step_payload(self, action: AthleteAction | Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(action, dict):
            return action
        if hasattr(action, "model_dump"):
            return action.model_dump()
        if hasattr(action, "__dict__"):
            return vars(action)
        return dict(action)

    def _parse_result(self, payload: Dict[str, Any]) -> StepResult[AthleteObservation]:
        obs_data = payload.get("observation", {})
        obs = AthleteObservation(**{
            k: v for k, v in obs_data.items()
            if k in AthleteObservation.model_fields
        })
        return StepResult(
            observation=obs,
            reward=payload.get("reward", 0.0) or 0.0,
            done=payload.get("done", False),
        )

    def _parse_state(self, payload: Dict[str, Any]) -> AthleteState:
        return AthleteState(**{
            k: v for k, v in payload.items()
            if k in AthleteState.model_fields
        })
