# Authoring NotebookLM queries — a field guide

**Who this is for.** An AI agent composing the `--question` text for this skill's query tool. This is
the *prompt-craft* companion to `agent-protocol.md` (which covers the tool's input/output contract, the
length budget, and the failure/retry loop — read that for "how the tool behaves"; read this for "how to
phrase the question"). Self-contained: assumes only general competence plus what these two files state.

**What NotebookLM is, and why phrasing matters.** NotebookLM ("the notebook") answers a question using
**only** the documents uploaded to the notebook you target — it is *source-grounded*. That is its
strength (it won't fabricate the way an open chatbot might) and its constraint (it refuses anything not
answerable from those sources, and it has no idea what *you* know — your draft, your citation keys, your
chat). A good query supplies everything the notebook needs and asks one precise thing. A bad query gets a
plausible-but-unattributable answer, or a refusal, or an answer to the wrong question.

---

## 1. The five properties of a good query

1. **Scoped** — name the exact source(s) to use, by *human-readable identity* (title + author + year),
   not by your internal citation key or macro. The notebook indexes the PDFs, not your `.bib`.
2. **Self-contained** — embed the claim, the context, and any term definitions inline. The notebook has
   no memory of your draft or prior turns (and prior turns in the same browser profile can *pollute* it —
   see §6).
3. **Single-purpose** — one load-bearing question per query. Decompose multi-part needs into a sequence
   of queries (or tightly-numbered sub-parts of *one short* query; see §3b).
4. **Expert-pitched** — write to a domain expert; state the precise claim, don't ask vaguely.
5. **Question-first** — put the load-bearing question at (or near) the **top**, before any long context
   block. A question buried under filler gets missed (symptom: an answer saying the question "appears to
   be missing").

---

## 2. Query anatomy

Most good queries are built from four slots, in this order:

```
[SCOPE]     Consider ONLY the publication "<TITLE>" by <LEAD AUTHOR> (<YEAR>). Answer strictly from it.
[ASK]       <one precise question — placed early>
[CONTEXT]   <the exact claim / draft wording / definitions the notebook needs, inline>
[OUTPUT]    Quote the relevant text and say which section. If it does not support this, say so explicitly.
```

- The `[OUTPUT]` directive is high-leverage: asking for a **verbatim quote + section** turns a vague
  "yes it's discussed" into a checkable excerpt, and asking it to **say so explicitly if unsupported**
  counters the model's pull to be agreeable.
- Keep the whole thing within the length budget in `agent-protocol.md` (≤255 words / ≤1900 chars; the
  tool now hard-fails over budget). If `[CONTEXT]` is large, tighten it or split the query — do not let
  it push the `[ASK]` down the page.

---

## 3. The core query types (templates + worked examples)

### 3a. Validation — does this source support this claim?

```
Consider ONLY the paper "<TITLE>" by <AUTHOR> (<YEAR>). Answer strictly from that paper.
Does it support the following claim: "<CLAIM>"? Quote the exact supporting sentence(s)
and name the section. If it does not support the claim, say so explicitly.
```

*Worked example.* `Consider ONLY the paper "Constant Function Market Makers: Multi-Asset Trades via
Convex Optimization" by Guillermo Angeris et al. (2021). Around section 2.5, does it define the local
exchange rate between two assets as the ratio of the partial derivatives of the trading function? Quote
the text and give the equation number.` → returned the §2.5 definition with the equation and the
"geometric-mean price" heading. **Why it worked:** one source, named by title; one precise structural
question; an output directive that forces a checkable quote.

### 3b. Numbered sub-questions inside one query

Acceptable when the prompt stays short and you genuinely want them answered together:

```
Consider ONLY "<TITLE>" by <AUTHOR> (<YEAR>). Answer each from that paper only:
(1) <question one>?  (2) <question two>?  Quote the relevant text for each.
```

Use this for tightly-coupled facts (e.g. a characterization *and* its origin credit). For independent
claims, prefer separate queries — cleaner attribution, no cross-bleed.

### 3c. Attribution scoping — which source supports X?

You **cannot** read the notebook's in-answer citation markers back to specific papers. So to attribute a
claim, don't ask "who says X?" against the whole corpus; instead run 3a **once per candidate source** you
shortlisted, each scoped to one named paper. The candidate that yields a clean supporting quote is your
attribution. (Shortlisting candidates is a separate retrieval step you do *before* querying.)

### 3d. De-jargon / clarity rewrite (synthesis) — with auxiliary context

When you want a dense passage restated in clearer terms, supply the three things the notebook lacks:

```
Rewrite the following passage in clear terms, using less jargon a reader must unpack;
you may split it into several sentences. Present it in simplified terms UNLESS technical
depth is essential here — and it [IS / IS NOT] essential.
A citation in it refers to "<TITLE>" by <AUTHOR> (<YEAR>) — treat that as the source.
The passage has ALREADY introduced and defined these terms; reuse them rather than coining
new ones: <TERMS>.
Passage: "<SNIPPET>"
```

- **Set the depth switch deliberately** (`IS` vs `IS NOT`) per passage — it controls whether the notebook
  preserves precise machinery or simplifies it.
- **List already-introduced terms** so it reuses your load-bearing vocabulary instead of substituting a
  looser synonym (e.g. it should keep "invariant", not swap in "trading rule").
- **Include the preceding sentence/paragraph** when the clause under edit depends on earlier setup (e.g.
  an "arbitrageur" who was introduced upstream) — the notebook then scopes its rewrite correctly.
- **Caveat:** a de-jargon answer is a *synthesis*, weaker evidence than a scoped factual quote. And the
  rewrite may **over-strengthen** a claim or strip a load-bearing qualifier — review before adopting (§6).

### 3e. Defensibility round — is *my* wording defensible?

Always run this before writing anything into a document from a notebook answer:

```
Consider ONLY "<TITLE>" by <AUTHOR> (<YEAR>). Is the following statement scientifically
defensible strictly from that paper: "<YOUR WORDING>"? Flag any over-statement, mis-attribution,
or scope error, and give the corrected, defensible version with a supporting quote.
```

*Worked example.* A draft said *"a single optimal trade is always better for the trader than splitting
it."* The defensibility query returned **not defensible**: true only for an arbitrageur seeking a fixed
net result, not a directional trader (who may split to manage price impact). The fix was to add the
**arbitrageur / same-net-result** scope. **Lesson:** the defensibility round catches missing scope
qualifiers that a confident first draft hides.

---

## 4. Supplying auxiliary context the notebook lacks

The notebook only knows the uploaded PDFs. It does **not** know:
- **Your citation keys or LaTeX macros** → always identify sources by title + author + year; never paste
  `SmithEtAl2021` or `\techterm{…}`.
- **Which paper a borrowed result came from** → state it inline ("this cited result is from <TITLE> …").
- **Your draft's established terminology** → list the terms it should reuse.
- **How precise you need it** → set the depth switch explicitly.
- **Your chat or prior queries** → re-state everything each time; treat each query as standalone.

---

## 5. Iteration discipline — two opposite dials

- **Validation / attribution: spend rounds freely.** A second, more specific re-confirmation ("In which
  way does <source> support <claim>?") is cheap and can shift your confidence — a subtle second round
  routinely catches an error the first missed. This mirrors how a careful human peer reviewer re-checks.
- **Distillation / abstraction: cap at ~1 confirmatory round.** Asking "tell me more" / "refine again"
  makes both the notebook and you **add** detail and re-introduce jargon on each pass — the abstraction
  *degrades*. Query economy and synthesis quality are independent: spending freely on validation does not
  license extra distillation rounds. Get one clear synthesis, then edit by hand.

Budget context: a typical per-source validation effort is a handful of queries (≈8–12), logged
individually rather than crammed into one mega-prompt.

---

## 6. Reading and trusting answers

- **Treat the notebook's citation labels as *suggestions*.** It sometimes invents plausible-looking keys
  that aren't in your bibliography — map every label to a real source before using it.
- **Treat quotes as *reported, verbatim-pending*.** Cross-check against the actual PDF before marking a
  quote verified. Substance can be supported while the exact quote location is still unconfirmed (two
  separate axes).
- **Plausibility-check scoped answers.** Single-source scoping (§3a/3c) is reliable but not absolute —
  the notebook occasionally reaches beyond the named source. If an answer seems to draw on outside
  knowledge, ask a follow-up to confirm the support is genuinely in the named paper.
- **Watch for editorializing and over-strengthening.** It may add praise ("profound insight") or
  strengthen a neutral claim into a stronger one — strip these when applying to a document.
- **Mind cross-domain analogy enthusiasm.** It may endorse an analogy to another field; keep the scope
  caveat the analogy needs.
- **Beware chat-history pollution.** The browser profile retains prior turns, which can leak into a new
  answer ("as you were testing earlier…"). Keep each query self-contained; if answers look contaminated,
  see `troubleshooting.md` (stale-answer handling).
- **Confirm receipt via the tool, not the notebook.** To check your full prompt was sent, read the tool's
  `Question:` echo in stdout — do **not** ask the notebook to repeat or echo your text (it refuses
  "administrative" non-source tasks, and matching a sentinel against its own echo gives false positives).

---

## 7. Anti-patterns (and the fix)

| Anti-pattern | Symptom | Fix |
|---|---|---|
| Citation key / LaTeX macro in the prompt | notebook can't resolve it | name source by title + author + year |
| Whole-corpus "who supports X?" | unattributable answer | scope to one named source, one per candidate (§3c) |
| Question buried after long context | "the question appears to be missing" | put the `[ASK]` first (§1) |
| Over-broad simplification, no scope | answer is "not defensible" | add the scope qualifier (whose perspective? what regime?) |
| Sprawling multi-part prompt | mixed/partial answer; length failure | one purpose per query; sequence follow-ups |
| Over-length prompt | tool `❌ Prompt over budget`, or a stall | shorten / split (see `agent-protocol.md` §4) |
| Asking it to echo / confirm a sentinel | refusal (source-grounded) | read the tool's `Question:` echo instead |
| Extra "refine again" distillation rounds | jargon/detail creep | one synthesis round, then edit by hand (§5) |

---

## 8. A worked end-to-end flow

1. **Validate** the claim against its cited source (3a) → get a supporting quote + section, or a clean
   "not supported".
2. If unsupported, **attribute** by running 3a across your other shortlisted candidates (3c) until one
   yields support — or conclude the claim is corpus-absent.
3. If you need to **restate** the passage for readers, run one de-jargon query with auxiliary context
   (3d), depth switch set deliberately.
4. **Defensibility round** (3e) on your *final* wording before it goes into the document.
5. **Record** the (claim, source, quote, verdict) so it isn't re-done; map any notebook-suggested
   citation label to a real key.

---

## 9. Pre-send checklist

- [ ] One load-bearing question, placed first?
- [ ] Sources named by title + author + year (no keys/macros)?
- [ ] Claim, context, and any term definitions embedded inline?
- [ ] Depth switch set (for rewrites)?
- [ ] Output directive present (quote + section; "say so if unsupported")?
- [ ] Within the length budget (`agent-protocol.md` §4)?

---

## Cross-references (in-skill)

- **Tool I/O contract, length budget, failure/retry loop:** `agent-protocol.md`.
- **CLI flags / scripts:** `api_reference.md`. **Failure modes & fixes:** `references/troubleshooting.md`.
- **Full claim-validation *methodology*** (per-claim loop, shortlist→enquire, evidence-authority ordering):
  the companion **`paper-claim-validation`** skill, if installed.
