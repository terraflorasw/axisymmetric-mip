"""E0d — rotate about a TRANSVERSE axis. The strongest rigid-motion probe.

The user's point: the cavity axis is z, so E0c's z-rotations leave the
axisymmetric solid literally unchanged — only the mesh moves. Rotating about x
or y TILTS the cavity axis away from the coordinate axis entirely, which is a
much stronger disruption, and E0b says exactly why it should matter.

🔑 A LADDER OF SYMMETRY DISRUPTION, weakest to strongest:

  1. rotate about z      solid invariant; cavity axis still ON the coordinate
                         z axis. Only the mesh changes.                  (E0c)
  2. translate           axis stays PARALLEL to z but leaves it.         (E0b)
  3. rotate 90 about x   cavity axis maps z -> y: still on A coordinate axis,
                         just a different one. 🔑 THIS SEPARATES "aligned with
                         z specifically" from "aligned with any axis".
  4. rotate 37 about x   axis points nowhere special. Full disruption.

PREDICTION, DECLARED BEFORE THE RUN — the degeneracy splitting should order

        (1) <= (3) < (2) < (4)

if what the mesh needs is ALIGNMENT WITH SOME COORDINATE AXIS. If instead it
orders (1) < (3) ~ (4), then only the ORIGINAL z alignment matters and 90 deg
buys nothing. 🔴 If (4) is no worse than (2), the whole "mesh inherits the
cavity's symmetry" reading from E0b is wrong and should be withdrawn.

VERIFICATION   physics.spectrum() — invariant under every rigid motion.
FALSIFICATION  TE011/TM111 splitting, true value EXACTLY zero, in every cell.
GATE           all meshes pairwise distinct, asserted before solving.
"""
import hashlib
import itertools
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import physics as ph
from e0_solver_vs_math import A_MM, L_MM, build, eigen_cfg, run, eig

CASES = [
    ("e0d_base",  []),                                              # 1
    ("e0d_x90",   ["--rotate-axis", "x", "--rotate", "90"]),        # 3
    ("e0d_y90",   ["--rotate-axis", "y", "--rotate", "90"]),        # 3
    ("e0d_x37",   ["--rotate-axis", "x", "--rotate", "37"]),        # 4
    ("e0d_y37",   ["--rotate-axis", "y", "--rotate", "37"]),        # 4
]

print(__doc__)
print("=" * 78, flush=True)
EX = ph.spectrum(A_MM, L_MM)

info = {}
for tag, extra in CASES:
    m, fac = build(tag, extra)
    h = hashlib.md5(pathlib.Path(f"{tag}.msh").read_bytes()).hexdigest()[:12]
    info[tag] = (m, h)
    print(f"    md5 {h}  rot {m['geometry_mm'].get('rotate_deg', 0):.0f} deg "
          f"about {m['geometry_mm'].get('rotate_axis')}", flush=True)

hs = {t: h for t, (_m, h) in info.items()}
dup = [(a, b) for a, b in itertools.combinations(hs, 2) if hs[a] == hs[b]]
if dup:
    sys.exit(f"🔴 IDENTICAL MESHES {dup}. NOT solving.")
print(f"  ✅ all {len(CASES)} meshes pairwise distinct\n", flush=True)

for tag, _e in CASES:
    run(tag, eigen_cfg(tag, info[tag][0]))
res = {t: eig(t) for t, _e in CASES}

print(f"\nΔ from EXACT, MHz — every cell should read 0.000\n")
print(f"{'mode':>7}{'exact':>11}" + "".join(f"{t.replace('e0d_',''):>10}"
                                            for t, _e in CASES))
for k, fx in sorted(EX.items(), key=lambda kv: kv[1]):
    ds = [1e3 * (min(res[t], key=lambda x: abs(x - fx)) - fx)
          for t, _e in CASES]
    print(f"{k:>7}{fx:>11.5f}" + "".join(f"{d:>10.3f}" for d in ds))

print(f"\n  🔑 FALSIFIER — TE011/TM111 splitting, true value EXACTLY 0:")
split = {}
for t, _e in CASES:
    n = sorted(res[t], key=lambda x: abs(x - EX["TE011"]))[:2]
    split[t] = 1e3 * abs(n[1] - n[0])
    print(f"    {t.replace('e0d_',''):>8}  {split[t]:7.3f} MHz   "
          f"({info[t][0]['tets']:,} tets)")
print(f"\n  for reference: E0b measured 1.199 MHz on-axis and 7.052 MHz "
      f"translated +256 mm")

json.dump({"exact": EX, **res, "md5": hs, "splitting_mhz": split,
           "tets": {t: info[t][0]["tets"] for t, _e in CASES}},
          open("e0d.result.json", "w"), indent=1)
print("\n  wrote e0d.result.json — NO VERDICT HERE", flush=True)
