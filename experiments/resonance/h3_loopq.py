"""H3 loop-size sweep — Q0, Q_ext and beta per loop, by EIGEN PAIRS. No fitting.

🔑 WHAT THIS MEASURES, AND WHY IT NEEDS TWO SOLVES PER LOOP.
For each loop size, solve the SAME mesh twice and take the difference:

    Q0  = eigen, port_bc="pec"      gap shorted -> no port loss -> UNLOADED Q
    Q_L = eigen, port_bc="lumped"   real 50 ohm load           -> LOADED Q
    1/Q_ext = 1/Q_L - 1/Q0     ->     beta = Q0 / Q_ext

**No |S11|, no dip depth, no Lorentzian, no phase, no branch decision.** That is
the whole point: every previous attempt at beta in this programme went through
the |S11| depth, which is identical for beta and 1/beta (§7x), and the branch
FLIPS with loading so no single choice is safe.

🔴 THE DECLARED OPEN QUESTION THIS EXISTS TO SETTLE. `e0k2_sizeq` was built to
explain a DRIVEN anomaly and its own eigen half is now void (open loop gap,
§7v). The anomaly itself is still unexplained:

    driven Q0 = 20,005 / 24,920 / 28,387 / 30,112
    for areas =     35 /     82 /    176 /    384 mm^2

**Smaller loops apparently costing MORE Q, monotonically, against a bare-cavity
44,384.** That is backwards: a smaller obstacle should perturb less.
⚠️ **Driven has a REAL port, so the open gap does NOT explain it.** The branch
error might; blended fits might; both untested. **Do not record it as explained
by the audit** — this rig measures Q0 per loop size a way that cannot have
either defect, and the answer is whatever it is.

🔴🔴 THE CLAIM BELOW -- "Q_ext is set by loop geometry, not by the load" -- IS
FALSE BY ~9%, established 2026-08-25. h3_driven's measured
S11 dip implies Q_ext ~8,100-8,600 from cold through 3e19 and 9,221 at 1e20.
✅ SETTLED. Refitting those sweeps with INTERPOLATED 3 dB edges (CONVENTIONS
7bh) makes the COLD driven value agree with the eigen pair to 0.78% (9,045 vs
9,117) -- which validates the fit -- and then Q_ext dips to 8,194 at ne=1e19 and
recovers to 9,322 at 1e20. A ~9% LOAD DEPENDENCE, not a geometry artefact.
⚠️ beta(ne) = Q0(ne)/Q_ext is therefore a ~9% approximation, not an identity.
⚠️ ALSO: this file's V1_ANCHOR says Q_ext = 9,117 (h3_step3) while the sweep at
11x8 returns 9,231, and h3_driven hardcodes Q_EXT_MEASURED = 9,231. Two values,
~1.25% apart, and their mesh styles are NOT documented in either place.

🔑 AND IT GIVES THE OPTIMISER ITS COUPLING AXIS. Q_ext is set by loop geometry
and is nearly independent of the plasma, so ONE eigen pair per loop size serves
every density. beta(ne) is then Q0(ne)/Q_ext — **matching to beta=1 becomes a
LOOP-SIZE choice made against a chosen operating density**, which is a design
knob the programme has never been able to state quantitatively.

⚠️ SIZES ARE e0k2_sizeq'S, DELIBERATELY. Same four loops, so the comparison is
direct rather than interpolated.
⚠️ GLOSSARY: the second number is a HALF-width. Area = ld * 2 * lw.

🔴 EIGEN ONLY (§7c, one rig one solver). The driven half of this comparison is
`h3_driven` and it has already run.

VERIFICATION
  V1  🔑 THE INTERNAL ANCHOR: at 11x8 this rig must reproduce `h3_step3`:
      Q0 = 43,523, Q_L = 7,538, Q_ext = 9,117, beta = 4.77. Same mesh style,
      same settings, same BCs. **If 11x8 does not reproduce, nothing else in
      the sweep means anything** — check that FIRST.
  V2  the groove must be 5x10 in every mesh except the declared control.
  V3  TE011 identified by CONTINUATION from the anchored grooved-no-loop
      2.450561 GHz, and reported WITH purity. Never by lowest A2/A0 (§7u).
  V4  Q0 -> 44,414 (grooved, no loop) as area -> 0. That is what "a smaller
      obstacle perturbs less" MEANS, and it is the only external anchor here.
FALSIFICATION
  🔴 F1  if eigen Q0 RISES with loop area — reproducing the driven trend — the
         backwards behaviour is REAL and physical, and both the branch and the
         blend explanations are dead. Report it; do not explain it away.
         ⚠️ ASSUMPTION: that the driven anomaly and this Q0 are the same
         quantity. They are both "unloaded Q of TE011", but if TE011 is
         misidentified at some loop size they are not comparable at all — which
         is why V3 demands purity on every reported mode.
  🔴 F2  if purity degrades with loop area (spread rising above ~0.02), the loop
         DOES hybridise TE011 beyond some size, and 11x8 merely sits below it.
         **That is a hard design constraint, not a curiosity** — it would bound
         loop size independently of coupling.
  🔴 F3  if beta crosses 1 inside the swept range, the critically-coupled loop
         size is MEASURED, not estimated. Report which side each size falls on.
  🔴 F4  if the no-groove control's Q0 differs from its grooved twin by more
         than ~2%, groove and loop INTERACT and the OPTIMIZER may not treat them
         as independent axes (§2b).
"""
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import solveconf
import eigmodes
from e0_solver_vs_math import (GEO, GEO_DESIGN, GROOVE_DESIGN, eigen_cfg,
                               run, volume_attrs)
from e0k2_anchor import design_point, wall_sigma, LOOP_PHI, LOOP_RW, LOOP_GAP
from h3_loaded import SECTORS, CAP_R_FRAC
from azimuthal import order as az_order
from e0k2_azim import sector_bins, read_sector_energy
from h3_ladder import purity, PROBE_PHI_DEG, PROBE_R_FRAC
import slug as S
import values

# 🔑 SLUG REGIME (7aw/7az). Every case, every eigen setting and the loop family
# itself now come from baseline-<slug>.json. This rig previously hardcoded a
# CAP-mounted loop, which is why item 7 step 1 -- the BARREL mount -- could not
# be expressed at all without editing the script.
SLUG = S.parse()
CFG = S.config(SLUG)
PRM = CFG["_run"]["parameters"]
TAG = S.out(SLUG)

