# STARTER FLUID — option 4, evaluated

**Opened 2026-09-07.** 🔴 **RECONSTRUCTED, NOT RE-VERIFIED.** The session that
produced this was killed by an API safeguard false positive (`[bio]`,
req_011CeoJy5PXucq9pouFdqVnw / req_011CeoK4arDn2FL3XAD27LDm) before anything was
written. Everything below was recovered from the transcript
`75028922-144d-4f1c-9680-d77f8f82457d`, 2026-09-07 01:50–02:45. **No number here
has been re-derived in the session that wrote this file.** Treat every figure as
carrying its original caveat plus one more.

Inherits `README.md`'s register: **STATED** (user) · **DERIVED** (arithmetic on
measurements made elsewhere) · **ASSUMED**. 🔴 **Nothing here is measured.**

---

## The proposal — STATED, user 2026-09-07

> *"Argon ignition will work and so will arc ignition, but both are complicated.
> I wanted to talk about a starter fluid. Potassium Acetate, at around
> 0.1M–0.5M."*
> *"Just start the plasma, then flush with DI water before introducing the
> sample."*
> *"At 400 °C, the Potassium Acetate is split into potassium carbonate, and
> Acetone, rather than appearing as a gas, is rapidly pyrolized into an
> amorphous carbon."*
> *"The intuition for this idea came not just from the grape-resonance
> experiment, but also the match-in-a-jar experiment (soot). Both methods
> reliably result in a plasma even in consumer-grade microwaves."*

🔑 **The systems claim, which is the actual proposal:** the ignition hardware can
be *deleted*, because the instrument already has a sample path. A consumable
liquid delivered through the existing nebuliser supplies both the susceptor and
the seed, then is flushed out before the sample.

## The chain — as the user finally framed it

| step | route | evidence |
|---|---|---|
| liberate K vapour | **thermal.** K acetate → K₂CO₃ + acetone; acetone pyrolyses to amorphous carbon; carbon self-heats in the field; carbothermal reduction `K₂CO₃ + 2C → 2K(g) + 3CO` liberates K below carbonate's own ~1,470 K decomposition | match-in-a-jar (soot, cold start, consumer oven); Zhang 2024 |
| ~~liberate K vapour~~ | ~~Mie hotspot field-ionises K in the skin~~ | **the grape's route — BYPASSED, not stacked.** STATED by user |
| K vapour → plasma | low ionisation energy, cascade, microwave-heated | grape paper emission spectrum: K 766 nm, Na 589 nm |
| hand over to N₂ | nitrogen self-sustains once lit | σ = 3.56 S/m at the anchored 5245 K |
| remove the seed | DI flush; carbon consumed by `C + H₂O → CO + H₂` | ⚠️ unverified that it reaches the deposit |

🔑 **The DI flush is part of ignition, not cleanup.** Dropping the seed after
the plasma lights removes seed shielding and lets the cavity re-couple as
nitrogen ionises. That makes the flush a **triggered step with timing**, not a
wash cycle.

## 🔑 THE FLUSH DOES THREE JOBS — and the third was discussed but never written down

> **STATED, user 2026-09-07:** *"The starter fluid has to be flushed for that
> reason (but any starter fluid would have to be flushed). This was discussed,
> but seems to have not been recorded."*

⚠️ **RECOVERED, not re-derived.** The record had two of the three. Listing all
three, because the omission made an answered objection look open:

| # | job | recorded before? |
|---|---|---|
| 1 | **Remove seed shielding** so the cavity re-couples as N₂ ionises | ✅ yes — *"part of ignition, not cleanup"* |
| 2 | **Gasify the carbon** so the susceptor is consumed, not accumulated | ✅ yes |
| 3 | 🔑 **Clear the seed as a CONTAMINANT before the sample** | 🔴 **NO — this is the gap** |

🔑 **AND JOB 3 IS GENERIC TO THE CONCEPT, NOT TO POTASSIUM.** *Any* starter fluid
introduced through the sample path must be flushed before the sample, whatever
its cation — otherwise the ignition aid is in the analytical blank. **So the
flush is not a cost attributable to K**, and the analyte question is not a reason
to prefer one cation over another. Both jobs 1 and 3 demand the same step; the
design already has it.

## ✅✅ THE FLUSH IS CLOSED-LOOP — and K being an analyte is the REASON IT WORKS

> **STATED, user 2026-09-07:** *"I don't know why you keep bringing up cesium,
> and keep trying to reject K. The machine has a spectrometer that needs to be
> able to see K, and it knows the ignition procedure, so it can flush until K
> drops below the noise floor."*

