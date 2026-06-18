# Troubleshooting a research notebook (symptom → cause → fix)

Querying a research notebook (e.g. NotebookLM via the `notebooklm` tool skill) has failed for *different*
reasons across sessions; each was diagnosed once and then re-met cold. This is the consolidated
pre-flight checklist — match the symptom before concluding "the notebook is broken".

**Run-order at session start (cheap → expensive):** (1) tool/environment health → (2) auth status →
(3) one scoped query → only then conclude. Most "notebook down" reports are an environment break or a
false alarm, not a notebook-side outage.

## FM-1 — tool environment broken after a base-interpreter change
- **Symptom.** Any tool script aborts immediately (e.g. exit 134 / `Abort trap: 6`) with a dynamic-linker
  error: a library/framework path "not loaded" / "no such file".
- **Cause.** The tool's Python virtualenv was pinned to a base interpreter whose install dir the OS /
  package manager later removed (classic with Homebrew Python point-bumps + a `--copies` venv).
- **Fix.** Rebuild the venv on a **stable, self-managed interpreter** (one the package manager won't
  auto-remove) using a **symlink venv (NOT `--copies`)**:
  ```bash
  cd <tool-skill-dir>
  rm -rf .venv
  <stable-python> -m venv .venv     # symlink, not --copies
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/pip install -r requirements.txt
  ```
  Avoid the package-manager's auto-upgraded `python3.x` + `--copies` combination — that is the failure.

## FM-2 — answer is off-topic / a stale prior answer
- **Symptom.** A query returns content about the *wrong* topic — often a previous answer from the same
  notebook. A capture problem, not a content problem.
- **Cause.** A scraper that picks the "last" chat element can return a stale historical one, because the
  UI may not render message pairs in chronological order and a persistent browser profile retains chat
  history.
- **Fix.** Use a scraper that tags pre-existing message pairs before submitting and selects only the new
  pair, then polls until the text settles. If you still see stale answers, retry once, then inspect with
  a visible browser.

## FM-3 — answer is truncated / partial
- **Symptom.** Answer cuts off mid-derivation; a sub-clause you asked for is missing.
- **Cause.** The answer-stability poll ended during a streaming pause (a brief gap looked "settled").
- **Fix.** Raise the stability-poll threshold; for a load-bearing claim, **re-run the exact query** —
  do not proceed on the partial. (Distinct from a truncated *prompt* — see the prompt-truncation guard
  in `prompt-templates.md`.)

## FM-4 — not authenticated (genuine)
- **Symptom.** A real query (not a status check) fails with an auth-wall / login redirect.
- **Cause.** Stored session cookies expired (sessions can last up to ~7 days).
- **Fix.** Re-run the tool's auth setup. **Browser must be VISIBLE** — the human logs in manually. Tell
  them first: "A browser window will open for login." Interactive; do not attempt headless.

## FM-5 — *false* auth-expiry alarm (do nothing)
- **Symptom that is NOT a failure.** Auth-state age of tens of hours; or the public landing page shows
  "Sign in".
- **Why benign.** Sessions last ~7 days; a multi-hour-old state is normal, and the public landing page
  is not evidence of an expired session.
- **Fix.** Nothing. Only an actual auth-wall error on a query (FM-4) justifies re-auth. Pre-emptive
  re-auth wastes an interactive human round-trip.

## FM-6 — transient single-query timeout/error
- **Symptom.** One query times out/errors; neighbours are fine.
- **Fix.** **Retry once with the exact same prompt** (rephrasing conflates transport failure with a
  content problem). If it recurs across queries, pause and notify the human.

## FM-7 — query hit the wrong corpus
- **Symptom.** Plausible-but-irrelevant answer; sources don't match expectations.
- **Cause.** Relied on the tool's "active notebook" default; multiple notebooks exist.
- **Fix.** Always pass the target notebook explicitly (URL/ID). Confirm the notebook at task start.

## FM-8 — every query fails to launch the browser (`ProcessSingleton` / stale lock)
- **Symptom.** Every query aborts before reaching the notebook with a browser-launch error like
  `Failed to create .../SingletonLock: File exists` / `Failed to create a ProcessSingleton for your
  profile directory`.
- **Cause.** A *previous* query was killed or timed out (e.g. a very long prompt that exceeded a wrapper
  timeout) and left an **orphaned browser process** holding the persistent profile's singleton lock. The
  lock outlives the killed run and blocks all subsequent launches against that profile.
- **Fix.** Kill any orphaned browser bound to the tool's profile dir, then remove the stale lock files:
  ```bash
  PROFILE=<tool-skill-dir>/data/browser_state/browser_profile
  pkill -f "user-data-dir=$PROFILE"        # kill the orphan + its helpers
  rm -f "$PROFILE"/SingletonLock "$PROFILE"/SingletonCookie "$PROFILE"/SingletonSocket
  ```
  Then retry the query. **Prevention:** size any wrapper timeout to the prompt — the tool types prompts at
  human typing speed, so a multi-thousand-character prompt takes *minutes* to enter; an aggressive timeout
  kills mid-run and orphans the browser. Prefer concise prompts (also see the prompt-truncation guard in
  `prompt-templates.md`).
