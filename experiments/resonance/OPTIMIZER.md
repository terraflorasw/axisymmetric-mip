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
| **hybridised Q** | 1/Q mixes linearly with m=1 admixture fraction f, from A2/A0 | **THIN** | predicts 31,242 vs 31,154 measured (**0.3%**) and 25,139 vs 24,411 (3.0%). ⚠️ TWO points. Falsifier: a third loop area must also land within a few % or this is a coincidence of two. |
| **plasma suppression of a dielectric shift** | Δf_loaded = (1 − 0.78)·Δf_cold | **VALIDATED over ε 2–11.6** | 77.7% at ε=2.00, 78.0% at 3.78, 78.3% at 6.00 — 0.6 points over a 3× range, each within one mesh pair, and it holds THROUGH the dilute→concentrate back-reaction crossover that was its declared falsifier. Mechanism measured: the plasma cuts E_elec at the tube ~75%, material-independently (74.4% vacuum, 74.7% quartz). ✅ **ε=11.6 MEASURED by DRIVEN** (`h3_sapphire`): 79.6%, predicted −2.9 MHz / measured −2.800. Full range 77.7→79.6%, **1.9 points over 5.8× in ε**. ⚠️ Drift is real and mildly increasing (+0.3/step to ε=6, +1.27 on the last step) — the law is NEARLY flat, not flat. ⚠️ Eigen cannot reach ε⁺/|ε⁻| > ~0.2–0.27; use driven there. |
| **sustainment vs density** | η(ne) flat ≥ 0.99 | **VALIDATED, 2 decades** | η = 0.9913 / 0.9959 / 0.9982 / 0.9980 / 0.9969 at ne = 1e18…1e20 on the r=2–8.5 mm annulus. ⚠️ Annulus ONLY — a 2 mm SOLID column gives 0.185 at ne=1e18 (17× less plasma). Do not carry η across geometries. |
| **driven sweep cost** | samples ∝ Q (step must resolve f₀/Q) | **VALIDATED** | empty ~35,800 samples for ±40 MHz, loaded ~130. Inverts the "driven is expensive" rule in the loaded regime. ⚠️ The BAND must bracket the widest feature; the step only has to resolve the narrowest. Getting that backwards cost two runs. |
| **groove depth scaling** | — | **RETIRED** | `Z₀·tan(βd)` → 2.93×, volume fraction → 2.00×, measured 1.72×. 🔴 Both assume a UNIFORM field across the slot. Worse, the local exponent FALLS from 1.22 (gd 5→10) to 0.78 (10→20): **it is not a power law**, so fitting one was answering the wrong question. Superseded by Slater. |

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

## 4. Objective terms

⚠️ A reward of "+N per MHz of shift" is unbounded and drives straight toward
λ/4, where Q collapses. Every term needs a bound and a physical justification.

| term | why | status |
|---|---|---|
| **TM111 rejection** | ⚠️ **satisfied ONLY under the TE-only architecture.** 5×10 mm puts TM111 478 loaded linewidths off resonance, drawing 7.4e-07 of resonant power; doubling the shift buys 4× on a number already 10⁶ down. 🔴 **But if TM ignition is pursued it becomes SELECTIVE rejection** — reject TM111 while ACCEPTING TE011 *and* TM020 or TM012 in the same ~100 MHz band. See §7 | VALIDATED for TE-only; 🔴 **UNSOLVED** for TM ignition |
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
