#!/usr/bin/env bash
# Stop a named rig AND its whole palace tree. By PID, never pkill -f.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
R="${1:?usage: ops/stoprig.sh <rig.py>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 90 ssh -i "$K" $H "
  for p in \$(ps -C python3 -o pid=,args= | grep -- '$R' | awk '{print \$1}'); do
    echo \"  killing rig \$p\"; kill -TERM \$p 2>/dev/null || true
  done
  sleep 2
  # the wrapper is orphaned by that kill; take its whole group
  for r in \$(ps -eo pid=,ppid=,comm= | awk '\$2==1 && (\$3==\"palace\" || \$3==\"prterun\") {print \$1}'); do
    for p in \$(ps -eo pid=,ppid= | awk -v P=\$r '\$2==P {print \$1}'); do
      for q in \$(ps -eo pid=,ppid= | awk -v P=\$p '\$2==P {print \$1}'); do kill -TERM \$q 2>/dev/null; done
      kill -TERM \$p 2>/dev/null
    done
    kill -TERM \$r 2>/dev/null; echo \"  killed launcher tree \$r\"
  done
  sleep 3
  echo -n '  palace ranks left: '; ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -vc Z || echo 0
  echo -n '  rigs left: '; ps -C python3 -o args= 2>/dev/null | grep -c '$R' || echo 0
"
