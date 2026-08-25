"""H3 — the CONTINUATION LADDER. Where does TE011 actually go?

🔴 WHY. `h3_cold` solved the finished cavity and could not identify TE011 in it.
Closed form says the BARE cavity has exactly TWO modes in 2.35-2.70 — TE011 and
TM111, both at **2.450000, exactly degenerate** (chi'01 = chi11). We measured
FOUR, none cleanly m=0 in band, and three different methods put TE011 in three
different places.

🔑 **"Where did it go" cannot be answered by solving the end state.** It needs
CONTINUATION from the one configuration where the label is EXACT, adding ONE
perturbation at a time — E1b's durable lesson, and what INSTRUMENT prescribes.

    step 1  bare (no groove, no loop)   ANCHOR: closed form, 2.450000 exactly
    step 2  + groove 5x10 (no loop)     ANCHOR: H2 — TM111 -64.25 MHz, TE011 +14 kHz
    step 3  + loop 11x8                 the design cavity, COLD
    (step 4 + plasma = LOADED, once 1-3 identify the mode)

All three are COLD (no plasma) — see GLOSSARY: cold/hot/loaded is a THERMAL and
plasma axis, and this ladder varies the CAVITY, not the regime.

## Why step 1 is identifiable at all, despite the degeneracy

The pair is degenerate in FREQUENCY, so frequency cannot separate it. Two things
can, and both are independent of frequency:
  - **azimuthal order** — TE011 is m=0, TM111 is m=1. Unmixed in a bare cavity,
    where INSTRUMENT records a 134x m=0/m=1 separation.
  - **Q ratio** — TE011's Q exceeds TM111's. H1's own falsifier used exactly this.

VERIFICATION
  V1  step 1: TE011 within **1.0 MHz** of 2.450000, offset POSITIVE (a
      discretised mesh is smaller than the true cavity, so it reads HIGH), one
      m=0 and one m=1 present, and **TE011's Q > TM111's Q**.
      🔴 **NOT E0's 0.058 MHz** — that bound was measured at **sf 0.96**, a
      finer mesh, and does not apply at sf 1.5. Measured here: two INDEPENDENT
      rigs at sf 1.5 give +0.467 (this) and +0.496 MHz (`h4_field` no-torch) —
      **a +0.48 MHz systematic with 0.029 MHz spread.** Quoting a bound from a
      different mesh resolution is CONVENTIONS §6, in the falsifier itself.
      🔑 The Q RATIO is the load-bearing half of V1 and is resolution-robust.
  V2  step 2: TM111 moves **-64.25 MHz** and TE011 moves **+0.014 MHz**, each
      within 15% — H2's measured numbers, an EXTERNAL anchor.
  V3  every step reports EVERY mode in the window with f, Q, m, A2/A0. A mode is
      followed by CONTINUATION from the previous step, never by nearest-2.45.
FALSIFICATION
  🔴 F1  if step 2 does not reproduce H2 within 15%, then H2's groove numbers do
         not transfer to this mesh/settings and **the baseline itself is in
         question**. Report it; do not adjust the groove to fit.
  🔴 F2  if adding the LOOP (step 3) moves TE011 by more than one linewidth,
         the loop is not a probe — it is part of the resonator, and every
         loop-size result must be re-read as a different cavity.
  🔴 F3  if a step's continuation jump exceeds 40 MHz, the mode was lost.
         Report; do not follow the nearest dip.
"""
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
import eigmodes
import azimuthal
from e0_solver_vs_math import GEO, GEO_DESIGN, eigen_cfg, run
from e0k2_anchor import (design_point, wall_sigma, LOOP_PHI, LOOP_RW, LOOP_GAP,
                         CAP_R_FRAC)
from e0k2_azim import sector_bins, read_sector_energy
from h3_loaded import SECTORS

