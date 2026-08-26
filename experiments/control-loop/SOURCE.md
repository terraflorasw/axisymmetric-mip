# SOURCE — the LDMOS, the tuner, and the control loop

**Created 2026-08-24 because this side of the machine was never written down.**
The programme has characterised the cavity (H1), the mode filter (H2), the
coupler and the plasma. **It has referenced "the LDMOS tuning band" as a hardware
anchor a dozen times without a single line saying what the LDMOS is.** Every
requirement below was derived from cavity measurements that had nowhere to land.

⚠️ **THIS DOCUMENT IS MOSTLY HYPOTHETICAL AND SAYS SO PER LINE.** Three tiers:
**STATED** (from the user) · **DERIVED** (a requirement the cavity measurements
impose) · **ASSUMED** (used by the programme with no provenance — treat as
§7ab).

---

## 1. Architecture — STATED (user, 2026-08-24)

    LDMOS ──> circulator ──> PIN-diode tuner ──> coupling loop ──> cavity
                  │                 ▲
              dump load             │  magnitude
                  │                 │
         dual directional coupler ──┘
         (forward + reflected)  ──> PID ──> LDMOS frequency

- **Dual directional coupler** at the LDMOS output, reading forward and
  reflected power.
- **Frequency sweep + PID** relocating to minimum reflected power.
- **PIN-diode tuner** matching magnitude.
- **Circulator** protecting the LDMOS.

✅ **Two degrees of freedom, which is what a complex match needs.** At resonance
the cavity is purely resistive, so **frequency zeroes the REACTANCE** and the
**PIN tuner transforms the RESISTANCE**. Sound in principle.
⚠️ The two loops interact: the PIN tuner changes the impedance the coupler sees,
which moves the apparent reflected-power minimum. A standard coupled-loop
control problem, not addressed here.

---

## 2. What the cavity REQUIRES of it — DERIVED, with sources

| requirement | value | from |
|---|---|---|
| **frequency span** | f₀ = **2.4515 → 2.4824 GHz** | `h3_driven`, cold → 1e20 |
| **frequency slew during ignition** | **+30.9 MHz** | same |
| **frequency resolution** | **≲ 100 kHz** (see §3) | cold linewidth 350 kHz |
| **match range** | **β 4.715 → 0.017 — a factor of 275** | `h3_loopq` + `h3_driven` |
| **worst VSWR** | **99.3, at n_e ≈ 1e19** — and the ANCHORED density is 7.3–8.6e18, just below it (§4f) | Q₀ minimum |
| **match direction** | **REVERSES** — over → under at n_e ≈ 5×10¹⁶ | β crosses 1 |
| **circulator dump** | up to **961 W of 1 kW** unmatched | Γ² at worst VSWR |
| **LDMOS load-pull** | must survive VSWR ~99 behind the circulator | same |

🔴 **THE MATCH RANGE IS THE HARD SPECIFICATION.** ~58:1 impedance transformation
at 1e20 and ~99:1 at 1e19. **Whether any tuner covers that at kW is the single
most load-bearing unknown on this side of the machine** — and it is answered by
sourcing against §4b's requirement, not by a solve. **No part is assumed here.**
⚠️ **VSWR is NON-MONOTONIC in density** — worst mid-range, not at the top. So is
the dump-load duty. Do not size either from the endpoints.

---

## 3. 🔴 THE HARD PART IS COLD ACQUISITION, NOT LOADED TRACKING

**This inverts where the attention has been going.**

| state | f₀ | Q_L | linewidth | as % of a 100 MHz band |
|---|---:|---:|---:|---:|
| **cold** | 2.4515 | 7,004 | **0.35 MHz** | **0.35%** |
| 1e18 | 2.4520 | 557 | 4.40 MHz | 4.4% |
| 1e20 | 2.4824 | 155 | 16.02 MHz | 16.0% |

🔴 **COLD, the resonance is 350 kHz wide inside a 100 MHz band.** A blind sweep
needs ≲100 kHz steps not to step over it — of order **1,000 points** before
anything has ignited.
✅ **LOADED it is 16 MHz wide — 45× easier** to find and to hold.

