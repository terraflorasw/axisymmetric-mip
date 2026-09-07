# Q_LEDGER.md — every Q currently in play, with its qualifiers

> User, 2026-09-04: *"the Q family of values have changed a lot over time, and
> frankly I lost track"*

**Built from `baselines.json` and the result files on 2026-09-04, not from
memory.** Regenerate rather than trust: the numbers below are extractions, and
`verify_identities.py` checks them.

## 🔑 A Q NEEDS THREE QUALIFIERS. Drop one and two measurements print identically.

| qualifier | values | why it matters |
|---|---|---|
| **state** | cold / loaded | <!-- q:ok defines the axis --> Q0 falls ~390x between them |
<!-- q:ok defines the axis --> | **cavity** | vacuum torch / **design torch (sapphire 9.39)** | the torch moves f0 ~10 MHz and Q_ext ~20% |
<!-- q:ok --> | **loop** | none / 11x8 cap / 11x8 barrel / + series gap | Q_ext moves **27x** across these |

⚠️ And for a LOADED value, a fourth: the **density**. ⚠️ `coupling.beta` is **not
a key in `baselines.json`** — it is a derived ratio, `Q0/Q_ext`, and both sides
must carry the same qualifiers.

---

## COLD — the cavity's own Q, by how much loop is in it

| Q0 | cavity | loop | solver | source |
|---:|---|---|---|---|
| 44,414 | grooved | **no loop** | eigen | `h3_loopq` anchor |
| 43,523 | vacuum torch | 11x8 cap | eigen, pec | `h3_step3` — the `eta.reference` |
| 43,422 | no torch | 11x8 cap | eigen, pec | `h3_loopq` |
| 37,516 | vacuum torch | barrel + gap2 **0.75** | eigen, pec | `h3-loop-gap2-02` |
| 27,863 | vacuum torch | barrel + gap2 **2.25** | eigen, pec | `h3-loop-gap2-02` |
| 30,235 | vacuum torch | barrel + gap2 2.25 | **driven**, branch-resolved | `h3-gap2load-01` |
| **29,724** | **DESIGN torch** | barrel + gap2 2.25 | **driven**, branch-resolved | `h3-gap2load-02` |

🔑 **The loop costs ~30% of `cavity.Q0.cold`** (43,523 cap -> 27,863 barrel+gap2 2.25, both vacuum torch, eigen). ✅ **The TORCH
costs almost nothing cold**: 30,235 (vacuum) vs 29,724 (design) = **1.7%**.
✅ Driven vs eigen on the same vacuum cavity: 30,235 vs 27,863 = **+8.5%**.

## COLD — Q_ext, i.e. how hard the port drains it

| Q_ext | loop | cavity | solver |
|---:|---|---|---|
| 9,231 | 11x8 cap | no torch | eigen pair |
| 9,117 | 11x8 cap | vacuum torch | eigen pair |
| 8,462 | 11x8 cap | vacuum torch | driven dip |
| 8,716 | 11x8 **barrel**, no gap | vacuum torch | eigen pair |
| 720 / 580 / 461 / **322** | barrel + gap2 0.75 / 1.0 / 1.5 / **2.25** | vacuum torch | eigen pair |
| 270 | barrel + gap2 2.25 | vacuum torch | **driven** |
| **253** | barrel + gap2 2.25 | **DESIGN torch** | **driven** |

🔴 **THE 27x LEVER IS THE SERIES GAP — AND IT IS THE KNOB, NOT A FIXED FEATURE.**
8,716 -> 322, the largest single effect in this table. ⚠️ I first wrote *"a
machined feature, not a tuning knob"*; that is **backwards**. It is set at
manufacture but it is **the design variable for reaching coupling.beta = 1**.

⚠️ **`gap2` HAS NO CANONICAL VALUE.** Every other loop parameter is in
`baselines.json` — `loop.size.mm`, `loop.gap.mm`, `loop.wire_r.mm`,
`loop.cap_r_frac`. `gap2` is **absent**, because it is a SWEPT parameter whose
sweep is recorded as *"not bracketed — 27.0x at 2.25 mm, still falling"*.
**2.25 mm is the widest PROBE, not a chosen design value**, so every row below it
reads "at gap2 = 2.25", never "for the design".

## LOADED — by density and cavity

| ne | cavity | loop | Q_L | Q0 | Q_ext | coupling beta | <!-- q:ok header -->
|---|---|---|---:|---:|---:|---:|
| 7.3e18 | vacuum | 11x8 **cap** | 106.9 | **108.3** | ~8,150 ⚠️ | 0.0133 ⚠️ |
| 7.9e18 | vacuum | 11x8 **cap** | 103.3 | **104.6** | ~8,221 ⚠️ | 0.0127 ⚠️ |
| 7.3e18 | vacuum | barrel + gap2 2.25 | 84.5 | 112 | 342 | 0.3278 |
| 7.9e18 | vacuum | barrel + gap2 2.25 | 81.7 | 107 | 343 | 0.3124 |
| 7.3e18 | **DESIGN** | barrel + gap2 2.25 | 62.8 | 79 | 305 | 0.2586 |
| **7.9e18** | **DESIGN** | barrel + gap2 2.25 | 60.6 | **76** | **305** | **0.2476** |
| 8.6e18 | **DESIGN** | barrel + gap2 2.25 | 58.5 | 72 | 306 | 0.2371 |

⚠️ **The two cap-loop rows' Q_ext and beta are LOW CONFIDENCE** — their dip is
**-0.22 dB**, below `h3_driven`'s own `SHALLOW_DB = 0.30`. `cavity.Q0.loaded`
(`cavity.Q0.loaded`, vacuum torch, 11x8 CAP loop, no series gap, at ne = 7.3 / 7.9 / 8.6e18 = 108.3 / 104.6 / 99.6) IS sound there, because coupling.beta.loaded << 1 makes Q0 ~ Q_L.

🔑 **On the DESIGN cavity (barrel + gap2 2.25), `cavity.Q_ext` moves only ~21% cold -> loaded (253 -> 305 at ne 7.9e18) but 27x with loop
geometry.** The plasma sits at r = 2-8.5 mm where TE011's E_phi is 7-31% of its
peak, while the loop is at the wall: a strong ABSORBER, a weak PERTURBER of the
field the loop couples to.

---

## ⚠️ SUPERSEDED / DO NOT QUOTE

| value | status |
|---|---|
| every `Q0` column in `h3-gap2load-01/-02` result JSON | computed with `Q_EXT_MEASURED` = 9,231, a **cap-loop** constant. Read `Q0_if_overcoupled` instead. Guard added 2026-09-04. |
| `Q0` = 70,353 in `h3-azimload-01` | **above the bare cavity** — impossible. True value 14,152. |
| `cavity.Q_ext.loaded` ~8,150-8,221, VACUUM torch, 11x8 cap loop, ne 7.3-8.6e18 | dip too shallow to fit |
| eta = 0.9985 in `h3-gap2load-02` (DESIGN cavity, barrel + gap2 2.25) | cross-solver AND cross-cavity reference; suppression flag was set and not read (§7by) |
| the coupling series as **DESIGN** numbers | measured on a VACUUM-torch cavity, pre-restoration (2026-08-26) |

## 🔴 WHAT IS STILL NOT MEASURED

- **`cavity.Q_ext.loaded` by an EIGEN pair** on any cavity — eigen fails at this
  density (R4, eps-near-zero). Every loaded Q_ext here is driven-only.
- **Any design-cavity eigen pair at all** — so driven has no cross-check on the
  cavity we are actually building.
- **The coupling series on the design cavity** — 8,716 / 720 / 322 are vacuum.

## coupling.beta.loaded — the mesh convergence series, 4 points (2026-09-05)

**Context, and every point shares it** — design cavity (torch eps 9.39, groove
5×10 mm), barrel mount, `loop_gap2` 2.25 mm, loop 11×8 mm, `plasma.n_e` 7.9e18,
driven/adaptive PROM. `ret:beta-not-mesh-converged`

| size_factor | tets | Q_L (barrel loop 11x8) | coupling.beta.loaded | cavity.Q0.loaded | cavity.Q_ext.loaded | step in beta |
|---|---|---|---|---|---|---|
| 1.5 | 124,203 | 60.59 | 0.2476 | 75.58 | 305.3 | — |
| 1.2 | 215,649 | 58.18 | 0.2882 | 74.95 | 260.1 | +16.41 % |
| 1.0 | 346,456 | 57.64 | 0.3007 | 74.97 | 249.3 | +4.35 % |
| 0.8 | 631,835 | 56.02 | 0.3264 | 74.31 | 227.6 | +8.56 % |

Artefacts: `h3-gap2load-02.95bb5900`, `h3-betaconv-1p2.596c2136`,
`h3-betaconv2-1p0.c6285d36`, `h3-betaconv2-0p8.f98d5f7b`.

