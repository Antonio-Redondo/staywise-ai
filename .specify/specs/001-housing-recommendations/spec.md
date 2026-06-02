# Feature Specification: Housing Recommendation Engine

**Feature Branch**: `001-housing-recommendations`

**Created**: 2026-05-28

**Status**: Draft

**Input**: Build a housing recommendation web app where users submit natural language descriptions and receive three matched listings with explanations, tradeoffs, and affiliate links.

## Clarifications

### Session 2026-05-28

- Q: Lifestyle tags source and input mechanism? → A: Predefined catalog of ~20–30 canonical tags (walkable, quiet, tech_hub, family_friendly, urban, suburban, near_schools, pet_friendly, modern_amenities, good_schools, low_crime, nightlife, cultural, green_space, waterfront, beach, mountains, golf_courses, retirement_community, co_working_spaces). Intent extraction maps user input to canonical tags via fuzzy matching; non-matching tags are dropped.
- Q: Amenities matching in listing scoring? → A: Predefined amenities catalog (~15–20 canonical amenities: pool, gym, parking, rooftop, doorman, elevator, laundry_in_unit, dishwasher, air_conditioning, heating, balcony, patio, fireplace, game_room, home_theater). Listing amenities sourced from Google Places API. Amenities match: count intersection of (user's must-haves mapped to canonical amenities) with (listing's amenities from Google Places).
- Q: Thread ID session lifetime and stale state recovery? → A: Thread ID lifetime is scoped to the browser session. If the browser closes, the old thread ID is orphaned. Re-visiting the app later generates a new session and thread ID. No recovery of prior state across browser sessions in v1.
- Q: Refinement node semantics — intent replacement vs. modification? → A: Intent modification (delta-based). Refinement input ("cheaper", "more transit") is parsed as a delta to the prior intent. A refinement step updates intent fields (e.g., lower budgetMax, increase walkScore weight). Neighborhoods and listings are re-scored with modified intent; prior data is retained and re-ranked.
- Q: Neighborhood catalog source and enrichment? → A: Static catalog of ~50–100 SF Bay Area neighborhoods (zip codes or neighborhood names) loaded at deploy time. Walk Score and median price fetched from external APIs on first request and cached in Redis (6-hour TTL). Subsequent requests read from cache.

---

## User Scenarios & Testing (mandatory)

User stories ordered by implementation priority. Each story is independently testable and delivers measurable value.

### User Story 1 — Submit Query and View Recommendations (Priority: P1)

A first-time visitor lands on the recommend page and submits what they want in a home. The app parses their intent, scores neighborhoods and listings, and displays three personalized recommendations with explanations.

**Why this priority**: This is the core value proposition. Without this, the app has no purpose.

**Independent Test**: Can be tested end-to-end by submitting a single query and asserting three recommendations appear with scores and explanations. Delivers complete user value in one atomic flow.

**Acceptance Scenarios**:

1. **Given** user lands on the recommend page, **When** they see a hero textarea with placeholder text, **Then** the placeholder reads "Tell me what you're looking for in your next home."
2. **Given** user types a free-text query like "3-bedroom house under $1M near transit in SF", **When** they submit, **Then** the page shows loading state and begins streaming results.
3. **Given** results stream back, **When** the UI receives parsed intent, **Then** editable chips appear showing extracted budget range, bedroom count, lifestyle tags, must-haves, and nice-to-haves.
4. **Given** an interactive map appears, **When** the neighborhood scores arrive, **Then** the map lights up showing the top 5 scored neighborhoods with visual priority.
5. **Given** listings are scored and ranked, **When** the top 3 are explained, **Then** each card displays photo, address, price, numeric score (0-100), two-sentence explanation of why it fits, one-sentence tradeoff statement, and a "View on {sourceDomain}" link.
6. **Given** an affiliate link is generated, **When** the user clicks it, **Then** they are routed to the source listing site with affiliate tracking parameters appended (e.g., `?ref=` for Realtor.com, `?cm_mmc=` for Apartments.com).
7. **Given** the page displays affiliate links, **When** the page loads, **Then** an FTC-compliant disclosure banner appears above the fold stating "This site contains affiliate links. We may earn a commission if you click through and complete a transaction at no cost to you."

