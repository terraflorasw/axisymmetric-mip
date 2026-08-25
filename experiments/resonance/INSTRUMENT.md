# The instrument

What gmsh + Palace can and cannot tell us about this cavity, measured against
closed-form physics rather than against itself.

**Read this, not the E0 rigs.** Every number below cites the experiment that
produced it; follow the citation only if you doubt the number.

Status: **characterised** on both frequency and loss, 2026-08-21.

---

## The recipe

| | | why |
|---|---|---|
| geometric order | **2** | order 1 faceting reads high by 0.5–3.6 MHz (E0f2) |
| solver order | **2** | order 1 is 12–17 MHz wrong, **mode-dependent by 40×** (E0g) |
| mesh | sf 0.96, ~83k tets | resolution matters at ~1.5 MHz (E0) |
| ranks | **32, one solve at a time** | 27.7×, 87% efficient; fan-out buys 4% (E0l) |
| wall | 3.5e7 S/m, declared in `baselines.json` | undeclared now REFUSES to solve |

Both orders are **2** and they are different discretisations. gmsh's order is how
well elements follow the true cylinder; Palace's is how well the basis represents
the field. Conflating them cost this programme a full invalidation.

## Error budget

Ordered by size. Everything here is TE011 at 2.45 GHz unless stated.

| channel | magnitude | source |
|---|---:|---|
| choosing too coarse a mesh | ~1.5 MHz | E0 |
| **absolute vs closed form, worst mode** | **0.361 MHz** | E0f2 |
| **absolute vs closed form, TE011** | **0.058 MHz** | E0f2 |
| exact degeneracy TE011/TM111 (true value 0) | 0.070 MHz | resplit |
| mesh-to-mesh, same geometry re-meshed | ≤0.021 MHz | E0b/c/d |
| mesher jitter, identical command | 0.008 MHz | E0kp |
| solver on an identical mesh | **0** (bit-exact) | E0e |
| rank count | **0** across 1–32 | E0l |

**Differential work is ~20 kHz. Absolute prediction is 60–360 kHz.** A sweep that
compares neighbouring geometries gets the tight number; a claim about an absolute
frequency gets the loose one.

## Losses

- **Q ∝ σ^0.5 exactly**, verified to 4 decimals across a decade of conductivity
  on all 14 modes (E0q). No absolute Q formula is used or needed — `physics.py`
  still refuses `wall_Q`, and that refusal stands.
- **TE011 Q = 36,548** at aluminium 3.5e7. **TM111 = 18,032** — half.
- Loaded linewidth at critical coupling: **~134 kHz**.
- Frequency moves only **38–48 kHz** across a full decade of σ, so wall material
  is a Q and surface-finish decision, not a tuning one.

## What a solve COSTS — and it is predictable

Added 2026-08-21, from 68 harvested Palace logs. `solvecost.py` is the tool.

**t ≈ 454 ns × ND_dofs × total_KSP_iterations**, at **32 ranks, solver order 2**,
good to **±15%** across a 4× range of runtimes and to **4%** out-of-sample on a
case it was not fitted to. `ND ≈ 6.44 × tets` at order 2, so problem size is known
from the mesh before anything is solved.

Cost is one line of the timing tree:

| | share of total |
|---|---:|
| **Preconditioner** | **75% median**, 68–84% across all 68 |
| Eigenvalue Solve | 0.1–19% |
| Linear Solve proper | 1.6–5.5% |

One multigrid setup per run, so this is per-APPLICATION cost — it rides on the
iteration count, not on setup.

🔴 **"Cost varies independently of tets" was 95% bookkeeping.** The same 83,322
tets spanned 227 s to 21,462 s. The expensive population ran **4 ranks on the
laptop**, the cheap one **32 ranks on the instance** — stated on each log's first
line. Normalised per rank-set the scatter collapses from **95× to 1.3×**. Wall
times were never comparable across the two, and `predict_seconds` REFUSES off
32 ranks / order 2 rather than extrapolating.

**The only unpredictable term is the KSP iteration count**, which is the
conditioning. That is what a preflight estimate cannot know and what a guard must
watch.

⚠️ **NLEPS divergence is a separate failure and looks nothing like slowness.**
The nonlinear eigen-iteration can go BACKWARDS — `nconv` stops rising while the
residual increases and the Armijo line search collapses (α ≈ 2e-3). A long
linear solve at the end is the SYMPTOM, not the disease. `solvecost.diagnose()`
detects it; its self-test carries the real diverging run as known-bad input.
Letting such a case run longer will not finish it.

