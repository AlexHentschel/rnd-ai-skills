# Probe design

How to build the stratified probe pool + expected-reach keys that drive the
paired retrieval eval. Probes are authored fresh per memory tree; this document
is the **method**, not a fixed pool. A small worked example is in
`probe-example.md`.

## What a probe is

A probe is a question you pose to a **cold agent** (fresh instance, no history,
pinned to only the staged memory tree). The agent answers by reading files; the
ordered file-reads (the **trace**) plus the answer are what you score. A probe
tests: *can a cold future session find and correctly use the right material?*

## Stratify on two axes

Design the pool so a change that helps easy cases while hurting hard ones cannot
hide behind an average.

- **Depth** — how much synthesis the task needs:
  - **D1** shallow fact-locate ("where is X defined?").
  - **D2** single-topic application ("how do I do X in this domain?").
  - **D3** multi-note synthesis ("design/argue X using several notes").
  - **D4** deep cross-cutting reasoning (a full correctness/verification task).
- **Closeness** — how directly the probe points at its target:
  - **near** — names the target concept/file.
  - **mid** — names the task but not the file.
  - **far** — describes only the *need*; the agent must infer where to look.

Aim for coverage across the grid. Record each probe's `[Depth][Closeness]` tag;
you will report verdicts split by stratum (the **stratum guard**).

## Expected-reach key (with per-arm variants)

For each probe, write an **expected-reach key** `K`: the set of files a correct
answer should reach. Keys are targets for scoring, not absolute ground truth — a
defensible reach outside `K` is judged on merit (and, if it recurs, promoted
into `K` with a logged note).

**Per-arm keys when a concept MOVES.** If the change relocates a concept, the
key differs between the two versions being compared:
- **prior arm key** — names the concept at its **old** location.
- **candidate arm key** — names the **new** location **plus** the index or
  pointer that should now route a cold agent there.

This is what lets you check that a move did not just relocate a file but kept it
*reachable* through the new routing.

## Session-start baseline

Most memory trees have a small set of **always-read entry files** — top-level
indexes and a primary log/style file — that a cold agent opens first regardless
of the task. List them once as the **session-start baseline** `B`. Do not
re-list `B` in every key; instead track, per probe, whether the agent's
session-start hygiene held. A change that breaks the baseline is a hard
regression. (Caveat: a task-driven cold agent often beelines and skips ritual
reads; judge hygiene only where the task actually needs the baseline.)

## The load-bearing technique: ambiguous-entry probes

An **ambiguous-entry probe** deliberately does **not** name the target file — it
describes only the need. Example shape: instead of "where is the retry-policy
note?", ask "I want to make a flaky downstream call resilient — what guidance do
I have and where?"

Why it is load-bearing: only an ambiguous-entry probe can detect a change in
**retrieval altitude** — i.e. whether a new index or a new domain lets a cold
agent reach a concept **from the top** instead of via a buried path. A probe
that names the target ("beeline" probe) will reach it whether or not the
altitude improved, so it **cannot** measure altitude. Use beeline probes only as
**guards** — to confirm a specific file is still reachable after a move — never
as the primary signal for a regroup/reindex.

Rule of thumb: **every structural change whose point is "make X easier to reach
from the top" needs at least one ambiguous-entry probe aimed at X**, plus beeline
guards on the specific files that moved.

## The probe-generation method (step by step)

1. **Inventory the change.** List what the candidate version changes — which
   concepts move, which indexes are added, which files split/merge.
2. **For each change, ask "what should now be easier to reach, and from where?"**
   Write one **ambiguous-entry** probe for that reach goal (primary signal).
3. **Add beeline guards** for each specific file that moved or split, to confirm
   it is still directly reachable (these must stay flat).
4. **Add control probes** in untouched areas, to confirm the change caused no
   spurious global drift.
5. **Spread across the Depth × Closeness grid** — deliberately include some
   far/deep probes; those are where structural changes bite hardest.
6. **Write the expected-reach key** for each probe, per-arm where a concept
   moved (old path for prior, new path + router for candidate).
7. **Fix a session-start baseline** and note which probes genuinely depend on it.
8. **Pin one model** for the whole cycle; run every probe against both arms with
   the same text and model.

## Scope note

Probes measure discoverability **within the staged memory tree only.** Anything
the agent relies on that lives *outside* that tree (host-level tools, external
skills) is not measured here — keep probes aimed at in-tree reach.
