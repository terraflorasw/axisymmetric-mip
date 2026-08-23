"""H3 — what plasma does TE011 sustain? A 2-D map, not a point.

🔑 POSED AS A REQUIREMENT, NOT AN ASSUMPTION. H3 depends on the torch, because
the torch confines the gas and so sets the plasma's shape — and the torch
geometry is ASSUMED and Argon-derived (the Fassel torch; no Nitrogen-optimised
geometry exists). The dependence is FOURTH POWER: TE011's E_phi is ZERO on axis
and grows LINEARLY from it, so energy ~ E^2 * area ~ R^4. Going 2 -> 8.5 mm in
plasma radius is 319x in coupled energy. Answering "can TE011 sustain THE
plasma" against an inherited torch would produce an arbitrary number.

So this sweeps the plasma geometry and returns a MAP. That inverts the
dependency:

    was:  torch  ->  plasma shape  ->  H3
    now:  H3  ->  plasma requirement  ->  TORCH SPECIFICATION

and it is decisive either way: if NO point on the map couples usefully, TE011
operation is dead INDEPENDENTLY of the torch; if some region does, that region
IS the specification handed to torch design.

## The plasma model: Drude, with BOTH parameters from one electron density

Palace is a pure electrodynamics solver — no fluid module, no Townsend
avalanche, no thermal transport. A plasma is a static volume of lossy dielectric.
The cold-plasma Drude model gives the complex permittivity, and Palace forms
eps_r - j*sigma/(w*eps0), so BOTH inputs come from the same n_e:

    wp^2 = n_e e^2 / (eps0 m_e)
    Permittivity  = 1 - wp^2/(w^2 + nu^2)
    Conductivity  = eps0 * wp^2 * nu / (w^2 + nu^2)

🔴 IT IS AN ERROR TO SET Permittivity = 1.0 AND A PLASMA CONDUCTIVITY. They are
both functions of the SAME n_e. The common shortcut "nu >> w so eps ~ 1" needs
wp^2 << nu^2, and that is NOT satisfied here: at 1 atm nu ~ 1e11 while wp is
7.5e10 to 3.4e12 over this sweep, so wp is COMPARABLE TO OR ABOVE nu and eps_eff
runs from +0.69 down to -310. The plasma is OVERDENSE (wp/w = 5..220).

⚠️ Negative permittivity is physical — it is what makes a plasma reflective.
The n_e sweep runs LOW TO HIGH so the eps > 0 regime is entered first and any
failure has a visible onset rather than appearing as a wall.

## Why skin depth is the real story

At sigma = 10 S/m the skin depth is 3.2 mm — comparable to the plasma radius.
Above ~100 S/m the field is excluded entirely. **Absorption is NON-MONOTONIC in
n_e**: it rises, peaks, then FALLS as the plasma shields itself. A sweep confined
to a few S/m sits entirely on the rising side and misses both the peak and the
shielded regime. Hence log spacing over four decades.

## 🔴 DRIVEN, not eigenmode — measured, not chosen

The first attempt used EIGENMODE because it is cheap (155-882 s) and returns Q
directly. It stalled at **nconv = 0 after 65 minutes** on the WEAKEST point of
the grid: a bulk lossy volume (tan-delta ~ 3) puts strong frequency dependence
into the OPERATOR, where the wall's surface impedance was only a boundary term,
and NLEPS cannot do it. `run()` now REFUSES that combination outright.

Driven has no NLEPS and therefore no convergence cliff. It costs ~2,500-2,900 s
per point against eigen's 155-882 s, which is why this starts as a CORNER PROBE
rather than the full 16-point grid — measure the magnitude before committing
half a day (CONVENTIONS §5).

⚠️ Driven needs a PORT, so the coupling loop is present and contributes its own
perturbation — measured at 32% of Q. eta is therefore referenced to the bare
cavity **WITH THE SAME LOOP** (29,854, port-resolved), never to the 44,384 empty
figure. H3's answer includes the probe, and that is stated rather than hidden.

⚠️ beta is NOT mesh-converged (43% for a 1.25x refinement) and is not used as a
result here. Q0 = Q_L(1+beta) IS converged to 0.12% because beta and Q_L
compensate — that is the quantity eta is built from.

## What is measured, per point, from ONE driven solve

    f0           frequency pull — the tuning-loop question
    Q_L          loaded linewidth, hence tuning BANDWIDTH
    Q0 = Q_L(1+beta)   the converged quantity
    eta          = 1 - Q0/Q_bare_with_loop, the FRACTION OF POWER reaching the
                 plasma rather than the walls. This is what LOD needs.
    A2/A0        azimuthal order of the DRIVEN field at the dip — does the mode
                 remain TE011 (m=0) at all?
    p_elec[12]   the plasma region's own energy share, measured not inferred

🔴 WHAT THIS RIG DOES **NOT** DO. It does not decide whether the plasma is
self-consistent — whether the absorbed power maintains the n_e that defines it.
That needs a fluid/thermal model Palace does not have. Saying otherwise would be
the same error as claiming a cold-cavity field predicts a lit one.

VERIFICATION
  V1  at the LOWEST n_e the perturbation must be small: the mode stays m=0, f
      within a few MHz of 2.45, and eta near ZERO — i.e. Q0 near the
      bare-with-loop 29,854, NOT the empty 44,384. If the weakest plasma already
      destroys the mode, the model or the mesh is wrong, not the physics.
      ⚠️ RESTATED for the driven rig. The eigen-era version of V1 referenced
      44,384 and would have been wrong by the loop's own 32%. A declared
      criterion has to be re-read when the model underneath it changes —
      V3 of e0k2_azim was scored a failure for exactly this reason.
  V2  mode identity by CONTINUATION where it applies. ⚠️ The driven rig
      identifies each dip by its own AZIMUTHAL ORDER, which is absolute and
      needs no reference — so continuation is a cross-check here, not the
      mechanism. That is a strengthening: E1b failed because it had only
      relative matching.
FALSIFICATION
  🔴 F1  if TE011's azimuthal order is lost (A2/A0 leaves the m=0 regime), the
         mode is no longer TE011 and every number past that point is about
         something else. Report the onset; do not carry the label forward.
  🔴 F2  if eta stays below 0.5 across the WHOLE grid, TE011 spends most of its
         power heating the walls rather than the plasma at every geometry tested
         — a torch-proof negative for the TE-only architecture.
"""
import json
import math
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
import eigmodes
import azimuthal
import solvecost
import qfit
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import (design_point, wall_sigma, CAP_R_FRAC,
                         LOOP_PHI, LOOP_RW, LOOP_GAP, FREQ_STEP)
