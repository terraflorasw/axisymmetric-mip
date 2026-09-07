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
| 2 | **The required residence time** | 🔴 LOD is still not stated anywhere. Until it is, "equal residence to 20 slm" is the only reference available, and it is itself inherited |
| 3 | Does a N₂ MIP sustain at 10–12 slm? | not asked |
| 4 | Nitrogen generator duty/purity at each flow | not asked; the generator, not just the compressor, may set the floor |
| 5 | Is a Fassel bore right for N₂? | `../spectroscopy/` item 6 |

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
