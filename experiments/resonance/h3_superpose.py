"""H3 (superpose) — does the SAPPHIRE shift and the PLASMA shift add?

🔴 WHY. H3 measured the plasma pull (+31.6 MHz) in a cavity whose torch tube was
electromagnetically VACUUM — `torch_material = 1.0`, the R101-in-eigen bug
`h4_field` diagnosed on 2026-08-23. H4 measured the sapphire shift (-13.7 MHz for
the outer tube alone) with no plasma. Both are sound; neither is the built
cavity.

HYPOTHESES currently carries the loaded operating point as **≈2.4665 GHz**, and
it got there by ADDING those two numbers. CONVENTIONS §4b: two quantities are
comparable only if what sits between them did not change, and here it did — one
has a plasma, the other a dielectric. **A sum of two epochs is not a
measurement.** This rig measures the combination directly.

⚠️ There is a specific reason to doubt superposition. `h4_field` measured that
sapphire CONCENTRATES the bore field — +10.4% at r=8.2 mm, +7.7% at 6.6 mm — and
that is exactly where the plasma lives (r_i=2.0, r_o=8.5 mm). A plasma sitting in
a stronger field is a stronger perturbation, so the two effects should
REINFORCE, not merely add.

## Committed predictions (stated BEFORE the solve)

Measured within THIS rig as f(case) - f(vac_bare):

    superposition          df_both  =  df_torch + df_plasma
    from the record        df_torch ~ -13.7 MHz,  df_plasma ~ +31.6 MHz
                           -> df_both ~ +17.9 MHz   (f0 ~ 2.4688 GHz)

🔑 **I predict superposition FAILS in a specific direction**: the sapphire raises
E in the annulus the plasma occupies, energy goes as E^2, so the plasma pull
should grow ~10-20% and

    df_both  >  df_torch + df_plasma          (measured ~ +21 MHz, f0 ~ 2.472)

A prediction with a SIGN is falsifiable; "roughly additive" is not.

## Design

Four cases, TWO meshes, so no comparison crosses a mesh it did not have to:

    vac_bare   torch eps=1.0   no plasma  |  mesh A   <- the reference
    sap_bare   torch eps=11.6  no plasma  |  mesh A   -> df_torch
    vac_hot    torch eps=1.0   plasma     |  mesh B   -> df_plasma
    sap_hot    torch eps=11.6  plasma     |  mesh B   -> df_both

Each pair differs ONLY in the permittivity bound from the sidecar — the same
byte-identical-mesh control `h4_field` used to isolate the dielectric.

🔴 EIGEN ONLY (CONVENTIONS §7c). Target 2.40 sits BELOW every expected mode
(2.435-2.49) — Palace returns N modes ABOVE the target, and putting it above is
how H2b invented a mode (§1).

VERIFICATION
  V1  every case identifies TE011 by AZIMUTHAL ORDER (m=0), never by max-Q.
  V2  df_torch must reproduce h4_field's outer-tube -13.71 MHz within 15%, and
      df_plasma h3_annular's +31.57 MHz within 15%. A rig that cannot reproduce
      the two measurements it is combining is not measuring their combination.
  V3  every case prints the torch eps it actually solved with, from the sidecar.
      run()'s check_torch_bound refuses a mismatch outright.
FALSIFICATION
  🔴 F1  if |df_both - (df_torch + df_plasma)| <= 2 MHz, superposition HOLDS,
         my reinforcement prediction is WRONG, and HYPOTHESES' added estimate
         stands as-is. Say so plainly.
  🔴 F2  if df_both < df_torch + df_plasma the effects ANTI-reinforce — opposite
         to the field-concentration argument, which would then be wrong.
  🔴 F3  if the loaded f0 leaves 2.40-2.50 GHz the built cavity is out of the
         LDMOS band and H1's design point does NOT survive operation. This is
         the number the whole rig exists to get right.
  🔴 F4  if azimuthal order leaves m=0 the mode is not TE011; report the onset.
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
# 🔴 GEO_DESIGN, not GEO. GEO is the BARE cavity (groove 0,0) and exists
# for instrument rigs comparing against closed form. This rig produces
# DESIGN numbers, so it needs the cavity being built — groove 5x10 (H2).
# Every result this rig produced before 2026-08-23 was groove-free and is
# DISCARDED; see CONVENTIONS §7f.
from e0_solver_vs_math import GEO_DESIGN as GEO, eigen_cfg, run
from e0k2_anchor import design_point, wall_sigma
from e0k2_azim import sector_bins, read_sector_energy
from h3_loaded import drude, Z_FRAC, EIGEN_TARGET, SECTORS

TAG = "h3_superpose"
Q_BARE = 44384.0
P_REF = 1000.0
N_MODES = 4
# 🔴 §7ab — this cites a rig that cited a rig. The original basis is SOLVER
# CONVERGENCE (h3_eigen's PI_1 map), not physics. No physical provenance exists.
NE = 1.0e20                 # a CONVERGENCE choice inherited twice over
RI, RO = 2.00, 8.50         # h3_annular's operating point
SAPPHIRE = (11.6, 3.5e-05)  # eps_r, tan-delta — geometry.py's default (R99)
QUARTZ = (3.78, 1.0e-04)    # h4_field measured this material; 1/3 the contrast
VACUUM = (1.0, 3.5e-05)
CASE_TIMEOUT_S = 900.0
# 🔴 WIDER THAN THE BAND, ON PURPOSE. F3 asks whether the loaded mode leaves
# 2.40-2.50 GHz. If the IDENTIFICATION window were also 2.40-2.50, an
# out-of-band result would come back as "no m=0 mode found" — the search would
# silently swallow the exact outcome the rig exists to detect (§3: nothing is
# dropped). Identify over a wide window; let F3 judge the band.
TE011_WINDOW = (2.35, 2.65)
SIZE_FACTORS = ["1.5", "1.42", "1.58"]
# prior expectations, from the two rigs being combined
DF_TORCH_REF = -13.71       # h4_field outer-sap
DF_PLASMA_REF = +31.57      # h3_annular i2_o8p5

# 🔴 A SWEEP IN eps, NOT TWO MATERIALS. h3_superpose run 2 measured that the
# PLASMA SUPPRESSES THE DIELECTRIC's frequency shift by 78% (quartz -3.104 MHz
# cold -> -0.684 MHz loaded), because the plasma excludes field from the bore and
# cuts E_elec at the tube ~75%. That was ONE dielectric. Whether the suppression
# is a LAW — the same fraction at every eps — is what makes it extrapolable to
# sapphire, whose loaded case does not converge.
#
# 🔑 Two questions, one sweep, and the second is free:
#   1. is the suppressed fraction CONSTANT in eps?  (a law, or a coincidence)
#   2. where exactly does the eigensolver stop converging? Measured so far only
#      as a bracket: quartz (ratio eps+/|eps-| = 0.126) works, sapphire (0.386)
#      does not. eps = 2, 6, 8 fill it in at 0.066, 0.199, 0.266.
#
# ⚠️ eps=1.0 is the CONTROL and must give suppression = 0 by construction (the
# "dielectric" is vacuum, so its cold shift is zero and the ratio is 0/0). The
# report skips it rather than printing a NaN as a data point.
#
# Ordered by ascending eps so the cheap, convergent cases land before the
# expensive failure (§8: results land as obtained). Sapphire is last.
DIELECTRICS = [("vac", 1.00, 3.5e-05),
               ("e2",  2.00, 3.5e-05),
               ("qtz", 3.78, 1.0e-04),
               ("e6",  6.00, 3.5e-05),
               ("e8",  8.00, 3.5e-05),
               ("sap", 11.60, 3.5e-05)]

#          name        torch_material   plasma
CASES = [(f"{n}_{k}", (e, t), k == "hot")
         for n, e, t in DIELECTRICS for k in ("bare", "hot")]
# every dielectric except the vacuum control gets a superposition test
PAIRS = [(n, f"{n}_bare", f"{n}_hot") for n, e, _ in DIELECTRICS if e != 1.0]


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    w = 2.0 * math.pi * 2.45e9
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    eps_p, sig_p = drude(NE, w)
    print(f"  cavity a={a:.4f} L={L:.4f}  Q_bare={Q_BARE:,.0f}")
    print(f"  plasma r={RI}-{RO} mm  z=+-{Z_FRAC}L  ne={NE:.0e}  "
          f"eps={eps_p:.3f}  sigma={sig_p:.3g} S/m")
    print(f"  sapphire eps={SAPPHIRE[0]}  target={EIGEN_TARGET}\n", flush=True)
    out = {"q_bare": Q_BARE, "ne": NE, "eps_plasma": eps_p, "sigma_plasma": sig_p,
           "ri_mm": RI, "ro_mm": RO, "sapphire": list(SAPPHIRE),
           "df_torch_ref": DF_TORCH_REF, "df_plasma_ref": DF_PLASMA_REF,
           "points": []}

    for name, tmat, hot in CASES:
        tag = f"{TAG}_{name}"
        rec = {"case": name, "torch_eps_requested": tmat[0], "plasma": hot,
               "tag": tag}
        print(f"  --- {name}: torch eps={tmat[0]}  plasma={hot}", flush=True)
        # 🔴 GEO CARRIES --no-torch, AND IT WINS. The first launch passed
        # `list(GEO) + [--torch-material 11.6,...]` and every case meshed with
        # torch_material 1.0 — sap_bare printed "torch: eps=1.0" and would have
        # measured the sapphire shift of a vacuum tube, i.e. zero, which is
        # h4_field run 1's bug reproduced two hours after I wrote it up.
        # `--no-torch` does NOT remove the tube: the sidecar still records
        # torch [20.0, 1.5]. It pins the MATERIAL to vacuum. h4_field strips the
        # flag (its lines 161-163); this rig must too.
        # ⚠️ --no-inner is KEPT: h3_annular's plasma geometry and h4_field's
        # outer-sap reference (-13.71 MHz) both have the inner tubes disabled,
        # and V2 compares against exactly those.
        args = ([x for x in GEO if x != "--no-torch"]
                + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                   "--sectors", str(SECTORS),
                   "--torch-material", f"{tmat[0]},{tmat[1]}"])
        if hot:
            thick = RO - RI
            ph_mesh = min(1.0, max(0.30, thick / 6.0))
            args += ["--plasma", f"{RI},{RO},{zlo:.4f},{zhi:.4f}",
                     "--plasma-h", f"{ph_mesh:.3f}"]
        ok, last = False, ""
        for sf in SIZE_FACTORS:
            r = subprocess.run([sys.executable, "geometry.py", "--out",
                                f"{tag}.msh", "--size-factor", sf] + args,
                               capture_output=True, text=True)
            if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
                ok = True
                rec["size_factor"] = sf
                if sf != SIZE_FACTORS[0]:
                    print(f"    ⚠️ mesh needed size-factor {sf}; REPORTED",
                          flush=True)
                break
            last = (r.stdout + r.stderr)[-200:]
        if not ok:
            rec["error"] = f"mesh failed at all size factors: {last}"
            print(f"    🔴 {rec['error'][:150]}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue

        m = solveconf.load_meta(f"{tag}.msh")
        attrs = m["attributes"]
        bins = sector_bins(m)
        vols = sorted({v for k, v in attrs.items()
                       if isinstance(v, int) and k not in ("wall", "port")}
                      | set(attrs.get("air") or []))
        c = eigen_cfg(tag, m, mesh=f"{tag}.msh", sigma=sigma_w,
                      n=N_MODES, target=EIGEN_TARGET)
        c["Solver"]["Order"] = 2
        c["Domains"]["Postprocessing"]["Energy"] = (
            [{"Index": 1, "Attributes": [attrs["bore"]]}]
            + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
        # Materials: torch bound FROM THE SIDECAR (R101), plasma if hot,
        # everything else vacuum. run() refuses a torch/mesh mismatch.
        tm = (m.get("geometry_mm") or {}).get("torch_material")
        if tm is None:
            rec["error"] = "sidecar names no torch_material — refusing to guess"
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        rec["torch_eps"] = float(tm[0])
        # 🔴 DID THE MESH HONOUR WHAT WE ASKED FOR? run()'s check_torch_bound
        # compares the CONFIG against the SIDECAR, and this rig binds from the
        # sidecar, so those two can never disagree — the guard is blind to a
        # mesh that ignored the request. That is exactly how the first launch
        # got four vacuum tubes past it. Compare REQUESTED against MESHED.
        if abs(float(tm[0]) - tmat[0]) > 1e-9:
            rec["error"] = (f"mesh ignored the request: asked for eps="
                            f"{tmat[0]}, sidecar says {float(tm[0])}. "
                            f"Refusing to measure the wrong dielectric.")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        print(f"    torch: requested eps={tmat[0]}, mesh has {float(tm[0])} ✅",
              flush=True)
        plain = set(vols)
        mats = []
        if attrs.get("torch") is not None:
            plain.discard(attrs["torch"])
            mats.append({"Attributes": [attrs["torch"]],
                         "Permittivity": float(tm[0]), "LossTan": float(tm[1]),
                         "Permeability": 1.0})
        if hot:
            if attrs.get("plasma") is None:
                rec["error"] = "no plasma attribute in a hot case"
                print(f"    🔴 {rec['error']}", flush=True)
                out["points"].append(rec); save(out); continue
            plain.discard(attrs["plasma"])
            mats.append({"Attributes": [attrs["plasma"]], "Permittivity": eps_p,
                         "Permeability": 1.0, "Conductivity": sig_p})
        mats.insert(0, {"Attributes": sorted(plain), "Permittivity": 1.0,
                        "Permeability": 1.0})
        c["Domains"]["Materials"] = mats
        rec["tets"] = m["tets"]
        try:
            run(tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
        except RuntimeError as e:
            rec["error"] = str(e)[:200]
            print(f"    🔴 {rec['error'][:150]}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue

        # mode identification: copied from h3_annular, which is the rig this
        # one extends. V1/F4 — AZIMUTHAL ORDER, never max-Q (the probe that
        # picked by max(Q) selected a mode with no bore field at all).
        modes = eigmodes.read(tag)
        qs = {}
        for line in (pathlib.Path("postpro") / tag /
                     "eig.csv").read_text().splitlines()[1:]:
            pp = line.split(",")
            if len(pp) > 3:
                qs[round(float(pp[0]))] = float(pp[3])
        sec = read_sector_energy(tag, bins)
        cands = []
        for md in modes:
            u = sec.get(float(md["m"]))
            if u is None and sec:
                u = sec[min(sec, key=lambda x: abs(x - md["m"]))]
            m_az, conf, harm = azimuthal.order(u) if u else (None, 0, {})
            if m_az == 0 and TE011_WINDOW[0] < md["f"] < TE011_WINDOW[1]:
                cands.append((md, harm))
        if not cands:
            rec["error"] = (f"F4: no m=0 mode in {TE011_WINDOW}; modes "
                            f"{[round(md['f'],5) for md in modes]}")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        if len(cands) > 1:
            rec["ambiguous"] = [round(cc[0]["f"], 6) for cc in cands]
            print(f"    ⚠️ {len(cands)} m=0 candidates {rec['ambiguous']} — "
                  f"taking nearest 2.45 and saying so", flush=True)
        pick, harm = min(cands, key=lambda cc: abs(cc[0]["f"] - 2.45))
        Q = qs.get(pick["m"], 0.0)
        rec.update(f_ghz=pick["f"], Q=Q, A2_A0=harm.get(2, 0.0))
        print(f"    f={pick['f']:.6f} GHz  Q={Q:,.0f}  "
              f"A2/A0={harm.get(2,0):.4f}", flush=True)
        out["points"].append(rec); save(out)
    _report(out)


def _report(out):
    P = {p["case"]: p for p in out["points"] if "f_ghz" in p}
    print("\n" + "=" * 78)
    print(f"  {'case':>10}{'torch eps':>11}{'plasma':>8}{'f GHz':>11}"
          f"{'df MHz':>10}{'Q':>9}")
    ref = P.get("vac_bare")
    for p in out["points"]:
        if "f_ghz" not in p:
            print(f"  {p['case']:>10}   🔴 {p.get('error','no result')[:52]}")
            continue
        df = (p["f_ghz"] - ref["f_ghz"]) * 1e3 if ref else float("nan")
        print(f"  {p['case']:>10}{p['torch_eps']:>11.1f}"
              f"{str(p['plasma']):>8}{p['f_ghz']:>11.6f}{df:>10.2f}"
              f"{p['Q']:>9,.0f}")
    print()
    if not ref:
        print("  🔴 vac_bare MISSING — every df is relative to it, so nothing "
              "is claimed.")
        return
    if "vac_hot" not in P:
        print("  🔴 vac_hot MISSING — df_plasma is undefined, so no superposition "
              "test is possible. Nothing is claimed.")
        return
    d_p = (P["vac_hot"]["f_ghz"] - ref["f_ghz"]) * 1e3
    print(f"  V2 df_plasma: {d_p:+.2f} MHz vs record {out['df_plasma_ref']:+.2f}"
          f" -> {100*abs(d_p/out['df_plasma_ref']-1):.1f}% "
          + ("✅" if abs(d_p/out["df_plasma_ref"]-1) <= 0.15 else "🔴 FIRES"))
    # 🔴 EVERY pair is reported, converged or not (§3: nothing is dropped, and a
    # dielectric that DIVERGES is itself a result about the instrument).
    tested = 0
    for name, bare, hot in PAIRS:
        if bare not in P:
            print(f"\n  {name}: bare case missing — no test")
            continue
        d_t = (P[bare]["f_ghz"] - ref["f_ghz"]) * 1e3
        if name == "sap":
            e = abs(d_t / out["df_torch_ref"] - 1)
            print(f"\n  V2 df_torch(sap): {d_t:+.2f} MHz vs record "
                  f"{out['df_torch_ref']:+.2f} -> {100*e:.1f}% "
                  + ("✅" if e <= 0.15 else "🔴 FIRES"))
        else:
            print(f"\n  df_torch({name}): {d_t:+.2f} MHz")
        if hot not in P:
            print(f"  🔴 {name}: loaded case did NOT converge — F1/F2 cannot be "
                  f"evaluated for this dielectric. The additive estimate "
                  f"{ref['f_ghz'] + (d_t + d_p)/1e3:.6f} GHz stays an ESTIMATE.")
            continue
        tested += 1
        d_b = (P[hot]["f_ghz"] - ref["f_ghz"]) * 1e3
        add, resid = d_t + d_p, d_b - (d_t + d_p)
        print(f"  df_torch {d_t:+.2f}  df_plasma {d_p:+.2f}  sum {add:+.2f}  "
              f"MEASURED {d_b:+.2f}  residual {resid:+.2f} MHz")
        if abs(resid) <= 2.0:
            print("  🔴 F1 FIRES — SUPERPOSITION HOLDS within 2 MHz. The "
                  "reinforcement prediction was WRONG; the added estimate stands.")
        elif resid > 0:
            # 🔴 STATE THE RESULT, NOT THE MECHANISM. This line used to end
            # "as predicted: the dielectric concentrates the field where the
            # plasma sits" — asserting at runtime a mechanism that is NOT
            # established. h4_field measured quartz DILUTING the bore field
            # (-5.7% at r=8.45 mm), which predicts the opposite sign, and this
            # rig declares no probe rake so it cannot settle it. A positive
            # cross-term needs no claim about the sign of the field change.
            # §7c: a rig printing a claim it did not measure is the failure that
            # let a RETRACTED assertion run as fact.
            print(f"  ✅ effects REINFORCE by {resid:+.2f} MHz "
                  f"({100*resid/add:.0f}% of the sum) — superposition FAILS. "
                  f"⚠️ MECHANISM UNRESOLVED: measured cross-term only; this rig "
                  f"has no probe rake and cannot attribute it.")
        else:
            print(f"  🔴 F2 FIRES — effects ANTI-reinforce by {resid:.2f} MHz; "
                  f"the field-concentration argument has the wrong sign.")
        f0 = P[hot]["f_ghz"]
        print(f"  🔑 BUILT CAVITY OPERATING ({name}): f0 = {f0:.6f} GHz, "
              f"Q = {P[hot]['Q']:,.0f}")
        print("  F3 " + (f"✅ inside 2.40-2.50 — H1's design point survives "
                         f"operation with {name}"
                         if 2.40 <= f0 <= 2.50 else
                         f"🔴 FIRES — {f0:.6f} GHz is OUTSIDE 2.40-2.50. The "
                         f"built cavity is out of the LDMOS band under load."))
    if not tested:
        print("\n  🔴 NO dielectric produced a converged loaded case. "
              "Superposition is UNTESTED and nothing is claimed about it.")

    # --- IS THE SUPPRESSION A LAW? The cold shift and the loaded shift for each
    # dielectric, each measured WITHIN one mesh pair, so the ratio is clean.
    hot0 = P.get("vac_hot")
    rows = []
    for name, bare, hot in PAIRS:
        if bare not in P:
            continue
        cold = (P[bare]["f_ghz"] - ref["f_ghz"]) * 1e3
        eps = P[bare].get("torch_eps")
        if hot not in P or not hot0:
            rows.append((name, eps, cold, None, None))
            continue
        loaded = (P[hot]["f_ghz"] - hot0["f_ghz"]) * 1e3
        supp = 1.0 - loaded / cold if cold else None
        rows.append((name, eps, cold, loaded, supp))
    if rows:
        print(f"\n  SUPPRESSION OF THE DIELECTRIC SHIFT BY THE PLASMA")
        print(f"  {'case':>6}{'eps':>7}{'ratio':>8}{'cold MHz':>11}"
              f"{'loaded MHz':>12}{'suppressed':>12}")
        for name, eps, cold, loaded, supp in rows:
            ratio = eps / 30.089 if eps else float("nan")
            if loaded is None:
                print(f"  {name:>6}{eps:>7.2f}{ratio:>8.3f}{cold:>11.3f}"
                      f"{'DID NOT CONVERGE':>24}")
            else:
                print(f"  {name:>6}{eps:>7.2f}{ratio:>8.3f}{cold:>11.3f}"
                      f"{loaded:>12.3f}{100*supp:>11.1f}%")
        got = [r for r in rows if r[4] is not None]
        if len(got) >= 2:
            ss = [r[4] for r in got]
            spread = max(ss) - min(ss)
            print(f"\n  suppression spans {100*min(ss):.1f}-{100*max(ss):.1f}% "
                  f"over eps {got[0][1]:g}-{got[-1][1]:g} "
                  f"(spread {100*spread:.1f} points)")
            if spread <= 0.05:
                # 🔴 THIS MESSAGE USED TO END "Extrapolating it to sapphire is
                # justified." It is not. Constancy over the MEASURED range says
                # nothing about a point 2x beyond the last one — that is §11's
                # error wearing a law's clothes, and the failed cases are failed
                # precisely because they are outside the range. State the range,
                # name anything past it as extrapolation, and let the reader
                # decide. Third time today a rig asserted past its own data.
                lo_e, hi_e = got[0][1], got[-1][1]
                print(f"  ✅ CONSTANT within 5 points OVER eps {lo_e:g}-{hi_e:g} "
                      f"— a LAW on that interval, set by the plasma's field "
                      f"exclusion and independent of the dielectric.")
                drift = (got[-1][4] - got[0][4]) / max(1, len(got) - 1)
                print(f"     ⚠️ drift {100*drift:+.2f} points per step; NOT flat, "
                      f"just nearly so.")
                miss = [r[1] for r in rows if r[4] is None]
                if miss:
                    print(f"     ⚠️ eps {', '.join('%g' % m for m in miss)} did "
                          f"NOT converge and are OUTSIDE the interval. Applying "
                          f"the law there is an EXTRAPOLATION "
                          f"({max(miss)/hi_e:.1f}x past the last point), not a "
                          f"measurement. Label it as one wherever it is used.")
            else:
                print("  🔴 NOT constant — the suppression DEPENDS on eps, so the "
                      "78% measured at quartz must NOT be extrapolated to "
                      "sapphire. Report the trend; do not fit two points.")
        elif len(got) == 1:
            print("\n  ⚠️ only one converged pair — a law needs at least two "
                  "(CONVENTIONS §11). Nothing is claimed about eps-dependence.")
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
