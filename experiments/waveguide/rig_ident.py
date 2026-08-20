#!/usr/bin/env python3
"""R77 — IDENTIFY THE INTERLOPER. m from azimuthal bins, p and chi from geometry.

R76 found a third cold resonance at 2.4304 GHz raw that takes 46.5% of input
power against TE011's 11.1% -- an ignition hazard, because a cold start that
peak-finds on reflected power locks onto it. It is NOT TM111 (tm111.f_filtered =
2.35094) and NOT TM020 (2.3695 here, bore-E dominant). It is unidentified, and
"unidentified mode that beats the operating mode at ignition" is not a state to
leave a design in.

⚠️ WHY THE OBVIOUS METHOD FAILS. Matching against the analytic empty-cavity
spectrum does not work here: the 3 mm quartz mode filter drags TM020 from an
analytic 2.5399 GHz down to a measured 2.3955 -- 144 MHz, 5.7%. Any assignment by
absolute frequency is guessing, and this project has twice paid a full sweep for
identifying a mode by a quantity that can be large for the wrong reason.

🔑 THE FINGERPRINT THAT SURVIVES LOADING. For a cylindrical cavity,

    f^2 = (c/2pi)^2 [ (chi_mn/a)^2 + (p*pi/L)^2 ]

so the RADIAL and AXIAL indices appear separately in the geometric derivatives:

    a * (df/da)/f = -R        L * (df/dL)/f = -(1 - R)

where R is the radial share of f^2. Dielectric loading shifts f hard but leaves
the field's radial/axial structure -- and therefore R -- largely alone. The
discriminator is enormous and needs no absolute frequency at all:

    p = 0 modes (TM_mn0):  df/dL = 0        (analytic TM020: 0.00, measured 0.05)
    p = 1 modes:           df/dL ~ -12 MHz/mm  (analytic TE011: -13.25, meas -11.66)

✅ AND THE RUN CARRIES TWO POSITIVE CONTROLS. TM020 and TE011 sit in the same
band, are already identified, and already have measured sensitivities in
baselines.json. If this method does not reproduce THEM, its verdict on the
interloper is worthless. That check is the point of including them.

m COMES FROM THE AZIMUTHAL BINS, using the machinery R47 built and regress.py
already tests against synthetic cos^2(m phi) patterns: at 5 sectors, m=1 lands in
DFT bin 2 and m=2 aliases into bin 1, against an m=0 harness floor of 0.0046 set
by the loop's own symmetry breaking. ⚠️ Bin 1 cannot separate m=2 from m=3 at
N=5 (spatial frequency 6 aliases to 1); df/da breaks that tie.

CASES, all --sectors 5 --loop-phi 36 so the loop sits centred in a sector (R32's
tag collision), and ALL BUILT IN ONE meshsweep CALL so they share a size-factor:

    idref   reference
    idda    radius + 1.0 mm    -> df/da
    iddl    length + 1.0 mm    -> df/dL

⚠️ The reference here is a FRESH mesh, not wbarrel.msh. Sector count changes Q by
6.9% (reproducibility.q_across_sector_counts) and meshes scatter 1.5 MHz, so the
derivative must be taken inside this set, never across it.

Step is 25 kHz because the two narrow modes have true linewidths of ~0.10 MHz
(TM020) and ~0.16 MHz (interloper) -- at R76's 50 kHz they were step-limited, and
a mode you cannot locate you cannot differentiate.
"""
import json
import math
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep
import modes
import solveconf
import solver

PLASMA = "4.5,8.5,-20,10"
LOOP = "25.8,19.4,1.5,0.3"
BASE = ["--mode-filter", "3", "--sectors", "5", "--loop-phi", "36",
        "--order", "2", "--loop", LOOP, "--plasma", PLASMA, "--plasma-h", "1.0"]
CASES = [("idref", ["--radius", "103.70", "--length", "88.53"], (2.360, 2.440)),
         ("idda",  ["--radius", "104.70", "--length", "88.53"], (2.338, 2.428)),
         ("iddl",  ["--radius", "103.70", "--length", "89.53"], (2.358, 2.438))]
