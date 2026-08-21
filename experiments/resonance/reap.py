#!/usr/bin/env python3
"""Kill ORPHANED Palace ranks. Safe by construction — no pattern matching.

WHY THIS EXISTS. `subprocess.run(timeout=…)` RAISES BUT DOES NOT KILL. Four
separate runs in one session left ranks alive past their own timeout; one of them
ran 90 minutes unnoticed, and twelve concurrent processes eventually thrashed the
user's machine during their standup. The drivers are fixed to Popen+kill, but a
driver that dies for any other reason still leaks.

🔴 AND THE OBVIOUS CLEANUP IS FORBIDDEN. `pkill -f palace` matches the harness
wrapper shell, which carries the entire command block in its argv — it kills the
calling shell (exit 144, observed three times in this project). So:

  · find candidates by EXACT executable name, never by substring of a command line
  · keep only those whose parent is gone (PPID 1) — a live parent means a live job
  · kill by PID, one at a time

    python3 reap.py          list orphans, kill nothing
    python3 reap.py --kill   kill them
"""
import os
import subprocess
import sys

EXE = "palace-x86_64.bin"
# 🔴 RANKS ARE NEVER DIRECT CHILDREN, AND THIS FILE ASSUMED THEY WERE. The real
# launch tree has two layers between the rig and the ranks:
#
#     palace   (a bash WRAPPER script)   <- this is what gets orphaned
#       └── prterun
#             └── palace-x86_64.bin xN
#
# So "palace-x86_64.bin with PPID 1" matched nothing while four ranks ground
# away for 20 minutes after E0v killed e0l_scaling.py — this file printed "no
# orphaned palace ranks" the whole time. An orphan detector that reports clean
# during a live leak is worse than none, because it is believed.
#
# Correct test: walk UP from each rank. If any ancestor has PPID 1, the whole
# tree is orphaned. That is independent of how many layers the launcher uses.
ROOTS = ("palace", "prterun")               # wrapper and MPI launcher


def _table():
    out = subprocess.run(["ps", "-eo", "pid=,ppid=,stat=,etime=,comm="],
                         capture_output=True, text=True).stdout
    procs = {}
    for line in out.splitlines():
        f = line.split(None, 4)
        if len(f) < 5:
            continue
        procs[int(f[0])] = {"ppid": int(f[1]), "stat": f[2], "etime": f[3],
                            "comm": f[4].strip()}
    return procs


def orphans():
    """[(pid, etime)] — ranks whose ANCESTRY reaches init, at any depth."""
    procs = _table()
    found = []
    for pid, p in procs.items():
        if p["comm"] != EXE[:15] or "Z" in p["stat"]:
            continue
        cur, seen = pid, set()
        while cur in procs and cur not in seen:
            seen.add(cur)
            nxt = procs[cur]["ppid"]
            if nxt == 1:
                found.append((pid, p["etime"]))
                break
            cur = nxt
    return sorted(found)


def orphan_roots():
    """The launcher processes to kill — killing ranks alone leaves these."""
    procs = _table()
    return sorted(pid for pid, p in procs.items()
                  if p["ppid"] == 1 and p["comm"] in ROOTS)


if __name__ == "__main__":
    o = orphans()
    if not o:
        print("no orphaned palace ranks")
        sys.exit(0)
    print(f"{len(o)} orphaned rank(s):")
    for pid, et in o:
        print(f"  pid {pid}  running {et}")
    roots = orphan_roots()
    if roots:
        print(f"orphaned launcher(s): {roots}  — killing ranks alone leaves "
              f"these, and they are what the rig actually spawned")
    if "--kill" in sys.argv:
        # ranks first, then the launchers above them
        for pid, _et in o:
            try:
                os.kill(pid, 15)
                print(f"  killed rank {pid}")
            except OSError as e:
                print(f"  {pid}: {e}")
        for pid in roots:
            try:
                os.kill(pid, 15)
                print(f"  killed launcher {pid}")
            except OSError as e:
                print(f"  {pid}: {e}")
    else:
        print("\n  (dry run — pass --kill to stop them)")
