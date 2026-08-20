#!/usr/bin/env python3
"""R78 — is the interloper a CAVITY mode at all, or a mode of the mode filter?

R77b falsified R77. A strong m=1 mode sits at 2.3431 GHz (DFT bin2 = 0.1774, 38.6x
the m=0 floor, against R47's 57.7x) -- that is TM111, in the band R77 never
searched, 52.8 MHz below TE011. So TM111 is accounted for, TE011 is accounted for,
and the 2.4382 interloper is STILL UNIDENTIFIED.

WHAT SURVIVES FROM R77, because it came from a geometric derivative and not from
a mode chart:

    p = 1          df/dL = -14.34 MHz/mm, and R(from df/da) + (1-R)(from df/dL)
                   = 1.05, two independent measurements agreeing
    chi_eff ~ 3.85 but chi = 3.8317 at p=1 admits ONLY TE011 and TM111, and BOTH
                   ARE NOW ASSIGNED ELSEWHERE. So the empty-cavity dispersion does
                   not describe this mode, which is itself the clue.
    m is weak      bin2 0.0499 = 10.8x floor, against TM111's 38.6x. Not a clean
                   m=1. Nor clean m=0: TE011 sits at 6.3x on the same mesh.

🔑 THE HYPOTHESIS. Of the four cold modes, this one has the LOWEST Q0 by a wide
margin -- 17,240 against TE011's 37,029, TM020's 23,378, TM111's 19,852 -- and Q0
is where the dielectric loss shows up. The only bulk dielectric bodies here are
the two 3 mm fused-quartz mode-filter annuli (OD 207.4, ID 20) and the torch tube.
A 207 mm annulus of eps_r ~ 3.8 is not a small perturbation; it is a dielectric
ring resonator in its own right, which is precisely how MICAP works.

⚠️ Note what this would mean: the mode filter, whose job is to SEPARATE the
degenerate competitor from TE011, would itself be supplying the mode that beats
TE011 for power at ignition.

THE TEST. Remove the annuli and see what the mode does. The discrimination is
enormous and needs no model:

    a CAVITY mode          shifts a few MHz and stays  (TE011 moved 4.5 MHz
                           between quartz and bare in R54)
    an ANNULUS mode        moves by tens to hundreds of MHz, or ceases to exist

Both cases are meshed in ONE meshsweep call so they share a size-factor, and the
band is widened to 2.30-2.48 GHz so a mode that moves a long way is FOUND rather
than reported absent -- R54 called TM111 and TM020 "absent" from a 160 MHz window
and had to retract it. Absent from a window is not absent.

⚠️ This is identification, not optimisation: it asks what the mode IS, and does
not choose a filter. R59 (groove depth and width) stays deferred.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import dq
import meshsweep
import modes
import solveconf
import solver

LOOP = "25.8,19.4,1.5,0.3"
PLASMA = "4.5,8.5,-20,10"
BASE = ["--radius", "103.70", "--length", "88.53", "--sectors", "5",
        "--loop-phi", "36", "--order", "2", "--loop", LOOP,
        "--plasma", PLASMA, "--plasma-h", "1.0"]
CASES = [("fltr3", ["--mode-filter", "3"]), ("fltr0", ["--mode-filter", "0"])]
BAND, STEP = (2.30, 2.48), 5e-5
AZ_FLOOR = 0.0046
REPLAY = "--replay" in sys.argv
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def run(tag):
    mesh = f"{tag}.msh"
    meta = solveconf.load_meta(mesh)
    pl = meta["attributes"].get("plasma")
    c, meta, dropped = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    for d in dropped:
        print(f"    dropped: {d}", flush=True)
    for m in c["Domains"]["Materials"]:
        if m["Attributes"] == [pl] and "Conductivity" in m:
            raise RuntimeError(f"{tag}: plasma still conducting")
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
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
    print(f"  {tag}: {dt:.0f}s", flush=True)


def spectrum(tag):
    recs = dq.load(tag)
    sect = modes.sector_energy(tag)
    if sect is None:
        raise RuntimeError(f"{tag}: no sector data")
    U = [r["U"] for r in recs]
    um = max(U)
    out = []
    for i in range(2, len(U) - 2):
        if U[i] == max(U[i - 2:i + 3]) and U[i] > 0.005 * um:
            b1, b2 = modes.azimuthal(sect[i])
            r = recs[i]
            out.append(dict(f=r["f"], rel=U[i] / um, pm=r["pm"], pe=r["pe"],
                            Q0=r["Q0"], eta=1 - r["gamma"] ** 2, b1=b1, b2=b2))
    return out


print(__doc__)
print("=" * 78, flush=True)
if not REPLAY:
    fac, _ = meshsweep.sweep(CASES, BASE)
    if not fac:
        sys.exit("mesh sweep failed — a mixed-density pair proves nothing")
    print(f"  ✅ both cases meshed at a COMMON size-factor {fac}", flush=True)

sp = {}
for tag, _e in CASES:
    if not (REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists()):
        run(tag)
    sp[tag] = spectrum(tag)
    print(f"\n  {tag}: {len(sp[tag])} resonance(s) in "
          f"{BAND[0]}-{BAND[1]} GHz")
    print(f"    {'f GHz':>9}{'rel':>8}{'bore-H':>9}{'bore-E':>10}{'Q0':>8}"
          f"{'eta':>7}{'b1(m2)':>9}{'b2(m1)':>9}{'b2/flr':>8}")
    for r in sp[tag]:
        print(f"    {r['f']:>9.4f}{r['rel']:>8.3f}{r['pm']:>9.5f}"
              f"{r['pe']:>10.6f}{r['Q0']:>8.0f}{100*r['eta']:>6.1f}%"
              f"{r['b1']:>9.4f}{r['b2']:>9.4f}{r['b2']/AZ_FLOOR:>8.1f}",
              flush=True)

print("\n" + "=" * 78)
print("WHAT MOVED WHEN THE QUARTZ CAME OUT")
# Track by field signature, which is intrinsic; report the shift for each.
import math


def near(r, cand):
    if not cand:
        return None, float("inf")
    def d(x):
        return sum((math.log10(max(x[k], 1e-9))
                    - math.log10(max(r[k], 1e-9))) ** 2 for k in ("pm", "pe"))
    b = min(cand, key=d)
    return b, d(b)


print(f"{'filter 3':>10}{'->':>4}{'filter 0':>10}{'shift MHz':>12}"
      f"{'sig dist':>10}{'Q0 3->0':>16}")
for r in sp["fltr3"]:
    b, d = near(r, sp["fltr0"])
    if b is None or d > 0.15:
        print(f"{r['f']:>10.4f}{'->':>4}{'NONE':>10}{'—':>12}{d:>10.3f}"
              f"{'':>16}   🔴 no counterpart")
        continue
    print(f"{r['f']:>10.4f}{'->':>4}{b['f']:>10.4f}"
          f"{1e3*(b['f']-r['f']):>12.1f}{d:>10.3f}"
          f"{r['Q0']:>8.0f}{b['Q0']:>8.0f}")

print("\nVERDICT ON THE INTERLOPER (the filter-3 mode at ~2.438)")
tgt = min(sp["fltr3"], key=lambda r: abs(r["f"] - 2.4382))
b, d = near(tgt, sp["fltr0"])
if b is None or d > 0.15:
    print("  🔑 IT HAS NO COUNTERPART WITHOUT THE QUARTZ. The mode filter is not "
          "merely\n     shifting this mode — it is CREATING it. The annuli are a "
          "dielectric ring\n     resonator, and the thing that beats TE011 for "
          "power at ignition is a mode\n     of the component installed to "
          "protect TE011.")
else:
    sh = 1e3 * (b["f"] - tgt["f"])
    print(f"  it maps to {b['f']:.4f} with the quartz removed, a shift of "
          f"{sh:+.1f} MHz")
    if abs(sh) < 15.0:
        print("  ✅ CAVITY MODE. It barely notices the dielectric, so it is a "
              "mode of the metal\n     box, not of the annuli. Identification "
              "must continue in the cavity chart —\n     and the p=1 / "
              "chi_eff 3.85 fingerprint still has to be reconciled with TE011\n"
              "     and TM111 both being assigned.")
    else:
        print(f"  🔑 STRONGLY FILTER-COUPLED: {abs(sh):.0f} MHz is far more than "
              "a cavity mode moves\n     (TE011 shifts ~4.5 MHz). Its frequency "
              "is set mostly by the quartz, so the\n     ignition hazard is a "
              "PROPERTY OF THE MODE FILTER and moves with any change\n     to "
              "it — including the groove.")

print("\n⚠️ One geometry, order 1, cold. This says what the mode is ATTACHED to. "
      "It does\n   not by itself give (m, n, p), and it does not choose a filter.")
print(flush=True)
