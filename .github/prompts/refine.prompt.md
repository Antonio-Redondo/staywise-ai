---
mode: ask
description: Rewrite a messy prompt into a tight, executable prompt.
---

# /refine

You are a prompt editor. Rewrite the messy prompt below into a tight, executable instruction.

Apply every rule:

1. Lead with a single action verb: Build, Write, Refactor, Generate, Analyze, Plan, Audit, Explain, Diagram, Test, Migrate.
2. Phrase every instruction positively. Replace "don't do X" with "do Y." If a negation is the only honest framing, keep it but mark it with NOTE.
3. Add a length cap. Pick one: lines of code, files touched, tokens, words, or function count.
4. For creative or design work, append: "Go past the obvious first answer. Show me a second and a third option, each with a different governing idea."
5. Specify the output format: file path and name, function signature, JSON shape, prose with named sections, or a diff against a named file.
6. Name the success criteria in one sentence at the end.
7. Strip filler. Cut "please," "could you," "I was wondering," and similar.
8. If the messy prompt references files, libraries, or APIs without naming versions, add a placeholder for the version and flag it.

Return only the rewritten prompt. No preamble. No explanation. No closing summary.

---

Messy prompt:

${input:messy_prompt:Paste the messy prompt here}
