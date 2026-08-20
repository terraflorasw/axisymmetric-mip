#!/usr/bin/env bash
# Autonomous fallback: abandon a non-converging order-2 solve and relaunch it
# tighter. Called only if final_o2 has not produced a result by the wakeup.
#
# Kill procedure is the TESTED one: exact argv match, kill by PID, never
# `pkill -f` (which matches the harness wrapper and kills the caller).
set -u
cd "$(dirname "$0")"
DRY="${1:-}"
echo "== fallback $(date -u '+%Y-%m-%d %H:%M:%SZ') =="

if [ -s final_o2.log ]; then
  echo "final_o2.log is non-empty — solve finished. NOT killing. Contents:"
  cat final_o2.log
  exit 0
fi

# identify the ranks by exact binary + config, zombie-filtered
# Require comm to be EXACTLY the solver binary. Matching on args alone also
# catches the awk doing the matching (its program text is in its own argv) and
# prterun, the MPI launcher. comm is truncated to 15 chars by the kernel, hence
# "palace-x86_64.b". Killing the ranks is enough — prterun and the python
# parent wind down on their own.
TARGETS=$(ps -eo pid=,stat=,comm=,args= \
  | awk '$2 !~ /Z/ && $3 == "palace-x86_64.b" && index($0, "final_o2.json") {print $1}')
echo "ranks matched: ${TARGETS:-<none>}"
[ -z "$TARGETS" ] && { echo "nothing running; will just relaunch"; }

if [ "$DRY" = "--dry-run" ]; then
  echo "(dry run — no kill, no relaunch)"
  ps -eo pid=,args= | awk 'index($0,"final_o2")' | sed 's/^/  would leave: /' | head -5
  exit 0
fi

for pid in $TARGETS; do kill -TERM "$pid" 2>/dev/null && echo "  TERM -> $pid"; done
sleep 5
STILL=$(ps -o pid= $TARGETS 2>/dev/null | wc -l)
[ "$STILL" -gt 0 ] && { echo "  escalating to KILL"; for pid in $TARGETS; do kill -KILL "$pid" 2>/dev/null; done; }
mkdir -p postpro/final_o2 && cat > postpro/final_o2/.aborted <<'MARK'
Abandoned: order-2 at N=10 did not converge within ~90 min. Superseded by
final_o2b (N=6, Target 2.45, Tol 1e-6). No usable data.
MARK

# Relaunch tighter. Preconditioner application was 77% of runtime in the
# earlier profile, and it scales with eigenvalue count and iteration count —
# so cut N and loosen Tol. 1e-6 is still far tighter than the ~4e-4 relative
# precision the design decision needs.
python3 - <<'PY'
import json, pathlib
c = json.loads(pathlib.Path("inj-base.json").read_text())
c["Model"]["Mesh"] = "final_o2.msh"
c["Solver"]["Order"] = 2
c["Solver"]["Eigenmode"].update({"Target": 2.45, "N": 6, "Tol": 1.0e-6, "Save": 0})
c["Problem"]["Output"] = "postpro/final_o2b"
pathlib.Path("final_o2b.json").write_text(json.dumps(c, indent=2))
print("  wrote final_o2b.json: N=6, Target 2.45, Tol 1e-6")
PY
export MAMBA_ROOT_PREFIX="$HOME/.local/share/mamba"
export PATH="$HOME/.local/share/mamba/envs/emsim/bin:$PATH"
# -np 4, and NOT more. nproc reports 8 but those are hardware THREADS; PRRTE
# allocates by physical cores, of which there are 4, so -np 6 fails outright
# with "not enough slots". run-eigenmode.sh has always computed this correctly
# via `lscpu -p=Core,Socket | sort -u | wc -l`. Hyperthreads would need
# --use-hwthread-cpus and are worth little for FP-heavy FEM anyway.
"$HOME/.local/opt/palace/bin/palace" -np 4 final_o2b.json > final_o2b.log 2>&1
echo "EXIT=$?" >> final_o2b.log
echo "relaunch finished; tail:"; tail -3 final_o2b.log
