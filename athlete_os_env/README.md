---
title: Fidenz Athlete OS Environment
emoji: "\U0001F3DF\uFE0F"
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
tags:
  - openenv
---

# Fidenz Athlete OS — Multi-Sport Player Simulation Platform

An **OpenEnv-compliant reinforcement learning environment** that simulates professional athletes as living, memory-bearing AI personas. Recruitment teams, coaches, and analytics staff can upload seed data and run constrained RL simulations to predict future performance under any team or league context.

> **For a detailed explanation of all mathematics, algorithms, and architecture, see [`TECHNICAL_DEEP_DIVE.html`](TECHNICAL_DEEP_DIVE.html).**

---

## Environment Description & Motivation

Real-world sports recruitment is a high-stakes decision involving incomplete data, contextual nuance, and uncertain futures. Traditional scouting relies on static stat sheets. **Fidenz Athlete OS** bridges this gap by:

1. **Modeling athletes as behavioral personas** — a 16-dimensional trait vector (speed, stamina, creativity, pressure tolerance, etc.) captures a player's behavioral fingerprint.
2. **Simulating match performance** — a probabilistic event engine generates structured match events (goals, assists, tackles, fouls) weighted by the persona traits, opponent strength, fatigue, and home advantage.
3. **Constraining persona drift** — a KL-divergence penalty ensures the RL policy doesn't warp the player's identity beyond plausible bounds.
4. **Building knowledge graphs** — an in-memory GraphRAG layer (replacing Neo4j/Zep Cloud) stores player-team-skill-match relationships for structured retrieval.

This is not a toy or game — it models a genuine task that recruitment analysts actually perform, and provides a rich, multi-dimensional observation space for agent evaluation.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    OpenEnv API Layer                          │
│  POST /reset  →  Observation    POST /step  →  Observation   │
│  GET  /state  →  State          GET  /health →  HealthResp   │
└────────────────────┬─────────────────────────┬───────────────┘
                     │                         │
             ┌───────▼───────┐         ┌───────▼───────┐
             │  Orchestrator  │◄───────►│  RL Engine    │
             │  (Swarm Router)│         │  PPO + KL     │
             └──┬──┬──┬──┬───┘         └───────────────┘
                │  │  │  │
    ┌───────┐ ┌▼┐┌▼┐┌▼┐┌▼───────┐
    │Ontology│ │P││S││G││ Report │
    │ Agent  │ │e││i││r││ Agent  │
    └────────┘ │r││m││a│└────────┘
               │s││R││d│
               │o││u││e│
               │n││n││r│
               │a││.││ │
               └─┘└─┘└─┘
                     │
             ┌───────▼───────┐
             │ In-Memory Graph│
             │ (Property Graph│
             │  + Vector Sim) │
             └────────────────┘
```

- **Multi-Agent Swarm**: Orchestrator routes actions to 6 specialized agents (Ontology, GraphBuilder, Persona, SimRunner, Grader, Report)
- **GraphRAG**: In-memory property graph with Player/Team/League/Skill/Match nodes, BFS traversal, and cosine vector similarity search
- **RL Engine**: PPO policy on a 16-dim persona trait vector with adaptive KL-divergence constraint to prevent persona drift
- **Simulation**: Probabilistic event engine with trait-weighted event sampling, fatigue model, and dual-context parallel simulation

---

## Action Space

```python
class AthleteAction(openenv.Action):
    action_type: str    # "simulate_round" | "query_persona" | "adjust_params"
    player_id: str      # Target player identifier
    target_context: dict # {"team": "Arsenal", "formation": "4-3-3", "role": "CF"}
    sim_params: dict     # {"opponent_strength": 0.7, "home_away": "away"}
    query: str           # Natural language query (for query_persona)
```

| Action Type | Description | Typical Use |
|-------------|-------------|-------------|
| `simulate_round` | Run one match simulation round | Core loop: observe → simulate → learn |
| `query_persona` | Retrieve persona info + graph context | Information gathering before simulation |
| `adjust_params` | Update simulation parameters | Tuning opponent strength, formation |

---

## Observation Space

```python
class AthleteObservation(openenv.Observation):
    # Inherited: done (bool), reward (float), metadata (dict)
    goal: str                        # Current task objective
    player_summary: str              # Player name + stats from last round
    round_result: dict               # {"goals": 1, "assists": 0, "rating": 7.2, "events": [...]}
    performance_metrics: dict        # {"tactical_fit": 0.72, "output_score": 0.65, ...}
    persona_drift_score: float       # KL divergence penalty from baseline
    graph_context: str               # Structured graph traversal + memory context
    step_hint: str                   # Reward-based hint for the agent
    screenshot_uri: str | None       # Optional (unused)
```

The observation provides rich signal at every step: raw match events, aggregated metrics, persona drift, graph context, and an adaptive hint.

---

## Tasks

| # | Task | Difficulty | Max Steps | Grader Description |
|---|------|-----------|-----------|---------------------|
| 1 | **Single Player Stat Prediction** | Easy | 10 | Binary prediction (above/below career mean) + confidence calibration + reasoning quality |
| 2 | **Player-Team Tactical Fit** | Medium | 20 | 5-round simulation scored on output plausibility (40%), tactical alignment (40%), narrative coherence (20%) |
| 3 | **Full Squad Recruitment Sim** | Hard | 50 | 10-match season for 11 players scored on squad output (30%), rotation (25%), injury management (20%), tactical evolution (15%), individual development (10%) |

All graders are **deterministic** and produce scores in **[0.0, 1.0]** with `np.clip`. Task difficulty genuinely escalates — Task 3 challenges even frontier models with multi-player optimization over a season-length horizon.

---

## Reward Function

The reward provides **partial credit per step** (not just sparse terminal feedback):

```
R_shaped = σ(0.40·output + 0.30·tactical + 0.20·coherence + 0.10·efficiency + penalties)
r_t = max(0, R_shaped − β·KL(π_current || π_baseline))
```

- **Bounded sigmoid** σ(x) with steepness=6.0, midpoint=0.5 → output always in [0, 1]
- **Hallucination penalty** (−0.3) for implausible stats
- **Repeat penalty** (−0.2) for 3+ consecutive identical actions
- **KL-divergence penalty** with adaptive β (grows when drift > 0.3, shrinks when < 0.05)

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_BASE_URL` | LLM API endpoint (OpenAI-compatible) | Yes |
| `MODEL_NAME` | Model identifier for inference | Yes |
| `HF_TOKEN` | Hugging Face / API authentication key | Yes |

