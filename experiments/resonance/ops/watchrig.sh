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
# Testable by design: the remote runner is injectable, so ops/watchrig_test.sh
# exercises host-death and blip-immunity WITHOUT needing a real instance.
#
#   ops/watchrig.sh <remote-log-path>
#   WATCH_SLEEP=5 WATCH_STRIKES=2 ops/watchrig.sh /path/to.log
set -uo pipefail

LOG="${1:?usage: watchrig.sh <remote-log-path>}"
SLEEP="${WATCH_SLEEP:-20}"
STRIKES="${WATCH_STRIKES:-3}"
PAT="${WATCH_PAT:-^  --- loop|^--- |pec: TE011|lumped: TE011|-> Q0=|SKIPPED|RESUMING|REPORTED|Traceback|^EXIT=}"

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
LAST=$(remote "wc -l < '$LOG' 2>/dev/null || echo 0" | tr -dc '0-9')
[ -z "$LAST" ] && LAST=0

# 🔑 POLL SLOWLY WHEN HEALTHY, CONFIRM FAST WHEN NOT.
# The 2026-08-25 miss was pure LATENCY: 4 strikes x 45 s meant ~4 minutes to
# call a reclamation, and the user saw the instance die at :49 and prompted at
# :52 — before the watcher spoke. Sleeping the FULL interval between failures
# is wasted patience: once a poll fails, the only question is blip-or-dead, and
# that is answered by retrying SOON, not by waiting.
RETRY="${WATCH_RETRY:-3}"
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
