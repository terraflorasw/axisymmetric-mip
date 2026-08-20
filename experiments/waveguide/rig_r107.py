"""R107 — the mode filter, measured SAME-MESH. Three materials, one mesh, no meshing.

🔑 WHY THIS RUN EXISTS. The filter's Q cost is quoted at 5.6% (R39) and the
groove's gain over it at 6.0% (R54). Both were measured ACROSS MESHES. The known
cross-mesh Q reproducibility on the SAME geometry is 6.9%
(reproducibility.q_across_sector_counts), and 40% when the skin depth is
under-resolved. 🔴 THE ENTIRE FILTER/GROOVE Q TRADE SITS BELOW THE NOISE IT WAS
MEASURED AGAINST. Frequencies were fine — 45 MHz of separation clears the 1.3-3.3
MHz frequency floor easily — but Q is far more mesh-sensitive than frequency and
nobody carried that through.

✅ THE FIX COSTS NOTHING. The filter is attribute 8, a SEPARATELY TAGGED VOLUME of
fused quartz. A quartz annulus with eps = 1.0 and tand = 0 IS AIR, exactly. So
"filter present" and "filter absent" are two MATERIAL states of ONE mesh, not two
geometries. Mesh error is common-mode and cancels; the solver is deterministic
(R105: 0.0000 MHz on a duplicated mesh), so the difference is exact.

    A  qz    eps 3.78,  tand 1.0e-4   fused quartz — the current design
    B  off   eps 1.0,   tand 0.0      no filter at all, EXACTLY
    C  sa    eps 11.6,  tand 3.5e-5   sapphire — free to ask, since the torch is
                                      already sapphire and its tand is 3x lower

🔑 C IS A REAL HARDWARE QUESTION, NOT A CONTROL. Higher eps perturbs MORE (better
separation) while lower tand costs LESS Q. If both move the right way, a sapphire
filter is strictly better than a quartz one and the part should change.

════════════════════════════════════════════════════════════════════════════════
CRITERIA, DECLARED BEFORE THE RUN
════════════════════════════════════════════════════════════════════════════════

1. PRIMARY — Q0(TE011) for each material, same mesh. The claim under test is that
   the quartz filter costs 5.6% of Q. Same-mesh means NO meshing noise; what
   remains is discretisation bias, which is common to all three and cancels in
   the ratio to first order.

2. SEPARATION — f(TE011) - f(TM111) for each. Against
   effect.filter_te011_tm111_separation = 45 MHz, itself a cross-mesh number.

3. 🔴 DEGENERACY GUARD, AND IT MAY VOID CASE B. TE011 and TM111 are EXACTLY
   degenerate in an ideal cylinder (chi'01 = chi11 = 3.8317). The filter exists
   to break that. With the filter OFF they may land within a few linewidths, and
   the record is explicit that NOTHING IS MEASURABLE THERE — a 0.16% mesh change
   swings pm/pe by 178% (reproducibility.degeneracy_sensitivity). If |df| is
   under 3 cold linewidths (~7 MHz), case B's Q and separation are NOT
   MEASUREMENTS and must be reported as void, not as numbers. That is a
   foreseeable outcome, not a failure: "the unfiltered cavity is unmeasurable" is
   itself the argument for the filter.

4. IDENTITY — both TE011 and TM111 are bore-H dominant, so bore-H alone cannot
   separate them. The discriminator is bore-E: R99 measured TE011 at 0.034% and
   the TM111 candidate at 0.247%, a 7x gap. TE011 = lowest bore-E; TM111 = the
   next bore-H mode below it.

5. CASES-DIFFER GATE (R101) — assert the three written configs actually carry
   eps 3.78 / 1.0 / 11.6 on attribute 8 before solving. One mesh means the usual
   md5 check cannot help here; the config IS the independent variable.

⚠️ SCOPE. This measures the filter as a DIELECTRIC ANNULUS. The groove
alternative is a geometry change and CANNOT be done same-mesh — that comparison
keeps its cross-mesh noise and its 6.9% Q floor.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import results
import solveconf
import solver

MESH = "s99sa.msh"
CASES = [("r107qz", 3.78, 1.0e-4), ("r107off", 1.0, 0.0), ("r107sa", 11.6, 3.5e-5)]
BAND, STEP = (2.30, 2.46), 5e-5
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def build(tag, eps, tand):
    m = solveconf.load_meta(MESH)
    br = m["attributes"].get("filter")
    if br is None:
        sys.exit(f"{MESH} has no brake/filter attribute — nothing to switch")
    pl = m["attributes"].get("plasma")
    c, m, _ = solveconf.driven(MESH, tag, BAND, step=STEP, order=1,
                               materials={pl: {"Permittivity": 1.0,
                                               "Permeability": 1.0}})
    # override the filter's material IN PLACE — this is the independent variable
    hit = 0
    for mat in c["Domains"]["Materials"]:
        if mat["Attributes"] == [br]:
            mat["Permittivity"], mat["LossTan"] = eps, tand
            hit += 1
    assert hit == 1, f"{tag}: {hit} materials on attribute {br}, expected 1"
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    return br


print(__doc__)
print("=" * 78, flush=True)
br = None
for tag, eps, tand in CASES:
    br = build(tag, eps, tand)

# 🔴 CRITERION 5, before any solve. One mesh means md5 cannot police this run —
# the CONFIG is the independent variable, so the config is what must be checked.
seen = {}
for tag, eps, _t in CASES:
    c = json.loads(pathlib.Path(f"{tag}.json").read_text())
    got = [m for m in c["Domains"]["Materials"] if m["Attributes"] == [br]][0]
    seen[tag] = (got["Permittivity"], got["LossTan"])
    print(f"  {tag}: attribute {br} eps={got['Permittivity']} "
          f"tand={got['LossTan']}", flush=True)
if len({v[0] for v in seen.values()}) != len(CASES):
    sys.exit("🔴 CRITERION 5 FAILED: the three configs do not carry distinct "
             "permittivities. The independent variable was not applied. "
             "NOT solving.")
print("  ✅ three distinct filter materials on one mesh — mesh error is "
      "common-mode\n", flush=True)

for tag, _e, _t in CASES:
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
    print(f"  {tag} solved in {dt:.0f}s", flush=True)

results.sweep([t for t, _e, _t in CASES], "r107",
              extra=dict(question="what does the mode filter actually cost and "
                                  "buy, measured same-mesh?",
                         mesh=MESH, filter_attribute=br,
                         materials={t: [e, d] for t, e, d in CASES},
                         q_claim_percent=5.6,
                         separation_claim_mhz=45.0,
                         degeneracy_guard_mhz=7.0,
                         note="same mesh for all three, so meshing noise is "
                              "common-mode; groove comparison is geometry and "
                              "cannot be done this way"))
print("\n  ⚠️ NO VERDICT HERE — run evaluate.py r107", flush=True)
