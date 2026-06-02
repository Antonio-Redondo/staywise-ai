# Tasks: Housing Recommendation Engine

**Status**: Generated via `/speckit.tasks` | **Date**: 2026-05-29

**Feature Branch**: `001-housing-recommendations`

**Input**: 
- Feature Specification: [spec.md](spec.md)
- Implementation Plan: [plan.md](plan.md)
- Stack Lock-ins: [.github/instructions/project-context.instructions.md](../../instructions/project-context.instructions.md)

---

## Overview

**User Stories** (in priority order):
- **US1** (P1): Submit Query and View Recommendations — Core value proposition
- **US2** (P2): Refine Results Without Re-parsing — Iterative discovery
- **US3** (P3): Handle Empty or Degraded Results Gracefully — Resilience

**Scope**: Split-stack implementation (Next.js frontend on Vercel + Python FastAPI backend on dedicated service)

**Testing**: Unit tests for backend agents, E2E tests for full pipeline, manual smoke tests required

**Verification at Each Phase**: 
- Backend phases: `pytest tests/ -v` passes, agents tested in isolation, E2E test validates full pipeline
- Frontend phases: `pnpm test`, `pnpm typecheck`, `pnpm build` all pass, manual test in browser
- Deployment phase: Full end-to-end smoke test (frontend calls backend, returns 3 recommendations)

---

## Task Format

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **[P]**: Task can run in parallel (different files, no dependencies)
- **[Story]**: Belongs to user story (US1, US2, US3) or foundational (none)
- **File paths**: Exact locations for implementation

---

## Phase 1: Backend Setup

**Goal**: Initialize Python FastAPI project and dependencies

- [ ] T001 Create `backend/pyproject.toml` with dependencies (fastapi, uvicorn, langgraph, anthropic, sqlalchemy, psycopg2-binary, pydantic, pytest, python-dotenv)
- [ ] T002 [P] Create `backend/requirements.txt` (pinned versions for deployment)
- [ ] T003 [P] Create `backend/.env.example` with all environment variables (ANTHROPIC_API_KEY, DATABASE_URL, LANGSMITH_*, etc.)
- [ ] T004 [P] Create `backend/app/main.py` initializing FastAPI app with CORS middleware
- [ ] T005 [P] Create `backend/tests/` directory structure with `pytest.ini` configuration
- [ ] T006 [P] Create `backend/Dockerfile` for containerization (Python 3.10+, uvicorn entrypoint)

**Verification**: 
```bash
cd backend
pip install -r requirements.txt
python -m pytest tests/ -v
```

---

## Phase 2: Backend Data Models and API Clients

**Goal**: Define Pydantic models and external API clients with timeout/retry/validation

### Data Models

- [ ] T007 Create `backend/app/models/__init__.py` with `__all__` exports
- [ ] T008 [P] Create `backend/app/models/intent.py` — Pydantic Intent model (budgetMin, budgetMax, bedroomsMin, bedroomsMax, lifestyleTags, mustHaves, niceToHaves, commuteTarget)
- [ ] T009 [P] Create `backend/app/models/listing.py` — Pydantic NormalizedListing model (id, sourceUrl, address, price, bedrooms, bathrooms, squareFeet, photoUrl, source, listedDate, amenities)
- [ ] T010 [P] Create `backend/app/models/neighborhood.py` — Pydantic NeighborhoodScore model (name, score, medianPrice, walkScore)
- [ ] T011 [P] Create `backend/app/models/api.py` — Pydantic request/response schemas (RecommendRequest, RecommendResponse, TrackClickRequest)

### External API Clients

- [ ] T012 Create `backend/app/clients/__init__.py` with client exports
- [ ] T013 [P] Create `backend/app/clients/anthropic.py` — Anthropic SDK singletons for claude-sonnet and claude-opus
- [ ] T014 [P] Create `backend/app/clients/real_estate_api.py` — RealEstateAPI client with 5s timeout, 2 retries, exponential backoff, Pydantic validation
- [ ] T015 [P] Create `backend/app/clients/walk_score.py` — Walk Score API client (timeout, retry, cache-aware)
- [ ] T016 [P] Create `backend/app/clients/google_places.py` — Google Places API client (timeout, retry, Pydantic validation)

