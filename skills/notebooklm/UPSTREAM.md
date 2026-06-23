# notebooklm skill — upstream provenance & local patch record

This skill is a **vendored, patched copy** of an external open-source skill. This file is the
single source of truth for: where it came from, the license terms, the exact changes we applied,
how to re-apply them to a newer upstream, and the cadence for checking upstream for updates.

## Upstream
- **Source repo:** https://github.com/PleasePrompto/notebooklm-skill
- **Vendored from:** commit `eea5cb2` — "feat: v1.3.0 - Modular Architecture, Timeout Fix, Thinking
  Detection" (2025-11-21). This is the pinned baseline; our patches below apply on top of it.
- **License:** MIT — *Copyright (c) 2025 Please Prompto!* (see the `LICENSE` file kept verbatim in
  this directory). MIT permits fork / modify / redistribute, **provided the original copyright and
  permission notice are retained** in copies/substantial portions. Our patches are additive and
  released under the same MIT terms. **This `UPSTREAM.md` is the attribution + change record** that
  documents our modifications (good open-source hygiene + the re-apply trail).

## License compliance checklist (when vendoring into a redistributable repo)
- [x] Keep upstream `LICENSE` verbatim in this directory.
- [x] State changes from upstream (this file's § Local patches).
- [x] Direct link to upstream (above).

## Upstream-revision check — cadence: AT MOST once per 7 days
**Last checked:** 2026-06-17 — **identical to baseline** (`compare/eea5cb2...master` → `status: identical`,
`ahead_by: 0`; upstream last push 2025-11-21). No upstream changes since vendoring; all local patches below
still apply. Next check due ≥ 2026-06-24.

**When to run:** when this skill is invoked **and** > 7 days since "Last checked". Do **not** check
more often (throttle on the date above). Needs network; if unavailable, note and defer.

**Procedure:**
1. GitHub API: `GET /repos/PleasePrompto/notebooklm-skill/compare/<pinned-sha>...master` and read
   `status` / `ahead_by`. (Upstream's default branch is **`master`**, not `main`.) `status: identical` /
   `ahead_by: 0` ⇒ nothing to do but bump "Last checked". Local `git fetch` works only if a remote points
   at the upstream repo — the vendored copy's `origin` is `ah-ai-skills`, so prefer the API compare.
2. If new upstream commits exist, list them and, per commit, judge whether it supersedes, conflicts
   with, or is orthogonal to a local patch below.
3. For each still-relevant local patch, **re-apply** per its re-apply instructions on top of the new
   upstream (or record why skipped). Re-run the FM checks named in each patch.
4. Update "Last checked" (date) and the pinned commit above.

(A future automation could move this to a scheduled hook; for now it is an invocation-time, throttled
manual check — agile-first.)

## Local patches (conceptual → implementation → how to re-apply)

### P1 — robust new-answer capture in `scripts/ask_question.py`  (fixes FM-2 stale answer + FM-3 truncation)
- **Conceptual.** Upstream picked the answer with `elements[-1]` (document-order "last" response).
  NotebookLM's chat DOM is **not** chronological and the persistent browser profile **retains chat
  history**, so `[-1]` returned stale / wrong-topic answers; streaming pauses also caused premature
  capture of a truncated answer.
- **Implementation (three parts, in the answer-wait section of `ask_notebooklm`):**
  1. **Hydration wait** — poll `document.querySelectorAll('div.chat-message-pair').length` until stable
     for 3 consecutive polls (~1.5 s) *before* marking the baseline, so late-loading history isn't
     mis-tagged.
  2. **Marker-based identity** — tag every existing `div.chat-message-pair` with `data-pre-submit="1"`;
     after submitting, select the new pair via `div.chat-message-pair:not([data-pre-submit])` and read
     the bot text from `.to-user-container .message-text-content`.
  3. **Stability threshold 3 → 6** consecutive identical polls (× 0.5 s = 3 s) to survive NotebookLM's
     streaming pauses (esp. around rendered equations); 0.5 s thinking-message skip; `SETTLED` debug log.
- **State of the vendored file:** `scripts/ask_question.py` shipped here is **already the patched
  version**. (A pre-patch `.bak` exists only in the original author's local working copy and is
  gitignored, so it is not in this repo. To see the patch as a diff, compare this file against pristine
  upstream `eea5cb2`.)
- **Re-apply to a newer upstream.** Locate the answer-wait loop in the new `ask_question.py`; replace
  the `elements[-1]` / `RESPONSE_SELECTORS` capture with the marker-based block (hydration wait →
  `data-pre-submit` marking → `:not([data-pre-submit])` selection → 6-poll stability). If upstream has
  refactored answer-capture into `browser_utils.py` / `browser_session.py`, port the same marker logic
  there. Verify: FM-2 (no stale/off-topic answers) and FM-3 (no mid-answer truncation).

### P2 — venv rebase onto a stable interpreter  (fixes FM-1)  [operational; not a tracked file change]
- **Conceptual.** A `--copies` venv pinned to a package-manager-managed Python (e.g. Homebrew) breaks
  on every point-bump (dyld "library not loaded" / missing framework).
- **Implementation.** Rebuild `.venv` as a **symlink** venv (not `--copies`) on a **stable, self-managed
  interpreter** that the package manager won't auto-remove.
- **Re-apply.** Not upstream-dependent; re-run after any interpreter change. Avoid the package-manager's
  `python3.x` + `--copies` combination.
- **Vendored-copy note:** machine-local — each user rebuilds their own venv (see `INSTALL.md`); never
  vendor a `.venv`.

### P3 — dormant unpatched copy of the stale-selection bug  [NOT yet patched; tracked]
- `browser_session.py` (`_snapshot_latest_response` / `_wait_for_latest_answer`) still uses the
  `responses[-1]` pattern. It is **not** invoked by `ask_question.py`, so it is harmless today. If a
  future code path calls it, apply the P1 marker logic there.

### P4 — provenance + operational pointers added to `SKILL.md`  [doc]
- A short "Upstream & local patches" block near the top of `SKILL.md` points here (`UPSTREAM.md`) for
  provenance/patches, **and** to `INSTALL.md` for install/operation — flagging inline that three stock
  lines below it are wrong for this vendored copy (rate limit = free tier not Pro; system Chrome not
  auto-Chromium; chat history *is* retained, so "no session persistence" is false). This keeps a foreign
  agent that loads `SKILL.md` as its entry point from acting on the stale stock guidance.
- **Re-apply.** Re-add the block after any upstream `SKILL.md` overwrite; re-check the three corrected
  lines still exist in the new upstream prose (drop any that upstream has since fixed).

### P5 — newline → Shift+Enter in `scripts/browser_utils.py::StealthUtils.human_type`  (fixes prompt-splitting)
- **Problem.** `human_type` typed the prompt char-by-char via `element.type(char)`. For a newline,
  Playwright emits an **Enter** keypress, which the NotebookLM chat input treats as **submit** — so a
  multi-paragraph prompt is sent as **several separate messages** (one per line-block). The notebook then
  answers each fragment and guesses the missing intent, injecting ambiguity/errors. (Confirmed 2026-06-17:
  one ~5.2k-char prompt landed as 3 messages; a 78-char 2-line probe landed as 2.)
- **Change.** In the per-char loop, intercept `"\n"` and send `page.keyboard.press("Shift+Enter")`
  (inserts a line break **without** submitting) instead of `element.type("\n")`. All other chars
  unchanged. The single explicit `page.keyboard.press("Enter")` in `ask_question.py` still does the one
  real submit, so the whole prompt arrives as **one** message with its line breaks intact.
- **Verified.** Live-tested 2026-06-17: a 2-line prompt whose line 2 referenced a nonce defined only on
  line 1 was answered using both lines ⇒ it arrived as a single message. NotebookLM's input treats
  Shift+Enter as newline-not-submit (standard chat-UI behaviour). If a future upstream/site change breaks
  that, the fallback is to replace `"\n"` with a space (flattens structure but still one message).
- **Does NOT fix the length cap.** A submittable prompt also has a max length (~300 words / ~3,900 chars
  dual budget; for prose the ~300-word/~2,000-char bound binds). An over-length single message won't
  submit at all. Keep prompts ≤255 words / ≤1900 chars (conservative) — see `INSTALL.md` / the methodology skill's
  `prompt-templates.md § Prompt-length / multiline guard`.
- **Re-apply.** After any upstream overwrite of `browser_utils.py`, re-add the `if char == "\n":
  page.keyboard.press("Shift+Enter")` branch in `human_type`'s typing loop (look for `for char in text:`
  / `element.type(char`).

### P6 — predictable prompt-length fail signal in `scripts/ask_question.py`  (turns silent over-length into a hard error)
- **Problem.** P5 fixes *splitting* but not the **length cap**: an over-length single message won't submit
  (web UI greys send; a programmatic submit then just hangs to the 120s answer timeout) — a slow, opaque
  failure. The tool previously did **no** length check and **no** verification that the typed prompt fully
  landed (if the input had a maxlength, an over-length prompt would be silently shortened and the wrong,
  truncated question answered). The calling agent had no clean signal to negotiate against.
- **Change (two guards + one flag, all in `ask_question.py`):**
  1. **Module caps** `MAX_PROMPT_CHARS = 1900`, `MAX_PROMPT_WORDS = 255` (conservative; see § P5).
  2. **Pre-flight budget guard** in `main()` (before browser/auth, so it fails fast): if the question
     exceeds either cap, print `❌ Prompt over budget: …` and `return 1`. `--allow-long` downgrades this to
     a `⚠️` warning and proceeds — this is the **adaptive-negotiation escape hatch** (caller's deliberate call).
  3. **Post-type entry assertion** in `ask_notebooklm()` (after `human_type`, before submit): read the
     input's current length via `page.evaluate`; if it holds fewer chars than intended (maxlength-style
     truncation), print `❌ Prompt not fully entered: …` and `return None` instead of submitting a truncated
     question.
- **Why this shape.** Keeps the existing fail-signal convention (`❌` lines + exit 1 / `❌ Failed to get
  answer`) so a foreign calling agent parses one consistent contract. The default is a hard, fast fail
  (predictable); the agent and tool *negotiate* via the cap + `--allow-long` rather than the tool silently
  guessing.
- **Does NOT change the happy path.** Under-budget prompts behave exactly as before.
- **Re-apply.** After any upstream overwrite of `ask_question.py`: re-add the two `MAX_PROMPT_*` constants,
  the `--allow-long` arg + pre-flight guard block in `main()` (anchor: right after `parser.parse_args()`),
  and the post-type length assertion (anchor: right after `StealthUtils.human_type(...)`, before the
  `# Submit` / `page.keyboard.press("Enter")`). Verify: an over-cap `--question` exits 1 with `❌ Prompt
  over budget`; the same with `--allow-long` warns and proceeds.

## Documentation corrections (kept in `INSTALL.md`, not patched into upstream prose)
Upstream `SKILL.md` carries guidance that is wrong for our usage; we correct it in `INSTALL.md` rather
than editing upstream prose, to keep the upstream diff minimal:
- "Rate limit 50/day" → that is the **free tier**; **Pro ≈ 500/day**.
- "Chromium installs automatically" → we launch **system Google Chrome** (`channel="chrome"`).
- "No session persistence" → **false**; the profile retains chat history (root cause of FM-2).
