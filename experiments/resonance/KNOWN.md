# KNOWN — what this programme has actually established

**One page. If it is not here, it is not established.**

### 📁 THE DOCUMENT SET — all of it, so none is missed again

| file | what it is | status |
|---|---|---|
| **`KNOWN.md`** | this — what is established | **read first** |
| **`GLOSSARY.md`** | 🔑 **say exactly this, mean exactly this.** Every entry caused a real error: cold/hot/loaded, the TWO "mode filter" devices, which cavity a Q belongs to, baseline vs frozen, loop half-width | **read second** |
| **`PLAN.md`** | 🔑 **the FIXED experiment list, E0–E4. "It does not grow."** Each with V and F declared before any driver. Has a *Parked* section for surprises that **do not spawn runs** | **authority on what experiments EXIST**; some status lines stale (E1 was deleted 2026-08-21) |
| `NEXT.md` | the queue only, no measurements | current |
| `CONVENTIONS.md` | recurring errors + corrected approach | current |
| `HYPOTHESES.md` | H0–H5, the working question set | current |
| `INSTRUMENT.md` | what gmsh+Palace can and cannot tell us | current |
| ➡️ **`../spectroscopy/`** | 🔴 **WHY any of this exists — and resonance is BLOCKED on one answer from it: the required GAS TEMPERATURE.** Saha turns that into n_e. Also holds the inherited-and-unverified assumptions (20 slm N₂, Fassel torch, working gas) that resonance has been building on | **NEW 2026-08-24** |
| ➡️ **`../control-loop/`** | 🔑 **the SOURCE side is its own programme now** (opened 2026-08-24): LDMOS, matching, and the control loop. `../control-loop/README.md` states what we have and what is needed; `../control-loop/SOURCE.md` holds the characterisation. ⏸️ **PARKED** — n_e is anchored, but ⚠️ **the second lever is NOT spent**: the aperture class is closed, the **LOOP was never designed** (§7al). Magnitude tuning is unsolved for the loop AS BUILT; 4.2× in Q_ext would make it off-the-shelf | **moved out 2026-08-24** |
| `OPTIMIZER.md` | priors for the eventual multi-variable optimisation | current |
| `METHODOLOGY.md` | tool-specific lessons, each paid for with a wrong answer | rev 4, 2026-08-20 |
| `DEPLOY.md` | running the programme on a rented machine | 2026-08-21 |
| `README.md` | the rules, and why the previous programme was abandoned | 2026-08-20 |

⚠️ **`FINDINGS.md` was REMOVED from the working tree 2026-08-23** so it stops
confusing sessions. It is in git and retrievable:

    git -C axisymmetric-mip show ba740d6:experiments/resonance/FINDINGS.md

Retrieve it only to follow a citation. It is 5,300 lines, three invalidated
eras, and it is not where you find out what is true.

⚠️ **Two numbering systems.** `PLAN.md` uses **E0–E4** (experiments, fixed).
`HYPOTHESES.md` uses **H0–H5** (questions, evolving). They are not the same
axis and neither supersedes the other.

Every entry names **what it is anchored to outside the programme.** A result
supported only by another result of this programme is not listed — that is the
inward-facing loop that ended the previous programme (`README.md`).

---

## ✅ E0 — the instrument
**Anchor: closed-form cavity mathematics.**

- Geometric order 2 **and** solver order 2. They are different discretisations;
  conflating them cost a full invalidation.
- TE011 within **0.058 MHz** of closed form. Differential work ~20 kHz; mesher
  jitter 8 kHz.
- **Q ∝ σ^0.5** to four decimals, across a decade of σ, all 14 modes.
- Bare TE011 **Q₀ = 44,384** at aluminium 3.5e7 (empty, **no loop, no groove**).
  🔴 **THIS IS NOT THE DESIGN CAVITY'S η REFERENCE.** Three configurations, three
  numbers, none transferable: **44,384** no loop/no groove · **29,854** loop, no
  groove · ❌ ~~12,368 the DESIGN cavity~~ **RETRACTED — an open-gap artifact**
  (§7v) · ✅ **43,523 the DESIGN cavity, port terminated** (`h3_step3`).
  🔑 **The fix is structural: measure the reference with the SAME rig, mesh and
  solver that measures the loaded cases.** `h3_driven` now takes its cold case
  as the reference rather than importing one, which removes the cross-solver and
  cross-mesh transfer that §7c keeps catching.
- Cost model `t ≈ 454 ns × ND_dofs × KSP_its`, ±15%, at 32 ranks / order 2.

## ✅ H1 — the cavity
**Anchor: an analytic max-min optimum over D/L.**

- **D/L = 1.525, a = 88.0045 mm, L = 115.4158 mm.**
- Nearest rival TE112 at **332.7 MHz** — a stationary point of the max-min, so
  tolerance-insensitive. Neither original candidate.
- ⚠️ **Poles to avoid**: TM012 crosses TE011 at D/L = 1.096440.

## ✅ H2 — the mode filter · **ANSWERED**
**Anchor: the LDMOS tuning range — a hardware constraint outside the programme.**

- **Annular groove, BASELINE 5 × 10 mm** (width × depth), both end caps.
  ⚠️ **"Baseline", not "frozen".** It was validated COLD. Loading moves every
  mode, so whether 5 × 10 still clears the band under load — and what size does
  if not — was **H3's to refine**. `GEO_DESIGN` carries the baseline.
  ✅ **ANSWERED 2026-08-24 (`h3_margin`): IT NEEDS NO REFINEMENT.** Groove depth
  moves the LOADED f₀ by 0.000 MHz over 7–14 mm, and depth PEAKS at 10 mm.
  **5 × 10 is optimal under load as well as cold** — so "baseline, not frozen"
  resolves to "baseline, and it survived the test."
- Mechanism: TE011's cap current is **azimuthal** and runs parallel to the slot;
  every TM mode has a **radial** component the slot cuts.
- Cold, measured: TM111 **−64.25 MHz**, TE011 moves **14 kHz**, Q cost **0.3%**.
- 🔑 **SUFFICIENCY IS ESTABLISHED, not deferred:** 64.25 MHz **clears the 50 MHz
  LDMOS band**. That is why the dimensions were not optimised further — 5 × 10
  puts every competitor out of the tuner's reach, so refining it buys nothing.
- ✅ **INDEPENDENTLY REPRODUCED 2026-08-24, `h3_ladder` step 2** — a second solve
  from the bare anchor, one perturbation, different rig and settings:

  | | H2 | ladder step 2 | agreement |
  |---|---:|---:|---|
  | TM111 shift | −64.25 MHz | **−62.95 MHz** | **2.0%** |
  | TE011 shift | +0.014 MHz | **+0.094 MHz** | 0.080 MHz |

  Grooved, no loop: **TM111 2.387135 (Q 13,339, m=1)**, **TE011 2.450561
  (Q 44,414, m=0, A2/A0 = 0.0003)**, purity **0.9985–1.0000, spread 0.0015**.
  ⚠️ **The Q cost is NOT resolved here.** H2 measured −0.3%; this run reads
  **+0.8%** (44,057 → 44,414). Bare Q itself differs from E0's 44,384 by 0.7%,
  so the mesh spread at sf 1.5 is ~1% and a 0.3% effect sits underneath it.
  Consistent with H2, but this measurement cannot confirm the sign.
- 🔴 **λ/4 = 30.59 mm is the depth to AVOID** — the slot resonates and Q
  collapses to ~3,000.
- ⚠️ An annular filter is **blind to m**.

## ✅ TE011's field structure
**Anchor: closed form, and it reproduces a ratio the code independently uses.**

- E is a **torus at r = 0.4805a**, zero on axis and zero at the wall.
- H_z max at mid-plane, zero at the caps; H_r max at the caps, zero at
  mid-plane, peaking radially at 0.4805a.
- Only ~0.1% of TE011's energy sits in an 8.5 mm bore.

---

## ✅ THE BARE-CAVITY MODE LANDSCAPE — measured 2026-08-23, `h3_ladder` step 1
**Anchor: closed form. This is the reference every later identification hangs on.**

| mode | f₀ GHz | Q | m | A2/A0 |
|---|---:|---:|---:|---:|
| TM111 | 2.450086 | 20,313 | 1 | 0.3055 |
| TM111 (2nd polarisation) | 2.450178 | 20,296 | 1 | 0.3058 |
| **TE011** | **2.450467** | **44,057** | **0** | **0.0023** |
| a second m=0 | 2.623005 | 24,352 | 0 | 0.0004 |

- **TE011 Q / TM111 Q = 2.17×** — H1's own falsifier, passing.
- **A2/A0 separates m=0 from m=1 by 130×** (0.0023 vs 0.306).
- The degenerate pair appears as a **doublet split by 0.092 MHz** — mesh
  asymmetry, since theory says exactly zero.
- ✅ **THE 2.623 GHz MODE IS TE311 — an ordinary cavity mode.** Closed form
  **2.622012 GHz** against 2.623005 measured: a 0.99 MHz match, the same sf-1.5
  systematic seen everywhere. Not spurious, not a meshing artifact.
- 🔴 **AND FINDING IT EXPOSED TWO COUPLED DEFECTS IN THE IDENTIFICATION CHAIN:**
  1. **`physics.spectrum` is INCOMPLETE** — it enumerates `m in range(3)`,
     `n in range(1,3)`, `p in range(0,3)`, i.e. **m ≤ 2, n ≤ 2, p ≤ 2**. TE311
     is invisible to it. **"The closed form has nothing there" is not a safe
     statement from this function.**
  2. **`azimuthal.order()` cannot resolve m ≥ 3** — `SECTORS = 5`, and its own
     comment says *"m in {0,1,2} in this window"*. **That validity range was
     chosen from the incomplete spectrum in (1).** TE311 (m=3) was reported as
     **m=0 with A2/A0 = 0.0004** — indistinguishable from TE011 by the exact
     test used to identify TE011.
  🔴 **CONSEQUENCE: "clean m=0" does NOT establish TE011.** Any identification
  resting on it needs a second, independent discriminator — Q ratio, frequency
  against a COMPLETE closed-form table, or continuation from a known state.

- ⚠️ **f₀ reads +0.467 MHz high** against closed form at **sf 1.5, geometric
  order 2** — a discretisation systematic, confirmed independently by
  `h4_field` (+0.496 MHz). E0's 0.058 MHz bound was measured at sf 0.96 and
  **does not apply at this resolution.**

## ✅ MODE PURITY — the first tool that measures how a cavity change alters the modes
**Anchor: TE011's exact field structure (E purely azimuthal), from closed form.**

    P = |E_phi|^2 / (|E_r|^2 + |E_phi|^2 + |E_z|^2)   at several phi

**TE011 is TE_0np: E_z = 0 (TE) and E_r = 0 (m=0), so P = 1 at EVERY phi.** Any
m ≠ 0 mode's P varies with φ. **The SPREAD across φ is the discriminator** — it
is a pointwise field test, so there is no harmonic decomposition and **nothing to
alias.** 6 probes, no extra solve.

**Validated 2026-08-23 on the bare cavity, where the answer is known:**

| mode | binned m | A2/A0 | P range | spread | verdict |
|---|---|---:|---|---:|---|
| TM111 | 1 | 0.306 | 0.31–1.00 | 0.690 | rejected ✅ |
| TM111 (2nd pol.) | 1 | 0.306 | 0.14–1.00 | 0.862 | rejected ✅ |
| **TE011** | 0 | 0.0023 | **0.9973–1.0000** | **0.0027** | **✅** |
| **TE311** | **0** | **0.0004** | 0.016–0.851 | **0.836** | **rejected ✅** |

🔑 **The TE311 row is the proof.** It was binned `m=0` with A2/A0 = 0.0004 —
*more* axisymmetric-looking than TE011 by the old test, and indistinguishable
from it. **Purity rejects it at a spread of 0.836.**

### 🔑 What it makes possible, and it is new

**A CONTINUOUS measure of how far a mode has been perturbed from ideal TE011**,
rather than a binary label. First measurement:

| cavity | best TE011-like purity |
|---|---|
| bare | **P ≥ 0.9973, spread 0.0027** |
| + groove 5×10, no loop | **P ≥ 0.9985, spread 0.0015** |
| design (groove 5×10 + loop 11×8) | **P ≈ 0.942, spread 0.0575** — no mode passes |

## ⚠️ SUPERSEDED — the two earlier element tables from 2026-08-24
**Kept only as a record of two wrong answers reached the same day. Do not quote.**

1. **Morning:** loop pulls TE011 **−10.56 MHz**, Q **×0.278**, purity −0.056.
   Built on `h3_cold`'s 2.440003 — an open-gap artifact.
2. **Afternoon:** loop moves TE011 **+0.939 MHz**, Q **×0.191**.
   Frequency was nearly right, Q was wrong: it divided the driven cold Q₀=8,462,
   which came from the WRONG COUPLING BRANCH.

✅ **The answer is below**: +0.93 MHz, Q ×0.980, purity 0.9998.
🔑 **Both errors share one shape — a number taken from a rig whose own caveat
was on the same line as the value** (`identification_uncertain: True`; the
undercoupled-branch comment on the `beta` assignment).

## 🔴🔴 AN UNASSIGNED PORT BOUNDARY OPENS THE LOOP GAP — the day's main finding
**`h3_step3`, 2026-08-24. Same mesh, only the port BC changed.**

    mesh sidecar:  port attribute = 91,  wall attribute = 90
    eigen config:  Boundaries assigned attribute 90 ONLY
    an UNASSIGNED boundary is PMC — the NATURAL BC of the curl-curl E
    formulation (n x H = 0). PEC is the ESSENTIAL one and must be imposed.

🔑 **So the loop's feed gap was left OPEN, and an open gap plus the loop is an LC
resonator that lands near 2.45 GHz.** It hybridises TE011 into a pair. Short the
gap and the loop becomes a small closed ring, resonant far above the band, which
barely perturbs the cavity.

| port BC | in-band modes | best purity |
|---|---|---|
| unassigned (**PMC — gap OPEN**) | 2.440003 **and** 2.494440 | 0.9423, spread 0.0575 |
| `pec` (gap shorted) | **2.451633**, Q 43,422 | **0.9997**, spread 0.0003 |
| `lumped` (**50 Ω — the machine**) | **2.451488**, Q_L 7,538 | **0.9998**, spread 0.0002 |
| driven S11 (50 Ω) | **2.451500** | — |

✅ **EIGEN AND DRIVEN AGREE TO 12 kHz** once the port is terminated — E0's mesh
jitter is 8 kHz. The 11.5 MHz gap was **entirely** the port boundary condition.
⚠️ **I first wrote that the default was PEC and that eigen SHORTED the loop.
That was backwards** — it is PMC and the gap was OPEN. The conclusion (different
cavities; the port BC is the cause; GATE 4 is the fix) held; the mechanism did
not. **A correct conclusion from a wrong mechanism will mispredict the next
case.**

