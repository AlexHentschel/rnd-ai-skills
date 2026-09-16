# Harness contract (host-agnostic)

The measurement instrument for the memory-maintenance cycle. This document is
the **portable spec**: it describes *what* the harness must do, independent of
any coding-agent host. A specific host (see `../harness/run_probe_cursor.py` for
one worked adapter) implements it; a different host writes its own adapter
against this same contract.

## Terms
- **Memory tree** — the directory of markdown files an agent loads as durable
  guidance (rules, knowledge notes, indexes). The thing under evaluation.
- **Cold agent** — a fresh agent instance with no conversation history, pinned
  to read only one staged memory tree.
- **Probe** — a natural-language question posed to the cold agent.
- **Trace** — the ordered sequence of file-read (and file-search) tool calls the
  agent made while answering.

## I/O contract

**Inputs**
- `rules` — path to a memory-tree directory to evaluate (its *contents* become
  the agent's memory).
- `prompt` — the probe text (or a path to a file containing it).
- `model` — the model identifier the cold agent runs on (pin one model for a
  whole cycle so it is not a confound).

**Outputs** (per run)
- The **ordered file-read trace**: which files the agent opened, in what order,
  distinguishing *opened/read* from *located-only* (a search that named a file
  without opening it). This distinction matters for scoring (see
  `scoring-rubric.md`).
- The **final answer** text.
- A run status and, ideally, a run identifier for auditability.

The **trace + final answer together are the discoverability signal.** The trace
shows *how* the agent reached (or failed to reach) the relevant material; the
answer shows *whether* it ended up correct.

## Isolation requirement (load-bearing)

The cold agent must see **only** the staged memory tree — no other project, no
host-level or user-level memory, no ambient files. Otherwise the trace no longer
reflects *that tree's* discoverability.

A proven isolation mechanism (host-agnostic in spirit):
1. Create a fresh temporary directory **outside any real workspace/project
   root**.
2. Copy the memory tree into it at the location the host expects project-scoped
   memory to live (e.g. a conventional `<tmp>/<project-memory-dir>/`).
3. Point the agent's working directory at that temp dir and configure it to load
   **project-scoped settings only** — not user/team/global sources — so nothing
   leaks in.
4. Run, capture, then discard the temp dir.

The requirement is: **staged tree in, isolated, nothing else visible.** How a
given host achieves "project-scoped only" varies; the adapter documents its
host's mechanism.

## Trace capture requirement

The adapter must surface the agent's tool activity so the caller can reconstruct
the ordered read set. At minimum, capture each file-read / file-search tool call
with its target path. Persist the trace + answer to a file per run (probes are
run in batches; you will parse these afterward).

## Paired-delta scoring interface

The harness runs **one probe against one tree** and returns one trace+answer. It
does **not** score. Scoring is a separate step (`scoring-rubric.md`) that
consumes **two** harness runs — the same probe against the *prior* tree and the
*candidate* tree — and compares them.

Contract obligations that make paired scoring valid:
- **Same probe text, same model, same isolation** for both arms.
- **Fresh cold agent per run** (no state carried between prior and candidate, or
  between probes).
- The two runs are independent; the caller pairs them by probe id.

Absolute reach on a single arm is noise; only the prior-vs-candidate **delta** on
the same probe draw is trusted.

## What the harness deliberately does NOT do

- **No scoring / no machine trace-metrics.** Verdicts are judged (by a human or
  a judging agent) per `scoring-rubric.md`. Auto-scoring is an unproven
  extension, out of scope.
- **No probe generation.** Probes are authored per the method in
  `probe-design.md`.
- **No standing/persistent state across cycles.** Each run stages fresh and
  discards.

## Adapter checklist (for a new host)

An adapter conforms if it: (1) takes `rules`, `prompt`/`prompt-file`, `model`;
(2) stages an isolated cold agent seeing only the staged tree; (3) emits the
ordered file-read trace + final answer to a persistable form; (4) runs one
probe against one tree per invocation; (5) carries no state between runs.
