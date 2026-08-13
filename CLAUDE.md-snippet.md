# Paste-ready `CLAUDE.md` snippet — always-on rules for this repo's skills

**Why this exists.** The skills in this repo are *on-demand* — each loads only when invoked. The rules below
must hold on **every** turn that touches the relevant work, even if the skill-invocation is skipped, so they
belong in your **always-loaded** context, not only in the skill. In Claude Code that is `CLAUDE.md`
(auto-loaded every session). In Cursor it is an always-apply rule (`.cursor/rules/*.mdc` with
`alwaysApply: true`). Paste the block(s) you use into yours.

---
## 1 — Research-notebook claim validation (pairs with the `paper-claim-validation` skill)
```markdown
## Scientific-claim & citation discipline (always on)

When validating, fact-checking, or writing any claim that cites or borrows from a source:

1. **Never intuit a citation.** Do not assert a reference's existence, bibliographic details, or which
   source supports a claim from training knowledge. Check the source corpus first; if a (source, claim)
   pairing is in neither my notes nor the corpus, treat it as UNVERIFIED and flag it — never fill the gap
   from memory.
2. **Corpus-scan-first.** Scan my own per-source notes → the source corpus → the live research notebook,
   in that order. Address every source by full title + lead author + year, never by a citation key.
3. **Confirm wording is defensible.** Before writing text from a research-notebook answer, run one more
   source-scoped check that the *intended wording* (not just the idea) is defensible from the named
   source.
4. **Guard prompt length.** A research notebook may silently truncate a long submitted prompt. Keep
   prompts short and single-purpose, or read back the submitted prompt before trusting the answer.
5. **Correctness over query parsimony** for *validation* (extra attribution queries are cheap and raise
   confidence) — but **cap refinement queries when *distilling* a source** into a short abstraction
   (extra rounds accrete jargon and degrade it).
6. **Classify before checking.** A research notebook of external papers can validate
   external-attribution and conceptual-borrowing claims, but NOT the paper's own internal mathematics —
   route those to the human authors; do not re-derive.

For the full procedure (per-claim loop, prompt templates, evidence-authority ordering, troubleshooting),
use the `paper-claim-validation` skill.
```
Trim to taste, but keep rules 1–4: they are the safeguards a skipped skill-invocation would otherwise drop.

---
## 2 — Reported-vulnerability confirmation (pairs with the `confirming-a-reported-vulnerability` skill)
```markdown
## Reported-vulnerability confirmation discipline (always on)

When handed a *reported* security vulnerability (an audit finding, bug-bounty report, scanner output, or a
colleague's claim) — usually with a proof-of-concept — and asked whether it is real / how bad / how broad:

1. **Treat the report and its PoC as a hypothesis, not a fact.** Re-derive the mechanism from the source
   code myself, against an explicit "what correct behaviour should be" yardstick. Do not restate the
   report's framing as my conclusion.
2. **Verify, don't accept — including recollections.** Re-check every claim from every source (reporter,
   PoC, and any expert's memory, including my own) against the code before relying on it.
3. **Don't get ahead of the evidence.** Analyse before writing the maintainer-facing report; independently
   re-derive each sibling site before filing it; record class-wide sweeps as a pending task rather than
   executing them mid-session.
4. **Confirm reachability, not just the mechanism.** A defect a real attacker cannot reach — or can reach
   only as a narrower attacker than claimed — is not the reported vulnerability. Settle the attacker model.
5. **Handle "it does not hold" with equal rigor.** A report can be invalid / benign / mis-scoped /
   over-stated; refute in spec terms rather than forcing a confirmation. (This side is less battle-tested —
   lean on my own spec-grounded reasoning, and do not let a confident report talk me into or out of a defect.)
6. **Responsible handling.** While a vuln is unfixed/undisclosed, keep exploit detail in the appropriate
   private channel. The "accept the finding" gate and the "publish the fix" gate are separate decisions.

For the full ten-move procedure, use the `confirming-a-reported-vulnerability` skill.
```
Trim to taste, but keep rules 1–3: they are the safeguards a skipped skill-invocation would otherwise drop.
