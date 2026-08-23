"""H3 (groove) — does the mode filter make TE011 the mode the TUNER picks?

🔴 TWO THINGS THIS RIG EXISTS FOR, and the first is an omission.

**1. EVERY LOADED SOLVE IN THIS PROGRAMME RAN WITHOUT THE GROOVE.**
H3, H6, the sapphire point and the loop sizing all carry `groove = [0.0, 0.0]`
in their sidecars, while the DESIGN specifies H2's groove frozen at **5 x 10 mm**.
The loaded programme measured a cavity that is not the one being built. Nothing
measured is wrong; its SCOPE was never stated.

⚠️ **`--mode-filter 0` in GEO is CORRECT and is not the omission.** That flag is
the QUARTZ ANNULUS, a superseded device; the groove replaced it. Two distinct
parts share the phrase "mode filter" in this tree — `--mode-filter <thickness>`
(quartz annulus, retired) and `--groove <w,depth>` (the annular slot, current).
Reading `--mode-filter 0` as "the filter is off" is wrong: the current filter has
its own flag, and THAT is the one nobody passed.

**2. THE TUNER PICKS THE DEEPEST IN-BAND DIP, AND IT IS NOT TE011.** Loaded at
ne=1e20, in 2.40-2.50 GHz, without the groove:

    11x8   2.4472 @ -1.28 dB   vs TE011 2.4824 @ -0.35 dB
    28x20  2.4428 @ -13.45 dB  vs TE011 2.4812 @ -0.69 dB

An LDMOS tuner minimising reflected power locks to the 2.44 mode every time. It
heats the plasma well (eta = 0.9947-0.9956) so it is not a loss channel — but
its SYMMETRY is unknown, and the whole TE-only architecture rests on E being
AZIMUTHAL so a high-TDS sample has no axial path to short.

## 🔑 The groove is a SYMMETRY DIAGNOSTIC, not just a filter

H2 measured the mechanism: an annular slot runs PARALLEL to TE011's azimuthal
cap current and CUTS the radial component every TM mode has. Cold, at gd=20:
TE011 moved -0.0 MHz / -0% Q while TM010 moved -32.8 MHz (-40% Q) and TM011
-113.8 MHz (-59% Q).

So the groove answers the open question without an eigen solve:

    groove barely touches 2.44  -> azimuthal cap current, TE-like, SAFE from TDS
    groove damps/moves 2.44     -> radial cap current, TM-like, would have been a
                                   trap the tuner walked into

Either outcome is decisive, which is what makes it worth running.

## Committed predictions (stated BEFORE the solve)

    TE011        moves < 1 MHz, Q cost < 1%     (H2 cold: 14 kHz, -0.3%, at 5x10)
    2.44 mode    UNKNOWN — this is the measurement

🔴 F1  if the groove does NOT change which dip is deepest in band, the annular
       filter cannot protect the tuner from the 2.44 mode. Report it; the fix is
       then a different filter or a different coupling, not a bigger groove.
🔴 F2  if TE011 moves more than 1 MHz or loses more than 1% of Q, the groove
       behaves differently UNDER LOAD than H2 measured it cold, and H2's frozen
       5x10 is not transferable to the loaded cavity.
🔴 F3  if the groove pushes any mode INTO 2.40-2.50 that was outside it, the
       filter has created a new tuner target. Check 2.6232 in particular.

VERIFICATION
  V1  the groove=off cases must reproduce h3_loopsize exactly (same geometry,
      same density) — 2.4824/-0.35 dB at 11x8, 2.4812/-0.69 dB at 28x20.
  V2  every case reports ALL in-band minima with eta, not just the selected one:
      the question is about ORDERING, so a rig that reports one dip cannot
      answer it.

⚠️ SHARES h3_driven's analysis; duplicates only the driver (§7c).
"""
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import solveconf
from e0_solver_vs_math import GEO
from e0k2_anchor import design_point, LOOP_PHI, LOOP_RW, LOOP_GAP, CAP_R_FRAC
from h3_loaded import drude, Z_FRAC, SECTORS
from h3_driven import (local_minima, fit_dip, read_s11, sweep,
                       COARSE_LO_GHZ, COARSE_HI_GHZ, COARSE_STEP_GHZ,
                       COARSE_MIN_DEPTH_DB, Q_BARE, RI, RO, SIZE_FACTORS)

