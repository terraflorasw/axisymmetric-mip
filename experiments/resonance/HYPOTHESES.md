# Hypotheses

**The working set.** One line per hypothesis, its state, and its conclusion if
closed. Experiments are attempts *at* a hypothesis; when a hypothesis closes, its
experiments collapse into the conclusion and become provenance in FINDINGS.md.

⚠️ **DRAFT — the hypothesis list is the user's to set.** This is assembled from
the record, not designed. Correct it.

## Why this file exists

R-numbers reached 113 and could not be collapsed: each was a finding, appended,
never retired, and no R could invalidate another. The E-series was heading the
same way — E0, E0b…E0m, E0kp, E0f2, E0v: fifteen sub-experiments named by order
of discovery rather than by structure.

Hypotheses are **durable and few**. Experiments are **attempts and many**. Keeping
them in one object is what makes the count only go up.

**The test: nobody should ever need to open E0b again.**

## States

`open` · `resolved` · `falsified` · `split` (the question was malformed and
divides) · `withdrawn` (ill-posed, and not replaced) · `premature` (well-posed,
but asked BEFORE the thing that sets its requirement — the measurements stand as
provenance; the open part moves to whatever sets the requirement)

⚠️ `premature` was added 2026-08-23 for H2 and it is the state this programme is
most likely to need again. It is the tail-chasing failure in hypothesis form:
answering a question correctly before knowing what the answer has to satisfy.

## Rules

1. A hypothesis is about **the machine or the physics**. Never about the
   instrument's implementation — "is gmsh deterministic" is an experiment inside
   H0, not an H of its own. Otherwise this becomes R-numbers with a prefix.
2. Every experiment declares **verification and falsification before it runs**.
3. A conclusion records **the falsifier's outcome**, not just a value — how hard
   it was pushed, and where it would break. Values alone cannot be collapsed;
   that is why 113 R-numbers could each be plausible and collectively useless.
4. A hypothesis that cannot be answered as posed is **split**, not accumulated
   against.

---

## H0 — the instrument reproduces known cavity physics · **RESOLVED**

Fifteen experiments (E0 … E0v, E0f2, E0kp, E0q) collapse to **INSTRUMENT.md**.

Headline: at geometric order 2 and solver order 2, TE011 lands within **0.058
MHz** of closed form, differential work is good to **~20 kHz**, and **Q ∝ σ^0.5**
holds to 4 decimals. Driven and eigenmode agree to **0.225 MHz** — the recorded
3.7× disagreement was an order-1 artifact.

⚠️ Cost of getting here: the solver order had been **1** by hidden default, and
every rig that did not override it was invalidated. Nothing about that was
visible from inside the instrument.

**Open sub-questions**, in INSTRUMENT.md § *What is NOT characterised*: absolute
Q has no anchor, dielectric loading is unverified, driven coupling is unmeasured.

## H1 — which aspect ratio · **RESOLVED: D/L 1.525, a 88.00, L 115.42**

✅ **AND IT SURVIVES THE TORCH (2026-08-23, `h4_field` run 2).** The design
point was chosen with `--no-torch`, so a dielectric large enough to move it out
of the LDMOS band would have invalidated it. Measured: sapphire −15.00 MHz,
quartz −3.36 MHz, all three cases inside 2.40–2.50 GHz. The 15 MHz is 4.5% of
the 332.7 MHz rival separation and does not threaten the mode ordering.
🔑 Slater predicted −15.3 MHz before the solve and was met to **2%**, at
ε = 11.6 — a perturbation theory holding well outside where it was expected to.

Two candidates, both resonating TE011 at 2.45 GHz empty, both regenerable from
`physics.py` in three lines:

| | a (mm) | L (mm) | D/L | nearest rival |
|---|---:|---:|---:|---|
| A | 103.244558 | 88.53 | 2.332 | TM210 at **76.6 MHz** |
| B | 86.743283 | 120.00 | 1.446 | TE112 at **245.7 MHz** |
| *optimum* | 88.005 | 115.42 | **1.525** | TE112 at **332.7 MHz** |

**Separation is settled analytically.** Max-min over D/L gives a single optimum
at 1.525; B is at 74% of it, A at 23%. A also sits on the shoulder of a TM210
pole (11.5 MHz at D/L 2.20), so it is tolerance-sensitive; the optimum is a
stationary point and is not.