# e0k2_sizeq's four loops. (ld, half-width) -> area = ld * 2 * lw
LOOPS = [(5.0, 3.5), (7.5, 5.5), (11.0, 8.0), (16.0, 12.0)]
ANCHOR_LOOP = tuple(values.get("loop.size.mm"))   # the one h3_step3 measured
# 🔴 THE AZIMUTHAL LOOP'S PARAMETERS ARE BASELINES ENTRIES, NOT CLI NUMBERS.
# Every other loop dimension — size, wire radius, port gap, phi, cap radius —
# is a canonical value with a source and a status. Introducing h/arc/strip as
# bare numbers on a geometry.py command line would repeat, in a worse form, the
# defect loop.gap.mm and loop.wire_r.mm are already flagged for: "geometry.py
# default, inherited. ⚠️ NO PROVENANCE."
# ⚠️ allow_tentative SAID OUT LOUD, as the store demands: none of these is a
# CHOSEN value. They are placeholders at the centre of the declared sweep
# range, and the sweep is what chooses them. A run that INHERITS one rather
# than sweeping over it is quoting a number nobody picked.
AZIM_H = values.get("loop.azim.h.mm", allow_tentative=True)
AZIM_ARC = values.get("loop.azim.arc.mm", allow_tentative=True)
LOOP_STRIP = values.get("loop.strip.mm", allow_tentative=True)

# 🔑 h3_step3's validated settings. Target 2.38 with N=8 returned a clean
# 4-mode window containing TE011 on this cavity; do not re-derive (PRIOR ART).
# 🔴 THE CONVERGENCE BUDGET REACHES THIS RIG BY IMPORT SIDE EFFECT.
# `solvecost.py` sets NLEPS_BUDGET = 1000. `h3_ladder.py:121` then does
# `_sc.NLEPS_BUDGET = 1400` at import time — and this rig imports `purity` from
# h3_ladder, so pulling in a FIELD-PROBE HELPER silently raises the budget for
# every solve here. Nothing at this call site said 1400; the run log did, and
# only when a case exceeded it.
# ✅ Say it explicitly, and let a run that believes its case is merely hard
# raise it in ITS OWN CONFIG — the rig's own message already prescribes
# "raise it deliberately", which should not mean editing a global.
import solvecost as _solvecost
NLEPS_BUDGET = int(PRM.get("nleps_budget", _solvecost.NLEPS_BUDGET))
_solvecost.NLEPS_BUDGET = NLEPS_BUDGET

N_MODES = int(PRM.get("n_modes", 8))
EIGEN_TARGET = float(PRM.get("eigen_target", 2.38))
EIGEN_TOL = float(PRM.get("eigen_tol", 1e-8))
CASE_TIMEOUT_S = float(PRM.get("case_timeout_s", 2700.0))
WINDOW = tuple(PRM.get("window", (2.35, 2.65)))

# external / prior anchors
Q_NOLOOP_GROOVED = 44414.0         # h3_ladder step 2, anchored against H2
F_NOLOOP_GROOVED = float(PRM.get("cont_seed_ghz", 2.450561))   # continuation seed
V1_ANCHOR = {"Q0": 43523.0, "Q_L": 7538.0, "Q_ext": 9117.0, "beta": 4.774}
# 🔴 THE ANCHOR IS PER-CONFIGURATION, AND SAYING SO IS THE WHOLE FIX.
# `h3_step3` measured those numbers on a CAP-mounted 11x8 loop with NO series
# capacitor and NO flange. The V1 check matched the anchor case on (ld, lw) and
# `grooved` ONLY, so every barrel+capacitor run was compared against a different
# coupler and V1 fired on all four rows. On 2026-08-27 it printed "THE ANCHOR
# DOES NOT REPRODUCE — treat every other row as SUSPECT" over a run whose own
# declared control reproduced `h3-loop-seriesc-01` to 0.6-1.9 %.
# ⚠️ A guard that fires when it should not is worse than no guard: it trains you
# to read past it. Same shape as §7c's eta-reference trap, and the fix is the
# same one `h3_driven.check_eta_reference` already uses — REFUSE TO QUOTE, not
# refuse to run.
V1_ANCHOR_CONFIG = {"mount": "cap", "gap2": 0.0, "flange": 0.0}
V1_TOL_FRAC = 0.05


def _loop_config(p):
    """The coupler configuration a point was measured in. Defaults match the
    era before mount/gap2/flange existed, when everything was a cap loop."""
    return {"mount": p.get("mount") or "cap",
            "gap2": float(p.get("gap2") or 0.0),
            "flange": float(p.get("flange") or 0.0)}


def check_v1(points, anchor=None, anchor_cfg=None, tol=None):
    """V1, as a pure function of the points so it can be tested without a solve.

    Returns (verdict, lines) — verdict is 'pass', 'FIRES on [...]',
    'suppressed' or 'not checked'.
    """
    anchor = V1_ANCHOR if anchor is None else anchor
    anchor_cfg = V1_ANCHOR_CONFIG if anchor_cfg is None else anchor_cfg
    tol = V1_TOL_FRAC if tol is None else tol
    same_loop = [p for p in points if p.get("Q0")
                 and (p["ld"], p["lw"]) == ANCHOR_LOOP and p.get("grooved")]
    anc = next((p for p in same_loop if _loop_config(p) == anchor_cfg), None)
    if anc is None:
        if same_loop:
            got = _loop_config(same_loop[0])
            return "suppressed", [
                f"  ⚠️ V1 SUPPRESSED — the anchor {anchor['Q_ext']:,.0f} is for a "
                f"{anchor_cfg['mount']} loop with gap2={anchor_cfg['gap2']:g}, "
                f"flange={anchor_cfg['flange']:g};",
                f"     this run meshes {got['mount']} gap2={got['gap2']:g} "
                f"flange={got['flange']:g}. **A DIFFERENT COUPLER.**",
                "     Comparing them is the wrong-cavity comparison (§7c), not a "
                "failed reproduction.",
                "     🔑 Anchor this run against a control in ITS OWN "
                "configuration instead.",
            ]
        return "not checked", [
            "  🔴 V1 CANNOT BE CHECKED — the 11x8 anchor case did not "
            "complete.\n     NOTHING IN THIS SWEEP IS QUOTABLE."]
    bad, lines = [], []
    for k, want in anchor.items():
        got = anc[k]
        off = abs(got - want) / want
        lines.append(f"  V1 {k:<6} {got:>10,.1f} vs h3_step3 {want:>10,.1f}  "
                     f"-> {off*100:>5.1f}%  "
                     + ("✅" if off <= tol else "🔴 FIRES"))
        if off > tol:
            bad.append(k)
    if bad:
        lines.append("  🔴 THE ANCHOR DOES NOT REPRODUCE. Treat every other row "
                     "as SUSPECT until this is\n     understood — same mesh "
                     "style, same settings, same BCs should give the same "
                     "numbers.")
    return ("pass" if not bad else f"FIRES on {bad}"), lines
