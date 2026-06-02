---
applyTo: "**"
---

# Project context

A housing recommendation app. Users describe what they want in natural language; the app returns three matched listings with explanations and affiliate links to the source listing site.

Update this file every quarter.

## Yearly target

- Hard number: 500 qualified affiliate clicks per week and $5,000+ in monthly affiliate revenue
- Deadline: December 31, 2026

A "qualified" click is one where the user lands on the partner site and stays for at least 30 seconds, tracked through the affiliate network's pixel.

## This quarter's single focus

Public launch in one metro area (San Francisco Bay Area) with RealEstateAPI.com as the sole listings source. End-of-quarter goal: 50 qualified affiliate clicks per week and the full pipeline running in production with LangSmith traces on every request.

## What we say no to

- Multi-city scope until the first metro hits target.
- Pure chat as the entry point. The flow is recommendation-first; chat is a refinement surface only.
- User accounts beyond email capture in v1.
- Native mobile apps. Web responsive only.
- Custom MLS broker partnerships. Use aggregator APIs.
- Second LLM provider as fallback in v1.

## Stack lock-ins

These do not change without an explicit decision and an updated entry in this file.

### Frontend (Next.js on Vercel)
- TypeScript 5+, strict mode
- Node 22 LTS
- Package manager: pnpm
- Next.js 15 (App Router)
- React Server Components by default
- shadcn/ui components owned in `src/components/ui/`
- Tailwind CSS v4
- Motion (formerly Framer Motion) for animations
- Lucide for icons
- Sonner for toasts
- next-themes for theming
- Mapbox GL JS for neighborhood overlays and listing pins
- Recharts via shadcn/ui charts for score breakdowns
- React Hook Form with Zod resolver
- Zod schemas in `src/types/` for API request/response validation

### Backend (Python + FastAPI)
- Python 3.10+
- FastAPI for HTTP API server
- Uvicorn as ASGI application server
- Package manager: pip or UV
- langchain and langgraph (Python versions) for agent orchestration
- anthropic SDK (Python) for LLM calls
- Pydantic for request/response validation (not Zod)
- SQLAlchemy for ORM
- Neon Postgres for state persistence and agent history
- psycopg2-binary for database driver
- Python unittest/pytest for testing
- deployment: separate service (Railway, Render, AWS, or self-hosted)

### Agent Layer (Python Backend)
- 5-agent pipeline via LangGraph (Python):
  1. Intent Agent (LLM node, claude-sonnet-4-6, temperature 0.2)
  2. Neighborhood Agent (pure deterministic function)
  3. Retrieval Agent (API calls to RealEstateAPI.com)
  4. Scoring Engine (deterministic skill, weights: price 30%, size 20%, neighborhood 25%, amenities 15%, freshness 10%)
  5. Explanation Agent (LLM node, claude-opus-4-7, temperature 0.4)
- LangGraph state persists to PostgreSQL via SQLAlchemy
- MemorySaver only in local tests

### LLM Models
- `claude-sonnet-4-6` for Intent Agent (temperature 0.2)
- `claude-opus-4-7` for Explanation Agent (temperature 0.4)
- Never exceed temperature 0.7
- Override the default model only with a written reason in the PR

### Observability
- LangSmith for LLM traces (env-var driven, auto-emit from LangGraph)
- Sentry for application errors (server-side Python)
- PostHog for product analytics (frontend only)

### Database and Cache
- Neon Postgres for primary data and LangGraph state persistence
- pgvector for any embedding-based search (optional)
- Upstash Redis for API response caching (6-hour TTL)
- Upstash Ratelimit for per-IP rate limiting (60 requests/hour)

### External APIs
- RealEstateAPI.com for listings (primary source, SF Bay Area)
- Walk Score API for walkability scoring (cached in Redis)
- Google Places API for amenities data
- Realtor.com affiliate links via Impact Radius
- Apartments.com affiliate links via CJ Affiliate

### Deployment
- Frontend: Vercel (Next.js)
- Backend: Separate service (Railway, Render, AWS, or self-hosted)
- Frontend calls Backend via HTTP (`POST /recommend`, `POST /track-click`)
- GitHub Actions for CI on both frontend and backend
- Preview deployments of frontend on every PR

### Testing
- Frontend: Vitest for unit tests, Playwright for E2E
- Backend: pytest for unit and integration tests
- LangSmith disabled in tests (`LANGSMITH_TRACING=false`)

## Listings data sources

- Primary: RealEstateAPI.com (developer-focused, transparent pricing, normalization built in, good Bay Area coverage)
- Secondary: None in v1. Add ATTOM Data once monthly revenue clears the cost of the higher tier.
- Location enrichment: Walk Score API for walkability and transit, Google Places API for amenities and points of interest
- Cache TTL: 6 hours for sale listings, 1 hour for rentals

## Affiliate partners and link format

Affiliate links route users to the source listing site, not back to RealEstateAPI.com.

- Realtor.com via Impact Radius: append `?ref=${REALTOR_AFFILIATE_ID}` to the source URL
- Apartments.com via CJ Affiliate: append `?cm_mmc=affiliate-${APARTMENTS_AFFILIATE_ID}` for rental listings
- Zillow listings: no affiliate program available; link out without affiliate parameters and do not count toward the qualified-click target
- Fallback: when no affiliate match exists for the source domain, generate a `View listing` link with no affiliate parameters and skip the click-track event

Disclosure requirement: every page that displays affiliate links shows an FTC-compliant disclosure above the fold, including the line "This site contains affiliate links. We may earn a commission if you click through and complete a transaction at no cost to you."

## Environment variables

The app expects these at runtime. Copilot should not invent new ones without asking.

- `ANTHROPIC_API_KEY`
- `LANGSMITH_API_KEY`
- `LANGSMITH_PROJECT` (set to `housing-rec-prod` in production, `housing-rec-dev` locally)
- `LANGSMITH_TRACING` (`true` in prod and dev, `false` in tests)
- `DATABASE_URL` (Neon Postgres, also used by the LangGraph checkpointer)
- `UPSTASH_REDIS_REST_URL`
- `UPSTASH_REDIS_REST_TOKEN`
- `NEXT_PUBLIC_MAPBOX_TOKEN`
- `REAL_ESTATE_API_KEY`
- `WALK_SCORE_API_KEY`
- `GOOGLE_PLACES_API_KEY`
- `REALTOR_AFFILIATE_ID`
- `APARTMENTS_AFFILIATE_ID`
- `SENTRY_DSN` (server) and `NEXT_PUBLIC_SENTRY_DSN` (client)
- `POSTHOG_KEY` and `NEXT_PUBLIC_POSTHOG_KEY`

## Out of scope this quarter

Anything in this list, Copilot must refuse to scaffold without me confirming first:

- User authentication and accounts
- Saved searches and email alerts
- Native mobile clients
- White-label tenancy
- A second LLM provider as fallback
- Self-hosted LangGraph Platform
- Vector search over listing descriptions
- Custom MLS data partnerships
- Multi-language support
