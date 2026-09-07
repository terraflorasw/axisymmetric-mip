# CONVENTIONS — canonical

**Read this at the start of every session.** These are not style preferences.
Each one is a mistake actually made here, usually more than once, and several
were made again within hours of being written down.

## 🔴 THIS FILE IS CANON. NON-ADHERENCE IS STALENESS.

> User, 2026-09-04: *"CONVENTIONS has to be canonical, and anything that doesn't
> adhere to it should be considered stale"*

**Anything in this repo that contradicts this file is stale** — a document, a
rig, a recorded value, or an entry in `INCIDENTS.md`. Do not reconcile the two;
**fix the thing that drifted, or mark it superseded** (§7.5).

## ⚠️ WHY IT WAS SPLIT, 2026-09-04

This file reached **3,454 lines, 90 % of it incident narratives.** At that size it
stopped being read, so its rules were **re-discovered and re-appended**, which
made it longer. The proof: §7bi (2026-08-25, *"no constants in scripts"*) already
covered the three constant-provenance defects written up AGAIN as §7bx/§7by/§7bz
on 2026-09-03/04. **An unreadable rulebook manufactures the failures it
documents.**

- **`CONVENTIONS.md` (here) — THE RULES.** Short enough to read in full.
- **`INCIDENTS.md` — THE EVIDENCE.** All 79 narratives, verbatim, nothing lost.

🔑 **CITATIONS STILL RESOLVE.** Ids `7a`–`7ca` were NOT renumbered (§7ay: pin
identifiers, supersede in prose). A reference to "CONVENTIONS §7bi" now reads as
**`INCIDENTS.md` §7bi**, and its RULE is in §7.1 below.

➡️ **ADDING A RULE:** if an incident restates an existing rule, **add its id to
that rule's citation list — do not append a new section.** A rule cited 5× is the
most valuable line in this file: it marks where the discipline does not hold.

Sorted by pattern, because the same shapes keep recurring in new clothes.

---

## 0. ONE NAME PER QUANTITY — AND IT IS THE `baselines.json` NAME

**Prose, comments and documentation use EXACTLY the identifier `baselines.json`
uses.** Not a variant, not a Greek letter, not a shorthand. Naming differences
are pervasively attention-splitting, and this repo already taxes attention by
spanning microwave engineering, plasma physics and Bessel analysis — three
vocabularies that collide on the same letters.

The style is `baselines.json`'s: **`<domain>.<quantity>[.<unit>]`**, dotted and
lowercase. It already exists for most quantities; use it rather than invent.

    wall.conductivity.s_per_m     sigma of the wall      (EXISTS)
    loop.conductivity.s_per_m     sigma of the loop      (EXISTS)
    torch.sapphire.permittivity   eps of the torch       (EXISTS)
    cavity.Q0.cold / cavity.Q_ext.cold Q                      (EXISTS)
    source.f0.ghz                 drive frequency        (EXISTS)
    coupling.beta                 Q0/Q_ext
    mode.beta_z                   AXIAL PROPAGATION CONSTANT pi/L — a DIFFERENT
                                  beta, used in mode.beta_z/mode.k_c
    mode.k_c                      cutoff wavenumber, bessel.chi_prime_01 / a
    plasma.collision_frequency    the plasma's nu — NOT a spectral frequency
    plasma.permittivity           the Drude eps, which goes NEGATIVE
    bessel.chi_prime_01           3.8317, and bessel.chi_11 equals it

🔴 **THE COLLISIONS ARE REAL AND ONE IS INTERNAL.**
  - `coupling.beta` vs **`mode.beta_z`** — both written "β" in this record.
    `KNOWN.md` uses β = pi/L in the field-ratio derivation while everything else
    means Q0/Q_ext. A reader cannot tell them apart, and neither can a search.
  - `coupling.beta` vs **plasma beta** (plasma pressure / magnetic pressure) —
    a plasma physicist reads every one of ours wrong.
  - `plasma.collision_frequency` vs **spectral frequency** — spectroscopy writes
    frequency as nu, and this instrument IS a spectrometer.
  - `wall.conductivity.s_per_m` vs **cross-section**, which is also sigma.