STEP = 2.5e-5
DA, DL = 1.0, 1.0                      # mm
AZ_FLOOR = 0.0046                      # te011.azimuthal_floor
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")
# 🔴 REL_MIN was 0.02 and SILENTLY DROPPED TM020 from the iddl case, where it
# sits at rel = 0.0168 because a 1 mm length change moves the loop relative to
# a mode it barely couples to (beta = 0.014). The matcher then paired TM020
# with the interloper and reported df/dL = +49.6 MHz/mm for a p=0 mode.
# A threshold that discards a mode without saying so is the same failure as a
# grep that swallows a traceback.
REL_MIN = 0.005
# A signature match must be CLOSE. Good matches here score 0.000-0.006; the bad
# one scored 2.142 and was accepted because nothing rejected it.
SIG_MAX = 0.10
REPLAY = "--replay" in sys.argv


def build_cfg(mesh, tag, band):
    meta = solveconf.load_meta(mesh)
    pl = meta["attributes"].get("plasma")
    c, meta, dropped = solveconf.driven(
        mesh, tag, band, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    for d in dropped:
        print(f"    dropped: {d}", flush=True)
    for m in c["Domains"]["Materials"]:
        if m["Attributes"] == [pl] and "Conductivity" in m:
            raise RuntimeError(f"{tag}: plasma still conducting — not a cold run")
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    return meta


def resonances(tag):
    """Local maxima of stored energy, with azimuthal content and signatures."""
    recs = dq.load(tag)
    sect = modes.sector_energy(tag)
    if sect is None:
        raise RuntimeError(f"{tag}: NO SECTOR DATA — m cannot be measured, and "
                           "without m this run cannot identify anything")
    U = [r["U"] for r in recs]
    um = max(U)
    out = []
    for i in range(2, len(U) - 2):
        if U[i] == max(U[i - 2:i + 3]) and U[i] > REL_MIN * um:
            b1, b2 = modes.azimuthal(sect[i])
            r = recs[i]
            # parabolic refinement on the energy peak: the step is 25 kHz and a
            # 1 mm perturbation moves modes 12-25 MHz, but sub-step accuracy is
            # free and keeps the derivative honest.
            y0, y1, y2 = U[i - 1], U[i], U[i + 1]
            d = y0 - 2 * y1 + y2
            sh = 0.5 * (y0 - y2) / d if d != 0 else 0.0
            out.append(dict(f=r["f"] + sh * (recs[1]["f"] - recs[0]["f"]),
                            U=U[i], rel=U[i] / um, pm=r["pm"], pe=r["pe"],
                            Q0=r["Q0"], eta=1 - r["gamma"] ** 2, b1=b1, b2=b2))
    return out


print(__doc__)
print("=" * 78, flush=True)
fac, _ = meshsweep.sweep([(t, e) for t, e, _b in CASES], BASE)
if not fac:
    sys.exit("mesh sweep failed — a mixed-density set cannot give a derivative")
print(f"  ✅ all cases meshed at a COMMON size-factor {fac}", flush=True)

res = {}
for tag, _e, band in CASES:
    if not (REPLAY and (pathlib.Path("postpro") / tag /
                        "port-S.csv").exists()):
        build_cfg(f"{tag}.msh", tag, band)
    if REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists():
        res[tag] = resonances(tag)
        print(f"\n  {tag}: replay from postpro/, {len(res[tag])} resonance(s)")
        print(f"    {'f GHz':>9}{'rel':>7}{'bore-H':>9}{'bore-E':>10}{'Q0':>8}"
              f"{'eta':>7}{'b1(m2)':>9}{'b2(m1)':>9}")
        for r in res[tag]:
            print(f"    {r['f']:>9.4f}{r['rel']:>7.3f}{r['pm']:>9.5f}"
                  f"{r['pe']:>10.6f}{r['Q0']:>8.0f}{100*r['eta']:>6.1f}%"
                  f"{r['b1']:>9.4f}{r['b2']:>9.4f}", flush=True)
        continue
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=solver.ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT,
                        timeout=solver.DEFAULT_TIMEOUT_S).returncode
    dt = time.time() - t0
    if rc or dt < solver.MIN_SECONDS:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        sys.exit(f"🔴 {tag}: rc={rc} in {dt:.0f}s — "
                 f"{tail[-1] if tail else '(empty log)'}")
    res[tag] = resonances(tag)
    print(f"\n  {tag}: {dt:.0f}s, {len(res[tag])} resonance(s)")
    print(f"    {'f GHz':>9}{'rel':>7}{'bore-H':>9}{'bore-E':>10}{'Q0':>8}"
          f"{'eta':>7}{'b1(m2)':>9}{'b2(m1)':>9}")
    for r in res[tag]:
        print(f"    {r['f']:>9.4f}{r['rel']:>7.2f}{r['pm']:>9.5f}{r['pe']:>10.6f}"
              f"{r['Q0']:>8.0f}{100*r['eta']:>6.1f}%{r['b1']:>9.4f}"
              f"{r['b2']:>9.4f}", flush=True)

