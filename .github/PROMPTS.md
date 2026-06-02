# Build prompts

Every Copilot Chat prompt you need, in order. Copy each one into Copilot Chat and wait for the verification step to pass before moving to the next.

Full context, environment setup, and external service signups live in `EXECUTION.md`. This file is the fast lane for the build itself.

---

## Phase 0 — Scaffold

### 0.1 Project skeleton

```
Scaffold a TypeScript Node project for a housing recommendation pipeline following the source layout in copilot-instructions.md. Use pnpm, Vitest, ESLint, Prettier, and tsx. Create folders: src/graph/, src/graph/nodes/, src/graph/nodes/prompts/, src/skills/, src/clients/, src/types/, src/data/, src/components/, src/components/ui/, src/app/, src/app/api/, src/db/, src/db/schema/, src/db/queries/, tests/graph/, tests/graph/nodes/, tests/skills/, tests/clients/. Add src/types/intent.ts with a stub Intent Zod schema and inferred type, src/types/listing.ts with stub NormalizedListing and ScoredListing Zod schemas. Output: full file tree plus package.json (with start, dev, build, test, lint, typecheck scripts), tsconfig.json (strict, paths alias @/* for src/*), .eslintrc.json, .prettierrc, vitest.config.ts, .gitignore, and .env.example listing every env var from project-context.instructions.md. Stay under 300 lines total. Success: pnpm install runs clean and pnpm test reports zero tests.
```

**Verify:** `pnpm install && pnpm test && pnpm typecheck && pnpm lint` all pass.

---

## Phase 1 — Deterministic skills

### 1.1 Listing normalizer

```
Build src/skills/normalize-listing.ts as a pure function normalizeListing(raw: unknown, source: ListingSource): NormalizedListing | null. ListingSource is 'realestate_api' | 'attom' | 'rentcast'. Return null on any missing required field. Write Vitest tests in tests/skills/normalize-listing.test.ts: one happy-path fixture per source and one rejection per source. Output: skill and test only. Success: pnpm test passes with six assertions.
```

**Verify:** `pnpm test` passes.

### 1.2 Scoring engine

```
Build src/skills/score-listing.ts. Export scoreListing(listing, intent, neighborhoodScores) returning ScoredListing with componentScores (priceScore, sizeScore, neighborhoodScore, amenityScore, freshnessScore, each 0-100). Weights: 0.30 price, 0.20 size, 0.25 neighborhood, 0.15 amenities, 0.10 freshness. Document formulas at the top. Tests: matching intent yields above 80, 50% over budget drops priceScore below 40, 60-day-old listing drops freshnessScore below 20, weights sum to 1.0. Output: skill and test. Success: pnpm test passes.
```

**Verify:** `pnpm test` passes.

### 1.3 Neighborhood mapper

```
Build src/skills/map-neighborhoods.ts. Export mapIntentToNeighborhoods(intent, catalog) returning Map<string, number>. Score each neighborhood 0-1 from tag overlap, price band fit, and walk/transit fit. Create src/data/neighborhoods.json with three Bay Area entries (Mission District, Hayes Valley, Berkeley Downtown). Tests: tag overlap drives score above 0.6, 2x budget mismatch drops score below 0.3, returns at least one for any non-empty intent. Output: skill, JSON, test. Success: pnpm test passes.
```

**Verify:** `pnpm test` passes. Commit: `feat: add three deterministic skills`.

---

## Phase 2 — State and clients

### 2.1 Graph state

```
Build src/graph/state.ts using Annotation.Root from @langchain/langgraph. Fields with reducers: userQuery (last-wins), intent (last-wins), neighborhoodScores (last-wins), listings (concat with dedupe by sourceUrl), scored (last-wins), explained (last-wins), errors (concat). Import Zod schemas from src/types/. Define ExplainedListing extending ScoredListing with whyItFits, tradeoffs, affiliateUrl. Export the StateAnnotation and the inferred GraphState type. Write a Vitest test verifying the dedupe reducer on the listings field. Output: state file, types update, test. Success: pnpm test passes.
```