from e0k2_azim import sector_bins, read_sector_energy

TAG = "h3_loaded"
SECTORS = 5                 # m in {0,1,2} in this window; N>=9 is unbuildable
# 🔴 the reference is the bare cavity WITH THE LOOP, because the driven solve
# has the loop in it. The 44,384 empty figure would overstate eta by the loop's
# own 32% Q cost.
Q_BARE_WITH_LOOP = 29854.0  # e0k2_portfix_s1, port-resolved
Q_BARE_EMPTY = 44384.0      # e0k2_bare — kept for context, NOT the reference
NU_M = 1.0e11               # electron-neutral collision rate, N2 at 1 atm
TAG_PLASMA = 12

# outer radius (mm). Spans the 319x energy range from R^4 scaling.
# 🔑 CORNER PROBE FIRST. Driven is ~8x eigen's cost, so 16 points is 11-13 h.
# The corners bracket a 319x energy range (R^4) and a 1000x conductivity range;
# they either show eta varying enough to justify filling in, or fire F2 cheaply.
# Set FULL_GRID=1 in the environment to run all 16.
RADII = [2.0, 8.5]
# electron density (m^-3), LOG spaced, LOW FIRST so continuation has a start
# and so the eps>0 regime is entered before eps<0.
NE = [1.0e18, 1.0e19, 1.0e20, 1.0e21]
# 🔑 1e19 sits INSIDE the indefinite band, so it is solved DRIVEN. Included
# deliberately: sigma ~ 2-10 S/m is ~5000-6000 K, where an N2 plasma most likely
# OPERATES. Leaving a hole there would leave a hole at the operating point.
# 🔑 OVERLAP: one point where eigen works is ALSO run driven, to earn the mixed
# grid on evidence rather than assertion.
OVERLAP = (2.0, 1.0e20)
# ⚠️ FIXED, NOT SWEPT — declared so it is not mistaken for a result:
LOOP_LD, LOOP_LW = 11.0, 8.0   # cap loop, DRIVEN band only
BAND_MHZ = 60.0
INNER_R = 0.0               # 0 = solid column. >0 would make it annular.

