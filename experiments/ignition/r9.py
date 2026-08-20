#!/usr/bin/env python3
"""R9 — how much of the ring's Q is hostage to the placeholder alumina tand?

R5 measured the ring at tand = 1e-4 for BOTH alumina and quartz and got
Q_wall 103,586 || Q_diel 11,081 = Q_total 10,011. The alumina figure is a
placeholder (ignition-study.md §9 q1) and the ring's Q is dielectric-dominated,
so every ring-vs-AMIP number rests on it -- including Q x eta = 43.0 vs 41.5.

Dielectric loss should be analytic: 1/Q_diel = sum_i p_elec[i] * tand_i, so
scaling the alumina tand by k gives

    Q_diel(k) = 1 / ((0.888*k + 0.0143) * 1e-4)

That is a PREDICTION, and R5's whole lesson is that predictions about extraction
get validated before they are trusted. Two solves at k = 0.5 and k = 2 test it.
If they land, the analytic curve is used for the rest instead of more solves.
"""
import json, pathlib, subprocess, sys, time
sys.path.insert(0, "../waveguide")
import dq

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
P_ALU, P_QTZ = 0.888, 0.0143          # electric-energy fractions, from the eigenmode
BASE = json.loads(pathlib.Path("total.json").read_text())
Q_WALL = 103586.0


def predict(k):
    qd = 1.0 / ((P_ALU * k + P_QTZ) * 1e-4)
    return qd, 1.0 / (1.0 / Q_WALL + 1.0 / qd)


print(f"{'k':>6}{'tand_alu':>11}{'Q_diel pred':>13}{'Q_tot pred':>12}"
      f"{'Q_tot meas':>12}{'agree':>8}")
print("-" * 62)
for k in (0.5, 2.0):
    tag = f"r9k{k}".replace(".", "p")
    c = json.loads(json.dumps(BASE))
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Domains"]["Materials"][0]["LossTan"] = 1.0e-4 * k      # alumina only
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    if not pathlib.Path(f"postpro/{tag}/port-S.csv").exists():
        rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"],
                            stdout=open(f"{tag}.log", "w"),
                            stderr=subprocess.STDOUT).returncode
        if rc:
            print(f"{k:>6}  FAILED, see {tag}.log"); continue
    recs = dq.load(tag)
    pk = dq.peaks(recs)
    if not pk:
        print(f"{k:>6}  no resonance"); continue
    r = max((recs[i] for i in pk), key=lambda x: x["U"])
    qd, qt = predict(k)
    print(f"{k:>6}{1e-4*k:>11.1e}{qd:>13,.0f}{qt:>12,.0f}{r['Q0']:>12,.0f}"
          f"{r['Q0']/qt:>8.3f}")

print("\nif the model holds, the ring's exposure across plausible alumina grades:")
print(f"  {'tand':>9}{'Q_diel':>10}{'Q_total':>10}{'Q x eta':>10}{'vs AMIP 41.5':>14}")
for t in (5e-5, 1e-4, 2e-4, 5e-4):
    qd, qt = predict(t / 1e-4)
    qe = qt * 0.0043
    print(f"  {t:>9.1e}{qd:>10,.0f}{qt:>10,.0f}{qe:>10.1f}{qe/41.5:>13.2f}x")
