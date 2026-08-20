#!/usr/bin/env python3
"""
Dielectric brake sweep — how much does an end-cap annulus split the
TE011 / TM111 degeneracy, and does TE011 stay put?

The prediction (refs/axisymmetric-feed.md, and the comment in geometry.py):

    every TE mode   transverse E ~ sin(p*pi*z/L)  ->  ZERO on both end caps
    every TM_mn1    E_z          ~ cos(p*pi*z/L)  ->  MAXIMUM on both end caps

so a dielectric lying against the caps should pull TM111 down hard and leave
TE011 essentially where it was. TE011's E vanishes at EVERY boundary — axis,
side wall (J1(chi'_01) = 0) and both caps — so the brake should also cost it
almost no Q.

Two things falsify the idea, and this sweep measures both:
  * TE011 moving with brake thickness  -> the null is not clean in practice
  * TE011 Q falling with thickness     -> the brake is lossy for it after all

Order 1 for speed; the SPLIT is the deliverable, and it is a difference
between two modes of the same mesh, so systematic order error largely cancels.

Usage:  python brake-sweep.py [--thicknesses 0 1 2 4 8] [--np 4]
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse import read_csv, fnum, FLAT_TOL, H_DOM  # noqa: E402

HOME = pathlib.Path.home()
MM = HOME / ".local/bin/micromamba"
PALACE = HOME / ".local/opt/palace/bin/palace"
ENVBIN = HOME / ".local/share/mamba/envs/emsim/bin"

TAG_BRAKE = 8


def run(cmd):
    env = {**os.environ, "PATH": f"{ENVBIN}:{os.environ['PATH']}",
           "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}
    return subprocess.run(cmd, env=env, capture_output=True, text=True)


def classify(d: pathlib.Path, ns: int):
    """Return (te011, tm111_like) as dicts, or (None, None)."""
    eig = read_csv(d / "eig.csv")
    en = read_csv(d / "domain-E.csv")
    if not eig or not en:
        return None, None
    modes = []
    for i in range(min(len(eig), len(en))):
        f = fnum(eig[i], "Re{f}", default=float("nan"))
        q = fnum(eig[i], "Q", default=float("nan"))
        ee = fnum(en[i], "E_elec[1]") or 0.0
        eh = fnum(en[i], "E_mag[1]") or 0.0
        eta = fnum(en[i], "p_elec[1]") or 0.0
        sec = []
        for k in range(3, 3 + ns):
            sec.append((fnum(en[i], f"E_elec[{k}]") or 0.0)
                       + (fnum(en[i], f"E_mag[{k}]") or 0.0))
        mean = sum(sec) / len(sec) if sec else 0.0
        cv = (math.sqrt(sum((s - mean) ** 2 for s in sec) / len(sec)) / mean
              if mean > 0 else float("nan"))
        modes.append(dict(f=f, q=q, eta=eta,
                          r=(ee / eh if eh > 0 else float("inf")), cv=cv))
    # TE011 is picked by bore E/H, not by the sector CV.
    #
    # At zero brake the CV is useless: TE011 and TM111 are EXACTLY degenerate,
    # so any linear combination of the triplet is also an eigenvector and the
    # solver returns arbitrary mixtures — the m=0 member is not cleanly
    # available to be found. Bore E/H still separates them, because TE011 is
    # the only one that is strongly magnetic on axis. The CV is reported so
    # the mixing can be watched breaking up as the brake thickens.
    band = [m for m in modes if 2.25 < m["f"] < 2.60]
    te = min(band, key=lambda m: m["r"]) if band else None
    others = [m for m in band if m is not te]
    tm = min(others, key=lambda m: abs(m["f"] - te["f"])) if (others and te) else None
    return te, tm


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--thicknesses", type=float, nargs="+",
                    default=[0.0, 1.0, 2.0, 4.0, 8.0], help="mm per end cap")
    ap.add_argument("--eps", type=float, default=3.78)
    ap.add_argument("--sectors", type=int, default=5)
    ap.add_argument("--np", type=int, default=4)
    ap.add_argument("--order", type=int, default=1)
    a = ap.parse_args()

    base = json.loads(re.sub(r'(^|\s)//[^\n]*', '',
                             pathlib.Path("eigenmode.json").read_text()))
    rows = []

    for t in a.thicknesses:
        tag = f"brake{int(round(t*10)):03d}"
        g = run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
                 "--out", f"{tag}.msh", "--brake", f"{t}",
                 "--brake-eps", f"{a.eps}", "--sectors", str(a.sectors),
                 "--order", str(a.order)])
        if g.returncode != 0:
            print(f"{tag}: MESH FAIL\n{g.stdout[-800:]}{g.stderr[-800:]}")
            continue

        cfg = json.loads(json.dumps(base))
        cfg["Model"]["Mesh"] = f"{tag}.msh"
        cfg["Solver"]["Order"] = a.order
        cfg["Solver"]["Eigenmode"].update({"Target": 2.0, "N": 12, "Save": 0})
        cfg["Problem"]["Output"] = f"postpro/{tag}"
        if t > 0:
            cfg["Domains"]["Materials"].append(
                {"Attributes": [TAG_BRAKE], "Permittivity": a.eps,
                 "Permeability": 1.0, "LossTan": 1.0e-4})
        pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg, indent=2))

        s = run([str(PALACE), "-np", str(a.np), f"{tag}.json"])
        if s.returncode != 0:
            print(f"{tag}: SOLVE FAIL\n{s.stdout[-800:]}")
            continue

        te, tm = classify(pathlib.Path(f"postpro/{tag}"), a.sectors)
        if not te:
            print(f"{tag}: no TE011-like mode found")
            continue
        rows.append((t, te, tm))
        split = (tm["f"] - te["f"]) * 1000 if tm else float("nan")
        print(f"{tag}: t={t:>4.1f} mm  TE011={te['f']:.4f} E/H={te['r']:.3f} "
              f"cv={te['cv']:.3f} eta={te['eta']*100:.3f}%  "
              f"partner={tm['f']:.4f}  split={split:+.0f} MHz", flush=True)

    if not rows:
        print("no results")
        return 1

    print("\n" + "=" * 76)
    print(f"{'t(mm)':>6} {'TE011':>9} {'dTE(MHz)':>9} {'bore E/H':>9} "
          f"{'cv':>7} {'partner':>9} {'split(MHz)':>11}")
    print("-" * 76)
    f0, q0 = rows[0][1]["f"], rows[0][1]["q"]
    for t, te, tm in rows:
        dte = (te["f"] - f0) * 1000
        dq = 100 * (te["q"] - q0) / q0 if q0 else float("nan")
        sp = (tm["f"] - te["f"]) * 1000 if tm else float("nan")
        print(f"{t:>6.1f} {te['f']:>9.4f} {dte:>+9.1f} {te['r']:>9.3f} "
              f"{te['cv']:>7.3f} {tm['f'] if tm else 0:>9.4f} {sp:>+11.1f}")
    print("=" * 76)
    print("Reading it: TE011 should barely move and barely lose Q, while the")
    print("partner drops away. If TE011 tracks the brake, its E is not")
    print("actually null at the caps and the idea does not work as stated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
