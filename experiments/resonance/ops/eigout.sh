#!/usr/bin/env bash
# What did a solve actually produce? Read-only.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
T="${1:?tag}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H "
  cd /opt/amip/repo/experiments/resonance || exit 9
  echo '  --- postpro/$T ---'
  ls -la postpro/$T/ 2>/dev/null | awk '{print \"   \",\$5,\$9}' || echo '    (none)'
  echo '  --- eig.csv ---'
  head -4 postpro/$T/eig.csv 2>/dev/null | sed 's/^/    /' || echo '    (none)'
  echo '  --- solver log tail ---'
  tail -14 ${T}_p.log 2>/dev/null | sed 's/^/    /'
"
