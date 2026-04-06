# ── Build frontend ──────────────────────────────
FROM node:20-slim AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build
# Output: /frontend/dist/

# ── Python API server ───────────────────────────
FROM python:3.11-slim

ENV PORT=7860
ENV WORKERS=1
ENV MAX_CONCURRENT_ENVS=100
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl git && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Inject built frontend into FastAPI static folder
COPY --from=frontend-builder /frontend/dist ./server/static

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s \
    CMD curl -f http://localhost:7860/health || exit 1

EXPOSE 7860

CMD uvicorn server.app:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}