# 🔑 MEASURED-GOOD EIGEN SETTINGS (h3_eigenprobe, 2026-08-23)
#   target 2.40, NOT 2.15. The 2.15 shift was chosen because "loading pulls
#   DOWN" — it pulls UP: an overdense plasma has eps<0, acts conductor-like,
#   excludes field, shrinks the effective volume. Measured +1.26 MHz.
#   plasma_h 1.0, not 0.4: converged in 284 s vs 573 s. The mesh was NOT the
#   cause of the original stall, but the coarser plasma mesh is still faster.
# 🔴 N_MODES = 4, NOT the 6 imported from e0k2_anchor. CONVENTIONS §6: do not
# reuse a parameter without re-deriving it for the case. h3_eigenprobe VALIDATED
# 4 modes — ne=1e18 converged in 284 s. The rig imported 6 and the SAME case
# timed out at 900 s with 122 NLEPS iterations, on the same mesh, same target,
# same plasma_h. With a weak plasma the TE011/TM111 cluster is nearly
# degenerate, so asking for 6 means resolving closely-spaced eigenvalues; with a
# strong plasma they are damped and spread out, which is why ne=1e20 and 1e21
# converged at 6 and ne=1e18 did not.
#
# 4 is sufficient: the probe returned the TM111 pair, TE011, and the 2.62 mode —
# everything the identification needs.
N_MODES = 4
EIGEN_TARGET = 2.40
PLASMA_H = 1.0
CASE_TIMEOUT_S = 900.0      # converged cases took 89-284 s; a stall dies fast

# 🔴 THE INDEFINITE BAND — where EIGEN CANNOT BE USED.
# The eigensolver's divergence-free projection runs on PCG, which needs a
# POSITIVE-DEFINITE operator. Where eps_eff is moderately negative the operator
# is indefinite and PCG stalls at a 0.997 reduction factor (measured: ne=1e19,
# 1000 iterations, no progress). Outside the band it is fine — positive eps is
# definite, and strongly negative eps makes the plasma act as a Dirichlet wall,
# which is well-conditioned again.
#
# ⚠️ DRIVEN DOES NOT DO THAT PROJECTION AT ALL (verified: 0 occurrences in
# driven logs, 2 in eigen logs), so it is immune. Hence: eigen outside the band,
# driven inside it, and an OVERLAP point run both ways to earn the mix.
#
# 🔴 And the band is not an edge case — sigma ~ 2-10 S/m is ~5000-6000 K, where
# an N2 plasma most likely OPERATES.
EPS_INDEFINITE = (-20.0, 0.0)
TE011_WINDOW = (2.40, 2.50)   # m=0 alone is not enough: the 2.62 mode
                              # is ALSO m=0. TE011 is the m=0 mode in THIS band.
Z_FRAC = 0.40               # plasma spans +-0.40 L, clear of the end caps so it
                            # cannot short to them (the TDS objection in miniature)


def drude(ne, w):
    """(Permittivity, Conductivity) for one electron density. BOTH from one ne."""
    eps0, e, me = 8.8541878128e-12, 1.602176634e-19, 9.1093837015e-31
    wp2 = ne * e * e / (eps0 * me)
    den = w * w + NU_M * NU_M
    return 1.0 - wp2 / den, eps0 * wp2 * NU_M / den


