"""E0k2-portfix — does beta agree between meshes now the port is RESOLVED?

🔴 THE DEFECT. The lumped port meshed with **2 elements** on a 1.8 x 0.30 mm
rectangle against a 1.2 mm floor: the primary port gap sat 4x below the mesh
floor. R62 diagnosed exactly this for the SERIES capacitor gap — "a first
attempt left it below the mesh floor and Q_ext came back identical to 4
significant figures across gaps of 0, 0.15, 0.30 and 0.60 mm" — and fixed it
there ONLY. The primary gap was never given the same treatment.

Consequences measured before the fix:
  * the SAME geometry at 1 and 5 azimuthal sectors gave beta 0.5598 and 0.3411,
    **39% apart**, with |S11|min differing by 4.8 dB;
  * the loop-area sizing sweep came back NON-MONOTONIC (1.50, 0.87, 0.56, 1.85),
    which no coupling model explains.

⚠️ Q0 = Q_L(1+beta) SURVIVED this. Q_L and beta come from the same S11 curve and
track whatever the actual coupling was, so the anchor's four driven-vs-eigen
comparisons held at 4.9-8.8% throughout. What was never trustworthy is beta as a
DESIGN quantity — "what coupling will this loop geometry give?"

THE FIX (R112): let the primary gap lower the mesh floor, as gap2 already does,
AND add a Ball refinement at the port centre — because lowering the floor alone
refines nothing (R15: the floor only stops a deliberate request being
overridden). Port: 2 -> 42 elements, tets +22%, floor 1.2 -> 0.096 mm, and both
meshes now give the SAME 42.

VERIFICATION
  V1  beta must agree between the 1-sector and 5-sector meshes to within 10%.
      They are the same geometry; only the partition differs.
  V2  Q0 = Q_L(1+beta) must still agree with the eigen Q, as it did before —
      the fix must not break what was already working.
FALSIFICATION
  🔴 F1  if beta still differs by tens of percent, the port was NOT the cause
         and the 39% comes from somewhere else. Say so; do not re-fit.
  🔴 F2  if Q0-vs-eigen agreement gets WORSE, the refinement has disturbed
         something that was right.
"""
import json
import values
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
import eigmodes
import qfit
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import (design_point, wall_sigma, shared_energy_list,
                         CAP_R_FRAC, LOOP_PHI, LOOP_RW, LOOP_GAP, N_MODES,
                         FREQ_STEP, BAND_HALFWIDTH_MHZ)

