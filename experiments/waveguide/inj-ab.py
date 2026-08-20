#!/usr/bin/env python3
"""A/B the torch model: outer tube only vs full Fassel assembly.

The injector sits ON AXIS, where TM020's E_z peaks, so it displaces gas from
the highest-field region. Attribute 1 is the PLASMA ZONE (clear bore
downstream of the intermediate tube), not the whole tube.
"""
import json, math, os, pathlib, re, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse import read_csv, fnum
HOME=pathlib.Path.home(); MM=HOME/".local/bin/micromamba"; PALACE=HOME/".local/opt/palace/bin/palace"
ENV={**os.environ,"PATH":f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
     "MAMBA_ROOT_PREFIX":str(HOME/".local/share/mamba")}
run=lambda c: subprocess.run(c,env=ENV,capture_output=True,text=True)
base=json.loads(pathlib.Path("inj-base.json").read_text())
rows=[]
for tag, extra in (("outer", ["--no-inner"]), ("fassel", [])):
    args=[str(MM),"run","-n","emsim","python","geometry.py","--out",f"tj_{tag}.msh",
          "--radius","102","--length","85","--brake","3","--order","2"]+extra
    ok=False
    for fac in ("1.00","0.96","1.06","0.90"):
        g=run(args+["--size-factor",fac])
        if g.returncode==0: ok=True; break
    if not ok:
        print(f"{tag}: MESH FAIL {g.stdout[-300:]}"); continue
    cfg=json.loads(json.dumps(base))
    cfg["Model"]["Mesh"]=f"tj_{tag}.msh"; cfg["Problem"]["Output"]=f"postpro/tj_{tag}"
    pathlib.Path(f"tj_{tag}.json").write_text(json.dumps(cfg,indent=2))
    s=run([str(PALACE),"-np","4",f"tj_{tag}.json"])
    if s.returncode!=0:
        print(f"{tag}: SOLVE FAIL {s.stdout[-300:]}"); continue
    d=pathlib.Path(f"postpro/tj_{tag}"); eig,en=read_csv(d/"eig.csv"),read_csv(d/"domain-E.csv")
    ig=max(range(min(len(eig),len(en))), key=lambda i: fnum(en[i],"p_elec[1]") or 0)
    op=max(range(min(len(eig),len(en))), key=lambda i: fnum(en[i],"p_mag[1]") or 0)
    rows.append((tag, fnum(eig[op],"Re{f}",default=0), fnum(eig[ig],"Re{f}",default=0),
                 (fnum(en[ig],"p_elec[1]") or 0)*100, fnum(eig[ig],"Q",default=0)))
    print(f"{tag:>7}: TE011={rows[-1][1]:.4f}  ignition={rows[-1][2]:.4f}  "
          f"plasmaE={rows[-1][3]:.3f}%  Q={rows[-1][4]:,.0f}", flush=True)
print("\n"+"="*72)
print(f"{'torch':>8} {'TE011':>9} {'ignition':>9} {'split(MHz)':>11} {'plasmaE%':>10}")
print("-"*72)
for t,o,i,pe,q in rows:
    print(f"{t:>8} {o:>9.4f} {i:>9.4f} {1000*(i-o):>+11.0f} {pe:>10.3f}")
if len(rows)==2:
    print("="*72)
    dte=1000*(rows[1][1]-rows[0][1]); dig=1000*(rows[1][2]-rows[0][2])
    print(f"inner tubes shift TE011 {dte:+.0f} MHz, ignition {dig:+.0f} MHz")
    print(f"plasma-zone E fraction {rows[0][3]:.3f}% -> {rows[1][3]:.3f}% "
          f"({rows[1][3]/rows[0][3]:.3f}x, field x{math.sqrt(rows[1][3]/rows[0][3]):.3f})")
