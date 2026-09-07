#!/usr/bin/env bash
# Watch a run BY SLUG, then DO THE END-OF-RUN THINGS. The only watch command
# that should be typed.
#
# 🔴 WHY A SLUG AND NOT A PATH. Two watch failures came from the CALL SITE, not
# the watcher: once a hand-typed remote path, once a buffering pipe. A slug is
# the one thing already known at launch; everything else is derived here, once.
#
# 🔴 AND WHY IT DOES NOT JUST WATCH. 2026-08-27: the watch fired correctly, the
# notification arrived, the results were read — and the INSTANCE SAT IDLE FOR
# 24 MINUTES because closing it down was a thing someone had to remember. A run
# is not done when the conclusion is written (§8b); it is done when the machine
# is idle-or-reassigned. So the end of the watch RUNS the end-of-run steps
# instead of reminding anyone to.
#
# Separation of concerns, deliberately:
#   ops/watchrig.sh   MECHANISM — poll, diff, mirror, detect the three endings.
#                     Has 16 tests. Do not put policy in it.
#   ops/watch.sh      POLICY — what to DO about each ending.
#
#   ops/watch.sh h3-ehratio-01
#   NO_FETCH=1 ops/watch.sh <slug>     # skip the automatic fetch
#
# ⚠️ DO NOT PIPE THIS into `tail`/`head`/anything buffering — you will see
# nothing until the run ends. Survivable (every line is mirrored to
# <slug>.watch.log) but the point of a watch is to watch.
set -uo pipefail
SLUG="${1:?usage: ops/watch.sh <slug>}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "$SLUG" in
  */*|*.log) echo "🔴 give a SLUG, not a path: ops/watch.sh h3-ehratio-01"; exit 2 ;;
esac

LOG="/opt/amip/repo/experiments/resonance/${SLUG}.log"

# 🔴 REPORT EVERY OTHER LIVE WATCH, HERE, AT ARMING TIME.
# 2026-09-06, user: "The monitors are multiplying. There are 4 now." Four runs
# went by, each arming a watch and a notification monitor, and nothing ever
# stopped the previous pair — so three were left tailing logs of finished runs
# and firing stale events. A watch exits on its own when the run appends EXIT=;
# whatever WRAPS it does not, and there was no place that said so.
# 🔑 The arming step is the only moment that can see the whole picture, so it
# prints it. Not an error — several watches are legitimate when several runs are
# live. Silent accumulation is the defect.
#
# ⚠️ TWO FALSE POSITIVES, both found by running it: `pgrep -f` matched THIS
# script (§7cf, third time) and it matched the harness shell whose command line
# merely CONTAINS the string. So: exclude the whole ancestry rather than just
# $$/$PPID, and require the last field to look like a slug — a wrapper's last
# field is a path, and a path has a slash.
# 🔴 REPORT EVERY OTHER LIVE WATCH, HERE, AT ARMING TIME.
# 2026-09-06, user: "The monitors are multiplying. There are 4 now." Four runs
# went by, each arming a watch and a notification monitor, and nothing ever
# stopped the previous pair — so three were left tailing logs of FINISHED runs
# and firing stale events. A watch exits on its own when the run appends EXIT=;
# whatever WRAPS it does not, and no place said so.
#
# 🔑 A PIDFILE REGISTRY, NOT `pgrep -f`. Four attempts to make a command-line
# match exclude only THIS invocation all failed, each on a different process:
# $$/$PPID missed the grandparent; an ancestry walk missed the child watch.sh
# spawns; process group missed that child too; and the last matched a SIBLING
# the wrapper pipeline created. Matching on command line means competing with
# every shell that happens to QUOTE the command — unwinnable. A pidfile says
# exactly who is watching what, with no inference at all.
_WDIR="$HERE/../.watchpids"
mkdir -p "$_WDIR" 2>/dev/null
_found=0
for _f in "$_WDIR"/*.pid; do
  [ -e "$_f" ] || continue
  _wpid="$(cat "$_f" 2>/dev/null)"
  _other="$(basename "$_f" .pid)"
  # ⚠️ SELF-CLEANING. A watch killed with SIGKILL leaves its file behind, and a
  # stale file reported as a live watch is exactly the noise this removes.
  # 🔴 A ZOMBIE PASSES `[ -d /proc/<pid> ]`. Found in real use, not in the tests:
  # a watch nohup'd from a shell that then exited was reaped by nobody, so it sat
  # as <defunct> with its /proc entry intact and was reported as a live watch on
  # a run that had finished an hour earlier — the exact false alarm this registry
  # exists to remove. /proc/<pid>/stat field 3 is the state; Z is dead.
  # ⚠️ field 2 is `comm` IN PARENTHESES and can contain spaces, so cut after the
  # closing paren rather than by field number.
  _st="$(sed 's/.*) //' "/proc/$_wpid/stat" 2>/dev/null | cut -d' ' -f1)"
  if [ -z "$_wpid" ] || [ -z "$_st" ] || [ "$_st" = "Z" ]; then
    rm -f "$_f"; continue
  fi
  [ "$_wpid" = "$$" ] && continue
  [ "$_found" -eq 0 ] && echo "  ⚠️  OTHER WATCHES ALREADY RUNNING:"
  _found=1
  _dup=""
  [ "$_other" = "$SLUG" ] && _dup="   🔴 SAME SLUG — about to watch it twice"
  printf "        pid %-8s %s%s\n" "$_wpid" "$_other" "$_dup"
done
if [ "$_found" -eq 1 ]; then
  echo "        Stop the ones whose runs have ended, and stop their monitors"
  echo "        too — the watch dies with its run, the monitor does not."
else
  echo "  ✅ no other watch running"
fi
# 🔴 CLAIM THE SLOT ONLY IF IT IS FREE, AND RELEASE IT ONLY IF IT IS STILL OURS.
# Found by the test, not by reading: watching a slug that ANOTHER live watch
# already held overwrote its pidfile and then, on exit, DELETED IT — so the
# duplicate check silently unregistered the very watch it had just warned about.
# The registry key is the slug, so two watches on one slug cannot both hold it;
# the first keeps it, and the second stays unregistered but still warns.
_HELD=0
if [ ! -e "$_WDIR/$SLUG.pid" ]; then
  echo $$ > "$_WDIR/$SLUG.pid"; _HELD=1
fi
# ⚠️ The poller trap further down CHAINS onto this rather than replacing it — an
# EXIT trap set later silently discards an earlier one, which is how the leaked
# poller this file already warns about came about.
trap '[ "$_HELD" = 1 ] && rm -f "$_WDIR/$SLUG.pid"' EXIT INT TERM

# 🔴 EVENTS=1 — FOR A NOTIFICATION HOST, NOT A HUMAN TERMINAL.
# 2026-09-05: a watch was hosted in a backgrounded shell and was KILLED AT THE
# HOST'S TIMEOUT (rc=124) four minutes into a ~5 h solve. The solve was fine —
# it is nohup'd on the instance — but nothing was watching it, and the exit
# looked like a watch that had ENDED rather than one that had DIED. A watch that
# outlives nothing is worse than no watch: it reports "done" when it means "I
# stopped looking".
# ✅ So this mode emits ONLY lines worth a notification, cheaply enough to run
# under a long-lived event host. The filter deliberately covers FAILURE as well
# as progress — a filter matching only good news is silent through a crash, and
# silence is indistinguishable from "still solving".
# ⚠️ --line-buffered / stdbuf -oL are what make the internal pipe legal here;
# the no-piping rule at the top is about BUFFERING callers, which is why a
# buffering pipe hid a live watch twice.
EV='🔴|⚠️|✅|EXIT=|--- ne=|RESUMED|beta|Q_ext|Q0|Traceback|Error|error|FAILED|Killed|OOM|rc=|finished|converged'

# 🔴 AND IT STARTS THE PROGRESS POLLER ITSELF. The rig log is silent for the
# whole of a long case, so watchrig alone gives an armed, correct, SILENT watch
# — see ops/solverprogress.sh. Starting it here rather than documenting it is
# the same rule as remote.sh exec'ing into the watch: if it must be remembered,
# it will eventually not be.
PROG_PID=""
if [ "${EVENTS:-0}" = "1" ] && [ "${NO_PROGRESS:-0}" != "1" ]; then
  "$HERE/solverprogress.sh" "$SLUG" "${PROGRESS_IV:-120}" &
  PROG_PID=$!
  # ⚠️ kill the poller on ANY exit, including the run finishing normally — a
  # leaked poller keeps ssh'ing at a dead host forever.
  trap '[ -n "$PROG_PID" ] && kill "$PROG_PID" 2>/dev/null; [ "$_HELD" = 1 ] && rm -f "$_WDIR/$SLUG.pid"' EXIT INT TERM
fi

# 🔴 AND IT NO LONGER ASKS TO BE RE-ARMED. rc=10 (a case turned over, run still
# going) used to PRINT "re-arm to watch the next one" — advice, at the exact
# moment the watch stopped. Same defect as ops/remote.sh printing the watch
# command: a step that must be remembered will eventually not be. Loop instead.
while :; do
  if [ "${EVENTS:-0}" = "1" ]; then
    "$HERE/watchrig.sh" "$LOG" 2>&1 | stdbuf -oL grep -E --line-buffered "$EV"
    # 🔑 PIPESTATUS, not $? — $? here is grep's, and grep exits 1 when it simply
    # matched nothing. Reading a status through a pipe is the single most
    # repeated mistake in this programme.
    RC=${PIPESTATUS[0]}
  else
    "$HERE/watchrig.sh" "$LOG"
    RC=$?
  fi
  [ "$RC" = "10" ] || break
  echo "  ⏸  case turned over — RE-ARMED automatically, run continues ($SLUG)"
done

echo
case "$RC" in
  0)
    echo "=============================================================="
    echo "  RUN FINISHED: $SLUG"
    # 🔑 FETCH IS PART OF THE RUN, NOT A FOLLOW-UP. §8b: h3_eigen and
    # h3_annular both exited 0, wrote complete results, and were never
    # fetched — three documents said H3 was NOT STARTED for a day.
    if [ "${NO_FETCH:-0}" = "1" ]; then
      echo "  ⚠️  fetch SKIPPED (NO_FETCH=1) — results are still only on the volume"
    else
      echo "  -- fetching results --"
      "$HERE/fetch.sh" 2>&1 | tail -3
    fi
    echo
    echo "  🔴 THE INSTANCE IS NOW IDLE AND STILL BILLING."
    "$HERE/status.sh" 2>&1 | sed -n '/== instance ==/,$p' | head -4
    echo
    echo "  Choose one, now — not later:"
    echo "    ops/go ops/remote.sh <rig.py> 32 <next-slug>   # keep it working"
    echo "    ops/go ops/shutdown.sh                         # sync, unmount, down"
    echo "  ⚠️  An idle instance costs the same as a solving one."
    echo "=============================================================="
    ;;
  2)
    echo "  🔴 HOST GONE — see the recovery steps above. Nothing to fetch:"
    echo "     the volume holds the completed cases, so remount and relaunch"
    echo "     the SAME slug rather than starting over."
    ;;
  10)
    # unreachable: the loop above re-arms on 10 and only breaks on a real ending.
    echo "  ⏸  case turnover escaped the re-arm loop — that is a BUG in watch.sh"
    ;;
  3)
    echo "  ⚠️  The run had ALREADY finished before this watch armed."
    echo "     Read the log, then fetch:  ops/go ops/fetch.sh"
    echo "     🔴 And check whether the instance has been idle since."
    ;;
esac
exit "$RC"
