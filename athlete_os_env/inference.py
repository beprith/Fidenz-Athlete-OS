"""
inference.py — Fidenz Athlete OS OpenEnv Baseline Inference Script
==================================================================
Meta OpenEnv Hackathon requirements:
  - OpenAI Client for all LLM calls (no other SDKs / raw HTTP for LLM)
  - API_BASE_URL, MODEL_NAME with defaults; HF_TOKEN required (no default)
  - Stdout: only [START] / [STEP] / [END] lines (see log_*); debug -> stderr
  - Target: < 20 min on 2 vCPU / 8 GB RAM

STDOUT FORMAT (protocol lines only):
  [START] task=<task_name> env=<benchmark> model=<model_name>
  [STEP] step=<n> action=<action_str> reward=<0.00> done=<true|false> error=<msg|null>
  [END] success=<true|false> steps=<n> rewards=<r1,r2,...,rn>
"""

import asyncio
import json
import os
import sys
import textwrap
import traceback
from typing import List, Optional
from urllib.parse import urlparse

from openai import OpenAI

from client import AthleteOSEnv
from models import AthleteAction, TASK_MAX_STEPS
from server.utils.score_bounds import clip_open_unit_interval

# ---------------------------------------------------------------------------
# Environment configuration (Hackathon: defaults via os.getenv second arg)
# ---------------------------------------------------------------------------
IMAGE_NAME = os.getenv("IMAGE_NAME")

API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None or not str(HF_TOKEN).strip():
    raise ValueError("HF_TOKEN environment variable is required")

BENCHMARK = "fidenz_athlete_os"
MAX_STEPS_OVERRIDE = None
TEMPERATURE = 0.3
MAX_TOKENS = 1024
SUCCESS_SCORE_THRESHOLD = 0.1

TASKS = [
    "single_player_stat_prediction",
    "player_team_fit_analysis",
    "full_squad_recruitment_sim",
]

FALLBACK_ACTION = '{"action_type": "simulate_round", "player_id": "default", "target_context": {"team": "Arsenal", "formation": "4-3-3", "role": "CF"}}'


def _merge_no_proxy_for_host(host: str) -> None:
    """Avoid HTTP(S)_PROXY breaking WSS to Space / local env hosts (mirrors OpenEnv localhost logic)."""
    if not host:
        return
    h = host.lower().split(":")[0]
    for key in ("NO_PROXY", "no_proxy"):
        cur = os.environ.get(key, "")
        parts = [p.strip() for p in cur.split(",") if p.strip()]
        if h not in [p.lower() for p in parts]:
            parts.append(h)
            os.environ[key] = ",".join(parts)


def explicit_env_base_url() -> Optional[str]:
    """Non-empty HTTP(S) base URL if the harness set any known env var (Phase 2 / Spaces)."""
    for key in (
        "ENV_BASE_URL",
        "OPENENV_BASE_URL",
        "OPENENV_URL",
        "SPACE_URL",
        "HF_SPACE_URL",
        "SPACE_APP_URL",
    ):
        v = os.environ.get(key, "").strip()
        if v:
            return v.rstrip("/")
    return None


def resolve_env_base_url() -> str:
    """URL of the running OpenEnv server; default local dev port."""
    return explicit_env_base_url() or "http://127.0.0.1:7860"


def _use_docker_image() -> bool:
    """Docker is unavailable in many CI / submission runners; allow opt-out."""
    if os.getenv("USE_DOCKER_IMAGE", "").strip().lower() in ("0", "false", "no", "off"):
        return False
    return bool(IMAGE_NAME)


async def connect_env_client() -> AthleteOSEnv:
    """
    Connect to the environment.

    Order (critical for Phase 2):
    1. Explicit ENV_BASE_URL / SPACE_URL / … — always wins over IMAGE_NAME so runners
       that inject the Space URL but also set IMAGE_NAME do not call from_docker_image.
    2. Else from_docker_image(IMAGE_NAME) when USE_DOCKER_IMAGE is not disabled.
    3. If Docker fails or is skipped, fall back to resolve_env_base_url() (localhost default).
    """
    explicit = explicit_env_base_url()
    if explicit:
        return await _connect_via_url(explicit)

    if IMAGE_NAME and _use_docker_image():
        try:
            return await AthleteOSEnv.from_docker_image(IMAGE_NAME)
        except Exception as exc:
            print(
                f"[DEBUG] from_docker_image({IMAGE_NAME!r}) failed ({type(exc).__name__}: {exc}); "
                "falling back to HTTP/WebSocket URL",
                flush=True,
                file=sys.stderr,
            )
            traceback.print_exc(file=sys.stderr)
            return await _connect_via_url(resolve_env_base_url())

    return await _connect_via_url(resolve_env_base_url())


async def _connect_via_url(url: str) -> AthleteOSEnv:
    parsed = urlparse(url)
    if parsed.hostname:
        _merge_no_proxy_for_host(parsed.hostname)
    print(f"[DEBUG] Connecting to environment at {url}", flush=True, file=sys.stderr)
    client = AthleteOSEnv(base_url=url)
    await client.connect()
    return client

