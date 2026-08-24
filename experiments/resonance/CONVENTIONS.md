# Conventions

**Read this at the start of every session.** These are not style preferences.
Each one is a mistake that was actually made here, usually more than once, and
several were made again within hours of being written down.

Sorted by pattern, because the same shapes keep recurring in new clothes.

---

## 1. Never infer state from a proxy. Ask the direct question.

This is the single most repeated error. Four instances in one session:

| proxy used | what it got wrong | direct question |
|---|---|---|
| Palace ranks = "busy" | `ops/go` nearly synced code into a live meshing run — rigs spend most of their life meshing with **zero** ranks | is the RIG process alive? |
| log growing = "alive" | the waiter declared a healthy E1b dead; gmsh meshes silently for minutes | is the rig's own `python3` running? |
| elapsed time = "solved" | `MIN_SECONDS=30` discarded a correct 5 s solve; the threshold was calibrated on hardware we no longer use | did it PRODUCE non-empty output? |
| frequency proximity = "which mode" | E1b failed three times; then H2b rebuilt the identical bug hours after the lesson was written | match by Q, multiplicity, or continuation |

🔑 **The sharpest form of this: a nearest-neighbour answer is only trustworthy
if what it found is NEARER than the edge of the region that was searched.**
Otherwise "nearest" is an artifact of where you stopped looking. H2b asked for
the mode nearest 2.45 GHz in a solve whose window began at 2.40, while the groove
had pushed that mode down to 2.387 — outside. The function returned a confident
2.606, a real mode of a different kind that even had a plausible Q ratio (0.472
against TM111's 0.456). Every guard passed. H2 had measured the same geometry
correctly, months of reasoning apart, only because it searched from 1.05.

And it is a BALL, not a side: the false candidate sat 156 MHz ABOVE the target
where the window ran 343 MHz, while the real mode was 63 MHz BELOW where it ran
only 50. Checking the side the candidate happens to lie on passes the bad case.

**And do not re-derive what something already knows.** `h1_aspect` re-searched
for the TM111 pair by frequency after `te011_tm111` had already identified them;
it returned empty whenever the pair split more than 100 kHz. Return the indices.

## 2. A value must reach the thing that consumes it

*"A baseline nobody reads is a claim, not a fact."*

- **R101** — `--torch-material` fed mesh sizing and the sidecar, never the
  solver. Two meshes with identical byte counts were the only tell.
- **R110** — aluminium adopted and written to `baselines.json`; the template
  kept **silver**, so every absolute Q in the record was 34% high.
- **solver order** — `eigen_cfg` hardcoded `Order: 1`; six rigs inherited it
  silently and all their conclusions had to be invalidated.
- **E0l** — `PRIOR` merged AFTER the summary table, so every speedup printed
  `NaN`.

✅ Bind from the source of truth, **announce the value in the log**, and make a
missing declaration **refuse to run** rather than substitute a default.

⚠️ A flag set to its own default is invisible. `--n-wl 8` where 8 is the default
made E0's "coarse" mesh identical to its "fine" one, so its resolution check was
vacuous for the programme's whole life. `noopflags.py` scans for these.

## 3. Nothing is silently dropped

*"A script that drops a row makes its own criterion invisible."*

- E1b's analysis sat one indent outside the shape loop: shape A was meshed and
  solved twice, then discarded, while the run printed a confident summary.
- H2b's Q guard excluded points from a fit without saying so — written into a
  file whose own docstring claims nothing is dropped.

✅ Report the failure, the count, and the reason. Where an exclusion feeds a
derived number, print that number **both with and without**.

## 4. Killing a process means killing its tree

- `pkill -f` matched the calling shell's own argv and **killed the shell three
  times**. Never use it. Select by exact executable name, kill by PID.
- `proc.kill()` kills only the bash wrapper. The real tree is
  **`palace` (wrapper) → `prterun` → `palace-x86_64.bin` ×N**, so the ranks are
  orphaned to PPID 1 and keep running — four of them for 20 minutes.
- `reap.py` looked for ranks whose OWN parent was init and reported "no orphans"
  throughout that leak, because ranks are **never** direct children.

✅ `start_new_session=True` + `os.killpg`. `ops/stoprig.sh` does rig + tree.

## 4b. A quantity measured in another epoch was measured on another machine

Two numbers from this programme are only comparable if the thing between them
did not change. Three times now the "surprising discrepancy" was bookkeeping:

| looked like | actually was |
|---|---|
| solve cost varying 95× at fixed tet count | **4 ranks on the laptop vs 32 on the instance** |
| driven and eigen disagreeing 3.7× on frequency | **solver order 1 vs 2** |
| one loop giving β = 0.067 then β = 27.5 | **two different cavity DESIGNS** — E0k predates H1 and ran D/L 2.343, the candidate H1 rejected |

🔴 In the last of these I described it as "a factor of 410 for a 15% change in
radius" — quoting the one dimension that had moved least (the length changed
30%, the aspect ratio 35%) and thereby making a different design look like a
perturbed one. Then I set it up as a mystery to be solved before work could
continue. It was not a mystery; it was two machines.

⚠️ **And a fourth, of a different kind:** hunting a mechanism for that same
410×, I derived TE011's fields with sin and cos swapped and concluded the barrel
loop sat on a field NODE. It sits at the MAXIMUM. The inverted forms satisfy
neither boundary condition, and a ratio quoted in the code (1.39) reproduces
exactly from the correct ones — a check that was available before writing the
conclusion into three documents. **When a "surprising discrepancy" tempts a new
mechanism, check the mechanism against something already in the record that it
must reproduce.**

✅ Before calling a difference surprising, list what else changed — epoch,
geometry, ranks, order, wall material, solver type — and say which of them you
have held fixed. If the answer is "none", the comparison is not a measurement.

## 5. Measure the magnitude before drawing the consequence

*"Measure the outcome, not the mechanism."*

- E0m found the mesher non-deterministic (46 µm of node motion). I wrote three
  consequences into the record — an invalidation, a repo-policy reversal, and a
  promotion of the cache to "infrastructure" — **before** measuring that it
  costs **66 Hz**. All three had to be withdrawn. The measurement took 8 minutes.
- Q_ext once turned a 21-point power gap into a "98× deficit".

## 6. Do not reuse a parameter without re-deriving it for the case

- `sf 0.96` and `target 1.05`, copied from the E0 rigs into H1, gave 110–120k
  elements and a shift-invert spanning 1.05→2.6 GHz: **over an hour per point**.
  Retargeted, the same measurement took ~2 minutes.
- **E0l's original scaling curve used a 10.7 s toy**; production solves are 106
  minutes at 1 rank. The toy said 32 ranks were 37% efficient and fan-out was
  worth 1.8×. Reality: **87% and 4%**. A benchmark 600× too small does not lose
  precision, it **inverts the answer**.
- λ/4 was predicted as the optimal groove depth. It is where the slot resonates
  and therefore the depth to **avoid** — right physics, wrong design goal.

## 6b. A model does not just predict values — it allocates the sampling budget

⚠️ **A directionally wrong model is more expensive than no model**, because it
concentrates effort confidently in the wrong place. No model gives you a spread;
a wrong model gives you a cluster.

H2 sampled groove depths 0, 10, 20, 27, 31, 34, 42, 52 mm. That was not
scattering — it was a deliberate cluster around `Z₀·tan(βd)`'s predicted optimum
at λ/4 = 30.59 mm. The model was right that λ/4 is special and wrong about the
SIGN of its usefulness: it is where the slot resonates and Q collapses to ~3,000,
the depth to AVOID. Result:

| gd | d/(λ/4) | outcome |
|---:|---:|---|
| 0 | 0.00 | control — measures nothing (the reference is analytic) |
| 10, 20 | 0.33, 0.65 | the only two usable points |
| 27, 31, 34 | 0.88–1.11 | at λ/4, Q collapsed |
| 42, 52 | 1.37, 1.70 | past the pole; 52 never converged |

**Five of eight cases landed in the unusable region.**

✅ Before committing a sweep, ask what the model says about WHERE IT IS VALID,
not only where the optimum is. A perturbation theory (Slater) concentrates
sampling where the design lives and degrades honestly as you approach the
resonance; a pole-seeking transmission-line model points AT the pole and says go
there.

## 6c. Ask whether the instrument CAN answer, not only what it costs

*"A cheap instrument that cannot answer the question is not cheap."*

