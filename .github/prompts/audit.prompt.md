---
mode: ask
description: Scan supplied text or code against the style guide and return a list of hits with rewrites.
---

# /audit

Scan the supplied text or code against every rule in `.github/instructions/style-guide.instructions.md`.

For each violation, output:

1. The location (line number, or quoted phrase if no line numbers)
2. Which rule was broken
3. A proposed rewrite

Format the output as a numbered list, one entry per violation. No preamble. No closing summary.

If the input passes clean, respond with exactly: `Clean. No style guide violations found.`

Pay special attention to:

- Banned words and phrases
- Em dashes
- Negative parallelism ("It's not X, it's Y")
- Paragraphs longer than three sentences
- Throat-clearing openers
- Closing summaries
- Code style violations (default exports, deep nesting, abbreviations)
- Stack-specific rules (mutating state in nodes, free-form LLM text parsing, model instances inside node bodies)

---

Text or code to audit:

${input:content:Paste the content here}