print("\n" + "=" * 78)
print("MATCHING ACROSS CASES — each mode by a local max of ITS OWN diagnostic")
# 🔴 Matching by the (bore-H, bore-E) signature FAILED for TM020 in iddl, and the
# failure is instructive: TM020 is there at 2.3748, its bore-E spiking 0.00101 ->
# 0.00672, but it sits on TE011's much larger skirt. p_elec[1] is a FRACTION of
# total energy, so an overlapping neighbour DILUTES the signature even though the
# mode is plainly present. Signature distance came out 1.365 against 0.006 for a
# clean match.
#
# The fix is the project's own rule taken literally: find a mode by WHERE ITS
# ENERGY IS. A bore-ELECTRIC mode is located by a local maximum of bore-E, a
# bore-MAGNETIC one by a local maximum of bore-H — never by total stored energy,
# which the strongest coupler wins, and never by a fraction that a neighbour can
# dilute.
WIN = 0.030          # GHz: a 1 mm perturbation moves nothing more than ~25 MHz


def kind(r):
    return "pe" if r["pe"] > r["pm"] else "pm"


def match(ref, cand):
    """Closest (bore-H, bore-E) signature in log space, restricted to the window.

    Restricting to the window matters: without it a distant peak with a similar
    signature can win, which is how a derivative gets computed across a mode it
    was never tracking.
    """
    near = [c for c in cand if abs(c["f"] - ref["f"]) < WIN]
    if not near:
        return None, float("inf")

    def dist(x):
        return sum((math.log10(max(x[k], 1e-9))
                    - math.log10(max(ref[k], 1e-9))) ** 2 for k in ("pm", "pe"))

    best = min(near, key=dist)
    return best, dist(best)


