#!/usr/bin/env python3
"""R83 — does COLD azimuthal contamination survive into LIT power deposition?

This replaces C1, which was withdrawn as a category error. C1 rejected ten filter
geometries on "TE011 azimuthal purity <= quartz" — a criterion that is

    a property of the RESONATOR   when purity is a property of the DRIVE
    measured COLD                 when the consequence is a LIT one
    integrated over the WHOLE     when what matters is the plasma torus
      CAVITY
    in STORED ENERGY              when the physics is integral sigma|E|^2 dphi

R83 measures the thing itself: the plasma toroid is split into azimuthal sectors
(--plasma-sectors, attributes 20..24, one Energy index each) and the LIT run
reports deposited power per unit azimuth. Deposited power is (sigma/eps0)*E_elec
— the relation R74 validated when its decomposition closed to 0.22 points — so at
one sigma across the torus the sector fractions ARE the deposition profile.

🔑 SCORED AS A RATIO, not against an absolute from another configuration. C1's
threshold was quartz's own number carried onto grooves that do not share its
losses. Here the metric is within-configuration and dimensionless:

    non-uniformity = (P_max - P_min) / P_mean   across the sectors

⚠️ AND THE sigma AXIS IS DIMENSIONLESS TOO. sigma = 30 S/m is an absolute; the
scale-free coordinate is SKIN DEPTH OVER PLASMA THICKNESS, delta/t, with
t = 4 mm (plasma.region 4.5-8.5). Re-reading R74 in it shows the eta minimum
sits at delta/t ~ 1, which is the physics: skin depth comparable to the absorber.

    sigma = 1    delta = 10.19 mm   delta/t = 2.55   TRANSPARENT — volume absorber
    sigma = 100  delta =  1.02 mm   delta/t = 0.25   OPAQUE — surface/shell

🔑 THE ANSWER PROBABLY DEPENDS ON THIS, which is why one sigma would not do:
a transparent plasma follows the vacuum field, so cold contamination should show
through; an opaque one screens, and may symmetrise the deposition regardless of
what the cold cavity looked like. Running one point would give an answer that
does not generalise, and this project has already published two of those.

CASES — two configurations spanning 10x in cold contamination, at both regimes:

    bare      cold TE011 bin1 = 0.2443   the extreme. A CONTROL, not a candidate:
                                         bare reverts to the chi'01 = chi11
                                         degeneracy and is not a design option.
    quartz 3  cold TE011 bin1 = 0.0263   the incumbent.

    x sigma = 1 and 100.  Four lit solves.

⚠️ 15 mm groove and any near-degenerate geometry are EXCLUDED — R81 showed a
0.16% mesh change swings pm/pe 178% there. The groove at 21 mm is deliberately
NOT in this run: if bare-vs-quartz shows no sensitivity, the candidate is moot
and one more solve would have been wasted. Cheap decisive test first.

WHAT EACH OUTCOME MEANS, fixed before the run:

  non-uniformity flat across a 10x span in cold bin1
        -> 🔑 C1 IS DEAD. The groove programme was optimising a quantity with no
           consequence, and sc06 is already adequate on symmetry grounds.
  non-uniformity tracks cold bin1
        -> C1 had a real referent. Replace it with THIS metric, which is an
           outcome, in the right region, in the right state, as a ratio.
  flat at one delta/t and not the other
        -> the criterion is regime-dependent and must be quoted with delta/t.

⚠️ What this cannot say: what uniformity the INSTRUMENT needs. That is an
analytical-chemistry spec, not an EM one. R83 answers the sensitivity question,
which is the gate — if deposition does not respond to a 10x change in cold
contamination, the spec never has to be argued about.

This driver solves and records. evaluate.py concludes.
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
import results
import solveconf
import solver

PLASMA = "4.5,8.5,-20,10"
T_PLASMA = 4.0                      # mm, radial thickness 4.5 -> 8.5
BASE = ["--radius", "103.70", "--length", "88.53", "--sectors", "5",
        "--loop-phi", "36", "--order", "2", "--loop", "25.8,19.4,1.5,0.3",
        "--plasma", PLASMA, "--plasma-h", "1.0", "--plasma-sectors"]
MESHES = [("p83bare", ["--mode-filter", "0"]),
          ("p83q3", ["--mode-filter", "3"]),
          # R85: the surviving groove candidate, cold bin1 0.0572 — between
          # quartz (0.0263) and bare (0.2443). ⚠️ Its mesh was built in a
          # SEPARATE call at a FORCED --size-factor 1.00, not by this sweep.
          # R27 forbids comparing across sweeps because the factor can silently
          # differ; here it was checked explicitly (all three at 1.00) rather
          # than guaranteed by construction. Run with --replay so the two
          # original cases are not re-solved onto a different mesh.
          ("p83g21", ["--mode-filter", "0", "--groove", "3,21"])]
SIGMAS = [1.0, 100.0]
BAND, STEP = (2.36, 2.50), 2.5e-4    # lit features are >= 3.9 MHz wide
COLD_BIN1 = {"p83bare": 0.2443, "p83q3": 0.0263, "p83g21": 0.0572}
REPLAY = "--replay" in sys.argv
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def skin_mm(sig, f=2.44e9):
    return 1e3 * math.sqrt(2.0 / (2 * math.pi * f * 4e-7 * math.pi * sig))


def tag_of(mesh, sig):
    """🔴 The first version was `str(sig).replace('.','p').rstrip('p0')`.

    rstrip takes a CHARACTER SET, not a suffix: '100p0'.rstrip('p0') strips every
    trailing p and 0 and returns '1'. sigma = 1 and sigma = 100 both became
    '_s1', so four solves wrote into two directories and the sigma=100 runs
    silently overwrote the sigma=1 runs. The run completed and printed plausible
    numbers — R32's tag collision, in a new spelling.

    `%g` on an int-valued float gives '1' and '100' with no separator to strip.
    """
    return f"{mesh}_s{sig:g}".replace(".", "p")


def run(mesh, sig, tag):
    meta = solveconf.load_meta(f"{mesh}.msh")
    sec = meta["attributes"].get("plasma_sectors")
    if not sec:
        raise RuntimeError(f"{mesh}: no plasma_sectors attribute. The whole "
                           "measurement is per-sector deposition; without it "
                           "this run has nothing to report.")
    mats = {a: {"Permittivity": 1.0, "Permeability": 1.0, "Conductivity": sig}
            for a in sec}
    c, meta, _ = solveconf.driven(f"{mesh}.msh", tag, BAND, step=STEP, order=1,
                                  materials=mats)
    idx = [e["Index"] for e in c["Domains"]["Postprocessing"]["Energy"]]
    missing = [a for a in sec if a not in idx]
    if missing:
        raise RuntimeError(f"{tag}: Energy blocks missing for {missing}")
    got = [m for m in c["Domains"]["Materials"] if m.get("Conductivity") == sig]
    if len(got) != len(sec):
        raise RuntimeError(f"{tag}: conductivity on {len(got)} of {len(sec)} "
                           "plasma sectors — an unlit wedge would read as zero "
                           "deposition and look like perfect screening")
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    d = skin_mm(sig)
    print(f"  {tag}: sigma={sig:g}, delta={d:.2f} mm, delta/t={d/T_PLASMA:.2f}, "
          f"{len(sec)} plasma sectors, {meta['tets']:,} tets", flush=True)
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
    fac, _ = meshsweep.sweep(MESHES, BASE)
    if not fac:
        sys.exit("mesh sweep failed")
    print(f"  ✅ both configurations meshed at a COMMON size-factor {fac}",
          flush=True)

# 🔑 A tag collision is silent — two cases write one directory and the second
# wins. Prove the mapping is injective BEFORE solving anything.
_want = [(tag_of(m, s), m, s) for m, _e in MESHES for s in SIGMAS]
_names = [t for t, _m, _s in _want]
if len(set(_names)) != len(_names):
    dupes = sorted({n for n in _names if _names.count(n) > 1})
    sys.exit(f"🔴 tag collision: {dupes} — {len(_names)} cases map to "
             f"{len(set(_names))} tags. Cases would overwrite each other.")

tags = []
for mesh, _e in MESHES:
    for sig in SIGMAS:
        t = tag_of(mesh, sig)
        tags.append((t, mesh, sig))
        if not (REPLAY and (pathlib.Path("postpro") / t / "port-S.csv").exists()):
            run(mesh, sig, t)

idx, got = results.sweep([t for t, _m, _s in tags], "r83",
                         extra=dict(sigmas=SIGMAS, t_plasma_mm=T_PLASMA,
                                    delta_over_t={s: round(skin_mm(s) / T_PLASMA, 3)
                                                  for s in SIGMAS},
                                    cold_bin1=COLD_BIN1,
                                    replaces="C1 (withdrawn, FINDINGS entry 126)"))
print(f"\n  wrote {len(got)} result files + r83.sweep.json")

print("\n" + "=" * 78)
print("AZIMUTHAL DEPOSITION IN THE PLASMA, at each run's max-eta point")
print(f"{'case':>14}{'d/t':>7}{'cold bin1':>11}{'eta':>8}"
      f"{'per-sector deposition':>34}{'non-unif':>10}")
for t, mesh, sig in tags:
    r = results.load(t)
    ms = [m for m in r["modes"] if m.get("plasma_sectors")]
    if not ms:
        print(f"{t:>14}  🔴 no per-sector data")
        continue
    m = max(ms, key=lambda x: x["eta"])
    ps = m["plasma_sectors"]
    tot = sum(ps)
    frac = [v / tot for v in ps] if tot else [0] * len(ps)
    nu = (max(frac) - min(frac)) / (1.0 / len(frac)) if tot else float("nan")
    print(f"{t:>14}{skin_mm(sig)/T_PLASMA:>7.2f}{COLD_BIN1[mesh]:>11.4f}"
          f"{100*m['eta']:>7.1f}%   " + " ".join(f"{100*f:5.1f}%" for f in frac)
          + f"{nu:>9.3f}")
print("\n  non-unif = (max - min)/mean over the sectors. 0 = perfectly "
      "axisymmetric deposition.")
print("  ⚠️ loop is at phi = 36 deg, the centre of sector 1.")
print("\n  next:  python3 evaluate.py --sweep r83")
print(flush=True)
