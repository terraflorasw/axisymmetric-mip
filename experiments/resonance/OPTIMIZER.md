# Optimizer priors

**What this file is.** The eventual co-design of torch + viewport + trap + bore
radius + coupling against an LOD objective is a 5+ dimensional, multi-objective,
expensive black-box problem — Bayesian Optimisation's home ground. This file is
what the isolation phase is producing FOR it, captured in the form a Bayesian
loop actually consumes.

🔑 **The point is not to list numbers.** A Gaussian Process with a zero mean must
learn the whole response surface from data; with a physics model as its PRIOR
MEAN it learns only the residual, which is worth a large factor in evaluations.
So a finding is only useful here if it is stated as *a function the surrogate can
evaluate*, with the evidence that it holds and the test that would break it.

⚠️ **Not yet. See § When to start.** Priors are being banked; the objective is
not yet definable, and a confidently-optimised proxy is worse than an
un-optimised one because it spends the budget and produces a number people trust.

---

## The rule

**Every entry carries a STATUS, the evidence, and the falsifier.** A prior with
no falsifier is a guess wearing a number, and this programme has been wrong often
enough — inverted field forms, a threshold on the wrong side of a false match, a
Q trend that was a mislabelling — that an unfalsifiable prior is a liability.

| status | means |
|---|---|
| **VALIDATED** | measured, with a declared falsifier that was pushed and held |
| **THIN** | measured, but on too few points to be a law (CONVENTIONS §11) |
| **ASSUMED** | plausible, not measured. Must not be used as a mean function |
| **RETIRED** | was believed, then falsified. Kept so it is not re-derived |

---

## 1. Search box — the bounds

GP cost scales badly with search volume, so every bound is evaluations saved.

