# torch-geometry — the torch is where three programmes collide

**Opened 2026-08-25.** `resonance/` needs the torch to couple. `spectroscopy/`
needs it to hold the plasma long enough to measure. **And the gas it consumes
decides whether this instrument sits on a bench or needs a utility room.**

🔴 **NOTHING IS MEASURED HERE.** This directory exists so the three-way trade
has a home. Every line is marked **STATED** (from the user) · **DERIVED** (an
arithmetic consequence of measurements made elsewhere) · **ASSUMED**.

⚠️ **Opening a directory is not a commitment to work it now** — the standing
decision is at the bottom.

---

## The three considerations — STATED, user 2026-08-25

> *"there are three considerations for a custom torch: EM, slm (LOD), and the
> nitrogen generator."*

| | constraint | owned by |
|---|---|---|
| **EM / RF** | bore sets how strongly the plasma loads TE011, so it sets coupling.beta and VSWR | `../resonance/` |
| **slm → residency → LOD** | bore area and flow set residence time, which sets detection limit | `../spectroscopy/` |
| **the nitrogen generator** | 🔑 **NEW, and it is a PRODUCT constraint** | **here** |

### 🔑 The third one is a different weight class

> **STATED:** *"At 10-12 L/min, we can use small quiet compressors right at the
> bench. At 20+ L/min, the loud heavy compressor would have to go into a utility
> room."*

**This is not a performance number, it is a form-factor decision.** A bore is a
drawing change. **Requiring a utility room is a change to what the product IS**,
and it is far harder to walk back. ⚠️ **The programme currently assumes 20 slm**
(`../spectroscopy/README.md` marks it **ASSUMED**, inherited from MP-AES/MICAP
practice) — **i.e. the loud side of the user's threshold, chosen by nobody.**

## 🔑 THE THREE CONSTRAINTS MAY POINT THE SAME WAY — DERIVED, not measured

Residence time is `L·A/Q`: **halve the flow and you must halve the bore area to
keep it.** A narrower bore is also what the EM wants. So:

| flow | bore for EQUAL residence | residence | Q₀ | coupling.beta | **VSWR** | siting |
|---:|---|---:|---:|---:|---:|---|
| **20 slm** | 2–8.50 mm *(as modelled)* | 59.3 ms | **105** | 0.0113 | **88** | 🔴 utility room |
| 12 slm | 2–6.70 mm | 59.3 ms | 243 | 0.0263 | **38** | ✅ bench |
| **10 slm** | **2–6.17 mm** | 59.3 ms | **325** | 0.0352 | **28** | ✅ bench |

✅ **Anchored on real measurement at the wide end:** `h3-bore-01` (2026-08-25)
measured 2–4 / 2–6 / 2–8.5 mm at the anchored density, and its 2–8.5 control
reproduced `h3-driven-anchor-01` to **0.27 %**. The 2–6 mm point — **which is
almost exactly the benchtop bore** — is **MEASURED at Q₀ = 360, VSWR 25.4.**
✅ Hot-zone length back-solves to **92.2 mm** from two independently documented
residence figures, agreeing to **0.4 %**.

🔑 **If it holds, the quiet compressor comes with a 2–3× better match** — and
`../control-loop/` says a 3-stub tuner is comfortable at **VSWR 20**, which this
approaches **without redesigning the loop at all.**

## 🔴 AND HERE IS WHY IT IS NOT A RESULT

**The table holds n_e FIXED at 7.9e18. It will not stay fixed.** Halving the gas
flow at constant power puts the same kilowatt into half the mass — **hotter gas,
higher n_e by Saha, MORE loading, and the VSWR gain shrinks.**

**DERIVED:** cancellation is complete at **n_e ×3.1 → 2.4e19**, which at
`../spectroscopy/`'s own sensitivity (2 decades per 1500 K) is **ΔT ≈ +368 K.**

🔴 **A few hundred kelvin is exactly the size of change halving the flow could
produce. THE CONFOUND IS THE SAME ORDER AS THE BENEFIT.** So this is a
**hypothesis with a number attached**, not a finding. It needs **T_gas as a
function of flow**, which is `../spectroscopy/`'s question, not one the EM model
can answer — the EM model *takes* n_e as input.

⚠️ Also unestablished: that a nitrogen MIP sustains at all at 10–12 slm, and
whether sample introduction survives the lower carrier flow.

## ✅ THE STANDING DECISION — STATED, user 2026-08-25

> *"I think we're fine modelling against a standard Fassel geometry for now as
> the dimensions are all known."*

**So: no custom torch modelling. `resonance/` continues on Fassel dimensions.**
The reason is good — Fassel is dimensioned in the literature, and a custom torch
would replace known numbers with invented ones.

⚠️ **But keep `../spectroscopy/` item 6 open:** the standard Fassel torch is
**Argon**-optimised, and this is a **Nitrogen** instrument. Modelling against it
is a decision to use known-but-wrong-gas dimensions **in preference to
unknown ones** — which is right, and is not the same as it being correct.

## What would move this

