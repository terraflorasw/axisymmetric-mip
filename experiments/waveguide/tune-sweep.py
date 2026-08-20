#!/usr/bin/env python3
"""
Ignition tuning sweep — land BOTH the operating mode and an ignition mode
inside the ISM band (2.4-2.5 GHz).

--------------------------------------------------------------------------
Why this experiment exists
--------------------------------------------------------------------------
FINDINGS.md left the route with a conflict: the circumferential slots of
axisymmetric-feed.md §5 remove every mode carrying axial wall current, which
is every TM mode — and every E-dominated mode is a TM mode, so the slots kill
exactly what mode-shift ignition needs.

The resolution is that the SLOTS ARE NO LONGER EARNING THEIR KEEP:

  * their job was killing TM111, the exact degenerate. The brake now does that
    by frequency separation, which is robust to feed asymmetry in a way
    symmetry-nulling is not.
  * m != 0 modes are nulled by the N-fold feed and are far off in frequency.
  * their only remaining function is suppressing TM modes generally, which is
    precisely the harm.

So: drop the slots, and adopt TM020 as the deliberate ignition mode. It is a
good one — m=0 so the symmetric feed drives it, E_z MAXIMUM on axis (J0(0)=1)
rather than merely present, 6.3% of its electric energy in the bore, and p=0
so that field is uniform along the whole torch, giving a long breakdown path.

--------------------------------------------------------------------------
Why the sweep is only 2-D and well conditioned
--------------------------------------------------------------------------
The handles are nearly orthogonal, which the ring architecture never managed:

    TM020  f = chi_02 * c / (2*pi*a)        -> radius ONLY (p=0, no z variation)
    TE011  f = f(a, L)                      -> radius and length
    brake                                   -> pulls TM down, leaves TE alone

so a sets the ignition mode, L then places the operating mode without moving
it, and the brake trims. Compare experiments/ignition, where ring scale and
enclosure diameter both moved both modes and had to be solved jointly.

Analytic starting point (empty cavity): a=105.8, L=90.0 gives TM020=2.490 and
TE011=2.400. Both are pulled down in practice — the torch takes TM020 down
~3.7% and TE011 ~1.4%, and the brake adds ~1.5% more on TM020 — so the sweep
is centred BELOW those radii to compensate.

Modes are identified by absolute bore energy fractions, never by a ratio:
    operating mode  = max bore MAGNETIC fraction  (axial H threading the torch)
    ignition mode   = max bore ELECTRIC fraction  (the gas that has to break)
See FINDINGS.md, "ratios are not discriminators".

Usage:  python tune-sweep.py [--radii 98 101 104 107] [--lengths 80 86 92 98]
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
from analyse import read_csv, fnum  # noqa: E402

HOME = pathlib.Path.home()
MM = HOME / ".local/bin/micromamba"
PALACE = HOME / ".local/opt/palace/bin/palace"
ENVBIN = HOME / ".local/share/mamba/envs/emsim/bin"

TAG_BRAKE = 8
ISM_LO, ISM_HI = 2.40, 2.50


def run(cmd):
    env = {**os.environ, "PATH": f"{ENVBIN}:{os.environ['PATH']}",
           "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}
    return subprocess.run(cmd, env=env, capture_output=True, text=True)


def modes_of(d: pathlib.Path, ns: int):
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
        out.append(dict(f=fnum(eig[i], "Re{f}", default=float("nan")),
                        q=fnum(eig[i], "Q", default=float("nan")),
                        pe=fnum(en[i], "p_elec[1]") or 0.0,
                        pm=fnum(en[i], "p_mag[1]") or 0.0,
                        cv=cv))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--radii", type=float, nargs="+",
                    default=[98.0, 101.0, 104.0, 107.0], help="mm")
    ap.add_argument("--lengths", type=float, nargs="+",
                    default=[80.0, 86.0, 92.0, 98.0], help="mm")
    ap.add_argument("--brake", type=float, default=2.0, help="mm per cap")
    ap.add_argument("--sectors", type=int, default=5)
    ap.add_argument("--np", type=int, default=4)
    ap.add_argument("--order", type=int, default=1, help="FEM order")
    a = ap.parse_args()

    base = json.loads(re.sub(r'(^|\s)//[^\n]*', '',
                             pathlib.Path("eigenmode.json").read_text()))
    grid = []

    for R in a.radii:
        for L in a.lengths:
            # brake belongs in the tag: without it, runs at different
            # brake thicknesses collide on the same postpro directory
            # and silently overwrite each other.
            tag = f"a{int(round(R))}L{int(round(L))}b{int(round(a.brake*10))}"
            # gmsh's high-order optimiser aborts the PROCESS (SIGABRT, exit
            # 134) when it cannot repair a curved element — a C++ terminate(),
            # not a catchable exception. Perturbing the mesh size changes the
            # element topology and reliably dodges it; measured on a=101,L=92,
            # where factor 1.00 aborts and 0.96 / 1.06 / 0.90 all succeed.
            g = None
            for factor in (1.00, 0.96, 1.06, 0.90):
                g = run([str(MM), "run", "-n", "emsim", "python",
                         "geometry.py", "--out", f"{tag}.msh",
                         "--radius", f"{R}", "--length", f"{L}",
                         "--brake", f"{a.brake}", "--sectors",
                         str(a.sectors), "--order", "2",
                         "--size-factor", f"{factor}"])
                if g.returncode == 0:
                    if factor != 1.00:
                        print(f"{tag}: curving failed at factor 1.00, "
                              f"succeeded at {factor}", flush=True)
                    break
            if g is None or g.returncode != 0:
                print(f"{tag}: MESH FAIL at every size factor — "
                      f"{g.stdout[-300:] if g else ''}", flush=True)
                continue

            cfg = json.loads(json.dumps(base))
            cfg["Model"]["Mesh"] = f"{tag}.msh"
            cfg["Solver"]["Order"] = a.order
            cfg["Solver"]["Eigenmode"].update({"Target": 2.0, "N": 14,
                                               "Save": 0})
            cfg["Problem"]["Output"] = f"postpro/{tag}"
            cfg["Domains"]["Materials"].append(
                {"Attributes": [TAG_BRAKE], "Permittivity": 3.78,
                 "Permeability": 1.0, "LossTan": 1.0e-4})
            pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg, indent=2))

            s = run([str(PALACE), "-np", str(a.np), f"{tag}.json"])
            if s.returncode != 0:
                print(f"{tag}: SOLVE FAIL — {s.stdout[-300:]}", flush=True)
                continue

            ms = modes_of(pathlib.Path(f"postpro/{tag}"), a.sectors)
            if not ms:
                print(f"{tag}: no output", flush=True)
                continue
            op = max(ms, key=lambda m: m["pm"])       # operating: bore H
            ig = max(ms, key=lambda m: m["pe"])       # ignition:  bore E
            grid.append((R, L, op, ig))
            both = (ISM_LO <= op["f"] <= ISM_HI) and (ISM_LO <= ig["f"] <= ISM_HI)
            print(f"{tag}: a={R:.0f} L={L:.0f}  TE011={op['f']:.4f} "
                  f"(cv {op['cv']:.3f})  ign={ig['f']:.4f} "
                  f"(boreE {ig['pe']*100:.2f}%)  "
                  f"split={1000*(ig['f']-op['f']):+.0f} MHz"
                  f"{'  << BOTH IN BAND' if both else ''}", flush=True)

    if not grid:
        print("no results")
        return 1

    print("\n" + "=" * 82)
    print(f"{'a(mm)':>6} {'L(mm)':>6} {'TE011':>9} {'ignition':>9} "
          f"{'split(MHz)':>11} {'boreE%':>8} {'in ISM':>8}")
    print("-" * 82)
    for R, L, op, ig in grid:
        both = (ISM_LO <= op["f"] <= ISM_HI) and (ISM_LO <= ig["f"] <= ISM_HI)
        print(f"{R:>6.0f} {L:>6.0f} {op['f']:>9.4f} {ig['f']:>9.4f} "
              f"{1000*(ig['f']-op['f']):>+11.0f} {ig['pe']*100:>8.2f} "
              f"{'YES' if both else '':>8}")

    inband = [g for g in grid
              if ISM_LO <= g[2]["f"] <= ISM_HI and ISM_LO <= g[3]["f"] <= ISM_HI]
    print("=" * 82)
    if inband:
        print(f"{len(inband)} geometries put BOTH modes in 2.4-2.5 GHz:")
        for R, L, op, ig in sorted(inband,
                                   key=lambda g: abs(g[3]["f"] - g[2]["f"])):
            print(f"  a={R:.0f} mm  L={L:.0f} mm  op={op['f']:.4f}  "
                  f"ign={ig['f']:.4f}  split={1000*(ig['f']-op['f']):+.0f} MHz")
        print("\nWant the split large enough to beat the loaded linewidth")
        print("(~15 MHz at loaded Q 165) and small enough for the amplifier.")
    else:
        print("NONE in band — widen the grid. Remember the pull is downward,")
        print("so if both modes read low, SHRINK the cavity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
