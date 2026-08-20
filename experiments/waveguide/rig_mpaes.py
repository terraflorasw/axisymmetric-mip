#!/usr/bin/env python3
"""R68 / R66 — IRIS-FED, PLASMA-LOADED cavity. The first test that can falsify
OUR MODEL rather than a geometry.

Every AMIP coupling result so far is self-referential: measured against a target
AMIP itself generated. The user's point closes that loop — MP-AES and MICAP are
demonstrably working 2.45 GHz microwave plasma sources, so a model that cannot
produce a matched microwave plasma is wrong, whatever it says about TE011.

What the literature says the working devices actually do:
  · MP-AES (Agilent 4100/4210) — a HAMMER CAVITY fed by a CAPACITIVE IRIS in a
    waveguide, coupling from the MAGNETIC field, explicitly unlike earlier
    E-coupled MIPs. On the market since 2012.
  · MICAP (Radom) — an alumina DIELECTRIC RESONATOR RING whose polarisation
    currents make an axial H field "analogous to the electrical current within a
    traditional ICP load coil". Same physics as TE011, smaller resonator.

Neither uses a loop. Both couple magnetically through a large aperture or a
directly-excited resonator. That is R66's topology argument, arrived at
independently by two companies.

🔑 WHY THIS IS NOW TRACTABLE, HAVING BEEN BLOCKED SINCE R63.
R64 blocked the iris rig: WavePort would not converge against the EMPTY cavity's
Q ~ 50,000, burning 3h51m and 50 min at 99.9% CPU without finishing. The empty
cavity was chosen for a clean analytic anchor, and that is exactly what made it
intractable.

Loading it with the plasma drops Q to ~320 — a 150x BROADER resonance. The
obstacle was never the port; it was the linewidth. Adding the physics we care
about is what makes the solve cheap.

🔢 THE OBSERVABLE IS beta, READ FROM |Gamma|, NOT FROM A LINEWIDTH.
With Q_plasma ~ 320 and Q_ext unknown and possibly >> 320, Q_L ~ Q_plasma and a
linewidth carries almost no information about Q_ext — a difference of two nearly
equal numbers. |Gamma| at the loaded resonance does:

        beta = (1 - |Gamma|) / (1 + |Gamma|)        [undercoupled branch]

        beta = 0.01  ->  |Gamma| = 0.980
        beta = 0.10  ->  |Gamma| = 0.818
        beta = 1.00  ->  |Gamma| = 0.000

That spread is enormous against the 16% |Gamma| systematic entry 109 found, and
every case here is read from an identically-shaped band so the systematic is
common-mode. beta is also exactly the quantity the design needs, with no
convention factor and no offset in the way.

⚠️ THE BRANCH AMBIGUITY IS REAL. |Gamma| alone cannot distinguish beta from
1/beta. It is resolved by the SWEEP: beta must rise monotonically with iris
diameter, so a |Gamma| that falls to a minimum and rises again marks the
crossing of beta = 1 and everything past it is overcoupled. A single point could
be misread; the sweep cannot.

VERDICTS, pre-registered:
  beta reaches ~1 at a feasible iris   ✅ the model DOES produce matched
     microwave-plasma coupling. Its verdict on TE011 can then be believed, and
     R66's slot/iris route is the answer for AMIP.
  beta stuck ~0.01 at every diameter   🔴 the model says a shipping instrument
     cannot work. THE MODEL IS WRONG, and every coupling conclusion from R56
     onward — including the 98x deficit — is void until it is fixed.

The second outcome is the valuable one, and it is the first test in this
programme whose failure mode is "our model is broken" rather than "this geometry
is bad".
"""
import json
import math
import os
import pathlib
import subprocess
import sys
import time

