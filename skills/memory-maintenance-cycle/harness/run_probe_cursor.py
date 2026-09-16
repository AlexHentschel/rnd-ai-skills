#!/usr/bin/env python3
"""Cursor reference adapter for the memory-maintenance-cycle harness.

Runs a *cold* local Cursor SDK agent whose ONLY memory is a specified rule-tree
copy, poses one probe, and prints the ordered file-read tool-call trace plus the
final answer. That trace + answer is the discoverability signal the paired eval
scores (see ../reference/harness-contract.md and ../reference/scoring-rubric.md).

This is ONE host adapter that conforms to the host-agnostic contract; a
different host writes its own adapter against that contract. It is
persona-neutral and argparse-driven: no hard-coded paths, no probe content
baked in.

Isolation mechanism (Cursor-specific): the SDK local runtime resolves
project-scoped settings relative to the agent's working directory. We stage the
given rule tree as `<tmp>/<memory-subdir>` in a fresh temp dir OUTSIDE any real
workspace root, point the agent's cwd at that temp dir, and set
`setting_sources=['project']` so only the staged tree loads (no user/team/global
memory leaks in). The temp dir is discarded after the run.

Usage:
  CURSOR_API_KEY=... python3 run_probe_cursor.py \
      --rules path/to/memory-tree \
      --setting project \
      --model auto \
      --prompt "Where is the retry policy defined? Read only; do not modify."

  # or read the probe from a file, and persist the trace+answer:
  python3 run_probe_cursor.py --rules path/to/tree \
      --prompt-file probe.txt --trace-out out/E1.candidate.log
"""
import argparse
import os
import shutil
import sys
import tempfile

try:
    from cursor_sdk import Agent, AgentOptions, LocalAgentOptions
except ImportError:  # SDK optional at import time; --help still works.
    Agent = AgentOptions = LocalAgentOptions = None


def _load_env_file() -> None:
    """Load KEY=VALUE lines from a sibling .env (gitignored) into os.environ.

    Lets the operator drop CURSOR_API_KEY into a sibling .env without pasting it
    anywhere tracked. Does not override an already-set env var.
    """
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(env_path):
        return
    with open(env_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key, val = key.strip(), val.strip().strip("'\"")
            os.environ.setdefault(key, val)


def _parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rules", required=True,
                    help="Source memory-tree dir; its CONTENTS become <tmp>/<memory-subdir>")
    ap.add_argument("--memory-subdir", default=".cursor/rules",
                    help="Where the host expects project-scoped memory (default: .cursor/rules)")
    ap.add_argument("--setting", default="project",
                    choices=["project", "all", "user", "team", "mdm", "plugins", "none"],
                    help="setting_sources value ('none' => [], inline-only). Use 'project' for isolation.")
    ap.add_argument("--model", default="auto",
                    help="Model id the cold agent runs on. Pin one model per cycle.")
    ap.add_argument("--prompt", default=None, help="Probe text")
    ap.add_argument("--prompt-file", default=None, help="File containing the probe text")
    ap.add_argument("--trace-out", default=None,
                    help="Optional path to also write the trace + final answer to")
    ap.add_argument("--keep", action="store_true", help="Keep the temp workspace for inspection")
    return ap.parse_args()


def main() -> int:
    _load_env_file()
    args = _parse_args()

    if Agent is None:
        print("FATAL: cursor_sdk not importable; install the Cursor SDK to run probes.",
              file=sys.stderr)
        return 4

    if not os.environ.get("CURSOR_API_KEY"):
        print("FATAL: CURSOR_API_KEY not set in env", file=sys.stderr)
        return 3

    if args.prompt_file:
        with open(args.prompt_file) as fh:
            prompt = fh.read()
    elif args.prompt:
        prompt = args.prompt
    else:
        print("FATAL: provide --prompt or --prompt-file", file=sys.stderr)
        return 3

    src = os.path.abspath(args.rules)
    if not os.path.isdir(src):
        print(f"FATAL: rules dir not found: {src}", file=sys.stderr)
        return 3

    lines = []

    def emit(text: str = "") -> None:
        print(text)
        lines.append(text)

    tmp = tempfile.mkdtemp(prefix="mem-harness-")
    rules_dst = os.path.join(tmp, *args.memory_subdir.split("/"))
    os.makedirs(os.path.dirname(rules_dst), exist_ok=True)
    shutil.copytree(src, rules_dst)
    setting_sources = [] if args.setting == "none" else [args.setting]
    emit(f"[harness] temp workspace:  {tmp}")
    emit(f"[harness] staged memory:   {rules_dst}")
    emit(f"[harness] setting_sources: {setting_sources}")
    emit(f"[harness] model:           {args.model}")
    emit("=" * 70)

    opts = AgentOptions(
        model=args.model,
        api_key=os.environ["CURSOR_API_KEY"],
        local=LocalAgentOptions(cwd=tmp, setting_sources=setting_sources),
    )

    tool_calls = []
    final_text_parts = []
    try:
        with Agent.create(opts) as agent:
            emit(f"[harness] agent_id: {getattr(agent, 'agent_id', '?')}")
            run = agent.send(prompt)
            emit(f"[harness] run.id:   {getattr(run, 'id', '?')}")
            for msg in run.messages():
                mtype = getattr(msg, "type", None)
                if mtype == "assistant":
                    for block in getattr(msg.message, "content", []) or []:
                        if getattr(block, "type", None) == "text":
                            final_text_parts.append(block.text)
                elif mtype == "tool_use" or "tool" in str(mtype or "").lower():
                    tool_calls.append(repr(msg)[:500])
            result = run.wait()
            emit("=" * 70)
            emit(f"[harness] STATUS: {getattr(result, 'status', '?')}")
            emit("=" * 70)
            emit("[harness] TOOL CALLS OBSERVED (ordered read/search trace):")
            for tc in tool_calls:
                emit("  - " + tc)
            emit("=" * 70)
            emit("[harness] FINAL ASSISTANT TEXT:")
            emit("".join(final_text_parts) or getattr(result, "result", ""))
    finally:
        if args.keep:
            emit(f"[harness] kept temp workspace: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)
        if args.trace_out:
            os.makedirs(os.path.dirname(os.path.abspath(args.trace_out)), exist_ok=True)
            with open(args.trace_out, "w") as fh:
                fh.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