### Database Setup

- [ ] T017 Create `backend/app/db/__init__.py`
- [ ] T018 [P] Create `backend/app/db/engine.py` — SQLAlchemy engine singleton, connection pooling
- [ ] T019 [P] Create `backend/app/db/models.py` — SQLAlchemy table definitions (clicks table: id, source, timestamp, affiliateNetwork, listingId)

**Verification**: 
```bash
python -c "from app.clients.anthropic import claude_sonnet, claude_opus; print('Clients loaded')"
python -c "from app.db.engine import engine; print(engine)"
pytest tests/unit/test_models.py -v
```

---

## Phase 3: Backend Agents and Skills

**Goal**: Implement 5-agent pipeline with full test coverage

### Agents

- [ ] T020 Create `backend/app/agents/__init__.py` with agent exports
- [ ] T021 Create `backend/app/agents/intent.py` — Intent Agent (LLM node, claude-sonnet, temp 0.2, structured output via Pydantic)
- [ ] T022 [P] Create `backend/app/agents/neighborhood.py` — Neighborhood Agent (pure function, scores 0–1 based on tags/price/walk)
- [ ] T023 [P] Create `backend/app/agents/retrieval.py` — Retrieval Agent (fetches from RealEstateAPI for top 5 neighborhoods)
- [ ] T024 [P] Create `backend/app/agents/scoring.py` — Scoring Engine (pure function, 0–100 weighted: price 30%, size 20%, neighborhood 25%, amenities 15%, freshness 10%)
- [ ] T025 [P] Create `backend/app/agents/explanation.py` — Explanation Agent (LLM node, claude-opus, temp 0.4, structured output)

### Tests

- [ ] T026 Create `backend/tests/unit/test_intent_agent.py` — Test intent parsing with multiple query styles
- [ ] T027 [P] Create `backend/tests/unit/test_neighborhood_agent.py` — Test neighborhood scoring with fixtures
- [ ] T028 [P] Create `backend/tests/unit/test_retrieval_agent.py` — Test listing retrieval and normalization with mocked API
- [ ] T029 [P] Create `backend/tests/unit/test_scoring_engine.py` — Test scoring formula returns 0–100, verified formulas documented
- [ ] T030 [P] Create `backend/tests/unit/test_explanation_agent.py` — Test explanation generation

**Verification**: 
```bash
pytest tests/unit/test_*_agent.py -v
# Each test passes, coverage >= 80%
```

---

## Phase 4: Backend LangGraph State and Compilation

**Goal**: Define LangGraph state and compile the 5-agent pipeline with PostgreSQL persistence

- [ ] T031 Create `backend/app/graph/__init__.py`
- [ ] T032 Create `backend/app/graph/state.py` — LangGraph StateDict with fields: userQuery, threadId, intent, neighborhoodScores, listings, scored, explained, errors
- [ ] T033 Create `backend/app/graph/graph.py` — Compile StateGraph with all 5 nodes, PostgreSQL saver for prod, MemorySaver for tests
- [ ] T034 Create `backend/tests/integration/test_graph_e2e.py` — End-to-end test: submit query, verify parse → map → retrieve → score → explain outputs 3 listings with explanations, use MemorySaver and mocked clients

**Verification**: 
```bash
pytest tests/integration/test_graph_e2e.py -v
# E2E test passes in < 10s, asserts 3 explained listings returned
```

---

## Phase 5: Backend API Routes

**Goal**: Implement HTTP routes for recommendation and click tracking

- [ ] T035 Create `backend/app/api/__init__.py`
- [ ] T036 Create `backend/app/api/routes.py` with:
  - `POST /api/recommend` — Accepts RecommendRequest (userQuery, threadId), calls graph.stream, returns streaming updates or JSON array
  - `POST /api/track-click` — Accepts TrackClickRequest, inserts to clicks table, returns success response
  - `GET /api/health` — Returns {"status": "ok"}
