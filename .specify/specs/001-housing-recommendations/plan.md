# Implementation Plan: Housing Recommendation Engine

**Branch**: `001-housing-recommendations` | **Date**: 2026-05-29 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-housing-recommendations/spec.md`

## Summary

Users submit natural language descriptions of their ideal home via a Next.js frontend on Vercel. The frontend calls a separate Python FastAPI backend service, which orchestrates a 5-agent LangGraph pipeline: Intent Agent (LLM) parses the query, Neighborhood Agent scores neighborhoods, Retrieval Agent fetches listings, Scoring Engine ranks them, and Explanation Agent writes personalized explanations. Results stream back to the frontend as JSON, displaying three recommendations with affiliate links. Refinements preserve prior intent via session-scoped thread IDs. The backend persists agent state in Neon Postgres, caches API responses in Upstash Redis, and emits LangSmith traces for observability.

## Technical Context

**Frontend (Next.js on Vercel)**:
- Language: TypeScript 5+, Node 22 LTS, pnpm
- Stack: Next.js 15 (App Router), React Server Components, shadcn/ui, Tailwind CSS v4, Mapbox GL JS
- Validation: Zod schemas for API request/response shapes
- Testing: Vitest, Playwright E2E

**Backend (Python FastAPI - Separate Service)**:
- Language: Python 3.10+, pip/UV for packages
- Framework: FastAPI with Uvicorn (ASGI)
- Agent Orchestration: LangGraph (Python) with 5 agents
- LLM: Anthropic Claude via `anthropic` SDK
- Validation: Pydantic models
- Database: SQLAlchemy ORM + Neon Postgres
- Testing: pytest
- Deployment: Separate service (Railway, Render, AWS, self-hosted)

**Persistence**: Neon Postgres (agent state + clicks table), Upstash Redis (6-hour API cache)

**Observability**: LangSmith (agent traces), Sentry (Python backend errors), PostHog (frontend analytics)

**Scale/Scope**:
- Launch metro: San Francisco Bay Area (~50–100 neighborhoods)
- Listings source: RealEstateAPI.com (primary)
- User base: Initial launch, growth target 50 qualified affiliate clicks/week

## Constitution Check

✅ **Code Principles Adapted for Split Stack**:
1. TypeScript strict in frontend, Python type hints in backend
2. Named exports throughout, no defaults
3. Zod for frontend boundaries, Pydantic for backend boundaries
4. Pure skills in backend (Scoring Engine), deterministic agents (Neighborhood)
5. LLM calls use structured output (withStructuredOutput in Python LangChain)
6. LLM instances as module-level singletons in backend
7. PostgreSQL state persistence in production, MemorySaver in tests
8. Style guide applied to all prose (comments, explanations, prompts)
9. Explicit environment variables in `.env.example` and docs
10. CI gates: frontend (`pnpm test`, typecheck, build), backend (`pytest`, type check via mypy)

✅ **Process Principles**: Linear Spec → Plan → Tasks → Implement. Tests prove completion. Errors via state, not exceptions. Manual verification required.

## Project Structure

### Documentation (this feature)

```text
.specify/specs/001-housing-recommendations/
├── spec.md              # Feature specification (COMPLETE)
├── plan.md              # This file (HOW to build it)
├── research.md          # Phase 0 output (to be generated)
├── data-model.md        # Phase 1 output (to be generated)
├── quickstart.md        # Phase 1 output (to be generated)
├── contracts/           # Phase 1 output (API contracts, to be generated)
├── checklists/
│   └── requirements.md  # Spec quality checklist (APPROVED)
└── tasks.md             # Phase 2 output via /speckit.tasks (to be generated)
```

### Frontend (Next.js on Vercel)

```text
src/
├── app/
│   ├── layout.tsx               # Root layout with Sentry/PostHog
│   ├── page.tsx                 # Recommend page (server component)
│   └── components/
│       ├── recommend-flow.tsx   # Client component (streaming form)
│       ├── intent-card.tsx      # Editable intent chips
│       ├── neighborhood-map.tsx # Mapbox GL JS integration
│       ├── listings-grid.tsx    # Three ListingCards with streaming
│       ├── listing-card.tsx     # Photo, address, price, score, explanation
│       ├── refine-chat.tsx      # Chat for refinements
│       └── ftc-disclosure.tsx   # Non-dismissible banner
│
├── components/
│   └── ui/
│       ├── card.tsx             # shadcn/ui Card (owned in repo)
│       ├── badge.tsx            # shadcn/ui Badge
│       ├── button.tsx           # shadcn/ui Button
│       ├── textarea.tsx         # shadcn/ui Textarea
│       └── ... (other shadcn components)
│
├── types/
│   ├── api.ts                   # API request/response schemas (Zod)
│   ├── intent.ts                # Intent schema
│   ├── listing.ts               # NormalizedListing schema
│   └── neighborhood.ts          # NeighborhoodScore schema
│
├── lib/
│   ├── utils.ts                 # Utility functions
│   ├── affiliate.ts             # Affiliate URL building
│   ├── api-client.ts            # Backend API calls
│   └── logging.ts               # Structured logging
│
└── styles/
    └── globals.css              # Tailwind directives, theme tokens

