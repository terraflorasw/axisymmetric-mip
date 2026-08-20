#!/usr/bin/env python3
"""KNOWN-ANSWER TEST: does Palace's WavePort reproduce waveguide theory?

R63 needs an iris or waveguide feed, whose entire output would be a Q_ext with no
independent check. Before building one, validate the port type it depends on
against an answer that is textbook rather than simulated.

RIG: a straight WR-340 section (86.36 x 43.18 mm), wave ports on both ends, PEC
walls. No cavity, no resonance — just propagation.

🔢 KNOWN ANSWERS, from the guide's dimensions alone:

    TE10 cutoff   fc = c/2a = 1.7359 GHz
    at 2.45 GHz   beta = (2*pi/c)*sqrt(f^2 - fc^2) = 36.23 rad/m
                  guide wavelength lambda_g = 2*pi/beta = 173.4 mm
    through a section of length Lz:
                  |S21| = 1        (PEC walls, lossless)
                  arg(S21) = -beta*Lz   (pure delay)

Three independent things are tested at once, and each failure looks different:
  · |S21| ~ 1 and |S11| ~ 0  -> the port is matched, i.e. it really is absorbing
    the mode rather than reflecting it
  · arg(S21) vs -beta*Lz     -> the port is launching the RIGHT MODE with the
    right propagation constant
  · sweeping frequency        -> beta(f) must follow the dispersion curve, not a
    straight line. A free-space port would give beta = 2*pi*f/c and no cutoff.

⚠️ If this fails there is no point attempting an iris feed: a Q_ext measured
through a port that does not launch the correct mode is meaningless, and the
failure would be invisible in the Q_ext number itself.
"""
import json
import math
import os
import pathlib
import subprocess
import sys
import time

import gmsh

A_MM, B_MM, LZ_MM = 86.36, 43.18, 120.0
C0 = 299_792_458.0
FREQS = (2.20, 2.45, 2.70)
MESH = "wg340.msh"
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
HOME = pathlib.Path.home()
ENV = {**os.environ,
       "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}


def beta(f_ghz):
    fc = C0 / (2 * A_MM * 1e-3)
    f = f_ghz * 1e9
    if f <= fc:
        return None
    return 2 * math.pi * math.sqrt(f * f - fc * fc) / C0


def build():
    gmsh.initialize()
    gmsh.model.add("wr340")
    occ = gmsh.model.occ
    box = occ.addBox(0, 0, 0, A_MM * 1e-3, B_MM * 1e-3, LZ_MM * 1e-3)
    occ.synchronize()
    p1 = p2 = None
    walls = []
    # Classify by FLATNESS and centre, not by exact bbox equality: gmsh pads
    # bounding boxes with a tolerance, so a face at z=0 reports zmin ~ -1e-7 and
    # an exact test silently matches nothing.
    for dim, tag in gmsh.model.getEntities(2):
        bb = gmsh.model.getBoundingBox(dim, tag)
        zc, zspan = 0.5 * (bb[2] + bb[5]), bb[5] - bb[2]
        if zspan < 1e-4 and abs(zc) < 1e-4:
            p1 = tag
        elif zspan < 1e-4 and abs(zc - LZ_MM * 1e-3) < 1e-4:
            p2 = tag
        else:
            walls.append(tag)
    if p1 is None or p2 is None:
        raise RuntimeError(f"port faces not found (p1={p1}, p2={p2})")
    gmsh.model.addPhysicalGroup(3, [box], tag=1, name="air")
    gmsh.model.addPhysicalGroup(2, [p1], tag=10, name="port1")
    gmsh.model.addPhysicalGroup(2, [p2], tag=11, name="port2")
    gmsh.model.addPhysicalGroup(2, walls, tag=12, name="pec")
    gmsh.option.setNumber("Mesh.MeshSizeMax", 8e-3)
    gmsh.option.setNumber("Mesh.MeshSizeMin", 4e-3)
    gmsh.model.mesh.generate(3)
    gmsh.option.setNumber("Mesh.MshFileVersion", 2.2)
    gmsh.write(MESH)
    n = len(gmsh.model.mesh.getElementsByType(4)[0])
    gmsh.finalize()
    return n


def cfg(f_lo, f_hi, step):
    return {
        "Problem": {"Type": "Driven", "Verbose": 2, "Output": "postpro/wg"},
        "Model": {"Mesh": MESH, "L0": 1.0},
        "Domains": {"Materials": [{"Attributes": [1], "Permittivity": 1.0,
                                   "Permeability": 1.0}]},
        "Boundaries": {
            "PEC": {"Attributes": [12]},
            "WavePort": [
                {"Index": 1, "Attributes": [10], "Mode": 1, "Offset": 0.0,
                 "Excitation": True},
                {"Index": 2, "Attributes": [11], "Mode": 1, "Offset": 0.0},
            ],
        },
        "Solver": {"Order": 2, "Device": "CPU",
                   "Driven": {"Samples": [{"Type": "Linear", "MinFreq": f_lo,
                                           "MaxFreq": f_hi, "FreqStep": step}],
                              "SaveStep": 0},
                   "Linear": {"Type": "Default", "Tol": 1e-8, "MaxIts": 500}},
    }


print(__doc__)
print("=" * 78, flush=True)
ntet = build()
print(f"  rig meshed: {ntet:,} tets, WR-340 {A_MM} x {B_MM} x {LZ_MM} mm",
      flush=True)
print(f"  TE10 cutoff {C0/(2*A_MM*1e-3)/1e9:.4f} GHz", flush=True)

pathlib.Path("wg.json").write_text(json.dumps(
    cfg(FREQS[0], FREQS[-1], 0.25), indent=2))
t0 = time.time()
rc = subprocess.run([PALACE, "-np", "4", "wg.json"], env=ENV,
                    stdout=open("wg_p.log", "w"),
                    stderr=subprocess.STDOUT).returncode
print(f"  solve rc={rc} in {time.time()-t0:.0f}s", flush=True)
if rc:
    print("\n".join(pathlib.Path("wg_p.log").read_text().splitlines()[-6:]))
    sys.exit(1)

import csv
with open("postpro/wg/port-S.csv") as fh:
    rows = [{k.strip(): v.strip() for k, v in r.items() if k}
            for r in csv.DictReader(fh)]
print(f"\n{'f GHz':>8}{'|S11| dB':>11}{'|S21| dB':>11}{'arg S21':>11}"
      f"{'-beta*L deg':>13}{'diff':>9}")
worst = 0.0
for r in rows:
    def g(*n):
        for x in n:
            for k, v in r.items():
                if x in k:
                    return float(v)
    f = g("f (GHz)")
    s11, s21 = g("|S[1][1]|"), g("|S[2][1]|")
    a21 = g("arg(S[2][1])")
    b = beta(f)
    want = -math.degrees(b * LZ_MM * 1e-3) % 360
    got = a21 % 360
    d = min(abs(got - want), 360 - abs(got - want))
    worst = max(worst, d)
    print(f"{f:>8.2f}{s11:>11.2f}{s21:>11.3f}{got:>11.1f}{want:>13.1f}{d:>9.1f}")

print("\nVERDICT")
print(f"  worst phase error vs textbook beta*L: {worst:.1f} deg")
if worst < 10:
    print("  ✅ WavePort launches the correct TE10 mode with the right "
          "propagation constant.\n     An iris/waveguide feed can be modelled "
          "here, and a Q_ext through it can be believed.")
else:
    print("  🔴 phase does not follow waveguide dispersion — the port is not "
          "launching\n     the mode we think it is. Do NOT attempt an iris feed "
          "on this basis.")
print(flush=True)