| | | blocked on |
|---|---|---|
| 1 | **T_gas as a function of gas flow** | 🔴 `../spectroscopy/` — turns the table above into a result or kills it |
| 2 | **The required residence time** | ✅ **TARGET STATED 2026-09-07** (soil macro/micronutrients — `../spectroscopy/` § THE TARGET IS STATED), and the level is favourable: mg/L majors, ~5–50 µg/L for B/Mo, i.e. OES not MS. 🔴 **STILL BLOCKED on the transfer function** — a concentration requirement is not a residence-time requirement, and nothing maps one to the other. ~~LOD is still not stated anywhere.~~ Until it is, "equal residence to 20 slm" is the only reference available, and it is itself inherited |
| 3 | Does a N₂ MIP sustain at 10–12 slm? | not asked |
| 4 | Nitrogen generator duty/purity at each flow | ✅ **LARGELY ANSWERED 2026-09-07.** Purity is floored LOW by the sample's own water, so a standard-tier generator suffices — **4.1–5 bar output at 12 slm, STATED by the user**. The remaining number is air FAD at pressure. ⚠️ Breaks only if aerosol desolvation is adopted |
| 5 | Is a Fassel bore right for N₂? | `../spectroscopy/` item 6 |

## 🔴 SUPERSEDED SAME DAY — ~~ITEM 4 IS THE BINDING ONE~~ · the purity premise is withdrawn

> 🔴 **SUPERSEDED 2026-09-07 by the user, hours after being written.**
> **Why:** the section below is built on purity being a free variable that LOD
> pushes UPWARD, making the air:N₂ ratio the binding cost. **The user states the
> opposite requirement:** *"We actually don't need high purity nitrogen for this
> application, because the samples will contain water anyway."*
> ✅ **And the arithmetic supports it** — see § THE SAMPLE FLOORS THE PURITY SPEC.
> **What survives:** the *shape* of the chain (purity → ratio → air demand) is
> right, and the observation that the generator multiplies where the compressor
> adds is right. **What is wrong is the direction**: purity is floored LOW by the
> sample, so the ratio is small, the air demand is modest, and item 4 is **not**
> the binding constraint. **Item 2 — residence time and LOD — is untouched and
> remains the live one.**
> ⚠️ **My inlet/outlet reading was also wrong**; corrected below.

**The original entry follows, unedited, for provenance.**

## 🔑 ITEM 4 — the generator multiplies, the compressor adds

> **STATED, user 2026-09-07:** *"The compressor will make enough for sure, the
> real question is the nitrogen generator."*

✅ **This retires the pressure flag above as the live concern** and promotes item 4
from "not asked" to the question that actually gates the flow target.

🔑 **WHY IT IS A DIFFERENT WEIGHT CLASS FROM THE COMPRESSOR.** A compressor is
sized in slm of *air*. A generator sits between them and its **air-to-nitrogen
ratio rises steeply with purity** — so N₂ demand is not added to the air budget,
it is **multiplied** by a factor the purity spec chooses. ⚠️ **ASSUMED, typical
vendor behaviour, NOT a datasheet for any part we have selected:** membrane and
PSA units run in the rough band of ~3:1 at modest purity to ~10:1 or worse as
purity is pushed toward five nines.

➡️ **Consequences, and they are the reason this is the floor:**
- **Cutting 20 → 12 slm of N₂ saves the AIR ratio times that**, so the flow target
  pays off superlinearly here and only linearly at the compressor. The
  bench-vs-utility-room threshold is therefore a **generator** threshold that has
  been attributed to the compressor.
- **Generators do not modulate well.** They are sized for peak draw and buffered,
  so a duty-cycle and receiver-volume question sits under the steady-state slm
  number that the record has been quoting as if it were the whole spec.

🔴 **AND ITEM 4 AND ITEM 2 ARE THE SAME MISSING STATEMENT.** Purity is not a free
choice: residual O₂/H₂O put molecular background into the UV, and
`LOD = 3*sigma_background / sensitivity`, so **the LOD target sets the purity spec
which sets the generator ratio which sets the air demand.** The chain is:

    target elements + detection limits  ->  background  ->  N2 purity
      ->  generator air:N2 ratio  ->  compressor slm  ->  bench or utility room

**Item 2 (required residence time) and item 4 (generator duty/purity) are both
blocked on the SAME unstated thing** — `../spectroscopy/` item 2, *"target
elements + detection limits — NOT STATED ANYWHERE."* 🔑 **That single statement
now gates the bore AND the gas plant.** It is the highest-leverage unblocked
item in this directory and it needs no solver.

### ✅ THE SAMPLE FLOORS THE PURITY SPEC — so purity is CHEAP, not expensive

> **STATED, user 2026-09-07:** *"We actually don't need high purity nitrogen for
> this application, because the samples will contain water anyway."*

✅ **DERIVED, and it puts a number on where the floor sits.** A nebulised aqueous
sample delivers oxygen to the plasma no matter how pure the carrier gas is.
1 mL/min of liquid water is **1.244 slm** of vapour; at ordinary concentric-
nebuliser transport efficiency (1–5 %) the delivered fraction of a 12 slm total is:

| uptake | transport | H₂O slm | as % of 12 slm |
|---:|---:|---:|---:|
| 0.4 mL/min | 1 % | 0.0050 | **0.041 %** |
| 0.4 mL/min | 5 % | 0.0249 | 0.207 % |
| 1.0 mL/min | 1 % | 0.0124 | 0.104 % |
| 1.0 mL/min | 5 % | 0.0622 | **0.518 %** |

