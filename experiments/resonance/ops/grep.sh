#!/usr/bin/env bash
# Grep a remote log. Read-only.  ops/go ops/grep.sh <tag> <pattern>
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
T="${1:?tag}"; P="${2:?pattern}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 60 ssh -i "$K" $H \
  "grep -E '$P' /opt/amip/repo/experiments/resonance/${T}.log 2>/dev/null | head -20"
