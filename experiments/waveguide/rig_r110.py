"""R110 — one mesh, two questions: the wall metal, and an attempt to FALSIFY R107.

Both are same-mesh (a boundary property and a volume material), so no meshing and
no mesh confound. This is the "battery" the orthogonal-questions idea asks for.

🔴 WHY THE WALL METAL. R58 adopted bare electropolished ALUMINIUM (3.5e7 S/m) on
optical grounds and wrote it to baselines. The Palace TEMPLATE kept SILVER
(6.3e7) and nothing ever bound the two, so EVERY SOLVE IN THIS RECORD HAS USED
SILVER WALLS and every absolute Q is high. Same failure as R101: a decision
recorded in one place and never connected to what consumes it.

✅ AND WE DO NOT NEED TO RE-SOLVE THE RECORD. Wall and dielectric losses add in
parallel and only the wall part scales:

        1/Q0(sigma) = A/sqrt(sigma) + 1/Qd

Two conductivities determine A and Qd; a third VALIDATES the law. Every silver Q
in the record then converts analytically, and eta follows from beta = Q0/Qext
because Qext is a coupling quantity and does not depend on wall loss.

🔑 WHY THE FILTER LADDER FALSIFIES R107. R107 claimed that removing the filter
makes TE011 and TM111 HYBRIDISE — bore-E 0.034% and 0.247% becoming 0.103% and
0.179%, averaging to exactly the parents' mean. That is the signature of a
two-mode avoided crossing, but it was inferred from TWO endpoints. An avoided
crossing makes a strong, falsifiable prediction about the PATH between them:

    ✅ if real   frequencies approach and REPEL smoothly; the two bore-E values
                 converge toward their common mean and swap character continuously
    🔴 if false  character jumps, or the modes cross without repelling, or the
                 bore-E values do not converge

R107's other claim — a sapphire filter costs 9.2% of Q — is tested the same way:
Q0(eps) must be SMOOTH. An erratic Q0(eps) means 9.2% was not a measurement.

⚠️ AND THE LADDER RUNS AT ALUMINIUM, which is the build. The dielectric/wall loss
balance shifts with wall metal, so the sapphire penalty may well be SMALLER at
3.5e7 than the 9.2% measured at silver. That is not a contradiction of R107; it
is R107 measured at the right operating point.

════════════════════════════════════════════════════════════════════════════════
CRITERIA, DECLARED BEFORE THE RUN
════════════════════════════════════════════════════════════════════════════════

1. WALL LAW — fit A and Qd from sigma = 6.3e7 and 3.5e7; predict Q0 at 1.0e7 and
   compare to the solved value. 🔴 If the prediction misses by more than 2%, the
   parallel-loss model is wrong and NOTHING may be rescaled analytically — the
   record would then genuinely need re-solving.

2. HYBRIDISATION — across the eps ladder, the two bore-H modes must show a smooth
   avoided crossing with bore-E converging toward the mean near closest approach.
   Report the minimum separation and the bore-E spread there.

3. SAPPHIRE PENALTY — Q0(eps) smooth and monotonic above the crossing. Report the
   quartz(3.78) -> sapphire(11.6) change AT ALUMINIUM, and state whether it
   differs from the 9.2% measured at silver.

4. 🔴 NO MODE LABELS NEAR THE CROSSING. Where the modes are within a few MHz they
   are mixtures and "TE011" does not name anything. Report the two bore-H modes
   sorted by FREQUENCY, with their bore-E, and let the reader see the swap. R59's
   tracker re-identified its target at every step and drew a clean curve through
   three different modes; a ladder through a crossing is exactly where that
   happens.

5. CASES-DIFFER (R101) — assert the written configs carry distinct eps / sigma
   before solving. One mesh means md5 cannot police this.
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
AG, AL, LO = 6.3e7, 3.5e7, 1.0e7
QZ = 3.78
WALL = [("r110wAg", QZ, AG), ("r110wAl", QZ, AL), ("r110wLo", QZ, LO)]
EPSL = [1.0, 1.4, 1.8, 2.2, 2.6, 3.0, 6.0, 8.5, 11.6]      # 3.78 = r110wAl
LADDER = [(f"r110e{str(e).replace('.', 'p')}", e, AL) for e in EPSL]
CASES = WALL + LADDER
BAND, STEP = (2.18, 2.44), 2e-4     # Q0 is omega*U/P (energy balance), so a
                                    # coarse step is safe — it is NOT a linewidth
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")


def build(tag, eps, sigma):
    m = solveconf.load_meta(MESH)
    br, pl = m["attributes"]["filter"], m["attributes"].get("plasma")
    c, m, _ = solveconf.driven(MESH, tag, BAND, step=STEP, order=1,
                               materials={pl: {"Permittivity": 1.0,
                                               "Permeability": 1.0}})
    hit = 0
    for mat in c["Domains"]["Materials"]:
        if mat["Attributes"] == [br]:
            mat["Permittivity"], mat["LossTan"] = eps, (0.0 if eps == 1.0
                                                        else 1.0e-4)
            hit += 1
    assert hit == 1, f"{tag}: {hit} filter materials"
    c["Boundaries"]["Conductivity"][0]["Conductivity"] = sigma
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    return eps, sigma


print(__doc__)
print("=" * 78, flush=True)
seen = {}
for tag, eps, sig in CASES:
    seen[tag] = build(tag, eps, sig)
    print(f"  {tag}: filter ε={eps:<5} wall σ={sig:.3g}", flush=True)
if len(set(seen.values())) != len(CASES):
    sys.exit("🔴 CRITERION 5 FAILED: configs are not distinct. NOT solving.")
print(f"  ✅ {len(CASES)} distinct configurations on ONE mesh\n", flush=True)

for tag, _e, _s in CASES:
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

results.sweep([t for t, _e, _s in CASES], "r110",
              extra=dict(question="wall-loss scaling law, and does the R107 "
                                  "avoided crossing survive a path test?",
                         mesh=MESH,
                         wall_cases={t: s for t, _e, s in WALL},
                         ladder={t: e for t, e, _s in LADDER},
                         al=AL, ag=AG, quartz_eps=QZ,
                         r107_sapphire_penalty_at_silver=9.2,
                         wall_law_gate_percent=2.0))
print("\n  ⚠️ NO VERDICT HERE — run evaluate.py r110", flush=True)
