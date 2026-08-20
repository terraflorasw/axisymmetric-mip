#!/usr/bin/env python3
"""R89 — is the R76/R78 disagreement PHYSICAL or NUMERICAL? (not an azimuth test)

R76 measured the cold interloper taking 46.5% of input power against TE011's
11.1%. R78/R79 measured 7.0% against 14.6%. I attributed the difference to loop
AZIMUTH and then retracted that as confounded. Re-examining before re-running:

🔑 AZIMUTH CANNOT MATTER, AND THE TEST SHOULD NOT VARY IT. Both meshes have
view_d = 0, chim_d = 0, feed_d = 0 — **the coupling loop is the ONLY azimuthal
feature in the model**. The cavity is otherwise axisymmetric, so rotating the loop
rotates the entire solution and changes no observable. A "loop azimuth sweep"
would measure nothing but mesh discretisation.

So the two runs differ in exactly two things that CAN matter:

    sectors      1  (R76 / wbarrel)      vs   5  (R78 / gq3)
    size-factor  1.06                    vs   1.00

and R54b already measured sector count alone moving TE011's Q by 6.9%.

⚠️ AND THE MODES MAY NOT BE THE SAME ONE: 2.4304 vs 2.4383 is 7.9 MHz apart.
Comparing "the interloper" across the two runs assumed an identification that was
never made.

DESIGN — one variable at a time, plus a null control that must return zero:

    az5a   sectors 5, loop-phi 36    the reference
    az5b   sectors 5, loop-phi 108   🔑 NULL CONTROL. 108 is another sector
                                     centre, so this is an EXACT symmetry
                                     operation. It must reproduce az5a
                                     identically. Whatever it does NOT reproduce
                                     is the numerical noise floor, and it
                                     calibrates how much of az5a-vs-az1 is real.
    az1    sectors 1, loop-phi 36    isolates sector count at a common
                                     size-factor

All three in ONE meshsweep, so the size-factor confound is removed by
construction rather than by argument.

⚠️ At sectors = 1 there is no azimuthal DFT — mode identity there rests on bore-H
/ bore-E and Q0 only. That is a limitation of the comparison, not a defect of the
run, and it is why az5b exists: it bounds the noise WITHIN the 5-sector family
where the full diagnostic set is available.

WHAT EACH OUTCOME MEANS, fixed before the run:

  az5b == az5a, and az1 differs
        -> the disagreement is SECTOR COUNT. R76's numbers are a 1-sector mesh
           artefact, R78's stand, and "never compare across sector counts"
           (R54b) extends from Q to mode competition.
  az5b != az5a
        -> the noise floor is larger than the effect being chased, and NEITHER
           run's competition ranking is trustworthy. Everything resting on
           "TE011 wins in band" would need re-deriving.
  all three agree
        -> the original 46.5% vs 7.0% came from the size-factor or the band, and
           the mesh is not the culprit.

This driver solves and records; evaluate.py concludes.
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
import results
import solveconf
import solver

BASE = ["--radius", "103.70", "--length", "88.53", "--order", "2",
        "--loop", "25.8,19.4,1.5,0.3", "--plasma", "4.5,8.5,-20,10",
        "--plasma-h", "1.0", "--mode-filter", "3"]
CASES = [("az5a", ["--sectors", "5", "--loop-phi", "36"]),
         ("az5b", ["--sectors", "5", "--loop-phi", "108"]),
         ("az1",  ["--sectors", "1", "--loop-phi", "36"])]
BAND, STEP = (2.30, 2.48), 5e-5      # matches R78's fltr3 window exactly
OFF = 0.02454
REPLAY = "--replay" in sys.argv
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def run(tag):
    mesh = f"{tag}.msh"
    meta = solveconf.load_meta(mesh)
    pl = meta["attributes"].get("plasma")
    c, meta, _ = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    print(f"  {tag}: sectors={meta['sectors']}, loop_phi={meta['loop_phi_deg']:.0f}"
          f", {meta['tets']:,} tets, sf {meta['size_factor']}", flush=True)
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
        sys.exit("mesh sweep failed — the size-factor confound must be removed "
                 "by construction, not argued away")
    print(f"  ✅ all 3 cases at a COMMON size-factor {fac} — the confound is gone",
          flush=True)

for tag, _e in CASES:
    if not (REPLAY and (pathlib.Path("postpro") / tag / "port-S.csv").exists()):
        run(tag)

idx, got = results.sweep([t for t, _e in CASES], "r89",
                         extra=dict(question="is the R76/R78 disagreement "
                                             "physical or numerical?",
                                    null_control="az5b must reproduce az5a "
                                                 "exactly — 108 deg is an exact "
                                                 "symmetry of a 5-sector mesh"))
print(f"\n  wrote {len(got)} result files + r89.sweep.json")

print("\n" + "=" * 78)
for tag, _e in CASES:
    r = results.load(tag)
    ms = sorted(r["modes"], key=lambda m: m["f"])
    print(f"\n  {tag}  ({r['sectors']} sector(s), phi={r['loop_phi_deg']:.0f}, "
          f"{r['tets']:,} tets)")
    print(f"    {'f raw':>9}{'f+off':>9}{'pm/pe':>8}{'Q0':>9}{'eta':>8}  band")
    for m in ms:
        fc = m["f"] + OFF
        pm = m.get("pm_over_pe")
        print(f"    {m['f']:>9.4f}{fc:>9.4f}"
              f"{(f'{pm:.1f}' if pm else '—'):>8}{m['Q0']:>9,.0f}"
              f"{100*m['eta']:>7.1f}%  {'IN ' if 2.400 < fc < 2.500 else 'out'}")

print("\n" + "=" * 78)
print("NULL CONTROL — az5b must reproduce az5a. Differences here are NOISE.")
a, b = results.load("az5a"), results.load("az5b")
for ma in sorted(a["modes"], key=lambda m: m["f"]):
    mb = min(b["modes"], key=lambda m: abs(m["f"] - ma["f"]))
    df = 1e3 * (mb["f"] - ma["f"])
    de = 100 * (mb["eta"] - ma["eta"])
    dq_ = 100 * (mb["Q0"] - ma["Q0"]) / ma["Q0"] if ma["Q0"] else float("nan")
    print(f"  {ma['f']:.4f} -> {mb['f']:.4f}   df {df:+6.2f} MHz   "
          f"d(eta) {de:+6.1f} pts   d(Q0) {dq_:+6.1f}%")
print("\n  next:  python3 evaluate.py --sweep r89")
print(flush=True)
