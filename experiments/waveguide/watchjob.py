#!/usr/bin/env python3
"""Watch a long job: wake on completion OR on a deadline, and DIAGNOSE either way.

Built after a night of doing this by hand. Two jobs burned hours unnoticed —
3h51m on a band 1,227 linewidths wide, and 50 min at 99.9% CPU on 37k unknowns
that never converged — because the only signal available was "has it finished",
which is silent precisely when something is wrong.

    watchjob.py LOGFILE EXPECTED_SECONDS --uid TOKEN [--sentinel REGEX]
    watchjob.py --newuid          # print a fresh token

Wakes on the FIRST of:
  · sentinel matched AND no process    -> COMPLETED
    (a sentinel alone NEVER ends the watch while the job is alive —
     a startup banner that quotes the sentinel would end it at once)
  · no matching process alive          -> EXITED (crashed, or finished quietly)
  · elapsed > 3x EXPECTED_SECONDS      -> OVERRUN, with a diagnosis

⚠️ Rule of thumb for EXPECTED_SECONDS: bound at ~3x what you expect, so a hang
self-reports instead of being discovered hours later by someone asking why it is
taking so long.

THE DIAGNOSIS IS THE POINT. On overrun it distinguishes:
  · log growing            -> slow but progressing; extend or accept
  · log frozen, CPU ~100%  -> NOT converging. A longer wait will not help.
  · log frozen, CPU ~0%    -> deadlocked or waiting on I/O
Those look identical from "still running", and they need opposite responses.

🔑 USE --uid. IT IS THE ONLY ROBUST WAY TO FIND THE JOB.

    UID=$(python3 watchjob.py --newuid)
    python3 -u sweep.py --uid $UID > job.log 2>&1; echo "EXIT=$?" >> job.log   # job
    python3 -u watchjob.py job.log 2600 --uid $UID --sentinel '^EXIT='         # watcher

The old PROC_PATTERN is still accepted and is still a trap. Every workaround for
it has been a way of spelling the job's name so the watcher cannot read its own
command line, and each one has failed differently:

  scatter.py        matches the watcher's own argv                -> never exits
  [s]catter.py      works, until the plain token appears anywhere
                    else in the same command block                -> never exits
  rig_si"gma.py"    quoted so the shell strips it for the child... but wrapped in
                    single quotes, so it did not: the child got a pattern that
                    matches no real process, and the wrapper's argv contained
                    that same literal text                        -> matched ITSELF
                                                                     and reported a
                                                                     finished job as
                                                                     still running

The pattern of failure is the point: bracketing only defeats self-match when the
REGEX TEXT and the ARGV TEXT differ, so every fix is one careless quote away from
re-synchronising them. --uid removes the class of bug instead of respelling it:

  · the token is RANDOM, so it cannot collide with anything incidental;
  · the watcher EXCLUDES ITS OWN PROCESS ANCESTRY (itself, its wrapper shell, and
    that shell's parents), which is exactly the set of processes that carry the
    watcher's command text. Self-match is then structurally impossible, not
    avoided by careful spelling.

The job's own wrapper shell also carries the token, and that is deliberate: it is
genuinely alive for as long as the job is, so detection survives the job re-execing
or shelling out to mpiexec.
"""
import os, random, re, string, subprocess, sys, time, pathlib

def newuid():
    """A token that cannot occur by accident in a process table."""
    return "wjuid" + "".join(random.choices(string.ascii_lowercase + string.digits,
                                            k=10))

def _ancestry(pid=None):
    """This process and every parent of it, by PID.

    These are the processes that carry THIS watcher's command line — and
    therefore the uid we are searching for. Excluding them is what makes the
    search self-blind by construction.
    """
    seen, pid = set(), pid or os.getpid()
    while pid and pid not in seen:
        seen.add(pid)
        try:
            stat = pathlib.Path(f"/proc/{pid}/stat").read_text()
            pid = int(stat[stat.rindex(")") + 2:].split()[1])   # ppid
        except (OSError, ValueError, IndexError):
            break
    return seen

