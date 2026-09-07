#!/usr/bin/env bash
# Q_ext of the COAX-FED azimuthal loop, reference plane AT THE WALL.
# 🔑 PEC walls: mandatory for the wave port's modal solve, and it makes
#    Q_L == Q_ext (no wall loss), which is the quantity we want.
cd /opt/amip/repo/experiments/resonance && source /opt/amip/env.sh
python3 - <<'PY'
import json, solveconf
c, _m, d = solveconf.driven("/tmp/C3.msh", "coaxq", (2.4390, 2.4400),
                            step=2.5e-5, order=2)      # 41 pts, ~7 across a 174 kHz linewidth
c["Solver"]["Driven"]["AdaptiveTol"] = 0.0
cond = c["Boundaries"].pop("Conductivity", [])
attrs = sorted({a for e in cond for a in e.get("Attributes", [])})
c["Boundaries"].setdefault("PEC", {"Attributes": []})
c["Boundaries"]["PEC"]["Attributes"] = sorted(set(c["Boundaries"]["PEC"].get("Attributes", [])) | set(attrs))
c["Problem"]["Output"] = "/tmp/coaxq"; c["Model"]["Mesh"] = "/tmp/C3.msh"
json.dump(c, open("/tmp/coaxq.json", "w"))
print("  41 pts 2.4390-2.4400 @ 25 kHz, PEC on", attrs)
PY
timeout 5400 palace -np 32 /tmp/coaxq.json > /tmp/coaxq.sol 2>&1
echo "PALACE rc=$?"
python3 - <<'PY'
import csv, math
def rows(p):
    with open(p) as f:
        rd=csv.reader(f); h=[x.strip() for x in next(rd)]
        return h,[[float(x) for x in r] for r in rd if r]
def col(h,n): return next(i for i,x in enumerate(h) if x.startswith(n))
he,E=rows("/tmp/coaxq/domain-E.csv"); hv,V=rows("/tmp/coaxq/port-V.csv")
hi,I=rows("/tmp/coaxq/port-I.csv");   hs,S=rows("/tmp/coaxq/port-S.csv")
ie,im=col(he,"E_elec (J)"),col(he,"E_mag (J)")
n=min(len(E),len(V),len(I),len(S))
k=max(range(n), key=lambda j: E[j][ie]+E[j][im])
W=E[k][ie]+E[k][im]
P=0.5*(V[k][col(hv,"Re{V[1]}")]*I[k][col(hi,"Re{I[1]}")]
      +V[k][col(hv,"Im{V[1]}")]*I[k][col(hi,"Im{I[1]}")])
print("  peak f=%.6f GHz  W=%.4e J  P=%.4e W  |S11|=%.3f dB"
      % (E[k][0],W,P,S[k][col(hs,"|S[1][1]| (dB)")]))
if P>0: print("  Q_ext (= Q_L with PEC walls) = %.0f" % (2*math.pi*E[k][0]*1e9*W/P))
PY
echo "COAXQ-DONE"
