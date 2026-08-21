"""Is a mesh hash difference REAL geometry, or a header artifact?

E0m found two identical serial gmsh commands producing different SHA-256 with
the SAME tet count. Before that can be called non-determinism, it has to be
shown that the bytes which differ are NODES and ELEMENTS, not a timestamp or a
filename embedded in the header. Same count + different bytes is precisely what
a trivial header difference looks like.

VERIFICATION   locate the first differing line and say which $Section it is in.
FALSIFICATION  if every difference is outside $Nodes/$Elements, the meshes are
               geometrically identical and E0m's verdict is an artifact.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshdet
from e0_solver_vs_math import GEO
from e0k_driven_vs_eigen import LOOP

GEOARGS = list(GEO) + list(LOOP) + ["--size-factor", "1.5"]


def sections(path):
    """line index -> section name, by walking $Section markers."""
    out, cur = [], "(header)"
    for line in open(path):
        s = line.strip()
        if s.startswith("$End"):
            out.append(cur); cur = "(between)"
        elif s.startswith("$"):
            cur = s[1:]; out.append(cur)
        else:
            out.append(cur)
    return out


def main():
    py = sys.executable
    a, b = "_md_a.msh", "_md_b.msh"
    print(__doc__)
    for out in (a, b):
        dt, h, n = meshdet.one(py, GEOARGS, 1, 0, out)
        print(f"  {out}: {dt:.1f}s  {n:,} tets  sha {h[:16]}")

    la = open(a).read().splitlines()
    lb = open(b).read().splitlines()
    print(f"\n  line counts: {len(la):,} vs {len(lb):,}")
    sa = sections(a)

    diffs = [i for i, (x, y) in enumerate(zip(la, lb)) if x != y]
    if not diffs and len(la) == len(lb):
        print("  ✅ files are line-identical — the hash difference was not real")
        return 0
    print(f"  differing lines: {len(diffs):,} of {min(len(la), len(lb)):,}")
    bysec = {}
    for i in diffs:
        bysec[sa[i] if i < len(sa) else "?"] = bysec.get(
            sa[i] if i < len(sa) else "?", 0) + 1
    print("  differences by section:")
    for k, v in sorted(bysec.items(), key=lambda x: -x[1]):
        print(f"    {k:<16} {v:,}")
    for i in diffs[:4]:
        sec = sa[i] if i < len(sa) else "?"
        print(f"\n  first diff @ line {i+1} (section {sec}):")
        print(f"    a: {la[i][:96]}")
        print(f"    b: {lb[i][:96]}")
    geo = {k: v for k, v in bysec.items() if k in ("Nodes", "Elements")}
    print()
    if geo:
        print(f"  🔴 REAL: {sum(geo.values()):,} differing lines are in "
              f"{sorted(geo)} — the geometry itself differs")
    else:
        print("  ✅ ARTIFACT: nothing differs inside $Nodes/$Elements")
    for f in (a, b):
        pathlib.Path(f).unlink(missing_ok=True)
        pathlib.Path(f).with_suffix(".meta.json").unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
