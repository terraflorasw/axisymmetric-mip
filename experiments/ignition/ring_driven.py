#!/usr/bin/env python3
"""Ring (MICAP-like dielectric resonator) with a coupling loop + lumped port.

R5. The ring's Q was previously reported as 26,847 (wall) ∥ 44,655 (dielectric)
= 16,767. The dielectric half is Palace's own LossTan result and is sound; the
WALL half is a closed form, and R2 proved that whole family low by ~1.8×. This
builds the driven model needed to measure it the same way AMIP's was measured,
so the two stop being compared on unlike footings.

Deliberately a separate file from geometry.py: that one is the eigenmode ring
and is referenced by a settled result (Q × η = 47.5). Editing it in place would
put a closed finding at risk to answer an open one.

Port construction is copied verbatim from ../waveguide/geometry.py, including
the two failure modes it encodes:
  - the port face must TOUCH both conductor ends. Inset even 2% and it floats,
    drives nothing, and returns S11 varying 0.036 dB with NO error raised.
  - Direction must lie IN the port surface, not normal to it, or Palace aborts.

PEC is assigned TOPOLOGICALLY (faces bounding exactly one volume). The bbox rule
in geometry.py is correct for a bare enclosure but would silently miss the loop
surfaces, leaving them as a natural (PMC) boundary — wrong, and quiet about it.
"""

from __future__ import annotations

import argparse
import math
import sys

import gmsh

P = dict(
    ring_od=50.8e-3, ring_id=25.4e-3, ring_len=19.05e-3,
    ring_eps=9.8, ring_tand=1.0e-4,
    torch_od=20.0e-3, torch_wall=1.5e-3, torch_eps=3.78, torch_tand=1.0e-4,
    encl_dia=80.0e-3, encl_len=120.0e-3,
    ring_scale=0.94,
    elems_per_wl=8.0, edge_refine=0.4,
    # Coupling loop: z=0 plane, normal z-hat, outside the ring OD, linking the
    # axial return flux of the TE01d mode. Sized to fit the radial clearance.
    loop_d=8.0e-3, loop_w=5.0e-3, loop_rw=0.8e-3, loop_gap=0.25e-3,
)

C0 = 299_792_458.0
F0 = 2.45e9
TAG_PORT = 91


def mesh_size(eps_r, f, n):
    return C0 / (f * math.sqrt(eps_r)) / n


