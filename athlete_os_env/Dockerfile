# Single base image only (python:3.11-slim) — avoids a second Docker Hub pull for
# node:20-slim, which often fails in validators with registry/network errors.

FROM python:3.11-slim

ENV PORT=7860
ENV WORKERS=1
ENV MAX_CONCURRENT_ENVS=100
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Node.js 18+ from Debian bookworm (required for Vite 5) + curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    ca-certificates \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Full app source (frontend sources; dist is usually not in repo)
COPY . .

WORKDIR /app/frontend
RUN npm ci && npm run build

WORKDIR /app
RUN rm -rf server/static && mv frontend/dist server/static

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s \
    CMD curl -f http://localhost:7860/health || exit 1

EXPOSE 7860

CMD uvicorn server.app:app --host 0.0.0.0 --port ${PORT} --workers ${WORKERS}
