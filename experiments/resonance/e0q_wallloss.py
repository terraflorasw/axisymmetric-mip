"""E0q — is the LOSS model right? The one part of the instrument with no anchor.

E0 characterises FREQUENCY well (0.058 MHz on TE011). It says nothing about Q,
and Q is not incidental: LOD runs through delivered power, which runs through Q
and coupling. Meanwhile every absolute Q in this programme was ~34% high because
the wall was silver by template default for its entire life.

🔑 AND WE CANNOT ANCHOR ABSOLUTE Q. physics.py refuses to supply wall_Q — "the
TE011 expression is easy to misquote" — and that refusal stands. But we do not
need it. For pure wall loss, Q depends on conductivity ONLY through the surface
resistance, so

        Q  ∝  sqrt(sigma)        EXACTLY, for every mode, with no geometry in it

That is a law, not an approximation, and it is testable without ever writing down
a Q formula. SAME MESH throughout, only the boundary conductivity changes, so
discretisation cancels exactly (METHODOLOGY 2b).

VERIFICATION   fit log Q against log sigma across four conductivities; the slope
               must be 0.5 for EVERY mode, not just TE011. And the Al:Ag pair
               must give physics.q_wall_ratio = 0.745356.
FALSIFICATION  a slope away from 0.5 by more than solver tolerance means Palace's
               impedance boundary condition does not scale as sqrt(sigma), and
               every Q this instrument produces is untrustworthy in a way no
               calibration constant can fix.

⚠️ Reports the FREQUENCY shift with conductivity too, as a measurement only. A
delta/2 wall-recession estimate came in 2-3x low with mode-dependent scatter
(E0), so it is NOT used as a check here — recorded, not trusted.

⚠️ PEC is not in the sweep: its Q is infinite and log(inf) is not a data point.
The PEC solve is the frequency reference, and E0 already has it.
"""
import json
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
from e0_solver_vs_math import A_MM, L_MM, build, eigen_cfg, run

TAG = "e0q"
# spans 10x, so a wrong exponent cannot hide in the noise of a narrow range
SIGMAS = [1.0e7, 2.0e7, 3.5e7, 6.3e7, 1.0e8]
AL, AG = 3.5e7, 6.3e7


def eig_q(tag):
    """[(f_ghz, Q)] from eig.csv — frequency AND quality factor."""
    f = pathlib.Path("postpro") / tag / "eig.csv"
    out = []
    for line in f.read_text().splitlines()[1:]:
        p = line.split(",")
        if len(p) > 3:
            out.append((float(p[1]), float(p[3])))
    return sorted(out)


def _checkpoint(path, payload):
    """Write results after EVERY case, not at the end.

    🔴 A spot reclamation on 2026-08-21 killed the instance mid-run. H1, H2 and
    H2b all wrote their result file only after the last case, so an interrupt
    lost every completed case with it — H2's table survived solely because it
    had been printed to a log and transcribed by hand. E0v already did this
    correctly ("written after EVERY case, so a death in case 2 cannot take case
    1 down with it"); the H rigs did not inherit it.

    Atomic: temp file then os.replace, so an interrupt DURING the write leaves
    the previous complete file rather than a truncated one.
    """
    import json as _j, os as _o, pathlib as _p
    p = _p.Path(path)
    t = p.with_suffix(p.suffix + f".tmp{_o.getpid()}")
    t.write_text(_j.dumps(payload, indent=1) + "\n")
    _o.replace(t, p)


def main():
    print(__doc__)
    print("=" * 78, flush=True)
    m, fac = build(TAG)
    print(f"  ONE mesh: {m['tets']:,} elements, sf {fac}\n", flush=True)
    EX = ph.spectrum(A_MM, L_MM)

    res = {}
    for s in SIGMAS:
        t = f"{TAG}_s{s:.0e}".replace("+", "").replace(".0e", "e")
        # 🔴 n=8 from a 1.05 GHz target reaches 2.363 GHz and STOPS SHORT of
        # TE011 at 2.444 — the first run validated the sqrt(sigma) law on eight
        # modes and missed the only one the machine runs on. n=14 covers it.
        c = eigen_cfg(t, m, mesh=f"{TAG}.msh", sigma=s, n=14, target=1.05)
        c["Solver"]["Order"] = 2
        print(f"  sigma {s:.2e} S/m", flush=True)
        run(t, c)
        res[s] = eig_q(t)
        print(f"    {len(res[s])} modes, TE011-ish Q = "
              f"{min(res[s], key=lambda x: abs(x[0]-EX['TE011']))[1]:,.0f}",
              flush=True)
        _checkpoint(f"{TAG}.partial.json",
                    {"sigmas_done": sorted(res), "complete": False,
                     "modes": {str(k): v for k, v in res.items()}})

    # every mode, not just TE011: the law applies to all of them
    n = min(len(v) for v in res.values())
    print(f"\n  Q vs sigma — slope of log Q against log sigma, must be 0.500\n")
    print(f"  {'mode':>5}{'f GHz':>10}" + "".join(f"{s:>12.1e}" for s in SIGMAS)
          + f"{'slope':>9}{'flag':>7}")
    rows, bad = [], []
    for i in range(n):
        qs = [res[s][i][1] for s in SIGMAS]
        f0 = res[SIGMAS[0]][i][0]
        xs = [math.log(s) for s in SIGMAS]
        ys = [math.log(q) for q in qs]
        mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
        slope = (sum((x-mx)*(y-my) for x, y in zip(xs, ys))
                 / sum((x-mx)**2 for x in xs))
        ok = abs(slope - 0.5) < 0.01
        if not ok:
            bad.append((i, slope))
        rows.append({"i": i, "f": f0, "Q": qs, "slope": slope})
        print(f"  {i:>5}{f0:>10.5f}" + "".join(f"{q:>12,.0f}" for q in qs)
              + f"{slope:>9.4f}{'' if ok else '  🔴':>7}")

    # the declared pair, against physics.py
    want = ph.q_wall_ratio(AL, AG)
    ia = SIGMAS.index(AL)
    ig = SIGMAS.index(AG)
    print(f"\n  Al:Ag ratio, predicted {want:.6f} (physics.q_wall_ratio):")
    for i in range(n):
        got = res[AL][i][1] / res[AG][i][1]
        print(f"    mode {i} ({res[AL][i][0]:.4f} GHz): {got:.6f}  "
              f"{'✅' if abs(got-want) < 1e-3 else '🔴'}")

    print(f"\n  frequency vs conductivity (MEASUREMENT, not a check):")
    for i in range(min(3, n)):
        fs = [res[s][i][0] for s in SIGMAS]
        print(f"    mode {i}: {1e6*(max(fs)-min(fs)):.1f} kHz across "
              f"{SIGMAS[0]:.0e}..{SIGMAS[-1]:.0e} S/m")

    json.dump({"sigmas": SIGMAS, "predicted_al_ag": want, "rows": rows,
               "tets": m["tets"]}, open(f"{TAG}.result.json", "w"), indent=1)
    print()
    if bad:
        print(f"  🔴 {len(bad)} mode(s) off the sqrt(sigma) law: "
              f"{[(i, round(s,4)) for i, s in bad]}")
    else:
        print(f"  ✅ every mode scales as sqrt(sigma) to within 0.01 in exponent")
    print(f"\n  wrote {TAG}.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
