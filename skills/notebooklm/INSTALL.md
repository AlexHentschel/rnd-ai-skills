# notebooklm skill — install & operate

This is the **research-notebook query tool** the `paper-claim-validation` skill depends on. It is a
**vendored, patched copy** of an external MIT-licensed skill — see `UPSTREAM.md` for provenance, the
full patch record, and the upstream-update procedure. This file is just how to stand it up and run it.

## Install
1. This skill ships **inside this repo** (vendored, already patched) — no separate clone needed. The
   upstream link + our changes are recorded in `UPSTREAM.md`; the original MIT `LICENSE` is retained here.
2. Place this skill where your host discovers skills (Claude Code: `~/.claude/skills/notebooklm/`;
   Cursor: `~/.cursor/skills/notebooklm/`). Share one copy across both hosts via a symlink if you use both.
3. **Build the venv FIRST, before you invoke the skill** — a **symlink** venv (not `--copies`) on a
   **stable interpreter** (one your package manager won't auto-remove). Do this manually:
   ```bash
   cd <skill-dir>
   rm -rf .venv
   <stable-python> -m venv .venv          # symlink, NOT --copies
   .venv/bin/python -m pip install --upgrade pip
   .venv/bin/pip install -r requirements.txt
   .venv/bin/python -m patchright install chrome   # browser driver — Chrome, not Chromium
   ```
   - **Why build it yourself (FM-1).** If you skip this and just invoke the skill, `run.py` auto-creates
     `.venv` using *whatever `python` launched it* — often a package-manager Python that a later point-bump
     removes, which then breaks every script (see `UPSTREAM.md` § Environment). Building a symlink venv on a stable
     interpreter up front avoids that; `run.py` reuses an existing `.venv` and won't rebuild it.
   - **Why the last line.** The tool drives Chrome (`channel="chrome"`), not Chromium. The skill's own
     `setup_environment.py` runs `patchright install chrome` automatically — but **only when it builds the
     venv**, so a manual build skips it. Run it yourself. If a query fails to launch a browser, re-run that
     line (or ensure system Google Chrome is installed).
4. Authenticate (visible browser, manual Google login):
   ```bash
   .venv/bin/python scripts/run.py auth_manager.py setup
   ```
5. Register/activate your notebook (the one fed with the paper's source corpus), then **always pass it
   explicitly** on queries (URL or ID) — do not rely on the "active notebook" default.
6. Smoke-test: `auth_manager.py status` → one scoped `ask_question.py` query.

## Corrections to the stock skill docs (do not trust these stock lines)
| Stock claim | Reality |
|---|---|
| "Rate limit (50/day)" | Free-tier figure. **Pro ≈ 500/day** (confirm your tier). Effectively non-binding for single-paper validation. |
| "Chromium installs automatically" / `patchright install chromium` | We launch **system Google Chrome** (`channel="chrome"`). No Chromium download. |
| "No session persistence (each question = new browser)" | **False** — the persistent profile retains chat history (root cause of the stale-answer bug, FM-2). |

## Cross-host (Cursor IDE + Claude Code) from one source
Both hosts read `skills/<name>/SKILL.md` (frontmatter treated as a union — each host uses the fields it
knows). Share one maintained copy via a **symlink** between `~/.claude/skills/<name>` and
`~/.cursor/skills/<name>`. (The Claude.ai **web** product uses a different mechanism — not covered here.)

## Machine-local, never copy
Auth cookies (`data/`), the `.venv`, and the active-notebook setting are **per-machine** — recreate them
on your side; never copy another machine's.

## Operational reminders
- Run `auth_manager.py status` at session start. Sessions last up to ~7 days; a tens-of-hours-old state
  is normal — do **not** pre-emptively re-auth (FM-5). Only an auth-wall error on a real query means
  re-auth (FM-4, interactive visible browser).
- Transient single-query error → retry once with the exact same prompt; if it recurs, pause (FM-6).
- Use `run.py` (or the venv python directly) so the environment is set up; never call scripts bare.

Full symptom→fix table (tool-agnostic): `../paper-claim-validation/reference/troubleshooting.md`.
Provenance + patch record + upstream-update procedure: `UPSTREAM.md`.