# Cavity at the AMIP design point, so a positive result transfers directly
# rather than describing some other resonator.
A_CAV, L_CAV = 103.70e-3, 88.53e-3
WALL_T = 2.0e-3
# Torch and plasma from baselines.json: plasma.region = [4.5, 8.5, -20, 10] mm,
# the R12 "toroid" case — hollow centre for the sample channel, axially
# concentrated. Quartz wall 8.5 -> 10.5 mm.
BORE_RI, BORE_RO = 8.5e-3, 10.5e-3
PL_RI, PL_RO = 4.5e-3, 8.5e-3
PL_ZLO, PL_ZHI = -20.0e-3, 10.0e-3
SIGMA = 30.0                    # ⚠️ ASSUMED — r12.py:26, error null. See R67.
EPS_QUARTZ = 3.78
WG_A, WG_B, WG_L = 86.36e-3, 43.18e-3, 90.0e-3

# 🔢 Sized for the LOADED cavity, not the empty one. R63's iris sweep ran
# 10-28 mm against Q ~ 50,000; here the load is 150x heavier, so the aperture
# has to be far larger to reach beta = 1. Spanning 20 -> 60 mm gives a 3x lever
# in diameter, i.e. 3^6 = 729x in Bethe coupling, which brackets any plausible
# crossing.
DIAMS_MM = (20.0, 30.0, 40.0, 50.0, 60.0)

# Loaded TE011 sits near 2.431 GHz (baselines plasma.f_loaded, +/-5 MHz mesh
# scatter) with a 7.6 MHz linewidth at Q = 320. A 60 MHz band is ~8 linewidths
# — wide enough to survive the peak-position scatter, narrow enough to sample
# well. 0.2 MHz step puts ~38 points across the linewidth.
BAND = (2.400, 2.460)
STEP = 2e-4
PLASMA_H = 0.8e-3               # R15: 0.8 mm gave Q = 319 vs 320 at 0.6 mm