TAG = "h3_groove"
NE = 1.0e20
GROOVE = (5.0, 10.0)            # H2's frozen design: width 5 mm, depth 10 mm
BAND = (2.40, 2.50)             # the LDMOS band — what the tuner can reach
# (loop_d, loop_hw, groove_on). Groove OFF first at each loop = the control.
CASES = [(11.0, 8.0, False), (11.0, 8.0, True),
         (28.0, 20.0, False), (28.0, 20.0, True)]
CONTROLS = {(11.0, 8.0): (2.4824, -0.35), (28.0, 20.0): (2.4812, -0.69)}


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build_mesh(tag, a, L, zlo, zhi, ld, lw, groove_on, rec):
    args = ([x for x in GEO if x != "--no-torch"]
            + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
               "--sectors", str(SECTORS),
               "--torch-material", "1.0,3.5e-05",
               "--plasma", f"{RI},{RO},{zlo:.4f},{zhi:.4f}",
               "--plasma-h", "1.000",
               "--loop", f"{ld},{lw},{LOOP_RW},{LOOP_GAP}",
               "--loop-cap", f"{CAP_R_FRAC * a:.4f}",
               "--loop-phi", LOOP_PHI])
    if groove_on:
        args += ["--groove", f"{GROOVE[0]},{GROOVE[1]}"]
    for sf in SIZE_FACTORS:
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            if sf != SIZE_FACTORS[0]:
                print(f"    ⚠️ mesh needed size-factor {sf}; REPORTED", flush=True)
            return solveconf.load_meta(f"{tag}.msh")
        rec["_err"] = (r.stdout + r.stderr)[-200:]
    return None


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    w = 2.0 * math.pi * 2.45e9
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    eps_p, sig_p = drude(NE, w)
    print(f"  loaded ne={NE:.0e}, plasma r={RI}-{RO} mm; groove "
          f"{GROOVE[0]:g} x {GROOVE[1]:g} mm (H2's frozen design)")
    print(f"  tuner band {BAND[0]}-{BAND[1]} GHz — a tuner locks to the DEEPEST "
          f"dip in here\n", flush=True)
    out = {"ne": NE, "groove_mm": list(GROOVE), "band": list(BAND),
           "q_bare_no_loop": Q_BARE, "points": []}
    for ld, lw, gon in CASES:
        tag = f"{TAG}_{ld:g}x{lw:g}_{'g' if gon else 'nog'}".replace(".", "p")
        rec = {"ld": ld, "lw": lw, "groove": gon, "tag": tag}
        print(f"  --- loop {ld:g}x{lw:g}, groove {'ON' if gon else 'OFF'}",
              flush=True)
        meta = build_mesh(tag, a, L, zlo, zhi, ld, lw, gon, rec)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_err','')[:150]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        rec.pop("_err", None)
        g = (meta.get("geometry_mm") or {}).get("groove")
        rec["groove_meshed"] = g
        want = list(GROOVE) if gon else [0.0, 0.0]
        if [float(x) for x in (g or [0, 0])] != [float(x) for x in want]:
            rec["error"] = (f"mesh ignored the groove request: asked {want}, "
                            f"sidecar says {g}. Refusing to measure the wrong "
                            f"cavity.")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        print(f"    groove in mesh: {g} ✅", flush=True)
        attrs = meta["attributes"]
        rec["tets"] = meta["tets"]
        try:
            sweep(tag, f"{tag}_wide", (COARSE_LO_GHZ, COARSE_HI_GHZ),
                  COARSE_STEP_GHZ, eps_p, sig_p, attrs)
        except RuntimeError as e:
            rec["error"] = f"sweep failed: {str(e)[:160]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        d = read_s11(f"{tag}_wide")
        mins = [m for m in local_minima(d) if abs(m[2]) >= COARSE_MIN_DEPTH_DB]
        # 🔑 V2 — report EVERY minimum with eta. The question is about ORDERING,
        # so a rig that returns one selected dip cannot answer it.
        rows = []
        for i, f, v in mins:
            fi = fit_dip(d, i)
            r = {"f_ghz": f, "s11_db": v, "beta": fi["beta"],
                 "in_band": BAND[0] <= f <= BAND[1]}
            if "Q_L" in fi:
                r.update(linewidth_mhz=fi["linewidth_mhz"], Q0=fi["Q0"],
                         eta=1.0 - fi["Q0"] / Q_BARE)
            S = abs((1 - fi["beta"]) / (1 + fi["beta"]))
            r["net_pct"] = 100 * (1 - S ** 2) * r.get("eta", 0.0)
            rows.append(r)
        rec["modes"] = rows
        ib = [r for r in rows if r["in_band"]]
        rec["deepest_in_band"] = min(ib, key=lambda r: r["s11_db"])["f_ghz"] if ib else None
        for r in rows:
            print(f"      {r['f_ghz']:.4f} @ {r['s11_db']:>7.2f} dB  "
                  f"beta={r['beta']:.4f}"
                  + (f"  eta={r['eta']:.4f}  net={r['net_pct']:.1f}%"
                     if "eta" in r else "  (width n/a)")
                  + ("  ← IN BAND" if r["in_band"] else ""), flush=True)
        out["points"].append(rec); save(out)
    _report(out)