Against a generator's own residual, counted as O atoms: 99.9 % N₂ → ~0.2 %,
99.5 % → ~1 %, 99.999 % → ~0.002 %.

🔑 **SO THE CROSSOVER IS AROUND 99.5–99.9 %.** Below it the generator dominates
the oxygen budget; above it **the sample does, and further purity is spent on a
contaminant the sample re-introduces anyway.** Five-nines nitrogen would be
~100× below the sample's own floor. ➡️ **Standard-tier generator, low air:N₂
ratio, small compressor** — the favourable branch of every trade above.

⚠️ **THE ONE CONDITION THAT BREAKS IT: AEROSOL DESOLVATION.** Stripping the
solvent before the plasma removes the floor and makes generator purity matter
again. 🔴 **And that is not hypothetical — the programme's T_gas anchor is Kuonen
2024, *"N₂ MICAP-MS with solution nebulization AND AEROSOL DESOLVATION"*.** If
this instrument desolvates, this section does not apply. **Not decided anywhere.**

⚠️ **And low purity is not free in the other direction:** O₂ oxidises a hot
injector tip, and NO/OH bands raise the UV background that `LOD` is defined
against. The claim here is that purity beyond the sample's own floor buys
nothing — **not** that purity is irrelevant.

### 🔑 THE SUPPLY-PRESSURE TIERS SPLIT ON A DECISION THAT WAS PARKED AS IRRELEVANT

> **STATED, user 2026-09-07:** *"I'm seeing 4.1 to 5 bar for standard nitrogen
> generators, then jumping to 7 bar for specialized mass spectrometers or
> dual-gas systems."*

🔴 **CORRECTION, same day: I read this as INLET air pressure. It is the
GENERATOR OUTPUT.** User, 2026-09-07: *"That's 4.1 to 5 bar at the nitrogen
generator output, 12 slm."* **That is the delivery spec to the torch, not the
demand on the compressor** — a different quantity, and it makes the number far
stronger than I gave it credit for.

✅ **AND IT CLOSES THE BACK-PRESSURE FLAG COMPLETELY.** § IF THE ANSWER IS "NO"
raised a thin-sheath-gap back-pressure worry. **4–5 bar of delivery against a
torch needing order tens of millibar is ~100× margin.** The sheath gap is free to
be as thin as the geometry wants. 🔴 **That flag is WITHDRAWN** — it was raised on
a supply pressure nobody had stated, and the stated one dwarfs the requirement.

🔴 **BUT THE TIER BOUNDARY IS MS-vs-OES, AND THAT DECISION IS PARKED.**
`../spectroscopy/README.md` says *"MS-vs-OES does not enter — same plasma,
different detector."* ✅ **True for the question it was written about** (required
gas temperature). 🔴 **False for the gas plant**: the 7 bar tier is *defined* by
MS and dual-gas. So a choice set aside as not mattering turns out to matter, for
an unrelated reason — a formula quoted outside its domain.

⚠️ **AND THE RECORD ALREADY LEANS ON THE MS SIDE WITHOUT HAVING CHOSEN IT.** The
T_gas anchor is **MICAP-MS** (Kuonen 2024), explicitly *"the plasma AS SAMPLED
THROUGH THE MS INTERFACE"*, and the 20 slm assumption came from MP-AES/MICAP
practice. **Three inherited numbers, and the detector they were inherited from is
formally undecided.**

🔑 **SO IT IS THE SAME FORM-FACTOR ARGUMENT, ONE LEVEL UP THE SUPPLY CHAIN.**
This directory already says a bore is a drawing change while a utility room
*"is a change to what the product IS"*. **Crossing from the standard generator
tier into the MS/dual-gas tier is a product-class boundary of the same kind** —
and it is set by the same unstated LOD/purity spec that gates items 2 and 4.

⚠️ **CROSS-LINK to `../ignition-options/STARTER-FLUID.md`, and it cuts both ways.**
That document lists *"whether it gasifies"* as unestablished, noting *"Pure N₂ has
no oxygen, but the DI flush does."* **Generator N₂ is not pure** — residual O₂ is
exactly what would burn off an accumulated carbon deposit between runs. So a
purity spec set only by spectroscopic background may be **over-specifying against
a residual that the ignition route wants**. Neither side has been asked.

## Rules

Inherits `../resonance/CONVENTIONS.md`. The ones that bite here:

- **§7ab** — a value chosen for convenience must never become "the operating
  point". **20 slm is on that path right now**: inherited from other
  instruments, never chosen, and now load-bearing for product form factor.
- **§7ac** — never mix a verified analysis with an unverified suggestion in one
  register. The table above is DERIVED and its confound is stated beside it.
- **§7z** — state the effect size that would matter. Done: **+368 K cancels it.**
- **§11** — two points cannot establish a scaling law. The bore extrapolation
  uses a **measured** local exponent (n = 0.884) from three points, and the
  benchtop bore sits **between** measured points rather than beyond them.

---

# 🔑 THE FLOW SPLIT AND THE 1 kW TARGET — STATED, user 2026-09-07

