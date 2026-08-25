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

### ⚠️ 7t-bis. Citing §7t is not the same as CHECKING which case is the control

🔴 **2026-08-24.** I landed E3 case B, correctly refused to quote it against
`h3_loopq` **citing §7t**, and named case E as the matched control — **from
memory, without opening the case matrix.** `e3_closure.py` line 115 says
`E_vac_torch = (wall=True, plasma=True, diel=True, VACUUM)`. **E carries the
plasma; B does not.** They differ in two variables. The rig's own torch-shift
line had it right all along: **A − E**, the matched all-loss pair.
🔑 **The consequence was not cosmetic.** A and E BOTH carry plasma, and plasma is
what breaks the preconditioner — so the torch shift is **not measurable by this
rig at all**, not "waiting on one more case". **Naming the wrong control hid a
blocker behind a delay.**
✅ **Invoking a rule proves you remembered the rule. It does not prove you
applied it.** The case matrix is eight lines; read it.


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

## 7ad. Coupled state variables set as independent constants

🔴 The plasma model carries **`NE = 1.0e20`** and **`NU_M = 1.0e11  # N2 at
1 atm`** as two separate constants. **They are not independent.** ν_m =
n_gas·⟨σ_m v_e⟩ and n_gas = P/kT, so a collision RATE at fixed PRESSURE is a
TEMPERATURE statement — and under LTE that same temperature fixes n_e through
Saha. **One state, three symbols, two of them assigned by hand.**

🔑 **NOTHING ERRORS when they disagree.** The solve runs, converges, and returns
a self-consistent-looking answer for a plasma that cannot exist. This is worse
than a wrong constant: it is a wrong *state*, and no single value is identifiably
at fault.

✅ **AND THE FIX WAS A REFRAMING, NOT A MEASUREMENT.** Saha turns n_e into a
thermometer: **n_e = 1e20 ⟺ T_gas ≈ 6,200 K**, and the whole measured EM grid
spans only 4,650–6,200 K. **An unanswerable question ("what density?") became a
checkable one ("what temperature does the analysis need?")** — answerable by
someone else, with an instrument, in units the application already uses.

✅ **Rules:**
- **Before assigning a constant, ask what else it determines.** If two constants
  are functions of one physical state, deriving both from that state is the only
  coherent option.
- **Prefer the parameterisation the APPLICATION speaks.** n_e is an EM
  convenience; T_gas is what the chemistry specifies and what an instrument
  reads. **Anchor on the axis someone can measure.**
- ⚠️ **Check the sensitivity before trusting a loose spec.** n_e moves two
  decades per 1,500 K here, so "about 6,000 K" is not a tight n_e — but it does
  bracket, which an unanchored density never did.
- ⚠️ **§7ab's sibling.** There the constant had no provenance; here it has no
  *consistency*. Both pass every test the code performs.

## 7ae. A relative quantity needs an origin, and "ΔT = 0" is not a temperature

🔴 `h3_hot` printed **"wall dT = +0 K"** and the user asked, reasonably, whether
that meant absolute zero. It did not — it was a RISE above a baseline. **But the
baseline was never stated anywhere.** `baselines.json` gives wall
σ = 3.5e7 S/m for "bare electropolished aluminium 6061" with **no reference
temperature**, and GLOSSARY defines COLD only as *"cavity at ambient"*.

🔑 **So the sweep was measuring from an unstated origin** — and it matters,
because α_R is itself quoted at 20 °C, so the linearisation needs to know where
it starts. **A ΔT with no T is the same species of unanchored constant as
§7ab's n_e**, just harder to notice because it looks like a well-defined zero.

✅ **Rules:**
- **Report the ABSOLUTE quantity, or state the origin in the same line.** The
  rig now prints `wall T = 293.1 K (20 C), i.e. dT = +0 K`.
- **A stated assumption can be argued with; an implied one cannot.** `T_COLD_K`
  is now a named constant marked ASSUMED, so the next reader can disagree with
  it instead of not seeing it.
- ⚠️ **Suspect every "Δ" in the record for a missing origin.** Δf has one (the
  cold f₀, measured). ΔT did not.

## 7af. GATE 5 — solve the mesh the sidecar describes

🔴 `h3_hot` built `h3_hot_0.msh` and asked the solver for `h3_hot_0_pec.msh`,
because one mesh is solved TWICE (port_bc pec and lumped) and the output tag was
reused as the mesh tag. **Palace returned `rc=1 in 2 s` with no useful message**,
three times, and the run exited 0 having measured nothing.

🔑 **THIS IS THE THIRD TIME THIS EXACT SHAPE HAS APPEARED.** `sweep()` once used
the OUTPUT tag to find the mesh; that was fixed with separate `mesh_tag`/
`out_tag`, the lesson was recorded — **and I reintroduced it in a new rig.**
A convention that is written down but not ENFORCED gets re-broken.

✅ **Now enforced, not remembered:** `eigen_cfg` compares the `mesh` argument
against `meta["mesh"]` — the sidecar records its own source — and refuses on
mismatch. **The metadata and the mesh cannot describe different cavities.**
- **When one input feeds several outputs, the tags MUST be separate parameters**,
  never derived from each other.
- ⚠️ **An opaque `rc=1` is a configuration error, not a solver failure.** Two
  seconds is not enough time to fail at physics.

## 7ag. When methods disagree, ask which one MEASURED something

🔴 A paper reported three plasma temperatures for the same instrument: **5220 K**
(pressure reduction), **12,850 K** (Longerich), **5,910–6,430 K** (Houk &
Praphairaksit). I first read that as a spread and quoted the abstract's
"~5000–6000 K". **User: *"Only one of those methods is empirical."***

🔑 **And that is decisive, not pedantic.** Pressure reduction MEASURES an
interface-pressure ratio with the plasma on and off. The other two infer T from
**the same MO⁺/M⁺ ion-ratio measurement** through different equilibrium models.
**Their 2× disagreement is model spread on identical data** — it says nothing
about the plasma and everything about the models. Averaging them, or quoting
their range, treats a modelling artefact as measurement uncertainty.

