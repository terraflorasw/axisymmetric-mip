# Defensive publication — microwave-induced plasma cavity, mode filter, coupler and starter fluid

**Purpose.** This document places the designs described below into the public
domain as prior art. It is published deliberately, without restriction on
reading or use beyond the repository's licences. Terraflora SW asserts no patent
rights over anything described here, and publishes it so that no one else can
validly claim them either. The publication date is this file's commit date; the
supporting technical record predates it and is in this repository's git history.

**Licences.** Code AGPL-3.0 (`LICENSE-CODE`), hardware CERN-OHL-S-2.0
(`LICENSE-HARDWARE`). Both strongly reciprocal.

---

## Why this exists

We are building a microwave-induced plasma instrument for **soil testing**. In
developing it we found that several general-purpose approaches to exciting and
coupling to such a plasma are covered by existing patents, and are therefore not
available to us. We consequently developed the alternatives described here.

We are publishing them rather than seeking protection for them. The intent is
that these designs remain available to anyone — including anyone else who finds
the general-purpose approaches unavailable for the same reason.

Nothing here is an assessment of any other party's rights, and nothing here is
offered as a substitute for a freedom-to-operate analysis.

---

## Search terms

Included so that anyone searching this field encounters this disclosure. These
are the terms under which the subject matter would reasonably be sought:

microwave induced plasma · MIP · microwave plasma cavity · microwave induced
plasma optical emission spectrometry · MIP-OES · nitrogen plasma torch ·
atmospheric pressure microwave plasma · 2.45 GHz resonant cavity · magnetron
driven plasma source

TE011 cavity · TE011 mode · cylindrical resonant cavity · right circular
cylindrical cavity · axisymmetric cavity · high-Q microwave cavity ·
TE011 TM111 degeneracy · degenerate mode suppression · mode filter ·
mode purity · spurious mode suppression · Bessel function root degeneracy ·
chi prime 01 · chi 11 · J0 prime J1 root coincidence

annular groove · circumferential groove · wall slot · circumferential slot ·
wall current interruption · axial wall current · azimuthal wall current ·
groove mode filter · slot-loaded cavity · degeneracy lifting groove

coupling loop · magnetic coupling loop · loop coupler · azimuthal coupling loop ·
wall-following loop · arc coupler · equatorial loop · loop standoff ·
external Q · critical coupling · coupling coefficient beta · VSWR ·
coaxial feedthrough · coaxial feed hole · coax entry · wave port · lumped port

loop standoff · wall gap · conductor centreline · image loading · loop
self-inductance near a conducting wall · E-field access · J0 J1 field profile ·
magnetic versus electric coupling · coupler placement within the mode

power balance closure · Poynting flux boundary integral · surface loss
integration · driven solve verification · S-parameter validation · port
normalisation · incident power convention · lumped port face planarity ·
non-planar port face · annular sector port · unloaded Q from stored energy ·
port-independent Q · broadband reflection offset · spurious absorption ·
discretisation error indicator

striker ignition · seed ignition · igniter electrode · plasma ignition threshold ·
breakdown field nitrogen · cavity-only ignition

starter fluid · consumable igniter · liquid igniter · ignition through the
nebuliser · sample introduction path ignition · hardware-free plasma ignition ·
alkali seeding · easily ionisable element · potassium seeding · caesium seeding ·
alkali carboxylate · potassium acetate · metal acetate · ketonic decomposition ·
alkali carbonate · carbothermal reduction · in-situ susceptor · sacrificial
susceptor · amorphous carbon susceptor · carbon microwave absorber · skin depth
in amorphous carbon · volumetric microwave absorption · seed shielding ·
overdense seed · deionised water flush · seed washout · analyte carryover

soil analysis · regenerative agriculture · soil nutrient spectroscopy ·
elemental analysis plasma source

---

## Disclosure 1 — Annular groove as a TE011/TM111 mode filter

### The problem

