"""E0j — the cost/accuracy frontier. What is the CHEAPEST setting that is good enough?

Three timeouts in a row (e0h, e0i, and e0g's order 3) say the question was posed
backwards. I kept asking "how accurate can this be" and paying 3007 s per solve.
The engineering question is the other one:

    WHAT IS THE CHEAPEST CONFIGURATION THAT CLEARS A STATED ACCURACY TARGET?

🔑 AND THE TARGET COMES FROM THE PHYSICS, NOT FROM AMBITION. The quantities this
instrument must resolve:

    cold linewidth            2.34 MHz
    tuner settable range     23    MHz
    TM020 clearance         195    MHz

**1 MHz on TE011 is ample.** E0g reached 0.361 MHz and cost 50 minutes — three
times better than needed, at 34x the price of order 1.

🔑 THE LEVER IS THAT ORDER 2 TOLERATES A MUCH COARSER MESH. A shift-invert
eigensolve factorises (A - sigma*B) whatever N you ask for, so reducing the mode
count from 22 to 6 saved almost nothing (e0i still timed out). Element COUNT is
the cost, and a richer field basis needs fewer elements for the same accuracy.
E0g's 83,322 elements at order 2 were 3x more accurate than required.

    size factor   0.96   83,322 el   3007 s   0.361 MHz   (E0g, the reference)
    this run       2.0 / 2.5 / 3.0, coarse, order 2

PREDICTION, DECLARED BEFORE THE RUN: order 2 on a ~10-15k element mesh clears
1 MHz in under two minutes — cheaper AND more accurate than order 1 on 83k
elements, which took 89 s to be 12 MHz wrong.

🔴 FALSIFIER: if accuracy degrades faster than ~h^2 as the mesh coarsens, the
order-2 advantage does not transfer to coarse meshes and the frontier is flat —
meaning there is no cheap accurate setting and every future run costs 50 minutes.

VERIFICATION   physics.spectrum(), exact.
FALSIFICATION  the exactly-degenerate splitting, true value 0, at each size.
"""
import hashlib
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
from e0_solver_vs_math import A_MM, L_MM, GEO, eigen_cfg, run, eig
import subprocess

SIZES = ["3.0", "2.5", "2.0", "1.5"]
TARGET_MHZ = 1.0

print(__doc__)
print("=" * 78, flush=True)
EX = ph.spectrum(A_MM, L_MM)
DEG = [("TE011", "TM111")]

rows = []
for sf in SIZES:
    tag = f"e0j_sf{sf.replace('.', 'p')}"
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--size-factor", sf] + GEO, capture_output=True,
                       text=True)
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        print(f"  sf {sf}: mesh FAILED, skipped", flush=True)
        continue
    m = solveconf.load_meta(f"{tag}.msh")
    cfg = eigen_cfg(tag, m, n=22, target=1.05)
    cfg["Solver"]["Order"] = 2
    print(f"  sf {sf}: {m['tets']:,} elements", flush=True)
    t0 = time.time()
    try:
        run(tag, cfg)
    except Exception as e:
        print(f"    🔴 {str(e)[:90]}", flush=True)
        continue
    dt = time.time() - t0
    v = eig(tag)
    p, _r = ph.match_exact(EX, v, DEG)
    mx = max(abs(1e3 * (p[k] - EX[k])) for k in p)
    te = 1e3 * (p["TE011"] - EX["TE011"]) if "TE011" in p else float("nan")
    n2 = sorted(v, key=lambda x: abs(x - EX["TE011"]))[:2]
    sp = 1e3 * abs(n2[1] - n2[0])
    rows.append((sf, m["tets"], dt, te, mx, sp))
    print(f"    {dt:5.0f}s   TE011 {te:+7.3f} MHz   max|Δ| {mx:6.3f}   "
          f"splitting {sp:6.3f}", flush=True)

print(f"\n{'sf':>6}{'elements':>10}{'seconds':>9}{'TE011 MHz':>11}"
      f"{'max|Δ|':>9}{'splitting':>11}{'verdict':>12}")
for sf, n, dt, te, mx, sp in rows:
    ok = abs(te) <= TARGET_MHZ
    print(f"{sf:>6}{n:>10,}{dt:>9.0f}{te:>11.3f}{mx:>9.3f}{sp:>11.3f}"
          f"{'✅ clears 1 MHz' if ok else '🔴 misses':>12}")
print(f"\n  reference — E0g: sf 0.96, 83,322 el, 3007 s, TE011 +0.058, "
      f"max 0.361, splitting 0.014")
print(f"  reference — order 1: sf 0.96, 83,322 el, 89 s, TE011 -11.998, "
      f"max 16.625, splitting 1.199")
ok = [r for r in rows if abs(r[3]) <= TARGET_MHZ]
if ok:
    best = min(ok, key=lambda r: r[2])
    print(f"\n  🔑 CHEAPEST SETTING CLEARING {TARGET_MHZ} MHz: sf {best[0]}, "
          f"{best[1]:,} elements, {best[2]:.0f} s")
    print(f"     that is {3007/best[2]:.0f}x cheaper than E0g and "
          f"{abs(11.998/best[3]):.0f}x more accurate than order 1")
json.dump({"target_mhz": TARGET_MHZ, "rows": rows}, open("e0j.result.json", "w"),
          indent=1)
print("\n  wrote e0j.result.json — NO VERDICT HERE", flush=True)
