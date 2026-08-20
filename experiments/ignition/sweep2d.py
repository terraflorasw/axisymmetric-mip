#!/usr/bin/env python3
"""
2-D design sweep: ring scale x enclosure diameter.

Findings so far (FINDINGS.md):
  * ring scale  sets the TE operating mode  (smaller ring -> higher f)
  * enclosure D sets TM010 ignition mode    (smaller D    -> higher f)
  * but smaller D ALSO raises TE, so the two interact -> solve jointly.

Goal: find (scale, D) where the TE mode sits at 2.45 GHz AND an E-dominated
bore mode (the ignition mode; ANY m is allowed) sits as close beneath/above
it as the amplifier's frequency agility can bridge.

Records ALL E-dominated bore modes per point, not just TM010 — the open
question is whether a higher-order cavity mode lands nearer TE than TM010 does.

Order 1 (0.17% error, established). CPU, 4 ranks. ~25 points, ~2 h.
"""
from __future__ import annotations

import json
import math
import os
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from analyse import read_csv, fnum, group_degenerate  # noqa: E402

HOME = pathlib.Path.home()
MM = HOME / ".local/bin/micromamba"
PALACE = HOME / ".local/opt/palace/bin/palace"
ENVBIN = HOME / ".local/share/mamba/envs/emsim/bin"
C0 = 299_792_458.0

DIAMETERS_MM = [80, 85, 90, 95, 100]
SCALES = [0.82, 0.85, 0.88, 0.91, 0.94]
TARGET_GHZ = 2.45


def run(cmd):
    env = {**os.environ, "PATH": f"{ENVBIN}:{os.environ['PATH']}",
           "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}
    return subprocess.run(cmd, env=env, capture_output=True, text=True)


def modes_of(d: pathlib.Path):
    eig = read_csv(d / "eig.csv")
    en = read_csv(d / "domain-E.csv")
    if not eig or not en:
        return None
    f = [fnum(r, "Re{f}", default=float("nan")) for r in eig]
    m0 = {i for g in group_degenerate(f) if len(g) == 1 for i in g}
    out = []
    for i in range(min(len(eig), len(en))):
        ee = fnum(en[i], "E_elec[1]") or 0.0
        eh = fnum(en[i], "E_mag[1]") or 0.0
        pe = fnum(en[i], "p_elec[2]") or 0.0
        pm = fnum(en[i], "p_mag[2]") or 0.0
        out.append(dict(f=f[i], m0=(i in m0),
                        r=(ee / eh if eh > 0 else float("inf")),
                        alu=(pe + pm) / 2.0))
    return out


def main() -> int:
    base = json.loads(re.sub(r'(^|\s)//[^\n]*', '',
                     pathlib.Path("eigenmode.json").read_text()))
    grid = {}

    for D in DIAMETERS_MM:
        for S in SCALES:
            tag = f"D{D}_S{int(S*100)}"
            od = 50.8 * S
            clearance = (D - od) / 2.0
            if clearance < 8.0:
                print(f"{tag}: SKIP (clearance {clearance:.1f} mm too small)")
                continue

            g = run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
                     "--encl-dia", str(D), "--ring-scale", f"{S}",
                     "--out", f"m_{tag}.msh", "--order", "1"])
            if g.returncode != 0:
                print(f"{tag}: MESH FAIL")
                continue

            cfg = dict(base)
            cfg["Model"] = {**base["Model"], "Mesh": f"m_{tag}.msh"}
            cfg["Solver"] = {**base["Solver"], "Order": 1}
            cfg["Solver"]["Eigenmode"] = {**base["Solver"]["Eigenmode"],
                                          "Target": 1.2, "N": 24, "Save": 0}
            cfg["Problem"] = {**base["Problem"], "Output": f"postpro/{tag}"}
            pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg, indent=2))

            s = run([str(PALACE), "-np", "4", f"{tag}.json"])
            if s.returncode != 0:
                print(f"{tag}: SOLVE FAIL")
                continue

            ms = modes_of(pathlib.Path(f"postpro/{tag}"))
            te = [m for m in ms if m["m0"] and m["r"] < 0.5 and m["alu"] > 0.25]
            te = min(te, key=lambda m: m["f"]) if te else None
            ig = [m for m in ms if m["r"] > 2.0 and m["alu"] < 0.25]  # any m
            grid[(D, S)] = (te, ig)

            tef = f"{te['f']:.4f}" if te else "—"
            # nearest ignition mode to the TE frequency
            near = None
            if te and ig:
                near = min(ig, key=lambda m: abs(m["f"] - te["f"]))
            nf = f"{near['f']:.4f}" if near else "—"
            gap = (f"{100*(near['f']-te['f'])/te['f']:+.1f}%"
                   if (te and near) else "—")
            print(f"{tag}: OD={od:.1f} clr={clearance:.0f}  "
                  f"TE={tef}  nearest-ign={nf}  gap={gap}", flush=True)

    # --- summary: pick points with TE within +/-1% of 2.45 ---
    print("\n" + "=" * 74)
    print("CANDIDATES  (TE within +/-1.5% of 2.45 GHz, smallest ignition gap)")
    print("-" * 74)
    cands = []
    for (D, S), (te, ig) in grid.items():
        if not te or not ig:
            continue
        if abs(te["f"] - TARGET_GHZ) / TARGET_GHZ > 0.015:
            continue
        near = min(ig, key=lambda m: abs(m["f"] - te["f"]))
        cands.append((abs(near["f"] - te["f"]), D, S, te["f"], near["f"],
                      near["m0"]))
    for gap, D, S, tef, igf, m0 in sorted(cands):
        print(f"  D={D}mm scale={S:.2f}  TE={tef:.4f}  ign={igf:.4f} "
              f"({'m=0' if m0 else 'm!=0'})  gap={1000*gap:.0f} MHz")
    if not cands:
        print("  none — widen the grid or the tolerance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
