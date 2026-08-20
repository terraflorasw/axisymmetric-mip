"""R103 — re-derive dTE011/dL, and find out WHY it disagrees with the record.

R99 measured -10.4 MHz/mm from TWO points (5.85 MHz over 0.56 mm). The record
says -13.06 (R46, three lengths, size-factor 0.96). A 20% disagreement matters
because BOTH of these rest on it:

    tune.settable_range   23 MHz = 16.4 lit drift + 5.1 machining tolerance
    the machining budget  L tolerance is this coefficient against ISM headroom

⚠️ A 2-POINT SLOPE CANNOT DETECT ITS OWN FAILURE. It has no residual, no
linearity check, and no way to tell an outlier from a trend. That alone justifies
re-taking it, independently of which number turns out right.

THREE CANDIDATE CAUSES, and the design separates two of them:

  (a) the VIEWPORT + LIGHT TRAP, which this mesh family has and R46's did not
  (b) SAPPHIRE vs quartz changing the L-derivative
  (c) 2-point noise, or an error in R46

LADDER A — sapphire, viewport+trap ON (the product): 5 lengths over 2 mm.
           Gives the coefficient we will actually use, plus a linearity residual.
LADDER B — sapphire, viewport and trap OFF: 3 lengths over the same span.
           A vs B isolates cause (a). If B lands near -13.06, the optical
           features are the explanation and R46 was right for its own geometry.

🔑 THE 2-POINT PAIR IS RE-MEASURED INSIDE LADDER A. 87.97 and 88.53 are both
ladder points, so the pairwise slope R99 reported can be compared against the
5-point fit ON THE SAME DATA. If they disagree, R99's pair was an outlier and
cause (c) is live.

════════════════════════════════════════════════════════════════════════════════
CRITERIA, DECLARED BEFORE THE RUN
════════════════════════════════════════════════════════════════════════════════

1. PRIMARY — dTE011/dL for the product, as a 5-point least-squares fit with its
   residual quoted. NOT a two-point difference. The residual is the result's
   error bar and must be reported even if it is small.

2. LINEARITY — max |residual| must be under 0.5 MHz across the 2 mm span. R46
   got three independent L_target values agreeing to 0.07 mm, which at 13 MHz/mm
   is ~0.9 MHz; under 0.5 MHz is therefore a comparable-or-better standard. If
   the residual exceeds it, the coefficient is not a constant over 2 mm and
   quoting any single number is wrong.

3. ATTRIBUTION — |slope_A - slope_B| against the A-vs-record gap. If B ~ -13.06
   the viewport+trap explains it; if B ~ -10.4 the optical features are NOT the
   cause and (b) or (c) is.

4. IDENTITY — TE011 is the bore-H mode with the LOWEST bore-E at every length.
   🔴 If the lowest-bore-E mode is not also a high-bore-H mode at any point, the
   tracker has hopped and that point is discarded, not fitted. R59's tracker
   re-identified its target at every depth and produced a clean-looking curve
   through three different modes.

⚠️ Band 2.36-2.44 follows TE011 across the whole span (2 mm x ~13 MHz/mm = 26 MHz
   of travel) with margin. It does NOT contain TM020 at the sapphire point
   (2.182), so TM020 is unavailable as a control here — the 5-point residual is
   the control instead.
"""
import json
import pathlib
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import meshsweep
import results
import solveconf
import solver

BASE = ["--radius", "103.70", "--order", "2", "--sectors", "1",
        "--loop", "25.8,19.4,1.5,0.3", "--loop-phi", "36",
        "--plasma", "4.5,8.5,-20,10", "--plasma-h", "1.0", "--mode-filter", "3"]
LA = [87.00, 87.50, 87.97, 88.53, 89.00]      # ladder A: product family
LB = [87.00, 87.97, 89.00]                    # ladder B: no viewport, no trap
CASES = ([(f"L3a{str(L).replace('.','p')}", ["--length", f"{L:.2f}"]) for L in LA]
         + [(f"L3b{str(L).replace('.','p')}",
             ["--length", f"{L:.2f}", "--viewport", "0", "--trap", "0,0,0"])
            for L in LB])
BAND, STEP = (2.36, 2.44), 5e-5
PALACE = str(pathlib.Path.home() / ".local/opt/palace/bin/palace")

# tags must be injective — 'rstrip' style collapsing has burned this record once
assert len({t for t, _ in CASES}) == len(CASES), "tag collision"


def run(tag):
    mesh = f"{tag}.msh"
    meta = solveconf.load_meta(mesh)
    pl = meta["attributes"].get("plasma")
    c, meta, _ = solveconf.driven(
        mesh, tag, BAND, step=STEP, order=1,
        materials={pl: {"Permittivity": 1.0, "Permeability": 1.0}})
    pathlib.Path(f"{tag}.json").write_text(json.dumps(c, indent=2))
    g = meta["geometry_mm"]
    got = [m for m in c["Domains"]["Materials"]
           if m["Attributes"] == [meta["attributes"]["torch"]]]
    assert len(got) == 1 and abs(got[0]["Permittivity"]
                                 - g["torch_material"][0]) < 1e-9, f"{tag}: R101"
    print(f"  {tag}: L={g['length']} view={g.get('viewport')} "
          f"trap={g.get('trap')} eps={g['torch_material'][0]} "
          f"{meta['tets']:,} tets", flush=True)
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
fac, _ = meshsweep.sweep(CASES, BASE)
if not fac:
    sys.exit("mesh sweep failed — a size-factor confound must be removed by "
             "construction, not argued away")
print(f"  ✅ all {len(CASES)} cases at a COMMON size-factor {fac}", flush=True)
for tag, _e in CASES:
    run(tag)
results.sweep([t for t, _e in CASES], "r103",
              extra=dict(question="what is dTE011/dL in the product family, and "
                                  "does the viewport+trap explain the 20% gap "
                                  "against R46's -13.06?",
                         ladder_a=LA, ladder_b=LB,
                         linearity_gate_mhz=0.5,
                         identity="TE011 = highest bore-H among the lowest "
                                  "bore-E; discard a point if they disagree"))
print("\n  ⚠️ NO VERDICT HERE — run evaluate.py r103", flush=True)