## 🔑 IDENTIFY TE011 BY FIELD STRUCTURE, NOT BY AZIMUTHAL ORDER

**User, 2026-08-23: "no matter how many sectors we add, something will modulus
into the wrong thing."** Correct, and it is unbounded: N sectors resolve
m ≤ N/4, and there is always an m above that folds back. **Chasing resolution
cannot close this.**

✅ **Ask the BINARY question instead — "is this TE011?" — and answer it from the
FIELD COMPONENTS, which do not alias.**

TE011 is TE_0np: **E_z = 0 (it is TE) and E_r = 0 (it is m=0). Its E is purely
azimuthal.** Palace's probes emit the full complex vector (`Re/Im{E_x,E_y,E_z}`),
so at a probe on the x-axis E_φ = E_y and E_r = E_x, and

    purity  P = |E_phi|^2 / (|E_r|^2 + |E_phi|^2 + |E_z|^2)

**Validated on `h4_field_no_torch`'s saved probes (no re-solving):**

| mode | \|E_r\| | \|E_φ\| | \|E_z\| | **P** |
|---|---:|---:|---:|---:|
| TM111 | 70.6 | 184.5 | 0.007 | 0.872 |
| TM111 (other pol.) | 185.8 | 70.4 | 0.057 | 0.126 |
| **TE011** | **0.85** | **184** | 0.032 | **0.9999** |
| TE311 | 0.36 | 3.49 | 0.054 | 0.989 |

🔑 **AND THE PART THAT DEFEATS ALIASING: TE011 has no φ-dependence, so P = 1 at
EVERY azimuthal position.** Any m ≠ 0 mode's P VARIES with φ — the two TM111
entries above are the same degenerate pair sampled at one φ, reading 0.872 and
0.126 precisely because they are orthogonal polarisations. **So probe several φ
and require P ≈ 1 at ALL of them.** That is a pointwise field-structure test: no
harmonic decomposition, no modulus, nothing to alias.

✅ **It is naturally a REJECTION test**, which is what is actually needed: it bins
into *not TE011* without having to name what the mode is instead.
⚠️ Single-φ purity is NOT sufficient on its own — an m≠0 polarisation can read
high at one angle (TE311 gives 0.989 here). **Multi-φ is the test; single-φ is a
screen.**
⚠️ Probes here sit at z = 0 (mid-plane) where E_z is small for everything, so
**E_z did not discriminate in this data** — the work was done by E_r vs E_φ.

## 🔴 THE IDENTIFICATION CHAIN HAS TWO COUPLED BLIND SPOTS (2026-08-23)

**`physics.spectrum` enumerates m ≤ 2, n ≤ 2, p ≤ 2.** Modes outside that are
absent from the reference table. **TE311 at 2.622012 GHz is one of them**, and it
sits 172 MHz above the design point where it competed with every driven sweep.

**`azimuthal.order()` uses `SECTORS = 5` and resolves only m ≤ 1.**
🔑 The limit is **m ≤ N/4**, not N/2: energy goes as cos²(mφ), which carries
angular harmonic **2m**, so Nyquist needs 2m ≤ N/2. At N=5 that is m ≤ 1.25.
⚠️ `SECTORS`' own comment claims *"m in {0,1,2}"* — **m=2 was never reliably
distinguishable either.** m=0 vs m=1 IS safe, which is what the bare-cavity
anchor (TE011 vs TM111) depends on. Its own
comment — *"m in {0,1,2} in this window"* — took that range FROM the incomplete
spectrum above. **The two blind spots are the same blind spot**, so a mode the
table cannot list is also a mode the classifier cannot label, and it is reported
as **m=0**: TE311 came back with A2/A0 = 0.0004.

✅ **FIXED 2026-08-23**: `order()` still returns 0 for a flat pattern — that is
the right answer as far as it can see — but now carries `_m_resolvable_max` and
`_aliasing_risk=True` in the harmonics dict, so a caller can tell "flat" from
"axisymmetric".
🔑 **The enumeration cutoff in `physics.spectrum` is defensible; the BINNING was
the defect.** A truncated table is a limit you work around by knowing it.
Returning **0** — which is not "unknown" but the specific answer meaning TE011 —
for a mode the method cannot resolve is a fault that manufactures confident
wrong identifications.

🔴 **Therefore "clean m=0" does NOT establish TE011.** It establishes "not m=1 or
m=2, as far as five sectors can tell". Identification needs a SECOND
discriminator that fails differently:
- **Q ratio** — TE011's Q is 2.17× TM111's, measured, and resolution-robust
- **frequency against a COMPLETE table** — extend the enumeration first
- **continuation** from a state where the label is already established

