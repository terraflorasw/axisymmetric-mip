"""H3/H6 (driven) — sustainment across the density gap eigen cannot enter.

🔴 WHY THIS RIG EXISTS. Two open questions need the same thing:

  H6  what is the minimum ne that still sustains? eta falls 0.947 (ne=1e20) ->
      0.185 (1e18), and ne=1e19 has NO DATA — it failed in h3_loaded (mesh
      ScaledJac) and in h3_eigenprobe (PCG stagnation, 92 non-convergences).
      Mass loading from a real high-TDS sample pushes ne DOWN, into exactly
      that gap. This gates H5.
  sapphire  its loaded point does not converge in eigen either (eps +11.6
      beside the plasma's -30.09).

🔑 DRIVEN COST SCALES WITH Q, so it is cheapest exactly where eigen fails. The
step must resolve the linewidth = f0/Q, so samples ~ Q. Calibrated on
e0k2_c11x8_drv (16,000 samples / 1,542 s = 96 ms/sample):

    empty cavity   Q=44,384  ->  ~24,000 samples  ~2,300 s
    loaded plasma  Q=156     ->  ~126 samples     ~12 s

⚠️ BUT THE GAP IS NOT THE LOADED REGIME. If eta at ne=1e19 is ~0.5 then
Q ~ 22,000 and a +-40 MHz sweep is ~18,000 samples (~29 min) — per point. The
cost is set by Q, which is THE UNKNOWN. So:

## Two stages, and the second is sized by the first

  COARSE  +-40 MHz, step 636 kHz (~126 samples, ~12 s). Finds WHERE the dip is.
          Too coarse to fit Q; it is not asked to.
  FINE    +-5 MHz about the located dip, step from the coarse dip's own width.
          8x cheaper than a wide fine sweep because the band, not the step,
          is what a located dip lets you shrink.

🔴 EIGEN IS NOT AN OPTION HERE (CONVENTIONS §7c: one rig, one solver — this is
the DRIVEN driver; h3_eigen and h3_superpose are the eigen ones). Driven has no
NLEPS and no divergence-free projection, which is the specific machinery that
stagnates at these permittivities.

## The mode-identity hazard, and how it is handled

🔴 A CAP LOOP CHANGES WHICH MODE IT READS. Small loops couple to a TM111
polarisation and only reach TE011 above ~176 mm^2; the dip looks the same either
way, so a driven sweep ALONE cannot tell you. This rig therefore:
  - uses the 11x8 cap loop (176 mm^2, the measured TE011 branch), and
  - VALIDATES against eigen at the two densities where eigen converges, before
    trusting driven where it does not.
⚠️ The band also protects: TM111 sits 332.7 MHz away, far outside +-40 MHz.

VERIFICATION
  🔴 V1 and V2 ARE SUSPENDED (2026-08-24). BOTH ANCHORS WERE GROOVE-FREE.
      V1 was: reproduce h3_superpose's eigen f0=2.481566 / Q=163.
      V2 was: reproduce h3_loaded's eigen eta=0.185 at ne=1e18.
      h3_superpose and h3_loaded are discarded (KNOWN.md § THE FILTER), and
      0.185 was ALSO the wrong geometry — a 2 mm solid column, not this
      2.0-8.5 mm annulus, 17x the plasma.
      🔑 Both would have PASSED against void numbers and printed green ticks.
      ✅ TO RESTORE: loaded eigen at ne=1e20 and ne=1e18 on GEO_DESIGN.
      ⚠️ UNTIL THEN THIS RIG IS UNVALIDATED AGAINST EIGEN. It reports its
      numbers and says they are un-cross-checked. That is the honest state.
      🔴 DO NOT re-point these at a convenient number to get a tick back.
  V3  every case reports its coarse dip AND its fine fit; a fine band that does
      not contain the coarse dip is a REFUSAL, not a silent re-centre.
  V4  the continuation seed and Q_REF must come from ONE cavity: cold TE011
      **2.451500 GHz / Q0 43,523**, groove 5x10 + loop 11x8 (`h3_step3`,
      port terminated). ⚠️ This line once read "2.440003 / 12,368 (h3_ladder)" —
      wrong numbers AND wrong provenance; both are retracted (§7v, §7s).
      `check_eta_reference()` enforces the geometry half at startup.
FALSIFICATION
  🔴 F1  if eta at ne=1e19 is below 0.5, the sustaining margin is one decade or
         less and mass loading is a hard constraint on the nebuliser. Report it.
  🔴 F2  if driven ALSO fails to converge at eps ~ 0, the limitation is the
         OPERATOR and not the eigen formulation — no solver in this toolchain
         answers H6. Say so; do not reach for a third solver.
  🔴 F3  if the coupling branch is AMBIGUOUS the fit refuses rather than
         guessing beta; Q_L still stands and is reported alone.
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
from e0k2_anchor import (design_point, wall_sigma, analyse_driven as fit,
                         LOOP_PHI, LOOP_RW, LOOP_GAP)
from h3_loaded import drude, Z_FRAC, SECTORS, LOOP_LD, LOOP_LW, CAP_R_FRAC

# 🔑 THE RUN NAMES ITSELF FROM ITS SLUG (CONVENTIONS 7aw/7bd), and every
# parameter comes from its config — including which AXIS it sweeps.
import slug as S
import values
SLUG = S.parse()
CFG = S.config(SLUG)
PRM = CFG["_run"]["parameters"]
TAG = S.out(SLUG)

# 🔴 THE ETA REFERENCE IS PER-CONFIGURATION. CONVENTIONS §7c.
# This rig meshes GEO_DESIGN (groove 5x10) with an 11x8 cap loop, so the ONLY
# valid reference is that cavity's own cold Q0 — measured 2026-08-24 by
# `h3_ladder` step 3 via continuation from the grooved state.
#   44,384 = no loop, no groove   (E0, a BARE cavity)
#   29,854 = loop, no groove
#   12,368 = groove 5x10 + loop 11x8  <- THIS cavity
# ⚠️ It was 44384.0 here until 2026-08-24. That is the bare-cavity number and it
# would have inflated every eta in this rig: 1 - Q0/44384 instead of
# 1 - Q0/12368 reads HIGH, and the error grows as the plasma loads the cavity.
# 🔴🔴 BOTH CONSTANTS BELOW WERE RETRACTED 2026-08-24. Kept ONLY as a record.
#   Q_REF = 12,368 and COLD_TE011_GHZ = 2.440003 came from `h3_cold`, whose eigen
#   solve left the loop's port UNASSIGNED — which is PMC, not PEC, so the feed gap
#   was OPEN. An open gap plus the loop is an LC resonator near 2.45 GHz that
#   HYBRIDISES TE011 into a pair (CONVENTIONS §7v). **Neither number describes any
#   mode this machine has.**
# ✅ THE MEASURED DESIGN CAVITY (port terminated, `h3_step3` / `h3_loopq`):
#       TE011 f0 = 2.451490 GHz (driven mesh) · 2.451633 (cold mesh)
#       Q0     = 43,523        Q_ext = 9,231        beta = 4.70
# ⚠️ Q_REF IS A VACUUM-TORCH NUMBER. h3_step3 meshed the torch at eps=1; the
# design torch is SAPPHIRE eps=11.6, worth +2.0% on Q0 (e3_closure case B:
# 44,387 wall-only with sapphire vs 43,523 here). So every eta normalised
# against it is ~2% off in the SAME direction -- a systematic, not noise.
# 🔴 Do not "correct" it by scaling: re-measure it on the design mesh when the
# torch is restored (NEXT.md). Stated here so the next reader is not surprised.
Q_REF = values.get("eta.reference", status="current")   # vacuum torch, port terminated
Q_REF_CONFIG = {"groove_mm": tuple(values.get("cavity.groove.mm")),
                "loop_mm": tuple(values.get("loop.size.mm"))}
Q_REF_SOURCE = ("h3_step3 eigen, port_bc=pec (direct Q0, no port loss); "
                "cross-checked by h3_loopq at 43,422 on the cold-style mesh")
COLD_TE011_GHZ = values.get("cavity.f0.cold.ghz", solver="driven",
                            mesh="vacuum_torch", extraction="s11_locator")
# ⚠️ COLD_TE011_GHZ is a CROSS-CHECK only. The cold case LOCATES f0 empirically
# and sets the continuation seed from what it finds (§7s) — this constant must
# never become the seed again.

# 🔴 THE COLD CASE NEEDS ITS OWN SWEEP, AND THIS IS WHY.
# Cold linewidth = f0/Q0 = 2.440/12,368 = **197 kHz**. COARSE_STEP_GHZ is
# 200 kHz, so the wide sweep puts ~1 SAMPLE ACROSS THE COLD RESONANCE — it
# would miss or mangle the very dip the anchor depends on.
# ⚠️ The loaded cases are the opposite problem and the wide sweep is right for
# them: Q ~ 163-253 means a 10-15 MHz linewidth, 50-75 samples across.
# 🔑 "The BAND must bracket the widest feature; the STEP only has to resolve the
# narrowest." Cold is the narrowest by ~50x, so it gets its own band and step.
# It is a CHECK AT A KNOWN LOCATION, not a search — a narrow band is legitimate
# here in a way it would not be for an unknown loaded mode.
# 🔴 THE COLD CASE LOCATES THE RESONANCE. IT DOES NOT CHECK AT AN ASSUMED SPOT.
# First attempt swept +-3 MHz around 2.440003 and found **ZERO local minima**.
# That is the correct outcome for a wrong assumption, and the lesson is that a
# narrow band around an unconfirmed number cannot tell "not here" from "nowhere".
# ⚠️ The band must bracket every candidate: grooved-no-loop TE011 sits at
# 2.450561 (ladder, ANCHORED), and h3_cold's two design candidates are 2.440003
# and 2.494440. 2.40-2.52 contains all three with room.
# 🔑 The step still only has to resolve the NARROWEST feature: 197 kHz cold
# linewidth / 25 kHz = ~8 samples across the 3 dB width.
COLD_LO_GHZ, COLD_HI_GHZ = 2.40, 2.52
COLD_STEP_GHZ = 25e-6             # ~4,800 samples, ~8 across the cold 3 dB width
RI, RO = 2.00, 8.50         # h3_annular's operating point
CASE_TIMEOUT_S = 1800.0
SIZE_FACTORS = ["1.5", "1.42", "1.58"]

# the density grid. 1e18 and 1e20 are ANCHORS (eigen has them); the rest is the
# gap. 3e18 sits closest to the eps sign change (eps=+0.067).
# 🔑 ne=0.0 IS THE ANCHOR CASE, AND IT IS FIRST ON PURPOSE.
# drude(0, w) returns exactly (eps=1.0, sigma=0.0) — the plasma region becomes
# vacuum, so this is the SAME cavity `h3_ladder` solved by EIGEN, on the SAME
# mesh this rig builds. It restores the external anchor chain that suspending
# V1/V2 removed: closed form -> H2 -> ladder eigen -> THIS driven sweep.
# 🔴 It is not a data point about plasma. It is the instrument check, and if it
# fails nothing after it is quotable.
# 🔴 THE ANCHORED OPERATING POINT, ADDED 2026-08-24. It was NEVER ON THIS GRID.
# n_e = 7.3-8.6e18 (LTE Saha from MICAP's measured 5220-5270 K). It falls in the
# 3e18 -> 1e19 gap, a 3.3x span across which VSWR runs 43.3 -> 99.3 on the
# STEEPEST limb of the curve, just below the peak between 1e19 and 3e19.
# Every operating-point number in the record -- VSWR 80-89, Q0~109, beta~0.012,
# ~45 A, 960 W dump -- was INTERPOLATED across that gap and never solved.
N_E_ANCHOR    = 7.9e18            # centre; the value to quote
N_E_ANCHOR_LO = 7.3e18            # MICAP 5220 K
N_E_ANCHOR_HI = 8.6e18            # MICAP 5270 K
NE_GRID = [float(x) for x in PRM.get(
    "ne_grid", [0.0, 1.0e18, 3.0e18,
                N_E_ANCHOR_LO, N_E_ANCHOR, N_E_ANCHOR_HI,   # <-- the machine
                1.0e19, 3.0e19, 1.0e20])]
# 🔴 EMPTY ON PURPOSE — BOTH FORMER ANCHORS WERE VOID (2026-08-24).
# They were:
#   1e20: f0=2.481566, Q=163   <- groove-free. KNOWN discards the +31.6 MHz pull.
#   1e18: eta=0.185            <- groove-free AND the wrong geometry: it is the
#                                 2 mm SOLID-COLUMN artifact, not this r=2-8.5
#                                 annulus, which does not collapse.
# 🔑 An anchor from the wrong cavity is worse than no anchor: it validates a
# wrong answer and rejects a right one. Re-earn these on GEO_DESIGN.
# ✅ RESTORED 2026-08-24 — the anchor this rig asked for now EXISTS.
# The note below said: "TO RESTORE: run the loaded eigen case at ne=1e20 on
# GEO_DESIGN". `e3_closure` case E_vac_torch IS that run — loaded eigen, 1e20,
# GEO_DESIGN (grooved, 11x8 loop), VACUUM torch (matches this rig's
# --torch-material 1.0), port_bc=pec so Q is Q0. Solved 1140 s, P>=0.9996.
#   f0 = 2.482470 GHz   Q0 = 163.2
# 🔑 It already AGREES with this rig's previous 1e20 point to 70 kHz (2.8e-5)
# and 3.42% in Q0 — an eigen-vs-driven cross-check on the DESIGN cavity, which
# is the external anchor V1 lost when both groove-free anchors were voided.
# ⚠️ 1e20 is NOT the operating point (see N_E_ANCHOR). This is an INSTRUMENT
# anchor -- it validates the solver pair, not the machine.
ANCHORS = {1.0e20: {"f0": 2.482470, "Q0": 163.2,
                    "src": "e3_closure E_vac_torch (eigen, GEO_DESIGN, pec)"}}

# 🔴 STAGE 1 IS WIDE AND COARSE, and both halves of that were wrong before.
#
# v1 used a 636 kHz step — one linewidth of the ne=1e20 case — and would have
# been blind to the 68 kHz dip at ne=1e18. v2 fixed the step (20 kHz) but kept a
# 45 MHz band, and THAT was the binding constraint: the loaded resonances run
# 7 MHz to >45 MHz wide, so the 3 dB points fell outside the band on 4 of 5
# cases and a second, broader feature at ~2.447 GHz sat partly inside it.
#
# 🔑 The real requirement is to BRACKET the widest feature, not to resolve the
# narrowest. 2.30-2.65 GHz at 200 kHz is 1,750 samples — FEWER than the 2,250
# v2 spent — and it brackets 7 MHz to ~350 MHz while still putting 34 points
# across the narrowest linewidth measured (6.84 MHz at ne=1e18).
COARSE_LO_GHZ, COARSE_HI_GHZ = 2.30, 2.65
COARSE_STEP_GHZ = 200e-6
MINIMA_WINDOW = 20              # samples each side to call something a local min
FINE_MIN_SAMPLES_ACROSS = 20    # refine only if the coarse width is thinner
COARSE_MIN_DEPTH_DB = 0.05      # a real dip in a noiseless solve is still a dip
COARSE_EDGE_MHZ = 2.0           # a selected dip this close to an edge is unbracketed
CONTINUATION_JUMP_MHZ = 25.0    # a bigger step than this between cases is REPORTED

# 🔴 MEASURED, NOT ESTIMATED (2026-08-24). Was 50,709 "from e0k2's 11x8 loop" —
# an eigen number from the era when the port was UNASSIGNED, i.e. the loop gap
# was OPEN (§7v). The real value is 5.6x smaller.
#   Q0(port PEC) = 43,523 ; Q_L(port 50 ohm) = 7,538  ->  Q_ext = 9,117
# 🔑 Q_ext is set by LOOP GEOMETRY and is nearly independent of the plasma, so
# ONE measurement serves the whole density sweep. That is what makes the
# branch-free Q0 below possible.
# ✅ UPDATED 2026-08-24 to h3_loopq's value: it measured Q_ext across FOUR loop
# sizes and found the turning point (Q_ext MINIMISES at 176 mm^2), where
# h3_step3 measured one. The two agree to 1.2% at 11x8 (9,117 vs 9,231).
# 🔑 Q_ext is also THERMALLY INVARIANT (h3_hot: x0.996 over +100 K), so one
# number serves cold, hot and loaded.
# 🔴 CANONICAL NAME: `cavity.Q_ext` — see values.py / baselines.json.
# ⚠️ THIS RIG IMPORTS A VALUE MEASURED ON A DIFFERENT CAVITY. It meshes a
# VACUUM torch (80,621 tets, sf 1.42); 9,231 is the NO-TORCH eigen pair
# (h3_loopq, GEO_DESIGN which carries --no-torch). The mesh-matched value is
# h3_step3's 9,117 — +1.25% apart. Every beta_resolved, Q0_branch_free and
# derived VSWR in this rig carries that import.
#   values.get("cavity.Q_ext", solver="eigen_pair", mesh="vacuum_torch",
#              ne=0.0, loop_mm=[11.0, 8.0])   -> 9117.0
# 🔴 NOT SWITCHED HERE: changing it moves every stored number, so it belongs to
# a deliberate re-run — and h3_qext is measuring the right value now anyway.
# The WARNING must not wait for that (CONVENTIONS 7ar).
# 🔑 BOUND, NOT LITERAL (7bl). The context is the argument list, so the
# no-torch/vacuum-torch mismatch below is now a VISIBLE choice rather than a
# number with a comment beside it. Flipping it is one edit: mesh="vacuum_torch".
Q_EXT_MEASURED = values.get("cavity.Q_ext", solver="eigen_pair",
                            mesh="no_torch", ne=0.0)
Q_EXT_SOURCE = ("h3_loopq eigen pairs (port_bc pec vs lumped), 11x8 loop; "
                "h3_step3 gives 9,117 on the driven-style mesh, 1.2% apart")
Q0_COLD_EIGEN = values.get("cavity.Q0.cold", solver="eigen",
                           mesh="vacuum_torch", port_bc="pec")
Q_EXT_EST = Q_EXT_MEASURED  # legacy name, kept so the forecast block still reads
SHALLOW_DB = 0.30       # below this the dip is too shallow to trust a fit from


def save(out):
    p = pathlib.Path(S.outfile(SLUG, "result.json"))
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def build_mesh(tag, a, L, zlo, zhi, eps_p, sig_p, rec, ri=None, ro=None, _ld_override=None):
    """Mesh with the cap loop AND the plasma. Returns meta or None.

    🔑 `ri`/`ro` are EXPLICIT so the plasma annulus can be a SWEEP AXIS. It was
    a module constant (RI, RO = 2.00, 8.50) — which made the bore look like
    plumbing when it is the dominant coupling lever: TE011's E_phi is ZERO on
    axis, so where the bore puts the plasma sets how hard it loads the cavity.
    """
    ri = RI if ri is None else ri
    ro = RO if ro is None else ro
    thick = ro - ri
    # 🔴 THE HEURISTIC min(1.0, max(0.30, thick/6)) MAKES MESH SIZE A FUNCTION OF
    # THE SWEPT VARIABLE. Two failures from that, 2026-08-25:
    #   (a) CONFOUND — Q0 would move for two reasons at once, mesh and geometry.
    #   (b) COST INVERSION — the THINNEST annulus gets the FINEST elements, so
    #       2-4 mm wanted ~564k plasma tets against the baseline's ~119k, in a
    #       region 5.7x smaller. Whole baseline mesh is 80,621 tets; gmsh sat on
    #       it for 16 minutes with no error and no output.
    # ✅ A sweep must hold the mesh FIXED. `plasma_h` now comes from the config;
    # the heuristic remains the default for single-point runs.
    # ⚠️ 1.0 mm is what the baseline used, so the 2-8.5 control reproduces.
    #    Physically ample: the skin depth is 6.89 mm, far larger than any
    #    annulus here, so the field varies slowly across it.
    _ph = PRM.get("plasma_h")
    ph_mesh = float(_ph) if _ph else min(1.0, max(0.30, thick / 6.0))
    # 🔑 LOOP GEOMETRY IS PER-RUN, defaulting to the historical constants so
    # every existing config meshes byte-identically. A loop SWEEP needs these
    # to vary; the eta guard below refuses to QUOTE eta when they do.
    _LD = float(_ld_override) if _ld_override else float(PRM.get("loop_ld", LOOP_LD))
    _LW = float(PRM.get("loop_lw", LOOP_LW))
    _MOUNT = PRM.get("loop_mount", "cap")
    _G2 = float(PRM.get("loop_gap2", 0.0))
    # 🔑 AZIMUTHAL MOUNT, added 2026-08-30 for the LOADED pivot. Conventions
    # mirrored EXACTLY from h3_loopq.build_mesh — h and arc are INDEPENDENT and
    # geometry.py takes the arc LENGTH, deriving the angle from R = a - h,
    # because a fixed angle at different h is a different length.
    # ⚠️ A STRIP IS A CROSS-SECTION, NOT A MOUNT — it applies to any topology.
    _AZIM = PRM.get("loop_azim")            # [h_mm, arc_mm]
    _STRIP = PRM.get("loop_strip")          # [axial_mm, radial_mm]
    if _MOUNT == "azim" and not _AZIM:
        raise SystemExit("loop_mount='azim' requires loop_azim [h_mm, arc_mm]")
    args = ([x for x in GEO if x != "--no-torch"]
            + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
               "--sectors", str(SECTORS),
               "--torch-material", "1.0,3.5e-05",
               "--plasma", f"{ri},{ro},{zlo:.4f},{zhi:.4f}",
               "--plasma-h", f"{ph_mesh:.3f}",
               "--loop", f"{_LD},{_LW},{LOOP_RW},{LOOP_GAP}",
               # 🔴 --loop-cap IS NOT OPTIONAL. Without it the loop mounts on the
               # BARREL, where the radius is forced to a and it links H_z rather
               # than H_r — a different coupling to a different field component,
               # i.e. a different instrument. h3_loaded and e0k2_anchor both
               # mount on the CAP at CAP_R_FRAC*a, and V1/V2 compare against
               # their numbers. Omitting it silently changes what is measured.
               "--loop-phi", LOOP_PHI]
            + (["--loop-azim-standoff",
                f"{float(_AZIM[0]):g},{float(_AZIM[1]):g}"]
               if _MOUNT == "azim" else
               [] if _MOUNT == "barrel"
               else ["--loop-cap", f"{CAP_R_FRAC * a:.4f}"])
            + (["--loop-strip",
                f"{float(_STRIP[0]):g},{float(_STRIP[1]):g}"] if _STRIP else [])
            + ([f"--loop-gap2", f"{_G2:g}"] if _G2 else []))
    if _G2 and _MOUNT != "barrel":
        raise SystemExit("loop_gap2 requires loop_mount='barrel' (geometry.py:427)")
    if _MOUNT == "azim":
        # 🔑 loop_azim[0] IS THE STANDOFF (the wall gap), not the centreline.
        _thalf = (float(_STRIP[1]) / 2.0) if _STRIP else LOOP_RW
        _cl = float(_AZIM[0]) + _thalf
        rec.update({"mount": "azim", "standoff_mm": float(_AZIM[0]),
                    "centreline_mm": _cl, "arc_mm": float(_AZIM[1]),
                    "unwound_mm": float(_AZIM[1]) - LOOP_GAP + 2*_cl,
                    "strip_mm": list(_STRIP) if _STRIP else None})
    # 🔴 AZIMUTHAL LOOPS ALSO RETRY OVER THE ARC'S CHORD COUNT — no single count
    # works for all h, and which one fails moves with every parameter change
    # (h3_loopq.build_mesh carries the measured table). RECORD what worked: a
    # run that cannot say which geometry it built cannot be compared.
    _chords = (7, 3, 9, 5, 11) if _MOUNT == "azim" else (None,)
    for nc in _chords:
        _env = dict(os.environ)
        if nc is not None:
            _env["AMIP_ARC_CHORDS"] = str(nc)
        for sf in SIZE_FACTORS:
            r = subprocess.run([sys.executable, "geometry.py", "--out",
                                f"{tag}.msh", "--size-factor", sf] + args,
                               capture_output=True, text=True, env=_env)
            if not r.returncode and pathlib.Path(f"{tag}.msh").exists():
                rec["size_factor"] = sf
                if nc is not None:
                    rec["arc_chords"] = nc
                if sf != SIZE_FACTORS[0] or (nc is not None and nc != _chords[0]):
                    print(f"    ⚠️ mesh needed size-factor {sf}"
                          + (f", {nc} chords" if nc is not None else "")
                          + "; REPORTED", flush=True)
                return solveconf.load_meta(f"{tag}.msh")
            rec["_last_mesh_err"] = (r.stdout + r.stderr)[-200:]
    return None



def local_minima(d, window=MINIMA_WINDOW):
    """Every local minimum of |S11|, not just the deepest.

    🔴 WHY THIS EXISTS. `analyse_driven` returns the GLOBAL minimum. At ne=1e20
    the band holds TWO features — a broad one at 2.4472 (-1.28 dB) and TE011 at
    2.4824 (-0.35 dB) — so the global minimum is the wrong mode, and every
    downstream guard then fires honestly on a feature nobody wanted. §1:
    "deepest" is a proxy for "the one we want", and it is a bad one.
    """
    out = []
    for i in range(window, len(d) - window):
        if d[i][1] == min(x[1] for x in d[i - window:i + window + 1]):
            if not out or abs(d[i][0] - out[-1][1]) > 2e-3:
                out.append((i, d[i][0], d[i][1]))
    return out


def fit_dip(d, i0, step_ghz=None):
    """beta, 3 dB width, Q_L, Q0 for the resonance at index i0.

    ⚠️ `step_ghz` is the step ACTUALLY swept. `n_across` was hardcoded to
    COARSE_STEP_GHZ, which silently OVERSTATED resolution for any sweep using a
    different step — including the cold anchor's 20 kHz. A resolution guard
    computed from the wrong step cannot fire.

    🔑 The outward search STOPS AT A LOCAL MAXIMUM. With two overlapping
    resonances the baseline is not flat, and a naive 3 dB crossing walks out of
    one feature and into its neighbour — which is how v2 got "3 dB points not
    inside the band" on cases whose dip was perfectly well resolved. The turning
    point between two dips is the honest edge of this one.
    """
    f0, s0db = d[i0]
    S0 = 10 ** (s0db / 20)
    # 🔴🔴 |S11| CANNOT DISTINGUISH beta FROM 1/beta, AND THIS LINE PICKED ONE.
    # It hardcoded the UNDERCOUPLED branch. On 2026-08-24 that was WRONG for the
    # COLD case and RIGHT for every loaded one — the branch FLIPS as the plasma
    # loads the cavity, so no single choice is safe:
    #   cold  measured Q_L=7,004, |S11|=-3.67 dB
    #         undercoupled beta=0.208 -> Q0= 8,462   <- what this line returned
    #         OVERCOUPLED  beta=4.803 -> Q0=40,645   <- the truth
    #   eigen settled it from first principles (no |S11|, no phase):
    #         Q0(port PEC)=43,523 and Q_L(port 50 ohm)=7,538 -> Q_ext=9,117,
    #         beta=4.774. `h3_step3`, 2026-08-24.
    # 🔑 The cold case is the ETA REFERENCE, so one wrong branch there shifted
    # EVERY eta in the run (0.9295 -> 0.9853 at ne=1e18).
    # ✅ Both branches are now returned and the CALLER must resolve it —
    # `e0k2_anchor.branch_from_phase` on the UNWRAPPED phase, or an eigen pair.
    b_under = (1 - S0) / (1 + S0)
    b_over = (1 + S0) / (1 - S0) if S0 < 1 else float("inf")
    b = b_under                             # reported for continuity; SUSPECT
    amax = 1 - S0 ** 2
    tgt = math.sqrt(max(0.0, 1 - amax / 2))

    def walk(rng):
        prev, pf = None, None
        for i in rng:
            v = 10 ** (d[i][1] / 20)
            if prev is not None:
                if (prev - tgt) * (v - tgt) <= 0:      # crossed the 3 dB level
                    # 🔴 RETURNING d[i][0] SNAPPED THE EDGE TO THE GRID, and Q_L
                    # is f0 divided by the width, so BOTH edges quantised. Each
                    # can be off by a step, bounding the error at ~2/N — but
                    # WHERE it lands inside that bound depends on whether the
                    # width happens to be commensurate with the step.
                    # ⚠️ THAT IS WHY A SAMPLE-COUNT RULE DOES NOT WORK: 1e20's
                    # 16.00 MHz width is exactly 80 x 200 kHz, so decimation to
                    # TEN samples moved nothing (0.0% error) while cold at EIGHT
                    # was -12.5%. Commensurate grids look accurate and are not.
                    # ✅ Linear interpolation of the crossing fixes it, tested by
                    # decimating this rig's own sweeps: cold -6.4% -> +0.0%,
                    # anchor -7.3% -> -0.3%, 1e20 -1.1% -> -0.1%. And it closes
                    # the eigen-driven gap on the cold case: Q0 40,654 -> 43,455
                    # against eigen's 43,523, i.e. 7.2% -> 0.16%.
                    if prev is not None and abs(v - prev) > 1e-18:
                        frac = (tgt - prev) / (v - prev)
                        if 0.0 <= frac <= 1.0:
                            return pf + (d[i][0] - pf) * frac, None
                    return d[i][0], None
                if v < prev:                            # turned back down: next feature
                    return None, f"turned at {d[i][0]:.4f} GHz before reaching 3 dB"
            prev, pf = v, d[i][0]
        return None, "reached the band edge"

    fl, why_l = walk(range(i0, -1, -1))
    fh, why_h = walk(range(i0, len(d)))
    half = None
    if fl is not None and fh is not None:
        lw = fh - fl
    elif fl is not None or fh is not None:
        # 🔑 ONE-SIDED FALLBACK. A Lorentzian is symmetric about f0, so a single
        # measurable half-width determines the whole. This rescues the common
        # case where one flank runs into a neighbouring resonance or the band
        # edge while the other is clean. ⚠️ It ASSUMES symmetry, which two
        # overlapping resonances violate — so it is FLAGGED, not silent, and the
        # side used is recorded.
        half = "low" if fl is not None else "high"
        lw = 2 * (f0 - fl) if fl is not None else 2 * (fh - f0)
        if lw <= 0:
            return {"f0": f0, "s11_db": s0db, "beta": b,
                    "error": f"one-sided width came out non-positive ({half})"}
    else:
        return {"f0": f0, "s11_db": s0db, "beta": b,
                "error": f"3 dB width not measurable (low: {why_l or 'ok'}; "
                         f"high: {why_h or 'ok'})"}
    ql = f0 / lw
    r = {"f0": f0, "s11_db": s0db, "beta": b,
         "beta_undercoupled": b_under, "beta_overcoupled": b_over,
         "Q0_if_undercoupled": None, "Q0_if_overcoupled": None,
         "branch": "UNRESOLVED — |S11| alone cannot pick; see fit_dip",
         "f_lo": fl, "f_hi": fh,
         "linewidth_mhz": lw * 1e3, "Q_L": ql,
         # 🔑 BRANCH-FREE Q0. Was `ql * (1 + b)` with b pinned to the
         # UNDERCOUPLED root of |S11| — a choice dressed as a formula (§7x).
         #     1/Q_L = 1/Q0 + 1/Q_ext   ->   Q0 = 1/(1/Q_L - 1/Q_ext)
         # Q_L comes from the LINEWIDTH and Q_ext from GEOMETRY; neither needs
         # the dip depth, so the beta/1-beta ambiguity never enters.
         "Q0": (1.0 / (1.0 / ql - 1.0 / Q_EXT_MEASURED)
                if ql < Q_EXT_MEASURED else None),
         "n_across": abs(lw) / (step_ghz or COARSE_STEP_GHZ)}
    r["Q0_if_undercoupled"] = ql * (1 + b_under)
    r["Q0_if_overcoupled"] = ql * (1 + b_over) if b_over != float("inf") else None
    if r["Q0"] is not None:
        r["beta_resolved"] = r["Q0"] / Q_EXT_MEASURED
        r["branch"] = ("OVERCOUPLED" if r["beta_resolved"] > 1.0
                       else "undercoupled")
        # 🔴 ILL-CONDITIONING GUARD. Q0 = 1/(1/Q_L - 1/Q_ext) subtracts two
        # nearly-equal reciprocals when Q_L approaches Q_ext, and the relative
        # error amplifies by exactly Q0/Q_L. Cold: 5.8x, so 7% in Q_L becomes
        # 40% in Q0. Loaded: ~1.01x, harmless. **Say which regime you are in.**
        r["error_amplification"] = r["Q0"] / ql
        if r["error_amplification"] > 2.0:
            r["Q0_ill_conditioned"] = True
    else:
        r["branch"] = "Q_L exceeds Q_ext — Q0 not derivable"
    if half:
        r["one_sided"] = half
        r["one_sided_reason"] = why_h if half == "low" else why_l
    return r


def read_s11(tag):
    import csv as _csv
    rows = list(_csv.reader(open(f"postpro/{tag}/port-S.csv")))
    h = [x.strip() for x in rows[0]]
    si = next(i for i, c in enumerate(h) if "S" in c and "dB" in c)
    return [(float(r[0]), float(r[si])) for r in rows[1:] if r and r[0].strip()]


def sweep(mesh_tag, out_tag, band, step, eps_p, sig_p, attrs):
    """One driven sweep over an EXISTING mesh.

    🔴 mesh_tag AND out_tag, separately, and this cost a launch. The first
    version took one `tag`, and the caller passed `f"{tag}_coarse"` so the two
    stages would not overwrite each other's postpro — which also made it look
    for `h3_driven_n18p00_coarse.msh`, a mesh that was never built. One mesh
    feeds BOTH stages; only the OUTPUT tag differs.
    """
    # 🔴 ASK THE DIRECT QUESTION FIRST (§1). The mesh either has a plasma
    # attribute or it does not; discovering that by parsing a "dropped" message
    # afterwards is inference from a proxy.
    pa = attrs.get("plasma")
    if pa is None:
        raise RuntimeError(f"{out_tag}: mesh has NO plasma attribute — there is "
                           f"nothing to load the cavity with.")
    mats = {pa: {"Permittivity": eps_p, "Conductivity": sig_p,
                 "Permeability": 1.0}}
    c, _meta, dropped = solveconf.driven(f"{mesh_tag}.msh", out_tag, band,
                                         step=step, order=2, materials=mats)
    # ⚠️ `dropped` is mostly BENIGN: the shared template asks for a brake/mode
    # filter that this mesh does not carry (--brake 0), and driven records that
    # rather than raising. My first guard refused on ANY drop and killed all
    # five cases on it. Report them (§3) — refuse only on the one that matters.
    if dropped:
        print(f"    ⚠️ template materials not in this mesh (benign): "
              f"{dropped}", flush=True)
    # 🔑 §7d — verify with the CONSUMER, using a value the request did not
    # supply: is the plasma actually in the config being solved, with the
    # conductivity asked for? A dropped or mis-bound plasma yields a perfectly
    # plausible UNLOADED resonance and nothing downstream could tell.
    got = [m for m in c["Domains"]["Materials"] if pa in (m.get("Attributes") or [])]
    if not got:
        raise RuntimeError(f"{out_tag}: plasma attribute {pa} is in the mesh but "
                           f"NO material in the solved config covers it — this "
                           f"would solve an EMPTY cavity and call it loaded.")
    gs = float(got[0].get("Conductivity", 0.0))
    if abs(gs - sig_p) > 1e-9 * max(1.0, abs(sig_p)):
        raise RuntimeError(f"{out_tag}: plasma conductivity in the config is "
                           f"{gs}, not the {sig_p} requested.")
    print(f"    plasma: attr {pa}, eps={eps_p:+.3f}, sigma={gs:.4g} S/m "
          f"(verified in the solved config)", flush=True)
    run(out_tag, c, timeout=CASE_TIMEOUT_S)
    return fit(out_tag)


ETA_VALID = True


def check_eta_reference():
    """🔴 Refuse to score eta against a reference from a different cavity.

    CONVENTIONS §7c. The reference is per-configuration AND per loop size;
    this rig hardcodes one, so assert the geometry it is about to mesh is
    the geometry the reference was measured on.
    """
    from e0_solver_vs_math import GROOVE_DESIGN
    want_g = tuple(Q_REF_CONFIG["groove_mm"])
    if tuple(GROOVE_DESIGN) != want_g:
        raise SystemExit(
            f"🔴 eta reference {Q_REF:,.0f} was measured at groove "
            f"{want_g[0]:g}x{want_g[1]:g}, but GROOVE_DESIGN is now "
            f"{GROOVE_DESIGN[0]:g}x{GROOVE_DESIGN[1]:g}. Re-measure the "
            f"reference on the new groove before quoting any eta.")
    want_l = tuple(Q_REF_CONFIG["loop_mm"])
    got_l = (float(PRM.get("loop_ld", LOOP_LD)), float(PRM.get("loop_lw", LOOP_LW)))
    got_mount = PRM.get("loop_mount", "cap")
    # 🔑 REFUSE TO QUOTE eta, NOT TO RUN. The guard's purpose is that Q0 depends
    # on loop size (44,414 no loop -> 12,368 at 11x8), so an eta normalised
    # against the WRONG reference is meaningless. That is a reason to withhold
    # eta, not to forbid measuring BETA -- which comes from the dip depth and
    # needs no reference at all. Blocking the whole run turned a reporting
    # guard into a capability limit (CONVENTIONS 7bp: instrument fit).
    if got_l != want_l or got_mount != "cap":
        globals()["ETA_VALID"] = False
        print(f"  ⚠️ eta SUPPRESSED: reference {Q_REF:,.0f} is for a "
              f"{want_l[0]:g}x{want_l[1]:g} CAP loop; this run meshes "
              f"{got_l[0]:g}x{got_l[1]:g} {got_mount}. beta and Q_L are still "
              f"valid — they come from the dip, not from Q_REF.", flush=True)


def main():
    check_eta_reference()
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    w = 2.0 * math.pi * 2.45e9
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    print(f"  cavity a={a:.4f} L={L:.4f}  "
          f"Q_ref(groove 5x10 + loop 11x8)={Q_REF:,.0f}")
    print(f"    eta reference: {Q_REF_SOURCE}")
    if PRM.get("loop_grid"):
        _axis = ("loop leg depth ld = "
                 + ", ".join(f"{v:g}" for v in PRM["loop_grid"])
                 + f" mm at fixed ne={float(PRM.get('ne_fixed', 0.0)):.1e}")
    elif PRM.get("annulus_grid"):
        _axis = ("annulus " + ", ".join(f"{c[0]:g}-{c[1]:g}"
                                        for c in PRM["annulus_grid"])
                 + f" mm at fixed ne={PRM['ne_fixed']:.1e}")
    else:
        _axis = f"density, annulus {RI}-{RO} mm"
    print(f"  SWEEP AXIS: {_axis}", flush=True)
    print(f"  plasma r={RI}-{RO} mm  z=+-{Z_FRAC}L   cap loop "
          f"{LOOP_LD}x{LOOP_LW} mm (TE011 branch)")
    ncoarse = round((COARSE_HI_GHZ - COARSE_LO_GHZ) / COARSE_STEP_GHZ)
    print(f"  ONE wide sweep {COARSE_LO_GHZ}-{COARSE_HI_GHZ} GHz @ "
          f"{COARSE_STEP_GHZ*1e6:.0f} kHz ({ncoarse:,} samples per case)")
    print(f"  selection: CONTINUATION from the unloaded TE011, seeded at "
          f"{COLD_TE011_GHZ:.6f} GHz (MEASURED cold TE011, not the "
          f"analytic {exact:.4f}); NOT the global minimum")
    print(f"  guards: dip >{COARSE_MIN_DEPTH_DB} dB, >{COARSE_EDGE_MHZ} MHz from "
          f"a band edge, continuation step <{CONTINUATION_JUMP_MHZ:.0f} MHz, "
          f"3 dB walk stops at the turning point between features\n", flush=True)
    print("  coupling forecast (beta = Q0/Q_ext, Q_ext ~ "
          f"{Q_EXT_EST:,.0f} from e0k2's 11x8 loop):")
    print(f"    {'eta':>8}{'Q0':>9}{'beta':>9}{'|S11|min':>11}")
    for eta in (0.2, 0.5, 0.9, 0.99, 0.999):   # illustrative only;
        # ⚠️ was (0.185, ..., 0.9963) — both VOID groove-free results,
        # and printing them as reference points lent them authority.
        q0 = Q_REF * (1 - eta)
        b = q0 / Q_EXT_EST
        db = 20.0 * math.log10(abs((1 - b) / (1 + b)))
        print(f"    {eta:>8.4f}{q0:>9,.0f}{b:>9.4f}{db:>10.2f}dB"
              + ("" if abs(db) >= SHALLOW_DB else "   🔴 too shallow to fit"))
    print("    ⚠️ the ne=1e20 end is where driven is WEAKEST and eigen already "
          "works; the gap is where driven is strongest.\n", flush=True)
    out = {"q_ref": Q_REF, "q_ref_config": {k: list(v) for k, v in
           Q_REF_CONFIG.items()}, "q_ref_source": Q_REF_SOURCE,
           "ri_mm": RI, "ro_mm": RO,
           "q_ext_est": Q_EXT_EST, "shallow_db": SHALLOW_DB,
           "ne_grid": NE_GRID, "anchors": {str(k): v for k, v in ANCHORS.items()},
           # 🔑 THE REPORT MUST FOLLOW THE AXIS TOO (7bj, one level up). The
           # summary keyed points by ne; a BORE sweep holds ne fixed, so all
           # three results collapsed onto one dict entry and the table printed
           # "no result" three times over a result file that was complete.
           # 🔴 2026-08-27: `loop_grid` was added to the SWEEP and NOT here,
           # so a LOOP sweep called itself "density" — and with ne fixed at 0.0
           # every case collapsed onto one key. That is the bore-sweep failure
           # this comment was written for, repeated on the next axis added.
           # The axis list has to grow with the sweep or the report follows the
           # wrong one.
           "sweep_axis": ("loop" if PRM.get("loop_grid") else
                          "annulus" if PRM.get("annulus_grid") else "density"),
           "points": []}

    # 🔴 CONTINUATION SEED — MEASURED, NOT ANALYTIC. Was `exact` (2.4500, the
    # closed-form BARE value) until 2026-08-24. This rig meshes groove 5x10 +
    # loop 11x8, whose cold TE011 sits at 2.451500 — ⚠️ this comment once said
    # 2.440003, an open-gap artifact. The seed is now LOCATED empirically
    # anyway, so no constant can steer it. Historically it was **10.56 MHz from the
    # seed**, and the loop is what moves it.
    # ⚠️ THIS EXACT BUG ALREADY COST A RUN: `h3_sapphire` was seeded from another
    # regime and selected 2.4472 instead of 2.4824. A seed from the wrong cavity
    # does not fail loudly — it walks the continuation onto the wrong dip.
    expect = COLD_TE011_GHZ
    # 🔑 SWEEP AXIS. Default: density at the fixed design annulus. A config
    # carrying `annulus_grid` sweeps the BORE at a fixed density instead — the
    # lever surfaced 2026-08-25 (KNOWN.md § THE TORCH BORE IS A COUPLING LEVER).
    _ann = PRM.get("annulus_grid")
    # 🔑 THIRD SWEEP AXIS: the LOOP itself. `loop_grid` is a list of leg depths,
    # swept at fixed density — the coupler is the subject, not the plasma.
    # Added because the unwound conductor length is L = 2*ld + crossbar - gap,
    # so ld carries TWICE the leverage of gap and is the variable to sweep
    # (CONVENTIONS 7bp: a sweep must span the governing variable).
    _lg = PRM.get("loop_grid")
    if _lg:
        SWEEP = [(float(PRM.get("ne_fixed", 0.0)), RI, RO, float(v))
                 for v in _lg]
    elif _ann:
        SWEEP = [(float(PRM["ne_fixed"]), float(c[0]), float(c[1]), float(PRM.get('loop_ld', LOOP_LD)))
                 for c in _ann]
    else:
        SWEEP = [(ne, RI, RO, float(PRM.get('loop_ld', LOOP_LD))) for ne in NE_GRID]
    # 🔴 A TAG THAT DOES NOT CARRY WHAT VARIES IS A COLLISION WAITING FOR
    # SOMEONE TO CHANGE THE AXIS — and it has now happened TWICE. Once when the
    # annulus became the axis (caught at case 2, from the log banner), and again
    # on 2026-08-27 when the LOOP did: four ld cases shared ONE tag, so one
    # .msh, one .meta.json and one postpro dir served all four. Cases 1-3's
    # artefacts were overwritten and ld appeared nowhere in the record.
    # 🔑 Naming discipline did not survive either time, so this does not rely on
    # it: the guard FAILS BEFORE THE FIRST SOLVE if any two cases would write to
    # the same place, whatever axis is added next.
    def case_tag(ne, ri, ro, ld):
        _n = "cold" if ne == 0.0 else (
            f"n{math.log10(ne):.2f}".replace(".", "p").replace("+", ""))
        _r = f"r{ri:g}-{ro:g}".replace(".", "p")
        _l = f"ld{ld:g}".replace(".", "p")
        return f"{TAG}_{_n}_{_r}_{_l}"

    _tags = [case_tag(*s) for s in SWEEP]
    if len(set(_tags)) != len(_tags):
        _dup = sorted({t for t in _tags if _tags.count(t) > 1})
        raise SystemExit(
            f"🔴 TAG COLLISION — {len(_tags)} cases produce "
            f"{len(set(_tags))} distinct tags. Cases sharing a tag share a "
            f"mesh, a postpro directory and an S11 file, so all but the last "
            f"are overwritten.\n     colliding: {_dup}\n"
            f"  🔑 case_tag() does not name a variable this sweep is varying. "
            f"Add it there, not in the caller.")

    for ne, ri, ro, _ld_case in SWEEP:
        eps_p, sig_p = drude(ne, w)
        # 🔴 THE TAG MUST NAME EVERY SWEPT VARIABLE, NOT JUST DENSITY.
        # It was f"{TAG}_n{log10(ne)}" — fine while ne was the only axis. With
        # the annulus as the axis and ne FIXED, all four cases collapsed onto
        # ONE tag: same mesh file, same postpro dir, and build_mesh reuses an
        # existing {tag}.msh — so cases 2..4 would have silently solved case 1's
        # geometry and the sweep would have reported a flat line.
        # 🔑 Caught before the second case, from the log banner. CONVENTIONS
        # 7ap at the CASE level: a name that does not carry what varies is a
        # collision waiting for someone to change the axis.
        tag = case_tag(ne, ri, ro, _ld_case)
        # 🔑 RECORD THE SLICE COORDINATES, not just the axis (NEXT.md's standing
        # requirement: "which other variables were held fixed, and at what").
        # `ld_mm` was the swept variable on 2026-08-27 and was in NO field of the
        # record — the four points were distinguishable only by array order,
        # which is an argument, not a measurement (§7bm).
        rec = {"ne": ne, "eps": eps_p, "sigma": sig_p, "tag": tag,
               "ri_mm": ri, "ro_mm": ro,
               "ld_mm": float(_ld_case),
               "lw_mm": float(PRM.get("loop_lw", LOOP_LW)),
               "loop_gap_mm": float(LOOP_GAP),
               "loop_gap2_mm": float(PRM.get("loop_gap2", 0.0)),
               "loop_mount": PRM.get("loop_mount", "cap")}
        if ne == 0.0:
            print("  --- COLD (ne=0, plasma region = vacuum) — THE ANCHOR CASE",
                  flush=True)
            print(f"      must reproduce eigen: f0={COLD_TE011_GHZ:.6f} GHz, "
                  f"Q0={Q_REF:,.0f}", flush=True)
        else:
            print(f"  --- ne={ne:.1e}  eps={eps_p:+.3f}  sigma={sig_p:.4g} S/m",
                  flush=True)
        meta = build_mesh(tag, a, L, zlo, zhi, eps_p, sig_p, rec, ri, ro,
                          _ld_override=_ld_case)
        if meta is None:
            rec["error"] = f"mesh failed: {rec.pop('_last_mesh_err','')[:150]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        rec.pop("_last_mesh_err", None)
        attrs = meta["attributes"]
        rec["tets"] = meta["tets"]

        # ---- STAGE 1: one WIDE sweep. Everything is extracted from it.
        if ne == 0.0:
            band = (COLD_LO_GHZ, COLD_HI_GHZ)
            step = COLD_STEP_GHZ
            print(f"      LOCATOR sweep {band[0]:.3f}-{band[1]:.3f} GHz @ "
                  f"{step*1e6:.0f} kHz "
                  f"({round((band[1]-band[0])/step):,} samples)", flush=True)
            print("      brackets grooved-no-loop 2.450561 (ANCHORED) and both "
                  "h3_cold candidates 2.440003 / 2.494440", flush=True)
        else:
            band = (COARSE_LO_GHZ, COARSE_HI_GHZ)
            step = COARSE_STEP_GHZ
        rec["sweep_band_ghz"], rec["sweep_step_ghz"] = list(band), step
        try:
            sweep(tag, f"{tag}_wide", band, step, eps_p, sig_p, attrs)
        except RuntimeError as e:
            rec["error"] = f"wide sweep failed: {str(e)[:160]}"
            print(f"    🔴 {rec['error']}\n    REPORTED.", flush=True)
            out["points"].append(rec); save(out); continue
        d = read_s11(f"{tag}_wide")
        mins = [m for m in local_minima(d) if abs(m[2]) >= COARSE_MIN_DEPTH_DB]
        rec["minima"] = [{"f_ghz": f, "s11_db": v} for _, f, v in mins]
        print(f"    {len(mins)} local minima: "
              + "  ".join(f"{f:.4f}@{v:.2f}dB" for _, f, v in mins[:6]), flush=True)
        if not mins:
            # ⚠️ Was hardcoded "2.30-2.65 GHz" regardless of what was swept, so
            # the cold failure reported a band it never touched. Print the truth.
            rec["error"] = (f"no local minimum in {band[0]:.4f}-{band[1]:.4f} GHz "
                            f"@ {step*1e6:.0f} kHz "
                            f"(depth threshold {COARSE_MIN_DEPTH_DB} dB)")
            print(f"    🔴 {rec['error']}", flush=True)
            if ne == 0.0:
                raise SystemExit(
                    "🔴 THE COLD LOCATOR FOUND NOTHING. STOPPING.\n"
                    "   The cold sweep supplies BOTH the external anchor and the\n"
                    "   continuation seed for every loaded case. Without it the\n"
                    "   loaded runs would walk from an assumed frequency onto\n"
                    "   whatever dip happens to sit nearest — which is how a rig\n"
                    "   returns confident numbers for the wrong mode.\n"
                    "   Widen COLD_LO_GHZ/COLD_HI_GHZ or lower "
                    "COARSE_MIN_DEPTH_DB, then re-run.")
            out["points"].append(rec); save(out); continue

        if ne == 0.0:
            # 🔑 THE SEED IS MEASURED HERE, NOT ASSUMED. Deepest dip wins for the
            # cold case only: with no plasma there is no continuation history to
            # follow, and depth is the honest discriminator for which resonance
            # this port actually couples to.
            i_c, f_c, v_c = min(mins, key=lambda m: m[2])
            print(f"    🔑 deepest cold dip: {f_c:.6f} GHz @ {v_c:.2f} dB",
                  flush=True)
            d_eig = (f_c - COLD_TE011_GHZ) * 1e3
            print(f"       vs h3_cold eigen {COLD_TE011_GHZ:.6f} -> "
                  f"{d_eig:+.3f} MHz", flush=True)
            print(f"       vs ladder grooved-no-loop 2.450561 -> "
                  f"{(f_c - 2.450561)*1e3:+.3f} MHz  (the loop's pull)",
                  flush=True)
            rec["cold_locator"] = {"f_ghz": f_c, "s11_db": v_c,
                                   "delta_vs_eigen_mhz": d_eig,
                                   "n_minima": len(mins)}
            expect = f_c        # 🔑 every loaded case now continues from MEASURED

        # ---- SELECT BY CONTINUATION, not by depth.
        # 🔑 `expect` starts at the UNLOADED TE011 (the plasma is a weak
        # perturbation at the lowest density) and then follows the mode. E1b:
        # identity across a large perturbation needs CONTINUATION, not endpoint
        # pairing — and the pull here is +2 MHz to +32 MHz in smooth steps.
        i_sel, f_sel, v_sel = min(mins, key=lambda m: abs(m[1] - expect))
        # 🔴 f0 WAS QUANTISED TO THE SWEEP GRID. Picking the lowest SAMPLE
        # reports f0 to the step, not to the resonance — every f0 this rig had
        # emitted was a grid multiple, which is why the anchor ladder
        # (2.4578 / 2.4586 / 2.4594) sat exactly 4 steps apart.
        # ✅ TESTED 2026-08-25 by decimating this rig's OWN anchor sweep: a
        # parabolic vertex through the three samples straddling the minimum
        # locates f0 to ~5 kHz even at a 1.6 MHz step — 25-300x better than
        # pick-lowest. Re-fitting the stored ladder moved f0 by -90..+88 kHz and
        # the anchor-band slope by -7.3% (1.231 -> 1.141 MHz per 1e18).
        # ⚠️ REFINES THE REPORTED f0 ONLY. Continuation still selects a SAMPLE,
        # and `i_sel` indexes `d` (local_minima yields (index_into_d, f, dB)).
        if 0 < i_sel < len(d) - 1:
            _y1, _y2, _y3 = d[i_sel - 1][1], d[i_sel][1], d[i_sel + 1][1]
            _den = _y1 - 2.0 * _y2 + _y3
            if abs(_den) > 1e-15:
                _h = d[i_sel + 1][0] - d[i_sel][0]
                _shift = 0.5 * _h * (_y1 - _y3) / _den
                if abs(_shift) <= _h:          # a vertex outside the bracket is a bad fit
                    rec["f0_grid_ghz"] = f_sel
                    rec["f0_interp_shift_khz"] = _shift * 1e6
                    f_sel = f_sel + _shift
        jump = (f_sel - expect) * 1e3
        rec["expect_ghz"], rec["jump_mhz"] = expect, jump
        if abs(jump) > CONTINUATION_JUMP_MHZ:
            rec["error"] = (f"continuation BROKE: nearest minimum to {expect:.4f} "
                            f"is {f_sel:.4f} GHz, a {jump:+.1f} MHz jump "
                            f"(> {CONTINUATION_JUMP_MHZ} MHz). Either the mode "
                            f"moved further than one step allows or this is a "
                            f"different mode. REPORTED, not followed.")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        edge = min(f_sel - COARSE_LO_GHZ, COARSE_HI_GHZ - f_sel) * 1e3
        if edge < COARSE_EDGE_MHZ:
            rec["error"] = (f"selected dip {f_sel:.4f} GHz is {edge:.1f} MHz from "
                            f"a band edge — not bracketed (§1)")
            print(f"    🔴 {rec['error']}", flush=True)
            out["points"].append(rec); save(out); continue
        print(f"    selected {f_sel:.6f} GHz ({jump:+.2f} MHz from expected "
              f"{expect:.4f}) — by CONTINUATION, not depth", flush=True)

        fi = fit_dip(d, i_sel, rec.get('sweep_step_ghz'))
        rec["wide_fit"] = fi
        if "Q_L" not in fi:
            rec["error"] = f"wide: {fi['error']}"
            print(f"    🔴 {rec['error']}", flush=True)
            expect = f_sel                  # the LOCATION is still good
            out["points"].append(rec); save(out); continue
        if fi["n_across"] < FINE_MIN_SAMPLES_ACROSS:
            print(f"    ⚠️ only {fi['n_across']:.0f} samples across the 3 dB "
                  f"width — width is under-resolved, Q_L is indicative only",
                  flush=True)
            rec["width_under_resolved"] = True
        if abs(fi["s11_db"]) < SHALLOW_DB:
            rec["shallow"] = True
            print(f"    ⚠️ |S11|min={fi['s11_db']:.3f} dB — deeply UNDERCOUPLED, "
                  f"beta and Q0 are LOW CONFIDENCE (Q_L stands; beta<<1 makes "
                  f"Q_L ~ Q0)", flush=True)
        rec["Q0"] = fi["Q0"]
        if ne == 0.0:
            # 🔑 THE COLD CASE IS THE REFERENCE, NOT A POINT SCORED AGAINST ONE.
            # 🔴 BUT TAKE IT FROM EIGEN, NOT FROM HERE. The cold cavity is
            # OVERCOUPLED (beta 4.77), so its Q0 is exactly where the
            # 1/Q_L - 1/Q_ext subtraction is worst conditioned (5.8x). Eigen
            # with the port SHORTED measures Q0 DIRECTLY — no port loss to
            # subtract, no amplification. Driven's own value is the CROSS-CHECK.
            # ⚠️ §7t still holds: this is not "importing a reference from
            # another cavity". Eigen and driven agree on f0 to 12 kHz, so it is
            # the same cavity — it is importing the BETTER-CONDITIONED estimate
            # of one quantity, and saying so.
            out["q_ref_driven_derived"] = fi["Q0"]
            out["q_ref_measured"] = Q0_COLD_EIGEN
            out["q_ref_source"] = "h3_step3 eigen, port_bc=pec (direct Q0)"
            out["q_ref_measured_f0"] = fi["f0"]
            rec["eta"] = None
            dd = fi["Q0"]
            print(f"    🔑 ETA REFERENCE: Q0={Q0_COLD_EIGEN:,.0f} "
                  f"(eigen, port shorted — direct)", flush=True)
            print(f"       driven-derived here: {dd:,.0f}"
                  + (f"  ({abs(dd-Q0_COLD_EIGEN)/Q0_COLD_EIGEN*100:.0f}% apart)"
                     if dd else "")
                  + "  — CROSS-CHECK; ill-conditioned when overcoupled",
                  flush=True)
            print(f"       branch here: {fi.get('branch')}  "
                  f"beta={fi.get('beta_resolved', float('nan')):.3f}  "
                  f"(error amplification {fi.get('error_amplification', 0):.1f}x)",
                  flush=True)
        else:
            # 🔴 SAME MESH, SAME SOLVER, SAME CAVITY. eta from a reference
            # measured by a DIFFERENT solver on a DIFFERENT mesh imports both
            # discretisation systematics into the ratio (§7c).
            qref = out.get("q_ref_measured")
            if qref is None:
                rec["eta"] = None
                rec["eta_error"] = "cold reference missing — eta not computable"
            else:
                rec["eta"] = 1.0 - fi["Q0"] / qref
        expect = fi["f0"]                   # advance the continuation
        print(f"    f0={fi['f0']:.6f} GHz  lw={fi['linewidth_mhz']:.2f} MHz  "
              f"Q_L={fi['Q_L']:,.0f}  beta={fi['beta']:.4f}  Q0={fi['Q0']:,.0f}  "
              + (f"eta={rec['eta']:.4f}" if rec.get("eta") is not None
                 else "eta=— (reference case)"), flush=True)
        out["points"].append(rec); save(out)
    _report(out)


def resolve_branch(w, ne):
    """Which root of |S11| is this? Returns the resolved beta, Q0 and Q_ext.

    🔴 `fit` returns the UNDERCOUPLED root beta_u = (1-|S11|)/(1+|S11|). The
    overcoupled root is its reciprocal, and |S11| ALONE CANNOT TELL THEM APART:
    both give a shallow dip. Reading the wrong one produced Q0 = 359 and 1,325
    on healthy cold barrel cases and a false "the rig is broken" alarm.

    🔴 THE DISCRIMINATOR IS ONLY VALID COLD, AND THAT GATE IS NOT OPTIONAL.
    It works by requiring Q0 to be the cavity's own cold Q0 — which is only true
    when there is no plasma to load it. At the anchored density Q0 ~ 105, so
    comparing against Q_ref = 43,523 would pick OVERcoupled for a case that is
    genuinely undercoupled (beta ~ 0.012) and invert every number downstream.
    ⚠️ This is the failure this repo keeps repeating: an instrument validated in
    one regime and reused in another without checking it still applies. So a
    loaded point is returned UNRESOLVED rather than guessed at.

    🔑 Q_ext is robust on either root — Q_ext = Q_L*(1+beta_u) overcoupled,
    which is Q_L to within a few percent. Q0 is the fragile number, not Q_ext.
    """
    qL, b_u = w["Q_L"], w["beta"]
    q0_u = qL * (1.0 + b_u)
    if not b_u:
        return {"resolved": False, "over": False, "beta": b_u, "Q0": q0_u,
                "Q_ext": float("nan"), "why": "beta = 0"}
    q0_o = qL * (1.0 + 1.0 / b_u)
    if ne != 0.0:
        # loaded: the cold anchor does not apply. Report the undercoupled root
        # as the fit gives it, and SAY it was not resolved.
        return {"resolved": False, "over": False, "beta": b_u, "Q0": q0_u,
                "Q_ext": q0_u / b_u,
                "why": f"loaded (ne={ne:.1e}) — the cold Q0 anchor does not "
                       f"apply, so the branch is NOT resolved here"}
    over = abs(math.log(q0_o / Q_REF)) < abs(math.log(q0_u / Q_REF))
    return {"resolved": True, "over": over,
            "beta": (1.0 / b_u) if over else b_u,
            "Q0": q0_o if over else q0_u,
            "Q_ext": qL * (1.0 + b_u) if over else q0_u / b_u,
            "why": f"cold: |ln(Q0/Q_ref)| against Q_ref = {Q_REF:,.0f}"}


def _report(out):
    print("\n" + "=" * 78)
    _axis_now = out.get("sweep_axis")
    _lead = (f"{'ld mm':<10}" if _axis_now == "loop" else
             f"{'bore mm':<10}" if _axis_now == "annulus" else f"  {'ne':>9}")
    print(f"{_lead}{'eps':>9}{'f0 GHz':>11}{'lw MHz':>9}{'Q_L':>8}"
          f"{'beta':>8}{'Q0':>7}{'eta':>9}")
    for p in out["points"]:
        # 🔴 WAS `if p.get("eta") is None`. eta is None BY DESIGN for every
        # reference case — and in a fixed-density bore sweep that is EVERY
        # point, so a complete run printed "no result" on all three rows while
        # result.json held all three fits. The comment below already prescribed
        # keying on wide_fit; only the `P = ` line beneath it was ever fixed.
        if not p.get("wide_fit"):
            print(f"  {p['ne']:>9.1e}{p['eps']:>9.3f}   🔴 "
                  + p.get("error", "no result")[:46])
            continue
        f = p["wide_fit"]
        flag = ""
        if f.get("one_sided"):
            flag = f"  1-sided({f['one_sided']})"
        elif p.get("width_under_resolved"):
            flag = "  width thin"
        lead = (f"  {p['ld_mm']:<8.1f}" if _axis_now == "loop" else
                f"{p['ri_mm']:.0f}-{p['ro_mm']:<7.1f}"
                if _axis_now == "annulus" else f"  {p['ne']:>9.1e}")
        eta = f"{p['eta']:>9.4f}" if p.get("eta") is not None else f"{'—':>9}"
        q0 = p.get("Q0", f.get("Q0"))
        # 🔴 A FIT CAN HAVE f0 AND DEPTH BUT NO WIDTH. If the 3 dB walk runs
        # off the band or turns at a competing feature, `linewidth_mhz`, `Q_L`
        # and `beta` are simply ABSENT — and this line used to KeyError, which
        # killed the whole report and lost the summary of a run that HAD
        # located both dips (2026-08-31, azimuthal loaded: cold 2.450325 at
        # -16.29 dB, loaded 2.455755 at -4.13 dB, +5.43 MHz pull, all recorded
        # in the result file and none of it printed). Print what exists.
        def _n(key, w, fmt):
            v = f.get(key)
            return f"{v:>{w}{fmt}}" if isinstance(v, (int, float)) else f"{'—':>{w}}"
        print(f"{lead}{p['eps']:>9.3f}" + _n('f0', 11, '.4f')
              + _n('linewidth_mhz', 9, '.2f') + _n('Q_L', 8, '.0f')
              + _n('beta', 8, '.4f')
              + (f"{q0:>7.0f}" if isinstance(q0, (int, float)) else f"{'—':>7}")
              + eta + flag)
    # 🔴 KEY ON A SUCCESSFUL FIT, NOT ON eta. The cold reference case has
    # eta=None BY DESIGN — it is the denominator, not a scored point — so
    # keying on eta silently dropped it and the summary reported the anchor
    # "PRODUCED NO FIT" while its Q0=8,462 sat in the result file being used
    # by every loaded point. §7d: two statements from one source disagreed.
    # 🔴 §7d — TWO VALUES FROM ONE SOURCE CANNOT DISAGREE. The Q0 column above
    # is the fit's UNDERCOUPLED root; the resolved table below reports the
    # branch the cold anchor actually selects. On the loop sweep those differ by
    # ~30x (1,490 vs 40,861 for ld=5), and printing both unlabelled in one
    # report is precisely the disagreement §7d forbids.
    if _axis_now == "loop":
        print("  ⚠️ the Q0 column above is the UNDERCOUPLED root, as `fit` "
              "returns it. These cold\n     barrel cases are OVERcoupled — "
              "see the branch-resolved table below, and read Q_ext\n"
              "     from there, not Q0 from here.")
    _key = ((lambda q: q["ld_mm"]) if _axis_now == "loop" else
            (lambda q: (q["ri_mm"], q["ro_mm"]))
            if _axis_now == "annulus" else (lambda q: q["ne"]))
    P = {_key(p): p for p in out["points"] if p.get("wide_fit")}
    if len(P) != len([q for q in out["points"] if q.get("wide_fit")]):
        print("  🔴 SWEEP KEY COLLIDES — two points share a key, so the "
              "summary below is reporting only one of them.")
    print()
    # 🔴🔴 V1 IS SUSPENDED, 2026-08-24 — ITS ANCHOR WAS DISCARDED.
    # It compared ne=1e20 against `h3_superpose`'s vac_hot (f0=2.481566, Q=163,
    # eta=0.9963). That run is GROOVE-FREE and KNOWN.md § NOT ESTABLISHED
    # discards it by name (the "+31.6 MHz loaded pull").
    # 🔑 The check would have PASSED against a void number and printed a green
    # tick — a validator anchored to the wrong cavity is worse than none (§7r).
    # ✅ TO RESTORE: run the loaded eigen case at ne=1e20 on GEO_DESIGN, then put
    #    its f0/eta here. Until then this rig is UNVALIDATED against eigen and
    #    says so, which is the honest state, not a defect.
    # ✅ V1' — THE COLD ANCHOR, AS A THREE-WAY. The cold sweep LOCATES the
    # resonance this port couples to; that location says which eigen story is
    # right, and the answer is not assumed either way.
    # 🔑 AXIS-AWARE CONTROL. On a LOOP sweep every case is cold, so P has no
    # 0.0 key at all and this block silently vanished. The control there is the
    # DESIGN loop — the case that must reproduce the measured family — exactly
    # as the design annulus is the control on a bore sweep.
    c = P.get(float(LOOP_LD)) if _axis_now == "loop" else P.get(0.0)
    if c and c.get("wide_fit"):
        f0c = c["wide_fit"]["f0"]; q0c = c["wide_fit"]["Q0"]
        d_cold = (f0c - COLD_TE011_GHZ) * 1e3       # h3_cold's design candidate
        d_grv = (f0c - 2.450561) * 1e3              # ladder grooved, NO loop
        print("  ✅ V1' COLD LOCATOR — where does this port actually resonate?")
        _br = resolve_branch(c["wide_fit"], c["ne"])
        print(f"     measured  f0={f0c:.6f} GHz   Q0={q0c:,.0f}   "
              f"|S11|={c['wide_fit']['s11_db']:.2f} dB")
        if _br["resolved"] and _br["over"]:
            # ⚠️ q0c above is the undercoupled root. Saying "eta is referenced
            # to THIS measured Q0" while that number is off by 30x is how a
            # wrong reference gets adopted (§7c has caught this name 4 times).
            print(f"     🔑 BRANCH: OVERcoupled — beta={_br['beta']:.1f}, so "
                  f"Q0={_br['Q0']:,.0f} and Q_ext={_br['Q_ext']:,.0f}.\n"
                  f"        The {q0c:,.0f} above is the UNDERCOUPLED root and "
                  f"is NOT this cavity's Q0.")
        print(f"     vs h3_cold eigen 2.440003 (A2/A0-selected, m_az=1) "
              f"-> {d_cold:+.3f} MHz")
        print(f"     vs ladder grooved-NO-loop 2.450561 (ANCHORED)   "
              f"-> {d_grv:+.3f} MHz")
        if abs(d_cold) <= 1.0:
            print("     🔑 h3_cold's 2.440003 IS the coupled resonance. The loop "
                  "pulls TE011 down\n"
                  "        ~10.6 MHz and Q0 12,368 stands as the eta reference.")
        elif abs(d_grv) <= 1.0:
            print("     🔴 THE LOOP BARELY MOVES TE011 — the port resonates at "
                  "the GROOVED-no-loop\n"
                  "        frequency. Then h3_cold's 2.440003 was a DIFFERENT "
                  "mode (it labelled it\n"
                  "        m_az=1 and picked it on lowest A2/A0), and "
                  "**Q0=12,368 is not the eta\n"
                  "        reference for TE011**. The -10.56 MHz continuation "
                  "argument fails with it.")
        else:
            print("     🔴 NEITHER. The coupled resonance is at neither eigen "
                  "candidate.\n"
                  "        Do not name this mode from frequency alone — get "
                  "purity on the eigen\n"
                  "        solve of THIS mesh before calling it TE011.")
        _q0ref = _br["Q0"] if _br["resolved"] else q0c
        print(f"     🔑 eta below is referenced to THIS measured "
              f"Q0={_q0ref:,.0f} — same mesh, same solver"
              + (", branch-resolved." if _br["resolved"] else "."))
    elif out.get("sweep_axis") == "annulus":
        # 🔑 A BORE SWEEP HAS NO COLD CASE AND DOES NOT NEED ONE. Its anchor is
        # the DESIGN annulus reproducing the density run. Printing "nothing here
        # is quotable" over a complete result set is how a good run gets thrown
        # away (7bl) — the message belongs to the density sweep, not this one.
        print("  ⓘ no cold case in a bore sweep — by design. The anchor is the "
              f"{RI:g}-{RO:g} mm control below.")
    else:
        print("  🔴 COLD LOCATOR PRODUCED NO FIT — no anchor and no seed. "
              "Nothing here is quotable.")
    print()

    # 🔴 WAS `P.get(1.0e20)`. 1e20 is NOT the operating point and never was —
    # it is 13x the anchored density (CONVENTIONS §7ab). Report the ANCHOR.
    # 🔑 AXIS-AWARE ANCHOR. On a bore sweep the anchor is the DESIGN annulus
    # (the control that must reproduce the density run), not a density.
    if _axis_now == "loop":
        a = P.get(float(LOOP_LD))     # the design loop = the control
    elif _axis_now == "annulus":
        a = P.get((RI, RO))   # the design annulus = the control
    else:
        a = P.get(N_E_ANCHOR)
    if a:
        print("  🔴 V1 SUSPENDED — no valid eigen anchor on the DESIGN cavity.")
        _eta = (f"{a['eta']:.4f}" if a.get("eta") is not None
                else "— (reference case)")
        # 🔴 branch-resolve before quoting. This line printed the
        # UNDERCOUPLED root as "measured here: Q0=", 30x low on a cold
        # overcoupled case, directly under a heading that invites adoption.
        _abr = resolve_branch(a["wide_fit"], a["ne"])
        _q0 = (_abr["Q0"] if _abr["resolved"]
               else a.get("Q0", a["wide_fit"].get("Q0")))
        print(f"     measured here: f0={a['wide_fit']['f0']:.6f} GHz  "
              f"eta={_eta}  Q0={_q0:,.0f}")
        print("     ⚠️ NOT cross-checked. The old anchor (2.481566 / 0.9963) was "
              "groove-free and is void.")
        print("     ⚠️ eta = 1 - Q0/Q_ref is INSENSITIVE to Q0 when Q0 << Q_ref. "
              "Quote eta, not Q0.")
    # ⚠️ These branches were once a bare `else:` whose body ran inside the `if`,
    # so the rig printed a measured eta AND "missing" for the same case.
    elif _axis_now in ("loop", "annulus"):
        # 🔴 NOT "the operating point was not measured". A fixed-density sweep
        # has no density anchor BY DESIGN; printing the density sweep's alarm
        # over a complete result set is how a good run gets thrown away.
        print("  🔴 the CONTROL case is missing — no design-loop/annulus "
              "point to place this sweep against.")
    else:
        print(f"  🔴 ne={N_E_ANCHOR:.1e} missing — THE OPERATING POINT WAS NOT "
              f"MEASURED. (Do not substitute 1e20: different regime — the plasma "
              f"shields there, delta/shell 0.30, vs 1.06 here.)")
    g = P.get(1.0e19)
    if g:
        print(f"\n  🔑 THE GAP: eta(ne=1e19, eps=-2.109) = {g['eta']:.4f}")
        # ⚠️ F1's PREMISE IS NOW STALE and its threshold is not re-tuned here.
        # It calls 1e19 "one decade below the operating point" — true when the
        # operating point was assumed to be 1e20. Against the anchored 7.9e18,
        # 1e19 is ABOVE it. And eta is flat (0.986-0.998) across the whole grid,
        # so this falsifier cannot discriminate anyway (§7z). Read it as a
        # RECORDED VALUE, not as a test, until it is restated.
        print("  ⚠️ F1's premise is stale: 1e19 is ABOVE the anchored 7.9e18, "
              "not a decade below it. Reported, not tested.")
        print("  F1 " + ("🔴 FIRES — eta < 0.5 one decade below the operating "
                         "point; mass loading is a HARD nebuliser constraint."
                         if g["eta"] < 0.5 else
                         f"✅ eta = {g['eta']:.4f} >= 0.5 — the margin survives. "
                         f"Mass loading is NOT a hard EM constraint."))
    elif _axis_now == "density":
        print("\n  🔴 ne=1e19 missing — the gap is NOT bridged (F2).")

    # ── bore sweep: report the LEVER, which is the whole question ────────────
    if out.get("sweep_axis") == "annulus":
        pts = sorted((q for q in out["points"] if q.get("wide_fit")),
                     key=lambda q: q["ro_mm"])
        if len(pts) >= 2:
            qe = out["q_ext_est"]
            # 🔴 DO NOT RECOMPUTE beta AS Q0/q_ext_est. beta is the PRIMARY
            # measurement (dip depth); Q0 is DERIVED from it as Q_L(1+beta).
            # Dividing by the cold q_ext_est=9,231 gave 0.0114 against the fit's
            # own 0.0127 — 12% apart, because the loop's IMPLIED Q_ext at this
            # operating point is ~8,221, not the cold no-torch value. Two
            # numbers from one solve disagreeing is 7d; quote the fit.
            print(f"\n  {'bore mm':<10}{'Q0':>8}{'beta':>9}{'VSWR':>8}"
                  f"{'Q_ext impl':>12}")
            for q in pts:
                w = q["wide_fit"]
                b = w["beta"]
                g = abs((b - 1.0) / (b + 1.0))
                qi = w["Q_L"] * (1.0 + b) / b if b else float("nan")
                print(f"  {q['ri_mm']:.0f}-{q['ro_mm']:<7.1f}{q['Q0']:>8.0f}"
                      f"{b:>9.4f}{(1 + g) / (1 - g):>8.1f}{qi:>12,.0f}")
            lo, hi = pts[0], pts[-1]
            print(f"\n  🔑 LEVER: {lo['ri_mm']:.0f}-{lo['ro_mm']:g} vs "
                  f"{hi['ri_mm']:.0f}-{hi['ro_mm']:g} mm moves Q0 by "
                  f"{lo['Q0'] / hi['Q0']:.1f}x.")
            print(f"     ⚠️ beta/VSWR are FITTED, not divided by "
                  f"q_ext_est={qe:,.0f}. Compare the Q_ext impl column against "
                  f"it: a drift means the LOOP's coupling is itself moving "
                  f"with the bore, which the Q0 ratio alone would hide.")
            print("     🔴 THE BORE IS NOT AN EM KNOB. Ordering is "
                  "slm -> residency -> LOD (user, 2026-08-25): the analysis "
                  "picks the bore and the EM copes. This measures the price.")

    # ── loop sweep: Q_ext vs UNWOUND CONDUCTOR LENGTH, and the λ/4 test ─────
    # 🔴 THE COUPLING BRANCH IS NOT OPTIONAL HERE, AND IT HAS BITTEN TWICE.
    # `fit` returns the UNDERCOUPLED root beta_u = (1-|S11|)/(1+|S11|). The
    # overcoupled root is its reciprocal, and |S11| ALONE CANNOT TELL THEM
    # APART — both roots give a shallow dip. These cold barrel cases are
    # strongly OVERcoupled, so the printed beta and the Q0 derived from it are
    # the wrong root; reading them as Q0 produced 359 and 1,325 and a false
    # "the rig is broken" alarm on a healthy run.
    #
    # 🔑 THE DISCRIMINATOR IS EXTERNAL, not a preference: with no plasma, Q0
    # MUST be the cavity's own cold Q0. The two roots differ by ~30x here, so
    # the choice is unambiguous even though Q_REF is a CAP-loop reference and
    # this is a barrel loop (that difference is percent, not decades).
    #
    # 🔑 AND Q_ext IS ROBUST ON EITHER ROOT:  Q_ext = Q0/beta = Q_L*(1+beta_u)
    # on the overcoupled root — Q_L to within a few percent. It barely uses the
    # ill-conditioned beta at all. Q0 is the fragile number here, NOT Q_ext,
    # which is why this table reports Q_ext as the measurement and Q0 as the
    # branch check. VSWR is branch-INVARIANT and is printed as a third witness.
    if _axis_now == "loop":
        pts = sorted((q for q in out["points"] if q.get("wide_fit")),
                     key=lambda q: q["ld_mm"])
        if len(pts) >= 2:
            print(f"\n  {'ld mm':>7}{'L_unwound':>11}{'L/(λ/4)':>10}"
                  f"{'Q_L':>8}{'VSWR':>8}{'Q_ext':>9}{'Q0 sel':>9}  branch")
            rows = []
            for q in pts:
                w = q["wide_fit"]
                qL, b_u = w["Q_L"], w["beta"]
                # unwound conductor: two radial legs of ld, plus the crossbar
                # (2*lw less the PORT gap), less the SERIES gap that breaks one
                # leg. Derived from the meshed geometry, not a quoted literal.
                Lc = (2.0 * q["ld_mm"] + (2.0 * q["lw_mm"] - q["loop_gap_mm"])
                      - q["loop_gap2_mm"])
                quarter = (299.792458 / w["f0"]) / 4.0     # mm, at THIS case's f0
                s11 = abs((b_u - 1.0) / (b_u + 1.0))
                vswr = (1 + s11) / (1 - s11)
                br = resolve_branch(w, q["ne"])
                if not br["resolved"]:
                    print(f"  {q['ld_mm']:>7.1f}  🔴 branch NOT resolved: "
                          f"{br['why']}")
                    continue
                over, q_ext, q0 = br["over"], br["Q_ext"], br["Q0"]
                rows.append({"ld": q["ld_mm"], "L": Lc, "q_ext": q_ext,
                             "q0": q0, "over": over})
                print(f"  {q['ld_mm']:>7.1f}{Lc:>11.2f}{Lc / quarter:>10.3f}"
                      f"{qL:>8.0f}{vswr:>8.1f}{q_ext:>9,.0f}{q0:>9,.0f}"
                      f"  {'OVER' if over else 'under'}coupled")
            print(f"     λ/4 = {(299.792458 / pts[0]['wide_fit']['f0']) / 4.0:.2f} mm"
                  f" · branch chosen by |ln(Q0/Q_ref)|, Q_ref = {Q_REF:,.0f}")

            # 🔴 THE FALSIFIERS THE CONFIG DECLARED. They were stated in the run
            # config's `falsification` field and existed NOWHERE IN THE CODE,
            # so the rig could not answer the question it was launched to ask.
            # §8b: the solve can succeed completely and the CONCLUSION still be
            # lost, because nothing in the rig was built to receive it.
            qs = [r["q_ext"] for r in rows]
            lo_i = qs.index(min(qs))
            spread = max(qs) / min(qs)
            mono = all(b <= a for a, b in zip(qs, qs[1:])) or \
                   all(b >= a for a, b in zip(qs, qs[1:]))
            print(f"\n  Q_ext spans {min(qs):,.0f}-{max(qs):,.0f} = "
                  f"{spread:.1f}x across L = {rows[0]['L']:.1f}-"
                  f"{rows[-1]['L']:.1f} mm")
            if spread < 1.5:
                print("  🔴 F-FLAT FIRES — Q_ext is flat across the whole span. "
                      "Conductor length is\n"
                      "     NOT the mechanism, and λ/4 AND the area/capacitance "
                      "story fail TOGETHER.")
            elif 0 < lo_i < len(qs) - 1:
                print(f"  ✅ λ/4 SUPPORTED — Q_ext has an INTERIOR MINIMUM at "
                      f"ld = {rows[lo_i]['ld']:g} mm,\n"
                      f"     L = {rows[lo_i]['L']:.2f} mm = "
                      f"{rows[lo_i]['L'] / ((299.792458 / pts[lo_i]['wide_fit']['f0']) / 4.0):.3f} λ/4."
                      f" A capacitance/area picture predicts no turn.")
            elif mono:
                print("  🔴 λ/4 NOT SUPPORTED on this span — Q_ext is MONOTONIC "
                      "and never turns.\n"
                      "     The area/capacitance story survives. ⚠️ A minimum "
                      "OUTSIDE the swept range\n"
                      "     is not excluded; state the span, not a universal.")
            else:
                print("  🔴 NEITHER — Q_ext is neither flat, monotonic, nor "
                      "singly-minimal.\n"
                      "     Do not fit a story to it; report the points.")
            print("  ⚠️ SLICE: cold (ne=0), barrel mount, "
                  f"lw={pts[0]['lw_mm']:g} mm, port gap="
                  f"{pts[0]['loop_gap_mm']:g} mm, series gap="
                  f"{pts[0]['loop_gap2_mm']:g} mm, bore {RI:g}-{RO:g} mm. "
                  "Q_ext is COLD and geometric;\n"
                  "     beta at any density is arithmetic on Q0(n_e)/Q_ext.")

    es = [p["eta"] for p in out["points"] if p.get("eta") is not None]
    if len(es) >= 2 and out.get("sweep_axis") != "annulus":
        print(f"\n  eta spans {min(es):.4f}-{max(es):.4f} across ne "
              f"{min(P):.0e}-{max(P):.0e} — absorption stays above "
              f"{100*min(es):.1f}% over {math.log10(max(P)/min(P)):.0f} decades.")
    print(f"\n  wrote {S.outfile(SLUG, 'result.json')}")


if __name__ == "__main__":
    main()
