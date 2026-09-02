# Defensive publication — microwave-induced plasma cavity, mode filter and coupler

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

## Where the numbers are, and how they are derived

This document deliberately states **mechanisms and derivations rather than
values**, because the values are still being refined. Every value lives in the
repository, and git history records what it was on any given date.

| quantity | how it is derived | where it lives |
|---|---|---|
| cavity radius and length | from the chosen diameter-to-length ratio and the source frequency, via the TE011 resonance condition `f = (c/2pi) sqrt((chi'_01/a)^2 + (p pi/L)^2)` | `physics.py: design_point()`, called by `e0k2_anchor.design_point()` |
| aspect ratio, groove size, wall and conductor materials | canonical values, each carrying a status flag and provenance | `experiments/resonance/baselines.json` |
| groove effect on mode purity and TM111 separation | eigenmode simulation, grooved vs ungrooved, with mode purity reported per solve | `experiments/resonance/KNOWN.md`, and the `h2`/`h2b` rigs |
| groove depth behaviour | parameter sweep over depth | `h2b_groovescale` |
| loop geometry and the coax hole | constructed in the mesh generator; the sidecar records standoff, centreline and port face separately | `geometry.py` (`--loop-azim-standoff`, `--loop-hole`) |
| coupling quantities | simulated; see the caveat below | `experiments/resonance/NEXT.md` |

**Reproducing any of it:** meshes are generated by `geometry.py` (gmsh/OCC) and
solved with Palace (MFEM) finite elements. Rig scripts, solver configurations and
their outputs are all in `experiments/resonance/`.

---

## What is deliberately NOT claimed

This section is part of the disclosure. The following were investigated and are
**not** established:

  - Any specific external Q, coupling coefficient, or VSWR for the coupler.
    Simulated values proved sensitive to the modelled port geometry.
  - Any operating electron density, plasma coupling efficiency, or claim about
    what plasma the cavity can sustain.
  - Any claim that TE011 is ultimately the correct mode for the finished
    instrument.

`NEXT.md` and `KNOWN.md` are a **working record**, including hypotheses that were
later retracted; they are not claims. This file is the claims.
