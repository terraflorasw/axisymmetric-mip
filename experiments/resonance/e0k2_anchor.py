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
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import eigmodes
import solveconf
import journal
from e0_solver_vs_math import GEO, eigen_cfg, run

TAG = "e0k2"
DL = 1.525                      # H1's answer. Not a hardcoded a/L pair.
LOOP = ["--loop", "25.8,19.4,1.5,0.3", "--loop-phi", "36"]
BAND_HALFWIDTH_MHZ = 20.0       # wide enough for the wings at Q ~ 4e4
N_MODES = 6
SIG_MARGIN_MIN = 5.0
BETA_MAX = 0.5
AMBIGUOUS_DEG = 10.0    # a phase swing this close to 180 has not decided


def design_point():
    """H1's cavity, DERIVED. physics.py owns the relation; nothing is copied."""
    from scipy.optimize import brentq
    L = brentq(lambda L: ph.f_mnp("TE", 0, 1, 1, DL * L / 2, L) - 2.45,
               20.0, 400.0, xtol=1e-10)
    return DL * L / 2, L


def wall_sigma():
    """🔴 BOUND FROM baselines.json, AND IT REFUSES. Substituting the template's
    silver is exactly how every absolute Q in this record became 34% high."""
    b = json.loads(pathlib.Path(__file__).with_name("baselines.json").read_text())
    try:
        return float(b["wall.conductivity"]["value"])
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
        prev = None
        for i in rng:
            v = 10 ** (d[i][1] / 20)
            if prev is not None and (prev - tgt) * (v - tgt) <= 0:
                f1, f2 = d[i - 1 if i > 0 else 0][0], d[i][0]
                return f1 + (tgt - prev) * (f2 - f1) / (v - prev) if v != prev else f2
            prev = v
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


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma = wall_sigma()
    print(f"  design point (H1, DERIVED): a={a:.4f} mm  L={L:.4f} mm  D/L={DL}")
    print(f"  wall: {sigma:.3g} S/m from baselines.json", flush=True)

    # 🔴 START FROM GEO, DO NOT HAND-ROLL THE FLAG LIST. The first version of
    # this rig passed only --radius/--length/--order and got the DEFAULTS for
    # everything else: 5 sectors, a torch (attr 2), the inner tubes, and every
    # aperture live. That is CONVENTIONS §12 — "apertures default ON, gate them
    # explicitly" — and it produced a non-manifold mesh that Palace rejected
    # ("Interior triangular face found connecting elements 39859, 40152 and
    # 40153") 2 s into the solve. It would ALSO have measured a loaded cavity
    # while claiming to anchor the empty one.
    #
    # GEO gates all of it and is what every E0/H1 rig uses. Later flags win in
    # argparse, so appending --radius/--length overrides GEO's own values —
    # the same pattern as h2b's build().
    geo = list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}"]
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{TAG}.msh",
                        "--size-factor", "1.5"] + geo + LOOP,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{TAG}.msh").exists():
        sys.exit(f"mesh failed: {(r.stdout + r.stderr)[-300:]}")
    m = solveconf.load_meta(f"{TAG}.msh")
    attrs = m["attributes"]
    energy = shared_energy_list(attrs)
    print(f"  ONE mesh: {m['tets']:,} tets, {m.get('sectors')} sector(s), "
          f"port attr {attrs.get('port')}, {len(energy)} energy regions "
          f"shared by both solves")
    # 🔴 DO NOT ASK THE ATTRIBUTE TABLE WHETHER THE CAVITY IS EMPTY. attrs
    # carries reserved attribute IDs — `torch: 2` is present whether or not a
    # torch was built, so a guard keyed on it refuses a perfectly empty mesh.
    # That is CONVENTIONS §1 with the proxy one level down from the last one.
    # The direct question is asked of the CONFIG, below, once both exist:
    # what permittivity and what loss does each domain actually get?
    g = m.get("geometry_mm") or {}
    print(f"  apertures (0 = off): viewport={g.get('viewport')}  "
          f"trap={g.get('trap')}  groove={g.get('groove')}  "
          f"torch_ext={g.get('torch_ext')}")
    print(f"  torch_material (eps, tan-delta): {g.get('torch_material')}\n",
          flush=True)

    EX = ph.spectrum(a, L, fmax=3.2)
    exact = EX["TE011"]
    # target BELOW the pair so the degenerate pair is inside the window with
    # room underneath — and declare that floor to te011_tm111.
    fmin = exact - 0.20
    print(f"  exact TE011 = TM111 = {exact:.6f} GHz (degenerate)")
    print(f"  eigen window floor {fmin:.4f} GHz\n", flush=True)

    # ---- eigen, LOSSY WALL (E0k's was PEC and could not give Q) ----
    te = f"{TAG}_eig"
    ce = eigen_cfg(te, m, mesh=f"{TAG}.msh", sigma=sigma, n=N_MODES, target=fmin)
    ce["Solver"]["Order"] = 2
    ce["Domains"]["Postprocessing"]["Energy"] = energy
    ce["Boundaries"].setdefault("PEC", {"Attributes": []})
    ce["Boundaries"]["PEC"] = {"Attributes": [attrs["port"]]}   # loop shorted

    td = f"{TAG}_drv"
    band = (exact - BAND_HALFWIDTH_MHZ / 1e3, exact + BAND_HALFWIDTH_MHZ / 1e3)
    cd, _meta, dropped = solveconf.driven(f"{TAG}.msh", td, band, step=2e-5, order=2)
    cd["Domains"]["Postprocessing"]["Energy"] = energy
    if dropped:
        print(f"    ⚠️ driven config dropped: {dropped}", flush=True)
    pathlib.Path(f"{td}.json").write_text(json.dumps(cd, indent=2))

    # 🔴 NORMALISE THE DRIVEN DOMAINS TO VACUUM, AND SAY SO.
    #
    # `--no-torch` does NOT remove the torch REGION: attribute 2 still carries
    # 9,479 elements, 28% of this mesh — it is simply vacuum that happens to be
    # tagged separately. But the sidecar records torch_material = [1.0, 3.5e-5],
    # a vacuum permittivity paired with a LOSS TANGENT, which is incoherent, and
    # solveconf.driven faithfully binds it. eigen_cfg meanwhile assigns
    # Permittivity 1.0 with no loss to every volume.
    #
    # So the two solves describe DIFFERENT CAVITIES, differing by a loss term —
    # sitting exactly on Q, the quantity this rig exists to anchor. Magnitude
    # depends on how much energy the region holds and is not the point: an
    # anchor cannot rest on two models of one cavity.
    #
    # ⚠️ SCOPED TO THIS RIG deliberately. The general fix belongs in solveconf
    # (its own rule: a material bound to something the mesh does not have
    # "describes a model it is not solving" — and vacuum-with-loss is the same
    # class of claim), but that changes every driven rig and is not this
    # measurement's job. FINDINGS records it.
    changed = []
    for mat in cd["Domains"]["Materials"]:
        for key, want in (("Permittivity", 1.0), ("LossTan", 0.0),
                          ("Conductivity", 0.0)):
            if key in mat and mat[key] != want:
                changed.append((mat.get("Attributes"), key, mat[key], want))
                mat[key] = want
    if changed:
        print("  🔧 driven domains normalised to vacuum, to match eigen:")
        for a_, k, was, now in changed:
            print(f"       attributes {a_}: {k} {was} -> {now}")
    pathlib.Path(f"{td}.json").write_text(json.dumps(cd, indent=2))

    # 🔑 BOTH CONFIGS EXIST BEFORE EITHER SOLVE RUNS, so the emptiness check
    # below costs nothing when it fires. Checking it between the two solves
    # would have paid for the eigen run first — and "declare the criteria
    # BEFORE the run" (§9) means before the FIRST one.

    # 🔑 THE DIRECT QUESTION, asked of BOTH configs: is this cavity actually
    # empty and lossless apart from the wall? An anchor for absolute Q must be
    # WALL-LOSS ONLY — a stray dielectric loss tangent sits directly on the
    # number being anchored. eigen_cfg assigns vacuum to every volume, but
    # solveconf.driven takes its materials from the TEMPLATE and the mesh's own
    # torch_material, so the two can silently disagree about the same region.
    bad = []
    for name, cfg in (("eigen", ce), ("driven", cd)):
        for mat in cfg["Domains"]["Materials"]:
            eps = mat.get("Permittivity", 1.0)
            tand = mat.get("LossTan", 0.0)
            sig_d = mat.get("Conductivity", 0.0)
            if abs(eps - 1.0) > 1e-12 or tand or sig_d:
                bad.append((name, mat.get("Attributes"), eps, tand, sig_d))
    print(f"  domain materials: {sum(len(c['Domains']['Materials']) for c in (ce, cd))} "
          f"entries across both configs")
    if bad:
        for n, a, e, t, sg in bad:
            print(f"    🔴 {n}: attributes {a} eps={e} tan-delta={t} sigma={sg}")
        raise RuntimeError(
            f"{TAG}: {len(bad)} domain(s) are not vacuum. This rig anchors "
            f"ABSOLUTE Q and the anchor must be WALL-LOSS ONLY — any dielectric "
            f"loss lands directly on the quantity being measured. Listed above; "
            f"fix the geometry flags or the template, do not proceed.")
    print(f"  ✅ every domain is vacuum in BOTH configs — wall loss only\n",
          flush=True)
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

    # ---- driven, SAME mesh, SAME wall ----
    print(f"\n  driven band {band[0]:.4f}-{band[1]:.4f} GHz", flush=True)
    run(td, cd)

    D = analyse_driven(td)
    out = {"domain_normalisation": [[a_, k, was, now]
                                   for a_, k, was, now in changed],
           "design": {"a_mm": a, "L_mm": L, "dl": DL, "sigma": sigma,
                      "tets": m["tets"], "exact_te011": exact},
           "driven": D,
           "eigen": [{"m": md["m"], "f": md["f"], "Q": qs.get(md["m"])}
                     for md in modes]}

    if "error" in D:
        print(f"\n  🔴 driven analysis failed: {D['error']}")
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
        return

    print(f"\n  DRIVEN: f0={D['f0']:.6f}  |S11|min={D['s11_db']:.3f} dB  "
          f"{D['branch']} (phase swing {D['phase_swing_deg']:.1f}°)")
    print(f"          linewidth {D['linewidth_khz']:.1f} kHz  beta={D['beta']:.4f}  "
          f"Q_L={D['Q_L']:,.0f}  ->  Q0={D['Q0']:,.0f}", flush=True)

    # ---- V1: identify the driven mode BY SIGNATURE ----
    dsig = sig_at(td, D["f0"])
    scored = sorted(((eigmodes._dist(dsig, md["sig"]), md) for md in modes),
                    key=lambda x: x[0])
    d0, best = scored[0]
    margin = (scored[1][0] / d0) if len(scored) > 1 and d0 > 0 else float("inf")
    out["identification"] = {"driven_sig": dsig, "best_f": best["f"],
                             "distance": d0, "margin": margin,
                             "ranked": [[round(x[0], 5), x[1]["f"]] for x in scored]}
    print(f"\n  IDENTIFICATION by signature (not frequency):")
    for dist, md in scored:
        print(f"    f={md['f']:.6f}  Q={qs.get(md['m'],0):>10,.0f}  d={dist:.5f}"
              + ("   <-- driven dip" if md is best else ""))
    print(f"    margin over next {margin:.1f}x "
          f"(V1 needs > {SIG_MARGIN_MIN})", flush=True)

    if margin < SIG_MARGIN_MIN:
        print(f"\n  🔴 F2 FIRES: signature margin {margin:.1f}x < {SIG_MARGIN_MIN}. "
              f"The loop has hybridised the degenerate pair. NO Q comparison is "
              f"claimed — and this does NOT fall back to nearest-frequency.")
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
        return

    # WHICH mode is it? Q separates the degenerate pair; declare the window
    # floor so te011_tm111 can refuse rather than reach past the edge of what
    # was searched — the guard added after H2b invented a TM111 at 2.60631.
    fs = [md["f"] for md in modes]
    qlist = [qs.get(md["m"], 0.0) for md in modes]
    pair = eigmodes.te011_tm111(fs, exact, qlist, fmin=fmin)
    label = "unidentified"
    if pair:
        if abs(best["f"] - pair["te011"]) < 1e-9:
            label = "TE011"
        elif best["f"] in [fs[i] for i in pair["tm111_indices"]]:
            label = "TM111 (one polarisation)"
        out["pair"] = {k: v for k, v in pair.items() if k != "triplet"}
        print(f"\n  the degenerate pair, by Q: TE011={pair['te011']:.6f}  "
              f"TM111={pair['tm111']:.6f}  (how={pair['how']})")
    else:
        print(f"\n  ⚠️ te011_tm111 REFUSED — the pair is not resolvable in this "
              f"window. The anchor below is for an UNLABELLED mode.")
    out["identification"]["mode_label"] = label
    print(f"  the loop coupled to: {label}", flush=True)

    qe = qs.get(best["m"])
    ratio = D["Q0"] / qe if qe else None
    out["anchor"] = {"Q0_driven": D["Q0"], "Q0_eigen": qe, "ratio": ratio}
    print(f"\n  {'='*70}\n  THE ANCHOR")
    print(f"    Q0 from the driven LINEWIDTH : {D['Q0']:>12,.0f}")
    print(f"    Q0 from the EIGENVALUE       : {qe:>12,.0f}")
    print(f"    ...for mode                  : {label:>12}")
    print(f"    ratio driven/eigen           : {ratio:>12.3f}")

    # ---- declared falsifiers, judged ----
    print(f"\n  DECLARED CRITERIA")
    v3 = abs(1e3 * (best["f"] - exact))
    print(f"    V3 loop perturbation: {v3:.2f} MHz from closed form "
          f"{'✅' if v3 < 5 else '🔴 the loop is a redesign, not a perturbation'}")
    print(f"    V2 beta={D['beta']:.4f} {'✅' if D['beta'] < BETA_MAX else '🔴 F3'}"
          f"  branch={D['branch']} by phase")
    agree = ratio is not None and abs(ratio - 1) <= 0.20
    print(f"    F1 |ratio-1| = {abs(ratio-1):.1%} "
          + ("✅ ABSOLUTE Q IS ANCHORED — two independent routes agree"
             if agree else
             "🔴 F1 FIRES: the two routes DISAGREE. Absolute Q is NOT anchored. "
             "This is the result; do not adjust the coupling model to close it."))
    out["verdict"] = {"anchored": bool(agree), "loop_shift_mhz": v3,
                      "beta_ok": bool(D["beta"] < BETA_MAX)}
    journal.log(TAG, event="anchor", **out["anchor"])
    json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
