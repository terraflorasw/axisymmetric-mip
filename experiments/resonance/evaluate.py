#!/usr/bin/env python3
"""Apply labels and criteria to measured results. Re-runnable; never re-solves.

The third of the three layers. results.py holds measurements and provenance; the
driver's docstring holds the criteria, declared before the run; this holds the
interpretation — and it is the layer that has been wrong every time.

    R54  verdict wrong three ways (author's own note: "the raw table is what stands")
    R74  unimodal plateau detector on a U-shaped curve
    R79  "TE011 already wins" — the band excluded the mode that beat it
    R59  mode-hopping tracker; and C4 never applied reachability

All four survived as data and died as interpretation. Separating them means the
next one costs a rerun of this file instead of a retraction in FINDINGS.

🔑 EVERY LABEL CARRIES THE RULE THAT PRODUCED IT. A label is a hypothesis. R77
called a mode TM111 on an elimination argument that imported a baseline from
another geometry; R59's tracker re-identified its target at every depth. If the
rule is printed next to the label, that failure is visible in the output instead
of buried in a classifier.

🔑 REACHABILITY IS APPLIED BEFORE RANKING, ALWAYS. A mode the amplifier cannot
drive is not a rival however much power it absorbs in the model. R59 scored modes
65 MHz above the LDMOS top and failed depths for it.

⚠️ OFFSETS ARE MODE-DEPENDENT. offset.te011 = +24.54 and offset.tm020 = +20.06 are
different numbers and neither is measured for other modes (R38 flags them
geometry-dependent too). Corrected frequencies here use the TE011 offset for
everything, which is WRONG BY A FEW MHz for non-TE011 modes and is stated on
every line rather than hidden.

USAGE
    evaluate.py <tag> [<tag>...]            label and tabulate, with reachability
    evaluate.py --sweep <name>              read a sweep index and score its cases
"""
import json
import pathlib
import sys

import results

OFF_TE = 0.02454
LDMOS = (2.400, 2.500)
AZ_FLOOR = 0.0046          # te011.azimuthal_floor, design loop (R47)
QUARTZ = dict(b1=0.0263, b2=0.0287, pm_over_pe=27.5, Q0=37059.0)


def label(m, spectrum):
    """(label, rule). Rules are stated so a wrong one is visible, not buried."""
    pmpe = m.get("pm_over_pe")
    b2 = m.get("b2") or 0.0
    b1 = m.get("b1") or 0.0
    if pmpe is not None and pmpe < 0.2:
        return "bore-E dominant", "pm/pe < 0.2 (TM020-like: E on axis)"
    hi = max((x.get("pm_over_pe") or 0) for x in spectrum)
    if pmpe is not None and pmpe == hi and pmpe > 5:
        return "bore-H dominant", "highest pm/pe in window, > 5 (TE011-like)"
    if b2 / AZ_FLOOR > 20:
        return "strong m=1", f"bin2 = {b2/AZ_FLOOR:.0f}x the m=0 floor"
    if b1 / AZ_FLOOR > 8:
        return "m=2 or m=3", f"bin1 = {b1/AZ_FLOOR:.0f}x floor (N=5 aliases both)"
    if (m.get("Q0") or 0) < 12000:
        return "low-Q (slot-like)", "Q0 < 12,000 — lossy, not a clean cavity mode"
    return "unlabelled", "no rule matched — this is not an identification"


def table(tag):
    d = results.load(tag)
    w = d["window"]
    print(f"\n{tag}  —  {d['tets']:,} tets, sf {d['size_factor']}, "
          f"order {d['order']}, "
          f"{'LIT σ=' + str(d['plasma_sigma']) if d['lit'] else 'COLD'}")
    print(f"  window {w['f_min']}–{w['f_max']} GHz @ {1e6*w['step']:.0f} kHz, "
          f"{w['n_samples']} samples, peaks above {100*w['peak_rel_threshold']:.1f}% "
          f"of max")
    print(f"  ⚠️ nothing outside that window was searched; absence here is "
          f"absence FROM IT")
    if d.get("geometry_mm"):
        g = d["geometry_mm"]
        print(f"  geometry: groove {g.get('groove')} mm, brake_t "
              f"{g.get('brake_t')} mm, radius {g.get('radius')}, "
              f"length {g.get('length')}")
    ms = sorted(d["modes"], key=lambda m: m["f"])
    print(f"    {'f raw':>9}{'f+TEoff':>9}{'reach':>7}{'pm/pe':>8}{'Q0':>9}"
          f"{'eta':>7}{'bin1':>8}{'bin2':>8}  label / rule")
    for m in ms:
        fc = m["f"] + OFF_TE
        reach = LDMOS[0] < fc < LDMOS[1]
        lab, rule = label(m, d["modes"])
        pmpe = m.get("pm_over_pe")
        print(f"    {m['f']:>9.4f}{fc:>9.4f}{'IN' if reach else 'out':>7}"
              f"{(f'{pmpe:.1f}' if pmpe else '—'):>8}{m['Q0']:>9,.0f}"
              f"{100*m['eta']:>6.1f}%{(m['b1'] or 0):>8.4f}{(m['b2'] or 0):>8.4f}"
              f"  {lab} [{rule}]")
    return d


