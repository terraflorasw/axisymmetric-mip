"""E0k2 — the absolute-Q ANCHOR, and the programme's first coupling numbers.

🔴 WHY. INSTRUMENT says "absolute Q has no external anchor — only its scaling
law. A Q number is trustworthy in ratio, not in absolute value." That limitation
is removable, and the way to remove it is to measure Q by a route that shares no
machinery with the eigenvalue: the LINEWIDTH of a driven resonance.

    eigen   Q from the imaginary part of a complex eigenvalue
    driven  Q_L from the 3 dB width of the absorbed-power curve,
            beta from the depth of the |S11| dip,  Q0 = Q_L (1 + beta)

Two routes, one mesh, one wall. If they agree, absolute Q is anchored for the
first time. If they do not, one of them has a systematic error and that is a
bigger finding than the anchor.

🔴 E0k TRIED THIS AND ALL FOUR OF ITS LEGS WERE WRONG. It is the only driven
data in the record (2 solves of 69) and:

  1. its driven solves used SILVER 6.3e7, the R110 template default, against
     baselines.json's aluminium — every Q from them ~34% high;
  2. its eigen counterpart was PEC, reporting Q ~ 2.1e9, which is noise, so it
     COULD NOT have compared Q at all — "compared only the resonant frequency"
     was forced by the configuration, not chosen;
  3. it ran a=103.70, L=88.53, D/L=2.343 — candidate A, which H1 REJECTED;
  4. its |S11| was never analysed. beta=0.0673 and Q_L=25,060 were sitting in
     postpro/e0k_drv2/port-S.csv the whole time.

Every one of those is fixed below.

🔑 MODE IDENTITY COMES FROM THE FIELD, NOT THE FREQUENCY. A driven solve returns
an |S11| dip, not a labelled mode, and TE011/TM111 are EXACTLY degenerate
(chi'01 = chi11) so the loop's ~1 MHz splitting is the only thing separating
them. Matching the dip to a mode by frequency is E1b's grave. Palace emits
p_elec/p_mag at EVERY driven frequency sample, so the driven field carries the
same energy fingerprint as an eigenmode and can be matched by SIGNATURE.
Validated on the existing E0k data: the driven field at 2.446420 matches the
eigen mode at 2.446475 with distance 0.0002, an 18.7x margin over the next mode.

⚠️ Both solves must emit the SAME energy regions in the SAME order or the
signatures are not comparable. eigen_cfg and solveconf.driven number them
differently, so this rig builds ONE list and injects it into both.

🔑 THE COUPLING BRANCH IS RESOLVED, NOT ASSUMED. |S11| alone cannot tell beta
from 1/beta — the dip depth is identical for both. The PHASE can: an overcoupled
resonance advances ~360 deg through resonance, an undercoupled one returns.
E0k's data swings 0.7 deg, so it was undercoupled, and this rig measures that
rather than assuming it.

VERIFICATION
  V1  the driven dip matches an eigen mode by signature with margin > 5x.
      Without that there is no identified mode and NO Q comparison is claimed.
  V2  beta << 1 for a diagnostic loop, and the phase test agrees with the
      branch chosen from the dip depth.
  V3  the loop must not move TE011 more than a few MHz from closed form. The
      "the loop is in both solves so it cancels" argument needs the loop to be
      a perturbation, not a redesign.
  V4  the TE011/TM111 splitting must exceed ~10 loaded linewidths, or the
      driven dip is TWO overlapping resonances and the 3 dB fit returns
      neither Q. This is why the groove is present: the pair is EXACTLY
      degenerate without it.

FALSIFICATION
  🔴 F1  Q0_driven and Q0_eigen differing by more than 20% means absolute Q is
         NOT anchored. That is the RESULT; it must not be explained away by
         adjusting the coupling model until the numbers meet.
  🔴 F2  signature margin < 5x means the loop has hybridised the degenerate
         pair. Report the failure; do not fall back to nearest-frequency.
  🔴 F3  beta > 0.5 means the loop loads the cavity heavily; Q0 = Q_L(1+beta)
         then rides on the branch choice and the anchor is not trustworthy.

⚠️ THE LOOP DIMENSIONS ARE INHERITED, and that is CONVENTIONS §6 territory:
25.8,19.4,1.5,0.3 was sized for a = 103.70 mm, where H_r peaks at
0.4805a = 49.83 mm. This cavity is a = 88.00 mm, where that radius is 42.29 mm.
The loop is NOT re-derived here — deliberately, because beta is an OUTPUT of
this rig rather than an input, and F3 fires if the inherited loop turns out to
load the cavity too hard. If F3 fires, the loop is what to change.

⚠️ WHICH mode the loop couples to is also an output. A barrel loop is not
guaranteed to pick TE011 over its degenerate TM111 partner, and with a lossy
wall Q settles it (TE011 has ~2x TM111's Q). The anchor is reported AGAINST THE
MODE IT ACTUALLY MEASURED, labelled — an anchor for TM111 is still an anchor,
but calling it TE011 would not be.

⚠️ This measures the EMPTY cavity at the H1 design point. It says nothing about
a plasma (H3) — but H3 needs exactly this rig, so it is built to be reused.
"""
import csv
import json
import math
import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import eigmodes
import values
import solveconf
import journal
from e0_solver_vs_math import GEO, eigen_cfg, run

