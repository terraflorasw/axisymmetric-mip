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

These are recorded so they are not lost. **They do not spawn runs.**

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
