#!/usr/bin/env python3
"""Re-extract the loop sweep, identifying TE011 by BORE MAGNETIC ENERGY.

The first pass picked the resonance as argmin|S11| over a coarse scan. With a
large loop perturbing the cavity there are several features in band, and the
minimum jumped between them — f0 came back non-monotonic in loop size
(2.451, 2.379, 2.422, 2.317), which is the tell.

TE011 is the mode with axial H threading the torch, so p_mag[1] (bore magnetic
energy fraction) identifies it uniquely. Same lesson as the brake sweep:
identify a mode by where its energy is, not by a ratio or an extremum of a
quantity that several modes share. No re-solving — the driven runs already
wrote domain-E.csv.
"""
import csv, math, pathlib, sys

def load(tag):
    d = pathlib.Path(f"postpro/{tag}")
    if not (d/"domain-E.csv").exists() or not (d/"port-S.csv").exists(): return None
    en = {}
    with open(d/"domain-E.csv") as fh:
        r = csv.DictReader(fh); hdr = [h.strip() for h in r.fieldnames]
        def col(row, want):
            for k in row:
                if k and want.lower() in k.strip().lower():
                    try: return float(row[k])
                    except (TypeError, ValueError): return None
            return None
        for row in r:
            f = col(row, "f (GHz)")
            if f is not None: en[round(f, 7)] = col(row, "p_mag[1]") or 0.0
    S = []
    with open(d/"port-S.csv") as fh:
        r = csv.reader(fh); next(r)
        for a in r:
            if len(a) >= 2: S.append((round(float(a[0]), 7), float(a[1])))
    return en, S

CASES = [("ls12x17", 204), ("ls20x28", 560), ("ls28x40", 1120), ("ls36x52", 1872)]
# Eigenmode dielectric-only Q for the design geometry. NOT the Q of the meshes
# swept below, and at Q~1e6 the linewidth (2.45 kHz) is far under the sweep step
# (10-20 kHz), so this is not a resolvable reference — see FINDINGS 2026-08-14.
# Harmless here: Q0 >> Q_L, so Q_ext ~ Q_L and the choice moves results 0.6%.
Q0 = 1.768472e6
print(f"{'tag':>10}{'area':>7}{'f(TE011)':>11}{'boreH%':>9}{'|S11|dB':>9}{'Q_L':>10}{'Q_ext':>11}")
prev = None
for tag, area in CASES:
    got = load(tag + "z") or load(tag + "c")
    if not got: print(f"{tag:>10}  no data"); continue
    en, S = got
    # TE011 = frequency of maximum bore magnetic energy fraction
    f_te = max(en, key=lambda k: en[k])
    smap = dict(S)
    s_at = smap.get(f_te)
    # linewidth about that frequency, from |S11|
    fs = sorted(smap)
    i0 = min(range(len(fs)), key=lambda i: abs(fs[i] - f_te))
    G0 = 10 ** (smap[fs[i0]] / 20); targ = (1 + G0 ** 2) / 2
    lo = hi = None
    for i in range(1, len(fs)):
        p1, p2 = 10 ** (smap[fs[i-1]]/10), 10 ** (smap[fs[i]]/10)
        if (p1 - targ) * (p2 - targ) < 0:
            fx = fs[i-1] + (fs[i]-fs[i-1])*(targ-p1)/(p2-p1)
            if fx < f_te: lo = fx
            elif hi is None: hi = fx
    QL = f_te/(hi-lo) if (lo and hi) else None
    Qe = (1/(1/QL - 1/Q0) if (QL and QL < Q0) else None)
    print(f"{tag:>10}{area:>7}{f_te:>11.5f}{en[f_te]*100:>9.3f}"
          f"{(s_at if s_at is not None else float('nan')):>9.3f}"
          f"{(f'{QL:,.0f}' if QL else '—'):>10}{(f'{Qe:,.0f}' if Qe else '—'):>11}")