TAG = "e0k2"
# 🔑 BOUND, NOT LITERAL (7bl). This same number lived here AND in h2_groove.py,
# while e0_solver_vs_math carried a CONTRADICTORY a/L pair as GEO's default.
DL = values.get("cavity.d_over_l")

# 🔑 CAP loop, not barrel. Both are sane placements — the barrel loop sits at
# TE011's H_z MAXIMUM, not a node (an earlier reading of this had sin and cos
# swapped; see FINDINGS 2026-08-21 RETRACTION). The cap wins because its RADIUS
# is a free continuous knob, and it links H_r at 1.39x the field the barrel sees.
# Mounted at the H_r peak r = 0.4805a, which is also a stationary point and so
# tolerance-insensitive — the same argument H1 used for D/L.
CAP_R_FRAC = values.get("loop.cap_r_frac")             # J1 peak: 1.8412 / chi'_01
LOOP_PHI = f'{values.get("loop.phi.deg"):g}'
# ⚠️ BOTH ARE TENTATIVE AND SAID SO OUT LOUD. NEXT.md item 7 records that the
# loop was forced into existence so driven solves would have a port, and that
# wire radius and port gap were NEVER CHOSEN — only area was ever swept. The
# tentative flag is the store refusing to let that pass as measured.
LOOP_RW = values.get("loop.wire_r.mm", allow_tentative=True)
LOOP_GAP = values.get("loop.gap.mm", allow_tentative=True)  # << wire radius

# (depth_mm, half_width_mm). beta ~ area^2 for a small loop; extrapolating from
# the barrel run's beta = 27.5 x 1.93 (the H_r/H_z power ratio) predicts
# 0.065 / 0.36 / 1.64 / 7.8 here.
# ⚠️ That extrapolation rests on ONE number from a run whose coupling branch was
# AMBIGUOUS, so the sweep deliberately spans ~250x in beta: being wrong by 10x
# either way still leaves a candidate in range. CONVENTIONS §11 — one point
# cannot fix a law, so do not bet a single solve on it.
CANDIDATES = [(5.0, 3.5), (7.5, 5.5), (11.0, 8.0), (16.0, 12.0)]

# 🔴 THE GROOVE IS A PRECONDITION FOR THIS MEASUREMENT, not a separate design
# question. TE011 and TM111 are EXACTLY degenerate at 2.45000 in an ungrooved
# cavity (χ′₀₁ = χ₁₁, at every D/L). The cap loop shifts the resonance only
# 0.37-0.44 MHz, so it splits the pair by well under a MHz — against measured
# linewidths of 184-306 kHz. The driven dip is then TWO OVERLAPPING RESONANCES
# and a single-Lorentzian 3 dB fit returns NEITHER Q, which is a systematic
# sitting directly on the number this rig exists to anchor.
#
# H2's validated groove moves TM111 by 64 MHz for a 0.3% cost in TE011's Q —
# 200-300 linewidths of separation for almost no perturbation to the mode being
# measured. With it in, the dip at 2.45 is unambiguously TE011.
#
# 🔑 --tag-groove costs nothing here and makes Slater's numerator
# (p_mag[groove] - p_elec[groove]) a free by-product of the same solve.
#
# ⚠️ Design variables can be separable while their MEASUREMENTS are not. These
# two are: the groove is at the cap corner (r near a), the loop at r = 0.4805a,
# and they barely interact physically — but the groove is what makes the loop's
# reading interpretable.
GROOVE_W, GROOVE_D = values.get("cavity.groove.mm")   # H2. BOUND, not copied

