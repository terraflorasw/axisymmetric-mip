#!/usr/bin/env python3
"""Driven-Q extraction. One implementation, so selection bugs happen once.

Q0 = omega*U / P_abs, with P_abs = P_inc(1 - |Gamma|^2).
Convention-free: no beta, no over/undercoupled branch, no factor of two.

Modes are identified by WHERE THE ENERGY IS — bore magnetic fraction for
TE011, bore electric fraction for TM020 — never by a ratio or by argmin|S11|.
Both of those picked the wrong mode earlier in this project.
"""
import csv, math, pathlib

def _rows(p):
    with open(p) as fh:
        r = csv.DictReader(fh)
        return [{k.strip(): v.strip() for k, v in x.items() if k} for x in r]

def _num(row, *names):
    for n in names:
        for k, v in row.items():
            if n.lower() in k.lower():
                try: return float(v)
                except (TypeError, ValueError): pass
    return None

def load(tag, base="postpro"):
    """Return list of dicts, one per frequency."""
    d = pathlib.Path(base) / tag
    en, S = _rows(d / "domain-E.csv"), _rows(d / "port-S.csv")
    V, I = _rows(d / "port-V.csv"), _rows(d / "port-I.csv")
    Pinc = 0.5 * _num(V[0], "V_inc") * _num(I[0], "I_inc")
    out = []
    for i in range(min(len(en), len(S))):
        f = _num(en[i], "f (GHz)")
        # Palace reports E_elec = (1/2)*int(eps|E|^2), which is TWICE the
        # time-averaged electric energy — and likewise E_mag. At resonance
        # E_elec == E_mag, so E_elec + E_mag double-counts the stored energy
        # and Q comes out exactly 2x too high. Caught by the ring, whose
        # dielectric Q is known three independent ways (11,054 / 11,083 /
        # 11,085) against this file's 22,161 = 1.999x.
        U = ((_num(en[i], "E_elec (J)") or 0)
             + (_num(en[i], "E_mag (J)") or 0)) / 2.0
        g = 10 ** (_num(S[i], "|S") / 20)
        P = Pinc * (1 - g * g)
        out.append(dict(f=f, U=U, gamma=g, s_db=_num(S[i], "|S"), Pabs=P,
                        pe=_num(en[i], "p_elec[1]") or 0.0,
                        pm=_num(en[i], "p_mag[1]") or 0.0,
                        Q0=(2 * math.pi * f * 1e9 * U / P) if P > 0 else None))
    return out

def peaks(recs, rel=0.2, sep=0.002, min_contrast=10.0):
    """Resonances = local maxima of STORED ENERGY (not |S11|, not Q).

    Guarded by CONTRAST: a real resonance raises stored energy by orders of
    magnitude. If max(U)/min(U) is small the sweep contains no resonance, and
    any 'peak' is noise or a window edge. Without this guard an order-2 run
    whose mode had moved out of the swept band still reported a peak — at the
    window edge, with |S11| flat at -0.01 dB.
    """
    if not recs: return []
    umax = max(r["U"] for r in recs); umin = min(r["U"] for r in recs)
    # DISCRIMINATOR IS THE GLOBAL MAXIMUM'S POSITION, NOT CONTRAST.
    # The o2drv failure this guard was written for had its resonance OUTSIDE the
    # window: U climbed monotonically to the window EDGE. A heavily plasma-loaded
    # resonance is broad and low-contrast (2.5x at sigma=10) but its maximum sits
    # INTERIOR with U falling both sides -- and a pure contrast test rejected it,
    # which is the opposite error. Contrast alone cannot separate the two:
    # o2drv scored 3.1x, a genuine loaded resonance 2.5x.
    if umin <= 0 or umax / umin < 1.5:
        return []                       # genuinely flat
    imax = max(range(len(recs)), key=lambda i: recs[i]["U"])
    edge = max(2, len(recs) // 50)
    if imax < edge or imax >= len(recs) - edge:
        return []                       # peak on the window edge: mode is outside
    idx = [i for i in range(2, len(recs) - 2)
           if recs[i]["U"] == max(x["U"] for x in recs[i-2:i+3])
           and recs[i]["U"] > rel * umax]
    merged = []
    for i in idx:
        if not merged or recs[i]["f"] - recs[merged[-1]]["f"] > sep: merged.append(i)
        elif recs[i]["U"] > recs[merged[-1]]["U"]: merged[-1] = i
    return merged

def identify(r, te_h=0.010, tm_e=0.020):
    """Identify by ABSOLUTE bore energy fraction, never by the pm>pe ratio.

    The ratio form mislabelled every peak in the R17 permittivity sweep: modes
    with boreH 0.05% and boreE 0.004% were called TE011 because 0.05 > 0.004,
    when neither is anywhere near TE011's 2.2% or TM020's 4.0%. FINDINGS states
    the rule -- 'identify a mode by where its energy is, never by a ratio of two
    quantities that can both be small' -- and this function was violating it.
    """
    if r["pm"] >= te_h and r["pm"] > r["pe"]: return "TE011"
    if r["pe"] >= tm_e and r["pe"] > r["pm"]: return "TM020"
    return "OTHER"

def report(tag, base="postpro"):
    recs = load(tag, base)
    out = []
    for i in peaks(recs):
        r = recs[i]
        out.append(dict(mode=identify(r), **{k: r[k] for k in
                        ("f", "Q0", "pe", "pm", "s_db")}))
    return out

if __name__ == "__main__":
    import sys
    for tag in (sys.argv[1:] or ["sigdrv", "tilt45"]):
        print(f"== {tag} ==")
        for m in report(tag):
            print(f"  {m['mode']:>6}  f={m['f']:.5f}  Q0={m['Q0']:>9,.0f}  "
                  f"boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%  "
                  f"|S11|={m['s_db']:7.3f} dB")