---

### User Story 2 — Refine Results Without Re-parsing (Priority: P2)

After viewing three recommendations, a user wants to refine the results (e.g., "show me cheaper options" or "prioritize transit"). They use a sticky chat interface at the bottom to refine without restating the original intent.

**Why this priority**: Enables iterative discovery and improves user engagement. Reusing prior state reduces latency and API calls.

**Independent Test**: Can be tested by submitting a base query, then sending a refinement message, and asserting that the new results reuse the prior intent (thread ID persists) and only re-score/re-explain, not re-parse.

**Acceptance Scenarios**:

1. **Given** three recommendations are displayed, **When** the user sees a sticky chat surface at the bottom, **Then** it shows a text input with placeholder text like "Refine your search (e.g., 'show me cheaper', 'more transit')".
2. **Given** user sends a refinement message, **When** the backend processes it, **Then** a thread ID persists in the URL as a query parameter (e.g., `?threadId=<uuid>`).
3. **Given** a refinement is received, **When** the backend scores and re-ranks listings with the new constraint, **Then** the prior parsed intent is reused and the explanation node runs again, not the parse-intent node.
4. **Given** refined results arrive, **When** the UI receives them, **Then** the new top 3 listings are displayed with updated scores and explanations that address the refinement.

---

### User Story 3 — Handle Empty or Degraded Results Gracefully (Priority: P3)

If RealEstateAPI returns no listings for the matched neighborhoods or if an explanation fails for one of the three listings, the app shows a helpful error state instead of crashing.

**Why this priority**: Improves resilience and user experience when external APIs fail. Enables the app to degrade gracefully.

**Independent Test**: Can be tested by mocking RealEstateAPI to return zero listings or by mocking the explanation node to fail on one of three listings, then asserting the UI renders appropriate fallback content.

**Acceptance Scenarios**:

1. **Given** the top 5 neighborhoods are scored, **When** RealEstateAPI returns zero listings for all of them, **Then** the page shows an empty state with text "No listings found. Try broadening your search criteria or adjusting your budget and location preferences."
2. **Given** three listings are scored, **When** the explanation node fails for listing #2, **Then** listing #1 and #3 display full cards with explanations, and listing #2 displays a partial card with photo, address, price, score, but a "Why it fits" placeholder instead of the narrative.
3. **Given** an error occurs in any pipeline stage, **When** the error is caught, **Then** it is appended to the state's error field (not thrown), and the UI renders an appropriate fallback or retry prompt based on the error type.

---

### Edge Cases

- What happens if the user submits a query with no extractable structure (e.g., random words)? Return a generic intent with no constraints and show all neighborhoods equally; let the user refine.
- What if RealEstateAPI rate-limits the request? Apply exponential backoff with retries (max 2 retries, 5-second timeout); if all retries fail, return the error to state and render a "service temporarily unavailable" message.
- What if the Mapbox token is invalid or the map fails to load? Render a graceful fallback showing neighborhood list as text instead of visual pins.
- What if a listing photo URL is broken? Show a placeholder image and continue rendering the card.
- What if the thread ID in the URL is stale (not found in the session)? Treat it as a new session and generate a new thread ID.

---

## Functional Requirements

### Intent Extraction

1. Parse free-text user query into a structured Intent object with: budget range (min, max in USD), bedroom range (min, max), lifestyle tags (selected from a predefined catalog of ~20–30 canonical tags: walkable, quiet, tech_hub, family_friendly, urban, suburban, near_schools, pet_friendly, modern_amenities, good_schools, low_crime, nightlife, cultural, green_space, waterfront, beach, mountains, golf_courses, retirement_community, co_working_spaces), must-haves (explicit non-negotiables, free-form text), nice-to-haves (desirable but not required, free-form text), and optional commute target (location name and max minutes).
2. Lifestyle tags are extracted by fuzzy-matching user input against the canonical catalog; only canonical tags are stored in Intent. Tags not in the catalog are dropped.
3. Validate extracted ranges: budget > 0, bedrooms >= 1, ranges have lower <= upper.
4. Handle queries with partial or missing information: if a field is not detected, leave it null or empty; the downstream stages handle nulls gracefully.
5. Extract exactly one intent per query; if the query is ambiguous, pick the most likely interpretation and document it in the explanation.