✅ **The empirical method was also the one that could be cross-checked**: it reads
5,680–5,780 K on an Ar ICP where independent literature says 5,000–5,280 K.

✅ **Rules:**
- **Classify before combining.** Measurement, model-fit, and calculation are
  three registers (§7ac again). A "range across methods" that mixes them is not
  an uncertainty band.
- **Prefer the method with an independent cross-check** over the method with the
  most sophisticated theory.
- **Look for the shared input.** Two methods that use the same raw data are not
  two pieces of evidence.
- ⚠️ **An abstract's summary range may span registers.** "~5000–6000 K" merged an
  empirical 5220 K with a modelled 5910–6430 K. The table had what the abstract
  did not.

## 7ah. Interpolating across a turning point you already found

🔴 With n_e anchored at 7–9e18 I reported that the tuner requirement "eases
substantially to VSWR ~25–35". **It does not — it rises to 80–89.** The anchored
density sits just BELOW n_e = 1e19, which is exactly where VSWR PEAKS at 99.3.

🔑 **I had measured that turning point myself the same day** (Q₀ minimises near
1e19 and recovers at 1e20) and written it into three documents — then eyeballed
an interpolation straight across it and got the SIGN of the consequence wrong.

⚠️ **The assumed value happened to sit on the FAR side of the worst case.** So
"moving to the truth" moved TOWARD the peak, which is the opposite of the
intuition that a corrected input improves things.

✅ **Rules:**
- **Interpolate in code against the measured grid, never by eye** — the arithmetic
  took one line and reversed the conclusion.
- **When a quantity is known to be non-monotonic, say where the extremum is
  BEFORE quoting any value near it.** §7aa said report argmax; this says USE it.
- ⚠️ **Correcting an input does not reliably improve an outcome.** Expecting it to
  is how a wrong sign survives a sanity check.

## 7ai. Simplify to isolate — then RESTORE. Nothing restored automatically.

**User, 2026-08-24: *"We simplified greatly to answer the instrument and
methodology issues, and then didn't add critical features back."*** That is the
whole mechanism, and it is not carelessness — **the simplification was correct.**
Stripping the cavity to a bare resonator is exactly how you find out whether the
mesher and solver can be trusted, which is what E0 and H1 needed.

🔴 **What failed is that a simplification has no expiry.** Four features came out
and stayed out:

| feature | how it reads in the config | how it behaves |
|---|---|---|
| groove | `--groove 0,0` | no mode filter — 31 rigs |
| port boundary | *unassigned* | PMC = feed gap OPEN — every looped eigen |
| torch | `--torch-material 1.0` or `--no-torch` | no dielectric — every rig |
| gas feed / chimney | `--feed 0,41`, `--chimney 0,41` | **torch sealed in solid metal — every rig, always** |

🔑 **EVERY ONE READS AS "NOT CONFIGURED" AND BEHAVES AS "NOT PRESENT".** A zero
diameter, an omitted flag, an unassigned boundary — none of them looks like a
claim about the machine, and all of them are one.
🔑 **AND EACH WAS CAUGHT FROM OUTSIDE THE RIG** — a person, a cross-solver
disagreement of 11.5 MHz, a downstream rig that NEEDED the missing dielectric,
and a question about where the gas goes. **Not one was caught by the rig that
had the defect**, because a rig cannot check what it does not represent.
⚠️ **R49 added the feed aperture BECAUSE its absence was a known defect**
(*"the model ended the tube flush against solid metal"*) — and the config that
everything inherits then set it back to zero. **A fix that is not the default is
not a fix.**

✅ **Rules:**
- **A simplification must carry its restoration.** Record what was removed, why,
  and the condition for putting it back — in the CONFIG, not in a commit
  message. `GEO` should have carried "these four are OFF for instrument work".
- **Enumerate the DESIGN's features and assert each is in the mesh**, against a
  list of what the machine has — not against what the rig meant to build.
- **A default that models ABSENCE is the dangerous kind.** Prefer a default that
  refuses, the way `port_bc` now does (§7v).
- ⚠️ **Ask what the thing physically has to do.** "Where does the gas go?" found
  in one question what four rigs and a full audit missed.

## 7aj. ~~Three times now, the rigs have modelled a cavity the design is not~~

🔴 **The groove.** `GEO` carried `--groove 0,0`; 31 rigs measured a cavity with
no mode filter. Caught by the user, not by a check.
🔴 **The port boundary.** Every looped eigen left the loop's feed gap
UNASSIGNED — which is PMC, i.e. OPEN — so it solved an LC resonator that
hybridised TE011. Caught by a driven/eigen disagreement of 11.5 MHz.
🔴 **The torch.** Five rigs mesh ε = 1.0; the design is sapphire ε = 11.6, and
`geometry.py` says so explicitly. Caught while designing a rig that NEEDED the
dielectric to exist.

🔑 **Three different features, three different mechanisms, ONE SHAPE: the design
has a thing, and the model does not.** None of them errored. All produced
converged, plausible, internally consistent numbers.

🔑 **AND EACH WAS CAUGHT BY SOMETHING OUTSIDE THE RIG** — a person, a
cross-solver disagreement, a downstream rig that needed the missing part. **Not
one was caught by the rig that had the defect**, because a rig cannot check what
it does not represent.

✅ **Rules:**
- **Enumerate the DESIGN's features, then assert each one is in the mesh.** The
  sidecar records geometry; compare it against a list of what the machine has,
  not against what the rig meant to build.
- **A default that models absence is the dangerous kind.** `--groove 0,0`,
  an unassigned boundary, `--torch-material 1.0` — each reads as "not
  configured" and behaves as "not present".
- **When a rig needs a feature to exist, check whether it does BEFORE relying on
  it.** E3 needed the dielectric; that is why it found the torch.
- ⚠️ **Suspect the next one.** Three found in one day means the audit is not
  finished, and the remaining ones are in the features nothing has needed yet.

## 7ak. A bound whose bad end is a geometry that does not exist

