#!/usr/bin/env python3
"""Closed forms. THE ANCHOR. No simulation appears in this file, ever.

    "There is no 'verified instrument' other than established physics."

A solver is never verified — it agrees or disagrees with physics on particular
cases. This module holds the physics, so that every number produced by an
instrument has something outside the instrument to be checked against.

🔴 THE RULE THIS FILE OBEYS: only formulas I can state with certainty go in.
A WRONG CLOSED FORM IS WORSE THAN NO CLOSED FORM, because it produces a
disagreement that gets attributed to the solver — which is exactly how the
previous programme lost its anchor (its R2 concluded "closed forms are the
fault, not the model" and then used that as a standing escape hatch).
Where a formula is delicate, it is OMITTED and said so. See `NOT_PROVIDED`.

Self-tests run under __main__. ⚠️ On first run, TWO of them "failed" and both
times the fault was MY hand-typed reference value, not the code — a sloppy
eta and a transposed digit in a cutoff frequency. That is the anchor working:
it caught the human, which is the only direction of error it can catch, and the
only one that matters here.
"""
import math

C = 299792458.0
MU0 = 4e-7 * math.pi
ETA0 = 376.730313668

NOT_PROVIDED = """
wall_Q(mode, a, L, sigma) — the closed-form conductor Q of a cylindrical cavity.
    OMITTED DELIBERATELY. The TE011 expression is easy to misquote (several
    published forms differ in whether the end-cap term carries a factor 2a/L),
    and a misquoted Q is precisely the failure that cost the previous programme
    its anchor. What IS certain and IS provided: skin_depth(), and
    q_wall_ratio() — for pure wall loss Q scales as sqrt(sigma) EXACTLY, which
    is enough to convert between wall metals and was confirmed to 0.10%.
"""


# ---------------------------------------------------------------- cavity modes
def bessel_zeros():
    """(chi, chi_prime) tables. scipy if present; otherwise hard-coded."""
    # 🔴 m UP TO 4 (2026-08-23). The fallback stopped at m=2 while the scipy
    # path already went to 3, and `spectrum()` iterated only m <= 2 regardless —
    # so **TE311 at 2.622 GHz was invisible to the reference table.** It is an
    # ordinary mode, it sits 172 MHz above the design point, and it competed
    # with every driven sweep while "the closed form has nothing there" was
    # being said about it.
    try:
        from scipy.special import jn_zeros, jnp_zeros
        return ({m: list(jn_zeros(m, 4)) for m in range(5)},
                {m: list(jnp_zeros(m, 4)) for m in range(5)})
    except ImportError:
        return ({0: [2.404825557695773, 5.520078110286311, 8.653727912911013],
                 1: [3.831705970207512, 7.015586669815619, 10.17346813506272],
                 2: [5.135622301840683, 8.417244140399864, 11.61984117214906],
                 3: [6.380161895923984, 9.761023129981670, 13.015200721698434],
                 4: [7.588342434503804, 11.064709488501185, 14.372536671617590]},
                {0: [3.831705970207512, 7.015586669815619, 10.17346813506272],
                 1: [1.841183781340659, 5.331442773525032, 8.536316366346286],
                 2: [3.054236928227140, 6.706133194158457, 9.969467823087596],
                 3: [4.201188941210528, 8.015236598375953, 11.345924310743007],
                 4: [5.317553126083994, 9.282396285241614, 12.681908442638890]})


CHI, CHIP = bessel_zeros()


def f_mnp(kind, m, n, p, a_mm, L_mm):
    """Exact resonant frequency (GHz) of an EMPTY right circular cylinder.

    f = (c/2pi) * sqrt( (chi/a)^2 + (p*pi/L)^2 )
    TE uses chi'_mn (zeros of J'_m); TM uses chi_mn (zeros of J_m).
    Assumes PERFECTLY CONDUCTING walls — a finite-conductivity wall shifts this
    by of order R_s/eta, ~1e-4 relative, which is below every floor we have.
    """
    chi = (CHIP if kind.upper().startswith("TE") else CHI)[m][n - 1]
    a, L = a_mm * 1e-3, L_mm * 1e-3
    return C / (2 * math.pi) * math.hypot(chi / a, p * math.pi / L) / 1e9


