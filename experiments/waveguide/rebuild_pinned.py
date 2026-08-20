#!/usr/bin/env python3
"""Rebuild the meshes the regression corpus pins, so each gets a sidecar.

R50. `solveconf` refuses a mesh without `<mesh>.meta.json` — correctly, since a
config assembled without it is guessing at the port direction and the attribute
list. Every existing mesh predates the sidecar, so the pinned set needs one
rebuild each.

⚠️ ONLY THE PINNED SET. There are 154 .msh files here totalling ~2.9 GB, nearly
all of them historical one-offs from closed questions. Rebuilding those would
cost hours and buy nothing: they are never re-solved, and their RESULTS live in
postpro/, which tier-1 regression reads directly.

Meshing is deterministic, so identical arguments at an identical size-factor
reproduce the identical mesh — verified tonight when c020/ov020 and q_filter/s5_mf
returned bit-identical frequencies from separate sweeps. These rebuilds should
therefore change nothing but the presence of the sidecar; `verify` checks that by
comparing element counts against what the corpus recorded.
"""
import pathlib
import subprocess
import sys

MM = pathlib.Path.home() / ".local/bin/micromamba"
COMMON = ["--radius", "103.70", "--length", "88.53", "--order", "2",
          "--loop", "12,8.5,1,0.3"]

# tag: (size-factor, extra args, expected tets from the run that produced it)
PINNED = {
    "choff":   ("0.96", ["--brake", "3", "--sectors", "1", "--loop-tilt", "45"], 103293),
    "c2141":   ("0.96", ["--brake", "3", "--sectors", "1", "--loop-tilt", "45",
                         "--chimney", "21,41"], None),
    "s5_mf":   ("0.96", ["--brake", "3", "--sectors", "5", "--loop-phi", "36",
                         "--loop-tilt", "45"], 114698),
    "s5_nomf": ("0.96", ["--brake", "0", "--sectors", "5", "--loop-phi", "36",
                         "--loop-tilt", "45"], None),
    "z0_mf":   ("0.96", ["--brake", "3", "--sectors", "5", "--loop-phi", "36"], None),
    "z0_nomf": ("0.96", ["--brake", "0", "--sectors", "5", "--loop-phi", "36"], None),
    "t45":     ("0.96", ["--brake", "3", "--sectors", "1", "--loop-tilt", "45"], None),
    "t00":     ("0.96", ["--brake", "3", "--sectors", "1"], None),
    "p_06":    ("0.93", ["--brake", "3", "--sectors", "1", "--loop-tilt", "45",
                         "--plasma", "4.5,8.5,-20.0,10.0", "--plasma-h", "0.6"], None),
}


def build(tag, fac, extra):
    out = f"{tag}.msh"
    g = subprocess.run([str(MM), "run", "-n", "emsim", "python", "geometry.py",
                        "--out", out, "--size-factor", fac] + COMMON + extra,
                       capture_output=True, text=True)
    if g.returncode != 0:
        for line in (g.stderr or g.stdout or "").strip().splitlines()[-3:]:
            print(f"      {line}", flush=True)
        return None
    tets = None
    for line in g.stdout.splitlines():
        if line.strip().startswith("mesh:"):
            tets = int(line.split()[1])
    return tets


print(__doc__)
print("=" * 78, flush=True)
bad = []
for tag, (fac, extra, want) in PINNED.items():
    tets = build(tag, fac, extra)
    side = pathlib.Path(f"{tag}.meta.json")
    if tets is None:
        print(f"  🔴 {tag}: MESH FAILED", flush=True)
        bad.append(tag)
        continue
    if not side.exists():
        print(f"  🔴 {tag}: built but NO SIDECAR — geometry.py is stale", flush=True)
        bad.append(tag)
        continue
    note = ""
    if want is not None:
        drift = abs(tets - want) / want
        note = (f"  ✅ matches recorded {want:,}" if drift < 1e-9
                else f"  🔴 recorded {want:,}, drift {100*drift:.2f}%")
        if drift >= 1e-9:
            bad.append(tag)
    print(f"  {tag:<9} {tets:>9,} tets, sidecar ok{note}", flush=True)

print("\n" + "=" * 78)
print(f"🔴 {len(bad)} problem(s): {', '.join(bad)}" if bad
      else f"✅ all {len(PINNED)} pinned meshes rebuilt with sidecars")
sys.exit(1 if bad else 0)
