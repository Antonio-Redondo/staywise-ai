# Copilot global instructions

You are working inside this repo, a housing recommendation app built with a Next.js frontend (Vercel) and Python FastAPI backend (separate service) orchestrating a 5-agent LangGraph pipeline.

## Architecture in one paragraph

A Next.js 15 frontend on Vercel collects user intent via textarea and calls a separate Python FastAPI backend service via HTTP. The backend runs a 5-agent LangGraph pipeline: Intent Agent (LLM, claude-sonnet) parses the query, Neighborhood Agent (pure function) scores neighborhoods, Retrieval Agent fetches listings from RealEstateAPI, Scoring Engine (skill) ranks them with a weighted formula, and Explanation Agent (LLM, claude-opus) writes personations explanations. Results stream back as JSON. State persists in Neon Postgres, LangGraph state checkpointing via SQLAlchemy, API responses cached in Upstash Redis (6h TTL). Observability via LangSmith (backend traces), Sentry (errors), PostHog (frontend analytics).

## Load order

Before any task, load context from these files in order:

1. `.github/instructions/about-me.instructions.md`
2. `.github/instructions/project-context.instructions.md` (now includes Python backend stack)
3. `.github/instructions/style-guide.instructions.md`
4. `.github/instructions/langgraph.instructions.md` when editing anything under backend Python agent code
5. `.github/instructions/ui.instructions.md` when editing anything under frontend `src/app/` or `src/components/`
6. `.github/instructions/db.instructions.md` when editing database-related code (frontend or backend)

## Source layout

### Frontend (Next.js on Vercel)

- `src/app/` for Next.js App Router pages and route handlers
- `src/components/` for React components on shadcn/ui
- `src/types/` for Zod schemas (API request/response validation)
- `src/lib/` for utilities and API client
- `src/styles/` for Tailwind globals

### Backend (Python FastAPI)

- `backend/app/agents/` for LLM and pure function agents
- `backend/app/graph/` for LangGraph state and compiled graph
- `backend/app/models/` for Pydantic models
- `backend/app/clients/` for external API wrappers (anthropic, real-estate-api, walk-score, google-places)
- `backend/app/db/` for database models and connection
- `backend/app/api/` for FastAPI routes
- `backend/tests/` mirrors structure for pytest coverage

## Routing rules

- Read every instructions file whose scope matches your task before generating.
- Never modify files in `dist/`, `build/`, `.next/`, `node_modules/`, `coverage/`, `__pycache__`, `.venv/`, or any `outputs/` directory unless I name a specific file.
- Save new deliverables under the directory matching their concern. Do not invent new top-level folders.
- If a request is ambiguous, ask exactly one clarifying question, then proceed.
- Apply the style guide to all generated prose, code comments, commit messages, and PR descriptions.

## Defaults when not specified

### Frontend
- Language: TypeScript with strict mode.
- Package manager: pnpm.
- Test runner: Vitest, one assertion per test where reasonable.
- Lint and format: ESLint plus Prettier using the project config.
- Module style: named exports only.
- Validation: Zod at every external boundary (API request/response).
- UI: shadcn/ui owned in src/components/ui/. Tailwind CSS v4 utility classes inline.

### Backend
- Language: Python 3.10+.
- Package manager: pip or UV.
- Test runner: pytest, concise assertions.
- Agent framework: LangGraph (Python), Anthropic SDK (Python).
- LLM: claude-sonnet-4-6 for Intent Agent (temp 0.2), claude-opus-4-7 for Explanation Agent (temp 0.4).
- Validation: Pydantic at every boundary (HTTP request/response, LLM output, env vars, API responses).
- Database: SQLAlchemy ORM with Postgres.
- State: LangGraph PostgreSQL checkpointer in production, MemorySaver in tests.

## Output expectations

- Show diffs, not full files, when editing.
- Cite the file path and line range you changed.
- After any non-trivial generation, run a self-audit against the style guide and fix hits before returning.
- For backend code, confirm pytest can run. For frontend code, confirm pnpm can build and test.

## When uncertain

Ask. Do not guess at file paths, library versions, environment variables, API contracts, or partner affiliate codes.

<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
implementation phases, and design approach, read the current plan:
[.specify/specs/001-housing-recommendations/plan.md](.specify/specs/001-housing-recommendations/plan.md)
<!-- SPECKIT END -->
