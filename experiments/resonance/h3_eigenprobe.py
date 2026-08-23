"""H3 probe — WHERE does the eigensolver stop converging on a lossy plasma?

🔴 WHY THIS EXISTS. One eigen configuration stalled (nconv=0, 65 min) and I
concluded "the eigenmode solver cannot handle a bulk lossy plasma" and wrote it
into INSTRUMENT as measured fact. **That was n=1.** Palace supports lossy
materials in eigenmode; the real question is whether THIS problem converges with
THESE settings, and nothing was varied before the capability claim was made.

🔑 AND EIGEN IS THE BETTER TOOL IF IT WORKS. H3 needs Q and f of the loaded
cavity. Eigen gives both DIRECTLY — no port, no coupling model, 155-882 s.
Driven gives them through a port that perturbs by 32% and via Q0 = Q_L(1+beta),
dragging beta into a measurement beta would otherwise contaminate, at 8x the
cost. Abandoning eigen on one failure gave up the better instrument without
establishing it was unusable.

## The design: vary ONE thing at a time from the configuration that failed

    baseline    ne=1e18, R=2, plasma-h 0.4, target 2.15   — must reproduce the stall
    coarse      plasma-h 1.0                              — tests the MESH RATIO
    target      target 2.40 instead of 2.15               — tests the SHIFT
    both        coarse + target                           — if either helps alone

then, on whatever configuration works, sweep n_e to find the BOUNDARY:

    1e15 .. 1e21, log — where does convergence actually stop?

⚠️ `--plasma-h 0.4` forced a 0.32 mm mesh floor against a 15 mm air size — a 47x
size ratio, which is hard on multigrid. That is the leading suspect and it is a
mesh problem, not a Palace limitation.

## Budgets: BOTH kinds, because they catch different failures

🔴 NLEPS_BUDGET alone cannot help here. The stall managed 19 NLEPS iterations in
65 minutes, so reaching 1,000 would take ~57 HOURS. A budget in ITERATIONS
catches many-cheap-iterations; this failure is few-expensive-iterations and needs
a WALL-CLOCK budget. Every case here gets 600 s — a working configuration solved
the bare cavity in 155 s, so 10 minutes is generous and a stall dies fast.

VERIFICATION
  V1  the baseline must STALL. If it converges, the original failure was
      environmental and nothing here is trustworthy — including the INSTRUMENT
      entry this probe exists to check.
  V2  any case that converges must give a physically sane result: TE011 near
      2.45 GHz with Q below the 44,384 bare value (a plasma can only ADD loss).
FALSIFICATION
  🔴 F1  if NO configuration converges at any n_e, the capability claim stands
         and driven is justified — with evidence rather than one data point.
  🔴 F2  if the baseline converges once the mesh ratio is fixed, then the stall
         was MY MESH, not Palace, and the INSTRUMENT entry must be retracted.
"""
import json
import math
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
import eigmodes
import solvecost
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import design_point, wall_sigma
from h3_loaded import drude, skin_depth, Z_FRAC, INNER_R, SECTORS

TAG = "h3_eigenprobe"
CASE_TIMEOUT_S = 600.0
R_MM = 2.0
N_MODES = 4                 # fewer than H3's 6: this asks CAN it, not what


def build(tag, a, L, ne, plasma_h):
    zlo, zhi = -Z_FRAC * L, Z_FRAC * L
    args = (list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                         "--sectors", str(SECTORS),
                         "--plasma", f"{INNER_R},{R_MM},{zlo:.4f},{zhi:.4f}",
                         "--plasma-h", f"{plasma_h:.3f}"])
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--size-factor", "1.5"] + args,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        raise RuntimeError(f"mesh failed: {(r.stdout + r.stderr)[-250:]}")
    return solveconf.load_meta(f"{tag}.msh")


