"""EIGEN + PURITY on the DESIGN cavity: what mode is at 2.4515, and is it TE011?

🔴 WHY THIS RIG EXISTS. Driven and eigen disagree about the design cavity, and
the disagreement is 11.5 MHz wide:

  `h3_driven` cold locator, 2.40-2.52 GHz @ 25 kHz, ONE minimum:
      2.451500 GHz, Q0 = 8,462, beta = 0.208, |S11| = -3.67 dB
  `h3_cold` eigen (N=4, target 2.38) returned FOUR modes and NONE at 2.4515:
      2.440003 (m_az=1, identification_uncertain) / 2.494440 / 2.606499 / 2.607352

2.451500 is +0.939 MHz from the ANCHORED grooved-no-loop TE011 (2.450561,
`h3_ladder` step 2, which reproduced H2 to 2.0%). So driven says the loop barely
moves TE011. h3_cold says TE011 is 10.5 MHz lower. Both cannot be right.

🔑 THREE CANDIDATE EXPLANATIONS, and this rig separates them BY CONSTRUCTION:
  (a) SETTINGS — N=4 was too few / target 2.38 placed badly, and eigen simply
      never returned the mode. Then 2.4515 is TE011 and h3_cold's list is short.
  (b) MESH — h3_cold meshes GEO_DESIGN with `--no-torch` (no torch body, no
      plasma region). h3_driven strips `--no-torch` and meshes a torch at
      eps=1.0 AND a plasma annulus at eps=1.0. Electrically both are vacuum, so
      this SHOULD NOT move a mode 11.5 MHz. If it does, that is the finding.
  (c) NOT AN EIGENMODE — the driven dip is a feed/port artifact. Q ~ 8,500 and
      beta = 0.208 argue against it, but it must be excluded by looking.

⚠️ TWO STEPS, ONE VARIABLE. Both use IDENTICAL eigen settings; they differ ONLY
in how the mesh is built. That is the whole design — it is why (a) and (b) can
be told apart at all, and why N is NOT set to h3_cold's 4.

🔴 EIGEN ONLY. CONVENTIONS §7c, "one rig, one solver": three failed launches and
two silently wrong values came from one file switching solver. The driven half
of this comparison is `h3_driven` and it has already run.

🔑 NO SELECTION HEURISTIC. This rig does NOT pick "the TE011". It reports every
mode in the window with f, Q, m_az, A2/A0 AND PURITY, and lets the reader see
what is there. Selecting by "lowest A2/A0" is what produced the wrong answer
that started this (§7u: h3_cold flagged `identification_uncertain: True` on that
exact point and I supplied the confidence anyway).

VERIFICATION
  V1  the grooved-no-loop anchor is 2.450561 GHz (`h3_ladder` step 2, which
      reproduced H2's TM111 shift to 2.0%). A mode within ~2 MHz of it, with
      HIGH PURITY, is TE011 barely perturbed by the loop -> driven is right.
  V2  the groove must be in BOTH meshes (sidecar `geometry_mm.groove` = 5,10).
      A groove-free mesh here is a different cavity (KNOWN.md § THE FILTER).
  V3  both steps must return a mode list that BRACKETS 2.4515 — i.e. at least
      one mode below and one above. A list that stops short cannot say "absent".
      🔴 If it does not bracket, this rig reports INCONCLUSIVE, not "no mode".
FALSIFICATION
  🔴 F1  if BOTH meshes show a high-purity mode at ~2.4515, explanation (a) is
         confirmed: h3_cold's N=4 was too few, and 12,368 was never TE011's Q.
  🔴 F2  if ONLY the driven-style mesh shows it, the torch/plasma REGIONS move a
         mode 11.5 MHz while being electrically vacuum. That is a meshing
         defect and it invalidates comparing any two rigs that differ this way.
  🔴 F3  if NEITHER shows a mode near 2.4515, the driven dip is not an
         eigenmode. Then `h3_driven`'s whole loaded series is measuring
         something the eigen formulation does not contain, and its eta column
         is suspect — report it and stop, do not rationalise.
  🔴 F4  if the mode nearest 2.4515 has LOW purity (spread > 0.10), it is not
         TE011 however well its frequency matches. Frequency agreement with an
         anchor is necessary, not sufficient — that is exactly the reasoning
         that produced the retracted -10.56 MHz story.
"""
import json
import values
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
import eigmodes
from e0_solver_vs_math import GEO_DESIGN, eigen_cfg, run, volume_attrs
from e0k2_anchor import design_point, wall_sigma, LOOP_PHI, LOOP_RW, LOOP_GAP
from h3_loaded import SECTORS, Z_FRAC, CAP_R_FRAC
from azimuthal import order as az_order
from e0k2_azim import sector_bins, read_sector_energy
from h3_ladder import purity, PROBE_PHI_DEG, PROBE_R_FRAC

