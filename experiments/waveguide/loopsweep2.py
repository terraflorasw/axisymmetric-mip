#!/usr/bin/env python3
"""Loop-size sweep, measuring Q_ext from LINEWIDTH.

Two stages per size, because the loop is a large perturbation and moves the
resonance out of any fixed window:
  1. coarse scan to locate f0
  2. zoom around it at fine resolution to resolve the linewidth

Q_L comes from the half-power width of the |S11| dip — robust — and
Q_ext follows from 1/Q_L = 1/Q0 + 1/Q_ext with Q0 from the eigenmode solve.
Re(Z) is NOT used: it is ill-conditioned when |Gamma| -> 1 and gave a 190x
spread on the same loop (see FINDINGS).
"""
import cmath, csv, json, math, os, pathlib, subprocess, sys
HOME=pathlib.Path.home(); MM=HOME/".local/bin/micromamba"; PALACE=HOME/".local/opt/palace/bin/palace"
ENV={**os.environ,"PATH":f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
     "MAMBA_ROOT_PREFIX":str(HOME/".local/share/mamba")}
run=lambda c: subprocess.run(c,env=ENV,capture_output=True,text=True)
base=json.loads(pathlib.Path("driven.json").read_text())
Q0_UNLOADED=1.768472e6          # TE011, PEC walls + dielectric, from eigenmode

def sweep(tag, mesh, lo, hi, step, series_C=None):
    cfg=json.loads(json.dumps(base))
    cfg["Model"]["Mesh"]=mesh; cfg["Problem"]["Output"]=f"postpro/{tag}"
    cfg["Solver"]["Driven"]["Samples"]=[{"Type":"Linear","MinFreq":lo,"MaxFreq":hi,
                                         "FreqStep":step}]
    if series_C is not None:
        cfg["Boundaries"]["LumpedPort"][0]["C"]=series_C
    pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg,indent=2))
    s=run([str(PALACE),"-np","4",f"{tag}.json"])
    if s.returncode!=0: return None
    f_,mg=[],[]
    with open(f"postpro/{tag}/port-S.csv") as fh:
        r=csv.reader(fh); next(r)
        for a in r:
            if len(a)>=2: f_.append(float(a[0])); mg.append(float(a[1]))
    return f_,mg

def analyse(f_,mg):
    i0=min(range(len(mg)), key=lambda i: mg[i])
    f0,s0=f_[i0],mg[i0]; G0=10**(s0/20)
    targ=(1+G0**2)/2
    lo=hi=None
    for i in range(1,len(f_)):
        p1,p2=10**(mg[i-1]/10),10**(mg[i]/10)
        if (p1-targ)*(p2-targ)<0:
            fx=f_[i-1]+(f_[i]-f_[i-1])*(targ-p1)/(p2-p1)
            if fx<f0: lo=fx
            elif hi is None: hi=fx
    QL=f0/(hi-lo) if (lo and hi) else None
    return f0,s0,QL

CASES=[(12,8.5),(20,14),(28,20),(36,26)]
print(f"{'d x 2w':>12}{'area':>8}{'f0 (GHz)':>11}{'|S11|dB':>9}{'Q_L':>10}{'Q_ext':>12}")
for d,w in CASES:
    tag=f"ls{d}x{int(2*w)}"
    ok=False
    for fac in ("1.00","0.96","1.06"):
        g=run([str(MM),"run","-n","emsim","python","geometry.py","--out",f"{tag}.msh",
               "--radius","101.43","--length","87.67","--brake","3","--sectors","1",
               "--loop",f"{d},{w},1,0.3","--order","2","--size-factor",fac])
        if g.returncode==0: ok=True; break
    if not ok: print(f"{f'{d}x{2*w}':>12}  MESH FAIL", flush=True); continue
    r1=sweep(f"{tag}c", f"{tag}.msh", 2.30, 2.50, 0.001)      # coarse locate
    if not r1: print(f"{f'{d}x{2*w}':>12}  COARSE FAIL", flush=True); continue
    f0c,_,_=analyse(*r1)
    r2=sweep(f"{tag}z", f"{tag}.msh", f0c-0.004, f0c+0.004, 0.00001)  # zoom
    if not r2: print(f"{f'{d}x{2*w}':>12}  ZOOM FAIL", flush=True); continue
    f0,s0,QL=analyse(*r2)
    if QL:
        Qe=1/(1/QL-1/Q0_UNLOADED) if QL<Q0_UNLOADED else float('inf')
        print(f"{f'{d}x{2*w}':>12}{2*d*w:>8.0f}{f0:>11.5f}{s0:>9.3f}{QL:>10,.0f}{Qe:>12,.0f}", flush=True)
    else:
        print(f"{f'{d}x{2*w}':>12}{2*d*w:>8.0f}{f0:>11.5f}{s0:>9.3f}    linewidth not bracketed", flush=True)
