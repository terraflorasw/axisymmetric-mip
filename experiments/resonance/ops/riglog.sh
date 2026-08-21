#!/usr/bin/env bash
# Tail a RIG's own log (not Palace's) on the instance. Read-only.
#   ops/go ops/riglog.sh e0k2_anchor [lines]
#
# 🔴 ops/getlog.sh looks for a '^A: '..'^B: ' block that only the e1 rigs ever
# emitted, so it returns SILENTLY EMPTY for every other rig — which is
# indistinguishable from a rig that has produced nothing, and a waiter built on
# it never fires. CONVENTIONS §1: ask the direct question.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
T="${1:?usage: ops/riglog.sh <rig-tag> [lines]}"
N="${2:-30}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H \
  "cd /opt/amip/repo/experiments/resonance || exit 9
   f=${T}.log
   if [ ! -f \"\$f\" ]; then echo \"  🔴 no \$f — has the rig started?\"; exit 1; fi
   echo \"  \$(wc -l < \"\$f\") lines, last modified \$(date -u -r \"\$f\" +%H:%M:%SZ)\"
   # is the rig still alive? ask directly, do not infer from the log
   n=\$(ps -C python3 -o args= 2>/dev/null | grep -c \"${T}\") || true
   echo \"  rig process: \${n:-0}\"
   tail -n $N \"\$f\""
