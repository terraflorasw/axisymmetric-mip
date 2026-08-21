"""HOW BIG is the mesher's node jitter, and WHICH nodes move?

"12 um" was the first differing node I happened to print; the next three were
0.5, 5.0 and 0.07 um. A single sample is not a magnitude. This measures the
distribution, and tests the obvious hypothesis:

  geometric order 1 is bit-identical, so the CORNER nodes are reproducible.
  Order 2 adds mid-edge nodes, projected onto the OCC surfaces. If only those
  move, the jitter is a surface-projection tolerance, not a mesher-wide
  instability -- and its size is then a property of that tolerance.

VERIFICATION   the count of moved nodes should match the count of nodes ADDED
               by going from order 1 to order 2 (the mid-edge nodes), and moved
               nodes should sit at ~the cavity radius (on the curved wall), not
               scattered through the volume.
FALSIFICATION  if interior nodes move too, or if the moved count exceeds the
               mid-edge count, the projection hypothesis is wrong.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshdet
from e0_solver_vs_math import GEO
from e0k_driven_vs_eigen import LOOP

ARGS = list(GEO) + list(LOOP) + ["--size-factor", "1.5"]


def nodes(path):
    """{id: (x,y,z)} from a v2.2 msh."""
    out, it = {}, iter(open(path))
    for line in it:
        if line.strip() == "$Nodes":
            n = int(next(it))
            for _ in range(n):
                p = next(it).split()
                out[int(p[0])] = (float(p[1]), float(p[2]), float(p[3]))
            break
    return out


def main():
    py = sys.executable
    print(__doc__)
    o1 = "_nj_o1.msh"
    a, b = "_nj_a.msh", "_nj_b.msh"
    args1 = [x for x in ARGS]
    i = args1.index("--order"); args1[i + 1] = "1"
    meshdet.one(py, args1, 1, 0, o1)
    meshdet.one(py, ARGS, 1, 0, a)
    meshdet.one(py, ARGS, 1, 1, b)

    n1, na, nb = nodes(o1), nodes(a), nodes(b)
    print(f"  order-1 nodes: {len(n1):,}")
    print(f"  order-2 nodes: {len(na):,}  (mid-edge added: {len(na)-len(n1):,})")

    common = set(na) & set(nb)
    d = []
    for k in common:
        p, q = na[k], nb[k]
        d.append((math.dist(p, q), k, math.hypot(p[0], p[1]), p[2]))
    d.sort(reverse=True)
    moved = [x for x in d if x[0] > 0]
    print(f"  nodes compared: {len(common):,}   moved: {len(moved):,} "
          f"({100*len(moved)/max(len(common),1):.1f}%)")
    if not moved:
        print("  ✅ no node moved")
        return 0
    mags = [x[0] for x in moved]
    mags.sort()
    def pct(p): return mags[min(len(mags)-1, int(p*len(mags)))]
    print(f"\n  displacement (um):  max {mags[-1]*1e6:9.2f}"
          f"   p99 {pct(0.99)*1e6:8.2f}   median {pct(0.5)*1e6:8.3f}"
          f"   min {mags[0]*1e6:8.4f}")
    rms = math.sqrt(sum(m*m for m in mags)/len(mags))
    print(f"  rms {rms*1e6:.3f} um")

    # where are the movers? r ~ cavity radius means the curved wall.
    rs = sorted(x[2] for x in moved)
    print(f"\n  radial position of moved nodes (mm): "
          f"min {rs[0]*1e3:.1f}  median {rs[len(rs)//2]*1e3:.1f}  "
          f"max {rs[-1]*1e3:.1f}")
    print(f"  cavity radius = 103.70 mm, loop is at r ~ 90-104 mm")
    inner = [r for r in rs if r < 0.080]
    print(f"  moved nodes at r < 80 mm (interior, away from the wall): "
          f"{len(inner):,} of {len(moved):,}")
    # 🔑 THE DECISIVE SPLIT: are the movers CORNER nodes or mid-edge nodes?
    # In a v2.2 msh gmsh numbers the order-1 vertices first, so ids <= len(n1)
    # are corners. If corners move, the base tet mesh is non-deterministic in
    # POSITION while identical in TOPOLOGY -- a different and worse fault than
    # a high-order projection tolerance, and it would contradict order-1 builds
    # being bit-identical.
    ncorner = len(n1)
    corner_moved = [x for x in moved if x[1] <= ncorner]
    mid_moved = [x for x in moved if x[1] > ncorner]
    print(f"\n  movers that are CORNER nodes (id <= {ncorner:,}): "
          f"{len(corner_moved):,}")
    print(f"  movers that are MID-EDGE nodes: {len(mid_moved):,}")
    if corner_moved:
        cm = sorted(x[0] for x in corner_moved)
        print(f"    corner displacement (um): max {cm[-1]*1e6:.2f}  "
              f"median {cm[len(cm)//2]*1e6:.3f}")
        print("    🔴 the LINEAR mesh is position-unstable, not just the "
              "high-order pass")
    else:
        print("    ✅ every mover is a mid-edge node — the linear mesh is stable")
    # do the order-1 corners match the order-2 corners?
    shared = [k for k in n1 if k in na]
    dc = [math.dist(n1[k], na[k]) for k in shared]
    dc.sort()
    print(f"\n  order-1 build vs order-2 build, shared ids ({len(shared):,}): "
          f"max {dc[-1]*1e6:.3f} um, median {dc[len(dc)//2]*1e6:.4f} um")

    n_mid = len(na) - len(n1)
    print(f"\n  moved {len(moved):,} vs mid-edge nodes added {n_mid:,} "
          f"({100*len(moved)/max(n_mid,1):.1f}% of them)")
    for f in (o1, a, b):
        pathlib.Path(f).unlink(missing_ok=True)
        pathlib.Path(f).with_suffix(".meta.json").unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
