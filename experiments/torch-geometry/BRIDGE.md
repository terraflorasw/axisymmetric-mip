# BRIDGE — Palace to OpenFOAM, one way

**Opened 2026-09-07**, on the user's proposal *"I think we can model it, by
bridging Palace and OpenFOAM."* Assessment and the reasons for one-way are in
`README.md` § PROPOSED. This file is the BUILD SCOPE.

🔴 **NOTHING IS MEASURED HERE YET.** Every line is **STATED** · **DERIVED** ·
**ASSUMED** · **TO DECIDE**.

## What it is, and what it is deliberately NOT

| | |
|---|---|
| ✅ **IS** | Palace computes the EM power deposition. OpenFOAM takes it as a **fixed heat source** and solves flow + conjugate heat transfer through the sapphire wall |
| 🔴 **IS NOT** | a two-way coupled plasma model. The `T -> n_e` step needs non-LTE and **`README.md` § ALSO WITHDRAWN already voided one calculation for using LTE Saha.** Do not close the loop |
| 🔑 **why that is legitimate** | `n_e` is anchored EXTERNALLY (MICAP 5220–5270 K), so the EM solve does not need CFD to tell it the conductivity — it is given |

## The four questions it exists to answer

1. **Wall temperature vs sheath flow** — is ~10 slm enough, and how much does
   sapphire's ~700 K headroom over quartz actually buy?
2. **Injector tip temperature vs intermediate flow** — the ~1 slm standoff
   stream, which has never been analysed at all.
3. **The analyte path and its residence time** — replacing the withdrawn table
   (`../resonance/KNOWN.md` scope stamp) with a number that is about the analyte.
4. **The ignition transient** — thermal shock in sapphire, whose expansion is
   ~10x quartz's. This is the case that argues AGAINST sapphire.

## The interface — and it is already calibrated, which is the unusual part

**Palace emits volumetric power deposition.** For the Drude plasma the
time-averaged dissipation per unit volume is

    q(r,z) = 0.5 * omega * eps_0 * eps'' * |E|^2

🔑 **THE HANDOFF IS SELF-CHECKING, AND THAT IS WHY THIS IS WORTH BUILDING.**
The volume integral of `q` over the plasma region must agree with the plasma's
share of absorbed power — and `../resonance/KNOWN.md` § THE POWER BALANCE closes
wall + port + loop to **97 %** against `P_inc(1-|S11|^2)`, with `P_inc` = 1 W
established. **So the bridge's input can be validated against a measurement the
programme already trusts, before any CFD is believed.**
➡️ **GATE: if the integral of `q` does not reconcile with the power balance,
stop. Do not run CFD on an unreconciled source.**

**Transport, TO DECIDE:** sample `q` onto a structured `(r,z)` table rather than
doing tet-to-polyhedron interpolation. The plasma is modelled as an axisymmetric
annulus, so `(r,z)` is its natural coordinate, and a table sidesteps mesh mapping
entirely. ⚠️ Costs an interpolation error that must be bounded, not assumed.

## The OpenFOAM side

| | |
|---|---|
| solver | `chtMultiRegionFoam` — ✅ **present and verified in parallel**, see `../resonance/DEPLOY.md` |
| regions | gas (fluid) · sapphire tube (solid) · injector (solid) · outer environment |
| inlets | **three**, per `README.md` § THE FLOW SPLIT: sheath 10 · intermediate 1 · injector 1 slm |
| source | `q(r,z)` into the energy equation via `fvOptions` |
| steady first | `chtMultiRegionSimpleFoam` for Q1–Q3; transient only for Q4 |

🔴 **THE BIGGEST PHYSICS RISK IS THE GAS PROPERTIES, AND IT IS THE CFD TWIN OF
THE LTE PROBLEM.** Nitrogen's thermal conductivity has a large **dissociation
peak near 7,000 K**, and it is precisely that peak which drives wall heat flux —
the quantity every one of the four questions depends on. **Standard OpenFOAM
thermophysical models (`sutherland`, `janaf`) do not represent it.** Tabulated
high-temperature N2 properties are required.
➡️ **This is a NAMED PREREQUISITE, not a detail.** A run using Sutherland
transport would produce confident wall temperatures that are wrong in the
direction that matters, and nothing in the output would say so.

