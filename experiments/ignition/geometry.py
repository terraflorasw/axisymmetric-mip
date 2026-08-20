#!/usr/bin/env python3
"""
Phase 1 eigenmode geometry — alumina dielectric resonator ring + ICP torch,
inside a metallic enclosure.

Dimensions from US10863611B2 Example 1 (the 2.45 GHz embodiment):
    alumina ring, 2.00" OD x 1.00" ID x 0.75" long, eps_r 9.8

See refs/coupling-architecture.md §2 and refs/ignition-study.md §4.1.

The coupling loop is deliberately ABSENT — Phase 1 solves for the unloaded
modes of the resonator. The loop is a perturbation and belongs in the Phase 2
driven model.

Outputs a Gmsh .msh with physical groups Palace expects.

    python geometry.py [--out ring.msh] [--order 2] [--show-sizes]
"""
from __future__ import annotations

import argparse
import math
import sys

import gmsh

# --------------------------------------------------------------------------
# Parameters — all lengths in metres
# --------------------------------------------------------------------------
P = dict(
    # Alumina ring (patent Example 1)
    ring_od=50.8e-3,
    ring_id=25.4e-3,
    ring_len=19.05e-3,
    ring_eps=9.8,
    ring_tand=1.0e-4,      # PLACEHOLDER — see refs/ignition-study.md §9 q1
    # Quartz torch outer tube
    torch_od=20.0e-3,
    torch_wall=1.5e-3,
    torch_eps=3.78,
    torch_tand=1.0e-4,
    # Metallic enclosure (PEC)
    encl_dia=160.0e-3,
    encl_len=120.0e-3,
    # Meshing: elements per wavelength *in each medium*
    elems_per_wl=8.0,      # coarse-ish; compensate with high-order FEM in Palace
    edge_refine=0.4,       # multiplier on ring-edge mesh size (field maxima)
)

C0 = 299_792_458.0
F0 = 2.45e9                # band centre used only for mesh sizing


def mesh_size(eps_r: float, f: float, n: float) -> float:
    """Target element size for n elements per wavelength in a medium."""
    return C0 / (f * math.sqrt(eps_r)) / n


def build(p: dict, out: str, msh_order: int, show_sizes: bool) -> None:
    gmsh.initialize()
    gmsh.model.add("dr_ring")
    occ = gmsh.model.occ

    encl_r = p["encl_dia"] / 2.0
    z0 = -p["encl_len"] / 2.0

    # Enclosure interior (becomes the air domain after fragmenting)
    encl = occ.addCylinder(0, 0, z0, 0, 0, p["encl_len"], encl_r)

    # Alumina ring, centred on the origin
    rz = -p["ring_len"] / 2.0
    ring_o = occ.addCylinder(0, 0, rz, 0, 0, p["ring_len"], p["ring_od"] / 2.0)
    ring_i = occ.addCylinder(0, 0, rz, 0, 0, p["ring_len"], p["ring_id"] / 2.0)
    ring, _ = occ.cut([(3, ring_o)], [(3, ring_i)], removeObject=True, removeTool=True)

    # Quartz torch tube, spanning the full enclosure length
    t_ro = p["torch_od"] / 2.0
    t_ri = t_ro - p["torch_wall"]
    tube_o = occ.addCylinder(0, 0, z0, 0, 0, p["encl_len"], t_ro)
    tube_i = occ.addCylinder(0, 0, z0, 0, 0, p["encl_len"], t_ri)
    tube, _ = occ.cut([(3, tube_o)], [(3, tube_i)], removeObject=True, removeTool=True)

    # Bore gas column (inside the torch) — kept separate so fields can be probed
    bore = occ.addCylinder(0, 0, z0, 0, 0, p["encl_len"], t_ri)

    # Conformal interfaces between everything. fragment() returns a provenance
    # map: out_map[i] lists the output volumes derived from input i. Far more
    # robust than inferring identity from bounding boxes after the fact.
    _, out_map = occ.fragment([(3, encl)], ring + tube + [(3, bore)])
    occ.synchronize()

    def tags_of(i):
        return {t for d, t in out_map[i] if d == 3}

    encl_pieces = tags_of(0)          # everything inside the enclosure
    alumina = tags_of(1)
    quartz = tags_of(2)
    bore_v = tags_of(3)
    air = encl_pieces - alumina - quartz - bore_v

    vols = {"alumina": sorted(alumina), "quartz": sorted(quartz),
            "bore": sorted(bore_v), "air": sorted(air)}

    for name, tags in vols.items():
        if not tags:
            for dim, tag in gmsh.model.getEntities(3):
                bb = gmsh.model.getBoundingBox(dim, tag)
                print(f"    vol {tag}: bbox {[f'{v*1e3:.1f}' for v in bb]}")
            sys.exit(f"ERROR: no volume classified as '{name}' — geometry changed?")
        gmsh.model.addPhysicalGroup(3, tags, name=name)

    # PEC: the outer enclosure surface. Everything on the enclosure boundary.
    pec = []
    for dim, tag in gmsh.model.getEntities(2):
        xmin, ymin, zmin, xmax, ymax, zmax = gmsh.model.getBoundingBox(dim, tag)
        r_out = max(abs(xmin), abs(xmax), abs(ymin), abs(ymax))
        on_wall = abs(r_out - encl_r) < 1e-6
        on_end = abs(zmin - z0) < 1e-6 and abs(zmax - z0) < 1e-6
        on_end |= abs(zmin - (z0 + p["encl_len"])) < 1e-6 and \
                 abs(zmax - (z0 + p["encl_len"])) < 1e-6
        if on_wall or on_end:
            pec.append(tag)
    gmsh.model.addPhysicalGroup(2, pec, name="pec")

    # ----------------------------------------------------------------------
    # Mesh sizing — per medium, refined at the ring edges where E peaks
    # ----------------------------------------------------------------------
    n = p["elems_per_wl"]
    h_air = mesh_size(1.0, F0, n)
    clearance = (p["encl_dia"] - p["ring_od"]) / 2.0
    h_air = min(h_air, clearance / 3.0)
    h_alu = mesh_size(p["ring_eps"], F0, n)
    h_qtz = mesh_size(p["torch_eps"], F0, n)

    if show_sizes:
        print(f"  target h: air {h_air*1e3:.1f} mm | alumina {h_alu*1e3:.1f} mm "
              f"| quartz {h_qtz*1e3:.1f} mm")

    gmsh.option.setNumber("Mesh.MeshSizeMin", h_alu * p["edge_refine"] * 0.5)
    gmsh.option.setNumber("Mesh.MeshSizeMax", h_air)
    gmsh.option.setNumber("Mesh.MeshSizeFromCurvature", 12)
    gmsh.option.setNumber("Mesh.MeshSizeExtendFromBoundary", 1)

    def set_pts(tags, h):
        for t in tags:
            for d, pt in gmsh.model.getBoundary([(3, t)], recursive=True,
                                                oriented=False):
                if d == 0:
                    gmsh.model.mesh.setSize([(0, pt)], h)

    set_pts(vols["air"], h_air)
    set_pts(vols["quartz"], h_qtz)
    set_pts(vols["bore"], h_qtz)
    set_pts(vols["alumina"], h_alu * p["edge_refine"])

    gmsh.model.mesh.generate(3)
    if msh_order > 1:
        # Curving order-2 elements against the cylindrical surfaces inverts a
        # few of them (negative Jacobian), which makes the FEM solve invalid.
        # These options must be set BEFORE setOrder — the repair happens during
        # high-order generation, not after.
        gmsh.option.setNumber("Mesh.HighOrderOptimize", 2)
        gmsh.option.setNumber("Mesh.HighOrderPassMax", 25)
        gmsh.option.setNumber("Mesh.HighOrderIterMax", 200)
        gmsh.model.mesh.setOrder(msh_order)

    # Verify. Negative Jacobians are silent poison. Sample the element MINIMUM
    # (minSICN), not the centroid — a curved element can be fine at its centre
    # and inverted against a curved face.
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
        print(f"  {bad} inverted elements (worst minSICN {worst:.3f}) — "
              f"repair pass {attempt + 1}")
        gmsh.model.mesh.optimize("HighOrderFastCurving", force=True)
        gmsh.model.mesh.optimize("HighOrder", force=True)
        bad, worst = count_inverted()

    if bad:
        sys.exit(f"ERROR: {bad} elements still inverted (worst minSICN "
                 f"{worst:.3f}). Mesh is invalid for FEM — increase "
                 f"MeshSizeFromCurvature, coarsen, or use --order 1.")
    print(f"  jacobian check: OK — 0 inverted, worst minSICN {worst:.3f}")

    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(out)

    ne = len(gmsh.model.mesh.getElementsByType(
        4 if msh_order == 1 else 11)[0])
    nn = len(gmsh.model.mesh.getNodes()[0])
    print(f"  mesh: {ne} tets, {nn} nodes, order {msh_order} -> {out}")

    gmsh.finalize()