🔑 **So the control problem is hardest BEFORE the plasma exists**, and easiest
once it does. That is worth designing for explicitly: a slow careful cold
acquisition, then a fast tracking loop once the linewidth opens up.
⚠️ And the cold cavity is **OVERCOUPLED (β = 4.715, VSWR 4.7)** — a comparatively
easy match. **The frequency loop is the difficult one cold; the magnitude loop is
the difficult one hot.** They do not peak together.

---

## 4. ASSUMED — no provenance, treat as §7ab

| assumption | used as | status |
|---|---|---|
| ~~band = 2.400–2.500 GHz~~ | a hardware constraint, everywhere | ✅ **ANCHORED 2026-08-24 (user): it is BOTH — the ISM allocation AND the part's bandwidth.** So it is immovable, and **out-of-band emission is a compliance limit** (§4a). No longer an assumption. |
| **P = 1 kW** | `P_REF` in five rigs | ⚠️ the code itself says *"a stated reference, not a design point"* — honest, and it means no power-derived number is anchored |
| tuning resolution / step | — | never stated; §3 says it matters |
| tuning slew rate | — | never stated; the ignition transient needs it |
| tuner match range | — | 🔴 **there is no "the" tuner yet.** A SKU is located FROM a requirement, not looked up. §4b states the requirement. |
| circulator isolation / dump rating | — | never stated; §2 gives the duty |
| LDMOS harmonic content | — | never considered. TE112 sits at 2.7827 GHz and other modes exist; a harmonic-rich source in a high-Q multi-mode cavity is worth one thought before it is dismissed |

---

## 4a. ✅ THE BAND — ANSWERED

**2.400–2.500 GHz is BOTH: the ISM allocation AND the LDMOS part's bandwidth**
(user, 2026-08-24). So it is **immovable** — not a procurement choice.

🔴 **Consequence, and it is not idle: out-of-band emission is a COMPLIANCE
limit, not just a tuning limit.** Harmonic content into a high-Q multi-mode
cavity (TE112 sits at 2.7827 GHz) has never been considered by any work here.
✅ f₀ reaches 2.4824 GHz at n_e = 1e20, so the measured locus fits with
**17.6 MHz** to spare — but the margin is a compliance margin.

## 4b. 🔑 REQUIREMENTS, BY COMPONENT — stated so SKUs can be sought

**Every number is MEASURED, DERIVED from a measurement, or flagged ASSUMED.
No part is assumed anywhere.**

### FIRM — measured, and these do not move

| quantity | value | source |
|---|---|---|
| f₀ locus, cold → 1e20 | **2.4515 → 2.4824 GHz** (span 30.9 MHz) | `h3_driven` |
| cold linewidth | **0.35 MHz** (Q_L = 7,004) | `h3_driven` |
| loaded linewidth @1e20 | **16.0 MHz** (Q_L = 155) | `h3_driven` |
| Q_ext (11×8 loop) | **9,231**, and it FLOORS there | `h3_loopq` |
| band | **2.400–2.500 GHz — ISM *and* the part's bandwidth** | user, 2026-08-24 |

### 🔴 CONDITIONAL — and the conditions are open questions, not details

| what | swings on | range |
|---|---|---|
| **the VSWR to match** | **where n_e actually is** (§7ab — unanchored) | **15.6 → 99.3**, worst MID-range |
| **whether the tuner tracks ignition** | a SEQUENCING choice, below | full 275× range vs **one impedance** |
| all absolute powers | P = 1 kW *(ASSUMED)* | scales linearly |
| tuner speed | **ignition dynamics — never measured here** | underivable |

### 1. TUNER

> 🔴 **READ §4d FIRST: MAGNITUDE TUNING IS UNSOLVED.** Four PIN candidates have
> been evaluated and rejected, for a STRUCTURAL reason. The line below is the
> REQUIREMENT, not a specification anything is known to meet.
>
> 📋 **REQUIREMENT —** *2.400–2.500 GHz, 1 kW CW forward: transform a purely-real
> load spanning VSWR 1:1 to 100:1 on both sides of 50 Ω, and survive ~1 kW
> reflected. Load side carries up to ~45 A or ~2.2 kV.*
>
> ⚠️ **Relaxed version, if the tuner is engaged only after ignition** (§4c):
> *…must transform a purely-real load of VSWR up to **90:1**, one side of 50 Ω.*
> 🔴 **REVISED UP 2026-08-24 from 60:1**, when n_e was anchored — see §4f. The
> steady-state requirement got HARDER, not easier.



