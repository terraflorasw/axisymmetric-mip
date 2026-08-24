# Next

Read **`KNOWN.md`** first — one page, everything established, and the index of
every document. Then **`PLAN.md`** — the FIXED experiment list (E0–E4), which
**does not grow**, and whose *Parked* section is where surprises go: they are
recorded so they are not lost, and **they do not spawn runs**. Then
`CONVENTIONS.md`, then `INSTRUMENT.md` / `HYPOTHESES.md` / `OPTIMIZER.md`.
**This file is the queue only** — it holds no measurements.
⚠️ `FINDINGS.md` is the ARCHIVE. Do not read it to find out what is known.

🔴 **THIS FILE WENT STALE FOR A DAY (fixed 2026-08-23).** It sat at 2026-08-22
saying the instance was shut down and *"H3 — THE SOLE GATE, and the whole queue
now"* while H3 and H6 were both being answered. It is a FIFTH working document
and the memory index listed only four, so no session opened it. **If you add a
doc, add it to the index, or it becomes a trap.** See CONVENTIONS §8b.

## Instance

**UP.** Address in `ops/env.sh` (one line — it was hardcoded in 29 places once).
`ops/go ops/status.sh` for state; `ops/go ops/remote.sh <rig.py> 32` to launch.

**After a spot reclamation:** launch `c7a.8xlarge` **in the volume's AZ** (EBS is
AZ-scoped — the easy mistake), attach, set the address in `ops/env.sh`, then
`NOSYNC=1 ops/go ops/mount.sh`. Exercised four times.
⚠️ `mount.sh` also checks that **pyflakes is in the env** — it lives on
`/opt/amip/envs/emsim`, NOT the root filesystem, because root is wiped by every
reclamation. Without it `preflight` silently stops checking undefined names.

## WHERE 2026-08-23 LANDED

🔴🔴 **EVERY ✅ IN THIS SECTION EXCEPT THE LAST ONE IS VOID. READ THIS FIRST.**
**These were all measured on a cavity with NO GROOVE.** `KNOWN.md` § NOT
ESTABLISHED discards them by name: η(ne), the +31.6 MHz loaded pull, loaded Q₀,
the 78% suppression law, sapphire's loaded point, β vs loop area, and all of
h4_field. **The design cavity has a mode filter; these do not describe it.**

⚠️ **The section is KEPT, not deleted, and the numbers are kept with it** — they
are real measurements of the wrong cavity, and each names a case the re-run must
cover (§7q: quarantine the claim, not the data). **Nothing here may be quoted.**
🔴 **The ✅ ticks below are what a stale banner looks like from the inside.** This
file already warned it went stale for a day; it then carried "H3 ANSWERED" for
another day after H3 was invalidated. **If you are reading ticks, check the date
and the cavity before you believe them.**

✅ **H3 ANSWERED.** TE011 sustains: η = 0.95–0.995 at the operating point.
Loaded pull **+31.6 MHz** (up), Q 44,384 → 163, linewidth 15.2 MHz, loaded
f₀ = 2.4815 GHz — in band. Third leg killing the in-band TM companion.
✅ **H6 ANSWERED (EM half)** — user-raised, and the premise I opened it on was
wrong. **η ≥ 99.1% across TWO DECADES of ne** (1e18–1e20). Mass loading is NOT a
hard EM constraint. The "collapse to 0.185" was a 2 mm SOLID-COLUMN artifact;
the annulus is 17× the plasma and does not collapse.
✅ **H4 field** — Slater holds at ε=11.6 (predicted −15.3, measured −15.00).
H1's design point survives the torch AND the plasma together.
✅ **Superposition FAILS**: the plasma SUPPRESSES a dielectric's shift by **78%**,
constant over ε 2–6, because it cuts E_elec at the tube ~75% material-independently.
✅ **THE ONE SURVIVOR — power density is a DEFINITION** (η·P/V), not a measurement — no optimum to
find; it is a FLOW question. H3's last "open" item closed with arithmetic.

## ✅ DONE — `h3_loopq`, the loop-size sweep (2026-08-24)

**10 eigen solves. Every β from an eigen PAIR, no fit anywhere.** V1 reproduced
`h3_step3` at 11×8 to 0.2 / 1.0 / 1.3 / 1.5% across two mesh styles.

✅✅ **F4 FIRED AND IT IS THE RESULT OF THE DAY: the groove is what makes the
coupling work.** Same loop, same mesh, groove or not — Q_ext **76,811 → 9,231
(8.3×)**, β **0.402 → 4.704** (crossing from under- to overcoupled), purity
**0.7593 → 0.9997**. Ungrooved, the degenerate TM111 hybridises with TE011 and
the loop couples to the blend. **A second, independent justification for the
groove, alongside H2's band clearance.** It also explains E0's **29,854** — 3.4%
from the 30,878 measured here, so that number was always a hybrid's Q.
🔴 **groove × loop are NOT SEPARABLE — the optimiser must search the joint space.**

🔴 **Coupling PEAKS at 176 mm²** (Q_ext minimises). 384 mm² is **dominated** —
weaker coupling AND 6.0% Q cost vs 2.2% — and is retired. Every grooved size is
OVERCOUPLED; **β = 1 extrapolates to ~10 mm² on the small-area branch.**
**To approach matching, go smaller; smaller is also cheaper in Q.**
✅ F1 does not fire — the driven anomaly was an extraction artefact.
⚠️ **but the branch explains only the 35 mm² point** (ratio 2.21 vs β 2.251);
at 82/176/384 it does not. Those cases were groove-free and some predate the
port-meshing fix. **Not fully explained — leave it that way.**
✅ F2 does not fire; V4 passes (35 mm² sits 0.5% from no-loop).

### ✅ DONE — PHASE B (`h3_margin`, 2026-08-24). **GEOMETRY CANNOT FIX THE MARGIN.**

12 cells, driven, ne=1e20. V1 reproduced `h3_driven` to **0.00 MHz**.

**Margin = f₀ → 2.500 GHz** (the tuner PARKS at f₀ — corrected 2026-08-24):

