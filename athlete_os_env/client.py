"""
AthleteOSEnv — typed HTTP client for the Fidenz Athlete OS OpenEnv environment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx

from models import AthleteAction, AthleteObservation, AthleteState


@dataclass
class StepResult:
    observation: AthleteObservation
    reward: float
    done: bool


class AthleteOSEnv:
    """Synchronous HTTP client that wraps the OpenEnv REST API."""

    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip("/")
        self._client: httpx.Client | None = None

    def sync(self) -> "AthleteOSEnv":
        return self

    def __enter__(self) -> "AthleteOSEnv":
        self._client = httpx.Client(base_url=self.base_url, timeout=120.0)
        return self

    def __exit__(self, *args: Any) -> None:
        if self._client:
            self._client.close()

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._client = httpx.Client(base_url=self.base_url, timeout=120.0)
        return self._client

    def set_task(self, task_id: str) -> None:
        """Pre-select a task for the next reset() call."""
        resp = self.client.post("/api/set-task", json={"task_id": task_id})
        resp.raise_for_status()

    def reset(self, task_id: str | None = None) -> StepResult:
        if task_id:
            self.set_task(task_id)
        resp = self.client.post("/reset", json={})
        resp.raise_for_status()
        data = resp.json()
        return self._parse_result(data)

    def step(self, action: AthleteAction | Dict[str, Any]) -> StepResult:
        if isinstance(action, AthleteAction):
            action_dict = action.model_dump()
        else:
            action_dict = action
        # OpenEnv step expects: {"action": {...}}
        resp = self.client.post("/step", json={"action": action_dict})
        resp.raise_for_status()
        data = resp.json()
        return self._parse_result(data)

    def state(self) -> AthleteState:
        resp = self.client.get("/state")
        resp.raise_for_status()
        data = resp.json()
        return AthleteState(**{
            k: v for k, v in data.items()
            if k in AthleteState.model_fields
        })

    def health(self) -> Dict[str, Any]:
        resp = self.client.get("/health")
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def _parse_result(data: Dict[str, Any]) -> StepResult:
        obs_data = data.get("observation", {})
        obs = AthleteObservation(**{
            k: v for k, v in obs_data.items()
            if k in AthleteObservation.model_fields
        })
        return StepResult(
            observation=obs,
            reward=data.get("reward", 0.0) or 0.0,
            done=data.get("done", False),
        )
