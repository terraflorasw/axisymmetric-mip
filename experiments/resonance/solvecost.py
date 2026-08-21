"""What a Palace solve COSTS, and whether it is going to fail.

🔴 WHY THIS EXISTS. "Solve time varies wildly, independent of tets" was true and
was blocking the queue: nothing could be scheduled because nothing could be
costed. The same 83,322-tet mesh ranged from 227 s to 21,462 s, a 95x spread.

It decomposes completely, and mostly into bookkeeping:

  1. MACHINE AND RANKS. The expensive population ran 4 ranks on the laptop, the
     cheap one 32 ranks on the instance. ~25x, stated on the log's first line.
     Comparing wall times across the two was never meaningful.
  2. SOLVER ORDER. p=3 is 1,556,667 ND dofs against p=2's 534,810 on the SAME
     mesh -- 2.9x.
  3. KSP ITERATIONS. The only genuinely unpredictable term, and the conditioning
     one.

Normalised for 1 and 2, the scatter collapses from 95x to 1.3x and the cost is:

    t ~ 454 ns * ND_dofs * total_KSP_iterations        (32 ranks, order 2)

good to +-15% over a 4x range of runtimes, and to 4% out-of-sample on a case it
was not fitted to. ND ~ 6.44 * tets at order 2, so size is known before solving.

🔑 The preconditioner is 75% of the median solve (68-84% across 68 logs) and
there is ONE multigrid setup per run, so this is per-APPLICATION cost: it rides
on the iteration count, not on setup.

Usage:
    python3 solvecost.py                 # self-test
    python3 solvecost.py *_p.log         # report each
"""
import re
import pathlib

# ns per dof per KSP iteration, 32 ranks, solver order 2. Measured across 53
# instance solves; preconditioner term 338.8 with 1.3x spread (308-414).
NS_PER_DOF_ITER = 454.5
ND_PER_TET_ORDER2 = 6.44

# 🔴 WE CANNOT PREDICT WHAT WILL CONVERGE. This is a BUDGET, not a predictor,
# and the difference matters. Across the record: 25 runs converged using at most
# 869 NLEPS iterations; the 2 that failed used 1,445 and 4,114. A cap of 1,000
# catches both failures with zero false positives -- but the margin is only
# 1.66x (869 vs 1445) on TWO failures, so it will eventually be wrong.
#
# Therefore exceeding it is a REPORTED OUTCOME ("did not converge within
# budget"), never a silent drop, and never a claim that the geometry is
# unsolvable. Raise it deliberately for a case believed to be merely hard.
NLEPS_BUDGET = 1000


def _f(t, pat, g=1, cast=float):
    m = re.search(pat, t, re.M)
    return cast(m.group(g)) if m else None