TAG = "h3_ladder"
WINDOW = (2.20, 2.55)   # report window; TE311 (2.622) is already identified
# 🔴 H2_GROOVE's ACTUAL WORKING SETTINGS. Three attempts at this:
#     run 1  target 2.30, N=6   -> 1,018 NLEPS, budget exceeded
#     run 2  target 2.25, N=10  -> 1,040 NLEPS, budget exceeded  (h2b's settings)
#     h2_groove, which DEMONSTRABLY solved this cavity (its -64.25 MHz is in the
#     record):  target=1.05,  n = count(closed-form modes <= 2.57) + 5  = 12
#
# 🔑 The lesson is counter-intuitive and worth keeping: a target FAR BELOW the
# spectrum converges where one placed just below the cluster does not. Shift-
# invert transforms eigenvalues to 1/(lambda - sigma); a sigma close to a tight
# cluster makes several transformed values huge and nearly equal, which is
# exactly the case Krylov methods separate slowly. Starting low means the first
# modes converged are the WELL-SEPARATED ones, and the cluster is reached with a
# good subspace already built.
# ⚠️ CONVENTIONS §6 criticises target=1.05 as SLOW (H1 inherited it and paid an
# hour per point). Both are true: it is slower per solve AND it converges where
# the fast setting fails. Speed and convergence are different axes.
# 🔴 N=10, NOT 12 — THE HIGHEST REQUESTED MODE IS THE ONE THAT STALLS.
# At N=12 the grooved solve climbed nconv 6->8->10->11 and then STUCK at 11/12
# while the iteration rate collapsed from 2.1 s to 56 s per NLEPS (1,277 -> 1,292
# in 14 minutes). Eleven modes were converged and thrown away with the timeout.
#
# 🔑 The ladder needs TE011 and TM111 (~2.45). Below them at this geometry sit
# TM010, TE111, TM011, TM110, TE211 — five — plus whatever the groove pulls down.
# N=10 covers the pair with slack and makes nconv=10 SUFFICIENT.
# ⚠️ I set 12 to also capture TE311 at 2.622, which is ALREADY IDENTIFIED from
# the bare solve. Padding the ceiling for a mode I did not need is what made the
# marginal mode marginal — the same shape as widening a parameter "for safety"
# without pricing it (§6).
N_MODES = 10
EIGEN_TARGET = 1.05
CASE_TIMEOUT_S = 5400.0     # 90 min: target=1.05 cost H2 "over an hour per point"

