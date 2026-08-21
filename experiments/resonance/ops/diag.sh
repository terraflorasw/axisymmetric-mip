#!/usr/bin/env bash
# Why did a rig stop? Distinguishes "still meshing" from "actually dead".
#   ops/go ops/diag.sh e1b_drive
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
TAG="${1:?usage: ops/diag.sh <tag>}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
timeout 60 ssh -i "$K" -o ConnectTimeout=15 $H "
  cd $R || exit 9
  echo '== python rigs alive =='
  ps -o pid=,etime=,args= -C python3 2>/dev/null | sed 's/^/  /' || echo '  none'
  echo '== gmsh alive =='
  pgrep -a gmsh 2>/dev/null | sed 's/^/  /' || echo '  none'
  echo -n '== palace ranks: '
  ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -vc Z || echo 0
  echo '== log =='
  stat -c '  %s bytes, mtime %y' $TAG.log 2>/dev/null || echo '  (no log)'
  echo '== meshes present =='
  ls -la --time-style=+%H:%M *.msh 2>/dev/null | awk '{print \"  \",\$5,\$6,\$7}' || echo '  none'
  echo '== tail =='
  tail -6 $TAG.log 2>/dev/null | sed 's/^/  /'
  echo '== kernel: OOM or signal =='
  sudo dmesg -T 2>/dev/null | grep -iE 'out of memory|oom-kill|killed process' | tail -3 | sed 's/^/  /' || echo '  (none)'
"
