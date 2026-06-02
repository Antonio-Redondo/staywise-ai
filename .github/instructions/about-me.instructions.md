---
applyTo: "**"
---

# About me

## Background

- Role: Builder shipping an AI-native housing recommendation product. Hands-on across frontend, agent layer, and infra.
- Years writing code: 8+
- Primary stack: TypeScript 5+, Node 22 LTS, Next.js 15 (App Router), Postgres
- Secondary stacks I touch: SQL, shell, occasional Python for data exploration
- LLM and agent framework experience: Working in LangChain and LangGraph (TypeScript). Comfortable with the Anthropic SDK directly and with the Vercel AI SDK for streaming UIs. Building my first production multi-agent pipeline with this project.
- Editor and OS: VS Code on macOS, with GitHub Copilot as the daily driver
- Hardware constraints: None

## How I work

- Branching model: GitHub Flow. Trunk-based with short-lived feature branches and PRs into `main`. Vercel preview deploys on every PR.
- Commit style: Conventional Commits (`feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`). Subject in imperative mood, under 72 characters. One logical change per commit.
- Testing philosophy: Pure functions in `src/skills/` get full unit coverage. Nodes get one focused test each with mocked clients. The compiled graph gets a single end-to-end test using `MemorySaver`. Boundary tests beat middle tests; if it touches an LLM or an external API, it gets a test.
- CI tools: GitHub Actions for lint, typecheck, test on every PR. Vercel for preview and prod deploys.
- Tools I rely on outside the editor: GitHub for repo and issues, LangSmith for LLM trace inspection, Sentry for runtime errors, PostHog for product analytics, Linear for planning, Notion for longer-form docs.

## How I write code

- Naming conventions: Verbose over abbreviated. Allowed short names: `id`, `url`, `db`, `ui`, `api`, standard acronyms. `camelCase` for variables and functions, `PascalCase` for types, components, and Zod schemas, `SCREAMING_SNAKE_CASE` for module-level constants.
- Comment density: Low. Comment the why, never the what. No comments that paraphrase the next line. `TODO` includes an owner and date.
- Function size ceiling: ~40 lines. Past that, extract a helper or move logic into a skill.
- File size ceiling: ~250 lines. One concern per file.
- Patterns I like: Named exports, pure functions, early returns, Zod schemas as the source of truth for shape, module-level singletons for model and client instances, structured logging with a request ID propagated through the graph.
- Patterns I dislike: Default exports, deeply nested conditionals, mixed concerns in one file, free-form text parsing from LLM responses, mutating state in place inside a LangGraph node, instantiating model clients inside loops or node bodies.

## How I write prose

- Doc format: Markdown. README at the root, ADRs in `docs/adr/` for non-trivial decisions, runbooks in `docs/runbooks/` for ops procedures. PR descriptions follow a short template: what changed, why, how to test.
- Tone: Direct and terse. Same anti-AI rules from the style guide apply to all my prose: no banned words, no em dashes, no negative parallelism, three-sentence paragraph cap.
- Audience for most docs: Future me, future contributors, and Copilot. Write for the reader who has the codebase open but not the context.

## How to talk to me

- Skip preamble. Lead with the answer.
- Show diffs, not full files, when editing.
- Cite file paths and line numbers when explaining changes.
- If I am wrong, say so directly. Do not soften it.
- When you finish a task, stop. Do not ask if I want more.
- For multi-step work, plan first in one short paragraph, then execute. Do not silently expand scope.
- Surface tradeoffs explicitly. When two approaches are reasonable, name both and recommend one with a one-line reason.
- When suggesting a library, name the version you assume. Flag it if you have not verified the version is current.
- Use the `/refine` prompt before pasting any messy prompt into a new chat.
