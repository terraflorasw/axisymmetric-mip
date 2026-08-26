# PLAN — the fixed experiment list

**It does not grow.** Five experiments, each with a verification and a
falsification declared here before any driver is written.

Ordering is by LOD dependency, not by curiosity.

---

## E0 — how far is this solver from mathematics?

**Not "verify the instrument."** Put a number on the disagreement between this
solver and the closed form, on the one case where the closed form is complete.

| | |
|---|---|
| **geometry** | EMPTY right circular cylinder, a = 103.70, L = 88.53 mm. Nothing else in it |
| **V** | `physics.spectrum()` — 9 modes below 3 GHz, exact for PEC walls |
| **F** | **TE₀₁₁/TM₁₁₁ splitting has a true value of EXACTLY ZERO** (χ′₀₁ = χ₁₁). Any splitting is pure artifact. Second falsifier: a bookkeeping-only change — retag a region, renumber an index — must not move a frequency |
| **gate** | the mesh must contain ONLY {bore, air, wall}. Asserted by completeness, not by a list of features to exclude — three attempts failed on exactly that |
| **outputs** | disagreement per mode; the degeneracy splitting; driven-vs-eigenmode on identical physics (this also settles the old R37) |

⚠️ E0 does not license anything. It bounds how much a later disagreement can be
attributed to the solver rather than to the model.

---

## ✅ E0 CLOSED — the standing recipe

**geometric order 2 · solver order 2 · size factor 2.0–2.5** (~8–13k elements,
10–16 min) gives TE₀₁₁ to ~0.2 MHz and **all modes within ~1.8 MHz**, against a
2.34 MHz cold linewidth. Use sf 0.96 (50 min) only when sub-0.4 MHz is needed.

🔴 **Never solver order 1.** It is 12–17 MHz wrong and no constant corrects it —
the error is mode-dependent by 40×.
🔴 **Judge a mesh by `max|Δ|` across the spectrum, not by TE₀₁₁.** At sf 3.0
TE₀₁₁ is right to 0.26 MHz while the spectrum is 10.6 MHz wrong.

---

## E1 — cavity dimensions a, L
**Door: delivered power.** The cavity must resonate at 2.45 GHz to be driven.

| | |
|---|---|
| **V** | empty-cylinder closed form; then the LOADED shift against first-order perturbation — the sign and rough size must follow from where the field is |
| **F** | **dTM₀₂₀/dL = 0 identically** (p = 0, no z-variation). Measure it across the length ladder: its drift IS the in-situ σ, and it is free |
| **watch** | the ±0.2 mm radius callout was justified by TM₀₂₀ headroom, which no longer binds. Re-derive what does |

---

## E2 — the mode landscape, and what the filter buys
**Door: delivered power** (rivals steal it) **and noise** (mode instability).

| | |
|---|---|
| **V** | the degeneracy is exact and immovable by aspect ratio. An avoided-crossing model predicts that hybrid character averages to the parents' mean |
| **F** | remove the filter (ε → 1.0, same mesh, exact) — the modes MUST hybridise and bore-E must converge to the mean. If they do not, the filter's justification is wrong |
| **method** | same-mesh throughout: ε is a material, so no geometry changes |

---

## E3 — coupling and delivered power η
**Door: delivered power → the sensitivity term of LOD.** The load-bearing one.

| | |
|---|---|
| **V** | circuit theory: η = 4β/(1+β)², β = Q₀/Q_ext. And **energy balance must close**: η_total = η_plasma + η_wall + η_dielectric |
| **F** | **the closure itself.** If the split does not sum to η_total within a few percent, the decomposition is wrong and only η_total may be quoted. This caught a factor-of-2 convention error once already |
| **method** | σ_plasma swept same-mesh; wall metal is a boundary property, also same-mesh |

---

## E4 — the optical path
**Door: background and collection.**

| | |
|---|---|
| **V** | circular-guide cutoff and evanescent attenuation, closed form; étendue for the trap |
| **F** | the measured Q cost of an aperture against the d³ Bethe scaling — two independent routes to the same number |
| 🔴 **blocked** | aperture diameters are set by the spectrometer f-number, which is external and unknown |

---

## ✅ E1 status

| | |
|---|---|
| **E1a** ✅ | design point is ANALYTIC — one-parameter family at 2.45 GHz; the filter is a theorem; TM₀₂₀ is radius-only; no in-band rivals when empty |
| **E1b** ⏸ | loaded perturbation — meshes at sf 2.0 (19k el), NOT 2.5. Ready to re-run with the fixed harness |
| **E1c** ✅ | **graded meshing is NOT worthwhile** — air ×3 removes 22% of elements, uniform sf 2.0 removes 79%. Answered by counting; `--air-coarsen` to be removed |

⚠️ **The size-factor floor is set by the THINNEST FEATURE, not the wavelength.**
E0j's recipe held on an empty cavity because it had no second scale. Loaded, sf
2.5 self-intersects on 1.0–1.5 mm tube walls; 2.0, 1.5 and 1.0 mesh, 1.2 does not
— constructibility is non-monotonic in two independent geometries now.

