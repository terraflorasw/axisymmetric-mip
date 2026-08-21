#!/usr/bin/env bash
# Show a file on the instance, whole or tailed. Read-only.
#   ops/go ops/rcat.sh e0k2_eig_p.log          # whole file
#   ops/go ops/rcat.sh e0k2_eig_p.log 40       # last 40 lines
#
# 🔴 Exists because getlog/grep/solverlog each assume a filename convention or
# a log format, and when the assumption misses they return SILENTLY EMPTY —
# which reads as "the file has nothing in it" rather than "I looked in the
# wrong place". This one takes the literal filename and says when it is absent.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
F="${1:?usage: ops/rcat.sh <filename> [tail-lines]}"
N="${2:-0}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H \
  "cd /opt/amip/repo/experiments/resonance || exit 9
   if [ ! -f '$F' ]; then
     echo \"  🔴 no such file: \$PWD/$F\"
     echo '  nearby:'; ls -1 | grep -F \"\$(echo '$F' | cut -d. -f1)\" | head -10
     exit 1
   fi
   echo \"  \$(wc -c < '$F') bytes, \$(wc -l < '$F') lines\"
   if [ '$N' -gt 0 ]; then tail -n '$N' '$F'; else cat '$F'; fi"
