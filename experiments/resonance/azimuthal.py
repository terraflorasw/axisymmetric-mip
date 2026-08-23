"""Azimuthal order m from sector energies — an EXACT mode discriminator.

🔴 WHY THIS EXISTS. Identifying a driven resonance by matching its energy
fingerprint to a reference library is a SIMILARITY SCORE WITH A THRESHOLD, and
it is thin exactly where we need it: measured margin over the best alternative
was 58.8x, 33.5x, 26.0x, then **4.5x** at the weakest coupling — and weak
coupling is the regime we want for a non-perturbing probe. A threshold that was
calibrated on the easy case (mode ABSENT) silently accepted a false match at
0.00397 while set to 0.010.

🔑 BUT TE011 AND TM111 DIFFER BY SYMMETRY, NOT BY DEGREE. TE011 is m=0,
azimuthally uniform. TM111 is m=1, going as cos(phi) and doubly degenerate. That
is a structural difference and it can be measured directly.

For a field ~ cos(m*phi), the ENERGY goes as cos^2(m*phi) = (1 + cos(2m*phi))/2.
So the azimuthal energy pattern is:

    m = 0   ->  flat.                      A2/A0 = 0
    m = 1   ->  one full cos(2phi) cycle.  A2/A0 = 0.5 for a pure polarisation
    m = 2   ->  cos(4phi).                 4th harmonic

with A_k the k-th angular harmonic of the per-sector energies. This needs NO
reference library, NO threshold calibrated on four points, and NO eigen solve —
only that the mesh carries azimuthal sectors.

⚠️ `geometry.py --sectors` already does this and its own help says "5 resolves
m=1..4". GEO sets `--sectors 1`, which throws it away, and NO solve in the
record has azimuthal bins. The capability was built and then disabled.

🔴 CHOOSING N IS A LOOKUP, NOT A GUESS — AND ALIASING IS REAL. Mode m lands on
angular harmonic k = 2m, and with N sectors k folds to min(k%N, N-k%N):

    N     m=0  m=1  m=2  m=3  m=4  m=5      resolves
    3,4,6   collisions among m=0,1,2         🔴 unusable
    5      0    2    1    1    2    0        m=0,1,2 only  (m=4 == m=1, m=5 == m=0)
    9      0    2    4    3    1    1        m=0..4        ✅
    11     0    2    4    5    3    1        m=0..4        ✅

⚠️ `geometry.py`'s help once claimed "5 resolves m=1..4". It does not: at N=5,
m=4 aliases onto m=1 and m=5 onto m=0. Corrected there.

✅ THE PROCEDURE: ask `physics.spectrum()` which modes lie in the solve window
and take their m. For the H1 cavity over 2.25-2.80 GHz that is TE011 (m=0),
TM111 (m=1), TE112 (m=1), TM210 (m=2) — so m in {0,1,2} and N=5 suffices. Then
add margin, because slot resonances, loop resonances and hybrids are NOT in the
closed form and can carry high m. **N=9 is the smallest that separates m=0..4**
and costs nothing but mesh regions.

⚠️ N >= 3 sectors also keeps the m=1 pair DEGENERATE: a C_n symmetric mesh
partition with n >= 3 has a 2-D irreducible representation for m=1, so it does
not split the polarisations the way a 1- or 2-fold partition would. Use 5.
Nyquist with N=5 resolves harmonics up to 2, which is what m=1 needs.
"""
import cmath
import math


def harmonics(sector_energies):
    """{k: |A_k|/A_0} for the angular harmonics of a sector-energy list.

    Sectors are assumed equal-width and in azimuthal order, centred at
    phi_i = 2*pi*(i + 0.5)/N.
    """
    u = list(sector_energies)
    n = len(u)
    if n < 3:
        raise ValueError(f"need >= 3 sectors to resolve an azimuthal harmonic, "
                         f"got {n}. The mesh was built with --sectors {n}.")
    a0 = sum(u) / n
    if a0 <= 0:
        raise ValueError("sector energies sum to zero — nothing to analyse")
    out = {}
    for k in range(1, n // 2 + 1):
        acc = 0j
        for i, v in enumerate(u):
            phi = 2.0 * math.pi * (i + 0.5) / n
            acc += v * cmath.exp(-1j * k * phi)
        out[k] = abs(acc) / n / a0
    return out


def order(sector_energies, flat_below=0.05):
    """(m, confidence, harmonics) — the azimuthal order of one mode.

    m = 0 when the 2nd harmonic is below `flat_below`; m = 1 when it dominates.
    `confidence` is the ratio between the deciding harmonic and the largest
    other one, so a mode that is neither cleanly flat nor cleanly cos(2phi)
    reports LOW confidence rather than a wrong answer.

    🔴 Returns m=None when nothing dominates. An unattended caller must treat
    that as "did not identify", never as a default.
    """
    h = harmonics(sector_energies)
    h2 = h.get(2, 0.0)
    others = [v for k, v in h.items() if k != 2]
    biggest_other = max(others) if others else 0.0
    if h2 < flat_below and biggest_other < flat_below:
        # flat: no azimuthal structure at all
        conf = flat_below / max(h2, biggest_other, 1e-12)
        return 0, conf, h
    if h2 >= flat_below and h2 > 2.0 * biggest_other:
        return 1, h2 / max(biggest_other, 1e-12), h
    return None, 0.0, h


def self_test():
    """Synthetic modes with known m, integrated over 5 equal sectors."""
    ok = True
    print("azimuthal self-test — synthetic modes, 5 sectors\n")
    n = 5

    def sector_energy(m, n=5, samples=2000):
        """Integral of cos^2(m*phi) over each sector."""
        out = []
        for i in range(n):
            lo = 2 * math.pi * i / n
            hi = 2 * math.pi * (i + 1) / n
            s = sum(math.cos(m * (lo + (hi - lo) * (j + 0.5) / samples)) ** 2
                    for j in range(samples))
            out.append(s * (hi - lo) / samples)
        return out

    for m_true in (0, 1):
        u = sector_energy(m_true, n)
        m, conf, h = order(u)
        good = m == m_true
        ok &= good
        print(f"  {'✅' if good else '🔴'} m={m_true}: identified m={m}  "
              f"conf={conf:.1f}  A2/A0={h.get(2,0):.4f}  "
              f"(theory: {0.0 if m_true==0 else 0.5:.4f})")

    # a BLEND of the two — must refuse, not guess
    a = sector_energy(0, n)
    b = sector_energy(1, n)
    mix = [0.5 * x + 0.5 * y for x, y in zip(a, b)]
    m, conf, h = order(mix)
    print(f"  ℹ️  50/50 blend: m={m} conf={conf:.1f} A2/A0={h.get(2,0):.4f}"
          f"  — a partial pattern, reported with its confidence")

    # a nearly-flat mode with mesh noise must still read m=0
    import random
    random.seed(1)
    noisy = [1.0 + random.uniform(-0.01, 0.01) for _ in range(n)]
    m, conf, h = order(noisy)
    good = m == 0
    ok &= good
    print(f"  {'✅' if good else '🔴'} flat + 1% mesh noise: m={m}  "
          f"A2/A0={h.get(2,0):.4f}")

    print(f"\n  {'✅ ALL PASS' if ok else '🔴 FAILURES ABOVE'}")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if self_test() else 1)
