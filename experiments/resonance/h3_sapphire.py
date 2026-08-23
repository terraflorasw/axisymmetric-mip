"""H3 (sapphire) — the loaded point at eps=11.6, where the eigensolver cannot go.

🔴 WHY. The suppression law — a plasma cuts a dielectric's frequency shift by
78% — is VALIDATED over eps 2-6 (77.7 / 78.0 / 78.3%, 0.6 points, holding through
the dilute->concentrate back-reaction crossover). Sapphire is eps=11.6, and
h3_superpose CANNOT reach it: eigen's divergence-free PCG stagnates once the
positive-to-negative permittivity ratio passes ~0.2-0.27, and 11.6/30.089 = 0.386
is well past that. Two 900 s timeouts confirmed it.

So "sapphire's loaded shift is about -2.9 MHz" is currently a **1.9x
EXTRAPOLATION** beyond the last measured point, and the design claim resting on
it — *torch material matters ~4.5x less in operation than cold measurements
suggest* — is only as good as that extrapolation.

🔑 DRIVEN CAN REACH IT, and cheaply, because this test needs only the dip
LOCATION. A dip's position is well defined even at the -0.06 dB a loaded cavity
gives this loop; it is the WIDTH that needs depth. Frequencies are all the
suppression law is made of.

## Committed predictions (stated BEFORE the solve)

Measured within THIS rig, each shift relative to its own vacuum-torch case at the
same density:

    quartz  (eps=3.78)   -0.68 MHz    (h3_superpose measured this in EIGEN;
                                        reproducing it validates driven here)
    sapphire (eps=11.6)  -2.9 MHz     (the law: -13.71 cold x 0.22)

🔴 If sapphire's loaded shift is NOT -2.9 +- 1.0 MHz, the suppression law does
NOT extrapolate to eps=11.6, and the "material matters 4.5x less" claim is
WITHDRAWN to a quartz-only statement. Say so plainly.

VERIFICATION
  V1  the vacuum case must reproduce h3_driven's ne=1e20 point, f0=2.4824 GHz,
      within 1 MHz. Same rig family, same mesh recipe, same density.
  V2  the quartz case must reproduce h3_superpose's EIGEN loaded shift of
      -0.684 MHz within 0.3 MHz. This is the driven-vs-eigen cross-check at a
      dielectric, and it is what licenses trusting driven at eps=11.6.
  V3  every case binds its torch permittivity FROM THE MESH SIDECAR and refuses
      a mismatch (R101 extended, in run()).
FALSIFICATION
  🔴 F1  sapphire loaded shift outside -2.9 +- 1.0 MHz -> the law does not reach
         eps=11.6. Withdraw the design claim; do not rescale the law to fit.
  🔴 F2  if continuation breaks (a step larger than CONTINUATION_JUMP_MHZ) the
         mode was lost; report it rather than following the nearest dip.
  🔴 F3  if the loaded f0 leaves 2.40-2.50 GHz, H1's design point does not
         survive a sapphire torch under load.

⚠️ SHARES h3_driven's ANALYSIS (local_minima, fit_dip, read_s11, sweep) and
duplicates only the DRIVER. CONVENTIONS §7c: duplicate the driver, share the
analysis — a rig that branches on what it is measuring is how h3_loaded acquired
five silent bugs.
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
# 🔴 GEO_DESIGN, not GEO. GEO is the BARE cavity (groove 0,0) and exists
# for instrument rigs comparing against closed form. This rig produces
# DESIGN numbers, so it needs the cavity being built — groove 5x10 (H2).
# Every result this rig produced before 2026-08-23 was groove-free and is
# DISCARDED; see CONVENTIONS §7f.
from e0_solver_vs_math import GEO_DESIGN as GEO, run
from e0k2_anchor import design_point, LOOP_PHI, LOOP_RW, LOOP_GAP, CAP_R_FRAC
from h3_loaded import drude, Z_FRAC, SECTORS, LOOP_LD, LOOP_LW
from h3_driven import (local_minima, fit_dip, read_s11, sweep,
                       COARSE_LO_GHZ, COARSE_HI_GHZ, COARSE_STEP_GHZ,
                       COARSE_MIN_DEPTH_DB, COARSE_EDGE_MHZ,
                       CONTINUATION_JUMP_MHZ, SHALLOW_DB, Q_BARE, RI, RO,
                       CASE_TIMEOUT_S, SIZE_FACTORS)

TAG = "h3_sapphire"
NE = 1.0e20
# (name, eps, tand). Ascending eps so continuation takes small steps and the
# cheap validated cases land before the one that cannot be checked any other way.
CASES = [("vac", 1.00, 3.5e-05),
         ("qtz", 3.78, 1.0e-04),
         ("sap", 11.60, 3.5e-05)]
# 🔴 THE CONTINUATION SEED IS A MEASURED POINT IN THIS REGIME, NOT AN ANALYTIC
# ONE FROM ANOTHER. Run 1 seeded at the analytic UNLOADED TE011 (2.4500) and the
# very first case selected 2.4472 instead of 2.4824 — because at ne=1e20 the
# plasma pull is +32 MHz, so the unloaded frequency is 32 MHz away while a
# competing feature sits 2.8 MHz away. Continuation only works if the FIRST step
# is small; seeding it outside the regime makes step one the largest of the run.
# ⚠️ h3_driven gets away with the analytic seed only because its first case is
# ne=1e18, where the pull is +2.4 MHz. Same seed, different regime, wrong answer.
SEED_GHZ = 2.4824           # h3_driven, ne=1e20, vacuum torch, MEASURED
SEED_TOL_MHZ = 1.0          # the vac case must land here or the run ABORTS
PRED_QTZ_MHZ = -0.684       # h3_superpose, EIGEN
PRED_SAP_MHZ = -2.9         # the suppression law extrapolated
SAP_TOL_MHZ = 1.0


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build_mesh(tag, a, L, zlo, zhi, eps_t, tand_t, rec):
    """Loop + torch AT A CHOSEN PERMITTIVITY + plasma.

    🔴 GEO carries --no-torch, which does not remove the tube but pins its
    material to vacuum and BEATS a later --torch-material. h3_superpose lost a
    whole launch to that. Strip it. --no-inner is KEPT: every shift this rig
    compares against was measured outer-tube-only.
    """
    thick = RO - RI
    ph_mesh = min(1.0, max(0.30, thick / 6.0))
    args = ([x for x in GEO if x != "--no-torch"]
            + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
               "--sectors", str(SECTORS),
               "--torch-material", f"{eps_t},{tand_t}",
               "--plasma", f"{RI},{RO},{zlo:.4f},{zhi:.4f}",
               "--plasma-h", f"{ph_mesh:.3f}",
               "--loop", f"{LOOP_LD},{LOOP_LW},{LOOP_RW},{LOOP_GAP}",
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
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    eps_p, sig_p = drude(NE, w)
    print(f"  cavity a={a:.4f} L={L:.4f}   plasma r={RI}-{RO} mm, "
          f"ne={NE:.0e}, eps={eps_p:+.3f}, sigma={sig_p:.4g} S/m")
    print(f"  wide sweep {COARSE_LO_GHZ}-{COARSE_HI_GHZ} GHz @ "
          f"{COARSE_STEP_GHZ*1e6:.0f} kHz; selection by CONTINUATION")
    print(f"  predicted: quartz {PRED_QTZ_MHZ:+.3f} MHz (eigen), "
          f"sapphire {PRED_SAP_MHZ:+.1f} +- {SAP_TOL_MHZ:.1f} MHz (the law)\n",
          flush=True)
    out = {"ne": NE, "eps_plasma": eps_p, "sigma_plasma": sig_p,
           "ri_mm": RI, "ro_mm": RO, "q_bare_no_loop": Q_BARE,
           "pred_qtz_mhz": PRED_QTZ_MHZ, "pred_sap_mhz": PRED_SAP_MHZ,
           "points": []}
    expect = SEED_GHZ
    for name, eps_t, tand_t in CASES:
        tag = f"{TAG}_{name}"
        rec = {"case": name, "torch_eps_requested": eps_t, "tag": tag}
        print(f"  --- {name}: torch eps={eps_t}", flush=True)
        meta = build_mesh(tag, a, L, zlo, zhi, eps_t, tand_t, rec)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_err','')[:150]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        rec.pop("_err", None)
        attrs = meta["attributes"]
        rec["tets"] = meta["tets"]
        tm = (meta.get("geometry_mm") or {}).get("torch_material")
        if tm is None or abs(float(tm[0]) - eps_t) > 1e-9:
            rec["error"] = (f"mesh ignored the request: asked eps={eps_t}, "
                            f"sidecar says {tm}. Refusing to measure the wrong "
                            f"dielectric.")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        rec["torch_eps"] = float(tm[0])
        print(f"    torch: requested {eps_t}, mesh has {float(tm[0])} ✅",
              flush=True)
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
        i_sel, f_sel, v_sel = min(mins, key=lambda m: abs(m[1] - expect))
        jump = (f_sel - expect) * 1e3
        rec["jump_mhz"] = jump
        if abs(jump) > CONTINUATION_JUMP_MHZ:
            rec["error"] = (f"F2: continuation BROKE — nearest minimum to "
                            f"{expect:.4f} is {f_sel:.4f} ({jump:+.1f} MHz)")
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
        if abs(fi["s11_db"]) < SHALLOW_DB:
            rec["shallow"] = True
            print(f"    ⚠️ |S11|min={fi['s11_db']:.3f} dB — deeply undercoupled; "
                  f"the LOCATION is what this rig needs and it is well defined, "
                  f"but any Q from it is low confidence.", flush=True)
        if "Q_L" in fi:
            rec["Q0"] = fi["Q0"]
            rec["eta"] = 1.0 - fi["Q0"] / Q_BARE
        print(f"    f0={fi['f0']:.6f} GHz ({jump:+.2f} MHz from expected)"
              + (f"  lw={fi['linewidth_mhz']:.2f} MHz  eta={rec['eta']:.4f}"
                 if "eta" in rec else "  (width not measurable)"), flush=True)
        # 🔴 ABORT ON A BAD SEED, do not build two more cases on it. V1 checks
        # this too, but V1 runs at the END — by then the quartz and sapphire
        # cases have followed the wrong mode and produced a SELF-CONSISTENT
        # wrong answer, which is far more dangerous than a crash.
        if name == "vac":
            off = abs(fi["f0"] - SEED_GHZ) * 1e3
            if off > SEED_TOL_MHZ:
                rec["error"] = (f"SEED CHECK FAILED: vacuum case landed at "
                                f"{fi['f0']:.4f} GHz, {off:.1f} MHz from the "
                                f"measured {SEED_GHZ} (h3_driven, same density, "
                                f"same geometry). Continuation would follow the "
                                f"WRONG MODE for every later case and the shifts "
                                f"would still look plausible. ABORTING.")
                print(f"    🔴 {rec['error']}", flush=True)
                out["points"].append(rec); save(out)
                _report(out)
                return
        expect = fi["f0"]
        out["points"].append(rec); save(out)
    _report(out)


def _report(out):
    P = {p["case"]: p for p in out["points"] if "f_ghz" in p}
    print("\n" + "=" * 78)
    print(f"  {'case':>6}{'eps':>7}{'f0 GHz':>11}{'shift MHz':>11}{'|S11| dB':>10}")
    ref = P.get("vac")
    for p in out["points"]:
        if "f_ghz" not in p:
            print(f"  {p['case']:>6}   🔴 {p.get('error','no result')[:52]}")
            continue
        sh = (p["f_ghz"] - ref["f_ghz"]) * 1e3 if ref else float("nan")
        print(f"  {p['case']:>6}{p['torch_eps']:>7.2f}{p['f_ghz']:>11.6f}"
              f"{sh:>11.3f}{p['fit']['s11_db']:>10.2f}")
    print()
    if not ref:
        print("  🔴 vacuum case MISSING — every shift is relative to it. "
              "Nothing is claimed.")
        return
    df = abs(ref["f_ghz"] - 2.4824) * 1e3
    print(f"  V1 vac f0={ref['f_ghz']:.4f} vs h3_driven 2.4824 -> {df:.2f} MHz "
          + ("✅" if df <= 1.0 else "🔴 FIRES"))
    q = P.get("qtz")
    if q:
        sh = (q["f_ghz"] - ref["f_ghz"]) * 1e3
        e = abs(sh - out["pred_qtz_mhz"])
        print(f"  V2 quartz shift {sh:+.3f} MHz vs EIGEN "
              f"{out['pred_qtz_mhz']:+.3f} -> {e:.3f} MHz "
              + ("✅ driven and eigen agree at a dielectric"
                 if e <= 0.3 else "🔴 FIRES — driven is NOT validated at a "
                 "dielectric, so eps=11.6 cannot be trusted either"))
    else:
        print("  🔴 quartz MISSING — the driven-vs-eigen cross-check at a "
              "dielectric did not run; sapphire is UNVALIDATED.")
    s = P.get("sap")
    if not s:
        print("\n  🔴 SAPPHIRE MISSING — the law stays a 1.9x extrapolation and "
              "the 'material matters 4.5x less' claim stays provisional.")
        return
    sh = (s["f_ghz"] - ref["f_ghz"]) * 1e3
    e = abs(sh - out["pred_sap_mhz"])
    print(f"\n  🔑 SAPPHIRE LOADED SHIFT: {sh:+.3f} MHz "
          f"(predicted {out['pred_sap_mhz']:+.1f} from the law, cold was -13.71)")
    print(f"     implied suppression {100*(1 - sh/-13.71):.1f}% "
          f"vs 78% measured over eps 2-6")
    print("  F1 " + (f"✅ within {SAP_TOL_MHZ:.1f} MHz — THE LAW REACHES eps=11.6. "
                     f"The design claim stands on measurement, not extrapolation."
                     if e <= SAP_TOL_MHZ else
                     f"🔴 FIRES — {e:.2f} MHz off. The suppression law does NOT "
                     f"extrapolate to eps=11.6. WITHDRAW the 'material matters "
                     f"4.5x less' claim to a quartz-only statement; do NOT "
                     f"rescale the law to fit this point."))
    print("  F3 " + ("✅ inside 2.40-2.50 — H1's design point survives a sapphire "
                     "torch under load"
                     if 2.40 <= s["f_ghz"] <= 2.50 else
                     f"🔴 FIRES — {s['f_ghz']:.6f} GHz is OUTSIDE the LDMOS band"))
    print(f"\n  wrote {TAG}.result.json")


if __name__ == "__main__":
    main()
