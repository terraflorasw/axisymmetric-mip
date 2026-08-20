"""R109 — the TRANSLATION probe. The microscope's other test.

The user's framing: the mesh and solver are a flawed lens. Rotate the slide about
the optical centre and real features rotate with it while optical artifacts stay
put. But that is blind to an artifact sitting ON the rotation axis — for those you
must TRANSLATE the slide.

🔑 WE ALREADY DID THE ROTATION, AND IT FAILED. R89 rotated the loop 36 deg ->
108 deg, a rigid rotation about the symmetry axis under which the physics is
EXACTLY invariant. It moved f by 1.55 MHz, Q0 by 2.5% and eta by 5.0 points. Those
are pure artifact, and they are why "TE011 wins in band" was retracted from three
places and why R57/R58 were closed analytically.

🔴 AND OUR PHYSICS LIVES ON THE AXIS. The torch, the injector (ID 2 mm, the finest
feature in the model), the plasma, and TM020's E_z maximum are all on or near
r = 0. R99's headline result is on-axis dielectric loading. ROTATION CANNOT
VALIDATE THE REGION THAT PRODUCED OUR BIGGEST CLAIM.

A rigid translation PERPENDICULAR to the symmetry axis is the missing probe: every
OCC seam and every fine near-axis feature lands somewhere new relative to the
mesher, while the physics is exactly unchanged. ⚠️ A z-translation would NOT do
it — it keeps everything on the same axis line and is blind in the same direction
rotation is. So all four cases below shift in x and/or y.

🔑 WHY THIS BEATS R105'S JITTER. R105 perturbed a length by 7.5 um: a true change
of 0.18 MHz and only a marginal mesh change. A rigid translation has a true change
of EXACTLY ZERO and a total mesh change. Zero signal, maximum noise — which is
what a noise probe should be, and it was available all along.

    r109a   ( 0, 0, 0)              reference
    r109b   (+7, 0, 0)               \
    r109c   ( 0,+5, 0)                > SMALL: their spread is the artifact floor
    r109d   (+3,-4, 0)               /
    r109e   (+256,+256,+256)         MAGNITUDE: the user's proposal
    r109f   (+10 m, 0, 0)            MAGNITUDE: two decades further
    r109g   (+100 km, 0, 0)          MAGNITUDE: five decades further

🔑 THE ORIGIN IS SPECIAL BY COINCIDENCE, NOT BY PRECISION. At x = y = 0 the cavity
axis lies exactly on the coordinate axis, so geometric predicates hit exact zeros
— and exact zeros are where degenerate tie-breaking lives in CAD and meshing
algorithms. Offsetting breaks that at NO precision cost.

════════════════════════════════════════════════════════════════════════════════
CRITERIA, DECLARED BEFORE THE RUN
════════════════════════════════════════════════════════════════════════════════

1. PRIMARY — the spread of f(TE011), Q0(TE011) and eta across the four cases IS
   the artifact floor for those observables. TRUE VALUE IS IDENTICAL, so there is
   no signal to separate: everything observed is noise. Report sd (ddof=1) and
   peak-to-peak.

2. SECOND ROUTE FOR Q AND ETA. Frequency already has three routes agreeing at
   1.3-1.6 MHz (R89 rotation, R105 jitter, reproducibility.mesh_to_mesh_scatter).
   🔴 Q0 (2.5%) and eta (5.0 points) rest on R89 ALONE. This gives them a second,
   independent one — and the first that can see on-axis artifacts.

3. AGREEMENT GATE — if the translation floor for f lands near 1.3-1.6 MHz, the
   frequency floor is confirmed by a fourth route and is not direction-dependent.
   🔴 If it is MUCH LARGER, then the axis IS a blind spot, R89 understated the
   floor, and every Q/eta comparison in the record needs re-reading against the
   larger number.

4. MAGNITUDE — r109e/f/g must agree with the SMALL group to within its own
   spread. 🔴 If they do not, coordinate magnitude matters and every model should
   be built near the origin; if they do, the question is closed for good and the
   offset is free to use as a probe.

5. IDENTITY — TE011 = lowest bore-E among bore-H dominant modes. If bore-E moves
   materially between cases, the mode is not being tracked and the spread is
   mis-attributed (R107: character, not frequency, is the indicator).

⚠️ NOT A CONVERGENCE STUDY. Every case is at the same size factor; this measures
   realisation scatter, not discretisation bias.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshsweep
import results
import solveconf
import solver

BASE = ["--radius", "103.70", "--length", "88.53", "--order", "2",
        "--sectors", "1", "--loop", "25.8,19.4,1.5,0.3", "--loop-phi", "36",
        "--plasma", "4.5,8.5,-20,10", "--plasma-h", "1.0", "--mode-filter", "3"]
# Two groups, two questions.
#
# SMALL — four awkward offsets a few mm apart. Their spread IS the artifact floor
# for f, Q0 and eta, because the true value is identical across all of them.
# Deliberately not round numbers and not powers of two: the point is to BREAK the
# exact coincidences that exist at x = y = 0, where the cavity axis lies exactly
# on the coordinate axis and geometric predicates evaluate to exact zeros.
#
# MAGNITUDE — 256 mm, 10 m, 100 km. 🔴 I previously argued far offsets would
# degrade precision; that was WRONG BY NINE ORDERS OF MAGNITUDE. A +256 mm offset
# moves the double spacing from 1.4e-17 to 5.6e-17 m, still 9 orders below OCC's
# ~1e-7 m tolerance, and parity only arrives near 2^31 m. So rather than argue
# the threshold, MEASURE it: if the answer is stable to 100 km, coordinate
# magnitude is a non-issue for anything we will ever build, and if it breaks
# earlier the cause is OCC tolerance handling or gmsh scaling, not the mantissa.
CASES = [("r109a", []),
         ("r109b", ["--offset", "7,0,0"]),
         ("r109c", ["--offset", "0,5,0"]),
         ("r109d", ["--offset", "3,-4,0"]),
         ("r109e", ["--offset", "256,256,256"]),
         ("r109f", ["--offset", "10000,0,0"]),
         ("r109g", ["--offset", "100000000,0,0"])]
BAND, STEP = (2.30, 2.46), 5e-5     # same window as R107, so it is comparable
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def run(tag):
    m = solveconf.load_meta(f"{tag}.msh")
    pl = m["attributes"].get("plasma")
    c, m, _ = solveconf.driven(f"{tag}.msh", tag, BAND, step=STEP, order=1,
                               materials={pl: {"Permittivity": 1.0,
                                               "Permeability": 1.0}})
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    g = m["geometry_mm"]
    print(f"  {tag}: offset {g.get('offset')} mm, {m['tets']:,} tets", flush=True)
    t0 = time.time()
    rc = subprocess.run([PALACE, "-np", "4", f"{tag}.json"], env=solver.ENV,
                        stdout=open(f"{tag}_p.log", "w"),
                        stderr=subprocess.STDOUT,
                        timeout=solver.DEFAULT_TIMEOUT_S).returncode
    dt = time.time() - t0
    if rc or dt < solver.MIN_SECONDS:
        tail = pathlib.Path(f"{tag}_p.log").read_text().strip().splitlines()
        raise RuntimeError(f"{tag}: rc={rc} in {dt:.0f}s — "
                           f"{tail[-1] if tail else '(empty log)'}")
    print(f"    solved in {dt:.0f}s", flush=True)


print(__doc__)
print("=" * 78, flush=True)
fac, _ = meshsweep.sweep(CASES, BASE)
if not fac:
    sys.exit("mesh sweep failed")
print(f"  ✅ all 4 cases at a COMMON size-factor {fac}", flush=True)

# 🔴 CASES-DIFFER GATE (R101). A rigid translation MUST change the mesh — that is
# the entire point. If gmsh returned identical meshes the probe measures nothing.
import hashlib
h = {t: hashlib.md5(pathlib.Path(f"{t}.msh").read_bytes()).hexdigest()[:10]
     for t, _e in CASES}
n = {t: solveconf.load_meta(f"{t}.msh")["tets"] for t, _e in CASES}
for t in h:
    print(f"  {t}: md5 {h[t]}  {n[t]:,} tets", flush=True)
if len(set(h.values())) != len(CASES):
    sys.exit("🔴 translation did not change the mesh — the probe measures "
             "nothing. NOT solving.")
print("  ✅ four distinct meshes of an IDENTICAL cavity\n", flush=True)

for tag, _e in CASES:
    run(tag)
results.sweep([t for t, _e in CASES], "r109",
              extra=dict(question="how much do f, Q0 and eta move under a RIGID "
                                  "translation, under which physics is exactly "
                                  "invariant?",
                         offsets={t: (e[1] if e else "0,0,0") for t, e in CASES},
                         tets=n, md5=h,
                         rotation_floor=dict(f_mhz=1.55, q0_percent=2.5,
                                             eta_points=5.0, source="R89"),
                         small=["r109a", "r109b", "r109c", "r109d"],
                         magnitude=["r109e", "r109f", "r109g"],
                         note="true value identical across all four — every "
                              "observed difference is artifact"))
print("\n  ⚠️ NO VERDICT HERE — run evaluate.py r109", flush=True)