⚠️ **READ THE sf 1.5 ROW FROM `wide_fit`, NOT FROM THE STORED `Q0`.**
`h3-gap2load-02` predates the derivation fix, so its stored `Q0` field is
**60.99** — computed from the cap loop's `Q_EXT_MEASURED` constant and failing
`verify_identities.py` by −19 %. The row above uses `wide_fit.Q0_if_undercoupled`
= **75.58**, which is exactly `Q_L(1+beta)` = 75.58 <!-- q:ok identity applied to the row above: loaded, design cavity, barrel loop 11x8 -->, the value the checker
computes as correct. ✅ The three later points pass identities outright.
🔑 So the series is sound, but only because the raw fit survived beside the bad
derived number — §7bx, a derived quantity must be reconstructible from the raw
measurements in the same artefact.

🔴 **NOT CONVERGED, and the step is NON-MONOTONE.** +4.35 % then +8.56 %: the
finest refinement moved `coupling.beta.loaded` about **twice as far as the one
before it**. A convergence series is supposed to show shrinking steps; this one
does not, so no Richardson-style extrapolation is defensible and **there is no
converged value to quote.** Quote it as *~0.33 and still rising with refinement*,
or do not quote it.

⚠️ **This corrects the 2026-09-04 reading**, which called it "still moving 4.3 %
at the finest resolution" and offered `~0.30` as a best estimate. That was the
three-point series, and the third point happened to fall at the narrowest step.

✅ **`cavity.Q0.loaded` IS stable: 0.88 % across the whole series** (75.58 /
74.95 / 74.97 / 74.31, no trend). This is the same compensation seen on
2026-08-23 — `coupling.beta.loaded` and `Q_L` move together and their product
`Q0 = Q_L(1+beta)` does not (barrel loop 11x8 throughout). <!-- q:ok identity, not a value -->
🔑 **So the mesh-sensitive quantity is the COUPLING,
not the cavity.** Any conclusion resting on `cavity.Q0.loaded` survives
refinement; any conclusion resting on `coupling.beta.loaded` or
`cavity.Q_ext.loaded` does not yet.

⚠️ **`cavity.Q_ext.loaded` spans 305.3 → 227.6, a 14.2 % spread**, still moving
−8.7 % on the last step. The 2026-09-04 statement that matching needs ≈3.3× is
therefore itself unconverged.

🔴 **The series cannot currently be extended.** sf 0.6 is ~1.5 M tets; sf 0.8
already held an ~80 GB plateau at 64 ranks on 123 GB, and tets scale ~sf⁻³.
Extending downward needs the Krylov basis bounded — see `Solver.Linear.MaxSize`
(§7cg), under test as `h3-betaconv3-0p8` against the sf 0.8 value above as its
reference.

## The azimuthal coupler, design cavity, sf 1.0 (h3-azimload-02, 2026-09-05)

Answering: *is `cavity.Q_ext.loaded` set by the LOOP or by the PLASMA?*
`ret:qext-state-independent`

**COLD — measured and branch-resolved.** f0 = 2.4384 GHz, |S11| = −10.34 dB,
Q_L = 4,897 (azimuthal loop, design cavity), overcoupled root beta = 1.874:

    cavity.Q0.cold   = 14,074      cavity.Q_ext.cold = 7,510
    (azimuthal loop, design cavity, no plasma, sf 1.0)

⚠️ Compare the barrel + gap2 2.25 coupler on the SAME cavity, also cold: Q_L = 144,
linewidth 16.96 MHz. The azimuthal loop couples far more weakly — a 0.50 MHz
linewidth against 16.96 MHz.

🔴 **LOADED — NOT MEASURED, and the question is NOT answered.** The loaded dip
has **no measurable 3 dB width**: the low side reached the 2.30 GHz band edge and
the high side turned at 2.4546 GHz before falling 3 dB. So:

    coupling.beta.loaded = 0.2053   (from the DIP DEPTH — sound)
    cavity.Q0.loaded     = UNAVAILABLE
    cavity.Q_ext.loaded  = UNAVAILABLE

🔑 **So `cavity.Q_ext.loaded` is still unmeasured on the azimuthal coupler**, and
*"Q_ext is geometric"* remains UNSUPPORTED — neither confirmed nor refuted by
this run. ⚠️ Do not read the barrel-vs-azimuthal comparison off `coupling.beta`
alone: beta is a ratio, and the two couplers' Q_L differ by ~34x cold, so equal
betas would not mean equal `cavity.Q_ext.loaded`.

⚠️ **This is a BAND/METHOD limitation, not a solver failure.** The PROM converged
cleanly (error 4.83e-04 at n=16, well inside `AdaptiveTol`). Re-running as-is
will reproduce it exactly. Settling it needs a wider sweep band or a complex-S11
fit that does not depend on a 3 dB crossing — a DESIGN change, not a re-run.

⚠️ Also unresolved here: the coupled resonance sits at **neither** eigen
candidate (−13.10 MHz vs `h3_cold` 2.440003, −12.16 MHz vs the anchored
grooved-no-loop 2.450561), so this mode is **not named**. Do not call it TE011
without mode purity on an eigen solve of this mesh.

## 🔴 THE gap2 = 2.25 mm BASIS IS STALE — every input to the choice has moved

**User, 2026-09-06:** *"I want to make sure we reconsider the gap2 width, since I
don't recall if it carried over from the barrel coupler. Also, we changed where
the loop was driven from in the interim, I think."*

✅ **It did NOT carry over.** `gap2 = 2.25 mm` was SELECTED, as the endpoint of a
sweep, on an explicit minimax over the cold and loaded states.
`ret:coupling-series-as-design` `ret:minimax-q0-105`

🔑 **AND THE MINIMAX REASONING STILL STANDS** — it is the most important result in
the coupler work and nothing here touches it: **one `cavity.Q_ext` serves two
states whose Q₀ differ by ~265×**, so driving `coupling.beta.loaded` to 1 costs
the ignition power (cold P_in 556 W → 15 W at 1 kW). *You cannot run a plasma you
never lit.* **Matching loaded is not the design target, and I wrongly implied it
was earlier on 2026-09-06.**

🔴 **What is stale is every NUMBER that picked the gap.** The sweep ran
**2026-08-25** and three things changed after it:

| date | change | affects it? |
|---|---|---|
| 2026-08-26 | torch restoration, vacuum ε=1 → quartz ε=9.39 | 🔴 yes — different cavity |
| 2026-08-27 | `TAG_LOOP = 92`: loop surface separated as **copper 5.8e7** | 🔴 yes — before it the wire was swept into `TAG_WALL` and modelled as the wall's **aluminium 3.5e7** |
| 2026-08-31 | port face → `0.9 × conductor half-extent` | ⚠️ probably not — that was the STRIP branch's 1.8× overshoot; the wire's face was already 0.9×, and commit `2e32105` is 336 insertions / 4 deletions, essentially not touching the barrel path |

🔴 **AND THE TABLE ASSUMED `cavity.Q0.loaded` = 105.** Measured, it is **74.31**,
stable to 0.88 % across the sf 1.5→0.8 series. 105 is ~41 % high, so
`coupling.beta.loaded` and VSWR are wrong at **every** gap in that table — and
therefore **which gap wins the minimax is itself unverified.**

⚠️ **2.25 mm was the LARGEST gap swept** (0.35 / 0.50 / 0.75 … 2.25). An endpoint,
not an interior optimum: whether the minimax keeps improving past it was never
tested.

⚠️ **Standing limitation, before and after:** *the coax transition does not
exist* — a lumped port on an internal face, no wall penetration, no dielectric
bead. A real feed adds reactance that none of these numbers carry.

➡️ **WHAT THIS LICENSES:** re-establish the gap2 lever on the **design cavity,
loaded, copper loop**, and recompute the minimax against the measured
`cavity.Q0.loaded` = 74.31. ⚠️ Bracket 2.25 rather than assuming it — it is
currently an untested endpoint. 🔑 Absolute `cavity.Q_ext.loaded` drifts ~9 % per
mesh refinement, but the drift is same-signed across gaps, so **differences
between gaps at a fixed size_factor are the trustworthy quantity** (`e0kp`'s
same-mesh differencing). `h3-betafloor-*` sets the error bar on how finely the
gaps can be resolved.

## 🔴 THE AZIMUTHAL LOADED CASE HAS NO RESONANCE (h3-azimload-02, 2026-09-06)

`ret:azimload02-beta-no-resonance`

**Read from `port-S.csv` (1,751 points), not from the rig's fit:**

| f (GHz) | \|S11\| dB | arg (deg) | |
|---|---:|---:|---|
| 2.4400 | −3.592 | −32.6 | TE011 continuation seed |
| 2.4600 | −3.623 | −33.0 | **lower than the "minimum"** |
| 2.6024 | **−12.388** | — | the only genuine in-band feature |

