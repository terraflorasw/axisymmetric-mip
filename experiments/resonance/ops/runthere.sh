#!/usr/bin/env bash
# Run a SHORT script on the instance synchronously and print its output.
# For checks and probes, not for solves — use ops/remote.sh for those.
#   ops/go ops/runthere.sh condcheck.py
set -uo pipefail
S="${1:?usage: ops/runthere.sh <script.py> [args...]}"; shift || true
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
timeout 600 ssh -i "$K" -o ConnectTimeout=15 $H \
  "cd $R && source /opt/amip/env.sh && python3 -u $S $*"
