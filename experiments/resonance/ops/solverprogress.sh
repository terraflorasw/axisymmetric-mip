#!/usr/bin/env bash
# SANCTIONED WATCHER — emit PROM/solver progress from inside a running case.
#
# 🔴 WHY THIS EXISTS. 2026-09-05: the watch was armed, correct, and silent for an
# hour, because `watchrig.sh` mirrors the RIG log and the rig prints per CASE —
# one line at the start, one at the end. A 5-hour driven solve is therefore a
# 5-hour silence, and silence is indistinguishable from a hang (§7cc). The USER
# supplied the progress signal instead ("1h again, 80GB steady"), which is the
# monitoring criterion *polls for progress* failing in the field.
#
# ✅ Palace's own log IS live. The adaptive PROM prints a greedy iteration with a
# sample count and an ERROR INDICATOR, which is the one number that says whether
# the case is converging or grinding — and it is comparable against AdaptiveTol.
#
# ⚠️ EMITS ONLY ON CHANGE. A poller that reprints its last line every interval is
# a flood, and a flood gets a watcher muted, which is how watching stops.
# ⚠️ ssh failures are NOT fatal here — a transient network error must not kill a
# progress poller. Host loss is watchrig's job to declare, not this one's.
#
#   ops/solverprogress.sh <slug> [interval_s]
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
SLUG="${1:?usage: ops/solverprogress.sh <slug> [interval_s]}"
IV="${2:-120}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
R=/opt/amip/repo/experiments/resonance
LAST=""
while :; do
  NOW=$(timeout 45 ssh -i "$K" -o BatchMode=yes -o ConnectTimeout=15 "$AMIP_HOST" \
    "cd $R 2>/dev/null || exit 9
     L=\$(ls -t ${SLUG}.*_p.log 2>/dev/null | head -1); [ -z \"\$L\" ] && exit 8
     G=\$(grep -aE 'Greedy iteration|^It [0-9]+/[0-9]+' \"\$L\" | tail -1)
     M=\$(free -g | sed -n 2p | awk '{print \$3\"/\"\$2\" GB\"}')
     E=\$(ps -C palace-x86_64.b -o etime= 2>/dev/null | head -1 | tr -d ' ')
     echo \"  ⏳ \$G | mem \$M | palace \$E\"" 2>/dev/null)
  # 🔴 DEDUP ON THE GREEDY LINE ONLY. First version compared the WHOLE string —
  # but it carries memory and elapsed time, which change every single poll, so
  # "emit only on change" emitted on every poll. Caught by smoke-testing the
  # thing rather than reading it: two identical iterations 22 s apart.
  KEY="${NOW%%| mem *}"
  # 🔴 `It n/1751` ADVANCES EVERY POLL BY DESIGN, so the greedy-line key
  # re-floods on the PROM evaluation phase — the very phase this was extended to
  # cover. Bucket it: report roughly every 100th point, so a 1751-point sweep is
  # ~17 events instead of one per poll. Parked note in NEXT.md predicted exactly
  # this; the fix is coarser granularity, NOT dropping the phase again.
  case "$KEY" in
    *"It "[0-9]*) N=$(printf '%s' "$KEY" | sed -n 's/.*It \([0-9]*\)\/.*/\1/p')
                  [ -n "$N" ] && KEY="It-bucket-$((N / 100))" ;;
  esac
  # exit 9/8 or a network blip -> empty. Say nothing; do not guess a cause.
  if [ -n "$NOW" ]; then
    NOWS=$(date -u +%s)
    if [ "$KEY" != "$LAST" ]; then
      echo "$NOW"; LAST="$KEY"; LASTEMIT=$NOWS
    elif [ $((NOWS - ${LASTEMIT:-0})) -ge "${HEARTBEAT_S:-1800}" ]; then
      # ⚠️ A HEARTBEAT, NOT NOISE. Without it a stalled greedy iteration is
      # SILENT, and §7cc is precisely that silence and progress look identical.
      echo "$NOW  (heartbeat — same iteration)"; LASTEMIT=$NOWS
    fi
  fi
  sleep "$IV"
done
