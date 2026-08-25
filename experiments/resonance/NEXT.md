# Next

**This file is the QUEUE. It holds no measurements.**
Read **`KNOWN.md`** first — that is what has been established, and it indexes
every document. Then `PLAN.md` (the FIXED experiment list, E0–E4), then
`CONVENTIONS.md`.

🔴 **PRUNED 2026-08-24.** This file had grown to 819 lines of layered narrative —
the same way `FINDINGS.md` did before it was removed for being unreadable. Every
conclusion in it is in `KNOWN.md`; the narrative is in git:

    git -C axisymmetric-mip log -p --follow experiments/resonance/NEXT.md

⚠️ **Do not re-grow it.** A result goes in `KNOWN.md`; a lesson goes in
`CONVENTIONS.md`; only the *queue* goes here.

## Instance

**UP.** Address in `ops/env.sh` (one line — it was hardcoded in 29 places once).
`ops/go ops/status.sh` for state; `ops/go ops/remote.sh <rig.py> 32` to launch.

**After a spot reclamation:** launch `c7a.8xlarge` **in the volume's AZ** (EBS is
AZ-scoped — the easy mistake), attach, set the address in `ops/env.sh`, then
`NOSYNC=1 ops/go ops/mount.sh`. Exercised four times.
⚠️ `mount.sh` also checks that **pyflakes is in the env** — it lives on
`/opt/amip/envs/emsim`, NOT the root filesystem, because root is wiped by every
reclamation. Without it `preflight` silently stops checking undefined names.


### 🔑 STANDING REQUIREMENT — EVERY eigen rig emits MODE PURITY

**6 probes, no extra solve.** `P = |E_φ|²/(|E_r|²+|E_φ|²+|E_z|²)` at ≥3 φ × ≥2 r;
report **P_min, P_max and SPREAD**. TE011 has P=1 at every φ, so the spread is the
discriminator, and it cannot alias.

🔑 **This is the first tool the programme has for "how does a cavity change alter
the modes", and almost everything downstream depends on it** — groove depth, loop
size, torch ε and n_e all perturb the mode landscape, and until now there was no
continuous measure of the result, only a binary label that could be wrong.

Implementation is in `h3_ladder.purity()`; the probe layout is
`PROBE_PHI_DEG=[0,40,80] × PROBE_R_FRAC=[0.4805, 0.25]`.
✅ Validated: rejects both TM111 polarisations AND TE311 (which A2/A0 binned as
m=0 with 0.0004), accepts bare TE011 at 0.9973–1.0000.
⚠️ Report P even when it PASSES — the value is the measurement, not the verdict.

### 🔑 STANDING REQUIREMENT — every H3 rig emits PRIORS, not just verdicts

**These results are CO-DEPENDENT.** Groove depth × loop size × n_e × torch
permittivity all move the same mode landscape, so the end state is not a list of
answers — it is a surrogate that can be optimised over the joint space.
`OPTIMIZER.md`'s own rule: *"a finding belongs there when stated as something a
surrogate can EVALUATE, not as a number."*

So every H3 rig must return, and its report must print:

| for the optimiser | not just |
|---|---|
| the CONSTRAINT value — how many modes in 2.40–2.50, and their margins | "the filter works" |
| the value AND its uncertainty (A2/A0, identification margin, one-sided vs two-sided width) | a bare number |
| the EVALUATION OUTCOME — converged / missing-data / infeasible, with NLEPS count | a silent gap |
| the COST — tets, ND dofs, seconds, NLEPS — so the cost model stays fitted | wall-clock in a log |
| **which other variables were held fixed, and at what** | an implicit context |

⚠️ **That last row is the co-dependence.** A number measured at one groove depth,
one loop size and one n_e is a SLICE. Record the slice coordinates or the
surrogate cannot place the point.

🔴 And a failed evaluation is **MISSING DATA, not a bad score** (§3). Scoring it
badly teaches the surrogate to avoid regions that are merely hard to solve.

---

## 🔴🔴 SCOPE REOPENED 2026-08-24 — THE MODEL WAS NEVER RESTORED

