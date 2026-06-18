# Agent ↔ NotebookLM protocol

**Who this is for.** An AI agent that drives this skill's query tool (`ask_question.py`) programmatically
and must communicate with it *predictably* — sizing prompts so they go through, reading the tool's
output to tell success from failure, and recovering without guessing. **NotebookLM** ("the notebook"):
a Google tool that answers a question *only* from the documents (PDFs/papers) you have uploaded to a
given notebook — source-grounded, so it does not invent facts the way a chatbot might, but it also
refuses anything not answerable from those sources.

This file is self-contained. It quotes the tool's exact output strings (they are the contract). For
the full CLI surface see `api_reference.md`; for failure-mode fixes see `references/troubleshooting.md`;
for corrections to stock docs (rate limit, browser, persistence) see `INSTALL.md`.

---

## 1. The contract at a glance

**Invoke (always via the `run.py` wrapper; always name the notebook explicitly):**

```bash
python scripts/run.py ask_question.py --question "<one focused question>" --notebook-url "<URL>"
```

- `--notebook-url <URL>` *or* `--notebook-id <id>`. **Pass one explicitly** — relying on the "active
  notebook" default queries the wrong corpus silently (a real failure mode).
- `--allow-long` — bypass the prompt-length guard (see §4). Use deliberately, not by default.
- `--show-browser` — run headed (for debugging / re-auth).

**Outcome is a contract on exit code + a marker line:**

| Exit | Means | What you'll see |
|---|---|---|
| `0` | success | a `====`-delimited block ending in the follow-up coda (see below) |
| `1` | failure | a `❌ …` line naming the cause (auth, notebook, over-budget, timeout, …) |

**Success payload** (`exit 0`) is exactly:

```
============================================================
Question: <verbatim echo of your --question>
============================================================

<answer text from the notebook>

============================================================
```

- The `Question:` line is the tool's **client-side receipt** of what it sent — read it to confirm your
  full prompt arrived (the notebook itself will *not* echo your text on request).
- The answer text ends with an appended coda beginning `EXTREMELY IMPORTANT: Is that ALL you need to
  know?`. This is a reminder **to you** to consider a follow-up; it is **not** part of the notebook's
  answer and it does **not** consume your prompt budget. Strip it before showing the answer to a user.

---

## 2. Reading the tool's output (signal → action)

The tool prints progress to stdout. You only need to branch on a few lines; the rest are informational.

| Line (verbatim, emoji included) | Meaning | Your action |
|---|---|---|
| `💬 Asking: {q}` / `📚 Notebook: {url}` | start; question + target echoed | confirm both match intent |
| `📚 Using active notebook: {name}` | you did **not** pass a notebook flag | stop and pass `--notebook-url`/`--id` unless this is intended |
| `📊 SETTLED  text_len=… head=… tail=…` | answer captured; its length + endpoints | sanity-check `tail` isn't mid-sentence |
| `✅ Got answer!` then the `====` block | success | parse answer between the 2nd and 3rd `====`; drop the coda |
| `⚠️ Not authenticated…` | session expired/never set | re-auth (`auth_manager.py setup`, visible browser); then retry |
| `❌ Notebook '{id}' not found` | bad `--notebook-id` | fix id or use `--notebook-url` |
| `❌ Prompt over budget: …` | your prompt exceeds the cap (§4) | shorten **or split into focused questions**; retry |
| `❌ Prompt not fully entered: …` | input truncated your prompt before submit | shorten; retry |
| `❌ Timeout waiting for answer` | 120s passed with no stable answer | prompt likely too long (but under cap) or notebook stuck — retry once, then shorten/split |
| `⚠️ Multiple unmarked pairs (N); taking the first` | answer-selection was ambiguous | treat answer skeptically; retry with a shorter prompt |
| `❌ Error: …` (+ traceback on stderr) | browser/launch error (often a stale profile lock) | see `troubleshooting.md` FM-8; retry after cleanup |
| `❌ Failed to get answer` | generic final failure (`exit 1`) | read the `❌`/`⚠️` line above it for the real cause |

Timing facts you can rely on: answer wait = **120s**; per-query the tool types your prompt at
human speed, so a multi-thousand-char prompt takes **minutes** (another reason to keep prompts short —
an over-long prompt can outlive a wrapper timeout and leave an orphaned browser; see FM-8).

---

## 3. Where to FOCUS — posing questions the notebook answers well

The notebook answers best when the question is **scoped, self-contained, and pitched at a domain
expert**. Embed everything it needs; it has no memory of your chat or your codebase. This section is the
summary; for the full prompt-craft field guide — query anatomy, per-type templates, worked
examples, answer-trust caveats, anti-patterns — see **`references/query-authoring.md`**.

