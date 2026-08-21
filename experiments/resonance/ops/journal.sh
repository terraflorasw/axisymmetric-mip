#!/usr/bin/env bash
# Solver order per run, from the per-run journals on the instance. Read-only.
# journal.log writes <run>.jsonl, one file per RUN — not a single journal.jsonl.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
timeout 90 ssh -i "$K" $H \
  'cd /opt/amip/repo/experiments/resonance || exit 9
   source /opt/amip/env.sh
   ls *.jsonl 2>/dev/null | sed "s/^/  journal: /" || echo "  no .jsonl files"
   python3 -u journal_audit.py'
