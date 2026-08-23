#!/usr/bin/env bash
# Run a rig on the instance: sync, lint there, launch detached, report.
#   ops/go ops/remote.sh e1b_drive.py [RANKS]
# instance address: ops/env.sh, overridable with $AMIP_HOST — SOURCED HERE,
# like every sibling script. This one relied on inheriting the variable and
# died with "unbound variable" the first time it was run standalone.
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -euo pipefail
RIG="${1:?usage: ops/remote.sh <rig.py> [ranks]}"
RANKS="${2:-4}"
# repo parent (holds aws.pem), derived from THIS script's location
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
TAG="${RIG%.py}"

echo "== sync =="
( cd ../../.. && bash rsync.sh ) | tail -2

echo "== refuse if anything is already running =="
BUSY=$(timeout 30 ssh -i "$K" $H \
  'ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l')
[ "$BUSY" = "0" ] || { echo "🔴 $BUSY rank(s) already running — refusing to collide"; exit 1; }

echo "== lint on the instance =="
# 🔴 THE LINT MUST SOURCE env.sh, BECAUSE THE LAUNCH DOES. Without it the gate
# ran /usr/bin/python3 while the rig runs /opt/amip/envs/emsim/bin/python3 —
# TWO DIFFERENT INTERPRETERS, different versions (3.12 in the env) and different
# installed packages. So preflight was certifying an environment the rig never
# executes in, which is CONVENTIONS §7: a checker that cannot see its subject.
# It is also how "pyflakes not installed" survived a root-level apt install —
# the fix landed in the interpreter nobody runs.
timeout 60 ssh -i "$K" $H "cd $R && source /opt/amip/env.sh && python3 preflight.py $RIG"

echo "== launch (detached, journalled) =="
timeout 60 ssh -i "$K" $H \
  "cd $R && nohup bash -c 'source /opt/amip/env.sh && PALACE_RANKS=$RANKS RUN=$TAG python3 -u $RIG > $TAG.log 2>&1; echo EXIT=\$? >> $TAG.log' >/dev/null 2>&1 & sleep 3; echo '  launched $RIG at $RANKS ranks'"
echo "  watch:  ops/go ops/status.sh"
echo "  fetch:  ops/go ops/fetch.sh"
