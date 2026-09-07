#!/usr/bin/env python3
"""cavity.Q0.loaded and |E| in the plasma, over the (eps, sigma) plane.

🔑 EVALUATION LAYER — no solve. `h3-q0map-01` emits the measurement; every
judgement here (which power, which coupler, what counts as matched) is applied
afterwards and can be re-run when any of them changes. Same split as
fieldcheck.py over h3_loopq.

WHAT IT ANSWERS
  1. cavity.Q0.loaded vs the plasma state -> the CRITICAL-COUPLING CURVE, since
     matched means cavity.Q_ext.loaded = cavity.Q0.loaded.
  2. the |E| profile across the plasma annulus -> whether the field is being
     SHIELDED out of the region the electrons occupy, which is what
     electron-impact dissociation actually depends on.
  3. for a GIVEN coupler, the fraction of incident power reaching the plasma
     across the state -> where delivery collapses, and how wide a tuner range
     the trajectory demands.

⚠️ WHAT IT CANNOT ANSWER: which (eps, sigma) the discharge actually sits at.
That is a plasma question — this maps the cavity's response to a state, not the
state. Nothing here should be read as choosing an operating point.
"""
import json
import math
import pathlib
import sys

from scipy.special import j1

A_MM, CHI01 = 88.0045, 3.8317      # design cavity radius; TE01 cutoff (zero of J1)


def te011_shape(r_mm):
    """|E_phi| ~ J1(chi'01 r/a), normalised at the caller's reference radius.

    ⚠️ chi'01 = 3.8317, NOT 2.405 — see coldfield.py §7cm. The check is that it
    reproduces the design frequency, and h3-field-01 measured the 8.5/4.25 ratio
    at 1.987 against this form's 1.974.
    """
    return j1(CHI01 * r_mm / A_MM)


def rows(slug="h3-q0map-01"):
    f = sorted(pathlib.Path(".").glob(f"{slug}.*.result.json"))
    if not f:
        return []
    d = json.loads(f[-1].read_text())
    out = []
    for p in d.get("points", []):
        w = p.get("wide_fit") or {}
        if not w.get("Q_L"):
            out.append({"eps": p.get("eps"), "sigma": p.get("sigma"),
                        "error": p.get("error") or w.get("error"), "Q_L": None,
                        "probe": p.get("probe_E_named") or {}})
            continue
        b = w.get("beta_undercoupled")
        out.append({
            "eps": p.get("eps"), "sigma": p.get("sigma"), "f0": w.get("f0"),
            "Q_L": w["Q_L"], "lw_mhz": w.get("linewidth_mhz"),
            "s11_db": w.get("s11_db"), "beta_u": b,
            "Q0_u": w.get("Q0_if_undercoupled"), "Q0_o": w.get("Q0_if_overcoupled"),
            "probe": p.get("probe_E_named") or {},
            "probe_r": p.get("probe_r_mm") or {}, "error": None})
    return out


# 🔴 NOTHING MEASURED IS HARDCODED HERE. preflight flagged an earlier draft for
# exactly that (§7bi, the most-repeated rule in this programme): Q_ext = 8735 and
# Q0_cold = 43611 are MEASUREMENTS and belong to the artefact, not to this file.
# ✅ Both are now BOOTSTRAPPED from the run's own vacuum row.
UNSHIELDED_MAX_SIGMA = 0.10    # a CHOICE: rows below this define the baseline law


def calibrate(rs):
    """(Q_ext, Q0_cold, K) from the run itself. No literals.

    🔑 THE VACUUM ROW BREAKS THE BRANCH DEGENERACY BY PHYSICS. With sigma = 0 the
    cavity is the empty grooved design cavity, whose Q0 is ~4e4 — so of the two
    roots the LARGER is Q0 and the smaller is Q_ext. Every other row then
    inherits that Q_ext, and the branch follows.
    """
    vac = next((r for r in rs if r["Q_L"] and r["sigma"] == 0), None)
    if not vac:
        return None, None, None
    q_ext, q0_cold = min(vac["Q0_u"], vac["Q0_o"]), max(vac["Q0_u"], vac["Q0_o"])
    ks = []
    for r in rs:
        if not r["Q_L"] or not (0 < r["sigma"] <= UNSHIELDED_MAX_SIGMA):
            continue
        _n, q0, _q = branch(r["Q0_u"], r["Q0_o"], q_ext)
        ks.append(r["sigma"] / (1.0 / q0 - 1.0 / q0_cold))
    return q_ext, q0_cold, (sum(ks) / len(ks) if ks else None)