def sanity_check(p: dict) -> None:
    """Independent order-of-magnitude anchor for the expected TE01d-like mode.

    The relation that already reproduced the patent geometry
    (refs/coupling-architecture.md §2): resonance when the ring mean diameter
    is on the order of the guide wavelength inside the ceramic.
    """
    lam_eff = C0 / F0 / math.sqrt(p["ring_eps"])
    d_mean = (p["ring_od"] + p["ring_id"]) / 2.0
    f_pred = C0 / (math.sqrt(p["ring_eps"]) * d_mean)
    print("  sanity check (independent of FEM):")
    print(f"    lambda_eff @2.45GHz = {lam_eff*1e3:.1f} mm")
    print(f"    ring mean diameter  = {d_mean*1e3:.1f} mm")
    print(f"    => expect a mode near {f_pred/1e9:.2f} GHz")
    print("    FEM result landing far from this indicates a modelling error,")
    print("    not a discovery.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="ring.msh")
    ap.add_argument("--encl-dia", type=float, default=None,
                    help="enclosure diameter in mm (overrides P)")
    ap.add_argument("--encl-len", type=float, default=None,
                    help="enclosure length in mm (overrides P)")
    ap.add_argument("--ring-scale", type=float, default=1.0,
                    help="uniform scale factor on ring OD/ID/length")
    ap.add_argument("--n-wl", type=float, default=None,
                    help="elements per wavelength (overrides P)")
    ap.add_argument("--order", type=int, default=2, choices=(1, 2))
    ap.add_argument("--show-sizes", action="store_true", default=True)
    a = ap.parse_args()

    if a.encl_dia is not None:
        P["encl_dia"] = a.encl_dia * 1e-3
    if a.ring_scale != 1.0:
        for k in ("ring_od", "ring_id", "ring_len"):
            P[k] *= a.ring_scale
    if a.encl_len is not None:
        P["encl_len"] = a.encl_len * 1e-3
    if a.n_wl is not None:
        P["elems_per_wl"] = a.n_wl

    print("Phase 1 eigenmode geometry")
    print(f"  enclosure dia {P['encl_dia']*1e3:.1f} mm  "
          f"(TM010 = {2.4048*C0/(math.pi*P['encl_dia'])/1e9:.3f} GHz empty)")
    sanity_check(P)
    build(P, a.out, a.order, a.show_sizes)
