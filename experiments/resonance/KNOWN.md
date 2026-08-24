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
| ➡️ **`../control-loop/`** | 🔑 **the SOURCE side is its own programme now** (opened 2026-08-24): LDMOS, matching, and the control loop. `README.md` states what we have and what is needed; `SOURCE.md` holds the characterisation. ⏸️ **PARKED** — re-entry when n_e is anchored or a coupler class beats Q_ext 9,231 | **moved out 2026-08-24** |
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
  groove · ⚠️ **12,368 the DESIGN cavity — DISPUTED**, see the ladder section.
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

## 🔴🔴 ne = 1e20 IS NOT "THE OPERATING POINT" — IT HAS NO PHYSICAL PROVENANCE
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
| **the η reference trap** | CONVENTIONS §7c | 44,384 no-loop/no-groove · 29,854 loop-no-groove · ✅ **12,368 the DESIGN cavity** (`h3_ladder`, 2026-08-24). **None transfers.** Solve it per configuration, **per loop size** |
| ✅ **terminating the loop in eigen** | `eigen_cfg(port_bc=...)` | **`lumped`** = 50 Ω LumpedPort, excitation off — the MACHINE, Q is LOADED. `pec` = shorted on purpose. `absorbing` = radiation BC, NOT the feed. **No default; a looped mesh without it is refused (GATE 4).** |
| 🔴 **eigen on a LOOPED cavity** | `h3_step3` | **Palace leaves the loop's port face (attr 91) at PEC — the loop is SHORTED.** It then resonates and splits TE011. Terminate attr 91, or accept you are solving a different cavity. **Never compare a looped eigen result to a driven one without this.** |
| **identifying a mode when labels fail** | `h3_ladder` | **continuation** — perturb ONE element from a state whose label is exact, and pick the candidate needing the smallest shift. Beat both purity and m-binning on the design cavity |
| **energy-balance falsifier** | `PLAN.md` E3 | η_total = η_plasma + η_wall + η_dielectric must close within a few % or **only η_total may be quoted** |
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
  **no-loop** 44,384 instead of the design cavity's 12,368, one-sided linewidths, and
  in places a mode whose identity the rig itself flagged. **Stop quoting these.**
- **β and Q_ext.** β is not mesh-converged (43% for a 1.25× refinement); Q_ext
  is not transferable between meshes.
- ~~**The 2.44 GHz TM-like mode.**~~ ✅ **RESOLVED 2026-08-24.** The design
  cavity's 2.440003 GHz mode is **TE011**, not a TM interloper — see the
  continuation ladder above. The `m=1` label came from azimuthal binning.

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