1. **Frequency** — 2.4515–2.4824 GHz minimum; sensibly the full ISM band.
2. **Match range** — transform a **REAL** load (the frequency loop makes it real
   at resonance, so this is a segment of the real axis, not a 2-D region):
   - **steady-state only (see §4c): ONE impedance**, VSWR **15.6–99.3** depending
     on n_e — **58.4 at the currently-assumed 1e20**;
   - **full transient tracking: VSWR 4.7 → ≈100 AND crossing 50 Ω**, i.e. the
     sign of the transformation reverses.
3. **Power** — pass ~1 kW forward *(ASSUMED)*; survive up to **961 W returned**.
4. **Impedance resolution** — fine enough to land inside the target; a few % of
   the transformation is ample. ⚠️ **This is NOT the 350 kHz figure** — that is a
   FREQUENCY requirement on the LDMOS, not an impedance one on the tuner.
5. **Speed** — **only matters if it must track ignition.** See §4c.

### 2. LDMOS

1. **Tunable across ≥ 30.9 MHz** within 2.400–2.500 GHz, reaching 2.4824 GHz.
2. 🔴 **Frequency resolution ≲ 100 kHz** — it must ACQUIRE and HOLD a **350 kHz**
   cold resonance inside a 100 MHz band. **This is the tightest control number in
   the document** (§3).
3. **Power** ~1 kW *(ASSUMED — but η, β, Q and all margins are ratios and
   frequencies, so this assumption failing is cheap)*.
4. **Load-pull** — must survive whatever the circulator leaves of VSWR ~100.
5. 🔴 **Out-of-band emission — the band is ISM, so this is a COMPLIANCE limit,
   not just a tuning limit.** Harmonic content into a high-Q multi-mode cavity
   (TE112 sits at 2.7827 GHz) has never been considered here.

### 3. CAVITY TEMPERATURE SENSOR

🔑 **Added 2026-08-24. Small requirement, and it removes a search problem.**

✅ **MEASURED 2026-08-24 (`h3_hot`), not estimated:**

| T_wall | f₀ GHz | Δf | Q₀ | Q_ext | β | VSWR |
|---:|---:|---:|---:|---:|---:|---:|
| 293 K | 2.451633 | — | 43,422 | 9,231 | 4.704 | 4.7 |
| 393 K | 2.445935 | **−5.70** | 36,374 | 9,194 | 3.956 | 4.0 |
| 493 K | 2.440206 | **−11.43** | 31,938 | 9,229 | 3.461 | 3.5 |

🔑 **Q_ext IS THERMALLY INVARIANT** (×0.996, ×0.9997) while Q₀ falls ×0.838 per
100 K. **So β tracks Q₀ alone, and one temperature reading gives BOTH derived
quantities**: f₀ = f₀(cold) − 5.70 MHz × ΔT/100, and β = Q₀(T)/9,215.
⚠️ Wall heating is slow (minutes), so this is not a fast-tracking problem — but
**a search window centred on the cold f₀ would miss a warm cavity**, and
first-start and restart begin at different frequencies.

1. **A wall temperature reading**, resolution ~10 K (≈0.6 MHz of detuning).
2. Used to compute f₀ ≈ f₀(cold) − 5.7 MHz × ΔT/100 as the **acquisition
   starting point**, instead of searching a 100 MHz band blind.
⚠️ **Unloaded only, for the MATCH.** Measured: unloaded β 4.704 → 3.956 at
+100 K → 3.461 at +200 K. **Loaded, the plasma is ~275× the wall loss and β does
not care.** ⚠️ Note the unloaded VSWR IMPROVES with heat (4.7 → 3.5), the
opposite direction to the loaded requirement.
🔑 **Thermal pulls OPPOSITE to the plasma** (−5.7 vs +30.9 MHz), so heating
partially cancels the loading shift and **buys back band margin**.

### 4. CIRCULATOR

1. Frequency 2.400–2.500 GHz.
2. **Isolation** sufficient to protect the LDMOS at VSWR ~100.
3. **Dump load** — worst case **961 W of 1 kW forward** (at n_e ≈ 1e19).
   ⚠️ **Duty depends on the sequencing choice**: transient-only if the tuner
   matches steady state, **CONTINUOUS if no tuner covers the required VSWR.**

