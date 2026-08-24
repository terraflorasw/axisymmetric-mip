"""E0k2-betacause — is the residual beta spread SYMMETRY or CONVERGENCE?

🔴 WHERE THIS STANDS. Resolving the lumped port (2 -> 42 elements, R112) cut the
beta spread between two meshes of identical geometry from 64.1% to 44.2%, and
improved Q0-vs-eigen to 1.1%. But V1 wanted <= 10%, F1 fired, and the declared
response was: the port was not the cause, look elsewhere, do NOT re-fit.

TWO CANDIDATES, and they are separable by construction:

  SYMMETRY    the sector partition imposes C_n symmetry on the mesh; the
              unpartitioned mesh imposes none. The mode is ~35% hybridised
              TE011/TM111, and hybridisation is driven by symmetry breaking, so
              different partitions may produce genuinely different MIXTURES.
  CONVERGENCE beta has never had a mesh convergence study. Every mesh figure in
              INSTRUMENT is for FREQUENCY (mesh-to-mesh <= 21 kHz); nothing
              establishes that beta is converged at sf = 1.5.

THE DESIGN. Three points, two comparisons, one variable changed each time:

  5 sectors @ sf 1.5    ALREADY SOLVED, beta = 0.4081        (reused, not re-run)
  9 sectors @ sf 1.5    changes SYMMETRY only    (C5 -> C9)
  5 sectors @ sf 1.2    changes RESOLUTION only  (finer mesh, same partition)

🔑 Both new cases carry AZIMUTHAL BINS, so A2/A0 — the hybridisation fraction —
is measurable on all three. If the mixture differs, that is a direct measurement
of the symmetry mechanism rather than an inference about it.

⚠️ The 1-sector mesh CANNOT be compared this way: with one bin there is no
azimuthal information at all. That is why it is excluded here — the diagnostic
requires the very feature under suspicion.

VERIFICATION / FALSIFICATION — declared as a 2x2, so no outcome is unfalsifiable
  V1  beta(5 @1.5) vs beta(9 @1.5) within 10%  -> partition is NOT the variable
  V2  beta(5 @1.5) vs beta(5 @1.2) within 10%  -> resolution is NOT the variable

  V1 pass, V2 fail -> 🔴 CONVERGENCE. beta is not converged at sf 1.5 and every
                        beta in the record needs a resolution study.
  V1 fail, V2 pass -> 🔴 SYMMETRY. The mesh partition changes the mode mixture;
                        beta is only comparable within one partition.
  both fail        -> 🔴 BOTH, or a third cause. Report; do not choose.
  both pass        -> 🔴 the 1-SECTOR mesh is the outlier and the question
                        becomes why an unpartitioned mesh differs at all.

⚠️ Do NOT adopt a mechanism this rig does not distinguish. Two plausible
mechanisms have already been adopted early in this programme and both were wrong.
"""
import json
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
import solveconf
import eigmodes
import qfit
import azimuthal
from e0_solver_vs_math import GEO, eigen_cfg, run
from e0k2_anchor import (design_point, wall_sigma, shared_energy_list,
                         CAP_R_FRAC, LOOP_PHI, LOOP_RW, LOOP_GAP, N_MODES,
                         FREQ_STEP, BAND_HALFWIDTH_MHZ)
from e0k2_azim import sector_bins, read_sector_energy

TAG = "e0k2_betacause"
LD, LW = 11.0, 8.0
# (label, sectors, size_factor) — the reused point is stated so the comparison
# is explicit rather than implied
REUSED = {"label": "5sec@1.5", "sectors": 5, "sf": "1.5", "beta": 0.4081,
          "tag": "e0k2_portfix_s5"}
CASES = [("9sec@1.5", 9, "1.5"), ("5sec@1.2", 5, "1.2")]