def attempt(label, a, L, sigma_w, exact, ne, plasma_h, target):
    """One configuration. Returns a record; NEVER raises past the caller."""
    w = 2.0 * math.pi * 2.45e9
    eps, sig = drude(ne, w)
    tag = f"{TAG}_{label}"
    rec = {"label": label, "ne": ne, "plasma_h": plasma_h, "target": target,
           "eps": eps, "sigma": sig}
    print(f"\n  --- {label}: ne={ne:.0e} plasma_h={plasma_h} target={target} "
          f"(eps={eps:.3f}, sigma={sig:.3g} S/m)", flush=True)
    try:
        m = build(tag, a, L, ne, plasma_h)
    except RuntimeError as e:
        rec["outcome"] = "mesh_failed"; rec["detail"] = str(e)
        print(f"    🔴 {e}", flush=True); return rec
    attrs = m["attributes"]
    floor = (m.get("sizing_mm") or {}).get("min")
    rec.update(tets=m["tets"], floor_mm=floor,
               size_ratio=(m.get("sizing_mm") or {}).get("air", 0) / floor
               if floor else None)
    print(f"    {m['tets']:,} tets, floor {floor:.3f} mm, "
          f"air/floor ratio {rec['size_ratio']:.0f}x", flush=True)

    vols = sorted({v for k, v in attrs.items()
                   if isinstance(v, int) and k not in ("wall", "port")}
                  | set(attrs.get("air") or []))
    c = eigen_cfg(tag, m, mesh=f"{tag}.msh", sigma=sigma_w,
                  n=N_MODES, target=target)
    c["Solver"]["Order"] = 2
    others = sorted(set(vols) - {attrs["plasma"]})
    c["Domains"]["Materials"] = [{"Attributes": others, "Permittivity": 1.0,
                                  "Permeability": 1.0},
                                 {"Attributes": [attrs["plasma"]],
                                  "Permittivity": eps, "Permeability": 1.0,
                                  "Conductivity": sig}]
    t0 = __import__("time").time()
    try:
        # 🔑 allow_lossy_eigen: this rig EXISTS to test that refusal's premise.
        run(tag, c, allow_lossy_eigen=True, timeout=CASE_TIMEOUT_S)
    except RuntimeError as e:
        dt = __import__("time").time() - t0
        h = solvecost.harvest(f"{tag}_p.log")
        rec.update(outcome="did_not_converge", seconds=dt,
                   nleps=h.get("nleps_its"), nconv=h.get("nleps_nconv"),
                   detail=str(e)[:180])
        print(f"    🔴 did not converge in {dt:.0f}s "
              f"(NLEPS {h.get('nleps_its')}, nconv {h.get('nleps_nconv')})",
              flush=True)
        return rec
    dt = __import__("time").time() - t0
    h = solvecost.harvest(f"{tag}_p.log")
    modes = eigmodes.read(tag)
    qs = {}
    for line in (pathlib.Path("postpro") / tag /
                 "eig.csv").read_text().splitlines()[1:]:
        pp = line.split(",")
        if len(pp) > 3:
            qs[round(float(pp[0]))] = float(pp[3])
    pick = max(modes, key=lambda md: qs.get(md["m"], 0)) if modes else None
    rec.update(outcome="converged", seconds=dt, nleps=h.get("nleps_its"),
               nconv=h.get("nleps_nconv"), n_modes=len(modes),
               f_ghz=pick["f"] if pick else None,
               Q=qs.get(pick["m"]) if pick else None)
    print(f"    ✅ converged in {dt:.0f}s — {len(modes)} modes, "
          f"highest-Q at {rec['f_ghz']:.6f} GHz, Q={rec['Q']:,.0f} "
          f"(NLEPS {h.get('nleps_its')})", flush=True)
    return rec


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma_w = wall_sigma()
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    out = {"case_timeout_s": CASE_TIMEOUT_S, "R_mm": R_MM, "cases": []}

    def save():
        import os
        p = pathlib.Path(f"{TAG}.result.json")
        t = p.with_suffix(p.suffix + f".tmp{os.getpid()}")
        t.write_text(json.dumps(out, indent=1) + "\n")
        os.replace(t, p)

    # ---- phase 1: vary ONE thing at a time from the failing configuration ----
    print(f"\n{'='*78}\n  PHASE 1 — reproduce the stall, then vary one thing\n")
    plan = [("baseline", 1e18, 0.4, 2.15),
            ("coarse",   1e18, 1.0, 2.15),
            ("target",   1e18, 0.4, 2.40),
            ("both",     1e18, 1.0, 2.40)]
    for label, ne, ph_, tgt in plan:
        out["cases"].append(attempt(label, a, L, sigma_w, exact, ne, ph_, tgt))
        save()

    base = next((c for c in out["cases"] if c["label"] == "baseline"), None)
    if base and base.get("outcome") == "converged":
        print(f"\n  🔴 V1 FAILS: the baseline CONVERGED. The original 65-minute "
              f"stall was environmental, not a capability limit — and the "
              f"INSTRUMENT entry claiming otherwise must be retracted.")
    works = [c for c in out["cases"] if c.get("outcome") == "converged"]
    if not works:
        print(f"\n  🔴 F1: NO configuration converged at ne=1e18. The capability "
              f"claim stands and driven is justified — now on 4 points, not 1.")
        save(); _summary(out); return

    best = min(works, key=lambda c: c["seconds"])
    print(f"\n  ✅ best configuration: {best['label']} "
          f"(plasma_h={best['plasma_h']}, target={best['target']}, "
          f"{best['seconds']:.0f}s)")
    if base and base.get("outcome") != "converged":
        print(f"  🔑 F2: the baseline stalled and {best['label']} did NOT — so "
              f"the stall was the CONFIGURATION, not Palace.")

    # ---- phase 2: sweep n_e on the working configuration -> the boundary ----
    print(f"\n{'='*78}\n  PHASE 2 — where does it actually stop? n_e sweep on "
          f"'{best['label']}'\n")
    for ne in (1e15, 1e16, 1e17, 1e19, 1e20, 1e21):
        out["cases"].append(attempt(f"ne{math.log10(ne):.0f}", a, L, sigma_w,
                                    exact, ne, best["plasma_h"], best["target"]))
        save()
    _summary(out)
    save()