TAG_AIR, TAG_QUARTZ, TAG_PLASMA = 1, 2, 12
TAG_PORT, TAG_PEC = 10, 11

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
HOME = pathlib.Path.home()
ENV = {**os.environ,
       "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}


def build(d_mm, out):
    """Meshing runs in a CHILD under micromamba, never in this process.

    Running the whole driver under `micromamba run` breaks signal handling once
    Python spawns Palace -> mpirun, and gmsh dies with "Interrupted system
    call". Every working driver here uses this split.
    """
    MM = pathlib.Path.home() / ".local/bin/micromamba"
    g = subprocess.run([str(MM), "run", "-n", "emsim", "python", __file__,
                        "--build", str(d_mm), out],
                       capture_output=True, text=True)
    if g.returncode != 0:
        raise RuntimeError((g.stderr or g.stdout).strip().splitlines()[-1])
    return json.loads(g.stdout.strip().splitlines()[-1])


def _build_child(d_mm, out):
    import gmsh
    d = d_mm * 1e-3
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("mpaes")
    occ = gmsh.model.occ

    zlo = -L_CAV / 2
    cav = occ.addCylinder(0, 0, zlo, 0, 0, L_CAV, A_CAV)
    # Iris through the barrel at the mid-plane, plus the WR-340 stub behind it.
    # 🔢 ORIENTATION: TE011's E at the barrel is E_phi, which at phi=0 points
    # along y. WR-340's TE10 has E along its SHORT dimension, so the 43.18 mm
    # side lies along y and the 86.36 mm side along z. Getting this wrong
    # couples to nothing and looks like a failed iris rather than a wrong rig.
    hole = occ.addCylinder(A_CAV, 0, 0, WALL_T, 0, 0, d / 2)
    wg = occ.addBox(A_CAV + WALL_T, -WG_B / 2, -WG_A / 2, WG_L, WG_B, WG_A)
    shell, _ = occ.fuse([(3, cav)], [(3, hole), (3, wg)])

    # Torch: quartz annulus BORE_RI..BORE_RO spanning the full cavity, and the
    # plasma torus inside it. Cut both out of the air volume so each becomes its
    # own region with its own material.
    quartz = occ.addCylinder(0, 0, zlo, 0, 0, L_CAV, BORE_RO)
    qin = occ.addCylinder(0, 0, zlo, 0, 0, L_CAV, BORE_RI)
    quartz_dt, _ = occ.cut([(3, quartz)], [(3, qin)], removeTool=False)

    pl_h = PL_ZHI - PL_ZLO
    pl = occ.addCylinder(0, 0, PL_ZLO, 0, 0, pl_h, PL_RO)
    plin = occ.addCylinder(0, 0, PL_ZLO, 0, 0, pl_h, PL_RI)
    plasma_dt, _ = occ.cut([(3, pl)], [(3, plin)])

    frag, _ = occ.fragment(shell, quartz_dt + plasma_dt)
    occ.synchronize()

    # Classify volumes by their centroid radius and extent rather than by tag
    # order, which fragment() does not preserve.
    air, quartz_v, plasma_v = [], [], []
    for dim, tag in gmsh.model.getEntities(3):
        bb = gmsh.model.getBoundingBox(dim, tag)
        rmax = max(abs(bb[0]), abs(bb[3]), abs(bb[1]), abs(bb[4]))
        zc = 0.5 * (bb[2] + bb[5])
        dz = bb[5] - bb[2]
        if rmax <= BORE_RO * 1.02 and rmax > BORE_RI * 0.98:
            quartz_v.append(tag)
        elif (rmax <= PL_RO * 1.02 and abs(dz - pl_h) < 1e-4
              and abs(zc - 0.5 * (PL_ZLO + PL_ZHI)) < 1e-4):
            plasma_v.append(tag)
        else:
            air.append(tag)
    if not plasma_v:
        raise RuntimeError("plasma sub-region not found after fragment")

    port, walls = None, []
    for dim, tag in gmsh.model.getEntities(2):
        bb = gmsh.model.getBoundingBox(dim, tag)
        xc, xspan = 0.5 * (bb[0] + bb[3]), bb[3] - bb[0]
        if xspan < 1e-4 and abs(xc - (A_CAV + WALL_T + WG_L)) < 1e-4:
            port = tag
        else:
            walls.append(tag)
    if port is None:
        raise RuntimeError("waveguide port face not found")

    gmsh.model.addPhysicalGroup(3, air, tag=TAG_AIR, name="air")
    gmsh.model.addPhysicalGroup(3, quartz_v, tag=TAG_QUARTZ, name="quartz")
    gmsh.model.addPhysicalGroup(3, plasma_v, tag=TAG_PLASMA, name="plasma")
    gmsh.model.addPhysicalGroup(2, [port], tag=TAG_PORT, name="wgport")
    gmsh.model.addPhysicalGroup(2, walls, tag=TAG_PEC, name="pec")

    # 🔢 The plasma skin depth at SIGMA = 30 S/m is 1.86 mm and R15 showed 0.8 mm
    # elements resolve it (Q = 319 vs 320 at 0.6 mm). A Cylinder field, NOT
    # set_pts: with MeshSizeExtendFromBoundary = 0 a boundary-point size is a
    # silent no-op, which once changed a mesh by 795 tets where 29,000 were
    # expected. MeshSizeMin must also be lowered or it clamps the request.
    gmsh.option.setNumber("Mesh.MeshSizeMax", 10e-3)
    gmsh.option.setNumber("Mesh.MeshSizeMin", min(PLASMA_H, d / 8.0) * 0.5)
    cyl = gmsh.model.mesh.field.add("Cylinder")
    gmsh.model.mesh.field.setNumber(cyl, "Radius", PL_RO * 1.5)
    gmsh.model.mesh.field.setNumber(cyl, "VIn", PLASMA_H)
    gmsh.model.mesh.field.setNumber(cyl, "VOut", 10e-3)
    gmsh.model.mesh.field.setNumber(cyl, "ZAxis", pl_h * 1.4)
    gmsh.model.mesh.field.setNumber(cyl, "ZCenter", 0.5 * (PL_ZLO + PL_ZHI))
    gmsh.model.mesh.field.setNumber(cyl, "XCenter", 0.0)
    gmsh.model.mesh.field.setNumber(cyl, "YCenter", 0.0)
    ball = gmsh.model.mesh.field.add("Ball")
    gmsh.model.mesh.field.setNumber(ball, "Radius", d)
    gmsh.model.mesh.field.setNumber(ball, "Thickness", 2 * d)
    gmsh.model.mesh.field.setNumber(ball, "VIn", d / 8.0)
    gmsh.model.mesh.field.setNumber(ball, "VOut", 10e-3)
    gmsh.model.mesh.field.setNumber(ball, "XCenter", A_CAV + WALL_T / 2)
    gmsh.model.mesh.field.setNumber(ball, "YCenter", 0.0)
    gmsh.model.mesh.field.setNumber(ball, "ZCenter", 0.0)
    mn = gmsh.model.mesh.field.add("Min")
    gmsh.model.mesh.field.setNumbers(mn, "FieldsList", [cyl, ball])
    gmsh.model.mesh.field.setAsBackgroundMesh(mn)
    gmsh.model.mesh.generate(3)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(out)
    meta = {"tets": len(gmsh.model.mesh.getElementsByType(4)[0]),
            "pec_surfaces": len(walls),
            "plasma_vols": len(plasma_v), "quartz_vols": len(quartz_v)}
    gmsh.finalize()
    print(json.dumps(meta))
    return meta


def cfg(mesh, tag):
    return {
        "Problem": {"Type": "Driven", "Verbose": 2, "Output": f"postpro/{tag}"},
        "Model": {"Mesh": mesh, "L0": 1.0},
        "Domains": {
            "Materials": [
                {"Attributes": [TAG_AIR], "Permittivity": 1.0,
                 "Permeability": 1.0},
                {"Attributes": [TAG_QUARTZ], "Permittivity": EPS_QUARTZ,
                 "Permeability": 1.0},
                {"Attributes": [TAG_PLASMA], "Permittivity": 1.0,
                 "Permeability": 1.0, "Conductivity": SIGMA},
            ],
            "Postprocessing": {"Energy": [{"Index": 1, "Attributes": [TAG_AIR]}]},
        },
        "Boundaries": {
            # Silver walls, not PEC — the endcaps carry real loss and the whole
            # point here is a power balance.
            "Conductivity": [{"Attributes": [TAG_PEC], "Conductivity": 6.3e7,
                              "Permeability": 1.0}],
            "WavePort": [{"Index": 1, "Attributes": [TAG_PORT], "Mode": 1,
                          "Offset": 0.0, "Excitation": True}],
        },
        "Solver": {"Order": 1, "Device": "CPU",
                   "Driven": {"Samples": [{"Type": "Linear",
                                           "MinFreq": BAND[0],
                                           "MaxFreq": BAND[1],
                                           "FreqStep": STEP}],
                              "AdaptiveTol": 1e-3, "AdaptiveMaxSamples": 30,
                              "SaveStep": 0},
                   "Linear": {"Type": "Default", "KSPType": "GMRES",
                              "Tol": 1e-8, "MaxIts": 500}},
    }


if len(sys.argv) == 4 and sys.argv[1] == "--build":
    _build_child(float(sys.argv[2]), sys.argv[3])
    sys.exit(0)

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import solver

print(__doc__)
print("=" * 78, flush=True)
rows = []
seen_tets = {}
for d in DIAMS_MM:
    tag = f"mp{int(d)}"
    mesh = f"{tag}.msh"
    try:
        meta = build(d, mesh)
    except RuntimeError as e:
        print(f"  🔴 {tag} (d={d} mm): mesh failed — {e}", flush=True)
        continue
    # Postcondition: the iris diameter MUST change the mesh. Two silent no-ops
    # in one night produced confident verdicts from meshes never modified.
    if meta["tets"] in seen_tets:
        print(f"  🔴 {tag}: identical tet count to {seen_tets[meta['tets']]} "
              f"({meta['tets']:,}) — the iris is not reaching the mesh",
              flush=True)
        continue
    seen_tets[meta["tets"]] = tag

    pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg(mesh, tag), indent=2))
    t0 = time.time()
    try:
        solver.solve(mesh, tag, BAND, cfg_path=f"{tag}.json")
    except Exception as e:
        print(f"  🔴 {tag} (d={d} mm): {e}", flush=True)
        continue
    dt = time.time() - t0

    recs = dq.load(tag)
    if not recs:
        print(f"  ⚠️ {tag} (d={d} mm): no records", flush=True)
        continue
    # The loaded peak is the largest-U record. NO mode label: the plasma
    # redistributes energy and the unloaded classifier mislabels it (modes.py
    # loaded() exists for exactly this reason).
    pk = max(recs, key=lambda r: r["U"])
    g = pk.get("gamma")
    beta = (1 - g) / (1 + g) if g is not None and g < 1 else None
    rows.append((d, meta["tets"], pk["f"], pk["Q0"], g, beta))
    print(f"  d={d:>5.1f} mm  {meta['tets']:>8,} tets  {dt:>5.0f}s  "
          f"f={pk['f']:.5f}  Q0={pk['Q0']:>8,.0f}  "
          f"|Gamma|={g if g is not None else float('nan'):.4f}  "
          f"beta={beta if beta else float('nan'):.4f}  "
          f"absorbed={100*(1-g**2) if g is not None else float('nan'):.1f}%",
          flush=True)

