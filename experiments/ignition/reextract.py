import pathlib, sys, math
sys.path.insert(0, ".")
from analyse import read_csv, fnum, group_degenerate
C0=299792458.0
print(f"{'D':>5} {'f(GHz)':>9} {'Q':>9} {'E/H':>9} {'%Al2O3':>7}  kind")
print("-"*58)
best={}
for dia in [90,95,100,110,120,140,160]:
    d=pathlib.Path(f"postpro/d{dia}")
    eig=read_csv(d/"eig.csv"); en=read_csv(d/"domain-E.csv")
    if not eig or not en: continue
    f=[fnum(r,"Re{f}",default=float('nan')) for r in eig]
    q=[fnum(r,"Q",default=float('nan')) for r in eig]
    m0={i for g in group_degenerate(f) if len(g)==1 for i in g}
    rows=[]
    for i in range(min(len(eig),len(en))):
        ee=fnum(en[i],"E_elec[1]") or 0.0; eh=fnum(en[i],"E_mag[1]") or 0.0
        pe=fnum(en[i],"p_elec[2]") or 0.0; pm=fnum(en[i],"p_mag[2]") or 0.0
        alu=(pe+pm)/2.0
        if alu>0.25 and i in m0:
            rows.append((f[i],q[i],(ee/eh if eh>0 else float('inf')),alu))
    for r in sorted(rows):
        kind="TE (H-dom)" if r[2]<0.5 else ("TM (E-dom)" if r[2]>2 else "mixed")
        print(f"{dia:>5} {r[0]:>9.4f} {r[1]:>9.0f} {r[2]:>9.3f} {r[3]*100:>6.1f}%  {kind}")
    best[dia]=rows
    print()