def _summary(out):
    print("\n" + "=" * 78)
    print(f"  {'case':<12}{'ne':>9}{'sigma':>10}{'plasma_h':>10}{'target':>8}"
          f"{'outcome':>18}{'s':>7}{'NLEPS':>7}{'nconv':>7}")
    for c in out["cases"]:
        print(f"  {c['label']:<12}{c['ne']:>9.0e}{c.get('sigma',0):>10.3g}"
              f"{c.get('plasma_h',0):>10.1f}{c.get('target',0):>8.2f}"
              f"{c.get('outcome','?'):>18}{c.get('seconds',0):>7.0f}"
              f"{str(c.get('nleps','-')):>7}{str(c.get('nconv','-')):>7}")
    conv = [c for c in out["cases"] if c.get("outcome") == "converged"]
    if not conv:
        print("\n  🔴 nothing converged. Driven is the tool, on evidence.")
        return
    sig_ok = max(c["sigma"] for c in conv)
    sig_bad = [c["sigma"] for c in out["cases"]
               if c.get("outcome") == "did_not_converge"]
    print(f"\n  converged up to sigma = {sig_ok:.3g} S/m")
    if sig_bad:
        print(f"  first failure at sigma = {min(sig_bad):.3g} S/m")
        print(f"  🔑 THE BOUNDARY is between them. H3's interesting range is "
              f"0.28-275 S/m; if the boundary sits below it, driven is needed "
              f"and now we know WHY and WHERE.")
    else:
        print(f"  ✅ no failures — eigen covers the whole probed range and H3 "
              f"stays eigen at 8x less cost than driven.")


if __name__ == "__main__":
    main()
