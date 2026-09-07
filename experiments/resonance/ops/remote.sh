#!/usr/bin/env bash
# Run a rig on the instance: sync, lint there, launch detached, report.
#   ops/go ops/remote.sh e1b_drive.py [RANKS]
# instance address: ops/env.sh, overridable with $AMIP_HOST — SOURCED HERE,
# like every sibling script. This one relied on inheriting the variable and
# died with "unbound variable" the first time it was run standalone.
HERE_OPS="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$HERE_OPS/env.sh"
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

# 🔴 DO NOT LAUNCH INTO A CLOSING TERMINATION WINDOW.
# 2026-08-28: a spot notice was issued at 00:28:51Z for termination at 00:30:46Z.
# I diagnosed a stagnating case, killed it, edited the config and relaunched at
# ~00:30 — into the last seconds of that window. The rig died before its first
# solve, and the whole cycle (kill, reconfigure, sync, lint, launch) was spent on
# a machine that was already condemned.
# 🔑 AWS publishes the notice ~2 minutes ahead at IMDS. `ops/spotwatch.sh` reads
# it to RECORD interruptions; this reads the same endpoint to REFUSE a launch.
# Same source, different consumer — no second way of asking.
echo "== refuse if this instance is already condemned =="
# 🔴 KEY ON THE HTTP STATUS, NOT THE BODY. With no notice pending IMDS returns a
# 404 whose body is an HTML page — not an empty string — so a substring test on
# the body is a coin flip on whether some word happens to appear in boilerplate.
# `ops/spotwatch.sh` already keys on the code; this uses the same rule so there
# is one way of asking, not two.  200 = notice pending, 404 = clear.
_CODE=$(timeout 20 ssh -i "$K" -o ConnectTimeout=10 $H '
  T=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
      -H "X-aws-ec2-metadata-token-ttl-seconds: 60" --max-time 3 2>/dev/null)
  curl -s -o /tmp/.spotnotice.$$ -w "%{http_code}" --max-time 3 \
      -H "X-aws-ec2-metadata-token: ${T:-}" \
      "http://169.254.169.254/latest/meta-data/spot/instance-action" 2>/dev/null
  echo " $(cat /tmp/.spotnotice.$$ 2>/dev/null | tr -d "\n")"
  rm -f /tmp/.spotnotice.$$' 2>/dev/null)
if [ "${_CODE%% *}" = "200" ]; then
  echo "  🔴 SPOT INTERRUPTION NOTICE ALREADY PENDING on this instance:"
  echo "     ${_CODE#* }"
  echo "     REFUSING to launch — it will die mid-solve. On 2026-08-28 a notice"
  echo "     was issued at 00:28:51Z for termination at 00:30:46Z and a relaunch"
  echo "     went in at ~00:30, dying before its first solve."
  echo "     Start a new instance, set ops/env.sh, NOSYNC=1 ops/go ops/mount.sh."
  exit 4
fi
echo "  no pending notice (IMDS ${_CODE%% *})"

# 🔴 ENV DOES NOT CROSS ssh BY ITSELF. This line hardcoded PALACE_RANKS and RUN,
# so any OTHER variable the caller exported was silently dropped — the rig ran
# with its config default and said nothing, which is the failure shape this
# programme keeps paying for (a guard that announces instead of gating; a value
# that differs from what was asked for with no record of it).
# ✅ Forward an EXPLICIT list, and PRINT what was forwarded so the launch banner
# shows the run's actual settings, not the ones that were intended.
FWD=""
for v in AMIP_CASE_TIMEOUT_S AMIP_MAX_SAMPLES; do
  if [ -n "${!v:-}" ]; then FWD="$FWD $v=${!v}"; echo "  forwarding $v=${!v}"; fi
done
[ -z "$FWD" ] && echo "  no env overrides (rig uses its config)"

