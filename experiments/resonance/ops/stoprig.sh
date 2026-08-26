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
  # 🔴 AND ITS MESHER. Killing the rig ORPHANS a running geometry.py: gmsh is a
  # child process, not part of the palace tree, so the loop below never saw it.
  # Found 2026-08-25 — a stopped rig left geometry.py meshing for minutes, and
  # the next launch was refused by ops/go's BUSY guard with no obvious cause.
  # A rig spends a large fraction of its life meshing (ops/go says so in terms),
  # so this is the MOST likely thing to be running when you stop one.
  for g in \$(ps -C python3 -o pid=,args= | grep -- 'geometry\.py' | awk '{print \$1}'); do
    echo \"  killing mesher \$g\"; kill -TERM \$g 2>/dev/null || true
  done
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
