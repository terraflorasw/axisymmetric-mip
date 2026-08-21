# Next

State at the end of the session of 2026-08-21. Read `CONVENTIONS.md` first, then
`INSTRUMENT.md` and `HYPOTHESES.md`. This file is the queue only.

## Instance — ec2-18-119-10-220.us-east-2, up 2026-08-21 22:10Z

Second reclamation in one session. Recovery was `NOSYNC=1 ops/go ops/mount.sh`
and one line in `ops/env.sh`; the volume came back on the same UUID with
everything intact. **The recovery path is now exercised twice and works.**

Fixed while doing it, all §2 "the value must reach its consumer" faults:
- **`ops/env.sh` now EXPORTS `AMIP_HOST`.** `ops/go` sources it then exec's the
  target as a separate process, so without export the child saw nothing —
  `ops/remote.sh` died on "unbound variable" the first time it ran standalone.
- **`ops/remote.sh` sources `env.sh`** like every sibling. It had been relying
  on inheritance.
- **`ops/riglog.sh` is new.** `ops/getlog.sh` greps a `^A: `..`^B: ` block only
  the e1 rigs ever emitted, so for any other rig it returns SILENTLY EMPTY —
  indistinguishable from a rig producing nothing, and a waiter built on it never
  fires. It also asks directly whether the rig process is alive.
- **`run()` in `e0_solver_vs_math.py` now kills the process GROUP**
  (`start_new_session=True` + `os.killpg`). It was the last caller still using
  `proc.kill()`, which orphans the `prterun` → ranks tree.

## RUNNING — E0k2, the absolute-Q anchor

`e0k2_anchor.py`, 32 ranks. This is the fix for the E0k audit (FINDINGS
2026-08-21, *"E0k is the only driven data in the record"*). All four legs:

| E0k's fault | E0k2 |
|---|---|
| driven used SILVER 6.3e7 | aluminium, **bound from baselines.json**, refuses if absent |
| eigen counterpart was PEC (Q ≈ 2e9, noise) | eigen with the **same lossy wall** |
| ran D/L 2.343 — the geometry H1 **rejected** | H1 design point, **derived** from `physics.py` |
| |S11| never analysed | β, Q_L, Q₀ extracted; coupling branch from **phase** |

🔑 **What it buys**: Q₀ by two routes that share no machinery — the driven
LINEWIDTH versus the eigenvalue's imaginary part. Agreement anchors absolute Q
for the first time; disagreement is a bigger finding than the anchor.

🔑 **Mode identity comes from the field.** Both solves emit the SAME energy
regions in the SAME order (eigen_cfg and solveconf.driven number them
differently — that had to be forced), so the driven dip is matched to an
eigenmode by SIGNATURE. Validated offline on E0k's own data first: distance
0.0002 with an 18.7× margin. The analysis path was dry-run against E0k's CSV and
reproduced β=0.0673, Q_L=25,060, 97.6 kHz exactly before any compute was spent.

⚠️ Two declared outputs, not inputs: **β** (the loop is inherited from a=103.7
and NOT re-derived for a=88.0 — F3 fires if it loads too hard) and **which mode
the loop couples to** (a barrel loop is not guaranteed to pick TE011 over its
degenerate TM111 partner; Q settles it, and the anchor is labelled with the mode
it actually measured).

## H2b — 8 cases still queued at target 2.25

Unchanged from the analysis above: `anchor`, `exp-eta3`, `exp-eta4` re-solved
plus the 5 never run. `control-1.525` and `exp-eta1` are sound as they stand.

🔑 **`prod-narrow` now has a route that does not exist in the eigen world.**
Its failure is NLEPS divergence, and **a driven solve has no NLEPS** — it is a
sequence of well-conditioned linear solves. The comparability objection that
killed the GMRES→SuperLU idea does not apply the same way: a driven measurement
of the whole width pair is driven-vs-driven, not one case solved differently
from its own control. E0k2 is also the proof that the driven path works at this
design point.

⚠️ Wire `solvecost.diagnose()` into the rigs as a budget check before the next
H2b launch — `NLEPS_BUDGET = 1000` would have cut prod-narrow at 24% of its run.

## H2 — the groove, what is left

- **Scaling law unresolved.** `Z₀·tan(βd)` predicts 2.93×, slot volume fraction
  2.00×, measured **1.72×**. Two derivations agree with each other and disagree
  with the data; something saturates. The four-point exponent sweep settles it.
- **Product test**: does `gw·gd` govern? If `Z₀·tan(βd)` is right, prod-narrow
  should give **1.23×** the anchor and prod-wide **0.94×** — not equal.
- **Transfer test**: same η at D/L 1.35 / 1.525 / 1.90. This is the one that says
  whether the ratio survives adding a torch and viewports.
- Then a **width sweep for Q cost** at the chosen depth.

⚠️ Avoid slots narrower than ~3 mm: 2 mm forced 58,303 tets against ~33,000 and
stalled the linear solve past 248 KSP iterations.

## H3 — the loaded cavity. Highest value, and it blocks H4

Nothing trustworthy exists about what a plasma does to this cavity, and it gates
the ignition architecture, the tuning-loop bandwidth, and whether the groove's
50 MHz margin survives operation.

- Mode identity across a perturbation this large needs **continuation** — small
  ε steps where each shift is far below mode spacing — not endpoint pairing.
- Move **one** dielectric at a time. E1b moved torch and filter together and
  nothing it produced was attributable.
- Also here: β, Q_ext, S11 — driven coupling is entirely unmeasured.

## Smaller, ready to run

- **E0f2's TE121 outlier**: −2.345 MHz at geometric order 1, the only negative of
  11 modes. Probably the least-converged mode at the top of the window; one solve
  with more modes settles it.
- **Bore radius is the dominant coupling lever** (30× vs aspect ratio's 2×) and
  the 8.5 mm figure is inherited from the retired record. It is capped by gas
  flow (R², >20 slm is a killer). Nobody has chosen it deliberately — and the
  actual slm at 8.5 mm is not in the record.
- **`run()` in `e0_solver_vs_math.py`** still uses `proc.kill()`, which orphans
  the `prterun` tree. `e0l_scaling.py` was fixed with
  `start_new_session=True` + `os.killpg`; `run()` should match.
- **DEPLOY.md still names the old host.** Update once the new one exists.

## Uncommitted

Everything from this session is uncommitted, including `CONVENTIONS.md`,
`INSTRUMENT.md`, `HYPOTHESES.md`, this file, the `ops/` additions, and the E1
deletions.