### 5. CONTROL LOOP

1. **Cold acquisition is the hard part** — 350 kHz needle, 100 MHz haystack,
   ~1,000 points at ≲100 kHz steps, before anything has ignited (§3).
2. **Then track +30.9 MHz** as the plasma forms.
3. **Loaded tracking is easy** — 16 MHz linewidth, 45× wider than cold.
4. ⚠️ **The two loops interact**: the tuner moves the impedance the coupler sees,
   which moves the apparent reflected-power minimum.
5. ⚠️ **A reflected-power minimiser passes a TRUE NULL** at n_e ≈ 5×10¹⁶, where
   β crosses 1. The match point is crossed, not approached.
6. 🔑 **A MAGNITUDE-ONLY DETECTOR INHERITS THE PROGRAMME'S OWN §7x ERROR.**
   |Γ| cannot distinguish β from 1/β — that is definitional, and this record
   demonstrates it: `fit_dip` read −3.67 dB and returned β = 0.208 when the truth
   was **4.804**. Either side of the β=1 crossing at ignition:

       cold side   beta 1.500  ->  -13.98 dB
       loaded side beta 0.667  ->  -13.99 dB

   **Identical reflected power, OPPOSITE tuner directions.** A magnitude-only PID
   is blind exactly where the tuner must reverse.
   ✅ **Downconverting BOTH coupler ports to a common IF and digitising them
   coherently gives complex Γ** — magnitude AND phase — so the loop knows which
   side of match it is on and can compute the tuner setting rather than search
   for it. The phase was already in our own port-S.csv and a diode detector
   would throw it away.
   ⚠️ **Register (§7ac): the branch argument above is DEFINITIONAL and
   demonstrated. A further idea — a wide-IF receiver to solve the 350 kHz cold
   acquisition in one look rather than ~1,000 steps — is UNVERIFIED architecture
   reasoning, and it needs a swept or broadband probe source, which a CW LDMOS
   is not.**

## 4f. 🔴 REQUIREMENT REVISED UP — n_e IS NOW ANCHORED, AND IT IS WORSE

**2026-08-24. `n_e` was the solver-convenience value `1e20`. It is now anchored
to a measured gas temperature, and the tuner requirement moved the WRONG WAY.**

**Anchor:** Kuonen, Hattendorf & Günther, *JAAS* **39**(5) 1388–1397 (2024),
Table 2 — **pressure-reduction method, N₂ MICAP: 5220 K / 5270 K.** Via LTE Saha
that is **n_e = 7.3–8.6 × 10¹⁸**, i.e. the assumed 1e20 was **13× too high**.
🔑 Only the pressure method is EMPIRICAL (it measures an interface pressure
ratio). The other two in that table infer T from the same MO⁺/M⁺ measurement
through different models and disagree by ~2×.

✅ **SUPERSEDED 2026-08-25 — THE ANCHOR BAND IS NOW MEASURED, NOT INTERPOLATED.**
`h3_driven` solved 7.3 / 7.9 / 8.6e18 directly (`../resonance/` item 8). The
column below marked *interpolated* was derived by interpolating across the
3e18→1e19 gap **and using a COLD Q_ext of 9,231 at every density**. β is now
taken from the **measured S11 dip**, which imports no Q_ext at all.

| | at 1e20 (assumed) | anchored, *interpolated* | **anchored, MEASURED** |
|---|---:|---:|---:|
| **VSWR** | 58.4 | ~~80–89~~ | ✅ **75–82** |
| load-side current @1 kW | 34.2 A | ~~40–42 A~~ | ✅ **39–40 A** |
| load-side voltage (hi-Z branch) | 1,709 V | ~~2,004–2,113 V~~ | ✅ **1,940–2,024 V** |
| circulator dump | 934 W | ~~951–956 W~~ | **948–952 W** |
| band margin | *17.6 MHz* | *40–41 MHz* | ✅ **41.4 MHz** |
| **ignition slew** | **+30.9 MHz** | — | 🔑 **+6.3 to +7.9 MHz** |
| **loaded linewidth** | 16.0 MHz | — | ✅ **23.0–25.0 MHz** |