🔴 I computed the feed aperture's TE11 cutoff for **uniform fill** — air
8.37 GHz, quartz 4.30, sapphire **2.46 GHz** — and wrote up *"the consumable
choice may have removed the RF seal."* Attenuation over the 41 mm aperture:
**59.7 / 51.3 / 4.6 dB.** Alarming, and wrong.

🔑 **The aperture is not uniformly filled and never was.** The ceramic is an
annulus holding **18.8% of the TE11 field energy** — three quarters sits in the
gas core. Field-weighted, sapphire's ε_eff is **3.0, not 11.6**, and the seal is
**53.8 dB.** No problem exists.

⚠️ **User: *"Uniform-fill? So, useless in other words."*** Worse than useless.
A bracket is honest when both ends are reachable. **Here the pessimistic end
described a solid sapphire rod filling the aperture — an object that is not in
the design** — so the "bound" was not conservative, it was fictional, and it
pointed attention at a non-problem.

✅ **Rules:**
- **Before quoting a bound, ask what geometry each end corresponds to.** If an
  end is unphysical, it is not a bound, it is a distraction.
- **A 55 dB bracket is not an answer.** When the range spans the decision
  threshold, the calculation has not been done yet — say so instead of reporting
  the alarming end.
- **The field distribution is usually available in closed form.** Weighting ε by
  |E|² took one integral and moved the answer by 49 dB. **The better calculation
  was cheap; I just did not do it before speaking.**
- ⚠️ **Same register error as §7ac**: a bound stated in the voice of a result.

## 7al. A component built to enable a MEASUREMENT is not a design choice

🔴 **The coupling loop exists because a DRIVEN solve needs a port.** User,
2026-08-24: *"some kind of loop was forced so we could evaluate driven, but we
never evaluated the design options."* Two of its five parameters have no
provenance at all (wire radius, gap), one is a meshing convenience (φ = 36°, a
sector centre), and the two that ARE justified were justified *afterwards*.

🔑 **AND THE PROGRAMME THEN BUILT ON IT AS IF IT WERE CHOSEN.** Q_ext = 9,231
became "a hard property of this design"; loaded β ≤ 0.017 followed; the tuner
requirement of VSWR ~100 followed from that; and "magnitude tuning is unsolved"
followed from that. **Four inferences deep, resting on a part nobody designed.**

⚠️ **The sweep that appeared to validate it did not.** `h3_loopq` varied AREA and
found an optimum — real, but an optimum *within* a family fixed by arbitrary
constants. **A parameter study inside an unchosen family reads exactly like a
design study and is not one.**

✅ **Rules:**
- **Label instrument-driven components at birth.** "This exists so the solver has
  a port" belongs in the constant's comment, not in someone's memory.
- **Before treating a measured floor as physical, ask what was held fixed.**
  Q_ext floored at 9,231 with r_w, turns, shape and mount all frozen.
- **Sizing the gap tells you whether it matters**: β = 1 needs 84× and is dead;
  VSWR 85 → 20 needs 4.2× and is a live question. **Compute the required factor
  before declaring something closed.**
- ⚠️ **Same family as §7ai** (simplify then fail to restore) and §7ab (a
  convenience becoming an operating point): **a decision made for the
  INSTRUMENT'S benefit, inherited as though it were the MACHINE'S.**

## 7am. A DESIGN OUTPUT reported as a MEASURED PROPERTY

🔴 **User, 2026-08-24: *"we designed a loop and then complained about
over/undercoupling as if we needed to simply accept the loop geometry as
given."*** β = Q₀/Q_ext. **Q_ext is the loop and nothing else.** So *"the cavity
is overcoupled"* is a category error — the cavity is not coupled to anything;
**the coupler WE CHOSE is.** Every β in the record described a part we picked and
read as a property we found.

⚠️ **The tell is the verb.** We wrote *"β RANGES over 275×"*, *"VSWR is worst
mid-range"*, *"the coupler class is closed"* — **observational grammar applied to
our own choices.** Nothing in the record ever said *"we SET β = 4.7."*

🔴 **The damage is that it propagates as a CONSTRAINT.** β → VSWR ~100 → 45 A →
960 W dump → *"magnitude tuning is unsolved; no part exists."* **A hardware
impossibility was derived from a number we were free to change**, and the
freedom was invisible because of how it was written down.

✅ **Rules:**
- **For every quantity, name what sets it.** If the answer is *"a choice we
  made"*, it is a **design variable** and it belongs in a design table with a
  target, not in a results table with a value.
- **Ask "what do we WANT this to be?" before "what is it?"** Asking it here
  produced the actual finding in one step: cold wants Q_ext = 43,422, loaded
  wants 109, **the two states want couplers 400× apart and no fixed one works.**
  That was derivable from numbers already in the record, months of them.
- ⚠️ **A parameter study is not permission to stop.** `h3_loopq` swept area and
  found an optimum — for an unstated state. **It is the best of four for LOADED
  and the worst of four for COLD.** An optimum without an objective is a
  coincidence.
- 🔑 **Check whether the knob is already pinned.** Three of the loop's five axes
  were already at maximum coupling (J₁ peak, normal orientation, sweep minimum).
  **Knowing that turns "make the coupling stronger" into a specific question:
  it can only come from turns or mount.**
- ⚠️ Related but distinct from **§7al** — that is about *provenance* (nobody
  chose it); this is about *grammar* (we chose it, then forgot we had).

## 7an. I re-derived a documented failure, and got it WRONG on the way

🔴 **2026-08-24.** E3's cases A and C died in the eigensolver. I spent a
forensic pass on 240 KB and 370 KB of solver logs, concluded *"perfect
correlation with the plasma"*, **landed that in KNOWN.md**, and was **falsified
40 minutes later by case E** — which carries the plasma and does NOT fail.

