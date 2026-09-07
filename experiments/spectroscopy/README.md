# spectroscopy — what the plasma has to DO, and what that requires of it

**Opened 2026-08-24.** `experiments/resonance/` builds a cavity that sustains a
plasma. `experiments/control-loop/` drives it. **This programme is the reason
either exists**: the analytical measurement the plasma is for.

✅ **ONE THING IS NOW ANCHORED: the gas temperature** (and therefore n_e) — see
below. **Everything else here is still a question**, and several of the entries
the other programmes build on are inherited rather than chosen.

---

## Why it was opened: resonance WAS blocked on one number

**`n_e` had no physical provenance.** Its origin was *solver convergence* — a
value chosen because an eigensolver converged there, laundered into "the
operating point" over six citations (`../resonance/CONVENTIONS.md` §7ab). It is
also **the dominant variable** in the cavity design: it moves the band margin
~25× more than any geometry knob, and it sets the impedance the matching network
must transform.
✅ **ANCHORED 2026-08-24 — the question below is ANSWERED.** The table that
follows is retained because it is how the answer converts.

✅ **IT DID NOT HAVE TO BE ANSWERED AS A DENSITY.** Under LTE the Saha
equation makes n_e a **thermometer**:

| n_e | **T_gas** | band margin | η | VSWR the tuner must reach |
|---:|---:|---:|---:|---:|
| 1e18 | **4,654 K** | 48.0 MHz | 0.9864 | 15.6 |
| 3e18 | 4,950 K | 46.6 | 0.9951 | 43.3 |
| 1e19 | 5,320 K | 39.2 | **0.9979** | **99.3** |
| 3e19 | 5,709 K | 26.0 | 0.9978 | 96.2 |
| 1e20 | **6,207 K** | 17.6 | 0.9964 | 58.4 |

## 🔑 THE QUESTION THIS PROGRAMME OWES THE OTHERS

> **What gas temperature does the analysis require?**

