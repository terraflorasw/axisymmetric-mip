#!/usr/bin/env bash
# Tail a Palace solver log on the instance. Read-only.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
T="${1:?tag}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H \
  "cd /opt/amip/repo/experiments/resonance || exit 9
   ls -la ${T}_p.log 2>/dev/null | awk '{print \"  \",\$5,\"bytes  \",\$6,\$7,\$8}'
   echo '  --- tail ---'
   tail -12 ${T}_p.log 2>/dev/null | sed 's/^/    /'"
