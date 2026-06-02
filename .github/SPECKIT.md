# Building with GitHub Spec Kit

Spec Kit is GitHub's open-source spec-driven development toolkit. Instead of pasting individual build prompts in order, you describe the system once at three increasing levels of detail (constitution, spec, plan), let Spec Kit generate a task list, then run the implementation.

This file walks you through using Spec Kit with everything else in `.github/`.

## How it fits with the existing configuration

Spec Kit and the `instructions/` files in this repo work together:

- **Spec Kit** drives the build at a high level: spec → plan → tasks → implement.
- **The `instructions/` files** give Copilot the style rules, code patterns, and project context it needs during implementation.

The same Copilot Chat session uses both. Spec Kit tells Copilot what to build next; the instructions tell it how to build it.

`EXECUTION.md` and `PROMPTS.md` remain useful as references. Spec Kit replaces the "paste this prompt, then this one" loop, not the underlying knowledge of what needs building.

## Important caveat

Spec Kit sometimes reports a task complete when generated code is missing, stubbed, or untested. The known failure mode is that the spec and plan read clean but the implementation is incomplete. Treat `/speckit.implement` as a starting point, not a finished feature.

After every implementation pass:

1. Run `pnpm test`
2. Run `pnpm typecheck`
3. Run `pnpm build`
4. Smoke test the behavior manually
5. Open the generated files and read them; Spec Kit's "done" claim is unreliable

## Install

You need `uv`, the Python package runner, first.