🔴 **|S11| is a MONOTONIC SLOPE** from −2.73 dB (2.30 GHz) to −5.25 dB (2.58 GHz).
The "local minimum" at 2.4474 is ripple: its neighbour is lower.
🔴 **AND THE PHASE SETTLES IT — 0.4° over 20 MHz.** A resonance of loaded
`Q_L` ≈ 56 (barrel loop 11x8 + gap2 2.25, quoted for scale) rotates
~180° across its linewidth. **There is no resonance there to measure.**

⚠️ **SO THE EARLIER DIAGNOSIS WAS WRONG.** I recorded twice that this was a fit
method problem — *"widen the band or fit complex S11"*. It is not. The band is
fine, the PROM converged (4.83e-04), and `qfit.py`'s circle fit cannot help
either: **there was nothing there to fit.**

🔑 **AND IT AGREES WITH THE DENSITY SWEEP.** `h3-azimne-01` at 7.9e18 recorded
loaded `Q_L = 4`, `W/W_peak = 0.15%`. That is a ~600 MHz linewidth — **wider than the
whole sweep band**, which is precisely a monotonic slope with no feature. The mode
is plausibly **absorbed out of existence at this density**, which is a PHYSICS
result, not an instrument failure — and it bears directly on the operating-density
fork.

🔴 **OPEN, AND IT MUST BE RESOLVED BEFORE EITHER RUN IS USED:** the BARREL coupler
on the SAME design cavity at the SAME 7.9e18 gives a clean **−5.886 dB dip,
loaded `Q_L` = 56.02, barrel loop 11x8 + gap2 2.25** (`h3-betaconv2-0p8`).
`cavity.Q0.loaded` is a CAVITY property, so
both couplers should see a similarly damped mode. **Either the two runs differ in
something not yet identified, or one of them is wrong.** ⚠️ Do not quote the
azimuthal-vs-barrel comparison — in either direction — until this is settled.

## ✅ THE MESH-TO-MESH FLOOR FOR coupling.beta — MEASURED (h3-betafloor-a, 2026-09-06)

**The question:** the 4-point convergence series moved +16.41 %, +4.35 %, +8.56 %
and was called NOT CONVERGED. That reading is only valid if the steps exceed the
mesh-to-mesh NOISE, which had never been measured for `coupling.beta`.
`e0kp_meshfloor` measured it for FREQUENCY on a BARE cavity (66 Hz over 3 meshes);
a coupling coefficient set by local field structure has no claim on that number.

