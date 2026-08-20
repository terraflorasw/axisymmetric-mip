#!/usr/bin/env python3
"""Loop-size sweep: grow the coupling loop until Re(Z) at resonance ~ 50 ohm.

Uses Re(Z) rather than Q_ext because the one-port Q extraction has an
over/undercoupled branch ambiguity that Re(Z) does not.
"""
import cmath, csv, json, math, os, pathlib, subprocess, sys
HOME=pathlib.Path.home(); MM=HOME/".local/bin/micromamba"; PALACE=HOME/".local/opt/palace/bin/palace"
ENV={**os.environ,"PATH":f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
     "MAMBA_ROOT_PREFIX":str(HOME/".local/share/mamba")}
run=lambda c: subprocess.run(c,env=ENV,capture_output=True,text=True)
base=json.loads(pathlib.Path("driven.json").read_text())
Z0=50.0
CASES=[(12,8.5),(24,17),(36,25)]      # depth, half-width in mm -> area 204, 816, 1800 mm^2
print(f"{'d x 2w (mm)':>14}{'area mm^2':>11}{'f0 (GHz)':>11}{'Rmax':>9}{'X at Rmax':>11}")
for d,w in CASES:
    tag=f"lp{d}x{int(2*w)}"
    ok=False
    for fac in ("1.00","0.96","1.06"):
        g=run([str(MM),"run","-n","emsim","python","geometry.py","--out",f"{tag}.msh",
               "--radius","101.43","--length","87.67","--brake","3","--sectors","1",
               "--loop",f"{d},{w},1,0.3","--order","2","--size-factor",fac])
        if g.returncode==0: ok=True; break
    if not ok:
        print(f"{f'{d} x {2*w}':>14}  MESH FAIL"); continue
    cfg=json.loads(json.dumps(base))
    cfg["Model"]["Mesh"]=f"{tag}.msh"; cfg["Problem"]["Output"]=f"postpro/{tag}"
    cfg["Solver"]["Driven"]["Samples"]=[{"Type":"Linear","MinFreq":2.40,"MaxFreq":2.50,
                                         "FreqStep":0.00002}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg,indent=2))
    s=run([str(PALACE),"-np","4",f"{tag}.json"])
    if s.returncode!=0:
        print(f"{f'{d} x {2*w}':>14}  SOLVE FAIL {s.stdout[-150:]}"); continue
    f_,mg,ph=[],[],[]
    with open(f"postpro/{tag}/port-S.csv") as fh:
        r=csv.reader(fh); next(r)
        for a in r:
            if len(a)>=3: f_.append(float(a[0])); mg.append(float(a[1])); ph.append(float(a[2]))
    def Z(i):
        G=10**(mg[i]/20)*cmath.exp(1j*math.radians(ph[i])); return Z0*(1+G)/(1-G)
    i0=max(range(len(f_)), key=lambda i: Z(i).real)
    z=Z(i0)
    print(f"{f'{d} x {2*w}':>14}{2*d*w:>11.0f}{f_[i0]:>11.5f}{z.real:>9.1f}{z.imag:>11.1f}", flush=True)