BETA_LO, BETA_HI = 0.1, 1.0     # the window the anchor needs
BAND_HALFWIDTH_MHZ = 40.0       # a strong loop shifts the resonance; leave room
# 🔴 5 kHz, NOT 20. At beta << 1 the loaded linewidth is ~55 kHz, and the old
# 20 kHz step put 2.8 samples across it — far too few to locate 3 dB points.
# 5 kHz gives 11. The PROM online phase is ~0.3 s regardless of grid size, so
# resolution here is nearly free; the previous value was simply inherited.
FREQ_STEP = 5e-6
N_MODES = 6
SIG_MARGIN_MIN = 5.0
# 🔴 WAS 0.5, which predates the [BETA_LO, BETA_HI] window and contradicted it:
# the rig reported "NOT anchored" for beta = 0.5598, a value inside its own
# stated target. One threshold, one place.
BETA_MAX = BETA_HI
AMBIGUOUS_DEG = 10.0    # a phase swing this close to 180 has not decided


def design_point():
    """H1's cavity, DERIVED. physics.py owns the relation; nothing is copied."""
    return ph.design_point(DL, values.get("source.f0.ghz"))


def wall_sigma():
    """🔴 BOUND FROM baselines.json, AND IT REFUSES. Substituting the template's
    silver is exactly how every absolute Q in this record became 34% high."""
    b = json.loads(pathlib.Path(__file__).with_name("baselines.json").read_text())
    # 🔑 CANONICAL NAME NOW CARRIES ITS UNIT: wall.conductivity.s_per_m.
    # A separate `unit:` field is missable, and a unit in the NAME can be wrong
    # (e0e's `delta_mhz` held GHz — a 1000x trap). values.check_units() now
    # cross-checks the two. The old name is still accepted so an in-flight run
    # cannot be broken by this rename, and it says so loudly.
    key = ("wall.conductivity.s_per_m" if "wall.conductivity.s_per_m" in b
           else "wall.conductivity")
    if key == "wall.conductivity":
        print("  ⚠️  baselines.json still uses the unit-less name "
              "'wall.conductivity'; rename it to 'wall.conductivity.s_per_m'.")
    try:
        return float(b[key]["value"])
    except (KeyError, TypeError, ValueError) as e:
        raise RuntimeError(
            f"wall.conductivity not declared in baselines.json ({e}). "
            f"Refusing to solve: an undeclared wall metal is how this "
            f"programme's absolute Q went 34% wrong once already.")


def shared_energy_list(attrs):
    """ONE definition of 'signature', used by BOTH solves.

    🔴 eigen_cfg numbers its regions 1 then 10+i; solveconf.driven uses 1 then
    2+i. Same regions, different indices and different ORDER, so the p_* columns
    would not line up and a signature comparison between the two would be
    silently meaningless. Build it once, inject it into both.
    """
    vols = sorted({v for k, v in attrs.items()
                   if isinstance(v, int) and k not in ("wall", "port")}
                  | set(attrs.get("air") or []))
    return [{"Index": 1, "Attributes": [attrs["bore"]]}] + \
           [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)]


def sig_at(tag, f_target):
    """Energy fingerprint of the DRIVEN field at the sample nearest f_target."""
    p = pathlib.Path("postpro") / tag / "domain-E.csv"
    rows = list(csv.reader(p.read_text().splitlines()))
    head = [h.strip() for h in rows[0]]
    cols = [i for i, h in enumerate(head)
            if h.startswith(("p_elec[", "p_mag["))]
    best, bd = None, float("inf")
    for r in rows[1:]:
        try:
            f = float(r[0])
        except (ValueError, IndexError):
            continue
        if abs(f - f_target) < bd:
            bd, best = abs(f - f_target), [float(r[i]) for i in cols]
    return best


def s11(tag):
    rows = list(csv.reader((pathlib.Path("postpro") / tag /
                            "port-S.csv").read_text().splitlines()))
    return [(float(r[0]), float(r[1]), float(r[2]))
            for r in rows[1:] if len(r) > 2]