In a right circular cylindrical cavity, **TE011 and TM111 are exactly degenerate at
every aspect ratio**. This follows from an identity between Bessel roots — the
first root of J0' equals the first root of J1 — so the two modes share a
resonant frequency for *any* diameter-to-length ratio. It is not a numerical
coincidence and cannot be removed by choosing the aspect ratio.

The consequence is practical, not academic. Any coupling structure that excites
TE011 also excites TM111, and the cavity supports a **hybrid of the two**. A
cavity believed to be operating in TE011 may be operating in something else
entirely, and any Q, efficiency or field distribution attributed to TE011 in that
state is attributed to the wrong field.

### The design

Cut a **circumferential (annular) groove into the cylindrical wall**, at the
cavity mid-plane, dimensioned as a width and a depth.

### Why it works

TE011 and TM111 differ in the direction of the wall current they require. TM111
needs **axial** wall current; TE011's wall current is **azimuthal**. A
circumferential slot lies across the axial current and along the azimuthal one,
so it obstructs TM111 while leaving TE011 substantially undisturbed. The groove
therefore shifts TM111 in frequency relative to TE011 and lifts the degeneracy.

Once separated, a coupling loop has nothing to mix TE011 with, and measured mode
purity rises from strongly hybridised to essentially pure TE011.

### Design constraints

  - **Depth is a real design variable** and its effect is *not* a simple power
    law; it must be characterised, not extrapolated.
  - **A depth near a quarter wavelength must be avoided**, because the groove is
    then resonant in its own right. Compute as `lambda/4 = c / (4 f)` at the
    operating frequency.

---

## Disclosure 2 — Azimuthal wall-following loop coupler with coaxial feedthrough

### The design

A coupling loop formed as a **circular arc concentric with the cavity wall**,
lying in the cavity mid-plane at a small standoff from the wall, closed to the
wall by **two radial legs**. This differs from the conventional radial loop,
which projects inward from the wall and links a different field component.

Lying along the wall at the equator, the arc sits where TE011's tangential
magnetic field is large, and its conductor runs *along* the wall current rather
than across it.

### Parameterisation — the part most easily got wrong

Specify the loop by **standoff and arc length, independently**:

  - **Standoff is the wall gap** — the height of the stud the conductor sits on,
    with the conductor growing *away* from the wall. The gap is then invariant
    under changes of conductor cross-section. Specifying the conductor
    *centreline* height instead makes the wall gap depend on conductor
    thickness, so two conductors of different thickness at the same nominal
    height sit at different distances from the wall and are not comparable.
  - **Arc length, not arc angle.** The angle subtended depends on the standoff,
    so a fixed angle at different standoffs is a different conductor length.

### Standoff is a design variable, not a mounting detail