### Refinement as Intent Modification

1. When a refinement message is received (e.g., "cheaper", "more transit", "need 4 bedrooms"), parse it as a delta to the prior intent, not a full query replacement.
2. Translate common refinement patterns into intent field updates:
   - "cheaper" / "lower price" → reduce `budgetMax` by ~10–20%
   - "more expensive" / "higher price" → increase `budgetMax` by ~10–20%
   - "more transit" / "better transit" → add or prioritize transit-related lifestyle tags (walkable, urban)
   - "quieter" / "quiet neighborhood" → add "quiet" lifestyle tag, lower nightlife/urban weight
   - "bigger" / "more space" → increase `bedroomsMin` or add "spacious" preference
   - "closer to X" → set or update `commuteTarget` with location and max minutes
   - "good schools" → add "good_schools" lifestyle tag
3. If a refinement is too ambiguous or doesn't map to a clear intent delta, treat it as a clarification request and ask the user.
4. Apply the delta to the prior intent; the modified intent is used for neighborhood and listing scoring in downstream nodes.
5. Preserve all prior intent fields not explicitly modified; only update fields that are directly addressed by the refinement.



### Neighborhood Scoring

1. Use a static catalog of ~50–100 SF Bay Area neighborhoods (zip codes or neighborhood names like "Mission District", "Marina", "Berkeley Hills", etc.), loaded at deploy time from a JSON file in `src/data/neighborhoods.json`.
2. For each neighborhood in the catalog, compute a score (0 to 1) based on three weighted components:
   - Tag overlap: count matching lifestyle tags from intent / total tags in catalog (40% weight)
   - Price band fit: if median neighborhood price (from cache or API) falls within user's budget range, score 1.0; otherwise, score is 1 - (distance from range / budget range), capped at 0 (40% weight)
   - Walk/transit fit: Walk Score (from cache or Walk Score API) >= 60 and transit availability (from Walk Score transit category) >= 50, score 1.0; otherwise, proportional score (20% weight)
3. On first request for a neighborhood's Walk Score or median price, fetch from external APIs (Walk Score API, RealEstateAPI or local market data) and cache in Upstash Redis with 6-hour TTL.
4. Subsequent requests for the same neighborhood use cached values.
5. Normalize each component to 0–1 before weighting.
6. Rank neighborhoods by score descending; cap results at top 5 for listings retrieval.
7. Document the scoring formula in the skill's docstring with examples.

### Listings Retrieval

1. Fetch listings from RealEstateAPI for the top 5 neighborhoods by score (if fewer than 5 neighborhoods exist, fetch for all).
2. Normalize every listing (regardless of source) into a unified NormalizedListing shape: `{ id, sourceUrl, address, price, bedrooms, bathrooms, squareFeet, photoUrl, source, listedDate }`.
3. Return `null` for any listing that cannot be normalized (e.g., missing critical fields like address or price).
4. Deduplicate listings by `sourceUrl` (keep first occurrence).
5. Cap total results at 50 listings after deduplication.
6. Apply a 5-second timeout with exponential backoff (max 2 retries) to all API calls; if all retries fail, return error to state.

### Listing Scoring

1. For each normalized listing, compute a weighted score (0 to 100) using the intent and neighborhood scores:
   - Price fit: (1 - |listing.price - intent.budgetMid| / intent.budgetRange) * 30
   - Size fit: (1 - |listing.bedrooms - intent.bedroomsMid| / intent.bedroomsRange) * 20
   - Neighborhood score * 25 (from neighborhood mapping stage)
   - Amenities match: count intersection of (user's must-haves matched to canonical amenities) and (listing's amenities from Google Places API) / total canonical amenities in must-haves, capped at 1, multiplied by 15
   - Freshness: (1 - days since listing.listedDate / 180) * 10, capped at 0
2. Document all formulas in the skill with examples.
3. Rank listings by score descending.
4. Rank order: sorted by score descending, return top 3 for explanation.

