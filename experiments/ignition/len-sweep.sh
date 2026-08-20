#!/usr/bin/env bash
set -e
export MAMBA_ROOT_PREFIX="$HOME/.local/share/mamba"
export PATH="$HOME/.local/share/mamba/envs/emsim/bin:$PATH"
for L in 60 90 120 200 300; do
  "$HOME/.local/bin/micromamba" run -n emsim python geometry.py \
     --encl-dia 100 --encl-len $L --out mL$L.msh --order 1 >/dev/null 2>&1
  python3 - <<PY
import json,re,pathlib
c=json.loads(re.sub(r'(^|\s)//[^\n]*','',pathlib.Path("eigenmode.json").read_text()))
c["Model"]["Mesh"]="mL$L.msh"; c["Solver"]["Order"]=1
c["Solver"]["Eigenmode"].update({"Target":1.2,"N":16,"Save":0})
c["Problem"]["Output"]="postpro/L$L"
pathlib.Path("L$L.json").write_text(json.dumps(c,indent=2))
PY
  "$HOME/.local/opt/palace/bin/palace" -np 4 L$L.json >/dev/null 2>&1
  echo -n "len=${L}mm  "
  "$HOME/.local/bin/micromamba" run -n emsim python - <<PY
import sys,pathlib; sys.path.insert(0,".")
from analyse import read_csv,fnum,group_degenerate
d=pathlib.Path("postpro/L$L"); eig=read_csv(d/"eig.csv"); en=read_csv(d/"domain-E.csv")
f=[fnum(r,"Re{f}",default=0) for r in eig]
m0={i for g in group_degenerate(f) if len(g)==1 for i in g}
best=None
for i in range(min(len(eig),len(en))):
    pe=fnum(en[i],"p_elec[2]") or 0; pm=fnum(en[i],"p_mag[2]") or 0
    ee=fnum(en[i],"E_elec[1]") or 0; eh=fnum(en[i],"E_mag[1]") or 0
    if (pe+pm)/2>0.25 and i in m0 and eh>0 and ee/eh<0.5:
        if best is None or f[i]<best[0]: best=(f[i],(pe+pm)/2)
print(f"ring TE = {best[0]:.4f} GHz  alu={best[1]*100:.1f}%" if best else "NOT FOUND")
PY
done