DRIVEN_ANOMALY = {35: 20005, 82: 24920, 176: 28387, 384: 30112}

# 🔴 CONFIGURABLE 2026-08-25, FOR THE RESTORATION. The seed below is the
# TORCH-FREE grooved cavity, and continuation refused anything >25 MHz from it.
# That is correct for a loop study on a fixed cavity and WRONG the moment the
# cavity itself changes: restoring the torch moves TE011 by more than the guard
# allows, so the guard would reject the very measurement it was asked for.
# A search window is a property of the QUESTION, so it belongs in the config.
CONT_MAX_MHZ = float(PRM.get("cont_max_mhz", 25.0))
PURITY_SPREAD_WARN = 0.02          # F2


def save(out):
    p = pathlib.Path(S.outfile(SLUG, "result.json"))
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def case_name(rec):
    """The case's name, from every variable that case actually varies.

    🔴 A NAME THAT DOES NOT CARRY WHAT VARIES IS A COLLISION. On 2026-08-27
    `h3_driven`'s loop axis omitted the swept variable: four cases shared one
    tag, so one mesh, one postpro directory and one S11 file served all four,
    and the sweep coordinate appeared in NO field of the record. An azimuthal
    sweep varies h, arc and the cross-section — none of which is ld or lw.
    """
    if rec.get("mount") == "azim":
        _st = rec.get("strip", LOOP_STRIP)
        head = ("azim_h{:g}_L{:g}".format(float(rec.get("h", AZIM_H)),
                                          float(rec.get("arc", AZIM_ARC)))
                + ("_strip{:g}x{:g}".format(*_st) if _st else "_wire"))
    else:
        head = "{:g}x{:g}".format(float(rec.get("ld", 0.0)),
                                  float(rec.get("lw", 0.0)))
    return (head
            # ⚠️ WAS f"_{rec['mount']}" * bool(rec.get("mount")) — the f-string
            # is evaluated BEFORE the multiply, so a case with no `mount` key
            # raised KeyError instead of contributing "". The legacy default
            # case list (LOOPS, used when a config supplies no `cases`) has no
            # mount, so that path could not have named a single case.
            + (f"_{rec['mount']}" if rec.get("mount") else "")
            + (f"_g2-{rec['gap2']:g}" if rec.get("gap2") else "")
            + (f"_fl-{rec['flange']:g}" if rec.get("flange") else "")
            + rec.get("name_suffix", ""))


def build(tag, ld, lw, a, L, grooved, rec):
    base = list(GEO_DESIGN) if grooved else list(GEO)
    # 🔑 PER-CASE GROOVE. The groove is normally the FROZEN design value and
    # must not vary — but a case may deliberately sweep it (h3-groove-gap-01
    # asks whether groove width shifts the loop's Q_ext curve). Overriding it
    # here keeps the frozen default intact for every other case, and the rig
    # still asserts the MESH matches whatever was requested.
    if rec.get("groove_mm"):
        gm = rec["groove_mm"]
        i = base.index("--groove")
        base[i + 1] = f"{float(gm[0]):g},{float(gm[1]):g}"
    args = (base + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                    "--sectors", str(SECTORS),
                    "--loop", f"{ld},{lw},{rec.get('rw', LOOP_RW)},"
                              f"{rec.get('gap', LOOP_GAP)}",
                    "--loop-phi", str(rec.get("phi", LOOP_PHI))])
    # 🔑 MOUNT. "cap" links H_r (radius free, 1.93x the coupled power of the
    # barrel); "barrel" is forced to r = a but is the ONLY mount that accepts
    # the series capacitor -- geometry.py:427 refuses --loop-gap2 with
    # --loop-cap. That refusal is what fixes item 7's step order.
    # 🔑 A STRIP IS A CROSS-SECTION, NOT A MOUNT — it applies to any topology.
    _strip = rec.get("strip", LOOP_STRIP)
    if _strip:
        args += ["--loop-strip", f"{float(_strip[0]):g},{float(_strip[1]):g}"]
    mount = rec.get("mount", "cap")
    if mount == "azim":
        # AZIMUTHAL: an arc of length `arc` at r = a - h, closed to the wall by
        # two radial legs. h and arc are INDEPENDENT — geometry.py takes the arc
        # LENGTH and derives the angle from R = a - h, because a fixed angle at
        # different h is a different length.
        _h = float(rec.get("h", AZIM_H))
        _arc = float(rec.get("arc", AZIM_ARC))
        args += ["--loop-azim", f"{_h:g},{_arc:g}"]
        rec.update({"h_mm": _h, "arc_mm": _arc,
                    "unwound_mm": _arc - float(rec.get("gap", LOOP_GAP)) + 2*_h,
                    "clearance_mm": _h - (float(_strip[1]) / 2.0 if _strip
                                          else float(rec.get("rw", LOOP_RW))),
                    "strip_mm": list(_strip) if _strip else None})
    elif mount == "cap":
        args += ["--loop-cap", f"{rec.get('cap_r_frac', CAP_R_FRAC) * a:.4f}"]
    elif mount != "barrel":
        raise SystemExit(f"unknown loop mount {mount!r}: want cap|barrel|azim")
    # the SERIES CAPACITOR (R62), barrel only
    if rec.get("gap2"):
        if mount != "barrel":
            raise SystemExit("gap2 requires mount=barrel (geometry.py:427)")
        args += ["--loop-gap2", f"{rec['gap2']:g}"]
        if rec.get("flange"):
            args += ["--loop-flange", f"{rec['flange']:g}"]
    for sf in ("1.5", "1.42", "1.58"):
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
            rec["size_factor"] = sf
            if sf != "1.5":
                print(f"      ⚠️ mesh needed size-factor {sf}; REPORTED",
                      flush=True)
            return solveconf.load_meta(f"{tag}.msh")
        rec["_err"] = (r.stdout + r.stderr)[-200:]
    return None


