#!/usr/bin/env python3
"""R72 — validate the FIELD MAP by ratios, using a probe small enough to be admissible.

This is NOT a coupler sweep. Six rounds of those returned a 140x scatter with
r^2 ~ 0 (R70/R71), because every one inserted a coupler into a degenerate mode
and measured its own back-reaction. The object being tested here is the MAP —
the linked flux computed from the mode field, with no coupler in it.

🔢 WHAT THE MAP PREDICTS. A cap loop's normal is radial, so it links
H_r ~ J1(chi'01 r/a). Coupled power goes as flux^2, so Q_ext ~ 1/J1^2 with an
interior minimum at r = 49.83 mm. Normalised to that minimum:

        r mm      15     30     50     70     90
        rel     4.73   1.52   1.00   1.49   6.53

⚠️ THE TEST IS ON RATIOS, NOT VALUES. Every absolute Q_ext in this project has
been wrong at least once — the +31.6 MHz offset, the 2x convention, the linewidth
step bias. A ratio against a common reference cancels all three, because they are
common-mode across cases built by one helper at one size-factor.

🔑 THE ADMISSIBILITY GATE, and why it is a HARD refusal rather than a warning.
R71: a coupler whose frequency pull exceeds ~1/10 of the mode separation is
inside the degenerate-perturbation regime, where the response is not a smooth
function of geometry at all. With the 3 mm mode filter the TE011-TM111 separation
is 64.3 MHz, so the limit is 6.4 MHz. sc06 — the best-coupling point ever
measured here — pulled 17.2 MHz and was 2.7x outside it. Its Q_ext = 1,084 is
therefore the LEAST trustworthy number in the set, not the most.

So the probe is deliberately small: ~96 mm^2, against the 178-1001 mm^2 of R70.
It couples weakly. That is the point — a probe that does not move the mode
measures the cavity, and a probe that does measures itself.

VERDICTS:
  ratios track 1/J1^2, interior min near 50 mm  ✅ the map is validated, and the
     R72 design estimate (cap at r=50 -> Q_ext ~ 400) rests on something tested
  ratios flat or monotonic                       🔴 the map is wrong. Since the
     map is just the mode field, that would mean the mode is not what we think —
     a far deeper problem than any coupler, and the first thing to chase
  any case exceeds the pull gate                 ⚠️ that case is REPORTED AND
     EXCLUDED from the fit, not silently averaged in
"""
import math
import pathlib
import sys

from scipy.special import jv

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep
import modes
import solver

A_MM = 103.70
CHI = 3.8317059702
J1MAX = 0.5818652
R_REF = 1.8411837813 / CHI * A_MM        # 49.83 mm, the J1 peak
# 🔑 ADMISSIBILITY: 1/10 of the mode separation the 3 mm filter buys (64.3 MHz).
MAX_PULL_MHZ = 6.4

# ~96 mm^2 probe (2*w*d), against R70's 178-1001. Small enough to stay under the
# pull gate; R70 measured 2.7 MHz at 178 mm^2, so this should sit near 1.5 MHz.
LOOP = "8,6,0.8,0.3"
BASE_ARGS = ["--radius", "103.70", "--length", "88.53", "--mode-filter", "3",
             "--azimuthal-bins", "1", "--order", "2", "--loop", LOOP]
RADII = (15.0, 30.0, 50.0, 70.0, 90.0)
CASES = [("pbarrel", [])] + [(f"pcap{int(r)}", ["--loop-cap", str(r)])
                             for r in RADII]
BAND = (2.39, 2.45)
STEP = 5e-5


def predicted(r_mm):
    """Q_ext relative to its minimum, from |H_r| ~ J1(chi'01 r/a)."""
    return (J1MAX / abs(jv(1, CHI * r_mm / A_MM))) ** 2


def q_ext(tag, te):
    recs = dq.load(tag)
    i0 = min(range(len(recs)), key=lambda i: abs(recs[i]["f"] - te["f"]))
    half = recs[i0]["U"] / 2.0
    lo = next((recs[i]["f"] for i in range(i0, -1, -1) if recs[i]["U"] <= half),
              None)
    hi = next((recs[i]["f"] for i in range(i0, len(recs)) if recs[i]["U"] <= half),
              None)
    if not (lo and hi and hi > lo):
        return None
    ql = te["f"] / (hi - lo)
    return (1.0 / (1.0 / ql - 1.0 / te["Q0"])) if ql < te["Q0"] else None


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS)
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")
res = solver.sweep([(f"{t}.msh", t) for t, _e in CASES], BAND, step=STEP)

rows = []
for tag, _e in CASES:
    te = modes.te011(res.get(tag, []))
    if not te:
        print(f"  ⚠️ {tag}: no TE011 found")
        continue
    r = None if tag == "pbarrel" else float(tag[4:])
    rows.append([tag, r, te, q_ext(tag, te)])

