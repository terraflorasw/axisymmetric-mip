"""H2 — the annular groove, against a formula rather than a search.

The groove is a shorted stub. A radial surface current arriving at the
barrel/end-cap corner sees the slot mouth with input impedance

    Z_in = j Z0 tan(beta d),    beta = 2 pi / lambda,  lambda = 122.36 mm

so d = lambda/4 = 30.59 mm is an OPEN circuit and blocks the current, and
d = lambda/2 = 61.18 mm is a SHORT and the groove is invisible. Position of the
resonance is set by DEPTH and is independent of width; width sets
Z0 ~ eta*gw/(2*pi*a) and the Q cost. So this is a one-dimensional sweep around a
predicted point, not a blind depth x width search.

🔑 WHY IT DISCRIMINATES. TE011 has NO end-cap surface current at all: at the cap
its H is purely axial (H_r ~ sin(pi z/L) -> 0 there), so n x H = 0. TM111 has
radial cap current that must cross the slot. The groove attacks a current one
mode has and the other does not.

🔑 THE TARGET IS THE SOURCE BAND, NOT A LINEWIDTH. The LDMOS tunes 2.40-2.50 GHz.
A rival outside that window cannot be excited at all, so TM111 needs >50 MHz of
detuning, not the maximum the groove can deliver. lambda/4 is over-design; the
product of this sweep is the MINIMUM depth that clears the band with margin, and
what that costs in Q.

VERIFICATION, declared before the run:
  1. TE011 must barely move. It has no cap current, so a groove that shifts
     TE011 as much as TM111 is not working by the claimed mechanism.
  2. the TM111 shift must follow tan(2 pi d / lambda) — rising toward 30.59 mm.

FALSIFICATION:
  🔴 TE011 shifting comparably to TM111 -> the mechanism is wrong, whatever the
     splitting does.
  🔴 no inversion or roll-off past lambda/4 -> it is not behaving as a stub, and
     the formula gives us nothing for choosing depth.

⚠️ sf 1.5 deliberately. This measures a SHIFT of tens of MHz; E0j puts TE011 at
~0.2 MHz on this mesh, i.e. <1% of the effect, and a depth sweep is a differential
comparison where discretisation largely cancels (METHODOLOGY 2b).

⚠️ Q here is an UPPER bound: physics.py refuses wall_Q, so Q is trustworthy in
ratio across the sweep, not absolutely.
"""
import json
import pathlib
import values
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eigmodes
import physics as ph
import solveconf
from e0_solver_vs_math import GEO, eigen_cfg, run
from scipy.optimize import brentq

TAG = "h2"
DL = values.get("cavity.d_over_l")   # H1. BOUND, not copied (7bl). The stub
                                 # resonance is set by lambda, not by cavity
                                 # dimensions, so the depth curve should transfer
                                 # across D/L — assumed, not yet checked.
LAM = 299.792458 / 2.45
DEPTHS = [0.0, 10.0, 20.0, 27.0, LAM / 4, 34.0, 42.0, 52.0]
WIDTH = 5.0
SIGMA = 3.5e7
BAND_MHZ = 50.0                  # half-width of the LDMOS tuning range


def shape(dl):
    L = brentq(lambda L: ph.f_mnp("TE", 0, 1, 1, dl * L / 2, L) - 2.45,
               20.0, 400.0, xtol=1e-10)
    return dl * L / 2, L


def build(tag, a, L, gd):
    args = list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}"]
    if gd > 0:
        args += ["--groove", f"{WIDTH},{gd}"]
    for sf in ("1.5", "1.2", "2.0", "1.0"):
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", sf] + args,
                           capture_output=True, text=True)
        if r.returncode == 0 and pathlib.Path(f"{tag}.msh").exists():
            return solveconf.load_meta(f"{tag}.msh"), sf
    err = [l for l in (r.stdout + r.stderr).splitlines() if "rror" in l]
    raise RuntimeError(f"{tag}: no size factor meshed — {err[-1:] }")


