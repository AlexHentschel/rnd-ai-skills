# Scoring rubric (persona-neutral)

How to turn two harness runs (same probe, prior vs candidate) into a verdict.
Applied **identically to both arms**. **The signal is the paired delta, not the
absolute level.** Revisable between iterations (state any revision audibly).

## Input per probe run

The harness output for one arm: the ordered file-read/file-search **trace** +
the **final answer**. Distinguish files the agent **opened/read** from files it
only **located** (a search that named a path without opening it) — parse the
opened set as the observed reach `R`.

## 1. Per-probe raw measures (per arm)

Given the probe's expected-reach key `K` (task-specific target files; per-arm
where a concept moved) and the session-start baseline `B` (always-read entry
files):

- **Recall (reach)** = |R ∩ K| / |K|. Did it surface the files it should?
  (misses = K \ R.)
- **Session-start hygiene** = did it open the baseline `B` **where the task needs
  it**? A task-driven cold agent often beelines and skips ritual reads — judge
  hygiene only where the task genuinely depends on the baseline. A change that
  breaks *needed* session-start retrieval is a hard regression.
- **Precision (directness)** = |R ∩ (K ∪ B ∪ defensible)| / |R|. Penalizes
  over-retrieval — files opened that are neither in the key, the baseline, nor
  defensibly justified. (`defensible` = a reasonable reach not in `K`, e.g. a
  related note; judge on merit, and if it recurs promote it into `K` with a
  logged note.)
- **Answer correctness** (3-state {ok / partial / wrong}) — does the answer
  (a) state the right identity/role, (b) name the right consult set, (c) avoid
  wrong-domain contamination?
- **Path-directness** (qualitative {direct / mixed / wandering}) — did it route
  efficiently (index → target) or wander (dead-end searches, re-reads,
  scattershot)?

## 2. Per-probe paired verdict {up / flat / down}

Compare candidate to prior on the **same** probe draw and model:
- **up** — recall ↑ (a previously-missed key file now reached) OR precision ↑
  (dropped a real over-retrieval) OR answer improved OR path became direct —
  **with no offsetting regression** on the other measures.
- **down** — the mirror: a key file newly missed, new over-retrieval, answer
  degraded, or session-start hygiene broken.
- **flat** — within noise. **Noise band: a ±1-file reach difference with
  unchanged answer-correctness and unchanged session-start hygiene is FLAT, not
  signal.** Directional signal requires an answer-quality change, a
  session-start-hygiene change, or a consistent ≥2-file shift in one direction.

## 3. Iteration verdict (aggregate, rationale-based — no numeric average)

- **ACCEPT** — net-up (more up than down) AND **no stratum systematically
  regressed** (especially far/deep, where structure bites) AND session-start
  hygiene intact where needed.
- **HOLD** — flat overall (ups ≈ downs, or all-flat). The change is
  discoverability-neutral; keep it only if justified on another axis
  (leanness / relations / fidelity) — **record which**. A near-null or
  calibration change landing HOLD is an expected, valid outcome.
- **REJECT** — net-down, OR any far/deep stratum regressed, OR any session-start
  break. Reverse the change, or fix and re-measure.

**Stratum guard:** always report the verdict **split by Depth × Closeness**, not
just the aggregate — a change can be net-up on easy-near while regressing
far/deep, and the split is the whole reason for stratifying.

## 4. Deliberately NOT done

- **No absolute score / no cross-iteration numeric comparison.** Level drifts
  with the sample; only the within-iteration paired delta is trusted.
- **No chasing 1-file wiggles.** Per-run model variance is real; the noise band
  absorbs it. If a probe's verdict flips on re-run with no tree change, widen the
  band or add a probe — do not over-read it.
- **No overfitting to a fixed sample.** Randomize the per-iteration draw (log the
  seed); run the **full pool** at milestones to bound regression on unsampled
  probes.

## 5. Logging (per iteration)

Record: the seed + sampled probe ids; per probe, both arms' (recall, precision,
session-start, answer, path) + the paired verdict; the aggregate verdict + the
stratum split; run ids + captured trace-file paths; any key revisions
(defensible-reach promotions) with rationale. This separates model/sampling
variance from real change and makes the verdict auditable by a cold reader.

## 6. Operational note

Auth typically does **not** persist across harness runs. Batch a whole probe
draw into ONE script so you approve once per draw (see
`../harness/example-driver.sh`). Pin one model for the whole cycle.
