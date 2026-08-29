# control-loop — the source, the match, and the control that drives them

**Opened 2026-08-24.** The cavity side is `experiments/resonance/`. This
programme is everything between the LDMOS and the coupling loop: frequency
acquisition and tracking, impedance matching, and the control that runs both.

🔴 **NOTHING HAS BEEN MEASURED HERE YET.** Every number below was DERIVED from
resonance's cavity measurements and had nowhere to live until now. Treat this
directory as a statement of the problem, not a body of results.

---

## Why it was opened

The requirement fell out of resonance's work and kept accumulating with no home:
tuner range, VSWR, dump-load duty, frequency slew, acquisition bandwidth. Worse,
**"the LDMOS tuning band" was cited as a hardware anchor a dozen times in the
resonance record without a single line saying what the LDMOS is.**

⚠️ It is also a genuine tangent to resonance's queue. **Opening a directory is
not a commitment to work it now** — see *When to come back*.

## What we have

**`SOURCE.md`** — the full characterisation, moved here from `resonance/`. Every
line marked **STATED** (from the user) · **DERIVED** (a requirement the cavity
measurements impose) · **ASSUMED** (no provenance).

The load side, all from measurement:

| | |
|---|---|
| f₀ locus, cold → 1e20 | **2.4515 → 2.4824 GHz** (+30.9 MHz slew at ignition) |
| cold linewidth | **0.35 MHz** (Q_L 7,004) |
| loaded linewidth @1e20 | **16.0 MHz** (Q_L 155) |
| β range | **4.715 → 0.017** — a factor of **275**, crossing 1 at n_e ≈ 5×10¹⁶ |
| VSWR | **4.7 → 99.3**, worst MID-range (Q₀ minimises near 1e19) |
| load-side at 1 kW matched | ✅ **39–42 A**, or **1.9–2.1 kV** on the high-Z branch *(MEASURED 2026-08-25; was 34–45 A from interpolated β)* |
| circulator dump | up to **961 W of 1 kW** unmatched |

**Architecture (STATED):** dual directional coupler at the LDMOS output reading
forward and reflected · frequency sweep + PID to minimise reflected · a magnitude
tuner · circulator.

### Three findings worth having up front

0. 🔴🔴 **THE COUPLING REQUIREMENT IS BIMODAL, AND NO FIXED LOOP MEETS IT.**
   β = Q₀/Q_ext, and **Q_ext is the coupling loop and nothing else.** Cold wants
   Q_ext = **43,422** (Q₀ = 43,422); loaded at the anchored density wants
   **109**. **The two states want couplers ~400× apart.** Every β and VSWR
   quoted below is therefore **a consequence of a loop we chose**, not a property
   of the cavity (`../resonance/CONVENTIONS.md` §7am).
   🔑 **This restates requirement 1 correctly:** the tuner was being asked to
   absorb a 400× swing **that the coupler could absorb part of, and nobody asked
   the coupler.** Whether it can is one cheap eigen sweep — see there.
1. 🔴 **THE HARD PART IS COLD ACQUISITION, NOT LOADED TRACKING.** Cold, the
   resonance is **0.35 MHz wide in a 100 MHz band** — ~1,000 blind steps, before
   anything has ignited. Loaded it is 16 MHz, **45× easier**. And cold is EASY to
   match (VSWR 4.7) while hot is HARD (VSWR 99). **The two loops do not peak
   together.**
2. 🔴 **MAGNITUDE TUNING IS UNSOLVED.** Four PIN-diode candidates evaluated and
   rejected (`SOURCE.md` §4d). The reason is **structural**: low C_j needs a
   small die, a small die has high thermal resistance, **so the parts that work
   at 2.45 GHz cannot carry 39–42 A.** Not a sourcing failure.
3. 🔑 **A MAGNITUDE-ONLY DETECTOR INHERITS RESONANCE'S OWN §7x ERROR.** |Γ|
   cannot distinguish β from 1/β. Either side of the ignition crossing reads
   −13.98 vs −13.99 dB: identical reflected power, **opposite tuner directions.**
   Downconvert both coupler ports coherently and use complex Γ.
   ✅ **NAMED 2026-08-25: an RF PHASE DETECTOR** (user). At f₀, Γ = (β−1)/(β+1)
   is REAL, so β and 1/β differ by exactly **180°** — **±45° resolution is
   ample**, and coupler directivity (even 20 dB) clears our operating points by
   16–20 dB. 🔴 **But at β = 1 the reflected wave vanishes and there is no phase
   to read**, so the crossing must be caught by the |Γ| minimum and applied by a
   state machine. See `SOURCE.md` § RF PHASE DETECTOR.

## What's needed

