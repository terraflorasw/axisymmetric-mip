# resonance — the AMIP cavity, re-derived under verification AND falsification

**Started 2026-08-20.** This is not a continuation of `../waveguide`. That
programme's record stands as an evidence trail and a failure catalogue; the only
files that transferred are the harness and `METHODOLOGY.md`.

## The three rules

**1. Physics is the anchor. There is no verified instrument.**
`physics.py` holds closed forms and contains no simulation. A solver is never
"verified" — it agrees or disagrees with physics on particular cases. Every
number produced by an instrument is checked against something outside it.

**2. Every result carries a VERIFICATION and a FALSIFICATION.**

| | |
|---|---|
| **V** | what must this agree with, from outside the instrument? A closed form, an exact degeneracy, a conservation law, or a quantity with analytically zero sensitivity |
| **F** | what measurement would show this is WRONG? Run it. A result with no F is an assertion |

Both are declared **before** the run, in the driver's docstring. A result with
only a V is a coincidence waiting to happen; a result with only an F is
unanchored.

**3. Work backwards from LOD.** `LOD ≈ 3·σ_background / sensitivity`. Everything
the cavity does reaches it through exactly two doors — **delivered power** and
**the optical path**. A question that cannot name its door is not a design input.

## Why the previous programme is not continued

Its register grew by generating its own questions: R99→R101→R103→R105→R106→
R107→R109→R110→R111→R112→R113, each opened by the previous result's
uncertainty. An inward-facing loop with no external anchor can only expand.
`CONSOLIDATION.md` in `../waveguide` records what survived the audit and what
did not.

⚠️ **Not everything there was wrong** — frequencies, same-mesh differences, mode
character and **lit η** all survive. But the explanatory layer does not, and no
number is imported here without passing V and F again.

## Layout

| | |
|---|---|
| `physics.py` | closed forms. **The anchor.** Self-tests must pass |
| `METHODOLOGY.md` | how gmsh and Palace lie. Read before designing any run |
| `PLAN.md` | the fixed experiment list. **It does not grow** |
| `baselines.json` | starts empty. An entry needs `verification` and `falsification` fields |
| `FINDINGS.md` | the new trail, append-only |
| harness | `geometry.py`, `solveconf.py`, `results.py`, `evaluate.py`, … |

## The standing prohibition

**No new register items during consolidation.** Surprises are parked in
`PLAN.md` §Parked. They do not spawn runs. The previous programme's failure mode
was not wrong answers — it was an expanding question set.