---

## Parked — surprises, NOT register items

### 🔎 WHAT DOES THE SERIES GAP ACTUALLY DO? (parked 2026-08-26)

**User: *"if 8mm is a meaningful capacitive gap, then the groove width probably
also is"*** — and that reframing is right. The groove width (5 mm), the groove
depth (10 mm) and the loop series gap (2.25 mm measured, ~8 mm extrapolated)
are **the same class of feature at the same scale**: conductor gaps of
λ/15 … λ/24, big enough to hold a real voltage, too small to radiate. Calling
one "a capacitive gap" and the other "a slot dimension" was inconsistent.

✅ **What that clarifies about the GROOVE.** TE011's wall current is AZIMUTHAL
(K = n × H = −φ̂·H_z), and the groove is an ANNULAR ring — it runs *parallel*
to that current and does not cut it. That is why TE011 survives while TM111,
whose currents cross it, is pushed down. 🔑 **So the groove width IS
capacitively meaningful — for the modes being REJECTED, not the one being
kept.** That is a better description of the mode filter than "a groove that
shifts TM111 down".

🔴 **AND THE LOOP GAP IS NOT UNDERSTOOD.** A series-LC picture says widening
the gap lowers C, raises X_C away from cancellation, and should WEAKEN
coupling. Measured, Q_ext falls monotonically 1,143 → 322 all the way to
2.25 mm. The LC fit was **retracted** after failing its own control at 44 %
residual (KNOWN.md § STEP 2).

**Untested hypothesis:** as the gap widens the loop stops being a current loop
and becomes partly a **capacitive probe**, coupling to E_φ instead of linking
H_z. E_φ at the gap radius (r ≈ 83.5 mm) is **13.9 % of peak** — small but not
zero, and the gap voltage is large. Would explain both why widening keeps
helping AND why purity degrades (an electric probe couples to a different mode
set).

⚠️ **PARKED, NOT QUEUED. User: *"It's a curiosity, but probably not something
we can resolve without a lot of sweeps."*** Correct — and a cold eigen solve on
the design cavity is now ~7 min at best, so a mechanism study is expensive.

### ✅ QUEUED AS `h3-groove-gap-01` — and the BAR IS CLASSIFICATION, not mechanism

**User, 2026-08-26: *"At the very least, we should be able to classify it as
'curious' or 'coincidence'."*** 🔑 **That is a better framing than mine.** "What
is the mechanism" is expensive and open-ended; "is there anything here at all"
is decidable in 8 solves.

**The measurement:** groove width 5 mm (frozen design, within-run control) and
8 mm, each at series gaps 0.75 and 2.25 mm. Compare the RATIO
`Q_ext(0.75)/Q_ext(2.25)` between groove widths — a shift in the ratio means
the curve moved, not merely scaled.

#### ✅ ANSWERED 2026-08-26 — 🔑 CURIOUS (marginal). See KNOWN.md § GROOVE × LOOP-GAP

**Ratio moved −6.43 %** against a 6 % threshold — curious by the pre-fixed rule,
**by 0.43 points**, corroborated independently by Q₀ (+0.40 % at gap 0.75 vs
+6.92 % at gap 2.25).
🔴 **THE MECHANISM BELOW IS INCOMPLETE.** The annular-current argument explains
why the groove barely moves TE011's **f₀** (−0.043 MHz measured) and does NOT
explain the **coupling**, which does interact with the gap.
🔑 **Consequence (user):** groove and loop gap are **potentially not independent
optimisation parameters — we need dependent priors.** Not a re-design; a
constraint on how any future joint sweep is modelled.

#### ⏸️ ~~STATE: 3 OF 4 CASES DONE — the test reduces to ONE NUMBER (2026-08-26)~~

**MEASURED so far, design cavity, barrel mount, 176 mm² loop:**

| groove w | gap 0.75 | gap 2.25 | ratio |
|---|---:|---:|---:|
| **5 mm** (frozen design) | **681** | **308** | **2.211** |
| **8 mm** | **702** | 🔴 **MISSING** | — |

🔑 **The whole verdict is one solve pair away.** With `gw8`/0.75 = 702 measured,
the outstanding `gw8`/2.25 value decides it outright:

| Q_ext(gw8, 2.25) | verdict |
|---|---|
| **305 – 331** | ⚪ **COINCIDENCE** — the groove SCALES coupling but does not move the optimum |
| < 300 or > 338 | 🔑 **CURIOUS** — the curve shifts; groove width and loop gap are coupled |

⚠️ **317 is exact uniform scaling** — dead centre of the coincidence band, and
what the annular-current prediction implies.

✅ **A REAL BY-PRODUCT ALREADY, whatever the ratio does:** groove width 5 → 8 mm
changes Q_ext by **+3.1 %** at gap 0.75 (681 → 702), which is above the ~1 %
discretisation floor. **The groove is a weak coupling knob** — small, but not
nothing, and not something the record previously claimed either way.

