---
applyTo: "**"
---

# Style guide

Applies to all generated prose, code comments, commit messages, PR descriptions, and chat responses.

## Banned words and phrases

Never use any of these:

delve, unlock, leverage, tapestry, navigate (figurative), embark, journey (figurative), realm, landscape (figurative), seamlessly, elevate, empower, ensure (when "make" works), robust, comprehensive (as filler), holistic, synergy, paradigm, pivotal, crucial, vital (as filler), it's worth noting, in conclusion, in summary, at the end of the day, when it comes to, in today's fast-paced world, in the ever-evolving, dive into, dive deep, deep dive, game-changer, cutting-edge, state-of-the-art, best-in-class, world-class, mission-critical, low-hanging fruit, move the needle, circle back, touch base, going forward.

## Banned patterns

- Negative parallelism: "It's not X, it's Y." Drop the X half. Just say Y.
- Em dashes anywhere. Use a comma, a period, parentheses, or a colon.
- Paragraphs longer than three sentences.
- Bullet lists where two sentences of prose would carry the same information.
- Hedging stacks: "might possibly perhaps approximately."
- Throat-clearing openers: "Great question," "Certainly," "Of course," "Let me think about this."
- Restating the question before answering.
- Closing summaries that repeat what was just said.

## Code style

- Named exports only. No default exports.
- Pure functions where the work allows.
- Early returns over nested conditionals.
- One concern per file.
- Avoid abbreviations in names. Exceptions: `id`, `url`, `db`, `ui`, `api`, standard acronyms.
- Prefer explicit types on public surfaces. Inference inside function bodies is fine.

## Stack-specific code rules

- LangGraph nodes return `Partial<State>`. Never mutate state in place.
- LangChain model instances are module-level singletons. Never instantiate inside a node body.
- Every LLM call binds a Zod schema via `withStructuredOutput`. Free-form text replies are not accepted.
- Pure deterministic logic lives under `src/skills/`. Nodes orchestrate, skills compute.
- React Server Components by default. Mark client components with `'use client'` only when they need browser APIs, state, or effects.
- Tailwind utility classes inline. No CSS modules. No styled-components. Single `globals.css` for tokens and resets.
- shadcn components are owned in `src/components/ui/`, not imported from a package. Edit them in place when you need a variant.

## Comments

- Comment the why, never the what.
- No comments that paraphrase the next line.
- `TODO` must include an owner and date: `// TODO(alice 2026-05-27): drop after migration ships`.
- Delete dead code. Do not comment it out.

## Commits

- Imperative mood: "Add X", not "Added X" or "Adds X".
- One logical change per commit.
- Subject under 72 characters.

## Self-audit

After generating any prose or code, scan the output against every rule above. Rewrite hits inline before returning. If you cannot remove a banned word without losing meaning, flag it and propose two alternatives.

## Trigger phrase

When I write "audit this against the style guide," scan the supplied text against every rule above and return a numbered list of hits with proposed rewrites.