def solve_case(tag, a, L, cap_r, sectors, sf, sigma, exact, fmin, band):
    args = (list(GEO) + ["--radius", f"{a:.6f}", "--length", f"{L:.6f}",
                         "--sectors", str(sectors),
                         "--loop", f"{LD},{LW},{LOOP_RW},{LOOP_GAP}",
                         "--loop-cap", f"{cap_r:.4f}", "--loop-phi", LOOP_PHI])
    r = subprocess.run([sys.executable, "geometry.py", "--out", f"{tag}.msh",
                        "--size-factor", sf] + args,
                       capture_output=True, text=True)
    if r.returncode or not pathlib.Path(f"{tag}.msh").exists():
        raise RuntimeError(f"{tag}: mesh failed — {(r.stdout + r.stderr)[-300:]}")
    for line in (r.stdout + r.stderr).splitlines():
        if "PORT refinement" in line:
            print(f"    {line.strip()}", flush=True)
    m = solveconf.load_meta(f"{tag}.msh")
    bins = sector_bins(m)
    en = shared_energy_list(m["attributes"])
    print(f"    {m['tets']:,} tets, {len(bins)} azimuthal bins, floor "
          f"{(m.get('sizing_mm') or {}).get('min'):.3f} mm", flush=True)
    if len(bins) != sectors:
        raise RuntimeError(f"{tag}: asked for {sectors} sectors, mesh has "
                           f"{len(bins)}. --sectors did not take effect.")

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
    cd, _mm, _dr = solveconf.driven(f"{tag}.msh", td, band, step=FREQ_STEP,
                                    order=2)
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
        raise RuntimeError(f"{td}: {res['error']}")

    near = min(modes, key=lambda x: abs(x["f"] - res["f0"]))
    ud = read_sector_energy(td, bins, row_key=res["f0"])
    m_d, conf_d, h_d = azimuthal.order(ud)
    sece = read_sector_energy(te, bins)
    ue = sece.get(float(near["m"])) or sece[min(sece, key=lambda x: abs(x - near["m"]))]
    m_e, conf_e, h_e = azimuthal.order(ue)
    return {"tets": m["tets"], "sectors": len(bins), "sf": sf,
            "beta": res["beta"], "Q_L": res["Q_L"], "s11_db": res["s11_db"],
            "f0": res["f0"], "Q0_driven": res["Q_L"] * (1 + res["beta"]),
            "Q_eigen": qs.get(near["m"]), "f_eigen": near["f"],
            "A2_A0_driven": h_d.get(2), "A2_A0_eigen": h_e.get(2)}


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    a, L = design_point()
    sigma = wall_sigma()
    cap_r = CAP_R_FRAC * a
    exact = ph.spectrum(a, L, fmax=3.2)["TE011"]
    fmin = exact - 0.20
    band = (exact - BAND_HALFWIDTH_MHZ / 1e3, exact + BAND_HALFWIDTH_MHZ / 1e3)
    out = {"reused": REUSED, "cases": {}}
    print(f"  reusing {REUSED['label']}: beta = {REUSED['beta']:.4f} "
          f"(from {REUSED['tag']}, not re-solved)\n", flush=True)

    for label, sectors, sf in CASES:
        tag = f"{TAG}_{label.replace('@','_').replace('.','p')}"
        print(f"\n{'='*78}\n  {label}  ({sectors} sectors, sf {sf})", flush=True)
        try:
            rec = solve_case(tag, a, L, cap_r, sectors, sf, sigma, exact, fmin, band)
        except RuntimeError as e:
            print(f"    🔴 {e}\n    REPORTED, not skipped.", flush=True)
            out["cases"][label] = {"error": str(e)}
            json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
            continue
        out["cases"][label] = rec
        print(f"    beta={rec['beta']:.4f}  Q_L={rec['Q_L']:,.0f}  "
              f"|S11|min={rec['s11_db']:.3f} dB")
        print(f"    Q0_driven={rec['Q0_driven']:,.0f} vs eigen "
              f"{rec['Q_eigen']:,.0f} -> {100*abs(rec['Q0_driven']/rec['Q_eigen']-1):.1f}%")
        print(f"    A2/A0: driven {rec['A2_A0_driven']:.4f}  "
              f"eigen {rec['A2_A0_eigen']:.4f}", flush=True)
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)

    print("\n" + "=" * 78)
    b0 = REUSED["beta"]
    got = {k: v for k, v in out["cases"].items() if "beta" in v}
    print(f"  {'case':<12}{'sectors':>9}{'sf':>6}{'beta':>9}{'vs 5@1.5':>10}"
          f"{'A2/A0 eig':>11}")
    print(f"  {REUSED['label']:<12}{5:>9}{'1.5':>6}{b0:>9.4f}{'—':>10}"
          f"{0.1087:>11.4f}")
    for k, v in got.items():
        print(f"  {k:<12}{v['sectors']:>9}{v['sf']:>6}{v['beta']:>9.4f}"
              f"{100*abs(v['beta']/b0-1):>9.1f}%{v['A2_A0_eigen']:>11.4f}")

    v1 = got.get("9sec@1.5")
    v2 = got.get("5sec@1.2")
    print()
    if not v1 or not v2:
        print("  🔴 a case is missing — the 2x2 cannot be resolved. REPORTED.")
        json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
        return
    d1, d2 = abs(v1["beta"] / b0 - 1), abs(v2["beta"] / b0 - 1)
    p1, p2 = d1 <= 0.10, d2 <= 0.10
    print(f"  V1 partition (5 vs 9 sectors): {d1:.1%} "
          + ("✅ partition is NOT the variable" if p1 else "🔴 partition MATTERS"))
    print(f"  V2 resolution (sf 1.5 vs 1.2): {d2:.1%} "
          + ("✅ resolution is NOT the variable" if p2 else "🔴 resolution MATTERS"))
    print()
    if p1 and not p2:
        verdict = ("🔴 CONVERGENCE. beta is not converged at sf 1.5. Every beta "
                   "in the record needs a resolution study before use.")
    elif p2 and not p1:
        verdict = ("🔴 SYMMETRY. The mesh partition changes the mode mixture; "
                   "beta is only comparable within one partition.")
    elif not p1 and not p2:
        verdict = ("🔴 BOTH, or a third cause. Report the numbers; do NOT choose "
                   "a mechanism this rig does not distinguish.")
    else:
        verdict = ("🔴 the 1-SECTOR mesh is the outlier — sectored meshes agree "
                   "with each other. The question becomes why an UNPARTITIONED "
                   "mesh differs at all.")
    print(f"  VERDICT: {verdict}")
    out["verdict"] = {"v1_partition_pct": d1, "v2_resolution_pct": d2,
                      "v1_pass": bool(p1), "v2_pass": bool(p2),
                      "text": verdict}
    json.dump(out, open(f"{TAG}.result.json", "w"), indent=1)
    print(f"\n  wrote {TAG}.result.json", flush=True)


if __name__ == "__main__":
    main()