⚠️ **This is why the "interloper" kept winning.** It was never an interloper: an
ordinary mode, invisible to the reference table, mislabelled by the classifier,
and therefore impossible to rule out by the tests in use.

## A coupling loop changes WHICH MODE it reads

🔴 **AND THE SPECIFIC MECHANISM IS AN ARTIFACT.** `e0k2_sizeq`, which produced
the table below, imports bare `GEO` and never passes `--groove` — verified: all
four of its meshes carry `groove = [0.0, 0.0]`. **In an ungrooved cavity TE011
and TM111 are EXACTLY degenerate** (χ′₀₁ = χ₁₁, at every D/L), so the dip is two
overlapping resonances and "which mode the loop reads" is a question about a
degeneracy the design REMOVES. `e0k2_anchor` grooved for precisely this reason
and says so: with the groove, TM111 is 64 MHz away — 200–300 linewidths — and
there is nothing at 2.45 to confuse.
**The ~176 mm² threshold is therefore not known to be a property of the loop.**
⚠️ Two rigs in the same family disagreed on whether the groove was needed, and
the one that skipped it produced the standing hazard.

> 🔴 **MEASURED ON A GROOVE-FREE CAVITY (2026-08-23) — RE-CHECK BEFORE RELYING
> ON IT.** Everything in this section comes from H3-era runs where `GEO` never
> passed `--groove`, while the design is frozen at 5 × 10 mm. **The filter
> changes which modes exist**, and these are statements about mode behaviour,
> convergence and coupling — all downstream of that. Not necessarily wrong;
> **not established for the cavity being built.**

🔴 Measured, 2026-08-22. A cap loop at r = 0.4805a couples preferentially to a
**TM111 polarisation** when small, and to **TE011** only above ~176 mm² of loop
area. The driven |S11| dip is at essentially the same frequency either way — the
triplet spans a few MHz — so **nothing about the dip tells you which mode you
measured.**

| loop area | mode read | its Q | TE011's own Q |
|---:|---|---:|---:|
| 35 mm² | TM111 | 21,925 | 37,525 |
| 82 mm² | TM111 | 26,201 | 29,073 |
| 176 mm² | **TE011** | 30,020 | 30,020 |
| 384 mm² | **TE011** | 31,665 | 31,665 |

⚠️ **A driven sweep alone cannot tell you.** It returns a dip, not a label.
Pair every driven solve with an eigen solve on the SAME mesh and match by energy
SIGNATURE — a comparison of driven Q against an assumed mode produced a
confident, entirely spurious "smaller loops cost more Q" trend.

⚠️ The loop also MIXES the triplet, not merely shifts it: `pair_q_ratio`
degrades from 1.000 (bare) through 1.087 to 1.364 as the loop grows, and TE011's
own Q is non-monotonic in loop area (37,525 / 29,073 / 30,020 / 31,665) with a
minimum near 82 mm². Unexplained; reported.

## Where a coupling loop goes, and what each one links

TE011, caps at z = 0, L:

    H_z ∝ J₀(χ′₀₁ r/a) · sin(πz/L)    ZERO at caps, MAX at mid-plane
    H_r ∝ J₁(χ′₀₁ r/a) · cos(πz/L)    MAX at caps, ZERO at mid-plane

- **Barrel loop** — `geometry.py` places it at z = 0, the mid-plane, lying in the
  x–y plane so it links **H_z**. That is the H_z **MAXIMUM**: a good placement.
  Its only coupling knob is AREA; the radius is fixed at the wall.
- **Cap loop** (`--loop-cap r`) — links **H_r**, which peaks at **r = 0.4805a**
  (the J₁ peak). 1.39× the |H_z| a barrel loop sees, so 1.93× in coupled power —
  and the RADIUS is a free, continuous knob, which the barrel's never is.

🔑 The 1.39 is reproducible from the field forms above and is the check that
settles which component is which:
`[(π/L)J₁(1.8412)] / [(χ′₀₁/a)|J₀(χ′₀₁)|] = 1.3875` at a = 103.70, L = 88.53.

🔴 **A retracted claim, kept here so it is not re-derived:** an earlier reading
of this file had the sin and cos swapped and concluded the barrel loop sits on a
TE011 node and "cannot couple to TE011". False — it sits at the maximum. The
inverted forms satisfy neither boundary condition, and the 1.39 check fails on
them by construction.

