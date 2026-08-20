"""R105 — characterise the per-mesh frequency scatter that bounds this record.

R103 found σ ≈ 2 MHz by accident, as the residual of a length ladder. That number
is the FLOOR on every frequency difference this harness reports, and several
closed results are differences of that order — so it deserves a measurement
rather than a by-product.

🔑 TWO THINGS ARE CURRENTLY CONFLATED, AND THEY BEHAVE OPPOSITELY:

  CONVERGENCE BIAS   systematic, shrinks with refinement, LARGELY CANCELS in a
                     difference between two similar meshes. Already handled by
                     the `frame` field (te011 raw->converged is +24.54 MHz).
  REALISATION NOISE  random per mesh, does NOT cancel in a difference, and is
                     what actually limits us. Never measured.

Calling both "mesh error" is why a 2 MHz scatter could sit unexamined next to a
24 MHz offset that is carefully tracked.

TWO LADDERS, each isolating one:

  LADDER C — convergence.  IDENTICAL geometry, five size factors.
      Geometry is byte-for-byte the same input, so EVERY difference is numerical.
      f(h) has a smooth trend; the trend is the bias, the residual is the noise.
      ⚠️ This deliberately VIOLATES the common-size-factor rule that meshsweep
      enforces. Here the size factor IS the independent variable, so the usual
      confound is the measurement. Meshes are therefore built directly.

  LADDER N — realisation null.  FIXED size factor, L perturbed by ±0.0075 mm.
      True frequency change across the whole span is 0.015 mm x 11.89 MHz/mm =
      0.18 MHz (R103), roughly ten times below the scatter being measured. So
      anything larger than 0.18 MHz is the mesher laying elements out
      differently, and nothing else.

════════════════════════════════════════════════════════════════════════════════
CRITERIA, DECLARED BEFORE THE RUN
════════════════════════════════════════════════════════════════════════════════

1. PRIMARY — σ_realisation from ladder N, as the RMS about its (known, 0.18 MHz)
   trend. This is the number that belongs in baselines as the difference floor.

2. CROSS-CHECK — σ from ladder C's residual about its fitted convergence trend
   must agree with σ from ladder N. Two independent routes; if they disagree by
   more than 2x, neither is characterised and the result is that we do not know.

3. 🔴 CASES-DIFFER GATE (the R101 lesson, applied before anything is read).
   Ladder N's meshes must ACTUALLY DIFFER — distinct tet counts or distinct
   md5s. A 7.5 micron change against ~1.5 mm elements might produce an
   IDENTICAL mesh, in which case ladder N measures zero and reports σ = 0, which
   would be false and flattering. If they do not differ, ladder N is DISCARDED,
   not interpreted.

4. CONVERGENCE DIRECTION — f must rise monotonically as the mesh refines
   (coarse meshes sit low; raw-order1 is 24.54 MHz BELOW converged for TE011).
   🔴 A non-monotonic ladder C means the trend is buried in noise, and then
   criterion 2's fit is meaningless and only ladder N stands.

5. CONSEQUENCE — report which recorded differences are within 2σ of this floor.
   R104 (15.0 vs 5.8 MHz) is the first candidate and may not need explaining.

⚠️ NOT MEASURED HERE: whether σ depends on size factor, geometry complexity, or
   proximity to a degeneracy. The record already notes a 0.16% mesh change
   swinging pm/pe by 178% NEAR A DEGENERACY — this run is far from one, so the
   number it produces is a floor for well-separated modes and must not be quoted
   for anything sitting on top of the TE011/TM111 crossing.
"""
import hashlib
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import results
import solveconf
import solver

GEO = ["--radius", "103.70", "--order", "2", "--sectors", "1",
       "--loop", "25.8,19.4,1.5,0.3", "--loop-phi", "36",
       "--plasma", "4.5,8.5,-20,10", "--plasma-h", "1.0", "--mode-filter", "3"]
