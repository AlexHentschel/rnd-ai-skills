# Research-notebook prompt templates

Copy-and-fill templates for the three query types. Keep every prompt **self-contained, short, precise,
and pitched at a domain expert**. One focused question per prompt; use follow-ups rather than one
sprawling multi-part prompt. Always name a paper by **full title + lead author + year** (the notebook
does not know internal citation keys).

Placeholders: `<TITLE>` `<AUTHOR>` `<YEAR>` = the source publication; `<CLAIM>` = the exact claim text;
`<WORDING>` = your intended sentence; `<TERMS>` = terms the paper has already introduced.

---

## 1. Source-presence + claim-defensibility (single-source scoped)
Used in the per-claim loop, Step 3.

```
Consider ONLY the publication "<TITLE>" by <AUTHOR> (<YEAR>). First confirm this paper is among your
sources. Then, using only that paper, state whether the following claim is scientifically defensible
from it, and cite the relevant result/section: "<CLAIM>". If the paper does not support it, say so
explicitly rather than drawing on any other source.
```
Plausibility-check the answer: does it actually reference content of `<TITLE>`? If it seems to draw on
other material, re-scope and ask a follow-up.

---

## 2. De-jargon / clarity rephrasing (with auxiliary context + depth switch)
Used to reframe a dense snippet into clearer prose without losing accuracy. Supply the auxiliary context
so the notebook reuses the paper's own terms and points at the right source.

```
Context for this request:
- The snippet below comes from a scientific paper. A citation in it refers to "<TITLE>" by <AUTHOR>
  (<YEAR>) — treat that as the source for the borrowed result.
- The paper has ALREADY introduced and defined these terms; reuse them rather than coining new ones:
  <TERMS>.
- Audience: domain experts; DeFi/technical terms may stand, but avoid dense compound jargon a reader
  must unpack.

Task: rephrase the snippet to be clearer and to reduce jargon/density. Present the external claim in
clear, potentially simplified terms UNLESS the technical depth is essential here — and it [IS / IS NOT]
essential in this context, so [keep it precise / you may simplify]. Do not change the scientific meaning.

Snippet:
"<SNIPPET>"
```
Set the depth switch (`IS`/`IS NOT`) deliberately per snippet.

---

## 3. Defensibility confirmation of generated wording
Used in the per-claim loop, Step 4 — before committing any text you wrote from a notebook answer.

```
Consider ONLY "<TITLE>" by <AUTHOR> (<YEAR>). I intend to write the following sentence in a paper, which
relies on this source: "<WORDING>". Using only that paper, is this sentence scientifically defensible as
written? Flag any over-statement, mis-attribution, or scope the source does not support.
```

---

## Prompt-length / multiline guard
**A long or multi-paragraph prompt does not arrive whole.** Two distinct mechanisms — both observed, not
theoretical:

- **Newlines split your prompt into several messages (the main hazard).** The automation tool *types* the
  prompt into the input box, and **each newline is entered as a "send" keystroke** — so a prompt with
  blank lines / paragraphs is submitted as **multiple separate messages**. The notebook then answers each
  fragment on its own and *guesses* the missing intent, injecting ambiguity and errors. The start of each
  later fragment can also be lost (typing resumes before the box is ready after a submit). A reply like
  *"your query was cut off … you didn't include the statement itself"* is this splitting — the notebook
  answered an early fragment that lacked the rest, **not** character-level truncation.
- **There is also a maximum submittable length** (the web UI greys out *send* past it). It is **not a flat
  character count** — fewer words allow more characters. Observed: whitespace-stripped prose accepted at
  ~3,900 chars / 2 words; normal prose caps near ~2,000 chars / ~300 words. Treat it as a **dual budget:
  roughly ≤300 words *and* ≤~3,900 chars, whichever you hit first** (for normal prose the ~300-word /
  ~2,000-char bound binds). An over-length single block **won't submit at all** (it stalls), rather than
  being silently shortened.

Defend against both:
1. **Newlines: handled by the tool (patched).** This vendored copy converts each newline to a line break
   (Shift+Enter) instead of a submit, so a multi-paragraph prompt arrives as **one** message — you do not
   need to strip newlines yourself. (Only relevant if you run an *unpatched* upstream copy: there, collapse
   newlines to spaces yourself. See `notebooklm/UPSTREAM.md` P5.)
2. **Length is still on you — keep each prompt under ≤255 words / ≤1900 chars** (a deliberately
   conservative cap; some users report the notebook accepts more, but stay safely under). An over-length
   prompt won't submit at all. Prefer short, single-purpose prompts (the templates above are sized for this).
3. **Put the load-bearing question early — never bury it after a long context block.**
4. **Read back what was actually sent.** The tool echoes your submitted prompt in its own output (a
   "Question: …" block) — check that. (Do not ask the notebook to echo your text: it is source-grounded
   and refuses such meta-instructions.)
5. If an answer looks like it missed part of your prompt, or one intended prompt produced several
   messages, assume splitting/over-length: strip newlines, shorten, split into focused prompts, and re-ask.

## Iteration etiquette
- Multiple back-and-forth rounds are expected where a point is subtle (validation).
- But when *distilling* a source into a short abstraction, stop early (≈≤1 confirmatory round): extra
  rounds accrete jargon and detail and make the abstraction worse, not better.