H3's loaded-cavity sweep was built as EIGENMODE because eigen is cheap
(155–882 s) and returns Q directly, making η = 1 − Q_loaded/Q_bare a one-solve
measurement. Driven costs 2,500–2,900 s. The reasoning was entirely about COST.

🔴 It stalled at **nconv = 0** after 65 minutes on the WEAKEST point of the grid.
A bulk lossy volume (tan δ ≈ 3) puts strong frequency dependence into the
OPERATOR, where the wall's surface impedance was only a boundary term, and NLEPS
cannot do it. The same cavity without the plasma solves in 155 s.

⚠️ **INSTRUMENT already said so, in this programme's own words** — *"driven has
no NLEPS, therefore no convergence cliff; the geometries where the eigensolver
diverges are exactly where driven should still work."* The limitation was
recorded. Nothing checked it, and the cost argument never met it.

✅ Before choosing a solver, ask in this order:
1. **CAN it represent the physics?** (a lossy volume is not a lossy boundary)
2. **CAN it converge on this class of problem?** — a separate question from (1),
   and the one `solvecost` cannot answer: it predicts the time of solves that
   converge, and says nothing about which converge at all
3. only then, what does it cost

🔴 **AND THEN I OVER-CORRECTED, WHICH IS THE OTHER HALF OF THE LESSON.** From
that one stall I wrote "the eigensolver cannot handle a bulk lossy plasma" into
INSTRUMENT as measured fact, and made `run()` REFUSE the combination. A
four-case probe showed the stall was **the shift target** — I had placed it
300 MHz below the mode "because loading pulls DOWN", and an overdense plasma
(ε<0, conductor-like, field-excluding) pulls **UP**. Eigen converges across the
whole intended range in 89–284 s.

⚠️ So the sequence was: choose on cost, fail, then generalise the failure into a
capability limit — **n = 1 in both directions.** The refusal in `run()` is now a
WARNING, not a refusal, because the premise it enforced was false.

🔑 Enforced, correctly this time: `run()` takes an explicit `timeout`, and a
lossy-eigenmode config prints what it is about to attempt rather than blocking
it. Checked in `run()` rather than `eigen_cfg` because eigen_cfg only ever
writes vacuum — callers mutate `Materials` afterwards, which is exactly how the
plasma got in. See §7.

🔑 And the budget is now LIVE. `solvecost.NLEPS_BUDGET` existed but was read only
AFTER `run()` returned, so a stalled solve still burned its full timeout —
65 minutes where the budget would have cut at ~1,000 NLEPS iterations. **A guard
that fires after the cost has been paid is a report, not a guard.** `run()` now
polls the log and kills the tree, raising a DISTINCT "did not converge within
budget" — missing data, not a bad result.

## 6d. Sample in the groups the equations fix, not the units you measure in

**User instruction, 2026-08-23: sample-point selection must not be influenced by
priors.** The way to guarantee that is not willpower — it is coordinates.

A grid laid out in RAW UNITS imports priors through its BOUNDS, silently:

- H3 swept plasma radius 2 → **8.5 mm**, and 8.5 mm is the INHERITED BORE — a
  number `OPTIMIZER.md` marks ASSUMED, doubly. The hypothesis was reposed
  specifically so the torch would not be assumed, and the assumption walked back
  in through the upper limit. **A sweep cannot produce a requirement that exceeds
  its own range**, so as built it could never report that the bore was too small.
- The n_e range came from a temperature estimate — another prior.

✅ **Sample in the dimensionless groups whose transitions the EQUATIONS fix.**
For a plasma in a cavity those are

    PI_1 = omega_p / nu_m   -> the sign of eps_eff (eps crosses 0 at wp = nu)
    PI_2 = R / delta        -> field penetration (delta = sqrt(2/(w mu sigma)))

Neither is a guess about the answer; both fall out of the constitutive relation.
Place points **log-symmetric about PI = 1**, which is agnostic about which side
the answer lies on — that is what makes it prior-free.

🔑 **And DIAGNOSE a proposed grid by expressing it in those groups before
running it.** H3's grid, so expressed:

| | below transition | above | nearest to it |
|---|---:|---:|---:|
| PI_2 | 3 of 8 | 5 | 1.03 ✅ |
| PI_1 | **2 of 8** | 6 | **0.56 / 1.78** 🔴 |

PI_1's transition was STRADDLED BUT NEVER SAMPLED — and it is precisely where
eps changes sign, where the div-free PCG fails, and where the sustaining
question lives. Two minutes of arithmetic would have shown that before 2.6 hours
of solving.

⚠️ The groups are NOT independent once geometry is imposed: at PI_1 = 0.1 the
skin depth is 109 mm, larger than the cavity radius, so PI_2 ≈ 1 is
geometrically unreachable there. That constraint is itself a finding, and it is
invisible in raw units.

✅ **CONFIRMED BY MEASUREMENT 2026-08-23, and it was a prediction.** This section
said PI_1's crossing is *"precisely where eps changes sign, where the div-free
PCG fails"* — written from the constitutive relation, before any of it was
measured. Then measured, on adjacent densities in one rig:

| ne | Drude eps | PCG |
|---:|---:|---|
| 1e18 | **+0.689** | solves, 281 s |
| 1e19 | **−2.109** | 🔴 92 non-convergences, reduction factor 1.007 |
| 1e20 | −30.089 | ✅ 0 non-convergences, factor 0.814 |
| 1e21 | −309.9 | solves, 100 s |

The failure is at **small |eps|**, not large: −30 and −310 are both healthy. The
auxiliary-space preconditioner needs a definite mass term and eps→0 removes it.

🔑 So the dimensionless group did two jobs: it told us where to SAMPLE, and it
told us where the INSTRUMENT CANNOT GO. Those turned out to be the same place —
which is worth knowing before a grid is committed, not after 2.6 hours of
solving. ⚠️ A second, unrelated regime also breaks the same preconditioner:
a high POSITIVE eps beside a strong negative one (sapphire eps=+11.6 against
plasma −30.09 stagnates; quartz +3.78 does not). Do not merge the two — they
share a symptom, and joining them by symptom is exactly how the wrong mechanism
got written down first.

This is [[design-is-dimensionless]] — already a standing project principle —
applied to SAMPLING rather than to scoring. Millimetres hid the lambda structure
once; they hid the transition structure again.

## 7. A checker must be able to see what it checks

Three versions of one scanner, in order:

1. regex over raw text — flagged **the comment documenting the bug** as the bug
2. `preflight.code_only()` — blanks strings, and the flags ARE strings, so it
   found nothing and **printed a clean bill of health**
3. AST walk over list literals — correct

Version 2 is the dangerous one: it passed. **A checker that cannot see its
subject is worse than none, because it is believed.** Give checkers self-tests
with known-bad input — `physics.py`'s caught two hand-typed constants, and
`eigmodes.py`'s caught the Q discriminator firing on PEC noise (Q ~1e15 passes a
ratio test happily).

## 7b. A refactor drops imports, and nothing sees it

Converting a rig from one solver to another removed `eigen_cfg` and `N_MODES`
from its imports; converting it back did not restore them. Both are used INSIDE
functions, so `ast.parse` passes, `python3 -c "import rig"` passes, and the rig
launches — then dies seconds in on the instance, after meshing, with a
`NameError`. Twice in one session.

✅ `preflight` now runs **pyflakes** for undefined names and reports them as
ERRORS. It found the second one immediately, at a line the first crash had not
reached.

⚠️ Delegated rather than hand-rolled, on purpose: scope analysis has to handle
comprehensions, walrus, `global`/`nonlocal` and star-imports, and §7 is the rule
about checkers that cannot see their subject.

🔑 The general shape: **a rig that imports its solver machinery from elsewhere
has a failure mode that only appears at call time on the remote host.** Cheap
static checks belong in the gate, not in the operator's memory.

## 7c. One rig, one solver. Do not parameterise the solver choice.

**User instruction, 2026-08-23, and the evidence for it is one file.**

`h3_loaded.py` was converted eigenmode → driven → eigenmode as the solver
question was settled. Every conversion left something behind:

| left behind | cost |
|---|---|
| `eigen_cfg` import dropped | failed launch |
| `N_MODES` import dropped | second failed launch |
| `Q_BARE` renamed, one reference missed | third failed launch |
| docstring still asserting "loading pulls DOWN" | a RETRACTED claim printed as fact at runtime |
| V1 referencing the empty 44,384 | wrong reference for a driven solve, which needs the with-loop 29,854 |