User: *"We simplified greatly to answer the instrument and methodology issues,
and then didn't add critical features back. That puts everything except viewports
back in scope (no viewports because we haven't chosen axial vs radial)."*

**BACK IN SCOPE:** torch material (**sapphire ε = 11.6**, not ε = 1 / absent) ·
**gas feed aperture** (−z cap) · **chimney/exhaust** (+z cap, 21 mm).
**STAYS OUT:** viewport + light trap — axial vs radial not chosen.

🔴 **No rig has EVER passed a non-zero chimney or feed.** As modelled, the torch
is sealed at both ends by solid metal. See `KNOWN.md`.
⚠️ **I raised an alarm about the feed aperture's RF seal and WITHDREW it**
(§7ak). The uniform-fill cutoff said sapphire gives 4.6 dB; field-weighted it
gives **53.8 dB — the seal holds**. The ceramic annulus carries only 18.8% of the
TE11 energy, so ε_eff is 3.0, not 11.6. **The apertures remain in scope as
COMPLETENESS items, not alarms**, and rank below the torch material.

⚠️ **E3 is running on a SEALED cavity with a sapphire torch.** Its 3-channel
closure is still valid for that geometry — but **apertures would add a RADIATION
channel it does not include**, so a re-run is needed once they are in.

**Scoping the restoration, in dependency order:**
1. **Decide the aperture dimensions.** `geometry.py` indicates chimney 21 mm
   (meeting torch outer radius 10 mm). Feed diameter and `torch_ext` need a
   decision — the feed must pass the torch and reach its plumbing.
2. **Re-mesh with torch + both apertures**, then re-run the frequency ladder:
   every f₀ in the record is for a torch-free, sealed cavity.
3. **Re-run E3** with the radiation channel present.
4. Then the loaded work (`h3_driven`, `h3_margin`) — band margins move with f₀.

## 🔑 THE ORDER — and why the circular dependency is NOT real

**User, 2026-08-24: *"we have a few open threads now, and some circular
dependencies... We have to change only one thing at once."*** ✅ The threads are
real. **One of the dependencies is not.**

**The apparent circle:** β and VSWR are DESIGN OUTPUTS of the loop (§7am) → so
measuring them at the anchored density seems worthless until the loop is chosen →
but choosing the loop needs the loaded Q₀ → which needs the anchored density.

🔑 **IT BREAKS, because H3 does not actually measure β — it measures Q₀:**

| quantity | set by | depends on the other? |
|---|---|---|
| **Q₀(n_e)** | cavity + plasma | ❌ **NO** |
| **Q_ext** | the loop | ❌ **NO** (cold, geometric) |
| β, VSWR, current, dump | **Q₀ / Q_ext** | derived — **arithmetic, not a solve** |

✅ **And in the LOADED regime the loop barely enters the extraction at all:**
Q₀ = 1/(1/Q_L − 1/Q_ext) with Q_L ≈ 155 and Q_ext = 9,231 gives **Q₀ = 1.017 ×
Q_L — a 1.7 % correction.** β ≪ 1, so **Q₀ is essentially measured directly.**
⚠️ The error amplification that bites when Q₀ ≫ Q_L does **not** apply here.

🔑 **So item 8 and item 7 are INDEPENDENT, and neither invalidates the other.**
Run 8 → Q₀ at the operating point, permanent. Run 7 → Q_ext per loop family,
permanent. **β for any loop × any density is then arithmetic on the pair.**

### The order

| | do | changes ONE thing | blocked by |
|---|---|---|---|
| **1st** | **item 8 — H3 at the anchored density** | **density** (torch, geometry, solver all unchanged) | **nothing** ✅ |
| 2nd | item 7 — Q_ext vs turns / mount | **loop** (cold, no plasma, no sapphire) | nothing ✅ |
| 3rd | one sapphire+plasma case at the **anchor** | **torch ε**, at the now-known density | needs 1st |
| 4th | E3 closure, or the preconditioner | — | needs 3rd's verdict |
| 5th | restoration: aperture dims → re-mesh → re-ladder | **geometry** | a DESIGN decision, not a measurement |

🔴 **WHY ITEM 8 IS FIRST and not item 7:** it is prepared, it is the only one
whose numbers were being **actively quoted wrong** (VSWR 80–89, β, 45 A, 960 W,
the 400× spread are all interpolated), and it changes exactly one variable
against a **measured 43-minute baseline**.
⚠️ **Its one known offset is quantified, not a confound:** vacuum torch →
f₀ high by ≈ 13.9 MHz, Q high by ≈ 2.2 % (E3 case B). **Band margins carry that
offset; Q₀, β and VSWR essentially do not.**
🔑 **Step 3 is also the test of the contrast diagnosis** — it predicts sapphire
+ plasma converges at the anchor (span +11.6/−1.46). **One case answers both.**

## THE QUEUE

| # | item | status |
|---|---|---|
| 1 | Matching network required | ✅ answered — tuner spec in `../control-loop/` |
| 2 | **Anchor n_e** | ✅ **7.3–8.6e18**, from MICAP's measured 5220–5270 K |
| 3 | Test the coupler class | 🔴 **REOPENED — and it is the biggest lever left.** ❌ Aperture is out (patented; the cavity IS the waveguide). 🔴 **But the LOOP was never designed** — forced into existence so driven solves would have a port; `h3_loopq` swept AREA only. **Q_ext = 9,231 floors ONE arbitrary family.** VSWR 85→20 needs 4.2×, β=1 needs 84×. See CONVENTIONS §7al |
| 4 | **H3's HOT leg** | ✅ **DONE — H3 IS COMPLETE** |
| **5** | **PLAN E3 — the energy-balance closure** | ⚠️ **RAN (EXIT=0), 3 of 5 landed.** ✅ **B, D, E.** ✅ **F2 resolved by a bound** (η_diel ≤ 2.27%; PLAN's ~2% CONFIRMED). ✅ **E gave an eigen↔driven cross-check — 70 kHz and 3.42% — which RESTORES V1's anchor.** 🔴 **A, C failed on the sapphire+plasma ε-contrast, already documented in `h3_driven` lines 10–11 BEFORE E3 was written** (§7an). 🔴 **F1 untested; η_plasma unquotable** |
| 6 | H4 ignition | ⏸️ parked |
| **8** | 🔴 **RE-RUN H3 AT THE ANCHORED DENSITY** | **PREPARED, NOT LAUNCHED — do this FIRST** |

### 8. 🔴 H3 at the anchored density — the operating point was never solved

**User, 2026-08-24: *"E3 seems like a waste of time at 1e20. In fact, we probably
have to re-run H3 with the right number."*** ✅ Both correct.

🔴 **`NE_GRID` never contained the anchor.** 7.3–8.6e18 falls in the 3e18 → 1e19
gap — **3.3× wide, VSWR 43.3 → 99.3 across it**, the steepest limb, just below
the peak. **VSWR 80–89, Q₀ ≈ 109, β ≈ 0.012, ~45 A, ~960 W and the 400× coupler
spread are ALL INTERPOLATED**, never solved.

✅ **PREPARED in `h3_driven.py` (edited, parses, NOT launched):**
- `N_E_ANCHOR = 7.9e18` with `_LO = 7.3e18`, `_HI = 8.6e18`, all three added to
  `NE_GRID` (now 9 points).
- The analysis block's hardcoded `P.get(1.0e20)` → `P.get(N_E_ANCHOR)`. **1e20
  was being reported as "the operating point" by the rig itself** (§7ab).
- ⚠️ **F1's premise is stale and I did NOT silently re-tune it.** It calls 1e19
  *"one decade below the operating point"* — true only when that meant 1e20;
  against 7.9e18, 1e19 is **above**. And η is flat 0.986–0.998 across the whole
  grid, so it cannot discriminate anyway (§7z). It now prints as a **recorded
  value, explicitly not a test**, pending a restatement.

    ops/go ops/remote.sh h3_driven.py 32      # DRIVEN — unaffected by the
                                              # eigen preconditioner defect

✅ **Backup at** `scratchpad/h3_driven.py.bak`.

**COST — measured, from the previous 6-point run (`h3_driven.log`, EXIT=0):**
COLD 441 s · 1e18 **986 s** · 3e18 319 s · 1e19 290 s · 3e19 286 s · 1e20 279 s
= **43 min.** The three anchor points bracket 3e18/1e19, both ~300 s, so
**+~15 min → ~58 min total.** 🔑 Driven cost scales with Q (samples ~ Q), which
is why 1e18 is the slow one and the loaded points are cheap.

🔴 **CAVEAT — THIS FIXES THE DENSITY, NOT THE GEOMETRY.** `h3_driven.py:235`
passes `--torch-material 1.0,3.5e-05`: **the torch is meshed as VACUUM.** E3
case B puts the sapphire torch at **≈ −13.9 MHz** (provisional). So the re-run's
f₀ and band margins will still be high by roughly that much, and the restoration
list above still applies. **Two known-wrong inputs; this corrects one.**
🔑 **Driven, not eigen** — fixed-ω linear solves, so **item 5's preconditioner
defect does not apply.** This is unblocked; E3 is not.
⚠️ `ops/go` will refuse to sync while E3 holds the instance. That guard is
correct — wait for E3 to finish rather than forcing `NOSYNC=1`.
| **7** | 🔴 **DESIGN the loop — barrel mount, then the SERIES CAPACITOR** | **Buildable now.** 🔑 A **45×** mechanism (Q_ext → ~320) is already in `geometry.py`, calculated and never simulated. Turns is NOT buildable |

### 7. 🔴 DESIGN the coupling loop — the question we never asked

**β is a DESIGN OUTPUT, not an observation** (`CONVENTIONS.md` §7am). Asking
*"what Q_ext do we WANT?"* gives, from numbers already in the record:

| state | Q₀ | Q_ext wanted | built 9,231 is |
|---|---:|---:|---|
| COLD (ignite) | 43,422 | **43,422** | 4.7× too LOW |
| LOADED @ 7.9e18 | 109 | **109** | **85× too HIGH** |

🔴 **The two states want couplers ~400× apart — no FIXED loop meets both.**
🔑 **Three of the loop's five axes are ALREADY pinned at maximum coupling**
(cap radius = J₁ peak, orientation normal, area = the sweep's Q_ext minimum).
⚠️ **These Q₀ figures are INTERPOLATED and are being re-measured now** (item 8);
the ratios above will shift when the anchor points land.

🔴 **REVISED after reading `geometry.py` — my first version of this item was
wrong twice.** (Checking buildability before writing the rig is what caught it.)

- 🔴 **TURNS IS NOT BUILDABLE.** There is no turns/helix parameter. **New OCC
  geometry, not a rig.** Deferred.
- 🔑 **THERE IS A THIRD AXIS I HAD RULED OUT, AND IT IS THE BIG ONE:** the
  **SERIES CAPACITOR** (`loop_gap2` + `loop_flange_r`), already implemented.
  `geometry.py:443–451` computes **0.196 pF cancels the loop's 332 Ω
  self-reactance, ~45× coupled power, Q_ext 14,442 → ~320.** Against our 9,231
  that lands near **205** — the same order as the **109** β = 1 needs.
  ⚠️ **CALCULATED, NEVER SIMULATED.** One attempt failed (0.056 pF, gap too
  wide, |Γ| 0.568 → 0.904 — *worse*); **the fix — flange AREA, r ≈ 1.9 mm — was
  diagnosed and implemented but never tested.**

**The rig — eigen `port_bc` pairs as in `h3_loopq`, ONE CHANGE PER STEP:**
1. **Cap → barrel mount**, single turn, same 176 mm², **no capacitor.**
   Isolates mount. ⚠️ Required first because **`--loop-gap2` is REFUSED with
   `--loop-cap`**, so the capacitor cannot be tested on the current loop.
2. **Add the series gap on the barrel loop**, `loop_gap2` swept, `loop_flange_r`
   at and around 1.9 mm. **This is the 45× test.**
3. Only then re-sweep area around whatever wins — the 176 mm² optimum was found
   at N=1 **on the cap** and does not transfer.

✅ **Falsifier, restated:** if step 2 does not move Q_ext by ≥4×, the loop family
IS exhausted and `../control-loop/`'s requirement 1 is real. 🔑 **But it is no
longer reasonable to ASSUME that** — a 45× mechanism sat unused in the builder
while this programme called the coupling a fixed property.

✅ **Falsifier:** if neither axis moves Q_ext by ≥4×, **the loop family is
genuinely exhausted** and `../control-loop/`'s requirement 1 is real. **That is
a result either way**, and it is currently assumed rather than measured.
⚠️ Do not open magnitude-tuner design before this runs.

### 5. ⚠️ PLAN E3 — RAN, 3 OF 5 LANDED, CLOSURE STILL UNANSWERED

✅ **RAN 2026-08-24, EXIT=0.** B_wall 808 s · D_dielectric 403 s ·
E_vac_torch 1140 s. 🔴 **A_all and C_plasma timed out at 2700 s** on the
sapphire+plasma ε-contrast (+11.6 beside −30.09) — **a failure the record had
already documented** (§7an, and now a PRIOR ART row).

🔴 **The rig's own verdict:** *"CLOSURE CANNOT BE TESTED — missing
['A_all', 'C_plasma']. E3 is UNANSWERED; every eta in the record stays
unfalsified."*

🔑 **DO NOT simply relaunch A and C.** They would run at 1e20, which is a
**different regime** (δ/shell 0.30, plasma shields) from the anchored operating
point (δ/shell 1.06, transparent). **Do item 8 first**, then re-test whether
sapphire+plasma converges at the anchor, where the span is **+11.6/−1.46**
rather than +11.6/−30.09 — the contrast mechanism predicts it should.

**After a spot reclamation:** launch `c7a.8xlarge` **in the volume's AZ** (EBS is
AZ-scoped), attach, set the address in `ops/env.sh`, then
`NOSYNC=1 ops/go ops/mount.sh`.
⚠️ `mount.sh` also checks pyflakes is in `/opt/amip/envs/emsim` — **not** the
root filesystem, which every reclamation wipes.

**What it will test:**

**η_total = η_plasma + η_wall + η_dielectric must close within a few %, or only
η_total may be quoted.**

🔑 **It is the declared falsifier for EVERY η in the record**, and it has never
been run. Today produced a corrected η column (0.986–0.998 over n_e 1e18–1e20)
and nothing has tested whether the loss budget adds up.
✅ **Now is the right time**: η is referenced to a measured design-cavity Q₀
(43,523), the coupling branch is resolved, and n_e is anchored — so E3 would
test the right budget rather than one built on a wrong regime.
⚠️ **Needs per-region energy bins**, which `eigen_cfg` already emits (one Energy
index per volume). The plumbing exists.

🔑 **METHOD:** one loss channel at a time on the SAME mesh — A all on, B wall
only, C plasma only, D dielectric only — then test
**1/Q_all = 1/Q_wall + 1/Q_plasma + 1/Q_diel**. That identity is exact IF the
field is the same in all four; **it fails when a channel is strong enough to
redistribute the field, which is exactly when "η_plasma" stops being a real
quantity.** So it tests whether the decomposition EXISTS, not arithmetic.
⚠️ **Runs at ne = 1e20, the STRONGEST test, not the operating point** — the
plasma is ~275× the wall loss there. It is also the only convergent density:
with the corrected ν_m the anchored 7.9e18 sits at PI₁ = 2.46, inside eigen's
untested gap, and 3e18 is where eigen is known to FAIL.

🔴 **AND IT CARRIES A SECOND TEST, from a defect found while writing it:**
**five rigs mesh the torch as VACUUM** when the design is sapphire ε = 11.6
(see `KNOWN.md`). Case E re-meshes with the vacuum torch so the frequency shift
is **measured, not inferred** — expected order −10 MHz. If confirmed, **every
band margin in the record is conservative by that amount.**

### 6. ⏸️ H4 — ignition
Parked. ⚠️ **"No mode cold-ignites" is UN-ANCHORED** — its source rigs were
groove-free and are discarded. Route 3 (saline as an ignition baseline) is
recorded in `PLAN.md`'s *Parked* section and does not spawn runs.
🔴 **Ignition DYNAMICS have never been measured or modelled anywhere in this
programme.** Everything is steady-state. That gap blocks the tuner's SPEED
requirement in `../control-loop/`.

---

## SIBLING PROGRAMMES

| | |
|---|---|
| **`../control-loop/`** | LDMOS, matching, control. ⏸️ **PARKED** — n_e anchored (VSWR ~100:1, ~45 A, ~2.2 kV, ~960 W dump), but ⚠️ **only ONE upstream lever is spent**: the loop family was never chosen, and 4.2× in Q_ext would move magnitude tuning from impossible to off-the-shelf. **Do not open tuner design before that is answered** |
| **`../spectroscopy/`** | Why any of it exists. ✅ Supplied the n_e anchor. 🔴 Top open item: **is LTE fair?** Non-LTE puts n_e ABOVE Saha — asymmetric, and it pushes toward the VSWR peak |

---

## STANDING REQUIREMENTS FOR ANY NEW RIG

- **Emit MODE PURITY** from every eigen solve (above).
- **Emit PRIORS, not just verdicts** — the value AND its uncertainty, the
  evaluation outcome, the cost, and which variables were held fixed and at what.
  `OPTIMIZER.md` is the consumer.
- **`eigen_cfg` now REFUSES** a looped mesh without an explicit `port_bc`
  (GATE 4) and a mesh the sidecar does not describe (GATE 5). Neither is
  optional; both cost a launch to learn.