🔴 **The correct answer was in the opening docstring of a rig I had open in the
same session.** `h3_driven.py` lines 10–11: *"sapphire — its loaded point does
not converge in eigen either (**eps +11.6 beside the plasma's −30.09**)."*
**The mechanism, both numbers, one sentence.** The same header cites
`h3_eigenprobe`'s **92 PCG non-convergences.**

🔑 **Two independent failures, and the second is the expensive one:**
1. **The index was incomplete.** KNOWN's PRIOR ART table had no row for it, so
   even a correct search of the INDEX would have missed it. *(Now added.)*
2. **I did not search the rigs.** `grep -n "converge" *.py` finds it. I went to
   the logs instead — **forensics on an artefact of the failure, rather than a
   search for whether the failure was known.**

⚠️ **AND IT COST INSTANCE TIME BEFORE IT COST REASONING.** E3 paired sapphire
with plasma in three of five cases. **The record already said that combination
does not converge in eigen. A, C and E were doomed at launch**, ~2 hours of
32-core time, and the search that would have caught it costs seconds.

✅ **Rules:**
- **A rig's DOCSTRING is prior art.** The index is a convenience, not the
  corpus. **Grep the rigs before deriving a mechanism**, not just KNOWN.md.
- 🔑 **When a solve fails, the FIRST question is "has this failed before?",
  not "what do the logs say?"** Logs describe *this* failure; the record tells
  you whether it is *a* failure. I inverted that order.
- **If you find prior art that was not indexed, index it in the same edit.**
  Otherwise the next person repeats exactly this.
- ⚠️ **This is CLAUDE.md's most-repeated error** (*"derived my own four times and
  was wrong four times"*). It was four. **It is five.**

## 7ao. `.result.json` is overwritten in place — and the journal is NOT a backup

🔴 **2026-08-25.** Relaunching `h3_driven` overwrote its own
`h3_driven.result.json` (the rig `save()`s incrementally to a fixed path). I
wrote in KNOWN.md that the prior values *"survive in `h3_driven.jsonl`, the
append-only journal"*. **They do not.** The journal is **22 lines of solve
metadata** — `{t, event, tag, seconds, ranks, order, mesh}` — with **zero**
occurrences of `f0`, `Q0` or `eta`. **It records that a solve happened, not what
it measured.**

⚠️ **I asserted the existence of an archive without opening it, in the document
that is supposed to be the authority.** One `head -2` disproved it. §7d.

✅ **Rules:**
- **Capture a `.result.json` before relaunching the same rig**, or accept the
  previous numbers are gone. Nothing else holds them.
- **`.jsonl` answers "what ran, how long, on what mesh".** For provenance and
  cost, it is the record. For PHYSICS, it holds nothing.
- 🔑 **Before citing any store as a backup, read one line of it.** The cost is a
  single command; the failure mode is discovering the gap after the data is
  already overwritten.
- ⚠️ This one landed soft — the new grid was a superset of the old, so nothing
  was actually lost. **That is luck, and it is not a reason to skip the check.**

## 7ap. 🔴 `ops/go` SYNCS BEFORE IT RUNS — a read-only tail DESTROYED a finished run

🔴 **2026-08-25, and this is the worst operational failure in the record.**
`h3_driven` completed its 9th and last solve at **00:45:58**. Seconds later I ran

    ops/go ops/riglog.sh h3_driven          # read-only. tails a log.

**`ops/go` syncs local→remote before running ANYTHING.** My local
`h3_driven.result.json` was the **stale 6-point file from the previous day**, and
`.gitignore:26` carries `!*.result.json` — an explicit **un-ignore**, so rsync
pushes it. The complete 9-point result was **overwritten by a day-old copy**,
along with `h3_driven.log`.

🔴 **AND `rsync -a` PRESERVES MTIME, SO THE CLOBBER IS INVISIBLE.** The remote
file did not look freshly written — it looked like it was from *yesterday*, which
is exactly what it now was. **The forensic signal a normal overwrite leaves —
a new timestamp — is the one thing rsync erases.**

⚠️ **THE GUARD DID NOT FIRE, AND IT WAS RIGHT NOT TO.** `ops/go` refuses to sync
while rigs run; the rig had finished ~30 s earlier. **The guard protects a
RUNNING solve. Nothing protects a FINISHED one**, and a finished one is exactly
when you reach for the log.

✅ **WHAT SAVED IT — and none of it was designed as a backup:**
- **8 of 9 points** were already in my scratchpad from progress reads.
- 🔑 **`postpro/<tag>/port-S.csv` SURVIVED.** Palace's raw output is per-tag and
  has no stale local counterpart, so rsync had nothing to push over it. The
  9th point was **re-fitted from the raw S11 sweep** and reproduced the previous
  run exactly (f₀ 2.4824, Q_L 155.1, Q₀ 157.8).

✅ **Rules:**
- 🔴 **Never `ops/go` anything after a run finishes until its results are
  pulled.** `ops/fetch.sh` first, or use plain `ssh` — read-only inspection does
  not need the gate.
- **`NOSYNC=1` for every read-only op.** The gate exists to stop bad *writes*;
  a tail is not a write.
- 🔑 **`postpro/<tag>/*.csv` is the real archive.** Not `.result.json` (clobbered
  by sync), not `.jsonl` (§7ao — metadata only). **Raw solver output is the only
  thing that survives, because nothing local shadows it.**
- ⚠️ **A safety gate scoped to one window teaches you to trust it in all
  windows.** I ran the command *because* the run was over.

## 7aq. Cross-SOLVER comparisons need the same GEOMETRY — and the same MESH

🔴 **User, 2026-08-25: *"Comparisons between eigen and driven have to happen on
the same geometry (torch, cavity, everything)."*** I had just published a
**"~9 % eigen↔driven disagreement on Q_ext"** built from eigen on a **NO-TORCH**
mesh (`h3_loopq`) against driven on a **vacuum-torch + plasma-region** mesh
(`h3_driven`). **Two cavities. There was no disagreement to report.**

⚠️ **AND I DEFENDED IT WITH THE WRONG NUMBER.** I argued the torch could not
matter because no-torch vs vacuum-torch shifts **Q₀** by only 0.23 %. **Q_ext is
not Q₀** — it is set by how the mode couples to the LOOP, and nothing in the
record measures the torch's effect on it. **Insensitivity of one quantity is not
evidence about another.**

🔑 **GEOMETRY IS NOT THE WHOLE OF "SAME".** `h3_step3` compares its `cold` and
`driven` styles at **`size_factor` 1.5 vs 1.42 — 43,685 vs 80,621 tets.**
A difference measured across that pair contains a **discretisation** term as
well as a geometry one, and they cannot be separated afterwards.

✅ **Rules:**
- **Before comparing two solvers, diff their `geometry_argv` and their mesh.**
  Both are in the result files. It is a mechanical check and it takes seconds.
- 🔑 **`--no-torch` is IN `GEO_DESIGN`** — so "both used GEO_DESIGN" does **not**
  mean "same cavity" once a rig strips or overrides it, as `h3_driven` does.
- **When solvers disagree, the first hypothesis is that they solved different
  problems**, not that one of them is wrong (§7ag asks which one MEASURED
  something; this asks whether they measured *the same thing*).
- ✅ **Prefer the estimator that needs no cross-rig import.** β from the dip
  depth uses one solve; β from Q₀/Q_ext imports a constant from another rig on
  another mesh, and inherits every difference between them.

## 7ar. 🔴 FIX IT NOW — a defect known only in the session is not known

🔴 **User, 2026-08-25: *"In general, always fix immediately. Otherwise the
understanding is only in the session context window and doesn't persist."***

⚠️ **I had just done the opposite, twice in one hour:**
- Found `GEO_DESIGN` contains `--no-torch` and wrote *"do not patch it silently
  — it belongs with the restoration."* **True about the RE-RUN. False about the
  CODE**, which kept a constant named `GEO_DESIGN` that is not the design.
- Found `h3_loopq`'s docstring asserts Q_ext is density-independent while my
  driven data questioned it — **and left the assertion standing.**

🔑 **A CONTEXT WINDOW IS NOT STORAGE.** Every session so far has ended with
someone re-deriving something the previous session knew (§7an: five times). The
gap is never *understanding*; it is that the understanding stayed in a
conversation instead of landing where the next reader will hit it.

✅ **Rules:**
- **Fix at the point of discovery.** Not at the end of the task, not "with the
  restoration", not "once the run finishes."
- 🔑 **"Fixing" a defect that would change results does NOT mean changing them
  silently.** It means making the defect **impossible to miss in the code**: a
  loud comment at the constant, a renamed symbol, an assertion that fires. **The
  behaviour can wait for a deliberate re-run; the WARNING cannot.**
- **Land it where the mistake would be repeated**, which is usually the source
  file — not only in `KNOWN.md`. A reader reaching for `GEO_DESIGN` is in
  `e0_solver_vs_math.py`, not in the findings.
- ⚠️ **Deferring is itself a decision with a failure mode**, and its failure mode
  is silent: the next session simply does not know.

## 7as. I assumed three APIs and read none — the same shape as `azimuthal.order()`

🔴 **2026-08-25.** `h3_qext` died on launch with
`TypeError: tuple indices must be integers or slices, not str` — **the exact
error the record already carries** for `azimuthal.order()` returning a tuple
that was treated as a dict. **Second occurrence, same shape.**

⚠️ **AND ONLY THE FIRST OF THREE FIRED.** Reading the sources afterwards:

| I wrote | it actually is |
|---|---|
| `design_point()["a_mm"]` | returns a **tuple** `(a_mm, L_mm)` |
| `purity(tag, mode)` | `purity(tag, mode_index, pts)` — **three** args |
| `mode["f_ghz"]`, `mode["Q"]` | `eigmodes.read()` yields `{m, f, sig}`; **Q is not in it** — it comes from `eig.csv` column 3, keyed by mode index |

🔑 **The crash was cheap because it happened at line 138, before any solve. The
other two would have fired AFTER a 500–1100 s eigen solve** — which is precisely
how the `azimuthal.order()` one cost 514 s.

✅ **AND THE WORKING PATTERN WAS TWENTY LINES AWAY.** `h3_loopq.solve_one` does
all three correctly. I imported from the same modules it imports from, and
invented my own calls instead of copying its.

✅ **Rules:**
- 🔑 **Before launching ANY rig, print the signatures you call:**
  `inspect.signature(f)` for each import, and one real invocation of the cheap
  ones. **It takes one command and it is not optional** — a rig that dies after
  the solve costs a session, one that dies before costs nothing.
- **If another rig already calls the function, copy its call site verbatim.**
  Do not re-derive the arguments from the docstring (§7an, again).
- ⚠️ **A return value described in prose is not a schema.** *"P and its SPREAD"*
  is a dict with two keys; *"f0, beta, Q_L, Q0"* is a dict; *"H1's cavity"* is a
  bare tuple. **Read the `return` statement.**

## 7at. `OPTIMIZER.md` IS the posterior store — read it before every evaluation

🔴 **User, 2026-08-25: *"Feels like we're having to do bayesian optimization
manually. Which is fine."*** ✅ **Exactly right, and it is the DESIGN.**
`OPTIMIZER.md` line 5: *"an expensive black-box problem — Bayesian Optimisation's
home ground. This file is what the isolation phase is producing FOR it."* It has
a **search box** (§1), **prior mean functions** (§2), an **evaluation policy**
(§3), and **measured evaluation cost for the acquisition function** (§3d).
**The manual phase is prior elicitation, on purpose.**

🔴 **AND I HAD STOPPED READING IT.** On 2026-08-25 I re-derived the cold coupling
branch from raw S11 CSVs and reported Q₀ = 40,652 as a finding. **`OPTIMIZER.md`
already said "branch-corrected cold Q₀ = 40,645"** — 0.02 % away — *and* noted
the earlier wrong-branch report. **Sixth §7an occurrence, and the most avoidable:
the file exists to be the memory.**

⚠️ **WORSE, I BLAMED THE RIG FOR MY OWN MISREAD.** I published *"the rig put the
cold point on the wrong branch"* after reading `wide_fit["beta"]`. **That field
is the raw root; the rig labels it `"branch": "UNRESOLVED — |S11| alone cannot
pick"` and separately returns `beta_undercoupled`, `beta_overcoupled`,
`Q0_if_undercoupled`, `Q0_if_overcoupled`, `beta_resolved`, `branch`,
`error_amplification` and `Q0_ill_conditioned`.** It got everything right. **I
took the one field it marks as unresolved and called it the rig's answer.**

✅ **Rules:**
- **Before designing the next evaluation, read `OPTIMIZER.md`.** It is where the
  last evaluation's information was supposed to go. A sequential design that
  ignores its own posterior is just a random walk with extra steps.
- 🔑 **When a rig returns several forms of a quantity, find the one it marks
  AUTHORITATIVE.** A field named `beta` is not automatically the answer; this rig
  deliberately returns the ambiguous root *and* the resolved one.
- ✅ **Disagreement between a rig's OWN estimates is a free measurement.** Cold
  `Q0_branch_free` (29,037) and `Q0_if_overcoupled` (40,645) agree only if
  `Q_EXT_MEASURED` is correct. They differ by 40 %, and the Q_ext that reconciles
  them is **8,462**. **That check was sitting unread in every result file.**
- ⚠️ **Land findings INTO `OPTIMIZER.md`, not only `KNOWN.md`** — as a function
  the surrogate can use, which is what that file asks for in its own §1.

## 7au. ✅ CANONICAL NAMES WITH CONTEXT — the fix for the whole 7c/7t/7aq family

🔑 **User, 2026-08-25: *"Rather than record values in files, we should
canonicalize their names. Basically, add a level of indirection, so we can record
different values in different contexts and refer to them by name."***

✅ **This is the general form of a bug this programme has hit at least ten
times.** Every one was a NAME meaning different measured things in different
contexts, and a value crossing that boundary unnoticed:

| name | values that have carried it |
|---|---|
| `eta.reference` | 44,384 · 29,854 · 12,368 · 43,523 — **§7c caught this ONE name four times** |
| `cavity.Q_ext` | 9,231 (no-torch eigen) · 9,117 (vacuum-torch eigen) · 8,462 (driven dip) |
| `cavity.Q0.cold` | 43,422 · 43,523 · 29,037 · 40,645 |
| `cavity.f0.cold` | 2.451633 · 2.451500 · 2.437762 |

✅ **IMPLEMENTED**: `values.py` + `contexts` in `baselines.json`.
**A name alone no longer resolves.** `get("cavity.Q_ext")` raises and prints all
three with the discriminating keys; `get("cavity.Q_ext", solver="driven_dip",
mesh="vacuum_torch", ne=0.0, loop_mm=[11,8])` returns one. **An unmeasured
context raises rather than falling back to the nearest** — which is §7aq stated
as code instead of as a warning. Retracted values stay recorded but invisible
unless asked for.

🔑 **IT GENERALISES THREE GUARDS ALREADY HAND-ROLLED HERE** — `wall_sigma()`
refusing an undeclared metal, `Q_REF_CONFIG` asserting groove/loop, GATE 4/5
refusing an implicit port BC or a mismatched mesh. **Same instinct, three
implementations, one value each.**

🔴 **AND WIRING IT FOUND ANOTHER ONE IMMEDIATELY.** `h3_driven` meshes a VACUUM
torch and hardcodes `Q_EXT_MEASURED = 9231` — **the NO-TORCH value.** The
mesh-matched number is 9,117. **+1.25 %, carried by every `beta_resolved`,
`Q0_branch_free` and derived VSWR in that rig.** Flagged at the constant; not
switched, because that moves stored numbers and `h3_qext` is measuring the right
one now.

✅ **Rules:**
- **A measured value that any other rig might read gets a canonical name and a
  context.** Not a literal in the rig that produced it.
- **Name the context axes that could differ**: solver, mesh/geometry state,
  extraction method, operating point. **If two rows differ only in an axis you
  did not record, you cannot tell them apart later** — which is exactly why
  `h3_step3`'s 9,117 has no documented mesh style.
- ⚠️ **Do not delete retracted values.** Record them with `retracted: true` and
  their falsification; a number that reappears is then recognisable.

## 7av. ✅ THE LINTER NOW ENFORCES IT — and the audit found what drifted

🔑 **User, 2026-08-25: *"That's what baselines.json was for, but we kind of
drifted away from it. We should audit everything for hardcoded values."*** and
***"There might be a linter opportunity. Any value not read from baselines.json
is an error."***

✅ **AUDITED** (`hardcoded_audit.py`, AST not grep): **49 measured values
hardcoded at module level across 27 files.** Worst first:

| finding | why it matters |
|---|---|
| 🔴 **`NE = 1e20` in NINE rigs** | the density was **anchored at 7.3–8.6e18** on 2026-08-24. **13× too high.** Every one, re-run today, measures a plasma we do not build |
| 🔴 **44,384 in EIGHT places under FIVE names** | `BARE_Q` · `Q_BARE` · `Q_BARE_EMPTY` · `Q_EMPTY_NO_LOOP` · `Q_TE011_BARE` — **and it is a RETRACTED `eta.reference`** (§7c) |
| 🔴 **35,000,000 in THREE rigs** | **`wall_sigma()` exists to bind exactly this and REFUSE without it.** The guard was bypassed by typing the number |
| ⚠️ **`Q_REF` means two things** | 44,414 (`h3_annular`) vs 43,523 (`h3_driven`) |
| ⚠️ 43,523 · 9,231 · 2.4515 · 44,414 | each under **two** names in different files |

✅ **ENFORCED**: `preflight.r_hardcoded_value`, in the gate `ops/go` already runs.
A measured-looking literal is an **ERROR**; a value from `values.get(...)` or
`wall_sigma()` passes; machinery (`N_MODES`, `CASE_TIMEOUT_S`) is ignored.
🔑 **RATCHET, NOT BIG BANG.** All 49 are grandfathered by `(file, name)` so the
gate did not brick 27 rigs. **A NEW hardcoded value errors immediately, and the
list may only shrink.**
✅ Verified with the consumer, not just the fixture: a fresh rig with
`Q_BARE`/`SIGMA`/`NE` produces **3 errors**; the same rig binding them produces
**0**.

### 🔴 AND THE SELF-TEST CAUGHT A GUARD THAT HAD NEVER FIRED

Adding the rule ran `--self-test`, which reported **`sh_rm_rf_var` does not fire
on its own known-bad.** Its regex was `rm\s+-[rf]{2}\s+$[A-Za-z_]` — **`$` is
an end-of-line anchor**, so it could never match. **The rule protecting against
`rm -rf $VAR/` deleting `/` has been dead since it was written.** Fixed to `\$`.
⚠️ **I made the inverse error in the same hour** — `\$` where I wanted an anchor
— which is why the fix comment names both directions.
🔑 **This is the file's own thesis proving itself:** *"a linter that never fires
is theatre."* **The self-test is the only reason anyone found out.**

## 7aw. ✅ ONE SLUG DETERMINES BOTH FILENAMES — inputs and outputs cannot drift

🔑 **User, 2026-08-25: *"characterize everything by config file, found by a
`--slug` parameter that contains the provenance from the docs"*** and
***"the slug could be anything, but it determines both the input and output
filenames."***

    --slug <slug>   reads  baseline-<slug>.json
                    writes <slug>.result.json · <slug>.log
                           <slug>_<case>.msh · postpro/<slug>_*

✅ **IMPLEMENTED**: `slug.py` — `parse()` (REFUSES without `--slug`, no default),
`config()` (REFUSES if the config is absent, and if the file's own `slug`
field disagrees with how it was loaded), `outfile()` / `out()` for names, and
`bind()` which resolves a canonical value **through the run's declared context**
rather than letting a rig reach for `values.get()` unrecorded.

🔴 **WHAT IT FIXES, ALL OF WHICH HAPPENED:**
- **§7ap the collision** — `h3_driven.result.json` was named for the **program**,
  so every run aimed at one path. A re-run overwrote the previous numbers; an
  rsync then pushed a day-old copy back with **mtime preserved**, so the clobber
  looked like an ordinary old file. **29 rig-named `.result.json` files were in
  this directory when the rule was written.**
- **§7ao the lost baseline** — nothing archives a result file. **A slug per run
  IS the archive**; there is no other.
- **§7au the context collapse** — the config's `binds` records *which* `Q_ext`
  this run used, in which context. `h3-driven-anchor-01` records, in its own
  caveats, that it binds `mesh=no_torch` while **meshing** `vacuum_torch`.
- **§7s the provenance gap** — "which run produced this?" is answered by the
  filename.

✅ **ENFORCED**: `preflight.r_output_not_slugged`. A module-level literal
`TAG = "..."` is an **ERROR** — it names the program, not the run. 32 existing
tags grandfathered; **the list may only shrink.**

⚠️ **VALIDATION IS FILESYSTEM-SAFETY ONLY.** The slug may be anything usable as
a filename component. **Carrying provenance is advice, not a gate** — the gate's
only job is that input and output cannot drift apart.

### ✅ AND THE REFERENCE IS CHECKED, NOT ASSERTED — `slug.py --check`

**User: *"ideally, we should use slugs that reference the docs so that we get
round-trips between code and prose."*** Both directions are verified:

- **forward** — every `baseline-*.json`'s `provenance.document` names a file and
  a section, and **the section text must actually appear in that file.** A run
  claiming a doc section nobody wrote is an error.
- **reverse** — every `baseline-*.json` a document cites **must exist on disk.**
  A document pointing at a run whose config is gone is an error.

🔑 **Its first run caught this very entry**, which used `baseline-<slug>.json` as a
metavariable and so "cited" a config that does not exist. **That is the checker
working**: prose drifts silently — a reference that is checked is the only kind
that stays true.

### 🔴 AND THE RATCHET BROKE ONCE, SILENTLY, BEFORE I CHECKED

My first grandfather list was built from the **filenames** that declare a `TAG`,
not the **TAG values** the rule compares against. **The self-test still passed**
— it only proves a rule fires on known-bad and is quiet on known-good — while
**33 of 34 rigs became unlaunchable.** Only running the rule across the whole
corpus showed it.
🔑 **A self-test proves a rule DISCRIMINATES. It says nothing about whether the
rule is survivable.** Any ratchet must be run against every existing file
before it is trusted, and that is now the last step of adding one.

## 7ax. ✅ COPY the store per run — never edit the global to ask a question

🔑 **User, 2026-08-25: *"we keep a global baselines.json, and then mutate it to
an appropriate slug version depending on case, run the sweeps against it, and
then either land the values back into the global baselines.json or if they're
not definitive, sideline them as tentative pending further investigation"*** —
and ***"I don't mean we edit baselines.json for every question, we COPY it."***

```
 baselines.json ──derive──▶ baseline-<slug>.json ──run──▶ <slug>.result.json
      ▲                       (a FULL COPY, frozen)              │
      └──── promote(definitive) ◀────── or ──────▶ promote(tentative)
```

✅ **`baseline-<slug>.json` IS a baselines.json** — same schema, every entry —
plus a `_run` block holding provenance, binds, parameters and the **sha256 of
the global it forked from.** The rig reads its values from **its own copy** and
never touches the global at run time.

🔴 **WHY THE COPY, NOT AN OVERRIDE FILE:**
- **The global can move mid-run** without changing what the run used.
- *"Which baselines did this run produce against?"* is **the file next to the
  result**, not a reconstruction from dates.
- **Mutating an input for one question is a local edit**, not a change everyone
  else silently inherits — **which is exactly how `eta.reference` was wrong four
  times (§7c) while no single run looked wrong.**

### ✅ `tentative` IS THE HALF THAT WAS ALWAYS MISSING

Values were previously either **asserted or absent**. A number that is measured
but **not yet trustworthy had nowhere to live, so it got asserted.** Now:
- `promote(..., status="definitive")` **REFUSES without a `verification`** —
  baselines.json's own `_meta` rule, finally enforced in code.
- `status="tentative"` is recorded, is visible in `describe()` marked
  **⚠️TENTATIVE**, and is **NOT returned by `values.get()`** unless the caller
  passes `allow_tentative=True` and says so at the call site.
- ⚠️ **The first real sideline is cold `Q_ext = 8,462` (driven dip)** — not
  wrong, **under-resolved**: 0.35 MHz linewidth at a 25 kHz step. It sits beside
  the definitive 9,117 with its own falsification.
- `promote()` also **refuses an undated row** — scripts here must not generate
  timestamps, and an undated result cannot be ordered against a retraction.

### ✅ ALL OF IT IS GIT-TRACKED, WHICH WAS ALREADY THE INTENT

`.gitignore` carries `!*.result.json` with the comment *"a bare `*.json` would
swallow baselines.json and every result file, **which are the evidence for every
claim**."* So value history, retractions and promotions are **diffs**, and a
retracted number is recoverable rather than deleted.

⚠️ **`baseline-h3-driven-anchor-01.json` carries `sha256: null` on purpose.**
That run executed **before this workflow existed**, so the global it ran against
was never snapshotted and cannot be recovered. **It is the reason the mechanism
exists**, and it is flagged in the file rather than quietly backfilled.

## 7ay. Slugs PIN doc identifiers — supersede in prose, never renumber

🔑 **User, 2026-08-25: *"every intermediate file needs the slug as well: meshes,
logs, etc. So that they never collide and always retain their reference back to
the docs. This means we can't reorder doc identifiers (such as with the H2 ↔ H3
fiasco) but the docs can be edited to say 'invalid, superseded' or whatever."***