None of these were physics errors. All of them were a file trying to be two
things, and the last two are worse than crashes: they were WRONG and they RAN.

✅ **Write a driver per solver.** `h3_eigen.py` and `h3_driven.py`, not one rig
with a `mode` branch. The two differ in more than a config call — they differ in
what reference Q means (no loop vs loop, 44,384 vs 29,854), in what identifies a
mode, and in what the declared criteria have to say. A branch hides all of that
behind one name.

🔑 This is §10 (separate the driver from the analysis) applied one level up:
**duplicate the DRIVER, share the ANALYSIS.** Two drivers emitting the same
record shape, one analysis layer reading both, is cheaper than one driver with a
switch — and re-analysis stays free either way.

⚠️ A genuine need for both solvers is not a reason to merge them. H3 needs eigen
outside the indefinite band and driven inside it; that is two drivers and one
map, not one driver with an `if`.

## 7d. Two values from ONE source cannot disagree

*"Verify with the thing that CONSUMES the value, not the thing you just changed."*

§7 says a checker must be able to see what it checks. This is the sharper form,
and it is subtler because **these checks all PASS**. If the check and its subject
are derived from a single source, agreement is arithmetic, not evidence — and a
green check is more dangerous than a missing one.

**Four instances, all on 2026-08-23.** Three were guards; the fourth was a
measurement, which is why the rule is not only about checkers.

| the check | what it compared | why it could not fail |
|---|---|---|
| `check_torch_bound` in `run()` | config eps vs **sidecar** eps | the rig BINDS the config from the sidecar |
| pyflakes on the instance | `ssh python3 preflight.py` | that is `/usr/bin/python3` — **the interpreter apt had just fixed**; rigs run the env's 3.12 |
| `h3_annular` power density | `pd` vs volume ratio | `pdens = eta * P_REF / vol` — pd is DEFINED ∝ 1/V |
| `h4_field` V2 gate | widened 5% → 20% | to accommodate a broken check, so it measured the bug's size |

Each one passed. The torch guard let four vacuum-tube meshes through the run it
was written to protect. The pyflakes check went green while the gate stayed
blind. The power-density "confirmation" of a committed 1.067×/1.125× prediction
was guaranteed the moment η did not move — I reported it as a hit on a
prediction, and it was a restatement of a definition.

✅ **The check must see a value the subject did not supply.** For the torch that
is the REQUEST — bind from the mesh (R101), *then assert the mesh is what was
ordered*:

    if abs(float(sidecar_eps) - requested_eps) > 1e-9:  refuse

✅ **Before sweeping a derived quantity, grep its assignment.** If the swept
variable appears on the right-hand side, the sweep plots a formula and the
solver only supplies a constant. `pdens = eta * P_REF / vol` reads like a
measurement in every table it appears in.

✅ **Verify by running the consumer.** Not a command that resembles it — the one
the system actually executes, in the environment it executes in.

🔴 **The harness bug this exposed, which had been live for the life of the
scripts:** `ops/remote.sh` LINTED with `/usr/bin/python3` and LAUNCHED with
`source /opt/amip/env.sh && python3` — **two different interpreters**, different
versions and different packages. The gate was certifying an environment the rig
never executes in. Both now source `env.sh` first.

⚠️ And tools the rigs need go in `/opt/amip/envs/emsim` via its own pip, never
apt: the root filesystem is wiped by every spot reclamation, the volume is not.
A fix that does not survive reclamation is not a fix, it is a delay.

## 7e. A print is where a claim escapes review

**Three instances on 2026-08-23, all in runtime strings, none in analysis.**

| rig | the string | what happened |
|---|---|---|
| `h3_superpose` | *"as predicted: the dielectric concentrates the field where the plasma sits"* | the mechanism was **FALSIFIED** hours later |
| `h4_field` | *"an ordinary second-order cross-term needs no claim about the sign"* | true when written, **stale within the hour** once the mechanism was measured |
| `h3_superpose` | *"Extrapolating it to sapphire is justified"* | it is **1.9× past the last point**, and the points beyond are unmeasured *because* the instrument cannot reach them |

🔑 **Analysis gets re-read and re-scored (§10). A hardcoded string does not.** It
is written once, in the mood of the moment, and then printed as fact on every
future run — including runs whose own data contradicts it. §7c already recorded
the worst form of this (a docstring asserting a RETRACTED claim at runtime); this
is the same failure in `print` rather than in `"""`.

✅ **A verdict string states WHAT WAS MEASURED and OVER WHAT RANGE. Never what it
implies.** The implication goes in FINDINGS, where it can be retracted without a
code change.

✅ Concretely, the fixed form: name the interval, quantify the drift rather than
calling it flat, and label anything outside as extrapolation *with its factor*:

    ✅ CONSTANT within 5 points OVER eps 2-6 — a LAW on that interval
       ⚠️ drift +0.30 points per step; NOT flat, just nearly so.
       ⚠️ eps 8, 11.6 are OUTSIDE the interval. Applying the law there is an
          EXTRAPOLATION (1.9x past the last point), not a measurement.

⚠️ The tell is the tense. "as predicted", "is justified", "needs no claim" are
all **conclusions**. A rig may print measurements, ranges, and which falsifier
fired — the reasoning about what they mean is not its job.

## 7f. A frozen parameter is not a removed part

*"Settled" became "absent" because the settled value never entered the baseline.*

🔴 **the groove omission, 2026-08-23 — the worst error of the session, and it invalidated the
scope of a day's work.** The cavity design is premised on a mode filter. `GEO`,
the shared geometry baseline that **31 rigs** inherit, never passed `--groove`.
Every loaded solve — H3, H6, the suppression law, sapphire, loop sizing — meshed
`groove = [0.0, 0.0]` and produced design numbers for a cavity nobody is
building. The headline results were all ABOUT THE MODE LANDSCAPE, which is
exactly what a mode filter changes.

**How H2's retirement caused it.** H2 was retired with the groove *frozen at
5×10 mm* and "its variables have left the design space". That is correct as a
statement about the SEARCH. It was silently implemented as leaving the GEOMETRY.

✅ **When you freeze a design parameter, write it into the shared baseline at its
frozen value, in the same edit that freezes it.** A frozen parameter is more
load-bearing than a swept one, not less: nothing will vary it again, so nothing
will notice it is missing.

### Why every guard missed it

- Nothing crashed; a groove-free cavity solves perfectly well.
- Cross-checks between rigs **agreed** — they shared the baseline, so they shared
  the defect. **Agreement between two things that inherit the same default is not
  validation** (§7d again, at the level of the geometry).
- The sidecars recorded `groove: [0.0, 0.0]` faithfully, every time. Nobody read
  a field that had never been interesting.

⚠️ **And a NAME made it worse.** Two parts share the phrase "mode filter":
`--mode-filter <t>` is the **quartz annulus, RETIRED**; `--groove <w,depth>` is
the **annular slot, CURRENT**. A reader checking "is the mode filter on?" finds
`--mode-filter 0`, reads it as a deliberate choice, and stops looking. **When a
part is superseded, the retired flag must not keep the generic name** — or every
future check answers the wrong question confidently.

✅ Enforced: `GEO` writes `--groove 0,0` EXPLICITLY (declaration, not omission),
`GEO_DESIGN` carries the frozen 5×10, and `run()` REFUSES a plasma solve on a
groove-free mesh unless the caller passes `allow_no_groove=True` and says why.
🔑 The plasma is the tell: a bare cavity is right for instrument rigs comparing
against closed form, and never right for a loaded design measurement.

🔑 **The general shape: ask what the DESIGN requires that the BASELINE does not
carry.** Defaults encode the state of the programme when they were written, and
the programme moves. Re-read the shared baseline against the current design
whenever a hypothesis retires.

## 7g. Do not mint revision numbers. The register IS the failure mode.

**2026-08-23, user-caught, and it is the most important entry in this file.**

`README.md` says why the previous programme was abandoned:

> *"Its register grew by generating its own questions: R99→R101→R103→R105→R106→
> R107→R109→R110→R111→R112→R113, each opened by the previous result's
> uncertainty. **An inward-facing loop with no external anchor can only
> expand.**"*

🔴 **I reproduced that failure exactly, in one session.** I minted "R113" for my
own finding — **colliding with the real R113** (`geometry.py`, the falsy-numeric
`--viewport 0` fix) and corrupting the citation chain — and "R112b", inventing
descent from the PORT fix for a TORCH binding whose actual ancestor is R101.

