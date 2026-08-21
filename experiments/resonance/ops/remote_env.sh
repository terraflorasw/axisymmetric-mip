#!/usr/bin/env bash
# Launch a rig on the instance with extra environment. Detached, journalled.
#   ops/go ops/remote_env.sh <rig.py> <ranks> KEY=VAL [KEY=VAL...]
set -euo pipefail
RIG="${1:?usage: ops/remote_env.sh <rig.py> <ranks> [KEY=VAL...]}"; shift
RANKS="${1:-4}"; shift || true
EXTRA="$*"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
TAG="${RIG%.py}"

echo "== sync =="
( cd ../../.. && bash rsync.sh ) | tail -1

BUSY=$(timeout 30 ssh -i "$K" $H \
  'ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l')
[ "$BUSY" = "0" ] || { echo "🔴 $BUSY rank(s) running — refusing to collide"; exit 1; }

timeout 60 ssh -i "$K" $H "cd $R && python3 preflight.py $RIG"
timeout 60 ssh -i "$K" $H \
  "cd $R && nohup bash -c 'source /opt/amip/env.sh && PALACE_RANKS=$RANKS RUN=$TAG $EXTRA python3 -u $RIG > $TAG.log 2>&1; echo EXIT=\$? >> $TAG.log' >/dev/null 2>&1 & sleep 3; echo '  launched $RIG, ranks=$RANKS, env: $EXTRA'"
