# Harness — run instructions

`run_probe_cursor.py` is the **Cursor reference adapter** for the paired
retrieval eval. It runs one probe against one staged memory tree with an
isolated cold agent and prints the ordered file-read trace + final answer. It
implements the host-agnostic contract in `../reference/harness-contract.md`.

## What it does (and the contract boundary)

- **In scope of this adapter:** stage a memory-tree copy in an isolated temp dir,
  run a cold Cursor SDK agent pinned to it, capture the trace + answer for **one
  probe against one tree**.
- **NOT in this adapter:** scoring, probe generation, pairing. Pairing =
  running the same probe against the *prior* and *candidate* trees (two
  invocations) and comparing per `../reference/scoring-rubric.md`. A driver
  script batches the runs; the human/judge scores the delta.
- **Foreign host?** Do not port this file. Read
  `../reference/harness-contract.md` and write your own adapter against it — the
  contract, not this script, is the portable artifact.

## Requirements

- Python 3.
- The Cursor SDK (`cursor_sdk`) installed in the environment. If it is not
  installed, `--help` still works and the script exits with a clear message
  instead of running.
- A `CURSOR_API_KEY` credential (see below).

## Credentials / auth

- Set `CURSOR_API_KEY` in the environment, **or** drop a gitignored `.env` file
  next to this script containing `CURSOR_API_KEY=...` (the script loads it and
  never overrides an already-set value). Do not commit the key.

## One card approval per draw

Auth approval typically does **not** persist across runs — each probe run may
prompt for one approval. For an unattended batch, put a whole probe draw into a
single driver script (see `example-driver.sh`) so you approve **once per draw**
rather than once per probe. For fully unattended runs, the script must be
allowlisted by the host so it does not block on approval.

## Out-of-sandbox note

The adapter creates a temp workspace **outside** any real project root and runs
a network-backed agent. If your environment sandboxes filesystem/network access,
run it with the sandbox relaxed (out-of-sandbox), and expect the one-approval-
per-draw prompt unless the command is allowlisted.

## Single-probe run

```bash
CURSOR_API_KEY=... python3 run_probe_cursor.py \
    --rules path/to/candidate-memory-tree \
    --setting project \
    --model auto \
    --prompt "Where is the retry policy defined? Read only; do not modify files." \
    --trace-out out/E3.candidate.log
```

Flags: `--rules` (memory tree to stage), `--memory-subdir` (where the host
expects project memory; default `.cursor/rules`), `--setting` (use `project`
for isolation), `--model` (pin one per cycle), `--prompt` / `--prompt-file`,
`--trace-out` (also persist trace+answer), `--keep` (keep temp dir).

## Manual smoke-test procedure

Validate the adapter end to end without a full eval:

1. **Static check (no auth needed):**
   `python3 run_probe_cursor.py --help` — argparse help prints.
2. **Make a tiny throwaway tree:** a temp dir with two or three trivial markdown
   files, one of which clearly answers a question (e.g. a file stating a made-up
   retry rule).
3. **Isolation check — expect the staged tree, nothing else:** run one probe
   whose answer exists only in the throwaway tree
   (`--prompt "What is the retry rule? Cite the file."`). Confirm the trace shows
   the agent reading files **from the staged temp path** and that the answer
   comes from your throwaway file — not from any real project. Add
   `--keep` to inspect the staged temp dir.
4. **Trace capture check:** confirm the `TOOL CALLS OBSERVED` block lists the
   file-read(s) in order, and that `--trace-out` wrote the same content to disk.
5. **Negative isolation check (optional):** run with `--setting none`; the agent
   should have no project memory and be unable to answer from the tree —
   confirming that `--setting project` is what loads the staged tree.

If steps 3–4 pass, the adapter is usable as the eval instrument.
