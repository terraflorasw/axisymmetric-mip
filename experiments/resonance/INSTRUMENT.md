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

## 🔴 The barrel loop cannot couple to TE011

`geometry.py` places every barrel-loop cylinder at **z = 0** with `z0 = -L/2`,
i.e. the cavity **mid-plane**, and the loop lies in the x–y plane so it links
**H_z**. TE011's H_z ∝ cos(π(z+L/2)/L) is **exactly zero there**, as is its
barrel wall current. The flux is zero regardless of loop width or depth.

Any β a barrel loop reports for TE011 is a residual, not a coupling — which is
why one loop gave β = 0.067 in one cavity and 27.5 in another.

✅ **Use `--loop-cap r`.** TE011's H_r is MAXIMUM at mid-plane and peaks at
r = 0.4805a, and the cap loop's radius is a free, continuous coupling knob —
the barrel's never is. Moving the barrel loop off mid-plane is not currently
expressible; z = 0 is hard-coded, not a flag.

⚠️ R69's *"1.39× the |H_z| a barrel loop sees at the wall"* compares PEAK
values, not the field at the loop's own plane. As a statement about the barrel
loop as built it is misleading.

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

- **Absolute Q has no external anchor** — only its scaling law. A Q number is
  trustworthy in ratio, not in absolute value.
- **Dielectric loading is unverified.** E1b failed three times and is retired; no
  claim about what a dielectric does to this cavity survives.
- **Driven-mode coupling** — β, Q_ext, S11 — is unmeasured. E0k compared only the
  resonant frequency.
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