⚠️ **Poles to avoid**: TM012 crosses TE011 at **D/L = 1.096440** (closed form,
`L/a = √(3π²/(χ′₀₁²−χ₀₁²))`), TM210 near 2.20, TM020 near 2.50.

🔑 **TM111 is exactly degenerate at EVERY D/L** — χ′₀₁ = χ₁₁ identically. Aspect
ratio governs every rival except the one that matters most. That is H2's job.

**ANSWERED.** Q(D/L) measured on a bare cavity: TE011 Q rises 27% as D/L falls
(36,308 at 2.332 → 46,220 at 1.200), so Q and bore coupling both favour low D/L
while separation peaks at 1.525. Between 1.446 and 1.525 the trade is separation
+35% against Q −1.4% and coupling −5%, so **separation decides: D/L 1.525**, which
is also the stationary point and therefore tolerance-insensitive. Candidate A is
beaten on all four axes. Cross-checked against E0q to −0.7%; falsifier (TE011 Q >
TM111 Q) passed at every point.

🔑 **Bore RADIUS dominates coupling, not aspect ratio** — 30× versus 2×. The real
constraint chain is slm ceiling → bore radius → coupling → input power. The
8.5 mm bore is inherited from the suspect record and is a design variable.

## H2 — the mode filter · **✅ ANSWERED. 5 × 10 mm clears the LDMOS band.**

🔑 **The groove is one of the three things this programme actually knows** (with
E0 and H1), and H3 is built on it. Do not read "retired" as "set aside".

**THE RESULT, live and consumed by H3:** an annular groove, **frozen at
5 × 10 mm**, both end caps. It runs PARALLEL to TE011's azimuthal cap current and
CUTS the radial component every TM mode has. Cold: TM111 **−64 MHz**, TE011
**14 kHz**, Q cost **0.3%**. 🔴 λ/4 = 30.59 mm is the depth to AVOID.
✅ Confirmed under load 2026-08-23: the filter is what makes TE011 the mode an
LDMOS tuner locks to; without it the tuner takes a TM-like mode at 2.44 GHz.

🔴 **"RETIRED AS PREMATURE" WAS WRONG AND IS WITHDRAWN (2026-08-23).** H2 did
answer sufficiency, against an EXTERNAL anchor — the LDMOS tuning range. The
record's own heading says it: *"The shallow regime works, and it is enough"*
(FINDINGS L1497). **At 10 mm depth TM111 is pushed 64.25 MHz, clearing the
50 MHz LDMOS band.** That is why dimension optimisation stopped: 5 × 10 moves
everything far enough out of the tuner's reach that refining it further bought
nothing.

**So H2 is ANSWERED, not set aside**, and it is anchored outside the programme —
which is what puts it alongside E0 and H1 as load-bearing. Its variables left the
SEARCH space because the question was closed, not because it was abandoned.

🔴 **And "left the design space" was once implemented as "left the geometry" —
`GEO` never carried the groove, and a full day of H3 measured a cavity without
it.** See CONVENTIONS §7f. The frozen value now lives in `GEO_DESIGN`.

⚠️ **The number H2 is NOT reused.** Renumbering would rewrite 41 references, 24
of them in FINDINGS.md — append-only provenance whose committed history already
carries this numbering. Gaps in the sequence are cheaper than broken citations.

## H3 — sustainment: COLD, HOT and LOADED · **NOT ANSWERED**

**H3 asks one thing: what are the sustainment numbers across the three regimes,
in the cavity H2 specifies.** Cold (no discharge), hot (gas heated, weakly
ionised), loaded (full plasma, and a real high-TDS sample). It consumes H2's
result — the groove, frozen at 5 × 10 mm — because that is the cavity.

🔴 **THERE IS NO "H3 WITHOUT THE GROOVE".** That is not a variant, a control, or
a first approximation. The filter decides which modes exist, and every quantity
H3 asks for is a property of the mode landscape. A groove-free measurement
answers a question nobody asked.