➡️ **The audit and the remaining repair order are in `NAMING.md`.**

✅ **RETROFIT, DO NOT ACCUMULATE.** Earlier entries differing in terminology from
later ones is itself the harm — a reader carries two vocabularies instead of
one. Append-over-rewrite protects RESULTS, not NAMES. Renaming a quantity does
not change what a superseded claim said; leaving two names for it does make the
claim harder to read.

⚠️ **WRITE THE ASCII FORM WHEN IT MUST BE FOUND.** The record mixes `eps` with
the Greek letter, `lambda` with its symbol. R4's diagnosis of eps-near-zero
conditioning hid through an afternoon of debugging because it is spelled with a
Greek epsilon and the search used ASCII. `ops/priorart.sh` transliterates both
ways.

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
- wavelength/4 was predicted as the optimal groove depth. It is where the slot resonates
  and therefore the depth to **avoid** — right physics, wrong design goal.

## 6b. A model does not just predict values — it allocates the sampling budget

⚠️ **A directionally wrong model is more expensive than no model**, because it
concentrates effort confidently in the wrong place. No model gives you a spread;
a wrong model gives you a cluster.

H2 sampled groove depths 0, 10, 20, 27, 31, 34, 42, 52 mm. That was not
scattering — it was a deliberate cluster around `Z₀·tan(βd)`'s predicted optimum
at wavelength/4 = 30.59 mm. The model was right that wavelength/4 is special and wrong about the
SIGN of its usefulness: it is where the slot resonates and Q collapses to ~3,000,
the depth to AVOID. Result:

| gd | d/(wavelength/4) | outcome |
|---:|---:|---|
| 0 | 0.00 | control — measures nothing (the reference is analytic) |
| 10, 20 | 0.33, 0.65 | the only two usable points |
| 27, 31, 34 | 0.88–1.11 | at wavelength/4, Q collapsed |
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
applied to SAMPLING rather than to scoring. Millimetres hid the wavelength structure
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

---

# §7 — RULES LEARNED FROM FAILURE

🔑 **THIS IS THE CANON. `INCIDENTS.md` IS THE EVIDENCE.** Each rule below was
learned by making the mistake; the narrative is in `INCIDENTS.md` under the ids
cited. **If a rule and an incident disagree, the rule wins and the incident is
stale.** Anything in this repo that does not adhere to this file is stale.

⚠️ **STATUS-ONLY INCIDENTS, deliberately carrying no rule:** `7az`, `7bc`, `7bf`
(migration scope, idempotence scope, migration outcome). They record what
happened, not what to do. The coverage audit expects exactly these three.

⚠️ **A rule citing SEVERAL ids has been learned several times.** That count is the
most useful column here — it says where the discipline does not hold.

## 7.0 🔴 ENFORCEMENT — the only thing that has ever stopped a repeat

> User, 2026-09-04: *"We have to have some way to stop making the same mistakes
> as the ones we just fixed"*

**The evidence is one day of this session, and it is unanimous.**

| held | why |
|---|---|
| `BARE_Q0_MAX` hardcode caught | **preflight refused** — in `verify_identities.py`, the file whose subject is hardcoded constants |
| quartz regression caught mid-repair | **the tentative guard refused** |
| `Q0_COLD_EIGEN`, a bad lookup nobody knew about | **`required_context` refused** |
| 5 rules dropped in the split, incl. one written the day before | **`audit_conventions` refused** |
| `eps_r` hole hiding a 3.3 MHz physics difference | **`audit_names` refused** |

| violated | why |
|---|---|
| *"check the exit code without a pipe"* (§7.6) — **3x in one day** | documented only |
| *"no constants in scripts"* — **learned 5x**, top recurrence | linter is BLIND to kwargs and CLI-arg literals |
| *"read OPTIMIZER.md before every evaluation"* | documented only — missed the beta-not-converged warning for two days |