🔴 **RECONSTRUCTED, NOT RE-VERIFIED.** Recovered from transcript
`75028922-144d-4f1c-9680-d77f8f82457d`, 2026-09-07 02:37–02:45, after an API
safeguard false positive killed the session before anything was written. The
STATED lines are the user's verbatim; the DERIVED arithmetic has not been
re-run.

## STATED — the target, and it is three streams, not one

> *"I would like to target a lower slm than 20. Preferably 10, because that can
> be met by only a quiet compressor running on 120/15."*
>
> 🔑 *"Careful not to conflate flows. For the heat-dissipating shell around the
> inside of the outer torch wall, we want about 10 slm. The intermediate is just
> to push the plasma off the tip of the injector, so that it doesn't melt (1 slm,
> say). Then the injector with aerosol, say another 1 slm."*
>
> *"And we're targeting 1 kW."*

| stream | slm | job |
|---|---:|---|
| outer / coolant shell | **10.0** | cools the outer tube wall; a boundary layer that **stays cool** |
| intermediate / auxiliary | **1.0** | pushes the plasma off the injector tip so it does not melt |
| injector / nebuliser | **1.0** | carries the aerosol — **and the starter fluid** |
| **total** | **~12** | |

## 🔑 CAN THE STARTER FLUID BUY A NARROWER TORCH? — the constraint splits in two (2026-09-07)

**Question, user 2026-09-07:** whether the starter-fluid route accommodates a
narrower torch. ⚠️ **DERIVED arithmetic below; nothing here is measured.**

✅ **The starter fluid does remove IGNITION as a bore constraint — but ignition
was never the thing setting the bore.** On the carbon route the deposit is a
volumetric absorber (skin depth 322 µm at σ = 1e3, still 3.2 mm at σ = 10,
against a sub-micron film), so ignition no longer needs a breakdown field in the
bore, at any diameter. The binding constraint was, and remains, **residence time
→ LOD**.

🔑 **AND THAT CONSTRAINT SPLITS INTO A PART THAT SURVIVES AND A PART THAT DOES
NOT.** `KNOWN.md`'s residence table reproduces exactly as a flat **20 slm** through
the analyte annulus over an implied **92 mm** length, **cold**:

- 🔴 **~~The RATIO is robust~~ — WITHDRAWN 2026-09-07.** I argued `t = L·A/Q`
  makes the 5.69× area ratio survive any flow or temperature correction.
  **The arithmetic is fine and the mapping is wrong.** User: *"The resident
  argument doesn't really hold, because the majority of Nitrogen goes toward the
  cooling sheath regardless."* 🔑 **The 2–8.5 mm annulus is the PLASMA annulus
  the EM model meshes. It is not the channel the ANALYTE occupies** — the sample
  goes up the injector as a central channel at ~1 slm, while the sheath's 10 slm
  flows outside the discharge doing a thermal job. **Narrowing the outer torch
  need not change the analyte channel at all**, so it need not change residence
  at all. The ratio holds only under the assumption being rejected: that the
  analyte traverses the full annulus at the total flow.
- 🔴 **The ABSOLUTE times (10.4 / 27.8 / 59.4 ms) do NOT.** Two large corrections
  are missing and they push OPPOSITE ways:
  1. **Wrong flow.** The table pushes all 20 slm through the analyte channel. In
     the three-stream split the analyte path is the **injector's ~1 slm**; the
     10 slm shell never enters it. Alone this makes residence ~20× LONGER.
     (§ THE FLOW SPLIT already makes this point for the deposit.)
  2. **Cold gas.** At discharge temperature the gas expands ~17×, so velocity
     rises and residence falls by about that factor.

