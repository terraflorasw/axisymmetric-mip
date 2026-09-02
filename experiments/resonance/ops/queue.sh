#!/usr/bin/env bash
# Run several rigs BACK TO BACK on the instance, unattended.
#
# 🔴 WHY THIS EXISTS. 2026-08-28: the instance stayed up from ~01:00 to 13:20
# with NOTHING RUNNING, because `ops/remote.sh` launches one rig and returns and
# nobody was awake to launch the next. A night of solve time was lost to the
# absence of a queue, not to any failure. User: *"Wish we'd queued that last
# night."*
#
#   ops/go ops/queue.sh h3_loopq.py:h3-loopcu-ld8-01 h3_loopq.py:h3-aspect-01
#   DRYRUN=1 ops/queue.sh <entries>     # validate and print, launch nothing
#
# Each entry is RIG.py:SLUG. They run in order, one at a time. A rig that fails
# does NOT stop the queue — a failed case is MISSING DATA (§3), and the next
# question should still get its turn.
#
# 🔴 THE LOOP READS QUEUE.list ON FD 3 AND GIVES EACH RIG </dev/null.
# First version used `while read ... done < QUEUE.list` with the rig inheriting
# the loop's stdin. The rig (or mpirun beneath it) CONSUMED THE REST OF THE
# LIST: 5 entries were validated, entry 1 ran, and the log said "QUEUE DONE" —
# which reads as success. A truncated batch that announces completion is worse
# than one that crashes. It now also counts what it ran and says so.
#
# 🔴 QUEUE.log AND QUEUE.list ARE GITIGNORED, DELIBERATELY. They are remote
# run-state living inside a tree that `rsync.sh` pushes wholesale. `fetch.sh`
# pulls `*.log`, so QUEUE.log came down to the working copy, and every later
# sync pushed that stale copy back over the RUNNING queue's record. Ignoring
# them keeps rsync's hands off. Do not "fix" this by fetching them.
#
# 🔑 EVERY SLUG KEEPS ITS OWN LOG, so `ops/watch.sh <slug>` works unchanged, per
# entry, exactly as for a single launch. The queue itself also logs to
# QUEUE.log so you can see where it got to overnight.
# ⚠️ A reclamation still ends the batch — the host is what disappears. Rigs with
# resume (h3_loopq) lose only the case in flight; relaunch the same slugs and
# the finished ones are skipped.
set -uo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
R=/opt/amip/repo/experiments/resonance
[ $# -ge 1 ] || { echo "usage: ops/queue.sh RIG.py:SLUG [RIG.py:SLUG ...]"; exit 2; }

# ---- validate EVERY entry before launching ANY of them ---------------------
# 🔴 Fail the whole batch on a bad entry rather than discovering it at 4am after
# the good ones have run. A missing config is the common case: slug.config()
# REFUSES rather than inventing defaults, so the rig would die instantly.
ENTRIES=()
for e in "$@"; do
  rig="${e%%:*}"; sl="${e##*:}"
  if [ "$rig" = "$e" ] || [ -z "$sl" ]; then
    echo "🔴 malformed entry '$e' — want RIG.py:SLUG"; exit 2; fi
  [ -f "$HERE/../$rig" ] || { echo "🔴 no such rig: $rig"; exit 2; }
  [ -f "$HERE/../baseline-$sl.json" ] || {
    echo "🔴 no config baseline-$sl.json — the config IS the characterisation."
    echo "   Write it first (python3 slug.py --new $sl, then fill it in)."; exit 2; }
  ENTRIES+=("$rig:$sl")
  echo "  ✅ $rig  --slug $sl"
done
echo "  $# entr(ies) validated"
if [ "${DRYRUN:-0}" = "1" ]; then echo "  DRYRUN=1 — nothing launched"; exit 0; fi

# ---- one sync, one spot check, then hand off to the instance ---------------
echo "== sync =="
( cd "$ROOT" && bash rsync.sh ) | tail -2

echo "== refuse if this instance is already condemned =="
_CODE=$(timeout 20 ssh -i "$K" -o ConnectTimeout=10 $H '
  T=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
      -H "X-aws-ec2-metadata-token-ttl-seconds: 60" --max-time 3 2>/dev/null)
  curl -s -o /dev/null -w "%{http_code}" --max-time 3 \
      -H "X-aws-ec2-metadata-token: ${T:-}" \
      "http://169.254.169.254/latest/meta-data/spot/instance-action" 2>/dev/null' \
  2>/dev/null)
[ "$_CODE" = "200" ] && { echo "  🔴 spot notice pending — refusing"; exit 4; }
echo "  no pending notice (IMDS ${_CODE:-?})"

echo "== refuse if anything is already running =="
_BUSY=$(timeout 20 ssh -i "$K" -o ConnectTimeout=10 $H \
  'ps -o args= -C python3 2>/dev/null | grep -c "^python3 -u [a-z]" || true')
[ "${_BUSY:-0}" -gt 0 ] && { echo "  🔴 $_BUSY rig(s) already running"; exit 5; }

printf '%s\n' "${ENTRIES[@]}" > /tmp/.amipqueue.$$
scp -q -i "$K" /tmp/.amipqueue.$$ "$H:$R/QUEUE.list" && rm -f /tmp/.amipqueue.$$

echo "== launch the batch (detached) =="
timeout 60 ssh -i "$K" $H "cd $R && nohup setsid bash -c '
  source /opt/amip/env.sh
  echo \"QUEUE START \$(date -u +%Y-%m-%dT%H:%M:%SZ) \$(wc -l < QUEUE.list) entries\" >> QUEUE.log
  n=0
  while IFS=: read -r rig sl <&3; do
    [ -n \"\$rig\" ] || continue
    n=\$((n+1))
    echo \"BEGIN  \$(date -u +%H:%M:%SZ)  \$rig --slug \$sl\" >> QUEUE.log
    PALACE_RANKS=32 RUN=\$sl python3 -u \$rig --slug \$sl > \$sl.log 2>&1 < /dev/null
    rc=\$?
    echo \"EXIT=\$rc\" >> \$sl.log
    echo \"END    \$(date -u +%H:%M:%SZ)  \$sl rc=\$rc\" >> QUEUE.log
  done 3< QUEUE.list
  want=\$(grep -c . QUEUE.list)
  if [ \"\$n\" -ne \"\$want\" ]; then
    echo \"QUEUE TRUNCATED: ran \$n of \$want entries\" >> QUEUE.log
  fi
  echo \"QUEUE DONE \$(date -u +%Y-%m-%dT%H:%M:%SZ) ran \$n/\$want\" >> QUEUE.log
' >/dev/null 2>&1 & sleep 3; echo '  batch launched'"
echo "  watch each:  ops/watch.sh <slug>"
echo "  queue state: ops/rcat.sh QUEUE.log   (or ssh + tail)"
