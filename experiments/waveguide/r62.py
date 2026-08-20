#!/usr/bin/env python3
"""R62 — does the SERIES capacitor actually take Q_ext from 14,442 to ~320?

The design specifies "small non-perturbing loop + series C". The coupler section
computes that 0.196 pF cancels the loop's 332 ohm self-reactance, raising coupled
power ~45x and landing Q_ext at ~320 — exactly what R56 measured as the
requirement for matching a lit plasma. **It has never been simulated.** Palace's
lumped-port R and C are in PARALLEL, so setting C on the port does not create a
series element; a real one is a break in the conductor.

geometry.py gained `--loop-gap2`: a second gap in a radial leg, in series with
the loop, with the port gap left alone in the crossbar.

MEASURED QUANTITY: Q_ext from the LINEWIDTH, not from |Gamma|.
    1/Q_L = 1/Q0 + 1/Q_ext  ->  Q_ext = 1/(1/Q_L - 1/Q0)
|Gamma| alone cannot distinguish over- from under-coupling, and this file already
recorded Re(Z) as ill-conditioned when |Gamma| -> 1 (section 12). Q_L comes from
the half-power width of the STORED-ENERGY peak, which is what dq.py's peak
finder works on.

⚠️ THE RISK THIS RUN IS REALLY TESTING. The gap is 0.15-0.6 mm against a
MeshSizeMin of ~1.2 mm, so the feature is smaller than the elements around it.
Two meshes at 0.15 and 0.30 mm came back with IDENTICAL element counts and
different checksums — the geometry differs, the discretisation does not. **If
Q_ext comes back independent of gap width, the mesh is not resolving the
capacitor** and the answer is local refinement, not a different gap. That is a
real possible outcome and it is not a null result.

    g_none   no second gap — reproduces the bare loop, Q_ext ~14,442
    g_060    0.60 mm
    g_030    0.30 mm
    g_015    0.15 mm   (parallel-plate estimate for 0.196 pF is ~0.14 mm)
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep
import modes
import solver

A, L = "103.70", "88.53"
BASE_ARGS = ["--radius", A, "--length", L, "--mode-filter", "3",
             "--azimuthal-bins", "1", "--order", "2", "--loop", "12,8.5,1,0.3"]
CASES = [("g_none", []), ("g_060", ["--loop-gap2", "0.60"]),
         ("g_030", ["--loop-gap2", "0.30"]), ("g_015", ["--loop-gap2", "0.15"])]
GAP = {"g_none": 0.0, "g_060": 0.60, "g_030": 0.30, "g_015": 0.15}
BAND = (2.30, 2.52)


def q_loaded(tag, f0):
    """Q_L from the half-power width of the stored-energy peak."""
    recs = dq.load(tag)
    if not recs:
        return None
    i0 = min(range(len(recs)), key=lambda i: abs(recs[i]["f"] - f0))
    half = recs[i0]["U"] / 2.0
    lo = hi = None
    for i in range(i0, -1, -1):
        if recs[i]["U"] <= half:
            lo = recs[i]["f"]
            break
    for i in range(i0, len(recs)):
        if recs[i]["U"] <= half:
            hi = recs[i]["f"]
            break
    if lo is None or hi is None or hi <= lo:
        return None
    return f0 / (hi - lo)


print(__doc__)
print("=" * 78, flush=True)

fac, _ = meshsweep.sweep(CASES, BASE_ARGS,
                         factors=("0.96", "1.00", "0.93", "0.90", "1.06"))
if not fac:
    sys.exit("mesh sweep failed — nothing comparable to report")

res = solver.sweep([(f"{t}.msh", t) for t, _e in CASES], BAND)

print("\n" + "=" * 78)
print(f"{'gap mm':>8}{'f0':>10}{'Q0':>10}{'Q_L':>10}{'Q_ext':>11}{'|S11| dB':>10}")
rows = []
for tag, _e in CASES:
    te = modes.te011(res[tag])
    if not te:
        print(f"{GAP[tag]:>8.2f}   no TE011 found")
        continue
    ql = q_loaded(tag, te["f"])
    qext = (1.0 / (1.0 / ql - 1.0 / te["Q0"])
            if ql and ql < te["Q0"] else None)
    rows.append((GAP[tag], te["Q0"], ql, qext))
    print(f"{GAP[tag]:>8.2f}{te['f']:>10.5f}{te['Q0']:>10,.0f}"
          f"{ql if ql else float('nan'):>10,.0f}"
          f"{qext if qext else float('nan'):>11,.0f}{te['s_db']:>10.3f}")

print("\nVERDICT")
if len(rows) >= 2:
    qs = [r[3] for r in rows if r[3]]
    if len(qs) >= 2 and max(qs) / min(qs) < 1.15:
        print("  🔴 Q_ext is INDEPENDENT of gap width — the 0.15-0.6 mm feature is "
              "below the mesh floor and is not being resolved.\n"
              "     The answer is local refinement at the gap, NOT a different "
              "gap. Do not read a coupling conclusion from this.")
    else:
        best = min((r for r in rows if r[3]), key=lambda r: abs(r[3] - 320))
        print(f"  ✅ Q_ext responds to gap width. Closest to the ~320 target: "
              f"gap {best[0]:.2f} mm -> Q_ext {best[3]:,.0f}")
        print(f"     bare loop here: {rows[0][3]:,.0f}" if rows[0][3] else "")
        print("     If a gap reaches ~320, the series C closes the match R56 "
              "said was 52x away, and entry 99 is withdrawn rather than "
              "suspended.")
print(flush=True)