| groove | 10 mm² | 35 mm² | 82 mm² | 176 mm² |
|---|---:|---:|---:|---:|
| 5×7 | — | 18.2 | 18.0 | 17.4 |
| 5×10 | — | 18.2 | 18.0 | **17.6** ← design |
| 5×14 | — | 18.2 | 18.0 | 17.4 |

🔴 **Whole grid spans 0.8 MHz; best is +0.6 MHz over the design point.**
⚠️ First tabulated on the 3 dB edge (9.3–10.0). **Headroom doubled; the
conclusion did not.** The
loaded f₀ is a PLASMA property: groove depth moves it **0.000 MHz**, loop area
0.8 MHz, the plasma **+30.9 MHz**.
✅ **H2's 5×10 needs no refinement under load** — the question that moved H2 up
is answered, and the answer is that depth has no purchase on loaded f₀.
Depth SATURATES by 10 mm and PEAKS there at 176 mm²: **5×10 is optimal.**
🔴 **THE LEVER IS DENSITY: 1e20 → 1e19 buys +16.2 MHz and IMPROVES η.**
⚠️ n_e is not only an EM parameter — the analytical cost is the emission side's
to judge. ⚠️ **1e20 was never established as the operating point by this
programme**; if it is a requirement from elsewhere, that requirement costs the
margin.
🔴 **Loaded β ≤ 0.017 for any cap loop** (Q_ext floors at 9,231) → **~93% of
power reflects**. Whether that is the system efficiency depends on a matching
element not visible here. **ASK before quoting 6.6%.**

### ➡️ THE SOURCE SIDE IS ITS OWN PROGRAMME NOW — `../control-loop/`

Opened 2026-08-24. LDMOS, matching, and the control loop had no home while "the
LDMOS tuning band" was cited here a dozen times as a hardware anchor. `SOURCE.md`
moved there; `README.md` states what we have and what is needed.

⏸️ **PARKED, and parking costs nothing** — its two gating questions are in THIS
queue for cavity reasons anyway (items 2 and 3 below). **Re-entry:** n_e
anchored, or a coupler class measured that floors Q_ext below 9,231.

🔴 **Its headline: MAGNITUDE TUNING IS UNSOLVED.** Four PIN candidates rejected
for a structural reason — low C_j ⇒ small die ⇒ high thermal resistance, **so
the parts that work at 2.45 GHz cannot carry the 34–45 A a matched 1 kW
demands.** Not a sourcing failure.
✅ **Two keepers that came back to us:** the band is **ISM AND the part** — hence
immovable, and **out-of-band emission is a compliance limit**. And **a
magnitude-only detector would inherit our own §7x error** — |Γ| cannot tell β
from 1/β, and either side of the ignition crossing reads −13.98 vs −13.99 dB.

### THE OPEN QUESTIONS NOW, in the order they block things

1. ✅ **ANSWERED — the hardware requires a matching network** (user,
   2026-08-24). Raw β was never a system efficiency; **"6.6% delivered / 93%
   reflected" is WITHDRAWN.** Details, the tuner range it specifies, and the
   corrected margin criterion are in `../control-loop/SOURCE.md`. ⏸️ **The tuner itself is
   PARKED — see above.**