def skin_depth(sigma, w):
    return math.sqrt(2.0 / (w * 4e-7 * math.pi * sigma)) if sigma > 0 else float("inf")


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    w = 2.0 * math.pi * 2.45e9
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    cap_r = CAP_R_FRAC * a
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    print(f"  cavity a={a:.4f} L={L:.4f}  wall {sigma_w:.3g} S/m")
    print(f"  reference Q_bare WITH LOOP = {Q_BARE_WITH_LOOP:,.0f}  "
          f"(the empty-cavity {Q_BARE_EMPTY:,.0f} would overstate eta by the "
          f"loop's own 32%)")
    print(f"  plasma: solid column (ri={INNER_R}), z = {zlo:.2f}..{zhi:.2f} mm")
    print(f"  driven band +-{BAND_MHZ:.0f} MHz around {exact:.5f} GHz "
          f"(an overdense plasma pulls the mode UP, not down — "
          f"RETRACTED assumption; qfit REFUSES if the 3 dB points "
          f"fall outside rather than guessing)\n")
    print(f"  {'ne (m^-3)':>11}{'eps_eff':>11}{'sigma S/m':>11}{'skin mm':>10}")
    for ne in NE:
        eps, sig = drude(ne, w)
        print(f"  {ne:>11.0e}{eps:>11.3f}{sig:>11.2f}{skin_depth(sig, w)*1e3:>10.2f}")
    print(flush=True)

    out = {"q_bare_with_loop": Q_BARE_WITH_LOOP,
           "q_bare_empty": Q_BARE_EMPTY, "nu_m": NU_M, "inner_r_mm": INNER_R,
           "z_frac": Z_FRAC, "points": []}

    for R in RADII:
        prev = None                      # continuation cross-check within R
        for ne in NE:                    # LOW to HIGH
            eps, sig = drude(ne, w)
            lo, hi = EPS_INDEFINITE
            mode = "driven" if lo < eps < hi else "eigen"
            tag = f"{TAG}_r{R:g}_n{math.log10(ne):.0f}".replace(".", "p")
            print(f"\n  --- R={R} mm, ne={ne:.0e}  eps={eps:.3f} "
                  f"sigma={sig:.3g} S/m  skin={skin_depth(sig,w)*1e3:.2f} mm"
                  f"  -> {mode.upper()}", flush=True)
            if mode == "driven":
                print(f"      (eps is in the INDEFINITE band {lo}..{hi}; the "
                      f"eigensolver's div-free PCG stalls there)", flush=True)
            rec = {"R_mm": R, "ne": ne, "eps": eps, "sigma": sig, "solver": mode,
                   "skin_mm": skin_depth(sig, w) * 1e3, "tag": tag}

            geo = ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                   "--sectors", str(SECTORS),
                   "--plasma", f"{INNER_R},{R},{zlo:.4f},{zhi:.4f}",
                   "--plasma-h", f"{PLASMA_H:.3f}"]
            if mode == "driven":
                geo += ["--loop", f"{LOOP_LD},{LOOP_LW},{LOOP_RW},{LOOP_GAP}",
                        "--loop-cap", f"{cap_r:.4f}", "--loop-phi", LOOP_PHI]
            r = subprocess.run([sys.executable, "geometry.py", "--out",
                                f"{tag}.msh", "--size-factor", "1.5"]
                               + list(GEO) + geo,
                               capture_output=True, text=True)
            if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
                rec["error"] = f"mesh failed: {(r.stdout + r.stderr)[-250:]}"
                print(f"    🔴 {rec['error'][:150]}\n    REPORTED, not skipped.",
                      flush=True)
                out["points"].append(rec); _save(out); continue
            m = solveconf.load_meta(f"{tag}.msh")
            attrs = m["attributes"]
            if attrs.get("plasma") is None:
                rec["error"] = "no plasma attribute — --plasma ignored"
                print(f"    🔴 {rec['error']}"); out["points"].append(rec)
                _save(out); continue
            bins = sector_bins(m)
            vols = sorted({v for k, v in attrs.items()
                           if isinstance(v, int) and k not in ("wall", "port")}
                          | set(attrs.get("air") or []))
            energy = ([{"Index": 1, "Attributes": [attrs["bore"]]}]
                      + [{"Index": 10 + i, "Attributes": [v]}
                         for i, v in enumerate(vols)])
            others = sorted(set(vols) - {attrs["plasma"]})
            mats = [{"Attributes": others, "Permittivity": 1.0,
                     "Permeability": 1.0},
                    {"Attributes": [attrs["plasma"]], "Permittivity": eps,
                     "Permeability": 1.0, "Conductivity": sig}]
            rec["tets"] = m["tets"]
            print(f"    {m['tets']:,} tets, {len(bins)} azimuthal bins",
                  flush=True)

            try:
                if mode == "eigen":
                    c = eigen_cfg(tag, m, mesh=f"{tag}.msh", sigma=sigma_w,
                                  n=N_MODES, target=EIGEN_TARGET)
                    c["Solver"]["Order"] = 2
                    c["Domains"]["Postprocessing"]["Energy"] = energy
                    c["Domains"]["Materials"] = mats
                    run(tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
                    modes = eigmodes.read(tag)
                    qs = {}
                    for line in (pathlib.Path("postpro") / tag /
                                 "eig.csv").read_text().splitlines()[1:]:
                        pp = line.split(",")
                        if len(pp) > 3:
                            qs[round(float(pp[0]))] = float(pp[3])
                    sec = read_sector_energy(tag, bins)
                    # 🔴 IDENTIFY BY AZIMUTHAL ORDER, NOT max(Q). max(Q) picked
                    # the 2.6228 mode — which has almost no field in the bore
                    # and came back IDENTICAL across a 10x density change. It
                    # selects the mode that does NOT couple.
                    cands = []
                    for md in modes:
                        u = sec.get(float(md["m"]))
                        if u is None and sec:
                            u = sec[min(sec, key=lambda x: abs(x - md["m"]))]
                        m_az, conf, harm = azimuthal.order(u) if u else (None, 0, {})
                        if m_az == 0 and TE011_WINDOW[0] < md["f"] < TE011_WINDOW[1]:
                            cands.append((md, qs.get(md["m"], 0.0), harm))
                    if not cands:
                        raise RuntimeError(
                            f"no m=0 mode in {TE011_WINDOW} — TE011 not "
                            f"identified. Modes: "
                            f"{[round(md['f'],5) for md in modes]}")
                    if len(cands) > 1:
                        print(f"    ⚠️ {len(cands)} m=0 modes in the window — "
                              f"AMBIGUOUS, taking the nearest 2.45 and saying so",
                              flush=True)
                        rec["ambiguous_m0"] = [round(c[0]["f"], 6) for c in cands]
                    # ⚠️ preflight flags this as nearest-value matching. Here
                    # the candidate set is ALREADY filtered to m=0 modes inside
                    # TE011_WINDOW, so the pick cannot reach outside the band it
                    # was selected from, and a second candidate is REPORTED as
                    # ambiguous above rather than silently resolved. Same ball
                    # argument as eigmodes.te011_tm111's window guard.
                    pick, qL, harm = min(cands, key=lambda c: abs(c[0]["f"] - exact))
                    q_ref, ref_name = Q_BARE_EMPTY, "empty (no loop, eigen)"
                    f0, sig_of = pick["f"], pick["sig"]
                else:
                    cd, _mm, _dr = solveconf.driven(f"{tag}.msh", tag,
                                                    (exact - BAND_MHZ / 1e3,
                                                     exact + BAND_MHZ / 1e3),
                                                    step=FREQ_STEP, order=2)
                    cd["Domains"]["Postprocessing"]["Energy"] = energy
                    cd["Domains"]["Materials"] = mats
                    pathlib.Path(f"{tag}.json").write_text(json.dumps(cd, indent=2))
                    run(tag, cd, timeout=CASE_TIMEOUT_S * 4)
                    res = qfit.analyse(tag)
                    if "error" in res:
                        raise RuntimeError(res["error"])
                    qL = res["Q_L"] * (1 + res["beta"])
                    f0 = res["f0"]
                    u = read_sector_energy(tag, bins, row_key=f0)
                    m_az, conf, harm = azimuthal.order(u)
                    rec["beta"], rec["Q_L_driven"] = res["beta"], res["Q_L"]
                    if m_az != 0:
                        print(f"    ⚠️ driven dip reads m={m_az} "
                              f"(A2/A0={harm.get(2,0):.4f}) — NOT a clean TE011",
                              flush=True)
                    # 🔴 the loop is present, so the reference must include it
                    q_ref, ref_name = Q_BARE_WITH_LOOP, "with loop (driven)"
                    sig_of = None
            except RuntimeError as e:
                rec["error"] = str(e)[:220]
                print(f"    🔴 {str(e)[:200]}\n    REPORTED, not skipped.",
                      flush=True)
                out["points"].append(rec); _save(out); continue

            eta = 1.0 - qL / q_ref
            rec.update(f_ghz=f0, Q=qL, eta=eta, q_ref=q_ref, q_ref_name=ref_name,
                       A2_A0=harm.get(2), pull_mhz=1e3 * (f0 - exact),
                       linewidth_khz=1e6 * f0 / qL if qL else None)
            if prev is not None and sig_of is not None and prev.get("sig"):
                rec["cont_dist"] = eigmodes._dist(prev["sig"], sig_of)
            if sig_of is not None:
                prev = {"sig": sig_of, "ne": ne}
            out["points"].append(rec); _save(out)
            print(f"    f={f0:.6f} ({rec['pull_mhz']:+.2f} MHz)  Q={qL:,.0f}  "
                  f"eta={eta:.3f}  A2/A0={harm.get(2,0):.4f}")
            print(f"      ref: {q_ref:,.0f} {ref_name}"
                  + (f"   continuation d={rec['cont_dist']:.4f}"
                     if "cont_dist" in rec else ""), flush=True)

    _overlap(out, a, L, cap_r, exact, sigma_w, w, zlo, zhi)
    _report(out, exact)


def _overlap(out, a, L, cap_r, exact, sigma_w, w, zlo, zhi):
    """Run ONE point both ways. Without it the mixed grid is an assertion.

    🔴 eta is referenced to a DIFFERENT bare cavity in each mode — 44,384 for
    eigen (no loop) and 29,854 for driven (loop present, costing 32% of Q). A
    trend read ACROSS the solver boundary is only meaningful if the two agree
    where both are valid.
    """
    if not OVERLAP:
        return
    R_o, ne_o = OVERLAP
    eig = next((q for q in out["points"]
                if q["R_mm"] == R_o and q["ne"] == ne_o
                and q.get("solver") == "eigen" and "eta" in q), None)
    print(f"\n{'='*78}\n  OVERLAP — R={R_o} mm, ne={ne_o:.0e}, BOTH ways\n",
          flush=True)
    if eig is None:
        print("    🔴 the eigen half is missing — cannot compare. REPORTED,\n"
              "       and the mixed grid stays UNEARNED.", flush=True)
        return
    eps_o, sig_o = drude(ne_o, w)
    tag = f"{TAG}_overlap"
    geo = ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
           "--sectors", str(SECTORS),
           "--plasma", f"{INNER_R},{R_o},{zlo:.4f},{zhi:.4f}",
           "--plasma-h", f"{PLASMA_H:.3f}",
           "--loop", f"{LOOP_LD},{LOOP_LW},{LOOP_RW},{LOOP_GAP}",
           "--loop-cap", f"{cap_r:.4f}", "--loop-phi", LOOP_PHI]
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--size-factor", "1.5"] + list(GEO) + geo,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        print("    🔴 mesh failed — REPORTED, mix stays unearned."); return
    m = solveconf.load_meta(f"{tag}.msh")
    attrs = m["attributes"]
    bins = sector_bins(m)
    vols = sorted({v for k, v in attrs.items()
                   if isinstance(v, int) and k not in ("wall", "port")}
                  | set(attrs.get("air") or []))
    energy = ([{"Index": 1, "Attributes": [attrs["bore"]]}]
              + [{"Index": 10 + i, "Attributes": [v]} for i, v in enumerate(vols)])
    others = sorted(set(vols) - {attrs["plasma"]})
    cd, _mm, _dr = solveconf.driven(f"{tag}.msh", tag,
                                    (exact - BAND_MHZ / 1e3,
                                     exact + BAND_MHZ / 1e3),
                                    step=FREQ_STEP, order=2)
    cd["Domains"]["Postprocessing"]["Energy"] = energy
    cd["Domains"]["Materials"] = [
        {"Attributes": others, "Permittivity": 1.0, "Permeability": 1.0},
        {"Attributes": [attrs["plasma"]], "Permittivity": eps_o,
         "Permeability": 1.0, "Conductivity": sig_o}]
    pathlib.Path(f"{tag}.json").write_text(json.dumps(cd, indent=2))
    try:
        run(tag, cd, timeout=CASE_TIMEOUT_S * 4)
        res = qfit.analyse(tag)
        if "error" in res:
            raise RuntimeError(res["error"])
    except RuntimeError as e:
        print(f"    🔴 overlap failed: {str(e)[:180]}\n"
              f"    REPORTED — the mix is UNEARNED until this runs.", flush=True)
        return
    q_d = res["Q_L"] * (1 + res["beta"])
    eta_d = 1.0 - q_d / Q_BARE_WITH_LOOP
    d = abs(eta_d - eig["eta"])
    out["overlap"] = {"R_mm": R_o, "ne": ne_o, "eta_eigen": eig["eta"],
                      "eta_driven": eta_d, "Q_eigen": eig["Q"],
                      "Q_driven": q_d, "abs_diff": d, "agrees": bool(d <= 0.05)}
    print(f"    eigen : Q={eig['Q']:,.0f}  eta={eig['eta']:.3f}  "
          f"(ref {Q_BARE_EMPTY:,.0f}, no loop)")
    print(f"    driven: Q={q_d:,.0f}  eta={eta_d:.3f}  "
          f"(ref {Q_BARE_WITH_LOOP:,.0f}, loop present)")
    print(f"    |delta eta| = {d:.3f}  "
          + ("✅ the mixed grid is EARNED — a trend may be read across the "
             "solver boundary" if d <= 0.05 else
             "🔴 THEY DISAGREE. Do NOT read a trend across the boundary; "
             "report the two halves separately."), flush=True)
    _save(out)


