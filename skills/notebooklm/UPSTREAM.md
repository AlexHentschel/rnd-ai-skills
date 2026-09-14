# notebooklm skill — upstream provenance & modifications

Vendored, patched copy of an external open-source skill. This file records where the skill came from,
its license, and how this version differs from upstream — for attribution and so the modifications can
be re-applied when upstream advances.

## Upstream
- **Source:** https://github.com/PleasePrompto/notebooklm-skill
- **Baseline:** commit `eea5cb2` (v1.3.0, 2025-11-21). Our modifications apply on top.
- **License:** MIT — *Copyright (c) 2025 Please Prompto!* (`LICENSE` retained verbatim). MIT permits
  fork / modify / redistribute provided the copyright and permission notice are kept; our modifications
  are additive under the same terms. This file is the required statement of modifications and the link
  back to the source.

## Checking upstream for updates
At most weekly. **Last checked:** 2026-09-08 — upstream unchanged since the baseline. Compare with
`GET /repos/PleasePrompto/notebooklm-skill/compare/eea5cb2...master` (upstream's default branch is
`master`). If upstream has advanced, re-apply the modifications below and update this note.

## Modifications relative to upstream
- **Answer selection** (`scripts/ask_question.py`). The reply is identified by marking the pre-existing
  chat pairs and reading the single new pair, with a hydration wait and a stability poll. Upstream reads
  the document-order last element, which returns stale answers because the persistent profile retains
  chat history.
- **Identity-by-content pair selection** (`scripts/ask_question.py`, 2026-09-08; fallbacks
  tightened 2026-09-09). Late-hydrating *historical* pairs can appear after the pre-submit
  marking and be misidentified as the new answer (observed live: a probe's "new" pair was an
  old "Consider ONLY the publication Timeswap V2…" exchange). Prefer the unmarked pair whose
  **user** message contains the full typed question (whitespace-normalized). If several unmarked
  pairs exist and any user bubble is still empty, keep polling. Several matches, or several
  unmarked with no match → keep polling (document order is not recency). Exactly
  one unmarked pair and no text match → use that pair (user bubble lag).
- **Body-only answer extraction** (`scripts/ask_question.py`, 2026-09-08). The current UI renders the
  bot answer inside `element-list-renderer` as `labs-tailwind-structural-element-view-v2` children plus
  citation `<ul>`s, with a collapsed `thinking-chain-view` ("Thoughts / expand_more") as a sibling.
  Reading whole `.message-text-content` settled on that ~21-char header placeholder before the body
  streamed (reproduced twice; derived from a live DOM probe, not guessed). Extraction joins the
  renderer's children excluding the thinking chain; if no renderer, strips `thinking-chain-view`
  from the message and uses the remainder. Empty body = not yet streamed, keep polling.
- **Multiline prompt entry** (`scripts/browser_utils.py`). Newlines are typed as `Shift+Enter` so a
  multi-paragraph prompt submits as one message. Upstream's per-character typing submits on each newline,
  splitting the prompt into several messages.
- **Prompt-length guard** (`scripts/ask_question.py`). A pre-flight budget check (≤255 words / ≤1900
  chars, overridable with `--allow-long`) plus a post-entry length assertion turn an over-length prompt
  into an explicit, fast failure instead of a silent hang or a truncated question.
- **App domain** (`scripts/auth_manager.py`, `scripts/ask_question.py`). URL matching accepts both
  `notebook.google.com` (current) and `notebooklm.google.com` (which 301-redirects to it), following
  Google's 2026-08 rebrand of NotebookLM to "Gemini Notebook." Upstream hardcodes the old domain, which
  stops matching after login.
- **Docs** (`SKILL.md`, `INSTALL.md`). `SKILL.md` points here and to `INSTALL.md`; `INSTALL.md` corrects
  stale upstream guidance — the rate limit is the free-tier figure (Pro ≈ 500/day), the skill launches
  system Chrome rather than auto-installed Chromium, chat history is retained, and "Gemini Notebook" is
  the same product.

## Not modified (tracked)
- `scripts/browser_session.py` still uses upstream's last-element answer selection. It is off the active
  code path; apply the answer-selection fix there if a future path starts calling it.

## Environment
- `.venv` is machine-local and never vendored. Build it as a symlink venv on a stable interpreter (not a
  package-manager Python that auto-removes on upgrade and breaks the scripts). See `INSTALL.md`.
