"""WHICH meshing stage is non-deterministic? Serial gmsh is not reproducible.

Two identical serial commands differ in 2,540 node COORDINATES with identical
topology. Topology fixed + positions moving points at a node-moving stage:
either the high-order optimiser (HighOrderOptimize=2, 25 passes, 200 iters) or
the linear smoother.

VERIFICATION   build the same geometry twice at each setting and hash it.
FALSIFICATION  if geometric order 1 (no high-order pass at all) is reproducible
               while order 2 is not, the high-order optimiser is the source.
               If order 1 also varies, the source is upstream of it.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshdet
from e0_solver_vs_math import GEO
from e0k_driven_vs_eigen import LOOP

BASE = [g for g in (list(GEO) + list(LOOP)) if g not in ("--order",)]
# strip the geometric order pair from GEO so we can vary it
_clean = []
skip = False
for g in list(GEO) + list(LOOP):
    if skip:
        skip = False
        continue
    if g == "--order":
        skip = True
        continue
    _clean.append(g)
SF = ["--size-factor", "1.5"]
CASES = [("order 1              ", _clean + ["--order", "1"] + SF),
         ("order 2, ho-opt 2    ", _clean + ["--order", "2"] + SF
          + ["--ho-optimize", "2"]),
         ("order 2, ho-opt 0    ", _clean + ["--order", "2"] + SF
          + ["--ho-optimize", "0"]),
         ("order 2, ho-opt 1    ", _clean + ["--order", "2"] + SF
          + ["--ho-optimize", "1"])]


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    for label, args in CASES:
        hs = []
        for r in range(2):
            out = f"_ms_{r}.msh"
            dt, h, n = meshdet.one(sys.executable, args, 1, r, out)
            hs.append(h)
            print(f"  {label}  rep {r}: {dt:6.1f}s  {n:>8,} tets  {h[:16]}",
                  flush=True)
            pathlib.Path(out).unlink(missing_ok=True)
            pathlib.Path(out).with_suffix(".meta.json").unlink(missing_ok=True)
        same = hs[0] == hs[1]
        print(f"  {label}: {'✅ REPRODUCIBLE' if same else '🔴 VARIES'}\n",
              flush=True)


if __name__ == "__main__":
    main()
