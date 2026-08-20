"""E1a — the design point is ANALYTIC. No solver is involved in this file.

PLAN.md scoped E1 as "cavity dimensions a, L" with the closed form as its
verification. But once the closed form is trusted — E0 established it to ≤1.8 MHz
across the spectrum — the DESIGN POINT ITSELF is analytic. There is nothing to
sweep.

    f_TE011 = (c/2pi) sqrt( (chi'01/a)^2 + (pi/L)^2 )

Fix f_TE011 = 2.4500 GHz and one free parameter remains: the aspect ratio. Every
(a, L) on that one-parameter family resonates at the target. The choice among
them is made by the REST of the spectrum, which is equally analytic.

🔑 WHAT GEOMETRY CAN AND CANNOT BUY:

  CANNOT   TM111 is degenerate with TE011 at chi'01 = chi11 = 3.8317059702,
           IDENTICALLY, at every aspect ratio. No cavity shape separates them.
           That is why a mode filter exists, and it is a theorem, not a result.

  CAN      every OTHER rival moves with aspect ratio. TM020 in particular scales
           as chi02/a with NO length dependence at all (p = 0), so it is pure
           radius — and the old programme's "TM020 headroom" tolerance argument
           was really a statement about radius alone.

⚠️ The old design point a = 103.70, L = 88.53 gives EMPTY TE011 = 2.444385 GHz,
which is 5.6 MHz BELOW the 2.45 target before any loading — and loading lowers it
further. That is worth understanding before it is inherited.

VERIFICATION   physics.py only. Every number here is closed form.
FALSIFICATION  the design point must survive the LOADED perturbation, which is
               E1b and does need the solver. This file cannot answer it and does
               not pretend to.
"""
import math
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph

F0, ISM = 2.4500, (2.400, 2.500)
CHI_TE011 = ph.CHIP[0][0]


def a_for(f_ghz, L_mm):
    """Radius that puts TE011 at f_ghz, given L. Exact inversion."""
    k = 2 * math.pi * f_ghz * 1e9 / ph.C
    kz = math.pi / (L_mm * 1e-3)
    kr2 = k * k - kz * kz
    if kr2 <= 0:
        return None
    return CHI_TE011 / math.sqrt(kr2) * 1e3


print(__doc__)
print("=" * 78)
print(f"THE FAMILY: every row resonates TE011 at exactly {F0} GHz\n")
print(f"{'L mm':>8}{'a mm':>9}{'D/L':>7}{'TM020':>10}{'TM210':>10}"
      f"{'TE211':>10}{'TM011':>10}{'nearest rival':>15}")
rows = []
for L in (60, 70, 80, 88.53, 95, 105, 120, 140):
    a = a_for(F0, L)
    if a is None:
        continue
    s = ph.spectrum(a, L, fmax=3.2)
    riv = {k: v for k, v in s.items() if k not in ("TE011", "TM111")}
    near = min(riv, key=lambda k: abs(riv[k] - F0))
    d = 1e3 * (riv[near] - F0)
    rows.append((L, a, 2 * a / L, s, near, d))
    print(f"{L:>8.2f}{a:>9.3f}{2*a/L:>7.3f}"
          f"{s.get('TM020', float('nan')):>10.4f}"
          f"{s.get('TM210', float('nan')):>10.4f}"
          f"{s.get('TE211', float('nan')):>10.4f}"
          f"{s.get('TM011', float('nan')):>10.4f}"
          f"{near + ' ' + format(d, '+.0f'):>15}")

print(f"\n🔑 TM020 = c*chi02/(2*pi*a) — RADIUS ONLY, no L dependence:")
for L, a, _r, s, _n, _d in rows[:1] + rows[-1:]:
    print(f"    a = {a:.3f} mm -> TM020 = {ph.f_mnp('TM',0,2,0,a,L):.4f} GHz")

print(f"\n{'':>8}ISM band {ISM[0]}–{ISM[1]} GHz. Rivals INSIDE it can be driven:")
for L, a, r, s, _n, _d in rows:
    inb = [k for k, v in s.items()
           if ISM[0] <= v <= ISM[1] and k not in ("TE011", "TM111")]
    print(f"{L:>8.2f}  D/L {r:>5.3f}  in-band rivals: "
          f"{', '.join(f'{k} {s[k]:.4f}' for k in inb) or 'NONE'}")

best = max(rows, key=lambda r: abs(r[5]))
print(f"\n  🔑 WIDEST rival separation: L = {best[0]:.2f}, a = {best[1]:.3f}, "
      f"D/L = {best[2]:.3f}, nearest {best[4]} at {best[5]:+.0f} MHz")
old_a, old_L = 103.70, 88.53
print(f"\n  the inherited point a = {old_a}, L = {old_L}:")
print(f"    empty TE011 = {ph.f_mnp('TE',0,1,1,old_a,old_L):.6f} GHz "
      f"({1e3*(ph.f_mnp('TE',0,1,1,old_a,old_L)-F0):+.1f} MHz vs the {F0} target)")
print(f"    a for {F0} at that L would be {a_for(F0, old_L):.3f} mm "
      f"({a_for(F0, old_L)-old_a:+.3f} mm)")