⚠️ Related correction: at the cap H is purely RADIAL, so TE011 DOES have
end-cap current and it is AZIMUTHAL. An annular groove works because it runs
PARALLEL to that current, not because the current is absent (HYPOTHESES still
says the latter).

## Driven or eigen — which question is being asked

They are not two ways to compute the same number. **Eigen has no port**, so β,
Q_ext, S11, delivered power and field amplitude at a given input power are
STRUCTURALLY unavailable from it.

> If the criterion is phrased in **watts, dB or coupling**, it is driven.
> If it is phrased as **which mode, at what frequency, with what Q₀**, it is eigen.

Measured on ONE mesh (E0k, 27,578 tets, order 2, 32 ranks) — the only place the
record compares them fairly:

| | driven | eigen |
|---|---:|---:|
| wall time | **54 s** | 277 s |
| GMRES solves | 8 | 102 |
| KSP iterations | 319 | 4,067 |
| delivered | S11, arg(S11) at 2,001 points over 40 MHz | 8 modes with f and Q |

⚠️ **Not a like-for-like 5×.** Eigen returned the mode landscape (~34 s/mode);
driven returned one resonance in detail. Eigen is the efficient way to SURVEY,
driven the efficient way to INTERROGATE.

🔑 **Frequency resolution is nearly free.** Palace's adaptive PROM converged in
**8 frequency samples** to emit 2,001 points; PROM construction and solve are
0.34 s each. Do not sweep by brute force.

### 🔑 DRIVEN COST SCALES WITH Q — so it is cheapest exactly where eigen fails

> 🔴 **MEASURED ON A GROOVE-FREE CAVITY (2026-08-23) — RE-CHECK BEFORE RELYING
> ON IT.** Everything in this section comes from H3-era runs where `GEO` never
> passed `--groove`, while the design is frozen at 5 × 10 mm. **The filter
> changes which modes exist**, and these are statements about mode behaviour,
> convergence and coupling — all downstream of that. Not necessarily wrong;
> **not established for the cavity being built.**

Added 2026-08-23. The "driven is 2,500–2,900 s" figure in the record was measured
on the **empty, high-Q** cavity and does not transfer. A driven sweep's cost is
its sample count, the step must resolve the linewidth, and linewidth = f₀/Q, so
**samples ∝ Q**:

| case | Q | linewidth | samples for ±40 MHz | est. |
|---|---:|---:|---:|---:|
| empty cavity | 44,384 | 0.056 MHz | ~35,800 | ~3,450 s |
| **loaded plasma** | **~150** | **~16 MHz** | **~130** | **~12 s** |

⚠️ And the two methods are complementary in the right direction: **eigen's cost
is roughly Q-independent but it FAILS where the operator is awkward; driven has
no NLEPS and no divergence-free projection and gets CHEAPER as Q falls.** The
regimes where eigen fails are the regimes where driven is cheapest.

### 🔴 EIGEN'S CONVERGENCE ENVELOPE — two measured regimes where it stops

> 🔴 **MEASURED ON A GROOVE-FREE CAVITY (2026-08-23) — RE-CHECK BEFORE RELYING
> ON IT.** Everything in this section comes from H3-era runs where `GEO` never
> passed `--groove`, while the design is frozen at 5 × 10 mm. **The filter
> changes which modes exist**, and these are statements about mode behaviour,
> convergence and coupling — all downstream of that. Not necessarily wrong;
> **not established for the cavity being built.**

1. **ε near ZERO.** At ne=1e19 (ε=−2.109) the divergence-free PCG stagnates: 92
   non-convergences, reduction factor 1.007. ne=1e20 (ε=−30.09) is healthy
   (0 non-convergences, factor 0.814) and ε=−310 solves in 100 s. **The failure
   is at small |ε|, NOT large.**
2. **High POSITIVE ε beside strong NEGATIVE ε.** At ne=1e20, by ratio ε⁺/|ε⁻|:
   1.00 (0.033) ✅, 3.78 (0.126) ✅, **6.00 (0.199) ✅, 8.00 (0.266) 🔴**,
   11.60 (0.386) 🔴. The boundary is between ε⁺ = 6 and 8.

⚠️ Do NOT merge these two — they share a symptom and joining them by symptom
produced the wrong mechanism first time.
⚠️ **"0 NLEPS iterations" is NOT a signature.** Identical runs gave 0, 49 and 115
NLEPS; the count only measures how many outer iterations fit the timeout.