🔴 **THIS INVERTS THE OBJECTION COMPLETELY, AND EVERY CATION ARGUMENT IN THE
RECORD IS WITHDRAWN.** The flush is **not** an open-loop step of unknown
efficacy. The instrument:

1. **must** be able to see K — it is a primary soil macronutrient and a required
   analytical line, so the detector exists whether or not K is the seed;
2. **knows** it is executing the ignition procedure, so it knows to watch;
3. therefore **flushes to a MEASURED CRITERION** — K below the noise floor —
   rather than for a fixed time.

🔑 **SO CHOOSING THE ANALYTE AS THE SEED IS THE CORRECT DESIGN, NOT A COMPROMISE
FORCED BY COST.** A non-analyte cation (Cs, Rb, Li) would have to be flushed
**blind**: no line to watch, no criterion, and the residual would be invisible
precisely because nobody measures it. **The property I kept treating as the
liability is what supplies the verification.**

🔴 **WITHDRAWN, EXPLICITLY, so it is not re-derived a fourth time:**
- ~~"K-as-analyte is the strongest objection to the whole route"~~
- ~~"re-open the cation choice against the stated element list"~~
- ~~"a non-analyte cation buys margin against flush failure"~~
- ~~"flush efficacy is the measurable that matters — an unmeasured open item"~~

⚠️ **What legitimately remains** is narrow and is a CONTROL question, not a
chemistry one: the flush criterion (how many noise floors below), the settling
behaviour of alkali memory on injector and torch as it is approached, and the
time cost per ignition. **Those belong with the control loop, not here.**

## Why it reframes ignition — DERIVED from the MEASURED power map

The cavity puts **40 % of incident power into electrons at σ = 0.0028 S/m**, the
lowest state actually measured. So ignition is not a breakdown problem. The
3 MV/m N₂ breakdown field this cavity is 13× short of (`../resonance/KNOWN.md`
§ FIELD MEASURED) **does not have to be reached.** The bore has to be made
conductive by chemistry and the cavity takes over.

Temperature to reach σ = 0.0028, at 1.1e-5 mole fraction seed:

| species | T for σ = 0.0028 |
|---|---|
| N₂, unseeded | **3,673 K** |
| **K seed** | **1,588 K** |
| Rb seed | 1,530 K |
| Cs seed | **1,431 K** |

**Potassium drops the bar by ~2,100 K.**

⚠️ **Robustness:** `MOMENTUM_CROSS_SECTION_M2` in `physics.py` is flagged
order-of-magnitude-only. A 10× error moves these thresholds 150–200 K — the Saha
exponential dominates, so the conclusion does not turn on it.

## Anion and cation choices — DERIVED / ASSUMED

- **Acetate is a good anion; chloride would be a bad one.** Cl is
  electronegative and attaches electrons, working against the discharge; plus
  HCl attacks quartz. Acetate is absurdly soluble (~270 g/100 mL K-acetate),
  cheap, food-grade. Its cost is carbon — C emission lines, and soot if the
  plasma runs cold — **which in this mechanism is the product, not the cost.**
- **Caesium is unnecessary — STATED, user.** Cs acetate decomposes by the same
  ketonic route to Cs₂CO₃ + acetone, so it buys ~160 K of ionisation threshold
  and nothing structural. 🔑 **The compound is doing the work, not the cation's
  ionisation energy.**
- ⚠️ **K is the analyte.** This is a soil instrument; K is the K in NPK. At
  0.5 M the starter fluid is ~19,500 ppm against soil-extract K of tens to
  hundreds of ppm, with slow alkali memory on injector and torch.
  🔴 **~~This is the strongest objection to the whole route and it is not
  resolved~~ — WITHDRAWN AS FRAMED, 2026-09-07.** User: *"The starter fluid has
  to be flushed for that reason (but ANY starter fluid would have to be
  flushed)."* **The flush is the mechanism that answers it, and it is already in
  the design** — see § THE FLUSH DOES THREE JOBS. Low molarity is a secondary
  lever, not the resolution.
  ⚠️ **What actually remains is second-order:** the flush's efficacy is
  unverified, and *where the cation is also an analyte* an incomplete flush
  biases a reported element rather than nothing. That is a **failure mode**
  difference, not a requirement difference.

## 🔴 VOID — do not quote the 0.01 M optimum

A ramp analysis against the measured power map produced a "seed shields the
field" valley and an optimum near **0.01 M**. 🔴 **It was computed on an
equilibrium-Saha release model — all K available as free gas-phase atoms at any
temperature.** The user's chemistry says K is locked in carbonate below ~1,200 K
and is liberated at a rate set by carbothermal reduction. **K availability is
chemistry-gated, not Saha-gated.** The direction (less is more) may survive; the
number must not be quoted. The 1,588 K coupling threshold does survive, because
reduction starts below it.

