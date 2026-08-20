#!/usr/bin/env python3
"""R10 — does Q's order-independence survive a plasma load?

R3 found Q moves only 0.6% between order 1 and 2 UNLOADED, because Q is a ratio
of energies over the same field and discretisation error is common-mode. A lossy
plasma is exactly where that might break: the loss is now a VOLUME term in the
bore, not a surface term on the walls, and it is concentrated where the mesh is
coarsest relative to the field gradient.

Palace's Material accepts Conductivity (S/m), which "activates the Ohmic loss
model in this domain" — so the plasma goes in as a conducting bore.

Sigma for an atmospheric N2 microwave plasma: sigma = n_e e^2/(m_e nu), with
nu ~ 1e12 /s and n_e ~ 1e20-1e21 /m^3, giving ~3-30 S/m. Swept 10/30/100 to
bracket it.

⚠️ This is a CRUDE plasma: uniform conductivity filling the whole bore column,
no self-consistency, no thermal or chemical model, and the real discharge is a
torus occupying part of that volume. It cannot predict plasma behaviour. It CAN
answer the numerical question asked, and it gives a first bound on Q_plasma —
which sec 2c of architecture-comparison.md currently ASSUMES as 200-500.

Bonus question it also answers: TE011 carries only 0.054% of its electric energy
in the bore against TM020's 3.978%. Whether that is enough to load appreciably is
visible directly in the loaded Q.
"""
import json, pathlib, subprocess, sys, time
import dq

PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
BASE = json.loads(pathlib.Path("driven-tilt45.json").read_text())
TAG_BORE = 1
UNLOADED = {"TE011": 45640, "TM020": 23169}


def run(tag, sigma, order):
    c = json.loads(json.dumps(BASE))
    c["Problem"]["Output"] = f"postpro/{tag}"
    c["Solver"]["Order"] = order
    for m in c["Domains"]["Materials"]:
        if m["Attributes"] == [TAG_BORE]:
            m["Conductivity"] = sigma
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    if not pathlib.Path(f"postpro/{tag}/port-S.csv").exists():
        t = time.time()
        rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"],
                            stdout=open(f"{tag}.log", "w"),
                            stderr=subprocess.STDOUT).returncode
        print(f"\n=== {tag} (sigma={sigma}, order {order}): exit {rc} "
              f"in {time.time()-t:.0f}s", flush=True)
        if rc:
            print(f"  FAILED — see {tag}.log"); return {}
    else:
        print(f"\n=== {tag}: already solved", flush=True)
    out = {}
    recs = dq.load(tag)
    for i in dq.peaks(recs):
        r = recs[i]
        m = dq.identify(r)
        out[m] = r
        qu = UNLOADED[m]
        # 1/Q_loaded = 1/Q_unloaded + 1/Q_plasma
        qp = 1 / (1 / r["Q0"] - 1 / qu) if r["Q0"] < qu else float("inf")
        frac = (1 / qp) / (1 / r["Q0"]) if qp != float("inf") else 0.0
        print(f"  {m}: f={r['f']:.5f}  Q0={r['Q0']:>8,.0f}  "
              f"Q_plasma={qp:>10,.0f}  plasma takes {frac*100:>5.1f}% of loss",
              flush=True)
    return out


res = {}
for s in (10.0, 30.0, 100.0):
    res[s] = run(f"pl{int(s)}o1", s, 1)

print("\n" + "=" * 70)
print("ORDER-1 SUMMARY — power reaching the plasma vs bore conductivity")
print(f"{'sigma':>8}{'TE011 Q0':>11}{'TE011 %':>10}{'TM020 Q0':>11}{'TM020 %':>10}")
for s, r in res.items():
    row = f"{s:>8.0f}"
    for m in ("TE011", "TM020"):
        if m in r:
            qu = UNLOADED[m]
            qp = 1 / (1 / r[m]["Q0"] - 1 / qu) if r[m]["Q0"] < qu else float("inf")
            f = (1 / qp) / (1 / r[m]["Q0"]) * 100 if qp != float("inf") else 0.0
            row += f"{r[m]['Q0']:>11,.0f}{f:>9.1f}%"
        else:
            row += f"{'—':>11}{'—':>10}"
    print(row)
print("""
Then order 2 at sigma=30 answers R10 proper: if Q moves ~1% as it did unloaded,
volume loss is common-mode too and every order-1 loaded result is usable.""")