| | | status |
|---|---|---|
| **1** | **A magnitude-matching approach that survives 39–42 A at 2.45 GHz** | ✅✅ **MATERIALLY CHANGED 2026-08-25 — see `../resonance/` § ITEM 7 STEP 2c.** A **series capacitor in one loop leg** drives Q_ext **8,716 → 322 (27×)**, measured. At the design bore that is **VSWR 83 → 3.1 loaded**, and tuner current goes as √VSWR, so **~40 A → ~8 A**. 🔴 **BUT THE TARGET IS NOW CONTESTED:** Q_ext serves cold AND loaded, whose Q₀ differ 265×, and optimising the loaded match takes cold ignition power from 556 W to 45 W. The minimax fixed loop is Q_ext ≈ 1,700 (VSWR ~16 both). **Which is right depends on `../ignition-options/`.** ⚠️ Original verdict retained: 🔴 UNSOLVED. No verified option. ⚠️ And see the loop question below — the requirement itself is not yet final. |
| **2** | Frequency acquisition of a 350 kHz resonance in a 100 MHz band | not designed |
| **3** | Complex-Γ sensing (vs magnitude-only) | argued, not designed |
| **4** | Tuner SPEED requirement | 🔴 **NOT DERIVABLE** — set by ignition dynamics, which no programme here has measured. Everything in resonance is steady-state. |
| **5** | Two-loop interaction (tuner moves the apparent reflected minimum) | unaddressed |

## 🔑 The two questions that gate all of it — and they live in `resonance`

**Both could REMOVE requirement 1 rather than satisfy it, and both are queued
there for cavity reasons anyway:**

- ✅ **ANCHORED 2026-08-24 — and it made the requirement WORSE.** n_e = **7.3–8.6
  × 10¹⁸** from a measured N₂ MICAP gas temperature of **5220–5270 K** (Kuonen
  et al., *JAAS* 39(5) 2024, Table 2, pressure-reduction method — the only
  empirical one of the three). The assumed 1e20 was **13× too high**.
  ✅ **MEASURED 2026-08-25, and MILDER than the interpolation said: VSWR
  75–82** at the anchor (not 80–89), **39–40 A** (not ~42), worst case **90 at
  3e19** (not 99.3 at 1e19). **Design to ~90:1.** See `SOURCE.md` §4f.
  🔑 **Two requirements got materially EASIER:** ignition slew **+7.1 MHz**, not
  +30.9 (that came from assuming 1e20), and the loaded resonance is **1.5×
  WIDER** at 23.8 MHz.
  ✅ Band margin went the other way: **17.6 → 41 MHz.**
- ✅✅ **COUPLER — ANSWERED 2026-08-25, and the answer is LARGE.** The loop
  was never designed; it has now been swept across mount, flange and series
  gap. **Q_ext 8,716 → 322 measured, a 27× lever, on a machined gap.** The 4.2×
  this document calls "an open question" is comfortably exceeded, and **β = 1
  (84×) is no longer obviously out of reach** — it is 3.1× away. 🔴 **The
  remaining question is not CAN it, but SHOULD it: see the cold/loaded trade
  above and `../ignition-options/`.**
- ⚠️ **Coupler — the ORIGINAL entry, retained:** ❌ Aperture coupling is
  out (patented; and this cavity IS the waveguide, so there is no shared wall to
  cut an iris in). 🔴 **But the LOOP was never designed** — it was forced into
  existence so driven solves would have a port, and only its AREA was ever swept,
  at fixed wire radius, cap radius, turn count and shape. **Q_ext = 9,231 is the
  floor of ONE arbitrary family.**
  🔑 **VSWR 85 → 20 needs Q_ext only 4.2× lower** — the difference between "no
  part exists" and "a standard tuner works". β = 1 needs 84× and is out of reach.
  **Whether loop design can deliver 4.2× has never been asked.**

## Rules

This programme inherits `resonance/CONVENTIONS.md`. The domain-general ones
already cost real work and apply directly here:

- **§7ab** — a value chosen for solvability must never become "the operating
  point". `n_e = 1e20` did, over six citations.
- **§7ac** — never mix a verified analysis with an unverified suggestion in one
  register. This document marks STATED / DERIVED / ASSUMED for that reason.
- **§7s** — provenance is what a rig DID, not reasoning added afterwards.
- **§7x** — |Γ| cannot pick the coupling branch. **The hardware has this problem
  too**, not just the solver.
- **§7z / §7aa** — state the effect size that would matter, and report argmax
  rather than endpoints. Three turning points have been found so far and two
  were misread.

## When to come back

⚠️ **RE-ENTRY CONDITION PARTLY MET 2026-08-24 — and I had called it fully met.**
✅ n_e is anchored **and now MEASURED at the operating point (2026-08-25):
VSWR ~90:1 worst case, 75–82 at the anchor, 39–42 A, 1.9–2.1 kV, ~950 W dump.**
⚠️ Harder than cold, but **milder than the interpolated figures this programme
was parked on.**
🔴 **But the second lever is NOT spent.** The aperture CLASS is closed; the
**loop was never designed** (`../resonance/CONVENTIONS.md` §7al). Q_ext = 9,231
is the floor of one arbitrary family — area swept, everything else frozen at
values two of which have no provenance at all.

🔑 **THE SIZING DECIDES WHETHER THAT MATTERS:**

| target | VSWR | Q_ext needed | vs 9,231 | verdict |
|---|---:|---:|---:|---|
| as built | 85 | 9,350 | 1.0× | — |
| **3-stub tuner is comfortable** | **20** | **2,200** | **4.2×** | 🔑 **open question** |
| matched | 1 | 110 | 84× | ❌ out of reach for a loop |

**Requirement 1 is unsolved for the loop AS BUILT. It is not established that it
is unsolved for a DESIGNED loop** — 4.2× is the difference between "no part
exists" and "buy a standard tuner". **Do not open magnitude-tuner design work
until the loop family question is answered**, because it could still move the
requirement out of the impossible region.
