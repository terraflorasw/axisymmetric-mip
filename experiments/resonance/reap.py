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


def orphans():
    out = subprocess.run(["ps", "-o", "pid=,ppid=,stat=,etime=,comm="],
                         capture_output=True, text=True).stdout
    found = []
    for line in out.splitlines():
        f = line.split(None, 4)
        if len(f) < 5 or f[4].strip() != EXE[:15]:
            continue
        pid, ppid, stat = int(f[0]), int(f[1]), f[2]
        if "Z" in stat:                      # container PID 1 does not reap
            continue
        if ppid == 1:                        # parent gone -> orphan
            found.append((pid, f[3]))
    return found


if __name__ == "__main__":
    o = orphans()
    if not o:
        print("no orphaned palace ranks")
        sys.exit(0)
    print(f"{len(o)} orphaned rank(s):")
    for pid, et in o:
        print(f"  pid {pid}  running {et}")
    if "--kill" in sys.argv:
        for pid, _et in o:
            try:
                os.kill(pid, 15)
                print(f"  killed {pid}")
            except OSError as e:
                print(f"  {pid}: {e}")
    else:
        print("\n  (dry run — pass --kill to stop them)")