def branch_from_phase(d, i0, w=60):
    """Overcoupled or undercoupled, from the PHASE — not assumed.

    An overcoupled one-port advances ~360 deg through resonance; an
    undercoupled one returns to where it started.
    """
    ph_ = [x[2] for x in d]
    un = [ph_[0]]
    for a, b in zip(ph_, ph_[1:]):
        dd = b - a
        while dd > 180:
            dd -= 360
        while dd < -180:
            dd += 360
        un.append(un[-1] + dd)
    lo, hi = max(0, i0 - w), min(len(d) - 1, i0 + w)
    swing = abs(un[hi] - un[lo])
    # 🔴 REPORT AMBIGUITY, DO NOT PICK A SIDE. The first version returned a
    # decided branch for a swing of 180.24 deg — 0.2 deg from the boundary —
    # and beta does 96.5% of the work in Q0 = Q_L(1+beta), so that 0.2 deg
    # decided almost the whole answer. |S11| cannot help: the dip depth is
    # IDENTICAL for beta and 1/beta (-0.631 dB for both 27.52 and 0.0363).
    # A measurement this close to the boundary has not resolved the branch.
    if abs(swing - 180.0) < AMBIGUOUS_DEG:
        return "AMBIGUOUS", swing
    return ("overcoupled" if swing > 180 else "undercoupled"), swing


def analyse_driven(tag):
    """f0, beta, Q_L, Q0 from the S11 curve. Returns a dict with its own workings."""
    d = s11(tag)
    i0 = min(range(len(d)), key=lambda i: d[i][1])
    f0, s0_db = d[i0][0], d[i0][1]
    S0 = 10 ** (s0_db / 20)
    branch, swing = branch_from_phase(d, i0)
    b_under, b_over = (1 - S0) / (1 + S0), (1 + S0) / (1 - S0)
    if branch == "AMBIGUOUS":
        return {"error": f"coupling branch UNRESOLVED — phase swing {swing:.2f}° "
                         f"is within {AMBIGUOUS_DEG}° of the 180° boundary, and "
                         f"|S11| is identical for beta={b_under:.4f} and "
                         f"beta={b_over:.2f}. Q0 = Q_L(1+beta) cannot be formed "
                         f"without the branch. Re-derive the loop so the "
                         f"resonance sits away from critical coupling.",
                "f0": f0, "s11_db": s0_db, "phase_swing_deg": swing,
                "beta_undercoupled": b_under, "beta_overcoupled": b_over}
    beta = b_under if branch == "undercoupled" else b_over

    # half-power points of the ABSORBED power, A = 1 - |S11|^2
    amax = 1 - S0 ** 2
    tgt = math.sqrt(max(0.0, 1 - amax / 2))

    def cross(rng):
        prev, pf = None, None
        for i in rng:
            v = 10 ** (d[i][1] / 20)
            if prev is not None and (prev - tgt) * (v - tgt) <= 0:
                # 🔴 WAS `f1 = d[i-1][0]`, WHICH IS THE WRONG BRACKET ON THE
                # DESCENDING WALK. `prev` is the value at the PREVIOUSLY VISITED
                # index — i+1 when walking down, i-1 when walking up — so
                # hardcoding i-1 straddles the wrong pair going down and places
                # the lower edge a step out. Track the previous FREQUENCY instead
                # and the bracket is right in both directions.
                # ⚠️ Verified 2026-08-25 on a synthetic resonator with a KNOWN
                # Q_L: tracking gives -0.35% at 13 samples across the width,
                # where snapping to the grid gives -6.65%.
                return (pf + (d[i][0] - pf) * ((tgt - prev) / (v - prev))
                        if v != prev else d[i][0])
            prev, pf = v, d[i][0]
        return None

    fl, fh = cross(range(i0, -1, -1)), cross(range(i0, len(d)))
    if fl is None or fh is None:
        return {"error": "3 dB points not inside the band — widen BAND, "
                         "REPORTED not guessed", "f0": f0, "s11_db": s0_db}
    ql = f0 / (fh - fl)
    return {"f0": f0, "s11_db": s0_db, "branch": branch, "phase_swing_deg": swing,
            "beta": beta, "f_lo": fl, "f_hi": fh,
            "linewidth_khz": 1e6 * (fh - fl), "Q_L": ql, "Q0": ql * (1 + beta),
            "n_samples": len(d)}


def _ckpt(path, payload):
    """Write after EVERY candidate, atomically.

    🔴 A spot reclamation killed a run mid-sweep twice on 2026-08-21. A rig that
    writes only at the end loses every completed case with it. temp + os.replace
    so an interrupt DURING the write leaves the previous complete file.
    """
    pth = pathlib.Path(path)
    tmp = pth.with_suffix(pth.suffix + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(payload, indent=1) + "\n")
    os.replace(tmp, pth)