✅ **This turns §7j from a rule people must remember into a property of the
filesystem.** §7j's cost is on the record: the sustainment/groove **swap** moved
the numbers while the status labels stayed with the numbers, `premature` landed
on a question that was already ANSWERED, the groove never entered `GEO`, and
**31 rigs measured a cavity nobody is building.**

🔴 **ONCE A SLUG EXISTS, ITS IDENTIFIER IS PINNED** — by every artefact carrying
it: `h3-qext-01.result.json`, `h3-qext-01.log`, `h3-qext-01_n18p90.msh`,
`postpro/h3-qext-01_n18p90_wide/`. **Renumbering H3 does not rename those**, and
nothing ever will. **The name on disk is the identifier's true owner.**

✅ **SO SUPERSESSION IS AN EDIT, NOT A MOVE:**
- Mark the doc section **"invalid, superseded by X"** and leave the identifier
  where it is. **Identifiers are append-only.**
- A new question gets a **new** identifier, never a recycled one.
- **This is exactly §7j's "DROP, do not swap"**, now with the drop enforced:
  a swap would orphan every artefact that cites the old number.

✅ **CHECKED**: `slug.py --check` verifies a slug's leading segment against the
`hypothesis` its config declares — so a run labelled `h3-*` that starts claiming
H4 is an ERROR, not a silent reattribution. **Verified by simulating exactly the
§7j drift: the check fires.**