def score(tag):
    """Criteria against the quartz reference, reachability applied first."""
    d = results.load(tag)
    ms = d["modes"]
    if not ms:
        return dict(tag=tag, error="no modes — run incomplete or window empty")
    te = max(ms, key=lambda m: m.get("pm_over_pe") or 0)
    riv = [m for m in ms if m is not te
           and LDMOS[0] < m["f"] + OFF_TE < LDMOS[1]]
    best = max(riv, key=lambda m: m["eta"]) if riv else None
    return dict(
        tag=tag, groove=(d.get("geometry_mm") or {}).get("groove"),
        te_f=te["f"], te_pmpe=te.get("pm_over_pe"), te_Q0=te["Q0"],
        te_eta=te["eta"], b1=te["b1"], b2=te["b2"],
        n_rivals=len(riv), best_rival_eta=(best["eta"] if best else None),
        c1=(te["b1"] <= QUARTZ["b1"] and te["b2"] <= QUARTZ["b2"]),
        c2=((te.get("pm_over_pe") or 0) >= QUARTZ["pm_over_pe"]),
        c3=(te["Q0"] >= QUARTZ["Q0"]),
        c4=(best is None or te["eta"] >= 2 * best["eta"]))


def r99(qz="s99qz", sa="s99sa", pr="s99pr", qzL="s99qzL", saL="s99saL",
        prL="s99prL"):
    """R99's declared criteria. Re-runnable; no solve.

    Mode identity is by SIGNATURE and the rule is printed with the label:
    TM020 is the bore-E dominant mode (E_z peaks on axis); TE011 is bore-H
    dominant with the LOWEST bore-E (its E_phi and E_z both vanish on axis).
    """
    b = json.loads(pathlib.Path("baselines.json").read_text())
    tm020_conv = b["tm020.f_converged"]["value"]
    dTM_da = 22.0          # MHz/mm, |dTM020/da|
    callout = 0.2          # mm, cav.radius drawing tolerance
    thresh = dTM_da * callout   # 4.4 MHz — the declared threshold

    def tm(tag):
        ms = results.load(tag)["modes"]
        m = max(ms, key=lambda x: x["bore_e"])
        return (m, m["bore_e"])

    # widest window each case's TM020 was actually seen in
    q, qe = tm(qz)                      # quartz: upper window
    a, ae = tm(saL)                     # sapphire L=88.53: low window
    p_, pe = tm(prL)                    # sapphire L=87.97: low window
    ctrl, ce = tm(qzL)                  # quartz in the LOW window: control

    d_mhz = 1e3 * (a["f"] - q["f"])
    conv = tm020_conv + (a["f"] - q["f"])
    clear = 1e3 * (2.400 - conv)
    null_mhz = 1e3 * abs(a["f"] - p_["f"])

    print("R99 — TM020 at the sapphire point. Labels by bore-E signature.\n")
    print(f"  quartz   TM020  f={q['f']:.5f}  boreE={100*qe:.3f}%  (upper window)")
    print(f"  sapphire TM020  f={a['f']:.5f}  boreE={100*ae:.3f}%  (low window)")
    print(f"  shift                          {d_mhz:+.1f} MHz\n")
    print(f"  CONTROL  quartz in the LOW window: max boreE {100*ce:.3f}% at "
          f"{ctrl['f']:.5f}")
    print(f"    {'✅' if ce < 0.005 else '🔴'} no spurious bore-E mode below "
          f"2.30 in quartz — the low window reads correctly\n")
    print(f"  NULL CONTROL  dTM020/dL = 0, so L=88.53 and L=87.97 must agree")
    print(f"    |Δf| = {null_mhz:.2f} MHz on a 0.20 MHz grid "
          f"({null_mhz/0.2:.0f} steps)")
    print(f"    {'✅' if null_mhz < 1.0 else '🔴'} TE011 moved 5.85 MHz for the "
          f"same ΔL — a {5.85/max(null_mhz,1e-9):.0f}x discrimination\n")
    print(f"  PRIMARY  clearance below the 2.400 GHz band floor")
    print(f"    frame: differential against tm020.f_converged={tm020_conv} "
          f"(never raw vs 2.400)")
    print(f"    f_converged(sapphire) = {conv:.5f} GHz")
    print(f"    clearance = {clear:.1f} MHz   threshold = {thresh:.1f} MHz")
    print(f"    {'✅' if clear >= thresh else '🔴'} passes by "
          f"{clear/thresh:.0f}x\n")
    print(f"  CONSEQUENCE  radius error needed to make TM020 reachable: "
          f"{clear/dTM_da:.2f} mm")
    print(f"    against a ±{callout} mm callout — TM020 is unreachable by "
          f"{clear/dTM_da/callout:.0f}x the drawing tolerance")
    return dict(shift_mhz=d_mhz, f_conv=conv, clearance_mhz=clear,
                threshold_mhz=thresh, null_mhz=null_mhz,
                da_to_reach_mm=clear/dTM_da)


