#!/usr/bin/env python3
"""How much tuning range does AMIP actually need? Answered in eta, not in MHz.

R74 left seven full eta(f) curves on disk -- sigma = 0.3 to 300 S/m, 501 points
each over 2.38-2.48 GHz, one frozen mesh. That is enough to answer the tuner
question without a new solve, and to answer it in the right units.

"16.4 MHz of drift" is not an answer. Two things have to be added to it before it
means anything:

  1. MHz is meaningless without the LINEWIDTH. A lit cavity at Q_L ~ 200 has an
     11 MHz linewidth, so 16.4 MHz is ~1.5 linewidths -- for an UNLIT cavity at
     Q_L ~ 18,000 the same drift is 120 linewidths. The same number is trivial in
     one state and hopeless in the other.
  2. 🔑 THE DESIGN QUESTION IS NOT "HOW MANY MHz" BUT "WHAT DOES NOT TUNING
     COST". Park the source at ONE fixed frequency, take the worst sigma, and
     read the delivered power. That is a number you can accept or reject. A
     range in MHz is not.

So this computes, from the measured curves:

  A. the drift, in MHz and in loaded linewidths, as a function of how much sigma
     uncertainty is actually admitted -- because 1000x was chosen to bracket the
     physics, not to describe a real plasma;
  B. the MINIMAX FIXED FREQUENCY: the single f that maximises the worst-case eta
     over the admitted sigma range, and what that worst case is;
  C. the value of a tuner = (worst case with perfect tracking) - (worst case
     with the best fixed frequency), in points of delivered power;
  D. the other contributors to required range, so sigma is not mistaken for the
     whole budget.

⚠️ SCOPE. This is the LIT cavity only, and one geometry (sc06 on the barrel,
order 1, one mesh). The cold-to-lit ignition excursion is NOT measured here and
is the larger term -- see the note at the end for why it needs a different sweep.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq

CASES = [(0.3, "s0p3"), (1.0, "s1"), (3.0, "s3"), (10.0, "s10"),
         (30.0, "s30"), (100.0, "s100"), (300.0, "s300")]
# Nested windows of admitted sigma uncertainty. The widest is R74's full sweep,
# chosen to bracket the physics; the narrowest is "we believe sigma to a factor
# of ~3", which is what a literature value would plausibly give us.
WINDOWS = [("1000x  (0.3-300, R74's full bracket)", 0.3, 300.0),
           ("100x   (1-100)", 1.0, 100.0),
           ("30x    (3-100, MP-AES to ICP class)", 3.0, 100.0),
           ("10x    (10-100)", 10.0, 100.0),
           ("~3x    (10-30, a pinned literature value)", 10.0, 30.0)]

print(__doc__)
print("=" * 78)

data = {}
for sig, tag in CASES:
    recs = dq.load(tag)
    if not recs:
        sys.exit(f"missing postpro for {tag} — run rig_sigma.py first")
    fs = [r["f"] for r in recs]
    eta = [1.0 - r["gamma"] ** 2 for r in recs]
    i = max(range(len(eta)), key=lambda j: eta[j])
    # Q_L is what a control loop sees: the loaded linewidth, not the unloaded one.
    # beta from the UNDERCOUPLED branch, which R74 settled by showing Q_ext =
    # Q0/beta is constant there and swings 22x on the other.
    e = eta[i]
    d = 2.0 * math.sqrt(max(0.0, 1.0 - e))
    beta = (2 - e - d) / e
    q0 = recs[i]["Q0"]
    ql = q0 / (1.0 + beta)
    data[sig] = dict(f=fs, eta=eta, fpk=fs[i], epk=e, q0=q0, beta=beta, ql=ql,
                     lw=1e3 * fs[i] / ql)          # linewidth in MHz

print("\nA. THE LIT-STATE DRIFT, AND WHAT A LINEWIDTH IS WORTH")
print(f"{'sigma':>7}{'f@max':>10}{'eta':>8}{'Q0':>7}{'beta':>7}{'Q_L':>7}"
      f"{'linewidth':>11}")
for sig, _t in CASES:
    d_ = data[sig]
    print(f"{sig:>7g}{d_['fpk']:>10.4f}{100*d_['epk']:>7.1f}%{d_['q0']:>7.0f}"
          f"{d_['beta']:>7.2f}{d_['ql']:>7.0f}{d_['lw']:>9.1f} MHz")

print("\nB. WHAT A FIXED-FREQUENCY SOURCE COSTS, per admitted sigma window")
print("   (minimax: the single f that maximises the WORST-CASE eta over the "
      "window)")
print(f"\n{'admitted sigma range':>42}{'drift':>9}{'in LW':>8}"
      f"{'tuned':>8}{'fixed':>8}{'best f':>10}{'cost':>8}")
grid = data[0.3]["f"]
for _s, _t in CASES:          # minimax indexes all cases by j: prove that is legal
    assert data[_s]["f"] == grid, f"{_t} is on a different frequency grid"
rows = []
for name, lo, hi in WINDOWS:
    sigs = [s for s, _t in CASES if lo - 1e-9 <= s <= hi + 1e-9]
    if len(sigs) < 2:
        continue
    pk = [data[s]["fpk"] for s in sigs]
    drift = 1e3 * (max(pk) - min(pk))
    lw = min(data[s]["lw"] for s in sigs)          # worst case = narrowest
    tuned = min(data[s]["epk"] for s in sigs)      # perfect tracking
    # minimax over the shared frequency grid
    best_f, best_worst = None, -1.0
    for j in range(len(grid)):
        w = min(data[s]["eta"][j] for s in sigs)
        if w > best_worst:
            best_f, best_worst = grid[j], w
    rows.append(dict(name=name, sigs=sigs, drift=drift, lw=drift / lw,
                     tuned=tuned, fixed=best_worst, f=best_f))
    print(f"{name:>42}{drift:>7.1f} MHz{drift/lw:>7.1f}{100*tuned:>7.1f}%"
          f"{100*best_worst:>7.1f}%{best_f:>10.4f}{100*(tuned-best_worst):>6.1f} pts")

# 🔑 BAND PLACEMENT NEEDS THE OFFSET. Everything above is order-1 RAW, where
# differences are valid but absolute frequencies are not (README: Q and delta-f
# are order-independent, absolute placement is not). Any claim about fitting
# inside the ISM band is an absolute claim, so it gets the offset.
OFF = json.loads(pathlib.Path("baselines.json").read_text())["offset.te011"]["value"]
ISM = (2.400, 2.500)
raw_lo = min(data[s_]["fpk"] for s_, _t in CASES)
raw_hi = max(data[s_]["fpk"] for s_, _t in CASES)
lo, hi = raw_lo + OFF / 1e3, raw_hi + OFF / 1e3
print("\nC. DOES IT FIT IN THE BAND? (absolute placement, offset applied)")
print(f"  order-1 raw     {raw_lo:.4f} - {raw_hi:.4f} GHz   "
      f"⚠️ NOT a band-placement claim")
print(f"  + offset.te011 {OFF:+.2f} MHz -> {lo:.4f} - {hi:.4f} GHz")
print(f"  ISM 2.400-2.500: {'✅ fits' if ISM[0] < lo and hi < ISM[1] else '🔴 does NOT fit'}"
      f", margin {1e3*(lo-ISM[0]):.0f} MHz below / {1e3*(ISM[1]-hi):.0f} MHz above")
print(f"  🔑 The whole lit sigma range spans {1e3*(hi-lo):.1f} MHz inside a "
      f"{1e3*(ISM[1]-ISM[0]):.0f} MHz band —\n     the amplifier has "
      f"{(ISM[1]-ISM[0])/(hi-lo):.0f}x more range than the plasma uncertainty needs.")
print("  ⚠️ offset.te011 was measured on the DESIGN geometry (choff.msh), not on "
      "wbarrel\n     with sc06's loop, and R38 flags it geometry-dependent. "
      "Treat the placement as\n     ~5 MHz accurate, which does not change the "
      "verdict.")

print("\nD. THE VERDICT — three different questions hide inside \"range\"")
full = rows[0]
tight = rows[-1]
mach = 2 * 0.2 * abs(json.loads(pathlib.Path("baselines.json").read_text())
                     ["sens.dte011_da"]["value"])
print("  Asking 'how much range' conflates three specs with different answers.")
print(f"\n  1. ONE FIXED FREQUENCY FOR ALL UNITS, no calibration")
print(f"     Worst case {100*full['fixed']:.1f}% at {full['f']:.4f} GHz over the "
      f"1000x bracket, against\n     {100*full['tuned']:.1f}% tuned — "
      f"🔴 a {100*(full['tuned']-full['fixed']):.0f}-POINT loss. Not viable "
      f"while sigma is unpinned.")
print(f"\n  2. SET ONCE AT COMMISSIONING, per instrument  ← what this design "
      f"actually needs")
print(f"     Must COVER {1e3*(hi-lo):.1f} MHz of sigma spread + "
      f"{mach:.1f} MHz of machining tolerance\n     ~= {1e3*(hi-lo)+mach:.0f} MHz "
      f"of RANGE, but requires no dynamic tracking at all.\n"
      f"     ✅ Comfortably inside the ISM band, and a solid-state source is "
      f"frequency-agile\n     by nature. Peak-find once, lock, done. "
      f"Build-time uncertainty is NOT a tuner.")
print(f"\n  3. TRACK sigma DURING OPERATION (sample aspiration loads the plasma)")
print(f"     This is the only one that needs a real tuner, and it is sized by "
      f"RUNTIME\n     VARIATION, not by a-priori uncertainty. At a 3x swing it "
      f"costs\n     {100*(tight['tuned']-tight['fixed']):.1f} points; at 10x, "
      f"{100*(rows[-2]['tuned']-rows[-2]['fixed']):.1f} points.")
print(f"\n  🔑 THE ANSWER: ~{1e3*(hi-lo)+mach+1.5:.0f} MHz of SETTABLE range, "
      f"and essentially ZERO dynamic range.")
print("     The lit resonance is broad (Q_L 156-612, linewidth 3.9-15.4 MHz), so "
      "the\n     16.4 MHz of sigma drift is ~1 linewidth and eta is flat across "
      "it. ✅ The\n     'no tuner, no moving parts' constraint SURVIVES — a "
      "mechanical tuner was never\n     the thing at issue; a frequency-agile "
      "source already covers it.")
print("\n  🔑 AND THE TUNER QUESTION IS THE sigma QUESTION AGAIN. The cost of "
      "not tuning\n     falls 52 -> 0.2 points as sigma is pinned from 1000x to "
      "3x. You do not need a\n     tuner; you need to KNOW sigma (AUDIT.md A5). "
      "That is the same conclusion R74\n     reached from the other direction.")

print("\nE. ⚠️ sigma IS NOT THE WHOLE BUDGET. The other contributors:")
b = json.loads(pathlib.Path("baselines.json").read_text())
da = b["sens.dte011_da"]["value"]
tol = 0.2
terms = [
    (f"plasma sigma, 1000x bracket (R74, MEASURED)", full["drift"], "lit"),
    (f"plasma sigma, pinned to ~3x (R74, MEASURED)", tight["drift"], "lit"),
    (f"machining: cav.radius +/-{tol} mm x {da} MHz/mm", 2 * tol * abs(da),
     "both"),
    ("mesh-to-mesh scatter (a MODEL error, not a real one)",
     b["reproducibility.mesh_to_mesh_scatter"]["value"], "model"),
    ("cold -> lit ignition step (R10, DIFFERENT geometry)", 24.0, "transient"),
]
for name, mhz, kind in terms:
    print(f"    {mhz:>6.1f} MHz  {name}   [{kind}]")
print(f"\n  🔑 Machining contributes {2*tol*abs(da):.1f} MHz — a third of the "
      f"sigma drift, and larger than\n     the drift over any REALISTIC sigma "
      f"window ({tight['drift']:.1f} MHz at 3x). But it is a FIXED offset\n"
      f"     per unit, not something a control loop tracks: it is absorbed at "
      f"build time by\n     cutting the cavity to length, which is what "
      f"cav.shim_quartz_to_all_sapphire already does.")
print("\n  🔴 THE TRANSIENT, NOT THE DRIFT, IS THE UNSOLVED PROBLEM. Unlit, "
      "Q_L ~ 18,000\n     and the linewidth is ~0.13 MHz; lit it is ~11 MHz, "
      "85x wider. The amplifier\n     must FIND a 0.13 MHz target to deposit "
      "ignition power, then follow a\n     resonance that moves tens of MHz "
      "and broadens 85x, within the ignition\n     timescale. That is a "
      "BANDWIDTH and ACQUISITION spec, not a range spec, and it\n     is the "
      "open risk the README already lists. This analysis does not touch it.")
print("\n⚠️ NOT MEASURED HERE: the cold resonance of THIS geometry. It needs a "
      "different\n   sweep — a 0.2 MHz step steps straight over a 0.13 MHz "
      "linewidth, which is the\n   linewidth_step_bias trap that already cost "
      "this project a Q measurement.")
