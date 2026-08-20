#!/usr/bin/env python3
"""R81 — IDENTIFY the slot modes by MEASURING where their energy is.

Three rounds of inference have failed to identify the modes the groove
introduces, and each failure came from reading identity out of scalars that
cannot carry it:

  R77   called the 2.4382 interloper TM111 by elimination — using a baseline
        from a DIFFERENT geometry, in a band chosen to exclude where that
        baseline pointed. Retracted.
  R78   proposed a dielectric resonance of the quartz annuli. Killed by its own
        control: the mode survives with the quartz removed.
  R59   tracked "the m=1 mode with the most stored energy" and re-identified its
        target at every depth. C5/C6 withdrawn.

🔑 THE MEASUREMENT THAT ENDS THE GUESSING. Give the groove its OWN mesh attribute
and read the fraction of each mode's energy inside it. That is not an inference:

    groove_frac ~ 0      a cavity mode. The groove perturbs it from outside.
    groove_frac large    a mode the groove CREATED. Its frequency is set by the
                         slot, and no cavity mode chart will ever predict it.

One number per mode, per depth. It settles what bore-H, bore-E and a 5-sector
DFT could not, because those three measure where a mode is NOT (the bore) and
this measures where it IS.

⚠️ WHAT THIS RUN DOES NOT FIX — and it must not be forgotten. The azimuthal
binning is still N = 5, which resolves NOTHING above m = 1:

        m0 = m5        "azimuthally clean" may be m=5
        m1 = m4 = m6   every "strong m=1" label in this project may be m=4
        m2 = m3 = m7   bin1 conflates two orders

and 2*pi*a = 5.3 lambda, so orders 5-6 are exactly what a ring structure makes.
N = 24 is the minimum that resolves m <= 6, and it is a SEPARATE run because
sector count moves Q by 6.9% (R54b) — a high-N mesh is an identification
instrument only, never a Q or f comparison. Registered as R82; not done here.

DEPTHS, chosen because their behaviour already differs and is already measured:

    15 mm   the crossing — TE011 hybridised, Q0 18,027, bin1/bin2 both ~0.13
    21 mm   the clean candidate — slot family parked ABOVE the band, 0 rivals
    26 mm   the catastrophe — Q0 collapses to 8,089, every mode lossy

🔑 What each depth is asked. At 21 mm: are the three modes above the band really
the slot's? At 26 mm: is the Q0 collapse TE011 HYBRIDISING with a slot mode
(groove_frac intermediate for both) or a slot mode SWAMPING it (one near zero,
one near one)? Those are different failures with different fixes, and no
measurement so far distinguishes them.

⚠️ TAGGING CHANGES THE MESH — 143,653 tets against 143,769 untagged, because the
slot is fragmented rather than fused. Verified 0.08%, but it means these
frequencies are NOT to be differenced against R59's. Comparisons live inside this
run. The untagged path was checked byte-identical first (143,769 both ways).

This driver solves and records. It does not conclude — evaluate.py does that, and
can be corrected without re-solving.
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

DEPTHS = [15.0, 21.0, 26.0]
WIDTH = 3.0
CASES = [(f"tg{int(d)}", ["--groove", f"{WIDTH},{d}", "--tag-groove"])
         for d in DEPTHS]
BASE = ["--radius", "103.70", "--length", "88.53", "--sectors", "5",
        "--loop-phi", "36", "--order", "2", "--loop", "25.8,19.4,1.5,0.3",
        "--plasma", "4.5,8.5,-20,10", "--plasma-h", "1.0", "--mode-filter", "0"]
BAND, STEP = (2.34, 2.56), 5e-5
REPLAY = "--replay" in sys.argv
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def run(tag, d):
    mesh = f"{tag}.msh"
    meta = solveconf.load_meta(mesh)
    g = meta["geometry_mm"]["groove"]
    if abs(g[0] - WIDTH) > 1e-6 or abs(g[1] - d) > 1e-6:
        raise RuntimeError(f"{tag}: asked for [{WIDTH},{d}], mesh says {g}")
    # 🔑 the assertion this whole run depends on: the slot must actually be a
    # separate attribute. Without it every groove_frac would read None, and a
    # missing measurement must never be mistaken for a measured zero.
    if meta["attributes"].get("groove") is None:
        raise RuntimeError(f"{tag}: --tag-groove did not produce a groove "
                           "attribute. The measurement this run exists for is "
                           "absent; do not read anything from it.")
    pl = meta["attributes"].get("plasma")
    c, meta, _ = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    idx = [e["Index"] for e in c["Domains"]["Postprocessing"]["Energy"]]
    if 80 not in idx:
        raise RuntimeError(f"{tag}: no Energy block on the groove (index 80). "
                           f"Have {idx}.")
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    print(f"  {tag}: groove {g} mm, attr {meta['attributes']['groove']}, "
          f"{meta['tets']:,} tets, energy indices {idx}", flush=True)
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
if not REPLAY:
    fac, _ = meshsweep.sweep(CASES, BASE)
    if not fac:
        sys.exit("mesh sweep failed")
    print(f"  ✅ all {len(CASES)} depths meshed at a COMMON size-factor {fac}",
          flush=True)

for (tag, _e), d in zip(CASES, DEPTHS):
    if not (REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists()):
        run(tag, d)

idx, got = results.sweep([t for t, _e in CASES], "r81",
                         extra=dict(width_mm=WIDTH, depths_mm=DEPTHS,
                                    tagged=True, sectors=5,
                                    azimuthal_caveat="N=5 conflates m1/m4/m6 "
                                                     "and m0/m5 — see R82"))
print(f"\n  wrote {len(got)} result files + r81.sweep.json")
print(f"  comparable: {idx['comparable']} — {idx['note']}")

print("\n" + "=" * 78)
print("ENERGY INSIDE THE SLOT, per mode  (the measurement, not a conclusion)")
for (tag, _e), d in zip(CASES, DEPTHS):
    r = results.load(tag)
    ms = sorted(r["modes"], key=lambda m: m["f"])
    print(f"\n  depth {d:.0f} mm — {len(ms)} modes")
    print(f"    {'f raw':>9}{'groove_frac':>13}{'pm/pe':>8}{'Q0':>9}{'eta':>7}"
          f"{'bin1':>8}{'bin2':>8}")
    for m in ms:
        gf = m.get("groove_frac")
        pmpe = m.get("pm_over_pe")
        print(f"    {m['f']:>9.4f}"
              f"{(f'{gf:.4f}' if gf is not None else 'NOT MEASURED'):>13}"
              f"{(f'{pmpe:.1f}' if pmpe else '—'):>8}{m['Q0']:>9,.0f}"
              f"{100*m['eta']:>6.1f}%{(m['b1'] or 0):>8.4f}"
              f"{(m['b2'] or 0):>8.4f}")
print("\n  next:  python3 evaluate.py --sweep r81")
print(flush=True)
