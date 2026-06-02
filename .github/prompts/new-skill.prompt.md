---
mode: edit
description: Scaffold a new deterministic skill (pure function) following the skills-vs-nodes rule.
---

# /new-skill

Create a new pure-function skill following the "skills versus nodes" rule in `.github/instructions/langgraph.instructions.md`.

Before generating, verify all three conditions hold for this skill:

1. It is a pure function (no I/O, no LLM, no env vars, no Date.now or Math.random unless seeded).
2. It is unit-testable with fixture inputs and deterministic outputs.
3. It would still make sense if the agent layer did not exist.

If any condition fails, stop and tell me this should be a node or a client, not a skill.

Generate two files:

1. **`src/skills/${input:skillName:Skill name in kebab-case, e.g. classify-amenity}.ts`**
   - Export a named function. No default export.
   - Explicit type signature on the public surface.
   - Early returns over nested conditionals.
   - JSDoc comment above the function explaining the why, not the what.

2. **`tests/skills/${skillName}.test.ts`**
   - Vitest tests covering at least one happy path, one boundary case, and one rejection case.
   - Inline fixtures, no shared test setup.
   - One assertion per test where reasonable.

---

**Purpose:** ${input:purpose:One sentence describing what this skill computes}

**Input type:** ${input:inputType:TypeScript signature for input}

**Output type:** ${input:outputType:TypeScript signature for output}

**Edge cases to cover in tests:** ${input:edgeCases:Comma-separated list}

---

Success criteria: `pnpm test` passes, `pnpm typecheck` passes, the skill is pure, and tests cover happy path plus edge cases.
