"""E0k — the missing cell. Isolate PROBLEM TYPE from LOADING.

The comparison as it stood changed two things at once:

    old, DRIVEN,    LOADED (quartz torch + filter)   offset +24.54 MHz   R38
    new, EIGENMODE, EMPTY                            offset +12.00 MHz   E0g

A factor of 2 — but problem type AND loading both differ, so the table cannot
attribute it. The user's point: there must be a "new, DRIVEN, EMPTY" row.

🔑 ONE MESH, FOUR SOLVES. Driven needs a port, so this mesh HAS a coupling loop.
That is fine, because the quantity measured is an ORDER-1 -> ORDER-2 OFFSET on a
FIXED mesh: the loop is present in both solves of each pair and cancels exactly,
the same way discretisation cancels. What does NOT cancel between the pairs is
the problem type, which is the whole point.

    eigenmode order 1  ->  eigenmode order 2   offset_eig
    driven    order 1  ->  driven    order 2   offset_drv

    offset_eig vs offset_drv  = PROBLEM TYPE, zero other differences
    offset_eig vs E0g's 12.00 = the LOOP's contribution (E0g had no loop)
    offset_drv vs R38's 24.54 = LOADING, at fixed problem type

VERIFICATION   the order-2 solves of both types are compared against
               physics.spectrum(). The loop perturbs, so agreement is expected
               to a few MHz, not exactly.

⚠️ NOTHING IS DISCARDED. Every solve's frequency is reported with its deviation
from exact and the diagnostics behind its mode pick, whether it looks right or
not. A script that drops a row makes its own criterion invisible — and criteria
in this project have been mis-specified three times (a sub-noise linearity gate,
a null control graded as a failure for passing, a degeneracy guard that watched
frequency instead of character). A criterion that deletes its evidence cannot be
caught being wrong. Flags go in a column; the row stays.
FALSIFICATION  🔴 if offset_eig and offset_drv differ by ~2x on ONE MESH with
               ONE geometry, the old R37 disagreement is real, survives at
               order 2, and is a property of the two solvers rather than of the
               old programme's setup. If they agree, R37 was an artifact and the
               24.54/12.00 gap is entirely LOADING.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import journal
import solveconf
import dq
from e0_solver_vs_math import A_MM, L_MM, GEO, eigen_cfg, run, eig

TAG = "e0k"
LOOP = ["--loop", "25.8,19.4,1.5,0.3", "--loop-phi", "36"]
BAND, STEP = (2.415, 2.455), 2e-5      # brackets order-1 (low) and order-2


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{TAG}.msh",
                        "--size-factor", "1.5"] + GEO + LOOP,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{TAG}.msh").exists():
        sys.exit(f"mesh failed: {(r.stdout + r.stderr)[-200:]}")
    m = solveconf.load_meta(f"{TAG}.msh")
    print(f"  ONE mesh: {m['tets']:,} el, port {m['attributes'].get('port')}, "
          f"loop tilt {m.get('loop_tilt_deg')}° phi {m.get('loop_phi_deg')}°\n",
          flush=True)
    EX = ph.spectrum(A_MM, L_MM, fmax=3.2)
    res = {}

    diag = {}
    for order in (1, 2):
        t = f"{TAG}_eig{order}"
        c = eigen_cfg(t, m, mesh=f"{TAG}.msh", n=8, target=2.40)
        c["Solver"]["Order"] = order
        print(f"  eigenmode order {order}", flush=True)
        run(t, c)
        v = eig(t)
        pick = min(v, key=lambda x: abs(x - EX["TE011"]))
        res[f"eig{order}"] = pick
        journal.log(TAG, event="pick", kind="eigenmode", order=order,
                    f_ghz=pick, **diag[f"eig{order}"])
        diag[f"eig{order}"] = {"n_modes": len(v),
                               "nearest3": [round(x, 5) for x in
                                            sorted(v, key=lambda x:
                                                   abs(x - EX["TE011"]))[:3]]}
        print(f"    picked {pick:.5f} from {len(v)} modes; nearest-3 "
              f"{diag[f'eig{order}']['nearest3']}", flush=True)

    for order in (1, 2):
        t = f"{TAG}_drv{order}"
        c, meta, dropped = solveconf.driven(f"{TAG}.msh", t, BAND, step=STEP,
                                            order=order)
        pathlib.Path(f"{t}.json").write_text(json.dumps(c, indent=2))
        print(f"  driven order {order}  band {BAND} step {STEP}", flush=True)
        run(t, c)
        recs = dq.load(t)
        if not recs:
            print(f"    🔴 {t}: no records — REPORTED as such, not skipped",
                  flush=True)
            res[f"drv{order}"] = None
            diag[f"drv{order}"] = {"error": "no records"}
            continue
        best = max(recs, key=lambda x: x.get("pe", 0) + x.get("pm", 0))
        res[f"drv{order}"] = best["f"]
        journal.log(TAG, event="pick", kind="driven", order=order,
                    f_ghz=best["f"])
        # the reader judges the mode pick, not the script: show the top three
        top = sorted(recs, key=lambda x: -(x.get("pe", 0) + x.get("pm", 0)))[:3]
        diag[f"drv{order}"] = {"n_samples": len(recs),
                               "top3_by_energy": [round(x["f"], 5) for x in top]}
        print(f"    picked {best['f']:.5f} from {len(recs)} samples; "
              f"top-3 by stored energy {[round(x['f'],5) for x in top]}",
              flush=True)

    print(f"\n{'':>12}{'order 1':>12}{'order 2':>12}{'OFFSET MHz':>13}"
          f"{'ord2 vs exact':>15}{'flag':>8}")
    for kind, lab in (("eig", "eigenmode"), ("drv", "driven")):
        a, b = res.get(f"{kind}1"), res.get(f"{kind}2")
        if a is None or b is None:
            print(f"{lab:>12}{str(a):>12}{str(b):>12}"
                  f"{'— incomplete, REPORTED':>36}")
            continue
        dev = 1e3 * (b - EX["TE011"])
        flag = "" if abs(dev) < 10 else "⚠️ >10MHz"
        print(f"{lab:>12}{a:>12.5f}{b:>12.5f}{1e3*(b-a):>13.2f}"
              f"{dev:>15.2f}{flag:>8}")
    print(f"\n  ⚠️ the flag marks a row for the READER's attention. Nothing is "
          f"withheld:\n     mode-pick diagnostics for every solve are in "
          f"e0k.result.json.")
    print(f"\n  exact TE011 (empty, no loop) = {EX['TE011']:.5f} GHz")
    print(f"\n  REFERENCE ROWS:")
    print(f"    old  DRIVEN    LOADED   offset +24.54  (R38)")
    print(f"    new  EIGENMODE EMPTY    offset +12.00  (E0g, no loop)")
    json.dump({"te011_exact": EX["TE011"], "picks": res,
               "mode_pick_diagnostics": diag},
              open("e0k.result.json", "w"), indent=1)
    print("\n  wrote e0k.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