# 🔴 TWO LIMITS BIND HERE, AND RAISING ONLY THE CLOCK WOULD NOT HELP.
# The last attempt reached **862 NLEPS in 1800 s** — PROGRESSING (the budget
# guard did not fire), so it ran out of wall time. But solvecost.NLEPS_BUDGET
# kills at 1000, so a longer clock alone hits the other limit ~140 iterations
# later.
#
# Evidence bounding the raise (CONVENTIONS §3 / solvecost):
#     25 runs that CONVERGED used <= 869
#     the 2 runs that FAILED used 1,445 and 4,114
# 862-and-still-going sits exactly at the edge of the converged envelope, so
# **1400 is the largest budget that stays BELOW the first known failure.** If it
# needs more than that, it is in the failure regime and should stop.
# ⚠️ Raised deliberately and locally, as run()'s own message instructs. It is
# NOT a global change.
import solvecost as _sc
_sc.NLEPS_BUDGET = 1400
SIZE_FACTORS = ["1.5", "1.42", "1.58"]
LOOP_D, LOOP_HW = 11.0, 8.0        # 176 mm^2 — GLOSSARY: w is a HALF-width
JUMP_MAX_MHZ = 40.0
# 🔑 FIELD-STRUCTURE PROBES — identify TE011 without azimuthal decomposition.
# TE011 is TE_0np: E_z = 0 (TE) and E_r = 0 (m=0), so E is purely AZIMUTHAL and
# its purity P = |E_phi|^2/(|E_r|^2+|E_phi|^2+|E_z|^2) is 1 at EVERY phi. An
# m != 0 mode's P VARIES with phi. Adding sectors cannot fix aliasing (N sectors
# resolve m <= N/4 and something always folds back); this test never decomposes,
# so there is no modulus to alias. Validated on h4_field's saved probes:
# TE011 P=0.9999, TM111 pair 0.872/0.126, TE311 0.989.
# ⚠️ The SPREAD across phi is the discriminator, not P at one angle.
PROBE_PHI_DEG = [0.0, 40.0, 80.0]        # avoid symmetry coincidences
PROBE_R_FRAC = [0.4805, 0.25]            # the J1 peak, and inboard of it
# ⚠️ THESE THRESHOLDS ARE NOT CALIBRATED FOR A LOOPED CAVITY. They were chosen
# from BARE-cavity behaviour (TE011 there reads 0.9973-1.0000, spread 0.0027)
# before any looped measurement existed — the same mistake as quoting E0's
# 0.058 MHz bound at sf 1.5. The design cavity's best candidate reads
# P 0.9423-0.9998, spread 0.0575, with the impurity concentrated INBOARD of the
# mode peak and phi-structure aligned with the loop at phi=36 deg.
# 🔑 REPORT THE NUMBER; treat the verdict as provisional until a looped-cavity
# baseline exists. A gate set from the wrong configuration measures the
# expectation, not the cavity.
PURITY_MIN = 0.99
PURITY_SPREAD_MAX = 0.02
# 🔴 The V1 gate is set from MEASURED reproducibility at THIS size factor, not
# from E0's fine-mesh bound. sf 1.5, geometric order 2: h3_ladder +0.467 MHz and
# h4_field +0.496 MHz against closed form — a +0.48 MHz systematic, 0.029 spread.
# A discretised mesh is smaller than the true cavity and therefore reads HIGH.
SF15_TOL_MHZ = 1.0
# H2's measured groove effect, the external anchor for step 2
H2_TM111_MHZ, H2_TE011_MHZ = -64.25, +0.014
#        (name, geo,          loop)
# 🔑 BARE + GROOVED only. ⚠️ 2026-08-24: this comment used to say `design`
# "already converged (2.440003, Q=12,368)". **Both numbers are RETRACTED** —
# they came from an eigen solve with the loop's port UNASSIGNED (= PMC = gap
# OPEN), which hybridises TE011 (§7v). The design cavity is 2.451490 / 43,523.
# The step is still skipped here, but for a different reason: it is
# banked; re-running it costs 30 min for a number we have. **bare is KEPT** — it
# is ~2 min and it supplies the continuation seed, without which `grooved` falls
# back to m=0 identification, which is exactly the test that cannot tell TE011
# from an aliased TE311.
STEPS = [("bare",     GEO,        False),
         ("grooved",  GEO_DESIGN, False)]


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build(tag, geo, loop, a, L, rec):
    args = (list(geo) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                         "--sectors", str(SECTORS)])
    if loop:
        args += ["--loop", f"{LOOP_D},{LOOP_HW},{LOOP_RW},{LOOP_GAP}",
                 "--loop-cap", f"{CAP_R_FRAC * a:.4f}", "--loop-phi", LOOP_PHI]
    for sf in SIZE_FACTORS:
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            return solveconf.load_meta(f"{tag}.msh")
        rec["_err"] = (r.stdout + r.stderr)[-200:]
    return None


