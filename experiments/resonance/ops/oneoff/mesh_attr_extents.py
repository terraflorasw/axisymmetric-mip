import sys, gmsh, math
gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0)
gmsh.open(sys.argv[1])
a = 88.004517
print("  physical groups present:", gmsh.model.getPhysicalGroups())
for dim, tag in gmsh.model.getPhysicalGroups():
    if dim != 2:
        continue
    nt, nc = gmsh.model.mesh.getNodesForPhysicalGroup(dim, tag)[:2]
    if len(nc) == 0:
        continue
    xs, ys, zs = nc[0::3]*1e3, nc[1::3]*1e3, nc[2::3]*1e3
    r = [math.hypot(x, y) for x, y in zip(xs, ys)]
    print("  dim2 attr %2d : %6d nodes   r %8.4f..%8.4f   z %8.4f..%8.4f"
          % (tag, len(r), min(r), max(r), min(zs), max(zs)))
gmsh.finalize()