✅ **Driven crosses both regimes.** It measured ε = +0.067 and ε = −2.109
cleanly, confirming INSTRUMENT's own long-standing claim that *"the geometries
where the eigensolver diverges are exactly where driven should still work."*

### 🔴 A DRIVEN SWEEP RETURNS THE DEEPEST DIP, NOT YOUR MODE

> 🔴 **MEASURED ON A GROOVE-FREE CAVITY (2026-08-23) — RE-CHECK BEFORE RELYING
> ON IT.** Everything in this section comes from H3-era runs where `GEO` never
> passed `--groove`, while the design is frozen at 5 × 10 mm. **The filter
> changes which modes exist**, and these are statements about mode behaviour,
> convergence and coupling — all downstream of that. Not necessarily wrong;
> **not established for the cavity being built.**

`analyse_driven` takes the **global** minimum of |S11|. In every loaded sweep on
the r=2–8.5 mm annulus there is a mode at **2.6232 GHz, up to 19× deeper than
TE011** — the cap loop couples to it far better. Selecting by depth returns a
smooth, plausible, entirely wrong row, and **widening the band makes it worse**.

✅ Select by **CONTINUATION** — seed at the unloaded mode and follow it in small
steps (measured pulls: +2.4, +1.0, +4.6, +15.0, +9.4 MHz) — or by **energy
signature** against an eigen solve on the same mesh.
🔑 **A guard on the QUALITY of a fit cannot tell you the fit is of the WRONG
THING.** Depth-threshold, band-edge and 3 dB-in-band guards all fired correctly
here and none could catch it. Identify the mode by something other than the
quantity being fitted.

🔴 **RETRACTED — I claimed the eigensolver could not do a lossy plasma. It can.**
That entry was written from ONE failed configuration and asserted a capability
limit. A four-case probe varying one thing at a time (2026-08-23) shows the
stall was **the SHIFT TARGET**, not the mesh and not Palace:

| plasma_h | target | outcome |
|---:|---:|---|
| 0.4 | 2.15 | stalled, nconv=0 |
| 1.0 | 2.15 | stalled, nconv=0 |
| 0.4 | **2.40** | **converged, 573 s** |
| 1.0 | **2.40** | **converged, 284 s** |

Eigen then converged at σ = 2.75e-4 through 275 S/m — the whole intended H3
range — in 89–284 s per point.

🔑 **And the target was wrong because a physical assumption was wrong.** I set it
300 MHz BELOW the mode "because loading pulls DOWN and hard". It pulls **UP**:
an overdense plasma has ε_eff < 0, behaves like a conductor, EXCLUDES field, and
therefore shrinks the effective volume and RAISES the frequency. Measured
+1.26 MHz at σ = 275 S/m. A shift target placed in an empty region 300 MHz away
is what NLEPS choked on.

🔑 **Driven has no NLEPS, therefore no convergence cliff.** Every convergence
failure in this record is a NONLINEAR EIGENVALUE failure — the Newton step and
Armijo line search collapsing near degeneracies. Driven is a sequence of
well-conditioned linear solves. **The geometries where the eigensolver diverges
(deep and narrow grooves) are exactly where driven should still work**, which
makes it the route for `prod-narrow` and `h2_d52` rather than abandoning them.

🔴 **Driven only sees what the PORT couples to.** It yields |S11| dips, not
labelled modes, and a mode the loop does not couple to is invisible. For
SUPPRESSION work that is a blind spot — you can be blind to the mode you are
suppressing. The port also perturbs; E0k kept the loop in both members of each
compared pair so it cancels.

⚠️ **H2's own criterion is a driven quantity** — *"TM111 far enough to draw no
power at 2.45 GHz"* — currently measured as an eigen frequency shift with "no
power" inferred from it. That is measuring the coefficient and arguing to the
outcome, the shape of the Q_ext error that once turned a 21-point power gap into
a "98x deficit". A driven confirmation at the chosen groove costs ~1 minute.

## 🔑 THE LOADED-CAVITY TOOLKIT (2026-08-23) — what to use, and what it cost to learn

> 🔴 **MEASURED ON A GROOVE-FREE CAVITY (2026-08-23) — RE-CHECK BEFORE RELYING
> ON IT.** Everything in this section comes from H3-era runs where `GEO` never
> passed `--groove`, while the design is frozen at 5 × 10 mm. **The filter
> changes which modes exist**, and these are statements about mode behaviour,
> convergence and coupling — all downstream of that. Not necessarily wrong;
> **not established for the cavity being built.**

The groove omission invalidated the SCOPE of that day's design numbers. **It did not touch the
instrument work, and that is the part worth keeping.** Measured across the
session:

