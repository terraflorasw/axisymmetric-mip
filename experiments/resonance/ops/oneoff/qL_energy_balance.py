#!/usr/bin/env python3
"""Q_L by ENERGY BALANCE from a driven run's postpro. No linewidth, no branch.

    Q_L = omega * (E_elec + E_mag) / (0.5 * Re{V I*})

At steady state on resonance the port delivers exactly what the materials
dissipate, so this is the LOADED Q (port included). Pair it with an eigen solve
at port_bc="pec" (loop shorted -> Q0) to get beta = Q0/Q_L - 1, which needs no
|S11| branch.

🔴 WHY THIS EXISTS. On the azimuthal loop all three usual routes failed:
   - eigen with plasma STALLS (PCG stagnation, nconv=0) even at eps_torch = 1
   - the loaded |S11| dip is 4.13 dB on a sloping baseline: no 3 dB width
   - dip depth gave beta = 0.734 or 1.362 where energy balance gave 3.14
   This one works because the driven solve writes W and P whether or not the
   response is resonant.

⚠️ Pick the row by stored-energy maximum NEAR the continuation-selected f0 —
   NOT the global maximum. Loaded, the global max is the 2.605/2.606 competitor
   cluster, not TE011.

usage: qL_energy_balance.py <postpro_dir> <f0_ghz> [window_ghz]
"""
import csv, math, sys

def rows(p):
    with open(p) as f:
        rd = csv.reader(f); hdr = [h.strip() for h in next(rd)]
        return hdr, [[float(x) for x in r] for r in rd if r]

def col(hdr, name):
    return next(i for i, h in enumerate(hdr) if h.startswith(name))

def main(D, f0, win=0.02):
    he, E = rows(D + "/domain-E.csv"); hv, V = rows(D + "/port-V.csv")
    hi, I = rows(D + "/port-I.csv");   hs, S = rows(D + "/port-S.csv")
    ie, im = col(he, "E_elec (J)"), col(he, "E_mag (J)")
    n = min(len(E), len(V), len(I), len(S))
    idx = [j for j in range(n) if abs(E[j][0] - f0) <= win]
    if not idx:
        print("  no rows within %.4f GHz of %.6f" % (win, f0)); return
    k = max(idx, key=lambda j: E[j][ie] + E[j][im])
    W = E[k][ie] + E[k][im]
    vr, vi = V[k][col(hv, "Re{V[1]}")], V[k][col(hv, "Im{V[1]}")]
    ir, ii = I[k][col(hi, "Re{I[1]}")], I[k][col(hi, "Im{I[1]}")]
    P = 0.5 * (vr * ir + vi * ii)
    peak = max(E[j][ie] + E[j][im] for j in range(n))
    print("  f=%.6f  W=%.4e J (%.3f%% of band peak)  P=%.4e W  |S11|=%.2f dB"
          % (E[k][0], W, 100 * W / peak, P, S[k][col(hs, "|S[1][1]| (dB)")]))
    if P > 0:
        print("  Q_L = %.1f" % (2 * math.pi * E[k][0] * 1e9 * W / P))
    else:
        print("  🔴 P_delivered <= 0 — not a driven-into-cavity row; check f0.")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1], float(sys.argv[2]),
         float(sys.argv[3]) if len(sys.argv) > 3 else 0.02)