- **Name sources by full title + lead author + year — never by citation key or macro.** The notebook
  grounds on the source PDFs; it does not know your `.bib` keys (`SmithEtAl2021`) or LaTeX macros.
  *Mini-template:* `Consider ONLY the publication "<FULL TITLE>" by <Lead Author> (<YEAR>). Answer
  strictly from that paper. <your question> Quote the relevant text and say which section.`
  Plausibility-check the answer: the notebook occasionally reaches beyond the named source.
- **One focused question per call.** Decompose a multi-part need into a sequence of short prompts +
  follow-ups, not one sprawling prompt. (Tightly-numbered sub-questions inside *one short* prompt are
  fine if it stays under the §4 budget.)
- **De-jargon / clarity rewrites — supply the context the notebook lacks.** When asking it to restate a
  dense passage: (a) say *which paper a cited result comes from* (title+author+year); (b) list the
  **terms the paper already introduced** so it reuses them instead of re-coining; (c) set a depth switch:
  *"present in clear, simplified terms UNLESS technical depth is essential here — and it [IS / IS NOT]."*
- **Run a defensibility round before writing anything from an answer.** Paste your drafted wording back
  and ask whether it is *scientifically defensible from the named source*; let it flag over-statement,
  mis-attribution, or scope errors. This catches subtle errors a first pass misses.
- **Put the load-bearing question early.** A question buried after a long context block can be missed
  (symptom: *"the question appears to be missing"*).
- **Treat the notebook's own citation labels as suggestions** (it sometimes invents plausible keys) and
  its quotes as *reported, verbatim-pending* until you check the PDF.

**Two iteration dials (opposite directions):**
- *Validation* (does source X support claim Y?): spend rounds freely — a second, more specific
  re-confirmation is cheap machine time and can shift your confidence.
- *Distillation* (turn sources into a short, clear abstraction): cap at ≈1 confirmatory round. Extra
  "tell me more" rounds make both the notebook and you **add** jargon/detail and *degrade* the
  abstraction. Query economy ≠ synthesis quality.

---

## 4. Where to CUT — the length budget

**Keep each prompt ≤ 255 words / ≤ 1900 chars.** This is a deliberately conservative bound. The notebook
will **not submit** an over-length prompt (its web UI greys out send past a word/char-coupled budget
~300 words / ~3900 chars; a programmatic over-length submit just hangs to the 120s timeout). Staying well
under avoids that whole class of slow, opaque failure.

This skill **enforces** the cap so failure is predictable, not silent:
- Over-cap `--question` → fast `❌ Prompt over budget: …` and `exit 1`. **Split into focused questions**
  (don't truncate mid-thought) and retry. `--allow-long` overrides if you have reason to.
- If the input truncates your text before submit → `❌ Prompt not fully entered: …` and abort (so it
  never answers a half-question).

Newlines are safe: this vendored copy types multi-line prompts as one message (no accidental
mid-prompt submit). You do **not** need to strip newlines. Still prefer tight, single-purpose prompts.

---

## 5. The negotiation loop (predictable fail → adaptive retry)

The tool's job is to fail *predictably*; your job is to read the signal and adapt. Loop:

1. **Size** the prompt under §4; focus it per §3.
2. **Invoke**; capture exit code + stdout.
3. **Branch:**
   - `exit 0` → parse the answer; read the follow-up coda; if the material is **insufficient for your
     task**, ask a focused follow-up (a fresh `ask_question.py` call) — don't proceed on a gap.
   - `❌ Prompt over budget` / `❌ Prompt not fully entered` → shorten or split; retry.
   - `❌ Timeout` → retry **once with the exact same prompt** (transient); if it recurs, shorten/split,
     or check health (`auth_manager.py status`, then one small query) before concluding the notebook is down.
   - `⚠️ Not authenticated` / `❌ Notebook not found` / `❌ Error` → fix the named cause (`troubleshooting.md`),
     then retry.
4. **Verify receipt** when in doubt: the stdout `Question:` echo is exactly what was sent.

Retry discipline: on a transient transport failure, retry the *same* prompt (don't rephrase — that
conflates a transport problem with a content problem). Rephrase/shorten only for length or content signals.

---

## 6. What lives elsewhere (so this file stays focused)

- **Full query-authoring field guide** (templates, worked examples, de-jargon, defensibility, anti-patterns): `references/query-authoring.md`.
- **Full CLI / scripts / data paths:** `api_reference.md`.
- **Failure modes & fixes (env/auth/browser/stale-lock, FM-1…FM-8):** `references/troubleshooting.md`.
- **Stock-doc corrections** (rate limit is Pro ≈ 500/day not 50; we launch system Chrome; the profile
  *does* retain chat history): `INSTALL.md`.
- **Follow-up agent protocol** (STOP → analyze → ask follow-up → synthesize): `SKILL.md § Follow-Up Mechanism`.
- **Full claim-validation methodology** (per-claim loop, shortlist→enquire, evidence hierarchy): the
  companion **`paper-claim-validation`** skill, if installed.
