"""H3 Phase B — LOADED band margin over the JOINT (groove depth x loop size) space.

🔴 THE CONSTRAINT THIS EXISTS TO MAP. At the design point (groove 5x10, loop
11x8) the loaded mode sits at f0 = 2.4824 GHz with a 16 MHz linewidth, so its
f0 sits **17.6 MHz** below the 2.500 GHz band edge, after a **+30.9 MHz** pull
from cold. ⚠️ Originally stated as 9.6 MHz using the upper 3 dB edge — the WRONG
criterion, since the tuner parks at f0 (corrected 2026-08-24). That is the thinnest number in the programme and it is a
HARD feasibility constraint (OPTIMIZER §3c), not an objective to trade off.

🔑 IT MUST BE A JOINT SWEEP, NOT TWO ONE-AXIS SWEEPS. `h3_loopq` F4 measured the
groove and the loop INTERACTING, and not subtly: the same 11x8 loop reads
Q_ext = 76,811 / beta = 0.402 without a groove and Q_ext = 9,231 / beta = 4.704
with one — 8.3x and 12x, crossing from under- to overcoupled. **A one-axis-at-a-
time sweep is invalid here** and any prior fitted that way is void.

🔑 WHAT PHASE A CHANGED ABOUT THIS SWEEP, and it is why B was not designed first:
  - **384 mm^2 is DROPPED.** It is dominated — weaker coupling AND 6.0% Q cost
    against 2.2%. Solving it loaded would spend a cell on a retired candidate.
  - **~10 mm^2 is ADDED.** Every measured size is OVERCOUPLED and beta = 1
    extrapolates to ~10 mm^2, so the interesting region is BELOW the swept
    range and has never been measured. ⚠️ That is an extrapolation off the far
    side of a turning point: this cell is a TEST of it, not a design point.
  - **Purity is NOT a constraint and gets no cells.** F2 never fired; the worst
    spread over a 11x span in area was 0.0010, 20x under the gate.

🔴 ETA IS NOT MEASURED HERE, AND THAT IS DELIBERATE.
Q0 = 1/(1/Q_L - 1/Q_ext) needs Q_ext for THAT (loop, groove) cell. F4 proved
Q_ext depends on the groove, so Phase A's value at 5x10 does not transfer to
other depths, and measuring it per cell is 24 more eigen solves.
**Band margin needs only f0 and the linewidth** — no Q0, no Q_ext, no coupling
branch, none of the machinery that has gone wrong four times. Q_L is reported
because the linewidth gives it for free; **Q0 and eta are NOT, and must not be
reconstructed from Phase A's Q_ext.**
⚠️ Also unknown: whether Q_ext is even the same loaded as cold — the plasma
changes the field at the loop. Eigen cannot check it at eps = -30 (the record
puts the eigen limit near eps+/|eps-| ~ 0.2-0.27), so it stays open.

⚠️ DRIVEN, ne = 1e20, the operating point. One density: this maps a CONSTRAINT
SURFACE at the worst case, not eta(ne), which is already measured and flat
(0.986-0.998) and is not what binds.

VERIFICATION
  V1  🔑 THE ANCHOR CELL is (groove 5x10, loop 11x8) — `h3_driven` measured it
      at f0 = 2.4824 GHz, lw = 16.00 MHz, margin 9.6 MHz. It must reproduce
      within ~1 MHz. **If it does not, no other cell is quotable.**
  V2  the groove meshed must equal the groove requested, per cell, from the
      sidecar. Depth is the swept variable here, so an unverified depth is a
      silently mislabelled row (§7f).
  V3  every cell reports ALL minima found, and the selected one, and WHY it was
      selected. Selection is by CONTINUATION from that cell's own cold estimate,
      never by depth alone (§7u).
FALSIFICATION
  🔴 F1  if NO cell clears the band by more than the anchor's 9.6 MHz, groove
         and loop geometry cannot fix the margin and the fix must come from
         elsewhere — cavity aspect (H1), operating density, or tuner range.
         **Report that; do not keep sweeping a space that has no answer in it.**
  🔴 F2  if the best cell's margin is under ~5 MHz, the DESIGN IS MARGINAL at
         the operating point and that is a finding about the machine, not about
         this sweep.
         ✅ ASSUMPTION RESOLVED 2026-08-24 by asking: the tuner is a dual
         directional coupler + PID frequency loop + PIN magnitude tuner, so it
         PARKS AT f0 and f0 is the criterion. Every margin here is ~8 MHz more
         generous than first reported. **The assumption was the finding.**
  🔴 F3  if deeper grooves make the margin WORSE, the groove is pulling the
         loaded mode UP as well as pushing competitors down, and depth is not a
         free knob — it trades band clearance against margin.
  🔴 F4  if a cell shows TWO comparable minima in band, the filter has failed at
         that geometry under load. That is the ALARM condition (§7i): report it
         and do not pick the deeper one.
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
from e0k2_anchor import design_point, LOOP_PHI, LOOP_RW, LOOP_GAP
from h3_loaded import drude, Z_FRAC, SECTORS, CAP_R_FRAC
from h3_driven import (local_minima, fit_dip, read_s11, sweep, RI, RO,
                       COARSE_MIN_DEPTH_DB, SIZE_FACTORS)

TAG = "h3_margin"

# 🔴 NOT AN OPERATING POINT. This value's provenance is SOLVER CONVERGENCE:
# h3_eigen measured where eigen converges vs PI_1 and 1e20 (PI_1 = 5.58) is in a
# convergent band. It then propagated through h3_annular -> h3_superpose -> here
# as "the operating point" (CONVENTIONS §7ab). **No physical basis is on record.**
# ⚠️ Every result at this density is CONDITIONAL. Report margin AS A FUNCTION of
# ne, never at a point, until ne is anchored from the application, literature,
# or a power balance.
NE = 1.0e20
BAND = (2.40, 2.50)                # the LDMOS tuning band
SWEEP_LO, SWEEP_HI = 2.42, 2.52    # brackets the loaded mode with room above 2.50
SWEEP_STEP = 200e-6                # 80 samples across a 16 MHz linewidth
CASE_TIMEOUT_S = 1800.0

# 🔑 loops: Phase A's three survivors plus the ~10 mm^2 TEST of the beta=1
# extrapolation. 384 mm^2 is dropped as dominated.
LOOPS = [(3.5, 1.5), (5.0, 3.5), (7.5, 5.5), (11.0, 8.0)]
# 🔴 groove DEPTHS, width fixed at the 5 mm baseline.
# lambda/4 = 30.59 mm is the depth to AVOID (the slot resonates, Q -> ~3,000).
GROOVE_W = 5.0
GROOVE_D = [7.0, 10.0, 14.0]

# cold f0 per loop from `h3_loopq` (grooved 5x10). Used ONLY to seed the
# continuation; the 10.5 mm^2 loop has no measurement so it extrapolates the
# small-area trend and is flagged.
COLD_F0 = {35: 2.450818, 82: 2.451084, 176: 2.451633}
COLD_F0_FALLBACK = 2.4506          # ~the no-loop value; a tiny loop barely moves it
PLASMA_PULL_MHZ = 30.9             # measured cold -> ne=1e20 at the anchor cell
CONT_WINDOW_MHZ = 15.0

ANCHOR = {"groove_d": 10.0, "loop": (11.0, 8.0),
          "f0": 2.4824, "lw_mhz": 16.00, "margin_mhz": 9.6}
V1_TOL_MHZ = 1.0
F2_MARGINAL_MHZ = 5.0


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def geo_with_groove(w, d):
    """GEO with the groove set to (w, d). GEO carries `--groove 0,0`."""
    g = list(GEO)
    i = g.index("--groove")
    g[i + 1] = f"{w:g},{d:g}"
    return [x for x in g if x != "--no-torch"]


def build(tag, ld, lw, gw, gd, a, L, eps_p, sig_p, rec):
    zhi = Z_FRAC * L
    args = (geo_with_groove(gw, gd)
            + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
               "--sectors", str(SECTORS),
               "--torch-material", "1.0,3.5e-05",
               "--plasma", f"{RI},{RO},{-zhi:.4f},{zhi:.4f}",
               "--plasma-h", "1.000",
               "--loop", f"{ld},{lw},{LOOP_RW},{LOOP_GAP}",
               "--loop-cap", f"{CAP_R_FRAC * a:.4f}",
               "--loop-phi", LOOP_PHI])
    for sf in SIZE_FACTORS:
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            if sf != SIZE_FACTORS[0]:
                print(f"      ⚠️ mesh needed size-factor {sf}; REPORTED",
                      flush=True)
            return solveconf.load_meta(f"{tag}.msh")
        rec["_err"] = (r.stdout + r.stderr)[-200:]
    return None


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    w = 2.0 * math.pi * 2.45e9
    eps_p, sig_p = drude(NE, w)
    print(f"  a={a:.4f} L={L:.4f}   ne={NE:.1e}  eps={eps_p:+.3f}  "
          f"sigma={sig_p:.4g} S/m")
    print(f"  band {BAND[0]}-{BAND[1]} GHz;  sweep {SWEEP_LO}-{SWEEP_HI} @ "
          f"{SWEEP_STEP*1e6:.0f} kHz "
          f"({round((SWEEP_HI-SWEEP_LO)/SWEEP_STEP):,} samples/cell)")
    print(f"  {len(LOOPS)} loops x {len(GROOVE_D)} groove depths = "
          f"{len(LOOPS)*len(GROOVE_D)} cells")
    print(f"  🔑 margin = {BAND[1]:.3f} - f0 (the tuner PARKS at f0).  NO Q0, NO Q_ext, "
          f"NO branch — none of it is needed.\n", flush=True)

    out = {"ne": NE, "eps": eps_p, "sigma": sig_p, "band": list(BAND),
           "anchor": ANCHOR, "groove_w": GROOVE_W, "cells": []}

    for gd in GROOVE_D:
        for ld, lw in LOOPS:
            area = ld * 2 * lw
            name = f"g{gd:g}_{ld:g}x{lw:g}"
            tag = f"{TAG}_{name}"
            rec = {"groove_w": GROOVE_W, "groove_d": gd, "ld": ld, "lw": lw,
                   "area_mm2": area, "name": name, "tag": tag}
            is_anchor = (gd == ANCHOR["groove_d"] and (ld, lw) == ANCHOR["loop"])
            print(f"  --- groove {GROOVE_W:g}x{gd:g}  loop {ld:g}x{lw:g} "
                  f"= {area:.0f} mm^2" + ("   🔑 V1 ANCHOR CELL" if is_anchor
                                          else ""), flush=True)
            out["cells"].append(rec)

            meta = build(tag, ld, lw, GROOVE_W, gd, a, L, eps_p, sig_p, rec)
            if meta is None:
                rec["error"] = f"mesh failed: {rec.pop('_err','')[:140]}"
                print(f"    🔴 {rec['error']}", flush=True)
                save(out); continue
            rec.pop("_err", None)

            # V2 — the swept variable must be the one that got meshed
            g = (meta.get("geometry_mm") or {}).get("groove") or [0, 0]
            rec["groove_meshed"] = list(map(float, g))
            rec["tets"] = meta["tets"]
            if tuple(map(float, g)) != (GROOVE_W, gd):
                rec["error"] = (f"V2 FIRES: meshed groove {g} != requested "
                                f"({GROOVE_W:g},{gd:g})")
                print(f"    🔴 {rec['error']}", flush=True)
                save(out); continue
            print(f"    groove in mesh: {g}   tets={meta['tets']:,}", flush=True)

            attrs = meta["attributes"]
            try:
                sweep(tag, f"{tag}_wide", (SWEEP_LO, SWEEP_HI), SWEEP_STEP,
                      eps_p, sig_p, attrs)
            except RuntimeError as e:
                rec["error"] = f"sweep failed: {str(e)[:150]}"
                print(f"    🔴 {rec['error']}", flush=True)
                save(out); continue

            d = read_s11(f"{tag}_wide")
            mins = [m for m in local_minima(d)
                    if abs(m[2]) >= COARSE_MIN_DEPTH_DB]
            # 🔴 SAVE THE MEASUREMENT BEFORE THE LABEL (§7q)
            rec["minima"] = [{"f_ghz": f, "s11_db": v} for _, f, v in mins]
            save(out)
            print(f"    {len(mins)} minima: "
                  + "  ".join(f"{f:.4f}@{v:.2f}dB" for _, f, v in mins[:6]),
                  flush=True)
            if not mins:
                rec["error"] = (f"no minimum in {SWEEP_LO}-{SWEEP_HI} @ "
                                f"{SWEEP_STEP*1e6:.0f} kHz")
                print(f"    🔴 {rec['error']}", flush=True)
                save(out); continue

            # F4 — two comparable minima IN BAND is the alarm, not a puzzle
            in_band = [m for m in mins if BAND[0] <= m[1] <= BAND[1]]
            rec["n_minima_in_band"] = len(in_band)
            if len(in_band) >= 2:
                dd = abs(in_band[0][2] - in_band[1][2])
                if dd < 3.0:
                    rec["f4_alarm"] = True
                    print(f"    🔴 F4 ALARM — {len(in_band)} minima IN BAND "
                          f"within {dd:.1f} dB of each other. The filter has "
                          f"FAILED at this geometry under load (§7i).",
                          flush=True)

            # V3 — select by continuation from THIS cell's cold estimate
            cold = COLD_F0.get(int(area), COLD_F0_FALLBACK)
            seed = cold + PLASMA_PULL_MHZ * 1e-3
            rec["cold_f0_used"] = cold
            rec["seed_ghz"] = seed
            rec["seed_extrapolated"] = int(area) not in COLD_F0
            i_sel, f_sel, v_sel = min(mins, key=lambda m: abs(m[1] - seed))
            jump = (f_sel - seed) * 1e3
            rec["selected_by"] = f"continuation {jump:+.2f} MHz from {seed:.4f}"
            if abs(jump) > CONT_WINDOW_MHZ:
                rec["error"] = (f"continuation BROKE: nearest minimum is "
                                f"{jump:+.2f} MHz from the seed")
                print(f"    🔴 {rec['error']}  (minima kept)", flush=True)
                save(out); continue

            fi = fit_dip(d, i_sel, SWEEP_STEP)
            if fi.get("error"):
                rec["error"] = f"fit: {fi['error'][:120]}"
                print(f"    🔴 {rec['error']}", flush=True)
                save(out); continue

            f0, lwm = fi["f0"], fi["linewidth_mhz"]
            hi = f0 + lwm / 2e3
            # 🔴 THE MARGIN IS f0, NOT THE 3 dB EDGE. Corrected 2026-08-24 once
            # the tuner architecture was known: a dual-directional-coupler +
            # PID frequency loop PARKS THE SOURCE AT f0, and the LDMOS emits at
            # ONE frequency — so the cavity linewidth is not a band-occupancy
            # constraint. F2's declared assumption, resolved by asking.
            # ⚠️ Reporting the 3 dB edge UNDERSTATED the headroom by ~2x
            # (9.6 vs 17.6 MHz at ne=1e20). The 3 dB value is kept beside it
            # because it still bounds how sharply detuning costs power.
            margin = (BAND[1] - f0) * 1e3
            margin_3db = (BAND[1] - hi) * 1e3
            rec.update(f0_ghz=f0, linewidth_mhz=lwm, Q_L=fi["Q_L"],
                       s11_db=fi["s11_db"], upper_3db_ghz=hi,
                       margin_mhz=margin, margin_3db_mhz=margin_3db,
                       in_band=(f0 <= BAND[1]))
            print(f"    f0={f0:.6f}  lw={lwm:.2f} MHz  Q_L={fi['Q_L']:,.0f}  "
                  f"upper3dB={hi:.4f}  margin={margin:+.1f} MHz  "
                  + ("✅" if margin > 0 else "🔴 OUT OF BAND"), flush=True)
            if is_anchor:
                df = abs(f0 - ANCHOR["f0"]) * 1e3
                rec["v1_df_mhz"] = df
                print(f"    🔑 V1: f0 {f0:.4f} vs h3_driven {ANCHOR['f0']:.4f} "
                      f"-> {df:.2f} MHz " + ("✅" if df <= V1_TOL_MHZ
                                             else "🔴 FIRES"), flush=True)
            save(out)

    # ---------------- V1 gates everything
    print("\n" + "=" * 78)
    anc = next((c for c in out["cells"] if c.get("v1_df_mhz") is not None), None)
    if anc is None:
        print("  🔴 V1 CANNOT BE CHECKED — the anchor cell did not complete.\n"
              "     NOTHING IN THIS SWEEP IS QUOTABLE.")
        out["v1"] = "not checked"
    elif anc["v1_df_mhz"] > V1_TOL_MHZ:
        print(f"  🔴 V1 FIRES — the anchor cell reads {anc['f0_ghz']:.4f}, "
              f"{anc['v1_df_mhz']:.2f} MHz from h3_driven's\n     "
              f"{ANCHOR['f0']:.4f}. Treat every other cell as SUSPECT.")
        out["v1"] = "FIRES"
    else:
        print(f"  ✅ V1 — anchor cell reproduces h3_driven to "
              f"{anc['v1_df_mhz']:.2f} MHz.")
        out["v1"] = "pass"

    ok = [c for c in out["cells"] if c.get("margin_mhz") is not None]
    if ok:
        print(f"\n  {'groove':>8}{'loop':>9}{'area':>7}{'f0 GHz':>11}"
              f"{'lw MHz':>9}{'up 3dB':>10}{'margin':>9}")
        for c in ok:
            print(f"  {GROOVE_W:g}x{c['groove_d']:<5g}{c['ld']:g}x{c['lw']:<6g}"
                  f"{c['area_mm2']:>7.0f}{c['f0_ghz']:>11.6f}"
                  f"{c['linewidth_mhz']:>9.2f}{c['upper_3db_ghz']:>10.4f}"
                  f"{c['margin_mhz']:>8.1f}"
                  + ("" if c["in_band"] else "  🔴")
                  + ("  🔑" if c.get("f4_alarm") else ""))

        best = max(ok, key=lambda c: c["margin_mhz"])
        print(f"\n  🔑 BEST: groove {GROOVE_W:g}x{best['groove_d']:g}, loop "
              f"{best['ld']:g}x{best['lw']:g} ({best['area_mm2']:.0f} mm^2) "
              f"-> margin {best['margin_mhz']:.1f} MHz")
        gain = best["margin_mhz"] - ANCHOR["margin_mhz"]
        print(f"     vs the design point's {ANCHOR['margin_mhz']:.1f} MHz "
              f"-> {gain:+.1f} MHz")
        out["best"] = {k: best[k] for k in
                       ("name", "groove_d", "ld", "lw", "area_mm2",
                        "f0_ghz", "linewidth_mhz", "margin_mhz")}

        # 🔴 A BINARY FALSIFIER PASSES ON A MEANINGLESS GAIN. F1 asked "does any
        # cell beat the anchor" and the answer is yes — by 0.4 MHz, across a 5x
        # loop-area and 2x groove-depth search. **That is a pass in letter and a
        # fire in spirit.** Report BOTH, and give the effect size the last word.
        spread = (max(c["margin_mhz"] for c in ok)
                  - min(c["margin_mhz"] for c in ok))
        out["margin_spread_mhz"] = spread
        print(f"     whole-grid spread: {spread:.1f} MHz across "
              f"{len(ok)} cells")
        if gain < 1.0:
            print(f"  🔴 F1 FIRES IN SUBSTANCE — the best cell beats the design "
                  f"point by only {gain:+.1f} MHz\n     and the ENTIRE grid "
                  f"spans {spread:.1f} MHz. **Groove and loop geometry cannot fix "
                  f"the\n     margin.** The fix must come from cavity aspect "
                  f"(H1), operating density, or\n     tuner range. Stop "
                  f"sweeping this space.")
            out["f1_substance"] = "FIRES — geometry cannot fix the margin"
        if gain <= 0:
            print("  🔴 F1 FIRES — NO cell beats the design point. Groove and "
                  "loop geometry\n     CANNOT fix the margin; the fix must come "
                  "from cavity aspect (H1),\n     operating density, or tuner "
                  "range. Stop sweeping this space.")
            out["f1"] = "FIRES"
        else:
            out["f1"] = "does not fire"
        if best["margin_mhz"] < F2_MARGINAL_MHZ:
            print(f"  🔴 F2 FIRES — even the best cell clears by only "
                  f"{best['margin_mhz']:.1f} MHz. **The design is MARGINAL at "
                  f"the\n     operating point.** That is a finding about the "
                  f"machine, not this sweep.")
            out["f2"] = "FIRES"
        else:
            out["f2"] = "does not fire"

        # F3 — does depth help or hurt?
        print()
        for ld, lw in LOOPS:
            row = sorted([c for c in ok if (c["ld"], c["lw"]) == (ld, lw)],
                         key=lambda c: c["groove_d"])
            if len(row) >= 2:
                trend = " -> ".join(f"{c['groove_d']:g}mm:{c['margin_mhz']:.1f}"
                                    for c in row)
                # 🔴 FIRST-vs-LAST CANNOT SEE A TURNING POINT, and this
                # programme has now hit three: Q_ext vs loop area, the groove
                # DEPTH law, and this. `row[-1] < row[0]` called 9.3 -> 9.6 ->
                # 9.4 "deeper helps" when the truth is a PEAK at 10 mm.
                ms = [c["margin_mhz"] for c in row]
                i_best = max(range(len(ms)), key=lambda i: ms[i])
                if i_best == 0:
                    verd = "🔴 deeper is WORSE — shallowest is best"
                elif i_best == len(ms) - 1:
                    verd = "deeper helps monotonically"
                else:
                    verd = (f"🔑 PEAK at {row[i_best]['groove_d']:g} mm — depth "
                            f"has an OPTIMUM, not a direction")
                print(f"  F3 loop {ld:g}x{lw:g}: {trend}   {verd}")
        alarms = [c["name"] for c in out["cells"] if c.get("f4_alarm")]
        if alarms:
            print(f"\n  🔴 F4 — filter failed under load at: {', '.join(alarms)}")
            out["f4_alarm_cells"] = alarms
    else:
        print("\n  🔴 no cell produced a margin. Nothing to report.")
    save(out)
    print(f"\n  result -> {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
