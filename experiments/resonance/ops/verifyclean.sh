#!/usr/bin/env bash
# Is the instance running the code we think it is? Read-only.
#   ops/go ops/verifyclean.sh
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
timeout 60 ssh -i "$K" -o ConnectTimeout=15 $H "
  cd $R || exit 9
  echo '  geometry.py on instance:'
  sha256sum geometry.py | awk '{print \"    sha \" substr(\$1,1,16)}'
  stat -c '    mtime %y' geometry.py
  if grep -q 'def cache_key' geometry.py; then
    echo '    contains: MESH CACHE'
  else
    echo '    contains: no cache (pre-cache version)'
  fi
"
echo "  geometry.py local:"
sha256sum geometry.py | awk '{print "    sha " substr($1,1,16)}'
grep -q 'def cache_key' geometry.py && echo "    contains: MESH CACHE" || echo "    contains: no cache"