print("\n" + "=" * 78)
print("VERDICT")
good = [r for r in rows if r[5]]
if len(good) >= 3:
    best = max(good, key=lambda r: r[5])
    gammas = [r[4] for r in good]
    imin = gammas.index(min(gammas))
    print(f"  best coupling at d = {best[0]} mm: |Gamma| = {best[4]:.4f}, "
          f"beta = {best[5]:.3f}, {100*(1-best[4]**2):.1f}% absorbed")
    if best[5] >= 0.5:
        print("\n  ✅ THE MODEL PRODUCES MATCHED MICROWAVE-PLASMA COUPLING.")
        print("     An iris reaches beta ~ 1 on the loaded TE011 cavity, so the "
              "model is not\n     broken and its verdict on TE011 can be "
              "believed. R66's aperture route is\n     the answer for AMIP, and "
              "the loop family is simply the wrong topology.")
        if 0 < imin < len(good) - 1:
            print(f"  🔑 |Gamma| MINIMUM at d = {good[imin][0]} mm with rise on "
                  "both sides — beta = 1\n     is CROSSED, resolving the "
                  "beta vs 1/beta branch ambiguity by the sweep.")
    elif best[5] > 0.1:
        print(f"\n  ⚠️ PARTIAL: beta reaches {best[5]:.2f}, within ~{1/best[5]:.0f}x "
              "of a match but not\n     there. The mechanism works; the aperture "
              "is too small or badly placed.\n     Extend the sweep before "
              "concluding anything about the model.")
    else:
        print(f"\n  🔴 beta never exceeds {best[5]:.3f} across a {DIAMS_MM[-1]/DIAMS_MM[0]:.0f}x "
              "diameter range.")
        print("     THE MODEL SAYS A SHIPPING INSTRUMENT CANNOT WORK. MP-AES has "
              "coupled a\n     2.45 GHz plasma through an iris since 2012. The "
              "model is wrong, and every\n     coupling conclusion from R56 "
              "onward — the 98x deficit included — is VOID\n     until it is "
              "found. Suspect first: the 2x convention at the WavePort, the\n"
              "     iris orientation vs E_phi, and SIGMA itself.")
    xs = [math.log(r[0]) for r in good]
    ys = [math.log(r[5]) for r in good]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    if den > 0:
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
        print(f"\n  log-log fit of beta vs iris diameter: slope = {slope:+.2f} "
              "(Bethe small-hole predicts +6)")
        if slope < 1.0:
            print("  ⚠️ far below +6 — the aperture is NOT behaving as a "
                  "small hole at these sizes,\n     so do not extrapolate the "
                  "sweep past its measured range.")
else:
    print(f"  too few usable points ({len(good)}) to judge — check the logs "
          "before reading anything into this")
print(flush=True)