🔑 **THE WORST CASE ACROSS THE WHOLE PLAUSIBLE RANGE IS NOW VSWR 90, AT 3e19** —
not 99.3 at 1e19. The peak is flatter and lower than the interpolation implied.
⚠️ **DESIGN TO ~90:1.** The anchor band's own upper end is 82; 90 covers the
whole grid with the density free to drift a decade.
✅ **Two requirements got materially easier and neither was expected to:** the
**ignition slew is 4.4× smaller** (+7.1 MHz, not +30.9 — that number came from
assuming 1e20), and the **loaded resonance is 1.5× WIDER** (23.8 MHz, not 16.0),
so the tracking loop has a broader target to hold.
⚠️ **Still a vacuum-torch cavity** — `GEO_DESIGN` carries `--no-torch` and
`h3_driven` meshes ε = 1. The design sapphire torch moves f₀ by ≈ −13.9 MHz
(which *widens* band margin to ≈ 55 MHz) and Q₀ by ≈ +2 %. **β and VSWR are
ratios and barely move.**

⚠️ **CAVEATS THAT TRAVEL WITH THE ANCHOR:** it is the plasma **as sampled through
the MS interface**, not the r = 2–8.5 mm annulus the EM model uses — different
region, and atmospheric plasmas have gradients. LTE is assumed, and non-LTE puts
n_e **above** Saha, which pushes VSWR further toward the peak.
✅ **Power is NOT a caveat**: an atmospheric plasma at 1450 W is BIGGER, not
hotter, so the paper's power vs this programme's 1 kW does not matter. Nor does
MS-vs-OES — same plasma, different detector.

## 4c. ✅ THE TUNER PROBABLY DOES NOT NEED TO TRACK IGNITION

**Delivered power with NO matching at all:**

| state | β | VSWR | delivered |
|---|---:|---:|---:|
| cold, pre-ignition | 4.715 | 4.7 | **57.7%** |
| β = 1 crossing | 1.000 | 1.0 | **100%** |
| 1e18 | 0.064 | 15.6 | 22.7% |
| 1e20 | 0.017 | 58.4 | 6.6% |

🔑 **COUPLING IS AT ITS BEST DURING IGNITION, NOT ITS WORST.** 58% enters cold,
it passes through a perfect match as the plasma forms, and only THEN collapses.
**The mismatch is entirely a steady-state problem.**

✅ **So the tuner can plausibly sit fixed through ignition and engage once the
plasma is established** — the circulator rides the transient, which is its job.
That reduces the requirement from *"275× range with a sign reversal, fast enough
to track plasma formation"* to **"match one steady-state impedance"**, and makes
the underivable speed requirement largely moot.
⚠️ **CONDITION: this assumes ignition succeeds at 58% coupling.** The record's
"no mode cold-ignites" claim is currently UNANCHORED (its source rigs were
groove-free), so **whether the cold field is sufficient is not established
here.** Confirm against the intended sequencing before relying on it.

## 4d. 🔴🔴 MAGNITUDE TUNING IS AN UNSOLVED PROBLEM

**STATE, 2026-08-24: no component or approach has been SHOWN to meet §4b.**
This section exists so that is on the record as an open problem rather than an
assumption that a part exists.

## 🔑 RF PHASE DETECTOR — the component that resolves β from 1/β

🔑 **User, 2026-08-25: *"We need an RF Phase Detector to distinguish Beta from
1/Beta in the control loop."*** ✅ **And the requirement is far cheaper than it
sounds, because at resonance the branch is a 180° flip.**

**At f₀ the reflection coefficient is REAL:** Γ = (β−1)/(β+1). So β and 1/β give
**identical |Γ| and opposite sign** — which is `resonance`'s §7x stated as
hardware, and why a power meter cannot ever resolve it:

| state | β | Γ | \|Γ\| | **arg Γ** | reflected of 1 kW |
|---|---:|---:|---:|---:|---:|
| **cold** (measured) | 4.774 | **+0.6536** | 0.654 | **0°** | 427 W |
| **anchor 7.9e18** | 0.0127 | **−0.9749** | 0.975 | **180°** | 950 W |
| 1e20 | 0.0171 | −0.9664 | 0.966 | 180° | 934 W |
| β = 1/4.774 | 0.2095 | **−0.6536** | **0.654** | **180°** | 427 W |

