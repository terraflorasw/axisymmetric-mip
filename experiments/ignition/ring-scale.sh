#!/usr/bin/env bash
set -e
export MAMBA_ROOT_PREFIX="$HOME/.local/share/mamba"
export PATH="$HOME/.local/share/mamba/envs/emsim/bin:$PATH"
for S in 1.00 0.95 0.92 0.90 0.88 0.85; do
  T=$(echo $S | tr -d .)
  "$HOME/.local/bin/micromamba" run -n emsim python geometry.py \
     --encl-dia 100 --ring-scale $S --out ms$T.msh --order 1 >/dev/null 2>&1
  python3 - <<PY
import json,re,pathlib
c=json.loads(re.sub(r'(^|\s)//[^\n]*','',pathlib.Path("eigenmode.json").read_text()))
c["Model"]["Mesh"]="ms$T.msh"; c["Solver"]["Order"]=1
c["Solver"]["Eigenmode"].update({"Target":1.2,"N":20,"Save":0})
c["Problem"]["Output"]="postpro/S$T"
pathlib.Path("S$T.json").write_text(json.dumps(c,indent=2))
PY
  "$HOME/.local/opt/palace/bin/palace" -np 4 S$T.json >/dev/null 2>&1
  echo -n "scale=$S  OD=$(python3 -c "print(f'{50.8*$S:.1f}')")mm ID=$(python3 -c "print(f'{25.4*$S:.1f}')")mm  "
  "$HOME/.local/bin/micromamba" run -n emsim python - <<PY
import sys,pathlib; sys.path.insert(0,".")
from analyse import read_csv,fnum,group_degenerate
d=pathlib.Path("postpro/S$T"); eig=read_csv(d/"eig.csv"); en=read_csv(d/"domain-E.csv")
f=[fnum(r,"Re{f}",default=0) for r in eig]
m0={i for g in group_degenerate(f) if len(g)==1 for i in g}
te=None; tm=None
for i in range(min(len(eig),len(en))):
    pe=fnum(en[i],"p_elec[2]") or 0; pm=fnum(en[i],"p_mag[2]") or 0
    ee=fnum(en[i],"E_elec[1]") or 0; eh=fnum(en[i],"E_mag[1]") or 0
    alu=(pe+pm)/2; r=(ee/eh if eh>0 else 9e9)
    if i in m0 and alu>0.25 and r<0.5 and (te is None or f[i]<te): te=f[i]
    if i in m0 and alu<0.10 and r>2.0 and (tm is None or f[i]<tm): tm=f[i]
print(f"TE={te:.4f} GHz  TM010={tm:.4f} GHz" if te and tm else f"TE={te}  TM={tm}")
PY
done
