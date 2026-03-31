"""
inference.py — Fidenz Athlete OS OpenEnv Baseline Inference Script
Place at project root. Reads API_BASE_URL, MODEL_NAME, HF_TOKEN from env vars.
Uses OpenAI client for all LLM calls per hackathon spec.
Runtime target: < 20 minutes on 2vCPU / 8GB RAM.
"""

import os
import json
from openai import OpenAI
from client import AthleteOSEnv, StepResult
from models import AthleteAction

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.environ.get("HF_TOKEN", "sk-placeholder")

SYSTEM_PROMPT = """You are a sports recruitment AI agent operating inside the Fidenz Athlete OS simulation environment.
Your goal is to evaluate player performance by issuing simulation actions and interpreting results.
Always respond with a valid JSON action in the format:
{"action_type": "simulate_round", "player_id": "<id>", "target_context": {...}}
or {"action_type": "query_persona", "player_id": "<id>", "query": "<question>"}
"""

MAX_STEPS = 30
TEMPERATURE = 0.3
MAX_TOKENS = 1024
TASKS = [
    "single_player_stat_prediction",
    "player_team_fit_analysis",
    "full_squad_recruitment_sim",
]

client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)


def parse_action(text: str) -> dict:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass
    return {
        "action_type": "simulate_round",
        "player_id": "default",
        "target_context": {"team": "Arsenal", "formation": "4-3-3", "role": "CF"},
    }


def run_task(env: AthleteOSEnv, task_id: str) -> float:
    result = env.reset(task_id=task_id)
    obs = result.observation
    history: list[str] = []

    for step in range(1, MAX_STEPS + 1):
        if result.done:
            break

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": (
                f"Goal: {obs.goal}\n"
                f"Player: {obs.player_summary}\n"
                f"Last round: {json.dumps(obs.round_result)}\n"
                f"Metrics: {json.dumps(obs.performance_metrics)}\n"
                f"Drift penalty: {obs.persona_drift_score:.3f}\n"
                f"Hint: {obs.step_hint}\n"
                f"History: {history[-5:]}\n"
                "Issue your next action as JSON:"
            )},
        ]

        try:
            completion = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
            )
            response_text = completion.choices[0].message.content or ""
        except Exception as exc:
            print(f"  LLM call failed: {exc}")
            response_text = '{"action_type": "simulate_round", "player_id": "default", "target_context": {"team": "Arsenal"}}'

        action_dict = parse_action(response_text)
        action = AthleteAction(**{
            k: v for k, v in action_dict.items()
            if k in AthleteAction.model_fields
        })

        result = env.step(action)
        obs = result.observation
        reward = result.reward or 0.0
        history.append(f"Step {step}: reward={reward:+.3f} drift={obs.persona_drift_score:.3f}")
        print(f"  [{task_id}] Step {step} | reward={reward:+.3f} | done={result.done}")

        if result.done:
            break

    return result.reward or 0.0


def main():
    env_url = os.environ.get("ENV_BASE_URL", "http://localhost:7860")
    scores: dict[str, float] = {}

    with AthleteOSEnv(base_url=env_url) as env:
        health = env.health()
        print(f"Environment: {health}")

        for task_id in TASKS:
            print(f"\n=== Running task: {task_id} ===")
            score = run_task(env, task_id)
            scores[task_id] = round(score, 4)
            print(f"  Final score: {score:.4f}")

    print("\n=== BASELINE SCORES ===")
    for task, score in scores.items():
        print(f"  {task}: {score:.4f}")
    total = sum(scores.values()) / len(scores) if scores else 0
    print(f"  AVERAGE: {total:.4f}")


if __name__ == "__main__":
    main()
