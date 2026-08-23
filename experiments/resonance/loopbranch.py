"""Re-score h3_loopsize's beta with the COUPLING BRANCH resolved from PHASE.

🔴 WHY. `h3_driven.fit_dip` computes beta from the dip depth as
(1-|S11|)/(1+|S11|) — always < 1, i.e. it ASSUMES undercoupled. That was safe
while every measured beta was 0.015-0.098, and it stops being safe the moment a
sweep is designed to REACH critical coupling.

|S11| is IDENTICAL for beta and 1/beta:

    beta=0.578 -> -11.46 dB          beta=1.730 -> -11.46 dB
    beta=0.300 ->  -5.38 dB          beta=3.330 ->  -5.38 dB

So a loop that actually reaches beta=1.73 is reported as 0.578, and the sweep
looks like beta RISING THEN SATURATING BELOW 1 — a smooth, physical-looking,
entirely wrong conclusion, and exactly the shape someone would believe.

🔑 The phase resolves it: an overcoupled one-port advances ~360 deg through
resonance, an undercoupled one returns to where it started. `e0k2_anchor` has
carried `branch_from_phase` for this since 2026-08-22 — including its own hard
lesson that a swing within a few degrees of 180 is AMBIGUOUS and must be
reported as such rather than decided.

⚠️ No re-solving. The phase column is already in port-S.csv (§10).
"""
import csv
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from e0k2_anchor import branch_from_phase
from h3_driven import local_minima, fit_dip, Q_BARE


def s11_with_phase(tag):
    rows = list(csv.reader(
        (pathlib.Path("postpro") / tag / "port-S.csv").read_text().splitlines()))
    return [(float(r[0]), float(r[1]), float(r[2]))
            for r in rows[1:] if len(r) > 2]


def main():
    src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1
                       else "h3_loopsize.result.json")
    out = json.loads(src.read_text())
    print(f"  re-scoring {src} with the branch resolved from PHASE\n")
    print(f"  {'loop':>9}{'area':>8}{'|S11|dB':>9}{'swing':>9}{'branch':>14}"
          f"{'beta':>9}{'was':>9}{'pred':>8}")
    rows = []
    for p in out["points"]:
        if "beta" not in p:
            continue
        d = s11_with_phase(f"{p['tag']}_wide")
        i0 = min(range(len(d)), key=lambda i: abs(d[i][0] - p["f_ghz"]))
        branch, swing = branch_from_phase(d, i0)
        S0 = 10 ** (p["fit"]["s11_db"] / 20)
        b_under = (1 - S0) / (1 + S0)
        b_over = (1 + S0) / (1 - S0) if S0 < 1 else float("inf")
        if branch == "AMBIGUOUS":
            beta = None
        else:
            beta = b_under if branch == "undercoupled" else b_over
        name = "%gx%g" % (p["ld"], p["lw"])
        print(f"  {name:>9}{p['area_mm2']:>8.0f}{p['fit']['s11_db']:>9.2f}"
              f"{swing:>8.1f}°{branch:>14}"
              + (f"{beta:>9.3f}" if beta else f"{'—':>9}")
              + f"{p['beta']:>9.3f}{p['beta_pred']:>8.3f}")
        if beta:
            rows.append((p["area_mm2"], beta, p["beta_pred"], p.get("eta")))
            p["beta_branch"] = branch
            p["phase_swing_deg"] = swing
            p["beta_resolved"] = beta
            if p.get("Q0"):
                p["Q_ext_resolved"] = p["Q0"] / beta
    if not rows:
        print("\n  🔴 no branch resolved — nothing re-scored.")
        return
    print()
    flipped = [r for r, p in zip(rows, [q for q in out["points"] if "beta" in q])
               if abs(r[1] - p["beta"]) > 1e-9]
    if flipped:
        print(f"  🔴 {len(flipped)} case(s) were OVERCOUPLED and had been "
              f"reported as their reciprocal.")
    else:
        print("  ✅ every case is undercoupled — the depth-only beta was right, "
              "and is now CHECKED rather than assumed.")
    if len(rows) >= 2:
        n = (math.log(rows[-1][1] / rows[0][1])
             / math.log(rows[-1][0] / rows[0][0]))
        print(f"  measured exponent with the branch resolved: "
              f"beta ~ area^{n:.2f}  (small-loop model: 2.00)")
    best = min(rows, key=lambda r: abs(r[1] - 1.0))
    S = abs((1 - best[1]) / (1 + best[1]))
    print(f"  🔑 closest to critical: {best[0]:.0f} mm^2, beta={best[1]:.3f}, "
          f"{100*S**2:.1f}% reflected")
    if best is rows[-1] and best[1] < 1.0:
        print("  ⚠️ still rising at the largest loop sampled — the optimum is "
              "NOT bracketed (§1).")
    p2 = src.with_name(src.stem + ".branch.json")
    p2.write_text(json.dumps(out, indent=1) + "\n")
    print(f"\n  wrote {p2}")


if __name__ == "__main__":
    main()