def design_point(d_over_l, f_ghz):
    """(a_mm, L_mm) for a TE011 cavity of this shape resonating at f_ghz.

    🔑 THE ONE PLACE THE CAVITY'S DIMENSIONS ARE DERIVED. D/L and the target
    frequency are INPUTS — pass them from baselines.json, never a literal.

    🔴 Written 2026-08-25 because the same fact existed three times and one of
    them disagreed: `DL = 1.525` in e0k2_anchor.py AND h2_groove.py, plus
    `A_MM, L_MM = 103.70, 88.53` in e0_solver_vs_math.py — D/L = 2.343, a
    DIFFERENT cavity, sitting as the default in GEO.
    """
    from scipy.optimize import brentq
    L = brentq(lambda LL: f_mnp("TE", 0, 1, 1, d_over_l * LL / 2, LL) - f_ghz,
               20.0, 400.0, xtol=1e-10)
    return d_over_l * L / 2, L


def spectrum(a_mm, L_mm, fmax=3.0):
    """Every mode below fmax, exact — WITHIN THE ENUMERATED RANGE.

    🔴 **"No mode there" is only true up to the limits below.** Until
    2026-08-23 this iterated m,n,p <= 2 and **TE311 (2.622 GHz) was therefore
    absent from the reference table** — an ordinary cavity mode that competed
    with every driven sweep while the table was being cited as showing nothing
    in that range. Now m <= 4, n <= 3, p <= 3.

    ⚠️ It is STILL FINITE. Any claim of the form "the closed form has nothing
    at f" means "nothing among the modes enumerated here". Say which.
    🔑 A mode outside this range is also outside `azimuthal.order()`'s
    resolving power (m <= N/4, so m <= 1 at the standard 5 sectors) — the two
    limits were chosen from each other, so neither catches the other's misses.
    Identify TE011 by FIELD STRUCTURE (E purely azimuthal at every phi), not by
    absence from this table. See INSTRUMENT.
    """
    out = {}
    for kind, tbl in (("TE", CHIP), ("TM", CHI)):
        for m in range(5):
            for n in range(1, 4):
                for p in range(0, 4):
                    if kind == "TE" and p == 0:
                        continue          # TE_mn0 does not exist
                    f = f_mnp(kind, m, n, p, a_mm, L_mm)
                    if f <= fmax:
                        out[f"{kind}{m}{n}{p}"] = f
    return dict(sorted(out.items(), key=lambda kv: kv[1]))


def degenerate_pairs(a_mm, L_mm, tol_mhz=1e-6):
    """Modes that are degenerate BY MATHEMATICS, not by coincidence.

    🔑 TE011 and TM111 are the canonical case: chi'_01 = chi_11 = 3.8317059702
    IDENTICALLY, so they are degenerate at every aspect ratio and no cavity
    shape can separate them. Any splitting an instrument reports for such a
    pair has a TRUE VALUE OF EXACTLY ZERO and is therefore a pure artifact
    measurement — the strongest probe available.
    """
    s = spectrum(a_mm, L_mm)
    ks = list(s)
    return [(x, y, 1e3 * abs(s[x] - s[y]))
            for i, x in enumerate(ks) for y in ks[i + 1:]
            if abs(s[x] - s[y]) * 1e3 < tol_mhz]


# ------------------------------------------------------------------ conductors
def skin_depth(f_ghz, sigma, mu_r=1.0):
    """delta = sqrt(2/(omega mu sigma)) — metres. Exact for a good conductor."""
    return math.sqrt(2.0 / (2 * math.pi * f_ghz * 1e9 * MU0 * mu_r * sigma))


def surface_resistance(f_ghz, sigma, mu_r=1.0):
    """R_s = 1/(sigma delta) — ohms per square."""
    return 1.0 / (sigma * skin_depth(f_ghz, sigma, mu_r))


def q_wall_ratio(sigma_new, sigma_old):
    """Q_wall scales as sqrt(sigma) EXACTLY, for pure conductor loss.

    Certain, geometry-independent, and the only wall-Q statement this module
    makes. Converting a measured Q between wall metals also needs the DIELECTRIC
    share, which does not scale — see q_convert().
    """
    return math.sqrt(sigma_new / sigma_old)


