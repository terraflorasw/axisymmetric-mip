#!/usr/bin/env bash
# Remove the retired E1 series from the instance. DRY RUN unless APPLY=1.
#
# rsync.sh has no --delete (deliberately: gitignored artifacts on the instance —
# meshes, postpro — are not in the local tree and --delete's protection rules
# make its behaviour here subtle). So retirement is explicit and by name.
#
#   ops/go ops/cleanremote.sh          # list what would go
#   APPLY=1 ops/go ops/cleanremote.sh  # actually remove
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
MODE="${APPLY:-0}"

BUSY=$(timeout 30 ssh -i "$K" $H \
  'r=$(ps -C python3 -o args= 2>/dev/null | grep -c "^python3 -u [a-z]")
   g=$(ps -C python3 -o args= 2>/dev/null | grep -c "geometry\.py")
   n=$(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l)
   echo $(( ${r:-0} + ${g:-0} + ${n:-0} ))' 2>/dev/null || echo unreachable)
if [ "$BUSY" != "0" ]; then
  echo "🔴 $BUSY process(es) running remotely — refusing to delete under a live run"
  exit 1
fi

timeout 120 ssh -i "$K" $H "
  cd $R || { echo 'wrong dir'; exit 9; }
  # sanity: only ever run this where the programme actually lives
  [ -f physics.py ] || { echo '🔴 no physics.py here — refusing'; exit 9; }
  echo '  targets:'
  ls -d e1*.py e1*.json e1*.msh e1*.meta.json e1*.log e1*.jsonl \
        postpro/e1* 2>/dev/null | sed 's/^/    /'
  echo -n '  total size: '
  du -shc e1*.py e1*.json e1*.msh e1*.meta.json postpro/e1* 2>/dev/null \
    | tail -1 | cut -f1
  if [ '$MODE' = '1' ]; then
    # literal globs, no variables in the rm — sh_rm_rf_var exists because a
    # variable that expands to empty turns 'rm -rf \$V/' into 'rm -rf /'
    # e1b_loaded.py is the RETIRED MONOLITH the split replaced. The first
    # version of this list named the replacements and not the thing they
    # replaced, leaving a runnable stale rig on the instance.
    rm -f e1_design_analytic.py e1b_drive.py e1b_analyse.py recover_e1b_manifest.py
    rm -f e1b_loaded.py
    rm -f e1b.result.json e1b.manifest.json
    rm -f e1b_*.json e1c_*.json e1cc_*.json
    rm -f e1b_*.msh e1c_*.msh e1cc_*.msh
    rm -f e1b_*.meta.json e1c_*.meta.json e1cc_*.meta.json
    rm -f e1b_*_p.log e1c_*_p.log e1cc_*_p.log e1b_loaded.log
    rm -f e1b.jsonl e1b_loaded.jsonl
    rm -rf postpro/e1b_A_tran postpro/e1b_A_load postpro/e1b_B_tran postpro/e1b_B_load
    rm -rf postpro/e1c_k1p0 postpro/e1c_k2p0 postpro/e1c_k3p0
    rm -rf postpro/e1cc_sf1p5 postpro/e1cc_sf2p0
    echo '  ✅ removed'
    echo -n '  remaining e1: '; ls -d e1* postpro/e1* 2>/dev/null | tr '\n' ' '; echo
    df -h /opt/amip | tail -1 | sed 's/^/  /'
  else
    echo '  (dry run — set APPLY=1 to remove)'
  fi
"