# Reference for the pull gate: the LEAST-perturbing case is the best available
# stand-in for the unloaded resonance, since no coupler-free case is solved here.
if not rows:
    sys.exit("no usable cases")
f_ref = max(x[2]["f"] for x in rows)
for x in rows:
    x.append((f_ref - x[2]["f"]) * 1000.0)         # pull, MHz

print("\n" + "=" * 78)
print(f"{'case':>9}{'r mm':>7}{'f0':>10}{'pull MHz':>10}{'Q0':>9}"
      f"{'Q_ext':>11}{'rel':>7}{'pred':>7}{'admis':>8}")
cap = [x for x in rows if x[1] is not None and x[3]
       and x[4] <= MAX_PULL_MHZ]
ref = min((x for x in cap), key=lambda x: abs(x[1] - R_REF), default=None)
qref = ref[3] if ref else None
for tag, r, te, qe, pull in rows:
    rel = (qe / qref) if (qe and qref) else None
    pred = predicted(r) if r else None
    ok = "ok" if pull <= MAX_PULL_MHZ else "EXCLUDED"
    print(f"{tag:>9}{(r if r else A_MM):>7.1f}{te['f']:>10.5f}{pull:>10.2f}"
          f"{te['Q0']:>9,.0f}{(qe if qe else float('nan')):>11,.0f}"
          f"{(rel if rel else float('nan')):>7.2f}"
          f"{(pred if pred else float('nan')):>7.2f}{ok:>8}")

excluded = [x for x in rows if x[4] > MAX_PULL_MHZ]
print("\nVERDICT")
if excluded:
    print(f"  ⚠️ {len(excluded)} case(s) EXCLUDED for pulling past "
          f"{MAX_PULL_MHZ} MHz: "
          + ", ".join(f"{x[0]} ({x[4]:.1f})" for x in excluded))
    print("     They are inside the degenerate-perturbation regime (R71) and "
          "measure their\n     own back-reaction. Not averaged in.")
if len(cap) >= 4 and qref:
    xs = [math.log(predicted(x[1])) for x in cap]
    ys = [math.log(x[3] / qref) for x in cap]
    mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
    den = sum((x - mx) ** 2 for x in xs)
    slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else 0
    pred_y = [my + slope * (x - mx) for x in xs]
    ss = 1 - (sum((y - p) ** 2 for y, p in zip(ys, pred_y))
              / sum((y - my) ** 2 for y in ys)) if len(set(ys)) > 1 else 0
    best = min(cap, key=lambda x: x[3])
    rs = [x[1] for x in cap]
    interior = best[1] not in (min(rs), max(rs))
    print(f"\n  measured-vs-map log-log slope = {slope:+.2f}  "
          f"(1.00 = exactly 1/J1^2),  r² = {ss:.3f}")
    print(f"  minimum Q_ext at r = {best[1]:.0f} mm; the J1 peak is at "
          f"{R_REF:.1f} mm")
    # 🔑 r² is quoted FIRST and always. §12 reported a slope of -0.07 with no
    # r² and it was fitting noise (R71). An exponent without an r² is not a
    # result here.
    if ss < 0.5:
        print(f"\n  🔴 r² = {ss:.3f} — THE FIT IS MEANINGLESS regardless of the "
              "slope. The ratios do\n     not track the map. Since the map is "
              "just the mode field, the mode is not\n     what we think it is; "
              "chase that before any coupler.")
    elif interior and 0.6 < slope < 1.5:
        print("\n  ✅ THE MAP IS VALIDATED. Ratios track 1/J1² with an interior "
              "minimum near\n     50 mm, measured entirely inside the "
              "admissible regime. The R72 estimate\n     (same coupler moved to "
              "the cap -> Q_ext ~ 400) rests on something tested.")
    else:
        print(f"\n  ⚠️ r² = {ss:.3f} is respectable but slope {slope:+.2f} / "
              f"minimum at {best[1]:.0f} mm do not\n     match the map cleanly. "
              "Something varies with radius besides flux — loop\n     "
              "inductance (R65) and residual mode pull both do.")
    bar = next((x for x in rows if x[1] is None and x[3]), None)
    if bar and best[3]:
        print(f"\n  barrel reference Q_ext {bar[3]:,.0f} vs best cap "
              f"{best[3]:,.0f} = {bar[3]/best[3]:.2f}x")
        print(f"     (map predicts 1.93x for identical footprints; "
              f"barrel pull {bar[4]:.1f} MHz)")
else:
    print(f"  too few ADMISSIBLE cap points ({len(cap)}) to test the map — "
          "shrink the probe and rerun")
print(flush=True)