🔴 **Everything measured for H3 on 2026-08-23 was groove-free and is DISCARDED**
— not "scope-invalid pending review", discarded. η(ne), the +31.6 MHz pull,
loaded Q₀, β vs loop area, the 78% suppression law, sapphire's loaded point.
Do not quote them and do not try to salvage them; re-measure from `GEO_DESIGN`.

✅ **What survives from that day is instrument, not cavity**: driven replaces
eigen for loaded work (12 eigen timeouts → 0 across 17 driven cases). See
INSTRUMENT's "loaded-cavity toolkit".

✅ **The one groove-correct measurement so far** (`h3_groove`, 2026-08-23):
**the filter makes TE011 the mode an LDMOS tuner locks to**, at both loop sizes
tested. Without it the tuner locks to a TM-like mode near 2.44 GHz every time —
the groove moves that mode −63.6 MHz, matching H2's cold TM111 −64 MHz.
⚠️ At the 28×20 loop, TE011 moved −12.80 MHz with the groove against +0.00 MHz
at 11×8. Either the groove differs under load or that mode is misidentified.
**Unresolved. Do not carry the number.**

### The regimes, and what each must produce

| regime | state | what H3 must return |
|---|---|---|
| **cold** | no discharge, gas fill | f₀, Q₀, and the coupling a tuner sees before ignition |
| **hot** | heated gas, weakly ionised | the trajectory between cold and loaded — where the tuner must track, and whether coupling holds through it |
| **loaded** | full plasma **+ a real high-TDS sample** | sustained f₀, Q₀, delivered power, and the sample-loading margin |

⚠️ **Sample delivery is the LOADED regime, not a separate hypothesis.** It was
briefly split out as "H6" on 2026-08-23; that was mine and it was wrong. Folded
back here. Its one durable observation stands and is H3's: the sample travels up
the central channel, r < 2 mm, which is exactly TE011's field null — the same
null that stops TE011 cold-igniting is what protects it from a conductive
sample column.

⚠️ Aerosol transport, desolvation and atomisation efficiency are CHEMISTRY, not
EM. They set what ne a sample produces; H3 asks what the cavity does with it.
Those belong with H5's external inputs.

## H4 — ignition · **TM IGNITION DISCARDED 2026-08-22. Auxiliary ignition adopted.**

🔴 **Killed by TWO INDEPENDENT MEASURED legs.** Either alone is sufficient;
together there is nothing to rescue.

**Leg 1 — the mode filter cannot spare a TM companion.** An annular groove is
axisymmetric and therefore **blind to m** by construction. TM111 is m=1; TM012
and TM020 are m=0; m is the only property separating keep from reject. Measured,
h2_d0 → h2_d20 by signature matching: TE011 moved **−0.0 MHz / −0% Q** while
TM010 moved −32.8 MHz (−40% Q) and TM011 −113.8 MHz (−59% Q). The groove spares
TE011 and nothing else.

**Leg 2 — no mode cold-ignites anyway.** Measured bore energy fractions
(`p_elec[bore]`, h2_d0) converted to reduced field:

| mode | bore energy | E/N @ 3 kW | vs ~100–150 Td threshold |
|---|---:|---:|---|
| TE011 | 0.079% | 7.0 Td | 15–20× short |
| TM111 | 0.674% | 13.8 Td | 7–11× short |
| **TM010** | **2.300%** | **35.9 Td** | **3–4× short** |

The best mode available falls 3–4× short at 3 kW. The TM companion was solving a
problem **it could not have solved either**.

⚠️ Corroborating, NOT a third leg: MP-AES reportedly ignites with Argon. The a
fortiori direction is sound physics — a diatomic gas dumps electron energy into
vibrational and rotational states below the ionisation threshold while monatomic
Ar has no such sink, so **N₂ is substantially harder to break down than Ar at the
same E/N**. An instrument reaching for Argon to get lit says the field alone is
marginal in the EASY gas. 🔴 But this is inference from another instrument's
behaviour, and MP-AES/MICAP figures have entered this record unexamined before
(the 20 slm ceiling). Verify; do not lean on it.

### ✅ ADOPTED: auxiliary ignition, TE-only architecture