def solve_one(tag, meta, sigma_w, port_bc, rec):
    """One eigen solve. Returns the mode list with purity, or None."""
    attrs = meta["attributes"]
    bins = sector_bins(meta)
    # 🔴 was its own copy of the surface/volume rule — one of NINE. A `loop`
    # surface got classified as a volume and Palace refused the config.
    vols = volume_attrs(meta)
    c = eigen_cfg(tag, meta, mesh=f"{tag}.msh", sigma=sigma_w,
                  n=N_MODES, target=EIGEN_TARGET, port_bc=port_bc,
                  tol=EIGEN_TOL)
    c["Solver"]["Order"] = 2
    c["Domains"]["Postprocessing"]["Energy"] = (
        [{"Index": 1, "Attributes": [attrs["bore"]]}]
        + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
    a_mm = rec["_a"]
    pts = [(rf * a_mm, math.radians(pd))
           for rf in PROBE_R_FRAC for pd in PROBE_PHI_DEG]
    probe_pts = [{"r_mm": r, "phi_deg": math.degrees(p_)} for r, p_ in pts]
    _probe_xyz = [(r * 1e-3 * math.cos(p_), r * 1e-3 * math.sin(p_), 0.0)
                  for r, p_ in pts]
    # 🔑 NAMED FIELD PROBES, APPENDED AFTER THE PURITY ONES.
    # The purity analysis addresses probes by INDEX, so appending is the only
    # safe place to add: it cannot shift an index that already exists. Same
    # rule geometry.py's fragment tool-order comment states for provenance.
    #
    # Two blockers need |E| at a point and nothing else (NEXT.md 7d, and
    # ../ignition-options/ item 2):
    #   series_gap — is the capacitor gap going to ARC at 1 kW? Estimated from
    #                the loop current it spans safe..arcing, so it must be
    #                MEASURED, not modelled.
    #   bore_edge  — can the cavity break down N2 in the torch bore UNAIDED?
    #                If not, cavity-only ignition does not exist and a striker
    #                is mandatory, which settles item 7's target outright.
    # E_phi ~ J1(kc r) sin(pi z/L), so the bore's largest field is at the
    # OUTER bore radius, at the MID-PLANE. Both probes sit at z = 0.
    _named = []
    _t_ri = 8.5                      # torch bore inner radius, mm
    for _nm, _rr in (("bore_edge", _t_ri), ("bore_mid", _t_ri / 2.0)):
        _named.append((_nm, _rr * 1e-3, 0.0, 0.0))
    # loop-frame -> cavity frame. The loop is built in the z=0 plane with its
    # legs along x at y = -+lw, then rotated by loop_phi about z. ONE rotation,
    # used by every loop-local probe below — it was inline in the series_gap
    # block and a second copy is how two probes drift apart.
    _ld, _lw = float(rec.get("ld") or 0.0), float(rec.get("lw") or 0.0)
    _xm = a_mm + 1.0 - _ld / 2.0        # leg mid-span: legs run x = a+2 .. a-ld
    _ph = math.radians(float(rec.get("phi", LOOP_PHI)))

    def _loop_xy(x_mm, y_mm):
        return ((x_mm * math.cos(_ph) - y_mm * math.sin(_ph)) * 1e-3,
                (x_mm * math.sin(_ph) + y_mm * math.cos(_ph)) * 1e-3)

    if rec.get("gap2"):
        # gap centre: the series break is in the -y leg only, at mid-span.
        _gx, _gy = _loop_xy(_xm, -_lw)
        _named.append(("series_gap", _gx, _gy, 0.0))
    # 🔑 LEG PROBES — THE ELECTRIC-vs-MAGNETIC DISCRIMINATOR (added 2026-08-27).
    #
    # rho = |E|/(c|B|) at `series_gap` reads 9.3 where TE011's own value at that
    # radius is 0.218 (`h3-field-01`, lumped) — E-dominated by 42x. ⚠️ That
    # ALONE proves nothing: a series capacitor has a voltage across it BY
    # CONSTRUCTION, so a large E in the gap is a working capacitor, not
    # necessarily a resonant element.
    #
    # 🔑 THE LEGS ARE WHERE THE TWO STORIES SEPARATE. They are current maxima:
    # a loop that couples by LINKING FLUX must be H-dominated there (rho < 1).
    # If the legs read E-dominated too, the structure is not coupling
    # magnetically anywhere and "loop" is the wrong word for it.
    #
    # 🔴 THE PROBE CANNOT SIT ON THE CONDUCTOR. The wire is CUT OUT of the
    # vacuum domain, so its centreline is not in the mesh at all and a probe
    # there reads nothing meaningful. These sit `rw + 1 mm` OUTSIDE the wire
    # surface, in vacuum, on the far side from the loop's interior.
    # ⚠️ So they are NEAR-FIELD probes beside the conductor, not on it, and the
    # +y/-y pair is the controlled comparison: same x, same offset, same
    # radius — one beside intact wire, one beside the broken leg.
    if _ld > 0:
        _off = float(rec.get("rw", LOOP_RW)) + 1.0
        for _nm, _yy in (("leg_intact", +(_lw + _off)),
                         ("leg_broken", -(_lw + _off))):
            _lx, _ly = _loop_xy(_xm, _yy)
            _named.append((_nm, _lx, _ly, 0.0))
        # 🔴 THE PORT GAP IS THE TIGHTER FEATURE AND WAS NEVER PROBED.
        # `loop.gap.mm` = 0.3 is NARROWER than the 0.5 mm series gap, and it
        # carries the DRIVE. `fieldcheck` gives the series gap a 4.08x breakdown
        # margin at 1 kW; the port gap has no probe at all, so the tighter of
        # the two conductor breaks is the one nobody has measured.
        # Centre matches geometry.py:565 — port_centre = (xi*cos, xi*sin, 0)
        # with xi = a - ld, i.e. the crossbar mid-span.
        # 🔑 SELF-DIAGNOSING: this probe sits ON the port face, so `pec` (face
        # SHORTED, E across it ~ 0) and `lumped` (50 ohm) MUST disagree here —
        # unlike the legs, which agreed to 0.1%. If the two read the same, the
        # probe is not seeing the port and the reading is not the gap field.
        _px, _py = _loop_xy(a_mm - _ld, 0.0)
        _named.append(("port_gap", _px, _py, 0.0))
    rec["probe_names"] = ([None] * len(_probe_xyz)
                          + [n for n, *_ in _named])
    rec["probe_named_mm"] = {n: [x * 1e3, y * 1e3, z * 1e3]
                             for n, x, y, z in _named}
    c["Domains"]["Postprocessing"]["Probe"] = [
        {"Index": i + 1, "Center": list(xyz)}
        for i, xyz in enumerate(_probe_xyz
                                + [(x, y, z) for _n, x, y, z in _named])]
    try:
        run(tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
    except RuntimeError as e:
        print(f"      🔴 {str(e)[:150]}", flush=True)
        return None
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
        m_az, conf, harm = az_order(u) if u else (None, 0, {})
        idx = round(float(md["m"]))
        pu = purity(tag, idx, probe_pts)
        found.append({"f_ghz": md["f"], "Q": qs.get(idx), "mode_index": idx,
                      "m_az": m_az, "A2_A0": harm.get(2, 0.0),
                      "P_min": (pu or {}).get("P_min"),
                      "spread": (pu or {}).get("spread")})
    return found


def read_named_probes(tag, mode_index, names):
    """|E| (eigenmode units) at each NAMED probe, plus the mode's stored energy.

    🔑 RAW ONLY. The eigenmode amplitude is arbitrary, so these numbers mean
    nothing until scaled by U_real/U_mode for a stated power — and THAT is a
    judgement (which power? which Q?) that belongs in a re-runnable analysis
    layer, not baked into the driver. The rig emits the measurement with its
    normalisation; `fieldcheck.py` applies the label.
    """
    import csv as _csv
    d = pathlib.Path("postpro") / tag
    out = {"probe_E_named": {}, "U_mode_J": None}
    f = d / "probe-E.csv"
    if f.exists():
        rows = list(_csv.reader(f.read_text().splitlines()))
        hdr = [x.strip() for x in rows[0]]
        row = next((r for r in rows[1:]
                    if r and round(float(r[0])) == mode_index), None)
        if row is not None:
            for i, nm in enumerate(names):
                if not nm:
                    continue                       # unnamed purity probe
                mag = 0.0
                for comp in ("x", "y", "z"):
                    for part in ("Re", "Im"):
                        key = f"{part}{{E_{comp}[{i + 1}]}} (V/m)"
                        if key in hdr:
                            mag += float(row[hdr.index(key)]) ** 2
                out["probe_E_named"][nm] = math.sqrt(mag)
    g = d / "domain-E.csv"
    if g.exists():
        rows = list(_csv.reader(g.read_text().splitlines()))
        hdr = [x.strip() for x in rows[0]]
        row = next((r for r in rows[1:]
                    if r and round(float(r[0])) == mode_index), None)
        if row is not None:
            try:
                ie = hdr.index("E_elec (J)"); im = hdr.index("E_mag (J)")
                out["U_mode_J"] = float(row[ie]) + float(row[im])
            except ValueError:
                pass
    return out


def pick_te011(found, seed):
    """🔑 CONTINUATION from an ANCHORED frequency, then REPORT purity.

    Never "lowest A2/A0" — that is how 2.440003 was picked, on a mode the rig
    itself had flagged `identification_uncertain` (§7u). Purity does not select
    here either; it is the independent check ON the selection.
    """
    if not found:
        return None, "no modes in window"
    m = min(found, key=lambda f: abs(f["f_ghz"] - seed))
    d = (m["f_ghz"] - seed) * 1e3
    if abs(d) > CONT_MAX_MHZ:
        return None, f"continuation BROKE: nearest is {d:+.2f} MHz from {seed:.6f}"
    return m, f"continuation {d:+.3f} MHz"


def partial_set(slug, enabled=True):
    """Per-BOUNDARY-CONDITION results already on disk for INCOMPLETE cases.

    🔑 `save()` already runs after EVERY port_bc, so a case interrupted between
    its `pec` and `lumped` solves has `modes_pec` on disk — the measurement is
    checkpointed, resume just never read it back. Case-level resume therefore
    re-solved a completed half.

    🔴 MEASURED COST, 2026-08-26: h3-groove-gap-01's `gw5_g2-2.25` pec solve was
    computed THREE times and lost twice — 12 minutes each, 36 minutes for one
    12-minute result — across two reclamations. At ~7-26 min per solve on the
    design cavity that is the largest remaining waste in the loop.
    """
    if not enabled:
        return {}
    prior = pathlib.Path(S.outfile(slug, "result.json"))
    if not prior.exists():
        return {}
    try:
        pj = json.loads(prior.read_text())
    except Exception:
        return {}
    return {r["name"]: r for r in pj.get("points", [])
            if r.get("name") and not r.get("Q_ext")
            and any(k.startswith("modes_") for k in r)}


def resume_set(slug, enabled=True):
    """Cases already COMPLETE for this slug+stamp, as {name: record}.

    🔑 Spot reclamation killed this rig twice on 2026-08-25, each time costing
    the COMPLETED cases too because a relaunch started from zero. The rig
    checkpoints per case; it just never read its own checkpoint back.

    Safe because the filename carries the config's sha256 stamp: a result.json
    under this name was produced by THIS config, so its finished cases answer
    exactly the question being asked now. A changed config gets a different
    stamp and therefore an empty resume set, automatically.

    🔴 A CASE COUNTS AS DONE ONLY WITH A Q_ext. ERRORS ARE RETRIED.
    The first version also skipped cases with a recorded `error`, reasoning
    that a deterministic failure should not be re-attempted. That is exactly
    backwards: you relaunch a failed run BECAUSE you fixed the cause, and
    sticky failures make the fix invisible. Observed 2026-08-25 — the torch
    restoration failed on a permittivity bug, I fixed it, and the relaunch
    SKIPPED both cases and reported "nothing quotable". A resume that
    remembers failures cannot be used to retry them.
    ⚠️ A half-written record is re-run too, never trusted.
    """
    if not enabled:
        return {}
    prior = pathlib.Path(S.outfile(slug, "result.json"))
    if not prior.exists():
        return {}
    try:
        pj = json.loads(prior.read_text())
    except Exception as e:
        print(f"  ⚠️ prior result unreadable ({e}); starting clean", flush=True)
        return {}
    return {r["name"]: r for r in pj.get("points", [])
            if r.get("name") and r.get("Q_ext")}

def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    print(f"  a={a:.4f} L={L:.4f}   grooved-no-loop anchor: "
          f"{F_NOLOOP_GROOVED:.6f} GHz, Q0={Q_NOLOOP_GROOVED:,.0f}")
    print(f"  eigen: target={EIGEN_TARGET}, N={N_MODES}, order 2 — "
          f"h3_step3's validated settings")
    _n = len(PRM.get("cases") or LOOPS) + (0 if PRM.get("cases") else 1)
    _nb = len(tuple(PRM.get("port_bcs") or ("pec", "lumped")))
    print(f"  {_n} case(s) x {_nb} port BC(s) "
          f"{tuple(PRM.get('port_bcs') or ('pec', 'lumped'))} = {_n*_nb} "
          f"solves\n", flush=True)

    out = {"anchor_no_loop": {"f_ghz": F_NOLOOP_GROOVED,
                              "Q0": Q_NOLOOP_GROOVED},
           "v1_anchor": V1_ANCHOR, "driven_anomaly_Q0": DRIVEN_ANOMALY,
           "points": []}

    # 🔑 RESUME. Spot reclamation killed this rig TWICE on 2026-08-25 (three
    # times in the session), each time costing every COMPLETED case as well as
    # the one in flight, because a relaunch started from zero. The rig already
    # checkpoints per case; it just never read its own checkpoint back.
    #
    # Safe because the output filename carries the config's sha256 stamp: a
    # result.json under this name was produced by THIS config, so its finished
    # cases answer exactly the question being asked now. A changed config gets
    # a different stamp and therefore an empty resume set, automatically.
    #
    # Set "resume": false in the config to force a clean re-run.
    done = resume_set(SLUG, PRM.get("resume", True))
    half = partial_set(SLUG, PRM.get("resume", True))
    if half:
        for _n, _r in sorted(half.items()):
            _bcs = sorted(k[len("modes_"):] for k in _r if k.startswith("modes_"))
            print(f"  🔑 PARTIAL: {_n} already has {', '.join(_bcs)} on disk — "
                  f"those solves will be REUSED, not repeated.", flush=True)
    if done:
        print(f"  🔑 RESUMING: {len(done)} case(s) already complete under "
              f"stamp {S.stamp(SLUG)} — {', '.join(sorted(done))}", flush=True)
        print("     re-running only what is missing. Set resume:false in the "
              "config to force a clean run.", flush=True)

    # 🔑 THE CASE LIST IS THE EXPERIMENT, so it lives in the config, not here.
    # Legacy default reproduces the 2026-08-24 area sweep exactly.
    _cases = PRM.get("cases")
    if not _cases:
        _cases = [{"ld": ld, "lw": lw, "grooved": True} for ld, lw in LOOPS]
        _cases.append({"ld": ANCHOR_LOOP[0], "lw": ANCHOR_LOOP[1],
                       "grooved": False, "name_suffix": "_nogroove"})

    # 🔴 NAME COLLISION IS FATAL AND MUST BE CAUGHT BEFORE THE FIRST SOLVE.
    # Cases sharing a name share a mesh, a postpro directory and an S11 file, so
    # all but the last are overwritten. This does not rely on remembering to put
    # the swept variable in the name: it FAILS if two cases would collide,
    # whatever axis is added next.
    _names = [case_name(dict(c)) for c in _cases]
    if len(set(_names)) != len(_names):
        _dup = sorted({n for n in _names if _names.count(n) > 1})
        raise SystemExit(
            f"🔴 CASE NAME COLLISION — {len(_names)} cases produce "
            f"{len(set(_names))} distinct names.\n     colliding: {_dup}\n"
            f"  🔑 case_name() does not carry a variable this sweep varies. "
            f"Add it THERE, not in the caller.")

    for _c in _cases:
        rec = dict(_c)
        # ⚠️ an AZIMUTHAL case has no ld/lw — its size is (h, arc). Reading them
        # unconditionally raised KeyError on the first such case.
        ld, lw = float(rec.get("ld", 0.0)), float(rec.get("lw", 0.0))
        grooved = bool(rec.get("grooved", True))
        area = ld * 2 * lw
        rec.setdefault("name", case_name(rec))
        name = rec["name"]
        rec.update({"ld": ld, "lw": lw, "area_mm2": area, "grooved": grooved,
                    "_a": a})
        if name in done:
            out["points"].append(done[name])
            _q = done[name].get("Q_ext")
            print(f"  --- loop {name}: ✅ SKIPPED, already complete"
                  + (f" (Q_ext={_q:,.0f})" if _q else " (recorded error)"),
                  flush=True)
            save(out)
            continue
        print(f"  --- loop {ld:g}x{lw:g} = {area:.0f} mm^2"
              f"  mount={rec.get('mount', 'cap')}"
              + (f"  gap2={rec['gap2']:g} flange={rec.get('flange', 0):g}"
                 if rec.get("gap2") else "")
              + ("" if grooved else "   🔑 NO-GROOVE CONTROL (F4)"), flush=True)

        # 🔑 APPEND FIRST. A record that is only appended on success cannot
        # carry a partial result, and the partial ones are the diagnostics.
        out["points"].append(rec)
        per_bc = {}
        # 🔑 WHICH PORT BCs TO SOLVE IS PART OF THE EXPERIMENT, so it lives in
        # the config — same reasoning as the case list above.
        # 🔴 THIS IS NOT "one rig, one solver". Both are EIGEN on the same mesh;
        # only the port termination differs, and the rig already treats them as
        # two solves of one case. What it buys: every expensive failure so far
        # has been `lumped` at strong coupling (ld=8 timed out at 2700 s having
        # burned 645 NLEPS; ld=14 stopped at 1402 NLEPS against a 1400 budget),
        # while `pec` converged every time. A study that needs only Q0 should
        # not pay for that. §7bp: useless solves cost more than interruptions.
        # ⚠️ eta/beta/Q_ext need BOTH; a pec-only run cannot report them and the
        # summary already handles a missing BC as missing data.
        _bcs = tuple(PRM.get("port_bcs") or ("pec", "lumped"))
        for _b in _bcs:
            if _b not in ("pec", "lumped"):
                raise SystemExit(f"🔴 port_bcs: {_b!r} is not a port BC this "
                                 f"rig solves (want 'pec' and/or 'lumped')")
        for port_bc in _bcs:
            tag = f"{TAG}_{name}_{port_bc}"
            meta = build(tag, ld, lw, a, L, grooved, rec)
            if meta is None:
                rec["error"] = f"mesh failed: {rec.pop('_err','')[:140]}"
                print(f"    🔴 {rec['error']}", flush=True)
                break
            rec.pop("_err", None)
            # 🔴 ASSERT THE DIMENSIONS TOO, NOT JUST THE GROOVE (2026-08-25).
            # Only the groove was ever checked against the sidecar. GEO carries
            # A_MM/L_MM = 103.70/88.53 -> D/L 2.343, while H1's answer is
            # DL = 1.525 -> a 88.0045, L 115.4158. Every H3 rig overrides with
            # design_point(), so the record is consistent — but nothing CHECKED
            # it, and baseline-h3-bore-01.json still records radius 103.7 in a
            # geometry block the rig silently overrode. Verify with the
            # consumer: the mesh is what you ordered, or it is an error.
            _gm = meta.get("geometry_mm") or {}
            for _k, _want in (("radius", a), ("length", L)):
                _got = _gm.get(_k)
                if _got is None or abs(float(_got) - _want) > 1e-3:
                    rec["error"] = (f"MESH IS NOT WHAT WAS ORDERED: {_k} "
                                    f"{_got}, wanted {_want:.6f}")
                    print(f"    🔴 {rec['error']}", flush=True)
                    break
            # 🔑 AND THE LOOP ITSELF. The sidecar records loop_mount, gap2 and
            # flange_r, so bind from it and assert it matches the REQUEST —
            # the mount is the entire independent variable of step 1, and the
            # flange is step 2's. A run that cannot prove which loop it built
            # cannot report a coupling ratio.
            _want_mount = rec.get("mount", "cap")
            _got_mount = _gm.get("loop_mount")
            if _got_mount != _want_mount:
                rec["error"] = (f"MOUNT MISMATCH: meshed {_got_mount!r}, "
                                f"requested {_want_mount!r}")
                print(f"    🔴 {rec['error']}", flush=True)
                break
            rec["mesh_mount"] = _got_mount
            rec["mesh_gap2_mm"] = _gm.get("loop_gap2")
            rec["mesh_flange_r_mm"] = _gm.get("loop_flange_r")
            for _k, _want in (("loop_gap2", float(rec.get("gap2") or 0.0)),
                              ("loop_flange_r", float(rec.get("flange") or 0.0))):
                _got = float(_gm.get(_k) or 0.0)
                if abs(_got - _want) > 1e-6:
                    rec["error"] = (f"{_k} MISMATCH: meshed {_got:g}, "
                                    f"requested {_want:g}")
                    print(f"    🔴 {rec['error']}", flush=True)
                    break
            if rec.get("error"):
                break
            g = (meta.get("geometry_mm") or {}).get("groove") or [0, 0]
            # 🔑 from the single source, never a literal. The groove omission
            # (31 rigs on the wrong cavity) began as a frozen value that lived
            # in one place and was retyped in another.
            want = (tuple(float(x) for x in rec["groove_mm"])
                    if rec.get("groove_mm")
                    else (tuple(GROOVE_DESIGN) if grooved else (0.0, 0.0)))
            if tuple(map(float, g)) != want:
                rec["error"] = f"V2 FIRES: groove {g}, wanted {want}"
                print(f"    🔴 {rec['error']}", flush=True)
                break
            rec["groove_meshed"] = list(map(float, g))
            rec["tets"] = meta["tets"]
            # 🔑 REUSE a boundary condition already solved and checkpointed.
            # The mesh is still rebuilt and every assert above still runs — only
            # the SOLVE is skipped, so a reused result is still verified against
            # the geometry it claims to describe.
            _prior_modes = (half.get(name) or {}).get(f"modes_{port_bc}")
            if _prior_modes:
                print(f"    ♻️  {port_bc}: reusing {len(_prior_modes)} mode(s) "
                      f"checkpointed before the interruption — not re-solving",
                      flush=True)
                found = _prior_modes
            else:
                found = solve_one(tag, meta, sigma_w, port_bc, rec)
            if not found:
                rec["error"] = f"{port_bc}: no modes in {WINDOW}"
                print(f"    🔴 {rec['error']}", flush=True)
                break
            # 🔴 SAVE THE MEASUREMENT BEFORE ATTEMPTING THE LABEL (§7q).
            # This block used to identify first and store only on success, so a
            # broken continuation discarded a converged mode list — ~10 minutes
            # of solve — because the LABEL failed. The frequencies, Qs and
            # purities were never in doubt. **Quarantine the label, not the
            # measurement**, and note that the case most likely to break
            # identification (a big loop that hybridises TE011, F2) is exactly
            # the one whose modes are most worth keeping.
            rec[f"modes_{port_bc}"] = found
            save(out)
            te, why = pick_te011(found, F_NOLOOP_GROOVED)
            if te is None:
                rec["error"] = f"{port_bc}: {why}"
                rec[f"identification_failed_{port_bc}"] = True
                print(f"    🔴 {rec['error']}", flush=True)
                print(f"       ⚠️ {len(found)} converged modes KEPT in the "
                      f"result file: "
                      + ", ".join(f"{m['f_ghz']:.4f}" for m in found[:6]),
                      flush=True)
                break
            per_bc[port_bc] = te
            rec[f"te011_{port_bc}"] = dict(te, selected_by=why)
            # RAW field measurement at the named probes, for fieldcheck.py
            _fp = read_named_probes(tag, te.get("mode_index"),
                                    rec.get("probe_names") or [])
            if _fp["probe_E_named"]:
                rec[f"field_{port_bc}"] = _fp
                _pe = _fp["probe_E_named"]
                print("      probes: " + "  ".join(
                    f"{k}={v:.3g}" for k, v in sorted(_pe.items())), flush=True)
            print(f"    {port_bc:>6}: TE011 {te['f_ghz']:.6f}  "
                  f"Q={te['Q']:>9,.0f}  P>={te['P_min']:.4f}  "
                  f"spread={te['spread']:.4f}   ({why})", flush=True)

        if len(per_bc) == 2:
            q0, ql = per_bc["pec"]["Q"], per_bc["lumped"]["Q"]
            if ql >= q0:
                rec["error"] = (f"Q_L={ql:,.0f} >= Q0={q0:,.0f} — a 50 ohm load "
                                f"cannot RAISE Q. Solve or identification wrong.")
                print(f"    🔴 {rec['error']}", flush=True)
            else:
                qext = 1.0 / (1.0 / ql - 1.0 / q0)
                beta = q0 / qext
                rec.update(Q0=q0, Q_L=ql, Q_ext=qext, beta=beta,
                           branch="OVERCOUPLED" if beta > 1 else "undercoupled",
                           error_amplification=q0 / ql,
                           dQ0_vs_noloop=q0 - Q_NOLOOP_GROOVED)
                print(f"    -> Q0={q0:>9,.0f}  Q_L={ql:>8,.0f}  "
                      f"Q_ext={qext:>9,.0f}  beta={beta:>7.3f}  "
                      f"{rec['branch']}", flush=True)
                if int(area) in DRIVEN_ANOMALY:
                    dv = DRIVEN_ANOMALY[int(area)]
                    print(f"       driven anomaly said Q0={dv:,} here -> "
                          f"eigen is {q0/dv:.2f}x that", flush=True)
        save(out)

    # ---------- V1 FIRST. Nothing else means anything until it passes.
    print("\n" + "=" * 78)
    out["v1"], _v1_lines = check_v1(out["points"])
    for _l in _v1_lines:
        print(_l)

    # ---------- the table
    ok = [p for p in out["points"] if p.get("Q0") and p["grooved"]]
    if ok:
        print(f"\n  {'loop':>9}{'area':>7}{'Q0':>10}{'Q_ext':>10}{'beta':>9}"
              f"{'branch':>14}{'P_min':>9}{'spread':>9}")
        for p in sorted(ok, key=lambda x: x["area_mm2"]):
            t = p["te011_pec"]
            print(f"  {p['name']:>9}{p['area_mm2']:>7.0f}{p['Q0']:>10,.0f}"
                  f"{p['Q_ext']:>10,.0f}{p['beta']:>9.3f}{p['branch']:>14}"
                  f"{t['P_min']:>9.4f}{t['spread']:>9.4f}")
        print(f"  {'none':>9}{0:>7.0f}{Q_NOLOOP_GROOVED:>10,.0f}"
              f"{'—':>10}{'—':>9}{'—':>14}{0.9985:>9.4f}{0.0015:>9.4f}"
              "   <- anchored, no loop")

        # F1: does Q0 rise with area, reproducing the driven trend?
        qs = [p["Q0"] for p in sorted(ok, key=lambda x: x["area_mm2"])]
        rising = all(b > a_ for a_, b in zip(qs, qs[1:]))
        falling = all(b < a_ for a_, b in zip(qs, qs[1:]))
        print()
        if rising:
            print("  🔴 F1 FIRES — eigen Q0 RISES with loop area, reproducing "
                  "the driven trend.\n     The backwards behaviour is REAL. "
                  "Branch error and blended fits are BOTH dead\n     as "
                  "explanations. Report it; do not explain it away.")
            out["f1"] = "FIRES — trend is real"
        elif falling:
            print("  ✅ F1 does not fire — Q0 FALLS with loop area, as a larger "
                  "obstacle should.\n     🔑 The driven anomaly was therefore an "
                  "ARTEFACT of the driven extraction,\n     not physics. It was "
                  "never explained by the open-gap audit (different\n     "
                  "defect) — this is the measurement that settles it.")
            out["f1"] = "does not fire — driven anomaly was extraction"
        else:
            print("  ⚠️ Q0 is NOT monotonic in loop area. Neither the driven "
                  "trend nor its reverse.\n     Report the numbers; do not "
                  "fit a law to four non-monotonic points.")
            out["f1"] = "non-monotonic"

        # V4: extrapolate toward zero area
        smallest = min(ok, key=lambda x: x["area_mm2"])
        d = (smallest["Q0"] - Q_NOLOOP_GROOVED) / Q_NOLOOP_GROOVED
        print(f"  V4 smallest loop ({smallest['area_mm2']:.0f} mm^2) Q0="
              f"{smallest['Q0']:,.0f} vs no-loop {Q_NOLOOP_GROOVED:,.0f} "
              f"-> {d*100:+.1f}%  "
              + ("✅" if abs(d) < 0.10 else "🔴 FIRES — a small loop should "
                 "approach the no-loop Q"))

        # F2: purity vs area
        worst = max(ok, key=lambda x: x["te011_pec"]["spread"])
        w = worst["te011_pec"]["spread"]
        print(f"  F2 worst purity spread {w:.4f} at {worst['name']} "
              + ("✅ no loop size hybridises TE011" if w <= PURITY_SPREAD_WARN
                 else "🔴 FIRES — the loop DOES hybridise TE011 above some "
                      "size; this BOUNDS loop size independently of coupling"))

        # F3: does beta cross 1?
        bs = [(p["area_mm2"], p["beta"]) for p in
              sorted(ok, key=lambda x: x["area_mm2"])]
        under = [x for x in bs if x[1] < 1]
        over = [x for x in bs if x[1] >= 1]
        if under and over:
            print(f"  🔑 F3 — beta CROSSES 1 between {under[-1][0]:.0f} and "
                  f"{over[0][0]:.0f} mm^2. **Critical coupling is MEASURED**, "
                  f"not estimated.")
            out["critical_between_mm2"] = [under[-1][0], over[0][0]]
        else:
            print(f"  ⚠️ beta does not cross 1 in the swept range "
                  f"({bs[0][1]:.2f} .. {bs[-1][1]:.2f}) — critical coupling is "
                  f"OUTSIDE it.")

    # ---------- F4: does the groove interact with the loop?
    ctl = next((p for p in out["points"]
                if not p["grooved"] and p.get("Q0")), None)
    twin = next((p for p in out["points"]
                 if p["grooved"] and p.get("Q0")
                 and (p["ld"], p["lw"]) == ANCHOR_LOOP), None)
    print()
    if ctl and twin:
        dq = (ctl["Q0"] - twin["Q0"]) / twin["Q0"]
        df = (ctl["te011_pec"]["f_ghz"] - twin["te011_pec"]["f_ghz"]) * 1e3
        print("  F4 SEPARABILITY — loop 11x8, groove vs none:")
        print(f"     Q0 {ctl['Q0']:,.0f} (no groove) vs {twin['Q0']:,.0f} "
              f"(grooved) -> {dq*100:+.1f}%")
        print(f"     f0 {df:+.3f} MHz")
        if abs(dq) <= 0.02:
            print("     ✅ the groove costs the same with a loop as without — "
                  "groove and loop are\n        SEPARABLE and the OPTIMIZER may "
                  "treat them as independent axes.")
            out["f4"] = "separable"
        else:
            print("     🔴 F4 FIRES — the groove's Q cost DEPENDS on the loop. "
                  "They INTERACT, and\n        the optimiser must search the "
                  "JOINT space (§2b). This also kills any\n        prior fitted "
                  "on one axis while holding the other fixed.")
            out["f4"] = "INTERACT"
    else:
        print("  ⚠️ F4 not evaluable — need both the control and its grooved "
              "twin.")
    save(out)
    print(f"\n  result -> {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