⚠️ **Coverage today:** 241 artefact f-strings already build from `TAG`, so they
inherit the slug as soon as `TAG` does — which `r_output_not_slugged` forces.
**49 build filenames with no tag at all** (e.g. `e0h_s{}.result.json`), and those
are the remaining leaks. **They are the burn-down list**, not a claim of done.

## 7az. ⏳ THE MIGRATION — scoped, planned, and NOT executed yet

🔑 **User, 2026-08-25: *"we also have to rename everything extant to conform to
the slug regime. And modify all scripts, and update CONVENTIONS.md."*** ✅ Right,
and the inventory says it is bigger than it looks.

### The inventory — 385 artefact files/dirs, 34 prefixes

| class | count | what happens |
|---|---:|---|
| ✅ prefix maps to a rig | **25 prefixes** | retro slug `<rig>-00` |
| 🔴 **NO OWNING RIG** | **9 prefixes, 37 files** | `e1b` `e1c` `e1cc` `scale` `e0fine` `e0coarse` `e0cond` `sfprobe` — **cannot be migrated** |
| ✅ already slugged | 1 | `h3-driven-anchor-01` |

🔴 **THE ORPHANS ARE THE INTERESTING PART. A slug must reference a doc section;
these can reference nothing** — their producing code is gone (the deleted
`waveguide`/`ignition` programmes, or earlier eras). **They are artefacts with
no provenance and no way to acquire any.** Quarantine or delete is a user call,
not a rename.