➡️ **So "is 2–4 mm long enough?" is currently unanswerable, and not because it is
hard** — because the absolute number has never been computed on the right flow at
the right temperature, and because **the LOD target it must be judged against is
still unstated** (`../spectroscopy/` item 2: *"target elements + detection limits
— NOT STATED ANYWHERE"*). 🔴 **A bore cannot be chosen until that is stated.**

## 🔎 PROPOSED — BRIDGE PALACE AND OpenFOAM (user, 2026-09-07). ASSESSED, NOT STARTED

➡️ **BUILD SCOPE IS IN `BRIDGE.md`.** OpenFOAM v2412 is installed and verified in
parallel on the volume (`../resonance/DEPLOY.md`); no bridge code exists yet.

> **STATED, user 2026-09-07:** *"I think we can model it, by bridging Palace and
> OpenFOAM."*

✅ **PRIOR ART SEARCHED 2026-09-07: nothing in this repo.** Externally the
approach is standard — coupled EM + CFD models of ICP/MIP torches are long
published and validated against measured temperature profiles, **so an external
anchor exists**, which is what `CLAUDE.md` requires before a new instrument
licenses anything.

🔑 **SPLIT IT. ONE DIRECTION IS TRACTABLE AND ANSWERS EVERY QUESTION ASKED; THE
OTHER RUNS INTO A TRAP THIS PROGRAMME HAS ALREADY PAID FOR.**

### ✅ ONE-WAY, Palace → OpenFOAM — this is the one to build

Palace supplies volumetric power deposition and surface heat flux; OpenFOAM does
the flow, conjugate heat transfer through the sapphire wall, and the three
streams. **No feedback required, because n_e is anchored EXTERNALLY** (MICAP
5220–5270 K) rather than being solved for.

🔑 **THE HANDOFF QUANTITY IS ALREADY CALIBRATED, WHICH IS UNUSUAL.**
`../resonance/KNOWN.md` § THE POWER BALANCE closes wall + port + loop to **97 %**
of the port's claimed absorption, and § COUPLER DISSIPATION gives wall 547 mW and
loop 4.97 mW per 1 W incident. **The interface between the two solvers is the one
quantity this programme has most recently validated.**

It answers, in order of what is currently blocking:
1. **Wall temperature vs sheath flow** — the 12 slm question, and the sapphire
   headroom claim above.
2. **Injector tip temperature vs intermediate flow** — the standoff that has
   never been analysed.
3. **The analyte path and its residence** — replacing the withdrawn table with a
   number that is about the analyte.
4. **Sapphire vs quartz**, including the ignition transient, which is thermal
   shock and therefore exactly a CHT problem.

### 🔴 TWO-WAY, feeding T back into (eps, sigma) — do NOT start here

- 🔴 **The `T -> n_e` step cannot use LTE Saha, and that is the whole difficulty.**
  This directory ALREADY VOIDED a calculation for it (§ ALSO WITHDRAWN): *"It
  used LTE Saha for n_e, which forces sigma to 3.5 S/m and kills the coupling by
  construction"*, and the record holds that **n_e is kinetics-limited** — the
  densities that matter are 4.8e16–1.2e18, one to two orders below equilibrium.
  **A coupled loop closed through Saha reproduces a known-void result with more
  machinery behind it.** Non-LTE needs a collisional-radiative or two-temperature
  model, which OpenFOAM does not have off the shelf.
- ⚠️ **AND PALACE'S MATERIAL MODEL IS PER MESH ATTRIBUTE.** Configs assign
  `{"Attributes": [...], "Permittivity": ...}` — one scalar per region. **A
  continuous `eps(r,z)` from CFD must be discretised into attribute zones**, i.e.
  a `geometry.py` change and a re-meshed cavity. That is the concrete engineering
  cost of two-way, on top of the physics problem.
- ⚠️ The loop would also traverse the **eps-near-zero** region where
  `CONVENTIONS.md` records the div-free PCG failing (92 non-convergences at
  ne = 1e19). A solver that stalls mid-iteration is worse than no loop.

### ➡️ IF IT IS BUILT, THE PROGRAMME'S OWN RULES APPLY TO IT

- 🔑 **It is a new INSTRUMENT, not a new experiment.** The list E0–E4 does not
  grow (§7k). But `CLAUDE.md`'s E0 exists precisely because an uncharacterised
  solver invalidated six rigs, so **budget a CFD E0**: reproduce a published
  torch case with measured temperature profiles before any of its numbers are
  quoted here.
- **One rig, one solver** (§ ONE RIG ONE SOLVER) applies across the bridge too:
  do not parameterise "EM or CFD" inside one script.
- **Name what the bridge CANNOT do**, the way `INSTRUMENT.md` does for Palace.

## ✅✅ MEASURED: WALL TEMPERATURE OF A GAS-COOLED FASSEL TORCH — and its flow is ours

**Engelhard, Scheffer, Maue, Hieftje & Buscher**, *Spectrochim. Acta B* **62**
(2007) 1161–1168 — `refs/1-s2.0-S0584854707002224-main.pdf`.
✅ **READ (primary), supplied by the user 2026-09-08.** IR thermography of
operating ICP torches, with emissivity (0.50→0.35 over 873–1323 K) and quartz
transmission (20 % at 3.75–4.02 µm) calibrated and corrected.

### 🔑 ITS CONVENTIONAL TORCH IS ALMOST OUR FLOW SPLIT, AT ALMOST OUR POWER

| stream | **this paper** | **our target** |
|---|---:|---:|
| outer / coolant | **12 L/min** | 10 slm |
| auxiliary / intermediate | **1 L/min** | 1 slm |
| central / injector | **1 L/min** | 1 slm |
| **total** | **14** | ~12 |
| **RF power** | **1400 W** | ~1000 W |

**Three streams, same roles, same order of magnitude, and the wall is cooled by
the OUTER PLASMA GAS — not by water.** This is the closest published match to
the machine this programme is designing that the record has found.

### ✅ THE MEASURED WALL TEMPERATURES

| torch | condition | wall `T` |
|---|---|---:|
| **conventional Fassel** | 14 L/min total, 1400 W | **max 725 ± 44 K** (after 3rd coil turn) |
| | between first two turns | 525 ± 32 K, 560 ± 34 K |
| | min→max spread | only **250 K** |
| **SHIP low-flow** | 0.6 L/min + 24 m/s cooling air | **1580 ± 95 K** |
| | + 48 m/s cooling air | 1275 ± 75 K |
| | inlet zone 0–15 mm | < 650 K |

⚠️ **Uncertainty ±6 %** — far tighter than the ±20–25 % of the Punjabi CFD paper.

### 🔴 AND IT SETTLES THE SAPPHIRE ARGUMENT WITH MEASURED NUMBERS ON BOTH SIDES

Its **Table 1** gives the fused quartz properties directly: **maximum working
temperature (continuous) 1433 K**, strain temperature 1398 K, softening 1983 K,
thermal conductivity **1.46 W/m·K at 373 K**.
✅ **My earlier handbook estimate (~1150 °C ≈ 1423 K continuous) is confirmed to
0.7 % by the paper's own table** — the sapphire-headroom arithmetic stands, now
anchored rather than recalled.

🔑 **THE LOW-FLOW TORCH AT 1580 ± 95 K IS ABOVE QUARTZ'S 1433 K CONTINUOUS
RATING.** That is not an extrapolation — it is a measured operating point on a
real low-flow torch, exceeding the material's own published limit. **Low flow
drives quartz past its rating; sapphire's ~2123 K does not.**
⚠️ The paper also notes *"temperatures above 1073 K can heavily influence the
long-term stability of ICP torches"*, while *"low temperatures (< 373 K)
contribute to sample deposition"* — **a design WINDOW, roughly 373–1073 K for
quartz**, which sapphire widens at the top.

⚠️ **WHAT STILL DOES NOT TRANSFER:** argon not nitrogen, 27.12 MHz coil not a
2.45 GHz cavity, and the SHIP torch is a different geometry cooled by external
air. **725 K is not our wall temperature.** What transfers is the flow split, the
power scale, the gas-cooled architecture, and the material limit.

## 🔑 SAPPHIRE'S OPERATING TEMPERATURE MAY BEAT TORCH DIAMETER AS THE FLOW LEVER

> **STATED, user 2026-09-07:** *"Another consideration is that sapphire has a
> higher operating temperature than quartz."*

⚠️ **ASSUMED, materials-handbook values — nothing here is measured.** Fused silica
serves continuously to ~1150 °C (it devitrifies above ~1100 °C; softening
1665 °C). Sapphire serves to ~1850 °C (melts 2053 °C). **~700 K of headroom.**

🔑 **AND THE SHEATH'S JOB IS DEFINED BY THAT LIMIT.** The 10 slm exists to hold
the wall below what the wall can take. Raise what it can take and the duty falls:

- **Radiative shedding at the limit goes as T⁴** — (2123/1423)⁴ = **~4.95×**. A
  sapphire wall at its own limit disposes of ~5× the heat a quartz wall can.
- **Convective removal goes as (T_wall − T_gas)**, so the allowable driving
  difference widens too.
- **Conductivity ~30 vs ~1.4 W/m·K (~21×)** spreads hotspots instead of
  concentrating them — relevant because N₂'s dissociation-driven conductivity
  peak delivers a *higher* heat flux than Ar would.

➡️ **SO SAPPHIRE, NOT DIAMETER, MAY BE THE THING THAT MAKES ~12 slm REACHABLE.**
It attacks the same constraint — wall heat load — without touching the geometry
the EM model is built on, without inventing torch dimensions the literature does
not have, and without the N₂-vs-Ar redesign question. **It is also already the
design material** (`baselines.json: torch.sapphire.permittivity`, measured 9.39),
chosen for the fluoride matrix — this is a second, independent payoff from a
decision already made.

⚠️ **THE COUNTER-CONSIDERATION, AND IT IS THE IGNITION TRANSIENT.** Expansion is
~0.55e-6/K for fused silica against ~5–8e-6/K for sapphire, ~10×. **Quartz has the
better thermal-shock behaviour**, so the case to check is not steady state but
the **cold, resonant, unloaded ignition transient** — the same worst case
`../resonance/KNOWN.md` § COUPLER DISSIPATION identifies for the loop. ⚠️ Also
unpriced: sapphire tube cost and whether a concentric Fassel geometry with
tangential inlets is even manufacturable in it.

## 🔴 RESIDENCE AND THE INTERMEDIATE FLOW ARE BOTH HAND-WAVED — stated plainly

> **STATED, user 2026-09-07:** *"Yes, we really have been only hand-waving at
> residence (and by extension, the intermediate flow that pushes the plasma off
> the tip of the injector, so that it doesn't melt it)."*

**Recorded so no future session treats either as established.**

- **Residence.** The only table in the record is `../resonance/KNOWN.md`'s, and
  it is the EM model's *plasma annulus* at the *total* flow, cold. It is not a
  statement about the analyte. See the withdrawal above.
- 🔴 **The intermediate stream (~1 slm) has NEVER been analysed at all**, and it
  is not a minor omission: its job is to **stand the plasma off the injector tip
  so the tip does not melt**. That standoff determines *where the analyte enters
  the hot zone*, which is the upstream boundary of any residence calculation.
  **So the residence question is downstream of a flow nobody has looked at.**
- 🔑 **Sapphire relaxes this one too** — a sapphire injector tip tolerates a
  hotter environment than a quartz one, so the standoff the intermediate stream
  must buy is smaller. Same lever, second application.

⚠️ **None of the three is answerable with Palace.** They are thermal and fluid
questions. **What this directory can honestly do is name them and refuse to let
EM numbers stand in for them** — which is exactly what the misapplied residence
table did three times in one session.

## ✅ THE CASE FOR A NARROWER TORCH — restated on the reasons that actually hold

> **STATED, user 2026-09-07:** *"I was thinking a narrower torch might be better
> overall, but maybe it isn't. I was considering it due to Fassel being designed
> for Argon, and because it might make 12slm easier to hit. The resident argument
> doesn't really hold, because the majority of Nitrogen goes toward the cooling
> sheath regardless."*

🔑 **THE OBJECTION I KEPT RAISING IS THE ONE THAT FAILS, AND THE REASONS FOR
NARROWING ARE UNTOUCHED BY IT.** Restated honestly:

| argument | direction | status |
|---|---|---|
| **Fassel is Argon-dimensioned** | → narrower | ✅ **real, and the record already says so.** `../spectroscopy/` item 6: Fassel is *"known-but-wrong-gas dimensions in preference to unknown ones — which is right, and is not the same as it being correct."* N₂ is not Ar: its dissociation-driven conductivity peak means a different heat flux and a differently shaped discharge. **Unquantified** |
| **makes 12 slm easier to hit** | → narrower | ✅ **real, and it is a SHEATH argument, not a residence one.** A narrower outer tube has less wall circumference to cool AND less annular area, so the same slm moves faster. Both help. **Unquantified** |
| **EM coupling / VSWR** | → narrower | ✅ **MEASURED** — `h3-bore-01`, 2–6 mm gives Q₀ = 360, VSWR 25.4 against 2–8.5 mm's VSWR ~79. ⚠️ Confounded: halving flow at fixed power raises n_e and the gain shrinks; cancellation at ~×3.1 |
| ~~residence time → LOD~~ | ~~→ wider~~ | 🔴 **WITHDRAWN above.** Applied to the plasma annulus and the total flow; the analyte is in the central channel at ~1 slm |

➡️ **SO THE BALANCE HAS MOVED TOWARD NARROWER**, and the two live reasons are
**thermal and fluid** — wall heat load, sheath velocity, and N₂-vs-Ar discharge
dimensions. 🔴 **None of them is answerable with this instrument.** Palace has no
thermal or fluid solver (§ THE MODEL CANNOT ANSWER FLOW QUESTIONS), and the EM
half is already measured across the range of interest.

⚠️ **THE STANDING DECISION IS UNCHANGED AND STILL RIGHT.** *"No custom torch
modelling; Fassel dimensions"* was justified on the ground that Fassel is
dimensioned in the literature while a custom torch replaces known numbers with
invented ones. **That reasoning is about MODELLING and is untouched by any of the
above** — the case for a narrower BUILD getting stronger is not a case for
modelling one. 🔑 **What would actually settle it is a thermal/fluid calculation
or a bench measurement, not a solve.**

🔴 **IF THE ANSWER IS "NO", THE COST LANDS ON THE SHEATH GAP — AND THEN ON
PRESSURE, NOT FLOW** (user, 2026-09-07: *"the 20 slm is mostly the outer cooling
sheath"*, and *"my guess is no ... which could pose a problem for the 12 slm
target"*). ⚠️ **DERIVED.**

The section above computes *"10 slm through a 17 mm Fassel bore = 0.73 m/s — low"*
and concludes ICP-like velocity means shrinking the bore. 🔴 **That divides the
sheath flow by the WHOLE BORE.** It is the bulk velocity in the discharge, not
the velocity in the sheath channel — and it is the channel that cools the quartz.
Inside the torch the sheath occupies an **annulus**, whose area is
`2*pi*R*gap` and is therefore a free variable at any bore:

| outer ID | gap | area | v at 10 slm, cold |
|---:|---:|---:|---:|
| 17 mm | 1.0 mm | 50.3 mm² | **3.32 m/s** |
| 19 mm | 1.0 mm | 56.5 mm² | 2.95 m/s |
| 22 mm | 1.0 mm | 66.0 mm² | 2.53 m/s |
| 22 mm | 0.5 mm | 33.8 mm² | **4.94 m/s** |

✅ **So a wide bore at 10 slm CAN hold ICP-like sheath velocity (~3–4 m/s cold)** —
but only on a **0.5–1.0 mm gap**, and since area goes as `R*gap`, **the gap must
shrink in proportion as the tube widens.**

🔑 **WHICH MOVES THE CONSTRAINT FROM FLOW TO PRESSURE, AND THE RECORD HAS NEVER
STATED A PRESSURE.** The compressor is specified by slm and by fitting a
120 V/15 A circuit; its **delivery pressure appears nowhere**. A narrow annulus is
where back-pressure is generated, so "wide bore + 10 slm" is bought with exactly
the quantity nobody has budgeted. ➡️ **The missing spec is the compressor's
delivery pressure against the torch's pressure drop** — and it is a plumbing
number, obtainable without any solve.

⚠️ **NOT A PROPOSAL.** `CLAUDE.md`'s standing decision for this directory is
*"No modelling: standing decision is Fassel"*, and § THE MODEL CANNOT ANSWER FLOW
QUESTIONS applies — Palace has neither a thermal nor a fluid solver. This is a
flag on a coupled constraint, not a torch design.

⚠️ **AND THERE IS A PULL TOWARD NARROW THAT IS INDEPENDENT OF IGNITION.**
`KNOWN.md` records a narrower bore raising Q₀ → raising `coupling.beta` →
collapsing VSWR (79 → ~4, load current 40 → 9 A), which *is* `../control-loop/`
requirement 1 solved by geometry. ⚠️ That scaling rests on two things the same
section says are not true (empty-cavity overlap; n_e held fixed while the bore
shrank). **A lever nobody has costed — not a recommendation.**

✅ **This supersedes the flat "20 slm" the programme has been assuming.** That
number is now stale in at least three places: this repo's `CLAUDE.md`
(*"The programme assumes 20"*), `../spectroscopy/README.md` (marked ASSUMED,
inherited from MP-AES/MICAP practice), and the residence-time table above, whose
20 slm row is the reference the other rows are held equal to. ⚠️ **The tables
above have NOT been recomputed against 12 slm in three streams.**

## 🔴 WITHDRAWN — "20 slm exceeds a 1 kW source"

A sensible-heat calculation gave 2.43 kW at 20 slm and 1.21 kW at 10 slm, and was
presented as a power *floor* — i.e. that the flow target was a feasibility
requirement, not a compressor convenience. 🔴 **It heated ALL the gas to 5245 K.
The coolant shell's entire job is to not be heated.**

| stream | slm | kW *if* it reached 5245 K |
|---|---:|---:|
| outer / coolant shell | 10.0 | 1.21 |
| intermediate | 1.0 | 0.12 |
| injector | 1.0 | 0.12 |

**The bracket is six-fold: 0.24 kW if only the core streams are heated, 1.46 kW
if everything is.** The withdrawn figure sat at the top of that bracket while
being called a floor. **What the shell absorbs leaves as a WALL HEAT LOAD, not
as enthalpy in the discharge — a different term in the energy balance entirely.**

✅ **What survives, and is sharper:**

- **The coolant shell is a thermal problem, not a plasma-power problem.** Its
  10 slm sets how much heat can be pulled off the quartz. That is the number to
  size wall load against — same class as the coupler thermals in
  `../resonance/KNOWN.md` § COUPLER DISSIPATION, and it needs the same tool
  Palace does not have.
- **The core streams are only ~2 slm**, so the plasma's own enthalpy demand is
  modest and far more comfortable against 1 kW than the withdrawn figure implied.
- 🔑 **It helps ignition.** Convective quenching of the starter fluid's carbon
  deposit is set by the **injector's ~1 slm**, not the shell's 10. The deposit
  sits in a much gentler environment than a flat flow assumption suggests. See
  `../ignition-options/STARTER-FLUID.md`.
- **It reopens bore diameter from the other end.** At 10 slm through a 17 mm
  Fassel bore the cold velocity is 0.73 m/s — low. Holding ICP-like velocities
  means shrinking the bore. 🔑 **Flow and diameter are one decision, not two.**

## 🔴 ALSO WITHDRAWN — the "operating point is an outcome" power balance

A zero-D balance against the measured coupling map put the discharge at
**~4,530 K**, concluding the plasma could not reach the anchored 5,245 K at 1 kW
and that the MICAP-anchored n_e was therefore not our operating point.

🔴 **VOID.** It used **LTE Saha** for n_e, which forces σ to 3.5 S/m and kills
the coupling by construction. `../resonance/Q_LEDGER.md` already says n_e is
**kinetics-limited, not LTE** — the densities that actually matter are 4.8e16 to
1.2e18, one to two orders below Saha equilibrium. It also quoted **VSWR 102** as
"at the anchored density" from the middle of an append-only ledger, ~80 lines
above the section that supersedes it:

> *"The plain loop's useful band (sigma 0.008–0.04, VSWR 1.3–3.1) is therefore a
> window the gas passes THROUGH, not a point it must be held at."*

✅ **What actually stands for the 1 kW target:** the plain barrel loop's useful
band is **VSWR 1.3–3.1 across σ 0.008–0.04**, inside the tuner budget, and the
gas sweeps through it while heating. **No VSWR 102, no coupling collapse, no
series gap needed.** User, 2026-09-07: *"You're reading old numbers. VSWR = 102
is nonsense."*

⚠️ **§7bp / read-forward:** `Q_LEDGER.md` is append-only. Quoting from its middle
imports premises the record has already dropped. This happened twice on
2026-09-07.

## ⚠️ THE MODEL CANNOT ANSWER FLOW QUESTIONS — flagged, and it was reached for twice

Our EM model has **a single homogeneous plasma annulus at r = 2.0–8.5 mm and no
stream structure at all** — no shell, no intermediate, no injector as distinct
regions. Every Q and coupling number in the record is for that annulus. That is
fine for coupling, since the EM only sees ε and σ. 🔴 **But it means the model
cannot represent the radial gradient three streams create**, and it must not be
reached for to answer flow questions. On 2026-09-07 it was, twice.

## What this adds to "What would move this"

| | | blocked on |
|---|---|---|
| 6 | **Does a N₂ MIP sustain at ~12 slm in three streams?** Residence falls to ~4 ms; the plasma may sit back into the torch or fail to stabilise | gas dynamics and torch design — **outside anything this programme models, and the constraint most likely to push back** |
| 7 | **Wall heat load on the quartz at 10 slm shell flow** | needs a thermal tool Palace does not have — same gap as coupler thermals |
| 8 | **Does a commercial N₂ MICAP run 15–20 slm?** If so it is not running on 1 kW, and the programme should know whether it has been implicitly assuming flow or power | literature; `../spectroscopy/` |