---

## Setup

### Local Development

```bash
cd athlete_os_env
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Start server
PYTHONPATH=. uvicorn server.app:app --port 7860

# Or use the entry point
PYTHONPATH=. python -m server.app
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev      # Dev server with HMR
npm run build    # Production build → dist/
```

### Docker

```bash
docker build -t fidenz-athlete-os .
docker run -p 7860:7860 \
  -e API_BASE_URL=https://api.openai.com/v1 \
  -e MODEL_NAME=gpt-4o-mini \
  -e HF_TOKEN=your_token \
  fidenz-athlete-os
```

### Run Baseline Inference

```bash
ENV_BASE_URL=http://localhost:7860 \
API_BASE_URL=https://api.openai.com/v1 \
MODEL_NAME=gpt-4o-mini \
HF_TOKEN=your_token \
python inference.py
```

---

## API Endpoints

### OpenEnv Standard (auto-registered via SDK)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/reset` | POST | Initialize new episode; body: `{seed?, episode_id?}` |
| `/step` | POST | Execute one step; body: `{action: {...}}` |
| `/state` | GET | Current episode state |
| `/health` | GET | Health check → `{status: "healthy"}` |
| `/schema` | GET | JSON schemas for action, observation, and state models |
| `/metadata` | GET | Environment name, description, version |

### Custom Extensions

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/set-task` | POST | Pre-select task for next reset: `{task_id: "..."}` |
| `/api/tasks` | GET | List available tasks with difficulty and max_steps |
| `/api/players` | GET | List sample player profiles |
| `/api/teams` | GET | List sample team profiles |
| `/api/graph` | GET | Current knowledge graph (nodes + edges) |
| `/api/report` | GET | Generate scouting report for active episode |
| `/api/upload` | POST | Upload CSV/JSON data file |
| `/ws/live` | WS | Real-time WebSocket event stream |

---

## Baseline Scores

| Task | Expected Score Range | Notes |
|------|---------------------|-------|
| Single Player Stat Prediction | 0.55 – 0.70 | Binary accuracy + confidence calibration |
| Player-Team Tactical Fit | 0.40 – 0.58 | Depends on formation/role alignment |
| Full Squad Recruitment Sim | 0.25 – 0.40 | Most challenging; requires multi-round strategy |

---

## Project Structure

```
athlete_os_env/
├── inference.py              # Baseline inference script (root, uses OpenAI client)
├── client.py                 # Typed HTTP client for the environment
├── models.py                 # Pydantic models (Action, Observation, State)
├── openenv.yaml              # OpenEnv manifest (3 tasks, env vars)
├── pyproject.toml            # Project metadata + [project.scripts] server entry
├── requirements.txt          # Python dependencies (includes openenv-core)
├── uv.lock                   # Reproducible dependency lock
├── Dockerfile                # Multi-stage: Node 20 (frontend) + Python 3.11 (server)
├── docker-compose.yml        # Local dev compose
├── TECHNICAL_DEEP_DIVE.html  # Detailed math & architecture explanation
├── README.md                 # This file
├── server/
│   ├── app.py                # FastAPI server (create_fastapi_app + custom routes)
│   ├── athlete_environment.py # Core OpenEnv Environment implementation
│   ├── agents/               # Swarm agents (orchestrator, persona, grader, etc.)
│   ├── graphrag/             # In-memory property graph + retriever + ontology
│   ├── rl/                   # PPO policy, KL constraint, reward engine, replay buffer
│   ├── simulation/           # Event engine, persona config, simulation runner
│   ├── utils/                # LLM client, sports data, logger, retry
│   └── static/               # Built Vue frontend (served by FastAPI)
└── frontend/
    ├── src/
    │   ├── views/            # Home, Workspace, SimulationRun, Squad, Report
    │   ├── components/       # PlayerCard, PitchView, RewardChart, SwarmStatusBar, etc.
    │   ├── store/            # Pinia stores (episode, squad, simulation)
    │   ├── api/              # Axios HTTP client + WebSocket composable
    │   └── router/           # Vue Router
    ├── package.json
    └── vite.config.js
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.11, FastAPI, OpenEnv-core, NumPy |
| **RL Engine** | PPO (logit-space, no neural network) + KL Constraint + GAE |
| **Knowledge** | In-memory property graph + cosine vector similarity |
| **Frontend** | Vue 3, Vite, Tailwind CSS, D3.js, Chart.js, Pinia |
| **Inference** | OpenAI client (reads API_BASE_URL, MODEL_NAME, HF_TOKEN) |
| **Deploy** | Docker (multi-stage), Hugging Face Spaces (port 7860) |

---

## Validation

```bash
# Pre-submission validation
openenv validate
# → [OK] athlete_os: Ready for multi-mode deployment

# Docker build
docker build -t fidenz-athlete-os .

# Smoke test
curl -X POST http://localhost:7860/reset -d '{}' -H 'Content-Type: application/json'
```

---

*Built by Fidenz Labs for the OpenEnv Hackathon.*