### Listing Explanation

1. For each of the top 3 listings, generate a two-sentence explanation of why it fits the user's intent. Explanations must:
   - Reference specific attributes (e.g., "3 bedrooms, $950k price tag" or "walkable to BART").
   - Address at least one element from the user's must-haves or lifestyle tags.
   - Be written in plain English, 2 sentences maximum.
   - Comply with the style guide (no banned words, no em dashes, clear and direct).
2. Generate a one-sentence tradeoff for each listing. Tradeoffs must:
   - Identify one realistic drawback or constraint relative to the intent (e.g., "Commute to downtown is 45 minutes" or "Smaller yard than typical for the price").
   - Be written as a neutral statement, not apologetic or negative.
   - Be 1 sentence maximum.
3. If explanation generation fails for a listing, return error to state; the UI will render a placeholder instead of a narrative.

### Affiliate URL Generation

1. For each top 3 listing, build an affiliate URL server-side based on the listing's source domain:
   - **Realtor.com**: append `?ref={REALTOR_AFFILIATE_ID}` to the listing's source URL
   - **Apartments.com**: append `?cm_mmc=affiliate-{APARTMENTS_AFFILIATE_ID}` to the listing's source URL
   - **Other domains**: link to the source URL without affiliate parameters
2. Validate that `REALTOR_AFFILIATE_ID` and `APARTMENTS_AFFILIATE_ID` are set in environment variables; if missing, fall back to the raw source URL and do not attempt affiliate tracking.
3. Encode all URL parameters correctly (e.g., spaces as `%20`).

### FTC Disclosure

1. Every page that displays one or more affiliate links must show an FTC-compliant disclosure banner above the fold.
2. The disclosure banner must display the exact text: "This site contains affiliate links. We may earn a commission if you click through and complete a transaction at no cost to you."
3. The banner must be non-dismissible (no close button or fade-out animation).
4. The banner must have a subtle background color (e.g., light gray or beige) to distinguish it from the main content without being visually jarring.

### Thread ID and Refinement State Reuse