def _report(out):
    print("\n" + "=" * 78)
    P = {(p["ld"], p["lw"], p["groove"]): p for p in out["points"] if "modes" in p}
    for (ld, lw) in ((11.0, 8.0), (28.0, 20.0)):
        off, on = P.get((ld, lw, False)), P.get((ld, lw, True))
        print(f"\n  LOOP {ld:g}x{lw:g}")
        for lbl, p in (("groove OFF", off), ("groove ON ", on)):
            if not p:
                print(f"    {lbl}: 🔴 missing")
                continue
            ib = [r for r in p["modes"] if r["in_band"]]
            if not ib:
                print(f"    {lbl}: no in-band mode at all")
                continue
            deep = min(ib, key=lambda r: r["s11_db"])
            te = min(ib, key=lambda r: abs(r["f_ghz"] - CONTROLS[(ld, lw)][0]))
            print(f"    {lbl}: tuner locks to {deep['f_ghz']:.4f} @ "
                  f"{deep['s11_db']:.2f} dB (net {deep['net_pct']:.1f}%)"
                  + ("  ✅ that IS TE011"
                     if abs(deep["f_ghz"] - te["f_ghz"]) < 1e-9 else
                     f"   TE011 is {te['f_ghz']:.4f} @ {te['s11_db']:.2f} dB "
                     f"(net {te['net_pct']:.1f}%)"))
        if off and on:
            # F2 — did the groove leave TE011 alone, as H2 measured cold?
            f_off = CONTROLS[(ld, lw)][0]
            t_off = min((r for r in off["modes"]), key=lambda r: abs(r["f_ghz"] - f_off))
            t_on = min((r for r in on["modes"]), key=lambda r: abs(r["f_ghz"] - f_off))
            dmhz = (t_on["f_ghz"] - t_off["f_ghz"]) * 1e3
            print(f"    F2 TE011 moved {dmhz:+.2f} MHz with the groove "
                  + ("✅ (H2 cold: 14 kHz)" if abs(dmhz) <= 1.0 else
                     "🔴 FIRES — the groove behaves differently UNDER LOAD than "
                     "H2 measured it cold; 5x10 is not transferable"))
            # F1 — did the ordering change?
            d_off = min((r for r in off["modes"] if r["in_band"]),
                        key=lambda r: r["s11_db"])["f_ghz"]
            d_on = min((r for r in on["modes"] if r["in_band"]),
                       key=lambda r: r["s11_db"])["f_ghz"]
            te_on = abs(d_on - t_on["f_ghz"]) < 1e-9
            print("    F1 " + ("✅ the groove MAKES TE011 the tuner's target"
                               if te_on else
                               f"🔴 FIRES — deepest in band is still "
                               f"{d_on:.4f}, not TE011. The annular filter "
                               f"cannot protect the tuner from it; the fix is a "
                               f"different filter or coupling, not a bigger groove."))
            print(f"    🔑 SYMMETRY READ-OUT: the 2.44 mode moved "
                  f"{(min((r for r in on['modes'] if r['in_band'] and abs(r['f_ghz']-2.445)<0.02), key=lambda r: abs(r['f_ghz']-2.445), default={'f_ghz':float('nan')})['f_ghz'] - d_off)*1e3:+.1f} MHz — "
                  f"a groove-BLIND mode has azimuthal cap current (TE-like, safe "
                  f"from TDS); a groove-SENSITIVE one is TM-like.")
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
