#!/usr/bin/env python3
"""Mode selection — ONE implementation of "which peak is which mode".

R50. Three separate wrong-mode picks in one night, each in its own ad-hoc
selector, each producing a confident wrong verdict:

  R39  dq.identify's te_h = 1% cut labelled the 1.2% TM111 family as TE011, so a
       hybridisation detector fired on the KNOWN-GOOD design point.
  R54  a pick-by-highest-Q selector grabbed the m=1/m=2 hybrid instead of TM111,
       making the bare TE011-TM111 separation read -2.6 MHz instead of +19.5.
  R61  the same mistake again, in a different script.

The fix is not a better threshold. It is using the property that DEFINES each
mode instead of a proxy that happens to correlate:

    TE011   bore MAGNETIC fraction >= 1.8%   (its own signature is ~2.08%; the
                                              cut must sit ABOVE the resident
                                              TM111 family at ~1.2%, not below)
    TM020   bore ELECTRIC fraction >= 2.0%   (~3.9%; TE011 is ~0.05%)
    TM111   among modes carrying ~1.2% bore-H, the one with MAXIMUM bin2 —
            i.e. maximum m=1 content. Energy is a proxy and it has failed twice;
            azimuthal index is the definition.

⚠️ TM111 selection REQUIRES sector data (--sectors 5 --loop-phi 36). Without it
there is no way to separate TM111 from the hybrid, and this module says so rather
than guessing.
"""
import cmath
import csv
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq

NSEC = 5
TE011_BORE_H = 0.018
TM020_BORE_E = 0.020
TM111_BORE_H = (0.008, 0.018)


def sector_energy(tag, base="postpro"):
    """Per-frequency energy fraction in each azimuthal bin, or None if absent."""
    p = pathlib.Path(base) / tag / "domain-E.csv"
    with open(p) as fh:
        rows = [{k.strip(): v.strip() for k, v in r.items() if k}
                for r in csv.DictReader(fh)]
    if not rows or f"p_elec[{1 + NSEC}]" not in " ".join(rows[0]):
        return None
    out = []
    for r in rows:
        vals = []
        for i in range(2, 2 + NSEC):
            e = m = 0.0
            for k, v in r.items():
                if f"p_elec[{i}]" in k:
                    e = float(v)
                elif f"p_mag[{i}]" in k:
                    m = float(v)
            vals.append(e + m)
        out.append(vals)
    return out


def azimuthal(U):
    """(bin1, bin2) as fractions of the mean. bin2 -> m=1, bin1 -> m=2 at N=5.

    A mode of index m has energy ~ cos^2(m phi), i.e. spatial frequency 2m, so
    m=1 lands in bin 2 and m=2 aliases into bin 1. Verified against synthetic
    patterns in regress.py -- uniform -> (0,0), cos^2 -> bin2 0.5, cos^2(2phi)
    -> bin1 0.5.
    """
    n = len(U)
    a0 = sum(U) / n
    if a0 <= 0:
        return 0.0, 0.0
    return tuple(abs(sum(U[k] * cmath.exp(-2j * math.pi * b * k / n)
                         for k in range(n))) / n / a0
                 for b in (1, 2))


def peaks(tag, base="postpro", rel=0.005, sep=0.0008):
    """Every resonance in a run, with azimuthal content where measurable."""
    recs = dq.load(tag, base)
    if not recs:
        return []
    sect = sector_energy(tag, base)
    umax = max(r["U"] for r in recs)
    out = []
    for i in dq.peaks(recs, rel=rel, sep=sep):
        r = recs[i]
        b1, b2 = azimuthal(sect[i]) if sect else (None, None)
        out.append(dict(f=r["f"], Q0=r["Q0"], pe=r["pe"], pm=r["pm"],
                        U=r["U"], rel=r["U"] / umax, s_db=r["s_db"],
                        gamma=r["gamma"], b1=b1, b2=b2))
    return out


def te011(ms):
    c = [m for m in ms if m["pm"] >= TE011_BORE_H]
    return max(c, key=lambda m: m["U"]) if c else None


def tm020(ms):
    c = [m for m in ms if m["pe"] >= TM020_BORE_E]
    return max(c, key=lambda m: m["U"]) if c else None


def loaded(ms):
    """The dominant resonance of a PLASMA-LOADED cavity.

    ⚠️ Deliberately returns no mode label. Every discriminator above is
    calibrated on UNLOADED modes, and a plasma redistributes the energy: the
    loaded resonance carries ~0.43% bore-H where an unloaded TE011 carries
    ~2.08%, so te011() correctly refuses it. Loaded, there is one dominant
    resonance and it is the operating one; assert its identity from the run's
    configuration, not from its signature.

    Caught by regress.py on its first execution, which is what the net is for.
    """
    return max(ms, key=lambda m: m["U"]) if ms else None


def tm111(ms):
    """Maximum m=1 content among the bore-H band. NOT maximum energy."""
    c = [m for m in ms if TM111_BORE_H[0] <= m["pm"] < TM111_BORE_H[1]]
    if not c:
        return None
    if any(m["b2"] is None for m in c):
        raise ValueError(
            "TM111 selection needs sector data (--sectors 5 --loop-phi 36); "
            "without it TM111 cannot be separated from the m=1/m=2 hybrid")
    return max(c, key=lambda m: m["b2"])


if __name__ == "__main__":
    for tag in sys.argv[1:]:
        print(f"== {tag}")
        ms = peaks(tag)
        for m in ms:
            az = ("" if m["b1"] is None
                  else f"  bin1={m['b1']:.4f} bin2={m['b2']:.4f}")
            print(f"   f={m['f']:.5f}  U/Um={m['rel']:.4f}  Q={m['Q0']:>9,.0f}"
                  f"  boreE={m['pe']*100:6.3f}%  boreH={m['pm']*100:6.3f}%{az}")
        for name, fn in (("TE011", te011), ("TM020", tm020), ("TM111", tm111)):
            try:
                m = fn(ms)
            except ValueError as e:
                print(f"   {name}: {e}")
                continue
            print(f"   {name}: " + (f"{m['f']:.5f}" if m else "not found"))
