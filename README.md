# ah-ai-skills

A dedicated repository of reusable AI skills (for **Cursor IDE** and **Claude Code**), cloned by
collaborators. It will accrue multiple skills over time; the first capability is **research-notebook
claim validation** for scientific papers.

## The first capability — NotebookLM claim validation (two-layer)
- **Tool layer — `skills/notebooklm/`** — a vendored, **patched copy** of an external MIT-licensed
  NotebookLM query skill (browser automation: auth, ask, scrape). Provenance + patch record +
  upstream-update procedure: `skills/notebooklm/UPSTREAM.md`; install/operate: `skills/notebooklm/INSTALL.md`.
- **Methodology layer — `skills/paper-claim-validation/`** — how to use the notebook for rigorous
  per-claim validation and clearer, less-jargon rephrasing. Entry point: its `SKILL.md`.
- **Always-on safeguard — `CLAUDE.md-snippet.md`** — paste into your `CLAUDE.md` / always-apply rule.

## Layout
```
ah-ai-skills/
├── README.md
├── CLAUDE.md-snippet.md                 ← paste into your CLAUDE.md / always-apply rule (do this!)
└── skills/
    ├── notebooklm/                      ← vendored + patched tool skill (MIT; see UPSTREAM.md/LICENSE)
    │   ├── UPSTREAM.md                  ← upstream ref + license + patch record + weekly-update check
    │   ├── INSTALL.md                   ← install / auth / operate; corrections to stock docs
    │   └── SKILL.md, scripts/, references/, LICENSE, requirements.txt  ← vendored skill files
    └── paper-claim-validation/          ← methodology skill (generic; persona-neutral)
        ├── SKILL.md
        └── reference/
            ├── per-claim-validation-loop.md
            ├── prompt-templates.md
            └── troubleshooting.md
```

## Install
1. Clone `ah-ai-skills`.
2. **Tool skill** — place `skills/notebooklm/` where your host discovers skills; build its venv and
   authenticate against *your* notebook (corpus fed with the paper's sources). Follow
   `skills/notebooklm/INSTALL.md` (note the symlink-venv requirement + the corrections to stock docs).
3. **Methodology skill** — place `skills/paper-claim-validation/` likewise. Share one copy across both
   hosts via a symlink if you use Cursor + Claude Code.
4. **Always-on rules** — paste `CLAUDE.md-snippet.md` into your `CLAUDE.md` (Claude Code) or an
   always-apply rule (Cursor). Not optional: a skill is on-demand, so the hard safeguards must also live
   always-on.
5. **Confirm the notebook** you query (pass URL/ID explicitly), then start with the per-claim loop.

## Design notes
- **Two skills, not one, not a plugin.** Tool vs methodology change for different reasons (the tool
  breaks on NotebookLM UI/auth changes; the methodology evolves with review practice) — separating them
  avoids coupled edits. No plugin yet: a plugin earns its place only when bundling always-on reflexes/
  hooks; we ship the always-on part as a `CLAUDE.md` snippet instead (agile-first).
- **Skill A is vendored (patched copy), upstream link kept in docs.** MIT licence permits it; we retain
  the upstream `LICENSE`, keep a direct upstream reference, and a patch record + re-apply instructions in
  `skills/notebooklm/UPSTREAM.md`, which also defines the **≤ weekly** upstream-update check.
- **Licensing.** The repo-root `LICENSE` (MIT) covers this repo's own authored content. The vendored
  `skills/notebooklm/` directory is separately covered by its **retained upstream MIT `LICENSE`** (© Please
  Prompto!) — the root licence does not claim it.
- **A skill is on-demand.** The validation rigor must hold every turn → the `CLAUDE.md` snippet (step 4)
  is what enforces it always-on; do not rely on the skill alone.

## What does NOT carry over
Machine-local state (auth cookies, the tool venv, the active-notebook setting) is per-machine — recreate
it on your side. The notebook **corpus** itself you supply (you already have NotebookLM fed with the same
sources).