➡️ **A RULE WITHOUT A REFUSAL IS A WISH.** Writing it down has never once stopped
a repeat in this programme; a check that fails closed has stopped several,
including inside the very repairs that were fixing the same class of defect.

🔑 **SO EVERY RULE CARRIES ITS ENFORCEMENT**, and the honest tags are:
- **⚙️ `<checker>`** — a machine refuses. The rule holds.
- **⚙️⚠️ `<checker>` PARTIAL** — a machine refuses SOME cases. **This is the most
  dangerous state**: the check reports clean and the reader believes it. *"No
  constants in scripts"* is enforced for uppercase module assignments and blind
  to kwargs and CLI-arg lists — which is exactly where all three of this week's
  wrong-cavity constants lived.
- **🖐️ UNENFORCED** — documented only. **Expect violations and plan for them.**

➡️ **THE BUILD QUEUE IS: rules learned 3+ times that are still 🖐️ or ⚙️⚠️.**
`audit_conventions.py` prints it. Adding enforcement to one of those is worth
more than adding a rule.

## 7.1 PROVENANCE — where a number came from

- ⚠️ **BUT "BIND IT" IS NOT ALWAYS RIGHT.** A literal in an OLD rig may be the
  RECORD of the geometry that run actually used. `e0k_driven_vs_eigen` meshes a
  25.8x19.4 loop (1,001 mm²) against the canonical 11x8 (176 mm², 5.7x smaller);
  binding it would silently change what the rig meshes and rewrite what the run
  did. ➡️ **Bind when the literal is a COPY of a canonical value. Leave it, with
  a reason, when it IS the provenance.** The test: would binding change what the
  rig meshes? Then it is history, not debt. *(2026-09-04)*
- **No constants in scripts. Bind from `baselines.json` or refuse.** ⚠️ The linter
  sees only module-level UPPERCASE assignments — **not kwargs, dict defaults, or
  literals inside CLI-argument lists**, which is where the biggest store hid.
  *(7bi, 7av, 7bx, 7by, 7bz — learned 5×)* ⚙️ `preflight r_hardcoded_value` + **`r_cli_literal`** (added 2026-09-04, closes the CLI-arg-literal blind spot that hid the torch for 9 days; 51 existing pairs grandfathered, list may only SHRINK). ⚠️ kwargs/dict-defaults remain uncovered — `_bind()` handles them by convention, not by refusal
- **A name that claims provenance must be enforceable.** `q_ref_measured`,
  `Q_EXT_MEASURED`, `cavity.Q_ext` — all named as measurements, all constants
  from another configuration. Audit the nouns: `measured`, `anchor`, `ref`,
  `est`. *(7by, 7bz, 7au)* ⚙️ `values.required_context` + `audit_names.py`
- **A canonical name carries CONTEXT, and the mandatory coordinates are
  declared.** A store cannot object to a coordinate the caller never named:
  use `required_context`. *(7au, 7bl, 7be, 7bz)* ⚙️ `values.required_context` + `audit_names.py`
- **A derived quantity must be reconstructible from the raw data beside it.**
  If `Q0` cannot be rebuilt from the `Q_L` and `beta` in the same artefact, it is
  a measurement plus an invisible assumption. `verify_identities.py` checks this.
  *(7bx, 7d)* ⚙️ `verify_identities.py`
- **Two values from one source cannot disagree**; **one rig, one solver.**
  *(7c, 7d)*
- **Measure the reference with the instrument that measures the cases.**
  Cross-solver comparisons need the same geometry AND the same mesh.
  *(7t, 7aq, 7ag)*
- **Reasoning added after a measurement is not its provenance.** *(7s)*
- **A physical STATE is one state — do not assign its coordinates by hand.**
  `NE` and `NU_M` were set as independent constants; nu_m = n_gas·⟨σv⟩ and
  n_gas = P/kT, so a collision rate at fixed pressure is a TEMPERATURE statement,
  which under LTE also fixes n_e. One state, three symbols, two assigned by hand,
  and nothing errored when they disagreed. *(7ad)*
