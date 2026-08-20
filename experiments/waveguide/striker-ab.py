#!/usr/bin/env python3
"""A/B the annular striker: does its field enhancement reach the bore gas?

Measured as the bore's share of the mode's ELECTRIC energy, with and without
the ridge. If the enhancement is confined outside the torch, the bore share is
unchanged and the striker is useless for ignition however large its local field.
"""
import json, math, os, pathlib, re, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse import read_csv, fnum

HOME = pathlib.Path.home()
MM = HOME/".local/bin/micromamba"; PALACE = HOME/".local/opt/palace/bin/palace"
ENV = {**os.environ, "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME/".local/share/mamba")}
run = lambda c: subprocess.run(c, env=ENV, capture_output=True, text=True)

CASES = [("none", None), ("h5r1", "5,1,11"), ("h5r25", "5,2.5,12.5"), ("h8r25", "8,2.5,12.5")]
base = json.loads(re.sub(r'(^|\s)//[^\n]*', '', pathlib.Path("eigenmode.json").read_text()))
rows = []
for tag, spec in CASES:
    args = [str(MM),"run","-n","emsim","python","geometry.py","--out",f"st_{tag}.msh",
            "--radius","102","--length","85","--order","2"]
    if spec: args += ["--striker", spec]
    ok = False
    for fac in ("1.00","0.96","1.06"):
        g = run(args + ["--size-factor", fac])
        if g.returncode == 0: ok = True; break
    if not ok:
        print(f"{tag}: MESH FAIL"); continue
    cfg = json.loads(json.dumps(base))
    cfg["Model"]["Mesh"] = f"st_{tag}.msh"; cfg["Solver"]["Order"] = 1
    cfg["Solver"]["Eigenmode"].update({"Target":2.0,"N":14,"Save":0})
    cfg["Problem"]["Output"] = f"postpro/st_{tag}"
    pathlib.Path(f"st_{tag}.json").write_text(json.dumps(cfg, indent=2))
    s = run([str(PALACE),"-np","4",f"st_{tag}.json"])
    if s.returncode != 0:
        print(f"{tag}: SOLVE FAIL {s.stdout[-200:]}"); continue
    d = pathlib.Path(f"postpro/st_{tag}")
    eig, en = read_csv(d/"eig.csv"), read_csv(d/"domain-E.csv")
    best = max(range(min(len(eig),len(en))), key=lambda i: fnum(en[i],"p_elec[1]") or 0)
    f = fnum(eig[best],"Re{f}",default=0); pe = fnum(en[best],"p_elec[1]") or 0
    q = fnum(eig[best],"Q",default=0)
    rows.append((tag, spec or "-", f, pe*100, q))
    print(f"{tag:>7} {spec or '-':>10}  ignition f={f:.4f}  boreE={pe*100:.3f}%  Q={q:,.0f}", flush=True)

print("\n" + "="*70)
print(f"{'case':>7} {'h,rtip,r':>12} {'f(GHz)':>9} {'boreE%':>9} {'vs none':>9}")
print("-"*70)
b0 = rows[0][3] if rows else 1
for tag, spec, f, pe, q in rows:
    print(f"{tag:>7} {spec:>12} {f:>9.4f} {pe:>9.3f} {pe/b0:>8.2f}x")
print("="*70)
print("field enhancement in the bore = sqrt(boreE ratio), since E ~ sqrt(energy)")
for tag, spec, f, pe, q in rows[1:]:
    print(f"  {tag}: bore field x{math.sqrt(pe/b0):.2f}")
