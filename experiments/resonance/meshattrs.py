"""Which volume attributes does a mesh ACTUALLY contain, and how many elements?

🔴 WHY. `solveconf`'s own rule is that binding a material to an attribute the
mesh lacks "describes a model it is not solving" — and it enforces that for the
brake (attr 8) and upstream (attr 11) by checking whether the sidecar reports
them as None. But `--no-torch` leaves `attrs["torch"] = 2` regardless, so the
torch's material (including its LOSS TANGENT) is bound whether or not a single
element carries that attribute.

The sidecar cannot answer this. The MESH can. Ask it.

    ops/go ops/runthere.sh meshattrs.py e0k2.msh
"""
import sys
import collections


def counts(path):
    import gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    try:
        gmsh.open(path)
        out = collections.Counter()
        for dim, tag in gmsh.model.getPhysicalGroups(2) + gmsh.model.getPhysicalGroups(3):
            name = gmsh.model.getPhysicalName(dim, tag)
            n = 0
            for ent in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
                types, tags, _ = gmsh.model.mesh.getElements(dim, ent)
                n += sum(len(t) for t in tags)
            out[(dim, tag, name)] = n
        return out
    finally:
        gmsh.finalize()


def main():
    if len(sys.argv) < 2:
        raise SystemExit("usage: meshattrs.py <mesh.msh>")
    for path in sys.argv[1:]:
        print(f"\n  {path}")
        c = counts(path)
        if not c:
            print("    🔴 no 3-D physical groups found")
            continue
        for (dim, tag, name), n in sorted(c.items()):
            mark = "   🔴 EMPTY — a material bound here solves nothing" if n == 0 else ""
            if dim == 2 and n < 10:
                mark = f"   🔴 ONLY {n} ELEMENTS — surface is UNRESOLVED"
            print(f"    {dim}D attr {tag:>3}  {name or '(unnamed)':<16} "
                  f"{n:>8,} elements{mark}")
        print(f"    total 3D {sum(v for (d,_t,_n),v in c.items() if d==3):,}")


if __name__ == "__main__":
    main()