- **A label keyed on a LITERAL will contradict the value it labels.** Label from
  the source you bind from. A mesh built on the correct axis announced `custom`
  while the wrong axis would have announced `SAPPHIRE`. *(7br)*

## 7.2 VALIDITY — is this a measurement of the thing we are building?

- **Once the design fixes a feature, a measurement without it is a different
  cavity.** Groove, torch, loop — each has voided a body of work.
  *(7m, 7aj, 7ai, 7f)*
- **Simplify to isolate, then RESTORE. Nothing restores itself.** *(7ai, 7f)*
- **Solve the mesh the sidecar describes** — bind from it and assert it matches
  the request. *(7af, 7ba)*
- **A bug fix that could invalidate a result means that result is invalid until
  proven otherwise.** *(7bm)*
- **A quantity measured in another epoch was measured on another machine.**
  *(4b, 7aq)*
- **A sweep must be legal in the geometry, not only in the physics.** *(7bk, 7ak)*

## 7.3 CLAIMS — what may be said about a number

- **A design OUTPUT is not a measured property**; a component built to enable a
  measurement is not a design choice. *(7am, 7al, 7ab)*
- **Surviving a falsifier is not confirmation.** A falsifier can fire for a
  reason its author never enumerated; a binary one passes on a meaningless
  effect size. *(7w, 7z, 7l)*
- **Measure the magnitude before drawing the consequence**, and **state the span
  a range covers before calling anything constant across it.** *(5, 7z)*
- **A wrong label can void a right number**, and a number corrected in a
  document is not corrected in the programme. *(7q, 7r, 7n)*
- **When the rig says it does not know, do not supply the confidence.** *(7u)*
- **A relative quantity needs a stated origin.** *"wall dT = +0 K"* is a RISE
  above a baseline that appeared nowhere — not a temperature. *(7ae)*
- **First-versus-last cannot see a turning point**; do not interpolate across one
  you have already found. *(7aa, 7ah)*

## 7.4 INSTRUMENT — what it can and cannot resolve

- **A competing in-band mode is an ALARM, not a finding.** *(7i)*
- **|S11| alone cannot pick the coupling branch, and the branch FLIPS with
  load.** Resolve by phase or an eigen pair; both roots must be recorded.
  *(7x)*
- **A sample-count rule is not a resolution rule — interpolate the 3 dB edges.**
  *(7bh, 7bg)*
- **A checker must be able to see what it checks** (§7), and **a guard must
  GATE, not announce** — a flag with no reader is a comment with extra steps.
  *(7, 7by)*
- **An unassigned boundary is a CHOSEN boundary**; out-of-range must not bin to a
  meaningful value. *(7v, 7o)*
- **A mesh gmsh accepts can still be topologically invalid.** *(7bn)*
- **Ask whether the instrument CAN answer, not only what it costs.** *(6c, 7bp)*
- **A safety margin is a COST, and an unpriced one breaks the solve.** An extra
  requested mode stalled NLEPS at 11 of 12 and nearly discarded eleven converged
  modes on the wall clock. Price the margin, or it spends the run. *(7p)*

## 7.5 ARTEFACTS — identity and survival

- **One slug determines both filenames; outputs carry the hash of their inputs.**
  A tag that does not name what varies is a collision waiting to happen — when
  the sweep axis changes, the tag changes with it. *(7aw, 7bd, 7bj, 7bb)* ⚙️ `slug.check_unique/check_stamps` + `preflight r_output_not_slugged`
- **Copy the store per run; never edit the global to ask a question.** *(7ax)*
- **`.result.json` is overwritten in place, and the journal is not a backup.**
  *(7ao, 7ap)*