TAG = "e0k2_portfix"
LD, LW = values.get("loop.size.mm")
BEFORE = {"s1": 0.5598, "s5": 0.3411}


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma = wall_sigma()
    cap_r = CAP_R_FRAC * a
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    fmin = exact - 0.20
    band = (exact - BAND_HALFWIDTH_MHZ / 1e3, exact + BAND_HALFWIDTH_MHZ / 1e3)
    out = {"before": BEFORE, "cases": {}}

    for key, extra in (("s1", []), ("s5", ["--sectors", "5"])):
        tag = f"{TAG}_{key}"
        print(f"\n{'='*78}\n  {tag}  ({'1 sector' if key=='s1' else '5 sectors'})",
              flush=True)
        args = (list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                             "--loop", f"{LD},{LW},{LOOP_RW},{LOOP_GAP}",
                             "--loop-cap", f"{cap_r:.4f}",
                             "--loop-phi", LOOP_PHI] + extra)
        r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                            "--size-factor", "1.5"] + args,
                           capture_output=True, text=True)
        if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
            print(f"    🔴 mesh failed — REPORTED, not skipped"); continue
        for line in (r.stdout + r.stderr).splitlines():
            if "PORT refinement" in line:
                print(f"    {line.strip()}", flush=True)
        m = solveconf.load_meta(f"{tag}.msh")
        en = shared_energy_list(m["attributes"])
        print(f"    {m['tets']:,} tets, floor "
              f"{(m.get('sizing_mm') or {}).get('min'):.3f} mm", flush=True)

        te = f"{tag}_eig"
        # 🔴 port_bc="lumped" — GATE 4, added 2026-08-24 (CONVENTIONS §7v).
        # This rig measures COUPLING, so the port must be the real 50 ohm
        # load — same R and Direction the driven template uses. Q is
        # LOADED (Q_L), not Q0.
        # ⚠️ UNASSIGNED IS PMC — an OPEN gap, which is an LC resonator
        # near 2.45 GHz that HYBRIDISES TE011 into a pair. Everything
        # this rig produced before today was measured that way.
        ce = eigen_cfg(te, m, mesh=f"{tag}.msh", sigma=sigma, n=N_MODES,
                       target=fmin, port_bc="lumped")
        ce["Solver"]["Order"] = 2
        ce["Domains"]["Postprocessing"]["Energy"] = en
        ce["Boundaries"]["PEC"] = {"Attributes": [m["attributes"]["port"]]}
        for mat in ce["Domains"]["Materials"]:
            for k, want in (("Permittivity", 1.0), ("LossTan", 0.0),
                            ("Conductivity", 0.0)):
                if k in mat and mat[k] != want:
                    mat[k] = want
        run(te, ce)
        qs = {}
        for line in (pathlib.Path("postpro") / te /
                     "eig.csv").read_text().splitlines()[1:]:
            p_ = line.split(",")
            if len(p_) > 3:
                qs[round(float(p_[0]))] = float(p_[3])
        modes = eigmodes.read(te)

        td = f"{tag}_drv"
        cd, _mm, _dr = solveconf.driven(f"{tag}.msh", td, band,
                                        step=FREQ_STEP, order=2)
        cd["Domains"]["Postprocessing"]["Energy"] = en
        for mat in cd["Domains"]["Materials"]:
            for k, want in (("Permittivity", 1.0), ("LossTan", 0.0),
                            ("Conductivity", 0.0)):
                if k in mat and mat[k] != want:
                    mat[k] = want
        pathlib.Path(f"{td}.json").write_text(json.dumps(cd, indent=2))
        run(td, cd)
        res = qfit.analyse(td)
        if "error" in res:
            print(f"    🔴 {res['error']}"); continue
        near = min(modes, key=lambda x: abs(x["f"] - res["f0"]))
        qe = qs.get(near["m"])
        q0 = res["Q_L"] * (1 + res["beta"])
        rec = {"tets": m["tets"], "beta": res["beta"], "Q_L": res["Q_L"],
               "s11_db": res["s11_db"], "branch": res["branch"],
               "f0": res["f0"], "Q0_driven": q0, "Q_eigen": qe,
               "f_eigen": near["f"]}
        out["cases"][key] = rec
        print(f"    beta={res['beta']:.4f} (was {BEFORE[key]:.4f})  "
              f"|S11|min={res['s11_db']:.3f} dB  Q_L={res['Q_L']:,.0f}")
        print(f"    Q0_driven={q0:,.0f}  vs eigen {qe:,.0f} -> "
              f"{100*abs(q0/qe-1):.1f}%", flush=True)
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)

    print("\n" + "=" * 78)
    if len(out["cases"]) < 2:
        print("  🔴 only one case completed — V1 cannot be evaluated. REPORTED.")
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
        return
    b1, b5 = out["cases"]["s1"]["beta"], out["cases"]["s5"]["beta"]
    spread = abs(b1 / b5 - 1)
    was = abs(BEFORE["s1"] / BEFORE["s5"] - 1)
    print(f"  {'':<14}{'beta before':>13}{'beta after':>12}")
    print(f"  {'1 sector':<14}{BEFORE['s1']:>13.4f}{b1:>12.4f}")
    print(f"  {'5 sectors':<14}{BEFORE['s5']:>13.4f}{b5:>12.4f}")
    print(f"  {'spread':<14}{was:>12.1%}{spread:>12.1%}")
    print()
    print(f"  V1 beta agrees within 10%: {spread:.1%} "
          + ("✅ THE PORT WAS THE CAUSE" if spread <= 0.10 else
             "🔴 F1 FIRES — the port was NOT the cause. Look elsewhere; do not re-fit."))
    for k in ("s1", "s5"):
        c = out["cases"][k]
        err = abs(c["Q0_driven"] / c["Q_eigen"] - 1)
        print(f"  V2 {k}: Q0 vs eigen {err:.1%} "
              + ("✅" if err <= 0.12 else "🔴 F2 — the fix disturbed what worked"))
    out["verdict"] = {"beta_spread_before": was, "beta_spread_after": spread,
                      "port_was_the_cause": bool(spread <= 0.10)}
    json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
