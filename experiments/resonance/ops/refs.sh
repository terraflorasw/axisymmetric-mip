#!/usr/bin/env bash
# Move CLOSED (rights-reserved) references between this machine and the volume.
#
# 🔴 WHY THIS EXISTS AS A SEPARATE COMMAND. `rsync.sh` carries
# `--filter=':- .gitignore'`, and `refs/closed/` is gitignored — so the DEFAULT
# sync deliberately skips these files. That is the safety property: a closed PDF
# cannot ride along into the repo, and cannot be pushed by accident. Moving them
# is therefore an explicit act, which is this script.
#
# 🔴 THEY LIVE OUTSIDE THE REPO COPY ON THE INSTANCE (/opt/amip/refs-closed),
# not under /opt/amip/repo. If they sat inside the repo tree, the next person to
# reason about "what is in the repo" would be wrong on both machines.
#
# ✅ The VOLUME is the durable home — it survives spot reclamation; an instance
# does not. The laptop copy is a working convenience.
#
#   ops/go ops/refs.sh push     # laptop -> volume
#   ops/go ops/refs.sh pull     # volume -> laptop
#   ops/go ops/refs.sh list     # what is on the volume
#
# ⚠️ NOSYNC=1 is the sane way to call these: the default repo sync is unrelated
# to what this moves.  NOSYNC=1 ops/go ops/refs.sh pull
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -uo pipefail
H="$AMIP_HOST"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"   # repo parent
K=${AWS_PEM:-$ROOT/aws.pem}
LOCAL="$ROOT/axisymmetric-mip/refs/closed"
REMOTE=/opt/amip/refs-closed
MODE="${1:-list}"

mkdir -p "$LOCAL"

# 🔴 Reach the host FIRST and fail loudly. §7bv: a launcher that cannot reach the
# host must FAIL, not narrate — and a silent no-op here looks exactly like an
# empty reference store.
if ! timeout 25 ssh -i "$K" -o ConnectTimeout=15 -o BatchMode=yes "$H" \
        "mkdir -p $REMOTE" 2>/dev/null; then
  echo "  🔴 refs: INSTANCE UNREACHABLE — $H"
  echo "     Nothing was transferred. (First contact with a replacement also"
  echo "     fails on an unknown host key: ssh once with StrictHostKeyChecking=accept-new.)"
  exit 3
fi

case "$MODE" in
  push)
    echo "== push  $LOCAL  ->  $H:$REMOTE"
    rsync -avz -e "ssh -i $K" "$LOCAL/" "$H:$REMOTE/" | tail -3
    ;;
  pull)
    echo "== pull  $H:$REMOTE  ->  $LOCAL"
    rsync -avz -e "ssh -i $K" "$H:$REMOTE/" "$LOCAL/" | tail -3
    ;;
  list)
    echo "== on the volume: $REMOTE"
    timeout 30 ssh -i "$K" "$H" "ls -la $REMOTE 2>/dev/null | tail -n +2" | sed 's/^/  /'
    echo "== local: $LOCAL"
    ls -la "$LOCAL" | tail -n +2 | sed 's/^/  /'
    ;;
  *)
    echo "usage: ops/refs.sh {push|pull|list}"; exit 2 ;;
esac

# 🔑 The CITATION is the record, not the file. refs/README.md is tracked and
# carries every reference with the numbers used, so nothing here is load-bearing.
echo "  ⚠️ closed refs are NOT in git and NOT in the default sync — refs/README.md is the record"