def eig_q(tag):
    f = pathlib.Path("postpro") / tag / "eig.csv"
    rows = []
    for line in f.read_text().splitlines()[1:]:
        p = line.split(",")
        if len(p) > 3:
            rows.append((float(p[1]), float(p[3])))
    rows.sort()
    return [r[0] for r in rows], [r[1] for r in rows]


def main():
    import math
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = shape(DL)
    EX = ph.spectrum(a, L, fmax=3.2)
    print(f"  D/L {DL}: a={a:.3f} L={L:.2f}, groove width {WIDTH} mm")
    print(f"  lambda/4 = {LAM/4:.2f} mm, lambda/2 = {LAM/2:.2f} mm\n", flush=True)

    out = []
    for gd in DEPTHS:
        tag = f"{TAG}_d{gd:.0f}"
        m, sf = build(tag, a, L, gd)
        n = sum(1 for f in EX.values() if f <= 2.57) + 5
        c = eigen_cfg(tag, m, mesh=f"{tag}.msh", sigma=SIGMA, n=n, target=1.05)
        c["Solver"]["Order"] = 2
        run(tag, c)
        fs, qs = eig_q(tag)
        d = eigmodes.te011_tm111(fs, EX["TE011"], qs)
        if not d:
            print(f"    🔴 depth {gd:.1f}: triplet unresolved — REPORTED")
            continue
        q_te = qs[d["te011_index"]]
        q_tm = sum(qs[i] for i in d["tm111_indices"]) / 2.0
        out.append({"depth_mm": gd, "sf": sf, "tets": m["tets"],
                    "te011": d["te011"], "tm111": d["tm111"],
                    "splitting_mhz": d["splitting_mhz"],
                    "q_te011": q_te, "q_tm111": q_tm, "how": d["how"]})
        print(f"    depth {gd:6.2f} mm  ({gd/LAM:.3f} lambda)  "
              f"TE011 {d['te011']:.5f}  TM111 {d['tm111']:.5f}  "
              f"split {d['splitting_mhz']:7.2f} MHz  Q_TE {q_te:,.0f}",
              flush=True)

    base = next((r for r in out if r["depth_mm"] == 0.0), None)
    print("\n" + "=" * 78)
    print(f"  {'depth':>8}{'d/lambda':>10}{'TE011 shift':>13}{'TM111 shift':>13}"
          f"{'splitting':>11}{'Q_TE011':>10}{'Q cost':>9}{'clears band':>13}")
    for r in out:
        dte = 1e3*(r["te011"] - base["te011"]) if base else float("nan")
        dtm = 1e3*(r["tm111"] - base["tm111"]) if base else float("nan")
        qc = (r["q_te011"]/base["q_te011"] - 1) if base else float("nan")
        ok = "✅" if r["splitting_mhz"] > BAND_MHZ else ""
        print(f"  {r['depth_mm']:>8.2f}{r['depth_mm']/LAM:>10.3f}{dte:>13.2f}"
              f"{dtm:>13.2f}{r['splitting_mhz']:>11.2f}{r['q_te011']:>10,.0f}"
              f"{qc:>8.1%}{ok:>13}")

    if base:
        moved = [(abs(1e3*(r['te011']-base['te011'])),
                  abs(1e3*(r['tm111']-base['tm111']))) for r in out
                 if r["depth_mm"] > 0]
        if moved:
            worst = max(t/max(m, 1e-9) for t, m in moved)
            print(f"\n  TE011 moves at most {worst:.1%} as much as TM111 "
                  f"{'✅ discriminating' if worst < 0.25 else '🔴 NOT discriminating'}")
    clears = [r for r in out if r["splitting_mhz"] > BAND_MHZ]
    if clears:
        mn = min(clears, key=lambda r: r["depth_mm"])
        print(f"  MINIMUM depth clearing the {BAND_MHZ:.0f} MHz band: "
              f"{mn['depth_mm']:.2f} mm ({mn['depth_mm']/LAM:.3f} lambda), "
              f"Q cost {(mn['q_te011']/base['q_te011']-1):+.1%}")
    else:
        print(f"  🔴 no depth tested clears {BAND_MHZ:.0f} MHz")
    json.dump({"dl": DL, "a": a, "L": L, "width_mm": WIDTH, "lambda_mm": LAM,
               "rows": out}, open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