⚠️ **And the numbering was the symptom, not the disease.** Look at what the
session's questions were ABOUT: a continuation seed, a coupling branch, a global
minimum, a mesh tag, a dropped material, an interpreter path. **Every one was
opened by the previous one's defect.** Not one came from the machine being built.
Meanwhile the single external fact that governed everything — *the cavity has a
mode filter* — went unchecked for a full day, and a person had to say so.

🔑 **THE LIVE PROVENANCE IS E0 AND H1, because they are the only results anchored
OUTSIDE the programme:** E0 against closed-form mathematics, H1 against an
analytic max-min optimum. A result whose only support is another result of mine
is not evidence; it is the loop expanding.

✅ **Rules:**
- **Never mint an R-number.** They are `geometry.py` code revisions with an
  owner and a chain. Cite a finding by DATE and DESCRIPTION.
- **Before starting work, name the external anchor.** Closed form, a measured
  datum, a published threshold, a hardware constraint, or a person. If the only
  anchor is an earlier result of this programme, the question is inward-facing.
- ⚠️ **Count the provenance depth.** If a conclusion is three or more results
  deep with no external contact, stop and go get contact. Depth is not rigour.
- 🔑 **A long run of self-generated fixes is a WARNING, not productivity.** The
  instrument genuinely improved this session — 12 eigen timeouts to 0 — and that
  is worth keeping. It is still an inward gain, and it did not answer a single
  question about the machine.

## 7h. An append-only archive is not a place to look things up

**User, 2026-08-23, considering deleting `FINDINGS.md`:** *"There is now so much
irrelevant information that it's hard to lock on to what's known and what the
next steps are."*

🔴 Correct, and the append-only rule caused it. 5,000 lines, 76 entries, three
invalidated eras, and **no way to tell live from dead without reading all of
it.** A file in that state is not neutral — it is actively misleading, because
every entry looks equally authoritative and the wrong ones are indistinguishable.

⚠️ Deleting it is not the answer: several invalidations are only comprehensible
against the numbers they replaced, and citations must not break. **But keeping it
readable was never the same as keeping it.**

✅ **Two files, two jobs:**
- **`KNOWN.md` — one page. What is established, and what is explicitly NOT.**
  Every entry names its EXTERNAL anchor. If it is not there, it is not known.
- **`FINDINGS.md` — the archive.** Append-only, for following citations. It
  opens by saying so and pointing at KNOWN.

🔑 **The test: how long does it take a newcomer to learn what is true?** If the
answer is "read 5,000 lines and know which era each entry belongs to", the record
has failed regardless of how correct each entry is. **Correctness per entry is
not the same as usability of the record**, and only the second one compounds.

## 7i. A COMPETING IN-BAND MODE IS AN ALARM, NOT A FINDING

**User, 2026-08-23:** *"alarms didn't really start to go off for me until you
mentioned 'interloper' and 'not tuning to TE'."*

🔑 **In a cavity with a working mode filter there should BE no competing in-band
mode.** That is what the filter is for. H2 measured it: the groove pushes TM111
**64.25 MHz**, clearing the 50 MHz LDMOS band, and the dimensions were frozen at
5 × 10 precisely because that puts every competitor out of the tuner's reach.

🔴 So when I reported, over several hours:
- a mode "19× deeper than TE011" breaking my analysis,
- an "interloper" the selection logic kept locking onto,
- "the tuner would not lock to TE011" at every loop size,

**every one of those was the same alarm, and I treated each as a puzzle to be
solved rather than as evidence the cavity was wrong.** I built continuation
selection, a seed rule, depth and edge guards — an elaborate apparatus for
navigating a mode landscape that should not have existed.

✅ **The check, and it is one line:** if a filtered design shows more than one
resonance inside the source's tuning band, **suspect the filter before building
machinery to cope.** Ask what the mesh actually contains.

⚠️ **The tell is machinery.** Needing progressively cleverer selection logic to
find the mode you want is not sophistication; it is the geometry telling you the
mode landscape is not the designed one. **Effort spent coping is effort not spent
checking.**

🔑 Related and worse: a CONTEXT RESET can drop the fact that a device exists
while leaving every downstream number intact and plausible. The design's mode
filter was lost this way — H2's result survived in FINDINGS and stopped being
present in the working set. **After a reset, re-read what the DESIGN contains,
not just what the last session was doing.**

## 7j. Renumbering carries LABELS across CONTENT. Drop, do not swap.

**Traced 2026-08-23, and it is the root of the session's worst failure.**

The sustainment question (cold / hot / loaded) was originally **H2**. It could
not be answered without characterising the groove first, so the two were
**SWAPPED**: groove became H2, sustainment became H3.

🔴 **The swap moved the numbers. The status labels stayed with the numbers.**
Old-H2 (sustainment) genuinely was `premature` — asked before the groove existed
to answer it. That verdict remained attached to the string "H2" and was then
re-rationalised onto the groove, **which had already answered its own question.**

🔴 **Rationalisation invents criteria.** To justify calling the groove premature,
the record acquired a target H2 never had — *"TM111 far enough to draw no
power… depends on plasma loading"* — in place of the real one, the **LDMOS
tuning range**, which H2 had MET (TM111 −64.25 MHz clears the 50 MHz band).
**A harder, unanswerable criterion was substituted for the satisfied one**, and a
completed result became an open question.

### The cost

Believing H2 unanswered made the groove look optional. It never entered `GEO`;
31 rigs inherited a groove-free cavity; a full day of H3 measured a cavity nobody
is building — and the extra in-band modes that resulted were treated as puzzles
rather than as the alarm they were (§7i).

✅ **DROP, do not swap.** When a hypothesis turns out to depend on one that does
not exist yet: **drop everything downstream and re-record the prerequisite as a
fresh question.** A drop forces re-derivation. A swap preserves history that is
now misattached, and **misattached history is worse than absent history because
it reads as authoritative.**

⚠️ If a swap is unavoidable, move the STATUS with the QUESTION, never with the
number — and re-state the criterion explicitly, because a criterion that is not
re-stated will be reconstructed, and reconstruction drifts toward whatever
justifies the label.

🔑 **The general tell: a result that was ANSWERED and is now described as
UNANSWERABLE.** Nothing was measured in between. Go and read what its criterion
actually was.

## 7k. Park surprises. The experiment list does not grow.

**`PLAN.md` has said this since 2026-08-20 and I never opened the file.**

> *"**It does not grow.** Five experiments, each with a verification and a
> falsification declared here before any driver is written. Ordering is by LOD
> dependency, not by curiosity."*
>
> *"**Parked — surprises, NOT register items.** These are recorded so they are
> not lost. **They do not spawn runs.**"*

🔴 On 2026-08-23 I spawned a run from nearly every surprise, invented a
hypothesis (H6) that duplicated an existing regime, and minted revision numbers —
reproducing precisely the register growth `README.md` blames for the previous
programme's abandonment. The mechanism to prevent it already existed, one file
away, with a section heading naming the exact failure.

✅ **A surprise goes in PLAN's Parked list.** It is recorded so it is not lost.
It does not become a run, a hypothesis, or a number.
✅ **Before opening any new line of work, open `PLAN.md`** and find which of
E0–E4 it belongs to. If it belongs to none, that is the signal to park it, not
to extend the list.

🔑 **And E3 already declared the falsifier for delivered power** —
**η_total = η_plasma + η_wall + η_dielectric must close within a few percent, or
only η_total may be quoted.** I reported "net into plasma" figures all session
without ever running that decomposition. **The check you need has often already
been written down by someone who thought about the question longer than you have
been looking at it.**

⚠️ Read the WHOLE document set before working (KNOWN.md indexes it). Three of ten
documents here went unopened for a full session, and two of them — `PLAN.md` and
`METHODOLOGY.md` — are the ones about not fooling yourself.

## 7l. A strict test on an uncertain classifier discards the measurement

**`h3_cold`, 2026-08-23.** Two eigen cases converged, found their modes, and the
rig reported *"no m=0 mode in the LDMOS band"* — because `azimuthal.order()`
returns `m=None` when a mode is MIXED, and the rig tested `m_az == 0`.