## ✅ WHAT THE LOOP ACTUALLY DOES TO TE011 — and it is nearly nothing

| cavity | f₀ GHz | Q | purity | spread |
|---|---:|---:|---:|---:|
| bare | 2.450467 | 44,057 | 0.9973 | 0.0027 |
| + groove 5 × 10 | 2.450561 | 44,414 | 0.9985 | 0.0015 |
| **+ loop 11 × 8** | **2.451490** | **43,523** | **0.9998** | **0.0002** |

**Loop: Δf = +0.93 MHz, Q ×0.980, purity UP.** 🔑 **BOTH ELEMENTS ARE NEARLY
FREE.** The groove costs 94 kHz and nothing in Q; the loop costs 0.93 MHz and 2%
in Q. **This replaces "the loop costs 3.6× in Q and all the purity", which was
the open-gap artifact.**

🔴 **RETRACTED, AND NOW FOR THE RIGHT REASON: "the loop hybridises TE011."**
It does not. **TE011 in the operating configuration is P ≥ 0.9998, spread
0.0002** — the cleanest of all three cavities. The 0.9423 / inboard-impurity /
φ=36°-aligned story was the open-gap LC resonator throughout.
✅ **THE TDS OBJECTION LOSES ITS PREMISE.** "A 94% azimuthal mode has 6% that is
not" described an artifact. At 0.9998 there is no meaningful non-azimuthal
component to weigh.
🔑 **It also explains `h3_cold` exactly**: 2.440003 and 2.494440 are the two
halves of TE011 mixed with the open-gap resonator — which is why they had
*identical* purity spreads and straddled 2.4505. Its `identification_uncertain:
True` and `m_az = 1` were both correct.

## ✅ ITEM 1b ANSWERED — THE COLD CAVITY IS OVERCOUPLED, β = 4.77
**From first principles: two eigen solves, no |S11|, no phase unwrapping.**

    Q0  (port PEC, no port loss)  = 43,523
    Q_L (port 50 ohm)             =  7,538
    1/Q_ext = 1/Q_L - 1/Q0  ->  Q_ext = 9,117  ->  beta = Q0/Q_ext = 4.774

🔴 **`h3_driven.fit_dip` HARDCODED THE UNDERCOUPLED BRANCH** (`b = (1-S)/(1+S)`).
For the cold case that is wrong: β = 0.208 → Q₀ = 8,462, where the truth is
β = 4.803 → **Q₀ = 40,645**, matching eigen's 43,523 to 7%.
🔑 **THE BRANCH FLIPS.** Cold is OVERCOUPLED; every loaded case is UNDERCOUPLED
(Q_ext ≈ 9,117 gives β = 0.065 at ne=1e18 against 0.070 fitted). **No single
branch choice is safe across a density sweep**, which is exactly why |S11| alone
cannot be trusted (`e0k2_anchor.branch_from_phase`, and item 1b, said so).
⚠️ **My phase read was wrong too.** I compared two WRAPPED phase values 6 MHz
apart and called it "returns to baseline → undercoupled". Unwrapped, the phase
advances **~326°** — the overcoupled signature. The tool for this already
existed and I eyeballed it instead.

## ⏳ H3 LOADED — measured 2026-08-24 on the DESIGN cavity, `h3_driven`
**Anchor: its OWN cold case (ne=0), same mesh, same solver, same extraction.**
✅ **CONFIRMED, AND THEN CORRECTED.** `h3_step3` first fired F3 — no eigenmode at
2.451500 — because the port was unassigned and the loop gap open. With the port
terminated, eigen finds TE011 at **2.451488**, twelve kilohertz from the driven
dip. **The mode is real and the table stands; its η column needed the coupling
branch fixed.**
⚠️ **A falsifier can fire for a reason its author did not enumerate.** F3 assumed
"not an eigenmode" implied "not real". Check the mechanism before executing the
consequence.

| ne | ε | f₀ GHz | Q₀ | **η** | β | VSWR | **margin (f₀→2.500)** | ~~3 dB edge~~ |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 (ref) | +1.000 | 2.451500 | **43,523** (eigen) | — | **4.715** OVER | 4.7 | **48.5 MHz** | ~~48.3~~ |
| 1e18 | +0.689 | 2.452000 | 593 | **0.9864** | 0.064 | 15.6 | **48.0** | ~~45.8~~ |
| 3e18 | +0.067 | 2.453400 | 213 | **0.9951** | 0.023 | 43.3 | **46.6** | ~~40.7~~ |
| 1e19 | −2.109 | 2.460800 | 93 | **0.9979** | 0.010 | **99.3** | **39.2** | ~~25.8~~ |
| 3e19 | −8.327 | 2.474000 | 96 | **0.9978** | 0.010 | 96.2 | **26.0** | ~~13.0~~ |
| 1e20 | −30.089 | 2.482400 | 158 | **0.9964** | 0.017 | 58.4 | **17.6** | ~~9.6~~ |

🔴 **THE MARGIN COLUMN WAS RECOMPUTED 2026-08-24.** It used the upper 3 dB edge;
the tuner **parks at f₀**, so f₀ is the criterion (see the tuner section above).
**The struck values are what this document said before and are wrong.**
🔑 **VSWR is NON-MONOTONIC and worst at 1e19** — Q₀'s minimum. The PIN tuner's
hardest condition is mid-range, not at the top.

🔴 **THE η COLUMN WAS RECOMPUTED 2026-08-24.** As first reported it used a cold
Q₀ of **8,462** — the undercoupled branch, wrong for the cold case. Old values:
0.9295 / 0.9748 / 0.9890 / 0.9886 / 0.9814.

🔑 **Q₀ IS NOW DERIVED WITHOUT THE BRANCH AT ALL:**

    1/Q_L = 1/Q0 + 1/Q_ext   ->   Q0 = 1 / (1/Q_L - 1/Q_ext)

Q_L from the LINEWIDTH, Q_ext = **9,117** from the eigen pair (geometry, one
measurement for the whole sweep). **The dip depth never enters, so β vs 1/β
cannot arise.**
🔴 **THE REFERENCE COMES FROM EIGEN (43,523), NOT FROM THIS FORMULA.** The cold
cavity is overcoupled, which is exactly where `1/Q_L − 1/Q_ext` subtracts two
near-equal reciprocals: the relative error amplifies by **Q₀/Q_L = 5.8×**, so
driven's 7% on Q_L becomes 40% on Q₀ (it gives 30,220 against eigen's 43,523).
Eigen with the port shorted measures Q₀ **directly** — no port loss to subtract.
✅ **Loaded cases are safe**: amplification is 1.01–1.07×, so Q₀ ≈ Q_L there.
⚠️ §7t is not violated. Eigen and driven agree on f₀ to 12 kHz — same cavity.
This imports the better-conditioned estimate of ONE quantity, and says so.
🔑 **η is insensitive to the choice**: 43,523 vs 40,645 moves every η by ≤0.001,
because Q₀_loaded ≪ Q₀_cold. **η is robust exactly where Q₀ is not.**
🔑 **f₀, Q_L and the linewidths are UNCHANGED** — they never depended on the
branch. Only Q₀ and η did. **The measurement was sound; the interpretation was
not**, which is why the raw columns are kept beside the derived one.

✅ **F1 DOES NOT FIRE.** η = **0.9979** at ne=1e19 against a 0.5 threshold. **Mass
loading is not a hard EM constraint** — now on the grooved cavity, where the
discarded groove-free version of this claim was not.
🔑 **η PLATEAUS AT 0.995–0.998 across the overdense range**, and the plateau is
real rather than saturating: Q₀ falls to 93 then **recovers to 158** at 1e20 as
the plasma turns reflective, so η is flat, not monotonic.
🔑 **THE BAND HOLDS.** Cumulative pull **+30.9 MHz**; at n_e = 1e20, **f₀ sits
17.6 MHz below 2.500** — and f₀ is the criterion, because the tuner parks there.
⚠️ **This paragraph previously read "the upper 3 dB edge sits 9.6 MHz below 2.50…
which is why groove size is a variable".** BOTH halves are now corrected: the
criterion is f₀ (2× more headroom) and Phase B showed **geometry has ~1 MHz of
authority over it regardless**. The 5 × 10 groove is optimal, not provisional.

⚠️ **β IS LOW-CONFIDENCE FROM 3e18 UP** — 0.011–0.026 against dips of −0.19 to
−0.45 dB. The loaded branch is now CHECKED rather than assumed (Q_ext ≈ 9,117
predicts 0.065 at 1e18 against 0.070 fitted), but the shallow dips still make
the magnitudes soft. **η is robust where β is not**: Q_L comes from a linewidth
resolved by 50–130 samples, and η now uses a branch-corrected reference.
⚠️ **ONE MINIMUM IN BAND IS NOT BAND CLEARANCE.** A driven sweep shows what the
PORT COUPLES TO, not what exists. The other two minima (≈2.38 and 2.6064) sit
outside the band, but mode COMPETITION is an eigen question.

## ✅✅ WHAT THE GROOVE IS ACTUALLY FOR — measured 2026-08-24, `h3_loopq` F4
**Anchor: the same 11×8 loop and an identical mesh, groove present or absent.**

| loop 11×8 | Q₀ | Q_L | Q_ext | β | purity | spread |
|---|---:|---:|---:|---:|---:|---:|
| **NO groove** | 30,878 | 22,024 | **76,811** | **0.402** under | **0.7593** | **0.2407** |
| **grooved 5×10** | **43,422** | 7,613 | **9,231** | **4.704** OVER | **0.9997** | 0.0003 |

🔑 **MECHANISM, AND IT IS NOT THE ONE H2 ESTABLISHED.** Ungrooved, TE011 and
TM111 are **exactly degenerate** (χ′₀₁ = χ₁₁ identically). The coupling loop
mixes them freely and what remains is a **hybrid**: purity 0.76. Grooved, TM111
sits 63 MHz away, the loop has nothing to mix TE011 *with*, and it stays at
0.9997.

✅ **THIS IS A SECOND, INDEPENDENT JUSTIFICATION FOR THE GROOVE.** H2 justified
it on **band clearance** — TM111 pushed out of the LDMOS tuning range. This is a
different failure the same part prevents: **without it, the coupler destroys the
mode it is trying to couple to.** Band clearance is about what the tuner locks
onto; this is about whether a clean TE011 survives having a feed attached.

🔑 **AND THE GROOVE IS WHAT MAKES THE COUPLING WORK AT ALL:**
- **Q_ext 76,811 → 9,231 — the loop is 8.3× more effective with the groove.**
- **β 0.402 → 4.704 — a 12× change that CROSSES from under- to overcoupled.**
- Q₀ +41%, and the mode goes from a blend to clean.

The hybrid's H_r is redistributed, so a loop that links H_r couples to it far
more weakly. **Coupling design on an ungrooved cavity would have optimised the
wrong structure entirely.**

✅ **IT ALSO EXPLAINS A NUMBER THAT HAS BEEN IN THE RECORD SINCE E0.**
**"29,854 = loop, no groove"** sits **3.4%** from the 30,878 measured here.
**That reference was never TE011's Q — it was a TE011/TM111 hybrid's.** Which is
why the loop appeared to cost 33% of the cavity's Q. **The loop costs 2.2%; the
DEGENERACY cost the rest.**
⚠️ Calling the 0.76-purity mode "TE011" is a stretch — it is the TE011-dominant
half of a pair, exactly the situation `e0k2_anchor` warned of: *a driven dip is
TWO overlapping resonances and a single-Lorentzian fit returns NEITHER Q.*

## ✅ LOOP SIZE — Q₀, Q_ext and β, by EIGEN PAIRS (`h3_loopq`, 2026-08-24)
**No |S11|, no depth, no Lorentzian, no phase, no branch decision.**

    Q0 = eigen port_bc="pec"   ·   Q_L = eigen port_bc="lumped"
    1/Q_ext = 1/Q_L - 1/Q0     ·   beta = Q0/Q_ext

| area mm² | f₀ GHz | Q₀ | Q_ext | β | Q cost | spread |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 2.450561 | 44,414 | — | — | — | 0.0015 |
| 35 | 2.450818 | 44,196 | 19,633 | 2.251 | 0.5% | 0.0001 |
| 82 | 2.451084 | 43,946 | 11,202 | 3.923 | 1.1% | 0.0000 |
| **176** | 2.451633 | 43,422 | **9,231** ← min | **4.704** ← max | 2.2% | 0.0003 |
| 384 | 2.452526 | 41,747 | 13,333 | 3.131 | 6.0% | 0.0010 |

🔴 **COUPLING PEAKS AT 176 mm² — THE DESIGN LOOP IS AT THE OPTIMUM.** Q_ext
falls, bottoms, then RISES. Ordinary transformer behaviour: mutual inductance
grows with area but the loop's SELF-inductance grows faster, so
k = M/√(L_loop·L_cav) peaks and falls. **A loop can be too big to couple well.**
🔴 **384 mm² IS STRICTLY DOMINATED** — weaker coupling AND 6.0% Q cost against
2.2%. It is retired, not a candidate.
🔑 **TO APPROACH MATCHING, GO SMALLER — AND SMALLER IS ALSO CHEAPER IN Q.** Both
axes point the same way. Every grooved size here is OVERCOUPLED; β = 1
extrapolates to **~10 mm²** on the small-area branch.
⚠️ **Extrapolate only on the small-area branch.** The curve has a turning point;
a monotonic fit through it is meaningless — the same error the groove-depth law
was retired for.

✅ **F1 DOES NOT FIRE.** Q₀ falls monotonically with area, as a larger obstacle
must. **The driven anomaly (Q₀ rising 20,005 → 30,112) was an artefact of the
driven extraction, not physics.**
⚠️ **The branch is only a PARTIAL explanation.** If the branch were the whole
error the ratio Q₀_eigen/Q₀_driven would equal β at every size. It does at
35 mm² (2.21 vs β=2.251) and **not** at 82/176/384 (1.76, 1.53, 1.39 vs β =
3.9, 4.7, 3.1). Those driven cases were also **groove-free** and some predate
the port-meshing fix. **Do not record the anomaly as fully explained.**
✅ V1 reproduced `h3_step3` at 11×8 to 0.2 / 1.0 / 1.3 / 1.5% — **across two
mesh styles**, so the eigen-pair method is portable.
✅ V4: the 35 mm² loop sits 0.5% from the no-loop Q₀. ✅ F2 does not fire —
purity is untouched at every size (worst spread 0.0010 at 384 mm²).

## 🔑 THE TUNER ARCHITECTURE, AND THE TWO CORRECTIONS IT FORCES
**User, 2026-08-24: dual directional coupler at the LDMOS output reading forward
and reflected · frequency sweep + PID to minimise reflected · PIN-diode tuner for
magnitude · circulator.**

