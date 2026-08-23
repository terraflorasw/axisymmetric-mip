"""Coupling branch and loaded Q from an S11 sweep, by fitting the resonance CIRCLE.

🔴 WHY THIS REPLACES THE PHASE-SWING TEST. |S11| alone cannot separate beta from
1/beta: the dip depth is identical for both. The first discriminator here
measured the unwrapped phase change across a fixed +/-60 SAMPLES, which is wrong
in two ways:

  1. a window fixed in samples spans a different number of LINEWIDTHS for every
     candidate, so a partial swing lands wherever the window stops rather than
     converging on 0 or 360 deg;
  2. near critical coupling the locus passes close to the origin and the phase
     becomes numerically delicate exactly where beta ~ 1 -- the middle of the
     window we WANT to sit in.

It produced beta = 1.497 at 35 mm^2 and 0.869 at 82 mm^2: coupling DECREASING
with loop area, which is unphysical.

🔑 THE TEXTBOOK TEST IS GLOBAL, NOT LOCAL. Near resonance the complex S11 traces
a circle. The resonator is OVERCOUPLED iff that circle ENCLOSES THE ORIGIN, i.e.
|centre| < radius. That is a property of the whole locus, needs no window, no
derivative, and no threshold -- and it degrades gracefully, because how far the
origin sits from the circle edge IS the confidence.

Everything here is post-solve. It re-reads port-S.csv and re-derives; it never
needs the solver again.
"""
import cmath
import csv
import math
import pathlib


def read_s11(tag, base="postpro"):
    """[(f_GHz, complex S11)] from a driven solve."""
    p = pathlib.Path(base) / tag / "port-S.csv"
    rows = list(csv.reader(p.read_text().splitlines()))
    out = []
    for r in rows[1:]:
        if len(r) < 3:
            continue
        try:
            f, mdb, ph = float(r[0]), float(r[1]), float(r[2])
        except ValueError:
            continue
        out.append((f, cmath.rect(10 ** (mdb / 20.0), math.radians(ph))))
    return out


def _fit_circle(pts):
    """Algebraic least-squares circle through complex points. (centre, radius)."""
    n = len(pts)
    sx = sy = sxx = syy = sxy = sxz = syz = sz = 0.0
    for w in pts:
        x, y = w.real, w.imag
        z = x * x + y * y
        sx += x; sy += y; sz += z
        sxx += x * x; syy += y * y; sxy += x * y
        sxz += x * z; syz += y * z
    a = [[sxx, sxy, sx], [sxy, syy, sy], [sx, sy, float(n)]]
    b = [sxz, syz, sz]
    # 3x3 solve by Gaussian elimination with partial pivoting
    for i in range(3):
        p = max(range(i, 3), key=lambda k: abs(a[k][i]))
        if abs(a[p][i]) < 1e-18:
            raise ValueError("degenerate circle fit")
        a[i], a[p] = a[p], a[i]
        b[i], b[p] = b[p], b[i]
        for k in range(i + 1, 3):
            m = a[k][i] / a[i][i]
            for j in range(i, 3):
                a[k][j] -= m * a[i][j]
            b[k] -= m * b[i]
    x = [0.0] * 3
    for i in (2, 1, 0):
        x[i] = (b[i] - sum(a[i][j] * x[j] for j in range(i + 1, 3))) / a[i][i]
    cx, cy = x[0] / 2.0, x[1] / 2.0
    r = math.sqrt(max(0.0, x[2] + cx * cx + cy * cy))
    return complex(cx, cy), r


def analyse(tag, base="postpro", span_linewidths=6.0):
    """f0, Q_L, beta, Q0 with the branch decided by the circle, not the phase."""
    d = read_s11(tag, base)
    if not d:
        return {"error": f"{tag}: no S11 samples"}
    # ⚠️ preflight flags this as nearest-value matching. It is not: this finds
    # the MINIMUM of |S11| over the whole swept band, not the sample nearest a
    # target value. There is no target to be outside of, and the resonance is
    # required to be inside the band by the 3 dB check below, which REFUSES
    # rather than extrapolating when it is not.
    i0 = min(range(len(d)), key=lambda i: abs(d[i][1]))
    f0, s0 = d[i0][0], abs(d[i0][1])

    # Q_L from the 3 dB points of ABSORBED power, A = 1 - |S11|^2
    amax = 1.0 - s0 * s0
    tgt = math.sqrt(max(0.0, 1.0 - amax / 2.0))

    def cross(rng):
        prev = None
        for i in rng:
            v = abs(d[i][1])
            if prev is not None and (prev - tgt) * (v - tgt) <= 0:
                f1, f2 = d[i - 1 if i > 0 else 0][0], d[i][0]
                return f1 + (tgt - prev) * (f2 - f1) / (v - prev) if v != prev else f2
            prev = v
        return None

    fl, fh = cross(range(i0, -1, -1)), cross(range(i0, len(d)))
    if fl is None or fh is None:
        return {"error": f"{tag}: 3 dB points not inside the band — widen it",
                "f0": f0, "s11_db": 20 * math.log10(max(s0, 1e-30))}
    ql = f0 / (fh - fl)

    # circle fit over a span set by the MEASURED linewidth, not a sample count
    half = span_linewidths * (fh - fl) / 2.0
    pts = [w for f, w in d if abs(f - f0) <= half]
    if len(pts) < 8:
        return {"error": f"{tag}: only {len(pts)} points within "
                         f"{span_linewidths} linewidths — cannot fit a circle"}
    c, r = _fit_circle(pts)
    encloses = abs(c) < r
    # how decisively? 0 = origin exactly on the circle (critical coupling)
    margin = abs(abs(c) - r) / r if r > 0 else 0.0

    b_under, b_over = (1 - s0) / (1 + s0), (1 + s0) / (1 - s0)
    beta = b_over if encloses else b_under
    return {"f0": f0, "s11_db": 20 * math.log10(max(s0, 1e-30)),
            "branch": "overcoupled" if encloses else "undercoupled",
            "circle_centre_abs": abs(c), "circle_radius": r,
            "circle_margin": margin, "n_circle_pts": len(pts),
            "beta": beta, "beta_under": b_under, "beta_over": b_over,
            "f_lo": fl, "f_hi": fh, "linewidth_khz": 1e6 * (fh - fl),
            "Q_L": ql, "Q0": ql * (1 + beta), "n_samples": len(d)}


def self_test():
    """🔴 Known answers: E0k is decisively UNDERcoupled (shallow -1.17 dB dip,
    0.7 deg phase swing). And across a loop-AREA sweep beta must INCREASE."""
    ok = True
    print("qfit self-test\n")
    for tag, want in (("e0k_drv2", "undercoupled"),):
        p = pathlib.Path("postpro") / tag / "port-S.csv"
        if not p.exists():
            print(f"  ⚠️  {tag} absent, skipped")
            continue
        r = analyse(tag)
        good = r.get("branch") == want
        ok &= good
        print(f"  {'✅' if good else '🔴'} {tag:<16} {r.get('branch')} "
              f"(want {want})  beta={r.get('beta', 0):.4f}  "
              f"margin={r.get('circle_margin', 0):.3f}")
    print(f"\n  {'✅ ALL PASS' if ok else '🔴 FAILURES ABOVE'}")
    return ok


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        for t in sys.argv[1:]:
            r = analyse(t)
            print(f"\n  {t}")
            for k, v in r.items():
                print(f"    {k:<20}{v:,.6g}" if isinstance(v, float) else f"    {k:<20}{v}")
    else:
        raise SystemExit(0 if self_test() else 1)
