## What changed

<!-- One paragraph. What this PR does. -->

## Why

<!-- One paragraph. The problem this solves or the user-facing reason. -->

## How to test

<!-- Steps the reviewer can follow to verify locally. Include commands or URLs. -->

## Checklist

- [ ] Tests pass locally (`pnpm test`)
- [ ] Lint clean (`pnpm lint`)
- [ ] Typecheck clean (`pnpm typecheck`)
- [ ] Self-audited against the style guide (run `/audit` in Copilot Chat)
- [ ] Affected `.github/instructions/*.md` files updated if architecture or scope changed
- [ ] New env vars added to `.env.example` and to `project-context.instructions.md`
- [ ] LangSmith trace inspected if the change touches the agent layer
- [ ] No banned style-guide words in user-facing copy or commit messages
