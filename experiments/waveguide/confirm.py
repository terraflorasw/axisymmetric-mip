#!/usr/bin/env python3
"""Confirm a single design point, full Fassel torch. Reports band margins.

The retune is arithmetic from the measured orthogonal sensitivities
(-23 MHz/mm on a for the ignition mode; -12 MHz/mm on a and -14 MHz/mm on L
for TE011). This checks it against a solve.
"""
import argparse, json, math, os, pathlib, subprocess, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse import read_csv, fnum

HOME = pathlib.Path.home()
MM, PALACE = HOME/".local/bin/micromamba", HOME/".local/opt/palace/bin/palace"
ENV = {**os.environ,
       "PATH": f"{HOME}/.local/share/mamba/envs/emsim/bin:{os.environ['PATH']}",
       "MAMBA_ROOT_PREFIX": str(HOME/".local/share/mamba")}
run = lambda c: subprocess.run(c, env=ENV, capture_output=True, text=True)
ISM_LO, ISM_HI = 2.400, 2.500

ap = argparse.ArgumentParser()
ap.add_argument("--radius", type=float, required=True)
ap.add_argument("--length", type=float, required=True)
ap.add_argument("--brake", type=float, default=3.0)
ap.add_argument("--order", type=int, default=1)
ap.add_argument("--tag", default=None)
ap.add_argument("--target", type=float, default=None)
ap.add_argument("--n", type=int, default=None)
ap.add_argument("--config", default="inj-base.json",
                help="base config; sigma-base.json for finite conductivity")
ap.add_argument("--size", type=float, default=None,
                help="pin the mesh size factor (h-refinement study)")
a = ap.parse_args()
tag = a.tag or f"c{a.radius:.2f}_{a.length:.2f}_b{a.brake:.1f}_o{a.order}".replace(".", "p")

g = None
# Pinning a single size factor removes the curving-failure retry, and gmsh
# aborts the process (SIGABRT) rather than raising. So a pinned size still
# gets nearby fallbacks: close enough to stay "the finer mesh", different
# enough in element topology to dodge the pathological element.
FACS = ([f"{a.size*m:.4f}" for m in (1.0, 0.97, 1.03, 0.94)]
        if a.size else ("1.00", "0.96", "1.06", "0.90"))
for fac in FACS:
    g = run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
             "--out", f"{tag}.msh", "--radius", f"{a.radius}",
             "--length", f"{a.length}", "--brake", f"{a.brake}",
             "--order", "2", "--size-factor", fac])
    if g.returncode == 0:
        if fac != "1.00": print(f"  (mesh needed size-factor {fac})")
        break
if g.returncode != 0:
    print(f"MESH FAIL\n{g.stdout[-600:]}{g.stderr[-400:]}"); sys.exit(1)

cfg = json.loads(pathlib.Path(a.config).read_text())
cfg["Model"]["Mesh"] = f"{tag}.msh"
cfg["Solver"]["Order"] = a.order
cfg["Problem"]["Output"] = f"postpro/{tag}"
if a.target is not None: cfg["Solver"]["Eigenmode"]["Target"] = a.target
if a.n is not None: cfg["Solver"]["Eigenmode"]["N"] = a.n
pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg, indent=2))

s = run([str(PALACE), "-np", "4", f"{tag}.json"])
if s.returncode != 0:
    print(f"SOLVE FAIL\n{s.stdout[-600:]}"); sys.exit(1)

d = pathlib.Path(f"postpro/{tag}")
eig, en = read_csv(d/"eig.csv"), read_csv(d/"domain-E.csv")
n = min(len(eig), len(en))
def sec_cv(i):
    v = [(fnum(en[i], f"E_elec[{k}]") or 0) + (fnum(en[i], f"E_mag[{k}]") or 0)
         for k in range(3, 8)]
    m = sum(v)/len(v)
    return math.sqrt(sum((x-m)**2 for x in v)/len(v))/m if m > 0 else float("nan")
op = max(range(n), key=lambda i: fnum(en[i], "p_mag[1]") or 0)
ig = max(range(n), key=lambda i: fnum(en[i], "p_elec[1]") or 0)
fo, fi = fnum(eig[op], "Re{f}", default=0), fnum(eig[ig], "Re{f}", default=0)
print(f"\ngeometry: a={a.radius} mm  L={a.length} mm  brake={a.brake} mm  order={a.order}")
print(f"  TE011    {fo:.4f} GHz   cv {sec_cv(op):.4f}   Q {fnum(eig[op],'Q',default=0):,.0f}")
print(f"  ignition {fi:.4f} GHz   plasmaE {(fnum(en[ig],'p_elec[1]') or 0)*100:.3f}%"
      f"   Q {fnum(eig[ig],'Q',default=0):,.0f}")
print(f"  split    {1000*(fi-fo):+.0f} MHz")
mo, mi = 1000*(ISM_HI-fo), 1000*(fi-ISM_LO)
print(f"\nband margins: TE011 {mo:+.1f} MHz to 2.500 | ignition {mi:+.1f} MHz to 2.400")
print(f"  worst case  TE011 {mo-3.4:+.1f} (cold, tolerance)"
      f" | ignition {mi-6.4-4.0:+.1f} (hot 100 K + tolerance)")
ok = mo-3.4 > 5 and mi-10.4 > 5 and abs(1000*(fi-fo)) > 30 and sec_cv(op) < 0.02
print(f"\nVERDICT: {'PASS' if ok else 'MARGINAL/FAIL'}"
      f"  (need >5 MHz worst-case both edges, |split|>30 MHz, cv<0.02)")
