"""H3 (loop sizing) — size the coupling loop for the LOADED cavity.

🔴 WHY NOW, AND NOT BEFORE. OPTIMIZER §3b said "beta and Q_ext have NO CONSUMER
until H3" because Q_ext must be sized to Q0 LOADED and Q0 loaded was unknown. It
is now measured: **Q0 = 80-360 across ne = 1e18-1e20** on the r=2.0-8.5 mm
annulus. There is a target to match.

🔴 AND THE CURRENT LOOP IS A 13x POWER PENALTY. Measured on the loaded cavity,
the 11x8 cap loop gives **beta = 0.0201**:

    beta=0.0201  ->  |S11| = 0.9606  ->  92.3% REFLECTED, 7.7% absorbed
    beta=1       ->  |S11| = 0       ->   0%  reflected, 100% absorbed

A loop tuned to read a Q=44,000 empty cavity is hopelessly undercoupled to a
Q=163 one — 272x less Q0, and beta = Q0/Q_ext falls with it. This is not a
subtlety; it is most of the source power.

⚠️ The OLD loop sizing sweep is VOID: it was run on the EMPTY cavity and its
beta is not mesh-converged (43% for a 1.25x refinement). This rig re-derives on
the LOADED mesh, which is the case that matters — CONVENTIONS §6.

## Committed prediction (stated BEFORE the solve)

beta ~ (loop area)^2 for a small loop. From beta = 0.0201 at 176 mm^2:

     d x hw    area     predicted beta
     11x8       176        0.020   (the measured anchor)
     16x12      384        0.096
     22x16      704        0.322
     28x20     1120        0.814
     34x24     1632        1.728

so **critical coupling near 1,200 mm^2**, about 7x the present area.

🔴 The area^2 law is a SMALL-LOOP approximation and these loops are not small —
34x24 spans r = 18-66 mm in an 88 mm cavity. **I expect it to break, and the
point of the sweep is to find where.** A prediction I expect to fail is still
worth committing: it makes the failure legible.

VERIFICATION
  V1  the 11x8 case must reproduce the measured beta = 0.0201 within 20% and
      f0 = 2.4824 GHz within 1 MHz. Same geometry, same density, same rig family.
  V2  every case identifies TE011 by CONTINUATION from the previous loop size,
      never by depth — a large loop couples strongly to the 2.6232 GHz mode.
FALSIFICATION
  🔴 F1  if beta at 1120 mm^2 is not within 2x of the predicted 0.814, the
         area^2 model does not hold on the loaded cavity. Report the measured
         exponent; do NOT refit and present it as the prior.
  🔴 F2  if f0 leaves 2.40-2.50 GHz at any loop size, that loop is not usable —
         the coupler would drag the cavity out of the LDMOS band.
  🔴 F3  if eta FALLS as the loop grows, the loop's own conductor loss is
         becoming comparable to the plasma's absorption, and eta stops meaning
         "power into the plasma". Report the onset — it bounds usable loop size
         independently of beta.

⚠️ SHARES h3_driven's ANALYSIS, duplicates only the DRIVER (§7c).
⚠️ eta here uses Q_BARE = 44,384, the NO-LOOP empty value, so a large lossy loop
inflates apparent absorption. That is F3's subject, not a bug — but do not quote
eta from this rig as "power into the plasma" without reading F3.
"""
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import solveconf
# 🔴 GEO_DESIGN, not GEO. GEO is the BARE cavity (groove 0,0) and exists
# for instrument rigs comparing against closed form. This rig produces
# DESIGN numbers, so it needs the cavity being built — groove 5x10 (H2).
# Every result this rig produced before 2026-08-23 was groove-free and is
# DISCARDED; see CONVENTIONS §7f.
from e0_solver_vs_math import GEO_DESIGN as GEO
from e0k2_anchor import design_point, LOOP_PHI, LOOP_RW, LOOP_GAP, CAP_R_FRAC
from h3_loaded import drude, Z_FRAC, SECTORS
from h3_driven import (local_minima, fit_dip, read_s11, sweep,
                       COARSE_LO_GHZ, COARSE_HI_GHZ, COARSE_STEP_GHZ,
                       COARSE_MIN_DEPTH_DB, COARSE_EDGE_MHZ,
                       CONTINUATION_JUMP_MHZ, Q_BARE, RI, RO, SIZE_FACTORS)

TAG = "h3_loopsize"
NE = 1.0e20
LOOPS = [(11.0, 8.0), (16.0, 12.0), (22.0, 16.0), (28.0, 20.0), (34.0, 24.0)]
BETA_REF, AREA_REF = 0.0201, 176.0      # measured, h3_driven ne=1e20
SEED_GHZ = 2.4824                       # measured, same density and geometry
SEED_TOL_MHZ = 1.0
BETA_TARGET = 1.0