def _te011(tag):
    """TE011 by signature, with the identity gate R103 declared.

    TE011 is bore-H dominant with the LOWEST bore-E (E_phi and E_z both vanish
    on axis). The gate: the lowest-bore-E mode must ALSO be among the top bore-H
    modes. R59's tracker re-identified its target at every depth and drew a
    clean curve through three different modes; this refuses the point instead.
    """
    ms = results.load(tag)["modes"]
    if not ms:
        return None, "no modes in window"
    lo = min(ms, key=lambda m: m["bore_e"])
    if lo["bore_h"] < 0.5 * max(m["bore_h"] for m in ms):
        return None, (f"lowest-bore-E mode has bore_h {100*lo['bore_h']:.3f}% "
                      f"vs max {100*max(m['bore_h'] for m in ms):.3f}% "
                      "— tracker hop, point discarded")
    return lo, None


def _fit(pts):
    """Least squares slope/intercept and max |residual|, in MHz and mm."""
    n = len(pts)
    mx = sum(x for x, _ in pts) / n
    my = sum(y for _, y in pts) / n
    sxx = sum((x - mx) ** 2 for x, _ in pts)
    sxy = sum((x - mx) * (y - my) for x, y in pts)
    b = sxy / sxx
    a = my - b * mx
    res = [1e3 * (y - (a + b * x)) for x, y in pts]          # MHz
    # R103: the SLOPE'S UNCERTAINTY, not just its residual. Each ladder point is
    # a SEPARATE MESH, so every point carries independent discretisation error;
    # a residual says "the points scatter", sigma_slope says "by how much that
    # moves the answer". Without it a 2-point slope looks as authoritative as a
    # 5-point fit, which is exactly the error R99 made.
    n = len(pts)
    sig = (sum(r * r for r in res) / max(n - 2, 1)) ** 0.5   # MHz, per point
    sxx_mm = sum((x - mx) ** 2 for x, _ in pts)
    return b * 1e3, a, max(abs(r) for r in res), res, sig, sig / sxx_mm ** 0.5