🔴 **BLOCKED ONLY BY COMPUTE.** Eleven spot reclamations on 2026-08-26 (two
confirmed by `/opt/amip/spot-interruptions.log`, which now records them). The
run resumes with `ops/go ops/remote.sh h3_loopq.py 32 h3-groove-gap-01` and
skips the three completed cases — **~25 minutes to finish.**

#### 🔑 THE DECISION RULE, FIXED BEFORE THE DATA EXISTS

Derived from the one measurement of the discretisation floor we have: gap
0.35 → 0.50 mm gave **0.8 %** on meshes differing by 122 tets, and **I read
that 0.8 % as a direction and was wrong.** Taking ~1 % per single Q_ext,
√2 for a ratio, √2 again for comparing two ratios → ~2 %.

| |Δ ratio| | verdict |
|---|---|
| **< 4 %** | ⚪ **COINCIDENCE** — no interaction above the floor. The mechanism story survives, WEAKLY |
| **4 – 6 %** | ⚠️ **UNRESOLVED** — do not call it either way; needs a finer mesh, not more cases |
| **> 6 %** | 🔑 **CURIOUS** — real interaction. Groove width is a coupling knob, and H2 / item 7 become COUPLED design problems |

🔑 **THREE outcomes, not two.** "Unresolved" is a real possibility and
collapsing it into either label is exactly how a 0.8 % step became a direction.
⚠️ **The verdict lives HERE, not in the rig** — the driver emits Q_ext with
provenance; the label is applied in a re-runnable layer, because the label is
the part that keeps being wrong.
⚠️ **Asymmetric evidence:** a POSITIVE result is informative. A NULL is weaker —
consistent with the annular-groove mechanism, but also with Q_ext simply being
insensitive to groove width for unrelated reasons.

✅ **THE CHEAP VERSION, IF IT IS EVER WANTED:** it needs NO new solves. Every
gap-sweep case already wrote per-region energy fractions (`domain-E.csv`) and
`A2/A0`. A loop turning into an electric probe should show a rising energy
fraction near the gap and a changing mode-content signature across the sweep
that is already on disk.


These are recorded so they are not lost. **They do not spawn runs.**

- 🔑 **SALINE AS AN IGNITION BASELINE (user, 2026-08-23).** ⚠️ **Not a proposed device — a REFERENCE.** No beads, no inserted objects. Plain saline is the simplest thing that could work, so it is what every more viable igniter must be measured against. It probably fails on its own; the value is knowing by how much. Khattak, Bianucci
  & Slepkov, **PNAS 116(10) 4000–4005 (2019)**, in `refs/`. Mie resonances in
  water spheres (ε̃ = 79 + i10 at 2.45 GHz) interact cooperatively to make a
  contact hotspot — **≈19× the vacuum field**, superfocusing to λ₀/100 — which
  field-ionises Na/K and cascades in the air.
  🔑 **Their Fig 1C is the saline case already done**: skinless >99%-water
  hydrogel beads form plasma after a brief NaCl immersion.
  🔑 **Absorption is ESSENTIAL, not a penalty** — it washes out sharp modes and
  leaves the hotspot, which also makes the effect size-TOLERANT (without it,
  9.5 mm works and 10 mm does not). A saline slug would stack three mechanisms: dielectric resonance
  (field concentration), lossy heating (the thermal kernel H4 says is required),
  and Na seeding (5.14 eV against N₂'s 15.6). **And the sample is already a
  solution** — no electrode, no erosion.
  ⚠️ Against it: TE011's field is ZERO on axis, which is exactly where the sample
  travels; a resonant sphere (~14 mm) barely fits a 17 mm bore; an aerosol is far
  too small to resonate. ⚠️ The "contamination" objection is WITHDRAWN as facile:
  the plasma is flushed at 15–20 slm, ignition and measurement are separated in
  time, and Na is already a major constituent of the high-TDS extracts being
  measured. What remains is **settling time and memory effects** — quantifiable,
  not disqualifying. Full treatment in HYPOTHESES H4 Route 3.
  **Deferred, not queued.**

- A sapphire mode filter costs 9–11% of Q, smooth and reproducible, but the
  mechanism is unestablished: dielectric is only ~2% of the loss budget, so it
  must be wall-loss redistribution. The filter has no Energy index anywhere, so
  its stored-energy fraction has never been measured.
- Eigenmode and driven disagreed 3.7× on ε sensitivity in the old programme,
  never diagnosed. **E0 tests whether the two paths differ at all.**
- Deliberately lossy walls nearly double cold coupling (η 11.6% → 20.4% at
  σ = 1e7) for ~1% of lit power. Never evaluated as a design option.
- 🔴 **The old record's below-cutoff attenuation is wrong by 1.70×.**
  `physics.evanescent_db_per_mm(2.45, 10.0)` = **3.167 dB/mm**, i.e. 63.3 dB
  over 20 mm, against a recorded 5.4 dB/mm and ~108 dB. The conclusion
  (apertures are RF-safe) survives — 63 dB is ample — but the number did not.
  **Found by physics alone, before any solve. First finding of this programme.**
