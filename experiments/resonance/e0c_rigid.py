"""E0c — the full rigid-motion factorial. Translation x rotation, 2 x 3.

Both operations are EXACT symmetries of Maxwell, so every frequency must be
identical across all six cases. Every difference is instrument, with no
modelling judgement involved anywhere.

    translation   0  and  +256 mm on each of x, y, z
    rotation      0, 120, 180 deg about the cavity axis

🔑 ROTATION IS THE PURER PROBE. The cavity is axisymmetric and empty, so a
rotation about z changes neither the physics NOR the OCC solid — not even the
bounding box. Only the parametric seam moves, and gmsh then lays out a different
mesh. Translation at least moves coordinates; rotation moves nothing a formula
could see.

🔑 AND THE FACTORIAL ASKS WHETHER THEY INTERACT. E0b found the two effects have
opposite characters: TE011's error was translation-STABLE (0.148 MHz) while the
exact degeneracy split 6x WORSE off-origin (1.199 -> 7.052 MHz). If rotation at
the origin also preserves the degeneracy, the origin's virtue is that it lets the
discretisation inherit the cavity's azimuthal symmetry — and 120 vs 180 deg
distinguishes a 3-fold from a 2-fold artifact.

VERIFICATION   physics.spectrum() — the same exact reference for all six.
FALSIFICATION  the TE011/TM111 splitting, true value EXACTLY zero, measured in
               every cell. Its VARIATION across the factorial is the artifact.
GATE           all six meshes must be pairwise distinct, asserted before solving.
"""
import hashlib
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
from e0_solver_vs_math import A_MM, L_MM, build, eigen_cfg, run, eig

OFFS = [("at0", []), ("off", ["--offset", "256,256,256"])]
ROTS = [0, 120, 180]
CASES = [(f"e0c_{o}_{r}", ex + (["--rotate", str(r)] if r else []))
         for (o, ex), r in itertools.product(OFFS, ROTS)]

print(__doc__)
print("=" * 78, flush=True)
EX = ph.spectrum(A_MM, L_MM)

info = {}
for tag, extra in CASES:
    m, fac = build(tag, extra)
    h = hashlib.md5(pathlib.Path(f"{tag}.msh").read_bytes()).hexdigest()[:12]
    info[tag] = (m, h)
    print(f"    md5 {h}", flush=True)

hs = {t: h for t, (_m, h) in info.items()}
dup = [(a, b) for a, b in itertools.combinations(hs, 2) if hs[a] == hs[b]]
if dup:
    sys.exit(f"🔴 IDENTICAL MESHES {dup} — those cells measure nothing. "
             "NOT solving.")
print(f"  ✅ all {len(CASES)} meshes pairwise distinct\n", flush=True)

for tag, _e in CASES:
    run(tag, eigen_cfg(tag, info[tag][0]))
res = {t: eig(t) for t, _e in CASES}


def near(tag, f):
    return min(res[tag], key=lambda x: abs(x - f))


print(f"\nΔ from EXACT, MHz — every cell should read 0.000\n")
hdr = "".join(f"{t.replace('e0c_',''):>12}" for t, _e in CASES)
print(f"{'mode':>7}{'exact':>11}{hdr}")
spread = {}
for k, fx in sorted(EX.items(), key=lambda kv: kv[1]):
    ds = [1e3 * (near(t, fx) - fx) for t, _e in CASES]
    spread[k] = max(ds) - min(ds)
    print(f"{k:>7}{fx:>11.5f}" + "".join(f"{d:>12.3f}" for d in ds))
print(f"\n{'':>18}" + "".join(f"{info[t][0]['tets']:>12,}" for t, _e in CASES)
      + "   tets")

print(f"\n  SPREAD across six rigid motions (pure instrument):")
for k, s in sorted(spread.items(), key=lambda kv: -kv[1]):
    print(f"    {k:>7}  {s:7.3f} MHz")

print(f"\n  🔑 FALSIFIER — TE011/TM111 splitting, true value EXACTLY 0:")
for t, _e in CASES:
    n = sorted(res[t], key=lambda x: abs(x - EX["TE011"]))[:2]
    print(f"    {t.replace('e0c_',''):>10}  {1e3*abs(n[1]-n[0]):7.3f} MHz")

json.dump({"exact": EX, **res, "md5": hs,
           "tets": {t: info[t][0]["tets"] for t, _e in CASES}},
          open("e0c.result.json", "w"), indent=1)
print("\n  wrote e0c.result.json — NO VERDICT HERE", flush=True)