- 🔴 **THREE CATEGORIES, THREE RULES. Most "append-only" damage is applying one
  category's rule to another.** *(7ay, 7ca, 7j, 7h)*

  | category | rule | why |
  |---|---|---|
  | **IDENTIFIERS** — slugs, §-ids, R-numbers | **APPEND-ONLY. Never renumber, never recycle.** | every artefact on disk cites them; a swap orphans all of it |
  | **DATA** — result files, frozen run configs, artefacts | **APPEND-ONLY. Never edited.** | an edited result is not a measurement; a stamped config orphans its solves |
  | **CLAIMS** — verdicts and conclusions in prose | 🔑 **EDITED IN PLACE when superseded.** | evaluation is re-runnable by design, and a stale ✅ heading re-asserts itself on every read |

  ➡️ **A superseded claim is stamped AT ITS OWN HEADING** with: that it is
  superseded, **why**, a **forward pointer**, and **what still survives** — the
  raw measurement usually outlives the conclusion drawn from it. The identifier
  stays put and the original text is kept below the stamp.

  ⚠️ **"Supersede in prose, never renumber" (§7ay) means SUPERSESSION IS AN EDIT
  TO THE ENTRY** — not a note filed elsewhere. Read the other way it contradicts
  the stamping rule, and that misreading is what produced `## ✅✅ ... IS
  MEASURED` sitting 90 lines below its own retraction.

## 7.6 OPERATIONS

- **Useless solves cost far more than spot interruptions.** *(7bp)*
- **Where reclamation is routine, case-level resume is feasibility, not polish**
  — and resume must restore the CONTINUATION, not just the result. *(7bw)*
- **A launcher that cannot reach the host must FAIL, not narrate.** ⚠️ And check
  an exit code without a pipe. *(7bv)* ⚙️ `ops/go` exit 3
- **Watch, do not poll; never pipe the watcher.** *(7bq — failed 4×)* ⚙️ `ops/remote.sh` execs into `ops/watch.sh`
- **A WATCH MUST OUTLIVE WHAT IT WATCHES, and one that dies must not look like a
  run that ended.** A backgrounded shell is capped by its HOST's timeout, so
  `rc=124` four minutes into a 5 h solve reads exactly like a finished watch.
  ⚠️ The solve is never at risk — it is `nohup`'d — so nothing fails and nobody
  looks. *(7cc)* ⚙️ `EVENTS=1 ops/watch.sh` under a long-lived event host
- **Progress lives in the SOLVER log, not the rig log.** A rig that prints per
  CASE gives an armed, correct, silent watch for the whole of a long case.
  *(7ce)* ⚙️ `ops/solverprogress.sh`, started by `ops/watch.sh` itself
- **A watcher's output is a measurement — smoke-test that it EMITS.** "It
  parses" and "it emits the right thing" are different claims; a dedup keyed on
  a line containing elapsed time emits every poll. *(7ce)*
- **`pkill -f` matches the shell that runs it.** Exclude `$$`, or keep the
  pattern out of your own argv. *(7cf — twice)*
- **A timeout is a RUNTIME property. Never put it in the input fingerprint.**
  It cannot change a number, only whether a number is obtained — so a cap that
  is part of `sha256(config)` means EXTENDING IT ORPHANS EVERY CASE ALREADY
  SOLVED. *(7cd)* ⚙️ `$AMIP_CASE_TIMEOUT_S`, effective value recorded per case
- **Env does not cross `ssh`.** A launcher that hardcodes its remote env drops
  every override silently and the rig runs its default without saying so.
  *(7cd)* ⚙️ `ops/remote.sh` forwards an explicit list and PRINTS it
- **A rig must not act when it is merely read.** *(7y)*
- **Do not narrate durations. I do not know how much time has passed.** *(7bo)* 🖐️ UNENFORCED
- **Fix it now — a defect known only in the session is not known.** *(7ar)*
- **A refactor drops imports and nothing sees it.** Names used only INSIDE
  functions survive `ast.parse` and a bare `import`, then die on the instance
  after meshing with a `NameError`. Twice in one session. *(7b)*