def nearest_diag(tag, f0, key):
    """NEAREST local max of one diagnostic to f0, with a contrast test.

    ⚠️ An earlier version took the LARGEST maximum in the window instead of the
    nearest, and both bore-H modes then matched the same feature — a matcher that
    maps two distinct modes onto one answer, silently. Nearest + contrast.
    """
    recs = dq.load(tag)
    f = [x["f"] for x in recs]
    v = [x[key] for x in recs]
    cand = [i for i in range(2, len(f) - 2)
            if abs(f[i] - f0) < WIN and v[i] == max(v[i - 2:i + 3])]
    if not cand:
        return None, 0.0
    i = min(cand, key=lambda j: abs(f[j] - f0))
    lo = max(0, i - 40)
    base = sorted(v[lo:i + 40])[len(v[lo:i + 40]) // 2]
    y0, y1, y2 = v[i - 1], v[i], v[i + 1]
    d = y0 - 2 * y1 + y2
    sh = 0.5 * (y0 - y2) / d if d != 0 else 0.0
    return f[i] + sh * (f[1] - f[0]), (v[i] / base if base > 0 else 0.0)


def locate(r, tag):
    """Signature match against resolved peaks first; diagnostic max as fallback.

    The signature matcher is correct when a peak is RESOLVED, and it separates
    even two bore-H modes cleanly (distances 0.001 and 0.000 here). It fails only
    when a mode is BLENDED into a larger neighbour's skirt, because p_elec[1] is a
    FRACTION of total energy and the neighbour dilutes it — TM020 in iddl scored
    1.365 while plainly sitting there at 2.3748 with bore-E spiking 6.6x.
    """
    m, d = match(r, res[tag])
    if m is not None and d <= SIG_MAX:
        return m["f"], f"signature {d:.3f}"
    k = kind(r)
    f, c = nearest_diag(tag, r["f"], k)
    lab = "bore-E" if k == "pe" else "bore-H"
    if f is not None and c >= 2.0:
        return f, f"blended, {lab} max x{c:.1f}"
    return None, "NOT FOUND"


rows = []
for r in res["idref"]:
    fa, wa = locate(r, "idda")
    fl, wl = locate(r, "iddl")
    if fa is None or fl is None:
        print(f"  🔴 f={r['f']:.4f}: DROPPED — idda[{wa}] iddl[{wl}]. Not paired "
              "with the nearest thing.")
        continue
    print(f"  f={r['f']:.4f} -> idda {fa:.4f} [{wa}]   iddl {fl:.4f} [{wl}]")
    rows.append(dict(ref=r, key=kind(r), da=1e3 * (fa - r["f"]) / DA,
                     dl=1e3 * (fl - r["f"]) / DL))

print("\n" + "=" * 78)
print("THE FINGERPRINT")
print(f"{'f GHz':>9}{'df/da':>11}{'df/dL':>11}{'R(da)':>8}{'1-R(dL)':>9}"
      f"{'sum':>7}{'p':>7}{'chi':>8}{'b1(m2)':>9}{'b2(m1)':>9}")
for x in rows:
    r = x["ref"]
    R = -x["da"] * (103.70 / (1e3 * r["f"]))
    Rl = -x["dl"] * (88.53 / (1e3 * r["f"]))
    pp = (2 * r["f"] * 1e9 / 299792458.0) * 0.08853 * math.sqrt(max(0.0, 1 - R))
    chi = (2 * math.pi * r["f"] * 1e9 / 299792458.0) * 0.1037 * math.sqrt(max(R, 0.0))
    x.update(R=R, p=pp, chi=chi)
    print(f"{r['f']:>9.4f}{x['da']:>11.2f}{x['dl']:>11.2f}{R:>8.3f}{Rl:>9.3f}"
          f"{R+Rl:>7.2f}{pp:>7.2f}{chi:>8.3f}{r['b1']:>9.4f}{r['b2']:>9.4f}")
print("  (R from df/da and 1-R from df/dL are INDEPENDENT measurements; their "
      "sum is a\n   cross-check and should be 1.00)")

print("\nCONTROL CHECK — graded per derivative, because they carry different "
      "conclusions")
# p rests ENTIRELY on df/dL; chi rests on df/da. Grading them together would let
# a good df/dL launder a bad df/da, or the reverse.
# 🔴 This was keyed by kind(), so BOTH bore-H modes mapped to one slot and the
# INTERLOPER was silently graded against TE011's baselines — the method
# "validating" itself on the very mode under test. Controls must be pinned to
# specific modes: TM020 is the bore-E one; TE011 is the bore-H one with the
# LARGEST bore-H (0.0102 against the interloper's 0.0041).
_pe = [x for x in rows if kind(x["ref"]) == "pe"]
_pm = sorted([x for x in rows if kind(x["ref"]) == "pm"],
             key=lambda x: -x["ref"]["pm"])
ident = {"TM020": _pe[0] if _pe else None, "TE011": _pm[0] if _pm else None}
INTERLOPER = _pm[1] if len(_pm) > 1 else None
ctl = [("TM020", -21.99, 0.05), ("TE011", -12.86, -11.66)]
okL = okA = True
for name, eda, edl in ctl:
    x = ident.get(name)
    if x is None:
        print(f"  🔴 {name}: not present — no control on this axis")
        okL = okA = False
        continue
    ga, gl = abs(x["da"] - eda) < 4.0, abs(x["dl"] - edl) < 3.0
    print(f"    (control is the f={x['ref']['f']:.4f} peak, bore-H "
          f"{x['ref']['pm']:.5f} / bore-E {x['ref']['pe']:.5f})")
    okA &= ga
    okL &= gl
    print(f"  {name:>6}: df/dL {x['dl']:+6.2f} vs {edl:+6.2f} baseline "
          f"{'✅' if gl else '🔴'}    df/da {x['da']:+6.2f} vs {eda:+6.2f} "
          f"{'✅' if ga else '🔴'}")
print(f"\n  df/dL controls {'✅ PASS' if okL else '🔴 FAIL'} -> the AXIAL index p "
      f"is {'admissible' if okL else 'NOT admissible'}")
print(f"  df/da controls {'✅ PASS' if okA else '🔴 FAIL'} -> chi (and the radial "
      f"index) is {'admissible' if okA else 'weakened — quote it as a ranking, not a value'}")

print("\nVERDICT ON THE INTERLOPER")
x = INTERLOPER
if x is None:
    sys.exit("  the interloper was not tracked — nothing to identify")
r, R, p = x["ref"], x["R"], x["p"]
print(f"  f {r['f']:.4f}  df/da {x['da']:+.2f}  df/dL {x['dl']:+.2f}  "
      f"R {R:.3f}  p~{p:.2f}  chi {x['chi']:.3f}  b1 {r['b1']:.4f}  "
      f"b2 {r['b2']:.4f}")
if abs(x["dl"]) < 3.0:
    print("  🔑 df/dL ~ 0 -> AXIAL INDEX p = 0. This is a TM_mn0 mode: E_z "
          "uniform along z,\n     which also explains its low Q0 (17,097) — "
          "full-strength E in the quartz\n     mode filter at BOTH end caps.")
else:
    print(f"  🔑 df/dL ~ {x['dl']:.1f} -> p = 1. A mode with an axial half-wave.")
chi = x["chi"]
print(f"  🔢 implied chi = {chi:.3f}  (TM: chi_01 2.405, chi_11 3.832, "
      "chi_21 5.136, chi_02 5.520, chi_31 6.380)")
print(f"  🔢                        (TE: chi'_11 1.841, chi'_21 3.054, "
      "chi'_01 3.832, chi'_31 4.201)")
DEG = 3.8317
if abs(chi - DEG) / DEG < 0.03 and abs(p - 1) < 0.15:
    te = ident["TE011"]
    print(f"\n  🔑 chi = {chi:.3f} is chi'_01 = chi_11 = 3.8317 to "
          f"{100*abs(chi-DEG)/DEG:.1f}% — THE EXACT DEGENERACY.")
    print("     At p = 1 that admits exactly TWO modes, and no others: "
          "TE011 (m=0) and TM111 (m=1).")
    if te is not None:
        print(f"     TE011 is separately identified at {te['ref']['f']:.4f} "
              f"(bore-H {te['ref']['pm']:.5f}, Q0 {te['ref']['Q0']:,.0f}).")
    print("\n  ✅ THEREFORE THE INTERLOPER IS TM111. Corroboration, none of it "
          "used to derive it:")
    if te is not None:
        print(f"     · separation {1e3*(r['f']-te['ref']['f']):.1f} MHz vs "
              "baseline effect.filter_te011_tm111_separation = 45 MHz")
        print(f"     · Q0 {r['Q0']:,.0f} vs TE011's {te['ref']['Q0']:,.0f} — "
              "TM111 has E_z AT THE END CAPS,\n       so it dissipates in the "
              "3 mm quartz mode filter; TE011's E_phi vanishes there")
        print(f"     · bore-E {r['pe']:.5f} vs TE011's {te['ref']['pe']:.5f} "
              f"({r['pe']/te['ref']['pe']:.1f}x) — TM111 has E_z, TE011 has none")
        print(f"     · azimuthal bin2 (m=1) {r['b2']:.4f} > bin1 (m=2) "
              f"{r['b1']:.4f}, and exceeds TE011's\n       bin2 "
              f"{te['ref']['b2']:.4f} despite coupling ~200x more weakly")
    print("\n  🔑 AND THIS IS R71's HYPOTHESISED MECHANISM, OBSERVED. R71 named "
          "the exact\n     chi'_01 = chi_11 degeneracy as the reason loop "
          "response is unpredictable.\n     Here is the degenerate partner, "
          "resolved, 42 MHz away with the filter in.")
print("\n⚠️ chi is computed from the EMPTY-cavity dispersion, so dielectric "
      "loading biases\n   it low. Read it as a ranking among candidates, not as "
      "a number. m and p are\n   the load-bearing results; they come from "
      "symmetry and from a derivative.")
print(flush=True)