# R105a: sf=1.15 FAILED high-order optimisation ("Failed to reach critical
# value in pass 1 for measure(s): ScaledJac"). Not every size factor yields a
# valid curved mesh for this geometry — which is exactly why meshsweep.FACTORS
# is a CANDIDATE LIST that gets tried in order, and ladder C bypasses it by
# design. Candidates below are meshsweep's known-good set plus two extremes;
# failures are SKIPPED AND REPORTED, not fatal, because "which factors are
# constructible" is itself part of the mesh-variability picture.
SF = [1.20, 1.06, 1.00, 0.96, 0.90, 0.85]           # ladder C, L fixed
LN = [88.5225, 88.5262, 88.5300, 88.5338, 88.5375]  # ladder N, sf fixed 0.96
L0, SF0 = 88.53, 0.96
BAND, STEP = (2.32, 2.42), 5e-5
PY = sys.executable
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def mesh(tag, length, sf):
    out = f"{tag}.msh"
    cmd = [PY, "geometry.py", "--out", out, "--length", f"{length:.4f}",
           "--size-factor", f"{sf:.4f}"] + GEO
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode or not pathlib.Path(out).exists():
        raise RuntimeError(f"{tag}: mesh failed — {r.stdout[-300:]}{r.stderr[-300:]}")
    m = solveconf.load_meta(out)
    h = hashlib.md5(pathlib.Path(out).read_bytes()).hexdigest()[:10]
    print(f"  {tag}: L={length:.4f} sf={sf:.4f} {m['tets']:>7,} tets md5 {h}",
          flush=True)
    return m["tets"], h


def run(tag):
    m = solveconf.load_meta(f"{tag}.msh")
    pl = m["attributes"].get("plasma")
    c, m, _ = solveconf.driven(f"{tag}.msh", tag, BAND, step=STEP, order=1,
                               materials={pl: {"Permittivity": 1.0,
                                               "Permeability": 1.0}})
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
    print(f"    solved in {dt:.0f}s", flush=True)


print(__doc__)
print("=" * 78, flush=True)

print("LADDER C — identical geometry, varying size factor", flush=True)
cinfo, cfail = {}, []
for sf in SF:
    t = f"r105c{str(sf).replace('.', 'p')}"
    try:
        cinfo[t] = mesh(t, L0, sf) + (sf,)
    except RuntimeError as e:
        cfail.append(sf)
        print(f"  ⚠️ sf={sf}: mesh failed, skipped — {str(e)[:90]}", flush=True)
if cfail:
    print(f"  ⚠️ ladder C lost {len(cfail)} factor(s): {cfail}", flush=True)
if len(cinfo) < 3:
    sys.exit(f"ladder C has {len(cinfo)} usable factors — too few to fit a "
             "convergence trend. Widen the candidate list.")

print("\nLADDER N — fixed size factor, 7.5 micron length perturbations",
      flush=True)
ninfo = {}
for L in LN:
    t = f"r105n{str(L).replace('.', 'p')}"
    ninfo[t] = mesh(t, L, SF0) + (L,)

# 🔴 CRITERION 3, BEFORE ANY SOLVE. Do not spend an hour measuring zero.
tets = {v[0] for v in ninfo.values()}
hashes = {v[1] for v in ninfo.values()}
print(f"\n  ladder N distinct tet counts: {len(tets)}/{len(ninfo)}; "
      f"distinct md5: {len(hashes)}/{len(ninfo)}", flush=True)
if len(hashes) == 1:
    sys.exit("🔴 CRITERION 3 FAILED: every ladder-N mesh is byte-identical. A "
             "7.5 micron perturbation did not change the mesh, so ladder N "
             "would measure sigma = 0 — which is an artefact, not a result. "
             "Widen the perturbation and re-run. NOT solving.")

print("\nSOLVING", flush=True)
tags = list(cinfo) + list(ninfo)
for t in tags:
    run(t)

results.sweep(tags, "r105",
              extra=dict(question="how much does a solved frequency move when "
                                  "only the MESH changes?",
                         ladder_c={t: v[2] for t, v in cinfo.items()},
                         ladder_n={t: v[2] for t, v in ninfo.items()},
                         tets={t: v[0] for t, v in {**cinfo, **ninfo}.items()},
                         md5={t: v[1] for t, v in {**cinfo, **ninfo}.items()},
                         n_true_span_mhz=0.18,
                         dfdL=-11.89,
                         ladder_c_failed=cfail))
print("\n  ⚠️ NO VERDICT HERE — run evaluate.py r105", flush=True)
