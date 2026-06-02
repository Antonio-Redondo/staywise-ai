# Execution runbook

How to go from empty repo to deployed product using this Copilot configuration.

Work through these parts in order. Each part ends with a verification step. Do not move to the next part until verification passes.

## Prerequisites

Install these on your machine:

- [ ] Node 22 LTS (use [nvm](https://github.com/nvm-sh/nvm) or [Volta](https://volta.sh) to manage)
- [ ] pnpm 9+ (`npm install -g pnpm`)
- [ ] Git
- [ ] VS Code
- [ ] GitHub Copilot and GitHub Copilot Chat extensions in VS Code
- [ ] An active GitHub Copilot Pro or Business subscription

Create accounts (free tier is fine to start):

- [ ] Anthropic (console.anthropic.com) for the API key
- [ ] LangSmith (smith.langchain.com) for LLM traces
- [ ] Neon (neon.tech) for Postgres
- [ ] Upstash (upstash.com) for Redis
- [ ] Mapbox (mapbox.com) for maps
- [ ] RealEstateAPI.com for listings
- [ ] Walk Score (walkscore.com/professional) for walkability scores
- [ ] Google Cloud Console for the Places API
- [ ] Vercel (vercel.com) for deployment
- [ ] GitHub for the repo

Defer until post-launch:

- [ ] Sentry account for error monitoring
- [ ] PostHog account for product analytics
- [ ] Impact Radius for the Realtor.com affiliate program
- [ ] CJ Affiliate for the Apartments.com affiliate program

## Part 1 — Install the Copilot configuration

1. Create a fresh empty repo on GitHub. Name it `housing-rec` or similar.
2. Clone it locally: `git clone git@github.com:<you>/housing-rec.git && cd housing-rec`.
3. Unzip `copilot-config.zip` at the repo root. After unzipping you should have a `.github/` folder containing `copilot-instructions.md`, `README.md`, `EXECUTION.md`, an `instructions/` folder with five files, and a `prompts/` folder with `refine.prompt.md`.
4. Commit and push:
   ```bash
   git add .github
   git commit -m "chore: add copilot instructions and execution runbook"
   git push
   ```
5. Open the repo in VS Code: `code .`
6. Open Copilot Chat with `Cmd+Ctrl+I` on macOS or `Ctrl+Alt+I` on Windows/Linux.
7. **Verify Copilot reads the config.** Ask: "What is the architecture of this project?" Copilot should answer with the LangGraph six-stage pipeline and mention the source layout from `copilot-instructions.md`. If it says it has no context, update the GitHub Copilot extension to the latest version and reload VS Code.

**Checkpoint:** Copilot describes the LangGraph pipeline without you re-explaining it.

## Part 2 — Personalize the instructions

1. Open `.github/instructions/about-me.instructions.md`. Skim every field. Edit anything that does not match your reality (OS, editor, branching style, tools).
2. Open `.github/instructions/project-context.instructions.md`. The defaults are filled in for the Bay Area launch. Adjust the launch metro, yearly target, or affiliate partners if your plan differs.
3. Commit:
   ```bash
   git add .github
   git commit -m "chore: personalize copilot instructions"
   git push
   ```

**Checkpoint:** Both files reflect your actual situation, not the defaults.

## Part 3 — Scaffold the project

Open Copilot Chat. Paste this prompt exactly:

```
Scaffold a TypeScript Node project for a housing recommendation pipeline following the source layout in copilot-instructions.md. Use pnpm, Vitest, ESLint, Prettier, and tsx for running. Create folders: src/graph/, src/graph/nodes/, src/graph/nodes/prompts/, src/skills/, src/clients/, src/types/, src/data/, src/components/, src/components/ui/, src/app/, src/app/api/, tests/graph/, tests/skills/, tests/clients/. Add src/types/intent.ts with a stub Intent Zod schema and inferred type, src/types/listing.ts with stub NormalizedListing and ScoredListing Zod schemas and inferred types. Output: full file tree plus contents of package.json (with start, dev, build, test, lint, typecheck scripts), tsconfig.json (strict mode, paths alias @/* for src/*), .eslintrc.json, .prettierrc, vitest.config.ts, .gitignore, .env.example listing every env var from project-context.instructions.md, and the two type files. Stay under 300 lines total. Success: pnpm install runs clean and pnpm test reports zero tests, no failures.
```

After Copilot generates the files, run:

```bash
pnpm install
pnpm test
pnpm typecheck
pnpm lint
```

All four commands should succeed.

Commit:
```bash
git add .
git commit -m "feat: scaffold project structure"
git push
```

**Checkpoint:** Clean install, zero tests run, zero type errors, zero lint errors.

## Part 4 — Build the three deterministic skills

These have no LLM calls and no external network. Pure functions. Test them thoroughly because every node depends on them.

**Skill 1.** Paste into Copilot Chat:

```
Build src/skills/normalize-listing.ts. Export a pure function normalizeListing(raw: unknown, source: ListingSource): NormalizedListing | null. Define ListingSource as 'realestate_api' | 'attom' | 'rentcast'. The NormalizedListing Zod schema lives in src/types/listing.ts with fields: id, sourceUrl, sourceDomain, address, lat, lng, neighborhoodSlug, priceUsd, bedrooms, bathrooms, sqft, photoUrls (string array), listedAt (ISO string), rawAmenities (string array). Return null when any required field is missing or fails Zod parsing. Write Vitest tests in tests/skills/normalize-listing.test.ts: one happy-path fixture per source and one missing-field rejection per source. Use realistic fixtures inline. Output: the type file update, skill file, and test file. Success: pnpm test passes with six assertions.
```

Run `pnpm test`. All six tests should pass.

**Skill 2.** Paste:

```
Build src/skills/score-listing.ts. Export scoreListing(listing: NormalizedListing, intent: Intent, neighborhoodScores: Map<string, number>): ScoredListing. ScoredListing extends NormalizedListing with score (0 to 100) and componentScores: priceScore, sizeScore, neighborhoodScore, amenityScore, freshnessScore, each 0 to 100. Weights: price 0.30, size 0.20, neighborhood 0.25, amenities 0.15, freshness 0.10. Document each component's formula in a comment block at the top. Scoring stays deterministic, no LLM. Write Vitest tests in tests/skills/score-listing.test.ts: a matching intent yields score above 80, a price 50 percent over budget drops priceScore below 40, a listing older than 60 days drops freshnessScore below 20, and one test asserting the weights sum to 1.0. Output: skill file and test file. Success: pnpm test passes.
```

Run `pnpm test`.

**Skill 3.** Paste:

```
Build src/skills/map-neighborhoods.ts. Export mapIntentToNeighborhoods(intent: Intent, catalog: NeighborhoodCatalog): Map<string, number>. NeighborhoodCatalog entries: slug, name, city, tags (string array), medianPriceUsd, walkScore, transitScore. Each neighborhood scores 0 to 1 based on tag overlap with intent.lifestyleTags, price band fit between intent.budgetUsd and medianPriceUsd, and walk/transit fit. Create src/data/neighborhoods.json with three sample Bay Area entries (Mission District, Hayes Valley, Berkeley Downtown). Write Vitest tests: tag overlap drives score above 0.6, a budget mismatch of 2x reduces score below 0.3, the function returns at least one neighborhood for any non-empty intent. Output: skill file, sample JSON, test file. Success: pnpm test passes.
```

Run `pnpm test` again. Everything should pass.

Commit:
```bash
git add .
git commit -m "feat: add normalize, score, and neighborhood mapping skills"
git push
```

**Checkpoint:** Three skills, all tests green.

## Part 5 — Set up external services

Before building the agent layer, get your keys. Copy `.env.example` to `.env.local`:

```bash
cp .env.example .env.local
```

Fill in each key as you go:

1. **Anthropic.** Console → API Keys → Create Key. Add to `.env.local` as `ANTHROPIC_API_KEY`.
2. **LangSmith.** smith.langchain.com → Settings → API Keys → Create. Set `LANGSMITH_API_KEY`. Set `LANGSMITH_PROJECT=housing-rec-dev` and `LANGSMITH_TRACING=true`.
3. **Neon Postgres.** neon.tech → Create project → choose region close to your Vercel region. Copy the connection string into `DATABASE_URL`. Run `psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"` to enable pgvector.
4. **Upstash Redis.** upstash.com → Create database → REST API. Copy `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN`.
5. **Mapbox.** account.mapbox.com → Tokens → Create new public token. Add as `NEXT_PUBLIC_MAPBOX_TOKEN`.
6. **RealEstateAPI.com.** Sign up, choose the lowest paid tier that covers your launch metro. Copy the key to `REAL_ESTATE_API_KEY`.
7. **Walk Score.** walkscore.com/professional → Sign up → API key. Add as `WALK_SCORE_API_KEY`.
8. **Google Places.** console.cloud.google.com → APIs and Services → Enable Places API → Credentials → Create API key. Restrict it to Places API only. Add as `GOOGLE_PLACES_API_KEY`.

Affiliate IDs can be empty strings for now. You will fill them in after Impact Radius and CJ Affiliate approve your application post-launch.

**Verify:** `pnpm dev` starts without errors complaining about missing env vars.

## Part 6 — Build the LangGraph state and clients

Paste into Copilot Chat:

```
Build src/graph/state.ts. Define the LangGraph state using Annotation.Root from @langchain/langgraph. Fields with their reducer behavior: userQuery (string, last-wins), intent (Intent or null, last-wins), neighborhoodScores (Record<string, number>, last-wins), listings (NormalizedListing[], concat with dedupe by sourceUrl), scored (ScoredListing[], last-wins), explained (ExplainedListing[], last-wins), errors (string[], concat). Import the Zod schemas from src/types/ for each shape. Define ExplainedListing in src/types/listing.ts extending ScoredListing with whyItFits, tradeoffs, affiliateUrl. Export both the StateAnnotation and an inferred TypeScript type GraphState. Write a Vitest test that creates a state instance and verifies the dedupe reducer on the listings field. Output: state.ts, types update, test file. Success: pnpm test passes.
```

Then the clients. Paste:

```
Build src/clients/anthropic.ts that exports two configured ChatAnthropic singletons: sonnetModel (model 'claude-sonnet-4-6', temperature 0.2) and opusModel (model 'claude-opus-4-7', temperature 0.4). Build src/clients/real-estate-api.ts that exports searchListings(neighborhoodSlugs: string[], filters: ListingFilters): Promise<unknown[]> calling RealEstateAPI.com with the key from REAL_ESTATE_API_KEY env var, 5-second timeout via AbortController, two retries with exponential backoff on rate-limit responses. Build src/clients/walk-score.ts and src/clients/google-places.ts as similar typed wrappers. Add Vitest tests for each client using msw or vi.fn() to mock fetch. Output: four client files plus their tests. Success: pnpm test passes.
```

Commit:
```bash
git add .
git commit -m "feat: add graph state and external clients"
git push
```

**Checkpoint:** State annotation compiles, client tests pass.

## Part 7 — Build the five graph nodes

Paste one prompt at a time. Run `pnpm test` after each.

**Node 1 — Parse intent:**

```
Build src/graph/nodes/parse-intent.ts. Export parseIntentNode(state: GraphState): Promise<Partial<GraphState>>. Use sonnetModel from src/clients/anthropic.ts. Bind the Intent Zod schema via withStructuredOutput. The prompt template lives at src/graph/nodes/prompts/parse-intent.md and instructs extraction of budget range, bedroom range, lifestyle tags, must-have list, nice-to-have list. On parse failure, return { errors: ['parse-intent: ' + message] } without throwing. Write a Vitest test mocking sonnetModel. Output: node, prompt file, test.
```

**Node 2 — Map neighborhoods:**

```
Build src/graph/nodes/map-neighborhoods.ts. Export mapNeighborhoodsNode(state: GraphState): Promise<Partial<GraphState>>. Read src/data/neighborhoods.json, call mapIntentToNeighborhoods skill, return { neighborhoodScores }. No LLM. Test asserts scores returned for at least one neighborhood given a fixture intent. Output: node and test.
```

**Node 3 — Fetch listings:**

```
Build src/graph/nodes/fetch-listings.ts. Export fetchListingsNode(state: GraphState): Promise<Partial<GraphState>>. Pick top 5 neighborhoods by score. Call src/clients/real-estate-api.ts. Pass results through normalizeListing skill. Dedupe by sourceUrl. Cap at 50. On all-clients-failed return { errors: ['fetch-listings: all sources failed'] }. Test with the client mocked, covering success and all-fail. Output: node and test.
```

**Node 4 — Score listings:**

```
Build src/graph/nodes/score-listings.ts. Export scoreListingsNode(state: GraphState): Promise<Partial<GraphState>>. Call scoreListing skill for each item in state.listings. Sort descending by score. Return { scored }. No LLM. Test asserts sort order and length. Output: node and test.
```

**Node 5 — Explain top:**

```
Build src/graph/nodes/explain-top.ts. Export explainTopNode(state: GraphState): Promise<Partial<GraphState>>. Take top 3 from state.scored. Use opusModel from src/clients/anthropic.ts with withStructuredOutput bound to a Zod schema for { whyItFits: string, tradeoffs: string }. Run 3 calls in parallel via Promise.all. Build affiliateUrl by checking sourceDomain against the affiliate map (realtor.com → REALTOR_AFFILIATE_ID, apartments.com → APARTMENTS_AFFILIATE_ID, fallback to no params). Prompt template at src/graph/nodes/prompts/explain.md applies the style guide. Test mocks opusModel and asserts whyItFits has no banned style-guide words. Output: node, prompt file, test.
```

Commit:
```bash
git add .
git commit -m "feat: add five LangGraph nodes"
git push
```

**Checkpoint:** All node tests pass.

## Part 8 — Compile the graph

Paste:

```
Build src/graph/index.ts. Import StateGraph and START, END from @langchain/langgraph. Topology: START → parse-intent → map-neighborhoods → fetch-listings → score-listings → explain-top → END. Use PostgresSaver from @langchain/langgraph-checkpoint-postgres as the checkpointer, reading DATABASE_URL from env. Export the compiled graph and a typed invoke(userQuery: string, threadId: string): Promise<GraphState> wrapper. Write a Vitest test using MemorySaver for the checkpointer that runs end-to-end with all nodes mocked and asserts exactly 3 entries in explained. Output: graph file and test.
```

Run `pnpm test`. Then run the graph once manually to seed the checkpointer table:

```bash
pnpm tsx -e "import { invoke } from './src/graph'; invoke('two bed near transit under 3500 in the mission', 'smoke-test').then(s => console.log(s.explained))"
```

If this completes and logs three listings, the agent layer works end-to-end against real services.

**Checkpoint:** Three explained listings printed, LangSmith dashboard shows the trace.

## Part 9 — Build the API route handler

Paste:

```
Build src/app/api/recommend/route.ts. POST handler accepts { userQuery: string, threadId: string }, validates with Zod. Call graph.stream(input, { configurable: { thread_id: threadId } }, { streamMode: 'updates' }). Pipe each update into an SSE response using the Vercel AI SDK's createDataStreamResponse. Each event carries { node: string, partial: Partial<GraphState> }. Set runtime to 'nodejs' and maxDuration to 60. Add a rate-limit check using Upstash Ratelimit (60 requests per hour per IP) before invoking the graph. Write a Vitest test mocking the graph stream and asserting SSE payload shape. Output: route file and test.
```

**Checkpoint:** `curl -N -X POST http://localhost:3000/api/recommend -H "Content-Type: application/json" -d '{"userQuery":"two bed near transit under 3500","threadId":"local-1"}'` streams updates.

## Part 10 — Build the UI

Paste:

```
Build src/app/(recommend)/page.tsx as a server component wrapping a client component RecommendFlow.tsx. RecommendFlow uses experimental_useObject from @ai-sdk/react pointed at /api/recommend. Layout: hero textarea at the top with placeholder "Tell me what you're looking for in your next home", submit button, then a progressive results area. As graph updates arrive, render: IntentCard (parsed intent as editable chips), NeighborhoodMap (Mapbox GL JS with neighborhoods colored by score), ListingsGrid with three ListingCard children that stream in. Each card shows photo, address, price, score badge, whyItFits streaming character by character, tradeoffs in a smaller line, primary CTA labeled "View on {sourceDomain}" pointing to affiliateUrl, and a small "Affiliate link" tag. Add an FTC disclosure banner above the fold. Use shadcn/ui Card, Badge, Button. Animate card entry with Motion's stagger preset. Add a sticky RefineChat at the bottom using assistant-ui's LangGraph adapter calling the same /api/recommend with the existing threadId. Output: page.tsx, RecommendFlow.tsx, IntentCard.tsx, NeighborhoodMap.tsx, ListingsGrid.tsx, ListingCard.tsx, RefineChat.tsx, FtcDisclosure.tsx. Success: pnpm dev shows the full flow.
```

Install any shadcn components Copilot references:

```bash
pnpm dlx shadcn@latest add card badge button textarea
```

Run `pnpm dev` and visit `http://localhost:3000`. Submit a query. Verify all three listings render with photos, scores, and affiliate links.

Commit:
```bash
git add .
git commit -m "feat: add streaming UI with map and refine chat"
git push
```

**Checkpoint:** Full flow works locally. Three listings appear within 10 seconds of submit.

## Part 11 — Deploy to Vercel

1. Go to vercel.com → New Project → Import your GitHub repo.
2. Framework preset: Next.js (auto-detected).
3. In Project Settings → Environment Variables, add every variable from `.env.local` for the Production environment. Set `LANGSMITH_PROJECT=housing-rec-prod`.
4. Click Deploy.
5. After the first deploy succeeds, run database migrations against the production Neon database:
   ```bash
   DATABASE_URL=<prod-url> pnpm tsx -e "import { PostgresSaver } from '@langchain/langgraph-checkpoint-postgres'; const cp = PostgresSaver.fromConnString(process.env.DATABASE_URL); await cp.setup();"
   ```
6. Smoke test the production URL: submit a query, confirm three listings.
7. Open LangSmith. Confirm a trace appeared in the `housing-rec-prod` project.

**Checkpoint:** Production URL works end-to-end. LangSmith shows the prod trace.

## Part 12 — Pre-launch checklist

Do every one of these before you tell anyone about the URL.

- [ ] Privacy policy page at `/privacy` linked from the footer.
- [ ] Terms of service page at `/terms` linked from the footer.
- [ ] FTC affiliate disclosure visible above the fold on every page that shows affiliate links.
- [ ] `robots.txt` allows indexing and points at `sitemap.xml`.
- [ ] Sentry installed with `SENTRY_DSN` set. Throw a test error in dev and confirm it appears.
- [ ] PostHog installed with `NEXT_PUBLIC_POSTHOG_KEY` set. Confirm the page-view event appears.
- [ ] Anthropic console cost alert set at your monthly budget cap.
- [ ] RealEstateAPI.com usage alert set at your monthly budget cap.
- [ ] LangSmith dashboard bookmarked.
- [ ] Vercel analytics enabled.
- [ ] Mobile responsive check on a real phone, not just the browser devtools.
- [ ] Lighthouse score above 90 on Performance, Accessibility, Best Practices, SEO.
- [ ] Click-track endpoint logs to Postgres so you can verify the affiliate funnel.

When all twelve boxes are checked, you are ready to launch.

## How to use Copilot during ongoing development

- For any new task, write your messy idea first. Run it through `/refine` in Copilot Chat. Paste the cleaned version into a new chat.
- When Copilot suggests code that violates the style guide, say "audit this against the style guide" and it will rescan and fix.
- When refactoring across files, paste the file paths first so Copilot's context window has them indexed.
- When adding a new external dependency, update `project-context.instructions.md` stack lock-ins in the same PR.
- At the start of each quarter, update `project-context.instructions.md` with the new yearly progress, this quarter's focus, and refreshed scope decisions.

## Troubleshooting

**Copilot does not seem to follow the instructions.** Restart VS Code. Confirm the GitHub Copilot extension is on the latest version. Confirm the `.github/` folder is at the repo root, not nested.

**LangGraph node imports fail with version conflicts.** All `@langchain/*` packages must use compatible versions. Pin them in `package.json` and run `pnpm install` again.

**LangSmith traces do not appear.** Confirm `LANGSMITH_TRACING=true`, the API key is valid, and the project name matches what you see in the LangSmith UI.

**The graph hangs on parse-intent.** Almost always an Anthropic API key issue or model name typo. Check the network tab in the trace.

**Listings come back empty.** RealEstateAPI.com tier may not cover your selected neighborhoods. Check the raw response in LangSmith.

**Affiliate URLs are missing parameters.** Affiliate IDs are not set in the env. Confirm `REALTOR_AFFILIATE_ID` and `APARTMENTS_AFFILIATE_ID` are populated in Vercel for the Production environment.