def r103(name="r103"):
    """R103's declared criteria. Re-runnable; no solve."""
    idx = json.loads(pathlib.Path(f"{name}.sweep.json").read_text())
    LA, LB = idx["extra"]["ladder_a"], idx["extra"]["ladder_b"]
    gate = idx["extra"]["linearity_gate_mhz"]
    RECORD = -13.06          # R46, no viewport/trap
    PAIR = -10.4             # R99's two-point value

    def ladder(Ls, pre):
        pts, bad = [], []
        for L in Ls:
            t = f"{pre}{str(L).replace('.', 'p')}"
            m, why = _te011(t)
            (bad if m is None else pts).append((L, why) if m is None
                                               else (L, m["f"]))
        return pts, bad

    out = {}
    print(f"R103 — dTE011/dL. TE011 by lowest-bore-E with a tracker-hop gate.\n")
    for key, Ls, pre, lab in (("A", LA, "L3a", "sapphire, viewport+trap ON"),
                              ("B", LB, "L3b", "sapphire, viewport+trap OFF")):
        pts, bad = ladder(Ls, pre)
        for L, why in bad:
            print(f"  🔴 ladder {key} L={L}: {why}")
        if len(pts) < 2:
            print(f"  🔴 ladder {key}: {len(pts)} usable points — no fit")
            continue
        slope, _a, mres, res, sig, sig_b = _fit(pts)
        out[key] = dict(slope=slope, max_resid=mres, n=len(pts),
                        sigma_point=sig, sigma_slope=sig_b)
        print(f"  LADDER {key} — {lab}  ({len(pts)} points)")
        for (L, f), r in zip(pts, res):
            print(f"    L={L:6.2f}  f={f:.5f}   resid {r:+.3f} MHz")
        print(f"    slope = {slope:+.2f} ± {sig_b:.2f} MHz/mm   "
              f"per-point σ = {sig:.2f} MHz   max|resid| = {mres:.3f} MHz")
        if key == "A":
            # R103 SELF-CORRECTION. The declared 0.5 MHz gate is BELOW the
            # per-mesh discretisation floor (~2-3 MHz here; R46's own three
            # lengths scattered 0.07 mm = 0.9 MHz). A gate under the noise floor
            # cannot pass whatever the physics does, so failing it says nothing
            # about linearity — it says the gate was mis-specified. Same lesson
            # as the meta["groove"] assert: a check that cannot pass is not a
            # check. Report the scatter and let the slope carry an error bar.
            if mres < gate:
                print(f"    ✅ residual {mres:.2f} < gate {gate} MHz — linear")
            elif sig > gate:
                print(f"    ⚠️ GATE MIS-SPECIFIED: declared {gate} MHz sits "
                      f"BELOW the per-mesh noise floor σ = {sig:.2f} MHz.")
                print(f"       Residuals are scatter, not curvature (signs "
                      f"{' '.join('+' if r > 0 else '-' for r in res)}), so this "
                      "is NOT evidence of nonlinearity.")
                print(f"       The honest statement is the slope WITH its "
                      f"uncertainty: {slope:+.2f} ± {sig_b:.2f} MHz/mm")
            else:
                print(f"    🔴 residual {mres:.2f} MHz exceeds gate {gate} AND "
                      f"the noise floor σ={sig:.2f} — genuinely nonlinear")
        print()

    if "A" in out:
        a = out["A"]["slope"]
        print(f"  PRIMARY   dTE011/dL (product) = {a:+.2f} MHz/mm")
        print(f"    vs R46 record {RECORD:+.2f}  ({100*(a-RECORD)/RECORD:+.0f}%)")
        print(f"    vs R99 2-point {PAIR:+.2f}  "
              f"({100*(a-PAIR)/PAIR:+.0f}%)")
        # was R99's specific pair an outlier within this ladder?
        pts = dict((L, f) for L, f in ladder(LA, "L3a")[0])
        if 87.97 in pts and 88.53 in pts:
            pair = 1e3 * (pts[88.53] - pts[87.97]) / (88.53 - 87.97)
            print(f"    R99's 87.97/88.53 pair, re-measured here: "
                  f"{pair:+.2f} MHz/mm")
            print(f"    {'⚠️ the PAIR disagrees with the FIT' if abs(pair-a) > 1.0
                       else '✅ pair and fit agree — R99 was not an outlier'}")
        print()
    if "A" in out and "B" in out:
        b = out["B"]["slope"]
        gapA = out["A"]["slope"] - RECORD
        gapB = b - RECORD
        print(f"  ATTRIBUTION  does the viewport+trap explain the gap?")
        print(f"    A (with)    {out['A']['slope']:+.2f}   gap vs record "
              f"{gapA:+.2f}")
        print(f"    B (without) {b:+.2f}   gap vs record {gapB:+.2f}")
        nsig = abs(out["A"]["slope"] - b) / (out["A"]["sigma_slope"] ** 2
                                             + out["B"]["sigma_slope"] ** 2) ** 0.5
        print(f"    A vs B differ by {abs(out['A']['slope']-b):.2f} MHz/mm "
              f"= {nsig:.2f}σ — {'consistent' if nsig < 2 else 'DIFFERENT'}")
        if abs(gapA) < 2 * out["A"]["sigma_slope"]:
            print("    ✅ NO GAP TO EXPLAIN — A agrees with the record to "
                  f"{abs(gapA)/out['A']['sigma_slope']:.2f}σ. The premise of "
                  "this attribution was a 2-point measurement with no error bar.")
        elif abs(gapB) < 0.4 * abs(gapA):
            print("    ✅ YES — removing the optical features recovers the "
                  "record. The viewport+trap ARE the cause.")
        elif abs(gapB - gapA) < 0.5:
            print("    🔴 NO — B has the same gap. The optical features are NOT "
                  "the cause; sapphire or R46 itself is.")
        else:
            print("    ⚠️ PARTIAL — the optical features explain some of it. "
                  "Do not attribute the remainder without measuring it.")
    return out


def _sd(xs):
    """Sample standard deviation, ddof=1. NOT the population sd.

    R105: estimating a scatter from n points about their own mean has n-1
    degrees of freedom. Using ddof=0 would flatter the number by sqrt((n-1)/n),
    which for n=5 is 11% — small, but this value is about to become the floor
    quoted against every other difference in the record.
    """
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    return (sum((x - m) ** 2 for x in xs) / (n - 1)) ** 0.5