| solver | rigs | timeouts | solver-seconds burned on failures |
|---|---:|---:|---:|
| **eigen** | 5 | **12** | **10,800 s (3 hours)** |
| **driven** | 4 | **0** | **0** |

**Zero convergence failures across 17 driven cases — on exactly the problems
eigen could not solve at all.** The convergence cliff is not a fact about the
physics; it is a fact about the eigenmode formulation.

### Use DRIVEN for anything loaded. The rule, and why.

- **No NLEPS and no divergence-free projection** — the two things that stagnate
  at ε ≈ 0 and at high ε⁺/|ε⁻|.
- **Cost ∝ Q**, so it gets CHEAPER the more heavily loaded the cavity is:
  ~35,800 samples for the empty cavity, ~130 loaded. The regimes where eigen
  fails are the regimes where driven is cheapest.
- Pair with eigen where BOTH work, to validate. Measured agreement: f₀ to
  **0.83 MHz**, η to **0.0006**, and a dielectric shift to **84 kHz**.

### Sizing a sweep: the BAND brackets the widest feature, the STEP resolves the narrowest

Getting this backwards cost two runs. A 636 kHz step (one linewidth of the most
loaded case) was blind to a 68 kHz dip; a 45 MHz band could not bracket a 45 MHz
linewidth. **One wide sweep, 2.30–2.65 GHz at 200 kHz (1,750 samples), covers
7 MHz to ~350 MHz features and is CHEAPER than the two-stage scheme it replaced.**

### 🔴 Identify the mode by something OTHER than the quantity being fitted

`analyse_driven` returns the **global** minimum. Loaded sweeps routinely contain
a mode 19× deeper than TE011, and a competing in-band one the tuner would
genuinely select. Selecting by depth gives a smooth, plausible, entirely wrong
row — and **widening the band makes it worse**.

✅ **Continuation**: seed at a MEASURED point IN THE SAME REGIME, follow in small
steps, and **abort if the first case misses the seed**. An analytic value from a
neighbouring regime is not a seed — seeding the ne=1e20 rig at the unloaded
frequency put a competing feature 2.8 MHz away and the truth 32 MHz away.
✅ Or **energy signature** against an eigen solve on the same mesh.
🔑 **A guard on the QUALITY of a fit cannot tell you the fit is of the WRONG
THING.** Depth-threshold, band-edge and 3 dB-in-band guards all fired correctly
on the wrong feature and none could catch it.

### ✅ What survives the groove re-check, and why

Not everything above is cavity-dependent. **These do not rest on which modes
exist**, so they stand:

| result | why it survives |
|---|---|
| **samples ∝ Q** for a driven sweep | arithmetic: the step must resolve f₀/Q. The SCALING holds; the specific sample counts quoted are groove-free |
| **η is robust where Q₀ is not** | arithmetic: η = 1 − Q₀/Q_bare is insensitive when Q₀ ≪ Q_bare |
| **\|S11\| cannot distinguish β from 1/β** | one-port circuit theory; resolve the branch from PHASE |
| **band brackets the widest feature, step resolves the narrowest** | a sampling argument, not a cavity result |
| **a guard on the QUALITY of a fit cannot tell you the fit is of the WRONG THING** | a statement about guards |
| **continuation needs a seed MEASURED in the same regime** | a statement about the method |

🔴 **These do NOT survive without re-checking**, because each is a claim about
mode behaviour in a cavity whose modes the filter changes: the ~176 mm²
mode-identity threshold; the ε-contrast convergence envelope (ε⁺ between 6 and
8); the 2.6232 GHz "19× deeper" competitor; the 12→0 timeout comparison; every β,
Q_ext and delivered-power figure; and the dielectric-shift numbers from
`h4_field`.

⚠️ **The distinction to hold onto: a method claim and a cavity claim can sit in
the same sentence.** "Driven is cheapest where eigen fails" is two claims — the
cost scaling (arithmetic, survives) and *where eigen fails* (measured
groove-free, does not).

### Extracting numbers you can trust

- **Quote η, not Q₀.** They agree on η to 0.0006 while differing ~17% on Q₀,
  because η = 1 − Q₀/Q_bare is insensitive when Q₀ ≪ Q_bare.
- **Q_ext is NOT transferable between meshes** — a value carried across gives Q₀
  12× off. β is not mesh-converged (43% for a 1.25× refinement) and Q_ext
  inherits it. Re-derive on the loaded mesh.
