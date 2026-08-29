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

"$HERE/watchrig.sh" "/opt/amip/repo/experiments/resonance/${SLUG}.log"
RC=$?

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
    echo "  ⏸  A CASE TURNED OVER — the run is still going."
    echo "     Re-arm to watch the next one:  ops/watch.sh $SLUG"
    echo "     (full history: $SLUG.watch.log)"
    ;;
  3)
    echo "  ⚠️  The run had ALREADY finished before this watch armed."
    echo "     Read the log, then fetch:  ops/go ops/fetch.sh"
    echo "     🔴 And check whether the instance has been idle since."
    ;;
esac
exit "$RC"