```bash
# macOS
brew install uv

# Linux / Windows
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then initialize Spec Kit in your existing repo:

```bash
cd housing-rec
uvx --from git+https://github.com/github/spec-kit.git specify init . --integration copilot
```

This adds two things without touching your existing files:

- `.specify/` — constitution, scripts, and templates that Spec Kit owns
- `.github/prompts/speckit.*.prompt.md` — the slash commands you invoke in Copilot Chat

Your existing `.github/instructions/`, `.github/copilot-instructions.md`, and your other `.github/prompts/*.prompt.md` files (refine, audit, new-node, new-skill) stay exactly as they are. Spec Kit's prompts use names like `speckit.specify.prompt.md` so there are no collisions.

Verify with:

```bash
uvx --from git+https://github.com/github/spec-kit.git specify check
```

## The workflow

In Copilot Chat, run these slash commands in order. Wait for each to complete and verify the output before moving on.

```
1. /speckit.constitution   set the project principles
2. /speckit.specify        describe what to build
3. /speckit.clarify        answer Spec Kit's clarifying questions
4. /speckit.plan           describe how to build it
5. /speckit.tasks          generate the task list
6. /speckit.checklist      generate a quality checklist (optional)
7. /speckit.analyze        cross-check spec, plan, tasks for consistency
8. /speckit.implement      execute the tasks (this writes code)
```

Below are the exact prompts to paste at each step.

## Step 1 — `/speckit.constitution`

Spec Kit's constitution is the project's rulebook. Paste this in Copilot Chat:

```
Create the project constitution for a housing recommendation app. Treat .github/instructions/style-guide.instructions.md and .github/instructions/project-context.instructions.md as authoritative; reference them rather than restating their contents.

Code principles:
1. TypeScript strict mode. No `any` in committed code without an inline comment explaining why.
2. Named exports only. No default exports.
3. Zod schemas are the single source of truth for every external boundary: LLM responses, route handler inputs, environment variables, third-party API responses.
4. Pure deterministic logic lives in src/skills/. LangGraph nodes orchestrate but contain no business logic that could be a pure function.
5. Every LLM call uses withStructuredOutput bound to a Zod schema. No free-form text parsing.
6. Model instances are module-level singletons. Never instantiate inside a node body or loop.
7. Production LangGraph runs use PostgresSaver. MemorySaver is for tests only.
8. Apply the style guide in .github/instructions/style-guide.instructions.md to all prose, code comments, commit messages, and user-facing copy.
9. No new env vars without adding them to .env.example and to project-context.instructions.md in the same PR.
10. Every PR must pass pnpm test, pnpm lint, pnpm typecheck, and pnpm build before merging.

Process principles:
- Spec → Plan → Tasks → Implement, in that order. Skipping phases is not allowed.
- A task is not done until tests pass and the verification step passes.
- If implementation reveals the spec is wrong, update the spec before continuing the implementation.
- LangGraph nodes return errors via state, not exceptions.
- After every /speckit.implement run, manually verify with pnpm test, pnpm typecheck, pnpm build, and a smoke test before declaring the task complete.

Cite the existing instruction files (style-guide, project-context, langgraph, ui, db) as binding for their respective scopes.
```

**Verify:** `.specify/memory/constitution.md` exists and reflects the principles above.

## Step 2 — `/speckit.specify`

The spec describes WHAT to build, not HOW. Paste this:

```
Build a housing recommendation web app. A user submits a natural language description of what they want in a home. The app returns three matched listings, each with an explanation, named tradeoffs, and an affiliate link to the source listing site.

User flow:

1. User lands on the recommend page. Hero textarea with placeholder "Tell me what you're looking for in your next home."
2. User submits a free-text query.
3. App streams parsed intent back as editable chips (budget range, bedroom range, lifestyle tags, must-haves, nice-to-haves).
4. App lights up an interactive map showing scored neighborhoods.
5. App streams three listing cards in score order. Each card shows photo, address, price, score, two-sentence why-it-fits, one-sentence tradeoff, primary CTA labeled "View on {sourceDomain}" linking through an affiliate URL, and a small "Affiliate link" tag.
6. A sticky chat surface at the bottom lets the user refine ("show me cheaper", "more transit") without restating the original intent. Refinements reuse prior state through a thread ID.

System behavior:

- Intent extraction: parse free text into structured Intent (budget range, bedrooms range, lifestyle tags, must-haves, nice-to-haves, optional commute target).
- Neighborhood matching: score each neighborhood in the catalog 0 to 1 based on tag overlap with lifestyle tags, price band fit between budget and median price, walk/transit fit.
- Listings retrieval: fetch listings from the partnered API for the top 5 neighborhoods by score. Normalize across sources. Dedupe by source URL. Cap at 50 results.
- Scoring: weighted score 0 to 100 per listing using intent and neighborhood scores. Components: price 30%, size 20%, neighborhood 25%, amenities 15%, freshness 10%.
- Explanation: for the top 3 scored listings, write a why-it-fits (max two sentences) and a tradeoffs line (one sentence). Apply the style guide.
- Affiliate URLs: build server-side using the partner code for the source domain. Realtor.com gets the Impact Radius partner code; Apartments.com gets the CJ Affiliate code; others fall back to the raw source URL.
- Disclosure: every page that displays affiliate links shows an FTC-compliant disclosure above the fold.

Success criteria:

- A user submits a query and sees three explained recommendations within 10 seconds on a normal connection.
- Affiliate links route correctly to the partner site with the tracking parameters appended.
- Refinement reuses prior intent without re-parsing from scratch.
- The pipeline emits a trace to LangSmith on every request.
- Each pipeline stage either completes successfully or returns an error in state that the UI can render.
- pnpm test passes with full coverage on the three core skills (listing normalizer, scoring engine, neighborhood mapper).

Out of scope for v1:
- User accounts beyond email capture
- Saved searches and email alerts
- Multi-metro support
- Native mobile apps
- A second LLM provider as fallback

Constraints from project-context.instructions.md: launch metro is the San Francisco Bay Area, primary listings source is RealEstateAPI.com, affiliate partners are Realtor.com via Impact Radius and Apartments.com via CJ Affiliate.
```

**Verify:** A spec markdown file lands in `.specify/specs/` (path depends on Spec Kit version). Read it. The "what" and "why" should be clear; the "how" should be absent or thin.

## Step 3 — `/speckit.clarify`

Spec Kit reads the spec and asks targeted clarifying questions. Answer each one. Common ones for this project:

- What happens if RealEstateAPI returns zero listings for the matched neighborhoods? → Show an empty state with a "broaden criteria" suggestion.
- How is the FTC disclosure styled? → A non-dismissible banner with subtle background, the exact wording is in project-context.instructions.md.
- What's the rate limit per user? → 60 requests per hour per IP via Upstash Ratelimit.
- How is the thread ID generated? → A UUID created client-side on the first submit, stored in the URL as a query param.
- What's the failure UI when an explanation fails for one of three listings? → Show the listing with a "why this fits" placeholder and the score, but no narrative.

Answer Spec Kit's actual questions, not these. The list above is just what typically comes up.

## Step 4 — `/speckit.plan`

The plan describes HOW to build it. Paste this:

```
Implement the system using the stack locked in by .github/instructions/project-context.instructions.md:

- TypeScript 5+, Node 22 LTS, pnpm
- Next.js 15 App Router on Vercel
- LangGraph (@langchain/langgraph) with @langchain/langgraph-checkpoint-postgres for production state
- @langchain/anthropic: claude-sonnet-4-6 for parse-intent (temperature 0.2), claude-opus-4-7 for explain-top (temperature 0.4)
- Neon Postgres with pgvector, Drizzle ORM
- Upstash Redis for caching and Upstash Ratelimit for per-IP limiting
- Mapbox GL JS for the neighborhood map
- shadcn/ui owned in src/components/ui/, Tailwind CSS v4
- Vercel AI SDK 5 (experimental_useObject) for streaming graph updates to the browser
- assistant-ui with the LangGraph adapter for the refine chat
- LangSmith for LLM observability, Sentry for app errors, PostHog for product analytics

Architecture:

A LangGraph StateGraph chains six nodes:
START → parse-intent (LLM) → map-neighborhoods (pure) → fetch-listings (hybrid) → score-listings (pure) → explain-top (LLM) → END

Three deterministic skills back the nodes:
1. normalize-listing — turns any source's raw listing JSON into the unified NormalizedListing shape; returns null on bad input.
2. score-listing — weighted scoring with documented per-component formulas at the top of the file.
3. map-neighborhoods — scores neighborhoods 0 to 1 from tag overlap, price band fit, walk/transit fit.

State (LangGraph Annotation.Root) with explicit reducers:
- userQuery (last-wins)
- intent (last-wins)
- neighborhoodScores (last-wins)
- listings (concat with dedupe by sourceUrl)
- scored (last-wins)
- explained (last-wins)
- errors (concat)

File layout follows the Source layout section of .github/copilot-instructions.md exactly. Do not invent new top-level folders.

Implementation phases (each phase ends green before the next begins):

Phase 1 — Scaffold the TypeScript project per copilot-instructions.md layout. Generate package.json scripts (dev, build, start, test, lint, typecheck), tsconfig.json (strict, @/* alias), ESLint, Prettier, Vitest config, .gitignore, and .env.example listing every env var from project-context.instructions.md.

Phase 2 — Build the three deterministic skills with full Vitest coverage. Inline fixtures, no shared setup.

Phase 3 — Build the LangGraph state annotation. Build four typed external clients (anthropic, real-estate-api, walk-score, google-places), each with 5-second timeouts via AbortController, two retries with exponential backoff on rate-limit errors, Zod validation on every response.

Phase 4 — Build the five graph nodes per the patterns in langgraph.instructions.md. Every node returns Partial<GraphState>. LLM nodes use module-level model singletons and withStructuredOutput with a Zod schema. Failures return errors via state, never throw.

Phase 5 — Compile the graph with PostgresSaver. Write an end-to-end test using MemorySaver with all clients mocked, asserting exactly three explained results.

Phase 6 — Build the POST /api/recommend route handler. Validate body with Zod, apply Upstash Ratelimit (60/hour/IP), call graph.stream with streamMode 'updates', pipe each update through createDataStreamResponse from the Vercel AI SDK. Runtime nodejs, maxDuration 60.

Phase 7 — Build the UI per ui.instructions.md. Server-component page wrapping a client RecommendFlow that uses experimental_useObject. Components: IntentCard, NeighborhoodMap (Mapbox GL JS), ListingsGrid streaming three ListingCards, RefineChat using assistant-ui's LangGraph adapter, FtcDisclosure banner. Use shadcn/ui Card, Badge, Button, Textarea. Stagger card entry with Motion (max 200ms total).

Phase 8 — Database setup. Drizzle schema for the clicks table per db.instructions.md. POST /api/track-click route handler. Initial migration applied to Neon.

Phase 9 — Observability. Wire Sentry for both server and client. Wire PostHog for page views and the recommend_submitted event. Confirm LangSmith traces appear.

Phase 10 — Deploy to Vercel. Add every env var. Initialize the LangGraph checkpointer tables on prod Neon. Smoke test.

Phase 11 — Pre-launch checklist from .github/EXECUTION.md Part 12.

Apply .github/instructions/langgraph.instructions.md when writing anything under src/graph/, src/skills/, src/clients/.
Apply .github/instructions/ui.instructions.md when writing anything under src/app/, src/components/.
Apply .github/instructions/db.instructions.md when writing anything under src/db/, drizzle/.
Apply .github/instructions/style-guide.instructions.md to all generated output.
```

**Verify:** A plan markdown lands in `.specify/`. It should be specific enough that someone could implement without asking architectural questions.

## Step 5 — `/speckit.tasks`

No input needed. Spec Kit reads the spec and plan and generates a numbered task list. Open the generated tasks file and read it end to end before moving on.

Look for these red flags:

- Tasks that bundle too much ("Build the entire UI" instead of one component per task)
- Missing test tasks
- Tasks that skip past the deterministic skills and start with LLM nodes
- Tasks that hardcode env vars instead of reading from process.env

If you see any, edit the tasks file directly before running `/speckit.implement`. Spec Kit will respect your edits.

## Step 6 — `/speckit.checklist` (optional)

Generates a quality checklist for the spec. Useful for catching ambiguity before it bites you in implementation. Run this; address anything it flags by editing the spec, then re-run `/speckit.tasks` if the spec changed.

## Step 7 — `/speckit.analyze`

Cross-checks spec, plan, and tasks for consistency. Fix any reported issues before implementing.

## Step 8 — `/speckit.implement`

This is where Copilot actually writes code. Spec Kit walks the task list one task at a time and asks Copilot to implement each.

**Do not let it run unsupervised.** After each task or batch of tasks:

1. Read the generated files
2. Run `pnpm test`
3. Run `pnpm typecheck`
4. Run `pnpm build`
5. If the task touched the agent layer, run the smoke test from `EXECUTION.md` Part 8
6. If the task touched the UI, manually load the page and verify

If a task reports complete but tests are missing or empty, re-prompt with: "The previous task reported complete but did not generate the tests required by the constitution. Re-run the task generating real tests, not stubs."

## After implementation

When all tasks are green and verified:

1. Commit: `git add . && git commit -m "feat: implement via spec-kit pipeline"`
2. Push: `git push`
3. Move to `EXECUTION.md` Part 11 to deploy.

## Adding features later

Spec Kit shines on incremental work. For a new feature:

1. Run `/speckit.specify` with just the new feature's spec.
2. Skip `/speckit.constitution` (it's set already).
3. Run `/speckit.plan` referencing the existing architecture.
4. Run `/speckit.tasks`, then `/speckit.analyze`, then `/speckit.implement`.
5. Verify, commit, deploy.

This is the right workflow for: adding a new node, adding a second listings source, adding saved searches when you move past v1 scope.

## When Spec Kit feels wrong

Spec Kit is not always the right tool. Drop back to `PROMPTS.md` (direct Copilot prompts) when:

- The task is a single small change (one file, under 50 lines)
- You're debugging something specific
- You're exploring a design option before committing to it
- Spec Kit's task generation has obviously misunderstood the request

The four custom slash commands (`/refine`, `/audit`, `/new-node`, `/new-skill`) work fine alongside Spec Kit. Use whichever fits the moment.

## Troubleshooting

**`specify init` fails with "uv not found".** Install uv with the commands at the top of this file.

**Spec Kit can't find Copilot.** Confirm the GitHub Copilot extension is installed and you are signed in. Re-run `specify check`.

**Tasks file generates against the wrong stack.** Your spec or plan probably did not reference `project-context.instructions.md` strongly enough. Edit the spec, re-run `/speckit.tasks`.

**`/speckit.implement` reports done but code is missing.** This is the known failure mode. Always verify manually. Re-prompt explicitly asking for the missing pieces with the file path.

**Generated tests are trivial.** Add a constitution principle: "Every test must include at least one assertion that would fail if the implementation were stubbed." Re-run.
