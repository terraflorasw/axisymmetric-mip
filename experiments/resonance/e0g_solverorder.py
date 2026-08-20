"""E0g — it was never the geometry. Raise the SOLVER order.

E0f swept the GEOMETRIC order at fixed everything else and the falsifier fired:

    mode     ord 1     ord 2     ord 3
    TE011  -10.292   -11.998   -11.986      <- order 2 -> 3 moves it 0.012 MHz
    TM020  -11.074   -14.423   -14.452
    TM210  -13.457   -16.625   -16.648
    splitting 1.221     1.199     1.200

🔴 GEOMETRIC ORDER 2 IS ALREADY CONVERGED. Cubic elements change nothing —
0.01-0.03 MHz. So the residual is NOT the mesh failing to follow the cylinder,
and the racing-sim analogy, though exactly right about the mechanism it names,
DOES NOT GOVERN HERE. My prediction that order 3 would collapse the error was
wrong, and E0f's declared falsifier says what that means: the error is in the
FIELD BASIS, not the geometry.

⚠️ Also wrong: I argued an inscribed polygon reads small so frequencies come out
HIGH. At geometric order 1 the signs are MIXED (TM011 +0.380, TE211 +0.627,
TM211 +1.372, but TE011 -10.292). A straight-sided tetrahedral tiling is not a
simple inscribed polygon and that intuition does not survive contact.

🔑 AND THE OLD PROGRAMME HAD THE RIGHT KNOB ALL ALONG. Its `offset.te011 =
+24.54 MHz` was measured as SOLVER order 1 -> 2 on one mesh. It was treated as a
fudge constant to be added; E0f says it is the dominant physical error term.

PREDICTION, DECLARED BEFORE THE RUN:

    TE011 sits -11.99 MHz low at solver order 1. If the field basis is the whole
    residual, SOLVER ORDER 2 SHOULD LAND IT NEAR ZERO -- moving it UP by ~12 MHz.

🔴 FALSIFIER: if order 2 overshoots, or leaves a residual larger than the ~1.2 MHz
mesh-realisation floor, then something ELSE is contributing and neither
discretisation explains it. And if the DEGENERACY SPLITTING does not shrink, the
splitting is not a discretisation artifact at all — it would then be a property of
the tetrahedral tiling's inability to represent the cavity's continuous azimuthal
symmetry, which no order of anything can fix.

VERIFICATION   physics.spectrum(), exact.
FALSIFICATION  splitting of the exactly-degenerate pair, true value 0.
"""
import hashlib
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
from e0_solver_vs_math import A_MM, L_MM, build, eigen_cfg, run, eig

SOLVER_ORDERS = [1, 2, 3]
MESH = "e0g"

print(__doc__)
print("=" * 78, flush=True)
EX = ph.spectrum(A_MM, L_MM)
DEG = [("TE011", "TM111")]

meta, fac = build(MESH)          # ONE mesh, geometric order 2 (converged)
print(f"    md5 {hashlib.md5(pathlib.Path(f'{MESH}.msh').read_bytes()).hexdigest()[:12]}",
      flush=True)
print("  🔑 ONE MESH for all three — solver order is a config setting, so this "
      "is a\n     SAME-MESH comparison and mesh-realisation error cancels "
      "exactly.\n", flush=True)

res = {}
for o in SOLVER_ORDERS:
    tag = f"e0g_s{o}"
    cfg = eigen_cfg(tag, meta, mesh=f"{MESH}.msh")
    cfg["Solver"]["Order"] = o
    assert cfg["Solver"]["Order"] == o
    print(f"  solver order {o}", flush=True)
    run(tag, cfg)
    res[tag] = eig(tag)

print(f"\nΔ from EXACT, MHz — one mesh, geometric order 2, solver order varied\n")
print(f"{'mode':>7}{'exact':>11}" + "".join(f"{'solver ' + str(o):>12}"
                                            for o in SOLVER_ORDERS))
for k, fx in sorted(EX.items(), key=lambda kv: kv[1]):
    row = []
    for o in SOLVER_ORDERS:
        p, _r = ph.match_exact(EX, res[f"e0g_s{o}"], DEG)
        row.append(f"{1e3*(p[k]-fx):>12.3f}" if k in p else f"{'—':>12}")
    print(f"{k:>7}{fx:>11.5f}" + "".join(row))

print(f"\n  🔑 FALSIFIER — TE011/TM111 splitting, true value EXACTLY 0:")
for o in SOLVER_ORDERS:
    v = res[f"e0g_s{o}"]
    n = sorted(v, key=lambda x: abs(x - EX["TE011"]))[:2]
    print(f"    solver order {o}:  {1e3*abs(n[1]-n[0]):8.3f} MHz")
print(f"\n  reference: mesh-realisation floor is ~1.2 MHz on this mesh "
      f"(E0e), and 1.2-7.1 MHz across realisations (E0b).")

json.dump({"exact": EX, **res, "mesh": MESH, "solver_orders": SOLVER_ORDERS,
           "tets": meta["tets"]}, open("e0g.result.json", "w"), indent=1)
print("\n  wrote e0g.result.json — NO VERDICT HERE", flush=True)