✅ **ANSWERED 2026-08-24 — anchored to MICAP** (user's choice of comparator).
**N₂ MICAP gas temperature = 5220 K / 5270 K**, pressure-reduction method,
Kuonen, Hattendorf & Günther, *JAAS* **39**(5) 1388–1397 (2024), Table 2.
→ **n_e = 7.3–8.6 × 10¹⁸** via LTE Saha. The programme's assumed 1e20 was
**13× too high**.
🔑 **Why that method:** of Table 2's three, **only pressure reduction is
empirical** — it measures an interface-pressure ratio with plasma on and off.
Longerich (12,850/13,800 K) and Houk & Praphairaksit (5,910–6,430 K) both infer
T from the SAME MO⁺/M⁺ ion-ratio data through different equilibrium models and
disagree by ~2×. That is model spread, not measurement spread, and the paper
notes Longerich "has always resulted in values between 9000 K and 13000 K".
✅ Cross-check: the same method reads 5,680–5,780 K on their Ar ICP against
independent literature values of 5,000–5,280 K.
⚠️ **It is the plasma AS SAMPLED THROUGH THE MS INTERFACE** — the analytical
zone at the cone, not the r = 2–8.5 mm annulus the EM model uses. Different
region, and atmospheric plasmas have gradients. **This is the caveat to attack
if the number is ever doubted.**
✅ Power does not enter (more power = bigger plasma, not hotter), and MS-vs-OES
does not either — same plasma, different detector.
⚠️ **SCOPE, added 2026-09-07: that is true of THIS question — the required gas
temperature — and NOT of the gas plant.** Nitrogen-generator supply pressure
tiers split on exactly the MS boundary (user: ~4.1–5 bar standard, **7 bar** for
MS or dual-gas), so the detector choice is load-bearing for the compressor and
generator even though it is irrelevant here. **Do not carry this line out of its
section.** See `../torch-geometry/README.md` § ITEM 4.

### 🔑 The consequence split in two directions
**Band margin 17.6 → 41.4 MHz** (good). **VSWR 58 → 75–82** (bad, but MEASURED
2026-08-25 and milder than the interpolated 80–89) — Q₀ minimises
near 1e19 and the anchored density sits just below it, so the match landed
*near* the worst case rather than away from it.

**Saha converts a temperature to n_e, and everything downstream follows** — which
is why reframing the question from "what density?" to "what temperature?" is what
made it answerable at all.

✅ **MEASURED 2026-08-25 — AND THE SENSITIVITY WORRY BELOW IS RETIRED.** All
three densities in the MICAP band were solved (`../resonance/` item 8):
**7.3 / 7.9 / 8.6e18 → Q₀ 108 / 104 / 99, f₀ 2.4578 / 2.4586 / 2.4594.**
🔑 **The full 50 K spread moves f₀ by 1.6 MHz and VSWR by ~9 %.** The mapping is
steep *in general* but **this anchor's own uncertainty is not a design problem**,
and a tighter temperature would not buy anything.

⚠️ **Sensitivity, so a loose answer is used correctly:** n_e moves **two decades
per ~1,500 K**. "About 6,000 K" is not a tight n_e — but it brackets, which an
unanchored density never did. A 500 K error is 5–10× in n_e.
⚠️ **The mapping is a LOWER BOUND.** It assumes LTE; a non-LTE plasma has
n_e *above* Saha-at-T_gas. A 1 kW atmospheric MIP is plausibly near-LTE, but that
has not been established here.

### And it decides more than the cavity

- **17.6 vs 48 MHz of band margin** — whether the LDMOS can stay on resonance.
- **VSWR 15.6 vs 99.3** — and the matching-network current goes as **√VSWR**, so
  this is a **hardware-cost decision**: 17.7 A at 1e18 against 44.6 A at 1e19.
  ✅ Now **MEASURED at 75–82** (2026-08-25; the interpolated 80–89 used a cold
  Q_ext at every density) — and `../control-loop/` REVISED ITS
  REQUIREMENT UPWARD as a result (§4f there). Magnitude tuning remains an
  **unsolved problem**, and is now unavoidable rather than possibly-dissolvable.
- ⚠️ Note η is flat (0.986–0.998) across the whole range — **efficiency does NOT
  discriminate.** Temperature has to come from the chemistry, not from the EM.

## What we have — almost nothing, and it is all inherited

| | status |
|---|---|
| target elements, detection limits | ✅ **STATED 2026-09-07: soil macro- and micronutrients, LOD downstream.** See § THE TARGET IS STATED. ⚠️ Extraction method still unnamed, and LOD→residence has no transfer function |
| required T_gas | ✅ **ANCHORED to MICAP: 5220–5270 K** (2024 JAAS, pressure method) |
| required n_e | ✅ **7.3–8.6e18**, derived from T_gas by Saha |
| working gas: **N₂** | ⚠️ treated as a hard anchor by resonance |
| gas flow **≤ 20 slm N₂** | 🔴 **ASSUMED** — taken from what MP-AES and MICAP happen to use. Not optimised, and the chain slm → bore radius → coupling → input power rests on it |
| torch geometry: **Fassel** | 🔴 **ASSUMED, WRONG GAS** — the standard Fassel torch is **Argon**-optimised. No Nitrogen-optimised torch geometry is in the record |
| sample: soil extracts, **high TDS** | ✅ **QUANTIFIED 2026-09-07** from the four stated methods: **0.03 % (saturated paste) to 7.71 % (AA 8.2), a ~240× span.** See § THE EXTRACTION METHODS ARE STATED |
| power ~1 kW | ⚠️ "a stated reference, not a design point" |

🔑 **Three of those are inherited from instruments that are not this one.** The
flow, the torch and the gas choice arrived together from MP-AES/MICAP practice,
and resonance has been building on all three.

## 🔑 THE CAVITY MAY MEASURE n_e ITSELF — 2026-08-25

**`../resonance/` § THE CAVITY IS ITS OWN PLASMA DIAGNOSTIC.** f₀ is
**monotonic** in n_e (2.4515 → 2.4824 cold → 1e20), slope **1.141 MHz per 1e18** *(was 1.23 from grid-quantised f₀; §7bh)*
near the anchor. The control loop **already tracks f₀**, so locating it to
100 kHz gives **n_e to ~1 %**.
🔴 **Temperature-limited:** the cavity pulls **−57.1 kHz/K**, so ±1 K → 0.6 % and
±10 K → 5.9 %. The cavity temperature sensor is already required for the control
loop; this gives it a second job.
⚠️ **RELATIVE, not absolute.** It tracks n_e against the Saha/MICAP calibration
rather than replacing it — but ±0.6 % tracking against a **±8 %** anchor means
**drift and shot-to-shot variation become visible without any optical access.**
🔑 **That is a question this programme owns:** is a relative n_e monitor useful
for the analysis, or does the measurement need absolute density?

## ✅✅ THE TARGET IS STATED — soil macro- and micronutrients (2026-09-07)

> **STATED, user 2026-09-07:** *"The machine should be optimized for soil macro-
> and micro-nutrients, then LOD is downstream from that."*

🔑 **THIS IS THE TOP OF THE CHAIN, AND IT HAS BEEN BLANK SINCE THIS DIRECTORY
OPENED.** Item 2 below, and `../torch-geometry/` items 2 and 4, were all blocked
on it. ⚠️ **It unblocks the SPECIFICATION, not yet the DERIVATION** — see the
last block.

### The element list — DERIVED from the stated target, needs an agronomic method reference

| class | elements | by plasma OES |
|---|---|---|
| primary macro | **N**, P, K | 🔴 **N: NO** (below) · P, K yes |
| secondary macro | Ca, Mg, S | yes; **S is deep-UV** |
| micro | B, Cu, Fe, Mn, Mo, Ni, Zn, **Cl** | yes except 🔴 **Cl** (halide, vacuum-UV, done by ISE/IC) |
| also routinely reported | Na (sodicity), Al (acidity) | yes |

⚠️ **ASSUMED:** the extract chemistry (Mehlich-3, Olsen, DTPA, hot-water B) and
its concentration ranges are standard agronomic practice but are **not yet cited
here**. ➡️ **Name the extraction method before any LOD number is fixed** — it sets
the dilution, and therefore the solution concentration the instrument sees.

### ✅ THE EXTRACTION METHODS ARE STATED — and they span ~240x in dissolved solids

> **STATED, user 2026-09-07:** *"Extraction methods I would expect people would
> want are: Mehlich-III, H3A, Saturated Paste, Ammonium Acetate (AA) 8.2."*

⚠️ **ASSUMED compositions** — standard practice, **not yet cited from the method
references**. Name the source before any number here is load-bearing.
**DERIVED:** non-volatile dissolved solids the extractant carries *before* soil.

| method | what it is for | non-volatile TDS | vs ~1–2 % OES tolerance |
|---|---|---:|---|
| **Saturated paste** | soluble salts, EC, sodicity, B | **0.03–0.26 %** (640×EC) | ✅ direct aspiration |
| **H3A** | soil-health, weak organic acids | ~0.1–0.3 % ⚠️ **VERIFY** | ✅ direct |
| **Mehlich-3** | universal: P, K, Ca, Mg, S, micros | **2.09 %** (0.25 M NH₄NO₃ dominates) | ⚠️ ~1.4× dilution |
| **AA 8.2** | exchangeable cations, CEC (calcareous) | **7.71 %** (1 M NH₄OAc) | 🔴 **~5× dilution** |

🔑 **THE TWO ENDS PULL IN OPPOSITE DIRECTIONS, AND THAT IS THE DESIGN PROBLEM.**

- **Saturated paste sets the LOD requirement.** It is essentially soil water —
  the analytes are at their most dilute and there is **no dilution headroom to
  give back**. This is the binding case for detection limit.
- **AA 8.2 sets the matrix requirement.** 7.7 % dissolved solids is far above
  what a plasma tolerates, so it must be diluted ~5× — **and that dilution
  multiplies its own effective LOD requirement by the same 5×.**

➡️ **So sample introduction must cover a ~240× TDS range**, and the instrument
cannot be optimised for the middle of it. ⚠️ **This finally quantifies the
`high TDS` row in the table above, which has read *"mentioned; never
quantified"* since this directory opened.**

### ⚠️ THREE CONSEQUENCES THAT ARE NOT ABOUT LOD

- ✅ **MEHLICH-3 CONTAINS FLUORIDE** (0.015 M NH₄F, at pH ~2.5) — **and the
  torch is SAPPHIRE, which is why.** STATED, user 2026-09-07: *"For Fluorine, the
  expectation is that we would use sapphire, not quartz, but quartz is used in
  the modelling so we can compare to other machines."* Single-crystal Al₂O₃ is
  far more resistant to HF than fused silica, so a routine fluoride-bearing
  matrix is **designed for, not tolerated**. 🔑 **And the quartz in the model is a
  deliberate COMPARABILITY choice, not an oversight** — `baselines.json` already
  carries `torch.sapphire.permittivity` = 9.39 as the design value, with quartz
  4.43 beside it. ⚠️ **Do not re-raise fluoride as a lifetime risk against the
  design**; it is a risk against the *comparison* geometry only.
- **Easily-ionised-element interference.** AA 8.2 is 1 M NH₄⁺ and the extracts
  carry soil Na and K. EIE loading shifts ionisation equilibrium and is a
  classic OES accuracy problem, **independent of detection limit**.
- ✅ **AA 8.2 and Mehlich-3 are the potassium methods**, and that is what makes
  the starter fluid SELF-VERIFYING rather than risky. STATED, user 2026-09-07:
  *"The machine has a spectrometer that needs to be able to see K, and it knows
  the ignition procedure, so it can flush until K drops below the noise floor."*
  🔑 **The flush is CLOSED-LOOP on the instrument's own detector** — K is a
  required analytical line, the instrument knows it is in the ignition sequence,
  and it flushes to a measured criterion instead of a fixed time.
  🔴 **SO K IS THE RIGHT CATION, NOT A COMPROMISE.** A non-analyte cation
  (Cs/Rb/Li) would have to be flushed **blind**, with no line to watch. 🔴 **Every
  argument in this session for switching cation is WITHDRAWN** — it treated an
  observable as a contaminant. See `../ignition-options/STARTER-FLUID.md`
  § THE FLUSH IS CLOSED-LOOP.

### 🔴 NITROGEN IS NOT MEASURABLE HERE, AND THE WORKING GAS MAKES IT WORSE

**N is the first letter of NPK and plasma OES cannot deliver it** in a soil
extract. 🔴 **And this instrument is a NITROGEN plasma — the analyte would be the
working gas, at ~10⁶ times the concentration.** Soil labs obtain N by combustion
or colorimetry on nitrate/ammonium, as a separate determination.
➡️ **Not a defect, but it MUST be stated**: "optimised for soil macronutrients"
cannot be read as including N, and a product claim should not imply it.

### 🔴 P AND S FORCE THE OPTICAL-PATH DECISION — this is H5, and it is TERMINAL

Their strong lines are **below 190 nm** (P ~177.5/178.3, S ~180.7/182.0 nm),
which **air-path optics cannot see**. The options are a purged or evacuated
spectrometer, or accepting the much weaker P 213.6 nm and effectively **no S**.

🔑 **That is an architecture decision of the same class as the utility room** —
it changes what the product is, it is forced by the element list, and it is now
forced *because the element list is stated*. `../resonance/HYPOTHESES.md` H5 is
"NOT STARTED · TERMINAL" and this is its first hard input.

### ✅ AND THE LEVEL IS FAVOURABLE — this is OES territory, not MS

⚠️ **ASSUMED ranges.** Soil-extract solution concentrations run ~100–3000 mg/L
(Ca) down to ~0.01–0.5 mg/L (Mo) and ~0.05–2 mg/L (B). Required LODs are
therefore roughly **mg/L for the majors and ~5–50 µg/L for the hardest micros
(B, Mo)** — routine for emission, nowhere near the ng/L demands that justify MS.

🔑 **This propagates favourably through every open trade of 2026-09-07:**
- **OES suffices → the MS/dual-gas 7 bar generator tier is not needed.**
- **No desolvation is implied → the sample-water purity floor HOLDS**
  (`../torch-geometry/` § THE SAMPLE FLOORS THE PURITY SPEC), so a standard-tier
  generator at 4.1–5 bar / 12 slm stands.
- **Modest LOD → the residence-time requirement is unlikely to be extreme**, which
  is the first news that a narrower bore might be affordable.

### ⚠️ WHAT IS STILL NOT DERIVABLE — and it is the honest limit of this entry

**Stating the elements gives a required CONCENTRATION. It does not give a
required RESIDENCE TIME.** That mapping needs a sensitivity model or an empirical
anchor (e.g. the LOD a comparable instrument achieves at a known residence), and
neither is in the record. 🔴 **So `../torch-geometry/` item 2 is HALF unblocked:
the target exists, the transfer function does not.** Do not let "LOD is stated"
become "the bore is chosen".

### 🔴 AND IT SHARPENS THE STARTER-FLUID CONFLICT FROM HYPOTHETICAL TO CONFIRMED

`../ignition-options/STARTER-FLUID.md` calls K-as-analyte *"the strongest
objection to the whole route and it is not resolved"* — 0.5 M K-acetate is
~19,500 ppm against soil-extract K of tens to hundreds of ppm. **K is now
CONFIRMED as a primary target analyte, so that objection is no longer
conditional.**

🔴 **CORRECTED SAME DAY — I OVERSTATED THIS.** User, 2026-09-07: *"The starter
fluid has to be flushed for that reason (but any starter fluid would have to be
flushed)."* **The flush answers it, it is already in the design, and it is
GENERIC** — any seed delivered through the sample path must be cleared before the
sample, whatever its cation. See `../ignition-options/STARTER-FLUID.md` § THE
FLUSH DOES THREE JOBS.

~~The argument for a non-K cation is that it is not an analyte, so re-open the
cation choice.~~ ➡️ **A non-analyte cation buys margin against flush FAILURE, not
relief from a requirement** — robustness, weighed against Cs acetate's cost. Cs
stays rejected on the user's original ground. 🔑 **What this promotes is the
measurable: FLUSH EFFICACY** — how much seed is left, measured wet-bench with a
blank after the sequence. Not which cation.

## What's needed

| | | why it blocks |
|---|---|---|
| ~~1~~ | ~~The required gas temperature~~ | ✅ **ANSWERED** — 5220–5270 K, anchored to MICAP |
| 2 | ✅ **HALF ANSWERED 2026-09-07** — target STATED (soil macro/micronutrients); the LOD→residence-time transfer function is still missing, so the bore is NOT yet choosable. ~~**Target elements + detection limits**~~ | 🔴 **NOW THE TOP OF A CHAIN, not just an input.** User 2026-08-25: **slm → residency → LOD**. Residence time in the ±0.4L hot zone is **59.4 ms** at 2–8.5 mm / 20 slm and **10.4 ms** at 2–4 mm. **LOD sets the required residency, which sets bore area and flow, and the EM must then cope** — `../resonance/` had this backwards and treated the bore as a coupling knob. **Until LOD is stated the bore cannot be chosen at all** |
| **2b** | **T_gas as a function of GAS FLOW** | 🔴 **NEW 2026-08-25, and it gates a PRODUCT decision.** `../torch-geometry/` derives that dropping to a benchtop 10 slm — with the bore narrowed to hold residence — takes VSWR 88 → 28. **But only if n_e holds.** Less gas for the same kilowatt runs hotter, and **n_e ×3.1 (ΔT ≈ +368 K) cancels the entire gain.** The EM model cannot answer this: it takes n_e as an input |
| **3** | **Whether LTE is fair** | 🔴 **now the top open item.** Non-LTE puts n_e ABOVE Saha — and since VSWR peaks near 1e19, that pushes the tuner requirement further toward the worst case |
| 4 | High-TDS tolerance, quantified | sample introduction, and the torch bore |
| 5 | Is 20 slm N₂ right, or inherited? | the whole flow → geometry → power chain. 🔑 **NOW ALSO A PRODUCT CONSTRAINT** — user 2026-08-25: 10–12 L/min runs off a quiet bench compressor, **20+ needs a loud one in a utility room**. The assumed 20 is on the wrong side of that line. See `../torch-geometry/` |
| 6 | Is a Fassel torch right for N₂? | every torch dimension currently comes from an Argon design |

## Rules

Inherits `../resonance/CONVENTIONS.md`. The ones that bite hardest here:

- **§7ab** — a value chosen for convenience must never become "the operating
  point". That is exactly how `n_e` got its status.
- **§7ac** — never mix a verified analysis with an unverified suggestion in one
  register. **Most of this document is questions; it should stay that way until
  something is measured.**
- **§7ad** — coupled state variables must not be set as independent constants.
  `n_e`, `NU_M` and `T_gas` are one state.
- **§7s** — provenance is what was DONE, not reasoning added afterwards.

🔴 **The entries marked ASSUMED above are load-bearing for another programme's
results. Anything answered here should be dated and attributed**, so resonance
can tell an anchor from an inheritance.
