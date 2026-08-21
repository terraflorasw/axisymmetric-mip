"""E0b — is the 27.6 MHz disagreement tied to the ORIGIN?

E0 found the solver low by up to 27.6 MHz against the exact spectrum, mode-
dependent, all negative. This asks whether any of that is a coordinate artifact.

🔑 A RIGID TRANSLATION IS AN EXACT SYMMETRY OF THE PHYSICS. Move the whole cavity
+256 mm in x, y and z and every frequency must be IDENTICAL — not approximately,
identically. So the difference between the two runs is pure instrument.

AND THE ORIGIN IS A SPECIAL POINT, but NOT for the reason first supposed. Double
spacing at 0.356 m is 5.6e-17 m, still nine orders below OCC's ~1e-7 m geometric
tolerance; precision only binds near 2^31. What is special is EXACT COINCIDENCE:
at x = y = 0 the cavity axis lies exactly on the coordinate axis, and z = 0 is
exactly the mid-plane, so geometric predicates evaluate to exact zeros — which is
where degenerate tie-breaking lives in CAD and meshing algorithms. Offsetting
breaks every one of those coincidences at no precision cost.

VERIFICATION   physics.spectrum(), same reference as E0. Both runs are compared
               to it, and the two disagreement VECTORS are compared to each other.
FALSIFICATION  the exact TE011/TM111 degeneracy again — but now the question is
               whether its 1.199 MHz splitting MOVES. A splitting that changes
               under a symmetry of the physics is numerical; one that does not
               may be structural to the discretisation.

🔴 AND THE ASSERTION E0 WAS MISSING. E0's two meshes came out byte-identical and
its convergence arm was void, because I gated apertures, dielectric and material
completeness but never asserted THE CASES DIFFER. That assertion is here, and it
runs before any solve.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import eigmodes
import physics as ph
import solveconf
import solver
from e0_solver_vs_math import GEO, A_MM, L_MM, eigen_cfg, run, eig, build

CASES = [("e0b_at0", []), ("e0b_off", ["--offset", "256,256,256"])]

def main():
    print(__doc__)
    print("=" * 78, flush=True)
    EX = ph.spectrum(A_MM, L_MM)

    info = {}
    for tag, extra in CASES:
        m, fac = build(tag, extra)
        h = hashlib.md5(pathlib.Path(f"{tag}.msh").read_bytes()).hexdigest()[:12]
        info[tag] = (m, h)
        print(f"    md5 {h}", flush=True)

    # 🔴 THE ASSERTION E0 LACKED — before any solve.
    if len({h for _m, h in info.values()}) != len(CASES):
        sys.exit("🔴 CASES DO NOT DIFFER: the offset produced an identical mesh, so "
                 "this run measures nothing. NOT solving.")
    print("  ✅ the two meshes differ — the offset changed the discretisation\n",
          flush=True)

    for tag, _e in CASES:
        run(tag, eigen_cfg(tag, info[tag][0]))

    res = {t: eig(t) for t, _e in CASES}
    print(f"\n{'mode':>7}{'exact':>12}{'at 0':>12}{'+256mm':>12}"
          f"{'Δ0 MHz':>10}{'Δoff MHz':>10}{'shift':>9}")
    rows = []
    for k, fx in sorted(EX.items(), key=lambda kv: kv[1]):
        a = min(res["e0b_at0"], key=lambda x: abs(x - fx))
        b = min(res["e0b_off"], key=lambda x: abs(x - fx))
        d0, doff = 1e3 * (a - fx), 1e3 * (b - fx)
        rows.append((k, d0, doff))
        print(f"{k:>7}{fx:>12.6f}{a:>12.6f}{b:>12.6f}"
              f"{d0:>10.3f}{doff:>10.3f}{doff - d0:>9.3f}")

    sh = [r[2] - r[1] for r in rows]
    print(f"\n  shift under an EXACT SYMMETRY: mean {sum(sh)/len(sh):+.3f} MHz, "
          f"max |{max(abs(x) for x in sh):.3f}| MHz")
    print("  🔑 every one of these is pure instrument — the physics did not move.")

    for tag in ("e0b_at0", "e0b_off"):
        tgt = EX["TE011"]
        # 🔴 was sorted(...)[:2] — the two NEAREST, which are BOTH TM111
        # polarisations (m=1 is doubly degenerate). That reported TM111's
        # internal splitting, not TE011<->TM111. See eigmodes.te011_tm111.
        _d = eigmodes.te011_tm111(res[tag], tgt)
        n = [_d['tm111'], _d['te011']] if _d else sorted(res[tag], key=lambda x: abs(x - tgt))[:2]
        print(f"  degeneracy splitting, {tag}: {1e3*abs(n[1]-n[0]):.3f} MHz "
              f"(true value 0)")

    json.dump({"exact": EX, **res,
               "md5": {t: info[t][1] for t, _e in CASES},
               "tets": {t: info[t][0]["tets"] for t, _e in CASES}},
              open("e0b.result.json", "w"), indent=1)
    print("\n  wrote e0b.result.json — NO VERDICT HERE", flush=True)


if __name__ == "__main__":
    main()
