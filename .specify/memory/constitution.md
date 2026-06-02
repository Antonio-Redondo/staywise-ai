<!--
SYNC IMPACT REPORT — Constitution v1.0.0

Created: 2026-05-28 (inaugural constitution)
Previous version: none (greenfield project)
Version bump: 1.0.0 (initial ratification)

Principles established:
- 10 code principles (TypeScript, named exports, Zod, pure skills, structured outputs, singletons, PostgresSaver, style guide, env vars, PR gates)
- 4 process principles (linear workflow Spec→Plan→Tasks→Implement, tests prove completion, state errors, manual verification)
- 2 LLM models locked in (Sonnet for parsing/routing, Opus for explanation)

Binding instruction files referenced (no duplication):
- .github/instructions/style-guide.instructions.md (prose, code comments, banned words, banned patterns)
- .github/instructions/project-context.instructions.md (quarterly targets, stack lock-ins, scope, env vars)
- .github/instructions/langgraph.instructions.md (node contract, state definition, error handling)
- .github/instructions/ui.instructions.md (component patterns, styling, server vs client)
- .github/instructions/db.instructions.md (schema, migrations, Drizzle)

Templates requiring verification:
- .specify/templates/plan-template.md: mentions "Constitution Check" gate — ✅ verified, Constitution Check should assert TypeScript strict, test coverage, Zod boundaries
- .specify/templates/spec-template.md: user stories with priorities — ✅ verified, aligns with linear workflow
- .specify/templates/tasks-template.md: note says "Tests are OPTIONAL" — ⚠️ UPDATE NEEDED: Constitution requires tests on every PR; this template guidance is outdated
- .specify/templates/checklist-template.md: not reviewed for this report

Deferred items: none

Follow-up actions:
1. Update tasks-template.md note to reflect mandatory testing requirement (Principle X)
2. Ensure /speckit.implement enforces test verification before marking tasks done
-->

# StayWiseAI Constitution

A housing recommendation app built with LangGraph and Next.js. Users describe what they want in natural language; the app returns three matched listings with explanations and affiliate links to the source listing site.

See [.github/instructions/project-context.instructions.md](.github/instructions/project-context.instructions.md) for the quarterly roadmap, target metrics, and stack lock-ins. See [.github/instructions/style-guide.instructions.md](.github/instructions/style-guide.instructions.md) for prose and code style rules.

## Code Principles

### I. TypeScript Strict Mode
All committed code uses TypeScript strict mode. No `any` types without an inline comment explaining why it is necessary.

### II. Named Exports Only
Every module exports named values only. Default exports are prohibited. Enables clear re-exports, simplifies circular dependency debugging, and supports partial module imports.

### III. Zod Schemas as Source of Truth
Zod schemas define the shape of every external boundary: LLM responses, route handler inputs, environment variables, third-party API responses, and database queries via Drizzle. Schemas are defined first; types are inferred from them, never hand-written.

### IV. Pure Skills, Orchestrated Nodes
All deterministic business logic lives in `src/skills/` as pure functions with no side effects. LangGraph nodes in `src/graph/nodes/` orchestrate only; they call skills and external clients but contain no logic that could be a pure function.

### V. Structured Output from Every LLM Call
Every call to an LLM model binds a Zod schema via `withStructuredOutput`. Free-form text parsing is prohibited. All models are sourced from `@langchain/anthropic` with the temperature and model configured in this constitution.

### VI. Model Instances as Module-Level Singletons
LLM model instances (e.g., `claudeSonnet`, `claudeOpus`) are created once at module scope in `src/clients/anthropic.ts`. Never instantiate models inside a node body, loop, or function. Export the instances as named exports; import them in nodes where needed.

### VII. Production State Persistence
Production LangGraph deployments use `PostgresSaver` for state checkpointing. Development and tests use `MemorySaver` only. The production database is Neon Postgres. See [.github/instructions/db.instructions.md](.github/instructions/db.instructions.md) for schema and migration rules.

### VIII. Style Guide Compliance
All generated prose (code comments, commit messages, PR descriptions, user-facing copy) adheres to [.github/instructions/style-guide.instructions.md](.github/instructions/style-guide.instructions.md). Comments explain the why, never the what. No banned words. No em dashes, no hedging, no throat-clearing openers.

### IX. Environment Variables are Explicit
New environment variables require three updates in the same PR: definition in `.env.example`, documentation in [.github/instructions/project-context.instructions.md](.github/instructions/project-context.instructions.md), and runtime read from `process.env` with Zod validation. No magic strings, no undocumented vars.

### X. Pull Request Quality Gate
Every PR must pass `pnpm test`, `pnpm lint`, `pnpm typecheck`, and `pnpm build` before merging. CI enforces this via GitHub Actions. Manual smoke tests are required for agent and UI changes before approval.

## Process Principles

### Linear Workflow: Spec → Plan → Tasks → Implement
Features are built in order: write the spec first (what), then the plan (how), then the task list, then the code. Skipping phases is not allowed. If implementation reveals the spec is wrong, update the spec first before continuing.

### Tests Prove Completion
A task is not done until tests pass and the verification step passes. Stub implementations are rejected. The constitution requires proof: green test output, type check output, and build output before claiming any task complete.

### State Errors Over Exceptions
LangGraph nodes do not throw exceptions on expected failures. They return `{ errors: ['node-name: message'] }` and let downstream nodes decide whether to continue. This allows graceful degradation and better error reporting to the frontend.

### Manual Verification After Every Implementation
After every `/speckit.implement` run, manually verify before declaring the feature done:
- Run `pnpm test`
- Run `pnpm typecheck`
- Run `pnpm build`
- Run a smoke test (manual UI test for frontend changes, graph trace inspection for agent changes)

## LLM Models and Temperature

- `claude-sonnet-4-6` for parsing and routing nodes (temperature 0.2)
- `claude-opus-4-7` for the explanation node (temperature 0.4)
- Never exceed temperature 0.7 in production
- Model overrides require a written reason in the PR description

## Scope and Stack References

For code style, testing discipline, and file layout, see [.github/instructions/style-guide.instructions.md](.github/instructions/style-guide.instructions.md), [.github/instructions/langgraph.instructions.md](.github/instructions/langgraph.instructions.md), [.github/instructions/ui.instructions.md](.github/instructions/ui.instructions.md), and [.github/instructions/db.instructions.md](.github/instructions/db.instructions.md). These instructions are binding for their respective scopes. Do not paraphrase or override them.

For quarterly targets, stack lock-ins, and what to say no to, see [.github/instructions/project-context.instructions.md](.github/instructions/project-context.instructions.md).

## Governance

This constitution supersedes all other development practices except the binding instruction files listed above. All PRs must comply with the code and process principles above. Amendments to this constitution require updating the version number, `LAST_AMENDED_DATE`, and a brief entry in the Sync Impact Report comment at the top of this file.

**Version**: 1.0.0 | **Ratified**: 2026-05-28 | **Last Amended**: 2026-05-28
