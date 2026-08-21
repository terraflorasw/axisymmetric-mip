"""E0h — separate BIAS from SCATTER. An ensemble over mesh realisations.

E0e established that mesh-realisation error is irreducible by care: the solver is
exact, gmsh is not translation-equivariant, and a single mesh is one draw from a
distribution nobody has sampled. It said the fix is refinement or ensembles.
This is the ensemble.

🔑 ROTATION ABOUT THE CAVITY AXIS IS THE PERFECT REALISATION GENERATOR. The
cavity is axisymmetric and empty, so a z-rotation leaves the OCC solid LITERALLY
UNCHANGED — same volume, same surface, same bounding box — while gmsh lays out a
completely different mesh. Every member of the ensemble is the SAME PHYSICAL
PROBLEM. No jitter, no approximation, no "small enough to ignore" argument.

THE QUESTION THIS ANSWERS, which no run so far has: how much of the ~12 MHz
disagreement is BIAS and how much is SCATTER?

    if the ENSEMBLE MEAN converges on the exact value   -> pure scatter, and
                                                           averaging fixes it
    if the ENSEMBLE MEAN stays low by ~12 MHz           -> SYSTEMATIC BIAS, and
                                                           ensembling removes
                                                           only the error bar,
                                                           never the offset

🔴 That distinction decides how this instrument may be used at all. A bias can be
corrected once and applied; scatter cannot be corrected, only averaged down. The
old programme's `offset.te011` assumed pure bias and never tested it.

VERIFICATION   physics.spectrum(). Compared against the ensemble MEAN, not
               against any single member.
FALSIFICATION  the exactly-degenerate splitting, true value 0, as a DISTRIBUTION.
               🔴 If its mean is far from zero it is a bias, not noise, and no
               ensemble will remove it — that would make it a hard resolution
               limit of tetrahedral meshing on an axisymmetric cavity.
GATE           all members pairwise distinct meshes, asserted before solving.
"""
import hashlib
import itertools
import json
import pathlib
import statistics
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eigmodes
import physics as ph
from e0_solver_vs_math import A_MM, L_MM, build, eigen_cfg, run, eig

ANGLES = [0, 15, 30, 45, 60, 75, 90, 105]
SOLVER_ORDER = int(sys.argv[1]) if len(sys.argv) > 1 else 2
CASES = [(f"e0h_r{a}", (["--rotate", str(a)] if a else [])) for a in ANGLES]

def main():
    print(__doc__)
    print("=" * 78, flush=True)
    print(f"  ensemble of {len(ANGLES)} rotations, SOLVER ORDER {SOLVER_ORDER}\n",
          flush=True)
    EX = ph.spectrum(A_MM, L_MM)
    DEG = [("TE011", "TM111")]

    info = {}
    for tag, extra in CASES:
        m, fac = build(tag, extra)
        h = hashlib.md5(pathlib.Path(f"{tag}.msh").read_bytes()).hexdigest()[:12]
        info[tag] = (m, h)
        print(f"    md5 {h}  {m['tets']:,} tets", flush=True)

    hs = {t: h for t, (_m, h) in info.items()}
    dup = [(a, b) for a, b in itertools.combinations(hs, 2) if hs[a] == hs[b]]
    if dup:
        sys.exit(f"🔴 IDENTICAL MESHES {dup} — the ensemble has repeated members "
                 "and its spread would be understated. NOT solving.")
    print(f"  ✅ {len(CASES)} distinct realisations of an IDENTICAL solid\n",
          flush=True)

    res = {}
    for tag, _e in CASES:
        cfg = eigen_cfg(tag, info[tag][0])
        cfg["Solver"]["Order"] = SOLVER_ORDER
        run(tag, cfg)
        res[tag] = eig(tag)

    print(f"\n{'mode':>7}{'exact':>11}{'mean':>12}{'BIAS MHz':>11}"
          f"{'SCATTER sd':>12}{'n':>4}")
    summary = {}
    for k, fx in sorted(EX.items(), key=lambda kv: kv[1]):
        vals = []
        for tag, _e in CASES:
            p, _r = ph.match_exact(EX, res[tag], DEG)
            if k in p:
                vals.append(p[k])
        if len(vals) < 3:
            print(f"{k:>7}{fx:>11.5f}{'— fewer than 3 members matched':>39}")
            continue
        mean = statistics.fmean(vals)
        sd = statistics.stdev(vals)
        summary[k] = dict(exact=fx, mean=mean, bias_mhz=1e3*(mean-fx),
                          scatter_mhz=1e3*sd, n=len(vals))
        print(f"{k:>7}{fx:>11.5f}{mean:>12.6f}{1e3*(mean-fx):>11.3f}"
              f"{1e3*sd:>12.3f}{len(vals):>4}")

    sp = []
    for tag, _e in CASES:
        # 🔴 was sorted(...)[:2] — the two NEAREST, which are BOTH TM111
        # polarisations (m=1 is doubly degenerate). That reported TM111's
        # internal splitting, not TE011<->TM111. See eigmodes.te011_tm111.
        _d = eigmodes.te011_tm111(res[tag], EX["TE011"])
        n = [_d['tm111'], _d['te011']] if _d else sorted(res[tag], key=lambda x: abs(x - EX["TE011"]))[:2]
        sp.append(1e3 * abs(n[1] - n[0]))
    print(f"\n  🔑 FALSIFIER — degenerate splitting across the ensemble "
          f"(true value 0):")
    print(f"     mean {statistics.fmean(sp):.3f} MHz   sd {statistics.stdev(sp):.3f}"
          f"   range {min(sp):.3f}–{max(sp):.3f}")
    print(f"     {'🔴 BIAS: averaging will not remove it' if statistics.fmean(sp) > 2*statistics.stdev(sp) else '⚠️ scatter-dominated'}")

    json.dump({"exact": EX, "solver_order": SOLVER_ORDER, "angles": ANGLES,
               "per_mode": summary, "splitting_mhz": sp, "md5": hs,
               **res}, open(f"e0h_s{SOLVER_ORDER}.result.json", "w"), indent=1)
    print(f"\n  wrote e0h_s{SOLVER_ORDER}.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