⚠️ **Note the last row: identical \|Γ\| to cold, opposite phase.** That is the
ambiguity, and phase is the only thing that breaks it.

### ⚠️ DOES THE DETECTOR RETIRE THE TUNER? Partly — and not on the part that killed it

**User, 2026-08-25: *"if we have an RF phase detector, then the old PIN diode
tuner becomes just a transistor."*** ⚠️ **Half right, and the half that is wrong
is the binding half.**

🔴 **SENSING IS NOT ACTUATING.** The detector says WHERE you are; something still
has to MOVE the impedance, and **the current it carries is set by P and Z alone:
I = √(P·VSWR/Z₀), independent of network topology.** A transistor carries the
same amps and dissipates in the same way. **The rejection was THERMAL** —
θ = 30 °C/W ⇒ 4.2 W ⇒ ~1.7 A from I²R_S in the ON state — **and a phase detector
removes no current.**

✅ **BUT IT DOES RELAX THE TUNER, GENUINELY — the CONTROL problem, not the POWER
problem.** Without phase you must **hill-climb on |Γ|**: continuous fine steps,
and it can **stall or reverse at the β ↔ 1/β ambiguity**. With complex Γ you
**solve** for the transformation in one shot, so **a SWITCHED tuner with a few
computed states replaces a continuously-variable one.** That is a real
simplification, and it is the sense in which "just a transistor" is right.

🔑 **AND THE LEVER THAT DOES ATTACK THE CURRENT IS THE COUPLER, because
I ∝ √VSWR:**

| VSWR | load current | vs GC4495 (~9 A) |
|---:|---:|---:|
| **79** (as built) | **39.7 A** | 4.4× short |
| **20** (3-stub comfortable) | **20.0 A** | **2.2× short** |
| 10 | 14.1 A | 1.6× short |
| 5 | 10.0 A | **1.1× short** |

**The loop redesign (`../resonance/NEXT.md` item 7) halves the current for a
4× VSWR improvement**, and the series capacitor there was sized at **~45× in
Q_ext**. **That is the only lever that touches the thermal wall.**

⚠️ **Whether a GaN transistor beats a silicon PIN on R_on × C_off is a SEPARATE,
UNVERIFIED question** — plausible, and exactly the kind of claim §4d already
warns was "asserted once in conversation without a datasheet". **Do not adopt it
without one.**

🔑 **Ranking, then:** ① fix β in the coupler (removes current *and* may remove
the tuner) → ② phase detector (removes the ambiguity, allows a discrete tuner)
→ ③ find a part that survives the residual current. **The detector is ②, and ②
does not substitute for ①.**

### ✅ THE SPEC IS MODEST

| | requirement | why |
|---|---|---|
| **phase resolution** | **±45° is ample** | it distinguishes 0° from 180°, not fractions of a degree |
| frequency | 2.45 GHz, over the LDMOS band | |
| \|Γ\| range | **0.65 → 0.98** | cold to loaded, i.e. 427–952 W reflected |
| reference | the **forward** port | it is a phase COMPARISON; the dual directional coupler already supplies both |

🔑 **Two usable methods, both needing phase and nothing else:**
- **parked at f₀** — the *sign* of Γ (0° vs 180°);
- **sweeping** — the *winding* of arg Γ (≈360° overcoupled vs returns-to-start
  undercoupled). ✅ That is exactly `e0k2_anchor.branch_from_phase`, so the
  hardware method and the solver method are the same method.

### 🔴 THE BINDING SPEC IS COUPLER DIRECTIVITY — AND IT IS NOT TIGHT

Forward power leaks into the reflected port at −D dB and **adds vectorially**, so
it corrupts the phase once \|Γ\| approaches the leakage:

| directivity | smallest \|Γ\| readable | β blinded |
|---:|---:|---|
| 20 dB | 0.100 | 0.82 < β < 1.22 |
| 30 dB | 0.032 | 0.94 < β < 1.07 |
| 40 dB | 0.010 | 0.98 < β < 1.02 |

✅ **Our operating points clear even 20 dB by ~16–20 dB.** Directivity only
matters near critical coupling.

### 🔴 AND THERE THE PHASE DOES NOT EXIST — SO DO NOT MEASURE IT