echo "== launch (detached, journalled) =="
# 🔴 `set -e` + `timeout 60 ssh` = THE EXEC BELOW NEVER RUNS. 2026-09-05: the
# launch ssh sometimes does not return (it holds the channel even though the job
# is detached and the remote `echo` has already printed). timeout kills it, 124
# meets `set -euo pipefail`, and the script DIES RIGHT HERE — after launching,
# before arming the watch. Both Monitor-hosted launches that day stopped at
# exactly "launched ... at 64 ranks" with rc=124 and watched nothing.
# ⚠️ So the "launch and watch are ONE operation" guarantee was resting on an ssh
# that sometimes does not come back. A guarantee with a hole is worse than none:
# it stops anyone looking for the hole.
# ✅ The launch ssh's exit code is NOT evidence either way. Ask the instance
# whether the rig is running — verify with the CONSUMER, not with the messenger.
set +e
timeout 60 ssh -i "$K" $H \
  "cd $R && nohup bash -c 'source /opt/amip/env.sh && PALACE_RANKS=$RANKS RUN=$TAG$FWD python3 -u $RIG $SLUG_ARG > $TAG.log 2>&1; echo EXIT=\$? >> $TAG.log' >/dev/null 2>&1 & sleep 3; echo '  launched $RIG at $RANKS ranks'"
LAUNCH_RC=$?
set -e
if [ "$LAUNCH_RC" -ne 0 ]; then
  echo "  ⚠️  launch ssh returned $LAUNCH_RC (124 = it held the channel past the"
  echo "      timeout). This is NOT evidence the launch failed — verifying."
fi
# 🔑 ps -C python3 + grep, NOT pgrep -f: pgrep's own argv contains the rig name
# and it matches ITSELF (§7cf, twice). `grep` is not a python3 process, so it
# cannot appear in `ps -C python3` output.
sleep 2
UP=$(timeout 30 ssh -i "$K" $H \
     "ps -C python3 -o args= 2>/dev/null | grep -c -- '-u $RIG'" 2>/dev/null | tr -dc '0-9')
if [ -z "$UP" ] || [ "$UP" -lt 1 ]; then
  echo "  🔴 THE RIG IS NOT RUNNING on the instance. The launch did not take."
  echo "     Nothing is watching because there is nothing to watch."
  exit 5
fi
echo "  ✅ verified: $UP rig process(es) live on the instance"

# 🔴 THIS SAID `watch: ops/go ops/status.sh` UNTIL 2026-08-27. status.sh is a
# SNAPSHOT — it answers "is anything running right now", not "tell me when a
# case lands". Pointing at it here is how launches ended up POLLED instead of
# watched, which CLAUDE.md forbids for exactly this reason. Name the watch.
# 🔴 LAUNCHING AND WATCHING ARE ONE OPERATION. Until 2026-09-05 this printed the
# watch command as ADVICE — and advice is not a guard. Across two days a chained
# launch left the next run unwatched TWICE, and every launch got a hand-rolled
# watcher instead of ops/watch.sh. Both were possible only because "now arm a
# watch" was a SEPARATE step someone had to remember.
# ✅ This no longer returns after launching — it EXECS INTO THE WATCH. There is
# no window in which a run is live and unwatched, and nothing left to substitute
# an ad-hoc loop for.
# ⚠️ NOWATCH=1 for deliberate exceptions (a batch that watches per slug itself).
# It SAYS SO LOUDLY rather than silently returning.
if [ -z "$SLUG_ARG" ]; then
  echo "  🔴 no slug — this launch cannot be watched BY NAME. Relaunch with one."
  exit 4
fi
if [ "${NOWATCH:-0}" = "1" ]; then
  echo "  ⚠️  NOWATCH=1 — this run is LIVE AND UNWATCHED. Arm one yourself:"
  echo "        ops/watch.sh $SLUG"
else
  echo "  == watching (launch and watch are ONE operation) =="
  echo "     mirrored to $SLUG.watch.log regardless of what the caller does"
  exec "$HERE_OPS/watch.sh" "$SLUG"
fi
echo "  snapshot: ops/go ops/status.sh   (is anything running — not a watch)"
echo "  fetch:  ops/go ops/fetch.sh"