- [ ] T037 Create error handling middleware (`backend/app/api/middleware.py`) — All exceptions caught, returned as JSON error responses
- [ ] T038 Add rate-limiting (Upstash or in-memory for tests) — 60 requests/hour/IP

**Verification**: 
```bash
pytest tests/unit/test_routes.py -v
# Routes start and respond correctly
curl -X GET http://localhost:8000/api/health | jq .
```

---

## Phase 6: Frontend Setup and API Integration

**Goal**: Initialize Next.js project and wire API client

### Frontend Setup

- [ ] T039 Create `package.json` with scripts (dev, build, start, test, lint, typecheck) and dependencies (next, react, typescript, tailwindcss, shadcn-ui, zod, etc.)
- [ ] T040 [P] Create `tsconfig.json` with strict mode, @/* alias
- [ ] T041 [P] Create `next.config.js` with Vercel deployment settings
- [ ] T042 [P] Create `.env.example` with NEXT_PUBLIC_API_URL, NEXT_PUBLIC_MAPBOX_TOKEN, NEXT_PUBLIC_SENTRY_DSN, etc.
- [ ] T043 [P] Create `.eslintrc.js` and `.prettierrc.json`
- [ ] T044 [P] Create `vitest.config.ts` with globals: true, coverage config
- [ ] T045 [P] Create `.gitignore` excluding .env.local, .next, node_modules, coverage

### API Client and Types

- [ ] T046 Create `src/types/api.ts` — Zod schemas for RecommendRequest, RecommendResponse, TrackClickRequest, ListingCard
- [ ] T047 [P] Create `src/lib/api-client.ts` — HTTP client for `/api/recommend` and `/api/track-click` calls to backend with error handling
- [ ] T048 [P] Create `src/lib/affiliate.ts` — Affiliate URL builder (Realtor.com Impact Radius, Apartments.com CJ Affiliate)

**Verification**: 
```bash
pnpm install
pnpm typecheck
pnpm build # Should succeed
```

---

## Phase 7: Frontend UI Components — User Story 1 (US1)

**Goal**: Implement UI for core recommendation flow

- [ ] T049 Create `src/app/layout.tsx` — Root layout with Sentry/PostHog initialization
- [ ] T050 Create `src/app/page.tsx` — Server component for recommend page with FTC disclosure banner
- [ ] T051 [P] Create `src/app/components/recommend-flow.tsx` — Client component wrapping form, calls `/api/recommend`, handles streaming updates
- [ ] T052 [P] Create `src/app/components/intent-card.tsx` — Display editable intent chips (budget, bedrooms, tags)
- [ ] T053 [P] Create `src/app/components/neighborhood-map.tsx` — Mapbox GL JS integration showing scored neighborhoods
- [ ] T054 [P] Create `src/app/components/listings-grid.tsx` — Streaming container for 3 ListingCards
- [ ] T055 [P] Create `src/app/components/listing-card.tsx` — Display photo, address, price, score (0–100), 2-sentence explanation, 1-sentence tradeoff, affiliate link
- [ ] T055a [P] Handle broken photoUrl in listing-card.tsx — Show placeholder image if URL is broken; continue rendering card without failing
- [ ] T056 [P] Create `src/app/components/ftc-disclosure.tsx` — Non-dismissible FTC compliance banner

### UI Tests

- [ ] T057 Create `tests/unit/components/test-recommend-flow.tsx` — Test form submission and API integration
- [ ] T058 [P] Create `tests/e2e/recommend.e2e.ts` — Playwright E2E test: submit query via UI, verify results display

**Verification**: 
```bash
pnpm test
pnpm typecheck
pnpm build
# Manual: Open http://localhost:3000, submit query, see 3 results
```

---

## Phase 8: Frontend UI Components — User Story 2 (US2)

**Goal**: Implement refinement chat interface

- [x] T059 Create `src/app/components/refine-chat.tsx` — Sticky chat surface for refinement messages (uses assistant-ui or custom implementation). MVP patterns: "cheaper", "more expensive", "more transit", "quieter", "bigger". Deferred: "closer to X", "good schools", ambiguous patterns
- [x] T060 Create `src/lib/thread-id.ts` — Generate/persist UUID in URL query parameter for session reuse
- [x] T061 Create test for refine-chat and thread ID persistence

**Verification**: 
```bash
pnpm test
# Manual: Submit query, refine with "show me cheaper", verify results change
```

---

## Phase 9: Frontend Error Handling — User Story 3 (US3)

**Goal**: Implement graceful degradation for empty/failed results

- [ ] T062 Create `src/app/components/empty-state.tsx` — Render when zero listings returned
- [ ] T063 Create `src/app/components/partial-listing-card.tsx` — Render listing with failed explanation (photo, address, price, score, no narrative)
- [ ] T064 Create `src/app/components/error-boundary.tsx` — Error boundary for graceful fallback
- [ ] T065 Update `recommend-flow.tsx` to catch and render errors from `/api/recommend`

### Tests

- [ ] T066 Create `tests/unit/test-error-states.tsx` — Test empty state, partial card, error boundary

**Verification**: 
```bash
pnpm test
# Manual: Mock API to return empty, verify empty state renders
```

---

## Phase 10: Frontend Database Integration

**Goal**: Track affiliate clicks

- [ ] T067 Create `src/app/api/track-click/route.ts` — POST handler calling backend `/api/track-click` and Realtor.com/Apartments.com affiliate pixels
- [ ] T068 Update `listing-card.tsx` to call track-click when affiliate link clicked
- [ ] T069 Create test for click tracking

**Verification**: 
```bash
# Manual: Click listing, verify click recorded in backend DB
```

---

## Phase 11: Frontend Observability

**Goal**: Wire Sentry and PostHog

- [ ] T070 Initialize Sentry SDK in `src/app/layout.tsx` for both server and client errors
- [ ] T071 Initialize PostHog SDK in `src/app/layout.tsx` for analytics
- [ ] T072 Emit `recommend_submitted` event to PostHog when user submits query
- [ ] T073 Create test verifying Sentry/PostHog initialized

**Verification**: 
```bash
# Manual: Submit query on staging, check PostHog for event, check Sentry for errors (if any)
```

---

## Phase 12: Backend Observability

**Goal**: Enable LangSmith tracing and Sentry error tracking

- [ ] T074 Configure LangSmith env vars in `.env.example` (LANGSMITH_API_KEY, LANGSMITH_PROJECT, LANGSMITH_TRACING)
- [ ] T075 Initialize Sentry SDK in `backend/app/main.py` for Python error tracking
- [ ] T076 Verify LangSmith auto-enabled via LangGraph integration (no custom code needed)
- [ ] T077 Create test submitting query via backend, verifying LangSmith trace appears

**Verification**: 
```bash
# Manual: Submit query via backend, check LangSmith project for traces
```

---

## Phase 13: Deployment

**Goal**: Deploy frontend to Vercel and backend to separate service

- [ ] T078 Deploy frontend to Vercel with all env vars (NEXT_PUBLIC_API_URL set to backend service URL, NEXT_PUBLIC_MAPBOX_TOKEN, etc.)
- [ ] T079 Deploy backend to Railway/Render/AWS with all env vars (DATABASE_URL, ANTHROPIC_API_KEY, LANGSMITH_*, etc.)
- [ ] T080 Initialize LangGraph PostgreSQL checkpointer tables on production database
- [ ] T081 Run database migrations on production Neon Postgres
- [ ] T082 Smoke test: POST to backend `/api/recommend` with test query, verify 3 recommendations returned
- [ ] T083 Smoke test: Call frontend on Vercel, submit query via UI, verify results display from backend

**Verification**: 
```bash
curl -X POST https://[backend-url]/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"userQuery":"3 bedroom house under 1M near BART"}' | jq .
# Opens frontend on Vercel, verifies results stream from backend
```

---

## Phase 14: Pre-Launch Checklist

**Goal**: Verify all systems operational and compliant

- [ ] T084 Verify all environment variables set and validated in both frontend and backend
- [ ] T085 Verify database migrations applied and schema correct
- [ ] T086 Verify LangSmith project created and traces flowing from production requests
- [ ] T087 Verify Sentry reporting errors from production
- [ ] T088 Verify PostHog tracking events
- [ ] T089 Verify affiliate link format correct (Impact Radius for Realtor.com, CJ Affiliate for Apartments.com)
- [ ] T090 Verify FTC disclosure present, visible, non-dismissible on every results page
- [ ] T091 Verify rate-limiting working (test with 61 requests/hour)
- [ ] T092 Verify empty state renders when zero listings returned
- [ ] T093 Verify explanation failure gracefully degrades (shows partial card)
- [ ] T094 Performance check: end-to-end latency < 10s on 4G connection
- [ ] T095 Mobile responsive check (DevTools)
- [ ] T096 CORS check: frontend can call backend from Vercel domain
- [ ] T096a Handle invalid/failed Mapbox GL JS token — Render fallback showing neighborhood list as text instead of visual map if load fails

**Verification**: All items in checklist signed off. Manual QA pass. Ready for public launch.

---

## Task Dependency Graph

```
Phase 1 (Setup)
├─→ Phase 2 (Models + Clients)
    ├─→ Phase 3 (Agents + Skills)
    │   ├─→ Phase 4 (LangGraph + E2E)
    │   │   └─→ Phase 5 (API Routes)
    │   │       └─→ Phase 6 (Frontend Setup)
    │   │           ├─→ Phase 7 (UI — US1)
    │   │           ├─→ Phase 8 (UI — US2)
    │   │           └─→ Phase 9 (Error Handling — US3)
    │   │               ├─→ Phase 10 (Database)
    │   │               ├─→ Phase 11 (Frontend Observability)
    │   │               └─→ Phase 12 (Backend Observability)
    │   │                   └─→ Phase 13 (Deployment)
    │   │                       └─→ Phase 14 (Pre-Launch)
    │   │
    │   └─→ Phase 12 (Backend Observability) [parallel after Phase 5]
```

## Parallel Execution Opportunities

**After Phase 2 (Models complete)**:
- T008–T030 (all agent definitions) can run in parallel

**After Phase 5 (Backend Routes complete)**:
- T039–T077 (all frontend work) can run in parallel with Phase 12 (Backend Observability)

**After Phase 9 (Error Handling complete)**:
- T062–T096 (remaining frontend and deployment) can proceed without blocking

---

## MVP Scope (Recommended)

**To ship minimum viable product, complete Phases 1–7**:
- ✅ Backend scaffold, models, agents (Phases 1–4)
- ✅ API routes (Phase 5)
- ✅ Frontend setup, API client (Phase 6)
- ✅ UI for core recommendation flow (Phase 7) — **Delivers US1 (P1)**
- ⏸️ Defer US2 (refinement), US3 (error handling), observability, deployment details

**Estimated effort to MVP**: ~40–50 hours of focused implementation

**To production launch, complete all phases 1–14**: ~80–100 hours

---

## Quality Gates

Each phase must pass:

1. **Backend phases**: `pytest tests/ -v` (≥80% coverage)
2. **Frontend phases**: `pnpm test`, `pnpm typecheck`, `pnpm build` all pass
3. **Integration**: Manual smoke test (backend and frontend working together)
4. **Deployment**: All env vars validated, migrations applied, traces flowing

If any gate fails, the phase is not done. Do not proceed to the next phase.

---

**Total Task Count**: 96 tasks across 14 phases

**Status**: ✅ Generated and ready for `/speckit.implement`
