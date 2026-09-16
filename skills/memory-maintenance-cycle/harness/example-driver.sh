#!/usr/bin/env bash
# Batch-draw driver TEMPLATE for the paired retrieval eval.
#
# Purpose: run a whole probe DRAW against BOTH arms (prior + candidate) in one
# process, so you approve auth ONCE per draw instead of once per probe.
# Each probe is run against the prior tree and the candidate tree; the two logs
# are then scored as a paired delta (see ../reference/scoring-rubric.md).
#
# This is a TEMPLATE: replace the <PLACEHOLDERS> below. Nothing here is tied to
# any specific memory tree.
set -uo pipefail

# --- Fill these in -----------------------------------------------------------
PY="<PATH-TO-PYTHON>"                       # e.g. python3, or a venv python
HARNESS="<PATH-TO>/run_probe_cursor.py"     # this dir's adapter
PRIOR="<PATH-TO-PRIOR-MEMORY-TREE>"         # version v(k-1)
CAND="<PATH-TO-CANDIDATE-MEMORY-TREE>"      # version v(k)
OUT="<PATH-TO-OUTPUT-DIR>"                  # where per-run logs are written
MODEL="auto"                                # pin ONE model for the whole cycle
# CURSOR_API_KEY must be set in the env or in a .env beside the adapter.
# -----------------------------------------------------------------------------

mkdir -p "$OUT"

# Map probe id -> probe text. Add one line per probe in your draw.
# Keep "Read only; do not modify files." so the cold agent does not edit the
# throwaway staged copy.
prompt_for () {
  case "$1" in
    P01) echo "<AMBIGUOUS-ENTRY PROBE TEXT — describes the need, does NOT name the target file>. Read only; do not modify files.";;
    P02) echo "<GUARD/BEELINE PROBE TEXT — names a specific moved file; must stay flat>. Read only; do not modify files.";;
    P03) echo "<CONTROL PROBE TEXT — untouched area; detects spurious drift>. Read only; do not modify files.";;
    # ... add the rest of the draw ...
  esac
}

# The draw: the probe ids to run this iteration.
PROBES="P01 P02 P03"

run () {
  local arm="$1" rules="$2" pid="$3"
  local pr; pr="$(prompt_for "$pid")"
  echo "=== $pid $arm START $(date +%H:%M:%S) ==="
  "$PY" "$HARNESS" --rules "$rules" --setting project --model "$MODEL" \
      --prompt "$pr" --trace-out "$OUT/${pid}.${arm}.log" \
      > "$OUT/${pid}.${arm}.stdout" 2>&1
  echo "=== $pid $arm DONE exit=$? ==="
}

for pid in $PROBES; do
  run prior "$PRIOR" "$pid"
  run cand  "$CAND"  "$pid"
done
echo "ALL DONE $(date +%H:%M:%S)  (logs in $OUT; score paired deltas per the rubric)"