✅ **Two degrees of freedom, which is what a complex match needs.** At resonance
the cavity is purely resistive, so **frequency zeroes the REACTANCE** and the
**PIN tuner transforms the RESISTANCE**. The architecture is sound in principle.

### 🔴 CORRECTION 1 — THE BAND MARGIN IS f₀, NOT THE 3 dB EDGE
**Everything I quoted as "margin" until now used the upper 3 dB edge. Wrong
criterion.** A frequency-tracking tuner **PARKS AT f₀**, and the LDMOS emits at
one frequency — the cavity linewidth is not a band-occupancy constraint.
*(This was `h3_margin`'s F2 declared assumption; the user's answer resolves it.)*

| n_e | f₀ | **margin (f₀ → 2.500)** | as previously quoted (3 dB) |
|---|---:|---:|---:|
| 1e18 | 2.4520 | **48.0 MHz** | 45.8 |
| 1e19 | 2.4608 | **39.2 MHz** | 25.8 |
| 3e19 | 2.4740 | **26.0 MHz** | 13.0 |
| 1e20 | 2.4824 | **17.6 MHz** | 9.6 |

🔑 **The margin situation is roughly TWICE as comfortable as this record said.**
✅ **Phase B's conclusion is UNCHANGED** — recomputed on f₀ the grid spans
17.4–18.2 MHz, i.e. **0.8 MHz of geometric authority** against 0.7 before.
**Only the absolute headroom doubles; geometry still cannot move it.**

### 🔴 CORRECTION 2 — THE MATCH IS WORST AT ~1e19, NOT AT 1e20

| n_e | β | **VSWR** | into circulator dump @1 kW |
|---|---:|---:|---:|
| cold | 4.715 | 4.7 | 423 W |
| 1e18 | 0.064 | 15.6 | 773 W |
| **1e19** | 0.010 | **99.3** | **961 W** |
| 3e19 | 0.010 | 96.2 | 959 W |
| 1e20 | 0.017 | 58.4 | 934 W |

🔑 **Because Q₀ MINIMISES at 1e19 (93) and recovers to 158.** The PIN tuner's
hardest job is in the MIDDLE of the density range, not at the top — non-obvious,
and exactly what a monotonic assumption would miss.
🔴 **The circulator dump is a near-full-power component**, and its worst case is
mid-density. Whether it ever sees that depends on the PIN tuner's range against
**VSWR 99**, which is now the specification that matters most.

### 🔑 TWO THINGS FOR THE CONTROL DESIGN
- **The tuner REVERSES DIRECTION during ignition.** Cold is **OVERCOUPLED**
  (β = 4.715); loaded is **UNDERCOUPLED**. It passes through unity transformation
  at **n_e ≈ 5×10¹⁶** and must then transform the OTHER way — while the frequency
  loop slews **+30.9 MHz** over the same transient. Both loops move fast and one
  changes sign.
- ⚠️ **A reflected-power minimiser sees a TRUE NULL at that crossing.** The match
  point is passed, not approached.

### ✅ AND THE AXES NOW AGREE ON LOW DENSITY
Band margin prefers low n_e · VSWR prefers low n_e · η peaks at 1e19 but spans
only 0.9864–0.9979 across the whole range. **1e18 wins on margin (48 MHz) AND
match (VSWR 15.6) for a 1.2-point η penalty.** Lower density is better on
essentially every electromagnetic axis — which sharpens why anchoring n_e
(§7ab) is the top open question.

## ✅ THE MATCHING NETWORK IS A HARDWARE REQUIREMENT — so β is a TUNER SPEC
**User, 2026-08-24: *"The intended hardware definitely requires a matching
network."* That settles the open question and changes what β MEANS.**

🔴 **"~93% of incident power reflects" and "6.6% delivered" ARE WITHDRAWN as
system numbers.** They were the raw, UNMATCHED coupling of a bare 50 Ω port —
a modelling boundary condition, not the machine. **Do not quote them.**

✅ **What the measurement actually specifies is the TUNER'S RANGE:**

| state | Q₀ | β | Z at the port |
|---|---:|---:|---|
| cold (no plasma) | 43,523 | **4.715** | 236 Ω (or 11 Ω) |
| 1e18 | 593 | 0.064 | 3.2 Ω (or 778 Ω) |
| 1e19 | 93 | 0.010 | 0.50 Ω (or 4,963 Ω) |
| 1e20 | 158 | 0.017 | 0.86 Ω (or 2,921 Ω) |

🔑 **THE TUNER MUST TRACK A FACTOR OF 275 IN β** (4.715 → 0.017), and
🔑 **IT CROSSES PERFECT MATCH AT n_e ≈ 5×10¹⁶ — essentially the instant of
ignition.** The system is OVERCOUPLED before that point and progressively
UNDERCOUPLED for every density after it.
⚠️ **A controller that hunts on reflected power passes through a true null
during the ignition transient.** The match point is not the destination; it is
crossed on the way to a deeply undercoupled steady state. Worth knowing before
tuning logic is written.
⚠️ The transformation at steady state is ~58:1. A 3-stub tuner does ~20:1
comfortably, so this is a real specification, not a formality — and a
high-ratio match is narrowband against a 16 MHz linewidth.

✅ **THIS UNBLOCKS "NET INTO PLASMA", WHICH THE RECORD BANNED.** It was banned
because β's branch was unresolved. β is now resolved from eigen pairs, and the
match is confirmed, so **net ≈ η × (match efficiency)** with η = 0.996. The only
missing term is tuner loss, which is a component spec, not a solve.

⚠️ **VIEWPORT, LIGHT TRAP AND CHIMNEY ARE DELIBERATELY OUT OF SCOPE** (user,
2026-08-24) — and they would not move β regardless. `GEO` disabling them is
intentional gating, NOT the groove omission's shape. **This is settled; do not
re-raise it.**

## ✅✅ H3 IS COMPLETE — the HOT leg, measured 2026-08-24 (`h3_hot`)
**Cold, hot and loaded are now all measured. H3 asked for all three.**

**Unloaded, no plasma, wall temperature scaled** (α = 23.1e-6/K on every
dimension — cavity, groove, loop, wire, gap — and σ by 1/(1+α_R·ΔT)):

| T_wall | ΔT | f₀ GHz | Δf | Q₀ | Q_ext | β | VSWR |
|---:|---:|---:|---:|---:|---:|---:|---:|
| **293 K** | +0 | 2.451633 | — | 43,422 | 9,231 | 4.704 | 4.7 |
| **393 K** | +100 | 2.445935 | **−5.70** | 36,374 | 9,194 | 3.956 | 4.0 |
| **493 K** | +200 | 2.440206 | **−11.43** | 31,938 | 9,229 | 3.461 | 3.5 |

✅ **V1 passes to 0.00–0.01%** on all four quantities against `h3_loopq` — the
anchor is bit-identical, so the sweep is trustworthy.
✅ **V2 — Δf/f = −αΔT** to 0.034 / 0.100 MHz. This is a GEOMETRY identity, so it
confirms the scaling reached the mesh rather than telling us physics.
✅ **V3 — Q₀ follows E0's √σ law** to 0.14% / 0.26%. **E0's law survives into the
hot regime.**
✅ **V4 — purity untouched** (worst spread 0.0003). Uniform scaling leaves the
mode shape alone, as it must.

🔑 **THE NEW RESULT: Q_ext IS THERMALLY INVARIANT.** ×0.9960 at +100 K, ×0.9997
at +200 K — flat, while Q₀ falls ×0.838 and ×0.736. **The loop expands with the
cavity and the coupling does not change**, so **β tracks Q₀ directly** (×0.841,
×0.736). F3's assumption is measured, not assumed.
🔑 **CONSEQUENCE FOR THE CONTROL LOOP:** the cold-to-hot difference is ENTIRELY
Q₀'s. A temperature reading gives f₀ as a computed offset (−5.70 MHz/100 K) and
β from Q₀ alone. **One sensor, two derived quantities, no search.**

🔴 **GLOSSARY's "Q × 0.78 at +100 K" IS NOT REPRODUCED — we measure ×0.838.**
That is exactly √σ with standard aluminium α_R = 4.29e-3/K. **0.78 would need
α_R = 6.44e-3/K, ~1.5× aluminium.** σ is an INPUT here, so this does not disprove
0.78 — but it does establish that **plain resistivity gives 0.838, and if 0.78 is
right the extra loss is something else.** Someone should say where it came from.

⚠️ **A LIMIT ON HOW FAR THIS SCALING CAN BE PUSHED.** V2's residual grows
non-linearly — 0.034 MHz at +100 K, 0.100 at +200 K — and uniform scaling makes
f ∝ 1/scale EXACTLY, so that is numerical. Tets go 43,685 → 43,717 → 44,018
(+0.76%) while volume grows 1.39%, so element density drifts with scale. **A
systematic, not noise.** Fine at these ΔT; do not extrapolate to +500 K.
⚠️ Wall σ(T) uses α_R = 4.29e-3/K, standard aluminium — an ASSUMPTION, and the
one GLOSSARY disagrees with.

## ~~🔴 H3's HOT LEG IS NOT DONE~~ — superseded by the above

**H3 asks for sustainment across COLD / HOT / LOADED. Cold and loaded are
measured; HOT never has been.** Nothing in the tree scales dimensions for
temperature, and the only `"hot"` string in a result file is a mislabelled
plasma density — the exact confusion GLOSSARY exists to stop.

**What the record already gives** (α = 23.1e-6/K, wall σ falling with T):

| wall ΔT | f₀ (unloaded) | Q₀ | β | VSWR |
|---|---:|---:|---:|---:|
| +0 K | 2.4515 | 43,523 | 4.715 | 4.7 |
| +100 K | **2.4458** | 33,948 | 3.678 | 3.7 |
| +200 K | 2.4401 | 26,479 | 2.869 | 2.9 |

🔑 **THE EFFECT SPLITS CLEANLY BY REGIME:**
- **Frequency — every state.** −5.7 MHz per 100 K, purely geometric. It pulls
  **OPPOSITE to the plasma** (+30.9 MHz), so **heating BUYS BACK margin.**
- **Match — UNLOADED ONLY.** Loaded, the plasma is **275×** the wall loss, so
  Q₀ moves 158.0 → 157.8 at +100 K. **Loaded β belongs to the plasma.**

✅ **AND THE REQUIREMENT THIS CREATES IS ONE SENSOR.** Given a cavity wall
temperature, f₀ is a computed offset from the cold value rather than something to
search for. **`../control-loop/` needs a temperature input; that is the whole
consequence.**
⚠️ **DO NOT OVERSTATE IT.** GLOSSARY calls HOT *"the regime that decides whether
the instrument restarts itself"* — that is emphasis, written to stop HOT being
dropped, **not a finding.** A hot cavity can be allowed to cool, or cooled
harder. **HOT is a parameter to read, not a barrier.**
🔑 **Still worth measuring** — one eigen solve at scaled dimensions and reduced
σ, two or three temperatures to check the coefficients are linear. **Cheap, and
it closes H3.**

## 🔴 THE LOOP WAS FORCED, NOT DESIGNED — and the tuner conclusion rests on it

**User, 2026-08-24: *"some kind of loop was forced so we could evaluate driven,
but we never evaluated the design options."*** A DRIVEN solve needs a port; a
port needs a loop; a loop was picked. **It was an instrument requirement, and no
coupler design exercise ever followed.**

