#!/usr/bin/env python3
"""R63 / test 4 — an IRIS-FED cavity, validated by its own scaling exponent.

R62 closed the loop route: a bigger loop restructures the mode (§12) and a series
capacitor does not cancel anything, because the loop is ~lambda/2 in perimeter
and not a lumped inductor. What remains is an iris or waveguide feed — which is
what MP-AES uses and what AMIP set out to avoid.

Two validations already passed:
  · the 2x convention is closed, so a Q_ext can be believed (entry 107)
  · Palace's WavePort reproduces WR-340 dispersion to 0.0 deg (rig_wg.py)

This is the third, and it validates the COUPLING physics rather than the port.

RIG: empty TE011 cavity at the design dimensions (no torch, no mode filter — a
clean mode with an analytic anchor), fed through a circular iris in the barrel
wall at mid-plane from a WR-340 section terminated by a WavePort.

🔢 THE KNOWN ANSWER IS AN EXPONENT, NOT A VALUE. Small-hole theory gives
aperture polarizability ~ d^3, so coupled power ~ d^6 and

        Q_ext  ~  d^-6

Fitting that exponent tests the coupling physics WITHOUT needing an absolute
constant — the same trick that worked for R36's delta^2 ovality law and R48's
tan(beta*d). Over 10 -> 28 mm the prediction is a 2.8^6 = 481x fall in Q_ext, so
the measurement has enormous dynamic range to fit against.

  slope ~ -6   ✅ Bethe coupling holds; an absolute Q_ext here is trustworthy
  slope ~ -3   ⚠️ the iris is not electrically small at these sizes
  no power law 🔴 something else dominates; do not trust an absolute Q_ext

ORIENTATION MATTERS. The cavity's TE011 field at the barrel is E_phi, which at
phi=0 points along y. WR-340's TE10 has E along its SHORT dimension, so the
43.18 mm side lies along y and the 86.36 mm side along z. Getting this wrong
couples to nothing and would look like a failed iris rather than a wrong rig.
"""
import json
import math
import os
import pathlib
import subprocess
import sys
import time

A_CAV, L_CAV = 103.70e-3, 88.53e-3
WG_A, WG_B, WG_L = 86.36e-3, 43.18e-3, 90.0e-3
WALL_T = 2.0e-3
C0 = 299_792_458.0
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
HOME = pathlib.Path.home()
ENV = {**os.environ,
       "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}
DIAMS_MM = (10.0, 14.0, 20.0, 28.0)
# ⚠️ NARROW, and centred on the ANALYTIC resonance. The empty cavity's TE011 is
# at 2.44438 GHz with Q ~ 50,000, i.e. a 49 kHz linewidth. A 60 MHz band is 1227
# linewidths wide and the adaptive ROM cannot resolve it: the first case ran
# 3h51m on a 34k-tet mesh that should take seconds. The analytic anchor is what
# makes a narrow band safe — we know where to look.
F_ANALYTIC = 2.44438
BAND = (F_ANALYTIC - 0.003, F_ANALYTIC + 0.003)


def build(d_mm, out):
    """Meshing runs in a CHILD under micromamba, never in this process.

    Running the whole driver under `micromamba run` fails once Python spawns
    Palace -> mpirun: signal handling breaks and gmsh dies with "Interrupted
    system call". Every working driver here uses this split, and meshsweep.py
    does the same thing for the same reason.
    """
    MM = pathlib.Path.home() / ".local/bin/micromamba"
    g = subprocess.run([str(MM), "run", "-n", "emsim", "python", __file__,
                        "--build", str(d_mm), out],
                       capture_output=True, text=True)
    if g.returncode != 0:
        raise RuntimeError((g.stderr or g.stdout).strip().splitlines()[-1])
    return int(g.stdout.strip().split()[-1])


def _build_child(d_mm, out):
    import gmsh
    d = d_mm * 1e-3
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)
    gmsh.model.add("iris")
    occ = gmsh.model.occ
    cav = occ.addCylinder(0, 0, -L_CAV / 2, 0, 0, L_CAV, A_CAV)
    hole = occ.addCylinder(A_CAV, 0, 0, WALL_T, 0, 0, d / 2)
    wg = occ.addBox(A_CAV + WALL_T, -WG_B / 2, -WG_A / 2, WG_L, WG_B, WG_A)
    out_dt, _ = occ.fuse([(3, cav)], [(3, hole), (3, wg)])
    occ.synchronize()
    vols = [t for dd, t in out_dt if dd == 3]

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

    gmsh.model.addPhysicalGroup(3, vols, tag=1, name="air")
    gmsh.model.addPhysicalGroup(2, [port], tag=10, name="wgport")
    gmsh.model.addPhysicalGroup(2, walls, tag=12, name="pec")

    gmsh.option.setNumber("Mesh.MeshSizeMax", 10e-3)
    gmsh.option.setNumber("Mesh.MeshSizeMin", max(d / 6.0, 0.8e-3))
    ball = gmsh.model.mesh.field.add("Ball")
    gmsh.model.mesh.field.setNumber(ball, "Radius", d)
    gmsh.model.mesh.field.setNumber(ball, "Thickness", 3 * d)
    gmsh.model.mesh.field.setNumber(ball, "VIn", d / 6.0)
    gmsh.model.mesh.field.setNumber(ball, "VOut", 10e-3)
    gmsh.model.mesh.field.setNumber(ball, "XCenter", A_CAV + WALL_T / 2)
    gmsh.model.mesh.field.setNumber(ball, "YCenter", 0.0)
    gmsh.model.mesh.field.setNumber(ball, "ZCenter", 0.0)
    gmsh.model.mesh.field.setAsBackgroundMesh(ball)
    gmsh.model.mesh.generate(3)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(out)
    n = len(gmsh.model.mesh.getElementsByType(4)[0])
    gmsh.finalize()
    print(f"tets {n}")
    return n


