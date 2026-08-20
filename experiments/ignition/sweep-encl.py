#!/usr/bin/env python3
"""
Enclosure-diameter calibration sweep.

Tracks TWO modes as the enclosure shrinks:

  ring TE mode  — m=0, H-dominated in the bore, high energy fraction in the
                  alumina. The OPERATING mode. Should land near 2.45 GHz if
                  the model reproduces the patent design.

  cavity TM010  — m=0, E-dominated in the bore, low energy fraction in the
                  ceramic. The IGNITION mode. Empty-cavity value is
                  f = 2.4048*c/(pi*D), pulled down by the ring loading.

Hypothesis under test (refs/coupling-architecture.md, refs/ignition-study.md):
the 160 mm enclosure is ~70% oversized, which simultaneously (a) leaves the
ring mode 17.5% low at 2.02 GHz and (b) strands TM010 far below the band.
Shrinking it should raise both. If one diameter puts the ring mode near
2.45 GHz AND TM010 within frequency-shift reach, mode-shift ignition has a
designed target rather than a hoped-for one.

Order 1 is used for speed — this is a TREND study. The 160 mm point doubles
as a calibration check against the known order-2 answer (ring = 2.0204 GHz).
"""
from __future__ import annotations

import json
import math
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

DIAMETERS_MM = [90, 95, 100, 110, 120, 140, 160]
ORDER = 1
NMODES = 24
TARGET = 1.2


def run(cmd, **kw):
    env = {**dict(__import__("os").environ),
           "PATH": f"{ENVBIN}:{__import__('os').environ['PATH']}",
           "MAMBA_ROOT_PREFIX": str(HOME / ".local/share/mamba")}
    return subprocess.run(cmd, env=env, capture_output=True, text=True, **kw)


def extract(d: pathlib.Path):
    """Return (ring_mode, tm010_mode) as dicts, or None each if absent."""
    eig = read_csv(d / "eig.csv")
    energy = read_csv(d / "domain-E.csv")
    if not eig or not energy:
        return None, None

    f = [fnum(r, "Re{f}", default=float("nan")) for r in eig]
    q = [fnum(r, "Q", default=float("nan")) for r in eig]
    groups = group_degenerate(f)
    m0 = {i for g in groups if len(g) == 1 for i in g}

    modes = []
    for i in range(min(len(eig), len(energy))):
        ee = fnum(energy[i], "E_elec[1]") or 0.0
        eh = fnum(energy[i], "E_mag[1]") or 0.0
        pe = fnum(energy[i], "p_elec[2]") or 0.0
        pm = fnum(energy[i], "p_mag[2]") or 0.0
        modes.append(dict(f=f[i], q=q[i], m0=(i in m0),
                          eh=(ee / eh if eh > 0 else float("inf")),
                          alu=(pe + pm) / 2.0))

    ring = [m for m in modes if m["m0"] and m["eh"] < 0.5 and m["alu"] > 0.25]
    ring = max(ring, key=lambda m: m["alu"]) if ring else None

    tm = [m for m in modes if m["m0"] and m["eh"] > 2.0 and m["alu"] < 0.10]
    tm = min(tm, key=lambda m: m["f"]) if tm else None
    return ring, tm


def main() -> int:
    base = json.loads(re.sub(r'(^|\s)//[^\n]*', '',
                     pathlib.Path("eigenmode.json").read_text()))
    rows = []

    for dia in DIAMETERS_MM:
        tag = f"d{dia}"
        msh = f"mesh_{tag}.msh"
        print(f"\n=== enclosure {dia} mm "
              f"(TM010 empty = {2.4048*C0/(math.pi*dia*1e-3)/1e9:.3f} GHz) ===",
              flush=True)

        g = run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
                 "--encl-dia", str(dia), "--out", msh, "--order", "1"])
        if g.returncode != 0:
            print(f"  MESH FAILED\n{g.stdout[-600:]}{g.stderr[-600:]}")
            continue
        ntet = re.search(r"mesh: (\d+) tets", g.stdout)
        print(f"  mesh ok ({ntet.group(1) if ntet else '?'} tets)", flush=True)

        cfg = dict(base)
        cfg["Model"] = {**base["Model"], "Mesh": msh}
        cfg["Solver"] = {**base["Solver"], "Order": ORDER}
        cfg["Solver"]["Eigenmode"] = {**base["Solver"]["Eigenmode"],
                                      "Target": TARGET, "N": NMODES, "Save": 0}
        cfg["Problem"] = {**base["Problem"], "Output": f"postpro/{tag}"}
        pathlib.Path(f"{tag}.json").write_text(json.dumps(cfg, indent=2))

        s = run([str(PALACE), "-np", "4", f"{tag}.json"])
        if s.returncode != 0:
            print(f"  SOLVE FAILED\n{s.stdout[-800:]}")
            continue

        ring, tm = extract(pathlib.Path(f"postpro/{tag}"))
        rows.append((dia, ring, tm))
        print(f"  ring TE : {ring['f']:.4f} GHz  Q={ring['q']:.0f}  "
              f"alu={ring['alu']*100:.0f}%" if ring else "  ring TE : NOT FOUND",
              flush=True)
        print(f"  TM010   : {tm['f']:.4f} GHz  E/H={tm['eh']:.0f}  "
              f"alu={tm['alu']*100:.1f}%" if tm else "  TM010   : NOT FOUND",
              flush=True)

    print("\n" + "=" * 78)
    print(f"{'D (mm)':>7}  {'ring TE':>9}  {'TM010':>9}  {'split':>8}  "
          f"{'TM010 empty':>11}")
    print("-" * 78)
    for dia, ring, tm in rows:
        rf = f"{ring['f']:.4f}" if ring else "—"
        tf = f"{tm['f']:.4f}" if tm else "—"
        sp = (f"{100*(tm['f']-ring['f'])/ring['f']:+.1f}%"
              if (ring and tm) else "—")
        print(f"{dia:>7}  {rf:>9}  {tf:>9}  {sp:>8}  "
              f"{2.4048*C0/(math.pi*dia*1e-3)/1e9:>11.3f}")

    print("\nReading it:")
    print("  * ring TE should rise toward 2.45 GHz as D shrinks (image effect).")
    print("  * TM010 should rise as 1/D and track the empty-cavity column.")
    print("  * 'split' is what a frequency-agile amplifier must cover to")
    print("    mode-shift from ignition to operation. Small is good.")
    print("  * The 160 mm row is the calibration check: order-2 gave ring")
    print("    = 2.0204 GHz. Order-1 error here bounds the whole sweep.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