- 🔴 **|S11| cannot distinguish β from 1/β.** −11.46 dB is 0.578 OR 1.730.
  Depth-only β silently assumes undercoupling — fine at β ~ 0.02, wrong the
  moment a sweep is designed to REACH critical coupling. Resolve the branch from
  PHASE (`branch_from_phase`), and report AMBIGUOUS near a 180° swing.
- **One-sided 3 dB widths are usable and must be flagged**: validated against
  two-sided at 14.00 vs 14.04 and 30.80 vs 30.40 MHz, η agreeing to the fourth
  decimal.

### Guards now in `run()`, on the config actually solved

`check_torch_bound` (R101, extended — permittivity must match the mesh sidecar, and the
mesh must match the REQUEST) and `check_groove_declared` (the groove omission — a plasma solve
on a groove-free cavity refuses). Both live in `run()` rather than the config
builders because callers assemble geometry themselves.

## 🔑 SHIFT TARGET: FAR BELOW converges where NEAR-THE-CLUSTER fails

**Measured 2026-08-23 on the GROOVED cavity, three attempts:**

| target | N | outcome |
|---:|---:|---|
| 2.30 | 6 | 🔴 1,018 NLEPS — budget exceeded |
| 2.25 | 10 | 🔴 1,040 NLEPS — budget exceeded |
| **1.05** | **12** | ✅ **`h2_groove` solved this cavity with these** — its −64.25 MHz is in the record |

🔑 **Why, and it is counter-intuitive.** Shift-invert transforms eigenvalues to
1/(λ − σ). A σ placed just below a TIGHT CLUSTER makes several transformed
values simultaneously huge and nearly equal — precisely what Krylov methods
separate slowly. Starting far below means the first modes converged are the
**well-separated** low ones, and the cluster is reached with a good subspace
already built.

⚠️ **This does NOT contradict CONVENTIONS §6**, which records target=1.05 as
expensive (H1 inherited it and paid an hour per point). **Both are true: it is
slower per solve AND it converges where the fast setting fails.** Speed and
convergence are different axes, and `solvecost` predicts only the first — it
"predicts the time of solves that converge, and says nothing about which
converge at all" (§6c).

✅ **Rule: put the target in a spectral GAP far from the cluster of interest, and
size N from a mode count** — `h2_groove`'s formula is
`n = count(closed-form modes ≤ ceiling) + 5`.
🔴 **And when a cavity class already has a rig that solved it, copy that rig's
settings before deriving your own.** Three attempts here; the working one was in
the repo the whole time.

## Convergence, unlike cost, CANNOT be predicted

🔴 Tested and negative. Three plausible guards, all of them wrong:

| guard | why it fails |
|---|---|
| nconv stalls N iterations | 604 succeeded, 614 failed — overlapping |
| residual rising K in a row | 146 and 381 such windows in runs that converged |
| residual ≫ best for current eigenvalue | healthy runs swing 1e6–1e8 there too |

Nor from geometry: the two failures sit at **opposite extremes** (deepest 52 mm,
narrowest 3 mm) with successes between them. Grooves deeper than ~10 mm always
make the nonlinear eigenproblem hard; hard is not the same as failing.

✅ **What works is a budget.** 25 converged runs used ≤ **869** NLEPS iterations;
the 2 failures used 1,445 and 4,114. `solvecost.NLEPS_BUDGET = 1000` catches both
with zero false positives — but on a **1.66× margin over two failures**, so it is
a budget and not a predictor: exceeding it is reported as *"did not converge
within budget"*, never a silent drop.

⚠️ `diagnose()`'s rising-residual test is **post-hoc only** — valid at the end of
a finished log, nonsense as a live abort.

## Two capabilities that came out of it

**Faceting is predictable before meshing.** `physics.faceting_shift_mhz` gives
geometric-order-1 error from the equal-area radius of an inscribed N-gon and the
radial share of f² — no simulation. Validated to **5%** across six modes (E0f2),
using the mesh's measured volume deficit. Mesh sizing for a target accuracy is a
calculation, not a sweep.

**Q identifies modes where frequency cannot.** TE011 has **2.03×** TM111's Q, and
the two are EXACTLY degenerate (χ′₀₁ = χ₁₁). `eigmodes.te011_tm111()` separates
them by Q when the wall is lossy and by multiplicity always (m=1 pairs, m=0 does
not). Free in every solve.

## What is NOT characterised

