#!/usr/bin/env bash
# Kill ORPHANED palace ranks on the instance (PPID==1), via reap.py.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 90 ssh -i "$K" $H \
  'cd /opt/amip/repo/experiments/resonance && source /opt/amip/env.sh
   echo "  before:"; ps -o pid=,ppid=,etime=,args= -C palace-x86_64.bin 2>/dev/null | sed "s/^/    /"
   python3 -u reap.py "$@"
   echo "  after:"; ps -o pid=,ppid=,etime= -C palace-x86_64.bin 2>/dev/null | sed "s/^/    /" || echo "    none"
   uptime | sed "s/^/  /"' -- "$@"
