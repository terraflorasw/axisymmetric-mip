"""E0v — re-verify the E0 series at SOLVER ORDER 2.

Six rigs took their solver order from a hardcoded default of 1. E0g later
measured order-1 error at 12-17 MHz, MODE-DEPENDENT BY 40x. Their conclusions
are therefore not refuted but NOT ESTABLISHED, exactly as E0f's was not until
E0f2 re-ran it and found the conclusion right for contaminated reasons.

This re-runs them with eigen_cfg's order now explicit (and announced in every
log line, so it can never be silently inherited again).

⚠️ ORDERING IS DELIBERATE. E0l times against e0fine.json, which E0 writes — so
E0 must run FIRST or E0l would measure order-1 timings while claiming order 2.
E0l runs LAST because it is by far the longest: 6 rank counts, and a 1-rank
order-2 solve of the fine mesh is ~12x the 32-rank time.

⚠️ NOTHING IS SKIPPED. A rig that fails is REPORTED with its exit code and log
tail, and the sequence CONTINUES. A re-verification that silently drops the rig
that broke would be worse than not running it.

VERIFICATION   each rig re-states its own declared checks; this file only
               establishes that every rig ran to completion at order 2.
FALSIFICATION  per rig, in the rig. Here: a non-zero exit, or a result file that
               did not change, means that rig was NOT re-verified.
"""
import json
import os
import pathlib
import subprocess
import sys
import time

RIGS = [
    ("e0_solver_vs_math.py", "e0", "writes e0fine.json that E0l needs"),
    ("e0b_offset.py", "e0b", "256mm translation"),
    ("e0c_rigid.py", "e0c", "translation x rotation"),
    ("e0d_transverse.py", "e0d", "transverse rotation axes"),
    ("e0e_nodeshift.py", "e0e", "node-shift translation invariance"),
    ("e0l_scaling.py", "e0l", "rank scaling — LONGEST, runs last"),
]
PER_RIG_TIMEOUT_S = 10800
OUT = "e0v.result.json"


def fingerprint(rig_stem):
    """What this rig's result file looked like, so we can tell it changed."""
    p = pathlib.Path(f"{rig_stem}.result.json")
    if not p.exists():
        return None
    st = p.stat()
    return {"bytes": st.st_size, "mtime": st.st_mtime}


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    before = {stem: fingerprint(stem) for _f, stem, _w in RIGS}
    rows = []
    for script, stem, why in RIGS:
        if not pathlib.Path(script).exists():
            rows.append({"rig": script, "status": "MISSING", "seconds": 0})
            print(f"\n🔴 {script}: NOT FOUND — reported, continuing", flush=True)
            continue
        print(f"\n{'='*78}\n  {script}  ({why})", flush=True)
        env = {**os.environ, "RUN": stem}
        log = pathlib.Path(f"{stem}_reverify.log")
        t0 = time.time()
        with open(log, "w") as fh:
            proc = subprocess.Popen([sys.executable, "-u", script], env=env,
                                    stdout=fh, stderr=subprocess.STDOUT)
            try:
                rc = proc.wait(timeout=PER_RIG_TIMEOUT_S)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
                rc = "TIMEOUT"
        dt = time.time() - t0
        after = fingerprint(stem)
        changed = (before[stem] != after) and after is not None
        rows.append({"rig": script, "stem": stem, "rc": rc,
                     "seconds": round(dt, 1), "result_changed": changed,
                     "log": str(log)})
        tail = log.read_text().strip().splitlines()[-2:]
        mark = "✅" if rc == 0 and changed else "🔴"
        print(f"  {mark} rc={rc} in {dt/60:.1f} min, "
              f"result file {'updated' if changed else 'UNCHANGED'}")
        for t in tail:
            print(f"      {t[:100]}")
        pathlib.Path(OUT).write_text(json.dumps(
            {"solver_order": 2, "rows": rows}, indent=1) + "\n")
        print(f"  (e0v.result.json updated, {len(rows)}/{len(RIGS)})", flush=True)

    print("\n" + "=" * 78)
    print(f"  {'rig':<26}{'rc':>8}{'minutes':>10}{'result':>12}")
    for r in rows:
        print(f"  {r['rig']:<26}{str(r.get('rc', '—')):>8}"
              f"{r['seconds']/60:>10.1f}"
              f"{('updated' if r.get('result_changed') else 'UNCHANGED'):>12}")
    bad = [r for r in rows if r.get("rc") != 0 or not r.get("result_changed")]
    print()
    if bad:
        print(f"  🔴 NOT re-verified: {[r['rig'] for r in bad]}")
    else:
        print(f"  ✅ all {len(rows)} rigs re-ran to completion at solver order 2")
    print("\n  wrote e0v.result.json — NO VERDICT HERE. Each rig's own declared")
    print("  checks are in its log; this only says they ran.", flush=True)


if __name__ == "__main__":
    main()