- **A fit that REFUSED has no fields. The consumer must expect that.** A
  missing `Q_L` killed a run in `_report` after every solve had finished —
  measurement honest, evaluation assuming success. ✅ Refuse, never substitute:
  a width invented from the band edge would look like a measurement. *(7ck)*
- **`set -e` + a `timeout` silently deletes everything after it.** The `exec`
  that made launching-and-watching atomic was skipped whenever the launch ssh
  ran long — the guarantee rested on an ssh that sometimes does not return.
  ✅ Capture the status, then ASK THE INSTANCE what is running. *(7cj)*
  ⚙️ `ops/remote.sh` verifies the rig and exits 5
- **A negative result from a simplified reproduction is not a negative result.**
  Three variants of the launch ssh returned cleanly in isolation; the hang needs
  the real rig. *(7cj)*
- **A checker is not a check until something RUNS it.** `verify_identities.py`
  crashed at import for two days — broken by the very audit it supports — and
  nothing said so: a gate that cannot start fails by not being there. *(7ci)*
  🖐️ UNENFORCED — nothing runs it on a launch the way `preflight` is run
- **A dependency's config schema is a fact to LOOK UP, not recall.** An invented
  Palace key failed validation in 2 s; the schema ships inside the build.
  ⚠️ And a rig whose every case failed still exits 0. *(7cg)*
- **Prefer a MEASURED INVARIANT to a physical prior when breaking a degeneracy.**
  A branch bootstrap ("an empty cavity has Q0 ~4e4") silently assumed a low-loss
  coupler and inverted Q0/Q_ext for a lossy one; the shared `sigma·Q_plasma`
  caught it, and only because probes had established the mode was shared. *(7cq)*
- **A rule that has never fired has not been TESTED — only run**, and it is
  indistinguishable from clean code. `r_none_format` passed `--self-test` while
  ~80% dead through three rounds: its name list missed new refusable values, a
  regex precedence bug skipped four of its five names (the fixture used the
  fifth), and its spec grammar could not see `>` alignment — the house style.
  ⚠️ **A fixture exercising ONE branch of an alternation certifies the
  alternation.** ⚠️ And making a value refusable is TWO edits — the code, and the
  lint's name list. *(7co, 7cp)* ⚙️ `_REFUSABLE` / `_REFUSABLE_ONLY_IN`
- **A correction from THIS conversation is prior art too — and the easiest to
  skip.** A retracted claim was restated an hour later, from the same file that
  held its retraction, and the false premise then drove a wrong conclusion.
  ⚠️ **Unsolved ≠ absent ≠ impossible.** *(7cn)*
- **A derived constant must be ANCHORED TO A KNOWN OUTPUT.** A TM01 Bessel zero
  stood in for TE011's and every field estimate was wrong; the one-line check is
  that the constant reproduces the design frequency. ⚙️ `coldfield.self_test`
  *(7cm)*
- **A coordinate must have ONE type.** `size_factor` is a string in some
  artefacts and a float in others; lexicographic order would have silently
  reordered a convergence series. *(7ch)*

## 7.7 PROCESS

- **Search prior art before deriving — and before REPAIRING.** Both fixes I
  "designed" on 2026-09-03 already existed, unadopted. *(7bt, 7an, 7as, 7at)* 🖐️ UNENFORCED — `ops/priorart.sh` exists; nothing makes you run it
- **The experiment list does not grow. Park surprises.** *(7k)*
- **Never mint revision numbers — the register IS the failure mode.** *(7g)*
- **Decontaminate a count before letting it justify a rewrite.** *(7bs)*
- **When a symbol has three meanings, spell the word out.** *(7bu)*
- **"Converged" is TWO claims — say SOLVER-converged or MESH-converged.** One is
  a property of a run whose failure is an error; the other is a property of a
  series whose failure is a RESULT with every solve succeeding. 84 uses across
  four documents, both senses, no definition. *(7cl)* ⚙️ `GLOSSARY.md § converged`
