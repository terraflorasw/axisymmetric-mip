#!/usr/bin/env bash
# Element counts of the meshes a run has built. Read-only.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
P="${1:?prefix}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H \
  "cd /opt/amip/repo/experiments/resonance || exit 9
   for f in ${P}*.meta.json; do
     [ -f \"\$f\" ] || continue
     python3 -c \"
import json,sys
d=json.load(open(sys.argv[1]))
g=d.get('geometry_mm',{})
print('  %-28s %8d tets  groove=%s  hmin=%.2f' % (
    sys.argv[1], d.get('tets',0), g.get('groove'),
    d.get('sizing_mm',{}).get('min',0)))\" \"\$f\"
   done"