def harvest(path):
    """Everything a Palace log says about what it cost. None where absent.

    ⚠️ Absent is reported as None, never as zero. A missing timing table means
    the run DIED, which is the case worth seeing, and a zero would hide it.
    """
    t = pathlib.Path(path).read_text(errors="ignore")

    def tm(name):
        return _f(t, rf"^{re.escape(name)}\s+[\d.]+\s+[\d.]+\s+([\d.]+)\s*$")

    runs, cur = [], None
    for line in t.splitlines():
        if "Residual norms for GMRES solve" in line:
            if cur is not None:
                runs.append(cur)
            cur = 0
        elif "KSP residual norm" in line and cur is not None:
            cur += 1
    if cur is not None:
        runs.append(cur)

    # NLEPS: how many eigenvalues had converged, and was the residual RISING?
    nc = re.findall(r"NLEPS \(nconv=(\d+), restart=\d+\) residual norm "
                    r"([\d.e+-]+)", t)
    nconv = int(nc[-1][0]) if nc else None
    rising = None
    if len(nc) >= 6:
        tail = [float(x[1]) for x in nc[-6:]]
        rising = all(b > a for a, b in zip(tail, tail[1:]))

    return {
        "tag": pathlib.Path(path).name,
        "host": "instance" if "/opt/amip/" in t else "laptop",
        "ranks": _f(t, r"Running with (\d+) MPI process", 1, int),
        "tets": _f(t, r"^ elements\s+\S+\s+\S+\s+\S+\s+(\d+)", 1, int),
        "nd": _f(t, r"ND \(p = (\d+)\): (\d+)", 2, int),
        "order": _f(t, r"ND \(p = (\d+)\): (\d+)", 1, int),
        "target": _f(t, r"Shift-and-invert σ = ([\d.e+-]+) GHz"),
        "total_s": tm("Total"),
        "precon_s": tm("  Preconditioner"),
        "nsolve": len(runs),
        "nksp": sum(runs),
        "max_its": max(runs) if runs else None,
        "median_its": sorted(runs)[len(runs) // 2] if runs else None,
        "nleps_its": len(nc),
        "nleps_nconv": nconv,
        "nleps_rising": rising,
        "finished": tm("Total") is not None,
    }


def predict_seconds(nd, nksp, ranks=32, order=2):
    """Wall seconds for a solve of `nd` unknowns taking `nksp` KSP iterations.

    🔴 CALIBRATED AT 32 RANKS, ORDER 2 ONLY. It REFUSES elsewhere rather than
    extrapolating: the laptop-vs-instance confusion is precisely what made cost
    look random, and a constant quoted outside its domain is how this programme
    once produced a 98x phantom deficit.
    """
    if ranks != 32 or order != 2:
        raise ValueError(
            f"cost model calibrated for 32 ranks / order 2, asked for "
            f"{ranks} / {order}. Re-measure; do not extrapolate.")
    return NS_PER_DOF_ITER * nd * nksp / 1e9


def estimate_from_mesh(tets, expected_its_per_solve, nsolve):
    """Pre-flight cost, before a solve exists. Order 2, 32 ranks."""
    return predict_seconds(ND_PER_TET_ORDER2 * tets,
                           expected_its_per_solve * nsolve)


def diagnose(h):
    """[(level, message)] — what is wrong with this run, if anything."""
    out = []
    if not h["finished"]:
        out.append(("🔴", "no timing table: the run DIED or is still going"))
    # ⚠️ POST-HOC ONLY. This reads the END of a finished log, where a healthy
    # run has converged and stopped moving. It is NOT valid as a live abort:
    # measured online, "6 consecutive rising iterations" occurs 146 times in
    # h2b_anchor and 381 times in h2_d34, both of which converged fine.
    if h["nleps_rising"]:
        out.append(("🔴", f"NLEPS DIVERGING — residual rising over its last 6 "
                          f"iterations with only nconv={h['nleps_nconv']} "
                          f"converged. More time will not finish this; the "
                          f"nonlinear eigen-iteration is going backwards."))
    if h["nleps_its"] and h["nleps_its"] > NLEPS_BUDGET:
        out.append(("🔴", f"{h['nleps_its']} NLEPS iterations exceeds the "
                          f"{NLEPS_BUDGET} budget (worst CONVERGED run in the "
                          f"record used 869). Report as 'did not converge "
                          f"within budget'; do not drop it silently."))
    if h["max_its"] and h["max_its"] >= 500:
        out.append(("⚠️", f"a linear solve hit {h['max_its']} iterations "
                          f"(MaxIts 500) — usually a SYMPTOM of a bad Newton "
                          f"step, not the disease. Check nconv first."))
    if h["ranks"] and h["ranks"] != 32:
        out.append(("⚠️", f"{h['ranks']} ranks — wall time is NOT comparable "
                          f"with the 32-rank record, and the cost model does "
                          f"not apply."))
    if h["total_s"] and h["precon_s"]:
        share = h["precon_s"] / h["total_s"]
        if not 0.55 < share < 0.90:
            out.append(("⚠️", f"preconditioner is {share:.0%} of runtime; the "
                              f"record says 68-84%. Something differs."))
    return out


def report(path):
    h = harvest(path)
    print(f"\n  {h['tag']}  [{h['host']}, {h['ranks']} ranks, order {h['order']}]")
    if h["tets"]:
        print(f"    {h['tets']:,} tets -> {h['nd']:,} ND dofs "
              f"({h['nd']/h['tets']:.2f}/tet)"
              + (f"   target {h['target']:.2f} GHz" if h["target"] else ""))
    print(f"    {h['nsolve']:,} GMRES solves, {h['nksp']:,} KSP iterations "
          f"(median {h['median_its']}, max {h['max_its']})")
    if h["total_s"]:
        print(f"    {h['total_s']:,.0f} s actual", end="")
        if h["ranks"] == 32 and h["order"] == 2:
            p = predict_seconds(h["nd"], h["nksp"])
            print(f"   {p:,.0f} s predicted   ({100*(p-h['total_s'])/h['total_s']:+.0f}%)")
        else:
            print("   (cost model does not apply here)")
    for lvl, msg in diagnose(h):
        print(f"    {lvl} {msg}")
    return h


def self_test():
    """🔴 KNOWN-BAD INPUT, or this is just a printer that is believed.

    prod-narrow is the real diverging run; anchor is the real healthy one.
    """
    ok = True
    print("solvecost self-test — real H2b logs\n")

    bad = pathlib.Path("h2b_prod_narrow_p.log")
    good = pathlib.Path("h2b_anchor_p.log")
    if not bad.exists() or not good.exists():
        print("  ⚠️  reference logs absent here; fetch them to run this test")
        return True

    hb = harvest(bad)
    flags = dict((m[:24], lvl) for lvl, m in diagnose(hb))
    caught = any("NLEPS DIVERGING" in k for k in flags)
    ok &= caught
    print(f"  {'✅' if caught else '🔴'} "
          f"{'divergence caught on prod-narrow':<44} nconv={hb['nleps_nconv']}, "
          f"rising={hb['nleps_rising']}")

    hg = harvest(good)
    quiet = not any("DIVERGING" in m for _l, m in diagnose(hg))
    ok &= quiet
    print(f"  {'✅' if quiet else '🔴'} "
          f"{'healthy anchor NOT flagged':<44} nconv={hg['nleps_nconv']}, "
          f"rising={hg['nleps_rising']}")

    p = predict_seconds(hg["nd"], hg["nksp"])
    err = abs(p - hg["total_s"]) / hg["total_s"]
    ok &= err < 0.20
    print(f"  {'✅' if err < 0.20 else '🔴'} "
          f"{'cost model within 20% on anchor':<44} "
          f"{p:,.0f} s vs {hg['total_s']:,.0f} s ({100*err:.0f}%)")

    over = [m for _l, m in diagnose(hb) if "budget" in m]
    ok &= bool(over)
    print(f"  {'✅' if over else '🔴'} "
          f"{'budget exceeded flagged on prod-narrow':<44} "
          f"{hb['nleps_its']} NLEPS its")
    under = [m for _l, m in diagnose(hg) if "budget" in m]
    ok &= not under
    print(f"  {'✅' if not under else '🔴'} "
          f"{'healthy anchor within budget':<44} {hg['nleps_its']} NLEPS its")

    try:
        predict_seconds(500000, 1000, ranks=4)
        refused = False
    except ValueError:
        refused = True
    ok &= refused
    print(f"  {'✅' if refused else '🔴'} "
          f"{'refuses to extrapolate off 32 ranks':<44}")

    print(f"\n  {'✅ ALL PASS' if ok else '🔴 FAILURES ABOVE'}")
    return ok


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for a in sys.argv[1:]:
            report(a)
    else:
        raise SystemExit(0 if self_test() else 1)