**Ignition needs a THERMAL KERNEL, not seed electrons.** Seeding removes the
statistical delay in waiting for an initiatory electron; it does NOT lower the
field required for net ionisation, which is set by E/N. At 3000–5000 K the
neutral density falls 10–17×, so the SAME cold field lands at 45–130 Td — into
the ionising range. A spark or Tesla discharge supplies exactly that: a hot
conductive filament. ICP applies it EXTERNALLY through the quartz, which also
avoids in-plasma electrode erosion — a real concern for a spectroscopy
instrument.

🔑 **The geometry inverts in our favour.** TE011's on-axis field null — the exact
reason it cannot ignite — makes an on-axis or near-axis igniter nearly invisible
to it (0.079% of its energy is there). The converse reinforces it: an axial
conductor strongly perturbs TM0n, whose E_z peaks on axis — the same physics as
the TDS-shorting objection that already rules TM out for OPERATION.

### What this collapses

- ✅ mode filter returns to the **TE-only case, SOLVED** at 5×10 mm
- ✅ **D/L stays at H1's optimum 1.525** — no longer dragged to 1.141 or 2.431
- ✅ no in-band companion → no 50 MHz near-rival → **no tuning plunger**
- ✅ the ~100 MHz band constraint disappears
- 🔴 **H3 becomes the SOLE gate**: can TE011 SUSTAIN a discharge once a thermal
  kernel exists? Not one question among several — the one the architecture
  turns on.

### Still to check

1. **The 100–150 Td threshold is a literature figure.** Microwave breakdown at
   1 atm is diffusion-loss and therefore geometry dependent. This programme has
   been burned by a formula quoted outside its domain. Verify.
   → 2026-08-22: partially discharged. ω/ν = 0.154 at 1 atm, so
   E_eff = 0.988·E_rms — the 2.45 GHz field is **99% as effective as DC** and the
   quasi-static criterion applies without correction. The DIFFUSION-loss concern
   is NOT discharged; that is what makes it geometry dependent.
2. **Does an on-axis conductor perturb TE011?** One eigen solve, ~165 s.
   → ✅ **ANSWERED 2026-08-23, and the answer is YES — strongly.** `h4_seed`:
   an on-axis plasma column of radius 1 mm over 10 mm drops **Q from 44,384 to
   34,611 — η = 0.22**, i.e. 22% of 1 kW absorbed by a seed ON THE AXIS. A
   2 mm column absorbs 80%.

   🔴 **This refutes "the geometry inverts in our favour" above.** That argument
   reads 0.079% of mode ENERGY in the bore as meaning a near-axis igniter is
   "nearly invisible" to TE011. **Energy fraction is not absorption.** E_φ is
   zero only AT r = 0; it rises linearly, reaching 3.7% of peak by r = 1 mm, and
   with σ = 27.5 S/m that is ample. Volume-averaging E_φ over the column predicts
   η = 0.29 / 0.12 against 0.22 / 0.10 measured — right order, over-predicting
   1.1–5.9× as the plasma shields its interior. An igniter placed near-axis for
   "invisibility" would load the cavity hard.

   ⚠️ Retracted in the same session: I proposed the absorption must be INDUCTIVE
   (H_z peaks on axis where E_φ nulls). The E-field arithmetic above accounts for
   it without invoking H, so that claim is withdrawn — it was asserted before
   being computed.
3. **What igniter, and where** — external through the torch wall, per ICP.

### 🔴 2026-08-22 — the "on-axis igniter is invisible" argument needs care

H4 above argues the on-axis null makes a near-axis igniter *nearly invisible* to
TE011, and calls this the geometry inverting in our favour. **That is right for
the ELECTRODE and wrong if applied to the KERNEL.** Absorbed power goes as
∫σ|E|²dV, and relative to a seed at r = 0.5 mm the same seed absorbs:

| seed at r | coupling | | seed at r | coupling |
|---:|---:|---|---:|---:|
| 2 mm | 16× | | 6 mm | 142× |
| 4 mm | 64× | | 8.5 mm | **279×** |

A kernel created on axis sits in the null the mode cannot grab. H4's adopted
answer — **external spark through the quartz, as ICP does** — already places the
kernel at large r, so the CONCLUSION is unaffected. But the reason it is right is
COUPLING, not just electrode erosion, and an igniter moved inboard for
"invisibility" would break ignition. ⚠️ Those are ratios of an analytic mode
profile; `h4_seed.py` measures them.

