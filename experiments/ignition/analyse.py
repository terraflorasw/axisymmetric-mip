#!/usr/bin/env python3
"""
Phase 1 deliverable: turn Palace eigenmode output into a mode table, classify
each mode, and say what it does or does not license concluding.

Classification (refs/ignition-study.md §4.1):

  operating mode  — must be m=0 AND magnetic-dominated in the bore. Axial H
                    threading the torch, azimuthal polarisation current in the
                    ring. An m!=0 mode cannot produce a symmetric toroid, so
                    azimuthal index is a HARD filter here, not a hint.

  ignition mode   — electric-dominated in the bore, ANY m. A loop feed is not
                    axisymmetric, so it can drive m!=0 modes. For breakdown we
                    only care about |E| in the gas, not about symmetry.

Azimuthal index is inferred from DEGENERACY: an axisymmetric structure gives
m!=0 modes as near-exact sin/cos degenerate pairs; m=0 modes appear singly.

Usage:  python analyse.py [--dir postpro/o2] [--band 2.4 2.5] [--target GHZ]
"""
from __future__ import annotations

import argparse
import csv
import math
import pathlib
import sys

DEGEN_RTOL = 2.0e-4      # relative frequency split below which modes are a pair


def read_csv(path: pathlib.Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as fh:
        rows = list(csv.DictReader(fh))
    return [{k.strip(): v.strip() for k, v in r.items() if k} for r in rows]


def fnum(row: dict, *names, default=None):
    for want in names:
        for k, v in row.items():
            if want.lower() in k.lower():
                try:
                    return float(v)
                except (TypeError, ValueError):
                    pass
    return default


def group_degenerate(freqs: list[float]) -> list[list[int]]:
    """Cluster indices whose frequencies agree to within DEGEN_RTOL."""
    groups: list[list[int]] = []
    for i, f in enumerate(freqs):
        if groups and abs(f - freqs[groups[-1][-1]]) <= DEGEN_RTOL * max(f, 1e-30):
            groups[-1].append(i)
        else:
            groups.append([i])
    return groups


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="postpro/o2")
    ap.add_argument("--band", nargs=2, type=float, default=[2.4, 2.5],
                    metavar=("LO", "HI"))
    ap.add_argument("--target", type=float, default=None,
                    help="solver target in GHz, for the completeness check")
    a = ap.parse_args()

    d = pathlib.Path(a.dir)
    eig = read_csv(d / "eig.csv")
    if not eig:
        print(f"No eigenvalues in {d}/eig.csv", file=sys.stderr)
        return 1
    energy = read_csv(d / "domain-E.csv")

    freqs = [fnum(r, "Re{f}", default=float("nan")) for r in eig]
    qs = [fnum(r, "Q", default=float("nan")) for r in eig]
    groups = group_degenerate(freqs)

    ratios, alu = [], []
    for i in range(len(eig)):
        ee = eh = pe = pm = None
        if energy and i < len(energy):
            ee = fnum(energy[i], "E_elec[1]")
            eh = fnum(energy[i], "E_mag[1]")
            # Energy Index 2 = alumina ring. Fraction of total field energy
            # stored in the ceramic separates a genuine DIELECTRIC RESONATOR
            # mode from an enclosure cavity mode that merely passes through.
            pe = fnum(energy[i], "p_elec[2]")
            pm = fnum(energy[i], "p_mag[2]")
        ratios.append((ee / eh) if (ee and eh and eh > 0) else float("nan"))
        alu.append(((pe or 0) + (pm or 0)) / 2.0 if (pe is not None) else float("nan"))

    print(f"\n{'#':>4}  {'f (GHz)':>9}  {'Q':>11}  {'bore E/H':>9}  "
          f"{'in Al2O3':>8}  {'m':>4}  {'ISM':>4}  classification")
    print("-" * 96)

    operating, ignition = [], []
    for g in groups:
        m0 = len(g) == 1
        for i in g:
            f, q, r = freqs[i], qs[i], ratios[i]
            in_band = a.band[0] <= f <= a.band[1]
            mlab = "0" if m0 else f"±{len(g)//2 or 1}"

            if math.isnan(r):
                cls = "unclassified"
            elif r < 0.5 and m0:
                cls = "OPERATING candidate (m=0, H-dominated)"
                operating.append((f, q, r, in_band))
            elif r < 0.5:
                cls = "H-dominated but m!=0 — cannot form a symmetric toroid"
            elif r > 2.0:
                cls = "IGNITION candidate (E-dominated in bore)"
                ignition.append((f, q, r, in_band, m0))
            else:
                cls = "mixed"

            kind = "RING" if alu[i] > 0.25 else ("box" if alu[i] < 0.10 else "mix")
            print(f"{i+1:>4}  {f:>9.4f}  {q:>11.1f}  {r:>9.3f}  "
                  f"{alu[i]*100:>7.1f}%  {mlab:>4}  "
                  f"{'yes' if in_band else '-':>4}  [{kind}] {cls}")

    print("\n" + "=" * 82)

    # ---- completeness gate: refuse to conclude from a one-sided spectrum ----
    fmin, fmax = min(freqs), max(freqs)
    tgt = a.target
    one_sided = tgt is not None and fmin > tgt * 1.001
    print("SPECTRUM COVERAGE")
    print(f"  found {len(freqs)} modes spanning {fmin:.3f} – {fmax:.3f} GHz")
    if one_sided:
        print(f"  !! Solver target was {tgt:.3f} GHz but the lowest mode found is")
        print(f"     {fmin:.3f} GHz. The spectrum BELOW {fmin:.3f} GHz is unexplored.")
        print(f"     No negative conclusion is licensed. Re-run with a lower Target.")
    elif fmin > a.band[0]:
        print(f"  !! Lowest mode {fmin:.3f} GHz is above the band floor "
              f"{a.band[0]:.3f} GHz — coverage below the band is unverified.")

    print("\nVERDICT")
    op_in = [m for m in operating if m[3]]
    ig_in = [m for m in ignition if m[3]]

    if op_in:
        f, q, r, _ = op_in[0]
        print(f"  Operating mode in band: {f:.4f} GHz, Q = {q:.0f}, E/H = {r:.3f}")
    elif operating:
        f, q, r, _ = min(operating, key=lambda t: abs(t[0] - sum(a.band) / 2))
        off = 100 * (f - sum(a.band) / 2) / (sum(a.band) / 2)
        print(f"  Nearest m=0 H-dominated mode: {f:.4f} GHz ({off:+.1f}% vs band centre)")
        print(f"    Patent Example 1 is a ~2.45 GHz design. A large offset points at")
        print(f"    the model — torch dimensions, enclosure, or the absent loop —")
        print(f"    before it points at the physics.")
    else:
        print("  No m=0 H-dominated mode found in the computed range.")

    if ig_in:
        print(f"\n  Ignition candidates in band: {len(ig_in)}")
        for f, q, r, _, m0 in ig_in:
            print(f"    {f:.4f} GHz  Q={q:.0f}  E/H={r:.1f}  m={'0' if m0 else '!=0'}")
        print("  -> Target A live. Proceed to Phase 2 driven analysis.")
    elif ignition and not one_sided:
        print(f"\n  Ignition candidates exist, all outside {a.band[0]}-{a.band[1]} GHz:")
        for f, q, r, _, m0 in ignition[:5]:
            print(f"    {f:.4f} GHz  Q={q:.0f}  E/H={r:.1f}  m={'0' if m0 else '!=0'}")
        print("  -> Out-of-band ignition needs an EMC argument (study §7).")
    elif ignition:
        print(f"\n  Ignition candidates found above the band, but coverage is")
        print(f"  incomplete — see above. Inconclusive.")

    print("\n  Caveats: UNLOADED mode structure only; says nothing about whether")
    print("  the plasma forms (study §3). Q inherits the placeholder alumina")
    print("  loss tangent (study §9 q1). The coupling loop is absent by design,")
    print("  so real f0 will sit below these values.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
