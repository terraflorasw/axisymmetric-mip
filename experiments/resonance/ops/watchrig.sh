#!/usr/bin/env bash
# Watch a remote rig log: emit progress as it lands, and STOP for the right
# reasons. Three watcher shapes were shipped on 2026-08-25 without a test and
# each failed differently:
#
#   Monitor + `tail -f`     per-case events ✅  ends on job done ❌  host death ❌
#   bash `until grep EXIT=` per-case events ❌  ends on job done ✅  host death ❌
#   poll-and-diff (this)    ✅                  ✅                   ✅
#
# 🔑 Ask of any watch: what does it emit (a) per unit of progress, (b) when the
# JOB ends, (c) when the MACHINE ends? All three need an answer.
#
# 🔴 AND A FOURTH, ADDED 2026-08-27: (d) CAN THE CALLER SILENTLY DISCARD IT?
# This watcher was invoked twice in one session as `ops/watchrig.sh ... | tail`.
# `tail` buffers its whole input until EOF, so every per-case event it emitted
# sat in a pipe that would not flush until the watch EXITED — a job stepping
# through cases looked identical to a job doing nothing. The watcher was alive
# and correct; the CALL SITE destroyed it, and nothing in the watcher could
# tell. Same shape as every other entry here: the instrument was fine and the
# way it was used was not.
# ✅ THE FIX IS NOT "REMEMBER NOT TO PIPE IT". Everything it prints is MIRRORED
# to a local file, so progress survives whatever the caller does with stdout.
# Use `ops/watch.sh <slug>`, which cannot be given the wrong path either.
#
# Testable by design: the remote runner is injectable, so ops/watchrig_test.sh
# exercises host-death and blip-immunity WITHOUT needing a real instance.
#
#   ops/watchrig.sh <remote-log-path>
#   WATCH_SLEEP=5 WATCH_STRIKES=2 ops/watchrig.sh /path/to.log
set -uo pipefail

LOG="${1:?usage: watchrig.sh <remote-log-path>}"
SLEEP="${WATCH_SLEEP:-20}"
STRIKES="${WATCH_STRIKES:-3}"

# 🔴 MIRROR EVERYTHING TO DISK. See (d) above: a caller that buffers or drops
# stdout must not be able to make a live watch look like a dead one. This is
# the only reason progress is recoverable after a bad invocation.
# Set WATCH_MIRROR=/dev/null to opt out (the test harness does).
_HERE_M="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIRROR="${WATCH_MIRROR:-$_HERE_M/../$(basename "$LOG" .log).watch.log}"
if [ "$MIRROR" != /dev/null ]; then
  printf '=== watch armed %s on %s ===\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "$LOG" >> "$MIRROR"
fi
exec > >(tee -a "$MIRROR") 2>&1
# 🔴 THE PATTERN WAS TUNED FOR ONE RIG AND REUSED BLIND ON ANOTHER.
# 2026-08-27: watching h3_driven with h3_loopq's pattern matched NOTHING —
# h3_loopq prints "--- loop ... / pec: TE011 / -> Q0=", h3_driven prints
# "--- COLD ... / f0=... beta=...". The watch ran, the solver turned over
# cases, and it reported nothing. The user noticed; the watcher did not.
# ⚠️ Same shape as every other failure in this file: an instrument validated
# in one regime, reused in another without checking it still sees anything.
PAT="${WATCH_PAT:-^ *--- |pec: TE011|lumped: TE011|-> Q0=|^ *f0=|beta=|branch here|SKIPPED|RESUMING|REPORTED|REPORTED|Traceback|no modes|TIMED OUT|🔴|^EXIT=}"

# The remote runner takes ONE argument: the shell command to run remotely.
# Default is ssh; the test substitutes a local stub. Injectable so the failure
# paths are reachable without terminating a real machine.
if [ -z "${WATCH_RUNNER:-}" ]; then
  HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  # shellcheck disable=SC1091
  . "$HERE/env.sh"
  KEY="$HERE/../../../../aws.pem"
  WATCH_RUNNER="ssh -o ConnectTimeout=10 -o BatchMode=yes -i $KEY $AMIP_HOST"
fi

remote() { timeout 30 $WATCH_RUNNER "$1" 2>/dev/null; }

FAILS=0
# 🔴 THE JOB MAY HAVE ALREADY FINISHED. Starting from the CURRENT end of the
# log (to avoid replaying backlog) means an EXIT= that is ALREADY THERE sits in
# the skipped region and the watch waits forever. Observed 2026-08-25: three
# runs failed in seconds, the watch armed afterwards, and it reported nothing
# at all until the user asked. A watch must not assume the job starts after it.
if remote "grep -q '^EXIT=' '$LOG' 2>/dev/null"; then
  echo "⚠️  the log ALREADY contains EXIT= — this run finished BEFORE the watch"
  echo "    armed. Nothing to stream; read the log directly."
  remote "grep -m1 '^EXIT=' '$LOG' 2>/dev/null"
  exit 3