| variable | bound | status | evidence / falsifier |
|---|---|---|---|
| f₀ | **2.45 GHz** | VALIDATED | hard anchor: ISM + tunable LDMOS 2.40–2.50. Not a free variable. |
| D/L | **1.525** | VALIDATED | H1: max-min stationary point over rival separation, so ∂(separation)/∂(D/L) = 0 and it is tolerance-insensitive. Falsifier "TE011 Q > TM111 Q" held at every point. |
| groove depth | **< ~21 mm** (0.7·λ/4) | VALIDATED | λ/4 = 30.59 mm is a POLE: the slot resonates and Q collapses to ~3,000. H2 measured it. Falsifier: TE011 must barely move — it fired at λ/4. |
| groove width | **≥ 3 mm** | VALIDATED by failure | 2 mm forced 58,303 tets and stalled the linear solve; 3 mm diverged in NLEPS. Both are hard evidence, not preference. |
| loop coupling β | **0.1 – 1** | 🔴 **UNUSABLE — β IS NOT MESH-CONVERGED** | 2026-08-23: β moved **43.1%** for a 1.25× linear refinement at fixed partition and port resolution (0.4081 → 0.2320), and is still falling. Resolving the port (R112, 2 → 42 elements) was necessary but not sufficient. 🔑 Meanwhile Q₀ = Q_L(1+β) moved **0.12%** — β and Q_L compensate. **Do not use β as a prior, a bound, or an objective term until a convergence series (sf 1.5/1.2/1.0/0.8) establishes where it lands.** |
| bore radius | 8.5 mm | 🔴 **ASSUMED, DOUBLY** | inherited from the pre-order-2 record — **order-1 solving is 12–17 MHz wrong and mode-dependent by 40×** — and probably from inherited geometry on top of that. Nobody has chosen it. It is the DOMINANT coupling lever (30× vs aspect ratio's 2×). |
| gas flow ceiling | ≤ 20 slm N₂ | 🔴 **ASSUMED** | lab Nitrogen SLPM taken from **MP-AES and MICAP**. Neither is an optimised number — they are what those instruments happen to use. Must be verified, not inherited. The chain slm → bore radius → coupling → input power rests entirely on it. |
| plasma radius | **SWEEP IT** | 🔑 **not an input — an OUTPUT of H3** | TE011 energy ∝ R⁴ near the axis (2→8.5 mm is **319×**), so any inherited value makes H3 arbitrary. H3 returns the range that sustains, and THAT becomes the torch specification. |
| torch geometry | Fassel | 🔴 **ASSUMED, WRONG GAS** | the standard Fassel torch is **Argon-optimised**. There is no Nitrogen-optimised torch geometry in the record or, as far as we know, anywhere. Every torch dimension is inherited from a different working gas. |

## 2. Prior mean functions — the surrogate's backbone

| model | form | status | evidence / falsifier |
|---|---|---|---|
| **wall loss scaling** | Q ∝ σ^0.5 | VALIDATED | 4 decimals, decade of σ, all 14 modes (E0q) |
| **solve cost** | t ≈ 454 ns × ND_dofs × KSP_its, ND ≈ 6.44·tets at order 2 | VALIDATED | ±15% over a 4× runtime range, 51 solves; 4% out-of-sample on a case it was not fitted to. ⚠️ 32 ranks / order 2 ONLY — `predict_seconds` refuses elsewhere. ⚠️ Fitted on EIGENMODE solves; a driven solve does different work and does not belong in it. |
| **faceting error** | `physics.faceting_shift_mhz` | VALIDATED | 5% across six modes (E0f2), from the mesh's measured volume deficit. Mesh sizing for a target accuracy is a calculation, not a sweep. |
| **groove frequency shift** | Slater: Δf/f₀ = −(p_mag[groove] − p_elec[groove])/2 | **UNVALIDATED — falsifier declared** | No free parameter. Requires `--tag-groove`, which defaults OFF and was never passed, so NO grooved solve in the record carries the bin. 🔴 Falsifier: for the 5×10 anchor it REQUIRES (p_mag−p_elec) = +5.17e-02 for TM111 (2.62× the volume share) and +1.14e-05 for TE011 (the two terms cancelling to 1e-5). Both are single numbers; if they miss, Slater is not the model. |
| **hybridised Q** | 1/Q mixes linearly with m=1 admixture fraction f, from A2/A0 | 🔴 **DO NOT USE — its source is LOOPED EIGEN, which SHORTS the loop** (`h3_step3`, 2026-08-24; CONVENTIONS §7v). The hybridisation it fits is almost certainly the shorted-loop ring resonating with TE011, which does not happen with a 50 Ω feed. **A law fitted to an artifact will extrapolate confidently and wrongly across loop size — the exact axis the optimiser wants to search.** Re-derive with attr 91 terminated, or drop. Was "THIN" on 2 points | predicts 31,242 vs 31,154 measured (**0.3%**) and 25,139 vs 24,411 (3.0%). ⚠️ TWO points. Falsifier: a third loop area must also land within a few % or this is a coincidence of two. |
| **plasma suppression of a dielectric shift** | Δf_loaded = (1 − 0.78)·Δf_cold | 🔴 **STATUS DISPUTED — was "VALIDATED", and `KNOWN.md` § NOT ESTABLISHED discards it by name as groove-free.** Two live documents disagreed; this row is the correction. ⚠️ **The DATA is kept** (§7q — quarantine the claim, not the measurement): the numbers below are real and internally consistent. **What is unproven is TRANSFER to a filtered cavity.** 🔑 Argument for transfer: the mechanism is LOCAL — the plasma cuts E_elec at the tube ~75% material-independently — and the groove sits on the END CAPS, far from the torch. Argument against: the suppression is a RATIO of two shifts, and shifts are mode-landscape quantities. ✅ **Test: one grooved ε-pair at a single ne.** If it lands near 78%, the law transfers and the whole ε 2–11.6 range comes back with it. | 77.7% at ε=2.00, 78.0% at 3.78, 78.3% at 6.00 — 0.6 points over a 3× range, each within one mesh pair, and it holds THROUGH the dilute→concentrate back-reaction crossover that was its declared falsifier. Mechanism measured: the plasma cuts E_elec at the tube ~75%, material-independently (74.4% vacuum, 74.7% quartz). ✅ **ε=11.6 MEASURED by DRIVEN** (`h3_sapphire`): 79.6%, predicted −2.9 MHz / measured −2.800. Full range 77.7→79.6%, **1.9 points over 5.8× in ε**. ⚠️ Drift is real and mildly increasing (+0.3/step to ε=6, +1.27 on the last step) — the law is NEARLY flat, not flat. ⚠️ Eigen cannot reach ε⁺/|ε⁻| > ~0.2–0.27; use driven there. |
| 🔴 **Q_ext vs loop area — NON-MONOTONIC** | Q_ext falls, MINIMISES near 176 mm², then RISES | ✅ **MEASURED 2026-08-24, `h3_loopq`** (eigen pairs, grooved) | Q_ext = 19,633 / 11,202 / **9,231** / 13,333 and β = 2.251 / 3.923 / **4.704** / 3.131 at 35 / 82 / **176** / 384 mm². 🔑 **Coupling PEAKS at 176 mm² — the design loop is at the optimum.** Transformer behaviour: M grows with area but L_loop grows faster, so k = M/√(L_loop·L_cav) turns over. **A loop can be too big to couple well.** 🔴 **DO NOT FIT A MONOTONIC LAW** — there is a turning point, and fitting through it is the error that retired the groove-depth law. Extrapolate only on the small-area branch. 🔴 **384 mm² is DOMINATED** (weaker coupling AND 6.0% Q cost vs 2.2%) — retired. 🔑 **Every grooved size is OVERCOUPLED; β = 1 extrapolates to ~10 mm².** To approach matching go SMALLER, which is also cheaper in Q — both objectives agree, which is unusual and worth exploiting. ⚠️ Fassel-torch intuition oversizes the coupler here by ~5×: an ICP load coil is ~20 mm, this cavity is β=4.7 at a fifth that area. |
| **Q₀ vs loop area** | Q₀ falls monotonically; cost mildly sublinear then superlinear | ✅ **MEASURED** | 44,414 (no loop) / 44,196 / 43,946 / 43,422 / 41,747. Q cost 0.5 / 1.1 / **2.2** / 6.0%. ΔQ₀ per mm² falls 6.23 → 5.71 → 5.64 then **turns up to 6.95** at 384 mm², while Δf per mm² keeps falling — **a big loop buys disproportionately more loss for less reactive perturbation.** Purity untouched at every size (worst spread 0.0010). |
| **coupling β vs density** | β = Q₀/Q_ext with Q_ext ≈ 9,117 fixed by geometry; β CROSSES 1 as the plasma loads | ✅ **MEASURED 2026-08-24** | Cold **β = 4.77 (OVERCOUPLED)** from two eigen solves — Q₀(PEC)=43,523, Q_L(50 Ω)=7,538. Every loaded case is UNDERCOUPLED (0.011–0.070). 🔑 **Q_ext is GEOMETRY and nearly constant; Q₀ moves two orders with ne, so the branch flips mid-sweep.** For the surrogate that means β is not a free parameter — it is `Q₀(ne)/Q_ext(loop geometry)`, and **matching to β=1 is a LOOP-SIZE choice made against a chosen operating density**. 🔴 Never fit β from \|S11\| alone (§7x). |
| **sustainment vs density (DESIGN cavity)** | η(ne) plateaus 0.995–0.998 over ne 1e18–1e20 | ⏳ **MEASURED 2026-08-24, PROVISIONAL** | `h3_driven` on groove 5×10 + loop 11×8, referenced to its OWN cold case (same mesh/solver/extraction, §7t). η = **0.9853 / 0.9948 / 0.9977 / 0.9976 / 0.9961** at ne = 1e18…1e20, referenced to the branch-corrected cold Q₀ = 40,645 (eigen cross-check 43,523). ⚠️ First reported as 0.9295…0.9814 on the wrong coupling branch. 🔑 **Not saturating — Q₀ falls 596→93 then RECOVERS to 158** as the plasma turns reflective, so the plateau is a real turning point the surrogate should model, not a ceiling. ✅ `h3_step3` confirms 2.451500 is TE011 (eigen 2.451488, 12 kHz). 🔴 **Do NOT carry the old groove-free η(ne) row's numbers into this** — different cavity, different reference. |
| 🔴 **band margin is a PLASMA property, not a geometry one** | margin ≈ 2.500 − (f₀ + lw/2), and f₀ is set by n_e | ✅ **MEASURED 2026-08-24, `h3_margin`, 12 cells** | **The whole (groove depth × loop area) grid spans 0.8 MHz**: 17.4–18.2 MHz on the f₀ criterion, best +0.6 MHz over the design point, across 5× in area and 2× in depth. ⚠️ First tabulated as 9.3–10.0 on the 3 dB edge; **the headroom doubled, the conclusion did not.** **Groove depth moves loaded f₀ by 0.000 MHz** (identical to 6 figures); loop area by 0.8 MHz; **the plasma by +30.9 MHz**. 🔴 **DO NOT give the optimiser groove depth or loop size as margin knobs — they have no authority over it.** 🔑 The lever is **operating density: 1e20 → 1e19 buys +16.2 MHz AND improves η (0.9964 → 0.9979)** — both objectives agree. ⚠️ But n_e is not only an EM parameter; the analytical cost belongs to the emission side and is unknown here. ⚠️ Groove depth SATURATES by 10 mm and PEAKS there at 176 mm² — **5×10 is at the optimum**, independently re-derived. |
| ✅ **β is a TUNER-RANGE spec, not an efficiency** | the network matches; the design question is the RANGE it must cover | ✅ **MEASURED + hardware confirmed 2026-08-24** | The hardware requires a matching network (user), so raw β never was a system efficiency. **The tuner must cover β = 4.715 (cold) → 0.017 (n_e=1e20): a factor of 275**, and it **crosses perfect match at n_e ≈ 5×10¹⁶** — essentially at ignition, **REVERSING DIRECTION** (overcoupled before, undercoupled after) while the frequency loop slews +30.9 MHz. 🔴 **VSWR is NON-MONOTONIC and WORST at ~1e19 (99.3), not at 1e20 (58.4)** — Q₀'s minimum. The PIN tuner's hardest condition is MID-RANGE. Circulator dump takes up to **961 W of 1 kW** unmatched. ⚠️ ~58:1 transformation at steady state; a 3-stub tuner does ~20:1 comfortably. 🔑 **For the optimiser: Q_ext should be scored on the RANGE it forces the tuner to cover, not on how close β sits to 1** — β=1 is unreachable in steady state and that is fine. 🔴 The old "6.6% delivered / 93% reflected" figures are WITHDRAWN. |
| 🔴 **loaded critical coupling is UNREACHABLE by loop geometry** | β_loaded = Q₀(n_e)/Q_ext, and Q_ext has a floor | ✅ **MEASURED** — ⚠️ **and no longer a defect**, see the tuner row above | Q₀ collapses **275×** cold→loaded (43,423 → 158) while Q_ext is geometry. Q_ext MINIMISES at **9,231**, so **β_loaded ≤ 0.017** for any cap loop of this family. **⚠️ **the raw-β "93% reflects" reading is WITHDRAWN** — the hardware matches (see the tuner row).** 🔑 **A loop critically coupled COLD is hopelessly undercoupled LOADED** — never carry a β between regimes. ⚠️ Whether 6.6% is the system efficiency depends on an impedance-matching element this programme cannot see; if the tuner only chases frequency into a fixed 50 Ω, β is the whole story. **Ask before treating it as a system number.** |
| **cold Q_ext predicts LOADED dip depth** | β_loaded = Q₀_loaded / Q_ext(cold) | ✅ **VALIDATED to ~20%** | Predicted −0.14 / −0.25 / −0.30 dB, measured −0.16 / −0.25 / −0.30 across 35 / 82 / 176 mm². 🔑 **One cold eigen pair per loop size predicts coupling at any density** — cheap, and it removes the need for a driven fit to get β. ⚠️ Good enough for coupling; NOT good enough to derive Q₀ from (the 1/Q_L − 1/Q_ext subtraction is ill-conditioned when overcoupled). |
| **band clearance under load (constraint, not objective)** | upper 3 dB edge must stay < 2.50 GHz | ⏳ **MEASURED, PROVISIONAL — margin is THIN** | 🔴 **CRITERION CORRECTED 2026-08-24: the tuner PARKS AT f₀, so the margin is f₀→2.500, NOT the 3 dB edge.** Cumulative pull **+30.9 MHz** cold→1e20; f₀=2.4824 leaves **17.6 MHz** (previously reported as 9.6 on the wrong criterion). ⚠️ The cavity linewidth is not a band-occupancy constraint — the LDMOS emits at ONE frequency. 🔴 **SUPERSEDED 2026-08-24 by `h3_margin`, which SEARCHED that joint space and found it flat.** This row previously read *"the feasibility constraint that makes groove size a live variable"* — **it is not.** Groove depth moves the loaded f₀ by **0.000 MHz** and the whole 12-cell grid spans 0.7 MHz. **The constraint is real; the geometry knobs have no authority over it.** The lever is n_e. ⚠️ A driven sweep bounds what the PORT COUPLES TO; mode competition still needs eigen. |
| **sustainment vs density (groove-free, OLD)** | η(ne) flat ≥ 0.99 | **VALIDATED, 2 decades** | η = 0.9913 / 0.9959 / 0.9982 / 0.9980 / 0.9969 at ne = 1e18…1e20 on the r=2–8.5 mm annulus. ⚠️ Annulus ONLY — a 2 mm SOLID column gives 0.185 at ne=1e18 (17× less plasma). Do not carry η across geometries. |
| **driven sweep cost** | samples ∝ Q (step must resolve f₀/Q) | **VALIDATED** | empty ~35,800 samples for ±40 MHz, loaded ~130. Inverts the "driven is expensive" rule in the loaded regime. ⚠️ The BAND must bracket the widest feature; the step only has to resolve the narrowest. Getting that backwards cost two runs. |
| **element cost ordering** | the LOOP dominates TE011's degradation; the groove is ~free | **MEASURED, and the ordering is safe** | ✅ `h3_ladder` 2026-08-24. **Groove 5×10 on the bare cavity** — a true single-element measurement, both endpoints solved: Δf **+0.094 MHz**, Q **×1.008**, purity **+0.0012**. **Adding the loop to that grooved cavity**: Δf **−10.558 MHz**, Q **×0.278**, purity **−0.0562**. 🔑 **Prior for the acquisition function: spend evaluations on LOOP geometry; treat groove size as cheap in Q and f.** The ordering is ~100× in Δf and holds regardless of how the second term is attributed. |
| 🔴 **groove × loop: NOT SEPARABLE** | the groove's effect DEPENDS on the loop, and enormously | ✅ **MEASURED 2026-08-24, `h3_loopq` F4** | Same 11×8 loop, identical mesh, groove present or absent: **Q_ext 76,811 → 9,231 (8.3×)** · **β 0.402 → 4.704 (12×, and it CROSSES 1)** · Q₀ 30,878 → 43,422 (+41%) · purity **0.7593 → 0.9997**. 🔑 **MECHANISM:** ungrooved, TE011 and TM111 are EXACTLY degenerate, so the loop hybridises them; the groove moves TM111 away and there is nothing left to mix with. 🔴 **THE OPTIMISER MUST SEARCH THE JOINT (groove, loop) SPACE.** Any prior fitted on one axis with the other fixed is invalid — including anything derived on an ungrooved cavity, where the loop couples to a *hybrid* and coupling design would optimise the wrong structure. ⚠️ This supersedes the earlier "separability is circular / untested" row: it is now tested, and the answer is NO. |
| **groove depth scaling** | — | **RETIRED** | `Z₀·tan(βd)` → 2.93×, volume fraction → 2.00×, measured 1.72×. 🔴 Both assume a UNIFORM field across the slot. Worse, the local exponent FALLS from 1.22 (gd 5→10) to 0.78 (10→20): **it is not a power law**, so fitting one was answering the wrong question. Superseded by Slater. |

## 2a. 🔴🔴 n_e IS A FREE VARIABLE, NOT A CONSTANT — AND IT IS THE DOMINANT ONE

**Added 2026-08-24, after `ne = 1e20` was found to have no physical provenance
(CONVENTIONS §7ab). Its origin is SOLVER CONVERGENCE: `h3_eigen` measured where
eigen converges against PI_1 and 1e20 sits in a convergent band. It reached
"the operating point" in six citation steps, none of which introduced the claim.**

🔑 **FOR THE SURROGATE THIS IS THE BIGGEST SINGLE CHANGE.** n_e was being treated
as a fixed condition under which geometry is optimised. It is not fixed, and it
**dominates every geometry knob measured**:

| lever | range | margin swing |
|---|---|---:|
| groove depth | 1.4× | 0.3 MHz |
| loop area | 5× | 0.6 MHz |
| **n_e** | 10× | **16.2 MHz** |

🔴 **SO n_e MUST ENTER THE SEARCH SPACE, NOT THE CONSTRAINT SET.** An optimiser
that holds n_e at 1e20 and searches geometry is searching the 0.6 MHz axis while
holding the 16 MHz one fixed at an arbitrary value.
⚠️ **BUT IT IS NOT THE OPTIMISER'S TO CHOOSE FREELY.** n_e is set by what the
application needs — atomisation and excitation — which is outside this
programme. **Treat it as an INPUT to be supplied and swept over, with the EM cost
of each value now measured**, rather than as something to minimise.
🔑 **The EM cost of lowering it is NEGATIVE** — η *improves* 0.9964 → 0.9979 from
1e20 to 1e19 while margin gains 16.2 MHz. **Both EM objectives prefer lower n_e.**
The constraint that stops you is analytical, not electromagnetic.

🔴 **AND THE INSTRUMENT HAS A HOLE AT n_e ≈ 1e19** (PI_1 = 1.76): eigen does not
converge there. **Driven does.** Any surrogate trained on eigen data will have no
samples at the most interesting density — record that as a sampling constraint,
not a region to avoid.

## 2b. 🔴 WHICH SOLVER PRODUCED A PRIOR IS PART OF THE PRIOR

**Added 2026-08-24 after eigen and driven disagreed by 11.5 MHz on the same mesh.**

An unassigned boundary is **PMC**, the natural BC of the curl-curl E formulation.
The mesh carries `port = 91`; the eigen config assigns a BC to attribute 90 only.
**So every eigen solve on a LOOPED cavity left the feed gap OPEN** — an LC
resonator near 2.45 GHz that hybridises TE011 into a pair. Terminate the port and
eigen agrees with driven to **12 kHz**.

🔑 **For the surrogate this is not a caveat, it is a factor.** Two points that
differ in solver are not two samples of one function; they are samples of two
different functions. **Tag every observation with its boundary condition** and
never fit across the boundary without a term for it.
🔴 **The looped-eigen corpus is suspect wholesale** — `h3_cold`, `h3_loopsize`,
`h3_eigen`, `h3_superpose`, every β-vs-loop-area figure, and the "hybridised Q"
prior below. **Loop geometry is exactly the axis the optimiser most wants to
search, and it is the axis this defect corrupts.**
✅ Loop-free eigen (`h3_ladder` steps 1–2, H2, E0, H1) is unaffected: no port.

## 3. Failure taxonomy — the evaluation policy

🔴 **An evaluation that did not converge is MISSING DATA, not a bad score.**
Scoring failure as "bad" teaches the surrogate to avoid regions that are
perfectly good and merely hard to solve. Every failure below must be returned as
a distinct outcome, never as a number.

| failure | detection | status |
|---|---|---|
| NLEPS divergence | `nconv` flat while residual rises; Armijo α collapses to ~2e-3 | VALIDATED post-hoc — ⚠️ NOT valid as a live abort (6-consecutive-rising fires 146× and 381× in runs that CONVERGED) |
| solve over budget | `NLEPS_BUDGET = 1000` | THIN — 25 converged runs used ≤ 869, the 2 failures used 1,445 and 4,114. **1.66× margin on two failures.** A budget, deliberately, not a predictor |
| non-manifold mesh | Palace rejects at startup | VALIDATED — caused by ungated geometry flags (CONVENTIONS §12) |
| mode outside the solved window | `eigmodes.te011_tm111` ball guard: refuse when the candidate is further from the target than the search reached in EITHER direction | VALIDATED — catches the real H2b case that invented a mode at 2.60631 |
| mode misidentified | signature distance + **margin over best alternative** | THIN — `reject_at = 0.002`, from 4 true matches (≤ 0.00088) and 4 nearest-false (≥ 0.00397). Separation only **4.5×**, and worst at weak coupling |
| **eigen wall-clock timeout while PROGRESSING** | NLEPS count rising, well under `NLEPS_BUDGET`, but the case exceeds its wall limit | 🔑 **NEW 2026-08-23** — `h3_cold` 11×8 cold: **174 NLEPS in 900 s**, budget 1,000. **Not a convergence failure**: it was iterating. ⚠️ 28×20 converged on IDENTICAL settings, so the boundary is marginal, not sharp. **Return as MISSING DATA and record the NLEPS count** — the count is what distinguishes "slow" from "stalled" |
| **classifier declines to label** | `azimuthal.order()` returns `m=None` on a MIXED mode | 🔑 **NEW 2026-08-23** — loaded A2/A0 = **0.3244** vs 0.0004 for an uncoupled mode. **The mixing is physics, not failure.** A strict `m == 0` test DISCARDS converged data (CONVENTIONS §7l). Return the mode with its A2/A0 and a flag, never nothing |
| wrong reference for a derived quantity | — | 🔴 **UNDETECTED, and it bit.** Comparing driven Q₀ against TE011's bare Q when two of four solves were reading TM111 produced a confident, entirely spurious trend. Nothing flagged it; an eigen sweep was needed. See §5 |

## 3b. 🔴 Coupling: β and Q_ext have NO CONSUMER until H3

β = Q₀/Q_ext, and β ≈ 1 at the OPERATING POINT is the real requirement. The
plasma is a loss inside the cavity, so it moves Q₀ by 1–2 orders of magnitude:
**a loop tuned to β = 1 empty is 10–100× undercoupled once lit.**

The design quantity is **Q_ext** — the loop's own property — sized so
**Q_ext ≈ Q₀ LOADED**.

✅ **Q₀ LOADED IS NOW MEASURED (2026-08-23).** On the r=2.0–8.5 mm annulus,
**Q₀ = 80–360 across ne = 1e18–1e20** (η = 0.991–0.998). So the matching target
exists: **Q_ext ≈ 10²**, against the ~5×10⁴ of the 11×8 cap loop — the loop must
couple roughly **300–500× more strongly** than the one that reads the empty
cavity.
🔑 This confirms the warning above quantitatively: measured β on the loaded
annulus is **0.015–0.098**, i.e. **10–65× undercoupled**, and the |S11| dip is
only 0.26–1.71 dB.
⚠️ **Q₀ itself is the WRONG number to carry forward.** Driven and eigen agree on
η to 0.0006 while differing ~17% on Q₀. Size the loop from **η and P_ref**, not
from a three-digit Q₀.
🔴 **Q_ext is NOT transferable between meshes** — e0k2's 50,709 gives a Q₀ 12×
different from the linewidth route. It is unconverged (71,990 vs 126,483, 76%
apart) and inherits β's 43% mesh non-convergence. **Re-derive it on the loaded
mesh; never carry it across.**

⚠️ β appeared in the anchor rigs only as an intermediate in Q₀ = Q_L(1+β), with a
[0.1, 1] window as measurement HYGIENE. Placing that in the declared criteria
made it look like a design target; it never was, and Q₀ is robust to β being
wrong regardless.

✅ **The gate is lifted, but the rule stands: re-derive on the LOADED mesh.**
CONVENTIONS §6 — do not reuse a parameter without re-deriving it for the case —
and the case is the loaded cavity, which now exists to derive against.

## 3c. 🔑 FEASIBILITY CONSTRAINTS — hard, and CO-DEPENDENT

⚠️ **These are not objective terms and must not be traded against one.** A point
that violates one is INFEASIBLE, not merely low-scoring.

| constraint | statement | status |
|---|---|---|
| **band clearance** | **exactly ONE mode in 2.40–2.50 GHz** (the LDMOS tuning range) — because the tuner locks to the deepest in-band dip and cannot be told which mode to prefer | 🔑 **NEW 2026-08-23.** Cold: H2 established 5×10 mm clears it (TM111 −64.25 MHz). Loaded: ONE measurement so far (11×8, ne=1e20, one mode in band at 2.4600) — ⚠️ and 2.507 sits only **7 MHz** outside the upper edge |
| **loop size ↔ band clearance** | at the SAME groove (5×10) and cold, **11×8 → filter holds, 28×20 → TWO modes in band** (2.4048 Q=13,623 A2/A0=0.256; 2.4460 Q=30,222 A2/A0=0.048). **Loop size alone flips feasibility.** | 🔑 **NEW 2026-08-23 `h3_cold`.** Two points, one groove, cold only |
| loaded band residency | the loaded TE011 must STAY inside 2.40–2.50 | THIN — the groove-free measurements are discarded; one grooved point exists |

🔴 **BAND CLEARANCE IS CO-DEPENDENT ON AT LEAST FOUR VARIABLES**, and this is why
the surrogate cannot treat them as separable:

    groove depth  x  loop size  x  n_e  x  torch permittivity  ->  mode landscape

Evidence that each moves it, all measured:
- **groove depth** — TM111 −64.25 MHz at 5×10 (H2)
- **loop size** — cold 28×20 shows **TWO** modes in band where 11×8 shows the
  filter working; a loop MIXES the triplet (`pair_q_ratio` 1.000 → 1.364)
- **n_e** — loading moves every mode; the loaded cluster sits at 2.362 / 2.460 /
  2.507 where cold it is elsewhere
- **torch permittivity** — a dielectric shifts f₀ (the groove-free numbers are
  discarded, but the DIRECTION is not in doubt)

🔑 **Consequence for the optimiser: band clearance must be evaluated as a
CONSTRAINT FUNCTION over the joint space, not inherited from a cold single-point
check.** H2's 5×10 is a validated BASELINE, not a feasible-everywhere constant.
~~**Refining it under load is H3's job.**~~ ✅ **DONE 2026-08-24 — `h3_margin`
found the loaded margin FLAT in groove depth (0.000 MHz over 7–14 mm) with an
optimum at 10 mm. 5 × 10 stands.**

## 3d. 🔑 EVALUATION COST AND OUTCOME — measured, for the acquisition function

⚠️ A surrogate that does not know what an evaluation COSTS, or how often it
returns nothing, will plan sweeps that cannot be run.

`h3_cold`, 2026-08-23, eigen order 2, 32 ranks, groove 5×10, N=6, target 2.30:

| case | tets | outcome | NLEPS reached |
|---|---:|---|---:|
| 11×8 cold | 43,685 | 🔴 timeout @900 s | 174 |
| 28×20 cold | 46,182 | ✅ converged | — |
| 11×8 loaded | 80,621 | ✅ converged | — |
| 28×20 loaded | 72,969 | 🔴 timeout @900 s | 27 |

🔑 **50% of evaluations returned MISSING DATA at a 900 s budget.** An acquisition
function must price that in, and §3 forbids scoring them as "bad".
🔑 **Loading roughly DOUBLES the mesh** (44–46k cold → 73–81k loaded) — a lossy
volume needs resolving — and the loaded operator costs far more per NLEPS
(27 iterations in 900 s vs 174 cold). **Cost is NOT a function of tets alone.**
⚠️ Both timeouts were **progressing**, not stalled (§3). The budget was wall
clock, not `NLEPS_BUDGET = 1000`.

## 4. Objective terms

🔑 **`P` (field-structure purity) is now the primary mode-quality term** — see
below. It is continuous, cheap, aliasing-proof, and it finally makes "how does
this cavity change alter the modes" a MEASURED quantity rather than a label.
**Every eigen evaluation should emit it.**

⚠️ A reward of "+N per MHz of shift" is unbounded and drives straight toward
λ/4, where Q collapses. Every term needs a bound and a physical justification.

| term | why | status |
|---|---|---|
| **TM111 rejection** | ⚠️ **satisfied ONLY under the TE-only architecture.** 5×10 mm puts TM111 478 loaded linewidths off resonance, drawing 7.4e-07 of resonant power; doubling the shift buys 4× on a number already 10⁶ down. 🔴 **But if TM ignition is pursued it becomes SELECTIVE rejection** — reject TM111 while ACCEPTING TE011 *and* TM020 or TM012 in the same ~100 MHz band. See §7 | VALIDATED for TE-only; 🔴 **UNSOLVED** for TM ignition |
| **mode purity P** (field-structure) | 🔑 **NEW 2026-08-23 and it is the measurable one.** P = \|E_φ\|²/(\|E_r\|²+\|E_φ\|²+\|E_z\|²) at several φ; TE011 has P=1 at every φ so the **SPREAD across φ** is the discriminator. **No decomposition, so no aliasing** — it correctly rejects TE311, which A2/A0 binned as m=0 with 0.0004. **Measured priors: bare P ≥ 0.9973 (spread 0.0027); design cavity with an 11×8 loop P ≈ 0.942 (spread 0.0575) — the loop HYBRIDISES TE011.** Costs 6 probes and no extra solve, so it can be emitted by every eigen evaluation | **VALIDATED** on the bare cavity against closed form; ⚠️ the design-cavity number is one loop, one configuration, cold |
| **mode purity A2/A0** | 🔑 first-class term, **not a classification step**. A geometry that reaches its target by HYBRIDISING TE011 with TM111 is not the design wanted — and A2/A0 detects that where a binary label says "TE011" and moves on | VALIDATED: 134× m=0/m=1 separation on the bare cavity, and a DRIVEN solve recovers the eigen value to **1.9%** |
| **identification margin** | the objective must REFUSE to score a point whose margin is poor | THIN — see §3 |
| delivered power | LOD runs through it | 🔴 BLOCKED on H3 |
| σ_background, sensitivity | LOD = 3σ/sensitivity | 🔴 BLOCKED on external optical inputs |

## 5. Known traps

🔴 **A driven solve returns a DIP, NOT A LABELLED MODE.** A cap loop couples
preferentially to a TM111 polarisation when small and to TE011 only above
~176 mm² — at essentially the same frequency either way. Pair every driven solve
with mode identification; never compare a driven quantity against an ASSUMED
mode.

🔴 **A probe at one azimuth breaks the symmetry that DEFINES m.** With a loop
present there is no pure TE011: the 176 mm² loop leaves the mode 35% TM111. So
"which mode is this" has no exact answer in a loaded cavity, and A2/A0 —
continuous — is the right question. It predicts Q to 0.3%.

🔴 **A probe can be weak in FREQUENCY and strong in Q.** The loop shifts TE011 by
0.40 MHz and changes its Q by 32%. Frequency is a volume integral, Q a
surface-current one. A frequency-perturbation check says NOTHING about Q.

🔴 **Design separability ≠ measurement separability.** Disjoint support (Slater
superposition) makes variables independent DESIGN choices; it does not make their
MEASUREMENTS independent.

🔴 **Cross-epoch comparison is not measurement.** Three "surprising"
discrepancies were bookkeeping: 95× in solve cost was laptop-4-ranks vs
instance-32; 3.7× driven-vs-eigen was solver order 1 vs 2; 410× in β was two
different cavity designs.

## 7. 🔴 The mode-filter constraint has TWO regimes, and one has no device

**TE-only architecture** — reject TM111, keep TE011. ✅ Solved: the annular
groove, 5×10 mm, TM111 −64 MHz for a 0.3% Q cost.

**TM-ignition architecture** — 🔴 **DISCARDED 2026-08-22** on two independent
measured legs: the annular groove cannot spare a TM companion (below), AND no
mode cold-ignites anyway (TM010, the best available at 29× TE011's bore energy,
reaches 36 Td at 3 kW against a ~100–150 Td threshold). Ignition is auxiliary —
a thermal kernel from an external spark — so the operating mode was never the
ignition question. See HYPOTHESES H4.

✅ **The architecture is therefore FIXED: TE-only.** The mode-filter variables
are settled at 5×10 mm and leave the search space.

Retained because the measurement is worth keeping:

| | cap current | groove |
|---|---|---|
| TE0np | purely AZIMUTHAL | parallel — unaffected |
| **TM0np** (TM012, TM020) | **purely RADIAL** | **cuts it — suppressed** |
| TM1np (TM111) | partly radial | suppressed (intended) |

H2's own data, signature-matched d0 → gd=20: TE011 moved **−0.0 MHz / −0% Q**,
while TM010 moved −32.8 MHz (−40% Q) and TM011 −113.8 MHz (−59% Q). **TE011 is
the only mode the groove spares.**

🔑 **Any AXISYMMETRIC filter is blind to m by construction.** TM111 is m=1;
TM012 and TM020 are m=0. The only property separating keep from reject is m, so
selective rejection REQUIRES an azimuthally structured perturbation — a
different device, not a tuned version of this one.

⚠️ And TE011's own survival depends on the filter running PARALLEL to its
azimuthal cap current, so an azimuthally structured filter risks the mode it
must protect. Not designed; do not guess.

**For the optimiser**: the mode-filter variables are NOT a continuous parameter
sweep. They are a discrete architecture choice that changes which constraint set
applies. Do not put groove width/depth in a search space until the architecture
is fixed.

## 8. Azimuthal binning — how many sectors

Mode m lands on angular harmonic **k = 2m**, folding under N sectors to
`min(k%N, N−k%N)`. Choosing N is a LOOKUP: ask `physics.spectrum()` which m are
in the window, then pick N with no collision among them, plus margin.

| N | resolves | note |
|---:|---|---|
| 3, 4, 6 | 🔴 nothing usable | collide among m = 0,1,2 |
| **5** | m = 0,1,2 | ⚠️ m=4 ≡ m=1 and m=5 ≡ m=0. Adequate for the 2.25–2.80 window ONLY because m≤2 there |
| ~~9~~ | ~~m = 0..4~~ | 🔴 **UNBUILDABLE**: air sectors start at attribute 3, so N=9 reaches 11 = `TAG_UPSTREAM` and gmsh refuses ("Physical volume 11 already exists"). **Any N ≥ 9 collides.** |
| **8** | m = 0,1,2 | the achievable maximum — same coverage as N=5 (m=3 aliases onto m=1, m=4 onto m=0) |

🔴 **No currently buildable sector count separates m=0..4.** Doing so requires
renumbering the reserved attributes in `geometry.py`. For the modes actually in
the 2.25–2.80 GHz window (m ∈ {0,1,2}) N=5 suffices, so nothing measured is
affected — what is lost is margin against unexpected high-m modes.

⚠️ `geometry.py`'s help claimed "5 resolves m=1..4". It does not. Corrected.
⚠️ N ≥ 3 keeps the m=1 pair degenerate (C_n with n≥3 has a 2-D irrep for m=1).

## When to start

🔴 **Not on the machinery — on the OBJECTIVE.** LOD = 3σ_background/sensitivity
needs the optical path (blocked on the spectrometer f-number, an external input)
and delivered power (H3, unmeasured). Until both land, any objective is a proxy.

**Readiness checklist:**
- [ ] H3 measured — plasma loading, and whether the groove's margin survives it
- [ ] optical inputs received — spectrometer f-number sets viewport, trap AND lapped-zone length
- [ ] Slater validated or refuted against its declared falsifier
- [ ] **bore radius chosen deliberately** — re-derived at order 2, not inherited
- [ ] **gas-flow ceiling measured for N₂**, not taken from MP-AES/MICAP
- [ ] **torch geometry derived for Nitrogen** — the Fassel geometry is Argon's
- [x] ✅ **mode-filter architecture FIXED: TE-only** (2026-08-22). TM ignition
      discarded on two independent measured legs. The groove is frozen at
      5×10 mm and its variables LEAVE the search space. No azimuthally
      structured filter is needed.
- [ ] identification margin re-derived for the loaded region topology
- [x] ✅ **driven-only azimuthal measurement demonstrated** (2026-08-22): a
      driven solve recovers the eigen A2/A0 to **1.9%** (0.1066 vs 0.1087).
      Eigen is needed ONCE per region topology to fix the pure-m endpoints, not
      per evaluation. ⚠️ The quantity is CONTINUOUS (hybridisation fraction),
      not a discrete label — with a probe present no mode is a pure m state.
