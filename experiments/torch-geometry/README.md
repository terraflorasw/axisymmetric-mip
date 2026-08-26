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
| **EM / RF** | bore sets how strongly the plasma loads TE011, so it sets β and VSWR | `../resonance/` |
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

| flow | bore for EQUAL residence | residence | Q₀ | β | **VSWR** | siting |
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
