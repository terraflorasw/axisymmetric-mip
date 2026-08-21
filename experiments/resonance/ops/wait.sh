#!/usr/bin/env bash
# Block until a remote rig finishes, then print its tail. Read-only.
#   ops/go ops/wait.sh e1b_drive [max_minutes]
#
# 🔴 The first version inferred death from "no palace ranks + log not growing".
# That is precisely what a long gmsh mesh looks like — it declared a healthy
# e1b_loaded dead while geometry.py was 3 minutes into meshing e1b_A.msh.
# Liveness is not a heuristic: ask whether the RIG PROCESS is still there.
# Alive = the rig's own python3 is running, or palace ranks are. Nothing else.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
TAG="${1:?usage: ops/wait.sh <tag> [max_minutes]}"
MAX="${2:-120}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
deadline=$(( $(date +%s) + MAX*60 ))

probe() {
  # prints "<rig_alive> <palace_ranks> <exit_lines> <log_bytes>"
  timeout 40 ssh -i "$K" -o ConnectTimeout=15 $H "
    cd $R 2>/dev/null || { echo '0 0 0 0'; exit 0; }
    # -C python3 matches by executable name, never by command line, so this
    # can never match the ssh invocation that is asking the question.
    rig=\$(ps -C python3 -o args= 2>/dev/null | grep -c '$TAG.py')
    n=\$(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -c -v Z)
    e=\$(grep -c '^EXIT=' $TAG.log 2>/dev/null)
    s=\$(stat -c %s $TAG.log 2>/dev/null)
    echo \"\${rig:-0} \${n:-0} \${e:-0} \${s:-0}\"
  " 2>/dev/null | tail -1
}

last=""
while :; do
  set -- $(probe)
  rig=${1:-0}; ranks=${2:-0}; done_=${3:-0}; bytes=${4:-0}
  if [ "$done_" != "0" ]; then
    echo "== $TAG finished =="
    timeout 40 ssh -i "$K" $H "tail -45 $R/$TAG.log" 2>&1
    exit 0
  fi
  if [ "$rig" = "0" ] && [ "$ranks" = "0" ]; then
    echo "🔴 $TAG: rig process gone, no EXIT line, log ${bytes}B — died"
    timeout 40 ssh -i "$K" $H "tail -30 $R/$TAG.log" 2>&1
    exit 1
  fi
  now=$(printf 'rig=%s ranks=%s log=%sB' "$rig" "$ranks" "$bytes")
  [ "$now" = "$last" ] || { echo "  $now"; last="$now"; }
  [ "$(date +%s)" -lt "$deadline" ] || { echo "🔴 $TAG: past ${MAX}min"; exit 2; }
  sleep 60
done