### 2.2 Anthropic client

```
Build src/clients/anthropic.ts exporting two module-level singleton ChatAnthropic instances: sonnetModel (claude-sonnet-4-6, temperature 0.2) and opusModel (claude-opus-4-7, temperature 0.4). Both read ANTHROPIC_API_KEY from env. Write a Vitest test asserting both are configured with the expected model strings.
```

### 2.3 External clients

```
Build src/clients/real-estate-api.ts, src/clients/walk-score.ts, src/clients/google-places.ts as typed wrappers. Each: exports a typed function, reads its key from the env var named in project-context.instructions.md, has a 5-second timeout via AbortController, retries twice with exponential backoff on rate-limit errors, validates every response with Zod before returning. Add Vitest tests for each using vi.fn() to mock fetch with one success and one rate-limit case. Output: three client files plus three test files.
```

**Verify:** `pnpm test` passes. Commit: `feat: add graph state and external clients`.

---

## Phase 3 — Graph nodes

### 3.1 Parse intent

```
Build src/graph/nodes/parse-intent.ts. Export parseIntentNode(state: GraphState): Promise<Partial<GraphState>>. Use sonnetModel from src/clients/anthropic.ts. Bind the Intent Zod schema via withStructuredOutput. The prompt template lives at src/graph/nodes/prompts/parse-intent.md and instructs extraction of budget range, bedroom range, lifestyle tags, must-have list, nice-to-have list. On parse failure return { errors: ['parse-intent: ' + message] } without throwing. Write a Vitest test mocking sonnetModel. Output: node, prompt file, test.
```

### 3.2 Map neighborhoods

```
Build src/graph/nodes/map-neighborhoods.ts. Export mapNeighborhoodsNode(state: GraphState): Promise<Partial<GraphState>>. Read src/data/neighborhoods.json, call the mapIntentToNeighborhoods skill, return { neighborhoodScores }. No LLM. Test asserts scores returned for at least one neighborhood given a fixture intent. Output: node and test.
```

### 3.3 Fetch listings

```
Build src/graph/nodes/fetch-listings.ts. Export fetchListingsNode(state: GraphState): Promise<Partial<GraphState>>. Pick the top 5 neighborhoods by score. Call src/clients/real-estate-api.ts. Pass each raw result through the normalizeListing skill. Drop nulls. Dedupe by sourceUrl. Cap at 50. On all-clients-failed return { errors: ['fetch-listings: all sources failed'] }. Write a Vitest test with the client mocked covering one success and one all-fail case. Output: node and test.
```

### 3.4 Score listings

```
Build src/graph/nodes/score-listings.ts. Export scoreListingsNode(state: GraphState): Promise<Partial<GraphState>>. Call scoreListing skill for each item in state.listings using state.intent and state.neighborhoodScores. Sort descending by score. Return { scored }. No LLM. Test asserts the output is sorted and length matches input. Output: node and test.
```

### 3.5 Explain top

```
Build src/graph/nodes/explain-top.ts. Export explainTopNode(state: GraphState): Promise<Partial<GraphState>>. Take the top 3 from state.scored. Use opusModel from src/clients/anthropic.ts with withStructuredOutput bound to a Zod schema for { whyItFits: string, tradeoffs: string }. Run the 3 calls in parallel via Promise.all. Build affiliateUrl by checking sourceDomain against the affiliate map (realtor.com → REALTOR_AFFILIATE_ID, apartments.com → APARTMENTS_AFFILIATE_ID, fallback to source URL with no params). The prompt template at src/graph/nodes/prompts/explain.md must apply the style guide rules. Test mocks opusModel and asserts whyItFits has no banned style-guide words. Output: node, prompt file, test.
```

**Verify:** `pnpm test` passes. Commit: `feat: add five LangGraph nodes`.

---

## Phase 4 — Compile the graph

### 4.1 Graph index