def r105(name="r105"):
    """R105's declared criteria. Re-runnable; no solve."""
    idx = json.loads(pathlib.Path(f"{name}.sweep.json").read_text())
    ex = idx["extra"]
    C, N = ex["ladder_c"], ex["ladder_n"]
    tets, md5, dfdL = ex["tets"], ex["md5"], ex["dfdL"]
    print("R105 — how much does a frequency move when only the MESH changes?\n")

    # --- CRITERION 3 first: did the cases actually differ? (the R101 lesson)
    nh = {md5[t] for t in N}
    nt = {tets[t] for t in N}
    print(f"  CASES-DIFFER GATE   ladder N: {len(nh)}/{len(N)} distinct md5, "
          f"{len(nt)}/{len(N)} distinct tet counts")
    if len(nh) == 1:
        print("    🔴 DISCARDED — identical meshes measure zero scatter by "
              "construction. That would be an artefact, not a result.")
        return None
    print("    ✅ the meshes differ, so ladder N measures something\n")

    # --- LADDER N: realisation noise, detrended by the KNOWN dTE011/dL
    rows, bad = [], []
    for t, L in sorted(N.items(), key=lambda kv: kv[1]):
        m, why = _te011(t)
        (bad if m is None else rows).append((t, L, why if m is None else m["f"]))
    for t, L, why in bad:
        print(f"    🔴 {t}: {why}")
    if len(rows) < 3:
        print("    🔴 too few usable ladder-N points")
        return None
    L0 = sum(L for _t, L, _f in rows) / len(rows)
    det = [1e3 * f - dfdL * (L - L0) for _t, L, f in rows]   # MHz, detrended
    sN = _sd(det)
    print(f"  LADDER N — fixed size factor, {1e3*(max(N.values())-min(N.values())):.1f} µm span")
    for (t, L, f), d in zip(rows, det):
        print(f"    L={L:.4f}  {tets[t]:>7,} tets  f={f:.5f}  "
              f"detrended {d - sum(det)/len(det):+.3f} MHz")
    print(f"    🔑 σ_realisation = {sN:.2f} MHz   "
          f"(true span from geometry: {ex['n_true_span_mhz']} MHz)")
    print(f"    peak-to-peak {max(det)-min(det):.2f} MHz — "
          f"{(max(det)-min(det))/ex['n_true_span_mhz']:.0f}x the real change\n")

    # --- LADDER C: convergence trend, residual is the same noise
    crow = []
    for t, sf in sorted(C.items(), key=lambda kv: -kv[1]):
        m, why = _te011(t)
        if m is None:
            print(f"    🔴 {t}: {why}")
            continue
        crow.append((sf, m["f"], tets[t]))
    sC = None
    if len(crow) >= 3:
        # order-1 Nedelec: frequency error ~ h^2, and sf is proportional to h
        pts = [(sf * sf, f) for sf, f, _n in crow]
        slope, icept, mres, res, sig, _sb = _fit(pts)
        sC = sig
        print(f"  LADDER C — identical geometry, size factor varied")
        for (sf, f, n), r in zip(crow, res):
            print(f"    sf={sf:.2f}  {n:>7,} tets  f={f:.5f}   resid {r:+.3f} MHz")
        fs = [f for _sf, f, _n in crow]
        mono = all(b >= a for a, b in zip(fs, fs[1:]))   # coarse->fine ascending
        print(f"    {'✅' if mono else '🔴'} monotonic with refinement "
              f"{'(coarse sits low, as expected)' if mono else
                 '— trend is buried in noise; only ladder N stands'}")
        print(f"    extrapolated f(h→0) = {icept:.5f} GHz "
              f"(vs finest solved {fs[-1]:.5f}, a {1e3*(icept-fs[-1]):+.1f} MHz "
              f"convergence bias)")
        print(f"    σ_C about the trend = {sig:.2f} MHz\n")

    # --- CROSS-CHECK
    if sC and sN:
        ratio = max(sC, sN) / min(sC, sN)
        print(f"  CROSS-CHECK  σ_N={sN:.2f}  σ_C={sC:.2f}  ratio {ratio:.2f}x")
        print(f"    {'✅ two independent routes agree' if ratio < 2 else
                   '🔴 routes DISAGREE by more than 2x — sigma is NOT '
                   'characterised; the honest answer is that we do not know'}\n")

    # --- CONSEQUENCE
    if sN:
        # 🔑 A NULL CONTROL AND A CLAIMED DIFFERENCE HAVE OPPOSITE PASS
        # CONDITIONS. A difference must EXCEED the noise to mean anything; an
        # agreement must fall INSIDE it. The first version of this printer
        # flagged R99b's null control 🔴 UNRESOLVED for landing at 0.3σ —
        # which is precisely what passing looks like. Same class as the
        # sub-noise gate in r103: the criterion, not the data, was wrong.
        hi = sC if sC and sC > sN else sN
        print(f"  CONSEQUENCE  σ = {sN:.2f} (ladder N) to {hi:.2f} MHz "
              f"(ladder C, conservative)")
        for lab, d, kind in (
                ("R104: 2.342-mode gap vs TE011", 9.2, "diff"),
                ("R99: TE011 quartz→sapphire", 5.8, "diff"),
                ("R99: TM020 quartz→sapphire", 190.9, "diff"),
                ("R99b: null control B vs C", 0.40, "null")):
            lo_s, hi_s = abs(d) / sN, abs(d) / hi
            if kind == "null":
                ok = abs(d) < 2 * hi
                print(f"    {'✅ PASSES' if ok else '🔴 FAILS'}  {lab}: {d} MHz "
                      f"= {hi_s:.1f}σ — an agreement claim passes by being "
                      f"INSIDE the noise")
            else:
                if abs(d) > 2 * hi:
                    v = "✅ resolved at both σ"
                elif abs(d) > 2 * sN:
                    v = "⚠️ resolved at σ_N only — NOT at the conservative σ"
                else:
                    v = "🔴 UNRESOLVED"
                print(f"    {v}  {lab}: {d} MHz = {lo_s:.1f}σ_N / "
                      f"{hi_s:.1f}σ_C")
    return dict(sigma_n=sN, sigma_c=sC)