TAG = "h3_step3"

# 🔴 IDENTICAL FOR BOTH STEPS. The comparison is meaningless otherwise.
# target 2.38 is h3_cold's, kept deliberately so a difference cannot be blamed
# on target placement. N is 8, NOT h3_cold's 4: four modes could not bracket
# 2.4515 and report its ABSENCE, and V3 requires bracketing.
# ⚠️ §7p — this is not padding. 2.4400 and 2.4944 are known to sit either side
# of the frequency in question, and h3_cold needed all four of its modes to
# reach 2.6074. Eight reaches past the region with room to see neighbours.
N_MODES = 8
EIGEN_TARGET = 2.38
CASE_TIMEOUT_S = 2700.0

# 🔑 THE THIRD STEP IS THE MACHINE, AND IT IS THE POINT OF THE RERUN.
# Steps 1-2 both left the port at PEC — i.e. SHORTED the loop — which is what
# `h3_step3`'s first run proved was happening everywhere (CONVENTIONS §7v).
# Step 3 terminates the same face in 50 ohm, exactly as the driven template
# does, so eigen finally solves the cavity the machine actually is.
# ⚠️ Its Q is LOADED (Q_L), not Q0 — a lumped port is a loss channel.
# 🔑 It is the ONLY step that can answer the open question: **what is TE011's
# PURITY in the operating configuration?** Driven cannot (it emits no purity);
# a shorted-loop eigen answers a different cavity.
STEPS = [("cold",   "pec"),        # reproduce h3_cold exactly — the artifact
         ("driven", "pec"),        # same, on the torch/plasma mesh
         ("driven", "lumped")]     # 🔑 THE MACHINE

LOOP_LD, LOOP_LW = values.get("loop.size.mm")   # the DESIGN loop, 176 mm^2
RI, RO = 2.00, 8.50                # h3_driven's plasma annulus
WINDOW = (2.35, 2.65)

ANCHOR_GROOVED_GHZ = 2.450561      # h3_ladder step 2, externally anchored
DRIVEN_DIP_GHZ = 2.451500          # h3_driven cold locator
H3COLD_PICK_GHZ = 2.440003         # what h3_cold called TE011
BRACKET_TOL_MHZ = 2.0
PURITY_SPREAD_MAX = 0.10           # F4; deliberately loose — see below

# ⚠️ 0.10, NOT the ladder's 0.02. The bare-cavity gate (P>=0.99, spread<=0.02)
# is NOT calibrated for a looped cavity and no looped measurement exists yet —
# that is the gap this rig exists to close. A loose threshold that only rejects
# CLEARLY hybridised modes is honest; the tight one would decide the answer in
# advance. Report the number; the verdict stays provisional either way.