**At β = 1, Γ = 0: the reflected wave VANISHES. There is no phase.** The record
puts the crossing at **n_e ≈ 5e16**, i.e. **transiently, during ignition**.
🔑 **So the branch flip must be detected by the \|Γ\| MINIMUM and applied by a
STATE MACHINE — not read from the detector.** Chasing the null with directivity
is buying resolution in the one region where the quantity is undefined.
⚠️ **This is the same shape as §7x itself**: the failure is not that the
instrument is imprecise, it is that the quantity is not there.

### What has to be met

Transform a **real** load of **VSWR up to ~90** at **2.45 GHz**, passing **1 kW**.
*(was ~100, from interpolated β; measured 2026-08-25 — worst case 90 at 3e19,
75–82 across the anchor band.)*
🔴 **And the binding number is not the diode, it is the load side**: a matched
transformation at 1 kW forces **39–42 A** (low-Z branch) or **1.9–2.1 kV**
(high-Z branch). That is set by P and Z — **it is what 1 kW into that impedance
IS**, independent of network topology. Both scale as **√VSWR**.

### Candidates evaluated and REJECTED

| part | class | why it fails at 2.45 GHz |
|---|---|---|
| **MA4PK200x / 300x** (MACOM KILOVOLT) | HF/VHF kW switching PIN | Characterised **1–100 MHz only** — 2.45 GHz is 24× above the highest point. C_T 3.2–4.0 pF ⇒ **16–20 Ω** off-state (vs ~5 kΩ at 10 MHz), so on/off collapses from ~50,000:1 to ~200:1. Stud/solder-lug package SRF *estimated* 1.3–2.8 GHz. |
| **UMX5601–5615** (Microsemi MRI) | MRI PIN, characterised 64/128/300 MHz | **L_S = 900 pH ⇒ 13.9 Ω at 2.45 GHz, which dominates BOTH states**: ON ≈ 0.3 + j13.9 Ω, OFF ≈ −j11.1 Ω. ~j25 Ω of reactance swing with almost no resistance contrast. SRF **crosses the band with bias** — 3.29 GHz at 2.6 pF, 1.77 GHz at 9 pF. |
| **GC4400 series** (Microsemi) | ✅ **microwave PIN, specified to 18 GHz** | **Right frequency class** — 0.10 pF gives a **650 Ω** off-state. 🔴 But thermally limited: θ = 30 °C/W ⇒ 4.2 W ⇒ **~1.7 A**. The high-current member (GC4495, ~9 A) has 2.5 pF ⇒ only 26 Ω off. |
| **MACOM Si PIN/NIP chips** | ✅ microwave die, low parasitics | Same shape: 0.06 pF ⇒ **1,083 Ω** off-state, but θ = 30 °C/W ⇒ **~1.3 A**. |

🔑 **THE REASON IS STRUCTURAL, NOT A SOURCING FAILURE.** Low C_j requires a small
die; a small die has high thermal resistance; **so the parts that work at
2.45 GHz are exactly the parts that cannot carry the current.** GC4490 gives a
650 Ω open and 1.7 A; GC4495 carries 9 A and gives a 26 Ω open. **Not available
in one die.** Against a 34–45 A requirement the gap is 4–30×.

⚠️ **Limits of this evaluation, stated so it is not over-read:** four datasheets,
not a market survey. The **34–45 A load-side figure is solid** (it is only P and
Z). The **per-part 1.3–9 A limits are DERIVED** from θ and R_S assuming the diode
dissipates I²R_S in the on state — real currents depend on where the device sits
in the network. Treat them as indicative of the class, not as ratings.

### Directions — NONE of these has been checked

🔴 **Nothing below is a solution. They are untested options.**
- **Mechanical / motorised tuning**, if speed is genuinely not required (§4c).
  ⚠️ **Whether ANY product reaches VSWR ~100 at 1 kW / 2.45 GHz is UNKNOWN.**
  This was asserted once in conversation without a datasheet; **that assertion is
  WITHDRAWN** and must not be treated as a finding (CONVENTIONS §7ac).
- **Series/parallel diode stacking** to divide voltage and share current.
  ⚠️ Every element added reintroduces the package parasitics that rejected the
  first two candidates. Unquantified here.