fi
# 🔑 DOES THE PATTERN MATCH THIS LOG AT ALL? A watcher that can see nothing
# is indistinguishable from a quiet job. Check once, loudly, at startup.
_seen=$(remote "grep -cE \"$PAT\" '$LOG' 2>/dev/null || echo 0" | tr -dc '0-9')
if [ "${_seen:-0}" = "0" ]; then
  echo "⚠️  the filter matches NOTHING in $LOG so far — this watch may be blind."
  echo "    Check WATCH_PAT against the rig's actual output format."
fi
LAST=$(remote "wc -l < '$LOG' 2>/dev/null || echo 0" | tr -dc '0-9')
[ -z "$LAST" ] && LAST=0

# 🔑 POLL SLOWLY WHEN HEALTHY, CONFIRM FAST WHEN NOT.
# The 2026-08-25 miss was pure LATENCY: 4 strikes x 45 s meant ~4 minutes to
# call a reclamation, and the user saw the instance die at :49 and prompted at
# :52 — before the watcher spoke. Sleeping the FULL interval between failures
# is wasted patience: once a poll fails, the only question is blip-or-dead, and
# that is answered by retrying SOON, not by waiting.
RETRY="${WATCH_RETRY:-3}"
# What counts as "a case turned over": any per-SOLVE verdict this rig family
# prints. Deliberately includes the failures — a case that times out or finds no
# modes has also turned over, and that is exactly when you want to be told.
STOP_RE="${WATCH_STOP_RE-(pec|lumped): TE011|(pec|lumped): no modes|-> Q0=|TIMED OUT|DID NOT CONVERGE}"
while true; do
  if [ "$FAILS" -eq 0 ]; then sleep "$SLEEP"; else sleep "$RETRY"; fi
  if RESP=$(remote "wc -l < '$LOG' 2>/dev/null || echo 0; awk 'NR>$LAST' '$LOG' 2>/dev/null"); then
    FAILS=0
    TOT=$(printf '%s\n' "$RESP" | head -1 | tr -dc '0-9')
    BODY=$(printf '%s\n' "$RESP" | tail -n +2)
    [ -n "$TOT" ] && LAST="$TOT"
    if [ -n "$BODY" ]; then
      printf '%s\n' "$BODY" | grep -E "$PAT" || true
      if printf '%s\n' "$BODY" | grep -q '^EXIT='; then
        echo "✅ run finished"
        exit 0
      fi
      # 🔴 EXIT AT A CASE BOUNDARY SO SOMETHING ACTUALLY GETS TOLD.
      # The mirror and the three endings were never the whole problem. The
      # harness that runs this re-invokes its caller when the COMMAND EXITS,
      # not when it prints — so a watch that streams per-case events and keeps
      # running notifies NOBODY until the whole job ends. Reported twice by the
      # user ("a step finished but the monitor is missing", "it just turned
      # over and again, the monitor didn't fire"), and both times I fixed a
      # different part of the watch.
      # 🔑 So: stop at each boundary and let the caller re-arm. Exit 10 means
      # "more to come", distinct from 0 (job done), 2 (host gone), 3 (already
      # finished). Set WATCH_STOP_RE= to disable and stream to the end.
      if [ -n "${STOP_RE:-}" ] \
         && printf '%s\n' "$BODY" | grep -qE "$STOP_RE"; then
        echo "⏸  case boundary — RE-ARM to continue watching"
        exit 10
      fi
    fi
  else
    FAILS=$((FAILS + 1))
    # One failure is a network blip. N in a row is the machine being gone.
    if [ "$FAILS" -ge "$STRIKES" ]; then
      # ⚠️ DO NOT CLAIM THE CAUSE. Unreachable is unreachable: a spot
      # reclamation, a crash, an OOM kill and a manual stop look identical
      # from here. ops/spotwatch.sh records the actual notice on the VOLUME.
      echo "🔴 HOST UNREACHABLE ${FAILS}x. Cause UNKNOWN from here — check"
      echo "   /opt/amip/spot-interruptions.log after remounting to tell a"
      echo "   reclamation from a crash. The volume holds"
      echo "   the completed cases. Set the new address in ops/env.sh, then"
      echo "   NOSYNC=1 ops/go ops/mount.sh, then relaunch the SAME slug —"
      echo "   resume skips whatever already finished."
      exit 2
    fi
  fi
done
