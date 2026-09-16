# Worked example probe set (persona-neutral)

A small, **fictional** example to show the *shape* of a probe pool, the per-arm
keys, and the ambiguous-entry-vs-guard distinction. It is illustrative only — do
not ship it; generate your own pool per `probe-design.md`.

## The fictional memory tree

A coding agent for a backend web service. Its memory tree (markdown files):

```
INDEX.md                      # top-level index (session-start)
domains/INDEX.md              # domain index (session-start)
style-guide.md                # writing/style rules (session-start)
domains/testing/flaky-tests.md
domains/testing/coverage-argument.md
domains/api-design/pagination.md
domains/api-design/rate-limiting.md      # <-- MOVES in the candidate
domains/api-design/retry-policy.md       # <-- MOVES in the candidate
domains/observability/structured-logging.md
domains/security/input-validation.md
```

**Session-start baseline `B`:** `INDEX.md`, `domains/INDEX.md`, `style-guide.md`.

## The candidate change

Create a new domain `domains/resilience/` with its own `domains/resilience/INDEX.md`,
and move `rate-limiting.md` and `retry-policy.md` into it (with back-links added
to `domains/api-design/` and an entry added to `domains/INDEX.md`). Goal: make
"resilience" concepts reachable **from the top** as a group, rather than buried
inside the API-design domain.

- **prior version** = tree above (the two files still under `api-design/`).
- **candidate version** = same tree + new `resilience/` domain holding the two
  moved files + routing added.

## The probe pool

Tags: `[Depth][Closeness]`. Keys are per-arm where a file moved.

### Primary signal — ambiguous-entry probes (do NOT name the target)

- **E1 · [D2][far] · resilience reach-from-top.**
  *"I need to make a flaky downstream call robust — throttling requests and
  retrying failures. What guidance do I have, and where?"*
  - prior key: `domains/api-design/rate-limiting.md`,
    `domains/api-design/retry-policy.md` (reached by scanning the api-design
    domain).
  - candidate key: `domains/resilience/INDEX.md` →
    `domains/resilience/rate-limiting.md`, `domains/resilience/retry-policy.md`
    (reached from the top via `domains/INDEX.md` → the new resilience domain).
  - *What it detects:* did the new domain raise retrieval altitude — can the
    cold agent now reach both concepts as a group from the top index?

- **E2 · [D3][far] · design a resilient client.**
  *"Design the client-side policy for calling an unreliable third-party API."*
  - prior key: the two api-design files + `domains/observability/structured-logging.md`.
  - candidate key: `domains/resilience/INDEX.md` + the two moved files +
    `structured-logging.md`.
  - *What it detects:* under synthesis load, does the regroup help the agent
    assemble the full set rather than miss one of the moved files?

### Guards — beeline probes (name the target; must stay FLAT)

- **E3 · [D1][near] · rate-limiting locate.**
  *"Where is the rate-limiting note?"*
  - prior key: `domains/api-design/rate-limiting.md`.
  - candidate key: `domains/resilience/rate-limiting.md`.
  - *Guard:* the moved file is still directly reachable. Must not regress.

- **E4 · [D1][near] · retry-policy locate.**
  *"Where is the retry-policy note?"*
  - prior key: `domains/api-design/retry-policy.md`.
  - candidate key: `domains/resilience/retry-policy.md`.

### Control — untouched area (must stay FLAT)

- **E5 · [D1][near] · pagination locate.**
  *"Where is the pagination guidance?"*
  - key (both arms): `domains/api-design/pagination.md`.
  - *Control:* an unrelated api-design query should be unaffected by the move —
    detects spurious global drift.

## Expected reading of results

- **Guards E3/E4 flat** (target reached in both arms, via new path in candidate)
  + **control E5 flat** ⇒ the move orphaned nothing and caused no drift.
- **Ambiguous-entry E1/E2 flat→up** (candidate reaches the same or fuller set,
  and now from the top index) ⇒ the regroup raised altitude. → **ACCEPT**.
- If instead E1/E2 went **down** (cold agent no longer finds the moved concepts
  from the top, e.g. `domains/INDEX.md` was not updated) while guards stayed flat
  ⇒ a routing gap ⇒ **REJECT** and fix the index before re-measuring. This is
  exactly the failure a beeline-only pool would have missed.
