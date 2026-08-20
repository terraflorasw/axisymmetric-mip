#!/usr/bin/env python3
"""R80 — groove WIDTH at the 21 mm depth R59 chose. Does Z0 ∝ w help or hurt?

R59 closed on depth: 21 mm is the only depth that leaves TE011 ALONE in the
amplifier band, because it parks the groove's own lossy resonances (Q0 3,188 to
5,717) at 2.52-2.55 corrected, above the LDMOS top. It also showed the groove is
a RESONATOR, not merely a detuner — at 26 mm one of those parasites lands on
TE011 and collapses it to Q0 8,089.

Width has never been varied in this project. R54 used 3 mm and R59 held it fixed.

🔑 THE MODEL AND ITS PREDICTION. The slot is a shorted annular parallel-plate
stub of radial width gw and axial depth gd:

        Z0 = eta0 * gw / (2*pi*a) = 1.73 ohm at gw = 3 mm
        X  = Z0 * tan(beta*gd)

so DEPTH sets the electrical length (where the pole is) and WIDTH sets Z0 (how
much reactance per unit length). Two competing consequences, and the run decides
which dominates:

  ✅ tolerance      dX/dd = beta*(Z0 + X^2/Z0) is MINIMISED at Z0 = X, i.e. at
                    lambda/8. A wider groove reaches a given detuning further from
                    the pole, on a gentler slope. For a fixed target, wider is
                    less sensitive to machining — the opposite of intuition.
  🔴 parasite drag  the groove's own resonances are what 21 mm was chosen to park.
                    Widening strengthens the slot's coupling to the cavity, and it
                    may drag that family DOWN into 2.400-2.500 — which would make
                    3 mm near-optimal and kill width as a lever.

⚠️ R59 ALSO SHOWED THE STUB MODEL IS INCOMPLETE: a simple stub has one pole per
lambda/2 and cannot produce a family of low-Q resonances every few mm of depth.
So the Z0 ∝ gw scaling is a PREDICTION UNDER A MODEL THAT IS ALREADY KNOWN TO BE
PARTIAL. It is being tested, not applied.

WIDTHS: 3 (tie point to R59's d21p0), 6, 9, 12 mm.

⚠️ Four points, not the three scoped. Three cannot distinguish a linear Z0 ∝ gw
trend from a saturating one, and the model's own optimum for a 2-3x stronger
detuning lands between 6 and 9 mm — so a point beyond it is needed to see whether
the trend turns over. The cost is one extra solve.

Indivisibility is not at issue here as it was for depth: width sets an impedance,
not an electrical length, so commensurate values carry no resonance risk.

⚠️ BAND 2.34-2.56, wider than R59's, so the parasitic family stays visible if
widening pushes it UP. Reachability is judged on 2.400-2.500 corrected; the rest
of the window exists so that "it left the band" can be distinguished from "it left
my window" — the error that has now cost this project three times.

BOTH DRIVER BUGS FROM R59 ARE FIXED HERE:
  · rivals are filtered to the AMPLIFIER BAND before ranking (R59's C4 scored
    modes the LDMOS cannot reach);
  · no mode is tracked by "largest of its type" across cases. Modes are matched to
    the gw = 3 reference by field signature with a rejection threshold, and an
    unmatched mode is REPORTED as unmatched rather than paired with whatever was
    nearest (R59's C5/C6 died of exactly that).
"""
import json
import math
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep
import modes
import results
import solveconf
import solver

DEPTH = 21.0
WIDTHS = [3.0, 6.0, 9.0, 12.0]
CASES = [(f"w{int(w)}d21", ["--groove", f"{w},{DEPTH}"]) for w in WIDTHS]
BASE = ["--radius", "103.70", "--length", "88.53", "--sectors", "5",
        "--loop-phi", "36", "--order", "2", "--loop", "25.8,19.4,1.5,0.3",
        "--plasma", "4.5,8.5,-20,10", "--plasma-h", "1.0", "--mode-filter", "0"]
