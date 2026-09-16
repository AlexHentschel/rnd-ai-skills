---
name: memory-maintenance-cycle
description: >-
  Run a full-memory maintenance cycle that reorganizes a coding agent's
  long-term memory / rule tree for better retrieval while provably preserving
  knowledge, using a paired cold-agent retrieval evaluation (score the prior
  and candidate versions on the same probe draw; the delta is the signal). Use
  when reorganizing, compacting, splitting, or restructuring a large agent
  memory and you need measured evidence that nothing was lost. Not for small
  single-file edits, where measurement overhead dominates.
disable-model-invocation: true
---

# Memory-maintenance cycle

Reorganize a coding agent's **long-term memory** — the tree of markdown files
(rules, knowledge notes, indexes) the agent reads to guide its own behavior —
so that it is easier to navigate and leaner, **while proving that no knowledge
became harder to find or was lost.** The proof comes from a *measurement*, not
an assertion: you run a fresh "cold" agent against the memory tree and observe
which files it opens to answer questions.

Key terms (used throughout):
- **Memory tree** — a directory of markdown files the agent loads as durable
  guidance: behavioral rules, domain concept notes, per-topic indexes, style
  notes, working logs. The unit you are reorganizing.
- **Cold agent** — a fresh agent instance with **no conversation history**,
  pinned to read **only** a given memory tree (no other project, no other
  memory leaks in). It stands in for "a future session that has forgotten
  everything except what is written down."