## 🔴 PHASE 0 IS TWO ANCHORS, NOT ONE — corrected 2026-09-07 before starting

⚠️ **MY FIRST SCOPE SAID "reproduce a published case with measured profiles".
That is not what E0 is.** `CLAUDE.md`: E0 is *"**Not 'verify the instrument.'**
Put a number on the disagreement between this solver and the **closed form**, on
the one case where the closed form is complete."* Those are different jobs and
conflating them would let model error and solver error hide in each other.

| | asks | anchored to | when |
|---|---|---|---|
| **E0-CFD** | how far is OpenFOAM from an EXACT answer, on the mechanism the bridge uses? | closed form / conservation | **now** |
| **model anchor** | is this model of THIS torch right — turbulence, properties, radiation? | published case with MEASURED T | later, and it is a bigger question |

🔑 **E0-CFD FIRST, AND IT IS CHEAP.** The bridge's correctness rests on one
mechanism: **a volumetric source term putting the right amount of energy into the
fluid.** That has an exact test — with an adiabatic wall, every watt of source
must appear as enthalpy rise:

    integral(q''' dV)  ==  mdot * cp * (T_out - T_in)

**No correlation, no measurement, no tuning.** It is the CFD twin of the power
balance that validates the Palace side, and it fails loudly if the source path,
the units, or the property model is wrong.

Second exact check, once a solid region is added: **radial conduction through the
tube wall** against the analytic logarithmic profile.

## ✅✅ PHASE 0a RESULT — the source path closes to 0.023 % (2026-09-07)

**Case:** `cfd/e0a_source/` — axisymmetric 5° wedge, R = 8.5 mm, L = 100 mm,
laminar, CONSTANT properties, **adiabatic wall**, uniform
`q''' = 5.84e5 W/m3` via `scalarSemiImplicitSource` on `h`, `volumeMode
specific`. `rhoSimpleFoam`, converged in **247 iterations**.
**Anchor: conservation of energy. No correlation, no measurement, no tuning.**

| quantity | value |
|---|---:|
| source, `q'''*V` | **0.184223472 W** |
| gas, `mdot*cp*(T_out-T_in)` | **0.184180506 W** |
| **closure** | **99.977 %  (−0.0233 %)** |
| `mdot` vs analytic `rho*U*A` | **+8.2 ppm** |
| mesh volume vs analytic wedge | **+2.65 ppm** |

✅ **THE VOLUMETRIC SOURCE PATH IS CORRECT**, including the wedge volume
weighting — which was the specific failure `volumeMode specific` was chosen to
expose. `mdot` matching to 8 ppm checks the inlet area independently.

🔑 **THE INSTRUMENT FLOOR: a difference must clear ~0.05 % to be physics rather
than discretisation.** That is this bridge's equivalent of E0's *"a difference
must clear ~0.1 MHz to be the model rather than the solver."*

### 🔑 AND IT FOUND A REAL BIAS: A WEDGE IS A TRIANGLE, NOT A SECTOR

| | volume, this case |
|---|---:|
| circular sector, 5° | 3.1525010e-07 m³ |
| **triangular wedge, 5°** | **3.1545031e-07 m³** |
| blockMesh | 3.1545115e-07 m³ |

**blockMesh is exact to the triangle (2.65 ppm). The +0.0638 % is GEOMETRIC** —
a wedge's radial faces are flat chords, so it circumscribes the sector it
represents.

🔴 **THIS MATTERS FOR THE BRIDGE AND IS EASY TO MISS.** Palace's `q(r,z)` is
defined on **true axisymmetric geometry**. Fed as W/m³ into a wedge, the same
`q'''` is integrated over 0.0638 % more volume, so **the torch case will
over-deliver power by 0.0638 % unless corrected.** ➡️ **Either scale `q'''` by
`sector/triangle = 0.999362`, or state the bias with every result.** It is
small — but it is 2.7× the closure error above, so it would be the DOMINANT
systematic if left unstated.

### ⚠️ OPERATIONAL — `residualControl` on `U` can never converge in a wedge

**Cost a wasted run.** `Uz` is the azimuthal component and is slaved by the wedge
BCs; its initial residual sticks around **3e-2** forever while `Ux` and `h` reach
**1e-10**. With `U` in `residualControl` the run cannot converge, so it never
writes, and **a converged solution looks exactly like a slow one** (§1: do not
infer state from a proxy). ✅ Gate on `p` and `h`. Also cap `GAMG maxIter` — at
machine-noise residuals it burned 1000 iterations per step.

### ✅ AND IT REPRODUCES BIT-FOR-BIT ON A SECOND MACHINE (2026-09-07)

OpenFOAM v2412 installed locally (`~/envs/cfd`, same conda-forge package, same
Pstream patch — the bug is in the package, not the machine). The 0a case rerun
there against the instance's numbers:

| | instance (32-core EC2) | laptop (8-core) |
|---|---|---|
| iterations to converge | 247 | **247** |
| `mdot` | 3.5428715246e-06 | **3.5428715246e-06** |
| `T_out` bulk | 3.4998675199e+02 | **3.4998675199e+02** |

🔑 **IDENTICAL TO ELEVEN DIGITS**, so §4b — *"a quantity measured in another epoch
was measured on another machine"* — **is answered by measurement here rather than
assumed away.** E0-scale CFD can move to the laptop with no cross-machine caveat.

➡️ **THE SPLIT THAT FOLLOWS:** develop and run E0/small cases **locally** (the
edit-run loop is seconds, and five successive dict errors each cost a sync + ssh
round trip remotely); keep the instance for anything large. 🔴 **Palace does not
move** — its env and all 513 solved cases are on the volume.
⚠️ The laptop has ~3 GB RAM free of 31 GB. It is a DEVELOPMENT machine for this,
not a fallback for the torch case.

### ⚠️ WHAT 0a DOES NOT ESTABLISH

- **Nothing about heat leaving through a wall** — the wall is adiabatic by
  design, so this is a pure source-and-carry check. That is **0b**.
- **Nothing about real gas properties.** Constant `cp`, `mu`, `Pr` on purpose.
  The N₂ dissociation peak named above is untouched and remains the phase-2 risk.
- **Nothing about turbulence.** Laminar, `Re` ≈ 1,100 at these conditions.
- **Nothing about the torch.** This is an instrument bound, not a model.

## ✅✅ PHASE 0b RESULT — conservation AND analytic conduction both pass (2026-09-07)

**Case:** `cfd/e0b_wall/` — 0a's wedge and `q'''`, plus a **sapphire solid
region** (r = 8.5→10.5 mm, kappa 25 W/m·K constant), `chtMultiRegionSimpleFoam`,
converged. Outer wall fixed at 300 K is the sink; **solid ends adiabatic so heat
must travel RADIALLY**, which is what makes the analytic form exact.

### ✅ CHECK 1 — global conservation, now including a wall loss

| term | W |
|---|---:|
| source `q'''*V` | 0.184223472 |
| gas `mdot*cp*dT` | 0.137371064 |
| wall `Q_outerWall` | 0.046811112 |
| **gas + wall** | **0.184182176** |
| **closure** | **99.978 %  (−0.0224 %)** |

🔑 **THE WALL CARRIES 25.4 % OF THE SOURCE**, so this is a real test of the
coupled path, not a rounding check — and it closes to the same **0.02 %** as 0a,
where the wall was adiabatic. **The fluid-solid interface conserves energy.**

### ✅ CHECK 2 — analytic radial conduction

`Q = 2*tan(2.5deg)*k*L*(T_i - T_o)/ln(R_o/R_i)` — the **triangular-wedge** form,
per 0a. `C` = 1.033106 W/K.

| | K |
|---|---:|
| predicted `T_interface` | 300.0453110 |
| **measured** `T_interface` | **300.0453161** |
| difference | **+5.06e-06 K → +0.0112 %** |

⚠️ **HONEST CAVEAT: the signal is small.** Sapphire conducts well and the wall is
thin, so at 0.18 W the drop across it is only **0.045 K** — the wall is nearly
isothermal. The *relative* agreement is excellent, but this validates the
conduction operator at low ΔT with **constant kappa**. 🔴 **Real sapphire kappa
falls steeply with temperature**, so it does NOT license large-ΔT conduction —
same phase-2 gap as the N₂ dissociation peak.
⚠️ **And do not scale this to the torch.** Different geometry, different power,
360° not 5°.

### ✅ WHAT PHASE 0 NOW ESTABLISHES, TOGETHER

| | |
|---|---|
| volumetric source → enthalpy | **0.023 %** (0a) |
| source → enthalpy + wall loss | **0.022 %** (0b) |
| conduction vs closed form | **0.011 %** (0b) |
| cross-machine reproduction | **exact to 11 digits** |

🔑 **INSTRUMENT FLOOR: ~0.05 %.** A CFD difference must clear that to be physics
rather than discretisation — the bridge's equivalent of E0's 0.1 MHz.

### 🔴 AUTHORING LESSON — five fatal errors, all self-inflicted

`chtMultiRegionSimpleFoam` refused to start five times: missing top-level
`system/fvSchemes`, `system/fvSolution`, `constant/regionProperties`, wrong
thermo type (`hePsiThermo` carried over from `rhoSimpleFoam`; it needs
**`heRhoThermo`**), and missing `0/solid/p`.

🔑 **CAUSE: I authored the case from scratch when a WORKING one was on the
volume.** `multiRegionHeater` had already been run and verified here; diffing
against it would have caught all five at once. That is §7.7 — **search prior art
before deriving** — and §7cg — *a dependency's config schema is a fact to LOOK
UP, not recall*.
✅ **Mitigating, and it is why this cost turns rather than results:** every one
failed at STARTUP with the missing item named. **None produced a plausible wrong
number.** ➡️ **For the torch case, start from a running multi-region case and
change it**, rather than assembling dicts from memory.

## 🔎 0c — CANDIDATE ANCHOR ASSESSED FROM THE PAPER ITSELF (2026-09-07)

**Punjabi et al., *Processes* 7 (2019) 133** — `refs/processes-07-00133-v3.pdf`,
supplied by the user. ✅ **READ, not searched** — and reading changed the verdict
twice, which is the §"read the paper" lesson again: the ABSTRACT advertises only
**impedance** validation, but §5.2.1 does carry measured temperature profiles.

### What it actually offers

| | |
|---|---|
| gas / pressure | **argon, atmospheric** |
| power (T-profile case) | **7.5 kW** (10 lpm) and **10 kW** (25 lpm) — not the 50 kW headline |
| frequency | **3 MHz** |
| geometry | two concentric quartz tubes, **inner ID 60 mm, outer OD 80 mm** |
| flows | plasma gas 3 lpm; **sheath 10 AND 25 lpm — a FLOW SWEEP** |
| measurement | radial + axial T profiles, axial station **192 mm** (coil centreline) |
| reported agreement | ±8 % (10 lpm), ~10 % (25 lpm) |
| **experimental error** | 🔴 **20–25 %, stated by the authors** |
| model | Fluent 14, vector potential via UDS, **LTE**, optically thin |

### 🔴 WHY IT CANNOT ANCHOR QUESTION 1, AND THIS IS DECISIVE

> *"Cooling water flows between the quartz tubes... the temperature of quartz
> tube facing water is less than about 330 K. The water flow rate is adjusted in
> such a manner that its temperature does not exceed 330 K."*

**Its wall is held near-isothermal BY WATER.** Our Q1 asks what the wall
temperature *becomes* when a **gas sheath** cools it — the wall temperature is
the unknown. A case that pins the wall with water cannot validate that path.
🔑 **The one number it does give — *"temperature at the quartz wall facing the
plasma is less than about 800 K"* — is mildly corroborative of Engelhard's 730 K
on a GAS-cooled Fassel torch, but it is an output of a different boundary
condition, not a test of ours.**

### ⚠️ AND REPRODUCING IT NEEDS AN ASSUMPTION OUR BRIDGE DOES NOT MAKE

They solve the **coil** EM (vector potential) coupled to the flow. Our bridge
takes `q` from **Palace**, which models a 2.45 GHz cavity, not a 3 MHz coil. To
reproduce this case we would have to **assume a radial deposition profile** —
introducing a fitted shape, so the exercise would test *CFD + an assumed
deposition* rather than the CFD alone. ⚠️ **That is exactly the confound 0a/0b
were designed to avoid.**

### ✅ RESOLVED 2026-09-08 — THE Q1 ANCHOR ARRIVED, so this one is used NARROWLY

**Engelhard et al. 2007 is now in `refs/` and READ.** It is the gas-cooled Fassel
wall-temperature measurement this section said was missing, so the split is now
clean rather than a compromise:

| | anchor | what it licenses |
|---|---|---|
| **Q1 wall T vs sheath flow** | **Engelhard 2007** — gas-cooled Fassel, 12/1/1 L/min at 1400 W, wall **725 ± 44 K**, ±6 % | the wall path |
| **Q3 gas-phase field vs sheath flow** | Punjabi 2019 — 10 vs 25 lpm sweep, ±20–25 % | the gas path only |
| **Q4 ignition transient** | 🔴 **neither.** Both are steady state | — |

🔑 **Engelhard's conventional torch is 12 outer / 1 auxiliary / 1 central L/min at
1400 W against our 10 / 1 / 1 at ~1000 W** — the closest published match to this
machine in the record, and its wall is cooled by the outer plasma gas, which is
the architecture Q1 is about.

### ➡️ RECOMMENDATION — adopt Punjabi NARROWLY, and do not let it license Q1

- ✅ **Use it for the GAS-PHASE thermal field and its response to sheath flow**,
  target the **10 lpm / 7.5 kW** case. That is genuinely relevant to **Q3**
  (residence), which is about the gas, not the wall.
- ✅ **Q1 now has its own anchor** — Engelhard 2007, in `refs/` and read. Do not
  quote Punjabi for wall temperature.
- 🔴 **Q4 (ignition transient) still has NO anchor.** Both papers are steady
  state, and thermal shock is a transient. **Do not let phase 0c imply otherwise.**
- ⚠️ **State the bar honestly:** with 20–25 % experimental error, agreement here
  is a weak license. It is ~400× looser than the 0.05 % instrument floor 0a/0b
  established, so **it bounds the MODEL, not the solver** — which is the split
  § PHASE 0 IS TWO ANCHORS already draws.

## 🔴 THE MODEL ANCHOR — still required before any TORCH number is quoted

`CLAUDE.md`: **name the external anchor before starting work**, and E0 exists
because an uncharacterised solver invalidated six rigs.

⚠️ **The tutorial that was run is a CODE check, not a physics anchor.** It proves
`chtMultiRegionFoam` solves and conjugates; it says nothing about whether this
model of this torch is right.

**TO DECIDE — the anchor case.** It must have MEASURED temperature profiles.
⚠️ Most published, well-validated torch models are **argon ICP**, and this is a
nitrogen MIP — the same known-but-wrong-gas compromise `../spectroscopy/` item 6
already records for the Fassel geometry. **Choosing the anchor is the first task,
and the choice must be written down with its gas.**

## Build order

| phase | | done when |
|---|---|---|
| ✅ **0a** | **E0-CFD**: volumetric source into a duct, adiabatic wall | ✅ **DONE 2026-09-07 — closes to 0.023 %.** See § PHASE 0a RESULT |
| ✅ **0b** | E0-CFD: add the solid wall | ✅ **DONE 2026-09-07** — conservation 0.022 %, conduction 0.011 % |
| 🔎 **0c** | model anchor **CHOSEN 2026-09-08**: Engelhard 2007 for the wall (Q1), Punjabi 2019 for the gas (Q3). **Both ARGON — stated, per the rule.** Q4 has none | reproduce Engelhard's 725 ± 44 K wall condition |
| **1** | `q(r,z)` export from Palace + reconciliation gate | integral agrees with the power balance |
| **2** | torch case: three streams, sapphire wall, Fassel dimensions | converges; wall T responds to sheath flow |
| **3** | answer Q1–Q4 | each in a document, per §8b |

## What it will NOT be able to say

- **`n_e`, or anything requiring it to be solved rather than given.**
- **Anything spectroscopic** — emission, background, LOD. Different instrument.
- **Whether the plasma sustains at 10–12 slm** (`README.md` open item 3). That is
  a discharge-physics question; a fixed heat source cannot answer it.
- **Two-way anything.** See the top of this file.

## Rules that bite here

- **One rig, one solver** — do not parameterise "EM or CFD" inside one script.
- **§7cb** — anything long-running gets `ops/watch.sh`, not a hand-rolled loop.
- **§8b** — a rig is done when the conclusion is in a document, not when it exits 0.
- 🔑 **Name what the bridge cannot do**, the way `INSTRUMENT.md` does for Palace.