- **A print is where a claim escapes review.** *(7e)*
- **Do not mix a verified analysis with an unverified suggestion.** *(7ac)*

## 7cb — ONE watcher. Do not hand-roll a monitor per launch.

> User, 2026-09-05: *"Before we continue though, we should have a more
> disciplined approach to monitoring."*

🔴 **THE STANDARD ALREADY EXISTED AND I IGNORED IT FOR A WHOLE SESSION.**
`ops/watchrig.sh` is the MECHANISM (poll, diff, mirror, detect the three
endings — **16 tests**); `ops/watch.sh` is the POLICY (fetch results, report the
instance is idle and billing). They already separate mechanism from policy — the
same critique that was made of the solve timeout on the same day.

I hand-wrote a bespoke `Monitor` grep loop for **every** launch on 2026-09-04/05.
Each was slightly different, each had to be tuned, and each reproduced a failure
`watchrig.sh` had already fixed:

| watchrig's four questions | my hand-rolled loops |
|---|---|
| (a) emits per unit of progress | ✅ |
| (b) ends when the JOB ends | ✅ |
| (c) ends when the MACHINE ends | ⚠️ only after 3 missed polls — 20 min late |
| (d) can the caller silently discard it? | 🔴 no mirroring; tuned the filter 3x |

➡️ **RULE: after any launch, arm `Monitor(command="ops/watch.sh <slug>")`.**
Never hand-roll a grep loop. If the standard watcher lacks something, FIX THE
WATCHER — that is what its 16 tests are for.

🔴 **AND A CHAINED LAUNCH MUST ARM THE NEXT WATCH IN THE SAME BREATH.** Twice
this session a monitor launched the next run and then exited, leaving it running
unwatched; the second time the user had to point it out. A chain that starts a
run without a watch is the operational twin of a guard that sets a flag nobody
reads (§7by).

✅ **ENFORCED 2026-09-05.** `ops/wait.sh` is EXPUNGED — measured against the
three criteria it answered only (b): it blocked and printed a tail, so a job
stepping through cases looked identical to a job doing nothing, and ssh failure
was not distinguished from a slow poll. It now REFUSES with the reasons rather
than silently forwarding, because a caller wanting a BLOCKING wait would
otherwise get a STREAMING watch and not notice.
⚙️ **`preflight sh_adhoc_watch`** refuses a hand-rolled remote watch loop
(`while true` + ssh + sleep, `tail -f *.log`, `until … grep … EXIT=`). Sanctioned
watchers carry `sanctioned-watcher: <why>` — `watchrig.sh` (the mechanism),
its test, `spotwatch.sh` (records notices on the VOLUME, not a rig watch), and
`queue.sh` (launches a batch, defers to `watch.sh` per slug).

✅ **AND THE LAUNCH ITSELF NOW ENFORCES IT (2026-09-05).** `ops/remote.sh` no
longer RETURNS after launching — it **execs into `ops/watch.sh`**. Launching and
watching are ONE operation, so there is no window in which a run is live and
unwatched, and nothing left for an ad-hoc loop to do.
- no slug -> **exit 4**: a run that cannot be watched by name is not launched.
- `NOWATCH=1` for a batch that watches per slug itself — and it says
  **"LIVE AND UNWATCHED"** rather than returning quietly.

🔑 **THE GENERAL FORM: DELETE THE STEP, DO NOT DOCUMENT IT.** Advice printed at
the end of a script is not a guard — this exact line said *"watch: ops/watch.sh
<slug> <- do this"* and was ignored on every launch for two days. A step that
must be remembered will eventually not be. ⚙️ `ops/remote.sh` exec + `preflight
sh_adhoc_watch`

⚠️ **RESIDUAL, and it is mine not the tooling's:** an assistant can still call
`ssh` directly instead of going through `ops/`. Nothing outside the repo can stop
that; §7cb is the rule, and the exec removes the incentive.