def r106(name="r106"):
    """R106's declared criteria. Re-runnable; no solve."""
    idx = json.loads(pathlib.Path(f"{name}.sweep.json").read_text())
    ex = idx["extra"]
    rec, o1, gate = (ex["recorded_offset_mhz"], ex["order1_same_mesh"],
                     ex["convergence_gate_mhz"])
    print("R106 — is offset.te011 = +24.54 still right for the sapphire + "
          "viewport + trap family?\n")
    f2 = {}
    for t in idx["cases"]:
        m, why = _te011(t)
        if m is None:
            print(f"  🔴 {t}: {why}")
            continue
        f2[t] = m["f"]
    if "r106o2f" not in f2:
        print("  🔴 the sf 0.96 order-2 solve is missing — no offset to report")
        return None

    # --- CONVERGENCE first. An unconverged order 2 has no offset worth quoting.
    if "r106o2c" in f2:
        drift = 1e3 * (f2["r106o2f"] - f2["r106o2c"])
        print(f"  CONVERGENCE  order 2 at sf 1.06 → 0.96: {drift:+.3f} MHz")
        print(f"    {'✅' if abs(drift) < gate else '🔴'} against the R105 mesh "
              f"floor {gate} MHz — {'order 2 is converged' if abs(drift) < gate
                 else 'NOT converged; the offset below cannot be quoted'}")
        print(f"    (R38b's original standard was 0.02 MHz between 0.96 and "
              f"0.90, a FINER and less demanding pair than this one)\n")
    else:
        drift = None
        print("  ⚠️ no coarse point — convergence UNTESTED in this family\n")

    # --- PRIMARY. Same mesh, so R105's scatter cancels exactly.
    print("  PRIMARY  offset = f(order 2) − f(order 1), SAME MESH")
    out = {}
    for t, sf in (("r106o2f", 0.96), ("r106o2c", 1.06)):
        if t not in f2:
            continue
        off = 1e3 * (f2[t] - o1[t])
        out[t] = off
        print(f"    sf {sf}:  order1 {o1[t]:.5f} → order2 {f2[t]:.5f}  "
              f"offset {off:+.2f} MHz")
    off96 = out.get("r106o2f")
    d = off96 - rec
    print(f"\n    recorded offset.te011 = {rec:+.2f} MHz  (quartz, no optics)")
    print(f"    measured here          = {off96:+.2f} MHz  (sapphire + viewport "
          f"+ trap)")
    print(f"    difference             = {d:+.2f} MHz "
          f"({100*d/rec:+.0f}% of the recorded value)")
    print("    🔑 this difference is IMMUNE to the R105 mesh floor: both numbers "
          "come\n       from the SAME mesh, and R105 showed the solver is "
          "deterministic to 0.0000 MHz.")
    if abs(d) < 1.0:
        print(f"\n    ✅ the recorded offset SURVIVES the geometry change. "
              "Re-measured, not assumed.")
    else:
        print(f"\n    🔴 THE OFFSET MOVED. Every 'converged' frequency in the "
              "record for this\n       family passes through it, and they are "
              f"all off by {d:+.2f} MHz.")
        print(f"       ⚠️ Band-placement claims are the ones to re-check: ISM "
              "ceiling is 2.500.")
    return dict(offset_sf096=off96, recorded=rec, delta=d, drift=drift)


