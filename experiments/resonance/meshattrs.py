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
        for dim, tag in gmsh.model.getPhysicalGroups(3):
            name = gmsh.model.getPhysicalName(dim, tag)
            n = 0
            for ent in gmsh.model.getEntitiesForPhysicalGroup(dim, tag):
                types, tags, _ = gmsh.model.mesh.getElements(dim, ent)
                n += sum(len(t) for t in tags)
            out[(tag, name)] = n
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
        for (tag, name), n in sorted(c.items()):
            mark = "   🔴 EMPTY — a material bound here solves nothing" if n == 0 else ""
            print(f"    attribute {tag:>3}  {name or '(unnamed)':<16} "
                  f"{n:>8,} elements{mark}")
        print(f"    total {sum(c.values()):,}")


if __name__ == "__main__":
    main()
