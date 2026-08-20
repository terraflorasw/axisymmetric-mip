#!/usr/bin/env python3
"""Tier-2 regression: re-solve pinned meshes through the NEW stack.

Tier 1 (regress.py) replays stored postpro CSVs in seconds and covers the
analysis layer. It cannot see the solve path — env, config assembly, port
direction, attribute binding — which is where the other half of the night's
failures lived.

This closes that gap by re-solving a pinned case through
geometry.py -> sidecar -> solveconf -> solver and checking it reproduces a
number the OLD hand-assembled path produced. If the stacks agree, the migration
is sound; if they diverge, the refactor changed physics and that is exactly what
a regression net exists to catch.

CASE CHOSEN: R60's loop-tilt pair. Two solves (~30 min), and it exercises the
single thing that broke R47 — the port Direction, which differs between the two
cases (0 deg vs 45 deg) and is now DERIVED from each mesh's sidecar rather than
copied. A migration bug there shows up immediately as a Palace abort or a wrong
suppression figure.

Recorded by the old path: TM020 is 18.3 dB down at the operational 0 deg tilt.
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import modes
import solver

BAND = (2.34, 2.50)
CASES = [("t45.msh", "rt2_t45"), ("t00.msh", "rt2_t00")]

print(__doc__)
print("=" * 78, flush=True)

for mesh, _tag in CASES:
    if not pathlib.Path(mesh).exists():
        sys.exit(f"{mesh} missing — run rebuild_pinned.py first")

res = solver.sweep(CASES, BAND)

print()
ratios = {}
for mesh, tag in CASES:
    ms = res[tag]
    te, tm = modes.te011(ms), modes.tm020(ms)
    if not (te and tm):
        sys.exit(f"🔴 {tag}: TE011 or TM020 not found — cannot compare")
    ratios[tag] = tm["rel"] / te["rel"]
    print(f"  {tag}: TE011 {te['f']:.5f} Q={te['Q0']:>9,.0f} | "
          f"TM020 {tm['f']:.5f} at {100*ratios[tag]:.2f}% of TE011", flush=True)

supp = -10 * math.log10(ratios["rt2_t00"] / ratios["rt2_t45"])
print("\n" + "=" * 78)
print(f"TM020 suppression at 0 deg: {supp:.2f} dB   (old path recorded 18.3)")
ok = abs(supp - 18.3) <= 0.5
print("✅ NEW STACK REPRODUCES THE OLD RESULT — migration is sound" if ok else
      "🔴 DIVERGED — the refactor changed the answer, not just the plumbing")
sys.exit(0 if ok else 1)
