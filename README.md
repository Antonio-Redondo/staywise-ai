# StayWiseAI

AI-powered housing recommendations. Describe the home you want in natural language; the
app parses your intent, scores neighborhoods, retrieves listings, ranks them, and explains
each match.

It's a two-part app:

| Part | Stack | Dev URL | Port |
|---|---|---|---|
| **Frontend** | Next.js 15 · React 18 · TypeScript | http://localhost:3000 | 3000 |
| **Backend** | FastAPI · 5-stage LangGraph pipeline · Python 3.11 | http://127.0.0.1:8000 | 8000 |

The frontend calls the backend at `http://localhost:8000` by default.

---

## ✅ What you need to run it

**Required tools** (must be installed first):

- **Python 3.11+** — for the backend
- **Node.js 18.18+** (20 LTS recommended) — for the frontend
- **pnpm** — the frontend's package manager (lockfile is `pnpm-lock.yaml`). The easiest way to
  get it is Corepack, which ships with Node: run `corepack enable` once.

**API keys / accounts:** **None required.** The app runs fully in **demo mode** out of the box —
the backend returns a built-in catalog of sample listings and the LLM agents fall back to
fast heuristics. You only need keys if you want live data (see [Configuration](#configuration)).

That's it. Two terminals, no database, no cloud accounts needed for a working local app.

---

## 🚀 Quick start

Open **two terminals**. Commands below are PowerShell (Windows); for macOS/Linux see the note
under each step.

### Terminal 1 — backend (port 8000)

```powershell
cd backend
python -m venv .venv                                  # first time only
.\.venv\Scripts\python.exe -m pip install -r requirements.txt   # first time only
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

> **macOS/Linux:** `python3 -m venv .venv` · `source .venv/bin/activate` · `pip install -r requirements.txt` · `uvicorn app.main:app --reload --port 8000`

### Terminal 2 — frontend (port 3000)

```powershell
cd frontend
corepack enable          # first time only — makes `pnpm` available
pnpm install             # first time only
pnpm dev
```

Then open **http://localhost:3000**, type something like
*"2 bed, walkable, near BART, under $4000"*, and click **Find recommendations**.

> The **first** `pnpm dev` is slower: Next.js compiles and, if needed, installs `@types/node`.

---

## 🔍 Verify it's working

```bash
# backend health
curl http://127.0.0.1:8000/health            # -> {"status":"ok"}

# full recommendation pipeline (returns 12 demo listings)
curl -X POST http://127.0.0.1:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"userQuery":"2 bed walkable near BART under $4000"}'
```

Interactive API docs (Swagger): **http://127.0.0.1:8000/docs**

---

## Configuration

> **Important:** the backend reads configuration **only from environment variables in the
> process** (`os.getenv`). It does **not** auto-load `.env` / `.env.local` files. The
> `*.env.example` files are templates — to apply a value you must export it in the shell
> **before** starting `uvicorn` (or wire up a loader yourself).

Everything below is **optional**. Leave it unset to stay in demo mode.

### Backend environment variables

| Variable | Needed for | If unset (demo mode) |
|---|---|---|
| `REAL_ESTATE_API_KEY` + `REAL_ESTATE_API_URL` | Live listings | Returns the built-in sample catalog |
| `ANTHROPIC_API_KEY` | LLM intent + explanations | Uses heuristic fallbacks |
| `DATABASE_URL` (Postgres) | `POST /api/track-click` click logging | `/api/recommend` works; `track-click` returns 500 |
| `WALK_SCORE_API_KEY`, `GOOGLE_PLACES_API_KEY` | Enrichment | Skipped |
| `LANGSMITH_*`, `SENTRY_DSN` | Tracing / error reporting | Best-effort; safely skipped |

Example — enabling a real listings provider in PowerShell:

```powershell
$env:REAL_ESTATE_API_KEY = "your-key"
$env:REAL_ESTATE_API_URL = "https://api.your-provider.com"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

See [`backend/.env.example`](backend/.env.example) for the full list.

### Frontend environment variables

Optional. Defaults work for local dev. To override, create `frontend/.env.local`
(Next.js **does** load this automatically):

| Variable | Default | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Backend base URL |

See [`frontend/.env.example`](frontend/.env.example) for optional Mapbox / analytics / affiliate keys.

---

## 🧪 Tests

```powershell
# backend (from backend/, venv active)
.\.venv\Scripts\python.exe -m pytest

# frontend unit tests (from frontend/)
pnpm test            # vitest

# frontend end-to-end (from frontend/)
pnpm e2e             # playwright
```

---

## 📁 Project structure

```
StayWiseAI/
├── backend/                    # FastAPI + LangGraph pipeline
│   └── app/
│       ├── main.py             # FastAPI app, CORS, rate limiter
│       ├── api/routes.py       # /api/recommend, /api/track-click, /api/health
│       ├── agents/             # intent → neighborhood → retrieval → scoring → explanation
│       ├── graph/              # pipeline orchestration + state
│       ├── clients/            # external API wrappers (incl. demo-mode listings)
│       ├── models/             # Pydantic models
│       └── db/                 # SQLAlchemy engine + models
├── frontend/                   # Next.js app
│   └── src/
│       ├── app/                # pages, layout, components, styles (globals.css)
│       └── lib/                # api-client, affiliate, thread-id helpers
└── .github/                    # Copilot / Spec Kit build configuration (see below)
```

---

## How the pipeline works

`POST /api/recommend` runs five stages:

1. **Intent** — parse budget, bedrooms, and lifestyle tags from the query
2. **Neighborhood** — score candidate neighborhoods
3. **Retrieval** — fetch + normalize listings (demo catalog when no API key)
4. **Scoring** — rank each listing (price, size, neighborhood, amenities, freshness)
5. **Explanation** — generate a short "why this matches" note per listing

---

## 🛠 Troubleshooting

| Symptom | Cause / fix |
|---|---|
| **"Failed to fetch"** in the browser | Backend isn't running, or it's on a different port. Confirm `curl http://127.0.0.1:8000/health` returns 200 and that the frontend's `NEXT_PUBLIC_API_URL` matches. |
| Recommend returns `getaddrinfo failed` | You set `REAL_ESTATE_API_KEY` but `REAL_ESTATE_API_URL` is missing/unreachable. Unset the key to return to demo mode, or fix the URL. |
| `track-click` returns 500 | Expected without a Postgres `DATABASE_URL`. The recommendation flow is unaffected. |
| `pnpm: command not found` | Run `corepack enable` (ships with Node 16.9+). |
| Port already in use | Change the port: backend `--port 8001`; frontend `pnpm dev -- -p 3001` (then set `NEXT_PUBLIC_API_URL` accordingly). |
| Listing photos don't load | The demo cards use remote example images and need internet. An inline placeholder is shown if a photo fails. |

---

## About `.github/`

The [`.github/`](.github/) folder holds the Copilot / GitHub Spec Kit configuration used to
**build** this project (instructions, prompts, slash commands, architecture docs). It is not
needed to run the app. Start with [`.github/README.md`](.github/README.md) and
[`.github/ARCHITECTURE.md`](.github/ARCHITECTURE.md) if you want to extend the system that way.
