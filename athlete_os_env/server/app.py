"""
FastAPI server — OpenEnv endpoints (via create_fastapi_app) + custom API + WebSocket + static files.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from openenv.core.env_server import create_fastapi_app

from models import AthleteAction, AthleteObservation
from server.athlete_environment import AthleteEnvironment

# ---------------------------------------------------------------------------
# Shared environment singleton
# ---------------------------------------------------------------------------

_env = AthleteEnvironment()

STATIC_DIR = Path(__file__).parent / "static"

# ---------------------------------------------------------------------------
# Create the OpenEnv-compliant FastAPI app via SDK factory
# ---------------------------------------------------------------------------

app = create_fastapi_app(
    env=lambda: _env,
    action_cls=AthleteAction,
    observation_cls=AthleteObservation,
)

app.title = "Fidenz Athlete OS Environment"
app.description = "Multi-sport player simulation platform — OpenEnv-compliant RL environment"
app.version = "0.1.0"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Custom API endpoints (beyond OpenEnv standard)
# ---------------------------------------------------------------------------

class SetTaskRequest(BaseModel):
    task_id: str


@app.post("/api/set-task")
async def set_task(req: SetTaskRequest):
    """Pre-select a task for the next reset() call."""
    _env.set_next_task(req.task_id)
    return {"ok": True, "task_id": req.task_id}


@app.get("/api/tasks")
async def list_tasks():
    return {
        "tasks": [
            {"id": "single_player_stat_prediction", "name": "Single Player Stat Prediction", "difficulty": "easy", "max_steps": 10},
            {"id": "player_team_fit_analysis", "name": "Player-Team Tactical Fit Analysis", "difficulty": "medium", "max_steps": 20},
            {"id": "full_squad_recruitment_sim", "name": "Full Squad Recruitment Simulation", "difficulty": "hard", "max_steps": 50},
        ]
    }


@app.get("/api/players")
async def list_players():
    from server.utils.sports_data import SAMPLE_PLAYERS
    return {"players": SAMPLE_PLAYERS}


@app.get("/api/teams")
async def list_teams():
    from server.utils.sports_data import SAMPLE_TEAMS
    return {"teams": SAMPLE_TEAMS}


@app.get("/api/graph")
async def get_graph():
    graph = _env.orchestrator.graph
    nodes = []
    for nid, data in graph._nodes.items():
        nodes.append({"id": nid, "label": data.get("name", nid), "type": data.get("entity_type", "Unknown"), **data})
    edges = []
    for edge in graph._edges:
        edges.append({
            "source": edge.source_id,
            "target": edge.target_id,
            "relation": edge.relation,
            **edge.properties,
        })
    return {"nodes": nodes, "edges": edges}


@app.get("/api/report")
async def get_report():
    state_data = _env.state
    if not state_data.persona_initialized:
        raise HTTPException(status_code=400, detail="No active episode")
    grade = _env.orchestrator.grade_episode(_env.state)
    report = _env.orchestrator.generate_report(_env.state, grade)
    return {"report": report, "grade": grade}


@app.post("/api/upload")
async def upload_data(file: UploadFile = File(...)):
    content = await file.read()
    return {"filename": file.filename, "size": len(content), "status": "received"}


# ---------------------------------------------------------------------------
# WebSocket for real-time updates
# ---------------------------------------------------------------------------

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        if ws in self.active:
            self.active.remove(ws)

    async def broadcast(self, message: dict):
        for ws in self.active:
            try:
                await ws.send_json(message)
            except Exception:
                pass


ws_manager = ConnectionManager()


def _sync_ws_callback(payload: dict):
    """Bridge sync env callbacks to async WebSocket broadcasts."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(ws_manager.broadcast(payload))
    except RuntimeError:
        pass


_env.register_ws_callback(_sync_ws_callback)


@app.websocket("/ws/live")
async def websocket_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            msg = json.loads(data)
            await ws.send_json({"type": "ack", "received": msg})
    except WebSocketDisconnect:
        ws_manager.disconnect(ws)


# ---------------------------------------------------------------------------
# Static frontend serving
# ---------------------------------------------------------------------------

if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
    if (STATIC_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(STATIC_DIR / "assets")), name="static-assets")

    @app.get("/app/{rest_of_path:path}")
    async def serve_spa(rest_of_path: str = ""):
        return FileResponse(str(STATIC_DIR / "index.html"))

    @app.get("/")
    async def serve_index():
        return FileResponse(str(STATIC_DIR / "index.html"))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    import uvicorn
    port = int(os.environ.get("PORT", "7860"))
    uvicorn.run(
        "server.app:app",
        host="0.0.0.0",
        port=port,
        workers=1,
        log_level="info",
    )


if __name__ == "__main__":
    main()
