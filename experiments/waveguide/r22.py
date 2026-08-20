#!/usr/bin/env python3
"""R22 — can TE011 even SEE a plasma that TM020 created on axis?

TM020's E_z peaks on axis, so it ignites a central column. TE011's E_phi is zero
on axis and wants an annulus. R12 measured the annular case (r 4.5-8.5) at 100%
of the full-bore shift, which implies the core contributes nothing. This runs the
complement -- plasma ONLY in the core -- and if that also shows ~0%, then a
TM020-ignited plasma is invisible to TE011 and the mode-shift scheme has a
bootstrap problem: the operating mode cannot grab what the ignition mode made.

Reference is the matched zero-conductivity run on the same mesh, as R12 required.
"""
import json, pathlib, subprocess, sys, time
import dq
MM=pathlib.Path.home()/".local/bin/micromamba"
PALACE=str(pathlib.Path.home()/".local/opt/palace/bin/palace")
BASE=json.loads(pathlib.Path("driven-tilt45.json").read_text())
for fac in ("1.00","0.96","1.06","0.90"):
    g=subprocess.run([str(MM),"run","-n","emsim","python","geometry.py","--out","core.msh",
        "--radius","101.43","--length","87.67","--brake","3","--sectors","1","--order","2",
        "--size-factor",fac,"--loop","12,8.5,1,0.3","--loop-tilt","45",
        "--plasma","0.0,4.5,-20.0,10.0"],capture_output=True,text=True)
    if g.returncode==0: print(f"core.msh built at size-factor {fac}"); break
else: print("MESH FAIL"); raise SystemExit
out={}
for tag,sig in (("coreref",None),("core30",30.0)):
    c=json.loads(json.dumps(BASE)); c["Model"]["Mesh"]="core.msh"
    c["Problem"]["Output"]=f"postpro/{tag}"
    m={"Attributes":[12],"Permittivity":1.0,"Permeability":1.0}
    if sig: m["Conductivity"]=sig
    c["Domains"]["Materials"].append(m)
    c["Solver"]["Driven"]["Samples"]=[{"Type":"Linear","MinFreq":2.42,"MaxFreq":2.50,"FreqStep":5e-5}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c,indent=2))
    rc=subprocess.run([PALACE,"-np","3",f"{tag}.json"],stdout=open(f"{tag}.log","w"),
                      stderr=subprocess.STDOUT).returncode
    r={x["mode"]:x for x in dq.report(tag)} if rc==0 else {}
    out[tag]=r.get("TE011")
    print(f"  {tag}: " + (f"f={out[tag]['f']:.5f} Q0={out[tag]['Q0']:,.0f}" if out[tag] else f"not found rc={rc}"),flush=True)
a,b=out.get("coreref"),out.get("core30")
if a and b:
    print("\n"+"="*66)
    print(f"  core-only plasma (r<4.5mm), sigma=30:")
    print(f"     shift {(b['f']-a['f'])*1000:+.2f} MHz   vs full-bore +21.1, annular +21.2")
    print(f"     Q0 {a['Q0']:,.0f} -> {b['Q0']:,.0f}  ({(b['Q0']/a['Q0']-1)*100:+.1f}%)")
    print(f"     vs full-bore Q collapse 45,640 -> 192 (-99.6%)")