BAND, STEP = (2.34, 2.56), 5e-5
OFF = 0.02454
LDMOS = (2.400, 2.500)
AZ_FLOOR = 0.0046
QREF = dict(b1=0.0263, b2=0.0287, pmpe=27.5, q0=37059.0)
SIG_MAX = 0.15
ETA0, A = 376.730, 0.10370
REPLAY = "--replay" in sys.argv
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def run(tag, w):
    mesh = f"{tag}.msh"
    meta = solveconf.load_meta(mesh)
    g = meta["geometry_mm"]["groove"]
    if abs(g[0] - w) > 1e-6 or abs(g[1] - DEPTH) > 1e-6:
        raise RuntimeError(f"{tag}: asked for [{w},{DEPTH}], mesh says {g}")
    if meta["attributes"].get("brake") is not None:
        raise RuntimeError(f"{tag}: groove case still carries a brake attribute")
    pl = meta["attributes"].get("plasma")
    c, meta, _ = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    print(f"  {tag}: groove {g} mm, {meta['tets']:,} tets", flush=True)
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


def spectrum(tag):
    recs = dq.load(tag)
    sect = modes.sector_energy(tag)
    if sect is None:
        raise RuntimeError(f"{tag}: no sector data")
    U = [r["U"] for r in recs]
    um = max(U)
    out = []
    for i in range(2, len(U) - 2):
        if U[i] == max(U[i - 2:i + 3]) and U[i] > 0.01 * um:
            b1, b2 = modes.azimuthal(sect[i])
            r = recs[i]
            out.append(dict(f=r["f"], rel=U[i] / um, pm=r["pm"], pe=r["pe"],
                            pmpe=r["pm"] / max(r["pe"], 1e-12), Q0=r["Q0"],
                            eta=1 - r["gamma"] ** 2, b1=b1, b2=b2,
                            inband=LDMOS[0] < r["f"] + OFF < LDMOS[1]))
    return out


print(__doc__)
print("=" * 78, flush=True)
def meshes_ready():
    """True only if every case's mesh exists, has the right groove, and they
    all share a size-factor. Verifying beats rebuilding — but a mesh that is
    merely PRESENT proves nothing, so the geometry is read back out of each
    sidecar rather than assumed from the filename."""
    facs = set()
    for (tag, _e), w in zip(CASES, WIDTHS):
        mp = pathlib.Path(f"{tag}.msh")
        sp_ = pathlib.Path(f"{tag}.meta.json")
        if not (mp.exists() and sp_.exists()):
            return False
        m = json.loads(sp_.read_text())
        g = m["geometry_mm"]["groove"]
        if abs(g[0] - w) > 1e-6 or abs(g[1] - DEPTH) > 1e-6:
            return False
        facs.add(m["size_factor"])
    return len(facs) == 1


if not REPLAY:
    if meshes_ready():
        print("  ✅ all widths already meshed, geometry verified from sidecars, "
              "common size-factor — reusing", flush=True)
    else:
        fac, _ = meshsweep.sweep(CASES, BASE)
        if not fac:
            sys.exit("mesh sweep failed — a mixed-density width ladder is not "
                     "a ladder")
        print(f"  ✅ all {len(CASES)} widths meshed at a COMMON size-factor "
              f"{fac}", flush=True)

sp = {}
for (tag, _e), w in zip(CASES, WIDTHS):
    if not (REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists()):
        run(tag, w)
    sp[w] = spectrum(tag)

# 🔑 THE DRIVER'S JOB ENDS HERE. It solves and it records; it does not conclude.
# Interpretation — labels, reachability, criteria, verdict — lives in evaluate.py,
# which reads these files and can be corrected without re-solving. The criteria
# themselves are in the docstring above, declared before the run, which is where
# the pre-commitment that the verdict block used to provide actually comes from.
idx, got = results.sweep([t for t, _e in CASES], "r80",
                         extra=dict(depth_mm=DEPTH, widths_mm=WIDTHS,
                                    model_Z0_ohm={w: round(ETA0 * w * 1e-3 /
                                                           (2 * math.pi * A), 3)
                                                  for w in WIDTHS},
                                    tie_point=dict(
                                        case="w3d21", against="d21p0 (R59)",
                                        expect="identical mesh (143,769 tets) "
                                               "so TE011 must reproduce to the "
                                               "digit; if it does not, stop")))
print(f"\n  wrote {len(got)} result files + r80.sweep.json")
print(f"  comparable: {idx['comparable']} — {idx['note']}")
for t, d in got.items():
    if "error" in d:
        print(f"    🔴 {t}: {d['error']}")
    else:
        print(f"    {t}: {len(d['modes'])} modes, {d['tets']:,} tets, "
              f"sf {d['size_factor']}")
print("\n  next:  python3 evaluate.py --sweep r80")
print("         python3 evaluate.py w3d21 w6d21 w9d21 w12d21")
print(flush=True)