def alive(pat, uid=None):
    """Lines from ps for the watched job. uid is exact-token and self-blind."""
    if not (pat or uid):
        return None
    out = subprocess.run(["ps", "-o", "pid=,stat=,pcpu=,args="],
                         capture_output=True, text=True).stdout
    mine = _ancestry() if uid else set()
    hits = []
    for l in out.splitlines():
        f = l.split(None, 3)
        if len(f) < 4 or " Z" in f[1][:2] or "Z" == f[1][:1]:
            continue
        if uid:
            if uid not in f[3] or int(f[0]) in mine:
                continue
        else:
            if not re.search(f"[{pat[0]}]{pat[1:]}", l):
                continue
        hits.append(l)
    return hits

def main():
    if "--newuid" in sys.argv:
        print(newuid())
        return
    flags = {"--sentinel", "--uid"}
    a, skip = [], False
    for i, x in enumerate(sys.argv[1:]):
        if skip:
            skip = False
        elif x in flags:
            skip = True
        elif not x.startswith("--"):
            a.append(x)
    sent = uid = None
    if "--sentinel" in sys.argv:
        sent = sys.argv[sys.argv.index("--sentinel") + 1]
    if "--uid" in sys.argv:
        uid = sys.argv[sys.argv.index("--uid") + 1]
    log, expect = pathlib.Path(a[0]), float(a[1])
    pat = a[2] if len(a) > 2 else None
    if uid and pat:
        sys.exit("give --uid OR a PROC_PATTERN, not both — two detectors "
                 "disagreeing is worse than one.")
    deadline = 3.0 * expect
    t0 = time.time()
    prev = log.stat().st_size if log.exists() else 0
    grew_at = t0
    while True:
        time.sleep(min(60.0, max(5.0, expect / 10.0)))
        el = time.time() - t0
        size = log.stat().st_size if log.exists() else 0
        if size > prev:
            prev, grew_at = size, time.time()
        txt = log.read_text(errors="replace") if log.exists() else ""
        procs = alive(pat, uid)
        # ⚠️ THE PROCESS IS AUTHORITATIVE OVER THE SENTINEL. A sentinel matched
        # while the job is still running is a FALSE COMPLETION, and it is easy
        # to hit: rig_cap.py prints its own docstring at startup, that docstring
        # documents its VERDICTS, and a --sentinel of 'VERDICT|EXIT=' matched at
        # 60 s on a 50-minute job. The watcher reported COMPLETED for a job that
        # had not begun its first solve.
        #
        # So a sentinel only ends the watch when no matching process is left. It
        # still helps when PROC_PATTERN is absent or does not match, which is
        # the case it exists for.
        if sent and re.search(sent, txt) and not ((pat or uid) and procs):
            print(f"✅ COMPLETED after {el:.0f}s (sentinel matched, no process "
                  f"alive)")
            break
        if (pat or uid) and not procs:
            print(f"⚠️ EXITED after {el:.0f}s — no matching process. "
                  f"Finished quietly, or crashed.")
            break
        if el > deadline:
            stale = time.time() - grew_at
            cpu = sum(float(l.split()[2]) for l in (procs or []) if l.split()[2:])
            print(f"🔴 OVERRUN: {el:.0f}s elapsed against {expect:.0f}s expected "
                  f"(ceiling {deadline:.0f}s)")
            print(f"   log last grew {stale:.0f}s ago; matched processes at "
                  f"{cpu:.0f}% CPU total")
            if stale > 120 and cpu > 50:
                print("   -> FROZEN LOG AT HIGH CPU: not converging. Waiting "
                      "longer will not help. Kill it and change the problem.")
            elif stale > 120:
                print("   -> frozen log at low CPU: deadlocked or blocked on I/O.")
            else:
                print("   -> still progressing, just slower than expected.")
            break
    tail = [l for l in txt.splitlines() if l.strip()][-3:]
    print("   last log lines:")
    for l in tail:
        print(f"     {l[:110]}")

main()
