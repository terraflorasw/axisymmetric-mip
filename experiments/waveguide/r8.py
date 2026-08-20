#!/usr/bin/env python3
"""R8 — why is the TM020 closed form 1.15x high when TE011's is only 1.03x?

Hypothesis: it is not a closed-form error at all. The closed forms describe a
BARE cavity. Ours contains a quartz torch and two quartz brakes, and TM020
carries 3.978% of its E-field in the bore against TE011's 0.054% — a 74x
stronger interaction with that quartz. If the "deficit" is dielectric loss, it
should vanish when the dielectrics go lossless, and vanish far more for TM020.

Same decomposition as R5 on the ring, which is what made that measurement
readable:
  nodiel  Conductivity walls, LOSSLESS dielectric -> Q_wall alone, the quantity
                                                     the closed form predicts
  pecdiel PEC walls, lossy dielectric             -> Q_diel alone
  (tilt45 already on disk)                        -> Q_total, the closure check

Both modes come out of a single solve: the 45-degree loop tilt drives TE011 and
TM020 together, which is why this geometry exists.
"""
import json, pathlib, subprocess, sys, time
import dq

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
BASE = json.loads(pathlib.Path("driven-tilt45.json").read_text())
CLOSED = {"TE011": 49182, "TM020": 26563}


def cfg(tag, tand, walls):
    c = json.loads(json.dumps(BASE))
    c["Problem"]["Output"] = f"postpro/{tag}"
    for m in c["Domains"]["Materials"]:
        if "LossTan" in m:
            m["LossTan"] = tand
    if walls == "pec":
        c["Boundaries"].pop("Conductivity", None)
        c["Boundaries"]["PEC"] = {"Attributes": [90]}
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))


def run(tag, tand, walls):
    cfg(tag, tand, walls)
    if pathlib.Path(f"postpro/{tag}/port-S.csv").exists():
        print(f"\n=== {tag}: already solved", flush=True)
    else:
        t = time.time()
        rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"],
                            stdout=open(f"{tag}.log", "w"),
                            stderr=subprocess.STDOUT).returncode
        print(f"\n=== {tag}: exit {rc} in {time.time()-t:.0f}s", flush=True)
        if rc:
            return {}
    out = {}
    recs = dq.load(tag)
    for i in dq.peaks(recs):
        r = recs[i]
        out[dq.identify(r)] = r
        print(f"  {dq.identify(r)}: f={r['f']:.5f}  Q0={r['Q0']:,.0f}  "
              f"|S11|={r['s_db']:.2f} dB", flush=True)
    return out


tot = run("tilt45", 1.0e-4, "sigma")          # cached
wall = run("t45nodiel", 0.0, "sigma")         # Q_wall alone
diel = run("t45pecdiel", 1.0e-4, "pec")       # Q_diel alone

print("\n" + "=" * 72)
print(f"{'mode':<8}{'Q_wall meas':>13}{'closed form':>13}{'ratio':>8}"
      f"{'Q_diel':>12}{'Q_total':>11}{'closure':>9}")
print("-" * 72)
for m in ("TE011", "TM020"):
    if m not in wall:
        print(f"{m:<8}  missing from the lossless run"); continue
    qw = wall[m]["Q0"]
    cf = CLOSED[m]
    row = f"{m:<8}{qw:>13,.0f}{cf:>13,.0f}{cf/qw:>8.2f}"
    if m in diel and m in tot:
        qd = diel[m]["Q0"]
        pred = 1 / (1 / qw + 1 / qd)
        row += f"{qd:>12,.0f}{tot[m]['Q0']:>11,.0f}{tot[m]['Q0']/pred:>9.3f}"
    print(row)
print("""
Reading it: if the closed form now matches Q_wall for BOTH modes, the closed
forms were never mode-dependent and the 1.15x was dielectric loss that TM020
feels 74x more strongly than TE011. If TM020 still sits 15% off with the
dielectric removed, the closed form really is worse for TM020 and the ignition
field inherits that.""")