tests/
├── unit/
│   └── lib/                     # Utility function tests
├── e2e/
│   └── recommend.e2e.ts         # Full user flow E2E tests
└── fixtures/
    └── mock-api-responses.json  # Test data

Root config:
├── package.json                 # Scripts: dev, build, start, test, lint, typecheck
├── tsconfig.json                # strict: true, @/* alias
├── .env.example                 # All frontend env vars
├── .eslintrc.js                 # ESLint config
├── .prettierrc.json             # Prettier config
├── vitest.config.ts             # Vitest with globals: true
├── playwright.config.ts         # Playwright E2E config
├── next.config.js               # Next.js config (Vercel deployment)
└── .gitignore                   # Excludes .env.local, build artifacts
```

### Backend (Python FastAPI - Separate Repository/Service)

```text
backend/
├── app/
│   ├── main.py                  # FastAPI app initialization
│   ├── agents/
│   │   ├── intent.py            # Intent Agent (LLM node)
│   │   ├── neighborhood.py      # Neighborhood Agent (pure function)
│   │   ├── retrieval.py         # Retrieval Agent (API calls)
│   │   ├── scoring.py           # Scoring Engine (skill function)
│   │   └── explanation.py       # Explanation Agent (LLM node)
│   │
│   ├── graph/
│   │   ├── state.py             # LangGraph StateDict definition
│   │   ├── graph.py             # Compiled StateGraph with PostgreSQL saver
│   │   └── nodes.py             # Node definitions (imports from agents/)
│   │
│   ├── models/
│   │   ├── intent.py            # Pydantic Intent model
│   │   ├── listing.py           # Pydantic NormalizedListing model
│   │   ├── neighborhood.py      # Pydantic NeighborhoodScore model
│   │   └── api.py               # Pydantic API request/response models
│   │
│   ├── clients/
│   │   ├── anthropic.py         # Anthropic SDK with singletons
│   │   ├── real_estate_api.py   # RealEstateAPI client (timeout/retry)
│   │   ├── walk_score.py        # Walk Score API client
│   │   └── google_places.py     # Google Places API client
│   │
│   ├── db/
│   │   ├── models.py            # SQLAlchemy table definitions
│   │   ├── engine.py            # Database connection singleton
│   │   └── migrations/          # Alembic migrations (git-tracked)
│   │
│   ├── api/
│   │   ├── routes.py            # POST /recommend, POST /track-click, GET /health
│   │   └── middleware.py        # CORS, rate-limiting, error handling
│   │
├── tests/
│   ├── unit/
│   │   ├── test_intent_agent.py
│   │   ├── test_neighborhood_agent.py
│   │   ├── test_scoring_engine.py
│   │   └── test_explanation_agent.py
│   ├── integration/
│   │   └── test_graph_e2e.py    # Full 5-agent pipeline test
│   └── fixtures/
│       └── mock_listings.json   # Test data
│
├── pyproject.toml               # Python dependencies (pip, Poetry, or UV)
├── .env.example                 # All backend env vars
├── requirements.txt             # Pinned versions (if using pip)
├── pytest.ini                   # pytest configuration
├── Dockerfile                   # Container image for backend service
├── .gitignore                   # Excludes __pycache__, .env.local, venv/
└── README.md                    # Backend setup and deployment guide
```

**Architecture Diagram**:

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Browser                                │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  │ HTTP/REST
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│             Next.js 15 Frontend (Vercel)                         │
│  - React Server Components + Client boundaries                  │
│  - Mapbox GL JS, shadcn/ui, Tailwind CSS v4                    │
│  - Calls: POST /api/recommend, POST /api/track-click          │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  │ HTTP/REST JSON
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│      Python FastAPI Backend (Railway/Render/Self-Hosted)       │
│                                                                  │
│  POST /recommend                                                 │
│  ├─→ Intent Agent (LLM, claude-sonnet)                         │
│      ├─→ Neighborhood Agent (pure)                             │
│          ├─→ Retrieval Agent (RealEstateAPI.com)               │
│              ├─→ Scoring Engine (skill)                         │
│                  ├─→ Explanation Agent (LLM, claude-opus)      │
│                      └─→ Return { listings: [...], errors: [] }
│                                                                  │
│  State: PostgreSQL (LangGraph storage)                          │
│  Cache: Upstash Redis (6h TTL for API responses)               │
│  Traces: LangSmith (auto-emit from LangGraph)                  │
└─────────────────────────────────────────────────────────────────┘
                                  │
                                  │ External APIs
                                  ├─→ RealEstateAPI.com
                                  ├─→ Walk Score API
                                  ├─→ Google Places API
                                  └─→ Anthropic API
```

