# `.github/` — Complete Copilot configuration for the housing recommendation app

Everything you need to build the app with GitHub Copilot. Drop this folder into your repo root; Copilot picks up the configuration automatically.

## Two ways to build

You have two workflows. Pick one or mix them.

### Path A — GitHub Spec Kit (recommended)

Specification-driven. You describe the system, Spec Kit generates the plan and tasks, Copilot implements. Read **`SPECKIT.md`** for installation and the exact prompts to paste at each step.

### Path B — Direct prompts (lower ceremony)

Paste pre-written prompts into Copilot Chat in order. Read **`EXECUTION.md`** for the runbook and **`PROMPTS.md`** for the full prompt sequence.

Both paths use the same underlying `.github/instructions/` files. Spec Kit operates at a higher level; direct prompts operate one step at a time. Spec Kit is better for the full initial build and for new features; direct prompts are better for small changes, debugging, and exploration.

## Start here

| You want to... | Open |
|---|---|
| Build with Spec Kit | `SPECKIT.md` |
| Build with direct prompts | `EXECUTION.md` (runbook) + `PROMPTS.md` (prompts) |
| Understand the system | `ARCHITECTURE.md` |
| Set up your machine and accounts | `EXECUTION.md` Parts 1-5 |
| Deploy to production | `EXECUTION.md` Part 11 onward |

## Full file inventory

### Documentation (you read these)

| File | Purpose |
|---|---|
| `README.md` | This file |
| `SPECKIT.md` | Spec Kit workflow with the exact prompts for this project |
| `EXECUTION.md` | Step-by-step runbook from empty repo to launch |
| `PROMPTS.md` | Every direct Copilot prompt in order |
| `ARCHITECTURE.md` | System diagrams, state flow, deployment topology |

### Copilot instructions (Copilot reads these automatically)

| File | Loads when |
|---|---|
| `copilot-instructions.md` | Every Copilot interaction in this repo |
| `instructions/about-me.instructions.md` | Every file |
| `instructions/project-context.instructions.md` | Every file |
| `instructions/style-guide.instructions.md` | Every file |
| `instructions/langgraph.instructions.md` | Editing `src/graph/`, `src/skills/`, `src/clients/` |
| `instructions/ui.instructions.md` | Editing `src/app/`, `src/components/` |
| `instructions/db.instructions.md` | Editing `src/db/`, `drizzle/` |

### Slash commands (you invoke these in Copilot Chat)

| Command | What it does |
|---|---|
| `/refine` | Rewrite a messy prompt into a tight executable one |
| `/audit` | Scan code or text against the style guide |
| `/new-node` | Scaffold a new LangGraph node with prompt and test |
| `/new-skill` | Scaffold a new pure-function skill with tests |

When you install Spec Kit (see `SPECKIT.md`), four more slash commands appear: `/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`, plus `/speckit.clarify`, `/speckit.checklist`, `/speckit.analyze`.

### Repo infrastructure (GitHub reads these automatically)

| File | Purpose |
|---|---|
| `workflows/ci.yml` | Typecheck, lint, test, build on every PR and push to main |
| `PULL_REQUEST_TEMPLATE.md` | Structured PR description with verification checklist |
| `dependabot.yml` | Weekly grouped dependency updates |

## How the pieces fit

When you ask Copilot anything in this repo, it reads `copilot-instructions.md` first. That file points it at the instructions files whose `applyTo` glob matches what you are editing. Style guide and project context apply everywhere. The LangGraph, UI, and DB files load only for their respective directories, so Copilot's context window stays focused on what matters.

The four custom slash commands and (after install) the eight Spec Kit slash commands show up in Copilot Chat once the files are committed.

## The recommended build flow

1. Drop `.github/` into a fresh repo, commit, push.
2. Open in VS Code with Copilot Chat. Ask "What is the architecture of this project?" to verify Copilot reads the instructions.
3. Read `ARCHITECTURE.md` (10 min) so you have the mental model.
4. Decide on Path A or Path B above. **For a fresh build, Path A (Spec Kit) handles more of the orchestration for you.**
5. Personalize `about-me.instructions.md` and adjust `project-context.instructions.md` if the defaults do not match your plan.
6. Provision the eight external services in `EXECUTION.md` Part 5.
7. Follow `SPECKIT.md` or `PROMPTS.md` to do the build.
8. Deploy following `EXECUTION.md` Part 11 onward.
9. Run the pre-launch checklist before announcing the URL.

## Ongoing development

Regardless of which build path you used, day-to-day:

- Run messy ideas through `/refine` before pasting them into a new chat
- Run generated code or copy through `/audit` before committing
- Use `/new-node` or `/new-skill` for additions; or `/speckit.specify` for larger features
- Update the relevant `instructions/*.md` file in the same PR as any architectural change

## Updating

| File | Update when |
|---|---|
| `about-me.instructions.md` | Tooling or preferences change |
| `project-context.instructions.md` | Every quarter, or when scope shifts |
| `style-guide.instructions.md` | You catch new AI-cliche words in Copilot output |
| `langgraph.instructions.md` | Agent layer architecture changes |
| `ui.instructions.md` | Frontend stack changes |
| `db.instructions.md` | Schema patterns or ORM changes |
| `EXECUTION.md` | After completing each part, so future you can retrace |
| `PROMPTS.md` | When you add a new build phase |
| `ARCHITECTURE.md` | When the pipeline topology changes |
| `SPECKIT.md` | When the Spec Kit version bumps or commands change |