```
Build src/graph/index.ts. Import StateGraph and START, END from @langchain/langgraph. Topology: START → parse-intent → map-neighborhoods → fetch-listings → score-listings → explain-top → END. Use PostgresSaver from @langchain/langgraph-checkpoint-postgres as the checkpointer, reading DATABASE_URL from env. Export the compiled graph and a typed invoke(userQuery: string, threadId: string): Promise<GraphState> wrapper. Write a Vitest test using MemorySaver for the checkpointer that runs an end-to-end invocation with all nodes mocked and asserts exactly 3 entries in explained. Output: graph file and test.
```

**Verify:** Run smoke test:
```bash
pnpm tsx -e "import('./src/graph').then(({ invoke }) => invoke('two bed near transit under 3500 in the mission', 'smoke-1').then(s => console.log(s.explained)))"
```
Three listings should print. LangSmith should show a trace.

---

## Phase 5 — API route handler

### 5.1 Recommend route

```
Build src/app/api/recommend/route.ts. POST handler accepts { userQuery: string, threadId: string }, validates with Zod. Apply Upstash Ratelimit (60 requests per hour per IP) before invoking the graph. Call graph.stream(input, { configurable: { thread_id: threadId } }, { streamMode: 'updates' }). Pipe each update into a Server-Sent Events response using createDataStreamResponse from the Vercel AI SDK. Each event payload is { node: string, partial: Partial<GraphState> }. Set runtime to 'nodejs' and maxDuration to 60. Write a Vitest test that mocks the graph stream and asserts the SSE payload format. Output: route file and test.
```

**Verify:** With `pnpm dev` running:
```bash
curl -N -X POST http://localhost:3000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"userQuery":"two bed near transit under 3500","threadId":"curl-1"}'
```
SSE events stream to stdout.

---

## Phase 6 — UI

### 6.1 Install shadcn primitives

```bash
pnpm dlx shadcn@latest add card badge button textarea
```

### 6.2 Full UI flow

```
Build src/app/(recommend)/page.tsx as a server component wrapping a client component RecommendFlow.tsx. RecommendFlow uses experimental_useObject from @ai-sdk/react pointed at /api/recommend. Layout: hero textarea at the top with placeholder "Tell me what you're looking for in your next home", submit button, then a progressive results area. As graph updates arrive, render: IntentCard (parsed intent as editable chips), NeighborhoodMap (Mapbox GL JS with neighborhoods colored by score, uses NEXT_PUBLIC_MAPBOX_TOKEN), ListingsGrid with three ListingCard children that stream in. Each card shows photo (next/image), address, price, score badge, whyItFits streaming character by character, tradeoffs in smaller text, primary CTA labeled "View on {sourceDomain}" pointing to affiliateUrl, and a small "Affiliate link" tag. Add an FtcDisclosure banner above the fold with the exact wording from project-context.instructions.md. Use shadcn/ui Card, Badge, Button, Textarea. Animate card entry with Motion's stagger preset, max 200ms total. Add a sticky RefineChat at the bottom using assistant-ui's LangGraph adapter calling the same /api/recommend with the existing threadId. Output: page.tsx, RecommendFlow.tsx, IntentCard.tsx, NeighborhoodMap.tsx, ListingsGrid.tsx, ListingCard.tsx, RefineChat.tsx, FtcDisclosure.tsx.
```

**Verify:** `pnpm dev`, visit `http://localhost:3000`, submit a query. Three listings appear within 10 seconds. Map shows colored neighborhoods. Affiliate links route correctly.

Commit: `feat: add streaming UI with map and refine chat`.

---

## Ongoing slash commands

Use these in Copilot Chat as you build:

- **`/refine`** — Rewrite a messy prompt into a tight, executable one
- **`/audit`** — Scan code or text against the style guide
- **`/new-node`** — Scaffold a new LangGraph node
- **`/new-skill`** — Scaffold a new pure-function skill

## Deployment prompts

Deployment is a Vercel UI flow plus three CLI commands. See `EXECUTION.md` Part 11 onward for the click-by-click guide.