- **Probe** — a question posed to a cold agent (e.g. "where is the retry
  policy defined?"). The agent answers by reading files.
- **Trace** — the ordered list of file-read tool calls the cold agent made
  while answering. The trace + the final answer is the raw signal: it shows
  *whether and how* the agent found the relevant material.
- **Discoverability** — whether a cold agent can actually reach the right file
  for a task. A file that is retained but unreachable is, in practice, absent.
- **Fidelity** — whether the knowledge is still present and correct.
- **Paired delta** — score the same probe against two versions of the tree
  (the prior version and the candidate you just edited) and compare. The
  *difference* between the two is trustworthy; the absolute level of either one
  is noisy.

## 1. Purpose

Large agent memories drift: files accumulate, indexes go stale, related notes
scatter, and a cold future session can no longer find what it needs. This cycle
restructures the tree (regroup, split, add indexes, tighten wording) and gates
every change on a measured retrieval eval, so structural improvements never
silently bury or drop knowledge.

## 2. When to use / when NOT to use

**Use** for whole-memory or large-subtree reorganization — regrouping topics
into new domains, splitting a bloated file, adding or restructuring indexes,
compacting duplication across many files — where fidelity is hard to eyeball
and a single wrong move can orphan a note.

**Do NOT use** for small, local edits (one or two files, an obvious rename, a
typo, a single new note). There the measurement overhead dominates and ordinary
review is enough. This cycle earns its cost only when the change is broad enough
that you cannot personally verify "nothing got harder to find."

## 3. Core principle

1. **Measured, not asserted.** A restructure is accepted only if a retrieval
   measurement shows it did not regress. "It looks cleaner" is not evidence.
2. **Discoverability outranks fidelity outranks leanness.** Keeping content is
   worthless if a cold agent can no longer reach it; shrinking the tree is
   worthless if it costs discoverability. Optimize in that priority order.
3. **Leanness has a legibility floor.** Compress only until a cold reader can
   still fully decode the content. Past that point, compression is a
   regression, not a saving — over-compression and bloat are symmetric failures.
4. **Paired delta is the trust unit.** A cold agent's file-reads vary run to
   run. Do not trust the absolute reach on one version. Trust only the
   *difference* between prior and candidate on the **same** probe draw and
   model. Delta = signal; level = noise.

## 4. The four-phase cycle

Run against a **held-constant reference** — an untouched copy of the original
tree — and revise **versioned deep copies** (v1, v2, …), never the live tree.

1. **Pre-plan** — align on scope (which subtree, what kinds of change) and
   *build the evaluation framework first*: decide the priority order (§3), the
   fidelity bar, and how you will measure. Do not start editing before you can
   measure.
2. **Draft** — author the change plan. **De-risk the measurement harness before
   anything else**: prove you can stage an isolated cold agent and capture its
   trace on one throwaway probe. The harness is the hardest unknown; validate it
   first.
3. **Execute** — loop, one change (or tight batch) at a time:
   `setup → apply → measure → verdict`.
   - **setup**: make a fresh copy of the current-best version.
   - **apply**: make the one structural change; record a migration ledger line
     for anything that moved (old location → new location + any index/pointer
     that should now route there).
   - **measure**: run the same probe draw against the prior version and the
     candidate (paired eval, §5–7).
   - **verdict**: emit ACCEPT / HOLD / REJECT (§7). An individual iteration need
     not leave a fully consistent tree; a dedicated close pass does.
4. **Close** — the consistency-close: (a) reference-integrity check (§8); (b) a
   **files-absent digest** — re-read the reference and confirm every durable
   piece of knowledge still has a home and is reachable; (c) a full-pool
   regression sweep (run the *entire* probe pool, not just per-iteration draws,
   to catch regressions on probes you did not sample); (d) synthesis of what
   changed and why.

## 5. The measurement instrument

To measure one probe:
1. Stage **two** versions of the memory tree — the prior version and the
   candidate.
2. For each, run a **cold agent isolated to that tree** (see
   `reference/harness-contract.md` for how isolation is achieved and why it
   matters) and pose the **same** probe.
3. Capture each run's **trace** (ordered file-reads) + **final answer**.
4. Score the **paired delta** (§6–7).

The isolation requirement is load-bearing: if the agent can see any memory other
than the staged tree, the trace no longer reflects *that tree's*
discoverability. Full I/O contract, isolation mechanism, and trace-capture
requirements: `reference/harness-contract.md`.

## 6. Probe design

A good pool is **stratified** so a change that helps in easy cases but hurts in
hard ones cannot hide behind an average.

- **Two axes:** **Depth** (how much synthesis the task needs: shallow
  fact-locate → deep multi-file correctness reasoning) × **Closeness** (how
  directly the probe names its target: near = names it, far = describes only the
  need).
- **Expected-reach key:** for each probe, the set of files a correct answer
  should reach. **When a change MOVES a concept, the key differs per arm** — the
  prior arm's key names the old location, the candidate arm's key names the new
  location plus the index/pointer that should now route there.
- **Session-start baseline:** the small set of always-read index/entry files a
  cold agent opens first. Track separately; a change that breaks it is a hard
  regression.
- **The load-bearing technique — ambiguous-entry probes.** A probe that does
  **not** name the target file is the only kind that can detect a *retrieval-
  altitude* change: did creating a new index or domain let a cold agent reach a
  concept **from the top**, rather than only via a buried path? Probes that name
  the target ("beeline" probes) cannot detect altitude changes — they will pass
  regardless — so use them only as **guards** (confirm a specific file is still
  reachable), never as the primary altitude signal.

Stratification schema, per-arm key schema, the ambiguous-entry technique, the
session-start baseline, and the step-by-step probe-generation method:
`reference/probe-design.md`. One small worked example pool:
`reference/probe-example.md`.

## 7. Scoring & verdict logic

Per probe, per arm, from the trace + answer, judge: **recall** (did it reach the
key files?), **precision/directness** (did it avoid opening irrelevant files?),
**session-start hygiene** (where the task needs it), **answer correctness**
(right identity, right consult set, no wrong-domain contamination), and
**path-directness** (index → target, vs wandering).

Then emit a **paired per-probe verdict** {up / flat / down} comparing candidate
to prior on the **same** draw:
- **Noise band:** a ±1-file reach difference with unchanged answer and unchanged
  session-start hygiene is **flat**, not signal. Real signal needs an answer-
  quality change, a session-start-hygiene change, or a consistent ≥2-file shift.

Roll up to an **iteration verdict** (rationale-based, no numeric average):
- **ACCEPT** — net-up AND no stratum systematically regressed (especially
  far/deep) AND session-start hygiene intact.
- **HOLD** — flat overall. Discoverability-neutral; keep the change only if
  justified on another axis (leanness/relations/fidelity) and record which. A
  near-null change landing HOLD is an expected, valid outcome.
- **REJECT** — net-down, OR any far/deep stratum regressed, OR any session-start
  break. Reverse or fix-and-re-measure.

**Stratum guard:** always report the verdict split by Depth × Closeness, not
just the aggregate — that split is the whole point of stratifying. Generalized,
persona-neutral rubric: `reference/scoring-rubric.md`.

## 8. Invariants (hard rules, non-tradeable)

- **Hold the reference constant.** The original tree is never edited; it is the
  fixed baseline every measurement and integrity check compares against.
- **Copy-forward, delete-free build.** Each version is a copy of the previous
  plus additive edits. **Defer ALL deletions to a single human-gated adoption
  pass** at the very end. Never delete during iteration.
- **Reference-integrity check at every milestone.** Keep a digest/checksum of
  the reference and re-verify it at each milestone. Any drift = **hard stop**
  (something touched the baseline; investigate before continuing).
- **Never auto-restructure foundational or safety rules.** Rules governing the
  agent's identity, mission, or destructive-operation safety are out of scope by
  construction — do not move, split, or rewrite them automatically.
- **Human sign-off gates adoption.** Merging the winning version back into the
  live tree (and performing the deferred deletes) is always a human decision.

## 9. Termination

- **Primary signal — diminishing returns:** stop when a full pass surfaces no
  change worth making. A terminal HOLD / no-change pass is a valid, successful
  ending — do **not** manufacture edits to look productive.
- **Fallback bounds:** a small iteration floor (so you actually exercise the
  loop) and a cap (so it cannot run forever).
- **Silence at a checkpoint = failure.** Every loop, including the close sweep,
  must emit an explicit verdict (ACCEPT / HOLD / REJECT) **and** a
  revision-or-no-change statement. Producing no verdict is itself a defect.

## 10. Dependency — the harness

The measurement needs a harness with two parts:
1. A **host-agnostic contract** (the primary spec): inputs = a memory-tree copy
   + a probe + a model; outputs = an ordered file-read trace + a final answer;
   plus the isolation requirement, trace capture, and the paired-delta scoring
   interface. Any host can implement it. → `reference/harness-contract.md`.
2. A **reference adapter** for one specific host (Cursor SDK), generalized and
   persona-neutral, argparse-driven. → `harness/run_probe_cursor.py`, with run
   instructions, auth/credential notes, and a manual smoke-test procedure in
   `harness/README.md`. Batch a whole probe draw into one script
   (`harness/example-driver.sh`) because auth approval does not persist across
   runs — one approval per draw.

A foreign host without the reference adapter writes its own adapter **against
the contract**; the contract, not the adapter, is the portable artifact.

## 11. Anti-criteria

- **Measured, not asserted** — no change is accepted on "looks better" alone.
- **Additive-first** — build by adding (new parent/index/back-link), not by
  destructive moves; deletes are deferred and human-gated.
- **Human-gated adopt** — nothing merges to the live tree without sign-off.
- **Foundational/safety rules untouched** — never auto-restructured.
- **Self-contained** — this method embeds everything it needs; it does not
  depend on any specific memory tree's internal names or paths.
