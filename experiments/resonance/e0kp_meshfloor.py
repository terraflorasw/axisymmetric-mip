"""E0kp — the REPRODUCIBILITY FLOOR of the whole instrument.

E0m: two IDENTICAL serial gmsh commands produce different order-2 meshes —
~2,540 node coordinates apart (~12 um), identical topology. Localised to
setOrder(2) (high-order node placement); geometric order 1 is bit-identical, and
disabling HighOrderOptimize does not help. It is not reachable by a flag.

So the question is not "is the mesher deterministic" — it is not — but HOW MUCH
FREQUENCY that costs. That number is the floor under every comparison this
programme makes between results that do not share a mesh FILE.

  N independent meshes, same command, same solver, same order.
  The SPREAD in TE011 is the floor.

VERIFICATION   all N meshes must have identical topology (same tet count); if
               they do not, the variation is coarser than node jitter and this
               measures something else.
FALSIFICATION  if the spread is comparable to the 1.3-3.3 MHz "cross-mesh error"
               already in the record, then that error was never about differing
               MESH PARAMETERS — it is irreducible mesher noise, and every
               cross-mesh comparison ever made carries it.

⚠️ This does not threaten same-mesh differencing (METHODOLOGY 2b), which reuses
one FILE. It sets the price of NOT doing that.
"""
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshdet
import physics as ph
import solveconf
from e0_solver_vs_math import A_MM, L_MM, GEO, eigen_cfg, run, eig
from e0k_driven_vs_eigen import LOOP

N = 3
GEOARGS = list(GEO) + list(LOOP) + ["--size-factor", "1.5"]
TAG = "e0kp"


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    ex = ph.spectrum(A_MM, L_MM, fmax=3.2)["TE011"]
    print(f"  exact TE011 (no loop) = {ex:.6f} GHz\n", flush=True)

    rows = []
    for i in range(N):
        mesh = f"{TAG}_{i}.msh"
        dt, sha, tets = meshdet.one(sys.executable, GEOARGS, 1, i, mesh)
        m = solveconf.load_meta(mesh)
        t = f"{TAG}_{i}"
        c = eigen_cfg(t, m, mesh=mesh, n=8, target=2.40)
        c["Solver"]["Order"] = 2
        run(t, c)
        v = eig(t)
        pick = min(v, key=lambda x: abs(x - ex))
        rows.append({"i": i, "mesh_sha256": sha, "tets": tets,
                     "mesh_seconds": round(dt, 1), "f": pick,
                     "all_modes": [round(x, 6) for x in sorted(v)]})
        print(f"  mesh {i}: {tets:,} tets  sha {sha[:16]}  ->  TE011 "
              f"{pick:.6f} GHz  ({1e3*(pick-ex):+.2f} MHz vs exact)", flush=True)

    fs = [r["f"] for r in rows]
    tets = {r["tets"] for r in rows}
    shas = {r["mesh_sha256"] for r in rows}
    spread = 1e3 * (max(fs) - min(fs))
    print("\n" + "=" * 78)
    print(f"  distinct meshes: {len(shas)} of {N}   topology: "
          f"{'IDENTICAL' if len(tets) == 1 else f'DIFFERS {sorted(tets)}'}")
    print(f"  TE011 spread over {N} identical commands = {spread:.3f} MHz")
    print(f"  recorded cross-mesh error for comparison   = 1.3 - 3.3 MHz")
    json.dump({"exact": ex, "n": N, "spread_mhz": spread, "rows": rows},
              open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
