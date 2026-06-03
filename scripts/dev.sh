#!/usr/bin/env bash
set -euo pipefail

echo "Setting up development environment (POSIX)"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv
fi

. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

: "${DATABASE_URL:=sqlite:///./dev.db}"
export DATABASE_URL
: "${ANTHROPIC_API_KEY:=placeholder}"
export ANTHROPIC_API_KEY
: "${REAL_ESTATE_API_KEY:=placeholder}"
export REAL_ESTATE_API_KEY
: "${LANGSMITH_TRACING:=false}"
export LANGSMITH_TRACING

echo "Initializing database tables..."
python -m app.db.init_db

echo "Starting development server (uvicorn) on http://0.0.0.0:8000"
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
