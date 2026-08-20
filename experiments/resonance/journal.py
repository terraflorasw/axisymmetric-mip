#!/usr/bin/env python3
"""Append-only run journal. One fsync'd JSON line per event, written AS IT HAPPENS.

WHY. Rigs held every result in memory and wrote one summary JSON at the end, so
an interruption lost the whole run's bookkeeping even though Palace had already
written each solve's output to postpro/. On a SPOT instance with a two-minute
termination notice that is the difference between losing one solve and losing a
day.

🔑 JSONL, NOT JSON. A whole-file rewrite can be truncated mid-write and leave
NOTHING readable. An append of one line either lands or does not, and every
earlier line stays valid — so a killed run yields a partial record instead of a
corrupt one. Each line is independently parseable, so recovery needs no special
case.

⚠️ fsync ON EVERY LINE. Without it the data sits in the page cache and a hard
termination loses it, which would defeat the entire point while looking fine in
testing.

    journal.log("e1b", event="solve", tag="e1b_A_tran", seconds=2141)
    journal.read("e1b")            -> [ {...}, {...} ]
"""
import json
import os
import pathlib
import time


def log(run, **fields):
    """Append one event. Never raises into the caller — a journal failure must
    not kill a run that is otherwise fine."""
    rec = dict(t=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), **fields)
    try:
        p = pathlib.Path(f"{run}.jsonl")
        with open(p, "a") as f:
            f.write(json.dumps(rec, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())
    except Exception as e:                      # noqa: BLE001
        print(f"  ⚠️ journal write failed ({e}) — run continues", flush=True)
    return rec


def read(run):
    """Every event, skipping any final torn line from a hard kill."""
    p = pathlib.Path(f"{run}.jsonl")
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            pass                                # a torn tail is expected
    return out


if __name__ == "__main__":
    import sys
    for r in sys.argv[1:]:
        ev = read(r)
        print(f"{r}: {len(ev)} events")
        for e in ev:
            print("  " + json.dumps(e)[:150])
