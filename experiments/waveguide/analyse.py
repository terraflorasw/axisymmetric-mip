#!/usr/bin/env python3
"""
Turn Palace eigenmode output into a mode table for the TE011 cavity, and test
the claim in refs/axisymmetric-feed.md §5: that TE011 is the ONLY mode in
2.0-3.0 GHz surviving both filters.

Two measurements per mode:

  azimuthal index m  — from the spread of field energy across the five air
                       sectors. Flat => m=0. This replaces the ignition
                       harness's degeneracy heuristic, which cannot work here:
                       chi'_0n == chi_1n exactly, so TE0np and TM1np sit at
                       the same frequency in a 3-fold cluster.

  bore E/H           — TE011 is magnetically dominated in the bore (axial H
                       maximum on axis, azimuthal E vanishing on axis). TM
                       modes are electrically dominated there.

The survivor test is simpler than it first looks. Circumferential wall slots
remove every mode carrying axial wall current, and J_z at the wall goes as m
for TE modes and is nonzero for all TM modes — so the slots alone reduce the
surviving set to TE0np. The N-fold feed symmetry is redundant margin. Hence:

    survives  <=>  m = 0  AND  H-dominated in the bore

Usage:  python analyse.py [--dir postpro/cav] [--sectors 5]
"""
from __future__ import annotations

import argparse
import csv
import math
import pathlib

C0 = 299_792_458.0

# Bessel roots, hardcoded to avoid a scipy dependency in the solver env.
JP = {  # roots of Jm'  -> TE_mnp
    0: [3.8317, 7.0156, 10.1735], 1: [1.8412, 5.3314, 8.5363],
    2: [3.0542, 6.7061, 9.9695], 3: [4.2012, 8.0152, 11.3459],
    4: [5.3175, 9.2824], 5: [6.4156, 10.5199], 6: [7.5013],
}
JZ = {  # roots of Jm   -> TM_mnp
    0: [2.4048, 5.5201, 8.6537], 1: [3.8317, 7.0156, 10.1735],
    2: [5.1356, 8.4172, 11.6198], 3: [6.3802, 9.7610],
    4: [7.5883, 11.0647], 5: [8.7715], 6: [9.9361],
}

FLAT_TOL = 0.02      # sector energy CV below this is called m=0
H_DOM = 0.5          # bore E/H below this is magnetically dominated
E_DOM = 2.0          # above this, electrically dominated


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


def analytic(a: float, L: float, lo=2.0, hi=3.0) -> list[tuple]:
    """Empty-cavity modes in the window, as (f_GHz, name, m)."""
    out = []
    for m, roots in JP.items():
        for n, x in enumerate(roots, 1):
            for p in range(1, 5):          # TE needs p >= 1
                f = C0 / (2 * math.pi) * math.sqrt(
                    (x / a) ** 2 + (p * math.pi / L) ** 2) / 1e9
                if lo < f < hi:
                    out.append((f, f"TE{m}{n}{p}", m))
    for m, roots in JZ.items():
        for n, x in enumerate(roots, 1):
            for p in range(0, 5):          # TM allows p = 0
                f = C0 / (2 * math.pi) * math.sqrt(
                    (x / a) ** 2 + (p * math.pi / L) ** 2) / 1e9
                if lo < f < hi:
                    out.append((f, f"TM{m}{n}{p}", m))
    return sorted(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="postpro/cav")
    ap.add_argument("--sectors", type=int, default=5)
    ap.add_argument("--radius", type=float, default=94.3, help="mm")
    ap.add_argument("--length", type=float, default=100.0, help="mm")
    a = ap.parse_args()

    d = pathlib.Path(a.dir)
    eig = read_csv(d / "eig.csv")
    en = read_csv(d / "domain-E.csv")
    if not eig or not en:
        print(f"no results in {d} — run Palace first")
        return 1

    ns = a.sectors
    sec_idx = list(range(3, 3 + ns))       # energy indices of the air sectors

    print(f"cavity {2*a.radius:.1f} mm dia x {a.length:.1f} mm, "
          f"{ns} sectors   [{d}]")
    print()
    print(f"{'f(GHz)':>9} {'Q':>9} {'bore E/H':>9} {'eta%':>7} "
          f"{'sector CV':>10} {'m':>5}  {'character':<14} survives")
    print("-" * 88)

    survivors = []
    table = []
    for i in range(min(len(eig), len(en))):
        f = fnum(eig[i], "Re{f}", default=float("nan"))
        q = fnum(eig[i], "Q", default=float("nan"))
        ee = fnum(en[i], "E_elec[1]") or 0.0
        eh = fnum(en[i], "E_mag[1]") or 0.0
        eta = fnum(en[i], "p_elec[1]") or 0.0
        ratio = ee / eh if eh > 0 else float("inf")

        sec = []
        for k in sec_idx:
            se = fnum(en[i], f"E_elec[{k}]") or 0.0
            sm = fnum(en[i], f"E_mag[{k}]") or 0.0
            sec.append(se + sm)
        mean = sum(sec) / len(sec) if sec else 0.0
        if mean > 0:
            var = sum((s - mean) ** 2 for s in sec) / len(sec)
            cv = math.sqrt(var) / mean
        else:
            cv = float("nan")

        is_m0 = cv < FLAT_TOL
        if ratio < H_DOM:
            char = "H-dom (TE)"
        elif ratio > E_DOM:
            char = "E-dom (TM)"
        else:
            char = "mixed"

        ok = is_m0 and ratio < H_DOM
        if ok:
            survivors.append((f, q, eta))
        table.append((f, q, ratio, eta, cv, is_m0, char, ok))

        print(f"{f:>9.4f} {q:>9.0f} {ratio:>9.3f} {eta*100:>7.3f} "
              f"{cv:>10.4f} {'0' if is_m0 else '!=0':>5}  {char:<14} "
              f"{'YES' if ok else ''}")

    # ---- compare against the empty-cavity analytic table -------------------
    print()
    print("Analytic empty-cavity modes in 2.0-3.0 GHz (torch pulls these down):")
    for f, nm, m in analytic(a.radius / 1000.0, a.length / 1000.0):
        near = min((abs(f - t[0]), t[0]) for t in table) if table else (0, 0)
        mark = f"  <- FEM {near[1]:.4f}" if near[0] < 0.05 else ""
        print(f"  {f:>8.4f}  {nm:<8} m={m}{mark}")

    # ---- the §5 claim ------------------------------------------------------
    print()
    print("=" * 72)
    if len(survivors) == 1:
        f, q, eta = survivors[0]
        print(f"CLAIM HOLDS — one survivor: {f:.4f} GHz, Q={q:,.0f}, "
              f"eta={eta*100:.3f}%")
        print(f"  figure of merit Q x eta = {q*eta:.1f}   "
              f"(alumina ring, D80/S0.94 operating mode: 47.5)")
        print("  Q here is the LOSSLESS-WALL value — Palace sees PEC, so this")
        print("  is not a conductor-loss Q. Compare shapes, not magnitudes,")
        print("  until a finite-conductivity run exists.")
    elif not survivors:
        print("CLAIM FAILS — no m=0 H-dominated mode found in the window.")
        print("  Check the cavity is above TE01 cutoff and that the sector")
        print("  physical groups reached Palace (see domain-E.csv columns).")
    else:
        print(f"CLAIM FAILS — {len(survivors)} survivors, not 1:")
        for f, q, eta in survivors:
            print(f"    {f:.4f} GHz  Q={q:,.0f}  eta={eta*100:.3f}%")
        print("  Two m=0 H-dominated modes close together means the feed")
        print("  cannot select between them by symmetry alone.")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