🔴 **2026-08-23 — the 279× ratio above is NOT CONFIRMED, and the "cannot grab"
half is WRONG.** `h4_seed` ran matched axis/wall pairs twice.

Run 1: all three WALL cases timed out (0–12 NLEPS) and all three AXIS cases
solved. Cause: a 0.5 mm shell at r = 8.25 mm meshed to **252,068 tets vs 36,967**
for an axis column — mesh cost for a shell scales with its SURFACE. Reported, not
retried. (An estimator I then wrote predicted 4,050 elements for that case —
wrong by 50×, because refinement bleeds outside the shell. Replaced with a guard
on the MEASURED tet count.)

Run 2 (thicker shells): the wall cases **SATURATE** at η = 0.9919–0.9933, so
η/V is set by their volume rather than their coupling. **F1 is not testable
against a saturated member** — the first report printed "wall couples 0x" (a
format bug on 0.124) and fired F1 on it; both were bugs, now fixed to report a
lower bound and decline the test.

What survives: **an axis seed couples strongly** (η = 0.22 at 1 mm, 0.80 at
2 mm), so "the mode cannot grab an on-axis kernel" is false. Whether the WALL
couples *more per unit volume* remains unmeasured, and needs an unsaturated wall
case — lower ne or a smaller shell that still meshes under TETS_MAX.

### ✅ 2026-08-23 — THE MEASURED FIELD MAP. `h4_field`, torch in the model.

Every field number above was computed from an ANALYTIC J₁ profile normalised to a
bare-cavity Q measured with `--no-torch --no-inner`. `h4_field` replaces it with a
solved map that contains the torch dielectric. Four cases, same mesh machinery,
18-point radial probe rake, all renormalised to 1 kW.

| case | f₀ GHz | shift | Q | E @ 8.2 mm |
|---|---:|---:|---:|---:|
| no-torch | 2.450496 | — | 44,245 | 2.34 kV/cm |
| outer sapphire | 2.436782 | **−13.71 MHz** | 44,280 | 2.59 |
| full sapphire | 2.435493 | **−15.00 MHz** | 44,215 | 2.59 |
| full quartz | 2.447135 | −3.36 MHz | 43,895 | 2.20 |

✅ **F1 passes on all three** — every torch case stays in 2.40–2.50 GHz, so H1's
design point survives the dielectric. ⚠️ But sapphire moves f₀ by **15 MHz**: a
tuning requirement, not a rounding error. ✅ V2 on Q: 0.31%.

#### 🔑 The bore field is 23% HIGHER than the bare map, uniformly

Measured (kV/cm **rms** at 1 kW), sapphire vs the analytic J₁ rms:

| r mm | no-torch | **sapphire** | quartz | J₁ rms | sap/J₁ |
|---:|---:|---:|---:|---:|---:|
| 2.0 | 0.77 | **0.64** | 0.54 | 0.52 | 1.23 |
| 4.0 | 1.29 | **1.28** | 1.09 | 1.04 | 1.23 |
| 6.0 | 1.80 | **1.91** | 1.62 | 1.55 | 1.23 |
| 6.6 | 1.95 | **2.10** | 1.78 | 1.70 | 1.23 |
| 8.2 | 2.34 | **2.59** | 2.20 | 2.10 | 1.23 |
| 8.45 | 2.41 | **2.67** | 2.27 | 2.16 | 1.23 |
| 10.5 | 2.90 | **3.14** | 2.76 | 2.66 | 1.18 |
| 20.0 | 4.97 | **4.93** | 4.77 | 4.73 | 1.04 |
| 42.3 | 7.21 | **7.08** | 7.10 | 6.96 | 1.02 |

**sap/J₁ is FLAT at 1.23 across r = 1.0–9.2 mm**, then converges to 1.02 at the
mode peak. A resolution artifact would not be flat — the no-torch column drifts
1.96 → 1.04 over the same range, which IS one (with no torch, 8 mm elements abut
the 1 mm refined bore at r = 8.5; the torch cases mesh the wall finely and are
better resolved). So the sapphire tube **concentrates 23% more field in the bore
with the mode shape preserved.**

#### 🔴 Every E/N number above this entry is 23% LOW

Recomputed for a sapphire torch (N₂, threshold 100–150 Td):