🔑 **The mixing was the physics, not a failure.** Loaded, the in-band mode has
A2/A0 = **0.3244**; the high-Q mode the plasma does not couple to has **0.0004**.
A plasma mixes the triplet. **A symmetry test is a poor discriminator under a
perturbation large enough to mix what it classifies** — E1b's lesson in a new
form.

🔴 **And the cost compounded**: the error path returned before `_report()`, so
**F1 — the filter check, the entire point of §7i — never printed**, on a run that
had the data to answer it.

✅ **Rules:**
- **A classifier that can say "I don't know" must not be consumed with `==`.**
  Report its value AND its confidence; select by a stated rule; FLAG uncertainty.
  Never discard a converged measurement because a label is missing.
- **Verdicts must not be hostage to a missing case.** A report that only runs
  when everything succeeded is a report you will not have when you need it most.
- ⚠️ The fallback must not be "nearest to the expected frequency" — that is §1.
  Use CONTINUATION from a regime where the label IS clean.

🔑 **The general shape: a hard test on a soft output.** The classifier was
honest; the consumer was not built for honesty. Ask what a checker returns when
it is unsure, before writing the comparison.

## 7m. Once the design fixes a feature, a measurement without it is a different cavity

**User, 2026-08-23:** *"Anything measured without grooves after H1 should be
discarded."*

🔑 **H1 fixed the cavity. From that point a groove-free mesh is not an
approximation of the design — it is a different resonator**, and its mode
landscape is the thing most measurements are about.

✅ **The rule, and it is a FILTER to run before believing any number:** after the
design fixes a feature, every measurement must carry it. **The one exception is
an instrument rig comparing against CLOSED FORM**, where a plain cylinder IS the
subject — that is what `GEO` is for, and `GEO_DESIGN` is for everything else.

✅ **Audit by the MESH SIDECAR, not by the flag list or the rig's intent.**
`geometry_mm.groove` is ground truth; a rig can pass a flag that loses to
`--no-torch`-style precedence, and did.

⚠️ Applying it on 2026-08-23 discarded **all 11 h4 meshes** — including the
Slater validation that had looked like one of the session's solid results — and
left `e0k2`'s Q = 44,384 valid only as a BARE-cavity number, never as the design
cavity's η reference.

🔑 **And note what it does NOT discard:** claims about the INSTRUMENT. "Driven
and eigen agree on Q extraction" is true of the solver regardless of cavity. The
split is the same one as §7f — a method claim and a cavity claim can sit in one
sentence, and only the second one dies.

## 7n. Fix the WORD before the next measurement

**User, 2026-08-23: "we need to get the terminology straight, so we're always
talking about the right things."**

🔴 **Four errors in one session were purely terminological**, and none of them
crashed anything:

| word | the two readings | what it cost |
|---|---|---|
| **hot** | "thermally hot cavity, re-ignition" vs "weakly ionised" | H3's third regime was planned as the wrong measurement, and a rig tagged its plasma cases `hot` |
| **mode filter** | `--groove` (current) vs `--mode-filter` (retired quartz annulus) | `--mode-filter 0` read as "deliberately off", so nobody looked for the real flag — the whole loaded programme ran on the wrong cavity |
| **frozen** | "settled, do not re-optimise" vs "removed from the geometry" | the groove never entered `GEO`, AND was treated as immutable when it is a baseline H3 must refine |
| **Q_bare** | which cavity? bare / with-loop / grooved+looped | η computed against a reference 3.6× too high, a defect the record had already documented |

🔑 **Ambiguity is invisible in a working system.** A wrong reading produces
numbers, plots and agreement; only the meaning is wrong, and meanings are not
type-checked. **The cost is paid later and attributed elsewhere** — I blamed the
solver, the mesh, the selection logic and the loop before the word.

✅ **`GLOSSARY.md` is the fix**, and it is short on purpose: each entry gives the
term, what it does NOT mean, and the error it caused. **Read it second, after
KNOWN.**
✅ **When a word turns out to carry two meanings, RETIRE THE WORD** — do not
disambiguate it in prose that the next reader will skip. "Frozen" is banned in
favour of *baseline* / *discarded*; "scope-invalid" in favour of *discarded*.
⚠️ And rename the CODE too. A rig that tags plasma cases `hot` teaches the
confusion to everyone who reads its output.

## 7o. Out-of-range must not bin to a meaningful value

**User, 2026-08-23: "It stands to reason that higher modes wouldn't be
identified... The problem is the binning into 0."**

🔴 `azimuthal.order()` returned **m=0 for TE311 (m=3)** with its highest
confidence. Five sectors resolve only m ≤ N/4 = 1; m=3 folds back and presents
as flat, and the code mapped flat → **0**.

🔑 **The distinction that matters: 0 was not "unknown". It was the answer meaning
TE011** — the exact conclusion the test existed to support. An out-of-range input
was silently converted into the most consequential in-range verdict.

⚠️ **The truncation itself was fine.** `physics.spectrum` enumerates m ≤ 2 and
that is a defensible cutoff — a table you know is truncated is a limit you work
around. **The fault was the classifier's, not the table's.**

✅ **Rules:**
- **A classifier must know its own resolvable range and say so.** `order()` now
  returns `_m_resolvable_max` and `_aliasing_risk` alongside the verdict.
- **Never let out-of-range collapse onto a MEANINGFUL category.** If it must
  collapse, collapse to *unknown* — never to the answer someone is hoping for.
- ⚠️ **Check the aliasing limit from the physics, not from the code comment.**
  `SECTORS`' comment claimed m ∈ {0,1,2}; the true limit is m ≤ N/4 because
  |E|² ~ cos²(mφ) carries harmonic **2m**. m=2 was never resolvable either.

🔑 **And the two limits were the SAME limit.** The classifier's range was chosen
from the incomplete spectrum, so a mode the table could not list was also a mode
the classifier could not label — and it was labelled anyway. **When two
components share an assumption, they do not check each other** (§7d, one level
up: not two values from one source, but two COMPONENTS from one source).

## 7p. A safety margin is a cost, and an unpriced one breaks the solve

🔴 `h3_ladder`'s grooved step **stalled at nconv = 11 of 12** for five straight
samples while the iteration rate collapsed **2.1 s → 56 s** per NLEPS. Eleven
converged modes were about to be thrown away by the wall clock.

🔑 **The twelfth mode was mine.** N=10 covers TE011 and TM111 with slack — five
modes sit below them at this geometry. **I set 12 to also capture TE311 at
2.622 — a mode ALREADY IDENTIFIED from the bare solve.** Padding the ceiling for
a result I already had is what made the marginal mode marginal.

⚠️ **The highest requested mode is the one that stalls.** In shift-invert the
top of the requested set is the worst-conditioned; asking for "a few extra, just
in case" does not cost a few extra percent, it moves the convergence cliff.

🔑 **THE SAME SHAPE FOUR TIMES**, each a parameter widened for safety without
pricing the widening: E0's 0.058 MHz threshold quoted outside its resolution ·
the 636 kHz coarse sweep step · the 307 MHz shift-invert span · N=12 here.
**Every one of them broke the thing it was meant to protect.**

✅ **Rules:**
- **If the budget cuts before the last mode converges, ask for FEWER modes** —
  do not raise the budget. More budget buys more of a stall.
- **Name what each unit of margin is for.** Margin covering a result you already
  have is not margin, it is load.
- **Make the success condition reachable**: N=10 makes `nconv = 10` sufficient.
  A target that requires the worst-conditioned mode has no partial credit.

## 7q. A wrong label can void a right number

🔴 A converged design-cavity Q₀ of **12,368** was struck from the record —
*"the η reference it printed is void"* — because the rig's azimuthal binning
labelled the mode **m=1**. The number was correct. **The classifier was the thing
that was broken** (§7o), and it took the measurement down with it.

🔑 **Discarding on a classifier verdict destroys evidence the classifier never
touched.** Frequency, Q and field data were all sound and independently
checkable; only the label was suspect. Continuation from the grooved state later
identified the same mode as TE011 and the same 12,368 stood — **a full re-run to
recover a number that had never actually been wrong.**

✅ **Rules:**
- **Quarantine the LABEL, not the MEASUREMENT.** Mark the identification
  disputed and keep f, Q and fields live.
- **Before voiding a result, ask which of its parts the fault can actually
  reach.** "The rig had a bug" is not a scope.
- ⚠️ **Symmetric to §7l.** There, a strict test discarded good data by refusing to
  label it; here, a bad label discarded good data by mislabelling it. **Both
  times the classifier's uncertainty was charged to the measurement.**