def build(p, out, msh_order):
    gmsh.initialize()
    gmsh.model.add("dr_ring_driven")
    occ = gmsh.model.occ

    s = p["ring_scale"]
    r_od, r_id, r_len = p["ring_od"] * s, p["ring_id"] * s, p["ring_len"] * s
    encl_r = p["encl_dia"] / 2.0
    z0 = -p["encl_len"] / 2.0

    clearance = encl_r - r_od / 2.0
    if p["loop_d"] >= clearance:
        sys.exit(f"ERROR: loop depth {p['loop_d']*1e3:.1f} mm exceeds the "
                 f"{clearance*1e3:.1f} mm clearance — it would intersect the ring.")

    encl = occ.addCylinder(0, 0, z0, 0, 0, p["encl_len"], encl_r)

    rz = -r_len / 2.0
    ring_o = occ.addCylinder(0, 0, rz, 0, 0, r_len, r_od / 2.0)
    ring_i = occ.addCylinder(0, 0, rz, 0, 0, r_len, r_id / 2.0)
    ring, _ = occ.cut([(3, ring_o)], [(3, ring_i)], removeObject=True, removeTool=True)

    t_ro = p["torch_od"] / 2.0
    t_ri = t_ro - p["torch_wall"]
    tube_o = occ.addCylinder(0, 0, z0, 0, 0, p["encl_len"], t_ro)
    tube_i = occ.addCylinder(0, 0, z0, 0, 0, p["encl_len"], t_ri)
    tube, _ = occ.cut([(3, tube_o)], [(3, tube_i)], removeObject=True, removeTool=True)

    bore = occ.addCylinder(0, 0, z0, 0, 0, p["encl_len"], t_ri)

    # --- coupling loop + port face, cut from the enclosure BEFORE fragmenting
    ld, lw, lrw, lg = p["loop_d"], p["loop_w"], p["loop_rw"], p["loop_gap"]
    xo, xi = encl_r + 2.0e-3, encl_r - ld
    segs = []
    for yy in (-lw, +lw):
        segs.append((3, occ.addCylinder(xo, yy, 0, xi - xo, 0, 0, lrw)))
    segs.append((3, occ.addCylinder(xi, -lw, 0, 0, lw - lg / 2, 0, lrw)))
    segs.append((3, occ.addCylinder(xi, lg / 2, 0, 0, lw - lg / 2, 0, lrw)))
    wire = occ.fuse([segs[0]], segs[1:])[0]
    encl_cut, _ = occ.cut([(3, encl)], wire, removeObject=True, removeTool=False)
    occ.remove(wire, recursive=True)

    # Rectangle spanning the gap, in the z=0 plane, Direction "+Y" along the wire.
    pf = occ.addRectangle(xi - 0.9 * lrw, -lg / 2, 0, 1.8 * lrw, lg)

    # One fragment, port face as a TOOL — not embed(), which refuses to make a
    # 2D face conformal with volumes it does not already touch.
    _, out_map = occ.fragment(encl_cut, ring + tube + [(3, bore), (2, pf)])
    occ.synchronize()

    def tags_of(i, dim=3):
        return {t for d, t in out_map[i] if d == dim}

    n_encl = len(encl_cut)
    encl_pieces = set()
    for i in range(n_encl):
        encl_pieces |= tags_of(i)
    alumina = tags_of(n_encl)
    quartz = tags_of(n_encl + 1)
    bore_v = tags_of(n_encl + 2)
    port_v = tags_of(n_encl + 3, dim=2)
    air = encl_pieces - alumina - quartz - bore_v

    vols = {"alumina": sorted(alumina), "quartz": sorted(quartz),
            "bore": sorted(bore_v), "air": sorted(air)}
    for name, tags in vols.items():
        if not tags:
            sys.exit(f"ERROR: no volume classified as '{name}'.")
        gmsh.model.addPhysicalGroup(3, tags, name=name)

    if not port_v:
        sys.exit("ERROR: port face vanished in the fragment.")
    gmsh.model.addPhysicalGroup(2, sorted(port_v), tag=TAG_PORT, name="port")
    print(f"  port face(s) {sorted(port_v)} -> attribute {TAG_PORT}")

    # PEC topologically: a face bounding exactly ONE volume is an outer wall or
    # a loop surface. Both are metal. The port face is excluded explicitly.
    pec, loop_faces = [], []
    for dim, tag in gmsh.model.getEntities(2):
        if tag in port_v:
            continue
        if len(gmsh.model.getAdjacencies(2, tag)[0]) != 1:
            continue
        pec.append(tag)
        # Separate the loop's own surfaces from the enclosure. Both are PEC,
        # but only the loop needs fine elements. Sizing the WHOLE air volume to
        # the loop's wire radius gave 1.8M tets against AMIP's 98k for the same
        # question — 18x the cost for no extra accuracy anywhere that matters.
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        r_out = max(abs(xmin), abs(xmax), abs(ymin), abs(ymax))
        on_wall = abs(r_out - encl_r) < 1e-6
        on_end = (abs(zmin - z0) < 1e-6 and abs(zmax - z0) < 1e-6) or \
                 (abs(zmin - (z0 + p["encl_len"])) < 1e-6 and
                  abs(zmax - (z0 + p["encl_len"])) < 1e-6)
        if not (on_wall or on_end):
            loop_faces.append(tag)
    gmsh.model.addPhysicalGroup(2, pec, name="pec")
    print(f"  PEC: {len(pec)} faces (topological), of which "
          f"{len(loop_faces)} are loop surfaces")

    n = p["elems_per_wl"]
    h_air = min(mesh_size(1.0, F0, n), clearance / 3.0)
    h_alu = mesh_size(p["ring_eps"], F0, n)
    h_qtz = mesh_size(p["torch_eps"], F0, n)
    print(f"  target h: air {h_air*1e3:.1f} | alumina {h_alu*1e3:.1f} "
          f"| quartz {h_qtz*1e3:.1f} mm")

    gmsh.option.setNumber("Mesh.MeshSizeMin", min(h_alu * p["edge_refine"] * 0.5,
                                                  lg * 0.8))
    gmsh.option.setNumber("Mesh.MeshSizeMax", h_air)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)

    def set_pts(tags, h, dim=3):
        for t in tags:
            for d, pt in gmsh.model.getBoundary([(dim, t)], recursive=True,
                                                oriented=False):
                if d == 0:
                    gmsh.model.mesh.setSize([(0, pt)], h)

    set_pts(vols["air"], h_air)
    set_pts(vols["quartz"], h_qtz)
    set_pts(vols["bore"], h_qtz)
    set_pts(vols["alumina"], h_alu * p["edge_refine"])
    set_pts(loop_faces, lrw * 0.9, dim=2)        # loop wire only, not the air
    set_pts(sorted(port_v), lg * 0.8, dim=2)     # resolve the gap itself

    gmsh.model.mesh.generate(3)
    if msh_order > 1:
        gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
        gmsh.option.setNumber("Mesh.HighOrderPassMax", 25)
        gmsh.option.setNumber("Mesh.HighOrderIterMax", 200)
        gmsh.model.mesh.setOrder(msh_order)

    def count_inverted():
        bad, worst = 0, 1.0
        for etype in gmsh.model.mesh.getElementTypes(3):
            tags, _ = gmsh.model.mesh.getElementsByType(etype)
            q = gmsh.model.mesh.getElementQualities(list(tags), "minSICN")
            bad += sum(1 for v in q if v <= 0.0)
            worst = min(worst, min(q) if len(q) else 1.0)
        return bad, worst

    bad, worst = count_inverted()
    for attempt in range(3):
        if bad == 0:
            break
        print(f"  {bad} inverted (worst {worst:.3f}) — repair {attempt+1}")
        gmsh.model.mesh.optimize("HighOrderFastCurving", force=True)
        gmsh.model.mesh.optimize("HighOrder", force=True)
        bad, worst = count_inverted()
    if bad:
        sys.exit(f"ERROR: {bad} elements inverted (worst {worst:.3f}).")
    print(f"  jacobian check: OK — worst minSICN {worst:.3f}")

    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(out)
    ne = len(gmsh.model.mesh.getElementsByType(4 if msh_order == 1 else 11)[0])
    print(f"  mesh: {ne} tets, order {msh_order} -> {out}")
    gmsh.finalize()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ring_drv.msh")
    ap.add_argument("--order", type=int, default=1, choices=(1, 2))
    ap.add_argument("--loop", type=str, default=None, help="d,w,rw,gap in mm")
    a = ap.parse_args()
    if a.loop:
        d, w, rw, g = (float(v) for v in a.loop.split(","))
        P["loop_d"], P["loop_w"] = d * 1e-3, w * 1e-3
        P["loop_rw"], P["loop_gap"] = rw * 1e-3, g * 1e-3
    build(P, a.out, a.order)