| r | E bare | **E sapphire** | 3000 K | 5000 K | 10,000 K |
|---:|---:|---:|---:|---:|---:|
| 3.0 mm | 0.78 | **0.96** | 39 | 65 | 131 Td |
| 6.5 mm | 1.68 | **2.07** | 84 | **141** | 282 Td |
| 8.5 mm | 2.17 | **2.67** | 109 | **182** | 364 Td |

At r = 8.5 mm a 5000 K arc channel reaches **182 Td, above threshold** rather
than at its edge (was 148). This does not overturn the electrode-placement
objection — there is still nowhere in a Fassel torch to put them — but the
FIELD half of N₂ arc ignition is more favourable than the bare map implied.

#### Argon contours, measured

| threshold | analytic (bare) | **sapphire** | quartz |
|---|---:|---:|---:|
| 1.7 kV/cm | 6.6 mm | **5.3 mm** | 6.3 mm |
| 2.1 kV/cm | 8.2 mm | **6.6 mm** | 7.8 mm |
| 2.5 kV/cm | 9.8 mm 🔴 outside | **7.9 mm ✅** | 9.4 mm 🔴 |

🔑 **The misfire scenario does not survive the real dielectric.** With sapphire,
even a purity-degraded 2.5 kV/cm threshold lands at 7.9 mm — inside the 8.5 mm
bore. The "razor-thin shell flush against the wall" was an artifact of leaving
the tube out of the model. ⚠️ With QUARTZ it does misfire at 2.5 kV/cm — the
development build is not a safe stand-in for the sapphire build here.

⚠️ **Uncertainty**: probe error runs 4% at r = 42 mm to ~19% at r = 5 mm in the
no-torch case; the torch cases are better resolved (flat ratio). r < 1 mm is
UNMEASURED — E ∝ J₁ ∝ r is ~1% of peak and 1 mm elements do not resolve it.

⚠️ **The quartz-vs-empty bore field is non-monotonic in ε** (1 → 3.78 → 11.6
gives 2.34 → 2.20 → 2.59 at r = 8.2 mm). Within the error band, and no mechanism
is claimed. Flagged, not explained.

🔴 **This run also found that `eigen_cfg` solves every torch as VACUUM** — see
FINDINGS 2026-08-23. Run 1 of this rig measured a +0.06 MHz shift for sapphire
because of it. The fix is local to `h4_field`; the general fix in `eigen_cfg` is
still outstanding, and any other eigen rig with a torch is still solving air.

### 2026-08-22 — radius-resolved E/N, and why Argon changes the answer

Leg 2 above quotes a single bore-averaged **7.0 Td for TE011 at 3 kW**. That
average hides a 4× radial variation, and the variation is what decides igniter
placement. At 1 kW, E_rms(r) from the measured Q₀ = 44,384:

| r | kV/cm rms | E/N @300 K | E/N @5000 K | E/N @10,000 K |
|---:|---:|---:|---:|---:|
| 3.0 mm | 0.78 | 3 Td | 53 Td | 106 Td |
| 6.5 mm | 1.68 | 7 Td | 114 Td | 228 Td |
| 8.5 mm | 2.17 | 9 Td | 148 Td | 296 Td |

**Breakdown is not the obstacle for an ARC.** A 1 atm N₂ spark reaches 10–20 kK,
putting E/N far above threshold even at r = 3 mm. The open question is
**HANDOVER**: when the arc stops, can the field deposit power fast enough to hold
the channel against recombination? That is a coupling question — `h4_seed.py`.

⚠️ **The Argon corroboration in Leg 2 is now sharper, and MEASURABLE against a
threshold.** Ar breaks down at ~1.5–4 kV/cm at 1 atm / 2.45 GHz vs ~30 kV/cm for
N₂/air. The cavity gives 2.17 kV/cm at r = 8.5 mm, so **Ar may already be over
threshold inside the torch at 1 kW with no arc enhancement**, while the cavity
peak (7.0 kV/cm) stays far below air's 30 — nothing breaks down outside the
torch. 🔴 But the conclusion is threshold-sensitive across the literature range:
at 1.5 kV/cm the field suffices for r > 5.8 mm (inside the torch); at 4.0 kV/cm
it needs r > 16.4 mm (**outside** it, so no ignition). Per H4's own warning about
MP-AES figures entering unexamined — **look up the Ar breakdown field; do not
lean on this.**