## 7r. A number corrected in a document is not corrected in the programme

🔴 Item 1a — the η reference — was answered, written into KNOWN, NEXT, OPTIMIZER
and memory, and **four rigs still had `Q_BARE = 44384.0` hardcoded.** The next
driven run would have divided by the bare cavity and printed a confident,
plausible, wrong η, with three documents nearby saying 12,368.

🔑 **The documents and the code are two stores of the same fact, and only one of
them runs.** Updating the readable one feels like finishing. It is not.

🔴 **Worse than the constant: `h3_driven`'s ANCHORS dict.** It carried
`1e20: Q=163` and `1e18: eta=0.185` — both from the discarded groove-free era,
the second also from the wrong geometry (a 2 mm solid column, not the annulus).
**An anchor from the wrong cavity does not merely fail to help: it VALIDATES a
wrong answer and REJECTS a right one.** No anchor beats a false one.

✅ **Rules:**
- **When a reference value changes, grep for it before closing the item.** The
  constant, its aliases, and anything that IMPORTS it (`h3_sapphire` imported
  `Q_BARE` from `h3_driven`).
- **Guard the value with the configuration it was measured on.**
  `check_eta_reference()` refuses to run when the groove or loop size differs.
  **A per-configuration constant needs a per-configuration assertion.**
- **Empty an anchor set you cannot vouch for.** `ANCHORS = {}` is honest; a stale
  entry is a silent validator.
- ⚠️ **Found by READING the rig before launching it.** The run would have exited
  0 and produced numbers. §8b says a rig is done when the conclusion lands; this
  says a fix is done when the code that consumes it changes.

## 7s. Reasoning added after a measurement is not its provenance

🔴 I recorded the design cavity's TE011 as **"2.440003 GHz, Q₀ = 12,368,
identified by continuation, `h3_ladder` step 3"** — into KNOWN, NEXT, OPTIMIZER,
memory and four rigs' source. **Two things in that sentence were false.**

1. **There is no step 3.** The ladder ran `['bare', 'grooved']` and stopped. I
   had watched it run and still wrote a third step, because the ladder's DESIGN
   had four steps and I quoted the design instead of the result file.
2. **It was not identified by continuation.** `h3_cold` picked it with
   `selected_by: "lowest A2/A0"` on a mode labelled `m_az = 1`. The continuation
   argument (−10.56 MHz vs +43.88 MHz) is **mine, constructed afterwards**.

🔑 **The argument may still be right — that is not the point.** Reasoning that
post-dates a measurement is a HYPOTHESIS about it. Recording it in the
`selected_by` slot overwrites how the number was actually obtained, and the next
reader cannot tell the difference. A driven sweep then found **zero minima**
within ±3 MHz of it, which is exactly the check the real provenance would have
invited and the invented one discouraged.

✅ **Rules:**
- **Provenance is what the rig DID, copied from the result file.** If you cannot
  point at the field, you are quoting your own reasoning.
- **Quote the `selected_by` verbatim**, including when it is a heuristic you no
  longer trust. `"lowest A2/A0"` carries a warning that `"by continuation"` hides.
- **A later argument gets its own line**, marked as argument, dated, and never
  merged into the measurement's description.
- ⚠️ **Check the RESULT FILE, not your memory of the plan.** Designs have steps
  that runs do not.

## 7t. Measure the reference with the instrument that measures the cases

🔴 §7c has now caught the η reference **four times**, each time as a different
wrong constant (44,384 · 29,854 · 12,368-from-another-rig). Patching the constant
has never worked, because the bug is not the value.

🔑 **The reference was always IMPORTED — a different rig, a different mesh, often
a different solver — and then divided into locally measured Q₀.** That ratio
silently carries both discretisation systematics and both selection heuristics.

✅ **The fix is structural: make the reference a CASE in the same run.**
`h3_driven` now sweeps `ne = 0` first — `drude(0, w)` is exactly ε=1, σ=0 — on
the same mesh, with the same solver and the same extraction, and every loaded η
is scored against that measured Q₀. An imported value becomes a CROSS-CHECK,
printed beside it, never the denominator.
⚠️ **It also fixes the seed.** The cold case now supplies the continuation start
empirically instead of hardcoding a frequency from elsewhere.

## 7u. The rig said it did not know, and I supplied the confidence

🔴 `h3_cold` recorded, on the same point, all of:
`selected_by: "lowest A2/A0"` · `m_az: 1` · **`identification_uncertain: True`**.
I took the frequency and Q from it and wrote **"TE011, identified by
continuation"** into five documents. A driven locator later found the real
resonance **11.5 MHz away**, and 2.440003 has no dip at all.

🔑 **The rig was honest. The flag was there, in the same object, one key above
the number I quoted.** Nothing was hidden and nothing had to be inferred —
`identification_uncertain: True` is not subtle. I did not look, because the
number was the thing I needed and it was right there.

🔴 **AND I BUILT A STORY THAT MADE IT FIT.** Purity 0.9423 concentrated inboard,
φ-structure aligned with the loop at φ=36°, a −10.56 MHz pull that beat the
+43.88 MHz alternative — mechanism, location and cause, mutually reinforcing.
**All of it about a mode the rig had labelled m=1.** The story did not survive
one question the port could answer directly.

✅ **Rules:**
- **Read the uncertainty fields before the value fields.** If a rig emits a
  doubt flag, it is part of the number, not metadata about it.
- **A coherent explanation is not corroboration.** Ask what OBSERVATION would
  differ if the identification were wrong, then make that observation. Here it
  cost one sweep.
- **Prefer the measurement that can say NO.** Purity, A2/A0 and continuation all
  scored a candidate. The locator asked "where is it?" and admitted the answer
  "not where you think" — which is why it was the one that worked.
- ⚠️ **When you find yourself supplying confidence a rig withheld, stop.** That
  is the whole error, and it has now happened with a label (§7q), a provenance
  (§7s) and an identification (here).

## 7v. An unassigned boundary is a CHOSEN boundary

🔴 Eigen and driven disagreed about the design cavity by **11.5 MHz** and neither
was wrong. The mesh has `port = 91`; the eigen config assigns a BC to
**attribute 90 only**. An unassigned boundary is **PMC** — the NATURAL BC of the
curl-curl E formulation (n × H = 0). PEC is the ESSENTIAL one and must be
imposed. **So every eigen solve on a looped cavity left the feed gap OPEN.**

🔑 **An open gap plus the loop is an LC resonator**, and it lands near 2.45 GHz
and hybridises TE011 into a pair (2.4400 / 2.4944, purity ~0.94, near-equal
spreads). Short the gap and the loop is a small closed ring resonant far above
the band, which barely perturbs anything: TE011 reads 2.4516, **P = 0.9997**.
Terminate it in 50 Ω and eigen matches driven to **12 kHz**. **Same mesh, same
geometry, same solver — three different cavities, selected by one absent line.**

⚠️ **I FIRST WROTE THE MECHANISM BACKWARDS**: "Palace defaults to PEC, so eigen
SHORTS the loop." The conclusion was right (different cavities; the port BC is
the cause; GATE 4 is the fix) and the physics was inverted. **A correct
conclusion resting on a wrong mechanism will mispredict the next case** — it
would have had me expect a shorted loop to be the harmful one, when shorting is
the benign approximation.

🔴 **THE FAILURE IS SILENT IN BOTH DIRECTIONS.** Nothing errors. The eigen solve
converges, reports plausible frequencies and Qs, and `h3_cold` even flagged
`identification_uncertain` for an unrelated reason. There is no message anywhere
saying "the port was not terminated" — the default IS the assignment.

🔴 **AND THE GATE THAT EXISTED IS WHY IT WAS INVISIBLE.** `eigen_cfg` already
carried **GATE 3**: *"every volume attribute gets vacuum, and we ASSERT none was
missed"* — and its check reads `k not in ("wall", "port")`, skipping surfaces as
out of scope. **The port was excluded from the volume gate as a surface, and no
surface gate existed.** A partial audit reads as an audit. **The presence of a
check made the uncovered case look covered.**

✅ **Rules:**
- **Enumerate every attribute in the mesh and assert each has an intended BC.**
  Not "did I set the ones I meant to" — "is every face accounted for".
  ✅ Implemented as **GATE 4** (2026-08-24): `port_bc` has NO default;
  `lumped` (50 Ω, the machine) / `pec` (shorted, and it says so) / `absorbing`.
  A looped mesh without it is refused. It correctly refuses 10 existing rigs.
