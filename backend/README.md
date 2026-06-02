"""Python backend for StayWiseAI.

Housing recommendation engine orchestrating a 5-agent LangGraph pipeline.

## Setup

1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env.local` and fill in API keys
3. `python -m uvicorn app.main:app --reload`

## Project Structure

```
app/
├── main.py           # FastAPI app initialization
├── agents/           # 5-agent pipeline nodes
├── graph/            # LangGraph state and compiled graph
├── models/           # Pydantic models
├── clients/          # External API wrappers
├── db/              # Database setup
└── api/             # Route handlers

tests/
├── unit/            # Unit tests for agents
├── integration/     # E2E tests
└── conftest.py      # Pytest fixtures
```

## API Routes

- `POST /api/recommend` — Submit user query, stream recommendations
- `POST /api/track-click` — Track affiliate click
- `GET /api/health` — Health check

## Architecture

5-agent LangGraph pipeline:
1. Intent Agent (LLM, claude-sonnet-4-6, temp 0.2)
2. Neighborhood Agent (pure function)
3. Retrieval Agent (API calls)
4. Scoring Engine (skill function)
5. Explanation Agent (LLM, claude-opus-4-7, temp 0.4)

State persists in Neon Postgres via SQLAlchemy + LangGraph checkpointer.
API responses cached in Upstash Redis (6-hour TTL).
Traces emitted to LangSmith for observability.