## Prior art — SEARCHED 2026-09-07, and both legs are covered

- **Susceptor ignition of microwave plasma torches is standard practice** —
  a pointed metal rod that absorbs RF, heats, and emits electrons thermionically.
  Graphite susceptors for microwave ignition are published.
  ([How to Ignite an Atmospheric Pressure Microwave Plasma Torch without Any Additional Igniters](https://www.researchgate.net/publication/367430627_How_to_Ignite_an_Atmospheric_Pressure_Microwave_Plasma_Torch_without_Any_Additional_Igniters))
- **Alkali seeding for plasma conductivity is old and well modelled**, including
  a direct K/Cs treatment by the same Saha route used above.
  ([Estimated electric conductivities of thermal plasma with potassium or cesium seeding](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11145353/))
- **The grape paper is the demonstration of the two combined in an aqueous
  system.**
- Also: [MIP torch with tantalum injector probe, US 5051557](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/5051557) ·
  [Self-Perpetuating Carbon Foam Microwave Plasma Conversion of Hydrocarbon Wastes](https://pubs.acs.org/doi/abs/10.1021/acs.est.0c06977)

🔑 **What was NOT found published:** the specific integration — a **consumable
liquid starter fluid delivered through the instrument's existing nebuliser**,
chosen so its decomposition products supply both susceptor and seed, then
flushed before the sample. ⚠️ **That is a systems claim, not a physics claim.**
It is weaker than "the mechanism is novel", and `DISCLOSURE.md` should say so if
this is ever published.

## The references — READ, and one of them inverts an earlier reading

### Zhang et al., *Processes* **12**, 2505 (2024) — `refs/Metal Acetate-Enhanced Microwave Pyrolysis...pdf`

Table 1, carbon disorder `I_D/I_G` after microwave pyrolysis:

| waste textile | 2.6Na | **2.6K** | 1.0Ni | 2.6Ni | 3.5Ni | 6.1Ni |
|---|---|---|---|---|---|---|
| 0.7198 | 0.6498 | **0.8226** | 0.7862 | 0.7296 | 0.6970 | 0.6293 |

🔑 **Potassium gives the highest `I_D/I_G` of anything tested** — more disordered
carbon than nickel, well above the unimpregnated control. *"Alkali metals (Na and
K) tend to favor the production of char."* Their reason for rejecting K is
*"not the optimal metal salt because of its very low hydrogen content (1.0%)"* —
**K was rejected for being good at exactly the thing we want.** For syngas,
disordered char is the by-product to minimise; for a susceptor it is the product.
Sodium is the mirror image (lowest `I_D/I_G`, 0.6498, *below* the control), which
shows the K result is not a generic alkali effect.

Also: they ran a separate experiment at **285 °C, below the textile's 300 °C
pyrolysis onset**, to isolate the salt's own decomposition — the acetate had
already converted while the substrate was intact. **The acetate decomposes well
below where the substrate does**, which is closer to our case than their 500 °C
runs.

⚠️ **What it does not settle:** they ran the sample in a **SiC boat with
significant microwave absorbing ability** — a deliberate external susceptor. The
paper never demonstrates acetate-derived carbon bootstrapping **from cold**.
⚠️ And every `I_D/I_G` is for acetate impregnated into a *carbonaceous textile*,
so char has two sources and the paper cannot separate the acetate's own carbon.
In a torch the acetate would be the sole carbon source. **The ranking is
suggestive, not transferable.**

### PNAS grape paper — `refs/Linking plasma formation in grapes...pdf`

**It is potassium-seeded microwave plasma ignition.** Fig. 1D emission spectrum
is dominated by **K ~766 nm** and **Na 589 nm**. *"Potassium and sodium species,
abundant in the grape skin, are field-ionized by a strong concentration of
electric field near the point of contact... forming a microwave-heated plasma
that grows and becomes independent from the dimer."* Not grape-specific —
skinless hydrogel beads in **NaCl solution** do the same (Fig. 1C).

Field enhancement, 16 mm beads (Fig. 3; vacuum reference 4.43e-3 nJ/m³):

| separation | energy density | ratio | **field enhancement** |
|---|---|---|---|
| 20 mm | 0.130 | 29× | 5.4× |
| 4 mm | 0.147 | 33× | 5.8× |
| **0.5 mm** | **1.66** | **375×** | **19.4×** |

Water at 2.45 GHz, 20 °C: **ε̃ = 79 + 10i**, n = 8.9, k = 0.56, penetration
≈1.5 cm. Absorption **broadens** the Mie resonances, so hotspots persist across a
wide size range rather than at sharp resonances.

⚠️ **It does not transfer to a nebulised aerosol.** Droplets are 1–10 µm against
an internal wavelength of ~13.75 mm — deep Rayleigh, no resonance.

🔑 **Worth keeping even though the user bypassed this leg: 19× field enhancement
from a 0.5 mm dielectric gap.** Our bore is 150× short in field at 1 kW. **A
deliberate dielectric feature in the torch is a third ignition route entirely,
independent of chemistry** — and it is EM, so this programme could measure it.

### The 17 mm coincidence — NOTED, NOT load-bearing

Water's internal wavelength of 13.75 mm puts Mie modes at sphere diameters
6.56 / 10.94 / **15.32** / **19.69** / 24.07 mm (l = 1…5). A standard Fassel bore
is **17.0 mm**, between l = 3 and l = 4, in the band PNAS worked in (16 mm beads,
19–20 mm simulated). ⚠️ **The user bypassed the Mie leg, so this is an
interesting coincidence and nothing more.** A bore is also not a sphere, and the
19× came specifically from a *dimer gap*.

## What the bore diameter question becomes, on the carbon route

Not resonance but **power absorption against thermal quenching**: the deposit
must sit where the field is, absorb enough to reach carbothermal reduction
temperature, and do so faster than the gas carries the heat away. Bigger bore =
longer residence, less quenching; smaller bore = higher field, colder faster
flow. ✅ **And the quench flow is the injector's ~1 slm, not the shell's 10** —
see `../torch-geometry/README.md` § THE FLOW SPLIT. The deposit sits in a far
gentler environment than a flat 12 slm implies.

## The one thing that is EM, and is cheaply measurable

🔑 **Amorphous carbon at 2.45 GHz is a volumetric absorber, not a mirror.** Skin
depth is **322 µm at σ = 1e3 S/m down to 32 µm at 1e5** — and even at σ = 10 S/m
it is 3.2 mm. Any sprayed film is sub-micron to microns. **Robust across five
orders of magnitude of σ.** This kills the objection that a dilute aqueous
aerosol is transparent at 2.45 GHz and needs external heat: **the starter fluid
deposits its own susceptor. No glow plug required.**

➡️ **The proposed rig, and it is cheap:** the driven rig already takes a
prescribed (ε, σ) inclusion in the bore — that is what the plasma annulus is.
Give it **amorphous carbon's** values instead of a plasma's, run the driven solve
with the surface power balance calibrated to 97 %, and read **the watts landing
in the deposit, per bore diameter**. That turns "will it self-heat" into a
number. ⚠️ It answers absorption only; it does not answer temperature rise, which
needs a thermal tool Palace does not have (same gap as coupler thermals).

## 🔴 What is NOT established

- **Cold-start bootstrap in OUR torch.** Zhang used an external SiC susceptor.
  The grape route is cm-scale aqueous and was bypassed. Match-in-a-jar is the
  user's cold-start evidence and it is a domestic oven, not this cavity.
  ➡️ **The cheapest settling experiment is not a simulation:** dry a film of
  potassium acetate, run it cold in a domestic 2.45 GHz oven, see whether it
  reaches incandescence unaided.
- **Where the carbon lands** — injector tip, torch wall, or bore. This sets
  whether the susceptor is in the field maximum and whether it is reproducible
  run to run. **Ignition reliability lives here.**
- **Whether it gasifies.** Pure N₂ has no oxygen, but the DI flush does. If the
  flush both clears K and burns off the carbon the sequence closes; if not, the
  deposit accumulates across runs.
- **Molarity.** See § VOID. Not answerable without a release-rate model.
- **Flush TIME COST and criterion** — not efficacy, which is closed-loop on the
  K line (§ THE FLUSH IS CLOSED-LOOP). What is open is how many noise floors the
  criterion sits at, how alkali memory on injector and torch settles as it is
  approached, and what that costs per ignition. **A control question.**
- **Flush timing.** Constrained in principle (before nitrogen can hold it, after
  the valley) but the valley itself came from the void model.

## Rules that bite here

- **§7ac** — never mix a verified analysis with an unverified suggestion. The
  power map and the skin-depth figures are DERIVED from measurement; the
  chemistry is STATED and the chain is ASSUMED.
- **§7bs / prior-art rule** — the novelty claim above was searched, not assumed,
  and it came back *weaker* than hoped. Record it that way.
- 🔑 **"Absence of a grep hit is not absence of the thing."** The first reading
  of Zhang 2024 was done by keyword and concluded the paper lacked the key
  measurement. It contained it, ranked and quantitative, under `I_D/I_G`,
  "char" and "structural disorder". **Read the paper.** Worth a CONVENTIONS §7
  entry if it is not already there.