1. On the first submit within a browser session, generate a UUID client-side and append it to the URL as `?threadId=<uuid>`.
2. On refinement within the same browser session, reuse the thread ID from the URL; if no thread ID exists in the URL, generate a new one.
3. Thread ID is scoped to the browser session. If the user closes the browser and returns later, the old thread ID is invalid; treat the request as a new session with a new thread ID.
4. Pass the thread ID to the backend in each request; the backend uses it to retrieve prior state from the session store (LangGraph's PostgresSaver).
5. **Refinement as Intent Modification**: When a refinement is received (e.g., "cheaper", "more transit"), it is parsed as a delta to the prior intent, not a full query replacement. A refinement-parsing step translates refinement input into intent field updates:
   - "cheaper" → lower `budgetMax` by ~10–20%
   - "more transit" → increase weight of transit-focused lifestyle tags or lower `walkScore` threshold
   - "closer to downtown" → set or modify `commuteTarget`
   - "bigger" → increase `bedroomsMin` or `squareFeetMin`
6. After the intent is modified, neighborhoods and listings are re-scored. Prior neighborhoods and listings data are retained and re-ranked with the new scoring; they are not re-fetched unless neighborhoods have changed significantly (top 5 differ).
7. The modified intent replaces the prior intent in state; subsequent refinements start from this modified intent.

### Error Handling and State

1. Errors at any stage (intent parsing, neighborhood mapping, listings fetch, scoring, explanation) are captured in state as `{ errors: ['stage: message'] }`, never thrown.
2. The frontend checks for errors at each stage and renders appropriate fallback UI or retry prompts.
3. If a node encounters an expected failure (e.g., empty listings, API rate limit), it returns the error in state and yields control to the graph's error handling edge, allowing subsequent nodes to decide whether to continue or gracefully degrade.

### LangSmith Tracing

1. Every request to the recommend endpoint automatically emits a trace to LangSmith via the `@langchain/langgraph` integration (no custom tracing code needed).
2. Traces must include all node execution times, state updates, and any errors encountered.
3. The LangSmith project name is set via the `LANGSMITH_PROJECT` environment variable (set to `housing-rec-prod` in production, `housing-rec-dev` locally).

---

## Success Criteria

### User Experience

- A user can submit a free-text query and see three explained recommendations within 10 seconds on a normal broadband connection (6 Mbps down).
- Editable chips for parsed intent appear within 2 seconds of query submission (streaming UX).
- The interactive neighborhood map appears and lights up within 3 seconds.
- Listing cards stream in over the course of 5–8 seconds (staggered entry), each displaying photo, address, price, score, explanation, tradeoff, and affiliate link.

### Correctness

- Affiliate links route correctly to the partner site with tracking parameters appended and verified via manual click-through testing on staging.
- Refinement requests reuse prior intent without re-invoking the parse-intent node (verified via LangSmith trace inspection).
- The pipeline emits a complete trace to LangSmith on every request (verified via project dashboard).

### Resilience

- Each pipeline stage either completes successfully or returns an error appended to state; no unhandled exceptions reach the frontend.
- If RealEstateAPI returns zero listings, the app renders an empty state with a "broaden criteria" suggestion instead of crashing.
- If an explanation fails for one of three listings, that listing shows a partial card with score but no narrative; the other two display full explanations.

### Code Quality

- `pnpm test` passes with full coverage on the three core skills:
  - Listing normalizer: 100% coverage, tests for valid and invalid input shapes
  - Scoring engine: 100% coverage, tests for all weighting components and edge cases
  - Neighborhood mapper: 100% coverage, tests for tag overlap, price fit, and walk/transit scoring
- All tests are runnable and non-flaky on CI (GitHub Actions).

### Analytics

- The app emits a `recommend_submitted` event to PostHog on every successful query submission, allowing tracking of user engagement.
- Affiliate link clicks are tracked via the partner networks' pixels (no custom tracking code needed).

---

## Key Entities

### Intent

```
{
  budgetMin: number (USD, >= 0),
  budgetMax: number (USD, >= budgetMin),
  bedroomsMin: number (>= 1),
  bedroomsMax: number (>= bedroomsMin),
  lifestyleTags: string[] (canonical tags from predefined catalog: walkable, quiet, tech_hub, family_friendly, urban, suburban, near_schools, pet_friendly, modern_amenities, good_schools, low_crime, nightlife, cultural, green_space, waterfront, beach, mountains, golf_courses, retirement_community, co_working_spaces, etc.),
  mustHaves: string[] (non-negotiables, free-form user text that will be mapped to canonical amenities during scoring),
  niceToHaves: string[] (desirable, free-form user text),
  commuteTarget?: { location: string, maxMinutes: number }
}
```

### NormalizedListing

```
{
  id: string (unique within source),
  sourceUrl: string (canonical URL at source),
  address: string,
  price: number (USD),
  bedrooms: number,
  bathrooms: number,
  squareFeet: number,
  photoUrl: string,
  source: "realtor" | "apartments" | "other",
  listedDate: Date,
  amenities: string[] (canonical amenities from predefined catalog, sourced from Google Places API: pool, gym, parking, rooftop, doorman, elevator, laundry_in_unit, dishwasher, air_conditioning, heating, balcony, patio, fireplace, game_room, home_theater, etc.)
}
```

### NeighborhoodScore

```
{
  neighborhood: string (name or zip code),
  score: number (0 to 1),
  components: {
    tagOverlap: number,
    priceBandFit: number,
    walkTransitFit: number
  }
}
```

### ListingScore

```
{
  listing: NormalizedListing,
  score: number (0 to 100),
  explanation: string (2 sentences max),
  tradeoff: string (1 sentence)
}
```

---

## Assumptions

### Data and APIs

- Neighborhood catalog: Static JSON file (`src/data/neighborhoods.json`) containing ~50–100 SF Bay Area neighborhoods with basic metadata (name, zip code, region). Loaded at deploy time.
- Walk Score API returns a numeric score 0–100 for any valid address. First request for a neighborhood walks/transits score is cached in Upstash Redis (6-hour TTL).
- Median neighborhood price is sourced from RealEstateAPI or market data APIs. First request is cached in Upstash Redis (6-hour TTL).
- RealEstateAPI.com reliably returns normalized JSON listings with the fields required by NormalizedListing (address, price, bedrooms, bathrooms, squareFeet, photoUrl). If a field is missing, the normalizer returns null and the listing is skipped.
- Google Places API returns amenity data (pool, gym, etc.) for locations queried. If amenities are unavailable, the listing is scored without that component.
- Affiliate partner networks (Impact Radius for Realtor.com, CJ Affiliate for Apartments.com) accept URL parameters in the format specified (e.g., `?ref=` and `?cm_mmc=`).

### User Behavior

- Users submit queries in English. Non-English queries are out of scope for v1.
- Users expect results within ~10 seconds; anything slower than 15 seconds is considered unresponsive.
- Users may refine multiple times within the same browser session; the thread ID persists and enables state reuse for the duration of that session.
- Cross-session state recovery (e.g., user returns hours/days later) is out of scope for v1. The old thread ID is discarded and a new session begins.

### Infrastructure

- Neon Postgres is the primary database and also hosts the LangGraph checkpointer tables.
- Upstash Redis is available for caching and rate-limiting.
- LangSmith is configured via environment variables and traces are sent automatically.
- Vercel deployment is the target; the recommend endpoint has a maxDuration of 60 seconds.

### Scope Boundaries

- User authentication is limited to email capture; no full user accounts or saved searches in v1.
- Multi-metro expansion is deferred; v1 targets San Francisco Bay Area only.
- Only RealEstateAPI.com is the listings source for v1; ATTOM Data is added only after monthly revenue clears cost threshold.
- No second LLM provider as fallback in v1; all LLM calls use Anthropic Claude.

---

## Out of Scope (v1)

- User accounts and authentication beyond email capture
- Saved searches and email alerts
- Multi-city or multi-state support
- Native mobile apps (web responsive only)
- White-label or tenancy models
- A second LLM provider as fallback
- Self-hosted LangGraph Platform
- Vector search over listing descriptions
- Custom MLS partnerships
- Multi-language support

---

## Constraints

### Business Constraints

- Launch metro: San Francisco Bay Area
- Primary listings source: RealEstateAPI.com
- Affiliate partners: Realtor.com (Impact Radius), Apartments.com (CJ Affiliate)
- Rate limit: 60 requests per hour per IP (via Upstash Ratelimit)

### Technical Constraints

- All LLM calls use Anthropic models only (Claude Sonnet for parsing/routing, Claude Opus for explanation).
- All external API calls have a 5-second timeout and max 2 retries with exponential backoff.
- Database and state checkpointer are Neon Postgres only.
- LangGraph nodes never throw exceptions; errors are returned via state.
- No blocking operations in route handlers; all I/O is async.

---

## Testing Strategy

### Unit Tests (Pure Skills)

1. **Listing Normalizer**: Test valid input shapes, missing required fields, edge cases (price = 0, bedrooms = 0.5), null handling.
2. **Scoring Engine**: Test all weight components, edge cases (intent with no constraints, all listings identical price), score range validation (0–100).
3. **Neighborhood Mapper**: Test tag overlap calculation, price band fit with various budget ranges, walk/transit scoring.

All unit tests use inline fixtures (no shared setup files) and Vitest.

### Integration Tests

1. **End-to-End Graph Test**: Mock all external clients (RealEstateAPI, Walk Score, Google Places, Anthropic), invoke graph.invoke with a test intent, assert the returned state contains exactly three explained listings with scores and tradeoffs.

### Manual Smoke Tests

1. Submit a real query on staging and verify three recommendations appear in under 10 seconds.
2. Click an affiliate link and verify the tracking parameters are appended and the user lands on the correct partner site.
3. Submit a refinement and verify the response reuses prior intent (check LangSmith trace to confirm parse-intent node was skipped).
4. Trigger an error (e.g., by rate-limiting the API) and verify the UI renders a fallback message instead of crashing.

---

**Status**: Ready for planning phase. All mandatory sections completed. No [NEEDS CLARIFICATION] markers present; all user requirements and success criteria are concrete and testable.
