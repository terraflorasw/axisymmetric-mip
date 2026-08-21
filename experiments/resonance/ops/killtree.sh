#!/usr/bin/env bash
# Kill an ORPHANED palace launch tree on the instance, leaf-first.
#
# 🔴 reap.py looks for palace-x86_64.bin with PPID==1 and finds nothing, because
# the ranks are never direct children. The real tree is:
#     palace (bash wrapper, gets orphaned to PPID 1)
#       -> prterun
#            -> palace-x86_64.bin xN
# Killing the rig leaves the WRAPPER orphaned and the ranks running under it.
#
# Selects by PID from a walked tree — never pkill -f, which matched the calling
# shell three times.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
MODE="${APPLY:-0}"
timeout 90 ssh -i "$K" $H "
  # orphan roots: a palace wrapper or prterun whose parent is init
  roots=\$(ps -eo pid=,ppid=,comm= | awk '\$2==1 && (\$3==\"palace\" || \$3==\"prterun\") {print \$1}')
  if [ -z \"\$roots\" ]; then echo '  no orphaned palace launch tree'; exit 0; fi
  for r in \$roots; do
    echo \"  orphan root \$r: \$(ps -o args= -p \$r | cut -c1-60)\"
    # descendants, breadth-first
    tree=\"\$r\"; frontier=\"\$r\"
    for depth in 1 2 3 4; do
      next=''
      for p in \$frontier; do
        kids=\$(ps -eo pid=,ppid= | awk -v P=\$p '\$2==P {print \$1}')
        next=\"\$next \$kids\"
      done
      [ -z \"\$(echo \$next)\" ] && break
      tree=\"\$tree \$next\"; frontier=\"\$next\"
    done
    echo \"    tree: \$(echo \$tree | tr '\n' ' ')\"
    if [ '$MODE' = '1' ]; then
      # leaf-first: reverse the list so children die before parents
      for p in \$(echo \$tree | tr ' ' '\n' | tac); do
        kill -TERM \$p 2>/dev/null && echo \"    killed \$p\"
      done
      sleep 3
      for p in \$(echo \$tree | tr ' ' '\n'); do kill -KILL \$p 2>/dev/null; done
    fi
  done
  sleep 2
  echo -n '  palace ranks remaining: '
  ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -vc Z || echo 0
  uptime | sed 's/^/  /'
"