- **Reduce the mismatch upstream instead of matching it.** Two levers; the
  situation is NOT as closed as this document said on 2026-08-24.
  ❌ **APERTURE COUPLING IS CLOSED** — the magnetic aperture is **patented**, and
  an iris needs a FEED GUIDE and a cavity to sit between, but **this cavity IS
  the waveguide**, so there is no shared wall to cut.
  🔴 **BUT THE LOOP ITSELF WAS NEVER DESIGNED.** User, 2026-08-24: *"some kind of
  loop was forced so we could evaluate driven, but we never evaluated the design
  options."* It exists because a DRIVEN solve needs a port. `h3_loopq` swept
  **AREA ONLY**, at fixed wire radius 1.0 mm, fixed cap radius 0.4805a, single
  turn, rectangular. **Q_ext floored at 9,231 WITHIN THAT FAMILY — the family was
  never chosen.**
  🔑 **AND THE TARGET IS NOT ABSURD.** β = 1 needs Q_ext 84× lower and is very
  likely unreachable. **But VSWR 85 → 20 — the difference between "no part
  exists" and "a standard 3-stub tuner works" — needs only 4.2×.**
  ⚠️ **So "magnitude tuning is unsolved" holds GIVEN AN UNDESIGNED COUPLER.**
  That is weaker than the claim this section previously made.

🔑 **THE TWO UPSTREAM QUESTIONS MUST BE ANSWERED BEFORE ANY TUNER IS DESIGNED OR
BOUGHT**, because either could remove the requirement rather than satisfy it.

---

## 4e. ⏸️ PARKED — and nothing is deferred that was not already queued

**Status 2026-08-24: the source/tuner side is a DESIGN problem, not a
measurement one, and it is a tangent to the cavity queue.**

🔑 **Parking costs nothing here, because the two questions that gate it are in
the cavity queue anyway for cavity reasons:**
- **Anchor n_e** (§7ab) — needed for every loaded result, AND it sets VSWR
  15.6→99.3, with tuner current going as √VSWR.
- **Test the coupler CLASS** — `h3_loopq`'s eigen-pair method measures Q_ext for
  any coupler, AND a lower Q_ext reduces the mismatch at source.

**Answering those two serves the cavity work first and may dissolve the tuner
requirement as a side effect.** ⚠️ **Do not open tuner design work before they
are answered** — the requirement could move by 3× in current, or disappear.

**RE-ENTRY CONDITIONS — n_e is anchored (done); the coupler is REOPENED.**
❌ Aperture coupling stays closed (patent + the cavity is the waveguide).
🔴 **But the LOOP was never designed** — only its area was swept, within one
arbitrary family. **A 4.2× reduction in Q_ext moves VSWR 85 → 20 and would
change what part is needed.** Whether loop design can deliver that is UNKNOWN
and has never been asked.

---

## 5. What would change on the cavity side if these are wrong

- **If the band is narrower than 100 MHz** — the margin numbers shrink directly.
  At 1e20, f₀ = 2.4824 needs the band to reach at least there.
- **If P ≠ 1 kW** — every absolute power figure scales, but **η, β, Q and the
  margins do not**: they are ratios and frequencies. This is the one assumption
  whose failure is cheap.
- **If the PIN tuner cannot reach VSWR 99** — the machine runs mismatched at
  mid-density, the dump load takes ~960 W, and **the loop/cavity coupling design
  would need revisiting** — most likely by changing the coupler CLASS, since
  `h3_loopq` showed loop SIZE cannot reach (Q_ext floors at 9,231).
- **If the frequency loop cannot resolve 350 kHz** — cold acquisition fails and
  ignition never starts, regardless of everything else in this programme.

---

## 6. What this document is NOT

⚠️ It is **not** an experiment, and it does not add one — PLAN's E0–E4 list is
unchanged (`README`: the experiment list does not grow). It is the missing
**boundary condition** for work already done, written down so the requirements
derived on 2026-08-24 have somewhere to live and so the next session can see
which of them are measurements and which are guesses.

🔑 **THE TWO MOST USEFUL ADDITIONS, AND NEITHER NEEDS A SOLVE:**
1. **Classify the band** (§4a) — regulatory, component, or decision.
2. **Answer whether anything meets §4b** — and if nothing does, that is a finding
   about the COUPLER, not about the tuner.
⚠️ **And one that DOES need work: ignition dynamics.** The tuner's speed
requirement cannot be derived from anything in this record, because every
measurement here is steady-state.