**Structure Decision**: Separate frontend (Next.js on Vercel) and backend (Python FastAPI on dedicated service) for clear separation of concerns. Frontend is thin (form submission, visualization). Backend orchestrates the 5-agent pipeline with full LangGraph integration. Communication via HTTP/JSON.

## Implementation Phases

Each phase ends when files are created, tests pass, and builds succeed. Manual smoke tests required for Phases 4, 5, 6 before declaring done.

### Phase 1: Backend Scaffold (Python)

**Deliverables**:
- `backend/pyproject.toml` or `backend/requirements.txt` with deps: fastapi, uvicorn, langgraph, anthropic, sqlalchemy, psycopg2-binary, pydantic, pytest
- `backend/.env.example` with all env vars
- `backend/app/main.py` initializing FastAPI app
- `backend/tests/` directory with pytest.ini
- `backend/Dockerfile` for containerization

**Verification**: `pip install -r requirements.txt`, `python -m pytest tests/ -v` passes, imports work.

### Phase 2: Backend Data Models and Clients

**Deliverables**:
- `backend/app/models/` with Pydantic models: Intent, NormalizedListing, NeighborhoodScore, ListingScore
- `backend/app/clients/anthropic.py` with Claude singletons
- `backend/app/clients/real_estate_api.py`, `walk_score.py`, `google_places.py` (timeout, retry, validation)
- `backend/app/db/engine.py` with SQLAlchemy connection singleton
- `backend/app/db/models.py` with clicks table schema

**Verification**: `python -c "from app.clients import anthropic; print(anthropic.claude_sonnet)"` works. Database connection established.

### Phase 3: Backend Agents and Skills

**Deliverables**:
- `backend/app/agents/intent.py` (LLM node, structured output)
- `backend/app/agents/neighborhood.py` (pure function)
- `backend/app/agents/retrieval.py` (API calls)
- `backend/app/agents/scoring.py` (skill function, 0–100 weighted formula)
- `backend/app/agents/explanation.py` (LLM node, structured output)
- Full pytest coverage for each agent
- Scoring formula documented at top of `scoring.py`

**Verification**: `pytest tests/unit/test_*_agent.py -v` passes. Each agent has ≥1 test. Scoring formula returns 0–100.

### Phase 4: Backend LangGraph and E2E Test

**Deliverables**:
- `backend/app/graph/state.py` defining LangGraph state (userQuery, intent, neighborhoodScores, listings, scored, explained, errors)
- `backend/app/graph/graph.py` compiling StateGraph with PostgreSQL saver in prod, MemorySaver in tests
- `backend/tests/integration/test_graph_e2e.py` testing full 5-agent pipeline with mocked clients
- E2E test asserts: parse → map → retrieve → score → explain returns 3 explained listings

