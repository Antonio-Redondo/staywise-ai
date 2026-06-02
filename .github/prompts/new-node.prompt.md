---
mode: edit
description: Scaffold a new LangGraph node following the patterns in langgraph.instructions.md.
---

# /new-node

Create a new LangGraph node following every rule in `.github/instructions/langgraph.instructions.md`.

Generate three files:

1. **`src/graph/nodes/${input:nodeName:Node name in kebab-case, e.g. fetch-listings}.ts`**
   - Export an async function named `${nodeName}Node` (camelCased) with signature `(state: GraphState) => Promise<Partial<GraphState>>`.
   - Return `{ errors: ['${nodeName}: message'] }` on expected failure. Never throw on expected failures.
   - Read only the state fields listed below.
   - Write only the state fields listed below.
   - If using a model, use the module-level singleton from `src/clients/anthropic.ts`. Never instantiate a model inside the function body.

2. **`src/graph/nodes/prompts/${nodeName}.md`** (skip if no LLM call)
   - System prompt that instructs the model how to interpret state and produce output matching the Zod schema.

3. **`tests/graph/nodes/${nodeName}.test.ts`**
   - Vitest test mocking the model client and any external clients.
   - At least one happy-path assertion and one error-path assertion.

Also output the diff to add this node and its edge to `src/graph/index.ts`.

---

**Purpose of this node:** ${input:purpose:One sentence describing what this node does}

**State fields it reads:** ${input:reads:Comma-separated field names}

**State fields it writes:** ${input:writes:Comma-separated field names}

**Model:** ${input:model:sonnet, opus, or none}

**Predecessor node in the graph:** ${input:predecessor:Node name this one runs after}

**Successor node in the graph:** ${input:successor:Node name this one runs before, or END}

---

Success criteria: `pnpm test` passes, `pnpm typecheck` passes, the graph compiles, and the new node respects the singleton-model rule.
