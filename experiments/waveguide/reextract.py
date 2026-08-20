#!/usr/bin/env python3
"""
Re-extract the brake sweep from saved CSVs. No re-solving.

The first pass identified TE011 as the mode with minimum bore E/H, and that is
WRONG. A mode at ~2.58 GHz has E/H = 0.019 against the real TE011's 0.029, so
"minimum E/H" tracked the impostor at every thickness and the whole sweep was
meaningless.

The right discriminator is the bore MAGNETIC energy fraction p_mag[1]. TE011 is
the ICP-analogue mode precisely because its axial H is maximum on axis, and it
holds ~3.4% of the mode's magnetic energy in the bore against the impostor's
0.09% — a 37x separation, not a marginal call. A ratio like E/H can be small
for two quite different reasons; an absolute energy fraction cannot.

Reports the three modes of the degenerate cluster together, because the point
of the brake is to watch bore magnetic energy CONCENTRATE into one of them as
the mixing breaks up.

Usage:  python reextract.py [--thicknesses 0 1 2 4 8]
"""
from __future__ import annotations

import argparse
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse import read_csv, fnum  # noqa: E402


def modes_of(d: pathlib.Path, ns: int = 5):
    eig = read_csv(d / "eig.csv")
    en = read_csv(d / "domain-E.csv")
    if not eig or not en:
        return []
    out = []
    for i in range(min(len(eig), len(en))):
        sec = [(fnum(en[i], f"E_elec[{k}]") or 0.0)
               + (fnum(en[i], f"E_mag[{k}]") or 0.0) for k in range(3, 3 + ns)]
        mean = sum(sec) / len(sec) if sec else 0.0
        cv = (math.sqrt(sum((s - mean) ** 2 for s in sec) / len(sec)) / mean
              if mean > 0 else float("nan"))
        ee = fnum(en[i], "E_elec[1]") or 0.0
        eh = fnum(en[i], "E_mag[1]") or 0.0
        out.append(dict(
            f=fnum(eig[i], "Re{f}", default=float("nan")),
            q=fnum(eig[i], "Q", default=float("nan")),
            pe=fnum(en[i], "p_elec[1]") or 0.0,     # bore electric fraction
            pm=fnum(en[i], "p_mag[1]") or 0.0,      # bore magnetic fraction
            r=(ee / eh if eh > 0 else float("inf")),
            cv=cv))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--thicknesses", type=float, nargs="+",
                    default=[0.0, 1.0, 2.0, 4.0, 8.0])
    ap.add_argument("--sectors", type=int, default=5)
    a = ap.parse_args()

    print("Brake sweep, re-extracted by bore MAGNETIC energy (p_mag[1]).")
    print("TE011 is the mode with the most axial H threading the torch.\n")

    rows = []
    for t in a.thicknesses:
        d = pathlib.Path(f"postpro/brake{int(round(t*10)):03d}")
        ms = modes_of(d, a.sectors)
        if not ms:
            print(f"t={t}: no data in {d}")
            continue
        ms.sort(key=lambda m: -m["pm"])
        te = ms[0]
        cluster = sorted([m for m in ms[:3]], key=lambda m: m["f"])
        rows.append((t, te, cluster))

        print(f"--- brake {t:.1f} mm ---   TE011 = {te['f']:.4f} GHz  "
              f"bore H {te['pm']*100:.3f}%  bore E {te['pe']*100:.4f}%  "
              f"cv {te['cv']:.4f}")
        for m in cluster:
            mark = " <- TE011" if m is te else ""
            print(f"      {m['f']:.4f}  boreH {m['pm']*100:>6.3f}%  "
                  f"boreE {m['pe']*100:>7.4f}%  E/H {m['r']:>6.3f}  "
                  f"cv {m['cv']:.4f}{mark}")

    if not rows:
        return 1

    print("\n" + "=" * 78)
    print(f"{'t(mm)':>6} {'TE011':>9} {'dTE(MHz)':>9} {'boreH%':>8} "
          f"{'cv':>7} {'purity':>8} {'split(MHz)':>11}")
    print("-" * 78)
    f0 = rows[0][1]["f"]
    for t, te, cluster in rows:
        # purity: how much of the cluster's bore magnetic energy is in TE011
        tot = sum(m["pm"] for m in cluster)
        purity = te["pm"] / tot if tot > 0 else float("nan")
        others = [m for m in cluster if m is not te]
        split = (min(abs(m["f"] - te["f"]) for m in others) * 1000
                 if others else float("nan"))
        print(f"{t:>6.1f} {te['f']:>9.4f} {(te['f']-f0)*1000:>+9.1f} "
              f"{te['pm']*100:>8.3f} {te['cv']:>7.4f} {purity:>8.3f} "
              f"{split:>11.1f}")
    print("=" * 78)
    print("purity -> 1 and cv -> 0 means the brake has separated TE011 from")
    print("the degenerate cluster. dTE is the cost: TE011 should barely move.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