**Verification**: `pytest tests/integration/test_graph_e2e.py -v` passes. E2E test runs in <10s with MemorySaver.

### Phase 5: Backend Routes and API

**Deliverables**:
- `backend/app/api/routes.py` with:
  - `POST /api/recommend` (body: userQuery, threadId; returns: SSE stream of updates or JSON)
  - `POST /api/track-click` (body: click data; Pydantic validation, inserts to DB)
  - `GET /api/health` (returns: {"status": "ok"})
- Error handling: all exceptions caught, returned in response JSON
- CORS middleware configured
- Rate-limiting via Upstash or simple in-memory counter for testing

**Verification**: `curl -X POST http://localhost:8000/api/recommend -H "Content-Type: application/json" -d '{"userQuery":"..."}' | jq .` returns valid JSON. `pytest tests/unit/test_routes.py -v` passes.

### Phase 6: Frontend Setup and API Integration

**Deliverables**:
- `src/types/api.ts` with Zod schemas for `/api/recommend` and `/api/track-click` requests/responses
- `src/lib/api-client.ts` HTTP client for calling backend (with error handling)
- `src/app/page.tsx` server component with layout
- `src/app/components/recommend-flow.tsx` (client component, form submission)
- `src/app/components/intent-card.tsx` (display parsed intent from backend)
- `src/app/components/neighborhood-map.tsx` (Mapbox with neighborhood data)
- `src/app/components/listings-grid.tsx` (streaming 3 ListingCards)
- `src/app/components/listing-card.tsx` (photo, address, price, score, explanation, affiliate link)
- `src/app/components/ftc-disclosure.tsx` (non-dismissible banner)
- Affiliate URL building in `src/lib/affiliate.ts`
- Motion stagger animations (max 200ms total)

**Verification**: `pnpm build` succeeds. Manual test: load http://localhost:3000, submit query, see streaming results from backend.

### Phase 7: Frontend Database Integration and Tracking

**Deliverables**:
- `src/app/api/track-click/route.ts` (POST handler calling backend `POST /api/track-click`)
- Clicks table populated in backend (verified via DB query)
- Click events tracked with source, timestamp, affiliateNetwork

**Verification**: Click a listing, verify row appears in Postgres clicks table.

### Phase 8: Frontend Observability

**Deliverables**:
- Sentry SDK initialized in `src/app/layout.tsx` (server-side errors)
- PostHog SDK initialized in `src/app/layout.tsx` (page views, `recommend_submitted` event)
- Manual verification: submit query, check PostHog for event, check Sentry for errors

**Verification**: `pnpm build` succeeds. Submit query on staging. Check PostHog dashboard for events.

### Phase 9: Backend Observability

**Deliverables**:
- LangSmith auto-enabled via LangGraph integration (no custom code)
- Sentry SDK in `backend/app/main.py` for Python errors
- `LANGSMITH_API_KEY`, `LANGSMITH_PROJECT`, `LANGSMITH_TRACING` configured in `.env.example`
- Manual verification: submit query via frontend, check LangSmith project for traces

**Verification**: LangSmith project dashboard shows traces. No unhandled exceptions in backend logs.

### Phase 10: Deployment

**Deliverables**:
- Backend deployed to Railway/Render/AWS (service URL in frontend env vars)
- All env vars set in both frontend and backend services
- LangGraph PostgreSQL checkpointer tables initialized
- Database migrations applied
- Frontend preview deploy on feature branch, prod deploy on main
- Smoke test: POST to backend `/api/recommend`, verify response

**Verification**: Frontend on Vercel calls backend service. Full pipeline returns 3 recommendations. LangSmith traces visible in prod project (housing-rec-prod).

### Phase 11: Pre-Launch Checklist

**Deliverables**:
- Verify (from `.github/EXECUTION.md` Part 12):
  - All env vars set and validated
  - Database migrations applied
  - LangSmith project created and traces flowing
  - Sentry errors reported (test with manual error trigger)
  - PostHog events captured
  - Affiliate link format validated
  - FTC disclosure present and non-dismissible
  - Rate-limiting working (if implemented)
  - Empty state renders when zero listings
  - Explanation failure gracefully degrades
  - Performance: end-to-end <10s, results streaming
  - Mobile responsive (DevTools check)
  - Cross-origin requests (CORS) working correctly