2. 🔴🔴 **ANCHOR n_e. IT HAS NO PROVENANCE AND IT IS THE DOMINANT VARIABLE.**
   User, 2026-08-24: *"an estimate from an earlier session... it has no
   provenance."* Confirmed, and the real origin is **solver convergence** —
   `h3_eigen`'s PI_1 map — laundered into "the operating point" over six
   citations (§7ab).
   🔴 **This makes "the band margin is 9.6 MHz" VOID as a design statement** and
   the question *is the margin adequate?* **ill-posed**, not merely unanswered.
   ✅ margin(n_e) and η(n_e) are measured and stand — report as FUNCTIONS of
   n_e, never at a point.
   **Routes, cheapest first:** ask the spectroscopy side what n_e the emission
   requires · an external literature anchor for atmospheric MIPs at 2.45 GHz in
   this power class · a power balance (E3's energy closure), which needs
   electron energy-loss data the programme lacks.
   ⚠️ **Eigen cannot solve at n_e ≈ 1e19** (PI_1 = 1.76) — the density with the
   best margin AND the best η. Driven can. That is an instrument limitation to
   state, not a region to avoid sampling.
3. 🔑 **TEST THE COUPLER CLASS — cheap, and it serves BOTH sides.**
   `geometry.py` states an *"iris-free route… no coupling structure"* as its
   premise. **That was a docstring decision, never a measurement**, and it fixed
   the coupler class before the cavity was even sized.
   ✅ `h3_loopq`'s **eigen-pair method measures Q_ext for ANY coupler the mesher
   can build** — two solves per geometry, no fitting, no branch ambiguity.
   🔑 **Q_ext FLOORS at 9,231 for a loop** (measured). An iris/aperture may reach
   lower, which would reduce mode-coupling loss AND cut the tuner requirement,
   since its current demand goes as √VSWR.
   ⚠️ Needs `geometry.py` to be able to mesh an aperture coupler — **unchecked**.

4. **PLAN E3 — the energy-balance closure** (η_total = η_plasma + η_wall +
   η_dielectric). Still never done, and it is the falsifier for every η here.
5. **H4 ignition**, still parked — and "no mode cold-ignites" is still
   un-anchored (its source rigs were groove-free).

### SUPERSEDED — the old Phase B plan

(kept for the reasoning; Phase B ran and its result is above)


Phase A (above) is cold and gives Q_ext per loop size. Phase B is the one the
band margin demands: **ne = 1e20, groove depth × loop size**, driven.
🔴 **Why it matters:** at 11×8 / groove 5×10 the loaded upper 3 dB edge sits
**17.6 MHz** below 2.500 after a **+30.9 MHz** pull (⚠️ this line said 9.6 MHz
until 2026-08-24, using the 3 dB edge instead of f₀). That is the thinnest number
in the programme and it is a HARD constraint (OPTIMIZER §3c).
✅ **PHASE A HAS RETURNED AND IT RESHAPES PHASE B:**
- **Drop 384 mm².** Dominated on both axes; solving it loaded would waste a cell.
- **ADD a size below 35 mm².** Everything measured is overcoupled and β = 1
  extrapolates to ~10 mm² — the interesting region is *below* the swept range,
  and it is unmeasured. ⚠️ It is an extrapolation across a turning point's far
  side; treat the first small-loop point as a TEST of ~10 mm², not a design.
- **Groove depth is the other axis and it is now co-dependent, not independent**
  (F4). Vary both together; a one-axis-at-a-time sweep is invalid here.
- **Purity is NOT a constraint on loop size** (F2 never fired, worst 0.0010), so
  do not spend cells on it. The binding constraints are **band margin (17.6 MHz)**
  and **β**.
⚠️ Loaded Q_ext may differ from cold — the plasma changes the field at the loop.
Phase A's Q_ext is a COLD number; check one loaded case against it before
treating Q_ext as geometry-only across the sweep.

## Queued, in order

🔴 **H3 IS THE PROGRAMME. It has three regimes and one cavity — H2's, with the
groove.** There is no groove-free variant; everything measured that way on
2026-08-23 is discarded, not pending.

### State of the tree (2026-08-23 cleanup)

- ✅ Design rigs now import **`GEO_DESIGN`** (groove 5×10): `h3_driven`,
  `h3_superpose`, `h3_sapphire`, `h3_loopsize`, `h3_eigen`, `h3_annular`.
  `h3_groove` deliberately keeps bare `GEO` — it toggles the groove itself.
- ✅ Groove-free results moved to **`discarded-2026-08-23-no-groove/`** with a
  README saying why. Nothing in there may be quoted.
- ✅ `FINDINGS.md` removed to git; `KNOWN.md` is the authority and indexes all
  ten documents. `METHODOLOGY.md`'s "FINDINGS wins" line updated to point at
  KNOWN.
- ✅ `CLAUDE.md` created at the REPO ROOT so a fresh session on any machine gets
  the orientation.
- ⚠️ **`loopbranch.py` is written and UNRUN** — resolves the coupling branch from
  phase. Needed before any β is quoted (item 1b).

0. ✅ **DONE — `h3_groove`.** The filter makes TE011 the mode the tuner locks to,
   at both loop sizes. Without it the tuner takes a TM-like mode at 2.44 GHz,
   which the groove moves −63.6 MHz (H2 cold: TM111 −64 MHz).
   🔴 **Unresolved**: at 28×20 TE011 moved −12.80 MHz vs +0.00 at 11×8. Either
   the groove differs under load or that mode is misidentified. Settle it in 1.

### 🔑 STANDING REQUIREMENT — EVERY eigen rig emits MODE PURITY

**6 probes, no extra solve.** `P = |E_φ|²/(|E_r|²+|E_φ|²+|E_z|²)` at ≥3 φ × ≥2 r;
report **P_min, P_max and SPREAD**. TE011 has P=1 at every φ, so the spread is the
discriminator, and it cannot alias.

🔑 **This is the first tool the programme has for "how does a cavity change alter
the modes", and almost everything downstream depends on it** — groove depth, loop
size, torch ε and n_e all perturb the mode landscape, and until now there was no
continuous measure of the result, only a binary label that could be wrong.

Implementation is in `h3_ladder.purity()`; the probe layout is
`PROBE_PHI_DEG=[0,40,80] × PROBE_R_FRAC=[0.4805, 0.25]`.
✅ Validated: rejects both TM111 polarisations AND TE311 (which A2/A0 binned as
m=0 with 0.0004), accepts bare TE011 at 0.9973–1.0000.
⚠️ Report P even when it PASSES — the value is the measurement, not the verdict.

### 🔑 STANDING REQUIREMENT — every H3 rig emits PRIORS, not just verdicts

**These results are CO-DEPENDENT.** Groove depth × loop size × n_e × torch
permittivity all move the same mode landscape, so the end state is not a list of
answers — it is a surrogate that can be optimised over the joint space.
`OPTIMIZER.md`'s own rule: *"a finding belongs there when stated as something a
surrogate can EVALUATE, not as a number."*

So every H3 rig must return, and its report must print:

| for the optimiser | not just |
|---|---|
| the CONSTRAINT value — how many modes in 2.40–2.50, and their margins | "the filter works" |
| the value AND its uncertainty (A2/A0, identification margin, one-sided vs two-sided width) | a bare number |
| the EVALUATION OUTCOME — converged / missing-data / infeasible, with NLEPS count | a silent gap |
| the COST — tets, ND dofs, seconds, NLEPS — so the cost model stays fitted | wall-clock in a log |
| **which other variables were held fixed, and at what** | an implicit context |

⚠️ **That last row is the co-dependence.** A number measured at one groove depth,
one loop size and one n_e is a SLICE. Record the slice coordinates or the
surrogate cannot place the point.

🔴 And a failed evaluation is **MISSING DATA, not a bad score** (§3). Scoring it
badly teaches the surrogate to avoid regions that are merely hard to solve.

### ✅ RESOLVED: the 2.623 GHz mode is **TE311**

Closed form **2.622012 GHz** vs 2.623005 measured — a 0.99 MHz match, the same
sf-1.5 systematic seen everywhere, and it reproduced exactly (Q 24,352 → 24,353)
under different eigen settings. **An ordinary cavity mode. Never an interloper.**

🔴 **Finding it exposed two coupled defects in the identification chain:**
1. **`physics.spectrum` enumerates only m ≤ 2, n ≤ 2, p ≤ 2** — TE311 is
   invisible to it. "The closed form has nothing there" is NOT a safe statement
   from this function. ⚠️ The truncation itself is defensible; you work around a
   table you know is truncated.
2. **`azimuthal.order()` binned TE311 (m=3) as m=0** with its highest
   confidence — **and that was the real defect.** `0` is not "unknown", it is
   the answer meaning TE011. Five sectors resolve only **m ≤ N/4 = 1**
   (|E|² ~ cos²(mφ) carries harmonic 2m), so m=2 was never resolvable either,
   despite `SECTORS`' comment claiming m ∈ {0,1,2}.
   ✅ **FIXED**: `order()` now returns `_m_resolvable_max` and
   `_aliasing_risk=True` alongside a flat verdict. CONVENTIONS §7o.

🔑 **Consequence: "clean m=0" does not establish TE011.** It needs a second
discriminator that fails differently — the Q ratio (TE011 is 2.17× TM111,
measured, resolution-robust), a COMPLETE frequency table, or continuation.
⚠️ The bare-cavity anchor survives because it has that second discriminator.

### 🔑 REPLACE m=0 IDENTIFICATION WITH A FIELD-STRUCTURE REJECTION TEST

**User: adding sectors cannot fix aliasing — something always moduluses into the
wrong thing.** Right, and unbounded. **Bin into "not TE011" instead.**

TE011 is TE_0np: E_z = 0 (TE) and E_r = 0 (m=0), so **E is purely azimuthal**.
Probes already emit the full complex vector, so

    P = |E_phi|^2 / (|E_r|^2 + |E_phi|^2 + |E_z|^2)

✅ **Validated on saved `h4_field` probes**: TE011 **P = 0.9999**, TM111 pair
0.872 / 0.126, TE311 0.989.
🔑 **TE011 has no φ-dependence, so P = 1 at EVERY φ** — an m≠0 mode's P varies
with φ. **Probe several φ, require P ≈ 1 at all.** No decomposition, no modulus,
nothing to alias.

**To do:**
1. Add probes at ≥3 azimuthal positions × ≥2 radii to the eigen rigs.
2. Report P per φ, and its SPREAD across φ — the spread is the discriminator.
3. Use it as a REJECTION: "not TE011" needs no alternative label.
4. ⚠️ Keep the Q ratio as the second, independent check (2.17× vs TM111).

### 🔴 STILL OPEN: extend `physics.spectrum`'s enumeration

It is the reference table every identification checks against, and it cannot see
m ≥ 3, n ≥ 3 or p ≥ 3. **Cheap, no solving.**
⚠️ **{m,n,p} ≤ 3 is probably enough in practice** — but it is a mitigation, not
a fix. The field-structure test above is the fix, because it does not depend on
enumerating anything. Until then, "no mode there" from
`spectrum()` means "no mode there among m,n,p ≤ 2".

### 🔴 OPEN: what is the 2.623 GHz mode? — ANSWERED ABOVE, kept for the trail

A converged mode appears at **2.623005 GHz** in the BARE cavity solve — m=0 by
azimuthal binning (A2/A0 = 0.0004), Q = 24,352 — and **the closed form has
nothing there.** Bare cylinder: TE011/TM111 at 2.450, then TE112/TM210 at
2.783/2.784. Among m=0 modes: 2.450, 2.906, 2.993, 3.326. **Nothing near 2.623.**

🔑 It matters because it is **what the driven sweeps kept selecting** — the
"interloper" that broke mode selection repeatedly. Until it is explained, any
identification that works by distinguishing TE011 from it rests on an unknown.

Candidates, cheap to separate:
1. **Spurious eigenmode** — check whether it survives a mesh refinement and a
   different shift target. A spurious mode typically moves or vanishes.
2. **A mode of the MESHED geometry, not the ideal cylinder** — the torch tube is
   geometrically present in every mesh even under `--no-torch` (that flag sets
   ε=1, it does not remove the tube). At ε=1 it should be EM-invisible, but that
   is an assumption worth testing.
3. **A family `physics.spectrum` does not enumerate** — check its index ranges
   against a hand-computed TE/TM table.

⚠️ Do NOT proceed to loaded identification until this is settled or explicitly
set aside. It is the single most persistent confounder in the record.

### 🔧 EIGEN SETTINGS FOR A GROOVED CAVITY — use **`h2_groove`'s**, not h2b's

🔴 `h3_ladder` step 2 (grooved, no loop) **did not converge**: 1,018 NLEPS
against the 1,000 budget, killed at 630 s. Returned as MISSING DATA by the
budget guard, correctly. Step 1 (bare) converged easily — **the groove is what
makes it hard.**

🔴 **h2b's settings ALSO failed** (1,040 NLEPS). Three attempts:

    target 2.30, N=6   -> 1,018 NLEPS, budget exceeded
    target 2.25, N=10  -> 1,040 NLEPS, budget exceeded   (h2b's)
    target 1.05, N=12  -> what `h2_groove` ACTUALLY used, and it solved this
                          cavity — its -64.25 MHz is the H2 anchor

✅ **Use `h2_groove`'s: `target = 1.05`, `n = count(closed-form ≤ 2.57) + 5`.**
🔑 **A target far BELOW the spectrum converges where one just below the cluster
does not** — shift-invert maps λ to 1/(λ−σ), and a σ near a tight cluster makes
several transformed values huge and nearly equal. Starting low converges the
well-separated modes first. INSTRUMENT has the full note.
⚠️ Slower per solve AND more likely to converge. **Speed and convergence are
different axes**; `solvecost` predicts only the first (§6c).

> *"At D/L 1.525 the closed form has nothing between TE211 at 2.10447 and the
> degenerate pair at 2.45000, so 2.25 buys 200 MHz of downward headroom at the
> cost of ZERO extra cavity modes."*

🔑 **Two rules from that, and I violated the second:**
1. **Put the shift target in a SPECTRAL GAP**, and find the gap from closed form
   — it is a calculation, not a guess.
2. **Do not ask for exactly the number of modes that straddles a cluster.** I
   used N=6; with the groove pulling TM111 to ~2.386 the six requested modes land
   on the near-degenerate triplet boundary. h2b uses **10** for slack.

⚠️ Note this is the OPPOSITE of the fix that worked for `h3_cold`, where
narrowing the span turned a timeout into a solve. **Span and mode count are not
one knob**, and the right setting depends on where the shift sits relative to the
cluster — not on how wide the window is.

### 🔧 FIXES TO `h3_cold.py` BEFORE THE NEXT RE-RUN (from the 2026-08-23 run)

The run produced real data and the rig **discarded most of it**. Fix these
first; do not re-launch as-is.

**1. Identification must DEGRADE, not ERROR.** `azimuthal.order()` returns
`m=None` when the mode is mixed, and the rig requires `m_az == 0` strictly, so
it printed *"no m=0 mode in the LDMOS band"* and **never reached the F1 report**
— on runs that had converged and found the mode.
🔑 **The mixing is REAL, not a failure**: loaded, the in-band mode has
A2/A0 = 0.3244 against 0.0004 for the high-Q mode the plasma does not couple to.
**A symmetry test is a poor discriminator under a perturbation this large** —
E1b's lesson, again.
✅ Report every mode in the window with f, Q, m, A2/A0; select the TE011
candidate by a STATED rule and FLAG it uncertain; never discard a converged mode.
⚠️ Do NOT select by "nearest 2.45" — that is §1. The correct discriminator is
CONTINUATION from the cold case, which needs fix 2 to exist.

**2. The cold 11×8 case timed out — and it was PROGRESSING, not stalled.**
174 NLEPS in 900 s, against a budget of 1,000 (25 converged runs used ≤869). It
was iterating, so the binding constraint is WALL TIME, not convergence.
✅ Raise `CASE_TIMEOUT_S` for cold cases (1,800 s), and/or narrow the shift-invert
span — I used `target 2.30, N=6` spanning 2.30→2.61 (307 MHz). §6: I chose the
target for safety against the H2b window trap and never re-derived its cost.
⚠️ 28×20 cold converged on the SAME settings, so this is marginal, not
systematic. Treat the marginality itself as envelope data.
🔴 **This case is the one that supplies the η reference (item 1a).** Until it
converges, 1a is still open and no loaded η can be computed.
✅ **SUPERSEDED 2026-08-24: Q₀ = 12,368** (`h3_ladder`). See below.

**3. `_report()` must run even when cases fail.** F1 — the filter check, the
whole point of §7i — never printed because earlier cases errored. Verdicts must
not be hostage to a missing case.

**4. The groove must be a VARIABLE, not `GEO_DESIGN`'s constant.** H3 LOADED has
to sweep groove DEPTH if a mode re-enters the band under load (item 3). The rig
currently hard-codes the 5 × 10 baseline with no way to vary it.

**5. Emit the prior, not the verdict.** The rig currently prints a pass/fail
per falsifier. It must also emit, per case: modes-in-band with margins, A2/A0
and identification margin, converged/missing/infeasible, tets + NLEPS +
seconds, and the fixed coordinates (groove w×d, loop d×hw, n_e, torch ε).
`OPTIMIZER.md` §3c is the consumer.

**6. What NOT to change.** Do not switch to driven (§7c, and eigen is right for
"which mode, at what frequency, with what Q₀"). Do not retarget mid-rig. Do not
add cases beyond E0–E4's scope (§7k).

### 📊 `h3_cold` STAGE 1 (cold only, narrowed span) — 2/2 converged, 4 falsifiers fired

✅ **The span fix worked**: target 2.30/N=6 → 2.38/N=4 turned a 900 s timeout
into a converged solve. Wall time was never the binding constraint.

| | 11×8 cold | 28×20 cold |
|---|---|---|
| in band | 2.4400 (m=1), 2.4944 (m=?) | 2.4048 (m=?, A2=.256), **2.4460 (m=?, A2=.048, Q=30,222)** |
| clean m=0 | 2.6065 (A2=.0008, Q=20,951) | 2.6028 (A2=.0069, Q=20,392) |

🔴 **F1 FIRES AT BOTH LOOP SIZES — two modes in band, with the groove.**
🔑 **This does not contradict `h3_groove`; it corrects what that run could
show.** Driven saw ONE dip at 11×8 and I read it as one mode. **A driven sweep
shows what the PORT COUPLES TO, not what EXISTS.** So "the filter makes TE011 the
tuner's target" stands; **"the filter clears the band" does not.**
🔴 **F3 FIRES: +6.02 MHz between loop sizes** — loop size moves the MODE, not
just the coupling. That was the alternative explanation for `h3_groove`'s
−12.80 MHz and it is now the likely one.
⚠️ V3 and F2 also fired, but on the 11×8 candidate this run picked BEFORE the
selection fix — it chose a mode labelled **m=1**. Both are downstream of that
bug, not independent evidence. **The η reference it printed (12,368) is void.**
✅ **OVERTURNED 2026-08-24.** The mode is TE011 by continuation, and 12,368
stands. The `m=1` label that voided it came from azimuthal binning — the test
TE311 defeated. **A wrong label voided a right number.**

🔑 **Best TE011 candidate anywhere in the run: 28×20's 2.4460** — A2/A0 = 0.048,
Q = 30,222, −4 MHz from closed form.
🔑 **Likely reason the landscape is not H2's: H2 measured the groove with NO
LOOP.** Groove-only and groove-plus-loop are different cavities, and the loop
mixes the triplet (`pair_q_ratio` 1.000 → 1.364).

### 🔴 NEXT: THE CONTINUATION LADDER, one perturbation at a time

The closed form says the bare cavity has exactly TWO modes in 2.35–2.70 —
**TE011 and TM111, both at 2.450000, exactly degenerate** (χ′₀₁ = χ₁₁). We
measured FOUR. "Where did TE011 go" cannot be answered by solving the finished
cavity; it needs continuation from the one state where the label is exact:

| step | cavity | anchor |
|---|---|---|
| 1 | bare, no groove, no loop | **closed form** — 2.450000 exactly; E0 validated the solver here to 0.058 MHz; the degenerate pair separates by Q ratio |
| 2 | + groove (5×10), no loop | **H2** — TM111 −64.25 MHz, TE011 +14 kHz. Checkable |
| 3 | + loop | the design cavity, COLD |
| 4 | + plasma | LOADED |

Each step is small enough for unambiguous pairing; steps 1–2 have EXTERNAL
anchors. **I skipped to step 3 and that is why nothing is identifiable.**
⚠️ Steps 1 and 2 are cheap (no loop, no plasma, ~44k tets).

| case | tets | outcome | modes in 2.40–2.50 |
|---|---:|---|---|
| 11×8 cold | 43,685 | 🔴 timeout (174 NLEPS) | — |
| 28×20 cold | 46,182 | ✅ | **2**: 2.4048 (Q=13,623, A2/A0=0.256), 2.4460 (Q=30,222, A2/A0=0.048) |
| 11×8 loaded | 80,621 | ✅ | **1**: 2.4600 (Q=253, A2/A0=0.324) |
| 28×20 loaded | 72,969 | 🔴 timeout (27 NLEPS) | — |

🔑 **The one real result: LOOP SIZE FLIPS BAND CLEARANCE.** Same groove, same
cold state — 11×8's filter holds, **28×20 puts TWO modes in the band**. F1 fired
and the rig said so instead of coping (§7i). That is a feasibility constraint
over the joint space, now in OPTIMIZER §3c.
⚠️ At 28×20 cold, 2.4460 (A2/A0 = 0.048) is fairly clean and looks like TE011;
2.4048 (A2/A0 = 0.256) is mixed. **Neither is labelled** — the strict `m == 0`
test discarded both.
⚠️ Loaded 11×8 keeps ONE mode in band. One density, one loop, unlabelled.

🔴 **STILL NO η REFERENCE.** 11×8 cold is the case that supplies it and it timed
out. **Item 1a remains open and blocks everything downstream.**
✅ **SUPERSEDED 2026-08-24 — 1a IS ANSWERED, Q₀ = 12,368.** See "ITEM 1a IS
ANSWERED" below. Left in place because it records why the ladder was built.

### 🔑 What the earlier `h3_groove` run established, provisionally

- **Loaded, 11×8, grooved: exactly ONE mode in 2.40–2.50** — at 2.4600, Q = 253.
  Loading did **not** bring the others back in at ne = 1e20.
  ⚠️ One density, one loop. The loaded cluster is 2.362 / 2.460 / 2.507, and
  **2.507 sits only 7 MHz outside the upper band edge** — the margin is thin.
- Cold 28×20 showed **two** modes in band (2.4048, 2.4460) — but that is a
  1,120 mm² loop, and a loop mixes the triplet. Not the design loop.
- The plasma cleanly separates what it loads (Q = 241–290) from what it does not
  (Q = 17,000–21,000 at 2.606).

### ✅ ITEM 1a IS ANSWERED — LADDER STEP 2 CONVERGED (2026-08-24)

`h3_ladder` bare → grooved, N=10, target 1.05. **V2 passes on both legs against
H2** (TM111 −62.95 vs −64.25 MHz, 2.0%; TE011 +0.094 vs +0.014 MHz).

| cavity | f₀ GHz | Q | purity |
|---|---:|---:|---:|
| bare | 2.450467 | 44,057 | 0.9973 |
| + groove 5 × 10 | 2.450561 | 44,414 | 0.9985 |
| + loop 11 × 8 (**design**) | 2.440003 | **12,368** | 0.9423 |

✅ **η REFERENCE FOR THE DESIGN CAVITY AT 11×8: Q₀ = 12,368.** The mode is TE011,
**identified by continuation** — from the grooved state the two candidates need
−10.56 MHz (2.440003) or +43.88 MHz (2.494440); only the first is a small
perturbation. This overrides the earlier "**the η reference it printed (12,368)
is void**" above: that verdict rested on the azimuthal `m=1` label, which is the
test TE311 already defeated. **Same number, sound justification.**

🔑 **THE GROOVE IS NEARLY FREE; THE LOOP COSTS EVERYTHING** — groove: +0.094 MHz,
Q ×1.008, purity **+0.0012**. Loop: −10.56 MHz, Q **×0.278**, purity **−0.0562**.
Mode impurity is a COUPLER effect, not a filter effect.
⚠️ **Still open, and 1a does not close them:** the purity gate is still
uncalibrated for a looped cavity (0.99/0.02 was set bare; the loop costs 0.056,
so the gate is simply wrong there, not the mode). The Q cost of the groove is
**not** resolved — +0.8% measured against H2's −0.3%, both inside a ~1% mesh
spread. **1a is answered per loop size; 28×20 has no reference.**

### ✅ CODE FIXED 2026-08-24 — the η reference was still 44,384 IN THE RIGS

Item 1a was answered in the documents while the **code still divided by the bare
cavity**. Found by reading `h3_driven.py` before launching it, not by running it.

| file | was | now |
|---|---|---|
| `h3_driven.py` | `Q_BARE = 44384.0` | `Q_REF = 12368.0` + `check_eta_reference()` |
| `h3_annular.py` | `Q_BARE = 44384.0` | `Q_REF = 12368.0` |
| `h3_sapphire.py` | imported `Q_BARE` | imports `Q_REF` |
| `h4_seed.py` | `Q_BARE = 44384.0` | banner — discarded rig, fix on re-run |

🔴 **`h3_driven`'s ANCHORS dict was VOID and is now empty.** It held
`1e20: f0=2.481566, Q=163` (groove-free) and `1e18: eta=0.185` (groove-free AND
the 2 mm SOLID-COLUMN artifact, not this annulus). **An anchor from the wrong
cavity validates a wrong answer and rejects a right one** — worse than none.
✅ `check_eta_reference()` refuses to run if `GROOVE_DESIGN` or the loop size
differs from what 12,368 was measured on. **Q₀ does not scale with loop size
(44,414 → 12,368 at 11×8); it must be re-measured.**
🔑 **A number corrected in a document is not corrected in the programme.** §8b's
sibling: land it in the CODE that consumes it, or the next run reproduces the bug
with the doc sitting right there saying otherwise.

### 🔴🔴 AN UNASSIGNED PORT BC OPENS THE LOOP GAP — reaches back through the record

`h3_step3`, 2026-08-24. Mesh has `port = 91`; the eigen config assigns a BC to
**attribute 90 only**; an unassigned boundary is **PMC** (the natural BC), so the
**feed gap was left OPEN** and open-gap+loop is an LC resonator near 2.45 GHz.
⚠️ I first wrote this as "defaults to PEC, shorts the loop" — backwards.

✅ **TE011 in the design cavity = 2.451490 GHz, Q₀ = 43,523, P = 0.9998.**
Eigen (port terminated) and driven agree to **12 kHz**. The loop costs
**+0.93 MHz and 2% in Q** — it does NOT split or degrade TE011.
✅ **ITEM 1b ANSWERED: cold is OVERCOUPLED, β = 4.77.** η recomputed to
**0.985–0.998**. **H3 LOADED stands with a corrected η column.**
🔴 `h3_cold`'s 2.440003 / 12,368 / 0.9423 purity are **open-gap artifacts**.

**WHAT THIS TOUCHES — audit before quoting any of it:**
1. **Every looped eigen result in the record.** `h3_cold`, `h3_loopsize`,
   `h3_eigen`, `h3_superpose`, and any β-vs-loop-area work. All shorted.
2. **The "hybridised Q" prior in OPTIMIZER** (1/Q mixes linearly with m=1
   admixture, 2 points, "THIN"). Its source is looped eigen — likely measuring
   shorted-loop hybridisation. **Do not use it.**
3. **The 176 mm² mode-identity threshold**, already flagged as needing re-check.
4. ⚠️ **`h3_ladder` steps 1–2 are FINE** — loop-free, no port to short.

✅ **GATE 4 IS IN (`e0_solver_vs_math.eigen_cfg`, 2026-08-24).**
`eigen_cfg` already had **GATE 3** — *"every volume attribute gets vacuum, and we
ASSERT none was missed"* — and it explicitly skips `wall` and `port` as surfaces.
🔑 **The port fell through BOTH: not a volume, and nothing assigned it a boundary
either. The gate that existed is why the gap was invisible.**

`port_bc` now has **NO DEFAULT**, because there is no safe one:

| value | meaning |
|---|---|
| **`lumped`** | 50 Ω `LumpedPort`, excitation off, mirroring the driven template's R and Direction. **THE MACHINE.** ⚠️ Q is LOADED |
| `pec` | short the loop deliberately — and it logs a warning saying so |
| `absorbing` | radiation BC. ⚠️ explicitly NOT the 50 Ω feed |

A mesh with a port and no `port_bc` is a **REFUSAL** naming the consequence.
All six paths tested (loop-free±bc, looped×3, junk).

🔴 **BLAST RADIUS — 10 rigs will now REFUSE until given an explicit `port_bc`:**
`e0k2_portfix`, `e0k2_azim`, `e0k2_betacause`, `e0k_driven_vs_eigen`,
`e0k2_anchor`, `e0k2_sizeq`, `h3_loaded`, `h3_cold`, `h3_ladder`, `h3_step3`.
**That is the correct list — every one meshes a loop and every one was shorting
it.** The refusal is DYNAMIC (keyed on the mesh actually having a port), so
`h3_ladder` steps 1–2 still run: they are loop-free.
✅ **Loop-free eigen is untouched**, `h2_groove` included — **H2 stands.**

**THE FIX, in order:**
- a. **Assert every mesh attribute has an intended BC** in `eigen_cfg`, and
     REFUSE when one is unassigned (§7v). This is the general guard and it is
     cheap; do it before any further eigen work on a looped cavity.
- b. Decide the physical intent per rig: terminate attr 91 in 50 Ω (an impedance
     eigenproblem) or state explicitly that a shorted loop is wanted.
- c. **TE011's purity in the operating configuration is UNMEASURED** and no eigen
     rig can measure it as things stand. That is the open question, and it is
     what the last measurement was supposed to settle.

### 🔴 NEW, CHEAP, AND IT BLOCKS THE OPTIMISER: loop 11×8 with NO groove

One eigen case, no plasma, sf 1.5, same settings as the ladder.

**Why:** the ladder gives groove-on-bare (a true single-element measurement) and
loop-on-grooved (a difference). **Summing them proves nothing** — the loop term
is defined as design − grooved, so the sum returns design − bare by construction.
The only non-circular check available **disagrees by 2.4×**: loop-on-bare Q
×0.673 (44,384 → 29,854, E0-era) against loop-on-grooved **×0.278**. Different
loop size, different resolution, or a **real groove–loop interaction** — both
elements cut the same end caps, so interaction is entirely plausible.

**Consequence if it interacts:** the OPTIMIZER **cannot factorise groove and loop
into independent axes**, and the "groove is cheap" prior does not transfer to
other loop sizes. That is a joint search space, not two separate ones.

⚠️ **This is a groove-free mesh AFTER H1 and it is NOT discarded** — it is a
deliberate control, the same status as h2/h2b's gd=0 cases (see KNOWN's audit
table). **Its purpose is to measure the groove's contribution by removing it.**
Label it as a control in the result file so no later audit sweeps it up.

### 🔑 THE SUPERSEDED CANDIDATE NOTE (kept — it shows what settled it)

**Design cavity (groove 5×10 + loop 11×8), COLD, converged:**
**TE011 = 2.440003 GHz, Q₀ = 12,368** — purity 0.9423–0.9998, impurity inboard,
φ-structure aligned with the loop at φ=36°.

**That Q₀ is the η reference item 1a needed** — measured on the grooved, looped
mesh, which is what §7c says neither 44,384 (no loop, no groove) nor 29,854
(loop, no groove) can substitute for.

⚠️ **Two things to settle before banking it:**
1. **Confirm the mode choice.** 2.440003 was chosen over 2.494440 on Q (12,368
   vs 3,576) and shift (−10.5 vs +44 MHz). **Neither passes the purity gate**,
   and the gate is uncalibrated for a looped cavity. A grooved-no-loop solve
   (ladder step 2) would settle it by continuation — it is the step that keeps
   timing out.
2. **The loop hybridises TE011** — 99.7% pure bare, ~94% inboard with the loop.
   Whether 6% non-azimuthal field matters for the TDS objection is a MAGNITUDE
   question, unanswered.

1. 🔴 **MEASUREMENT HYGIENE — before any loaded number is quoted again.**
   a. **MEASURE the η reference on the GROOVED, LOOPED mesh — PER LOOP SIZE.**
      Every loaded η on 2026-08-23 used `Q_BARE = 44,384`, the no-loop,
      no-groove value, while every driven mesh had a loop.
      🔴 **CORRECTION (caught by a fresh session, 2026-08-23): 29,854 is NOT the
      substitute.** I wrote it as though §7c's with-loop figure were the answer.
      It is itself **groove-free AND from a different loop geometry**, so it is
      wrong on both axes. There is no number to look up — **Q_bare must be
      SOLVED for each loop size on the grooved, looped mesh.**
      ⚠️ That makes 1a a solve, not a re-score, and it is why nothing else can
      be re-run first.
   b. **Resolve the coupling branch from PHASE** before reporting β.
      |S11| cannot tell β from 1/β: −11.46 dB is 0.578 OR 1.730.
      `loopbranch.py` is written and unrun.
   c. **Fix mode identification under the groove** — settle 0's −12.80 MHz.
   d. 🔑 **CLOSE THE ENERGY BALANCE — `PLAN.md` E3 declared this falsifier
      before any of this was built and it was never run:**
      **η_total = η_plasma + η_wall + η_dielectric.** If the split does not sum
      to η_total within a few percent, **the decomposition is wrong and ONLY
      η_total may be quoted.** Every "into the plasma" figure I produced was an
      undecomposed η_total wearing a decomposition's name. PLAN notes this
      already caught a factor-of-2 convention error once.
   e. Only then may delivered-power figures be quoted at all.

2. 🔑 **H3 COLD** — no discharge, gas fill. f₀, Q₀, and what a tuner sees before
   ignition. The acquisition point for the ignition sequence, never measured
   with the groove. Also supplies the **η reference** (item 1a).

3. ✅ **DONE 2026-08-24 — see PHASE B above. The groove turned out NOT to be a
   live variable: depth moves the loaded f₀ by 0.000 MHz and PEAKS at 10 mm, so
   5 × 10 stands. The item below is kept because its REASONING was right — the
   question had to be asked; the answer is just "no refinement needed".**
   ⚠️ One part of it is still OPEN: "if a TM mode re-enters the band under load"
   was NOT tested — `h3_margin` is DRIVEN, and a driven sweep shows what the
   PORT COUPLES TO, not what EXISTS. **Mode competition under load needs an
   eigen solve on the loaded design cavity, and eigen struggles at ε = −30.**

   🔑 **H3 LOADED — AND THE GROOVE IS A VARIABLE HERE, NOT A CONSTANT.**
   🔑 H2's 5 × 10 mm was validated **COLD**. **Loading moves every mode**, so a
   groove that clears the LDMOS band cold may not clear it loaded. Refining it
   is H3's job — that is *why* H2 was answered first, to give a baseline to
   refine rather than a constant to inherit.
   **Measure:** the loaded mode landscape in 2.40–2.50 at the baseline groove.
   **If a TM mode re-enters the band under load**, sweep groove depth until it
   clears — the depth law is known non-power-law (exponent 1.22 → 0.78 over
   gd 5→20) and 🔴 **λ/4 = 30.59 mm is the depth to AVOID** (the slot resonates,
   Q collapses to ~3,000).
   ⚠️ Sweep DEPTH, not width: H2's data covers depth; width was fixed at 5 mm.

4. 🔑 **H3 HOT — RE-IGNITION in a cavity that has already been operating.**
   🔴 Corrected 2026-08-23: HOT is a **THERMAL state, not a plasma-density
   slice**. Hot walls, hot gas, **no plasma**. This is the restart case, and the
   plasma WILL go out in service.
   Three large differences from COLD, all quantified:
   - **dimensions**: aluminium α = 23.1e-6/K → **−5.7 MHz at +100 K** against a
     100 MHz tuner band
   - **gas density**: n ∝ 1/T → at 3000 K, **E/N is 10× higher for the same
     field**. 🔑 This is the thermal-kernel mechanism H4 requires — a hot cavity
     may re-ignite where a cold one cannot
   - **wall σ**: −0.4%/K, Q ∝ σ^0.5 → **Q × 0.78 at +100 K**
   ⚠️ Needs a wall-temperature and gas-temperature estimate first; both are
   external inputs, not EM outputs.

5. **H3 LOADED + SAMPLE** — a real high-TDS matrix. The sample travels up the
   central channel (r < 2 mm), which is TE011's field null.
   ⚠️ What ne a sample actually produces is CHEMISTRY (aerosol transport,
   desolvation, atomisation) and is an H5 external input, not an EM question.

6. **P_required(ne)** — the plasma power balance. Without it the operating point
   cannot be closed: P_delivered alone does not say whether the discharge holds.

7. **H4 — ignition.** TM ignition is discarded; auxiliary/thermal-kernel is the
   adopted route. Needs H3 COLD first (the acquisition point).

8. **H5 — the optical path to LOD. TERMINAL.** Blocked on external inputs
   (spectrometer f-number, uniformity spec, coolant interlock), not simulation.

## Retired / not on the path

- **H2 (the groove)** — RETIRED `premature` 2026-08-23. Frozen at 5×10 mm; its
  variables have left the design space. What remains is MODEL VALIDATION (does
  Slater predict the shift?), a free by-product of any future grooved solve with
  `--tag-groove`. Not a hypothesis, not on the path.
- **The loop sizing sweep** — VOID. β is not mesh-converged (43% for a 1.25×
  refinement) and the sweep was built on it. Supersede with item 2, which sizes
  against a loaded Q₀ that now exists.

## Still open, recorded and not narrated

- **TE011's Q is non-monotonic in loop area** (37,525 / 29,073 / 30,020 /
  31,665, minimum near 82 mm²) while `pair_q_ratio` degrades 1.000 → 1.364. The
  loop MIXES the triplet rather than merely shifting it. May be explained by the
  port fix; check after item 1.
- **The 100–150 Td avalanche threshold is a literature figure.** Microwave
  breakdown at 1 atm is diffusion-loss and therefore geometry dependent. Verify
  before leaning on the ignition conclusion.
- **Three inherited assumptions are now marked ASSUMED in OPTIMIZER.md** and
  must not be used as priors: the 8.5 mm bore (from order-1 solving), the 20 slm
  N₂ ceiling (from MP-AES/MICAP, not optimised), and the Fassel torch geometry
  (Argon-optimised; there is no N₂ equivalent).


