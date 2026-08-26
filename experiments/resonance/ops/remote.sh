#!/usr/bin/env bash
# Run a rig on the instance: sync, lint there, launch detached, report.
#   ops/go ops/remote.sh e1b_drive.py [RANKS]
# instance address: ops/env.sh, overridable with $AMIP_HOST — SOURCED HERE,
# like every sibling script. This one relied on inheriting the variable and
# died with "unbound variable" the first time it was run standalone.
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/env.sh"
set -euo pipefail
RIG="${1:?usage: ops/remote.sh <rig.py> [ranks] [slug]}"
RANKS="${2:-4}"
# 🔑 SLUG (optional during migration, CONVENTIONS 7aw/7az). When given it names
# the log, the RUN env var and the rig's own --slug, so nothing this run writes
# can collide with another run of the same rig. Without it the log falls back to
# the RIG NAME, which is exactly the collision 7ap describes — so it warns.
SLUG="${3:-}"
# repo parent (holds aws.pem), derived from THIS script's location
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
K=${AWS_PEM:-$ROOT/aws.pem}
H="$AMIP_HOST"
R=/opt/amip/repo/experiments/resonance
if [ -n "$SLUG" ]; then
  TAG="$SLUG"
  SLUG_ARG="--slug $SLUG"
  # 🔑 RANKS COMES FROM THE CONFIG, NOT THE COMMAND LINE. It was in both, with
  # nothing reconciling them — the config could record 32 while the run used 4,
  # and the config is what a later reader trusts. Two sources of truth for a
  # parameter that affects the run is not idempotent, it is a coin toss you
  # cannot see. The CLI value is now only a cross-check.
  CFG_RANKS=$(python3 - "$SLUG" <<'PYEOF'
import json, sys
try:
    d = json.load(open("baseline-%s.json" % sys.argv[1]))
    print(d["_run"]["parameters"].get("ranks") or "")
except Exception:
    print("")
PYEOF
)
  if [ -n "$CFG_RANKS" ]; then
    if [ "$CFG_RANKS" != "$RANKS" ]; then
      echo "  ⚠️  ranks: config says $CFG_RANKS, command line said $RANKS."
      echo "     USING THE CONFIG ($CFG_RANKS) — it is what the record will claim."
    fi
    RANKS="$CFG_RANKS"
  else
    echo "  ⚠️  baseline-$SLUG.json records no ranks; using $RANKS from the"
    echo "     command line. Add parameters.ranks so the run is reproducible."
  fi
else
  TAG="${RIG%.py}"
  SLUG_ARG=""
  echo "  ⚠️  no slug given — log is $TAG.log, named for the RIG not the RUN."
  echo "     A re-run overwrites it (CONVENTIONS 7ap). Pass a slug:"
  echo "     ops/go ops/remote.sh $RIG $RANKS <slug>"
fi

echo "== sync =="
( cd ../../.. && bash rsync.sh ) | tail -2

echo "== refuse if anything is already running =="
# 🔴 THIS COUNTED ONLY PALACE RANKS UNTIL 2026-08-25 — the identical bug ops/go
# documents and fixed: "BUSY MEANS 'A RIG IS RUNNING', NOT 'PALACE IS RUNNING'.
# A rig spends a large fraction of its life meshing, and its whole
# post-processing tail, with ZERO ranks alive." So this gate read 0 while a rig
# was still fitting and writing results, and would happily launch a second rig
# into it. The fix landed in ops/go and NOT here — CONVENTIONS 7r: a correction
# made in one place is not a correction to the programme.
BUSY=$(timeout 30 ssh -i "$K" $H \
  'r=$(ps -C python3 -o args= 2>/dev/null | grep -c "^python3 -u [a-z]")
   g=$(ps -C python3 -o args= 2>/dev/null | grep -c "geometry\.py")
   n=$(ps -o stat= -C palace-x86_64.bin 2>/dev/null | grep -v Z | wc -l)
   echo $(( ${r:-0} + ${g:-0} + ${n:-0} ))')
[ "$BUSY" = "0" ] || { echo "🔴 $BUSY rig/mesh/rank process(es) already running — refusing to collide"; exit 1; }

echo "== lint on the instance =="
# 🔴 THE LINT MUST SOURCE env.sh, BECAUSE THE LAUNCH DOES. Without it the gate
# ran /usr/bin/python3 while the rig runs /opt/amip/envs/emsim/bin/python3 —
# TWO DIFFERENT INTERPRETERS, different versions (3.12 in the env) and different
# installed packages. So preflight was certifying an environment the rig never
# executes in, which is CONVENTIONS §7: a checker that cannot see its subject.
# It is also how "pyflakes not installed" survived a root-level apt install —
# the fix landed in the interpreter nobody runs.
timeout 60 ssh -i "$K" $H "cd $R && source /opt/amip/env.sh && python3 preflight.py $RIG"

echo "== launch (detached, journalled) =="
timeout 60 ssh -i "$K" $H \
  "cd $R && nohup bash -c 'source /opt/amip/env.sh && PALACE_RANKS=$RANKS RUN=$TAG python3 -u $RIG $SLUG_ARG > $TAG.log 2>&1; echo EXIT=\$? >> $TAG.log' >/dev/null 2>&1 & sleep 3; echo '  launched $RIG at $RANKS ranks'"
echo "  watch:  ops/go ops/status.sh"
echo "  fetch:  ops/go ops/fetch.sh"
