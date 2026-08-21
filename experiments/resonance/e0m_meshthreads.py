"""E0m — is THREADED meshing reproducible, and does it produce the SAME mesh?

Meshing became the critical path once solves moved to 32 ranks (E1b: 10.6 min
meshing vs 9.4 min solving). gmsh here IS built with OpenMP, and
General.NumThreads has been 1 for every mesh this programme has ever built.

Run on E0k's EXACT geometry, so that if the parallel mesh differs, e0kp can
solve it and compare against E0k's serial-mesh numbers directly.

TWO SEPARATE QUESTIONS, and a thread count must pass both to be adopted:

  1. REPRODUCIBLE — repeats at the same thread count give an identical SHA-256.
     A racing mesher would make "same mesh" mean "same command line", and the
     whole error budget (METHODOLOGY 2b) rests on the stronger claim.
  2. IDENTICAL TO SERIAL — threads=N gives the same mesh as threads=1. A count
     can be perfectly repeatable and still produce a DIFFERENT mesh, which would
     put the 1.3-3.3 MHz cross-mesh error on every comparison with existing
     results.

FALSIFICATION  any hash difference between repeats at one thread count rules
               that count out outright. Passing (1) but failing (2) does NOT
               rule it out — it means adoption is a MESH CHANGE and must be
               re-baselined, which is what e0kp measures.

⚠️ Tet COUNT is not the test. Two meshes can share a tet count and place nodes
differently, and node placement is what the solver sees. Hash the file.
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshdet
from e0_solver_vs_math import GEO
from e0k_driven_vs_eigen import LOOP

THREADS = [1, 8, 32]
REPEATS = 2
SF = "1.5"
GEOARGS = list(GEO) + list(LOOP) + ["--size-factor", SF]


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    print(f"  geometry: {' '.join(GEOARGS)}\n", flush=True)
    rows = {}
    for t in THREADS:
        res = []
        for r in range(REPEATS):
            out = f"e0m_t{t}_r{r}.msh"
            dt, h, n = meshdet.one(sys.executable, GEOARGS, t, r, out)
            res.append((dt, h, n))
            print(f"  threads={t:<3} rep {r}: {dt:7.1f}s  {n:>8,} tets  {h[:16]}",
                  flush=True)
            for p in (out, str(pathlib.Path(out).with_suffix(".meta.json"))):
                pathlib.Path(p).unlink(missing_ok=True)
        same = len({h for _, h, _ in res}) == 1
        rows[t] = {"best_s": min(d for d, _, _ in res),
                   "reproducible": same, "sha": res[0][1], "tets": res[0][2],
                   "times": [round(d, 1) for d, _, _ in res]}
        print(f"  threads={t:<3} -> "
              f"{'REPRODUCIBLE' if same else '🔴 NOT REPRODUCIBLE'}"
              f"  best {rows[t]['best_s']:.1f}s\n", flush=True)

    base = rows[THREADS[0]]
    print("=" * 78)
    print(f"  {'threads':>8}{'best s':>10}{'speedup':>9}{'reproducible':>14}"
          f"{'same as serial':>16}")
    for t in THREADS:
        r = rows[t]
        r["same_as_serial"] = (r["sha"] == base["sha"])
        print(f"  {t:>8}{r['best_s']:>10.1f}{base['best_s']/r['best_s']:>8.2f}x"
              f"{('yes' if r['reproducible'] else 'NO'):>14}"
              f"{('yes' if r['same_as_serial'] else 'NO'):>16}")

    bad = [t for t in THREADS if not rows[t]["reproducible"]]
    diff = [t for t in THREADS if not rows[t]["same_as_serial"]]
    print()
    if bad:
        print(f"  🔴 NOT reproducible at {bad} — those counts are ruled out")
    else:
        print("  ✅ every thread count reproduced its own mesh exactly")
    if diff:
        print(f"  ⚠️ threads={diff} produce a DIFFERENT mesh from serial. "
              f"Repeatable, but adopting one is a MESH CHANGE — run e0kp to "
              f"measure whether it moves the physics.")
    else:
        print("  ✅ identical to the serial mesh — adoption changes no result")
    json.dump({"geometry": GEOARGS, "repeats": REPEATS, "rows":
               {str(k): v for k, v in rows.items()}},
              open("e0m.result.json", "w"), indent=1)
    print("\n  wrote e0m.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
