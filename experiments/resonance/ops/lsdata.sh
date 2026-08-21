#!/usr/bin/env bash
# What solver output actually exists on the instance? Read-only.
#
#   ops/go ops/lsdata.sh            # everything
#   ops/go ops/lsdata.sh 'h2b_*'    # one rig (QUOTE the glob — it must expand
#                                   # on the instance, not on the laptop)
#
# 🔴 A DIRECTORY IS NOT A SOLVED CASE. The reclamation of 2026-08-21 19:47 UTC
# killed a rig mid-case, and a case interrupted during its solve leaves a
# postpro dir with a short or absent eig.csv. Report the LINE COUNTS and let
# them be compared, rather than reporting existence.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
G="${1:-*}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H "G='$G' bash -s" <<'REMOTE'
  cd /opt/amip/repo/experiments/resonance/postpro 2>/dev/null || exit 9
  shopt -s nullglob
  n=0
  for d in $G; do
    [ -d "$d" ] || continue
    n=$((n+1))
    e=$( [ -f "$d/eig.csv" ] && wc -l < "$d/eig.csv" || echo 0 )
    m=$( [ -f "$d/domain-E.csv" ] && wc -l < "$d/domain-E.csv" || echo 0 )
    t=$(date -u -r "$d" +%Y-%m-%dT%H:%MZ 2>/dev/null)
    printf "  %-22s eig.csv %3s   domain-E.csv %3s   %s\n" "$d" "$e" "$m" "$t"
  done
  echo "  -- $n dir(s) matching '$G'"
REMOTE