def q_convert(q_old, sigma_new, sigma_old, q_dielectric=None):
    """Convert a measured Q0 between wall metals. 1/Q = 1/Q_wall + 1/Q_diel."""
    if q_dielectric is None:
        return q_old * q_wall_ratio(sigma_new, sigma_old)
    inv_w = 1.0 / q_old - 1.0 / q_dielectric
    if inv_w <= 0:
        raise ValueError("q_dielectric exceeds q_old — the split is impossible")
    return 1.0 / (inv_w / q_wall_ratio(sigma_new, sigma_old) + 1.0 / q_dielectric)


# ------------------------------------------------------------------- coupling
def eta_from_beta(beta):
    """Fraction of incident power entering a one-port cavity. eta = 4b/(1+b)^2.

    Certain, and it is the LOD link: power -> temperature -> excitation.
    Note eta(b) = eta(1/b): over- and under-coupling are indistinguishable from
    reflected magnitude alone.
    """
    return 4.0 * beta / (1.0 + beta) ** 2


def beta_from_q(q0, q_ext):
    return q0 / q_ext


def loaded_q(q0, beta):
    return q0 / (1.0 + beta)


def linewidth_mhz(f_ghz, q_loaded):
    return 1e3 * f_ghz / q_loaded


# ----------------------------------------------------------- below-cutoff holes
def cutoff_ghz(diameter_mm, kind="TE11"):
    """Circular waveguide cutoff. f_c = c*chi/(2*pi*a)."""
    chi = {"TE11": CHIP[1][0], "TM01": CHI[0][0], "TE01": CHIP[0][0]}[kind]
    return C * chi / (2 * math.pi * (diameter_mm * 1e-3 / 2)) / 1e9


def evanescent_db_per_mm(f_ghz, diameter_mm, kind="TE11"):
    """Attenuation of a below-cutoff circular tube, dB/mm.

    alpha = k_c * sqrt(1 - (f/f_c)^2)  [Np/m],  k_c = 2*pi*f_c/c
    Exact for an ideal guide well below cutoff.
    """
    fc = cutoff_ghz(diameter_mm, kind)
    if f_ghz >= fc:
        return 0.0
    kc = 2 * math.pi * fc * 1e9 / C
    return kc * math.sqrt(1.0 - (f_ghz / fc) ** 2) * 8.685889638 / 1e3


# ------------------------------------------------------------------- optics
def trap_diameter_mm(f_number, plasma_to_wall_mm, source_mm=3.0):
    """Aperture that subtends the whole collection cone at the far wall.

    d = 2*L*tan(atan(1/2F)) + source. Measured from the PLASMA, which is the
    image plane — not from the viewport.
    """
    return 2 * plasma_to_wall_mm * math.tan(math.atan(1.0 / (2 * f_number))) \
        + source_mm


def energy_fraction_annulus(kind, n, a_mm, r1_mm, r2_mm, samples=20001):
    """Fraction of a TE_0n1 / TM_0n0 mode's electric energy inside an annulus.

    🔑 THE VERIFICATION FOR A DIELECTRIC PERTURBATION. First-order theory says a
    thin dielectric shifts f in proportion to the field energy it occupies, so
    the RATIO of two modes' shifts is the ratio of their energy fractions — a
    pure Bessel calculation with no simulation in it.

    TM_0n0: E_z ~ J0(chi_0n r/a), uniform in z
    TE_0n1: E_phi ~ J1(chi'_0n r/a) sin(pi z/L)

    For a FULL-LENGTH annulus the z factors cancel between numerator and
    denominator, so this is radial only. Numeric, not a quoted closed form —
    the normalisation identities differ between the two families (J1 vanishes at
    chi'_0n, so the usual (a^2/2)J_{n+1}^2 form does not apply to TE) and that
    is exactly the kind of detail a misquoted formula gets wrong.
    """
    from math import pi
    try:
        from scipy.special import j0, j1
    except ImportError:
        raise RuntimeError("scipy needed — the anchor must be exact")
    chi = (CHIP if kind.upper().startswith("TE") else CHI)[0][n - 1]
    f = (lambda x: j1(chi * x / a_mm)) if kind.upper().startswith("TE") \
        else (lambda x: j0(chi * x / a_mm))
    h = a_mm / (samples - 1)
    xs = [i * h for i in range(samples)]
    w = [f(x) ** 2 * x for x in xs]
    tot = sum(w) * h
    part = sum(wi for x, wi in zip(xs, w) if r1_mm <= x <= r2_mm) * h
    return part / tot