⚠️ **Corrected 2026-08-22**: MICAP-OES runs at **1 kW with Argon ignition**, not
1.5 kW. I had written 1.5 kW and drawn an inference from it. This is the second
time an MP-AES/MICAP figure entered this record unverified — the first was the
20 slm ceiling, which H4 already flags.

---

### The original H4, retained as provenance — the TM-companion analysis

🔴 **2026-08-22: does ignition need a TM mode at all?** Everything below assumes
the OPERATING mode must also break down the gas. That assumption has never been
examined, and it may be false.

**The two thresholds are different, and H4 conflated them:**

| | requirement | can TE011 do it? |
|---|---|---|
| **cold breakdown** | ~30 kV/cm for N₂ at 1 atm | 🔴 NO — TE011 gives ~1.1 kV/cm in the bore at 1 kW, **27× short** |
| **sustaining a seeded discharge** | far lower, and field redistributes once conductive | ⚠️ **UNMEASURED — this is H3** |

Essentially no plasma source asks its operating mode to do the breakdown. ICP
torches seed electrons with a Tesla coil applied EXTERNALLY through the quartz;
the operating field then sustains. If ignition is auxiliary, the whole in-band
companion architecture below is unnecessary.

🔑 **AND THE GEOMETRY INVERTS IN OUR FAVOUR.** TE011's on-axis field null — the
exact reason it cannot ignite — is what makes an on-axis igniter nearly
invisible to it: only ~0.1% of TE011's energy is in the bore. The converse
reinforces it: an axial conductor strongly perturbs any TM0n mode (E_z is
maximum on axis), which is the same physics as the TDS-shorting objection that
already rules TM out for OPERATION. An axial igniter is compatible with TE011
and incompatible with TM.

**What dropping the TM-ignition premise would buy:**
- the groove / TM-ignition conflict **evaporates** (see FINDINGS 2026-08-22) —
  the mode filter returns to the TE-only case, which is SOLVED
- **D/L stays at H1's optimum 1.525** instead of being dragged to 1.141 or 2.431
  to place a companion in band
- no in-band companion → no 50 MHz near-rival → **no tuning plunger**
- the ~100 MHz band constraint relaxes entirely

**To settle it, cheapest first:**
1. **Does an on-axis conductor perturb TE011?** One eigen solve, ~165 s, all
   machinery exists. Decides igniter placement.
2. **What do comparable instruments ACTUALLY use to ignite?** External and
   verifiable. ⚠️ Verify, do not inherit — MP-AES and MICAP numbers have already
   leaked into this record as unexamined assumptions (the 20 slm ceiling).
3. **Can TE011 SUSTAIN a seeded discharge?** H3 — and under this reframe H3 is
   no longer one gate among several, it is THE question the architecture turns on.

⚠️ The 1.1 kV/cm above is a COLD-CAVITY number. It shows TE011 cannot
cold-ignite and nothing more: once plasma exists it is conductive, the field
redistributes completely, and that calculation does not apply.



🔴 **TM ignition at a single 2.45 GHz source is FALSIFIED, analytically.** Only
m=0 TM modes have on-axis E_z (J_m(0)=0 unless m=0). TM010 and TM011 can **never**
be degenerate with TE011 at any D/L (χ₀₁ < χ′₀₁ with an identical axial term).
TM012 can — at **D/L = 1.0964**, which is exactly the pole that destroys TE011
purity. On-axis field and TE011 operation are mutually exclusive at one frequency.

⚠️ Not falsified in general. Two routes remain open, and BOTH are BLOCKED on
the same missing measurement.

**In-band companion.** Ignite on a TM mode, transition to TE011, *then* introduce
the sample — so the TDS shorting objection does not apply during ignition. A
companion can be placed at 2.500 GHz, 50 MHz from TE011 and inside the LDMOS
band: TM012 at D/L 1.141 (TE011 bore coupling 0.484%) or TM020 at D/L 2.431
(0.185%). TM012 dominates. But an in-band companion IS a near rival — 50 MHz
instead of 333 — and a tuning plunger is the only way to have both (cheap here:
TE011 has no axial wall currents, so a sliding short costs almost no Q).

