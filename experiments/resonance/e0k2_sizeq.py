"""E0k2-sizeQ — eigenmode Q for every loop size, with NO fitting anywhere.

🔴 THE ANOMALY THIS EXISTS TO KILL. Driven fits across the loop-area sweep gave
Q0 = 20,005 / 24,920 / 28,387 / 30,112 for areas 35 / 82 / 176 / 384 mm^2 —
SMALLER loops apparently costing MORE Q, monotonically, against a bare-cavity
Q0 of 44,384. That is backwards: a smaller obstacle should perturb less.

🔑 THE SUSPICION, AND WHY IT IS ONLY A SUSPICION. Absorbed power is EXACTLY
Lorentzian for a single resonance. Fitting one to these curves over +/-3
linewidths gives rms/peak of 19.3% / 2.4% / 1.8% / 1.1% — the fit degrades
monotonically as the loop shrinks, and at 35 mm^2 the 3 dB width and the
Lorentzian fit disagree by 2x. So the trend may be an artifact of forcing a
one-resonance model onto a two-resonance curve, with the contamination growing
as the loop's splitting of the degenerate pair shrinks.

⚠️ That is inference from fits, and this programme has twice adopted a
plausible mechanism before measuring it. Eigenmode Q needs NO fit, NO coupling
model, NO branch decision and NO probe: Palace returns the complex eigenvalue
and Q is its imaginary part. If the eigen trend is flat or rises with area, the
driven trend was the artifact. If eigen reproduces the backwards trend, it is
real and something physical is going on.

VERIFICATION
  V1  every solve identifies TE011 by Q (frequencies are near-degenerate, so
      frequency cannot), and TE011 must out-Q TM111 in each.
  V2  Q must fall monotonically toward the bare-cavity 44,384 as loop area
      falls — that is what "a smaller obstacle perturbs less" MEANS.

FALSIFICATION
  🔴 F1  if eigen Q rises with loop area, matching the driven trend, the
         backwards behaviour is REAL and the fitting explanation is dead.
  🔴 F2  the measured TE011/TM111 splitting per size tests the blend story
         directly. Blending needs the smallest loop's splitting to be a few
         linewidths and the largest's to be many.
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import eigmodes
import solveconf
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import (design_point, wall_sigma, shared_energy_list,
                         CANDIDATES, CAP_R_FRAC, LOOP_PHI, LOOP_RW, LOOP_GAP,
                         N_MODES)

TAG = "e0k2_sizeq"
BARE_Q = 44384.0


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma = wall_sigma()
    cap_r = CAP_R_FRAC * a
    EX = ph.spectrum(a, L, fmax=3.2)
    exact = EX["TE011"]
    fmin = exact - 0.20
    print(f"  a={a:.4f} L={L:.4f}  wall {sigma:.3g}  cap loop r={cap_r:.3f}\n",
          flush=True)

    out = []
    for ld, lw in CANDIDATES:
        base = f"e0k2_c{ld:g}x{lw:g}".replace(".", "p")
        tag = f"{base}_eig"
        area = 2 * ld * lw
        print(f"  --- {base}: {ld} x {lw} mm, area {area:.0f} mm^2", flush=True)
        # 🔑 REUSE the mesh the sizing sweep already built. Re-meshing would be
        # a different mesh (gmsh jitter is 8 kHz, small but pointless here) and
        # would break the comparison with the driven solve on the SAME file.
        msh = pathlib.Path(f"{base}.msh")
        if not msh.exists():
            geo = list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}"]
            loop = ["--loop", f"{ld},{lw},{LOOP_RW},{LOOP_GAP}",
                    "--loop-cap", f"{cap_r:.4f}", "--loop-phi", LOOP_PHI]
            r = subprocess.run([sys.executable, "geometry.py", "--out", str(msh),
                                "--size-factor", "1.5"] + geo + loop,
                               capture_output=True, text=True)
            if r.returncode or not msh.exists():
                print(f"    🔴 mesh failed — REPORTED, not skipped"); continue
            print(f"    (re-meshed)")
        else:
            print(f"    reusing {msh}")
        m = solveconf.load_meta(str(msh))
        attrs = m["attributes"]
        if pathlib.Path("postpro", tag, "eig.csv").exists():
            print(f"    reusing existing solve {tag}")
        else:
            c = eigen_cfg(tag, m, mesh=str(msh), sigma=sigma,
                          n=N_MODES, target=fmin)
            c["Solver"]["Order"] = 2
            c["Domains"]["Postprocessing"]["Energy"] = shared_energy_list(attrs)
            c["Boundaries"]["PEC"] = {"Attributes": [attrs["port"]]}
            for mat in c["Domains"]["Materials"]:
                for k, want in (("Permittivity", 1.0), ("LossTan", 0.0),
                                ("Conductivity", 0.0)):
                    if k in mat and mat[k] != want:
                        mat[k] = want
            try:
                run(tag, c)
            except RuntimeError as e:
                print(f"    🔴 {e}\n    REPORTED, not skipped."); continue

        modes = eigmodes.read(tag)
        qs = {}
        for line in (pathlib.Path("postpro") / tag /
                     "eig.csv").read_text().splitlines()[1:]:
            p_ = line.split(",")
            if len(p_) > 3:
                qs[round(float(p_[0]))] = float(p_[3])
        fs = [md["f"] for md in modes]
        ql = [qs.get(md["m"], 0.0) for md in modes]
        pair = eigmodes.te011_tm111(fs, exact, ql, fmin=fmin)
        rec = {"tag": base, "ld": ld, "lw": lw, "area": area,
               "modes": [{"f": md["f"], "Q": qs.get(md["m"])} for md in modes]}
        if not pair:
            print(f"    🔴 te011_tm111 REFUSED — no Q for this size")
            out.append(rec)
            continue
        q_te = ql[pair["te011_index"]]
        q_tm = sum(ql[i] for i in pair["tm111_indices"]) / 2.0
        rec.update(q_te011=q_te, q_tm111=q_tm, f_te011=pair["te011"],
                   splitting_mhz=pair["splitting_mhz"],
                   q_margin=pair["q_margin"], pair_q_ratio=pair["pair_q_ratio"],
                   how=pair["how"])
        out.append(rec)
        print(f"    TE011 {pair['te011']:.6f}  Q={q_te:,.0f}  "
              f"({100*(1-q_te/BARE_Q):+.1f}% vs bare)  "
              f"split {pair['splitting_mhz']:.3f} MHz  "
              f"q_margin {pair['q_margin']:.2f}", flush=True)
        json.dump({"bare_q": BARE_Q, "sizes": out},
                  open(f"{TAG}.result.json", "w"), indent=1)

    print("\n" + "=" * 78)
    print(f"  {'area':>7}{'eigen Q':>11}{'vs bare':>10}{'split MHz':>11}"
          f"{'driven Q0':>11}{'driven vs bare':>16}")
    DRV = {35: 20005, 82: 24920, 176: 28387, 384: 30112}
    good = [r for r in out if "q_te011" in r]
    for r in good:
        d = DRV.get(int(r["area"]))
        print(f"  {r['area']:>7.0f}{r['q_te011']:>11,.0f}"
              f"{100*(1-r['q_te011']/BARE_Q):>9.1f}%{r['splitting_mhz']:>11.3f}"
              + (f"{d:>11,}{100*(1-d/BARE_Q):>15.1f}%" if d else f"{'—':>11}{'—':>16}"))
    print(f"  {'bare':>7}{BARE_Q:>11,.0f}{0.0:>9.1f}%{'0 (exact)':>11}")

    if len(good) > 1:
        qs_ = [r["q_te011"] for r in sorted(good, key=lambda r: r["area"])]
        rising = all(b >= a_ for a_, b in zip(qs_, qs_[1:]))
        falling = all(b <= a_ for a_, b in zip(qs_, qs_[1:]))
        print()
        if falling:
            print("  ✅ V2/F1: eigen Q FALLS as loop area rises — a bigger obstacle")
            print("     perturbs more, as physics requires. The driven trend was")
            print("     the artifact, and the single-Lorentzian fit quality")
            print("     (19.3% -> 1.1% rms as area rises) is why.")
        elif rising:
            print("  🔴 F1 FIRES: eigen Q RISES with loop area, reproducing the")
            print("     driven trend with no fitting involved. The backwards")
            print("     behaviour is REAL. Do not explain it away — find it.")
        else:
            print("  ⚠️ eigen Q is NON-MONOTONIC in loop area. Neither the fitting")
            print("     explanation nor a simple perturbation picture survives;")
            print("     report the numbers and investigate, do not narrate.")
    json.dump({"bare_q": BARE_Q, "sizes": out},
              open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
