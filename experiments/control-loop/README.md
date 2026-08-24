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
| load-side at 1 kW matched | **34–45 A**, or **1.7–2.2 kV** on the high-Z branch |
| circulator dump | up to **961 W of 1 kW** unmatched |

**Architecture (STATED):** dual directional coupler at the LDMOS output reading
forward and reflected · frequency sweep + PID to minimise reflected · a magnitude
tuner · circulator.

### Three findings worth having up front

1. 🔴 **THE HARD PART IS COLD ACQUISITION, NOT LOADED TRACKING.** Cold, the
   resonance is **0.35 MHz wide in a 100 MHz band** — ~1,000 blind steps, before
   anything has ignited. Loaded it is 16 MHz, **45× easier**. And cold is EASY to
   match (VSWR 4.7) while hot is HARD (VSWR 99). **The two loops do not peak
   together.**
2. 🔴 **MAGNITUDE TUNING IS UNSOLVED.** Four PIN-diode candidates evaluated and
   rejected (`SOURCE.md` §4d). The reason is **structural**: low C_j needs a
   small die, a small die has high thermal resistance, **so the parts that work
   at 2.45 GHz cannot carry 34–45 A.** Not a sourcing failure.
3. 🔑 **A MAGNITUDE-ONLY DETECTOR INHERITS RESONANCE'S OWN §7x ERROR.** |Γ|
   cannot distinguish β from 1/β. Either side of the ignition crossing reads
   −13.98 vs −13.99 dB: identical reflected power, **opposite tuner directions.**
   Downconvert both coupler ports coherently and use complex Γ.

## What's needed

| | | status |
|---|---|---|
| **1** | **A magnitude-matching approach that survives 34–45 A at 2.45 GHz** | 🔴 **UNSOLVED.** No verified option. |
| **2** | Frequency acquisition of a 350 kHz resonance in a 100 MHz band | not designed |
| **3** | Complex-Γ sensing (vs magnitude-only) | argued, not designed |
| **4** | Tuner SPEED requirement | 🔴 **NOT DERIVABLE** — set by ignition dynamics, which no programme here has measured. Everything in resonance is steady-state. |
| **5** | Two-loop interaction (tuner moves the apparent reflected minimum) | unaddressed |

## 🔑 The two questions that gate all of it — and they live in `resonance`

**Both could REMOVE requirement 1 rather than satisfy it, and both are queued
there for cavity reasons anyway:**

- **Anchor n_e.** It has no physical provenance — its origin is *solver
  convergence* (resonance CONVENTIONS §7ab). VSWR spans **15.6 → 99.3** across
  the plausible range and the current demand goes as **√VSWR**: 17.7 A at 1e18
  against 44.6 A at 1e19. **This is a hardware-cost decision.**
- **Test the coupler class.** `geometry.py`'s *"iris-free route… no coupling
  structure"* was a docstring decision, never a measurement. **Q_ext floors at
  9,231 for a loop**, so loop size cannot reduce the mismatch — but an
  iris/aperture might, and `h3_loopq`'s eigen-pair method measures Q_ext for any
  coupler the mesher can build.

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

⏸️ **PARKED.** Re-entry condition: **n_e anchored**, or **a coupler class
measured that floors Q_ext below 9,231.**

🔴 **Do not open design work before then** — the requirement could move 3× in
current, or disappear.