⚠️ **`00` IS A WEAK CLAIM.** These are the residue of an era where a re-run
overwrote its predecessor in place (§7ap), so "run 00" may be the third run with
the first two destroyed. The retro configs carry `sha256: null` and say so.

### 🔴 MY FIRST PLAN WAS WRONG AND THE DRY RUN CAUGHT IT

I keyed the migration on `TAG`. It produced **195 renames and missed every
mesh** — because **only 32 of 87 rigs declare a `TAG` at all.** The prefixes on
disk are ground truth; the TAG table is a partial index of them. **A migration
planned from the code would have renamed the logs and orphaned 369 MB of meshes
from their sidecars.**

### ⏳ TWO PRECONDITIONS, BOTH CURRENTLY UNMET

1. 🔴 **NO RESTORE POINT.** 37 files are uncommitted, so `git checkout` to undo
   a bad rename would also discard today's work. **And `*.msh` and `*.meta.json`
   are GITIGNORED** — 369 MB with no safety net at all, including **the sidecar
   GATE 5 validates every mesh against.** A rename that misses a sidecar breaks
   every solve that uses it.
2. 🔴 **A RIG IS RUNNING.** `h3_qext` is writing artefacts now. It is excluded
   from the plan by name, and nothing may be synced until it exits.

✅ **`migrate_slugs.py` plans and refuses.** `--apply` is deliberately
unimplemented until both clear. **The plan file is the deliverable; the rename
is not, yet.**

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
