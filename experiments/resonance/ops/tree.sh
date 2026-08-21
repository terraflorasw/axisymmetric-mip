#!/usr/bin/env bash
# What is the ancestry of the running palace ranks? Read-only.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H '
  for p in $(ps -o pid= -C palace-x86_64.bin 2>/dev/null | head -1); do
    echo "  walking up from palace rank $p:"
    cur=$p
    for i in 1 2 3 4 5 6; do
      read -r ppid comm args <<<"$(ps -o ppid=,comm=,args= -p $cur 2>/dev/null)"
      [ -n "${ppid:-}" ] || break
      echo "    pid $cur  ppid $ppid  $comm  ${args:0:60}"
      [ "$ppid" = "1" ] && { echo "    ^ this ones parent is init = ORPHANED"; break; }
      cur=$ppid
    done
  done'
