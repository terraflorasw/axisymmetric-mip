#!/usr/bin/env bash
# Solver order in the INPUT configs on the instance. Read-only.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H \
  'cd /opt/amip/repo/experiments/resonance || exit 9
   for f in e1b_*.json e0k_*.json; do
     [ -f "$f" ] || continue
     case "$f" in *result*|*manifest*) continue;; esac
     o=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get(\"Solver\",{}).get(\"Order\"))" "$f" 2>/dev/null)
     t=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get(\"Problem\",{}).get(\"Type\"))" "$f" 2>/dev/null)
     printf "  %-22s Order=%s  Type=%s\n" "$f" "$o" "$t"
   done'
