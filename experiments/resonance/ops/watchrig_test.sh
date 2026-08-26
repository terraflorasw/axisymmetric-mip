#!/usr/bin/env bash
# Does ops/watchrig.sh actually fire, and actually NOT fire?
#
# 🔴 WRITTEN BECAUSE THREE WATCHERS WERE SHIPPED UNTESTED IN ONE DAY, each
# broken in a different direction: one never stopped, one was silent for the
# whole run, one was correct but slow. User, 2026-08-25: *"I'll keep using spot
# until we can verify the monitor works correctly in all cases."*
#
# The remote runner is injectable, so HOST DEATH is reachable here without
# terminating a machine. A test that needs a real reclamation is a test nobody
# runs (§7d).
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
W="$HERE/watchrig.sh"
TD=$(mktemp -d); trap 'rm -rf "$TD"' EXIT
LOG="$TD/rig.log"
PASS=0; FAIL=0
ok() { if [ "$1" = "$2" ]; then echo "  ✅ $3"; PASS=$((PASS+1));
       else echo "  🔴 $3 — got [$1] want [$2]"; FAIL=$((FAIL+1)); fi }

# stub runners. Each takes the remote command as one arg, like ssh does.
export STUB_STATE="$TD/state"
cat > "$TD/alive" <<'S'
#!/usr/bin/env bash
eval "$1"
S
cat > "$TD/dead" <<'S'
#!/usr/bin/env bash
exit 255      # what ssh returns when it cannot connect
S
cat > "$TD/flaky" <<'S'
#!/usr/bin/env bash
n=$(cat "$STUB_STATE" 2>/dev/null || echo 0); echo $((n+1)) > "$STUB_STATE"
[ "$n" -lt 1 ] && exit 255     # fail ONCE, then recover
eval "$1"
S
chmod +x "$TD/alive" "$TD/dead" "$TD/flaky"

echo "== 1. PROGRESS: new lines are emitted as they land =="
printf 'boot\n' > "$LOG"
( sleep 1; printf '  --- loop 11x8 = 176 mm^2  mount=barrel\n' >> "$LOG"
  sleep 1; printf '    -> Q0=   43,463  Q_ext=    8,716\n' >> "$LOG"
  sleep 2; printf 'EXIT=0\n' >> "$LOG" ) &
OUT=$(WATCH_RUNNER="$TD/alive" WATCH_SLEEP=1 WATCH_STRIKES=3 timeout 30 "$W" "$LOG")
wait
echo "$OUT" | grep -q -- '--- loop 11x8' && ok yes yes "emits the case-start line" || ok no yes "emits the case-start line"
echo "$OUT" | grep -q 'Q_ext=    8,716'  && ok yes yes "emits the result line"     || ok no yes "emits the result line"
echo "$OUT" | grep -q 'boot'             && ok no  yes "does NOT replay pre-existing backlog" || ok yes yes "does NOT replay pre-existing backlog"

echo "== 2. JOB ENDS: exits 0 on the EXIT= sentinel =="
printf 'x\n' > "$LOG"; ( sleep 1; printf 'EXIT=0\n' >> "$LOG" ) &
OUT=$(WATCH_RUNNER="$TD/alive" WATCH_SLEEP=1 timeout 20 "$W" "$LOG"); RC=$?
wait
ok "$RC" 0 "exit code 0 when the job finishes"
echo "$OUT" | grep -q 'run finished' && ok yes yes "says the run finished" || ok no yes "says the run finished"

echo "== 3. MACHINE ENDS: fires on repeated unreachability =="
printf 'x\n' > "$LOG"
OUT=$(WATCH_RUNNER="$TD/dead" WATCH_SLEEP=1 WATCH_STRIKES=3 timeout 30 "$W" "$LOG"); RC=$?
ok "$RC" 2 "exit code 2 when the host is gone"
echo "$OUT" | grep -q 'HOST UNREACHABLE' && ok yes yes "names the reclamation" || ok no yes "names the reclamation"
echo "$OUT" | grep -q 'relaunch the SAME slug' && ok yes yes "states the recovery step" || ok no yes "states the recovery step"

echo "== 4. NO FALSE POSITIVE: one blip must NOT trip it =="
printf 'x\n' > "$LOG"; rm -f "$STUB_STATE"
( sleep 3; printf 'EXIT=0\n' >> "$LOG" ) &
OUT=$(WATCH_RUNNER="$TD/flaky" WATCH_SLEEP=1 WATCH_STRIKES=3 timeout 30 "$W" "$LOG"); RC=$?
wait
ok "$RC" 0 "survives a single ssh failure and still completes"
echo "$OUT" | grep -q 'HOST UNREACHABLE' && ok yes no "does not cry reclamation on a blip" || ok no no "does not cry reclamation on a blip"

echo "== 5. ALREADY FINISHED: a completed run must not be watched silently =="
printf 'boot\nEXIT=0\n' > "$LOG"      # sentinel is ALREADY in the log
OUT=$(WATCH_RUNNER="$TD/alive" WATCH_SLEEP=1 timeout 20 "$W" "$LOG"); RC=$?
ok "$RC" 3 "exit code 3 when the run finished before the watch armed"
echo "$OUT" | grep -q 'ALREADY contains EXIT=' && ok yes yes "says so instead of waiting" || ok no yes "says so instead of waiting"

echo
echo "  $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