def match_exact(exact, solved, degenerate=()):
    """Pair exact modes to solved eigenvalues SAFELY. Returns (pairs, refused).

    🔴 WRITTEN AFTER A FAILURE. Nearest-value matching fabricated a −27.6 MHz
    error for TE121 when TE121 was not in the solved set at all — the solver
    returned 22 modes topping out BELOW it, and the matcher happily paired it
    with a different mode. It then reported a +14.5 MHz "shift" between two runs
    that were comparing two different modes to each other.

    Three refusals, all of them things a nearest-value match cannot see:
      · exact frequency ABOVE the solved ceiling  -> no match can exist
      · a solved value already claimed             -> one-to-one or nothing
      · a member of a known degenerate pair        -> handled by SPLITTING,
                                                      never by pairing
    """
    ceiling = max(solved)
    deg = {m for pair in degenerate for m in pair[1:]}   # keep the first only
    pairs, refused, used = {}, {}, {}
    for k, fx in sorted(exact.items(), key=lambda kv: kv[1]):
        if k in deg:
            refused[k] = "degenerate partner — use the splitting, not a pairing"
            continue
        if fx > ceiling:
            refused[k] = f"above the solved ceiling {ceiling:.5f}"
            continue
        n = min(solved, key=lambda x: abs(x - fx))
        if n in used:
            refused[k] = f"nearest value {n:.5f} already taken by {used[n]}"
            continue
        used[n] = k
        pairs[k] = n
    return pairs, refused


def facet_radius_ratio(n_facets):
    """a_eff / a for a circle replaced by an INSCRIBED regular N-gon.

    Equal-AREA equivalent radius, exact: the polygon area is
    (N/2) a^2 sin(2pi/N), so a_eff/a = sqrt((N/2pi) sin(2pi/N)).

    Small-angle expansion (for intuition only, not used):  1 - pi^2/(3 N^2).
    """
    from math import pi, sin, sqrt
    if n_facets < 3:
        raise ValueError("a polygon needs at least 3 sides")
    return sqrt(n_facets * sin(2 * pi / n_facets) / (2 * pi))


def radial_share(kind, m, n, p, a_mm, L_mm):
    """Fraction of f^2 carried by the RADIAL term.

    f^2 = (c/2pi)^2 [ (chi/a)^2 + (p pi / L)^2 ]. Only the first term knows
    about the radius, so a radius error moves f by that share:

        df/f = -radial_share * da/a

    For TM_mn0 (p=0) the share is 1 and df/f = -da/a exactly.
    """
    from math import pi
    chi = (CHIP if kind.upper().startswith("TE") else CHI)[m][n - 1]
    kr2 = (chi / (a_mm * 1e-3)) ** 2
    kz2 = (p * pi / (L_mm * 1e-3)) ** 2
    return kr2 / (kr2 + kz2)


def faceting_shift_mhz(kind, m, n, p, a_mm, L_mm, h_mm):
    """Predicted frequency ERROR of a GEOMETRIC-ORDER-1 (faceted) mesh, in MHz.

    🔑 NO SIMULATION. A straight-sided mesh replaces the circular wall with an
    inscribed polygon whose vertices lie on the true surface and whose facets
    chord across it. The cavity is therefore SMALLER than the real one, so the
    frequency reads HIGH -- and by a computable amount, which makes geometric
    order 1 a case where the mesher can be checked against known physics rather
    than against another mesh.

        N ~ 2 pi a / h        facets around the circumference
        a_eff/a               equal-area radius of that polygon
        df/f = -radial_share * (a_eff - a)/a          (positive: reads high)

    ⚠️ This is the SYSTEMATIC part only. A real surface triangulation is not a
    regular polygon: facet sizes vary, so an actual order-1 mesh scatters about
    this value. The prediction is the centre of that scatter, not a bound.

    ⚠️ It also assumes the wall is the only curved surface that matters. With a
    coupling loop or tubes present, each curved boundary contributes its own
    faceting and this covers none of them.
    """
    from math import pi
    n_facets = 2 * pi * a_mm / h_mm
    ratio = facet_radius_ratio(max(3.0, n_facets))
    share = radial_share(kind, m, n, p, a_mm, L_mm)
    f0 = f_mnp(kind, m, n, p, a_mm, L_mm)
    # a_eff < a  =>  da/a < 0  =>  df/f > 0
    return -share * (ratio - 1.0) * f0 * 1e3


