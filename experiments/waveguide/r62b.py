#!/usr/bin/env python3
"""R62b — sweep the series capacitor's FLANGE RADIUS to find cancellation.

Established so far:
  · Palace's port C is PARALLEL (52 s test) — a series capacitor must be
    geometric, so the gap route is correct.
  · A bare 0.15 mm gap DOES change the coupling: |Gamma| 0.568 -> 0.904. But it
    made coupling WORSE, so it is on the BLOCKING side — too little capacitance,
    adding reactance rather than cancelling the loop's +332 ohm.
  · C = eps0*A/d says the fix is AREA at a meshable gap, not a smaller gap.

At a 0.5 mm gap the parallel-plate estimate puts cancellation at ~1.9 mm flange
radius:

    flange r      C pF    Zc ohm   net with +332j
        1.0      0.056     -1168      -836   blocking
        1.5      0.125      -519      -187
       1.9       0.201      -323        +9   CANCELLED
        2.5      0.348      -187      +145   over-corrected

PREDICTION: |Gamma| should show a distinct MINIMUM near 1.9 mm — a resonant
cancellation, not a trend. Fringing between discs makes the real C larger than
parallel-plate, so the true optimum should sit at a SMALLER radius than 1.9;
if the minimum lands at or below 1.5 that is fringing, not a failure.

🔴 A MONOTONIC result would falsify the lumped picture entirely: it would mean
the loop is not an inductor with a series capacitor but a distributed structure
(its perimeter is ~58 mm against lambda = 122 mm, i.e. ~lambda/2), and the
coupler section's analytic 45x would be wrong at its foundation rather than in
its arithmetic.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep
import modes
import solver

A, L, GAP = "103.70", "88.53", "0.5"
BASE_ARGS = ["--radius", A, "--length", L, "--mode-filter", "3",
             "--azimuthal-bins", "1", "--order", "2", "--loop", "12,8.5,1,0.3"]
CASES = [("f_none", []),
         ("f_10", ["--loop-gap2", GAP, "--loop-flange", "1.0"]),
         ("f_15", ["--loop-gap2", GAP, "--loop-flange", "1.5"]),
         ("f_19", ["--loop-gap2", GAP, "--loop-flange", "1.9"]),
         ("f_25", ["--loop-gap2", GAP, "--loop-flange", "2.5"])]
FLANGE = {"f_none": None, "f_10": 1.0, "f_15": 1.5, "f_19": 1.9, "f_25": 2.5}
BAND = (2.39, 2.45)


def q_loaded(tag, f0):
    recs = dq.load(tag)
    i0 = min(range(len(recs)), key=lambda i: abs(recs[i]["f"] - f0))
    half = recs[i0]["U"] / 2.0
    lo = next((recs[i]["f"] for i in range(i0, -1, -1) if recs[i]["U"] <= half),
              None)
    hi = next((recs[i]["f"] for i in range(i0, len(recs)) if recs[i]["U"] <= half),
              None)
    return f0 / (hi - lo) if lo and hi and hi > lo else None


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = solver.sweep([(f"{t}.msh", t) for t, _e in CASES], BAND, step=5e-5)

print("\n" + "=" * 78)
print(f"{'flange':>8}{'f0':>10}{'Q0':>10}{'Q_ext':>11}{'|Gamma|':>10}{'absorbed':>10}")
rows = []
for tag, _e in CASES:
    te = modes.te011(res[tag])
    if not te:
        print(f"{str(FLANGE[tag]):>8}   no TE011 found")
        continue
    ql = q_loaded(tag, te["f"])
    qext = (1.0 / (1.0 / ql - 1.0 / te["Q0"])) if ql and ql < te["Q0"] else None
    rows.append((FLANGE[tag], te["gamma"], qext))
    print(f"{str(FLANGE[tag]):>8}{te['f']:>10.5f}{te['Q0']:>10,.0f}"
          f"{(qext if qext else float('nan')):>11,.0f}{te['gamma']:>10.4f}"
          f"{100*(1-te['gamma']**2):>9.1f}%")

print("\nVERDICT")
flanged = [r for r in rows if r[0] is not None]
if len(flanged) >= 3:
    best = min(flanged, key=lambda r: r[1])
    ends = [flanged[0][1], flanged[-1][1]]
    if best[0] not in (flanged[0][0], flanged[-1][0]):
        print(f"  ✅ MINIMUM at flange {best[0]} mm: |Gamma| {best[1]:.4f}, "
              f"{100*(1-best[1]**2):.0f}% absorbed"
              + (f", Q_ext {best[2]:,.0f}" if best[2] else ""))
        print("     A resonant cancellation, as the lumped picture predicts. "
              "The series C is real and tunable.")
    else:
        print(f"  🔴 MONOTONIC across {flanged[0][0]}-{flanged[-1][0]} mm "
              f"(|Gamma| {ends[0]:.4f} -> {ends[1]:.4f}) — no cancellation.")
        print("     The loop is not a lumped inductor with a series capacitor; "
              "its perimeter is ~lambda/2. The coupler section's 45x rests on a "
              "model that does not apply.")
    ref = next((r for r in rows if r[0] is None), None)
    if ref:
        print(f"  bare loop reference: |Gamma| {ref[1]:.4f}, "
              f"{100*(1-ref[1]**2):.0f}% absorbed")
print(flush=True)
