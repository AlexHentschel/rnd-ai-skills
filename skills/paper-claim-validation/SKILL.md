---
name: paper-claim-validation
description: Use when validating, fact-checking, or revising the factual and citation claims of a scientific paper against a curated research notebook (e.g. a NotebookLM of the paper's source corpus). Covers the per-claim validation loop, single-source scoping, de-jargon / clarity prompting with auxiliary context, scientific-defensibility iteration, a prompt-length truncation guard, evidence-authority ordering, and troubleshooting. Pairs with a research-notebook query tool (e.g. the `notebooklm` skill).
---

# Paper claim validation with a research notebook

Validate that a scientific paper's **claims** are (a) supported by the sources it cites and (b) stated
in clear, scientifically defensible terms — using a **research notebook**: a tool (e.g. NotebookLM,
"NLM") that answers questions grounded *only* in a fixed corpus of uploaded papers. This skill is the
*methodology*; it relies on a separate *tool* skill (e.g. `notebooklm`) to actually run queries.

## When to use
- Fact-checking or citation-validating a section of a paper before submission/revision.
- Reframing a dense/jargon-heavy snippet into clearer prose without losing scientific accuracy.
- Confirming that wording you generate from a notebook answer is actually defensible from the source.

## Hard rules — always apply (these also belong in your always-on layer)
A skill is *on-demand*: it loads only when invoked. These rules must hold **every turn**, so also place
them in your always-loaded context (`CLAUDE.md` for Claude Code; an always-apply rule for Cursor). See
`../../CLAUDE.md-snippet.md` for a paste-ready block.

1. **Citations cannot be intuited.** Never assert a reference's existence, its bibliographic details, or
   *which* source supports a claim from model training knowledge. Check the corpus first. If a
   (source, claim) pairing is in neither your notes nor the corpus, treat it as **unverified** and flag
   it — do not fill the gap from memory. (Intuiting an attribution is the single most common failure.)
2. **Corpus-scan-first.** Before claiming support, scan: your own per-source notes (if any) → the
   notebook corpus (the actual source texts) → the live notebook. Address sources by **full title +
   lead author + year**, never by an internal citation key.
3. **Correctness over query parsimony.** A research-notebook query is cheap machine time. Spend an
   extra confirmation/attribution query whenever it could shift confidence. (Query budget is a reason
   to skip only if you are genuinely near a daily ceiling.) **But more queries help *validation*, not
   *synthesis*** — when distilling a source into a short abstraction, cap refinement queries (≈≤1
   confirmatory): extra "tell me more" turns degrade an abstraction with accreted jargon/detail.

## The per-claim validation loop
Full recipe: `reference/per-claim-validation-loop.md`. In brief, per checkable claim:
1. **Classify** — *external-attribution* (cites a specific external result) · *conceptual-borrowing*
   (invokes a named external concept by analogy) · *internal-mathematical* (the paper's own
   derivation/theorem). **A research notebook cannot verify internal-mathematical claims** — enumerate
   and route them to the human authors; do not re-derive.
2. **Shortlist** candidate source(s) the claim might rest on (corpus search + your notes + a topical index).
3. **Single-source-scoped enquiry** per candidate (see prompting, below): confirm the source is in the
   corpus, then ask whether the *specific* claim is scientifically defensible from it.
4. **Defensibility round** — before writing anything from an answer, run one more scoped query that
   states *your intended wording* and asks the notebook to confirm it is defensible from that source.
5. **Record** verdict + support-mode (`direct external` / `conceptual` / `both`) so it is not redone.

## Prompting the research notebook
Templates + worked examples: `reference/prompt-templates.md`. Core technique:
- **One focused question per prompt** (plus follow-ups), short, precise, pitched at a domain expert.
- **Single-source scoping** — name exactly one publication (title + author + year) and instruct the
  notebook to use **only** that source. This is the workaround for the tool's key limit: its in-answer
  citation markers are **not** traceable to a backing source from outside, so scoping is the only way
  to attribute support to a *specific* paper. Plausibility-check the answer (the tool occasionally
  strays beyond the named source).
- **De-jargon / clarity prompting (with auxiliary context).** To get a clearer, less dense rephrasing
  of a snippet (e.g. unpacking a term like "convexity cost"), give the notebook the context it needs:
  - **which paper a citation refers to** (full title + author + year) — the notebook does not know your bibkeys;
  - **which technical terms the paper has already introduced**, so it reuses them instead of re-coining;
  - an explicit **depth switch**: "present this in clear, simplified terms **unless** the technical
    depth is essential here, in which case keep it precise" — state which applies.
- **Defensibility iteration** — always close with a round confirming the generated wording is
  scientifically defensible from the named source (rule 1 + loop step 4).

## Prompt-length / truncation guard
The notebook may silently **truncate a long submitted prompt**. Before trusting an answer to a long or
multi-part prompt: either (a) keep prompts short and single-purpose (preferred), or (b) **read back the
submitted prompt** from the tool (confirm the full text was received) — or length-check upfront. A
truncated prompt yields an answer to a question you did not ask. (Distinct from truncated *answers* —
see troubleshooting.)

## Evidence-authority ordering (which evidence wins on disagreement)
1. **Human-vetted source summaries/exports** (exported *and* checked by a domain expert) — most authoritative.
2. **Live research-notebook answers** — a probe/validation record; can stray beyond a named source.
3. **Your own derived per-source notes** — fastest to retrieve, but derived; lower than (1)/(2).
4. **The original source PDF** — ground truth on a specific point, used **surgically** (a targeted,
   thorough read of the one relevant section/equation), never a bulk "read the whole PDF and trust it" pass.
Training knowledge is **not** an authority for any citation.

## Troubleshooting
Symptom → cause → fix table for the common research-notebook failure modes (broken environment, stale/
off-topic answer, truncated answer, auth, wrong corpus, transient error): `reference/troubleshooting.md`.

## Dependency — the query tool
This skill assumes a research-notebook query tool is installed and authenticated (e.g. the `notebooklm`
skill, vendored in this repo). Install + operational notes: `../notebooklm/INSTALL.md`; its upstream
provenance + patch record: `../notebooklm/UPSTREAM.md`; the **agent↔tool contract** (how to read the
tool's output signals, the prompt-length budget, the predictable over-budget failure + retry loop):
`../notebooklm/references/agent-protocol.md`. **Confirm which notebook (corpus) you are
querying before any query** — pass it explicitly; do not rely on a tool's "active notebook" default.