def _te_tm(tag):
    """TE011 and TM111 by bore signature, with the rule stated in the output.

    Both are bore-H dominant, so bore-H alone cannot separate them. bore-E can:
    R99 measured TE011 at 0.034% and the TM111 candidate at 0.247%, a 7x gap.
    Among the bore-H dominant modes, TE011 is the LOWEST bore-E and TM111 the
    HIGHEST. Deliberately not "the mode below TE011" — with the filter off TM111
    rises toward TE011 and may cross it, and an ordering rule would then swap
    the labels silently.
    """
    ms = results.load(tag)["modes"]
    if len(ms) < 2:
        return None, None, "fewer than two modes in the window"
    hmax = max(m["bore_h"] for m in ms)
    hi = [m for m in ms if m["bore_h"] > 0.5 * hmax]
    if len(hi) < 2:
        return None, None, (f"only {len(hi)} bore-H dominant mode(s) — TM111 "
                            "not in the window, or hybridised")
    te = min(hi, key=lambda m: m["bore_e"])
    tm = max(hi, key=lambda m: m["bore_e"])
    if te is tm:
        return None, None, "TE011 and TM111 resolve to the same mode"
    return te, tm, None


def r107(name="r107"):
    """R107's declared criteria. Re-runnable; no solve."""
    idx = json.loads(pathlib.Path(f"{name}.sweep.json").read_text())
    ex = idx["extra"]
    mats, guard = ex["materials"], ex["degeneracy_guard_mhz"]
    print("R107 — the mode filter, measured SAME-MESH on "
          f"{ex['mesh']} (attribute {ex['filter_attribute']}).")
    print("Labels: among bore-H dominant modes, TE011 = lowest bore-E, "
          "TM111 = highest.\n")
    out = {}
    for t in idx["cases"]:
        eps, tand = mats[t]
        te, tm, why = _te_tm(t)
        if te is None:
            print(f"  🔴 {t} (ε={eps}): {why}")
            continue
        sep = 1e3 * (te["f"] - tm["f"])
        out[t] = dict(eps=eps, tand=tand, f_te=te["f"], q_te=te["Q0"],
                      f_tm=tm["f"], sep=sep, bore_e_te=te["bore_e"],
                      bore_e_tm=tm["bore_e"])
        print(f"  {t:>9}  ε={eps:<5} tanδ={tand:<8}  TE011 {te['f']:.5f} "
              f"Q0={te['Q0']:>8,.0f}  TM111 {tm['f']:.5f}  sep {sep:+7.1f} MHz")
        print(f"{'':13}bore-E: TE011 {100*te['bore_e']:.3f}%  "
              f"TM111 {100*tm['bore_e']:.3f}%")
    print()

    # 🔴 DEGENERACY GUARD — may void the unfiltered case
    for t, d in out.items():
        if abs(d["sep"]) < guard:
            print(f"  🔴 {t}: TE011 and TM111 are {abs(d['sep']):.1f} MHz apart, "
                  f"inside the {guard} MHz degeneracy guard.")
            print("     NOTHING IS MEASURABLE THERE — a 0.16% mesh change swings "
                  "pm/pe by 178%.")
            print("     Q and separation for this case are VOID, not small. "
                  "⚠️ And that IS the\n     argument for the filter: an "
                  "unfiltered cavity is not a working cavity.")
            d["void"] = True
    print()

    ref = out.get("r107qz")
    off = out.get("r107off")
    sa = out.get("r107sa")
    if ref and off and not off.get("void"):
        dq = 100 * (off["q_te"] - ref["q_te"]) / off["q_te"]
        print(f"  PRIMARY  Q cost of the QUARTZ filter, same mesh: {dq:+.2f}%")
        print(f"    claim under test: {ex['q_claim_percent']}% (cross-mesh, "
              f"against a 6.9% cross-mesh Q floor)")
        print(f"    ✅ this number has NO meshing noise — one mesh, deterministic "
              "solver")
    elif off and off.get("void"):
        print("  PRIMARY  🔴 the Q cost CANNOT be quoted: the unfiltered "
              "reference is degenerate.")
        print("    ⚠️ The 5.6% claim compares against a state that is not "
              "measurable, so it was\n       never a well-posed number — "
              "independently of the mesh noise that motivated this run.")
    if ref and sa:
        dq = 100 * (sa["q_te"] - ref["q_te"]) / ref["q_te"]
        dsep = abs(sa["sep"]) - abs(ref["sep"])
        print(f"\n  SAPPHIRE vs QUARTZ filter (same mesh)")
        print(f"    Q0        {ref['q_te']:,.0f} → {sa['q_te']:,.0f}  "
              f"({dq:+.2f}%)")
        print(f"    separation {abs(ref['sep']):.1f} → {abs(sa['sep']):.1f} MHz "
              f"({dsep:+.1f})")
        better = dq > 0 and dsep > 0
        if better:
            print("    ✅ STRICTLY BETTER on both axes — higher ε separates more, "
                  "lower tanδ costs less.\n       The filter should be sapphire, "
                  "and the torch already is.")
        elif dq > 0 or dsep > 0:
            print("    ⚠️ better on one axis only — a trade, not a free win. "
                  "Which axis wins is\n       set by whether Q or separation is "
                  "the binding constraint.")
        else:
            print("    🔴 worse on both — keep quartz.")
    return out


