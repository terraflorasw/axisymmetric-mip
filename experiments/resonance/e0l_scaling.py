"""E0l — how many ranks per solve? Measured, after months of assertion.

I have repeatedly claimed this workload is memory-bandwidth-bound and never
measured it. On a 32-core c7a that claim decides how the machine is used:

    bandwidth-bound  -> more ranks per solve buys little; run MANY solves at 4
    core-bound       -> few big solves scale, and fan-out is less important

TWO QUESTIONS, one run:

1. SPEED     wall time vs rank count on one fixed mesh and config.
2. 🔑 ANSWER does the rank count CHANGE THE RESULT? MPI partitions the domain,
             so the floating-point summation order differs. E0e proved
             determinism at FIXED ranks; this asks whether ranks themselves are
             a variable that has to be controlled. If TE011 moves with -np, then
             every comparison in this project must hold rank count fixed, and
             the acceptance test's exact match with the laptop was partly luck.

VERIFICATION   physics.spectrum() — every rank count must land at the same
               distance from the closed form.
FALSIFICATION  if TE011 shifts by more than the ~1.2 MHz mesh floor across rank
               counts, rank count is a hidden variable and prior comparisons
               need re-reading.
"""
import json
import os
import signal
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solver

CFG = "e0fine.json"
# Selectable so the expensive points can be reused instead of re-paid. The
# order-2 1-rank solve is 106 MINUTES; re-running it to get the 4/8/16/32 points
# would cost 2.7 hours for nothing.
RANKS = [int(x) for x in os.environ.get("E0L_RANKS", "1,2,4,8,16,32").split(",")]
# measured 2026-08-21 at solver order 2 on this same CFG; merged into the output
# so the curve is complete without re-running them. rc=0, TE011 identical.
PRIOR = {1: 6385.9, 2: 3301.3}
# 🔴 LEGACY CAVITY, DELIBERATELY NOT BOUND. 103.70/88.53 is D/L = 2.343 —
# candidate A, which H1 REJECTED. This script ANALYSES data meshed at those
# dimensions, so the closed form here must use them or the comparison is
# meaningless. Binding it to cavity.d_over_l would silently break that.
# ⚠️ THEREFORE NOTHING HERE IS A DESIGN NUMBER. Re-run on H1's cavity is
# queued in NEXT.md § THE GEO RE-RUN LIST (2026-08-25).
A_MM, L_MM = 103.70, 88.53   # LEGACY — see above


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    if not pathlib.Path(CFG).exists():
        sys.exit(f"{CFG} missing — run e0_solver_vs_math.py first")
    EX = ph.spectrum(A_MM, L_MM)
    rows = []
    # 🔴 MERGE PRIOR FIRST. The first version appended these AFTER the summary
    # table, so every speedup and efficiency cell printed NaN — the -np 1
    # reference was not in `rows` when the table was built. A merge that happens
    # after the thing that consumes it is the same defect as a baseline nobody
    # reads (R110) and a flag that never reaches the solver (R101).
    _measured = {n for n in RANKS}
    for n, dt in sorted(PRIOR.items()):
        if n not in _measured:
            rows.append((n, dt, 0, None))
            print(f"    -np {n:<4} {dt:8.1f}s  (PRIOR, measured earlier)",
                  flush=True)
    for n in RANKS:
        t0 = time.time()
        proc = subprocess.Popen([solver.PALACE, "-np", str(n), CFG],
                                env=solver.ENV,
                                stdout=open(f"scale_{n}.log", "w"),
                                stderr=subprocess.STDOUT,
                                start_new_session=True)
        try:
            rc = proc.wait(timeout=solver.DEFAULT_TIMEOUT_S)
        except subprocess.TimeoutExpired:
            # 🔴 proc.kill() KILLS ONLY THE BASH WRAPPER. The real tree is
            #   palace (wrapper) -> prterun -> palace-x86_64.bin xN
            # so killing the wrapper orphans prterun and every rank to PPID 1.
            # Observed: four ranks ran 20 minutes after E0v killed this rig, and
            # reap.py reported "no orphaned palace ranks" the entire time
            # because it only looked for ranks whose OWN parent was init.
            # start_new_session + killpg takes the whole group.
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError):
                proc.kill()
            proc.wait(); rc = -1
        dt = time.time() - t0
        f = pathlib.Path("postpro/e0fine/eig.csv")
        v = sorted(float(l.split(",")[1])
                   for l in f.read_text().splitlines()[1:]
                   if len(l.split(",")) > 2) if rc == 0 and f.exists() else []
        te = min(v, key=lambda x: abs(x - EX["TE011"])) if v else float("nan")
        rows.append((n, dt, rc, te))
        print(f"  -np {n:<3} {dt:7.1f}s  rc={rc}  TE011={te:.7f}", flush=True)

    base = next((r for r in rows if r[0] == 1 and r[2] == 0), None)
    print(f"\n{'ranks':>6}{'seconds':>10}{'speedup':>10}{'efficiency':>12}"
          f"{'TE011 GHz':>13}{'Δ vs -np 1':>12}")
    for n, dt, rc, te in rows:
        sp = base[1] / dt if base and dt else float("nan")
        d = 1e3 * (te - base[3]) if base else float("nan")
        print(f"{n:>6}{dt:>10.1f}{sp:>9.2f}x{100*sp/n:>11.0f}%{te:>13.7f}"
              f"{d:>12.4f}")
    ok = [r for r in rows if r[2] == 0]
    if len(ok) > 1:
        spread = 1e3 * (max(r[3] for r in ok) - min(r[3] for r in ok))
        print(f"\n  🔑 TE011 spread across ALL rank counts: {spread:.4f} MHz")
        print(f"     {'✅ rank count is NOT a variable' if spread < 0.01 else '🔴 RANK COUNT CHANGES THE ANSWER — it must be held fixed'}")
    rows.sort()
    json.dump([{"ranks": n, "seconds": dt, "rc": rc, "te011": te}
               for n, dt, rc, te in rows],
              open("e0l.result.json", "w"), indent=1)
    print("\n  wrote e0l.result.json", flush=True)


if __name__ == "__main__":
    main()