def save(out):
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build(tag, style, a, L, rec):
    """Two mesh styles, ONE geometry. `style` is the only thing that varies.

    'cold'   — exactly h3_cold: GEO_DESIGN as-is, so `--no-torch` STAYS and
               there is no torch body and no plasma region.
    'driven' — exactly h3_driven's ne=0 case: `--no-torch` STRIPPED, a torch at
               eps=1.0 tand=3.5e-05, and a plasma annulus at eps=1, sigma=0.
               Electrically vacuum, geometrically present.
    """
    zhi = Z_FRAC * L
    zlo = -zhi
    if style == "cold":
        base = list(GEO_DESIGN)
        extra = []
    else:
        base = [x for x in GEO_DESIGN if x != "--no-torch"]
        extra = ["--torch-material", "1.0,3.5e-05",
                 "--plasma", f"{RI},{RO},{zlo:.4f},{zhi:.4f}",
                 "--plasma-h", "1.000"]
    args = (base + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                    "--sectors", str(SECTORS),
                    "--loop", f"{LOOP_LD},{LOOP_LW},{LOOP_RW},{LOOP_GAP}",
                    "--loop-cap", f"{CAP_R_FRAC * a:.4f}",
                    "--loop-phi", LOOP_PHI] + extra)
    rec["mesh_style"] = style
    rec["geometry_argv"] = args
    for sf in ("1.5", "1.42", "1.58"):
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            if sf != "1.5":
                print(f"    ⚠️ mesh needed size-factor {sf}; REPORTED", flush=True)
            return solveconf.load_meta(f"{tag}.msh")
        rec["_err"] = (r.stdout + r.stderr)[-200:]
    return None


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    print(f"  a={a:.4f} L={L:.4f}   closed-form TE011 = {exact:.6f} GHz")
    print(f"  loop {LOOP_LD:g}x{LOOP_LW:g} mm = {LOOP_LD*2*LOOP_LW:.0f} mm^2 "
          f"(GLOSSARY: the second number is a HALF-width)")
    print(f"  eigen: target={EIGEN_TARGET}, N={N_MODES} — IDENTICAL for both "
          f"steps, so only the MESH differs")
    print(f"  the question: is there a mode at {DRIVEN_DIP_GHZ:.6f}, and is it "
          f"TE011?\n", flush=True)

    out = {"anchor_grooved_ghz": ANCHOR_GROOVED_GHZ,
           "driven_dip_ghz": DRIVEN_DIP_GHZ,
           "h3cold_pick_ghz": H3COLD_PICK_GHZ,
           "n_modes": N_MODES, "eigen_target": EIGEN_TARGET, "steps": []}

    for style, port_bc in STEPS:
        tag = f"{TAG}_{style}_{port_bc}"
        rec = {"style": style, "port_bc": port_bc, "tag": tag}
        print(f"  --- mesh style: {style}   port_bc: {port_bc}", flush=True)
        meta = build(tag, style, a, L, rec)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_err','')[:150]}"
            print(f"    🔴 {rec['error']}", flush=True)
            out["steps"].append(rec); save(out); continue
        rec.pop("_err", None)

        # V2 — the groove must actually be in the mesh
        g = (meta.get("geometry_mm") or {}).get("groove") or [0, 0]
        rec["groove_meshed"] = list(map(float, g))
        rec["tets"] = meta["tets"]
        print(f"    groove in mesh: {g}   tets={meta['tets']:,}", flush=True)
        if tuple(rec["groove_meshed"]) != tuple(values.get("cavity.groove.mm")):
            rec["error"] = (f"V2 FIRES: groove {g} is not 5x10 — this is not "
                            f"the design cavity")
            print(f"    🔴 {rec['error']}", flush=True)
            out["steps"].append(rec); save(out); continue

        attrs = meta["attributes"]
        bins = sector_bins(meta)
        # 🔴 was a local copy of the surface/volume rule — one of
        # NINE. A `loop` SURFACE got classified as a VOLUME and
        # Palace refused the config (2026-08-27). One definition.
        vols = volume_attrs(meta)
        c = eigen_cfg(tag, meta, mesh=f"{tag}.msh", sigma=sigma_w,
                      n=N_MODES, target=EIGEN_TARGET, port_bc=port_bc)
        c["Solver"]["Order"] = 2
        c["Domains"]["Postprocessing"]["Energy"] = (
            [{"Index": 1, "Attributes": [attrs["bore"]]}]
            + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
        pts = [(rf * a, math.radians(pd))
               for rf in PROBE_R_FRAC for pd in PROBE_PHI_DEG]
        rec["probe_pts"] = [{"r_mm": r, "phi_deg": math.degrees(p_)}
                            for r, p_ in pts]
        c["Domains"]["Postprocessing"]["Probe"] = [
            {"Index": i + 1,
             "Center": [r * 1e-3 * math.cos(p_), r * 1e-3 * math.sin(p_), 0.0]}
            for i, (r, p_) in enumerate(pts)]
        try:
            run(tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
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
            # ⚠️ order() returns a TUPLE (m, confidence, harmonics) — NOT a dict.
            # Treating it as a dict is what crashed the first launch, AFTER a
            # 514 s solve had already succeeded (§8b: the solve is not the rig).
            m_az, conf, harm = az_order(u) if u else (None, 0, {})
            idx = round(float(md["m"]))
            pu = purity(tag, idx, rec["probe_pts"])
            found.append({"f_ghz": md["f"], "Q": qs.get(idx),
                          "mode_index": idx,
                          "m_az": m_az, "A2_A0": harm.get(2, 0.0),
                          "az_confidence": conf,
                          "aliasing_risk": harm.get("_aliasing_risk"),
                          "m_resolvable_max": harm.get("_m_resolvable_max"),
                          "P_min": (pu or {}).get("P_min"),
                          "P_max": (pu or {}).get("P_max"),
                          "spread": (pu or {}).get("spread"),
                          "purity": pu})
        rec["modes"] = found
        rec["all_f_ghz"] = [f["f_ghz"] for f in found]
        rec["n_solved"] = len(modes)
        if not found:
            rec["verdict"] = (f"INCONCLUSIVE — {len(modes)} modes solved but "
                              f"NONE inside the window {WINDOW}")
            print(f"    🔴 V3 FIRES: {rec['verdict']}", flush=True)
            print("       solved: "
                  + ", ".join(f"{m['f']:.4f}" for m in modes[:10]), flush=True)
            out["steps"].append(rec); save(out); continue
        print(f"    {len(found)} modes returned "
              f"({min(rec['all_f_ghz']):.4f} - {max(rec['all_f_ghz']):.4f} GHz)",
              flush=True)
        print(f"    {'f GHz':>10}{'Q':>10}{'m':>4}{'A2/A0':>9}"
              f"{'P_min':>9}{'spread':>9}", flush=True)
        for f in found:
            print(f"    {f['f_ghz']:>10.6f}"
                  + (f"{f['Q']:>10,.0f}" if f["Q"] else f"{'—':>10}")
                  + f"{str(f['m_az']):>4}"
                  + (f"{f['A2_A0']:>9.4f}" if f["A2_A0"] is not None
                     else f"{'—':>9}")
                  + (f"{f['P_min']:>9.4f}{f['spread']:>9.4f}"
                     if f["P_min"] is not None else f"{'—':>9}{'—':>9}"),
                  flush=True)

        # ---- V3: does the list BRACKET the frequency in question?
        below = [f for f in found if f["f_ghz"] < DRIVEN_DIP_GHZ]
        above = [f for f in found if f["f_ghz"] > DRIVEN_DIP_GHZ]
        rec["brackets"] = bool(below and above)
        if not rec["brackets"]:
            rec["verdict"] = "INCONCLUSIVE — mode list does not bracket 2.4515"
            print(f"    🔴 V3 FIRES: {rec['verdict']}. A list that stops short "
                  f"cannot establish ABSENCE.", flush=True)
            out["steps"].append(rec); save(out); continue

        near = min(found, key=lambda f: abs(f["f_ghz"] - DRIVEN_DIP_GHZ))
        d = (near["f_ghz"] - DRIVEN_DIP_GHZ) * 1e3
        rec["nearest_to_driven"] = {"f_ghz": near["f_ghz"], "delta_mhz": d,
                                    "Q": near["Q"], "P_min": near["P_min"],
                                    "spread": near["spread"]}
        print(f"    nearest to the driven dip: {near['f_ghz']:.6f} "
              f"({d:+.3f} MHz)", flush=True)
        print(f"      vs grooved-no-loop anchor {ANCHOR_GROOVED_GHZ:.6f} -> "
              f"{(near['f_ghz']-ANCHOR_GROOVED_GHZ)*1e3:+.3f} MHz "
              f"(the loop's pull)", flush=True)
        if abs(d) > BRACKET_TOL_MHZ:
            rec["verdict"] = (f"NO eigenmode within {BRACKET_TOL_MHZ:g} MHz of "
                              f"the driven dip (nearest {d:+.3f} MHz)")
            print(f"    🔴 F3 territory: {rec['verdict']}", flush=True)
        elif near["spread"] is None:
            rec["verdict"] = "mode present but PURITY MISSING — cannot identify"
            print(f"    🔴 {rec['verdict']}", flush=True)
        elif near["spread"] > PURITY_SPREAD_MAX:
            rec["verdict"] = (f"mode present but HYBRIDISED "
                              f"(spread {near['spread']:.4f} > "
                              f"{PURITY_SPREAD_MAX}) — NOT clean TE011")
            print(f"    🔴 F4 FIRES: {rec['verdict']}", flush=True)
            print("       ⚠️ frequency agreement with an anchor is "
                  "NECESSARY, NOT SUFFICIENT.", flush=True)
        else:
            rec["verdict"] = (f"TE011 — P>={near['P_min']:.4f}, spread "
                              f"{near['spread']:.4f}, {d:+.3f} MHz from driven")
            print(f"    ✅ {rec['verdict']}", flush=True)
        out["steps"].append(rec); save(out)

    # ---- the comparison the rig exists for
    print("\n" + "=" * 78)
    ok = [x for x in out["steps"] if x.get("modes")]
    by = {(x["style"], x["port_bc"]): x for x in ok}
    shorted = [by.get(("cold", "pec")), by.get(("driven", "pec"))]
    machine = by.get(("driven", "lumped"))

    for lbl, st in (("cold/pec", shorted[0]), ("driven/pec", shorted[1]),
                    ("driven/LUMPED (the machine)", machine)):
        if st is None:
            print(f"  {lbl:<30} — no modes")
            continue
        n = st.get("nearest_to_driven")
        print(f"  {lbl:<30} {st['tets']:>7,} tets   "
              + (f"nearest {n['f_ghz']:.6f} ({n['delta_mhz']:+.2f} MHz)"
                 if n else "does not bracket 2.4515"))

    if machine is None:
        print("\n  🔴 THE LUMPED-PORT STEP PRODUCED NOTHING — the open question "
              "(TE011's purity in\n     the operating configuration) is STILL "
              "unanswered. Do not substitute a\n     shorted-loop number for "
              "it.")
        out["conclusion"] = "machine step failed"
    else:
        n = machine["nearest_to_driven"]
        near = min(machine["modes"], key=lambda f: abs(f["f_ghz"] - DRIVEN_DIP_GHZ))
        agree = abs(n["delta_mhz"]) <= BRACKET_TOL_MHZ
        print("\n  🔑 THE ANSWER THIS RIG WAS RERUN FOR:")
        print(f"     driven (50 ohm, S11)      : {DRIVEN_DIP_GHZ:.6f} GHz")
        print(f"     eigen  (50 ohm, lumped)   : {near['f_ghz']:.6f} GHz "
              f"({n['delta_mhz']:+.3f} MHz)")
        print("     -> the two solvers "
              + ("AGREE ✅ — same cavity, same mode. §7v is confirmed and the "
                 "11.5 MHz\n        gap was ENTIRELY the port boundary "
                 "condition." if agree else
                 "STILL DISAGREE 🔴 — the port BC was not the whole story. "
                 "Do NOT\n        rationalise; something else differs."))
        if near.get("spread") is not None:
            print(f"\n     🔑 TE011 PURITY IN THE OPERATING CONFIGURATION: "
                  f"P >= {near['P_min']:.4f}, spread {near['spread']:.4f}")
            sh = [x for x in shorted if x]
            if sh:
                s0 = min(sh[0]["modes"], key=lambda f: abs(f["f_ghz"] - DRIVEN_DIP_GHZ))
                print(f"        shorted-loop eigen said: P >= {s0['P_min']:.4f}, "
                      f"spread {s0['spread']:.4f}  ⚠️ different cavity")
            print("        grooved, NO loop        : P >= 0.9985, "
                  "spread 0.0015 (ladder step 2, anchored)")
            if near["spread"] <= 0.02:
                print("     ✅ THE LOOP DOES NOT DEGRADE TE011. The ~0.94 purity "
                      "in the record is a\n        SHORTED-LOOP artifact and "
                      "the TDS objection loses its premise.")
            else:
                print("     🔴 THE LOOP DOES DEGRADE TE011, even properly "
                      "terminated. The magnitude\n        is now measured and "
                      "the TDS question is live on real numbers.")
            out["te011_operating_purity"] = {"f_ghz": near["f_ghz"],
                                             "P_min": near["P_min"],
                                             "spread": near["spread"],
                                             "Q_loaded": near["Q"]}
        else:
            print("     🔴 PURITY MISSING on the machine step — probe output "
                  "absent.")
        out["conclusion"] = "agree" if agree else "still disagree"
    save(out)
    print("\n  result -> " + f"{TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