- ⚠️ **When you add a gate, write down what it does NOT cover.** GATE 3's own
  exclusion list was the map to the hole, and nobody read it as one.
- **A default is a decision made by someone who was not looking at your problem.**
  Write it explicitly even when the default is what you want, so the next reader
  sees a choice rather than an absence.
- **Cross-solver agreement is not a free check.** Eigen and driven share a mesh
  and a geometry; they do NOT share boundary conditions, excitation, or what
  "the cavity" means. Compare them only after listing what differs.
- ⚠️ **When two instruments disagree by far more than either's error bar, suspect
  the PROBLEM DEFINITION before the numerics.** I spent the first pass looking
  for a meshing artifact and an interference blend — both plausible, both wrong —
  because I assumed the two solvers were asked the same question.

## 7w. A falsifier can fire for a reason its author never enumerated

🔴 `h3_step3` declared F3: *"if NEITHER mesh has an eigenmode near 2.4515, the
driven dip is not a cavity eigenmode, and `h3_driven`'s loaded series is
measuring something the eigen formulation does not contain — its eta column is
SUSPECT."* **F3 fired. Its premise was correct and its conclusion was wrong.**

🔑 The driven dip is not an eigenmode *of the shorted-loop problem eigen solves*.
It is exactly the resonance of the problem the MACHINE poses. I had written the
consequence assuming only one explanation for the premise, and the true one was
not in my list of three.

✅ **Rules:**
- **A fired falsifier is a prompt to find the mechanism, not a licence to execute
  a pre-written consequence.** Declaring F/V up front stops motivated reasoning;
  it does not make the enumeration complete.
- **State a falsifier's ASSUMPTION alongside its action.** F3 assumed "not an
  eigenmode" implies "not physical". Written down, that assumption is visibly
  the weak link.
- ⚠️ **Do not let a declared consequence override evidence gathered afterwards.**
  The S11 phase rotated fully through resonance and returned to baseline — a
  textbook undercoupled one-port. That was already on disk when F3 fired.

## 7x. |S11| cannot pick the branch, and the branch FLIPS mid-sweep

🔴 `h3_driven.fit_dip` computed `b = (1 - S0) / (1 + S0)` — the UNDERCOUPLED
branch, hardcoded, with a comment saying `beta<<1 here`. |S11| is identical for
β and 1/β, so that line is a CHOICE presented as a formula.

🔑 **It was wrong for the cold case and right for every loaded one.**

    cold, |S11| = -3.67 dB, Q_L = 7,004
        undercoupled  beta = 0.208  ->  Q0 =  8,462   <- what was returned
        OVERCOUPLED   beta = 4.803  ->  Q0 = 40,645   <- the truth
    eigen, from first principles (no |S11|, no phase):
        Q0(port PEC) = 43,523 ; Q_L(port 50 ohm) = 7,538
        1/Q_ext = 1/Q_L - 1/Q0  ->  Q_ext = 9,117  ->  beta = 4.774

**The cold cavity is OVERCOUPLED; every loaded case is UNDERCOUPLED.** The
plasma drops Q₀ by two orders while Q_ext is geometry and barely moves, so β
crosses 1 during the sweep. **No single branch choice is safe across a density
series**, and a per-rig constant is the wrong shape of answer entirely.

🔴 **THE COLD CASE WAS THE η REFERENCE**, so one wrong branch there shifted every
η in the run (0.9295 → 0.9853 at ne=1e18). ⚠️ f₀, Q_L and linewidths were
unaffected — they never depended on β. **The measurement was sound; the
interpretation was not.**

⚠️ **AND I MISREAD THE PHASE CHECK.** I compared two WRAPPED phase values 6 MHz
apart, saw −3.9° and +6.2°, and called it "returns to baseline → undercoupled".
Unwrapped, the phase advances **~326°** — overcoupled. `e0k2_anchor.
branch_from_phase` exists to do exactly this and I eyeballed it instead (§7a).

✅ **Rules:**
- **Return BOTH branches and make the caller resolve one.** `fit_dip` now emits
  `beta_undercoupled`, `beta_overcoupled`, `Q0_if_*` and `branch: UNRESOLVED`.
- **Resolve it with something that is not |S11|**: unwrapped phase, or a pair of
  eigen solves (`port_bc="pec"` for Q₀ and `"lumped"` for Q_L → Q_ext → β).
  The eigen route needs no phase and no fitting at all.
- **Never let a branch constant be a per-rig setting.** It is a per-CASE
  property that can change inside one sweep.
- ⚠️ **A comment asserting the regime (`beta<<1 here`) is not a check.** It was
  true when written and became false without anything failing.

## 7y. A rig must not act when it is merely read

🔴 `h4_reanalyse.py` had no `if __name__ == "__main__":` guard. Its analysis —
including `h4_field._report(...)`, which **rewrites `h4_field.result.json`** —
ran at module level. **Any `import h4_reanalyse` silently regenerated a result
file.** Found by import-checking the tree after a rename, not by anything failing.

🔑 **The danger is not the wasted work, it is the WRITE.** A result file that
can be rewritten by an unrelated import has no provenance: its mtime, and
possibly its contents, depend on who imported what and when.

✅ **Rules:**
- **Every rig ends with `if __name__ == "__main__": main()`.** No exceptions for
  "it's just a re-scoring script" — those are the ones that write.
- **Import-check the whole tree after any rename or signature change.** One pass
  caught this, a broken `Q_BARE` import in `h3_loopsize`, and confirmed the other
  ~40 modules were clean.
- ⚠️ **Analysis layers are rigs too.** `h4_reanalyse` is exactly the
  "separate measurement from evaluation" layer the record asks for — and it
  still needs the guard, because it produces a file.

## 7z. A binary falsifier passes on a meaningless effect size

🔴 `h3_margin` F1 asked: *"if NO cell clears the band by more than the anchor's
9.6 MHz, geometry cannot fix the margin."* One cell reached 10.0. **F1 did not
fire.** The honest reading is the opposite: the best cell beat the design point
by **0.4 MHz** across a 5× loop-area and 2× groove-depth search, and the ENTIRE
12-cell grid spans **0.7 MHz**. Geometry cannot fix the margin.

🔑 **The falsifier tested the SIGN of an effect when the question was its SIZE.**
Written as a threshold it was satisfiable by noise, and it would have licensed
"F1 does not fire → geometry helps" — a true sentence and a false conclusion.

✅ **Rules:**
- **State the effect size that would MATTER, not just the direction.** F1 should
  have read "…by more than N MHz", with N argued from the tuner's real tolerance.
- **Always report the SPREAD of the whole sweep beside the best cell.** One
  number cannot distinguish a real optimum from a flat surface with noise on it.
- **Compare against the next lever, not only against the baseline.** 0.4 MHz
  from geometry is only legible next to 16.2 MHz from operating density.
- ⚠️ Related to §7l and §7q: a strict test on an uncertain quantity discards
  data; a *loose* test on a precise one manufactures a finding.

## 7aa. First-versus-last cannot see a turning point

🔴 `h3_margin` F3 tested `row[-1] < row[0]` and printed **"deeper helps"** for
9.3 → 9.6 → 9.4. The truth is a **PEAK at 10 mm**. The endpoints were nearly
equal and the interior held the entire result.

🔴 **THIS PROGRAMME HAS NOW HIT THREE TURNING POINTS AND MISREAD TWO:**
- **groove DEPTH scaling** — a power law was fitted, then retired when the local
  exponent fell 1.22 → 0.78. *"It is not a power law, so fitting one was
  answering the wrong question."*
- **Q_ext vs loop area** — I read "saturating" from exponents −0.65 then −0.27,
  and it was the approach to a **minimum at 176 mm²**; Q_ext then RISES.
- **groove depth vs loaded margin** — first-vs-last called a peak a trend.

🔑 **A monotonic summary of a non-monotonic quantity is not an approximation, it
is the wrong answer** — it points the optimiser in a direction that does not
exist, and it extrapolates confidently past the turn.

✅ **Rules:**
- **Report `argmax`/`argmin`, never endpoint comparisons.** If the extremum is
  interior, say "OPTIMUM at x", not "increasing" or "decreasing".
- **Three points is the minimum that can SEE a turning point and cannot
  characterise it.** Treat an interior extremum on three points as a flag to
  measure more, not as a located optimum.
