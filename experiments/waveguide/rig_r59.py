#!/usr/bin/env python3
"""R59 — CHOOSE THE GROOVE DEPTH. A ladder bracketing the TE011/TM111 crossing.

R59 was deferred as optimisation. R79 changed what it is: at a 15 mm groove there
is NO PURE TE011 — two modes 3.5 MHz apart, azimuthal content 26-33x the m=0
floor, Q0 down 45%, and 67.3% of cold power landing in the mixed state. The groove
had swept TM111 onto TE011 and they hybridised. **Depth does not tune the
operating mode; it decides whether the operating mode exists.** That is a
constraint on the design as it stands, which is why this is now running.

🔑 WHAT THE LADDER BRACKETS, AND WHY THESE DEPTHS.

Measured so far on THIS geometry (sc06 loop), TM111 minus TE011:

    bare      +26.8 MHz   (TM111 above)
    15 mm       ~0        HYBRIDISED — the crossing
    30.6 mm   -11.7 MHz   (TM111 below)

So TM111 sweeps DOWNWARD through TE011 as depth increases, and the crossing sits
near 15 mm. ⚠️ Note 15.3 mm is lambda/8 at 2.4 GHz — the crossing may be a
resonant feature of the slot rather than an accident, which would make it
predictable. The ladder tests that.

    10   below the crossing: fixes the approach rate and confirms TM111 above
    15   THE CROSSING — tie point to R79, and a known-answer check on this sweep
    21   R54's estimated pole (20-23 mm). Tests whether a pole exists here at all:
         R79's three points show the SEPARATION moving monotonically, which a pole
         would not do, so R54's inference is in question
    26   first candidate clear of both crossing and pole
    30.6 lambda/4 — second tie point to R79
    36   past lambda/4: does deeper keep improving, or turn over?

Indivisibility: the four NEW depths (10, 21, 26, 36) are none of lambda/8 = 15.3,
lambda/4 = 30.6, 3*lambda/8 = 45.9 or lambda/2 = 61.2, so a resonant slot length
cannot be mistaken for a trend. 15 and 30.6 are deliberate repeats, not probes.

⚠️ ALL SIX IN ONE meshsweep CALL. R79's cases came from a different sweep; mixing
them in would be the R11/R27 error that has cost this project three sweeps.

🔑 TWO PURITY METRICS THAT DISAGREE, AND BOTH ARE REPORTED.

    pm/pe        bore TE-character.   quartz 27.5, lambda/4 58.4  -> lambda/4 wins
    bin1, bin2   azimuthal asymmetry. quartz 0.026, lambda/4 0.079 -> quartz wins 3x

R54 measured lambda/4 CLEANEST on bin1 (0.0027 vs quartz 0.0046) using the DESIGN
loop. With sc06 the whole azimuthal floor rises 10-30x and the ranking inverts:
sc06 is now the dominant symmetry breaker, not the filter. So a depth chosen on
R54's numbers is a depth chosen for a coupler we are not using. Both metrics are
carried here and neither is allowed to stand alone.

DECISION CRITERIA, fixed BEFORE the run so the table cannot be read selectively:

  C1 azimuthal   bin1 and bin2 <= quartz's 0.0263 / 0.0287       (what the filter buys)
  C2 bore TE     pm/pe >= quartz's 27.5
  C3 Q0          TE011 Q0 >= quartz's 37,059                     (the +6% claim)
  C4 ignition    eta(TE011) >= 2x eta(best rival) in band        (R76's hazard)
  C5 separation  |f(TM111) - f(TE011)| >= 10 cold linewidths = 23.4 MHz
  C6 tolerance   |d(separation)/d(depth)| * 0.2 mm <= 1 linewidth (2.34 MHz)
                 -> |d sep/d depth| <= 11.7 MHz/mm, from the ladder spacing

C6 is the production criterion and it is the one no previous run could compute,
because it needs the ladder rather than a point. TM020 placement is REPORTED, not
gated: R60 measured it 18.3 dB down at the operational tilt and the AUDIT demoted
the band floor to a second layer.

⚠️ This SELECTS a value, which is optimisation, and it runs only because the user
asked for it after R79 showed the mode's existence is at stake.
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
        "--plasma", PLASMA, "--plasma-h", "1.0", "--mode-filter", "0"]
DEPTHS = [10.0, 15.0, 21.0, 26.0, 30.6, 36.0]
CASES = [(f"d{str(d).replace('.', 'p')}", ["--groove", f"3,{d}"]) for d in DEPTHS]
BAND, STEP = (2.34, 2.54), 5e-5
OFF_TE, OFF_TM = 0.02454, 0.02006
AZ_FLOOR = 0.0046
QREF = dict(b1=0.0263, b2=0.0287, pmpe=27.5, q0=37059.0)   # quartz 3 mm, R79
LW = 2.341                                                  # TE011 cold FWHM, MHz
REPLAY = "--replay" in sys.argv
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def run(tag, depth):
    mesh = f"{tag}.msh"
    meta = solveconf.load_meta(mesh)
    g = meta["geometry_mm"]["groove"]
    if abs(g[1] - depth) > 1e-6:
        raise RuntimeError(f"{tag}: asked for depth {depth}, mesh says {g}")
    if meta["attributes"].get("brake") is not None:
        raise RuntimeError(f"{tag}: groove case still carries a brake attribute")
    pl = meta["attributes"].get("plasma")
    c, meta, dropped = solveconf.driven(
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
        raise RuntimeError(f"{tag}: no sector data — m is unmeasurable")
    U = [r["U"] for r in recs]
    um = max(U)
    out = []
    for i in range(2, len(U) - 2):
        if U[i] == max(U[i - 2:i + 3]) and U[i] > 0.001 * um:
            b1, b2 = modes.azimuthal(sect[i])
            r = recs[i]
            out.append(dict(f=r["f"], rel=U[i] / um, pm=r["pm"], pe=r["pe"],
                            pmpe=r["pm"] / max(r["pe"], 1e-12), Q0=r["Q0"],
                            eta=1 - r["gamma"] ** 2, b1=b1, b2=b2))
    return out


def classify(sp):
    """TE011 = the bore-MAGNETIC mode with the highest pm/pe. TM020 = bore-E.

    ⚠️ NO Q0 THRESHOLD. R79's labeller required Q0 > 25,000 and therefore refused
    to name a TE011 at 15 mm — where the honest answer is that TE011 exists but is
    HYBRIDISED and its Q0 has collapsed. A classifier that declines to name a
    degraded mode hides exactly the failure being looked for.
    """
    te = max(sp, key=lambda r: r["pmpe"]) if sp else None
    tm020 = max(sp, key=lambda r: r["pe"]) if sp else None
    m1 = [r for r in sp if r is not te and r["b2"] / AZ_FLOOR > 8]
    tm111 = max(m1, key=lambda r: r["rel"]) if m1 else None
    return te, tm020, tm111


print(__doc__)
print("=" * 78, flush=True)
if not REPLAY:
    fac, _ = meshsweep.sweep(CASES, BASE)
    if not fac:
        sys.exit("mesh sweep failed — a mixed-density ladder is not a ladder")
    print(f"  ✅ all {len(CASES)} depths meshed at a COMMON size-factor {fac}",
          flush=True)

rows = []
for (tag, _e), d in zip(CASES, DEPTHS):
    if not (REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists()):
        run(tag, d)
    sp = spectrum(tag)
    te, tm020, tm111 = classify(sp)
    best_rival = max([r for r in sp if r is not te], key=lambda r: r["eta"],
                     default=None)
    rows.append(dict(d=d, tag=tag, sp=sp, te=te, tm020=tm020, tm111=tm111,
                     rival=best_rival,
                     sep=(1e3 * (tm111["f"] - te["f"]) if (tm111 and te) else None)))
    print(f"    depth {d:>5.1f}: TE011 f={te['f']:.4f} pm/pe={te['pmpe']:.1f} "
          f"Q0={te['Q0']:,.0f} eta={100*te['eta']:.1f}% "
          f"bin1={te['b1']:.4f} bin2={te['b2']:.4f}", flush=True)

print("\n" + "=" * 78)
print("THE LADDER")
print(f"{'depth':>7}{'TE011 f':>10}{'pm/pe':>8}{'Q0':>9}{'bin1':>8}{'bin2':>8}"
      f"{'eta':>7}{'TM111 sep':>11}{'TM020+off':>11}{'rival eta':>10}")
for r in rows:
    te, sep = r["te"], r["sep"]
    tm = r["tm020"]
    print(f"{r['d']:>7.1f}{te['f']:>10.4f}{te['pmpe']:>8.1f}{te['Q0']:>9,.0f}"
          f"{te['b1']:>8.4f}{te['b2']:>8.4f}{100*te['eta']:>6.1f}%"
          f"{(f'{sep:+.1f}' if sep is not None else '—'):>11}"
          f"{(tm['f']+OFF_TM if tm else float('nan')):>11.4f}"
          f"{(100*r['rival']['eta'] if r['rival'] else 0):>9.1f}%")

print("\nWHERE THE CROSSING IS")
xs = [(r["d"], r["sep"]) for r in rows if r["sep"] is not None]
cross = None
for (d0, s0), (d1, s1) in zip(xs, xs[1:]):
    if s0 * s1 < 0:
        cross = d0 + (d1 - d0) * abs(s0) / (abs(s0) + abs(s1))
        print(f"  🔑 TM111 crosses TE011 between {d0:.1f} and {d1:.1f} mm, "
              f"at ~{cross:.1f} mm")
        print(f"     λ/8 at 2.4 GHz is 15.3 mm — "
              + ("✅ consistent, the crossing is a RESONANT slot feature"
                 if abs(cross - 15.3) < 2.0 else
                 "⚠️ NOT λ/8, so the crossing is not a simple slot resonance"))
if cross is None:
    print("  ⚠️ no sign change in the sampled range — the crossing is outside "
          "10-36 mm,\n     or the ladder stepped over it")

print("\nTOLERANCE (C6) — d(separation)/d(depth), and what ±0.2 mm machining costs")
for (d0, s0), (d1, s1) in zip(xs, xs[1:]):
    g = (s1 - s0) / (d1 - d0)
    print(f"  {d0:>5.1f}-{d1:>5.1f} mm: {g:>+7.2f} MHz/mm  -> ±0.2 mm moves "
          f"TM111 {abs(0.2*g):>5.2f} MHz = {abs(0.2*g)/LW:>4.2f} linewidths"
          + ("  ✅" if abs(0.2 * g) <= LW else "  🔴"))

print("\nCRITERIA")
print(f"{'depth':>7}{'C1 azim':>9}{'C2 pm/pe':>10}{'C3 Q0':>8}{'C4 ign':>8}"
      f"{'C5 sep':>8}  verdict")
ok_rows = []
for r in rows:
    te, sep = r["te"], r["sep"]
    c1 = te["b1"] <= QREF["b1"] and te["b2"] <= QREF["b2"]
    c2 = te["pmpe"] >= QREF["pmpe"]
    c3 = te["Q0"] >= QREF["q0"]
    c4 = (r["rival"] is None) or (te["eta"] >= 2 * r["rival"]["eta"])
    c5 = sep is not None and abs(sep) >= 10 * LW
    n = sum((c1, c2, c3, c4, c5))
    if n == 5:
        ok_rows.append(r)
    m = lambda b: "✅" if b else "🔴"
    print(f"{r['d']:>7.1f}{m(c1):>8}{m(c2):>9}{m(c3):>7}{m(c4):>7}{m(c5):>7}"
          f"  {n}/5")

print("\nVERDICT")
if ok_rows:
    best = max(ok_rows, key=lambda r: r["te"]["Q0"])
    print(f"  ✅ {len(ok_rows)} depth(s) pass all five. Best on Q0: "
          f"{best['d']:.1f} mm.")
else:
    print("  🔴 NO DEPTH PASSES ALL FIVE. Report which criterion each fails and "
          "do NOT\n     pick a winner by relaxing one silently — that is how "
          "R54's verdict block was\n     wrong three ways. If C1 is the "
          "universal failure, the binding problem is the\n     COUPLER's "
          "symmetry breaking, not the filter, and R59 cannot fix it.")
print("\n⚠️ Cold, order 1, one loop azimuth, sc06's coupler. C1 is measured "
      "against a floor\n   that sc06 itself sets — see the docstring.")
print(flush=True)
