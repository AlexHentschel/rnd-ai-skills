# Paste-ready `CLAUDE.md` snippet — always-on rules for research-notebook claim validation

**Why this exists.** The `paper-claim-validation` skill is *on-demand* — it loads only when invoked. The
rules below must hold on **every** turn that touches citations/claims, so they belong in your
**always-loaded** context, not only in the skill. In Claude Code that is `CLAUDE.md` (auto-loaded every
session). In Cursor it is an always-apply rule (`.cursor/rules/*.mdc` with `alwaysApply: true`). Paste
the block below into yours.

---
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
---

Trim to taste, but keep rules 1–4: they are the safeguards a skipped skill-invocation would otherwise drop.
