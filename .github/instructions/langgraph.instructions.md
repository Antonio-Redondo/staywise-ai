---
applyTo: "src/graph/**,src/skills/**,src/clients/**"
---

# LangGraph and agent patterns

Load this whenever editing the agent layer.

## State definition

State lives in `src/graph/state.ts` as a single `Annotation.Root`. Each field declares an explicit reducer.

- Scalar fields use the default last-wins reducer.
- Array fields use a concat reducer with a dedupe key where it matters (listings dedupe by `sourceUrl`).
- Error fields use a concat reducer so multiple nodes can append.

The exported `GraphState` type is the inferred type, not a hand-written interface. The annotation is the single source of truth for state shape.

## Node contract

Every node file under `src/graph/nodes/` exports a single async function with this shape:

```ts
export async function nodeNameNode(state: GraphState): Promise<Partial<GraphState>>
```

Rules:

- Nodes never throw on expected failures. They return `{ errors: ['node-name: message'] }` and the next node decides whether to continue.
- Nodes never call other nodes. Routing happens at the graph level via edges.
- Nodes do not read environment variables directly. Clients in `src/clients/` do that.
- Nodes do not contain branching business logic that belongs in a skill. If a node body has more than two real branches, extract a skill.

## LLM call pattern

```ts
import { ChatAnthropic } from '@langchain/anthropic'
import { z } from 'zod'

const model = new ChatAnthropic({
  model: 'claude-sonnet-4-6',
  temperature: 0.2,
})

const schema = z.object({ /* ... */ })

const structured = model.withStructuredOutput(schema, { name: 'ExtractedIntent' })

const result = await structured.invoke([
  { role: 'system', content: SYSTEM_PROMPT },
  { role: 'user', content: state.userQuery },
])
```

Rules:

- Model instances are module-level singletons. Never instantiate inside a node body.
- Every LLM call uses `withStructuredOutput` with a Zod schema. No free-form text parsing.
- System prompts live in `src/graph/nodes/prompts/*.md` and load at module init via `fs.readFileSync` (or a build-time import plugin if configured).
- Temperature: 0.2 for parsing nodes, 0.4 for explanation nodes, never above 0.7.
- Model choice: Sonnet for parsing and routing, Opus for explanation. Override only with a written reason in the PR.

## Graph compilation

```ts
import { StateGraph, START, END } from '@langchain/langgraph'
import { PostgresSaver } from '@langchain/langgraph-checkpoint-postgres'

const checkpointer = PostgresSaver.fromConnString(process.env.DATABASE_URL!)

export const graph = new StateGraph(StateAnnotation)
  .addNode('parse-intent', parseIntentNode)
  .addNode('map-neighborhoods', mapNeighborhoodsNode)
  .addNode('fetch-listings', fetchListingsNode)
  .addNode('score-listings', scoreListingsNode)
  .addNode('explain-top', explainTopNode)
  .addEdge(START, 'parse-intent')
  .addEdge('parse-intent', 'map-neighborhoods')
  .addEdge('map-neighborhoods', 'fetch-listings')
  .addEdge('fetch-listings', 'score-listings')
  .addEdge('score-listings', 'explain-top')
  .addEdge('explain-top', END)
  .compile({ checkpointer })
```

Rules:

- Production builds use `PostgresSaver`. Tests use `MemorySaver`. Never ship `MemorySaver` to prod.
- Add conditional edges only when the routing decision is data-driven. Do not use them for error handling (use the errors field on state instead).
- Keep the topology readable. If you need a diagram to understand it, refactor.

## Observability

LangSmith picks up traces automatically when these env vars are set:

```
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=...
LANGSMITH_PROJECT=housing-rec-prod
```

Do not write custom tracing code. Do not log full state to console; the listings arrays alone will flood your logs. Log structured events with a request ID when extra detail is needed.

## Skills versus nodes

A piece of code belongs in `src/skills/` when all three are true:

1. It is a pure function (no I/O, no LLM, no env vars).
2. It is unit-testable with fixture inputs and deterministic outputs.
3. It would still make sense if you removed the agent layer entirely.

If any of those fail, it belongs in a node, not a skill.

## Client layer

Clients in `src/clients/` wrap external APIs. They are the only place env vars are read.

- One file per external service (`anthropic.ts`, `attom.ts`, `realestate-api.ts`, `walk-score.ts`).
- Each exports typed functions, not raw `fetch` calls scattered through node code.
- Wrap every external call with a timeout via `AbortController`.
- Retry on rate-limit errors with exponential backoff, max two retries.
- Validate every response with Zod before returning.

## Streaming graph updates

For the recommend route handler, use `graph.stream(input, config, { streamMode: 'updates' })`. Pipe each update into an SSE response via the Vercel AI SDK's `createDataStreamResponse`. Each update carries the node name and a partial state.

## Testing

- Skills get full unit coverage with fixture data.
- Nodes get one test each, mocking the model client.
- The compiled graph gets one end-to-end test using `MemorySaver` with all clients mocked.
- LangSmith is disabled in tests.
- Run `pnpm test` before any commit that touches `src/graph/` or `src/skills/`.