- ✅ **Absolute Q EXTRACTION is now anchored** (2026-08-22). Four independent
  driven-vs-eigen comparisons agree to **4.9–8.8%**, across TWO modes (TE011 and
  TM111) and an 11× range of coupling-loop area: driven Q₀ from the S11
  linewidth and dip depth against the eigenvalue's imaginary part. The bare
  cavity measures **44,384**, reproducing the recorded value exactly.
  ⚠️ Both routes share one mesh, one wall conductivity and one solver, so this
  validates the EXTRACTION of Q, not the surface-impedance physics behind it. An
  external anchor still needs a measured cavity.
- 🔴 **Dielectric loading — DISCARDED, groove-free.** `h4_field`'s 11 meshes all
  carry `groove = [0,0]`; it was measured after H1 on a cavity that is not the
  design. **Every number below is retained only as a record of what the wrong
  cavity said.** Outer sapphire tube −13.71 MHz, all three tubes −15.00 MHz
  against a Slater prediction of −15.3 committed before the solve — **2%**, at
  ε=11.6. Quartz −3.10 (outer) / −3.36 (full). Q cost 0.3%. All configurations
  stay inside 2.40–2.50 GHz.
  🔑 **And the plasma SUPPRESSES the dielectric shift by 78%** — quartz −3.104
  cold → −0.684 loaded — because the plasma excludes field from the bore and cuts
  E_elec at the tube ~75%, material-independently (74.4% vacuum tube, 74.7%
  quartz). Constant to 0.6 points over ε 2–6; **ε=11.6 is a 1.9× extrapolation,
  not a measurement.**
- ✅ **Driven-mode coupling is now measured** — β = 0.015–0.098 on the loaded
  annulus, and driven f₀/η validated against eigen on the SAME geometry to
  0.83 MHz and 0.0006.
  🔴 **But Q_ext is NOT transferable between meshes.** ⚠️ **2026-08-24: e0k2's 50,709 was measured with the loop's port UNASSIGNED (= gap OPEN, §7v) and is retracted. Measured value: Q_ext = 9,231**, and it is thermally invariant (`h3_loopq`, `h3_hot`). Historically, e0k2's Q_ext≈50,709 gives
  Q₀ 12× different from the linewidth route on a different mesh. β is not
  mesh-converged (43% for a 1.25× refinement); Q_ext inherits that.
  🔑 **Quote η, not Q₀.** Driven and eigen agree on η to **0.0006** while
  differing ~17% on Q₀, because η = 1 − Q₀/Q_bare is insensitive when
  Q₀ ≪ Q_bare.
- **TE121** sits at 0.361 MHz, the worst mode, and is the least-converged in the
  window. The faceting model is validated for modes well inside the window; the
  topmost mode is not a test of it.

## Where a check belongs

`preflight` catches CODE patterns — `pkill -f`, missing main guards,
nearest-value matching, falsy numeric flags. It cannot catch "this Q is
physically implausible for this mode": that needs domain knowledge and runtime
values. **The linter guards the harness; a rig's declared checks guard the
physics.** The mistakes they catch do not overlap, and neither substitutes for
the other.

⚠️ A guard that EXCLUDES a point must announce it — count, identity, reason —
and where it feeds a derived number, that number should be reported both with
and without. A criterion that deletes its evidence cannot be caught being wrong.

## Q context: which side of the trade we are on

Measured TE011 Q₀ = **44,384** (aluminium, bare cavity). That is the HIGH-Q side
of a real instrument trade: MP-AES gives up roughly half its Q for stability
against an **untunable magnetron**, because the cavity must tolerate drift the
source cannot follow.

We have a **tunable LDMOS across 2.4–2.5 GHz**, so we are entitled to the high-Q
side — which is why a Q collapse is a FAULT here, not a design choice, and why
~0.5×Q is a meaningful plausibility boundary rather than an arbitrary threshold.

The consequence: critically coupled Q_L ≈ 22,192, loaded linewidth **~110 kHz**,
against a 100 MHz tuning range — roughly 900 linewidths. The source can follow in
RANGE easily; what it needs is **loop BANDWIDTH**, since one linewidth is only
110 kHz. How fast is set by the plasma perturbation, which is H3 and unmeasured.

## Re-verifying

`ops/go ops/remote.sh e0v_reverify.py 32` re-runs the E0 series. It reports a rig
that fails and one whose result file did not change, rather than skipping either.
`physics.py`, `eigmodes.py`, `cachetest.py` and `condcheck.py` have self-tests;
run them first — `physics.py`'s caught two hand-typed reference values on its
first run, and `eigmodes.py`'s caught the Q discriminator firing on PEC noise.
