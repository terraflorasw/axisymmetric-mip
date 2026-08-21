"""E0i — do the rigid-motion violations survive at solver order 2?

E0g changed what is worth measuring. At solver order 2 the instrument reproduces
the exact spectrum to 0.361 MHz and holds an exact degeneracy to 0.014 MHz. So
the 8-member ensemble drafted for a 12 MHz error is no longer worth 7 hours of
machine time — 0.36 MHz is already far below the 2.34 MHz cold linewidth and the
23 MHz tuning range. ⚠️ SCOPE DELIBERATELY REDUCED, and recorded as such rather
than quietly dropped.

WHAT STILL MATTERS is closing the thread the user opened: rigid motions moved
frequencies by ~4 MHz and split an exact degeneracy 6x. All of that was measured
at SOLVER ORDER 1. If it collapses at order 2, the tooling was never suspect —
it was being under-resolved, and the correct reading of E0b/E0c is "order 1 is
inadequate", not "gmsh is unreliable".

    at0     reference
    off     +256 mm on x, y, z   — exact symmetry, E0b measured 4.074 MHz here
    rot120  120 deg about the cavity axis — solid literally unchanged

PREDICTION, DECLARED BEFORE THE RUN: every shift below 0.1 MHz, and the
degenerate splitting below 0.05 MHz in all three.

🔴 FALSIFIER: if the shifts stay near 4 MHz while the absolute accuracy is
0.36 MHz, then realisation error is NOT discretisation error — it would be a
separate, order-independent defect, and the ensemble becomes mandatory after all.

⚠️ FOCUSED EIGENSOLVE. Target 2.40 GHz with N=6 instead of 1.05 with N=22: the
falsifier only needs the degenerate pair and its neighbours, and 22 modes is what
made order 2 cost 3007 s. This changes the eigensolver's work, so these absolute
values are NOT directly comparable with E0g's — the SHIFTS between the three
cases are, because all three use identical settings.
"""
import hashlib
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eigmodes
import physics as ph
from e0_solver_vs_math import A_MM, L_MM, build, eigen_cfg, run, eig

CASES = [("e0i_at0", []),
         ("e0i_off", ["--offset", "256,256,256"]),
         ("e0i_rot120", ["--rotate", "120"])]

def main():
    print(__doc__)
    print("=" * 78, flush=True)
    EX = ph.spectrum(A_MM, L_MM)
    DEG = [("TE011", "TM111")]

    info = {}
    for tag, extra in CASES:
        m, fac = build(tag, extra)
        h = hashlib.md5(pathlib.Path(f"{tag}.msh").read_bytes()).hexdigest()[:12]
        info[tag] = (m, h)
        print(f"    md5 {h}  {m['tets']:,} tets", flush=True)
    if len({h for _m, h in info.values()}) != len(CASES):
        sys.exit("🔴 identical meshes — NOT solving.")
    print("  ✅ three distinct realisations of one physical problem\n", flush=True)

    res = {}
    for tag, _e in CASES:
        cfg = eigen_cfg(tag, info[tag][0], n=6, target=2.40)
        cfg["Solver"]["Order"] = 2
        run(tag, cfg)
        res[tag] = eig(tag)

    base = "e0i_at0"
    print(f"\n{'mode':>7}{'exact':>11}" + "".join(f"{t.replace('e0i_',''):>12}"
                                                  for t, _e in CASES)
          + f"{'max shift':>11}")
    for k, fx in sorted(EX.items(), key=lambda kv: kv[1]):
        vals = {}
        for t, _e in CASES:
            p, _r = ph.match_exact(EX, res[t], DEG)
            if k in p:
                vals[t] = p[k]
        if len(vals) < len(CASES):
            continue
        row = "".join(f"{1e3*(vals[t]-fx):>12.3f}" for t, _e in CASES)
        sh = 1e3 * (max(vals.values()) - min(vals.values()))
        print(f"{k:>7}{fx:>11.5f}{row}{sh:>11.3f}")

    print(f"\n  🔑 FALSIFIER — degenerate splitting, true value EXACTLY 0:")
    for t, _e in CASES:
        # 🔴 was sorted(...)[:2] — the two NEAREST, which are BOTH TM111
        # polarisations (m=1 is doubly degenerate). That reported TM111's
        # internal splitting, not TE011<->TM111. See eigmodes.te011_tm111.
        _d = eigmodes.te011_tm111(res[t], EX["TE011"])
        n = [_d['tm111'], _d['te011']] if _d else sorted(res[t], key=lambda x: abs(x - EX["TE011"]))[:2]
        print(f"    {t.replace('e0i_',''):>8}  {1e3*abs(n[1]-n[0]):8.4f} MHz")
    print(f"\n  at SOLVER ORDER 1 the same comparison gave: shifts up to 4.074 MHz, "
          f"splitting 1.199 / 7.052 / 1.268 MHz")

    json.dump({"exact": EX, **res, "md5": {t: info[t][1] for t, _e in CASES},
               "solver_order": 2, "eigen_target": 2.40, "eigen_n": 6},
              open("e0i.result.json", "w"), indent=1)
    print("\n  wrote e0i.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
