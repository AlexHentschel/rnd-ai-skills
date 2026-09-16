# Provenance — memory-maintenance-cycle

## Origin
Distilled from **two fully-worked, human-supervised full-memory maintenance cycles** on a large,
long-lived coding-agent memory tree (markdown rules + concept notes + indexes). Both cycles reorganized
the tree for retrieval while gating every structural change on a **paired cold-agent retrieval eval**
(score the prior and candidate versions on the same probe draw; trust the delta, not the level). The
**method** is the product — no host-specific tree names, paths, or persona content are reproduced here; the
worked example in `reference/probe-example.md` is illustrative only.

## How it was derived
Reflective extraction from the two cycles' execution records (plan + migration ledger + per-iteration
setup/apply/measure/verdict + end-of-cycle synthesis), not from any one memory tree:
1. Reconstruct the four-phase spine (pre-plan → draft → execute-loop → close) actually run.
2. Abstract to a host-agnostic contract: the priority order (discoverability > fidelity > leanness), the
   paired-delta trust unit, the stratified probe design (Depth × Closeness + ambiguous-entry altitude
   probes), and the ACCEPT/HOLD/REJECT verdict logic — dropping all tree-specific names.
3. Split the portable **contract** (`reference/harness-contract.md`) from the one concrete **reference
   adapter** (`harness/run_probe_cursor.py`, Cursor SDK) so a foreign host writes its own adapter against
   the contract rather than porting the script.

## Evidence basis & confidence
- Derived from **2 completed cycles** (the second independently reinforcing the first).
- The **isolation mechanism** (stage the tree in a temp dir outside any workspace root; cold agent pinned
  to project-scoped settings only) and the **trace-as-signal** approach were validated on live runs.
- The reference adapter is **Cursor-SDK-specific**; the contract is host-agnostic.

## Scope deferrals (intentional — not shipped; future hypotheses, not built)
- **No second/third host adapter** — only the host-agnostic contract + this one Cursor adapter.
- **No auto-scorer / machine-scored trace metrics** — scoring stays human/judge-led (a machine reach-trace
  misses semantic-routing quality).
- **No probe-generator CLI** — the probe-design method + one worked example ship instead.
- **No relation-audit or graph-search as separate skills** — relation-audit belongs as a close-phase step.
- **No standing cross-cycle probe pool infrastructure.**

If generalizing beyond this manifest becomes tempting, ship as-is and record the further deferral here
rather than expanding scope silently.

## Dates & licensing
- Installed into this repo 2026-09-16 (generalized from cycles run 2026-08 and 2026-09).
- Original authored content; covered by the repository-root `LICENSE` (MIT).