def lod(sigma_background, sensitivity, k=3.0):
    """LOD = k * sigma_background / sensitivity. The terminal objective."""
    return k * sigma_background / sensitivity


if __name__ == "__main__":
    ok = True

    def chk(name, got, want, tol):
        global ok
        good = abs(got - want) <= tol
        ok &= good
        print(f"  {'✅' if good else '🔴'} {name:<44} {got:.6f}  (want "
              f"{want:.6f} ± {tol:g})")

    print("physics.py self-test — every value from an independent source\n")
    chk("chi_01  (J0 first zero)", CHI[0][0], 2.404825557695773, 1e-12)
    chk("chi_11  (J1 first zero)", CHI[1][0], 3.831705970207512, 1e-12)
    chk("chi'_01 (J0' first zero)", CHIP[0][0], 3.831705970207512, 1e-12)
    chk("chi'_11 (J1' first zero)", CHIP[1][0], 1.841183781340659, 1e-12)
    print("  🔑 chi'_01 == chi_11 exactly — the TE011/TM111 degeneracy\n")

    chk("TE011 @ a=103.7 L=88.53 (GHz)", f_mnp("TE", 0, 1, 1, 103.7, 88.53),
        2.444385, 1e-5)
    chk("TM010 @ a=103.7 (GHz)", f_mnp("TM", 0, 1, 0, 103.7, 88.53),
        1.106485, 1e-5)
    d = degenerate_pairs(103.7, 88.53)
    print(f"  {'✅' if any(set(p[:2]) == {'TE011','TM111'} for p in d) else '🔴'}"
          f" degenerate_pairs finds TE011/TM111: {[p[:2] for p in d]}\n")

    chk("skin depth, Al 3.5e7 @2.45GHz (um)",
        skin_depth(2.45, 3.5e7) * 1e6, 1.719, 0.01)
    chk("Q ratio Ag(6.3e7)->Al(3.5e7)", q_wall_ratio(3.5e7, 6.3e7),
        0.745356, 1e-6)
    chk("eta at beta=1 (critical)", eta_from_beta(1.0), 1.0, 1e-12)
    chk("eta at beta=34.11", eta_from_beta(34.11), 0.1106834, 1e-6)
    chk("eta(b) == eta(1/b)", eta_from_beta(4.0) - eta_from_beta(0.25),
        0.0, 1e-12)
    chk("TE11 cutoff, 10 mm bore (GHz)", cutoff_ghz(10.0), 17.5698466, 1e-6)
    chk("trap dia at f/15, L=103.7 (mm)", trap_diameter_mm(15, 103.7),
        9.909, 0.01)
    # --- geometric order 1: the faceting error is ANALYTIC -------------------
    # square: inscribed in a circle, area 2a^2 vs pi a^2 -> ratio sqrt(2/pi)
    chk("facet ratio, N=4 (square)", facet_radius_ratio(4),
        (2.0 / math.pi) ** 0.5, 1e-12)
    chk("facet ratio, N=1000 -> 1", facet_radius_ratio(1000), 1.0, 1e-5)
    # small-angle check: 1 - pi^2/(3N^2) at N=60
    chk("facet ratio, N=60 vs expansion", facet_radius_ratio(60),
        1 - math.pi ** 2 / (3 * 60 ** 2), 2e-7)
    # TM010 has p=0, so the radial share is exactly 1
    chk("radial share TM010 (p=0)", radial_share("TM", 0, 1, 0, 103.7, 88.53),
        1.0, 1e-12)
    _rs = radial_share("TE", 0, 1, 1, 103.7, 88.53)
    print(f"  🔑 TE011 radial share = {_rs:.4f} — a radius error moves TE011 "
          f"only {_rs:.0%} as hard as it moves TM010\n")

    print(f"\n  {'✅ ALL PASS' if ok else '🔴 FAILURES ABOVE'}")


