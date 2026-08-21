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
divides) · `withdrawn` (ill-posed, and not replaced)

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

## H2 — which mode filter defeats TM111 · **OPEN**

The only mode still needing suppression once H1 is chosen.

| | annular groove | dielectric brake |
|---|---|---|
| acts on | **wall currents** | fields at the end cap |
| discriminates because | TE011 has NO end-cap surface current (H is purely axial there, so n×H = 0); TM111 has radial cap current crossing the slot | — |
| loads the cavity | no | yes, ε=3.78 |
| free parameters | width, depth | thickness, ε |

🔑 **The groove has a formula, not a search space.** The slot is a shorted stub;
its mouth presents `Z_in = jZ₀·tan(βd)`, so **d = λ/4 = 30.59 mm** is an open
circuit and blocks the current, and **d = λ/2** makes it invisible. Predicted
optimum 30.6 mm, effect ∝ tan(2πd/λ), **inverting past λ/4** — a sharp falsifier.
Width sets Z₀ ≈ η·gw/(2πa) and the Q cost, not the resonance. One depth sweep
around a predicted point, plus a width sweep for Q only.

⚠️ **The brake is weakly coupled to the mode it targets.** A dielectric on a
conductor with **normal** E has the field expelled (D continuous ⇒ E/εᵣ inside),
giving an εᵣ² ≈ 14× lower sensitivity than tangential E. TM0n0 **and TM111** are
both normal-E at the caps. That is consistent with the observation that the brake
never moved TM020.

**Target**: TM111 far enough to draw no power at 2.45 GHz. Loaded linewidth is
~134 kHz, so **~10 MHz is ~75 linewidths** — ample. The question is the minimum
depth that reaches it, and what it costs in Q.

**Precondition**: no torch, no viewport. An axisymmetric cavity keeps TE0n and
TM0n from hybridising — the mechanism that made E1b's modes uninterpretable.

## H3 — the loaded cavity · **NOT STARTED · BLOCKS H4**

How far does an operating plasma move TE011, and what does it do to Q and to the
mode landscape? A conductive column is a much stronger perturbation than a
dielectric tube, and nothing trustworthy exists: E1b failed three times trying to
measure a *dielectric* shift and was retired.

Also here: β, Q_ext, S11 — driven coupling is unmeasured (E0k compared only the
resonant frequency). LOD runs through delivered power, so this is on the critical
path, not an optimisation.

⚠️ Mode identity across a perturbation this large needs **continuation**, not
endpoint pairing — that is E1b's one durable lesson.

## H4 — ignition · **OPEN, one route analytically closed**

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

🔴 **BLOCKED ON H3.** Every version of this turns on how far plasma loading moves
TE011. At 50 MHz of margin, a loading shift larger than that converts the
companion into a collision. E1b never produced a trustworthy loading number, and
a conductive plasma is a far stronger perturbation than the dielectric tube it
failed to measure. **Characterise the plasma perturbation before spending
anything else on ignition architecture.**

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
