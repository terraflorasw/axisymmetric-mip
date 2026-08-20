"""E0e — is it the MESHER or the SOLVER? A decisive separation.

E0b/E0c found frequencies moving by up to 4 MHz, and an exactly-degenerate pair
splitting 6x further apart, under a RIGID TRANSLATION — which is an exact
symmetry of Maxwell. The correct answer is ZERO. Calling that "about one noise
floor" is normalising a failed exact test, which is what I did and should not
have.

🔑 THE TWO CANDIDATES CAN BE SEPARATED EXACTLY.

  MESHER   gmsh is not translation-equivariant: re-meshing a moved solid gives a
           DIFFERENT discretisation (83,322 vs 83,809 tets). Different mesh,
           different error. Expected in kind; the question is magnitude.

  SOLVER   if Palace/MFEM's answer depends on absolute coordinates at all, that
           is a genuine defect: the discrete problem should be identical.

TO SEPARATE THEM, TRANSLATE THE MESH ITSELF, NOT THE GEOMETRY. Take the exact
mesh already solved at the origin and add 256 mm to every node coordinate.
Identical topology, identical connectivity, identical element shapes, identical
quality — ONLY the absolute coordinates differ.

    result == origin result   ->  the solver is exactly translation-invariant,
                                  and 100% of E0b's shift is gmsh re-meshing
    result != origin result   ->  the SOLVER is coordinate-dependent. That is a
                                  bug, and every number this project has ever
                                  produced is downstream of it

VERIFICATION   physics.spectrum(), unchanged.
FALSIFICATION  the degenerate pair's splitting, true value exactly 0, compared
               against the 1.199 MHz measured on this very mesh at the origin.
GATE           the shifted mesh must have the SAME element count and the same
               node count as its parent. If it does not, the transform did more
               than translate and the test is void.
"""
import json
import pathlib
import sys

import gmsh

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
from e0_solver_vs_math import A_MM, L_MM, eigen_cfg, run, eig

SRC, DST, D = "e0b_at0", "e0e_shift", 0.256

print(__doc__)
print("=" * 78, flush=True)

gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 0)
# 🔴 geometry.py writes MSH 2.2; gmsh.write defaults to 4.1 and
# MFEM then aborts with "vertex index doesn't exist". Match the
# parent exactly — the whole point is that ONLY coordinates differ.
gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
gmsh.merge(f"{SRC}.msh")
tags0, coords0, _ = gmsh.model.mesh.getNodes()
n_el0 = sum(len(t) for _d, ts in [(3, gmsh.model.mesh.getElementsByType(11))]
            for t in [ts[0]])
gmsh.model.mesh.affineTransform([1, 0, 0, D,
                                 0, 1, 0, D,
                                 0, 0, 1, D])
tags1, coords1, _ = gmsh.model.mesh.getNodes()
n_el1 = len(gmsh.model.mesh.getElementsByType(11)[0])
gmsh.write(f"{DST}.msh")
gmsh.finalize()

print(f"  nodes {len(tags0):,} -> {len(tags1):,}   order-2 tets "
      f"{n_el0:,} -> {n_el1:,}")
moved = [coords1[i] - coords0[i] for i in range(0, 9, 1)]
print(f"  first three node deltas: {[round(m, 6) for m in moved[:9]]}")
if len(tags0) != len(tags1) or n_el0 != n_el1:
    sys.exit("🔴 the transform changed the mesh — test void")
if any(abs(m - D) > 1e-9 for m in moved):
    sys.exit(f"🔴 nodes did not move by exactly {D} m — test void")
print(f"  ✅ IDENTICAL DISCRETISATION, coordinates shifted by exactly {D} m\n",
      flush=True)

# reuse the parent's sidecar: same topology, same attributes
meta = solveconf.load_meta(f"{SRC}.msh")
cfg = eigen_cfg(DST, meta, mesh=f"{DST}.msh")
run(DST, cfg)

EX = ph.spectrum(A_MM, L_MM)
a, b = eig(SRC), eig(DST)
print(f"\n  {SRC}: {len(a)} modes    {DST}: {len(b)} modes")
print(f"\n{'i':>3}{'origin':>13}{'nodes+256mm':>14}{'Δ MHz':>12}")
ds = []
for i, (x, y) in enumerate(zip(a, b)):
    ds.append(1e3 * (y - x))
    print(f"{i:>3}{x:>13.7f}{y:>14.7f}{1e3*(y-x):>12.6f}")
print(f"\n  max |Δ| = {max(abs(v) for v in ds):.6f} MHz")
for tag, v in ((SRC, a), (DST, b)):
    n = sorted(v, key=lambda x: abs(x - EX["TE011"]))[:2]
    print(f"  degeneracy splitting, {tag}: {1e3*abs(n[1]-n[0]):.6f} MHz")
json.dump({"origin": a, "shifted": b, "delta_mhz": ds},
          open("e0e.result.json", "w"), indent=1)
print("\n  wrote e0e.result.json — NO VERDICT HERE", flush=True)
