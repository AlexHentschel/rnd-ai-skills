# The per-claim validation loop (full recipe)

Run this once per checkable claim in the section under review. Neutral, tool-agnostic; assumes a
research notebook (e.g. NotebookLM) grounded in the paper's source corpus.

## Step 0 — Extract checkable claims
Read the prose and list every statement that asserts a fact, a result, or an attribution. Skip pure
prose connectives. Each becomes one row in your work queue.

## Step 1 — Classify each claim
| Class | What it is | Notebook can verify? | Action |
|---|---|---|---|
| **external-attribution** | cites a specific external result ("by [Author, §X]") | yes | does the cited source actually state this, in the place cited? |
| **conceptual-borrowing** | invokes a named external concept by analogy ("Balancer-style geometric mean", "Aave-style fixed LTV") with no formal cite | yes | does the concept genuinely originate where implied? is it cited at all? |
| **internal-mathematical** | the paper's OWN definition / derivation / theorem | **NO** | enumerate (statement + location + dependencies) and route to the human authors; **do not re-derive** |

The classification is load-bearing: a notebook of *external* papers cannot validate the paper's *own*
mathematics. Mixing the two is how a "validation pass" produces false confidence.

## Step 2 — Shortlist candidate sources
For class-1/2 claims, list every publication that might support the claim — not only the currently-cited
one. Sources: corpus full-text search (by author surname + key terms), your own per-source notes, a
topical index of the corpus. Shortlisting is a *separate* triage step from enquiring (Step 3).

## Step 3 — Single-source-scoped enquiry (per candidate)
For each shortlisted source, run a scoped query (see `prompt-templates.md`):
1. Confirm the notebook **has** that paper as a source.
2. Ask whether the **specific** claim is scientifically defensible from **that** source only.
3. Plausibility-check (the tool can stray beyond the named source); ask follow-ups where subtle.
Repeating across *all* candidates is also how you surface *additional* supporting works (a richer
citation set), not just validate the cited one.

## Step 4 — Defensibility round (before writing anything)
If you will write or reword text based on an answer, run one more scoped query that states **your
intended wording** and asks the notebook to confirm it is defensible from the named source. This catches
the gap between "the source supports the idea" and "the source supports *this sentence*".

## Step 5 — Record the verdict
Per claim, record:
- **verdict:** supported / unsupported / unresolved-after-checks.
- **support-mode:** `direct external` (named source states it) · `conceptual` (named concept originates
  there) · `both`.
- a pointer to the evidence (the query transcript + the authoritative summary).
A claim's citation *bracket* may be **individually** sufficient (each cite stands alone) or
**collectively** sufficient (the set supports it though no single member does). Flag a claim only when
its bracket is neither — never flag a deliberately-collective bracket because one member is partial alone.

## Flagging discipline (calibration)
Every flag costs a human reviewer time, and the human reviews everything regardless. The goal is to
**reduce revision rounds**, not pre-empt review. So: raise genuine support-gaps and genuinely-unresolved
cases; do **not** flag where corpus + notebook jointly confirm support (a false positive spends review
for no gain). When uncertain, weigh the cost of a false-positive flag (one unit of human review) against
a missed weak citation (a later revision round), and lean toward flagging only when the gap is real.

## Corpus-absent but real sources
A citation can be legitimately *corpus-absent*: real and standard, just not in the notebook (distinct
from hallucinated). For a **low-stakes / illustrative** claim (an exemplar, not a contested or
load-bearing technical claim): web-verify both the bibliographic metadata **and** the supporting passage
(peer-reviewed article / spec / docs / source), add the cite, and **record the non-notebook provenance
explicitly** so a later pass cannot mistake it for notebook-grounded. **Contested / load-bearing /
technical claims still require notebook or surgical primary-source grounding — never web-only.**
