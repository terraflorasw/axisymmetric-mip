"""E0f — is the error GEOMETRIC? Raise the mesh's geometric order.

The user's analogy, and it names the mechanism precisely:

    "If the driving physics operate on the polygons, then you get hard seams
     that upset the car, unnaturally. The driving simulation has to happen on
     the analog curve of the driving surface, not the mesh derived from it."

🔑 FEM HAS TWO SEPARATE DISCRETISATIONS AND THEY ARE ROUTINELY CONFLATED:

    GEOMETRIC ORDER   how closely the elements follow the TRUE cylinder
    SOLVER ORDER      how well the basis represents E and H on those elements

The seam problem is the FIRST one. Curved isoparametric elements are the partial
fix; isogeometric analysis — using the CAD spline basis directly as the FEM basis
— is the full version of "simulate on the analytic curve, not the mesh".

🔢 AND THE SIGN IS THE CLUE. A straight-chorded cylinder INSCRIBES the true one,
so it reads too SMALL and frequencies come out HIGH:

    48 segments around the circumference -> sagitta 222 um -> TE011 +5.24 MHz

But E0 measured every mode LOW (TE011 -12.0 MHz) at geometric order 2. So the
quadratic elements are not merely failing to reach the circle — they appear to
OVERSHOOT it, making the cavity effectively LARGER. That is a specific, physical
claim about element curvature and it is testable.

PREDICTION, DECLARED BEFORE THE RUN:

    order 1   |Δ| large and POSITIVE (inscribed polygon, cavity too small)
    order 2   |Δ| smaller but NEGATIVE (overshoot)
    order 3   |Δ| collapses toward zero
    order 4   |Δ| negligible

🔴 FALSIFIER: if |Δ| PLATEAUS at order 2 instead of collapsing, the residual is
NOT geometric — it is the field basis (solver order 1), and raising geometric
order further is wasted. That would refute the analogy's applicability here, and
the fix would be solver order, not element curvature.

⚠️ SOLVER ORDER IS HELD AT 1 THROUGHOUT so that only the geometry varies.
⚠️ SIZE FACTOR IS HELD FIXED so element COUNT is roughly constant — this is not
   a refinement study, it is a representation study.

VERIFICATION   physics.spectrum(), exact.
FALSIFICATION  the exactly-degenerate TE011/TM111 splitting. If it is geometric,
               it should collapse with order too.
GATE           meshes pairwise distinct; every exact mode below the solved
               ceiling; one-to-one matching (physics.match_exact).
"""
import hashlib
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
from e0_solver_vs_math import A_MM, L_MM, GEO, build, eigen_cfg, run, eig

ORDERS = [1, 2, 3]
CASES = [(f"e0f_o{o}", ["--order", str(o)]) for o in ORDERS]

print(__doc__)
print("=" * 78, flush=True)
EX = ph.spectrum(A_MM, L_MM)
DEG = [("TE011", "TM111")]

info = {}
for tag, extra in CASES:
    # build() passes GEO which already contains --order 2; the LAST occurrence
    # wins in argparse, so the per-case override is appended after it.
    m, fac = build(tag, extra)
    h = hashlib.md5(pathlib.Path(f"{tag}.msh").read_bytes()).hexdigest()[:12]
    info[tag] = (m, h)
    print(f"    md5 {h}  mesh_order {m.get('mesh_order')}", flush=True)

hs = {t: h for t, (_m, h) in info.items()}
if len(set(hs.values())) != len(CASES):
    sys.exit("🔴 identical meshes across geometric orders — NOT solving.")
print(f"  ✅ {len(CASES)} distinct meshes\n", flush=True)

for tag, _e in CASES:
    run(tag, eigen_cfg(tag, info[tag][0]))
res = {t: eig(t) for t, _e in CASES}

print(f"\nΔ from EXACT, MHz — solver order held at 1, size factor held fixed\n")
print(f"{'mode':>7}{'exact':>11}" + "".join(f"{'ord ' + str(o):>11}"
                                            for o in ORDERS))
for k, fx in sorted(EX.items(), key=lambda kv: kv[1]):
    row = []
    for t, _e in CASES:
        p, r = ph.match_exact(EX, res[t], DEG)
        row.append(f"{1e3*(p[k]-fx):>11.3f}" if k in p else f"{'—':>11}")
    print(f"{k:>7}{fx:>11.5f}" + "".join(row))

print(f"\n{'':>18}" + "".join(f"{info[t][0]['tets']:>11,}" for t, _e in CASES)
      + "   elements")
print(f"\n  🔑 FALSIFIER — TE011/TM111 splitting, true value EXACTLY 0:")
for t, _e in CASES:
    n = sorted(res[t], key=lambda x: abs(x - EX["TE011"]))[:2]
    print(f"    geometric order {t[-1]}:  {1e3*abs(n[1]-n[0]):8.3f} MHz")

json.dump({"exact": EX, **res, "md5": hs, "orders": ORDERS,
           "tets": {t: info[t][0]["tets"] for t, _e in CASES}},
          open("e0f.result.json", "w"), indent=1)
print("\n  wrote e0f.result.json — NO VERDICT HERE", flush=True)