def cfg(mesh, tag):
    return {
        "Problem": {"Type": "Driven", "Verbose": 2, "Output": f"postpro/{tag}"},
        "Model": {"Mesh": mesh, "L0": 1.0},
        "Domains": {"Materials": [{"Attributes": [1], "Permittivity": 1.0,
                                   "Permeability": 1.0}],
                    "Postprocessing": {"Energy": [{"Index": 1,
                                                   "Attributes": [1]}]}},
        "Boundaries": {
            "Conductivity": [{"Attributes": [12], "Conductivity": 6.3e7,
                              "Permeability": 1.0}],
            "WavePort": [{"Index": 1, "Attributes": [10], "Mode": 1,
                          "Offset": 0.0, "Excitation": True}],
        },
        "Solver": {"Order": 1, "Device": "CPU",
                   "Driven": {"Samples": [{"Type": "Linear", "MinFreq": BAND[0],
                                           "MaxFreq": BAND[1],
                                           "FreqStep": 5e-6},],
                              "AdaptiveTol": 1e-3, "AdaptiveMaxSamples": 40,
                              "SaveStep": 0},
                   "Linear": {"Type": "Default", "KSPType": "GMRES",
                              "Tol": 1e-8, "MaxIts": 500}},
    }


if len(sys.argv) == 4 and sys.argv[1] == "--build":
    _build_child(float(sys.argv[2]), sys.argv[3])
    sys.exit(0)

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq

print(__doc__)
print("=" * 78, flush=True)
rows = []
for d in DIAMS_MM:
    tag = f"ir{int(d)}"
    mesh = f"{tag}.msh"
    n = build(d, mesh)
    pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg(mesh, tag), indent=2))
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT).returncode
    dt = time.time() - t0
    if rc:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        print(f"  🔴 {tag} (d={d} mm): rc={rc} — {tail[-1] if tail else ''}",
              flush=True)
        continue
    recs = dq.load(tag)
    idx = dq.peaks(recs, rel=0.05, sep=0.002)
    if not idx:
        print(f"  ⚠️ {tag} (d={d} mm): no resonance in band", flush=True)
        continue
    pk = max((recs[i] for i in idx), key=lambda r: r["U"])
    half = pk["U"] / 2
    i0 = recs.index(pk)
    lo = next((recs[i]["f"] for i in range(i0, -1, -1) if recs[i]["U"] <= half), None)
    hi = next((recs[i]["f"] for i in range(i0, len(recs)) if recs[i]["U"] <= half), None)
    ql = pk["f"] / (hi - lo) if lo and hi and hi > lo else None
    qext = 1.0 / (1.0 / ql - 1.0 / pk["Q0"]) if ql and ql < pk["Q0"] else None
    rows.append((d, pk["f"], pk["Q0"], ql, qext))
    print(f"  d={d:>5.1f} mm  {n:>8,} tets  {dt:>5.0f}s  f={pk['f']:.5f}  "
          f"Q0={pk['Q0']:>9,.0f}  Q_L={ql if ql else float('nan'):>9,.0f}  "
          f"Q_ext={qext if qext else float('nan'):>10,.0f}", flush=True)

print("\n" + "=" * 78)
good = [(d, q) for d, _f, _q0, _ql, q in rows if q]
if len(good) >= 3:
    xs = [math.log(d) for d, _q in good]
    ys = [math.log(q) for _d, q in good]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den
    print(f"  log-log fit of Q_ext vs iris diameter: slope = {slope:.2f}")
    print(f"  Bethe small-hole theory predicts -6")
    if -7.5 < slope < -4.5:
        print("\n  ✅ Q_ext ~ d^-6 CONFIRMED — Bethe coupling holds, the iris feed "
              "is\n     physically modelled, and an absolute Q_ext from it can be "
              "trusted.")
    elif slope < -1:
        print(f"\n  ⚠️ a power law, but exponent {slope:.2f} not -6 — the iris is "
              "not\n     electrically small at these diameters. Usable, but the "
              "small-hole\n     formula is not the right extrapolation.")
    else:
        print("\n  🔴 no clear power law — something other than aperture coupling "
              "dominates.\n     Do not trust an absolute Q_ext from this "
              "geometry.")
else:
    print("  too few usable points to fit")
print(flush=True)