- ⚠️ **Never extrapolate through a turn.** The β = 1 loop-size estimate is valid
  only on the small-area branch, and saying so is part of the number.

## 7ab. A value chosen for SOLVABILITY became "the operating point"

🔴 **`ne = 1e20` has no physical provenance. Its provenance is that the eigen
solver converges there.** User, 2026-08-24: *"an estimate from an earlier
session. As far as I know, it has no provenance."* The code says so plainly:

    h3_eigen    : PI_1 = wp/sqrt(w^2+nu^2); measured SOLVER behaviour --
                  0.02..0.56 converges | 1.76 FAILS | 5.58..17.6 converges
    h3_annular  : NE = 1.0e20   # PI_1 = 5.58, the row h3_eigen proved solvable
    h3_superpose: NE = 1.0e20   # the row h3_eigen and h3_annular both proved
                                # solvable
    h3_groove / h3_sapphire / h3_loopsize : NE = 1.0e20   (no comment at all)
    h3_driven   : top of the density grid
    h3_margin   : NE = 1.0e20   # the operating point   <- I wrote this TODAY

🔑 **SIX STEPS FROM "the solver converges here" TO "the operating point", and I
completed the laundering myself.** Each step was individually reasonable: cite
the rig that proved it solvable, then cite the rig that cited it, then stop
citing anything. **No step introduced the claim; the claim accumulated.**

🔴 **AND THE SOLVER'S BLIND SPOT IS AT THE INTERESTING DENSITY.** PI_1 = 1.76
fails, which maps to **ne ~ 1e19** — the density that gives a 25.8 MHz band
margin against 9.6 at 1e20. **The one place eigen cannot look is the place the
design would prefer to be.** (Driven works there, which is why it could be
measured at all.)

✅ **Rules:**
- **A value picked for numerical convenience must carry that label FOREVER**, in
  the constant's own comment, not in the docstring of the rig three steps back.
- **"Proved solvable" is not "is the case."** When a sampling point is chosen
  from convergence behaviour, the physical value remains UNKNOWN and every
  result at that point is *conditional*, not *operating*.
- **Grep for the value before calling anything "the operating point."** If no
  file states where it came from, it came from nowhere.
- ⚠️ **Check whether the solver's unusable band overlaps the region of
  interest.** If it does, that is an instrument limitation to report, not a
  region to quietly avoid sampling.

## 7ac. Do not mix a verified analysis with an unverified suggestion

🔴 I evaluated four PIN-diode datasheets against a 2.45 GHz requirement —
capacitances, package inductances, self-resonances, thermal limits, all computed
from stated numbers — concluded none worked, and then in the same breath offered
*"motorised waveguide stub tuners at 2.45 GHz / kW are an established product
class for exactly this application."*

🔑 **That last sentence had no datasheet behind it.** It came from general
knowledge, was never checked against the VSWR ~100 / 1 kW requirement, and was
delivered in the same register as the computed results. **A reader cannot tell
which parts of that message were measured and which were asserted.**

⚠️ **The rejections were the finding; the suggestion was not.** User, 2026-08-24:
*"if anything SOURCE would need to say that magnitude tuning is an unsolved
problem so far, and why the suggested options wouldn't work."* Correct — an
unsolved problem, honestly bounded, is worth more than a plausible answer,
because the next person acts on it differently.

✅ **Rules:**
- **Mark the register when it changes.** "Computed from the datasheet" and "I
  believe this class exists" are different claims and must not share a paragraph
  unlabelled.
- **A negative result is a result. Do not soften it with an unverified positive.**
  The urge to end on a solution is what produces the unchecked sentence.
- **When recording, write what was RULED OUT and why.** Untested directions go in
  a list explicitly marked untested, never as a recommendation.
- ⚠️ Same shape as §7u (supplying confidence a rig withheld) and §7s (reasoning
  becoming provenance): **the failure is always presenting a weaker claim in the
  register of a stronger one.**

## 8. Land results in files, immediately

A spot reclamation killed the instance mid-run. H1, H2 and H2b wrote their result
files only after the last case, so an interrupt lost every completed case.

✅ **Checkpoint after every case**, atomically (temp file + `os.replace`), so an
interrupt during the write leaves the previous complete file.
✅ Write conclusions to FINDINGS **as they are obtained**, not at session end.
H2's table survived only because it was transcribed by hand from a log on a
machine that no longer existed.

### 8b. The other half: the DATA can survive perfectly and the CONCLUSION still be lost

🔴 `h3_eigen` finished 2026-08-22 21:37 and `h3_annular` 23:30. Both exited 0 and
wrote complete `result.json` files. **Neither was fetched. Neither got a FINDINGS
entry.** `HYPOTHESES.md` went on reading *"H3 — NOT STARTED · THE SOLE GATE"* for
a day, and every session that read it repeated that the programme's only open
gate was unmeasured — while ~20 converged solves answering it sat on the volume.
It was the USER who said "I think we answered H3", against three documents and a
memory file all saying otherwise.

⚠️ Nothing failed. No interrupt, no reclamation, no corrupt file — the persistent
EBS did its job. The rule above was satisfied *by the rig* and still lost the
result, because it guards the wrong boundary: it protects data from the machine,
not conclusions from the operator.

🔑 **A rig is not done when it exits 0. It is done when the conclusion is in a
document.** The gap between those two is where a whole hypothesis went missing.

✅ `fetch` + FINDINGS entry are part of the RUN, not follow-up work. Do them
before launching the next rig — a queued rig is how the previous one's result
gets skipped.
✅ **When picking up a restarted session, `ls -lt` the INSTANCE, not just the
repo.** The repo is the stale copy; the volume is where results actually land.
✅ A hypothesis marked NOT STARTED whose rigs exist on disk is a **contradiction
to be checked**, not a status to be read out.

🔴 **AND A DOCUMENT THAT IS NOT IN THE INDEX IS NEVER READ.** `NEXT.md` — the
queue — sat a full day at *"H3 — THE SOLE GATE, and the whole queue now"* while
H3 and H6 were both being answered, because the memory index named four working
documents and there are five. Nobody ignored it; nobody knew it was there.
✅ **If you add a doc, add it to the index in the same edit.** An unindexed doc
is worse than no doc: it is a confident, plausible, stale answer waiting for
someone to trust it.

## 9. Declare verification AND falsification before the run

This is what actually caught things. Every retraction this session came from a
criterion fixed in advance, where it could not be quietly reinterpreted:

- E1b's **sign test** caught the mode pairing twice
- E0kp's *"if the spread is comparable to 1.3–3.3 MHz"* forced a retraction I had
  already written into FINDINGS — it came back at 0.0001× the threshold
- H2's *"TE011 must barely move"* caught the λ/4 hybridisation

Prefer a falsifier that tests the **identification**, not only the physics: H1's
"TE011 Q must exceed TM111 Q" guards the tool that does the picking.

## 10. Separate the driver from the analysis

*"Drivers emit data with provenance; labels and verdicts live in a re-runnable
layer, because that layer is the one that keeps being wrong."*

Every E1b failure was in analysis, and each cost solver hours only because the
two were welded. After splitting, shape A was recovered in **0.334 s** instead of
9 minutes of re-solving, and `resplit.py` later re-scored **nine rigs** offline
after a shared bug — no re-solving either time.

✅ Rigs emit raw data + a manifest with provenance (mesh SHA, seconds, settings).
Analysis reads it. **When a result looks wrong, re-analyse before re-running.**

## 11. Two points cannot establish a scaling law

The groove's depth dependence had two points. `Z₀·tan(βd)` predicts 2.93×,
volume fraction 2.00×, measured 1.72× — below both. Two competing derivations
agreed with each other and disagreed with the data, which is only visible with
enough points to fit an exponent.

## 12. Housekeeping that has bitten

- **`.gitignore` trailing comments do nothing.** `*.msh  # 4.8 GB` is a literal
  pattern matching nothing. Verify with `git check-ignore` against real paths.
- **`grep -c` exits 1 on zero**, so `cmd || echo 0` prints twice.
- **Numeric flags: guard on `is not None`.** `if a.viewport:` made
  `--viewport 0` silently impossible once the default changed.
- **The instance address lives in `ops/env.sh`.** It was hardcoded in 29 places
  when a spot reclamation changed it.
- **Apertures default ON.** `--viewport` and `--trap` were live in E1b because
  R98 changed a default. Gate them explicitly, as `e0_solver_vs_math` does.