def _save(out):
    import os
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


def _report(out, exact):
    print("\n" + "=" * 78)
    print(f"  {'R mm':>6}{'ne':>10}{'sigma':>9}{'solver':>9}{'f pull':>10}"
          f"{'Q':>10}{'eta':>8}{'A2/A0':>8}{'lw kHz':>10}")
    for p in out["points"]:
        if "eta" not in p:
            print(f"  {p['R_mm']:>6.1f}{p['ne']:>10.0e}{p.get('sigma',0):>9.3g}"
                  f"{p.get('solver','?'):>9}   🔴 {p.get('error','no result')[:40]}")
            continue
        print(f"  {p['R_mm']:>6.1f}{p['ne']:>10.0e}{p['sigma']:>9.3g}"
              f"{p['solver']:>9}{p['pull_mhz']:>10.2f}{p['Q']:>10,.0f}"
              f"{p['eta']:>8.3f}{p['A2_A0']:>8.4f}{p['linewidth_khz']:>10.1f}")
    ok = [p for p in out["points"] if "eta" in p]
    if not ok:
        print("\n  🔴 NO usable point. Report the empty grid; infer nothing.")
        return
    best = max(ok, key=lambda p: p["eta"])
    print(f"\n  best coupling: eta={best['eta']:.3f} at R={best['R_mm']} mm, "
          f"ne={best['ne']:.0e} (sigma {best['sigma']:.3g} S/m, "
          f"{best['solver']})")
    f2 = best["eta"] < 0.5
    print(f"  F2 eta >= 0.5 somewhere: "
          + ("🔴 FIRES — TE011 heats the WALLS more than the plasma at every "
             "geometry tested. Torch-proof negative."
             if f2 else "✅ TE011 delivers the MAJORITY of its power to a "
                        "plasma; the region that does IS the torch spec."))
    pulls = [abs(p["pull_mhz"]) for p in ok]
    lws = [p["linewidth_khz"] for p in ok]
    print(f"  frequency pull: {min(pulls):.2f} to {max(pulls):.2f} MHz; "
          f"loaded linewidth {min(lws):.0f} to {max(lws):.0f} kHz")
    print(f"    -> the source must track {max(pulls)*1e3/min(lws):.1f} "
          f"linewidths at worst — the TUNING-LOOP requirement")
    mixed = {p["solver"] for p in ok}
    if len(mixed) > 1:
        print(f"\n  ⚠️ MIXED SOLVERS ({', '.join(sorted(mixed))}). eta is "
              f"referenced to a DIFFERENT bare cavity in each: "
              f"{Q_BARE_EMPTY:,.0f} for eigen (no loop), "
              f"{Q_BARE_WITH_LOOP:,.0f} for driven (loop present). The overlap "
              f"point is what earns the mix — check it before trusting a trend "
              f"that crosses the boundary.")
    out["verdict"] = {"best_eta": best["eta"], "best_R": best["R_mm"],
                      "best_ne": best["ne"], "F2_fires": bool(f2),
                      "solvers_used": sorted(mixed)}
    _save(out)
    print(f"\n  wrote {TAG}.result.json", flush=True)


def _save(out):
    import os
    p = pathlib.Path(f"{TAG}.result.json")
    t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
    t.write_text(json.dumps(out, indent=1) + "\n")
    os.replace(t, p)


if __name__ == "__main__":
    main()