| parameter | value | provenance |
|---|---|---|
| `CAP_R_FRAC` | 0.4805 | ✅ **DERIVED** — J₁ peak, 1.8412/χ′₀₁; a STATIONARY point, so tolerance-insensitive (H1's argument) |
| `LOOP_LD, LOOP_LW` | 11 × 8 mm | ✅ **justified retrospectively** — `h3_loopq` found Q_ext minimises at 176 mm² |
| `LOOP_PHI` | **36°** | ⚠️ **a MESHING choice** — a sector centre at N=5 (72° wedges → centres 36/108/180/252/324). **EM-irrelevant for TE011**, which is m=0 and axisymmetric. Coupled to the sector binning and to the port `Direction` — R47 died in 7 s when the loop moved to 36° and Direction stayed at 0 |
| `LOOP_RW` | 1.0 mm | 🔴 **NO PROVENANCE, NEVER SWEPT** |
| `LOOP_GAP` | 0.3 mm | 🔴 **NO PROVENANCE**, and fails its own comment: *"gap must stay ≪ wire radius"* is 0.3/1.0 — a factor of 3 |

🔴 **`h3_loopq` SWEPT AREA ONLY.** Fixed wire radius, fixed cap radius, single
turn, rectangular. **Q_ext floored at 9,231 WITHIN THAT FAMILY. The family was
never chosen**, and the loop's self-inductance goes as ln(1/r_w), so the turning
point at 176 mm² is itself a function of an arbitrary constant.

🔑 **AND THIS REOPENS THE TUNER PROBLEM'S FRAMING.** `../control-loop/` recorded
magnitude tuning as unsolved with both upstream levers spent. **One of them is not
spent:**

| target | VSWR | Q_ext needed | vs 9,231 |
|---|---:|---:|---:|
| as built | 85 | 9,350 | 1.0× |
| **comfortable 3-stub tuner** | **20** | **2,200** | **4.2×** |
| matched | 1 | 110 | 84× |

**β = 1 needs 84× and is very likely unreachable. VSWR 85 → 20 needs 4.2×** — the
difference between "no part exists" and "a standard tuner works". **Whether loop
design can deliver that has never been asked.**
⚠️ ❌ Aperture coupling stays closed (patented; and the cavity IS the waveguide,
so there is no shared wall for an iris). **This is about the LOOP family, not a
return to apertures.**

## 🔴🔴 β WAS REPORTED AS AN OBSERVATION. IT IS A DESIGN OUTPUT.

**User, 2026-08-24: *"we designed a loop and then complained about
over/undercoupling as if we needed to simply accept the loop geometry as
given."*** ✅ **Correct, and it is worse than the provenance gap above.**

🔑 **Q₀ is the cavity and the load. Q_ext is THE LOOP, and nothing else.**
β = Q₀/Q_ext. So *"the cavity is overcoupled cold at β = 4.7 and undercoupled
loaded at β = 0.012"* is a **category error**: the cavity is not coupled to
anything. **The LOOP WE CHOSE is. Every β in the record is a statement about a
part we picked, written as though it were a property we found.**

⚠️ **And the programme then reasoned FORWARD from it** — β range → VSWR ~100 →
45 A → 960 W dump → *"magnitude tuning is unsolved"*. **A chosen value became a
constraint, and the constraint became a hardware impossibility.**

### The design question that was never asked: *what Q_ext do we WANT?*

| state | Q₀ | **Q_ext wanted (β=1)** | built | off by |
|---|---:|---:|---:|---:|
| **COLD** — build field to ignite | 43,422 | **43,422** | 9,231 | **4.7× too LOW** |
| **LOADED** @ anchored 7.9e18 | 109 | **109** | 9,231 | **85× too HIGH** |
| loaded @ 1e20 (old assumption) | 158 | 158 | 9,231 | 58× too high |

✅ Q₀_loaded is recovered two independent ways and they agree: 1/(1/155 − 1/9231)
= **158** from the measured loaded Q_L, and 9231/85 = **109** from VSWR at the
anchored density (Q₀ minimises near 1e19, so the anchored point is the lower).

## 🔴 THE FINDING: THE TWO STATES WANT LOOPS 400× APART

**No FIXED loop can be matched in both, by a factor of ~400.** This is
structural — it follows from Q₀ collapsing 43,422 → 109 when the plasma lights —
and **it is not a sourcing problem, a tuner problem, or a parts problem.**

🔑 **THIS IS THE REAL SHAPE OF `../control-loop/`'s REQUIREMENT 1**, and it is a
better statement than *"magnitude tuning is unsolved"*: **the tuner was being
asked to absorb a 400× swing that the COUPLER could absorb part of, and nobody
asked the coupler.** Cold and loaded do not merely *"not peak together"* — they
want opposite loops.

### Where the built loop actually sits: at MAX COUPLING on 3 of its 5 axes

| axis | built | status |
|---|---|---|
| cap radius | 0.4805a | ✅ **already the J₁ PEAK = max coupling.** No headroom |
| orientation | normal to B | ✅ **already max.** No headroom |
| area | 176 mm² | ✅ **already the sweep's Q_ext MINIMUM.** No headroom *in area* |
| **turns** | **1** | 🔴 **NEVER TRIED** |
| **mount** | **cap** | 🔴 **NEVER COMPARED** to the barrel wall |

⚠️ **I FIRST WROTE "so the 84× must come from TURNS or MOUNT". BOTH HALVES WERE
WRONG**, and checking `geometry.py` before writing the rig is what caught it:

🔴 **TURNS IS NOT BUILDABLE.** `geometry.py`'s loop takes `loop_d, loop_w,
loop_rw, loop_gap, loop_cap_r, loop_gap2, loop_phi, loop_tilt, loop_flange_r/t`
— **there is no turns parameter and no helix.** Multi-turn is new OCC geometry,
not a rig. **Item 7's turns sweep is a geometry project, not an afternoon.**

## 🔑🔑 AND THERE IS A THIRD AXIS, ALREADY IMPLEMENTED, THAT I HAD RULED OUT

**`geometry.py:443–451` — the SERIES CAPACITOR (`loop_gap2` + `loop_flange_r`),
a break in the conductor that resonates out the loop's own inductance:**

> *"0.196 pF cancels the loop's **332 ohm** self-reactance, raising coupled power
> **~45×** and taking **Q_ext from 14,442 to ~320** — exactly what R56 measured
> as the requirement for matching a lit plasma. **It had never been simulated:**
> Palace's lumped-port R and C are in PARALLEL, so setting C on the port does not
> create a series element."*

🔑 **45× IS THE RIGHT ORDER FOR THE PROBLEM.** Against our Q_ext = 9,231 it lands
near **205**, versus the **109** that β = 1 needs at the anchored density — and
far past the **2,200** that makes a 3-stub tuner comfortable. **This is a
mechanism for the 84×, not a nibble at it.**

⚠️ **STATUS, STATED HONESTLY (§7ac):**
- The 45× is **CALCULATED, NEVER SIMULATED** — the comment says so itself.
- Numbers are **R-era, on a DIFFERENT cavity** (Q_ext 14,442, not 9,231).
- 🔴 **The one attempt FAILED**: a bare wire end at a meshable 0.5 mm gap gives
  **0.056 pF (−1183 Ω)**, which BLOCKS the loop current instead of resonating it
  — **measured, |Γ| 0.568 → 0.904, coupling got WORSE.**
- ✅ **The failure was DIAGNOSED and the fix implemented but never tested:**
  C = ε₀A/d says the lever is **AREA, not gap** → **flange discs, r ≈ 1.9 mm at
  0.5 mm**, which is also the more buildable part. `loop_flange_r` exists.
- ⚠️ **Barrel-only** — `--loop-gap2` is refused with `--loop-cap`, and the
  current design IS a cap loop. **So mount and capacitor are coupled**, and must
  be changed in that order, not together.

🔴 **THE COUPLING FIX WAS ALREADY IDENTIFIED, IMPLEMENTED, AND NOT CARRIED
OVER.** This programme measured β, called it a property, and derived a hardware
impossibility from it — **while a mechanism sized at 45× sat unused in the
geometry builder.** §7am and §7an in one object.
⚠️ **And 176 mm² is the best of the four for LOADED and the WORST for COLD** —
`h3_loopq` optimised without ever saying *for which state*.

### ⚠️ UNVERIFIED ANALYSIS (§7ac) — turns depend on a mechanism we never identified

The area sweep TURNS OVER between 176 and 384 mm². **Why it turns over decides
the sign of the turns axis**, and both readings fit the data:

| perimeter | 0.138λ | 0.212λ | **0.311λ** | 0.459λ |
|---|---:|---:|---:|---:|
| Q_ext | 19,633 | 11,202 | **9,231** | 13,333 |

- **If FOOTPRINT-limited** (flux cancels across a big loop): Q_ext ∝ 1/(A·N)², so
  **N=2 → Q_ext 2,308, VSWR 21 — that IS the 3-stub target.** But the conductor
  reaches 0.62λ.
- **If ELECTRICAL-LENGTH-limited** (the turnover sits exactly where a loop stops
  being magnetically small): at fixed length A ∝ (L/N)², so A·N ∝ L²/N and
  **turns make it 4× WORSE at N=2.**

🔴 **Same parameter, opposite sign, decided by a mechanism nobody measured.**
**This is one cheap eigen sweep** (Q_ext vs N at fixed footprint) and it settles
whether `../control-loop/` requirement 1 is impossible or off-the-shelf.

## ✅ THE TEMPERATURE AXIS — n_e is a THERMOMETER, not a free parameter
**Computed 2026-08-24 from constants already in the code. No literature values.**

Under LTE, Saha fixes n_e from the gas temperature. Re-expressing the measured
EM grid on that axis turns an unanswerable question into a checkable one:

| n_e | **T_gas** | margin (f₀→2.500) | η | VSWR |
|---:|---:|---:|---:|---:|
| 1e18 | **4,654 K** | 48.0 MHz | 0.9864 | 15.6 |
| 3e18 | 4,950 K | 46.6 | 0.9951 | 43.3 |
| 1e19 | 5,320 K | 39.2 | **0.9979** | **99.3** |
| 3e19 | 5,709 K | 26.0 | 0.9978 | 96.2 |
| 1e20 | **6,207 K** | 17.6 | 0.9964 | 58.4 |

🔑 **"n_e = 1e20" IS A CLAIM THAT THE GAS SITS AT ~6,200 K.** That is a far more
checkable statement than a density: gas temperature is measurable by optical
emission and is what the analytical chemistry actually specifies, since
atomisation and excitation set a temperature requirement.
🔑 **THE WHOLE MEASURED RANGE IS ONLY 4,650–6,200 K.** n_e moves **two decades
over ~1,500 K** — exponentially sensitive. A loose temperature spec still
brackets n_e usefully, but a 500 K error is a 5–10× error in n_e and therefore a
large error in VSWR.
✅ **So the anchoring question is now: WHAT GAS TEMPERATURE DOES THE ANALYSIS
NEED?** That belongs to `../spectroscopy/`, and Saha converts the answer.

⚠️ **ASSUMPTIONS, and they matter (§7ac — this is a CALCULATION, not a
measurement):** **LTE** — a 1 kW atmospheric MIP is plausibly near-LTE but not
guaranteed; **non-LTE puts n_e ABOVE Saha-at-T_gas, so this is a LOWER BOUND**.
**Full N₂ dissociation** — fine above ~5,000 K, unreliable below. **Atomic N
ionisation at 14.53 eV**, g_i/g_0 = 9/4.

## 🔴 n_e, NU_M AND T_gas ARE ONE STATE — THE CODE SETS TWO OF THEM SEPARATELY

`h3_loaded.py` carries **`NU_M = 1.0e11  # electron-neutral collision rate, N2 at
1 atm`** — with **no temperature**. But a collision RATE at fixed PRESSURE *is* a
temperature statement: ν_m = n_gas·⟨σ_m v_e⟩, and n_gas = P/kT.

🔴 **So NU_M is a second unanchored constant of exactly the §7ab species**, and
it is **not independent of n_e** — both are functions of the same plasma state.
⚠️ Inverting it is weak: depending on the assumed momentum-transfer cross-section
and electron temperature it implies anywhere from **2,500 K to 6,900 K**. **Do
not use it to pin anything** — it is quoted here only to show the coupling is
real and currently unhonoured.

✅ **THE RULE THIS IMPLIES:** n_e, NU_M and T_gas must be set from ONE state, not
as three separate constants. Whatever anchors the temperature must set all three.

## 🔴🔴 THE MODEL WAS SIMPLIFIED AND NEVER RESTORED — SCOPE REOPENED 2026-08-24

**User: *"We simplified greatly to answer the instrument and methodology issues,
and then didn't add critical features back."*** That is the correct diagnosis and
it is better than "the rigs modelled the wrong cavity": the simplification was
DELIBERATE and RIGHT for isolating instrument behaviour. **The failure is that
nothing put the features back.**

| feature | design | every model | status |
|---|---|---|---|
| **groove** | 5 × 10 mm | `--groove 0,0` for 31 rigs | ✅ restored 2026-08-23 |
| **port boundary** | 50 Ω feed | unassigned = PMC = gap OPEN | ✅ restored (GATE 4) |
| **torch material** | **sapphire ε = 11.6** | ε = 1 or no torch body at all | 🔴 **BACK IN SCOPE** |
| **gas feed aperture** (−z cap) | torch penetrates to its plumbing | `--feed 0,41` = absent | 🔴 **BACK IN SCOPE** |
| **chimney / exhaust** (+z cap) | 21 mm bore | `--chimney 0,41` = absent | 🔴 **BACK IN SCOPE** |
| viewport + light trap | radial apertures | `--viewport 0`, `--trap 0,0,0` | ⏸️ **stays OUT — axial vs radial not chosen** |

🔴 **NO RIG HAS EVER PASSED A NON-ZERO CHIMNEY OR FEED.** They were not disabled
by a regression; **they were never restored after the simplification.** And R49
added the feed *because* its absence was a defect — `geometry.py`: *"until now
the model ended the tube flush against solid metal — the aperture did not exist
at all."*
⚠️ **As modelled, the torch is sealed at both ends by solid metal.** Gas cannot
enter or leave. That is not a machine.

### ⚠️ THE FEED APERTURE — an alarm I raised and then WITHDREW the same hour

🔴 **I claimed the sapphire torch "may have removed the RF seal". IT DOES NOT.**
That came from a UNIFORM-FILL cutoff calculation — treating the whole 21 mm
aperture as solid sapphire — which is not the geometry. **Weighting by the actual
TE11 field distribution:**

| | ε_eff | attenuation over 41 mm | uniform-fill claimed |
|---|---:|---:|---:|
| air | 1.00 | 59.7 dB | 59.7 |
| quartz | 1.52 | 58.2 dB | 51.3 |
| **sapphire** | **3.00** | **53.8 dB** | **4.6** ❌ |

**The ceramic annulus holds only 18.8% of the field energy** — 75.3% is in the
gas core, 5.9% in the outer gap — so ε_eff = 1 + (ε−1)·0.188 = 3.0, not 11.6.
**The seal holds at ~54 dB.**
⚠️ **First-order perturbation**, so it assumes the field does not redistribute; a
real ε = 11.6 region pulls field into itself, raising ε_eff and lowering the
attenuation. **53.8 dB is an UPPER bound** — but 20 dB of seal needs ε_eff > 10.5,
which is far from 3.0.

🔑 **THE LESSON IS THE ERROR, NOT THE NUMBER.** A 4.6-to-60 dB bracket was
presented with its pessimistic end in the voice of a result. **The bound was not
merely wide — its bad end corresponded to a geometry that does not exist.**
CONVENTIONS §7ak.

✅ **The aperture stays IN SCOPE** — it is a real feature, absent from every
model, and it interrupts cap currents whether or not it seals. But it is a
COMPLETENESS item, **not an alarm**, and it ranks below the torch material: ε =
11.6 vs ε = 1 in the CAVITY is a ~15 MHz frequency effect that certainly matters.

## 🔴 THE TORCH ITSELF## 🔴 THE TORCH ITSELF — five rigs mesh it as VACUUM, three omit it entirely
**Found 2026-08-24 while designing E3. Not yet quantified on the design cavity.**

`geometry.py`'s default torch is **sapphire, ε = 11.6, tanδ = 3.5e-5**, and the
file states why in terms:

> *"R99: the build is ALL SAPPHIRE and PERMANENT (not a swappable consumable),
> so sapphire is the DEFAULT — **simulating quartz by default would model a
> cavity we are not building.**"*

🔴 **AUDITED 2026-08-24 — AND IT IS EVERY RIG, IN ONE OF TWO WAYS:**

| rig | `--no-torch` | torch material | torch is |
|---|---|---|---|
| `h3_ladder`, `h3_loopq`, `h3_hot` | **KEPT** | — | **ABSENT — no torch body at all** |
| `h3_driven`, `h3_margin`, `h3_step3`, `h3_groove`, `h3_loopsize` | stripped | `1.0,3.5e-05` | **ε = 1 — vacuum** |

🔑 **AND THOSE TWO ARE THE SAME THING.** `h3_step3` compared a no-torch mesh
against a vacuum-torch mesh and got f₀ agreeing to **12 kHz** — which is what
"ε = 1" means. **So EVERY frequency in the record is for a TORCH-FREE cavity**,
and the design has a sapphire one. That is simpler and worse than "five rigs
differ from three".

**What it should and should not touch:**
- 🔴 **FREQUENCY — materially, and it reaches EVERYTHING.** `h4_field` measured
  a sapphire torch at **−15.00 MHz** on a bare cavity. ⚠️ That rig is groove-free
  and DISCARDED, so treat −15 MHz as an ORDER, not a number.
  🔑 **Plausible in magnitude**: at the torch radius (r ≈ 8.5 mm) TE011's E_φ is
  ~31% of its peak, so the tube sits in ~10% of peak energy density over a small
  volume — small, not negligible. −15 MHz is 0.61% of f₀.
  🔴 **If it transfers, the cold ladder (2.450467 / 2.450561 / 2.451490), the
  loaded pull, and every band margin are all high by that amount.**
- ✅ **Direction is favourable**: higher ε pulls f₀ DOWN, so the real cavity
  resonates BELOW what was modelled and **every band margin in the record is
  CONSERVATIVE** — by an unmeasured amount.
- ✅ **Q, η and β: little.** tanδ = 3.5e-5 either way, and those are ratios.
  PLAN puts the dielectric at *"~2% of the loss budget"* — itself untested.
- 🔴 **E3 cannot decompose a dielectric that is not there.** With ε = 1 the
  dielectric channel is nearly empty, which is why `e3_closure` meshes the
  DESIGN torch and re-meshes case E with vacuum to MEASURE the shift.

### ⏳ E3 CASE B HAS LANDED — the first grooved-cavity solve with the DESIGN torch

**2026-08-24, 808 s.** `wall=True, plasma=False, dielectric=False, torch_eps=11.6`.

| | `h3_loopq` 11×8 (no torch) | **E3 case B** (sapphire) | Δ |
|---|---:|---:|---:|
| f₀ | 2.451633 | **2.437762** | **−13.87 MHz** |
| Q_wall | 43,422 | **44,387** | **+2.2 %** |
| purity | 0.9998 | **0.9998** | — |

⚠️ **PROVISIONAL — this is NOT the torch shift, and E IS NOT ITS CONTROL.**
I wrote earlier that "E − B is the number to quote". **Wrong.** `e3_closure.py`
defines `E_vac_torch = (wall=True, plasma=True, diel=True, VACUUM)` — **E carries
the PLASMA; B does not.** They differ in TWO things. The rig's own torch-shift
line is `A_all.f0 − E_vac_torch.f0` — **A − E**, the matched all-loss pair.
🔴 **AND BOTH A AND E CARRY PLASMA, so both hit the preconditioner defect below.**
A has already timed out. **The torch shift is therefore NOT MEASURABLE by this
rig until the preconditioner is fixed** — a harder blocker than "one case failed".

✅ **What B does establish, provisionally:**
- **Magnitude and sign are as predicted.** −13.87 MHz sits between my Slater
  estimate (−11.24, outer wall only) and DISCARDED `h4_field` (−15.00, all tubes,
  bare cavity). **The ordering is the one the physics implies**, which is weak
  corroboration that the torch binding is reaching the solve.
- **F3 will not fire** (it wanted "order −10 MHz").
- 🔑 **Q_wall went UP, and that is expected, not an anomaly.** The dielectric
  stores energy in the torch, so the WALL takes a smaller share:
  Q_wall = ωW/P_wall rises because W rises. ⚠️ **Q_wall is not Q₀** — the
  dielectric's own loss is case D, and F2 fires if it exceeds ~5 %.
- 🔴 **A_all TIMED OUT at 2700 s / 226 NLEPS iterations.** Without Q_all there is
  **no closure**, so E3's falsifier cannot yet fire either way. B converging in
  808 s says the difficulty is the plasma term or the COMBINATION, not the torch
  — **C discriminates that**, and it is running now.

## 🔴🔴 `GEO_DESIGN` IS NOT THE DESIGN — it contains `--no-torch`

**User, 2026-08-25: *"Aren't the eigensolves based on bad torch geometry?"***
✅ **Yes, and the constant's NAME is the reason nobody noticed.**

`GEO` carries `--no-torch`, and `GEO_DESIGN` is built from `GEO` **changing only
the groove** — so **`--no-torch` survives into it.** ⚠️ CLAUDE.md instructs
*"Use GEO_DESIGN, not GEO — GEO is the BARE cavity... GEO_DESIGN is the cavity
being built."* **That is true about the groove and FALSE about the torch.**

| rig | value | what it actually meshed |
|---|---|---|
| `h3_loopq` | **Q_ext = 9,231**, Q₀ = 43,422 | `GEO_DESIGN` as-is → **NO TORCH BODY** |
| `h3_step3` | **Q_REF = 43,523** | driven-style mesh → torch at **ε = 1 (vacuum)** |
| `h3_driven` | **every operating-point number** | torch **ε = 1** + plasma region |
| `e3` case B | Q_wall = 44,387 | torch **ε = 11.6 — THE DESIGN** |

### 🔴 AND THE "9 % EIGEN↔DRIVEN Q_ext GAP" IS WITHDRAWN — I COMPARED TWO CAVITIES

**User, 2026-08-25: *"Comparisons between eigen and driven have to happen on the
same geometry (torch, cavity, everything)."*** 🔴 **Mine did not.**
Eigen **9,231** is `h3_loopq` on a **NO-TORCH** mesh. Driven **~8,400** is
`h3_driven` on a **vacuum-torch + plasma-region** mesh. **Different cavities —
so there is no measured disagreement to explain, and none to defend.**

⚠️ **I tried to wave it away with 43,422 vs 43,523 = 0.23 %.** That is a
legitimate no-torch-vs-vacuum-torch delta **for Q₀**, and it says nothing about
**Q_ext**, which is set by how the mode couples to the LOOP. **A quantity's
insensitivity does not transfer to a different quantity.**

### ⚠️ AND GEOMETRY-MATCHED IS NOT ENOUGH — THE MESH MUST MATCH TOO

`h3_step3` runs `cold` and `driven` styles to compare them, and meshes them at
**different resolutions by design**: `size_factor` **1.5 vs 1.42**, giving
**43,685 vs 80,621 tets**. **A comparison across those two carries a
discretisation difference as well as a geometry one**, and neither is separable
after the fact.

### ✅ THE AUDIT — which comparisons in this record are actually matched

| comparison | geometry | verdict |
|---|---|---|
| **E3 case E ↔ `h3_driven` @1e20** | both vacuum torch + plasma, 1e20 | ✅ **MATCHED** — the 70 kHz / 3.42 % agreement stands (⚠️ separately-built meshes) |
| eigen Q_ext 9,231 ↔ driven ~8,400 | **no-torch vs vacuum-torch** | 🔴 **VOID** |
| eigen cold Q₀ 43,422 ↔ driven re-fit 40,652 | **no-torch vs vacuum-torch** | 🔴 **VOID** — the "6.4 %" is not a method result |
| `h3_loopq` 43,422 ↔ `h3_step3` 43,523 | both eigen, no-torch vs vacuum | ✅ a **geometry** delta within one solver |

### ✅ MESH FINGERPRINTS — `h3_step3`'s "driven" style IS matched to `h3_driven`

| | tets | size_factor | torch |
|---|---:|---:|---|
| `h3_driven_cold` / `_n18p90` / `_n20p00` | **80,621** | **1.42** | body, ε = 1 |
| `h3_step3` **driven** style | **80,621** | **1.42** | body, ε = 1 |
| `h3_step3` **cold** style | 43,685 | 1.50 | **none** |
| `h3_loopq` | — | — | **none** (`GEO_DESIGN`) |

🔑 **So the eigen number that is geometry- AND mesh-matched to every driven
result is `h3_step3`'s driven-style pair — and `h3_loopq`'s `V1_ANCHOR` records
it as Q_ext = 9,117**, not the 9,231 that `h3_driven` hardcodes.
⚠️ **Which of `h3_step3`'s two styles produced 9,117 is NOT documented**, and its
result file is stale (it still carries the retracted Q = 12,368 / f₀ = 2.440003).
**Both eigen values, 9,117 and 9,231, sit ~8–9 % above the driven-implied 8,462**
— so the gap does not hinge on which one, but it is still an inference.
✅ **`h3_qext` measures it directly, on a mesh whose fingerprint is known.**

## ✅✅ F1 ANSWERED — eigen and driven DO disagree, and the gap is in Q_L alone

**`h3_qext`, 2026-08-25, cold, on the IDENTICAL mesh `h3_driven_cold.msh`
(80,621 tets) — no geometry difference left to blame:**

| | eigen pair | driven dip | gap |
|---|---:|---:|---:|
| Q₀ | 43,523 | 40,652 | −6.6 % |
| **Q_L** | **7,538** | **7,004** | **−7.1 %** |
| **β** | **4.7740** | **4.8041** | **+0.6 %** ✅ |
| Q_ext | **9,117** | 8,462 | −7.2 % |

🔑 **β AGREES TO 0.6 %. THE ENTIRE DISAGREEMENT IS Q_L** — and Q_L is the 3 dB
LINEWIDTH: **0.35 MHz sampled at 25 kHz, ~14 points across.** `h3_driven`'s own
docstring calls its cold case a **LOCATOR** for exactly this reason. **So this
is not a solver disagreement; it is a resolution limit on one side**, and it
lands on the quantity most sensitive to it.
✅ **Cold Q_ext = 9,117 (eigen) is the better number.** The driven 8,462 inherits
a 7 % linewidth error.

### ✅ AND IT REPRODUCES `h3_step3`'s V1_ANCHOR TO FOUR FIGURES

**recorded** Q₀ = 43,523 · Q_L = 7,538 · Q_ext = 9,117 · β = 4.774
**measured** Q₀ = 43,523 · Q_L = 7,538 · Q_ext = 9,117 · β = 4.7740

🔑 **This settles a question `baselines.json` recorded as unanswered:** which of
`h3_step3`'s two mesh styles produced 9,117. **The vacuum-torch one.** The
registry entry now carries the reproduction as its verification.
⚠️ **And it confirms `h3_driven` imports the wrong one** — it hardcodes 9,231,
the NO-TORCH value, while meshing vacuum torch. **+1.25 %.**

### 🔑 THE ANCHOR CASE IS THE REAL TEST, AND IT IS RUNNING NOW

**Prediction, before the data:** at 7.9e18 the linewidth is **23.8 MHz** — 68×
wider than cold, ~119 samples across at the same step. **If the cold gap is
resolution, eigen and driven should agree closely at the anchor.** If a 7 % gap
survives there, it is a genuine method difference and the cold case was not the
explanation.

🔑 **TO GET A REAL Q_ext, RUN THE EIGEN PAIR ON THE DRIVEN MESH.** `pec` and
`lumped` on **the same `h3_driven_n*.msh` files that are already built** — no
new geometry, no re-meshing, and it lands Q_ext at every density including the
anchor. **Until then, quote β from the DIP, which needs no Q_ext at all.**

### 🔴 But the DESIGN torch is a real offset, and NO eigen anchor has ever used it

- **Q₀: 43,523 (vacuum) → 44,387 (sapphire) = +2.0 %.** **`Q_REF`, the η
  reference every driven point is normalised against, is ~2 % low**, and §7c has
  already caught that constant being wrong four times.
- **f₀: −13.87 MHz.** Every eigen f₀ in the record — the ladder, the margins,
  H1's aspect work, H2's groove validation — is **high by about that**.
- 🔑 **And so is everything I measured today.** The anchor run fixed the
  DENSITY; it is still a vacuum-torch cavity. **f₀ = 2.4586 becomes ≈ 2.4447**,
  and the 41.4 MHz band margin becomes ≈ 55 MHz — *better*, but not what is
  written down.
- ✅ **β and VSWR should barely move** — they are ratios, and the torch changes
  Q₀ by 2 %.

🔑 **THE FIX IS ONE LINE AND A RE-RUN, NOT AN INVESTIGATION:** `GEO_DESIGN` must
drop `--no-torch` and carry `--torch-material 11.6,3.5e-05`. ⚠️ **Do not patch it
silently** — it invalidates every stored f₀, so it belongs with the restoration
(apertures, chimney) as one geometry change, measured once.

## ✅✅ THE OPERATING POINT IS MEASURED — 2026-08-25, first time ever

📎 **`baseline-h3-driven-anchor-01.json`** · results `h3-driven-anchor-01.result.json`
*(the config records the question, the bindings, and three caveats — including
that it binds `cavity.Q_ext` at `mesh=no_torch` while meshing `vacuum_torch`.
`slug.py --check` verifies this citation resolves in both directions.)*

**`h3_driven`, 9-point grid. The anchored band 7.3–8.6e18 was never on any grid
before this run.** Centre point **n_e = 7.9e18, ε = −1.456**:

| | **MEASURED** | previously in the record | |
|---|---:|---:|---|
| **f₀** | **2.4586** | 2.4824 (at 1e20) | |
| **Q₀** | **104** | 109 *(interpolated)* | ✅ interpolation was sound |
| **Q_L** | **103** | 155 (at 1e20) | |
| **linewidth** | **23.8 MHz** | 16.0 MHz (at 1e20) | ✅ **1.5× WIDER** |
| **η** | **0.9976** | — | flat 0.9864→0.9976, **does not discriminate** |

### 🔑 THREE CORRECTIONS, ALL FAVOURABLE TO `../control-loop/`

1. 🔑 **IGNITION SLEW IS 4.4× SMALLER.** Cold 2.4515 → lit **2.4586** is
   **+7.1 MHz**, not the **+30.9 MHz** the source spec was built on (which
   assumed 1e20). **The frequency loop has to chase a quarter of what was
   specified.**
2. ✅ **THE LOADED RESONANCE IS WIDER, NOT NARROWER** — 23.8 MHz against the
   assumed 16.0, because Q_L is 103 not 155. **Easier to sit on.**
3. ✅ **BAND MARGIN 41.4 MHz** to the 2.5 GHz edge, versus 17.6 MHz at 1e20.

### ✅ THE FULL BAND — and the ANCHOR'S OWN UNCERTAINTY BARELY MATTERS

**MICAP's 5220–5270 K maps to n_e 7.3–8.6e18. All three solved:**

| n_e | ε_r | f₀ | **slew** | width | Q_L | Q₀ | η |
|---|---:|---:|---:|---:|---:|---:|---:|
| 7.3e18 | −1.270 | 2.4578 | **+6.3** | 23.0 | 107 | 108 | 0.9975 |
| **7.9e18** | **−1.456** | **2.4586** | **+7.1** | **23.8** | **103** | **104** | **0.9976** |
| 8.6e18 | −1.674 | 2.4594 | **+7.9** | 25.0 | 98 | 99 | 0.9977 |

🔑 **THE WHOLE 50 K SPREAD MOVES f₀ BY 1.6 MHz, SLEW BY 1.6 MHz, AND VSWR BY
~9 %.** ✅ **This retires a worry `../spectroscopy/` raised explicitly** — that
n_e moves *"two decades per ~1,500 K"* and *"a 500 K error is 5–10× in n_e"*.
**True in general, and irrelevant here:** MICAP's quoted spread is 50 K, not
500 K, and the design is flat across it. **The anchor does not need to be
tighter than it already is.**
⚠️ Unchanged: this is the LTE lower bound. Non-LTE puts n_e higher, and the
trend above shows that direction costs VSWR (75 → 82 across the band).

### ✅ VSWR IS NOW SETTLED — and it is BETTER than the record says

**The two β estimates differed 13 %. Resolved by deriving Q_ext from the dip
alone, with no imported constant:  Q_ext = Q_L(1+β_dip)/β_dip.**

| n_e | Q_L | β_dip | **Q_ext implied** | vs cold 9,231 |
|---|---:|---:|---:|---:|
| 1e18 | 557 | 0.0704 | 8,478 | −8.2 % |
| 3e18 | 208 | 0.0257 | 8,304 | −10.0 % |
| **7.3e18** | 107 | 0.0133 | **8,150** | **−11.7 %** |
| **7.9e18** | 103 | 0.0127 | **8,221** | **−10.9 %** |
| **8.6e18** | 98 | 0.0122 | **8,162** | **−11.6 %** |
| 1e19 | 92 | 0.0114 | 8,118 | −12.1 % |
| 3e19 | 95 | 0.0112 | 8,625 | −6.6 % |
| 1e20 | 155 | 0.0171 | **9,225** | **−0.1 %** |

⚠️ **I FIRST READ THIS AS "Q_ext FALLS ~11 % UNDER LOAD". THAT WAS WRONG** — the
cold row was missing, because the rig had put the cold point on the **wrong
coupling branch**. Re-fitting cold from the phase gives **Q_ext = 8,462**, so:

| cold | 1e18 | 3e18 | **7.9e18** | 1e19 | 3e19 | 1e20 |
|---:|---:|---:|---:|---:|---:|---:|
| **8,462** | 8,478 | 8,304 | **8,221** | 8,118 | 8,625 | **9,221** |

🔑 **Q_ext IS ROUGHLY FLAT AT ~8,100–8,600 FROM COLD THROUGH 3e19** (a ±3 %
wander with a shallow minimum near 1e19), **and rises to 9,221 only at 1e20.**
**This is not a loading effect.**

🔴 **WHAT IT ACTUALLY EXPOSES IS AN EIGEN↔DRIVEN DISAGREEMENT ON Q_ext.** The
driven sweeps imply **~8,400 cold**; `h3_loopq`'s eigen pair method gave
**9,231** on the same cold cavity — **a ~9 % systematic between two methods**,
not a physical variation. ⚠️ **Unresolved, and it propagates into every β
computed as Q₀/Q_ext.** The measured dip does not depend on it.
**The record used 9,231 at every density**, which makes β too small and VSWR too
large.

> ## ✅ **VSWR AT THE OPERATING POINT IS 75–82, NOT 85–93.**

⚠️ **MY PRE-REGISTERED TEST WAS ILL-CONDITIONED AND COULD NOT HAVE WORKED.**
I proposed β_true = Q₀(eigen)/Q_L − 1. **β here is 1.7 %, while eigen and driven
agree on Q₀ only to 3.4 %** — the uncertainty is twice the quantity. That method
swings β from 0.017 to 0.052 on a 3.4 % wobble. **Differencing two nearly-equal
Q's cannot measure a small β.** ✅ **The dip depth can**, because it reads |S11|
directly: at 1e20, −0.2973 dB → β = 0.0171, and the implied Q_ext = 9,225
recovers the cold value to 0.1 % — **an internal consistency check the
differencing method fails.**
🔴 **Neither prediction A (Q_ext constant) nor B (2.9× collapse) was right.**
The answer is a modest, density-dependent 11 %.

## ⏳ H3 RE-RUN AT THE ANCHOR — LAUNCHED 2026-08-24, cold anchor landed

**9-point grid, `h3_driven` 32 ranks.** ✅ **COLD (n_e = 0) solved in 462 s**
(previous run 441 s — same instrument).

| | driven (this run) | eigen (`h3_step3`) | |
|---|---:|---:|---|
| **f₀** | 2.4515 | 2.451633 | ✅ **133 kHz** (0.38 of the 350 kHz linewidth) |
| **Q_L** | **7,004** | — | ✅ reproduces the record's cold Q_L exactly |
| **Q₀ branch-free** (uses Q_ext = 9,231) | **29,037** | **43,422** | 🔴 **33 % low** |
| **Q₀ overcoupled branch** (rig's own field) | **40,645** | **43,422** | ✅ **6.4 % low** |

🔴🔴 **RETRACTED — THE RIG DID NOT GET THE BRANCH WRONG. I READ THE WRONG
FIELD.** I published *"the rig put the cold point on the wrong coupling branch"*
after reading `wide_fit["beta"]` = 0.2082. **That field is the raw undercoupled
root, and the rig labels it** `"branch": "UNRESOLVED — |S11| alone cannot pick"`.
**The rig does all of this correctly and always did:**

| field | cold value | |
|---|---:|---|
| `beta` | 0.2082 | raw root — **explicitly UNRESOLVED**, what I misread |
| `beta_undercoupled` / `beta_overcoupled` | 0.2082 / **4.803** | **both returned** |
| `Q0_if_undercoupled` / `Q0_if_overcoupled` | 8,462 / **40,645** | **both returned** |
| `beta_resolved` → `branch` | 3.146 → **"OVERCOUPLED"** | ✅ **resolved, correctly** |
| `error_amplification` | **4.15**, `Q0_ill_conditioned: true` | ✅ **flagged** |

🔑 **AND `OPTIMIZER.md` ALREADY RECORDED THE ANSWER**: *"the branch-corrected
cold Q₀ = **40,645**"*, with *"first reported ... on the wrong coupling branch"*.
**My re-fit from raw S11 got 40,652 — 0.02 % away from a number already in the
priors file.** §7an, sixth occurrence.

✅ **WHAT IS ACTUALLY NEW, AND THE RIG HANDS IT TO YOU FREE:** its two Q₀
estimates only agree **if `Q_EXT_MEASURED` is right.**
**Branch-free 29,037 vs overcoupled 40,645 — they differ by 40 %**, and the
Q_ext that reconciles them is **8,462**, not 9,231. **That is a built-in Q_ext
consistency check sitting unread in every result file.**
✅ **The LOADED points are untouched** — every one is β ≪ 1, unambiguously
undercoupled, and the re-fit reproduces all eight of the rig's own values
exactly.

⚠️ **BUT Q₀ = 29,037 IS NOW SITTING IN `h3_driven.result.json` AND IS WRONG BY
A THIRD.** ✅ It does not contaminate η: `Q_REF = 43,523` is a **guarded
constant** (`Q_REF_CONFIG` asserts groove 5×10 + loop 11×8, `h3_step3` eigen,
port terminated), **not** the measured cold Q₀. **Quote the cold case as a
LOCATOR and an f₀; never as a Q.**

⚠️ **AND LAUNCHING OVERWROTE THE PREVIOUS RUN'S `result.json`** — the rig saves
incrementally to the same path.
🔴 **I FIRST WROTE that the prior values "survive in `h3_driven.jsonl`, the
append-only journal". THEY DO NOT.** Reading it shows 22 lines of **solve
metadata only** — `{t, event, tag, seconds, ranks, order, mesh}` — and **zero
lines containing f0, Q0 or eta.** The journal records **that a solve happened,
not what it measured.** ⚠️ I asserted an archive I had not opened, in the
authority document; §7d — a check that cannot fail is not a check.

✅ **PRACTICAL IMPACT: NIL, but by luck rather than design.** The new 9-point
grid re-measures **every** density the old 6-point grid held, so the old values
are superseded rather than lost, and the eigen↔driven cross-check can simply be
redone against the new 1e20 point. The three old values (Q₀ 92.87 / 96.22 /
157.81) were captured before launch and are retained above for comparison.

🔑 **THE REAL RULE:** a rig's `.result.json` is **overwritten in place by the
next run of the same rig**, and **nothing else archives its numbers.** Capture
before relaunching, or accept that the previous run's results are gone.

## 🔴🔴 EVERY LOADED RESULT IS AT THE WRONG DENSITY — 2026-08-24

**User: *"E3 seems like a waste of time at 1e20. In fact, we probably have to
re-run H3 with the right number."*** ✅ **Both correct, and they are DIFFERENT
problems with different costs.**

### E3 at 1e20 is not a slow measurement of the right thing — it is the wrong regime

The plasma annulus is **r = 2.00–8.50 mm, a 6.50 mm shell**:

| n_e | ε_r | σ_p | skin depth δ | **δ / shell** | |
|---|---:|---:|---:|---:|---|
| **1e20** | −30.09 | 27.53 S/m | 1.94 mm | **0.30** | **E3 ran here** |
| 3e19 | −8.33 | 8.26 | 3.54 | 0.54 | |
| 1e19 | −2.11 | 2.75 | 6.13 | 0.94 | |
| **7.9e18** | **−1.46** | **2.18** | **6.89** | **1.06** | **ANCHORED** |

🔴 **At 1e20 the plasma partially SHIELDS** (δ ≈ ⅓ of the shell) — loss is
surface-like. **At the anchored density the field penetrates FULLY** (δ slightly
exceeds the whole shell) — loss is volumetric. **E3 decomposes the loss.
Decomposing it in the shielded regime says nothing about the transparent one.**
**Repairing E3's failed cases at 1e20 would buy a correct answer to a question
about a plasma this machine does not make.**

✅ **WHAT SURVIVES, AND IT IS THE GOOD HALF:** cases **B** and **D** carry NO
plasma, so **Q_wall = 44,387 and Q_diel = 1,911,259 are density-INDEPENDENT.**
🔑 **And so is F2's answer** — the bound η_diel ≤ (1/Q_D)/(1/Q_B + 1/Q_D) = 2.27 %
holds at ANY density, because plasma loss can only ever be ≥ 0. **The two cases
that succeeded are exactly the two that did not depend on the wrong number, and
the three that failed were the three that would have been wrong anyway.**

### H3: the anchored operating point was NEVER SOLVED

`h3_driven.py:159` — `NE_GRID = [0, 1e18, 3e18, 1e19, 3e19, 1e20]`.

| n_e | 1e18 | 3e18 | **← 7.3–8.6e18 →** | 1e19 | 3e19 | 1e20 |
|---|---:|---:|:---:|---:|---:|---:|
| VSWR | 15.6 | 43.3 | **NOT ON THE GRID** | 99.3 | 96.2 | 58.4 |
| margin (MHz) | 48.0 | 46.6 | **NOT ON THE GRID** | 39.2 | 26.0 | 17.6 |

🔴 **The anchor falls in a 3.3× gap across which VSWR changes 2.3×**, on the
steepest limb, immediately below the peak between 1e19 and 3e19. **Every number
I have quoted at the operating point — VSWR 80–89, Q₀ ≈ 109, β ≈ 0.012, ~45 A,
960 W dump, and the 400× coupler spread — is INTERPOLATED there.**
⚠️ **§7ah's neighbour:** not interpolating *across* a turning point, but up the
steep approach *to* one.

✅ **AND THIS ONE IS CHEAP AND UNBLOCKED.** `h3_driven` is a **DRIVEN** sweep —
fixed-ω linear solves, **not** the eigen path, so **it does not touch the
preconditioner defect that killed A, C and E.** Adding the anchor to `NE_GRID`
and re-running is ordinary work.

🔑 **SEQUENCE: fix the DENSITY before fixing the SOLVER.** E3 cannot be
re-targeted to the anchor until the preconditioner is fixed **and** the anchor is
the worst-conditioned point on the ε axis (ε ≈ −1.46, near zero). H3 needs
neither. **Do H3 first; it is the one that changes live numbers.**

### ✅ E3 CASE D LANDED — and F2 is RESOLVED, by a BOUND, without the failed cases

**Q_dielectric = 1,911,259** (f₀ = 2.437789). With **Q_wall = 44,387**:

🔑 **F2 ("fires if η_dielectric exceeds ~5%") can be settled WITHOUT Q_all.**
1/Q_all = 1/Q_wall + 1/Q_plasma + 1/Q_diel, and **the missing plasma term only
makes 1/Q_all BIGGER**, which only makes the dielectric's share SMALLER. So
dropping it gives a rigorous **upper bound**:

> **η_dielectric ≤ (1/Q_D)/(1/Q_B + 1/Q_D) = 2.27 %**

✅ **F2 CANNOT FIRE.** ✅ **PLAN's *"dielectric is only ~2% of the loss budget"*
— untested until now — is CONFIRMED at 2.27 % cold.
✅ Loaded at the anchored density it is **0.0057 %**: utterly negligible.
✅ V3 holds (both channel Qs exceed any plausible Q_all).

🔑 **A falsifier that needed 4 cases was decided by 2**, because the unmeasured
term has a known SIGN. ⚠️ **This does not rescue F1** — the closure itself still
needs Q_all, and η_plasma stays unquotable.
🔑 **Free instrument check:** B and D put f₀ at 2.437762 and 2.437789 — **27 kHz
apart (1.1e-5)** on two independent solves with the same torch and different loss
sets. Loss barely moves f₀, as it should.

### 🔴🔴 E3 IS BLOCKED BY A SOLVER DEFECT, NOT A TIMEOUT — diagnosed 2026-08-24

**Cases A and C both died. They died the SAME way, and it is not slowness.**

| case | plasma? | log | **"PCG did NOT converge"** | of those, **reduction factor 1.000** | GMRES failures |
|---|---|---:|---:|---:|---:|
| **B_wall** | ✗ | 179 KB | **0** | 0 | 0 |
| **C_plasma** | ✓ | 240 KB | **173** | **8** | 0 |
| **A_all** | ✓ | 370 KB | **111** | **6** | 0 |

⚠️ **I FIRST WROTE "perfect correlation with the plasma". CASE E FALSIFIES THAT.**
`E_vac_torch` carries the plasma at the same 1e20 — with a **VACUUM** torch — and
at 93 KB of log it has **0 PCG failures**. The pattern is not plasma:

| case | torch ε | plasma | PCG failures |
|---|---:|---|---:|
| B_wall | **+11.6** | ✗ | **0** (complete, 179 KB) |
| **E_vac_torch** | **+1.0** | **✓** | **0 so far** (93 KB, RUNNING) |
| A_all | **+11.6** | **✓** | **111** |
| C_plasma | **+11.6** | **✓** | **173** |

🔑 **Neither ingredient alone fails. Only BOTH together do** — a permittivity
span from **+11.6 to −30.09 in one mesh.**

🔴🔴 **AND THIS WAS ALREADY IN THE RECORD BEFORE E3 WAS WRITTEN.**
`h3_driven.py` lines 10–11, in its opening docstring:

> *"sapphire — its loaded point does not converge in eigen either (**eps +11.6
> beside the plasma's −30.09**)."*

**That is the contrast mechanism, named exactly, with both numbers.** The same
header records `h3_eigenprobe` hitting **PCG stagnation, 92 non-convergences**.
🔴 **So E3's cases A, C and E were KNOWN-DOOMED at launch** — A and C pair
sapphire with plasma, which the record already said does not converge in eigen.
⚠️ **It was not in KNOWN's PRIOR ART table.** It is now.
✅✅ **E FINISHED AND CONVERGED — 1140 s, f₀ = 2.482470, Q = 163.2, P ≥ 0.9996,
ZERO PCG failures.** The mechanism is **settled**, and it is the CONTRAST:
**plasma alone does not break the eigensolver; sapphire beside plasma does.**

## ✅ AND CASE E IS WORTH MORE THAN E3 WAS — an EIGEN↔DRIVEN CROSS-CHECK

**Two independent solvers, same cavity, same density, neither told about the
other:**

| | f₀ (GHz) | Q₀ |
|---|---:|---:|
| **DRIVEN** — `h3_driven`, sweep + Lorentzian fit | 2.482400 | **157.81** |
| **EIGEN** — `e3_closure` E, NLEPS, port shorted | 2.482470 | **163.20** |
| **agreement** | **70 kHz (2.8e-5)** | **3.42 %** |

*(both: GEO_DESIGN grooved + 11×8 loop, VACUUM torch, n_e = 1e20, Q₀)*

🔑 **THIS RESTORES THE ANCHOR V1 LOST.** `h3_driven` suspended V1 because its
reference — `h3_superpose` vac_hot (f₀ = 2.481566, Q = 163) — was **groove-free
and void**, and the rig wrote its own restore condition: *"run the loaded eigen
case at ne=1e20 on GEO_DESIGN"*. **Case E IS that run.** ✅ Now installed as
`ANCHORS[1e20]` in the prepared `h3_driven.py`.
⚠️ **It anchors the INSTRUMENT, not the machine** — 1e20 is still the wrong
density. Two solvers agreeing says the solvers are right, not that the point is.
🔑 **Note the void anchor had Q = 163 too, and f₀ 0.9 MHz lower.** Consistent:
at Q ≈ 163 the plasma dominates loss completely, so **the groove stops mattering
for Q while still moving f₀** — which is why a groove-free Q looked reusable and
a groove-free f₀ never was.

🔴 **E3'S CLOSURE REMAINS UNANSWERED** — the rig's own verdict: *"CLOSURE CANNOT
BE TESTED — missing ['A_all', 'C_plasma']. Every eta in the record stays
unfalsified."* **F1 is untested, η_plasma unquotable.** ✅ F2 stands (bounded).
🔑 **A vacuum-torch closure IS now reachable** — E proves that family converges —
**but it would characterise a cavity with no sapphire, at 13× the real density.**
**Fix the density first (item 8), then re-test whether sapphire+plasma converges
at the anchor, where the span is +11.6/−1.46 instead of +11.6/−30.09.**

🔴 **A reduction factor of exactly 1.000 means the solver made NO progress at
all — not slow, STALLED.** More wall-clock cannot fix it. A_all's "226 NLEPS
iterations" and C_plasma's "0" are the same disease at different depths.

⚠️ **MECHANISM — NARROWED, NOT SETTLED.** The plasma has **ε_r = −30.089**, so
the operator is **indefinite** and **PCG requires a positive-definite operator.**
That is necessary but demonstrably **not sufficient**: E has the same indefinite
plasma and has not failed. **What A and C add is the ε = +11.6 sapphire
alongside it.** ⚠️ **The outer solver is not the problem**: we set
`KSPType: GMRES` and **GMRES failed 0 times in all three cases.** The failing
PCG is an *inner* solve inside the preconditioner — and the config asks for
`"Type": "Default"` and **has never chosen a preconditioner at all.**

### 🔴 AND THE OPERATING POINT IS THE HARD END, NOT THE EASY ONE

ε_r **crosses zero between 1e18 and 1e19** (ν_m = 1.00e11 /s, recovered from the
rig's own ε at 1e20):

| n_e | 1e20 | 3e19 | 1e19 | **7.9e18 (ANCHORED)** | 1e18 |
|---|---:|---:|---:|---:|---:|
| ε_r | **−30.09** | −8.33 | −2.11 | **−1.46** | +0.69 |

🔴 **E3 ran at 1e20 because it was *"the only convergent point"* — the point
FURTHEST from the operating density.**
⚠️ **WHICH WAY THE ANCHOR CUTS DEPENDS ON THE MECHANISM, AND THEY DISAGREE:**
- **If ε-near-zero conditioning** → the anchor (ε ≈ −1.46) is the **WORST** point
  on the axis and E3 gets **harder** there.
- **If ε CONTRAST** (the live hypothesis) → the span narrows from +11.6/−30.09 to
  **+11.6/−1.46**, and E3 gets **EASIER** at the anchor.

🔑 **These are opposite predictions, and E3-at-the-anchor is the test.** Do not
plan the preconditioner work until E finishes and the mechanism is named.

⚠️ **§7ab again, inverted.** Not "a solvable value became the operating point" —
this time *"the operating point was skipped because it was not solvable"*, and the
substitute is the least representative point available. ✅ The rig recorded this
honestly at the time (*"the anchored 7.9e+18 sits in eigen's untested gap"*), so
the provenance survived; **only the consequence was not drawn.**

⚠️ **The fix is a PRECONDITIONER choice and is NOT yet verified** (§7ac) — no
Palace config schema is installed on the instance, so **do not paste a setting
from memory.** Check Palace's documented `Linear` options first.
🔑 **B and D still stand** — they carry no plasma and are unaffected.

🔑 **THIS IS THE THIRD TIME THE RIGS HAVE MODELLED A CAVITY THE DESIGN IS NOT** —
the groove (31 rigs, `GEO` never passed `--groove`), the port boundary (every
looped eigen, gap left OPEN), and now the torch. **Three different features,
three different mechanisms, one shape.** CONVENTIONS §7ai.

## ✅✅ n_e IS ANCHORED — 7.3–8.6 × 10¹⁸, from a MEASURED gas temperature
**2026-08-24. The programme's assumed 1e20 was 13× too high.**

**Anchor:** Kuonen, Hattendorf & Günther, *J. Anal. At. Spectrom.* **39**(5)
1388–1397 (2024), Table 2 — **pressure-reduction method, N₂ MICAP: 5220 K and
5270 K** (two sample-introduction conditions). `refs/Quantification
capabilities of N2 MICAP-MS...pdf`. Comparator chosen by the user: *"the
temperature range should be the same as MICAP."*

🔑 **WHY THAT METHOD AND NOT THE OTHER TWO.** Table 2 reports three:

| method | N₂ MICAP | Ar ICP |
|---|---|---|
| **pressure reduction** ← *the only EMPIRICAL one* | **5220 / 5270 K** | 5780 / 5680 K |
| Longerich | 12,850 / 13,800 K | 13,170 / 12,600 K |
| Houk & Praphairaksit | 5,910–6,430 K | 6,060–6,710 K |

Pressure reduction **measures an interface-pressure ratio** with the plasma on
and off. **The other two infer T from the SAME MO⁺/M⁺ ion-ratio data through
different equilibrium models and disagree by ~2×** — that is MODEL spread, not
measurement spread. The paper notes Longerich *"has always resulted in values
between 9000 K and 13000 K"* regardless of plasma.
✅ **Cross-check:** the same method reads 5,680–5,780 K on their Ar ICP against
independent literature values of 5,000–5,280 K.

✅ **NU_M IS NOW DERIVED FROM THE SAME TEMPERATURE**, not set by hand —
`physics.plasma_state(T_gas)` returns (n_e, ν_m, n_heavy) from one input,
closing §7ad. At 5245 K it gives ν_m ≈ 6.3e10 against the hand-set 1.0e11 —
within 60%, so the old value was not wildly wrong, but it was never *derived*.

### 🔴 THE CONSEQUENCE SPLITS IN OPPOSITE DIRECTIONS

| | at 1e20 (assumed) | **anchored (7.3–8.6e18)** |
|---|---:|---:|
| **band margin** | 17.6 MHz | **40–41 MHz** ✅ |
| **VSWR** | 58.4 | **80–89** 🔴 |
| load-side current @1 kW | 34.2 A | **40–42 A** |
| η | 0.9964 | ~0.993 |

🔑 **THE BAND-MARGIN PROBLEM DISSOLVES; THE MATCH GETS WORSE.** Q₀ MINIMISES near
n_e = 1e19 and RECOVERS at 1e20, so **the assumed value sat on the FAR side of
the worst case and the real density sits just BELOW it.** Moving to the truth
moved toward the peak. `../control-loop/` has revised its requirement UPWARD.
⚠️ **1e19 (VSWR 99.3) is inside the plausible band — design to ~100:1.**

⚠️ **CAVEATS THAT TRAVEL WITH IT.** The number is the plasma **as sampled through
the MS interface** — the analytical zone at the sampling cone, not the
r = 2–8.5 mm annulus the EM model uses. Different region, and atmospheric plasmas
have gradients. **LTE is assumed; non-LTE puts n_e ABOVE Saha**, which pushes
VSWR further toward the peak, so the caveat is not symmetric.
✅ **Power is NOT a caveat** — an atmospheric plasma at 1450 W is BIGGER, not
hotter, so the paper's power vs this programme's 1 kW does not matter.
✅ **MS-vs-OES is not one either** — same plasma, different detector.

## 🔴 SUPERSEDED — ne = 1e20 AND ITS SOLVER-CONVENIENCE PROVENANCE
**User, 2026-08-24: *"an estimate from an earlier session. As far as I know, it
has no provenance."* Checked, and it is worse than that: the provenance is
SOLVER CONVERGENCE.**

`h3_eigen` measured where the eigen solver converges against the dimensionless
PI_1 = ω_p/√(ω²+ν²): **0.02–0.56 converges · 1.76 FAILS · 5.58–17.6 converges.**
Then `h3_annular` set `NE = 1.0e20  # PI_1 = 5.58, the row h3_eigen proved
solvable`, `h3_superpose` cited h3_annular, three more rigs copied it with no
comment at all, and `h3_margin` (today, mine) labelled it **"the operating
point"**. **Six steps, no step introducing the claim, the claim accumulating.**
CONVENTIONS §7ab.

🔴 **WHAT THIS VOIDS — AND WHAT IT DOES NOT.**
- ✅ **margin(n_e) is MEASURED and stands.** So does η(n_e), and the whole Phase
  A/B geometry result. They are sweeps; they do not depend on which point is
  "operating".
- 🔴 **"The band margin is 9.6 MHz" is VOID TWICE OVER.** It is the margin at a
  density chosen because a solver converged there, AND it used the 3 dB edge
  instead of f₀. On the tuner's own criterion it is **17.6 MHz** — still at an
  unanchored density.
- 🔴 **"At the operating point" must be struck from every η, β and power claim.**
  There is no established operating point.
- 🔴 **The design question — is the margin adequate? — is UNANSWERABLE until
  n_e is anchored.** It is not a hard question awaiting more solves; it is
  ill-posed as stated.

| n_e | margin (f₀→2.500) | η | VSWR | note |
|---|---:|---:|---:|---|
| 1e18 | **48.0 MHz** | 0.9864 | **15.6** | best margin AND best match |
| 3e18 | 46.6 | 0.9951 | 43.3 | |
| **1e19** | **39.2** | **0.9979** | **99.3** | 🔴 **eigen CANNOT solve here** (PI₁=1.76); worst VSWR |
| 3e19 | 26.0 | 0.9978 | 96.2 | |
| 1e20 | 17.6 | 0.9964 | 58.4 | the solver-convenient value |

🔴 **THE SOLVER'S BLIND SPOT IS AT THE INTERESTING DENSITY.** PI_1 = 1.76 maps to
**n_e ≈ 1e19** — the density with a comfortable margin AND the best η. **The one
place eigen cannot look is where the design would prefer to be.** Driven works
there, which is the only reason it was measured.

✅ **TWO REASSURANCES, BOTH MEASURED, NOT ARGUED:**
1. **The pull SATURATES.** Cold → 1e20 is +30.9 MHz total, but the last 3.3× in
   density contributes only **+8.4 MHz**. There is no cliff above 1e20.
2. **The linewidth NARROWS at the top** (26.0 → 16.0 MHz) as the plasma turns
   reflective, giving margin back. Both effects oppose a runaway.

🔑 **HOW TO ANCHOR IT, in increasing order of effort:**
- **Ask what the application needs.** n_e is set by the emission requirement,
  not by the cavity. This is a question for the spectroscopy side, and it may
  already have an answer.
- **Literature for atmospheric-pressure MIPs at 2.45 GHz** in this power class.
  An external anchor, which is what the programme's rules require.
- **A power balance** (PLAN E3's energy closure): the absorbed power sustains a
  particular n_e. Self-consistent, and needs electron energy-loss data the
  programme does not currently have.
⚠️ **Until then, report results AS A FUNCTION of n_e and never at a point.**

## ✅ H3 PHASE B — the band margin CANNOT be fixed by geometry (`h3_margin`)
**Driven, ne = 1e20, the joint (groove depth × loop area) space. 12 cells.**
**Anchor: `h3_driven`'s design cell — reproduced to 0.00 MHz.**

**Margin = f₀ → 2.500 GHz** (recomputed on the tuner's actual criterion):

| groove | 10 mm² | 35 mm² | 82 mm² | 176 mm² |
|---|---:|---:|---:|---:|
| 5 × 7 | — | 18.2 | 18.0 | 17.4 |
| 5 × 10 | — | 18.2 | 18.0 | **17.6** ← design |
| 5 × 14 | — | 18.2 | 18.0 | 17.4 |

🔴 **THE WHOLE GRID SPANS 0.8 MHz.** Best cell beats the design point by
**+0.6 MHz** across a **5× loop-area** and **2× groove-depth** search.
**Groove and loop geometry cannot fix the band margin.**
⚠️ Originally tabulated on the 3 dB edge (9.3–10.0, spread 0.7). **The absolute
headroom doubled; the CONCLUSION is unchanged** — geometry has ~1 MHz of
authority either way.

🔑 **WHY, AND IT IS THE USEFUL PART: THE LOADED f₀ IS A PLASMA PROPERTY.**

| what moves f₀ | amount |
|---|---:|
| groove depth 7 → 14 mm, at fixed loop | **0.000 MHz** (identical to 6 figures) |
| loop area 35 → 176 mm² | 0.8 MHz (suppressed from 0.8 MHz cold) |
| **the plasma** | **+30.9 MHz** |

✅ **THIS ANSWERS THE QUESTION H2 WAS MOVED UP TO ENABLE.** H2 called 5 × 10 a
*baseline*, to be refined under load. **It needs no refinement: depth has no
purchase on the loaded frequency at all.** The groove pushes competitors and
leaves TE011 alone — cold AND loaded. That is the filter working as designed,
confirmed from a direction H2 never tested.
🔑 **Groove depth SATURATES by 10 mm**, and at 176 mm² it **PEAKS** there
(17.4 → 17.6 → 17.4 on f₀). **5 × 10 is at the optimum**, independently
re-derived.

🔴 **THE REAL LEVER IS DENSITY, BY A FACTOR OF ~25 — AND DENSITY IS UNANCHORED
(see above), so this is the lever AND the open question:**

| lever | range | margin swing |
|---|---|---:|
| groove depth | 1.4× | 0.3 MHz |
| loop area | 5× | 0.6 MHz |
| **ne, 1e20 → 1e19** | 10× | **+16.2 MHz** |

**And it is not a trade: η goes 0.9964 → 0.9979 — it IMPROVES**, because that is
where the Q₀ turning point sits. Both objectives move the same way.
⚠️ **SCOPE BOUNDARY, AND IT IS NOT THIS PROGRAMME'S TO CROSS.** η and band margin
are ELECTROMAGNETIC. n_e also drives atomisation and excitation, so "run at
1e19" is a claim about the CAVITY that the spectroscopy may refuse. **The EM
cost is zero; the analytical cost is unknown and belongs to the emission side.**
🔴 **AND 1e20 IS NOT AN OPERATING POINT AT ALL — its provenance is solver
convergence (§7ab, section above).** So "the margin is thin" was never a finding
about the machine. **It is a finding about a density nobody chose.**

⚠️ **THE 10 mm² LOOP HAS NO MEASURABLE RESONANCE UNDER LOAD**, at any depth —
β ≈ 0.004 gives a ~0.06 dB dip. I sized that cell from a **cold** β = 1
extrapolation, but Q₀ collapses 275× under load (43,423 → 158) while Q_ext is
geometry, so β collapses with it. **A loop critically coupled cold is hopelessly
undercoupled loaded.** One regime's number quoted in another — the §7c shape.
🔴 **AND THE CONSEQUENCE IS STRUCTURAL: Q_ext MINIMISES at 9,231 (Phase A), so
loaded β CANNOT EXCEED 0.017 with a cap loop of this family.** Loaded critical
coupling is not merely unachieved, it is **unreachable by loop geometry**.
✅ **RESOLVED 2026-08-24: the hardware requires a MATCHING NETWORK** (user), so
the raw β is a tuner specification, not an efficiency. **The 6.6% figure is
withdrawn** — see the matching-network section above.

✅ **A METHOD RESULT WORTH KEEPING: cold Q_ext PREDICTS loaded dip depth.**
Predicted −0.14 / −0.25 / −0.30 dB from Phase A's cold Q_ext with a loaded Q₀;
measured **−0.16 / −0.25 / −0.30**. So Q_ext transfers cold → loaded to ~20%.
⚠️ Good enough to predict coupling; **not** good enough to derive Q₀ from.

## 🧾 THE LOOPED-EIGEN AUDIT — completed 2026-08-24
**Every eigen result on a cavity WITH a loop was measured with the feed gap
open (§7v). This is the disposition of each.**

| rig | what it claimed | verdict |
|---|---|---|
| `e0k2_sizeq` | eigen Q per loop size; killed a "backwards" driven trend | 🔴 **VOID.** Its `q_te011` at 176 mm² reads **30,020**; properly measured the same loop gives **43,523**. The mode it identified was half a hybridised pair |
| `e0k2_azim` | azimuthal discriminator validated on real solves | 🔴 **VOID on looped solves.** The discriminator itself is fine (and superseded by purity) |
| `e0k2_betacause` | is the β spread symmetry or convergence? | 🔴 **VOID.** Open gap AND an unresolved branch |
| `e0k2_portfix` | β agreement between meshes after the port fix | 🔴 **VOID** for the same two reasons. ⚠️ The **port-meshing** fix it made (2 → 42 elements) is real and independent |
| `h3_cold` | design-cavity cold modes, Q₀ = 12,368 | 🔴 **VOID** — the pair 2.440003 / 2.494440 |
| `h3_loopsize` | β vs loop area | 🔴 **VOID twice over** — groove-free AND branch-unresolved |
| OPTIMIZER **hybridised Q** prior | 1/Q mixes with m=1 admixture | 🔴 **DO NOT USE.** It fits the open-gap hybridisation |
| **176 mm² mode-identity threshold** | | 🔴 **VOID.** Derived from `e0k2_sizeq` |
| `h3_ladder` steps 1–2 | bare and grooved anchors | ✅ **STAND** — loop-free, no port |
| `h2_groove`, `h2b`, E0 family, `h1_aspect` | | ✅ **STAND** — loop-free |
| `e0k2_anchor` **methods** | `branch_from_phase`, `analyse_driven` | ✅ **METHODS STAND**; its looped eigen numbers do not |
| driven f₀, Q_L, linewidths (all rigs) | | ✅ **STAND** — never depended on the port BC or the branch |

🔑 **THE DIVIDING LINE IS SHARP AND WORTH KEEPING**: a claim survives if it rests
on **a loop-free eigen solve**, or on **driven f₀/Q_L/linewidth**. It dies if it
rests on a looped eigen **mode identity, Q, or purity**, or on a **β from |S11|
depth**.

⚠️ **ONE THING THE AUDIT DID *NOT* SETTLE.** `e0k2_sizeq` existed to explain a
DRIVEN anomaly — Q₀ = 20,005 / 24,920 / 28,387 / 30,112 for 35 / 82 / 176 /
384 mm², smaller loops apparently costing more Q. **Driven has a real port, so
the open gap does not explain it.** The branch error might, and so might a
blended fit — **both untested.** It is now a declared question for the loop-size
sweep, which measures Q_ext and Q₀ per loop size properly. **Do not record the
anomaly as explained.**

### ✅ Code fixed in the same pass, so the audit cannot un-happen

| fix | where |
|---|---|
| **GATE 4** — no surface reaches the solver by default | `eigen_cfg` |
| explicit `port_bc` on all 9 looped rigs, intent commented | `e0k2_*`, `h3_cold`, `h3_ladder`, `h3_loaded`, `e0k_driven_vs_eigen` |
| **branch-free Q₀** = 1/(1/Q_L − 1/Q_ext), + ill-conditioning guard | `h3_driven.fit_dip` |
| `Q_ext` 50,709 → **9,117** (measured, was an open-gap number) | `h3_driven` |
| η reference → **44,414** (grooved, NO loop — this rig has none) | `h3_annular` |
| η reference → **43,523** (grooved + loop) | `h3_groove`, `h3_loopsize` |
| result files stamped `INVALID_open_loop_gap`, data left intact | 5 `.result.json` |
| rig no longer rewrites a result file **on import** | `h4_reanalyse` |

## 🔎 PRIOR ART — which rig already solved this

**Search here BEFORE deriving your own settings or method.** On 2026-08-23 I
derived my own four times and was wrong four times, in ways the existing solution
had already handled. That is a SEARCH failure, not a reasoning failure, and this
table is the fix.

| problem | solved by | what it uses |
|---|---|---|
| **eigen on a GROOVED cavity** | `h2_groove` | **target = 1.05**, `n = count(closed-form modes ≤ 2.57) + 5` = 12, σ = 3.5e7, sf 1.5. 🔴 A target just below the cluster (2.25, 2.30) does NOT converge — three attempts |
| **coupling BRANCH from |S11|** | `e0k2_anchor.branch_from_phase` | phase swing through resonance; ~360° overcoupled vs returns-to-start undercoupled. Reports **AMBIGUOUS** within a few degrees of 180° |
| **driven Q₀ extraction** | `e0k2_anchor.analyse_driven` | 3 dB width of ABSORBED power + dip depth → Q_L, β, Q₀ |
| **why a grooved solve needs the groove** | `e0k2_anchor` docstring | TE011/TM111 are EXACTLY degenerate ungrooved, so a driven dip is TWO overlapping resonances and a single-Lorentzian fit returns NEITHER Q |
| **the η reference trap** | CONVENTIONS §7c | 44,384 no-loop/no-groove · 29,854 loop-no-groove **(a HYBRID's Q — §7v)** · ❌ ~~12,368~~ **retracted, open-gap artifact** · ✅ **43,523 the DESIGN cavity, port terminated** (`h3_step3`/`h3_loopq`). **None of the first three transfers.** |
| ✅ **terminating the loop in eigen** | `eigen_cfg(port_bc=...)` | **`lumped`** = 50 Ω LumpedPort, excitation off — the MACHINE, Q is LOADED. `pec` = shorted on purpose. `absorbing` = radiation BC, NOT the feed. **No default; a looped mesh without it is refused (GATE 4).** |
| 🔴 **eigen on a LOOPED cavity** | `h3_step3` | **Palace leaves the loop's port face (attr 91) at PEC — the loop is SHORTED.** It then resonates and splits TE011. Terminate attr 91, or accept you are solving a different cavity. **Never compare a looped eigen result to a driven one without this.** |
| **identifying a mode when labels fail** | `h3_ladder` | **continuation** — perturb ONE element from a state whose label is exact, and pick the candidate needing the smallest shift. Beat both purity and m-binning on the design cavity |
| **energy-balance falsifier** | `PLAN.md` E3 | η_total = η_plasma + η_wall + η_dielectric must close within a few % or **only η_total may be quoted** |
| 🔴 **eigen with SAPPHIRE + PLASMA does NOT converge** | **`h3_driven` docstring (lines 10–11)** — *"sapphire: its loaded point does not converge in eigen either (eps +11.6 beside the plasma's −30.09)"*; and `h3_eigenprobe` found **PCG stagnation, 92 non-convergences**, at ne=1e19 | 🔑 **THE CONTRAST, named explicitly, BEFORE E3 was written.** Neither ingredient alone fails. **Use DRIVEN** — its cost scales with Q, so it is cheapest exactly where eigen fails |
| **groove depth law** | `h2b_groovescale` | not a power law — local exponent 1.22 (gd 5→10) → 0.78 (10→20). 🔴 λ/4 = 30.59 mm is the depth to AVOID |
| **mode window / target trap** | `h2b_groovescale` docstring | Palace returns N modes ABOVE target; the groove pushes TM111 DOWN, so a target inside the band loses it through the floor |

## 🔑 THE FILTER — apply this before believing any number here

**Anything measured WITHOUT the groove, AFTER H1, is discarded.** H1 fixed the
cavity; from that point on, a groove-free mesh is a different cavity and its
mode landscape is not the design's.

**The one exception: instrument rigs comparing against CLOSED FORM.** A plain
cylinder is the point there — that is E0's job, and `GEO` exists for it.

Audited 2026-08-23 by mesh sidecar (`geometry_mm.groove`):

| family | verdict |
|---|---|
| `e0*` instrument rigs | bare is **CORRECT** — closed-form comparison |
| `h1` | the boundary itself; the groove did not exist yet |
| `h2`, `h2b` | ✅ grooved (the bare ones are deliberate gd=0 controls) |
| **`h4` — all 11 meshes** | 🔴 **DISCARDED.** `h4_field` (dielectric shifts, the Slater result) and `h4_seed`, all groove-free |
| **`h3` — 66 of 72** | 🔴 **DISCARDED.** The 6 grooved are 2026-08-23's `h3_groove` and `h3_cold` |
| `e0k2` — all 10 | ✅ **instrument rig — bare is CORRECT.** Its purpose was to characterise a BARE cavity against eigen AND driven, so the plain cylinder is the subject. Its extraction validation stands. ⚠️ Its **Q = 44,384 is a bare-cavity number** and must NOT be used as the design cavity's η reference — that is a different measurement, not a defect in e0k2 |
| `probecheck`, `portcheck`, `plasmacheck` | bare infrastructure checks; their numbers are bare-cavity |

## 🔴 NOT ESTABLISHED — do not quote

- **All of H4's field work (`h4_field`, `h4_seed`).** Groove-free. This
  discards the Slater validation (predicted −15.3 MHz, measured −15.00), the
  torch dielectric shifts, the bore field map and the E/N ignition numbers.
  🔑 **Consequence: "no mode cold-ignites" is NOT currently anchored.** It is
  probably right and it must be re-measured with the groove.
- **All non-groove H3/H6 work (2026-08-23).** η(ne), the +31.6 MHz loaded pull,
  loaded Q₀, the 78% suppression law, sapphire's loaded point, β vs loop area.
  ⚠️ **`OPTIMIZER.md` carried the 78% law as VALIDATED until 2026-08-24** — two
  live documents disagreeing about the same result. Now marked DISPUTED there,
  with the data kept and a one-pair grooved test named. **When two documents
  disagree, neither is authority until the disagreement is written down.**
  Measured on a cavity with **no mode filter**; the design has one. The cavity
  was wrong, so the mode landscape was wrong, and every one of those results is
  *about* the mode landscape.
- **"Net into plasma" figures.** A product of a β whose coupling branch is
  unresolved (|S11| cannot distinguish β from 1/β), an η referenced to the
  **no-loop** 44,384 instead of the design cavity's **43,523**, one-sided linewidths, and
  in places a mode whose identity the rig itself flagged. **Stop quoting these.**
- **β and Q_ext.** β is not mesh-converged (43% for a 1.25× refinement); Q_ext
  is not transferable between meshes.
- ~~**The 2.44 GHz TM-like mode.**~~ 🔴 **RESOLVED TWICE, and the FIRST answer
  was wrong.** I said 2.440003 was TE011 "by continuation". It is not: with the
  loop's port TERMINATED the design cavity's TE011 is **2.451490**, and
  2.440003 / 2.494440 are the two halves of a pair produced by an **OPEN feed
  gap** (§7v). **Neither is a mode this machine has.**

## 🔑 KEPT FROM 2026-08-23 — and only the part that is not cavity-dependent

⚠️ **Even the instrument gains need splitting.** A method claim and a cavity
claim often sit in one sentence. INSTRUMENT now marks which is which; five of
its sections carry a GROOVE-FREE re-check banner.

**Survives** (arithmetic or circuit theory, independent of which modes exist):
driven sweep cost ∝ Q; η robust where Q₀ is not; |S11| cannot distinguish β from
1/β; band-vs-step sizing; continuation needs a seed measured in-regime; a guard
on fit QUALITY cannot detect a fit of the WRONG THING.

**Does NOT survive without re-checking** (claims about mode behaviour in a cavity
whose modes the filter changes): the ~176 mm² mode-identity threshold — its
source rig `e0k2_sizeq` was groove-free and TE011/TM111 are EXACTLY degenerate
ungrooved, so it may be an artifact of a degeneracy the design removes; the
ε-contrast convergence envelope; the 2.6232 GHz competitor; the 12→0 eigen/driven
timeout comparison; every β, Q_ext and delivered-power figure; `h4_field`'s
dielectric shifts.

## 🔑 The old note, kept for the numbers

Driven replaces eigen for loaded work: **12 eigen timeouts / 3 h wasted → 0
across 17 driven cases.** Cost ∝ Q, so driven is cheapest exactly where eigen
fails. Full method in INSTRUMENT's "loaded-cavity toolkit".
⚠️ This is an inward gain. It answered no question about the machine.

---

**Next steps live in `NEXT.md`.** This file says what is known; that one says
what to do. Keeping them apart is the point — one document with both jobs is how
`FINDINGS.md` became unreadable.