**Verification**: Checklist signed off. Manual QA pass. Ready for public launch.

---

## Next Steps

1. ✅ **Spec complete and clarified** (Session 2026-05-28)
2. ✅ **Plan created with hybrid split architecture** (Session 2026-05-29)
3. ⏭️ **Phase 0 Research**: Research Python FastAPI best practices, PostgreSQL checkpointing in LangGraph Python, deployment options
4. ⏭️ **Phase 1 Design**: Generate research.md, data-model.md, quickstart.md
5. ⏭️ **Task Generation**: Run `/speckit.tasks` to generate numbered, dependency-ordered tasks
6. ⏭️ **Consistency Analysis**: Run `/speckit.analyze` to cross-check spec, plan, and tasks
7. ⏭️ **Implementation**: Run `/speckit.implement` to execute phases with manual verification

---

**Plan Created**: 2026-05-29 | **Architecture**: Next.js Frontend + Python FastAPI Backend (Separate Services) | **Status**: Ready for Phase 0 Research

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

✅ **Code Principles Adapted for Split Stack**:
1. TypeScript strict in frontend, Python type hints in backend
2. Named exports throughout, no defaults
3. Zod for frontend boundaries, Pydantic for backend boundaries
4. Pure skills in backend (Scoring Engine), deterministic agents (Neighborhood)
5. LLM calls use structured output (withStructuredOutput in Python LangChain)
6. LLM instances as module-level singletons in backend
7. PostgreSQL state persistence in production, MemorySaver in tests
8. Style guide applied to all prose (comments, explanations, prompts)
9. Explicit environment variables in `.env.example` and docs
10. CI gates: frontend (`pnpm test`, typecheck, build), backend (`pytest`, type check via mypy)

✅ **Process Principles**: Linear Spec → Plan → Tasks → Implement. Tests prove completion. Errors via state, not exceptions. Manual verification required.





## Design Artifacts (to be generated)

The planning workflow (Phases 0–1) will generate:

1. **research.md** (Phase 0): Researches Python FastAPI patterns, SQLAlchemy with PostgreSQL, LangGraph Python state persistence, pytest best practices, containerization (Docker), Pydantic validation, external APIs (RealEstateAPI.com, Walk Score, Google Places).

2. **data-model.md** (Phase 1): Detailed entity definitions for both frontend and backend: Intent, NormalizedListing, NeighborhoodScore, ListingScore. Frontend uses Zod, backend uses Pydantic. State management in LangGraph (Python).

3. **quickstart.md** (Phase 1): Setup guide for both frontend and backend:
   - Frontend: `pnpm install`, `pnpm dev`, http://localhost:3000
   - Backend: `pip install -r requirements.txt`, `python -m uvicorn app.main:app --reload`, http://localhost:8000/docs

4. **contracts/** (Phase 1): API contracts between frontend and backend:
   - `POST /api/recommend` request/response schema
   - `POST /api/track-click` request/response schema
   - Error response schema

These artifacts support the task generation phase (Phase 2) and provide reference documentation during implementation (Phases 1–11).

---

## Next Steps

1. ✅ **Spec complete and clarified** (Session 2026-05-28)
2. ✅ **Plan created with hybrid split architecture** (Session 2026-05-29)
3. ⏭️ **Phase 0 Research**: Research Python FastAPI best practices, PostgreSQL checkpointing in LangGraph Python, deployment options
4. ⏭️ **Phase 1 Design**: Generate research.md, data-model.md, quickstart.md
5. ⏭️ **Task Generation**: Run `/speckit.tasks` to generate numbered, dependency-ordered tasks
6. ⏭️ **Consistency Analysis**: Run `/speckit.analyze` to cross-check spec, plan, and tasks
7. ⏭️ **Implementation**: Run `/speckit.implement` to execute phases with manual verification

---

**Plan Created**: 2026-05-29 | **Architecture**: Next.js Frontend + Python FastAPI Backend (Separate Services) | **Status**: Ready for Phase 0 Research