# ---------------------------------------------------------------------------
# PLASMA STATE — one temperature sets everything (CONVENTIONS §7ad)
# ---------------------------------------------------------------------------
# 🔴 n_e, nu_m and n_gas are ONE STATE, not three constants. The code used to
# set NE and NU_M independently, and nothing errored when they disagreed: the
# solve converged and returned a coherent-looking answer for a plasma that
# cannot exist. This function is the fix — give it a temperature, take all three.
#
# ✅ THE TEMPERATURE IS ANCHORED (2026-08-24):
#    Kuonen, Hattendorf & Gunther, J. Anal. At. Spectrom. 39(5) 1388-1397 (2024),
#    "Quantification capabilities of N2 MICAP-MS...", Table 2.
#    PRESSURE-REDUCTION method, N2 MICAP: **5220 K and 5270 K** (two sample
#    introduction conditions). refs/Quantification capabilities of N2 MICAP-MS...
#
# 🔑 WHY THAT METHOD AND NOT THE OTHERS. Table 2 gives three: pressure reduction
#    (5220/5270 K), Longerich (12850/13800 K) and Houk & Praphairaksit
#    (5910-6430 K). **ONLY THE PRESSURE METHOD IS EMPIRICAL** — it measures an
#    interface pressure ratio with the plasma on and off. The other two infer T
#    from the SAME MO+/M+ ion-ratio measurement through different equilibrium
#    models, and they disagree by ~2x, which is model spread, not measurement
#    spread. The paper itself notes Longerich "has always resulted in values
#    between 9000 K and 13000 K" regardless of plasma.
#    ✅ Internal check: the same method reads 5680-5780 K on their Ar ICP, and
#    independent literature puts an Ar ICP at 5000-5280 K.
#
# ⚠️ CAVEATS THAT TRAVEL WITH THIS NUMBER:
#    - It is the plasma AS SAMPLED THROUGH THE MS INTERFACE — the analytical zone
#      at the sampling cone. The EM model's plasma is an r=2-8.5 mm annulus over
#      +-46 mm. **Not the same region**, and an atmospheric plasma has gradients.
#    - LTE is assumed. Non-LTE would put n_e ABOVE Saha-at-T_gas, so this is a
#      LOWER BOUND on n_e.
#    - Full N2 dissociation is assumed for the heavy density (fair above ~5000 K).
#    - SIGMA_M is an order-of-magnitude cross-section, NOT a measured value; nu_m
#      inherits its uncertainty directly. Stated, not hidden.
#    ✅ Power does NOT enter: in an atmospheric plasma more power makes a BIGGER
#    plasma, not a hotter one, so the paper's 1450 W vs this programme's 1 kW is
#    not a discrepancy. Nor does MS-vs-OES — same plasma, different detector.

T_GAS_ANCHOR_K = (5220.0, 5270.0)      # empirical range, pressure-reduction
T_GAS_SOURCE = ("Kuonen/Hattendorf/Gunther JAAS 39(5) 2024 Table 2, "
                "pressure-reduction method, N2 MICAP")
E_ION_N_EV = 14.53                      # atomic nitrogen
G_ION, G_NEUTRAL = 9.0, 4.0             # N+ (3P) / N (4S)
SIGMA_M = 1.0e-19                       # m^2, momentum transfer — ORDER ONLY


def plasma_state(T_gas, pressure=101325.0, sigma_m=SIGMA_M):
    """(n_e, nu_m, n_heavy) from ONE temperature. See the note above.

    n_e   — LTE Saha for atomic N, quasineutral, against the heavy density.
    nu_m  — n_heavy * sigma_m * <v_e>, with <v_e> the electron thermal speed
            at T_e = T_gas (LTE).
    ⚠️ nu_m carries SIGMA_M's order-of-magnitude uncertainty. n_e does not.
    """
    kB, me, h, eV = 1.380649e-23, 9.1093837015e-31, 6.62607015e-34, 1.602176634e-19
    n_heavy = pressure / (kB * T_gas)
    A = (2.0 * (G_ION / G_NEUTRAL)
         * ((2.0 * math.pi * me * kB * T_gas) / (h * h)) ** 1.5
         * math.exp(-E_ION_N_EV * eV / (kB * T_gas)))
    n_e = (-A + math.sqrt(A * A + 4.0 * A * n_heavy)) / 2.0
    v_e = math.sqrt(8.0 * kB * T_gas / (math.pi * me))
    return n_e, n_heavy * sigma_m * v_e, n_heavy