def purity(tag, mode_index, pts):
    """P = |E_phi|^2 / (|E_r|^2+|E_phi|^2+|E_z|^2) at each probe, and its SPREAD.

    🔑 TE011 is TE_0np: E_z = 0 and E_r = 0, so E is purely azimuthal and P = 1
    at EVERY phi. An m != 0 mode's P varies with phi. **The spread across phi is
    the discriminator** — a single angle can read high for the wrong reason
    (TE311 gave 0.989 at one probe in h4_field).

    ⚠️ At phi != 0 the cylindrical components are a ROTATION of the Cartesian
    ones, not E_x/E_y directly:
        E_r   =  E_x cos(phi) + E_y sin(phi)
        E_phi = -E_x sin(phi) + E_y cos(phi)
    """
    import csv as _csv
    f = pathlib.Path("postpro") / tag / "probe-E.csv"
    if not f.exists():
        return None
    rows = list(_csv.reader(f.read_text().splitlines()))
    h = [x.strip() for x in rows[0]]
    row = next((r for r in rows[1:] if r and round(float(r[0])) == mode_index),
               None)
    if row is None:
        return None
    out = []
    for i, pt in enumerate(pts, start=1):
        try:
            def cx(ax):
                return complex(float(row[h.index(f"Re{{E_{ax}[{i}]}} (V/m)")]),
                               float(row[h.index(f"Im{{E_{ax}[{i}]}} (V/m)")]))
            ex, ey, ez = cx("x"), cx("y"), cx("z")
        except (ValueError, IndexError):
            continue
        ph_ = math.radians(pt["phi_deg"])
        er = ex * math.cos(ph_) + ey * math.sin(ph_)
        ep = -ex * math.sin(ph_) + ey * math.cos(ph_)
        tot = abs(er) ** 2 + abs(ep) ** 2 + abs(ez) ** 2
        if tot <= 0:
            continue
        out.append({"r_mm": pt["r_mm"], "phi_deg": pt["phi_deg"],
                    "P": abs(ep) ** 2 / tot, "E_r": abs(er),
                    "E_phi": abs(ep), "E_z": abs(ez)})
    if not out:
        return None
    ps = [o["P"] for o in out]
    return {"per_probe": out, "P_min": min(ps), "P_max": max(ps),
            "spread": max(ps) - min(ps)}


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    print(f"  a={a:.4f} L={L:.4f}   closed form TE011 = TM111 = {exact:.6f} GHz "
          f"(EXACTLY degenerate)")
    print(f"  loop for step 3: {LOOP_D:g}x{LOOP_HW:g} mm = "
          f"{LOOP_D*2*LOOP_HW:.0f} mm^2\n", flush=True)
    out = {"exact": exact, "h2_tm111_mhz": H2_TM111_MHZ,
           "h2_te011_mhz": H2_TE011_MHZ, "steps": []}
    prev_te = None
    for name, geo, loop in STEPS:
        tag = f"{TAG}_{name}"
        rec = {"step": name, "loop": loop, "tag": tag}
        print(f"  --- step: {name}"
              + ("  (groove 5x10)" if geo is GEO_DESIGN else "  (BARE)")
              + ("  + loop" if loop else ""), flush=True)
        meta = build(tag, geo, loop, a, L, rec)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_err','')[:150]}"
            print(f"    🔴 {rec['error']}", flush=True)
            out["steps"].append(rec); save(out); continue
        rec.pop("_err", None)
        g = (meta.get("geometry_mm") or {}).get("groove") or [0, 0]
        rec["groove_meshed"] = list(map(float, g))
        rec["tets"] = meta["tets"]
        print(f"    groove in mesh: {g}   tets={meta['tets']:,}", flush=True)
        attrs = meta["attributes"]
        bins = sector_bins(meta)
        vols = sorted({v for k, v in attrs.items()
                       if isinstance(v, int) and k not in ("wall", "port")}
                      | set(attrs.get("air") or []))
        # 🔴 port_bc="pec" — GATE 4, added 2026-08-24 (CONVENTIONS §7v).
        # This rig wants the UNLOADED Q, so the port must not be a loss
        # channel. Shorting the gap makes the loop a small closed ring
        # resonant far above the band: TE011 is left essentially
        # unperturbed (P=0.9997) and Q excludes port loss.
        # ⚠️ UNASSIGNED IS PMC — an OPEN gap, which is an LC resonator
        # near 2.45 GHz that HYBRIDISES TE011 into a pair. Everything
        # this rig produced before today was measured that way.
        c = eigen_cfg(tag, meta, mesh=f"{tag}.msh", sigma=sigma_w,
                      n=N_MODES, target=EIGEN_TARGET,
                      port_bc=("pec" if loop else None))
        c["Solver"]["Order"] = 2
        c["Domains"]["Postprocessing"]["Energy"] = (
            [{"Index": 1, "Attributes": [attrs["bore"]]}]
            + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
        pts = [(rf * a, math.radians(pd))
               for rf in PROBE_R_FRAC for pd in PROBE_PHI_DEG]
        rec["probe_pts"] = [{"r_mm": r, "phi_deg": math.degrees(ph_)}
                            for r, ph_ in pts]
        c["Domains"]["Postprocessing"]["Probe"] = [
            {"Index": i + 1,
             "Center": [r * 1e-3 * math.cos(ph_), r * 1e-3 * math.sin(ph_), 0.0]}
            for i, (r, ph_) in enumerate(pts)]
        try:
            run(tag, c, timeout=CASE_TIMEOUT_S)
        except RuntimeError as e:
            rec["error"] = str(e)[:170]
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["steps"].append(rec); save(out); continue
        modes = eigmodes.read(tag)
        qs = {}
        for line in (pathlib.Path("postpro") / tag /
                     "eig.csv").read_text().splitlines()[1:]:
            pp = line.split(",")
            if len(pp) > 3:
                qs[round(float(pp[0]))] = float(pp[3])
        sec = read_sector_energy(tag, bins)
        found = []
        for md in modes:
            if not (WINDOW[0] < md["f"] < WINDOW[1]):
                continue
            u = sec.get(float(md["m"]))
            if u is None and sec:
                u = sec[min(sec, key=lambda x: abs(x - md["m"]))]
            m_az, conf, harm = azimuthal.order(u) if u else (None, 0, {})
            found.append({"f_ghz": md["f"], "Q": qs.get(md["m"], 0.0),
                          "mode_index": round(float(md["m"])),
                          "m_az": m_az, "A2_A0": harm.get(2, 0.0)})
        rec["modes"] = found
        for m in found:
            print(f"      {m['f_ghz']:.6f} GHz  Q={m['Q']:>9,.0f}  "
                  f"m={m['m_az']}  A2/A0={m['A2_A0']:.4f}", flush=True)
        # --- identify TE011
        if prev_te is None:
            # step 1: the pair is degenerate in FREQUENCY. Separate by SYMMETRY.
            m0 = [m for m in found if m["m_az"] == 0]
            if not m0:
                rec["error"] = ("step 1: no clean m=0 in a BARE cavity — the "
                                "azimuthal classifier is not working, and "
                                "nothing downstream can be trusted")
                print(f"    🔴 {rec['error']}", flush=True)
                out["steps"].append(rec); save(out); continue
            te = min(m0, key=lambda m: abs(m["f_ghz"] - exact))
            how = "m=0 (bare, unmixed)"
        else:
            cand = min(found, key=lambda m: abs(m["f_ghz"] - prev_te))
            jump = (cand["f_ghz"] - prev_te) * 1e3
            if abs(jump) > JUMP_MAX_MHZ:
                rec["error"] = (f"F3: continuation jump {jump:+.1f} MHz from "
                                f"{prev_te:.6f} exceeds {JUMP_MAX_MHZ} — mode "
                                f"LOST, not followed")
                print(f"    🔴 {rec['error']}", flush=True)
                out["steps"].append(rec); save(out); continue
            te, how = cand, f"continuation ({jump:+.2f} MHz)"
        rec["te011"] = dict(te, selected_by=how)
        print(f"    🔑 TE011: {te['f_ghz']:.6f} GHz  Q={te['Q']:,.0f}  "
              f"m={te['m_az']}  A2/A0={te['A2_A0']:.4f}   by {how}", flush=True)
        # 🔑 the sector-free check: purity at every phi, and its SPREAD
        pu = purity(tag, te.get("mode_index", 0), rec.get("probe_pts") or [])
        if pu:
            rec["purity"] = pu
            ok = pu["P_min"] >= PURITY_MIN and pu["spread"] <= PURITY_SPREAD_MAX
            print(f"       purity P = {pu['P_min']:.4f}-{pu['P_max']:.4f}, "
                  f"spread {pu['spread']:.4f} across "
                  f"{len(pu['per_probe'])} probes  "
                  + ("✅ consistent with TE011 (E purely azimuthal at every phi)"
                     if ok else
                     "🔴 NOT TE011 — E is not purely azimuthal, or P varies "
                     "with phi (which m=0 cannot do)"), flush=True)
        prev_te = te["f_ghz"]
        out["steps"].append(rec); save(out)
    try:
        _report(out)
    except Exception as e:
        print(f"\n  🔴 _report FAILED: {type(e).__name__}: {e}")
        print("     Data is in the result.json; re-scoring is free (§10).")


def _report(out):
    S = {r["step"]: r for r in out["steps"] if "te011" in r}
    print("\n" + "=" * 78)
    print(f"  {'step':>9}{'groove':>10}{'loop':>6}{'TE011 GHz':>12}{'Q':>10}"
          f"{'m':>4}{'A2/A0':>9}{'move':>10}")
    prev = None
    for r in out["steps"]:
        if "te011" not in r:
            print(f"  {r['step']:>9}   🔴 " + r.get("error", "")[:52]); continue
        t = r["te011"]
        mv = "—" if prev is None else f"{(t['f_ghz']-prev)*1e3:+.2f} MHz"
        gm = "5x10" if r.get("groove_meshed", [0, 0])[0] > 0 else "none"
        print(f"  {r['step']:>9}{gm:>10}{('yes' if r['loop'] else 'no'):>6}"
              f"{t['f_ghz']:>12.6f}{t['Q']:>10,.0f}{str(t['m_az']):>4}"
              f"{t['A2_A0']:>9.4f}{mv:>10}")
        prev = t["f_ghz"]
    print()
    b = S.get("bare")
    if b:
        sd = (b["te011"]["f_ghz"] - out["exact"]) * 1e3       # SIGNED
        d = abs(sd)
        others = [m for m in b["modes"] if m["m_az"] == 1]
        ok = d <= SF15_TOL_MHZ and sd > 0
        print(f"  V1 bare TE011 {b['te011']['f_ghz']:.6f} vs closed form "
              f"{out['exact']:.6f} -> {sd:+.3f} MHz "
              + ("✅ within the sf-1.5 systematic (+0.48 +- 0.03 MHz, measured "
                 "on two independent rigs); a discretised mesh reads HIGH"
                 if ok else
                 f"🔴 FIRES — outside +0..{SF15_TOL_MHZ:g} MHz. A NEGATIVE offset "
                 f"would mean the mesh reads LOW, which discretisation does not "
                 f"explain."))
        if others:
            tm = min(others, key=lambda m: abs(m["f_ghz"] - out["exact"]))
            print(f"     TM111 (m=1) at {tm['f_ghz']:.6f}, Q={tm['Q']:,.0f} — "
                  f"TE011 Q {'>' if b['te011']['Q'] > tm['Q'] else '<'} TM111 Q "
                  + ("✅" if b["te011"]["Q"] > tm["Q"] else "🔴 FIRES"))
            out["bare_tm111"] = tm["f_ghz"]
        else:
            print("     🔴 no m=1 mode found in the bare cavity — the degenerate "
                  "partner is missing, so V1 is only half checked")
    g = S.get("grooved")
    if b and g:
        dte = (g["te011"]["f_ghz"] - b["te011"]["f_ghz"]) * 1e3
        e = abs(dte - out["h2_te011_mhz"])
        print(f"\n  V2 groove moves TE011 {dte:+.3f} MHz vs H2's "
              f"{out['h2_te011_mhz']:+.3f} -> {e:.3f} MHz "
              + ("✅" if e <= 1.0 else "🔴 FIRES — H2's groove numbers do NOT "
                 "transfer here; the BASELINE is in question (F1)"))
        tm_b = out.get("bare_tm111")
        tms = [m for m in g["modes"] if m["m_az"] == 1]
        if tm_b and tms:
            tm_g = min(tms, key=lambda m: abs(m["f_ghz"] - (tm_b + out["h2_tm111_mhz"]/1e3)))
            dtm = (tm_g["f_ghz"] - tm_b) * 1e3
            r = abs(dtm / out["h2_tm111_mhz"] - 1)
            print(f"     groove moves TM111 {dtm:+.2f} MHz vs H2's "
                  f"{out['h2_tm111_mhz']:+.2f} -> {100*r:.1f}% "
                  + ("✅" if r <= 0.15 else "🔴 FIRES (F1)"))
    d3 = S.get("design")
    if g and d3:
        dl = (d3["te011"]["f_ghz"] - g["te011"]["f_ghz"]) * 1e3
        lw = d3["te011"]["f_ghz"] / max(d3["te011"]["Q"], 1) * 1e3
        print(f"\n  F2 the LOOP moves TE011 {dl:+.2f} MHz; one linewidth is "
              f"{lw:.3f} MHz -> {abs(dl)/lw:.0f} linewidths "
              + ("✅ a probe" if abs(dl) <= lw else
                 "🔴 FIRES — the loop is PART OF THE RESONATOR, not a probe. "
                 "Every loop-size result is a different cavity."))
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
