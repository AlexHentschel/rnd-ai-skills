# README — what's here and which file to open

A collection of written guidance for setting up and running an AI assistant well over the long term. This page is the
router: find your goal, open (or point the AI at) the matching file. You need no prior context to use this table — each
file is written to be read on its own. Point the AI at one file; it will follow the links inside to the details.

**Want the full map instead of a router?** Open `00-OVERVIEW.md`.

## Instantiate a persona (start here when creating or adopting one)

> **This tree is the recipe, not the house.** These files are a reference corpus describing *how* to set up
> and run a persona. Instantiating a persona means writing that persona's own files into a target project —
> **do not mutate the files in this tree** when you do it. Treat the corpus as read-only source material.
>
> **First decide which path you are on:**
>
> - **Adopting an already-running persona** (the persona's memory + rules already exist; you are a fresh
>   session onboarding to it) → follow *that persona's* own session-start retrieval. Generic path when it
>   has none of its own: the reading order in `00-OVERVIEW.md`, then `01-MEMORY-SYSTEM.md § Active
>   Retrieval`. **Do not** run the bootstrap templates below — the infrastructure already exists.
>
> - **Creating a new persona from scratch** → **before writing anything, get explicit answers to both:**
>   1. **Which project / workspace should receive the persona's files?** (Do not assume; ask.)
>   2. **Single project, or multiple coexisting projects / workspaces?**
>
>   Then route: **single →** `08-BOOTSTRAPPING.md`; **multiple (or a single-project persona you expect to
>   grow into several) →** `11-MULTI-PROJECT-BOOTSTRAP.md`.
>
> **Host shape.** Where the always-on files physically land depends on the host (Cursor: `.mdc` rules under
> `.cursor/rules/`; Claude Code: `CLAUDE.md` + skills/hooks). `08`/`11` describe the Cursor shape; adapting to
> another host is a known step, not a blocker — see `host-portability.md` (general method) and
> `host-adaptation-claude-code.md` (the worked Claude Code instance).
>
> **Destructive-ops is part of Genesis, not a later add-on.** Instantiating a persona includes an always-on
> hard-gate *stub* (never delete without an explicit per-file grant) plus an empty grant ledger. The full
> protocol, and how it splits across the four persona primitives (identity / memory / capabilities /
> reflexes), lives in `destructive-operations.md`. Point a *different* persona's agent at that file +
> `host-portability.md` §7 — they do not need this corpus's originating persona.

## "I want to…" → open this

| I want to… | Open / point the AI to |
|---|---|
| Get oriented — see everything and how it fits | `00-OVERVIEW.md` |
| Understand why this collection exists and how it was built | `EXTRACTION-PLAN.md` |
| Help the AI improve over time and stop repeating mistakes | `03-SELF-IMPROVEMENT.md` |
| Fix it when the AI's self-improvement itself keeps stalling | `09-RECURSIVE-LEARNING.md` |
| Give the AI memory that carries over between sessions | `01-MEMORY-SYSTEM.md` |
| Reorganize that memory once it grows large or messy | `10-ADAPTIVE-MEMORY-STRUCTURE.md` |
| Tune how the AI communicates and works with you | `02-INTERACTION-STYLE.md` |
| Make the AI handle facts and claims carefully (no overstated certainty) | `04-EVIDENCE-AND-VALIDATION.md` |
| Avoid the common ways the AI goes wrong | `06-FAILURE-MODES.md` |
| Set standards for code and for written documents | `05-CODE-AND-DOCUMENTS.md` |
| Write good commit messages and pull-request descriptions | `pull-request-and-commit-message-authoring.md` |
| Start a brand-new AI setup from scratch (single project) | `08-BOOTSTRAPPING.md` |
| Start or grow an AI setup that spans several projects | `11-MULTI-PROJECT-BOOTSTRAP.md` |
| Move the AI setup to a different host (general method) | `host-portability.md` |
| Adapt the setup to Claude Code (not Cursor) | `host-adaptation-claude-code.md` |
| Make the AI write notes its future self can actually reuse | `cold-ai-paradigm.md` |
| Keep the chat lean — persist task working notes on disk | `working-notes-lean-context.md` |
| Know where the AI's working-notes folder lives, whether it is committed, and that claims in it can still be authoritative | `ai-notes-convention.md` |
| Stop the AI deleting files without an explicit, specific grant | `destructive-operations.md` |
| Write rules that actually change the AI's behavior | `Effective Behavioral Guidelines.md` |
| Get a plan for a task that won't fall apart partway through | `Flexible Plans for AI Execution.md` |
| Have the AI draft a plan, then critique and refine it before acting | `plan-refinement-loop.md` |
| See the big-picture lessons behind all of the above | `07-META-LEARNINGS.md` |

## Notes

- The numbered files (`00`–`11`) are the main guidance, roughly in reading order. The named files are standalone
  topics you reach for when the goal above calls for them. `destructive-operations.md` is one of those: instantiate
  it at bootstrap (`08` / `11`), and keep the hard-gate *sentence* always-on even if the full protocol is on-demand.
- `writes-thinks-speaks.md` is an earlier, narrower take that `cold-ai-paradigm.md` later absorbed — read it only for
  background.
- `exemplary-artifacts/` holds real worked examples referenced by the guidance (e.g. a filled-in plan for
  `plan-refinement-loop.md`).
- If two files seem to overlap, prefer the one whose row matches your goal most exactly; it will point you onward.
