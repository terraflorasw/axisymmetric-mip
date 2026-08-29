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

echo "== 6. THE CALLER CANNOT HIDE IT: progress survives a buffering pipe =="
# 🔴 THE REGRESSION THIS GUARDS. `ops/watchrig.sh ... | tail -60` was used twice
# in one session. `tail` holds its whole input until EOF, so a watch that was
# alive and emitting per-case events produced NOTHING until the run ended — a
# job stepping through cases was indistinguishable from a dead watch. The
# watcher was correct; the call site destroyed it. Nothing in the watcher could
# detect that, so instead it MIRRORS every line to disk.
printf 'x\n' > "$LOG"; rm -f "$STUB_STATE"
MIR="$TD/mirror.watch.log"; rm -f "$MIR"
( sleep 2; printf '  --- loop 8x8 = 128 mm^2\n' >> "$LOG"
  sleep 2; printf '    -> Q0=40,147\nEXIT=0\n' >> "$LOG" ) &
# stdout thrown away entirely — the worst case a caller can inflict
WATCH_MIRROR="$MIR" WATCH_RUNNER="$TD/alive" WATCH_SLEEP=1 \
  timeout 30 "$W" "$LOG" > /dev/null 2>&1; RC=$?
wait
ok "$RC" 0 "still completes with stdout discarded"
grep -q 'loop 8x8' "$MIR" && ok yes yes "per-case progress reached the mirror" \
  || ok no yes "per-case progress reached the mirror"
grep -q 'Q0=40,147' "$MIR" && ok yes yes "result line reached the mirror" \
  || ok no yes "result line reached the mirror"
grep -q 'watch armed' "$MIR" && ok yes yes "mirror records when the watch armed" \
  || ok no yes "mirror records when the watch armed"

echo "== 7. CASE BOUNDARY: exits 10 so the caller is actually notified =="
# 🔴 THE REGRESSION THIS GUARDS. Reported twice: "a step finished but the
# monitor is missing", then "it just turned over and again, the monitor didn't
# fire". The watch was alive, matching and mirroring — but the harness running
# it re-invokes on COMMAND EXIT, not on output, so streaming forever notified
# nobody until the whole job ended. Printing is not telling.
printf 'x\n' > "$LOG"; rm -f "$STUB_STATE"
( sleep 2; printf '       pec: TE011 2.4420  Q= 40,716\n' >> "$LOG"
  sleep 6; printf 'EXIT=0\n' >> "$LOG" ) &
OUT=$(WATCH_MIRROR=/dev/null WATCH_RUNNER="$TD/alive" WATCH_SLEEP=1 \
      timeout 30 "$W" "$LOG"); RC=$?
ok "$RC" 10 "exit 10 at a per-solve verdict, not 0"
echo "$OUT" | grep -q 'RE-ARM' && ok yes yes "says to re-arm" || ok no yes "says to re-arm"
echo "$OUT" | grep -q 'pec: TE011' && ok yes yes "emits the line it stopped on" \
  || ok no yes "emits the line it stopped on"
wait

echo "== 7b. JOB END STILL WINS over a boundary on the same poll =="
# A poll that brings BOTH a verdict and EXIT= must report the job finished (0),
# not a boundary (10) — otherwise the last case of a run never triggers the
# end-of-run fetch and the instance is left idle. That is the failure that left
# a box burning for 24 minutes on 2026-08-27.
printf 'x\n' > "$LOG"; rm -f "$STUB_STATE"
( sleep 2; printf '    lumped: TE011 2.4417  Q= 1,090\nEXIT=0\n' >> "$LOG" ) &
OUT=$(WATCH_MIRROR=/dev/null WATCH_RUNNER="$TD/alive" WATCH_SLEEP=1 \
      timeout 30 "$W" "$LOG"); RC=$?
wait
ok "$RC" 0 "exit 0 when the same poll carries EXIT="
echo "$OUT" | grep -q 'run finished' && ok yes yes "reports the job finished" \
  || ok no yes "reports the job finished"

echo "== 7c. WATCH_STOP_RE= disables boundaries (stream to the end) =="
printf 'x\n' > "$LOG"; rm -f "$STUB_STATE"
( sleep 2; printf '       pec: TE011 2.4420  Q= 40,716\n' >> "$LOG"
  sleep 3; printf 'EXIT=0\n' >> "$LOG" ) &
OUT=$(WATCH_STOP_RE= WATCH_MIRROR=/dev/null WATCH_RUNNER="$TD/alive" \
      WATCH_SLEEP=1 timeout 30 "$W" "$LOG"); RC=$?
wait
ok "$RC" 0 "streams past the verdict to the end when disabled"

echo
echo "  $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
