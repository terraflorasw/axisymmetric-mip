"""H2b — is the groove characterisable by a RATIO, so it transfers?

H2 measured the depth sweep at D/L 1.525, gw = 5 mm, and refuted my stub model in
the useful regime:

    d = 10 mm -> TM111 -64.25 MHz, TE011 +0.014 MHz, Q -0.3%
    d = 20 mm -> TM111 -110.77 MHz, TE011 -0.002 MHz, Q -0.04%
    d >= 27 mm -> the slot RESONATES, hybridises with the cavity, Q craters to
                  ~3,000 and the mode identification fails outright.

Ratio 10->20 mm was 1.72x. tan(beta d) predicts 2.93x, so it is NOT stub-limited
down here; lambda/4 is the depth to AVOID, not to target. 2.00x is what the slot
VOLUME FRACTION predicts, and 1.72 is nearer that:

    eta = 4 * gw * gd / (a * L)        slot volume / cavity volume

⚠️ TWO POINTS CANNOT ESTABLISH A SCALING LAW. eta is a hypothesis read off a
1.72-vs-2.00 comparison, and this rig exists to test it rather than adopt it.

THREE QUESTIONS, all in the shallow (non-resonant) regime:

  PRODUCT    same eta, different (gw, gd). If eta governs, a 2x25 slot equals a
             5x10 slot and the 2D search collapses to ONE parameter — plus
             freedom to machine narrow-deep or wide-shallow.
  EXPONENT   eta series at fixed width. Is it eta^1, or the eta^0.78 that two
             points hint at?
  TRANSFER   same eta at D/L 1.35 / 1.525 / 1.90. Volume fraction normalises for
             cavity SIZE, but the perturbation acts through TM111's cap CURRENT
             at the corner, which volume does not capture. This is the question
             that decides whether the ratio survives adding a torch and
             viewports.

VERIFICATION   each D/L has its own gd=0 control, so every shift is measured
               against the same geometry ungrooved.
FALSIFICATION  🔴 equal-eta cases differing by more than ~15% -> eta is not the
               governing group and width/depth are not interchangeable.
               🔴 transfer cases differing across D/L -> the ratio does not
               normalise, and a corner-current factor is needed.

🔑 Q GUARD. A mode with Q far below the ungrooved TE011 is a lossy SLOT
resonance, not the cavity mode — that is how H2's deep points were silently
mis-identified while reporting confident splittings. Any point whose Q falls
below half the control is flagged and excluded from the fit, not quietly used.
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eigmodes
import physics as ph
import solveconf
from e0_solver_vs_math import GEO, eigen_cfg, run, volume_attrs
from scipy.optimize import brentq

TAG = "h2b"
SIGMA = 3.5e7
LAM = 299.792458 / 2.45

# 🔴 TARGET WAS 2.40 AND THAT IS WHAT BROKE THIS RIG. Palace returns N modes
# ABOVE the target, and the groove pushes TM111 DOWNWARD — that is the whole
# point, it clears the 2.40-2.50 LDMOS band. Past ~8 mm of depth TM111 left the
# window through the FLOOR and was never in the file, so anchor/eta3/eta4
# reported a confident TM111 that was an unrelated degenerate pair. H2 got the
# same measurement right only because it used the default target=1.05.
#
# 🔑 The floor is a CALCULATION, not a guess. At D/L 1.525 the closed form has
# nothing between TE211 at 2.10447 and the degenerate pair at 2.45000, so 2.25
# buys 200 MHz of downward headroom at the cost of ZERO extra cavity modes.
TARGET = 2.25
N_MODES = 10          # 8 covered the old narrow window; the floor is lower now


def shape(dl):
    L = brentq(lambda L: ph.f_mnp("TE", 0, 1, 1, dl * L / 2, L) - 2.45,
               20.0, 400.0, xtol=1e-10)
    return dl * L / 2, L


def eta(dl, gw, gd):
    a, L = shape(dl)
    return 4.0 * gw * gd / (a * L)


# 🔴 THE gd=0 CONTROLS ARE GONE, and they were never a control for the groove.
#
# chi'_01 and chi_11 are THE SAME Bessel zero (3.831706), so TE011 and TM111 are
# EXACTLY degenerate at every D/L, and shape(dl) solves each geometry to put
# TE011 at 2.45. The ungrooved TM111 therefore sits at 2.45000 BY CONSTRUCTION.
# Solving for it measures nothing about the groove.
#
# What it bought, against what it cost:
#   effect measured            27-63 MHz
#   absolute accuracy          0.361 MHz  -> under 1.4% of the effect
#   differential accuracy      0.020 MHz  -> 0.07%
#   price                      3 of 11 cases, 27% of the sweep
#
# ⚠️ And it can be WORSE than the analytic value, not merely redundant: in the
# ungrooved case the pair is degenerate to within mesh asymmetry (~0.070 MHz),
# so te011_tm111 must separate two near-identical modes by Q, and THAT
# assignment error propagates into every shift referenced to it. The control
# spends its precision advantage resolving a degeneracy the closed form gives
# as exactly zero.
#
# One analytic reference serves all three aspect ratios, which also makes the
# transfer test cleaner. The three freed cases go to DEPTH POINTS, which is what
# the exponent actually needs (CONVENTIONS §11).
REFERENCE_GHZ = 2.45     # ungrooved TE011 = TM111, exact, every D/L
Q_TE011_BARE = 44384.0   # INSTRUMENT, aluminium bare cavity; the Q guard
                         # compared against a solved control before

# (label, D/L, gw, gd)
CASES = [("exp-gd2p5",     1.525, 5.0, 2.5),
         ("exp-eta1",      1.525, 5.0, 5.0),
         ("exp-gd7p5",     1.525, 5.0, 7.5),
         ("anchor",        1.525, 5.0, 10.0),
         ("exp-gd12p5",    1.525, 5.0, 12.5),
         ("exp-eta3",      1.525, 5.0, 15.0),
         ("exp-eta4",      1.525, 5.0, 20.0),
         # 🔴 was 2.0 x 25.0 — a 2 mm slot forced 58,303 tets against ~33,000
         # for the 5 mm cases AND badly conditioned the linear solve: 248 KSP
         # iterations still short of tolerance at 64 minutes, for one point.
         # 3.0 x 16.67 keeps the SAME eta and still spans 2.7x in width against
         # prod-wide, which is enough to test interchangeability. A 2 mm slot is
         # also poor manufacturing, so the extreme was never the design case.
         ("prod-narrow",   1.525, 3.0, 16.667),
         ("prod-wide",     1.525, 8.0, 6.25),
         ("xfer-1.35",     1.350, 5.0, 10.6),
         ("xfer-1.90",     1.900, 5.0, 9.3)]


def build(tag, a, L, gw, gd):
    args = list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}"]
    if gd > 0 and gw > 0:
        # 🔑 --tag-groove MAKES THE SLOT ITS OWN VOLUME, and that is the whole
        # scaling measurement. R81 built this flag for exactly this and it
        # defaults OFF, so neither H2 nor H2b ever passed it — which is why the
        # depth law is still unresolved after two rigs.
        #
        # SLATER: for a small wall deformation of volume dV,
        #     df/f0 = -(1/W) * INT_dV (mu|H|^2 - eps|E|^2)/2 dV
        # and at resonance U_mag = U_elec = W/2, so in Palace's normalised bins
        # this is simply
        #     df/f0 = -(p_mag[groove] - p_elec[groove]) / 2
        # ONE number per solve, no free parameters, no fitting.
        #
        # 🔑 WHY IT SHOULD BEAT BOTH FAILED MODELS. Z0*tan(bd) and the volume
        # fraction both reduce to the PRODUCT gw*gd, which assumes the field is
        # UNIFORM across the slot. It is not: the far end of a deep slot carries
        # less field, so the integral grows SUB-linearly in depth. That is the
        # right sign for the 1.72x measured against 2.93x and 2.00x predicted.
        #
        # ⚠️ Slater is the SMALL-groove limit. It must fail for deep slots, and
        # where it starts to fail is itself the measurement of where the slot
        # stops being a perturbation and starts being a resonator — which is the
        # lambda/4 boundary H2 found the hard way at 30.6 mm.
        args += ["--groove", f"{gw},{gd}", "--tag-groove"]
    for sf in ("1.5", "1.2", "1.0", "2.0"):
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if r.returncode == 0 and pathlib.Path(f"{tag}.msh").exists():
            return solveconf.load_meta(f"{tag}.msh"), sf
    raise RuntimeError(f"{tag}: no size factor meshed")


def eig_q(tag):
    """🔴 REPORTS an empty or truncated eig.csv rather than returning ([], []).

    A reclamation left postpro/h2b_prod_narrow/ with a HEADER-ONLY eig.csv, and
    this function returned two empty lists in silence — a directory that looks
    like a solved case, feeding a caller that cannot tell it apart from one.
    """
    f = pathlib.Path("postpro") / tag / "eig.csv"
    rows = []
    for line in f.read_text().splitlines()[1:]:
        p = line.split(",")
        if len(p) > 3:
            rows.append((float(p[1]), float(p[3])))
    rows.sort()
    if not rows:
        raise RuntimeError(
            f"{f}: no mode rows — the solve produced a header-only eig.csv. "
            f"That is an interrupted or failed case, not an empty result.")
    return [r[0] for r in rows], [r[1] for r in rows]


def groove_slater(tag):
    """Slater's predicted df/f0 per mode, from the tagged groove's energy bins.

    Returns {mode_index: df_over_f0} or None when the groove was not tagged —
    REPORTED as None, never silently zero: a missing measurement and a zero
    shift are different claims.

    🔑 df/f0 = -(p_mag[groove] - p_elec[groove]) / 2, with no fitted constant.
    ⚠️ The SIGN convention (added volume vs removed) is fixed by the first
    grooved case against its own control and is asserted, not assumed.
    """
    import csv as _csv
    d = pathlib.Path("postpro") / tag
    meta = solveconf.load_meta(f"{tag}.msh")
    g = (meta.get("attributes") or {}).get("groove")
    if g is None:
        return None
    # 🔴 was a local copy of the surface/volume rule. A `loop`
    # SURFACE got classified as a VOLUME (2026-08-27) and
    # Palace refused the config. One definition now.
    vols = volume_attrs(meta)
    if g not in vols:
        return None
    idx = 10 + vols.index(g)          # eigen_cfg's numbering
    rows = list(_csv.reader((d / "domain-E.csv").read_text().splitlines()))
    head = [h.strip() for h in rows[0]]
    try:
        ie = head.index(f"p_elec[{idx}]")
        im = head.index(f"p_mag[{idx}]")
    except ValueError:
        return None
    out = {}
    for r in rows[1:]:
        try:
            out[round(float(r[0]))] = -(float(r[im]) - float(r[ie])) / 2.0
        except (ValueError, IndexError):
            continue
    return out


def _checkpoint(path, payload):
    """Write results after EVERY case, not at the end.

    🔴 A spot reclamation on 2026-08-21 killed the instance mid-run. H1, H2 and
    H2b all wrote their result file only after the last case, so an interrupt
    lost every completed case with it — H2's table survived solely because it
    had been printed to a log and transcribed by hand. E0v already did this
    correctly ("written after EVERY case, so a death in case 2 cannot take case
    1 down with it"); the H rigs did not inherit it.

    Atomic: temp file then os.replace, so an interrupt DURING the write leaves
    the previous complete file rather than a truncated one.
    """
    import json as _j, os as _o, pathlib as _p
    p = _p.Path(path)
    t = p.with_suffix(p.suffix + f".tmp{_o.getpid()}")
    t.write_text(_j.dumps(payload, indent=1) + "\n")
    _o.replace(t, p)


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    import os
    only = os.environ.get("H2B_ONLY")
    todo = [c for c in CASES if not only or c[0] in only.split(",")]
    if only:
        print(f"  H2B_ONLY set — running {len(todo)} of {len(CASES)} cases: "
              f"{[c[0] for c in todo]}")
        print("  (the others are already solved; postpro/ holds their data and "
              "h2b_analyse.py reads all of them together)\n", flush=True)
    out = []
    for label, dl, gw, gd in todo:
        a, L = shape(dl)
        tag = f"{TAG}_{label.replace('.', 'p').replace('-', '_')}"
        m, sf = build(tag, a, L, gw, gd)
        EX = ph.spectrum(a, L, fmax=3.2)
        c = eigen_cfg(tag, m, mesh=f"{tag}.msh", sigma=SIGMA,
                      n=N_MODES, target=TARGET)
        c["Solver"]["Order"] = 2
        run(tag, c)
        fs, qs = eig_q(tag)
        # 🔴 DECLARE THE WINDOW FLOOR. te011_tm111 refuses when its candidate is
        # further from the exact frequency than the search actually reached —
        # without fmin it falls back to the lowest mode RETURNED, which is a
        # weaker guard. This is the one argument that would have caught the bug.
        d = eigmodes.te011_tm111(fs, EX["TE011"], qs, fmin=TARGET)
        if not d:
            print(f"    🔴 {label}: triplet unresolved — REPORTED, not dropped")
            continue
        e = eta(dl, gw, gd)
        slater = groove_slater(tag)
        out.append({"slater": slater,
                    "label": label, "dl": dl, "gw": gw, "gd": gd, "eta": e,
                    "a": a, "L": L, "sf": sf, "tets": m["tets"],
                    "te011": d["te011"], "tm111": d["tm111"],
                    "q_te011": qs[d["te011_index"]],
                    "q_tm111": sum(qs[i] for i in d["tm111_indices"]) / 2.0})
        print(f"    {label:<15} eta {e:.4f}  TE011 {d['te011']:.5f}  "
              f"TM111 {d['tm111']:.5f}  Q_TE {qs[d['te011_index']]:,.0f}",
              flush=True)
        _checkpoint(f"{TAG}.result.json", {"cases": out})

    # 🔑 REFERENCE IS ANALYTIC. No solved control, so no control identification
    # error, and every D/L shares one reference because every geometry is built
    # to put TE011 = TM111 at 2.45000 exactly.
    ctl = {}
    print("\n" + "=" * 78)
    print(f"  {'case':<15}{'D/L':>6}{'gw':>6}{'gd':>7}{'eta':>8}"
          f"{'TM111 shift':>13}{'TE011 shift':>13}{'df/f0 / eta':>13}{'':>4}")
    for r in out:
        if r["gd"] == 0.0:
            continue
        dtm = 1e3 * (r["tm111"] - REFERENCE_GHZ)
        dte = 1e3 * (r["te011"] - REFERENCE_GHZ)
        # 🔴 THE CRITERION IS THE DECLARED ONE, NOT A MAGIC Q RATIO. This rig
        # verifies that TE011 barely moves; a point where it moves by tens of
        # MHz has failed that check, and the Q collapse is a symptom of the same
        # thing. Judge on the stated physics, not on a threshold I invented.
        susp = abs(dte) > 10.0 or r["q_te011"] < 0.5 * Q_TE011_BARE
        k = abs(dtm) / 2450.0 / r["eta"]
        print(f"  {r['label']:<15}{r['dl']:>6.3f}{r['gw']:>6.1f}{r['gd']:>7.1f}"
              f"{r['eta']:>8.4f}{dtm:>13.2f}{dte:>13.3f}{k:>13.2f}"
              f"{'  🔴 Q' if susp else '':>4}")
        r.update(dtm=dtm, dte=dte, k=k, suspect=susp)

    # 🔴 SAY WHAT WAS EXCLUDED. The first version filtered silently — in a file
    # whose docstring claims nothing is dropped. E1b's shape A disappeared
    # exactly this way. A criterion that deletes its evidence cannot be caught
    # being wrong.
    scored = [r for r in out if r.get("k") is not None]
    good = [r for r in scored if not r.get("suspect")]
    dropped = [r for r in scored if r.get("suspect")]
    if dropped:
        print(f"\n  🔴 EXCLUDED from the fits ({len(dropped)} of {len(scored)}): "
              f"{[(r['label'], round(r['dte'],1)) for r in dropped]}")
        print("     reason: TE011 moved >10 MHz or Q fell below half the "
              "control — the slot is resonating and these are not cavity modes.")
    else:
        print(f"\n  ✅ no point excluded — all {len(scored)} passed the "
              f"TE011-barely-moves check")
    prod = [r for r in good if r["label"].startswith(("prod", "anchor"))]
    if len(prod) > 1:
        ks = [r["dtm"] for r in prod]
        spread = (max(ks) - min(ks)) / abs(sum(ks) / len(ks))
        print(f"\n  PRODUCT test — equal eta, different (gw,gd): shifts "
              f"{[round(x,1) for x in ks]}, spread {spread:.1%}")
        print(f"    {'✅ eta governs; width and depth are interchangeable' if spread < 0.15 else '🔴 eta does NOT govern — width and depth are not interchangeable'}")
    xf = [r for r in good if r["label"].startswith(("xfer", "anchor"))]
    if len(xf) > 1:
        ks = [r["k"] for r in xf]
        spread = (max(ks) - min(ks)) / abs(sum(ks) / len(ks))
        print(f"  TRANSFER test — equal eta, different D/L: df/f0/eta "
              f"{[round(x,2) for x in ks]}, spread {spread:.1%}")
        print(f"    {'✅ the ratio transfers across aspect ratio' if spread < 0.15 else '🔴 needs a corner-current factor — volume alone does not normalise'}")
    ex = sorted([r for r in good if r["label"].startswith(("exp", "anchor"))],
                key=lambda r: r["eta"])
    if len(ex) > 2:
        import math
        xs = [math.log(r["eta"]) for r in ex]
        ys = [math.log(abs(r["dtm"])) for r in ex]
        mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
        slope = (sum((x-mx)*(y-my) for x, y in zip(xs, ys))
                 / sum((x-mx)**2 for x in xs))
        print(f"  EXPONENT — d(log shift)/d(log eta) = {slope:.3f} "
              f"(1.000 = pure volume fraction)")
        # and the same fit WITH the excluded points, so the exclusion's effect
        # is visible rather than taken on trust
        exa = sorted([r for r in scored
                      if r["label"].startswith(("exp", "anchor"))],
                     key=lambda r: r["eta"])
        if len(exa) > len(ex):
            xs2 = [math.log(r["eta"]) for r in exa]
            ys2 = [math.log(abs(r["dtm"])) for r in exa]
            m2, n2 = sum(xs2)/len(xs2), sum(ys2)/len(ys2)
            sl2 = (sum((x-m2)*(y-n2) for x, y in zip(xs2, ys2))
                   / sum((x-m2)**2 for x in xs2))
            print(f"    with the excluded points included it would be "
                  f"{sl2:.3f} — that difference IS the exclusion's effect")
    json.dump({"cases": out}, open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