SYSTEM_PROMPT = textwrap.dedent("""\
    You are a sports recruitment AI agent operating inside the Fidenz Athlete OS
    simulation environment. Your goal is to evaluate player performance by issuing
    simulation actions and interpreting results.
    Always respond with a valid JSON action in the format:
    {"action_type": "simulate_round", "player_id": "<id>", "target_context": {...}}
    or {"action_type": "query_persona", "player_id": "<id>", "query": "<question>"}
""").strip()

llm_client = OpenAI(api_key=HF_TOKEN, base_url=API_BASE_URL)


# ---------------------------------------------------------------------------
# Structured stdout logging (mandatory format)
# ---------------------------------------------------------------------------

def log_start(task: str, env: str, model: str) -> None:
    print(f"[START] task={task} env={env} model={model}", flush=True)


def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    # Single-line stdout: strip newlines from error text
    if error:
        error_val = error.replace("\n", " ").replace("\r", " ")
    else:
        error_val = "null"
    done_val = str(done).lower()
    print(
        f"[STEP] step={step} action={action} reward={reward:.2f} done={done_val} error={error_val}",
        flush=True,
    )


def log_end(success: bool, steps: int, rewards: List[float]) -> None:
    """Hackathon format: [END] has success, steps, rewards only (no score field)."""
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(
        f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_action(text: str) -> dict:
    try:
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception:
        pass
    return json.loads(FALLBACK_ACTION)


def build_user_prompt(step: int, obs, history: List[str]) -> str:
    last_round = obs.round_result if obs.round_result is not None else {}
    metrics = obs.performance_metrics if obs.performance_metrics is not None else {}
    return textwrap.dedent(f"""\
        Goal: {obs.goal}
        Player: {obs.player_summary}
        Last round: {json.dumps(last_round)}
        Metrics: {json.dumps(metrics)}
        Drift penalty: {obs.persona_drift_score:.3f}
        Hint: {obs.step_hint or ''}
        History: {history[-5:]}
        Issue your next action as JSON:
    """).strip()


def get_model_action(step: int, obs, history: List[str]) -> str:
    user_prompt = build_user_prompt(step, obs, history)
    try:
        completion = llm_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        return (completion.choices[0].message.content or "").strip()
    except Exception as exc:
        print(f"[DEBUG] Model request failed: {exc}", flush=True, file=sys.stderr)
        return FALLBACK_ACTION


# ---------------------------------------------------------------------------
# Task runner
# ---------------------------------------------------------------------------

async def run_task(env: AthleteOSEnv, task_id: str) -> float:
    max_steps = TASK_MAX_STEPS.get(task_id, 20)
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_id, env=BENCHMARK, model=MODEL_NAME)

    try:
        result = await env.reset(task_id=task_id)
        obs = result.observation
        history: List[str] = []

        for step in range(1, max_steps + 1):
            if result.done:
                break

            response_text = get_model_action(step, obs, history)
            action_dict = parse_action(response_text)
            try:
                action = AthleteAction(**{
                    k: v for k, v in action_dict.items()
                    if k in AthleteAction.model_fields
                })
            except Exception as exc:
                print(f"[DEBUG] Invalid action shape, using fallback: {exc}", flush=True, file=sys.stderr)
                action = AthleteAction.model_validate_json(FALLBACK_ACTION)
                action_dict = json.loads(FALLBACK_ACTION)
            action_str = json.dumps(action_dict, separators=(",", ":"))

            result = await env.step(action)
            obs = result.observation
            reward = result.reward or 0.0
            done = result.done
            error = obs.last_action_error

            rewards.append(reward)
            steps_taken = step

            log_step(
                step=step,
                action=action_str,
                reward=reward,
                done=done,
                error=error,
            )

            history.append(f"Step {step}: {action_str} -> reward {reward:+.2f}")

            if done:
                break

        raw = sum(rewards) / max(len(rewards), 1)
        score = clip_open_unit_interval(min(max(raw, 0.0), 1.0))
        success = score >= SUCCESS_SCORE_THRESHOLD

    finally:
        log_end(success=success, steps=steps_taken, rewards=rewards)

    return score


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    env: Optional[AthleteOSEnv] = None
    try:
        env = await connect_env_client()

        all_scores: dict[str, float] = {}
        for task_id in TASKS:
            score = await run_task(env, task_id)
            all_scores[task_id] = round(score, 4)

        print(f"[DEBUG] === BASELINE SCORES ===", flush=True, file=sys.stderr)
        for task, score in all_scores.items():
            print(f"[DEBUG]   {task}: {score:.4f}", flush=True, file=sys.stderr)
        total = sum(all_scores.values()) / len(all_scores) if all_scores else 0
        print(f"[DEBUG]   AVERAGE: {total:.4f}", flush=True, file=sys.stderr)

    finally:
        if env is not None:
            try:
                await env.close()
            except Exception as exc:
                print(f"[DEBUG] env.close() failed (ignored): {exc}", flush=True, file=sys.stderr)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception:
        traceback.print_exc(file=sys.stderr)
        raise