# ---------------------------------------------------------------------------
# METHODOLOGY §2c — the geometry-sweep protocol, made executable.
# Prose in a document is a suggestion; a function that refuses is a rule.
# ---------------------------------------------------------------------------

def insitu_sigma(invariant_ghz):
    """σ in MHz from a quantity whose TRUE value did not change across a sweep.

    🔑 This is the error bar, and it beats a fit residual because a residual
    conflates real nonlinearity with mesh noise and cannot separate them. An
    invariant's drift is noise by construction. Measured on the same meshes as
    the signal, in the same run, for free.

    e.g. f(TM020) across a LENGTH ladder: dTM020/dL = 0 identically (p = 0).
    """
    mhz = [1e3 * f for f in invariant_ghz]
    return _sd(mhz)


def plan_span(sigma_mhz, n, target_slope_err):
    """Span needed for a target σ_slope. METHODOLOGY §2c.

    σ_slope = σ/√Sxx and Sxx ≈ n·W²/12 for n points evenly spread over W.
    Call this BEFORE running: it turns "how fine a sweep do I need" into
    arithmetic instead of a guess, and it usually says the span is impractical.
    """
    return sigma_mhz * (12.0 / n) ** 0.5 / target_slope_err


def sweep_verdict(signal_mhz, sigma_insitu, k=2.0, label="signal"):
    """Refuse a result that does not clear k σ. Returns (ok, message)."""
    if sigma_insitu is None or sigma_insitu <= 0:
        return False, ("🔴 no in-situ σ — the sweep declared no invariant, so it "
                       "has no error bar (METHODOLOGY §2c)")
    n = abs(signal_mhz) / sigma_insitu
    if n >= k:
        return True, f"✅ {label} {signal_mhz:+.2f} MHz = {n:.1f}σ_insitu"
    return False, (f"🔴 {label} {signal_mhz:+.2f} MHz is only {n:.1f}σ_insitu "
                   f"(need {k}σ) — NOT resolved by this sweep")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if "--sweep" in sys.argv:
        idx = json.loads(pathlib.Path(f"{a[0]}.sweep.json").read_text())
        print(f"sweep '{idx['sweep']}': {len(idx['cases'])} cases, "
              f"comparable={idx['comparable']}")
        print(f"  {idx['note']}")
        print(f"\n{'case':>10}{'groove':>14}{'TE f':>9}{'pm/pe':>8}{'Q0':>9}"
              f"{'eta':>7}{'bin1':>8}{'rivals':>8}{'best riv':>10}"
              f"  C1 C2 C3 C4")
        for t in idx["cases"]:
            s = score(t)
            if "error" in s:
                print(f"{t:>10}  🔴 {s['error']}")
                continue
            m = lambda b: "✅" if b else "🔴"
            br = f"{100*s['best_rival_eta']:.1f}%" if s["best_rival_eta"] else "none"
            print(f"{t:>10}{str(s['groove']):>14}{s['te_f']:>9.4f}"
                  f"{s['te_pmpe']:>8.1f}{s['te_Q0']:>9,.0f}"
                  f"{100*s['te_eta']:>6.1f}%{s['b1']:>8.4f}{s['n_rivals']:>8}"
                  f"{br:>10}  {m(s['c1'])} {m(s['c2'])} {m(s['c3'])} {m(s['c4'])}")
        print("\n⚠️ C1 azimuthal ≤ quartz · C2 pm/pe ≥ quartz · C3 Q0 ≥ quartz · "
              "C4 TE011 ≥ 2× best REACHABLE rival")
    else:
        for t in a:
            table(t)