def area_mm2(d, hw):
    return d * 2.0 * hw


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build_mesh(tag, a, L, zlo, zhi, ld, lw, rec):
    args = ([x for x in GEO if x != "--no-torch"]
            + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
               "--sectors", str(SECTORS),
               "--torch-material", "1.0,3.5e-05",
               "--plasma", f"{RI},{RO},{zlo:.4f},{zhi:.4f}",
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
    cap_r = CAP_R_FRAC * a
    print(f"  cavity a={a:.4f} L={L:.4f}   cap loop at r={cap_r:.2f} mm "
          f"(the H_r peak)")
    print(f"  plasma r={RI}-{RO} mm  ne={NE:.0e}  eps={eps_p:+.3f}  "
          f"sigma={sig_p:.4g} S/m")
    print(f"  anchor: beta={BETA_REF} at {AREA_REF:.0f} mm^2 (h3_driven)")
    print(f"  {'d x hw':>10}{'area':>8}{'pred beta':>11}{'r span':>16}")
    for ld, lw in LOOPS:
        ar = area_mm2(ld, lw)
        print(f"  {f'{ld:g}x{lw:g}':>10}{ar:>8.0f}"
              f"{BETA_REF*(ar/AREA_REF)**2:>11.3f}"
              f"{f'{cap_r-lw:.1f}-{cap_r+lw:.1f} mm':>16}")
    print(flush=True)
    out = {"ne": NE, "q_bare_no_loop": Q_BARE, "beta_ref": BETA_REF,
           "area_ref": AREA_REF, "cap_r_mm": cap_r, "points": []}
    expect = SEED_GHZ
    for ld, lw in LOOPS:
        ar = area_mm2(ld, lw)
        tag = f"{TAG}_{ld:g}x{lw:g}".replace(".", "p")
        rec = {"ld": ld, "lw": lw, "area_mm2": ar, "tag": tag,
               "beta_pred": BETA_REF * (ar / AREA_REF) ** 2}
        print(f"  --- loop {ld:g}x{lw:g} mm, area {ar:.0f} mm^2 "
              f"(predicted beta {rec['beta_pred']:.3f})", flush=True)
        meta = build_mesh(tag, a, L, zlo, zhi, ld, lw, rec)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_err','')[:150]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        rec.pop("_err", None)
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
        rec["minima"] = [{"f_ghz": f, "s11_db": v} for _, f, v in mins]
        print(f"    {len(mins)} local minima: "
              + "  ".join(f"{f:.4f}@{v:.2f}dB" for _, f, v in mins[:6]), flush=True)
        if not mins:
            rec["error"] = "no local minimum in band"
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        i_sel, f_sel, _v = min(mins, key=lambda m: abs(m[1] - expect))
        jump = (f_sel - expect) * 1e3
        rec["jump_mhz"] = jump
        if abs(jump) > CONTINUATION_JUMP_MHZ:
            rec["error"] = (f"F2/continuation BROKE: nearest to {expect:.4f} is "
                            f"{f_sel:.4f} ({jump:+.1f} MHz). A large loop couples "
                            f"hard to the 2.6232 mode; NOT following it.")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        edge = min(f_sel - COARSE_LO_GHZ, COARSE_HI_GHZ - f_sel) * 1e3
        if edge < COARSE_EDGE_MHZ:
            rec["error"] = f"selected dip {edge:.1f} MHz from a band edge (§1)"
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        fi = fit_dip(d, i_sel)
        rec["fit"] = fi
        rec["f_ghz"] = fi["f0"]
        rec["beta"] = fi["beta"]
        if "Q_L" in fi:
            rec["Q0"] = fi["Q0"]
            rec["eta"] = 1.0 - fi["Q0"] / Q_BARE
            rec["Q_ext"] = fi["Q0"] / fi["beta"] if fi["beta"] else None
        if ld == LOOPS[0][0] and lw == LOOPS[0][1]:
            off = abs(fi["f0"] - SEED_GHZ) * 1e3
            if off > SEED_TOL_MHZ:
                rec["error"] = (f"SEED CHECK FAILED: {fi['f0']:.4f} is {off:.1f} "
                                f"MHz from the measured {SEED_GHZ}. Continuation "
                                f"would follow the wrong mode for every later "
                                f"loop. ABORTING.")
                print(f"    🔴 {rec['error']}", flush=True)
                out["points"].append(rec); save(out); _report(out); return
        print(f"    f0={fi['f0']:.6f} ({jump:+.2f} MHz)  |S11|={fi['s11_db']:.2f} dB"
              f"  beta={fi['beta']:.4f} (pred {rec['beta_pred']:.3f})"
              + (f"  Q0={fi['Q0']:.0f}  eta={rec['eta']:.4f}" if "eta" in rec else ""),
              flush=True)
        expect = fi["f0"]
        out["points"].append(rec); save(out)
    _report(out)


def _report(out):
    P = [p for p in out["points"] if "beta" in p]
    print("\n" + "=" * 78)
    print(f"  {'loop':>9}{'area':>8}{'f0 GHz':>10}{'|S11|dB':>9}{'beta':>9}"
          f"{'pred':>8}{'Q_ext':>9}{'eta':>8}{'refl%':>7}")
    for p in out["points"]:
        name = "%gx%g" % (p["ld"], p["lw"])
        if "beta" not in p:
            print(f"  {name:>9}{p['area_mm2']:>8.0f}   🔴 "
                  + p.get("error", "")[:40])
            continue
        S = abs((1 - p["beta"]) / (1 + p["beta"]))
        qe = f"{p['Q_ext']:>9.0f}" if p.get("Q_ext") else f"{'-':>9}"
        et = f"{p['eta']:>8.4f}" if "eta" in p else f"{'-':>8}"
        print(f"  {name:>9}{p['area_mm2']:>8.0f}{p['f_ghz']:>10.4f}"
              f"{p['fit']['s11_db']:>9.2f}{p['beta']:>9.4f}"
              f"{p['beta_pred']:>8.3f}" + qe + et + f"{100*S**2:>7.1f}")
    if not P:
        print("\n  🔴 nothing measured — no loop sizing is claimed.")
        return
    a0 = P[0]
    print(f"\n  V1 {a0['area_mm2']:.0f} mm^2: beta={a0['beta']:.4f} vs measured "
          f"{out['beta_ref']} -> {100*abs(a0['beta']/out['beta_ref']-1):.1f}% "
          + ("✅" if abs(a0["beta"]/out["beta_ref"] - 1) <= 0.20 else "🔴 FIRES"))
    # F1 — does area^2 hold?
    big = [p for p in P if abs(p["area_mm2"] - 1120) < 1]
    if big:
        b = big[0]
        r = b["beta"] / b["beta_pred"]
        print(f"  F1 1120 mm^2: beta={b['beta']:.3f} vs predicted "
              f"{b['beta_pred']:.3f} -> {r:.2f}x "
              + ("✅ area^2 holds within 2x"
                 if 0.5 <= r <= 2.0 else
                 "🔴 FIRES — area^2 does NOT hold on the loaded cavity"))
    # measured exponent, reported not refitted into the prior
    if len(P) >= 2:
        lo, hi = P[0], P[-1]
        n = (math.log(hi["beta"] / lo["beta"])
             / math.log(hi["area_mm2"] / lo["area_mm2"]))
        print(f"  measured exponent over {lo['area_mm2']:.0f}-{hi['area_mm2']:.0f} "
              f"mm^2: beta ~ area^{n:.2f}  (the small-loop model says 2.00)")
    # F2 / F3
    oob = [p for p in P if not (2.40 <= p["f_ghz"] <= 2.50)]
    print("  F2 " + ("✅ every loop keeps f0 inside 2.40-2.50"
                     if not oob else
                     "🔴 FIRES — out of band at area "
                     + ", ".join(f"{p['area_mm2']:.0f}" for p in oob)))
    es = [(p["area_mm2"], p["eta"]) for p in P if "eta" in p]
    if len(es) >= 2:
        drop = [a for (a, e), (_a0, e0) in zip(es[1:], es[:-1]) if e < e0 - 0.002]
        print("  F3 " + ("✅ eta does not fall as the loop grows — loop conductor "
                         "loss stays small against the plasma"
                         if not drop else
                         f"🔴 FIRES — eta FALLS from area {drop[0]:.0f} mm^2 up; "
                         f"loop loss is becoming comparable to the plasma and "
                         f"eta no longer means 'power into the plasma'"))
    # the design recommendation
    best = min(P, key=lambda p: abs(p["beta"] - BETA_TARGET))
    bname = "%gx%g" % (best["ld"], best["lw"])
    refl_best = 100 * abs((1 - best["beta"]) / (1 + best["beta"])) ** 2
    refl_now = 100 * abs((1 - a0["beta"]) / (1 + a0["beta"])) ** 2
    print(f"\n  🔑 CLOSEST TO CRITICAL COUPLING: {bname} mm "
          f"({best['area_mm2']:.0f} mm^2), beta={best['beta']:.3f}, "
          f"{refl_best:.1f}% reflected  (vs {refl_now:.1f}% at the present "
          f"{a0['area_mm2']:.0f} mm^2)")
    if best is P[-1] and best["beta"] < BETA_TARGET:
        print("  ⚠️ the best point is the LARGEST loop sampled and it is still "
              "undercoupled — beta is still rising at the edge of the range (§1). "
              "The optimum is NOT bracketed; extend the sweep or accept that a "
              "matching network must make up the rest.")
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
