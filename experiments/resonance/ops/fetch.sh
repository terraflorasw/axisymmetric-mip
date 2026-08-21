#!/usr/bin/env bash
# Pull results back. ALLOWLIST — with unknown filenames a whitelist fails safe.
# instance address: ops/env.sh, overridable with $AMIP_HOST
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -euo pipefail
# repo parent (holds aws.pem), derived from THIS script's location
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
rsync -avz -e "ssh -i $K" \
  --include='*.result.json' --include='*.criteria.json' --include='*.jsonl' \
  --include='*.log' --include='postpro/***' --include='*/' --exclude='*' \
  "$H:$R/" . | tail -4