**Method** (`e0kp`'s, reused): identical parameters, `--no-cache` to force an
independent build, verify **identical topology and DIFFERENT mesh sha**.
✅ 346,456 tets both; cold mesh `d9a101c0…` vs cached `c76d1fba…`; loaded mesh
`bdd14b79…`, `from_cache` ABSENT.

**All rows: design cavity, barrel loop 11x8 + gap2 2.25 mm, sf 1.0; LOADED at
`plasma.n_e` 7.9e18.** <!-- q:ok coordinates stated for every row of the table -->

| state | quantity | cached mesh | fresh mesh | relative |
|---|---|---:|---:|---:|
| COLD | Q_L (barrel 11x8 + gap2 2.25) | 176.35915 | 176.36116 | **1.1e-5** |
| COLD | `coupling.beta.cold` | 0.0069875744 | 0.0069875943 | **2.8e-6** |
| LOADED | Q_L (barrel 11x8 + gap2 2.25) | 57.63730718215648 | 57.637307182125795 | **5.3e-13** |
| LOADED | `coupling.beta.loaded` | 0.3007130004646102 | 0.30071300046696636 | **7.8e-12** |

🔑 **THE FLOOR FOR `coupling.beta.loaded` IS ~1e-11 — FLOATING-POINT NOISE.** The
convergence steps of 4.35 % and 8.56 % are **~9 orders of magnitude above it.**

✅ **SO THE NON-CONVERGENCE IS REAL — AND IT IS *MESH* NON-CONVERGENCE.**
⚠️ User, 2026-09-06: *"this means their Q_ext doesn't agree at different size
factors, not that the solves failed."* Exactly so, and the wording matters:
**every solve in the series SOLVER-converged.** The sf 1.5/1.2/1.0/0.8 runs all
reached `AdaptiveTol` (the sf 0.8 loaded case at n=22, error 2.98e-05) and
returned clean fits. What does not happen is that the RESULTING `Q_ext` settles
as the mesh is refined: 305.3 / 260.1 / 249.3 / 227.6, still moving −8.7 % on the
last step.
🔑 So this is a **resolution** statement about a SERIES, not a failure of any run
— and it is not mesher noise either, since the floor is 1e-11.
`ret:beta-not-mesh-converged` stands as written. See GLOSSARY § *converged*.

🔑 **AND COLD IS ~7 ORDERS MORE MESH-SENSITIVE THAN LOADED** (1e-5 vs 1e-12).
Physically consistent: cold loss is set by wall conductivity and the coupler —
SURFACE quantities that node placement perturbs — while the loaded case is
dominated by bulk absorption in the plasma volume, which 12 µm of node jitter
does not touch. ⚠️ It also means a cold repeatability number must NOT be quoted
as the floor for a loaded one, or vice versa.

⚠️ **ONE PAIR, NOT THREE.** Replicates B and C were cancelled under the
2026-09-06 coupler decision (no further barrel work). With a floor at 1e-11,
further replicates would resolve nothing — but this is a PAIR, so it bounds the
floor rather than estimating a spread.

## ✅ THE VSWR ≤ 3 BUDGET CHANGES THE COUPLER TARGET (2026-09-06)

**User:** *"I've been budgeting VSWR up to 3 for now. It seems feasible to build,
with lots of room for error. But, yet to be characterized beyond back of the
napkin calculations."*

🔴 **MISREAD ON FIRST WRITING, AND THE ERROR INVERTED THE CONCLUSION.** This
entry originally read VSWR ≤ 3 as an acceptable OPERATING POINT — "a band, not a
point target" — and concluded the coupler was 2 % from adequate. **Wrong.** User,
2026-09-06: *"it can't be that close to 3 and still be workable. By 'budgeting' I
mean how much change in cavity impedance can be absorbed by the frequency and
magnitude tuner."*

✅ **VSWR 3 IS THE TUNER'S ABSORPTION RANGE, NOT THE COUPLER'S TARGET.** It is
headroom for VARIATION — plasma state drift, thermal shift, build tolerance —
around a design that should itself sit near **VSWR = 1**. A static coupler AT
VSWR 3.06 has spent the entire budget before any variation exists, leaving the
tuner nothing to absorb with. <!-- q:ok a budget, not a value -->
Read that way, the mesh-convergence series is a VSWR series (all rows: design
cavity, barrel loop 11x8 + gap2 2.25 mm, `plasma.n_e` 7.9e18):

| size_factor | `coupling.beta.loaded` | `cavity.Q_ext.loaded` | VSWR | → plasma |
|---:|---:|---:|---:|---:|
| 1.5 | 0.2476 | 305.3 | 4.04 | 63.4 % |
| 1.2 | 0.2882 | 260.1 | 3.47 | 69.3 % |
| 1.0 | 0.3007 | 249.3 | 3.33 | 70.9 % |
| **0.8** | **0.3264** | **227.6** | **3.06** | **74.0 %** |

*(design cavity, barrel loop 11x8 + gap2 2.25 mm, `plasma.n_e` 7.9e18, driven.)*

🔴 **SO THE TARGET IS 3.06×, AND THE SWEEP MEASURES THE DISTANCE TO IT.** At
sf 0.8 the coupler sits at VSWR 3.06, i.e. **3.06× away from matched**:
`cavity.Q_ext.loaded` must fall from 227.6 to ≈ 75 (= `cavity.Q0.loaded`).
🔑 The size-factor series is not a pass/fail against a budget — **it tells us how
far the coupler is from VSWR = 1**, and the answer is "a factor of three, and the
estimate is still moving."
➡️ **A BETTER COUPLER IS STILL WORTH CHASING** (user, 2026-09-06).

⚠️ **AND THE DISTANCE IS ONLY KNOWN TO ~9 %.** `coupling.beta.loaded` moved
**+8.56 %** on the 1.0 → 0.8 refinement and is still rising, so "3.06×" is itself
uncertain at that level and the true figure is somewhat SMALLER.
`ret:beta-not-mesh-converged` ⚠️ That does not change the conclusion — 3× is 3×
whether it is 2.8 or 3.1 — which is why sub-0.8 convergence stays DEPRIORITISED,
as decided earlier on 2026-09-06.

⚠️ **THE BUDGET ITSELF IS BACK-OF-NAPKIN** (user's words) and is NOT
characterised: *"yet to be characterized beyond back of the napkin
calculations."* It is a claim about what a tuner can ABSORB, and the tuner is
unspecified (`../control-loop/` item 2). So the 3.06× target is firm; the 3× of
headroom around it is provisional.

## ✅✅ THE Q0 MAP OVER (eps, sigma) — h3-q0map-01, 2026-09-07

Design cavity, **plain barrel loop 11x8, NO series gap**, sf 1.0, one shared
mesh (346,456 tets) across all eight rows — so every difference below is physics,
not discretisation. `plasma_source: prescribed`; **`ne` is undefined by design**
and must not be back-inferred.

| eps | sigma | branch | `coupling.beta.loaded` | `cavity.Q0.loaded` | `cavity.Q_ext.loaded` | Q_plasma | sigma·Q_pl |
|---:|---:|---|---:|---:|---:|---:|---:|
| +1.000 | 0.0000 | OVER | 4.967 | 43,611 | 8,780 | — | — |
| +0.997 | 0.0028 | OVER | 2.520 | 22,074 | 8,761 | 44,699 | 125.2 |
| +0.991 | 0.0083 | OVER | 1.302 | 11,298 | 8,675 | 15,248 | 126.6 |
| +0.977 | 0.0204 | UNDER | 0.613 | 5,387 | 8,782 | 6,146 | 125.4 |
| +0.953 | 0.0413 | UNDER | 0.324 | 2,845 | 8,779 | 3,044 | 125.7 |
| +0.907 | 0.0826 | UNDER | 0.168 | 1,476 | 8,775 | 1,527 | 126.2 |
| +0.689 | 0.2753 | UNDER | 0.053 | 461 | 8,749 | 466 | **128.4** |
| −1.456 | 2.1746 | UNDER | 0.0098 | 83.7 | 8,576 | 83.9 | **182.4** |

### ✅ 1. `cavity.Q_ext.loaded` IS GEOMETRIC — 2.3 % over a 520× change in Q0

8,576–8,782 while `cavity.Q0.loaded` fell **43,611 → 83.7**. Mean 8,735 against
`KNOWN.md`'s independently recorded **8,716** for this loop ("no capacitor") —
**0.2 %**, from a different rig and era, with nothing tuned to hit it.
🔑 **This is the evidence `ret:qext-state-independent` said did not exist.** That
retraction stands as written — it rejected a claim resting on ONE coupler
compared with itself — but the claim itself is now supported on the design
cavity across two decades of loading. ⚠️ For THIS loop. A different coupler must
show it separately.

### ✅ 2. THE COUPLING BRANCH, RESOLVED BY CONSISTENCY

The rig reported *"Q_L exceeds Q_ext — Q0 not derivable"* <!-- q:ok verbatim rig
message, not a value; every row is design cavity / plain barrel loop / loaded -->
on **every** row: one dip cannot separate a coupling
coefficient from its reciprocal. But `Q0_if_overcoupled ≡
Q_ext_if_undercoupled`, so across a SERIES only one assignment keeps a geometric
quantity geometric. It picks OVER for the first three rows and UNDER after —
**`beta` passes through 1 between sigma 0.0083 and 0.0204.**
🔑 Cheaper and more robust than the phase-swing test (`e0k2_anchor`), and it works
only because the coupler is held FIXED while the plasma varies.

### ✅ 3. CRITICALLY COUPLED AT sigma ≈ 0.0115 S/m, WITH NO SERIES GAP

From `1/Q0 = 1/43,611 + sigma/125.8` <!-- q:ok the fitted law; all rows are the
design cavity, plain barrel loop 11x8, loaded -->, `cavity.Q0.loaded` =
`cavity.Q_ext.loaded` = 8,735 at
**sigma ≈ 0.0115 S/m**. ⚠️ Not a design recommendation — whether the discharge
sits there is a plasma question. But the bare loop matches itself somewhere in
the avalanche regime, and `h3-azimne-01` independently put its power-transfer
optimum in the same decade on a different cavity with a different loop.

### 🔑 4. `sigma · Q_plasma` = 125.8, THEN IT BREAKS

Constant to **±0.6 % over a 30× range** (sigma 0.0028–0.0826): `Q_plasma = K/sigma`
exactly, which is perturbation theory with a FIXED field distribution — **the
plasma is not shielding anywhere in that range.** Then **+2.1 % at 0.2753** and
**+45.0 % at 2.1746**: absorption falls below proportional, which is shielding.

### ✅ 5. AND THE PROBES CORROBORATE, AT THE SAME ROW

|E| across the bore, normalised at `bore_edge` (closed-form TE011: 0.2391 /
0.5065 / 1 / 3.1989):

    sigma      bore_in  bore_mid  field_peak
    0.0000      0.2396    0.5097      2.7431
    0.0826      0.2392    0.5091      2.7489     <- unchanged to 0.2%
    0.2753      0.2430    0.5090      2.7584
    2.1746      0.2517    0.4883      3.2250     <- moves

**Flat to 0.2 % through sigma 0.0826, moving at 2.1746** — the same row the law
breaks. 🔑 **Two independent observables, one transition.** ⚠️ `bore_mid` falls
(−4 %) as field is expelled from the plasma interior, while `field_peak` RISES
17 % toward the empty-cavity value: the mode reverting to a cavity with a
conducting rod in it. ⚠️ `bore_in` RISES rather than falling — it sits at the
annulus INNER boundary with a vacuum core inside it, so it is not a simple
decay-from-the-surface point; do not read it as a skin-depth probe.

⚠️ **THE TRANSITION IS BRACKETED, NOT LOCATED** — sigma 0.28 to 2.17 is an 8×
gap. `h3-q0map-02` fills it.

⚠️ **AND A COUPLER-INDEPENDENCE CLAIM I MADE EARLIER IS WRONG.** I estimated the
coupler changes `cavity.Q0.loaded` by ~0.1 %, from a loss budget. MEASURED at the
same state (eps −1.456, sigma 2.175, sf 1.0): **83.7 with the plain loop vs 74.97
with barrel + gap2 2.25 — 12 %.** The estimate counted only the loop's added
LOSS; a strongly-coupled loop also PERTURBS THE MODE, which is the larger effect.
🔑 So `Q0.loaded` is a cavity property to ~12 %, not to 0.1 %.

## ✅✅ THE SHIELDING TRANSITION — h3-q0map-01 + -02 COMBINED, 2026-09-07

Twelve states, design cavity, plain barrel loop 11x8, no series gap, sf 1.0.
`h3-q0map-02` fills the 8× gap `-01` left. `plasma_source: prescribed`.

| sigma | eps | branch | `cavity.Q0.loaded` | `cavity.Q_ext.loaded` | sigma·Q_pl | vs K | bore_in | bore_mid |
|---:|---:|---|---:|---:|---:|---:|---:|---:|
| 0.0000 | +1.000 | OVER | 43,611 | 8,780 | — | — | 0.2396 | 0.5097 |
| 0.0028 | +0.997 | OVER | 22,074 | 8,761 | 125.2 | −0.5 % | 0.2396 | 0.5097 |
| 0.0083 | +0.991 | OVER | 11,298 | 8,675 | 126.6 | +0.6 % | 0.2396 | 0.5097 |
| 0.0204 | +0.977 | UNDER | 5,387 | 8,782 | 125.4 | −0.3 % | 0.2395 | 0.5095 |
| 0.0413 | +0.953 | UNDER | 2,845 | 8,779 | 125.7 | −0.1 % | 0.2394 | 0.5094 |
| 0.0826 | +0.907 | UNDER | 1,476 | 8,775 | 126.2 | +0.3 % | 0.2392 | 0.5091 |
| 0.2753 | +0.689 | UNDER | 461 | 8,749 | 128.4 | +2.1 % | 0.2430 | 0.5090 |
| 0.4200 | +0.460 | UNDER | 310 | 8,728 | 131.0 | +4.1 % | 0.2499 | 0.5092 |
| 0.6300 | +0.240 | UNDER | 212 | 8,700 | 134.4 | +6.8 % | 0.2581 | 0.5096 |
| 0.9500 | −0.220 | UNDER | 149 | 8,662 | 142.1 | +13.0 % | 0.2625 | 0.5067 |
| 1.4000 | −0.700 | UNDER | 110 | 8,621 | 154.3 | +22.7 % | 0.2607 | 0.5009 |
| 2.1746 | −1.456 | UNDER | 83.7 | 8,576 | 182.4 | +45.0 % | 0.2517 | 0.4883 |

### 🔑 1. THERE IS NO SHIELDING THRESHOLD — IT IS A GRADIENT

`sigma·Q_plasma` = 125.8 ± 0.6 % up to sigma 0.083, then **+2.1 → +4.1 → +6.8 →
+13.0 → +22.7 → +45.0 %**: smooth, monotonic, accelerating. **No onset sigma can
be quoted**, and that IS the result — the plasma grades into a mirror rather than
switching. ➡️ The penalty for placing a coupler above sigma ≈ 0.1 is continuous,
not a cliff.

### 🔴 2. AND THE ONSET IS **NOT** THE eps = 0 CROSSING

At sigma 0.95, `eps` = **−0.220** — already over-dense — and the departure is only
**13 %**. The transition is well under way at eps = +0.69 and far from complete at
eps = −0.22. ⚠️ **Over-dense ≠ shielding.** `h3-azimne-01` already corrected the
"over-dense mirror" framing once (*"the mechanism is ABSORPTION, not cutoff"*);
this measures the same thing on the design cavity and puts numbers on it.

### ✅ 3. `cavity.Q_ext.loaded` IS GEOMETRIC — AND ITS DRIFT IS PHYSICS

8,576–8,782 (**2.3 %**) while `cavity.Q0.loaded` fell **43,611 → 83.7 (520×)**.
🔑 But the residual is not scatter: `Q_ext` falls **monotonically with the
shielding deviation** — 8,780 while the law holds, 8,576 at +45 %. **Geometric to
~0.5 % while the plasma is a perturbation; drifting ~2 % once it expels field**,
which is the coupling responding to a changed field distribution.
⚠️ `ret:qext-state-independent` retracted this claim as resting on ONE coupler
compared with itself. It is now supported for THIS loop across 520× of loading —
still one coupler. A different coupler must show it separately.

### ✅ 4. THE PROBES CORROBORATE, AND DISAGREE ABOUT WHERE

`bore_in` rises from 0.2396 to a **peak of 0.2625 at sigma 0.95, then FALLS back
to 0.2517**. `bore_mid` is flat to 0.5090 until sigma 0.63, then falls
monotonically to 0.4883. 🔑 **Two probes, two different transition points** —
`bore_mid` (inside the annulus) tracks the law; `bore_in` turns over at sigma
0.95. ⚠️ `bore_in` sits at the annulus INNER boundary with a VACUUM CORE inside
it, so it is not a decay-from-the-surface probe and its non-monotonicity should
not be read as one. **Do not average them.**

### ➡️ WHAT THIS LICENSES, AND WHAT IT DOES NOT

✅ `cavity.Q0.loaded` is now interpolable across four decades of sigma: below
0.083 by `1/Q0 = 1/43,611 + sigma/125.8` <!-- q:ok fitted law; every row is
design cavity / plain barrel loop 11x8 / loaded -->, above it from this table.
✅ Critical coupling for THIS loop sits at **sigma ≈ 0.0115 S/m**, deep in the
unshielded regime.
🔴 **It does NOT say where the discharge sits.** That is a plasma question, and
`ret:operating-point-79e18` still stands.

## ✅✅✅ POWER INTO THE ELECTRON CLOUD — THE DESIGN CURVE (2026-09-07)

**User:** *"what does this mean for coupling to the electron cloud"* — the
question the whole map was built for. Power reaching the electrons is
`(1 − |Γ|²) · eta_plasma`, and both factors come from the twelve measured states.
Plain barrel loop 11x8, **no series gap**, design cavity, sf 1.0.

| sigma | eps | `coupling.beta.loaded` | VSWR | into cavity | eta_plasma | **→ ELECTRONS** |
|---:|---:|---:|---:|---:|---:|---:|
| 0.0000 | +1.000 | 4.967 | 4.97 | — | 0.0 % | **0.0 %** — no absorber |
| 0.0028 | +0.997 | 2.520 | 2.52 | 81.4 % | 49.4 % | **40.2 %** |
| 0.0083 | +0.991 | 1.302 | 1.30 | 98.3 % | 74.1 % | **72.8 %** |
| **0.0204** | +0.977 | 0.613 | **1.63** | 94.3 % | 87.6 % | **82.6 %** ← PEAK |
| 0.0413 | +0.953 | 0.324 | 3.09 | 73.9 % | 93.5 % | **69.1 %** |
| 0.0826 | +0.907 | 0.168 | 5.95 | 49.3 % | 96.6 % | **47.6 %** |
| 0.2753 | +0.689 | 0.053 | 18.96 | 19.0 % | 98.9 % | **18.8 %** |
| 0.4200 | +0.460 | 0.035 | 28.19 | 13.2 % | 99.3 % | **13.1 %** |
| 0.6300 | +0.240 | 0.024 | 40.98 | 9.3 % | 99.5 % | **9.3 %** |
| 0.9500 | −0.220 | 0.017 | 58.11 | 6.7 % | 99.7 % | **6.6 %** |
| 1.4000 | −0.700 | 0.013 | 78.41 | 5.0 % | 99.7 % | **5.0 %** |
| 2.1746 | −1.456 | 0.010 | 102.5 | 3.8 % | 99.8 % | **3.8 %** |

### 🔑 1. A SHARP OPTIMUM — 82.6 % — AND THE PLAIN LOOP IS ALREADY ON IT

Two factors fight: **`eta_plasma` RISES** with sigma (49 → 99.8 %; at low
ionisation most dissipated power heats the COPPER, not the electrons) while
**the match COLLAPSES** (`cavity.Q0.loaded` falls straight through
`cavity.Q_ext.loaded`, so `coupling.beta.loaded` goes 2.52 → 0.010). They cross
at **sigma ≈ 0.02**. No series gap, no tuner, no redesign.

### 🔴 2. THE OPERATING POINT BEATS THE COUPLER BY 22×

    sigma 0.0204  ->  82.6 %      sigma 2.1746  ->  3.8 %

**Where you run, not what you build.** At the anchored density the cavity passes
99.8 % of what it dissipates to the electrons — and only 3.8 % of INCIDENT power
gets in, at **VSWR 102**.
⚠️ **So "we need 3.06× more coupling" was answering the wrong question.** That was
derived at sigma 2.17; buying it would match the design at the one place it should
not operate. **Withdrawn as a target.**

### 🔑 3. BEST MATCH ≠ BEST POWER TRANSFER

VSWR 1.30 at sigma 0.0083 delivers **72.8 %**; VSWR 1.63 at 0.0204 delivers
**82.6 %**. `eta_plasma` is still climbing (74 → 88 %), so it is worth ~0.3 of
VSWR to reach a state where more of the absorbed power lands on ELECTRONS rather
than walls. 🔴 **Minimising VSWR would cost ~10 points of delivered power.**

### ✅ 4. AND IT SIZES THE TUNER

Across sigma 0.008–0.04 — the useful band — the excursion is **VSWR 1.3 → 3.1**,
inside the user's working budget of 3. Cold start sits at **4.97**, just outside.
⚠️ If the discharge instead sits at the anchored density, VSWR is **102** and no
tuner of that class reaches it: that is the regime where a series gap is needed.
🔑 Compare the barrel + gap2 2.25 coupler COLD: `coupling.beta.cold` = 156, i.e.
**VSWR 156.** The series gap makes the cold mismatch dramatically WORSE — the
trade the retired minimax table was built around.

### 🔴 5. SHIELDING IS NEVER THE LIMIT

The peak sits at sigma ≈ 0.02, a factor of ~5 BELOW where `sigma·Q_plasma` first
bends. **Power delivery collapses from MISMATCH, long before the field stops
reaching the electrons.** ➡️ The electron-impact worry — *"can the field still
reach them?"* — is answered YES throughout the useful band.

⚠️ **TWO CAVEATS THAT TRAVEL WITH THIS TABLE.** (a) ONE coupler:
`cavity.Q_ext.loaded` = 8,735 is what places the peak, and a stronger coupler
moves it to HIGHER sigma. (b) The sigma axis maps to `plasma.n_e` only through the
collision rate, which is the unmade `NU_M` decision — **the SHAPE is robust, the
sigma→density labelling is not.** `ret:operating-point-79e18`

## ✅ THE OPTIMUM SURVIVES THE COLLISION-RATE QUESTION (2026-09-07)

**User:** *"a plasma_state of 5245K is the result of Nitrogen re-association,
which we have no control over. Conversely, the 1e11 figure would be accurate for
Nitrogen entering the torch. We're interested in the boundary in-between."*

🔑 **SO `NU_M` IS NOT ONE NUMBER TO DECIDE — IT IS A RANGE THE GAS TRAVERSES.**
`nu = n_heavy · sigma_cs · <v_e>` falls as the gas heats (n_heavy drops) and rises
with electron temperature. Across the boundary it spans **~1.6e12 → 6.3e10**, more
than an order of magnitude.

⚠️ **AND 1e11 IS NOT THE ENTERING VALUE.** Under LTE it corresponds to
**~2000 K** — mid-boundary. Entering gas at 300 K gives ~2.6e11, and with
field-heated electrons (T_e ≫ T_gas, which is the actual condition there) ~1.6e12.
**The rigs have been using a mid-transition figure all along**, which is defensible
but was never stated as such.

### 🔑 WHY THE (eps, sigma) AXIS WAS THE RIGHT CHOICE

The map assumes NO collision rate — it is parameterised on what Maxwell sees. So
the question "which nu?" can be asked OF the map instead of being baked into it.
Asking what state reaches the **82.6 % optimum (sigma = 0.0204)** at each stage:

| stage | T_gas | T_e | nu | `plasma.n_e` needed | eps |
|---|---:|---:|---:|---:|---:|
| entering, electrons at 1 eV | 300 | 11,604 | 1.64e12 | 1.19e18 | 0.9986 |
| warming, electrons at 1 eV | 1,500 | 11,604 | 3.27e11 | 2.38e17 | 0.9930 |
| warm, electrons at 0.5 eV | 3,000 | 5,802 | 1.16e11 | 8.53e16 | 0.9801 |
| developed, LTE | 5,245 | 5,245 | 6.30e10 | 4.83e16 | 0.9634 |

✅ **sigma = 0.02 IS REACHABLE AT EVERY STAGE** — it needs a different `plasma.n_e`
at each (1.2e18 → 4.8e16), and **eps stays in 0.963–0.999 throughout**, i.e. inside
the densely-sampled rows 2–6 of the map. **The optimum is not an artefact of one
assumed collision rate**, and it holds across a **26× spread in nu**.

### 🔴 WHICH DEMOTES THE `NU_M` DECISION

⚠️ I ranked deciding `NU_M` as the top next step on 2026-09-07, calling it a
blocker because *"every sigma→density statement is provisional."* **That framing
was wrong.** The coupler sees SIGMA; the optimum is at sigma ≈ 0.02; that holds
whichever nu applies. What nu changes is only **the ionisation fraction the plasma
side must achieve to land there** — an input to THEIR problem, not a gate on ours.
✅ The internal inconsistency in the rigs is still real and still worth fixing —
`drude()` takes `nu` explicitly. It is housekeeping, not a blocker.

### ➡️ AND IT MAKES THE BOUNDARY THE OPERATIVE PICTURE

At fixed `plasma.n_e`, **higher nu means LOWER sigma** — so the entering region
sits at the low-sigma end and sweeps RIGHTWARD as the gas heats. The plain loop's
useful band (sigma 0.008–0.04, VSWR 1.3–3.1) is therefore **a window the gas
passes THROUGH**, not a point it must be held at.
🔴 **Whether it DWELLS there long enough, and whether `plasma.n_e` reaches the
required 1e17–1e18 while it does, is KINETICS.** This map cannot answer it.

⚠️ **T_e = 1 eV / 0.5 eV ARE ILLUSTRATIVE, NOT DERIVED** — nothing in this
programme has measured an electron temperature. And nu inherits
`MOMENTUM_CROSS_SECTION_M2 = 1e-19 m²`, flagged ORDER ONLY. Treat the nu column as
a SCALE; the robust claim is that sigma = 0.02 is reachable throughout, which holds
across the whole 26× spread.

## 🔴 THE AZIMUTHAL ARM IS NOT MEASURED — A 44 % PEDESTAL THAT CANNOT BE PHYSICAL

**User, 2026-09-07:** *"Something feels off. A plain barrel loop happens to match
basically perfectly, while a different loop behaves completely different?"*
✅ **Correct.** `ret:azimuthal-driven-pedestal`

### THE EVIDENCE, IN THE ORDER IT NARROWS

| check | barrel | azimuthal |
|---|---|---|
| off-resonance baseline, **with plasma** | −0.00 dB | −2.51 dB |
| off-resonance baseline, **VACUUM (sigma = 0)** | **−0.00 dB** | **−2.40 dB** |
| implied broadband absorption | ~0 % | **~44 %** |

🔴 **A CLOSED VACUUM CAVITY OF COPPER AND ALUMINIUM CANNOT ABSORB 44 % OF INCIDENT
POWER AT EVERY FREQUENCY.** And it is not the conductor: the arc's surface
resistance is **~33 mOhm** against the **~7 Ohm** that −2.40 dB implies —
**0.46 %** of what is needed.

✅ **NOT THE CONFIGURATION EITHER.** The solved `Boundaries` are IDENTICAL to the
barrel's — attribute 91, `R = 50.0`, `Rs = 0.0`, same materials (90 → 3.5e7,
92 → 5.8e7), even the same `Direction` vector. ➡️ **So it is the MESH GEOMETRY —
the port face or the loop — and that is where to look.**

### WHAT THIS RETRACTS

`cavity.Q_ext.loaded` = 41,633 · `cavity.Q0.cold` = 18,206 · "4.7× weaker
coupling" · the **93.5 % `Q_ext` drift reported as F2 firing** · the predicted
69.6 % power delivery. **All rest on a loaded `Q_L` (azimuthal loop, standoff 2.0
/ arc 12.24) from a 3 dB walk across a pedestal**, and the identity
`Q_ext = Q_L(1+beta)/beta` <!-- q:ok identity, not a value --> inherits the error.
⚠️ **`coupling.beta` IS SOUND** — the circle fit on the complex locus agrees with
the rig to 0.15 % in BOTH arms (barrel 0.6143 vs 0.6134; azimuthal 0.2868 vs
0.2868). The defect is in the WIDTH, not the depth.

### 🔑 AND IT UNIFIES THREE FAILURES PREVIOUSLY TREATED AS SEPARATE

| run | symptom | previously called |
|---|---|---|
| `h3-azimload-01` | `cavity.Q0.cold` = 70,353, **above the bare cavity** | an identity failure |
| `h3-azimload-02` | **no resonance at all** at sigma 2.175 | a band/method limit |
| `h3-azimmap-01` | 44 % pedestal; 3 of 7 rows unfittable | F2 — "Q_ext is not geometric here" |

**Three anomalies, three explanations, one defect.** Each was diagnosed on its own
terms and none of them prompted a look at the arm they share.

### ✅ WHAT IS UNAFFECTED

**The barrel maps stand entirely** — baseline 0.00 dB, no pedestal,
`cavity.Q_ext.loaded` (design cavity, plain barrel loop 11x8) 8,735
± 1.2 % over 520×, `sigma·Q_plasma` = 125.8, the shielding transition, and the
82.6 % optimum. ⚠️ But the COUPLER-FAMILY COMPARISON is void in both directions:
there is no trustworthy azimuthal measurement to compare against.

### ➡️ HOW TO SETTLE IT

🔑 **An EIGEN solve with the port SHORTED sidesteps the port entirely**
(`h3_step3`'s method) and gives `cavity.Q0.cold` for the azimuthal loop
independently. If it returns ~18,000 the loop really is lossy and only the DRIVEN
extraction is broken; if it returns ~43,000 the loss is an artefact of the port
face. ⚠️ Cheap, and it discriminates the two candidates in one run.

## THE AZIMUTHAL PEDESTAL IS A DISCRETISATION ARTEFACT

*2026-09-06. `ret:azimuthal-driven-pedestal` asked which of two candidates —
the port face or the loop mesh — puts a 44 % broadband absorption under the
azimuthal |S11|. **It is neither the port nor the physics: it is the mesh, and
it has never been converged.** Established entirely from artefacts already on
disk. No solver time.*

### The configuration is identical, so it cannot be the configuration

The two runs' `*_resolved.json` — the exact config Palace consumed — agree
field for field except the mesh filename and the sweep band:

| | `h3-azimmap-01` (azim) | `h3-q0map-01` (barrel) |
|---|---|---|
| `LumpedPort` | R = 50, `Direction` [−0.5878, 0.8090, 0] | **identical** |
| `Conductivity` | attr 90 → 3.5e7, attr 92 → 5.8e7 | **identical** |
| `Materials` | vacuum / sapphire 9.39 @ 3.5e-5 / sectors | **identical** |
| `Solver` block | SuperLU, order 2, adaptive tol 1e-3, 40 samples | **identical** |
| MPI ranks | 32 | 32 |

Ranks are not recorded in any artefact; both were recovered from Palace's
per-rank `PeakMemoryGrowthMegabytes` (sum/max ∈ [30.1, 33.4]).
⚠️ **That is a gap worth closing** — rank count is a coordinate of every
observation and `ops/remote.sh` already warns when a baseline omits it.

🔑 The port `Direction` being byte-identical is not a coincidence and not a bug:
both gaps sit at φ = 36° with the conductor running tangentially there, so
(−sin 36°, cos 36°, 0) is correct for a radial loop's crossbar **and** for an
arc's midpoint.

### The error indicator separates the two arms cleanly

At essentially the same element count:

| run | tets | baseline \|S11\| | err norm | err max |
|---|---|---|---|---|
| `h3-q0map-01` barrel, vacuum | 346,118 | **−0.010 dB** | 0.074 | **5.85e-3** |
| `h3-azimmap-01` azim, vacuum | 349,530 | **−2.456 dB** | 0.457 | **1.29e-1** |

**22× the discretisation error for 1 % more elements.** Swept across all 40
runs with both files on disk the split is total: every run with baseline ≈ 0 dB
has `err max` ≤ 9.3e-2, and every run carrying a pedestal has `err max` between
1.29e-1 and 1.62e-1.

### The pedestal shrinks under refinement — physical loss would not

Two runs meshed the **same azimuthal geometry** (standoff 2.0 mm, arc 12.24 mm,
7 chords, groove 5×10, sapphire torch) and differ only in `size_factor`:

| run | size factor | tets | no-plasma baseline | absorbed | err max |
|---|---|---|---|---|---|
| `h3-azimne-01` | 1.5 | 124,622 | **−4.108 dB** | 61 % | 1.52e-1 |
| `h3-azimmap-01` | 1.0 | 349,530 | **−2.456 dB** | 43 % | 1.29e-1 |

🔴 **2.8× the elements removed 30 % of the absorption.** A real loss mechanism —
conductor, dielectric, radiation — is mesh-independent by construction. This one
is a function of `h`, which makes it discretisation error, not power.

### And it tracks the WALL GAP at fixed resolution

`h3-azimload-02` meshes the same loop at **standoff 3.0 mm** instead of 2.0,
at the same size factor and within 0.4 % of the same element count:

| run | standoff | size factor | tets | no-plasma baseline | absorbed |
|---|---|---|---|---|---|
| `h3-azimmap-01` | 2.0 mm | 1.0 | 349,530 | −2.456 dB | 43 % |
| `h3-azimload-02` | 3.0 mm | 1.0 | 351,049 | −3.717 dB | 58 % |
| `h3-azimne-01` | 2.0 mm | 1.5 | 124,622 | −4.108 dB | 61 % |

🔑 **Moving the conductor FURTHER from the wall makes it worse**, with the
element count held. So the under-resolved thing scales with the conductor's
near-field volume — and the ARC REFINEMENT field is 0.25 mm elements inside a
ball of radius **2.0 mm** (= 2·`loop_rw`) with 2.0 mm of grading, which at a 2–3
mm standoff does not reach the wall at all.

🔴 **AND IT IS FALSIFIED.** `h3-azimwall-01` widened the reach to
`max(2·rc, _hh + 0.5 mm)` = 3.5 mm. It took effect — the run's own refinement
report (new instrumentation, first use) reads *"ARC refinement: 0.500 mm within
3.5 mm of 11 points along the conductor"*, and the mesh grew 349,530 → **366,681
tets**. The pedestal did not move:

| | tets | arc reach | baseline | err max |
|---|---|---|---|---|
| `h3-azimmap-01` | 349,530 | 2.0 mm | −2.456 dB | 1.29e-1 |
| `h3-azimchord-01` (no-op) | 349,530 | 2.0 mm | −2.456 dB | 1.29e-1 |
| `h3-azimwall-01` | 366,681 | **3.5 mm** | **−2.467 dB** | 1.28e-1 |

⚠️ **This does not revive the standoff correlation, and it does not refute
global refinement** — 124,622 → 349,530 tets moved the baseline 1.65 dB, while
this step is only +4.9 % elements (≈1.6 % in `h`). It refutes the specific claim
that *the unrefined conductor-to-wall gap* is the sink.

### ➡️ Stop proposing sinks; measure the sink

Two mechanisms have now been proposed and killed — arc faceting (which did not
exist) and the wall gap (which did not matter) — and **neither needed to be
guessed at, because the sink is directly measurable.** Palace's
`Boundaries.Postprocessing.SurfaceFlux` with `Type: "Power"` integrates the
Poynting flux through a named boundary. Nothing in this programme has ever used
it.

`h3-azimpower-01` (running) and `h3-barrelpower-01` put a Power flux on the
**wall**, the **port** and the **loop conductor** separately, attributes bound
from the mesh sidecar. The arithmetic decides it outright:

- **wall + port + loop ≈ 43 % of incident** → the loss is real *in the model*,
  and whichever surface carries it names the next question.
- **they sum to ≈ 0** → nothing is absorbing, and the pedestal is an **|S11|
  normalisation defect** — which would void the azimuthal corpus for a different
  reason and put every driven |S11| in the programme in scope.

🔑 The barrel run is not optional: it is the calibration. Its surfaces must sum
to ≈ 0 absorbed, or the azimuthal number cannot be read at all.

### An azimuthal loop is not intrinsically broken

`e0k2-azim-00` runs an azimuthal loop in the **E0 instrument cavity** (bare
cylinder, no groove, no torch) at 35,738 tets and reads **−0.011 dB**, err max
7.24e-2 — a textbook lossless one-port. So the defect is not "azimuthal loops
mesh badly"; it is this loop **inside the design cavity**, and 10× the element
budget makes it worse rather than better.

⚠️ **This is the part I cannot yet localise.** No Paraview output survives, so
the per-element indicator cannot be mapped. The one clue is domain energy: off
resonance the sector holding the loop carries **32.4 %** of `E_elec` against
16.6 % in each of the other four (a 1.95× concentration), where the barrel's
same sector carries 22.4 % against 19.1 % (1.17×).

### Ruled out, so that nobody re-tests them

- **The port face.** Configuration identical; `port_pw` never enters it.
- **A dead refinement branch.** The ARC field *does* fire: `p["loop_azim"]` is
  assigned at `geometry.py:455` and read at `geometry.py:1778`, both inside
  `build()`, in that order — 0.25 mm elements within 2.0 mm of ~13 ball centres
  along the conductor. ⚠️ It looked dead because `h3_driven.build_mesh` passes
  `capture_output=True` and discards the mesher's stdout on success, so
  geometry.py's refinement report has never been read for any azimuthal run.
- **The eigen sidestep this ledger recommended.** Tried: `h3-eigencheck-02`
  stalled — bit-identical NLEPS residual 3.547620e-08 across 80 iterations,
  Armijo backtracks = 9 every iteration, each restart freezing at 1.357e-01.
  🔑 **A badly conditioned operator is the same symptom in a different solver**,
  which is corroboration rather than a separate problem.

### ➡️ Step 1 tested nothing, and finding out why was worth more than the run

`h3-azimchord-01` set `arc_chords` 7 → 11, vacuum, everything else
`h3-azimmap-01` verbatim. It came back **bit-identical** — 349,530 tets, −2.456
dB baseline, err max 1.29e-1, every digit the same.

🔴 **`arc_chords` NEVER HAD A CONSUMER.** It was read from `AMIP_ARC_CHORDS`,
stored in `P`, written into every mesh sidecar and every azimuthal run record,
and *retried over* by both rigs — and no geometry code ever used it. The arc is
an **OCC torus** (`occ.revolve`, `geometry.py:498`). The polyline-chord
construction the flag is named for was built in August and **abandoned**: Palace
refused the mesh outright (`MFEM abort: STable3D::operator()`).

So the faceting hypothesis this run was built on had no referent — **there are no
facets** — and I should have read the construction before writing the run. Worse
than a wasted solve, though, is what it exposes: every azimuthal artefact in the
programme carries `arc_chords: 7`, **a geometry coordinate that was never true**,
and both rigs' "retry over the chord count, and RECORD what worked" loops
re-meshed identical geometry and reported whichever value they happened to try
first. `h3_loopq`'s measured table of which counts mesh is measuring nothing.

✅ Removed 2026-09-06: `geometry.py` now **refuses** `AMIP_ARC_CHORDS` rather
than ignoring it, and the retry loops are gone from both `h3_driven` and
`h3_loopq`. ⚠️ **Recorded `arc_chords` values in existing artefacts are noise.
Do not read them as geometry** (`ret:azimuthal-arc-chords`). They do *not*
invalidate the meshes — every one is the torus construction — only the
coordinate claimed for them.

🔴 **Until this closes, the standing retraction holds**: the azimuthal arm has
no trustworthy driven measurement, and the coupler-family comparison is void in
both directions.

### 🔴 THE MESHER CHANGED — azimuthal meshes are not comparable across 2026-09-06

`geometry.py`'s arc refinement balls sat on the conductor **centreline** with
radius `2.0 * loop_rw` = 2.0 mm, while the wall is `_hh` = standoff + t/2 away —
**3.0 mm at standoff 2, 4.0 mm at standoff 3**. The refinement therefore stopped
1.0 / 2.0 mm short of the wall, leaving cavity-scale elements in the gap where
an azimuthal loop's field is strongest. Reach is now `max(2*rc, _hh + 0.5 mm)`
and is pinnable as `arc_ball_mm` (`AMIP_ARC_BALL_MM`) and recorded in the mesh
sidecar.

⚠️ **Every azimuthal mesh built before this is a different mesh from every one
built after.** The mesh cache keys on the geometry parameters, so old entries
are still reachable and still valid *as the thing they were* — they are just not
the same instrument. Compare across the boundary only with `arc_ball_mm` in hand.

⚠️ **Two other instrument gaps found on the way, both now closed in code but not
yet exercised by any run:** `h3_driven` discarded the mesher's stdout on success,
so no artefact could say how a mesh had been refined — it now keeps the
refinement report in the record; and `arc_chords` had only a retry-fallback list,
so the arc resolution was an *outcome* of a run rather than an input, which is
fatal for exactly this kind of series. It is now pinnable, like `size_factor`.

⚠️ **Still open: MPI rank count is in no artefact.** Both maps compared above ran
at 32 ranks, recovered from Palace's per-rank memory rather than from anything
the programme recorded. `ops/remote.sh` already warns when a baseline omits
`parameters.ranks`; nothing yet acts on the warning.

## ✅ THE POWER BALANCE CLOSES ON THE BARREL AND FAILS ON THE AZIMUTHAL

*2026-09-07. `h3-barrelpower-01` / `h3-azimpower-01`, vacuum, 64 ranks. The
first surface power measurement in this programme.*

`Boundaries.Postprocessing.SurfaceFlux` with `Type: "Power"` on the **wall**,
the **port** and the **loop conductor** separately, attributes bound from the
mesh sidecar. Closure = (surface power) / (power the port says was absorbed).

| arm | point | \|S11\| | absorbed | wall | port | loop | **closure** |
|---|---|---|---|---|---|---|---|
| barrel | off-resonance | −0.004 dB | 0.00089 W | 7.08e-4 | −3.8e-6 | 9.3e-5 | **89.1 %** |
| barrel | ON RESONANCE | −3.546 dB | 0.55800 W | 5.47e-1 | −2.4e-4 | −5.0e-3 | **97.0 %** |
| azim | off-resonance | −2.500 dB | 0.43769 W | 3.67e-4 | 1.31e-3 | −9.9e-5 | **0.4 %** |
| azim | ON RESONANCE | −8.160 dB | 0.84723 W | 1.94e-1 | 1.88e-3 | −5.5e-4 | **23.0 %** |

⚠️ The barrel's high-frequency edge is omitted: absorbed fraction 0.0004 there,
so the ratio is noise over noise and supports nothing either way.

### ✅ The instrument is calibrated

**The barrel closes to 97 % on resonance.** Every watt the port says is absorbed
is found on a surface. F2 did not fire, so the azimuthal number can be read.

### ✅ AND IT SETTLES THE DRIVE NORMALISATION — P_inc = 1 W

Long open, and blocking every absolute field quote: the port reports
`V_inc` = 7.0711 V = √50 and it was unclear whether that meant 0.5 W or 1 W
(an energy-balance estimate had suggested ~0.31 W). The barrel's closure **is**
the measurement: its on-resonance surfaces imply `P_inc` = **0.970 W**, 3 % from
1 W, and 0.5 W would put the closure at 194 %. So `P_inc` = 1 W — Palace's
`V_inc` = √(P·R) convention, i.e. `P = |V|²/R`, not `|V|²/2R`.

### 🔴 The azimuthal arm fails the balance ON RESONANCE TOO

This is **wider than the pedestal**. Off resonance the port claims 0.438 W and
the model dissipates 0.4 % of it — 275× short. But **on resonance only 23 %** of
the claimed absorption exists either. So it is not merely that the baseline sits
too low: the **dip is wrong as well**, and every quantity read off it —
`Q_L`, `coupling.beta`, and every `Q_ext`/`Q0` derived from them — inherits it.
⚠️ `ret:azimuthal-driven-pedestal` framed this as "`Q_L` comes from a 3 dB walk
on a pedestal". That was too narrow. The dip depth is independently wrong.

### ➡️ The port face, which I wrongly ruled out

`geometry.py` names the cause 30 lines above the arc construction:

> *the gap faces are planes at ±psi, so the port face spanning them is an
> annular **SECTOR**, and Palace's lumped port requires a **FLAT** element
> ("bounding box discovered length should match projected length"). pec solves;
> lumped does not. Q_ext therefore needs the port face fixed — **that is the
> open problem**, on a mesh that is otherwise known good.*

The barrel's gap is a planar slot in a straight crossbar; the azimuthal one is a
curved sector. A lumped port on a non-flat face integrates the wrong voltage and
current, so `|S11|` is wrong **with no power imbalance to notice** — nothing is
flowing anywhere, which is exactly what the closure column shows.

🔴 **I RULED THE PORT FACE OUT ON BAD REASONING, AND WROTE "DO NOT RE-TEST"
INTO THIS LEDGER AND INTO THE REGISTRY.** I compared the `LumpedPort`
*configuration* — identical `R`, identical `Direction` — and concluded the port
could not be involved. But the defect is in the **mesh face the port is attached
to**, which no amount of config diffing can show. That entry would have steered
the next reader away from the cause. It is withdrawn.

⚠️ **And the discretisation story above is demoted to correlation.** The error
indicator really is 22× the barrel's, and the pedestal really did fall from
−4.108 to −2.456 dB under refinement — but refinement was changing *how wrong
the port-face integration is*, not how much power is lost, because **no power is
lost**. Mesh dependence is a symptom here, not the mechanism.

## ✅ THE WALL GAP CAUSES THE PEDESTAL — h = 10.5 REMOVES IT

*2026-09-07, `h3-azimh-drv-01`. User: "The intent here is to investigate if the
short gap is the cause rather than something about the loop itself." It is.*

One variable against `h3-azimpower-01`: standoff 2.0 → 10.5 mm. `arc_ball_mm`
pinned at 2.0 so the mesh around the conductor is identical; 354,424 tets against
349,530, size factor 1 in both.

| | off-res \|S11\| | err norm | err max | closure off-res | closure on-res |
|---|---|---|---|---|---|
| barrel | −0.004 dB | 0.0436 | 3.19e-3 | 89.1 % | 97.0 % |
| azim **h = 2.0** | **−2.500 dB** | 0.4564 | 1.28e-1 | 0.4 % | 23.0 % |
| azim **h = 10.5** | **−0.005 dB** | 0.0524 | 1.14e-2 | 67 % | 7.9 % |

🔑 **The pedestal is gone.** −2.500 dB → −0.005 dB, indistinguishable from the
barrel's −0.004. And the discretisation error went with it: `err max` fell 11×,
to within 3.6× of the barrel. Both defects were the near-wall placement.

⚠️ **This narrows `ret:azimuthal-driven-pedestal`, it does not lift it.** The
defect is a property of the loop AT h ≤ 3, not of the azimuthal topology. Every
existing azimuthal driven number was taken at h = 2.0 or 3.0 and stays void.

### ✅ THE FIRST TRUSTWORTHY AZIMUTHAL CAVITY Q₀

`Q0 = ω·W/P_loss` — stored energy over dissipated power, using **no |S11|, no
port normalisation and no fit**, so none of the suspect machinery touches it:

| arm | f₀ | W (J) | P_wall+loop | **Q₀(energy)** |
|---|---|---|---|---|
| barrel | 2.43985 | 1.5884e-6 | 0.55154 W | **44,149** |
| azim h = 10.5 | 2.44040 | 2.0044e-7 | 0.07000 W | **43,907** |

Both land on the eigen-confirmed ~43,000 (`h3-eigencheck-01`: 43,470). **The
cavity at h = 10.5 is normal**, and this is the first azimuthal cavity Q₀ in the
programme that does not descend from a broken port.

### 🔴 STILL UNRESOLVED — the resonant peak

The on-resonance closure is **7.9 %**, worse than h = 2.0's 23 %, and the width
does not fit the Q₀ above. `Q_L` measured two independent ways agrees —
**2,302** from the wall-power half-maximum, 2,281 from the rig's |S11| fit
(barrel: 7,176 and 7,323, agreeing to 2 %) — so the broad resonance is real as
measured. But `Q0 = Q_L(1+beta)` with `Q_L` = 2,302 and Q₀ = 43,907 needs
β = 18.1, while the dip depth −9.405 dB admits only β = 0.494 or its reciprocal
2.024. Those cannot all be true.

🔑 **Q₀(energy) is a RATIO and survives a common scale error; the closure is an
ABSOLUTE and does not.** That they disagree this way says the peak is
mis-scaled, not that the physics is wrong. ⚠️ The adaptive PROM converged on 6
samples with a final greedy error of 1.002e-05 against a 1e-3 tolerance, so it
claims the peak is resolved — which argues against simple under-sampling and
means the cause is NOT yet identified. Do not assume it is the PROM.

⚠️ **So coupling is still not measurable on the azimuthal arm.** `beta` and
`Q_ext` need the resonant peak, and the peak is the part that does not add up.