def build_mesh(tag, a, L, ld, lw, cap_r):
    """One mesh with a CAP loop. Returns the sidecar."""
    geo = list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}"]
    loop = ["--loop", f"{ld},{lw},{LOOP_RW},{LOOP_GAP}",
            "--loop-cap", f"{cap_r:.4f}", "--loop-phi", LOOP_PHI]
    groove = (["--groove", f"{GROOVE_W},{GROOVE_D}", "--tag-groove"]
              if GROOVE_W > 0 and GROOVE_D > 0 else [])
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--size-factor", "1.5"] + geo + loop + groove,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        raise RuntimeError(f"{tag}: mesh failed — {(r.stdout + r.stderr)[-300:]}")
    return solveconf.load_meta(f"{tag}.msh")


def vacuum_check(cfgs):
    """Every domain vacuum in EVERY config, or refuse. Returns the edits made.

    🔴 eigen_cfg assigns vacuum to all volumes; solveconf.driven takes materials
    from the template and the mesh's own torch_material, which reads
    [1.0, 3.5e-05] — a vacuum permittivity paired with a LOSS TANGENT. The two
    solves would describe different cavities, differing by a loss term, on the
    very quantity this rig anchors.
    """
    changed = []
    for name, cfg in cfgs:
        for mat in cfg["Domains"]["Materials"]:
            for key, want in (("Permittivity", 1.0), ("LossTan", 0.0),
                              ("Conductivity", 0.0)):
                if key in mat and mat[key] != want:
                    changed.append((name, mat.get("Attributes"), key,
                                    mat[key], want))
                    mat[key] = want
    return changed


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma = wall_sigma()
    cap_r = CAP_R_FRAC * a
    print(f"  design point (H1, DERIVED): a={a:.4f} mm  L={L:.4f} mm  D/L={DL}")
    print(f"  wall: {sigma:.3g} S/m from baselines.json")
    print(f"  CAP loop at r = {CAP_R_FRAC} x a = {cap_r:.3f} mm "
          f"(TE011 H_r peak, J1 max)")
    print(f"  GROOVE {GROOVE_W} x {GROOVE_D} mm, TAGGED — separates the "
          f"degenerate pair so the dip is ONE mode, and gives Slater's bins free")
    EX = ph.spectrum(a, L, fmax=3.2)
    exact = EX["TE011"]
    band = (exact - BAND_HALFWIDTH_MHZ / 1e3, exact + BAND_HALFWIDTH_MHZ / 1e3)
    fmin = exact - 0.20
    print(f"  exact TE011 = TM111 = {exact:.6f} GHz (degenerate)")
    print(f"  driven band {band[0]:.4f}-{band[1]:.4f} GHz, step {FREQ_STEP*1e6:.0f} kHz")
    print(f"  TARGET: beta in [{BETA_LO}, {BETA_HI}]\n", flush=True)

    # ---------------- PHASE 1: size the loop, driven solves only -------------
    print("=" * 78)
    print("  PHASE 1 — size the loop. Driven only; no eigen solve is spent on a")
    print("  geometry that turns out to be coupled wrong.\n", flush=True)
    sized = []
    for ld, lw in CANDIDATES:
        tag = f"{TAG}_c{ld:g}x{lw:g}".replace(".", "p")
        area = 2 * ld * lw
        print(f"  --- {tag}: {ld} x {lw} mm, area {area:.0f} mm^2", flush=True)
        try:
            m = build_mesh(tag, a, L, ld, lw, cap_r)
        except RuntimeError as e:
            print(f"    🔴 {e}\n    REPORTED, not skipped.", flush=True)
            sized.append({"tag": tag, "ld": ld, "lw": lw, "area": area,
                          "error": str(e)})
            continue
        energy = shared_energy_list(m["attributes"])
        td = f"{tag}_drv"
        cd, _meta, dropped = solveconf.driven(f"{tag}.msh", td, band,
                                              step=FREQ_STEP, order=2)
        cd["Domains"]["Postprocessing"]["Energy"] = energy
        for nm, att, k, was, now in vacuum_check([("driven", cd)]):
            print(f"    🔧 {nm} {att}: {k} {was} -> {now}", flush=True)
        pathlib.Path(f"{td}.json").write_text(json.dumps(cd, indent=2))
        print(f"    {m['tets']:,} tets" + (f", dropped {dropped}" if dropped else ""),
              flush=True)
        try:
            run(td, cd)
        except RuntimeError as e:
            print(f"    🔴 solve failed: {e}\n    REPORTED, not skipped.", flush=True)
            sized.append({"tag": tag, "ld": ld, "lw": lw, "area": area,
                          "error": str(e)})
            continue
        D = analyse_driven(td)
        rec = {"tag": tag, "ld": ld, "lw": lw, "area": area, "mesh": m["tets"],
               "energy": energy, **D}
        sized.append(rec)
        if "error" in D:
            print(f"    🔴 {D['error']}", flush=True)
        else:
            print(f"    f0={D['f0']:.6f}  |S11|={D['s11_db']:.3f} dB  "
                  f"{D['branch']}  beta={D['beta']:.4f}  "
                  f"Q_L={D['Q_L']:,.0f}  linewidth {D['linewidth_khz']:.1f} kHz",
                  flush=True)
        _ckpt(f"{TAG}.sizing.json", {"candidates": sized})

    print("\n" + "=" * 78)
    print(f"  {'candidate':<20}{'area':>7}{'beta':>12}{'Q_L':>10}{'branch':>14}"
          f"{'in range':>10}")
    ok = []
    for r in sized:
        if "error" in r or "beta" not in r:
            print(f"  {r['tag']:<20}{r['area']:>7.0f}{'—':>12}{'—':>10}"
                  f"{'FAILED':>14}{'':>10}")
            continue
        good = BETA_LO <= r["beta"] <= BETA_HI
        if good:
            ok.append(r)
        print(f"  {r['tag']:<20}{r['area']:>7.0f}{r['beta']:>12.4f}"
              f"{r['Q_L']:>10,.0f}{r['branch']:>14}{'✅' if good else '':>10}")

    if not ok:
        print(f"\n  🔴 NO candidate landed in [{BETA_LO}, {BETA_HI}]. "
              f"The anchor is NOT run — a Q0 = Q_L(1+beta) built outside that "
              f"window rides on the coupling model, which is exactly what the "
              f"last attempt showed. Re-scale from the betas above: "
              f"beta ~ area^2, so area_new = area_old * sqrt(target/measured).")
        json.dump({"candidates": sized}, open(f"{TAG}.sizing.json", "w"), indent=1)
        return

    # Closest to the geometric centre of the window.
    # ⚠️ preflight flags this as nearest-value matching, correctly in spirit.
    # It is safe HERE because `ok` is already filtered to BETA_LO..BETA_HI, so
    # the pick cannot reach past the edge of the searched set — the same ball
    # argument as eigmodes.te011_tm111's window guard. If no candidate is in
    # range the function has already returned above rather than picking the
    # least-bad one, which is the failure mode the rule exists to catch.
    import math as _m
    centre = _m.sqrt(BETA_LO * BETA_HI)
    best = min(ok, key=lambda r: abs(_m.log(r["beta"] / centre)))
    print(f"\n  chosen: {best['tag']}  beta={best['beta']:.4f} "
          f"(window centre {centre:.3f})", flush=True)

    # ---------------- PHASE 2: the anchor, on the chosen mesh ----------------
    print("\n" + "=" * 78)
    print("  PHASE 2 — the anchor. Eigen on the SAME mesh, SAME wall; the driven")
    print("  solve from phase 1 is reused, not repeated.\n", flush=True)
    tag = best["tag"]
    m = solveconf.load_meta(f"{tag}.msh")
    attrs = m["attributes"]
    te = f"{tag}_eig"
    # 🔴 port_bc="pec" — GATE 4, added 2026-08-24 (CONVENTIONS §7v).
    # This rig wants the UNLOADED Q, so the port must not be a loss
    # channel. Shorting the gap makes the loop a small closed ring
    # resonant far above the band: TE011 is left essentially
    # unperturbed (P=0.9997) and Q excludes port loss.
    # ⚠️ UNASSIGNED IS PMC — an OPEN gap, which is an LC resonator
    # near 2.45 GHz that HYBRIDISES TE011 into a pair. Everything
    # this rig produced before today was measured that way.
    ce = eigen_cfg(te, m, mesh=f"{tag}.msh", sigma=sigma, n=N_MODES,
                   target=fmin, port_bc="pec")
    ce["Solver"]["Order"] = 2
    ce["Domains"]["Postprocessing"]["Energy"] = best["energy"]
    ce["Boundaries"]["PEC"] = {"Attributes": [attrs["port"]]}   # loop shorted
    for nm, att, k, was, now in vacuum_check([("eigen", ce)]):
        print(f"    🔧 {nm} {att}: {k} {was} -> {now}", flush=True)
    run(te, ce)

    modes = eigmodes.read(te)
    qs = {}
    for line in (pathlib.Path("postpro") / te / "eig.csv").read_text().splitlines()[1:]:
        p_ = line.split(",")
        if len(p_) > 3:
            qs[round(float(p_[0]))] = float(p_[3])
    print(f"    {len(modes)} modes:", flush=True)
    for md in modes:
        print(f"      f={md['f']:.6f}  Q={qs.get(md['m'], 0):,.0f}", flush=True)

    D = {k: v for k, v in best.items() if k not in ("energy",)}
    out = {"design": {"a_mm": a, "L_mm": L, "dl": DL, "sigma": sigma,
                      "cap_r_mm": cap_r, "exact_te011": exact},
           "sizing": [{k: v for k, v in r.items() if k != "energy"}
                      for r in sized],
           "chosen": tag, "driven": D,
           "eigen": [{"m": md["m"], "f": md["f"], "Q": qs.get(md["m"])}
                     for md in modes]}

    # identify the driven dip BY SIGNATURE
    dsig = sig_at(f"{tag}_drv", D["f0"])
    scored = sorted(((eigmodes._dist(dsig, md["sig"]), md) for md in modes),
                    key=lambda x: x[0])
    d0, bestmode = scored[0]
    margin = (scored[1][0] / d0) if len(scored) > 1 and d0 > 0 else float("inf")
    out["identification"] = {"distance": d0, "margin": margin,
                             "ranked": [[round(x[0], 5), x[1]["f"]] for x in scored]}
    print(f"\n  IDENTIFICATION by signature (not frequency):")
    for dist, md in scored:
        print(f"    f={md['f']:.6f}  Q={qs.get(md['m'],0):>10,.0f}  d={dist:.5f}"
              + ("   <-- driven dip" if md is bestmode else ""))
    print(f"    margin over next {margin:.1f}x (V1 needs > {SIG_MARGIN_MIN})",
          flush=True)
    if margin < SIG_MARGIN_MIN:
        print(f"\n  🔴 F2 FIRES: margin {margin:.1f}x < {SIG_MARGIN_MIN}. NO Q "
              f"comparison is claimed, and this does NOT fall back to "
              f"nearest-frequency.")
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
        return

    fs = [md["f"] for md in modes]
    qlist = [qs.get(md["m"], 0.0) for md in modes]
    pair = eigmodes.te011_tm111(fs, exact, qlist, fmin=fmin)
    label = "unidentified"
    if pair:
        if abs(bestmode["f"] - pair["te011"]) < 1e-9:
            label = "TE011"
        elif bestmode["f"] in [fs[i] for i in pair["tm111_indices"]]:
            label = "TM111 (one polarisation)"
        out["pair"] = {k: v for k, v in pair.items() if k != "triplet"}
        print(f"\n  degenerate pair by Q: TE011={pair['te011']:.6f}  "
              f"TM111={pair['tm111']:.6f}  (how={pair['how']})")
        # 🔑 the identification's OWN falsifier, H1's: TE011 must out-Q TM111
        i_te = pair["te011_index"]
        q_te = qlist[i_te]
        q_tm = sum(qlist[i] for i in pair["tm111_indices"]) / 2.0
        okq = q_te > q_tm
        print(f"    falsifier TE011 Q > TM111 Q: {q_te:,.0f} vs {q_tm:,.0f} "
              + ("✅" if okq else "🔴 INVERTED — the labelling is not trustworthy"))
        out["pair"]["falsifier_te011_outQs_tm111"] = bool(okq)
        if not okq:
            label += " [LABEL SUSPECT: Q inversion]"
    else:
        print(f"\n  ⚠️ te011_tm111 REFUSED — pair not resolvable in this window.")
    out["identification"]["mode_label"] = label
    print(f"  the loop coupled to: {label}", flush=True)

    qe = qs.get(bestmode["m"])
    ratio = D["Q0"] / qe if qe else None
    out["anchor"] = {"Q0_driven": D["Q0"], "Q0_eigen": qe, "ratio": ratio,
                     "beta": D["beta"], "Q_L": D["Q_L"]}
    print(f"\n  {'='*70}\n  THE ANCHOR")
    print(f"    Q0 from the driven LINEWIDTH : {D['Q0']:>12,.0f}")
    print(f"    Q0 from the EIGENVALUE       : {qe:>12,.0f}")
    print(f"    ...for mode                  : {label:>12}")
    print(f"    ratio driven/eigen           : {ratio:>12.3f}")
    print(f"    beta                         : {D['beta']:>12.4f}")
    print(f"    beta's share of Q0           : {100*(1-1/(1+D['beta'])):>11.1f}%")

    print(f"\n  DECLARED CRITERIA")
    # V4 — is the dip ONE mode? Ask the eigen solve for the actual splitting
    # and compare it with the loaded linewidth the driven fit assumed.
    v4_ok, sep_lw = None, None
    if pair:
        sep_mhz = abs(pair["te011"] - pair["tm111"]) * 1e3
        sep_lw = sep_mhz * 1e3 / D["linewidth_khz"]
        v4_ok = sep_lw >= 10.0
        out["blend"] = {"splitting_mhz": sep_mhz, "linewidths": sep_lw,
                        "resolved": bool(v4_ok)}
        print(f"    V4 TE011/TM111 splitting {sep_mhz:.3f} MHz = "
              f"{sep_lw:.1f} loaded linewidths "
              + ("✅ the dip is ONE mode" if v4_ok else
                 "🔴 OVERLAPPING — the 3 dB fit returns neither Q, and the "
                 "anchor below is contaminated"))
    else:
        print(f"    V4 splitting UNKNOWN — the pair was not resolvable, so "
              f"whether the dip is one mode is not established")
    v3 = abs(1e3 * (bestmode["f"] - exact))
    print(f"    V3 loop perturbation: {v3:.2f} MHz "
          + ("✅" if v3 < 5 else "🔴 the loop is a redesign, not a perturbation"))
    # V5 — what does the PROBE cost in Q? Frequency perturbation (V3) says
    # nothing about it: f is a volume integral, Q is a surface-current one, and
    # an obstacle at a current maximum can be negligible in the first and
    # dominant in the second. Measured by subtraction against a loop-free solve.
    bare = pathlib.Path(f"{TAG}_bare.result.json")
    if bare.exists():
        qb = json.loads(bare.read_text()).get("q_te011")
        if qb:
            cost = 1.0 - qe / qb
            out["v5"] = {"q_bare": qb, "q_with_loop": qe, "q_cost_frac": cost}
            print(f"    V5 loop Q cost: {qe:,.0f} vs bare {qb:,.0f} = "
                  f"{100*cost:+.1f}% "
                  + ("✅ the probe is weak in Q too" if abs(cost) < 0.10 else
                     "🔴 the probe DOMINATES Q — this anchors cavity+loop, "
                     "not the design cavity"))
    else:
        print(f"    V5 loop Q cost: UNKNOWN — no {TAG}_bare.result.json. "
              f"Run e0k2_bare.py; do NOT assume the probe is free.")
    print(f"    V2 beta={D['beta']:.4f} {'✅' if D['beta'] <= BETA_MAX else '⚠️ above BETA_MAX'}"
          f"  branch={D['branch']} by phase (swing {D['phase_swing_deg']:.1f}°)")
    agree = ratio is not None and abs(ratio - 1) <= 0.20
    print(f"    F1 |ratio-1| = {abs(ratio-1):.1%} "
          + ("✅ two independent routes agree" if agree else
             "🔴 F1 FIRES: the routes DISAGREE. Do not adjust the coupling "
             "model to close it."))
    v5_ok = out.get("v5", {}).get("q_cost_frac")
    v5_ok = (abs(v5_ok) < 0.10) if v5_ok is not None else False
    out["verdict"] = {"anchored": bool(agree and v3 < 5 and D["beta"] <= BETA_MAX
                                       and v4_ok and v5_ok),
                      "v5_measured": "v5" in out,
                      "loop_shift_mhz": v3, "F1_agree": bool(agree)}
    if out["verdict"]["anchored"]:
        print(f"\n  ✅ ABSOLUTE Q IS ANCHORED: {qe:,.0f} for {label}, confirmed "
              f"by an independent linewidth measurement to {abs(ratio-1):.1%}.")
    else:
        print(f"\n  ⚠️ NOT anchored: F1 agreeing is necessary but not sufficient "
              f"— V3 and the beta window must hold too, or the number describes "
              f"a cavity dominated by its own probe.")
    journal.log(TAG, event="anchor", **out["anchor"])
    json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