def branch(q0_under, q0_over, ref):
    """Pick the branch that keeps cavity.Q_ext geometric.

    🔑 Q0_if_overcoupled == Q_ext_if_undercoupled identically, so across a SERIES
    only one assignment holds a geometric quantity constant. One dip cannot do
    this — the rig says "Q0 not derivable" on every row, correctly.
    """
    if abs(q0_under - ref) <= abs(q0_over - ref):
        return "OVER", q0_over, q0_under
    return "UNDER", q0_under, q0_over


def main():
    rs = rows(sys.argv[1] if len(sys.argv) > 1 else "h3-q0map-01")
    if not rs:
        print("  no artefact yet"); return 0
    print(f"  {'eps':>8}{'sigma':>8}{'f0 GHz':>10}{'Q_L':>10}{'lw MHz':>9}"
          f"{'s11 dB':>8}{'Q0(under)':>11}{'Q0(over)':>10}")
    for r in rs:
        if r["Q_L"] is None:
            print(f"  {r['eps']:>8.4f}{r['sigma']:>8.4f}   🔴 {str(r['error'])[:58]}")
            continue
        print(f"  {r['eps']:>8.4f}{r['sigma']:>8.4f}{r['f0']:>10.5f}{r['Q_L']:>10.1f}"
              f"{r['lw_mhz']:>9.3f}{r['s11_db']:>8.2f}{r['Q0_u']:>11.1f}{r['Q0_o']:>10.1f}")

    # ---- the shielding law ----
    Q_EXT_MAP, Q0_COLD_MAP, K_UNSHIELDED = calibrate(rs)
    if not Q_EXT_MAP:
        print("\n  no vacuum row — cannot calibrate the branch or the law")
        return 0
    print(f"\n  calibrated FROM THIS RUN: Q_ext = {Q_EXT_MAP:,.0f}, "
          f"Q0_cold = {Q0_COLD_MAP:,.0f}, K = {K_UNSHIELDED:.2f} "
          f"(rows with sigma <= {UNSHIELDED_MAX_SIGMA})")
    print(f"\n  {'sigma':>8}{'branch':>7}{'Q0.loaded':>11}{'Q_ext':>9}"
          f"{'Q_plasma':>10}{'s*Q_pl':>9}{'vs K':>8}")
    for r in rs:
        if r["Q_L"] is None:
            continue
        nm, q0, qx = branch(r["Q0_u"], r["Q0_o"], Q_EXT_MAP)
        if r["sigma"] == 0:
            print(f"  {r['sigma']:>8.4f}{nm:>7}{q0:>11,.0f}{qx:>9,.0f}"
                  f"{'—':>10}{'—':>9}{'—':>8}")
            continue
        qp = 1.0 / (1.0 / q0 - 1.0 / Q0_COLD_MAP)
        k = r["sigma"] * qp
        print(f"  {r['sigma']:>8.4f}{nm:>7}{q0:>11,.1f}{qx:>9,.0f}{qp:>10,.1f}"
              f"{k:>9.1f}{(k/K_UNSHIELDED-1)*100:>+7.1f}%")
    print("  A POSITIVE deviation is the plasma absorbing LESS than")
    print("  proportionally — i.e. SHIELDING.")

    # ---- probe shape: is the field being shielded out of the plasma? ----
    have = [r for r in rs if r.get("probe")]
    if have:
        ref = "bore_edge"
        print(f"\n  |E| PROFILE, normalised at {ref}. Closed-form TE011 in the last")
        print("  row; a LOADED row falling BELOW it is the field being shielded")
        print("  out of the region the electrons occupy.\n")
        names = [n for n in ("bore_in", "bore_mid", "bore_edge", "field_peak")
                 if n in have[0]["probe"]]
        print("  " + f"{'sigma':>8}" + "".join(f"{n:>12}" for n in names)
              + f"{'|E| @'+ref:>12}")
        for r in have:
            p, e0 = r["probe"], r["probe"].get(ref)
            if not e0:
                continue
            print(f"  {r['sigma']:>8.4f}"
                  + "".join(f"{p[n]/e0:>12.4f}" for n in names)
                  + f"{e0:>12,.0f}")
        rr = have[0].get("probe_r") or {}
        if rr:
            base = te011_shape(rr[ref])
            print("  " + f"{'TE011':>8}"
                  + "".join(f"{te011_shape(rr[n])/base:>12.4f}" for n in names)
                  + f"{'(closed form)':>12}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