**Second source.** TM010 at 1.32 GHz, TM011 at 1.82 GHz. Cost and architecture,
not physics.

🔴 **NO LONGER BLOCKED — AND H3'S ANSWER KILLS IT (2026-08-23).** This was
waiting on how far plasma loading moves TE011, on the stated criterion that *"at
50 MHz of margin, a loading shift larger than that converts the companion into a
collision."* Measured: **+31.6 MHz, with a loaded linewidth of 15.2 MHz.** The
pull eats 63% of the margin and the two resonances then overlap within a
linewidth. **The in-band companion is dead on its own declared test** — a third
independent leg, after the m-blindness of the annular filter and the failure of
every mode to cold-ignite.

**Second source** (TM010 at 1.32 GHz, TM011 at 1.82 GHz) is untouched by this;
it remains cost and architecture, not physics. Auxiliary/thermal-kernel ignition
remains the adopted route and needs neither.

## H5 — the optical path to LOD · **NOT STARTED · TERMINAL**

`LOD = 3σ_background / sensitivity`. Everything above serves this. Reached through
exactly two doors: **delivered power** (H3) and **the optical path**.

⚠️ Blocked on external inputs, not on simulation: spectrometer f-number (sets
viewport, trap AND lapped-zone length), uniformity spec, cavity temperature rise,
coolant interlock.

---

## Retired

**E1 — the loading measurement · WITHDRAWN, ill-posed.** It moved torch and filter
permittivity together, so no shift it produced was attributable, and it tried to
track a mode across a perturbation large enough to force crossings. Deleted
2026-08-21; the design point survives as a three-line calculation. What it
established: mode identity across a large perturbation needs **continuation**, not
endpoint pairing; and TM020 under an on-axis dielectric is not perturbed but
rebuilt (19–26% of f₀).

**H2 — ⚠️ THE "RETIRED / PREMATURE" ENTRY THAT WAS HERE IS WITHDRAWN.**
H2 is ANSWERED and live — see its section above. What follows explains how it
came to be mislabelled, because the mechanism will recur.

### 🔑 The renumbering artifact, in full

**H2 and H3 were SWAPPED.** The sustainment question — cold / hot / loaded — was
originally **H2**. It could not be answered without characterising the groove
first, so the groove question became H2 and sustainment became H3.

🔴 **The swap moved the NUMBERS. The status labels stayed with the numbers, not
with the questions.** Old-H2 (sustainment) genuinely *was* premature — asked
before the groove existed to answer it. That "premature" verdict remained
attached to the label "H2" and was then re-rationalised onto the groove, which
had already answered its own question.

🔴 **And the rationalisation invented a criterion.** The retired entry claimed
H2's target was *"TM111 far enough to draw no power"*, which *"depends on plasma
loading (H3, unmeasured)"*. **That was never H2's criterion.** H2's criterion was
the **LDMOS tuning range** — a hardware constraint requiring no plasma
measurement — and it was MET: TM111 pushed 64.25 MHz, clearing the 50 MHz band.
FINDINGS' own heading: *"The shallow regime works, and it is enough."*
**A harder, unanswerable criterion was substituted for the real, satisfied one,
turning a completed result into an open question.**

✅ **What should have happened:** everything after H1 dropped, and H2 recorded
fresh as the groove question. A DROP forces re-derivation; a SWAP preserves
history that is now misattached — and misattached history is worse than absent
history, because it reads as authoritative.

### The downstream cost

Believing H2 unanswered made the groove look optional. `GEO` never carried it,
31 rigs inherited a groove-free cavity, and a full day of H3 measured a cavity
nobody is building — while I treated the resulting extra in-band modes as puzzles
to solve rather than as the alarm they were (§7i).

## H6 — *(dissolved 2026-08-23 into H3's loaded regime)*

I opened H6 on 2026-08-23 for "sustainment under sample delivery". **That was a
hypothesis I invented while chasing a groove-free H3, and it should not have
existed** — sample delivery is one of H3's three regimes, not a question of its
own. Folded back into H3; nothing is lost because everything it measured was
groove-free and is discarded anyway.

🔑 The number is not reused. Gaps beat broken citations.
