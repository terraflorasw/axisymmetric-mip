#!/usr/bin/env bash
# Stop solves safely. NEVER pkill -f: it matches the calling shell's own argv.
# Selects by exact executable name and kills by PID, one at a time.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
WHERE=${1:-local}
# repo parent (holds aws.pem), derived from THIS script's location
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
kill_local() {
  mapfile -t P < <(ps -o pid=,stat= -C palace-x86_64.bin 2>/dev/null \
                   | awk '$2 !~ /Z/ {print $1}')
  [ ${#P[@]} -gt 0 ] || { echo "  nothing to stop"; return; }
  echo "  stopping ${#P[@]} rank(s): ${P[*]}"
  for p in "${P[@]}"; do kill -TERM "$p" 2>/dev/null || true; done
  sleep 3
  echo "  remaining: $(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l)"
}
case "$WHERE" in
  local)  kill_local ;;
  remote) timeout 30 ssh -i "$K" $H \
            'for p in $(ps -o pid=,stat= -C palace-x86_64.bin 2>/dev/null | awk "\$2 !~ /Z/ {print \$1}"); do kill -TERM $p; done; sleep 3; echo "  remaining: $(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l)"' ;;
  # Stop the RIG as well as its ranks. Killing only the ranks makes run() see a
  # failed solve, which a multi-rig runner records and then MARCHES ON to the
  # next rig — the opposite of stopping. Parent first, so it cannot launch
  # another child while we are killing this one.
  # ps -C matches the EXECUTABLE name; the arg match only filters that list, so
  # this can never select the calling shell the way pkill -f did (three times).
  rigs)  timeout 60 ssh -i "$K" $H \
            'kill_by() {
               for p in $(ps -C python3 -o pid=,args= 2>/dev/null | grep -- "$1" | awk "{print \$1}"); do
                 echo "  killing $p ($1)"; kill -TERM "$p" 2>/dev/null || true
               done
             }
             kill_by e0v_reverify.py
             sleep 2
             kill_by "e0.*\.py"
             sleep 2
             for p in $(ps -o pid=,stat= -C palace-x86_64.bin 2>/dev/null | awk "\$2 !~ /Z/ {print \$1}"); do kill -TERM $p; done
             sleep 3
             echo "  rigs left:  $(ps -C python3 -o args= 2>/dev/null | grep -c "e0.*\.py" || true)"
             echo "  ranks left: $(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l)"' ;;
  *) echo "usage: ops/stop.sh [local|remote|rigs]"; exit 2 ;;
esac
