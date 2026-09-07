#!/usr/bin/env python3
"""|E| inside the torch during the COLD start, from measured Q and coupling.

🔑 EVALUATION LAYER — no solve. It answers one design question: does perfecting
the COLD match buy a field worth having inside the torch? The coupler minimax
(KNOWN.md) traded loaded performance against cold VSWR, so the value of the cold
state has to be a NUMBER, not an intuition.

⚠️ ANALYTIC TE011 IN A BARE CYLINDER. No groove, no quartz torch (eps 9.39), no
loop. E_phi is TANGENTIAL at the torch's cylindrical wall, so it is continuous
across that boundary and the dielectric does not step it — but the dielectric
does perturb the MODE SHAPE, and this does not model that. Indicative only:
`fieldcheck.py` is the authoritative path once a rig records probe fields.

🔴 TE011 HAS NO E ON THE AXIS. E_phi ~ J1(kc r), and J1(0) = 0 identically. The
electric field is zero on the centreline by symmetry and rises with radius, which
is why the numbers are quoted ACROSS the torch bore rather than at its centre.

VERIFICATION   fill time 2Q/omega is reported: if it is << the start window, the
               steady-state numbers are the right ones and there is no transient
               to exploit.
FALSIFICATION  if |E| at a perfect cold match reaches the target, the cold state
               is worth optimising for and the minimax trade was real.
"""
import math
import sys
from scipy.special import j1, jv

A_M, L_M = 0.0880045, 0.1154158        # design cavity
# 🔴 chi'01 = 3.8317, THE FIRST ZERO OF J1 (= J0'), NOT 2.405.
# 2.405 is the first zero of J0 itself — a TM01 constant. This file used it, and
# every |E| it printed on 2026-09-06 was wrong. Caught by reading probecheck.py,
# which states TE011's profile as J1(chi'01 r/a) peaking at r = 0.4805a.
# ✅ THE CHECK THAT WOULD HAVE CAUGHT IT IMMEDIATELY, now in the self-test below:
# the constant must reproduce the cavity's DESIGN FREQUENCY. chi'01 gives
# 2.4500 GHz on a = 88.0045, L = 115.4158 mm; 2.405 gives 1.8404 GHz.
KC_A = 3.8317                           # chi'01 — TE01n cutoff (first zero of J1)


def te011_volume_factor():
    """int|E|^2 dV = E0^2 * V * this. Analytic, so it is checkable by hand.

    ⚠️ At chi'01, J1(KC_A) = 0 by definition, so the general form collapses to
    (a^2/2)*J0(chi'01)^2 — kept in general form so it stays right if KC_A moves.
    """
    j1a = j1(KC_A)
    j1pa = jv(0, KC_A) - j1a / KC_A
    radial = 0.5 * (j1pa ** 2 + (1 - 1 / KC_A ** 2) * j1a ** 2)
    return radial * 0.5                 # * <sin^2(pi z/L)> = 1/2


def self_test():
    """🔴 THE CONSTANT MUST REPRODUCE THE DESIGN FREQUENCY. That single check
    would have caught the 2.405/3.8317 error before any number was quoted."""
    f = 2.99792458e8 / (2*math.pi) * math.sqrt((KC_A/A_M)**2 + (math.pi/L_M)**2)
    assert abs(f - 2.45e9) < 2e6, f"KC_A gives f_TE011 = {f/1e9:.4f} GHz, not 2.45"
    assert abs(j1(KC_A)) < 1e-4, "chi'01 must be a zero of J1"
    print(f"  ✅ self-test: KC_A={KC_A} -> f_TE011 = {f/1e9:.4f} GHz, J1(KC_A)~0")


def e0_from_coupling(p_in_w, beta, q_loaded, f_hz):
    """Peak |E| in the cavity, and the power actually delivered."""
    gamma = (beta - 1.0) / (beta + 1.0)
    p_del = p_in_w * (1.0 - gamma * gamma)
    u = q_loaded * p_del / (2 * math.pi * f_hz)
    v = math.pi * A_M * A_M * L_M
    return math.sqrt(u / (8.854e-12 / 2 * v * te011_volume_factor())), p_del


def e_at_radius(e0, r_m):
    return e0 * j1(KC_A * r_m / A_M)


def main():
    self_test()
    f0, q_l, beta = 2.44245e9, 143.98, 156.178   # h3-betaconv2-0p8 COLD, sf 0.8
    q0 = q_l * (1.0 + beta)
    p_in = 1000.0
    print(f"  design cavity, COLD, barrel loop 11x8 + gap2 2.25 mm, {p_in:.0f} W in")
    print(f"  measured: f0 {f0/1e9:.5f} GHz  Q_L {q_l:.1f}  beta {beta:.1f} "
          f"(overcoupled)  -> Q0 {q0:,.0f}")
    for label, b, ql in (("measured cold", beta, q_l),
                         ("perfect cold match (beta=1)", 1.0, q0 / 2)):
        e0, p_del = e0_from_coupling(p_in, b, ql, f0)
        tau = 2 * ql / (2 * math.pi * f0)
        print(f"\n  {label}: {p_del:.1f} W delivered, fill time {tau*1e9:,.0f} ns")
        print(f"     peak |E| anywhere in the cavity : {e0/1e5:8.4f} kV/cm")
        for r_mm in (0.0, 2.0, 8.5):
            print(f"     |E| at r = {r_mm:4.1f} mm            : "
                  f"{e_at_radius(e0, r_mm/1e3)/1e5:8.4f} kV/cm"
                  + ("   <- axis: ZERO by symmetry" if r_mm == 0 else ""))
    print("\n  ⚠️ analytic bare-cylinder TE011 — indicative, not a measurement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
