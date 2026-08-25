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
| target elements, detection limits | 🔴 **not stated anywhere** |
| required T_gas | ✅ **ANCHORED to MICAP: 5220–5270 K** (2024 JAAS, pressure method) |
| required n_e | ✅ **7.3–8.6e18**, derived from T_gas by Saha |
| working gas: **N₂** | ⚠️ treated as a hard anchor by resonance |
| gas flow **≤ 20 slm N₂** | 🔴 **ASSUMED** — taken from what MP-AES and MICAP happen to use. Not optimised, and the chain slm → bore radius → coupling → input power rests on it |
| torch geometry: **Fassel** | 🔴 **ASSUMED, WRONG GAS** — the standard Fassel torch is **Argon**-optimised. No Nitrogen-optimised torch geometry is in the record |
| sample: soil extracts, **high TDS** | mentioned; never quantified |
| power ~1 kW | ⚠️ "a stated reference, not a design point" |

🔑 **Three of those are inherited from instruments that are not this one.** The
flow, the torch and the gas choice arrived together from MP-AES/MICAP practice,
and resonance has been building on all three.

## What's needed

| | | why it blocks |
|---|---|---|
| ~~1~~ | ~~The required gas temperature~~ | ✅ **ANSWERED** — 5220–5270 K, anchored to MICAP |
| 2 | Target elements + detection limits | sets 1 |
| **3** | **Whether LTE is fair** | 🔴 **now the top open item.** Non-LTE puts n_e ABOVE Saha — and since VSWR peaks near 1e19, that pushes the tuner requirement further toward the worst case |
| 4 | High-TDS tolerance, quantified | sample introduction, and the torch bore |
| 5 | Is 20 slm N₂ right, or inherited? | the whole flow → geometry → power chain |
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
