#!/usr/bin/env bash
# SHA-256 of the meshes a completed run used. Read-only.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
H="$AMIP_HOST"
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 90 ssh -i "$K" $H \
  'cd /opt/amip/repo/experiments/resonance && sha256sum e1b_*.msh 2>/dev/null'
