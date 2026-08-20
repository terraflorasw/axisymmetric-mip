#!/usr/bin/env python3
"""R5 — measure the ring's Q by driven energy balance, as AMIP's was measured.

Three runs, because the third is only trustworthy if the first two are:

  pecref  PEC walls + lossy dielectric   -> must reproduce Q_d ~ 11,084, which
                                            the eigenmode already gives. This is
                                            the VALIDATION: if driven energy
                                            balance cannot recover a Q we
                                            already know on this geometry, the
                                            wall number it produces means
                                            nothing.
  wall    Conductivity walls, LOSSLESS   -> Q_wall alone. The number R5 exists
                                            to get. Closed form said 26,847.
  total   Conductivity walls + lossy     -> Q_total. Must equal Q_wall ∥ Q_d,
                                            a closure check on the other two.

sigma = 6.3e7 (silver) to match AMIP's measurement exactly. Comparing a ring at
copper against AMIP at silver would repeat, in a new form, the unlike-footing
error this whole recheck exists to correct.
"""
import json, pathlib, subprocess, sys, time
sys.path.insert(0, "../waveguide")
import dq

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
SIGMA = 6.3e7
F0 = 2.4289          # located by ring_locate.json, with the loop present

MATS = lambda tand: [
    {"Attributes": [1], "Permittivity": 9.8, "Permeability": 1.0, "LossTan": tand},
    {"Attributes": [2], "Permittivity": 3.78, "Permeability": 1.0, "LossTan": tand},
    {"Attributes": [3], "Permittivity": 1.0, "Permeability": 1.0},
    {"Attributes": [4], "Permittivity": 1.0, "Permeability": 1.0}]
ENERGY = [{"Index": 1, "Attributes": [3]}, {"Index": 2, "Attributes": [1]},
          {"Index": 3, "Attributes": [2]}]


def cfg(tag, tand, walls):
    b = {"LumpedPort": [{"Index": 1, "Attributes": [91], "Direction": "+Y",
                         "R": 50.0, "Excitation": True}]}
    if walls == "pec":
        b["PEC"] = {"Attributes": [92]}
    else:
        b["Conductivity"] = [{"Attributes": [92], "Conductivity": SIGMA,
                              "Permeability": 1.0}]
    c = {"Problem": {"Type": "Driven", "Verbose": 2, "Output": f"postpro/{tag}"},
         "Model": {"Mesh": "ring_drv.msh", "L0": 1.0},
         "Domains": {"Materials": MATS(tand),
                     "Postprocessing": {"Energy": ENERGY}},
         "Boundaries": b,
         "Solver": {"Order": 1, "Device": "CPU",
                    "Driven": {"Samples": [{"Type": "Linear", "MinFreq": F0 - 0.010,
                                            "MaxFreq": F0 + 0.010, "FreqStep": 2e-5}],
                               "AdaptiveTol": 1e-3, "AdaptiveMaxSamples": 40,
                               "SaveStep": 0},
                    "Linear": {"Type": "Default", "KSPType": "GMRES",
                               "Tol": 1e-8, "MaxIts": 500}}}
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    return c


RUNS = [("pecref", 1.0e-4, "pec"), ("wall", 0.0, "sigma"), ("total", 1.0e-4, "sigma")]
res = {}
for tag, tand, walls in RUNS:
    cfg(tag, tand, walls)
    done = pathlib.Path(f"postpro/{tag}/port-S.csv").exists()
    if done:
        print(f"\n=== {tag}: already solved, re-extracting", flush=True)
    else:
        t = time.time()
        rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"],
                            stdout=open(f"{tag}.log", "w"),
                            stderr=subprocess.STDOUT).returncode
        print(f"\n=== {tag}: exit {rc} in {time.time()-t:.0f}s", flush=True)
        if rc != 0:
            print(f"  FAILED — see {tag}.log"); continue
    recs = dq.load(tag)
    # peaks() returns INDICES into recs, not records.
    pk = [recs[i] for i in dq.peaks(recs)]
    if not pk:
        print("  no resonance in band (contrast guard)"); continue
    r = max(pk, key=lambda x: x["U"])
    res[tag] = r
    print(f"  f={r['f']:.5f}  Q0={r['Q0']:,.0f}  |S11|={r['s_db']:.2f} dB  "
          f"|G|={r['gamma']:.4f}  boreH={r['pm']*100:.2f}%", flush=True)

print("\n" + "=" * 62)
if "pecref" in res:
    q = res["pecref"]["Q0"]
    print(f"VALIDATION  driven PEC+lossy = {q:,.0f}  vs eigenmode Q_d 11,084 "
          f"-> {q/11084:.3f}x")
if "wall" in res:
    print(f"Q_wall MEASURED = {res['wall']['Q0']:,.0f}   vs closed form 26,847 "
          f"-> {res['wall']['Q0']/26847:.2f}x")
if "wall" in res and "pecref" in res:
    qw, qd = res["wall"]["Q0"], res["pecref"]["Q0"]
    pred = 1.0 / (1.0 / qw + 1.0 / qd)
    print(f"predicted Q_total = {qw:,.0f} || {qd:,.0f} = {pred:,.0f}")
    if "total" in res:
        print(f"measured  Q_total = {res['total']['Q0']:,.0f}  "
              f"-> closure {res['total']['Q0']/pred:.3f}x")
        print(f"\nfield at 1 kW scales as sqrt(Q): 7.88 kV/cm x "
              f"sqrt({res['total']['Q0']:,.0f}/16,767) = "
              f"{7.88*(res['total']['Q0']/16767)**0.5:.2f} kV/cm")