The standoff sets a **trade between the two field components**, and the trade is
one-sided at the wall:

  - TE011's azimuthal electric field goes as `J1(chi'_01 r/a)`. Because
    `chi'_01` is itself a zero of `J1`, **E_phi is identically zero at the
    cavity wall** — a conductor placed hard against the wall sits in
    essentially no electric field.
  - TE011's axial magnetic field goes as `J0(chi'_01 r/a)`, which is **not**
    zero at the wall. `J0(chi'_01) ~= -0.403`, near its extremum.

So reducing the standoff maximises the magnetic flux the loop links while
driving the local electric field to zero, and increasing it recovers electric
field at modest cost in magnetic. Over the first ~12 % of the radius the
electric field rises by several times while `|J0|` falls by roughly a tenth —
**the exchange rate strongly favours moving off the wall**, and a design that
treats the standoff as a mechanical clearance rather than an electrical
parameter gives that up by default.

⚠️ A wall-following loop is therefore **not** simply "a loop, but curved". Its
defining property is *where it sits in the mode*, and the standoff is the
control on that.

### Coaxial feedthrough

Feed the loop by a **coaxial line entering through a clearance hole in the
cylindrical wall** at one leg's azimuth. The leg passes through the hole and *is*
the coaxial inner conductor; the hole wall is the outer conductor.

  - **Size the hole from the required line impedance**, not from a connector
    choice: `Z0 = (eta0 / (2 pi sqrt(eps_r))) * ln(r_outer / r_inner)`, which for
    air reduces to `Z0 ~= 59.96 * ln(r_outer / r_inner)` ohms.
  - **The inner conductor must pass through.** A bare hole of this size is a
    circular waveguide far below cutoff at the operating frequency — compute as
    `f_c = chi'_11 * c / (2 pi r)` — and carries no power. With the inner
    conductor present it is a coaxial line supporting TEM, which has no cutoff.
    The hole is a feedthrough only because something conducts through it.
  - Placing the drive at the wall entry rather than mid-arc puts the **port
    reference plane at the wall**, which is where a VNA measurement would be
    referenced.

---

## Disclosure 3 — Verifying a driven cavity model by closing its power balance

Published because it is the step that distinguishes a coupler measurement from a
plausible number, and because we spent weeks on numbers that had never been
subjected to it.

### The problem

A frequency-domain driven solve reports `S11`, from which the absorbed power
follows as `P_inc(1 - |S11|^2)`. **That figure is not a measurement of anything
being absorbed.** If the port's geometry or normalisation is wrong, `S11` is
wrong, no conservation law is violated anywhere in the solve, and the result is
self-consistent, mesh-convergent-looking and false.

### The method

  - Integrate the **Poynting flux through each dissipative boundary separately**
    — cavity wall, coupler conductor, port — as a post-processing step on the
    same solve.
  - Compare the **sum against `P_inc(1 - |S11|^2)`**. Call the ratio the
    *closure*. A correct one-port model closes to within a few percent.
  - **Calibrate on a geometry already trusted, in the same run set.** An absolute
    closure figure means little alone; the same figure on a known-good coupler,
    same solver and mesh settings, is what turns it into a verdict.
  - The closure also **determines the drive normalisation**: the incident power
    implied by the trusted geometry's closure resolves what the port's reported
    incident voltage means, which is otherwise a convention to be guessed.

### The port-independent cavity Q

`Q0 = omega * W / P_loss`, with `W` the stored field energy and `P_loss` the
summed surface dissipation, uses **no S-parameter, no port normalisation and no
resonance fit**. It therefore yields a cavity Q even on a model whose port is
demonstrably wrong, and it can be checked against an eigenmode solve of the same
cavity, which shares none of the driven machinery.

  - ⚠️ `Q0` derived this way is a **ratio**, so it survives an error that scales
    energy and dissipated power together. The closure is an **absolute** and does
    not. The two disagreeing in that particular pattern localises the fault to
    the scale of the resonant response rather than to the physics — which is a
    diagnostic in its own right.

### Applying it to a curved-gap loop coupler

A lumped port is defined on the face spanning a gap cut in the conductor. When
the conductor is an arc, that face is an **annular sector, not a plane**. Solvers
that require a planar port face may accept the non-planar one without error and
return a wrong `S11`. The failure is worst where the loop is closest to the wall.

  - **The diagnostic signature is a broadband off-resonance offset**: a lossless
    cavity must reflect essentially all incident power away from resonance, so a
    persistent flat offset in `|S11|` with no matching surface dissipation is a
    port-model defect, not a loss.
  - Discretisation-error indicators correlate with it and are **not** its cause;
    refining the mesh changes how wrong the port integration is without any power
    moving. **Treating a mesh-dependent artefact as a mesh-resolution problem is
    the trap**, and it costs whole studies.

---

## Disclosure 4 — Consumable liquid starter fluid delivered through the sample path

### The problem

A resonant cavity of this class does not reach the breakdown field of
atmospheric-pressure nitrogen at practical drive powers, by a margin that more
power does not close. **An external ignition assist is therefore mandatory**, and
this is true of commercial microwave-induced plasma instruments generally.

Every standard assist adds hardware at the torch: a high-voltage spark or Tesla
coil brings a supply and its EMI into an instrument built around a sensitive
optical measurement; an argon start brings a second gas cylinder and its flow
control; a mechanical striker brings a moving part, and an eroding electrode,
into the hottest region of the instrument.

### The design

Deliver a **consumable liquid starter fluid — a dilute aqueous alkali-metal
carboxylate, for example potassium acetate — through the instrument's existing
nebuliser and injector.** Ignite, then flush with deionised water before the
sample is introduced.

🔑 **No ignition hardware is added, because the sample-introduction path is the
ignition path.** The instrument already has a nebuliser, an injector and a rinse
step; the disclosure is that these are sufficient to start the discharge.

### Why it works — one compound supplies both requirements

On heating, an alkali carboxylate decomposes by the ketonic route to the alkali
carbonate plus a ketone, and the ketone pyrolyses to **amorphous carbon** rather
than escaping as vapour. That single decomposition supplies both of the things
ignition needs, in the same deposit and in intimate contact:

  - **A susceptor.** Amorphous carbon at 2.45 GHz has a skin depth of tens to
    hundreds of micrometres across the plausible conductivity range, and
    millimetres even at the low end. **Any film deposited from solution is far
    thinner than its own skin depth**, so it absorbs volumetrically throughout
    rather than reflecting — a lossy absorber, not a mirror. The deposit is
    therefore heated *directly by the cavity field*, with no external heat
    source. This is the step that makes the fluid self-starting: a dilute
    aqueous aerosol is nearly transparent at 2.45 GHz and could not otherwise
    heat itself.
  - **A seed.** Because the carbon forms alongside, and in contact with, the
    carbonate, **carbothermal reduction** liberates alkali vapour well below the
    temperature at which that carbonate decomposes on its own. An alkali vapour
    has a far lower ionisation energy than nitrogen, so the temperature at which
    the bore reaches any given conductivity falls by of order two thousand
    kelvin relative to unseeded nitrogen — a range reachable by a self-heating
    deposit, which the breakdown field is not.

Once the bore is conductive the cavity couples into it and the working gas takes
over. **The deionised-water flush is then part of ignition, not cleanup**, and it
does three things at once:

  - **It removes seed shielding**, letting the cavity re-couple as the working
    gas ionises.
  - **It gasifies the carbon at temperature**, so the susceptor is consumed
    rather than accumulating from run to run.
  - **It clears the seed before the sample**, so the ignition aid is not present
    in the analytical blank. This requirement is **generic to the method, not to
    any particular salt**: any starter fluid delivered through the sample
    introduction path must be flushed before measurement, whatever its cation.

🔑 **And the flush is closed-loop, which is the part that makes the choice of
seed non-obvious.** Because the seed cation is deliberately chosen to be an
element the instrument already measures, **the instrument can watch its own
contamination recede and flush to a measured criterion** — seed emission below
the noise floor — rather than for a fixed, assumed time. The controller knows it
is executing the ignition sequence, and the analytical detector is the sensor.

**A seed that is NOT an analyte would have to be flushed blind**, with no line to
monitor and a residual that is invisible precisely because nothing measures it.
**Selecting the seed from the target element list is therefore a design choice
that buys in-situ verification**, and it is disclosed as such.

**That the same flush satisfies all three is a property of the sequence, not a
coincidence**, and it is part of what is disclosed here.

### Choice of anion and cation

  - **The anion should decompose to a carbon residue and benign gases.**
    Carboxylates do. **Halides should be avoided** principally because they are
    electronegative: they attach free electrons and work directly against the
    discharge being started. (They also attack a fused-silica torch, though that
    is secondary where the torch is sapphire — which is the material a
    fluoride-bearing sample matrix already requires.)
  - **The cation's ionisation energy is the smaller effect.** The decomposition
    route is what supplies the mechanism; a heavier alkali buys a modest
    reduction in threshold temperature and nothing structural.
  - **Choose the cation FROM the target element list, not away from it.** In a
    soil instrument potassium is a primary macronutrient, so the spectrometer
    must resolve it regardless; using it as the seed makes the flush verifiable
    against the instrument's own measurement. The intuition to avoid an analyte
    is backwards here — it trades a monitored residual for an unmonitored one.
    Molarity remains a secondary lever on how much must be flushed.

### What is already public, and what is not

Stated so the boundary of this disclosure is unambiguous. Each leg is
established independently:

  - **Susceptor ignition of microwave plasma torches is standard practice**,
    typically as a solid pointed rod or graphite element placed in the field.
  - **Alkali seeding to raise plasma conductivity is long established** and
    modelled by the standard equilibrium route, including for potassium and
    caesium specifically.
  - **Alkali-seeded microwave plasma formation in aqueous bodies is documented**
    in the household-oven literature on grapes and hydrogel beads, where alkali
    species in the aqueous body are field-ionised at a dielectric hotspot.

**The sources, named so the boundary can be checked rather than taken on
trust.** Copies of the last two are in `refs/`:

  - *How to Ignite an Atmospheric Pressure Microwave Plasma Torch without Any
    Additional Igniters* — graphite/susceptor ignition of a torch.
  - *Estimated electric conductivities of thermal plasma with potassium or
    cesium seeding* (PMC11145353) — the alkali-seeding conductivity route.
  - *Self-Perpetuating Carbon Foam Microwave Plasma Conversion of Hydrocarbon
    Wastes*, Environ. Sci. Technol. (`acs.est.0c06977`) — a carbon susceptor
    sustained by its own feedstock.
  - US 5051557 — MIP torch with a tantalum injector probe: ignition hardware
    placed in the sample path, which is the approach this disclosure removes.
  - Zhang et al., *Processes* **12**, 2505 (2024) — metal-acetate-enhanced
    microwave pyrolysis. Its Table 1 ranks potassium acetate highest in carbon
    disorder of every salt tested, and it decomposes the acetate below the
    substrate's own pyrolysis onset. ⚠️ Run in an external SiC susceptor boat, on
    a carbonaceous substrate — so it supports the decomposition chain but **not**
    the cold-start bootstrap, which is why that is listed as unestablished below.
  - *Linking plasma formation in grapes to microwave resonances of aqueous
    dimers* (PNAS) — potassium/sodium seeded microwave plasma ignition in an
    aqueous body, and the source of the grape/hydrogel observation above.

🔑 **What is disclosed here is the integration**: a *consumable liquid* whose
decomposition products supply the susceptor and the seed **together**, delivered
through the sample-introduction path the instrument already has, and flushed out
before measurement — so that the instrument contains no ignition hardware at all.
This is a systems claim rather than a claim about new physics, and it is
published on that basis.

### What is NOT established, and is disclosed as unestablished

  - 🔴 **The cold-start bootstrap has not been demonstrated in this torch.**
    Published metal-carboxylate microwave-pyrolysis work heats the sample inside
    an external susceptor vessel, so it does not show that carbon deposited from
    the salt initiates absorption *from cold*. The supporting observations for
    cold start are qualitative.
  - **No molarity is claimed.** The concentration that ignites without shielding
    the field is not established, and any figure derived from an equilibrium
    release model is unsound here — alkali availability is gated by the
    reduction chemistry, not by ionisation equilibrium.
  - **Where the carbon deposits** — injector tip, torch wall, or bore — is not
    established. It decides whether the susceptor sits in the field maximum, and
    therefore whether ignition is reproducible run to run.
  - **Whether the flush fully gasifies the deposit** is not established.
  - No claim is made about the plasma the discharge reaches after ignition.

---

## Where the numbers are, and how they are derived

This document deliberately states **mechanisms and derivations rather than
values**, because the values are still being refined. Disclosure 3 is stated the
same way: it is a *method*, and its worth does not depend on any number this
project happens to hold today. Every value lives in the
repository, and git history records what it was on any given date.

| quantity | how it is derived | where it lives |
|---|---|---|
| cavity radius and length | from the chosen diameter-to-length ratio and the source frequency, via the TE011 resonance condition `f = (c/2pi) sqrt((chi'_01/a)^2 + (p pi/L)^2)` | `physics.py: design_point()`, called by `e0k2_anchor.design_point()` |
| aspect ratio, groove size, wall and conductor materials | canonical values, each carrying a status flag and provenance | `experiments/resonance/baselines.json` |
| groove effect on mode purity and TM111 separation | eigenmode simulation, grooved vs ungrooved, with mode purity reported per solve | `experiments/resonance/KNOWN.md`, and the `h2`/`h2b` rigs |
| groove depth behaviour | parameter sweep over depth | `h2b_groovescale` |
| loop geometry and the coax hole | constructed in the mesh generator; the sidecar records standoff, centreline and port face separately | `geometry.py` (`--loop-azim-standoff`, `--loop-hole`) |
| coupling quantities | simulated; see the caveat below | `experiments/resonance/Q_LEDGER.md` |
| standoff, and the field components it trades between | closed form for TE011, `E_phi ~ J1(chi'_01 r/a)` and `H_z ~ J0(chi'_01 r/a)`, evaluated at the conductor centreline | `experiments/resonance/Q_LEDGER.md`, `coldfield.py` |
| power balance closure, and the drive normalisation it fixes | `SurfaceFlux` boundary integrals on wall / port / conductor, against `P_inc(1 - \|S11\|^2)`, calibrated on a trusted coupler | `experiments/resonance/KNOWN.md`, `h3_driven.py` |
| unloaded Q by the port-independent route | `Q0 = omega W / P_loss` from stored energy and summed surface dissipation; cross-checked against an eigenmode solve | `experiments/resonance/KNOWN.md`, `Q_LEDGER.md` |
| coupler and wall dissipation | the same surface integrals, scaled linearly in drive power | `experiments/resonance/KNOWN.md` |
| starter-fluid ignition — the chain, its supporting literature and its gaps | decomposition chemistry STATED; skin depth and seeded-conductivity thresholds DERIVED against the measured coupling map; nothing measured | `experiments/ignition-options/STARTER-FLUID.md` |

**Reproducing any of it:** meshes are generated by `geometry.py` (gmsh/OCC) and
solved with Palace (MFEM) finite elements. Rig scripts, solver configurations and
their outputs are all in `experiments/resonance/`.

---

## What is deliberately NOT claimed

This section is part of the disclosure. The following were investigated and are
**not** established:

  - Any specific external Q, coupling coefficient, or VSWR for the **azimuthal**
    coupler. The sensitivity to modelled port geometry noted in earlier revisions
    has since been localised — see Disclosure 3 — but the coupling quantities
    themselves remain unestablished for that coupler.
  - Any operating electron density, plasma coupling efficiency, or claim about
    what plasma the cavity can sustain.
  - Any claim that TE011 is ultimately the correct mode for the finished
    instrument.
  - Any thermal design. Coupler and wall dissipation have been computed from the
    field solution, but no thermal model exists and no temperature is claimed.
    Note only that a coupling loop's **power density** is several times the cavity
    wall's, and that the worst case for it is the cold, resonant, unloaded state
    rather than normal operation.
  - Any tolerance, machining or tuning-range specification. Not characterised.

### Assumed, and stated so it is not mistaken for a claim

The architecture **assumes an external ignition source**. A cavity of this class
does not reach the breakdown field of atmospheric-pressure nitrogen at practical
drive powers, by a margin that more power does not close. This is consistent with
commercial microwave-induced plasma instruments generally, and is recorded here
as a design premise rather than a limitation of the designs disclosed above.

**Disclosure 4 is an approach to supplying that assist without dedicated
hardware, and it is disclosed as an approach rather than as a demonstrated
one** — see its own *What is NOT established*. Nothing elsewhere in this document
depends on it: Disclosures 1–3 stand whether ignition is by starter fluid,
striker, spark or an argon start.

`NEXT.md` and `KNOWN.md` are a **working record**, including hypotheses that were
later retracted; they are not claims. This file is the claims.
