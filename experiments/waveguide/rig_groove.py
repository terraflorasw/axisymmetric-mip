#!/usr/bin/env python3
"""R79 — does the ignition competitor survive the GROOVE? The question as asked.

The user: "Would the interloper disappear with the brakes, or would it still
appear with the grooves?" R78 answers only the first half — its cases are quartz
and BARE, and bare is not a groove. A groove is a resonant slot structure at the
cap/barrel corner; it can host modes of its own, and R54 measured it moving TM
modes by -100 MHz (15 mm) and +136 MHz (lambda/4). "Removed the dielectric" and
"installed a slot" are different experiments.

🔑 THE QUESTION IS REFRAMED TO THE ONE THAT MATTERS OPERATIONALLY. Not "does this
mode exist" -- R54 already had to retract an "absent" that meant "outside my
window" -- but:

    AT IGNITION, DOES ANY NON-TE011 MODE BEAT TE011 FOR ABSORBED POWER,
    WITHIN THE AMPLIFIER'S REACH?

A mode driven to 2.25 or 2.55 GHz is unreachable and therefore harmless, whatever
it is. So this sweeps the amplifier's window and reports the competitor ranking
inside it. It makes NO claim about modes outside, and does not need to.

⚠️ WHY THIS IS NOT R59, AND NOT OPTIMISATION. It runs the two depths R54 already
used, 15 mm and lambda/4 = 30.6 mm, which BRACKET the unmeasured pole. It does not
choose a depth or look for a better one -- it asks whether the competitor exists
in the groove architecture at either end of the bracket. Existence, not selection.
R59 stays deferred.

CASES, one meshsweep call so they share a size-factor, quartz carried as the tie
point to R78:

    gq3     --mode-filter 3                  the geometry every result today used
    gv15    --mode-filter 0 --groove 3,15    below the pole (TM modes move DOWN)
    gv31    --mode-filter 0 --groove 3,30.6  above it (TM modes move UP)

Band 2.35-2.49 GHz at 50 kHz. Corrected by offset.te011 (+24.54) that is
2.375-2.515, i.e. the 2.400-2.500 LDMOS band plus a margin at each end. Step is
50 kHz because the narrow modes here run 0.10-0.18 MHz FWHM and at 200 kHz they
would be stepped over -- the linewidth_step_bias trap.

WHAT COUNTS AS AN ANSWER:
  · TE011 ranks FIRST on eta inside the band  -> the hazard is a quartz artefact
                                                 and the groove removes it
  · something else still ranks first          -> the hazard is architectural, and
                                                 ignition frequency must be
                                                 commanded regardless of filter
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
import solveconf
import solver

LOOP = "25.8,19.4,1.5,0.3"
PLASMA = "4.5,8.5,-20,10"
BASE = ["--radius", "103.70", "--length", "88.53", "--sectors", "5",
        "--loop-phi", "36", "--order", "2", "--loop", LOOP,
        "--plasma", PLASMA, "--plasma-h", "1.0"]
CASES = [("gq3",  ["--mode-filter", "3"]),
         ("gv15", ["--mode-filter", "0", "--groove", "3,15"]),
         ("gv31", ["--mode-filter", "0", "--groove", "3,30.6"])]
LABEL = {"gq3": "quartz 3 mm", "gv15": "groove 15 mm", "gv31": "groove λ/4"}
BAND, STEP = (2.35, 2.49), 5e-5
AZ_FLOOR = 0.0046
OFFSET = 0.02454
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
    # Assert the mesh is what the case NAME claims. A groove case that silently
    # kept its quartz, or a quartz case whose groove never got cut, would look
    # entirely plausible in the output — this is the silent-no-op class that has
    # produced confident wrong verdicts here twice.
    # 🔴 This read meta["groove"], which does not exist — the sidecar keeps
    # geometry under "geometry_mm". It returned None for EVERY case, including
    # the quartz one that never asked for a groove, and aborted a correct run
    # after 18 minutes of good solve. An assertion that cannot pass is not a
    # safety net; it is a second way to lose the answer. Verified against the
    # sidecars: gq3 [0,0]/brake 3.0, gv15 [3,15]/brake 0, gv31 [3,30.6]/brake 0.
    g = meta["geometry_mm"]["groove"]
    has_brake = meta["attributes"].get("brake") is not None
    wants_groove = "--groove" in dict(CASES)[tag]
    if wants_groove and g[1] <= 0:
        raise RuntimeError(f"{tag}: --groove requested but mesh reports "
                           f"groove={g}. The cut did not happen.")
    if wants_groove and has_brake:
        raise RuntimeError(f"{tag}: groove case still carries a brake attribute")
    if not wants_groove and not has_brake:
        raise RuntimeError(f"{tag}: quartz case has NO brake attribute")
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    print(f"    ✅ mesh checks: groove={g} mm, brake attr present={has_brake}",
          flush=True)
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
        if U[i] == max(U[i - 2:i + 3]) and U[i] > 0.003 * um:
            b1, b2 = modes.azimuthal(sect[i])
            r = recs[i]
            out.append(dict(f=r["f"], rel=U[i] / um, pm=r["pm"], pe=r["pe"],
                            Q0=r["Q0"], eta=1 - r["gamma"] ** 2, b1=b1, b2=b2))
    return out


def call_it(r):
    """TE011 is the bore-MAGNETIC mode with negligible bore-E and the highest Q0.

    Labels are advisory; the ranking below does not depend on them except for
    identifying TE011 itself, which is done on bore-H/bore-E ratio — the rule
    that has survived this project, unlike every ratio-of-two-small-numbers.
    """
    if r["pe"] > 5 * r["pm"]:
        return "TM020-like (bore-E)"
    if r["pm"] > 8 * r["pe"] and r["Q0"] > 25000:
        return "TE011"
    if r["b2"] / AZ_FLOOR > 20:
        return "m=1 (TM111-like)"
    return "other"


print(__doc__)
print("=" * 78, flush=True)
if not REPLAY:
    fac, _ = meshsweep.sweep(CASES, BASE)
    if not fac:
        sys.exit("mesh sweep failed — a mixed-density set proves nothing")
    print(f"  ✅ all 3 cases meshed at a COMMON size-factor {fac}", flush=True)

sp = {}
for tag, _e in CASES:
    if not (REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists()):
        run(tag)
    sp[tag] = spectrum(tag)

print("\n" + "=" * 78)
for tag, _e in CASES:
    print(f"\n  {LABEL[tag]}  ({tag}) — {len(sp[tag])} resonance(s) in "
          f"{BAND[0]}-{BAND[1]} GHz")
    print(f"    {'f raw':>9}{'f+off':>9}{'bore-H':>9}{'bore-E':>10}{'Q0':>8}"
          f"{'eta':>8}{'b2/flr':>8}  label")
    for r in sorted(sp[tag], key=lambda x: -x["eta"]):
        print(f"    {r['f']:>9.4f}{r['f']+OFFSET:>9.4f}{r['pm']:>9.5f}"
              f"{r['pe']:>10.6f}{r['Q0']:>8.0f}{100*r['eta']:>7.1f}%"
              f"{r['b2']/AZ_FLOOR:>8.1f}  {call_it(r)}")

print("\n" + "=" * 78)
print("THE ANSWER — who wins the power at ignition, inside the amplifier's band")
print(f"{'case':>14}{'TE011 eta':>11}{'best rival':>12}{'rival eta':>11}"
      f"{'ratio':>8}{'gap MHz':>9}  rival")
verdicts = []
for tag, _e in CASES:
    te = [r for r in sp[tag] if call_it(r) == "TE011"]
    if not te:
        print(f"{LABEL[tag]:>14}   🔴 TE011 not identified in band — cannot rank")
        verdicts.append(None)
        continue
    te = max(te, key=lambda r: r["Q0"])
    rivals = [r for r in sp[tag] if r is not te]
    if not rivals:
        print(f"{LABEL[tag]:>14}{100*te['eta']:>10.1f}%{'none':>12}")
        verdicts.append(True)
        continue
    rv = max(rivals, key=lambda r: r["eta"])
    win = te["eta"] >= rv["eta"]
    verdicts.append(win)
    print(f"{LABEL[tag]:>14}{100*te['eta']:>10.1f}%{rv['f']:>12.4f}"
          f"{100*rv['eta']:>10.1f}%{rv['eta']/te['eta']:>8.2f}"
          f"{1e3*(rv['f']-te['f']):>9.1f}  {call_it(rv)}"
          + ("   ✅ TE011 wins" if win else "   🔴 RIVAL WINS"))

print("\nVERDICT")
q, g15, g31 = verdicts
if q is False and g15 and g31:
    print("  ✅ THE HAZARD IS A QUARTZ ARTEFACT. With either groove depth TE011 "
          "takes the most\n     power at ignition; with the quartz it does not. "
          "Dropping the annuli removes\n     the competitor, and the groove was "
          "already the decision.")
elif q is False and not (g15 and g31):
    print("  🔴 THE HAZARD IS ARCHITECTURAL, not a property of the quartz. A "
          "non-TE011 mode\n     still outcouples TE011 with the groove in "
          "place, so 'command the ignition\n     frequency, do not search for "
          "it' stands regardless of which filter is built.")
elif q:
    print("  ⚠️ TE011 already wins WITH the quartz on this mesh, so this run "
          "does not\n     reproduce the hazard and cannot say whether the "
          "groove removes it. Note the\n     hazard was measured at loop-phi 0 "
          "(R76) and this is loop-phi 36 — the\n     competitor ranking depends "
          "on loop AZIMUTH, which is its own finding.")
else:
    print("  mixed — read the per-case table above; do not compress this into a "
          "verdict")
print("\n⚠️ SCOPE: one loop azimuth, cold, order 1, 2.35-2.49 GHz only. Modes "
      "driven outside\n   that window are unreachable by a 2.4-2.5 GHz LDMOS and "
      "are deliberately not\n   tracked — this is a reachability claim, NOT a "
      "mode census, and it is not R59.")
print(flush=True)
