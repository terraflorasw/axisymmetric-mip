#!/usr/bin/env python3
"""Unattended recheck queue: R2, R6, R3. Each step logs and continues on failure."""
import json, math, os, pathlib, subprocess, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
HOME=pathlib.Path.home(); MM=HOME/".local/bin/micromamba"; PALACE=HOME/".local/opt/palace/bin/palace"
ENV={**os.environ,"PATH":f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
     "MAMBA_ROOT_PREFIX":str(HOME/".local/share/mamba")}
run=lambda c: subprocess.run(c,env=ENV,capture_output=True,text=True)
base=json.loads(pathlib.Path("driven-sigma.json").read_text())
Q_DIEL_TE = 1.768472e6

def solve(tag, cfg):
    pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg,indent=2))
    t=time.monotonic(); s=run([str(PALACE),"-np","4",f"{tag}.json"])
    if s.returncode!=0:
        print(f"  {tag}: SOLVE FAIL\n{s.stdout[-400:]}", flush=True); return None
    print(f"  {tag}: solved in {time.monotonic()-t:.0f}s", flush=True)
    return dq.report(tag)

def mesh(tag, extra):
    for fac in ("1.00","0.96","1.06","0.90","0.85"):
        g=run([str(MM),"run","-n","emsim","python","geometry.py","--out",f"{tag}.msh",
               "--radius","101.43","--length","87.67","--brake","3","--sectors","1",
               "--order","2","--size-factor",fac]+extra)
        if g.returncode==0:
            if fac!="1.00": print(f"  {tag}: mesh ok at size-factor {fac}", flush=True)
            return True
    print(f"  {tag}: MESH FAIL at every size factor", flush=True); return False

print("="*70); print("R2 — does Palace's Conductivity BC scale as Q_wall ~ sqrt(sigma)?"); print("="*70)
Q0_base=90323
Qw_base=1/(1/Q0_base-1/Q_DIEL_TE)
print(f"  baseline sigma=6.3e7: Q0={Q0_base:,}  ->  implied Q_wall={Qw_base:,.0f}")
print(f"  at 4x sigma, theory says Q_wall doubles -> Q0 = "
      f"{1/(1/(2*Qw_base)+1/Q_DIEL_TE):,.0f}", flush=True)
cfg=json.loads(json.dumps(base)); cfg["Model"]["Mesh"]="ls12x17.msh"
cfg["Problem"]["Output"]="postpro/sig4x"
cfg["Boundaries"]["Conductivity"][0]["Conductivity"]=2.52e8
cfg["Solver"]["Driven"]["Samples"]=[{"Type":"Linear","MinFreq":2.4460,"MaxFreq":2.4560,"FreqStep":0.00001}]
r=solve("sig4x",cfg)
if r:
    for m in r:
        Qw=1/(1/m["Q0"]-1/Q_DIEL_TE) if m["Q0"]<Q_DIEL_TE else float('inf')
        print(f"  MEASURED {m['mode']}: Q0={m['Q0']:,.0f}  Q_wall={Qw:,.0f}  "
              f"ratio to baseline Q_wall = {Qw/Qw_base:.2f}x   (theory: 2.00x)", flush=True)

print(); print("="*70); print("R6 — viewport effect on the IGNITION mode TM020"); print("="*70)
if mesh("tiltvp", ["--loop","12,8.5,1,0.3","--loop-tilt","45","--viewport","25"]):
    cfg=json.loads(json.dumps(base)); cfg["Model"]["Mesh"]="tiltvp.msh"
    cfg["Problem"]["Output"]="postpro/tiltvp"
    k=math.cos(math.radians(45)); cfg["Boundaries"]["LumpedPort"][0]["Direction"]=[0.0,k,k]
    cfg["Solver"]["Driven"]["Samples"]=[{"Type":"Linear","MinFreq":2.40,"MaxFreq":2.50,"FreqStep":0.00002}]
    cfg["Solver"]["Driven"]["AdaptiveMaxSamples"]=40
    r=solve("tiltvp",cfg)
    if r:
        ref={m["mode"]:m for m in dq.report("tilt45")}
        for m in r:
            b=ref.get(m["mode"])
            d=f"  ΔQ={100*(m['Q0']/b['Q0']-1):+.1f}%  Δf={1000*(m['f']-b['f']):+.1f} MHz" if b else ""
            print(f"  {m['mode']}: f={m['f']:.5f}  Q0={m['Q0']:,.0f}{d}", flush=True)

print(); print("="*70); print("R3 — does DRIVEN converge at order 2, where eigensolves failed 3x?"); print("="*70)
cfg=json.loads(json.dumps(base)); cfg["Model"]["Mesh"]="ls12x17.msh"
cfg["Problem"]["Output"]="postpro/o2drv"; cfg["Solver"]["Order"]=2
cfg["Solver"]["Driven"]["Samples"]=[{"Type":"Linear","MinFreq":2.4400,"MaxFreq":2.4700,"FreqStep":0.00002}]
t=time.monotonic(); r=solve("o2drv",cfg)
if r:
    ref={m["mode"]:m for m in dq.report("sigdrv")}
    for m in r:
        b=ref.get(m["mode"])
        d=f"   vs order 1: Δf={1000*(m['f']-b['f']):+.1f} MHz, ΔQ={100*(m['Q0']/b['Q0']-1):+.1f}%" if b else ""
        print(f"  {m['mode']}: f={m['f']:.5f}  Q0={m['Q0']:,.0f}{d}", flush=True)
    print("  -> order-2 IS reachable by driven analysis", flush=True)
print("\nqueue complete", flush=True)
