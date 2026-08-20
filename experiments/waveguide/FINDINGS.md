# TE₀₁₁ cavity — findings

Companion to [`refs/axisymmetric-feed.md`](../../refs/axisymmetric-feed.md).
Convention, as in the ignition experiment: **append only, newest at the bottom.**
**All dates and times are UTC.**

⚠️ **Read [`../../README.md`](../../README.md) first.** It carries the current
design point and the do-not-retry list, and is ~1/15th the length. Come here for
*why* something is believed, or before re-opening a settled question.

⚠️ The "reference geometry" quoted inside early entries (188.6 mm × 100 mm, and
later 202.9 × 85.48) is **superseded**. Current: **202.9 mm dia × 87.67 mm**.

## Index

*Regenerated metadata, not a log entry. The entries below are append-only.*

| § | entry | what it settles |
|---|---|---|
| 1 | Phase 1: mode table, and the brake | TE₀₁₁ matches analytic; brake lifts the exact TE₀₁₁/TM₁₁₁ degeneracy. Two harness bugs |
| 2 | Ignition: drop the slots, adopt TM₀₂₀ | Slots kill every E-dominated mode. Orthogonal tuning handles |
| 3 | Design point a=102, L=85 | ⛔ **superseded** by §9 |
| 4 | Materials, surface finish and thermal | Silver-plated 6061; no anodize on RF surfaces; seam topology |
| 5 | Field margin: the gate, answered | 8.05 kV/cm at 1 kW. Target A fails at 1 atm; **pressure is the only lever** |
| 6 | The striker does not work | ⛔ **negative — do not retry.** Quartz wall keeps metal ≥4 mm from the gas |
| 7 | Real torch: injector and intermediate tube | Costs 4% field; forces a retune. No torch modification needed |
| 8 | Design point confirmed with real torch | ⛔ **superseded** by §9 |
| 9 | Order-1 sweeps are not mesh-converged | Invalidates §3 and §8. Establishes the **+10.4 MHz** offset at h=0.60 |
| 10 | Finite-conductivity abandoned | ⛔ **negative — do not retry.** Perturbative Q stands |
| 11 | The coupler: orthogonality solves the Q mismatch | Two ports, orthogonal, no tuner. Loop sizing |
| — | **OPEN RISK — the pressure ramp** | 🔴 The top unquantified assumption. Not simulable |
| 12 | Driven model works; bare loop cannot match | Driven converges where eigensolves fail. **Self-inductance limit** |
| 13 | Ring field measured; both incumbents ignite on argon | Ring 7.88 vs AMIP 8.17 kV/cm — within 3.5%. ✅ MICAP *and* MP-AES both carry argon to start |
| 14 | Silver-wall Q measured via driven+conductivity | Q₀ = **90,323**, 1.9× the perturbative estimate. Method cross-checks on PEC to 13%. Discrepancy unexplained |
| 14b | Radial viewport nearly free | **0.9% of Q at 25 mm.** Falsifies the axial-viewing constraint; brake need not be the window |
| — | **RECHECK QUEUE** | R1–R6 reopened by the driven method |
| 15 | **R1 answered — 180 Torr** | TM₀₂₀ Q measured **46,339** (1.74× perturbative). Field 10.79 kV/cm. R2 localised to the closed-form family |
| 16 | R2, R4, R6 answered | ✅ Conductivity BC exact (2.01× vs 2.00×) — **closed forms are the fault**. Viewport free on both modes. Q_ext 13,852 |

---

## 2026-08-13 — Phase 1: mode table, and the brake

### Two harness bugs, both of which produced confident wrong output

Recorded because neither announced itself, and one burned two hours of solve.

**1. Variable shadowing silently skipped the mesh write.** A wedge-cut result
named `out` shadowed `build()`'s output-filename parameter, so `gmsh.write(out)`
raised an `AttributeError` — but the "jacobian check: OK" line printed
immediately before it, and the traceback was being filtered out by a `grep` on
the command output. The stale mesh from the previous build survived on disk and
a solve ran on it for 1 h 50 m. **Check exit codes, and never filter the stream
you are diagnosing from.**

**2. Bounding-box PEC detection is wrong for wedges.** The ignition harness
tests wall membership with `max(|x|,|y|)`, correct for a full cylinder. Rewriting
it as `hypot(x,y)` looks more correct and is worse: the bounding-box corner of a
72° wedge's outer face sits at ~1.38a, not a, so most of the cavity wall never
got tagged and Palace applied its natural (magnetic-wall) condition there. The
result was a spectrum of localised junk at Q ~ 3 × 10⁸.

**Fixed topologically: an exterior face is one with a single adjacent volume.**
The cavity is closed, so every exterior face is wall. No coordinates involved,
so it cannot be broken by changing the geometry.

### Baseline — the analytic table is confirmed

With PEC correct, FEM matches the empty-cavity analytic prediction to ~1%:

| analytic | mode | m | FEM |
|---:|---|---:|---:|
| 2.1529 | TE₂₁₁ | 2 | 2.1559 |
| 2.4506 | TE₀₁₁ / TM₁₁₁ | 0 / 1 | 2.4211 / 2.4293 / 2.4321 |
| 2.5985 | TM₂₁₀ | 2 | 2.6013 |
| 2.6011 | TE₃₁₁ | 3 | 2.6028 |
| 2.7930 | TM₀₂₀ | 0 | 2.6893 |

🔢 **TE₀₁₁ at 2.4211 GHz with η = 0.101%**, against the 0.092% predicted
analytically in `axisymmetric-feed.md` §6. The filling-factor argument survives
a real solve with the torch present.

### The degeneracy is worse than a nuisance — it is not resolvable

The §5 sole-survivor test **failed** on the bare cavity, and not because the
claim is wrong. Because χ′₀ₙ = χ₁ₙ exactly, any linear combination of the
TE₀₁₁/TM₁₁₁ triplet is also an eigenvector, so **the solver returns arbitrary
mixtures.** The torch alone splits the triplet by only 8.3 MHz, and the
most-TE₀₁₁ member still came back with sector CV 0.10 — reading as m≠0.

So the pure mode is not merely hard to excite in hardware. It is not cleanly
*available*, in simulation or in reality, until something lifts the degeneracy.

### The dielectric brake works

An annulus of fused quartz (ε_r 3.78) lying flat against each end cap, inner
radius 10 mm, outer radius 94.3 mm. **Not a resonator** — no in-band resonance
of its own, and it does not generate the plasma. It exploits an exact field
contrast at the end plane:

```
every TE mode   transverse E ~ sin(p*pi*z/L)  ->  ZERO on both caps
every TM_mn1    E_z          ~ cos(p*pi*z/L)  ->  MAXIMUM on both caps
```

| t (mm) | TE₀₁₁ | ΔTE (MHz) | bore H % | sector CV | TM₁₁₁ pair | split (MHz) |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 2.4233 | — | 3.425 | 0.1009 | 2.4317 / 2.4345 | 8.3 |
| 1 | 2.4183 | −5.1 | 3.408 | 0.0601 | 2.4054 / 2.4079 | 10.3 |
| **2** | **2.4174** | **−6.0** | **3.426** | **0.0098** | 2.3805 / 2.3815 | **35.9** |
| 4 | 2.4100 | −13.3 | 3.400 | 0.0102 | 2.3207 / 2.3215 | 88.5 |
| 8 | 2.3823 | −41.1 | 3.356 | 0.0069 | 2.1832 / 2.1848 | 197.4 |

🔢 **Selectivity ≈ 8:1.** At 2 mm the TM pair moves −51 MHz while TE₀₁₁ moves
−6 MHz. It degrades to ~6:1 by 8 mm, as expected — TE₀₁₁'s E is zero only *at*
z = 0 and rises across a thick layer, so the null is only exploitable while the
brake is thin.

**The mixing breaks up at 2 mm.** Sector CV falls 0.1009 → 0.0098, an order of
magnitude, and TE₀₁₁'s bore magnetic fraction stays flat at 3.4% throughout —
its character is preserved while its partners walk away.

**Design point: 2 mm per cap.** 36 MHz of split for 6 MHz of detuning.

### With the brake, the §5 claim holds

Re-running the survivor test at t = 2 mm gives **exactly one survivor**:
TE₀₁₁ at 2.4174 GHz, CV 0.0098, η = 0.080%. The only other m=0 mode in band
(TM₀₂₀ at 2.6502) is electrically dominated and is excluded on character — and
would independently be killed by the circumferential slots.

> **So the brake is load-bearing, not an optimisation.** Without it the sole-mode
> property that the whole architecture rests on does not exist.

🔢 **And it is nearly free.** Brake-limited Q is 2.16 × 10⁶ against a copper-wall
Q of ~53,000, so combined Q ≈ 51,700 — a **2.5% penalty**. Wall loss dominates
completely; the brake's dielectric loss is irrelevant.

### The classifier lesson — ratios are not discriminators

The first pass identified TE₀₁₁ as the mode with minimum bore E/H, and tracked
the **wrong mode at every thickness**: a mode near 2.58 GHz has E/H = 0.019
against the real TE₀₁₁'s 0.029. That sweep reported TE₀₁₁ moving −198 MHz and
looked like a clean falsification of the whole idea.

**A ratio can be small for two different reasons; an absolute energy fraction
cannot.** The real TE₀₁₁ holds 3.43% of the mode's magnetic energy in the bore
against the impostor's 0.09% — a 37× separation rather than a marginal call.
`reextract.py` re-derives the sweep from saved CSVs on that basis.

Generalising: **identify a mode by where its energy is, not by a ratio of two
quantities that can both be small.**

### Caveats

- ⚠️ **PEC walls.** Every Q here is a lossless-wall value set only by quartz
  tanδ. The Q × η figure of merit is therefore *not* comparable to the alumina
  ring's 47.5 — that one carries real dielectric loss. A finite-conductivity run
  is needed before any coupling comparison.
- ⚠️ **Slots not modelled.** The circumferential mode filters of §5 are still
  argued from wall-current topology only. They radiate, so they need an
  absorbing boundary, not PEC.
- ⚠️ Order 1 throughout. The ignition work found order-1 frequency error can
  reach 0.45%; splits are differences on a shared mesh, so they should be more
  robust than absolute values, but the design point deserves an order-2 check.
- η fell 0.101% → 0.080% once the mode was pure, so the earlier figure was
  inflated by contamination. 0.080% is the number to use, against 0.092%
  analytic.

### Next

1. **Order-2 confirmation** at t = 2 mm.
2. **Finite-conductivity walls** — makes Q and Q × η mean something and lets the
   ceramic-free-vs-ceramic comparison in §6 actually be made.
3. **Model the slots**, with an absorbing boundary, and check they damp TM₀₂₀ and
   the m≠0 family as the wall-current argument claims.
4. **Ignition mode.** Still the open question that could sink the route: §5's
   filtering suppresses E-dominated modes, which is exactly what mode-shift
   ignition needs. TM₀₂₀ at 2.65 GHz with η = 6.3% is the obvious candidate —
   E-dominated, m=0, 233 MHz above TE₀₁₁ — but it is also precisely what the
   slots are designed to kill. **These two requirements are in direct conflict
   and the conflict is not yet resolved.**

---

## 2026-08-13 — Ignition: drop the slots, adopt TM₀₂₀

The previous entry closed on a conflict: §5's circumferential slots remove
every mode carrying axial wall current — which is every TM mode — and every
E-dominated mode is a TM mode. The slots kill exactly what mode-shift ignition
needs.

**Resolved by removing the slots, not by reconciling them.**

Their real job was killing TM₁₁₁, the exact degenerate. The brake now does that
by frequency separation, which is robust to feed asymmetry in a way
symmetry-nulling is not — the reason the brake was added at all. The m≠0 modes
are nulled by the N-fold feed *and* sit far off in frequency (2.15, 2.60 GHz).
So the slots' only remaining function was suppressing TM modes generally, which
is precisely the harm. They are now redundant and costly.

### TM₀₂₀ is a better ignition mode than the ring's

| property | consequence |
|---|---|
| m = 0 | the symmetric feed **drives** it rather than fighting it |
| E_z ∝ J₀(χ₀₂ r/a), max at r=0 | field is **maximum on axis**, not merely present |
| bore electric fraction ~5–6% | vs the operating mode's 0.08% — a 60× contrast |
| p = 0, no z-variation | uniform along the **whole torch**: a long breakdown path, not a hot spot |

### The handles are orthogonal — the ring's central difficulty does not occur

```
TM020   f = chi_02 * c / (2*pi*a)   -> radius ONLY (p=0)
TE011   f = f(a, L)                 -> radius and length
brake                               -> pulls TM down, leaves TE alone
```

🔢 Measured over the first sweep, at fixed radius, varying L from 80 to 98 mm:

| | ignition mode moves | TE₀₁₁ moves | ratio |
|---|---:|---:|---:|
| a = 98 mm | 13 MHz | 216 MHz | **17:1** |
| a = 101 mm | 13 MHz | 221 MHz | **17:1** |

**Length is a near-pure handle on the operating mode.** Contrast
`experiments/ignition` §4, where ring scale and enclosure diameter both moved
both modes, and tuning the operating mode onto target actively pushed the
ignition mode *away* — the finding that forced a joint 2-D solve there.

### First sweep — 4 radii × 4 lengths, 2 mm brake, order 1

| a (mm) | L (mm) | TE₀₁₁ | ignition | split (MHz) | both in ISM |
|---:|---:|---:|---:|---:|:--:|
| 98 | 92 | 2.4404 | 2.5446 | +104 | |
| 101 | 86 | 2.4777 | 2.4726 | −5 | ✅ |
| 104 | 80 | 2.4979 | 2.4019 | −96 | ✅ |
| **104** | **86** | **2.4418** | **2.4052** | **−37** | ✅ |

Best is a=104, L=86: both modes in band, split 37 MHz against a ~15 MHz loaded
linewidth. The split is negative — the ignition mode sits *below* the operating
mode, as it did for the ring.

⚠️ **Sector CV degrades across the space** — 0.009 at a=101/L=86 but 0.274 at
a=104/L=80. A 2 mm brake is not uniformly sufficient; brake thickness may need
to scale with geometry. Any chosen point must be checked for CV, not just
frequency.

### Two self-inflicted failures, recorded

**Editing a file that a running job shells out to.** `geometry.py` was patched
while the sweep was invoking it once per grid point, and it was briefly
referencing a helper that had just been deleted. `NameError: name 'curve' is
not defined` destroyed 6 of 16 points. Freeze the inputs of a running sweep.

**gmsh's high-order optimiser aborts the process.** When it cannot repair a
curved element it raises a C++ `std::runtime_error` that reaches `terminate()`
— SIGABRT, exit 134. It never becomes a Python exception, so `try/except`
cannot catch it; only the calling process can respond. Perturbing the mesh size
changes element topology and reliably dodges it: at a=101/L=92, size factor
1.00 aborts while 0.96, 1.06 and 0.90 all succeed. `tune-sweep.py` now retries
across factors before giving up.

### Next

1. Refinement over a ∈ {102,103,104}, L ∈ {82,84,86,88} — running.
2. **Check sector CV at the chosen point**, and thicken the brake if it is not
   below ~0.02. Frequency alone is not sufficient evidence of a clean mode.
3. Order-2 confirmation of the final geometry.
4. The ignition question this whole entry serves is still only half answered.
   A mode with 5–6% of its electric energy in the bore *exists* and is
   reachable — but §4.2/§4.3 of `refs/ignition-study.md` need |E| in V/m
   against the N₂ breakdown threshold, and that needs a **driven** solve, not
   an eigenmode one. Mode existence is necessary, not sufficient.

---

## 2026-08-14 — Design point: a=102, L=85, brake 3 mm

### Retune at 3 mm brake

The 2 mm brake left sector CV in the 0.025–0.045 range across much of the
design space — frequencies in band but the operating mode not cleanly m=0.
Going to 3 mm fixes purity but pulls TM₀₂₀ down 27 MHz/mm, out of the band.
Both are handles on the same mode, so it is an arithmetic retune: shrink the
radius to push TM₀₂₀ back up, lengthen to bring TE₀₁₁ back down.

| a (mm) | L (mm) | TE₀₁₁ | ignition | split (MHz) | CV | TE margin | ign margin |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 101 | 85 | 2.4885 | 2.4450 | −43 | **0.010** | 11.5 | 45.0 |
| 101 | 86 | 2.4773 | 2.4473 | −30 | **0.010** | 22.7 | 47.3 |
| 101 | 87 | 2.4590 | 2.4468 | −12 | 0.016 | 41.0 | 46.8 |
| **102** | **85** | **2.4786** | **2.4218** | **−57** | 0.018 | **21.4** | **21.8** |
| 102 | 86 | 2.4626 | 2.4239 | −39 | 0.020 | 37.4 | 23.9 |
| 102 | 87 | 2.4482 | 2.4247 | −23 | 0.022 | 48.2 | 24.7 |

Margins are to the 2.400 / 2.500 GHz band edges.

### Recommended geometry

| | |
|---|---|
| Cavity | **204.0 mm dia × 85.0 mm**, copper, barrel bored from bar |
| Brake / window | **3 mm fused quartz annulus** against each end cap, 20 mm clear aperture on axis, 204 mm OD |
| Torch | 20 mm OD / 17 mm ID quartz (unchanged) |
| **Operating mode** | **TE₀₁₁, 2.4786 GHz**, sector CV 0.018, η = 0.08% |
| **Ignition mode** | **TM₀₂₀, 2.4218 GHz**, 5.20% of its E in the bore |
| Mode shift | **−57 MHz**, 3.9 loaded linewidths |
| Feed | 4 loops from a radial divider, one amplifier |
| Absent by design | no dielectric resonator, no iris, no slots |

Chosen over a=101/L=86 (CV 0.010 but only −30 MHz split) and a=101/L=85
(−43 MHz but TE₀₁₁ just 11.5 MHz below the band edge). a=102/L=85 is the only
point with a split beyond 3 linewidths, CV inside 0.02, and **balanced** margins
at both edges.

### Tolerance — 0.005" (0.127 mm) is comfortable

🔢 Measured sensitivities:

| dimension | dTE₀₁₁/dx | d(ign)/dx |
|---|---:|---:|
| radius a | −12 MHz/mm | −23 MHz/mm |
| length L | −14 MHz/mm | +1 MHz/mm |
| brake t | −0.8 MHz/mm | −26 MHz/mm |

The radius figure matches the closed form −f/a = −23.7 MHz/mm, an independent
check that TM₀₂₀ behaves exactly as the analytic model says.

Stacking ±0.127 mm on all three: **TE₀₁₁ ±2.3 MHz, ignition ±4.4 MHz, split
±4.0 MHz** (RSS). Against ~21 MHz margins that is 5–9×. **0.010" would also
clear.** This is not a tight-tolerance part.

⚠️ **Direction matters for the two edges.** Thermal expansion moves everything
down, so the TE₀₁₁ upper-edge violation is worst **cold** and the ignition
lower-edge violation is worst **hot**. At a=102/L=85, worst case cold is
TE₀₁₁ = 2.4820 (18 MHz margin) and worst case hot (100 K rise) is
ignition = 2.4114 (11 MHz margin). Both hold.

### Dimensional tolerance is not the binding constraint

🔢 The **unloaded** linewidth is f/Q = 2.45 GHz / 52,000 = **47 kHz**. Machining
scatter of ±2.3 MHz is fifty times that, so no achievable tolerance lets the
unloaded resonance be hit by construction — and pre-ignition is exactly when it
must be hit. 🔢 Copper's 16.5 ppm/K gives −40 kHz/K, i.e. **0.86 unloaded
linewidths per kelvin**; the cavity walks tens of linewidths during warm-up.

**S11 sensing and f₀ tracking are load-bearing, not conveniences** — the same
conclusion `coupling-architecture.md` §0 reached for the ring.

### Seams matter more than sizes ⚠️

From wall-current topology, same basis as the mode-filter argument:

- TE₀₁₁'s wall current is **purely azimuthal**. A circumferential barrel/end-cap
  seam is crossed by axial current only, which TE₀₁₁ does not have — so **that
  joint is electrically invisible to the operating mode.** Bolt it; no RF
  gasket, no welding.
- **The barrel must be one piece.** A longitudinal seam (rolled-and-welded tube)
  cuts azimuthal current head-on. Bore from bar or spin it.
- ⚠️ **But TM₀₂₀ does carry axial current across that end-cap seam.** The joint
  that is free for operation is lossy for **ignition** — the mode that needs
  high Q to build field. That seam wants real RF contact even though the
  operating mode is indifferent to it. Easy to miss.

🔢 Specify surface finish: skin depth is 1.34 µm, and as-machined Ra of
1.6–3.2 µm is comparable or larger, worth tens of percent of Q.

### What this does NOT establish

The eigenmode programme has gone as far as it can. It shows a suitable mode
**exists** at a reachable frequency with 5.2% of its electric energy in the
bore. It cannot show the field is strong enough to break down nitrogen.

`refs/ignition-study.md` §6 gates Target A on a **≥2× field margin** against the
N₂ breakdown threshold, in V/m at a stated drive power. That needs a **driven**
solve, not an eigenmode one. Everything above is necessary and not sufficient.

### Next

1. **Order-2 confirmation** of a=102 / L=85 / 3 mm.
2. **Finite-conductivity walls** — makes Q real, and lets §6's Q × η comparison
   against the alumina ring finally be made.
3. **Driven solve** at the ignition mode: |E|max in the bore vs drive power,
   against `ignition-study.md` §4.3. This is the gate.
4. Sanity-check the 4-loop radial divider excites TE₀₁₁ and not the m≠0 family,
   which so far is argued from symmetry alone.

---

## 2026-08-14 — Materials, surface finish and thermal

### Surface finish is an ignition-phase parameter only

🔢 Ideal-copper Q for the a=102 / L=85 geometry is **46,433** — not the 53,060
quoted earlier, which was the original a=94.3 / L=100 cavity. The shorter cavity
has proportionally more end-wall loss. Unloaded linewidth is therefore **53 kHz**
and thermal drift 0.76 unloaded linewidths per kelvin. Tolerance conclusions are
unchanged: machining scatter is still ~43× the linewidth.

| finish | Ra (µm) | Q | linewidth | E vs ideal |
|---|---:|---:|---:|---:|
| lapped / plated | 0.2 | 45,300 | 54 kHz | 0.99 |
| ground | 0.4 | 42,400 | 58 kHz | 0.96 |
| fine machined | 0.8 | 34,400 | 71 kHz | 0.86 |
| machined | 1.6 | 26,500 | 92 kHz | 0.76 |
| as-milled | 3.2 | 24,000 | 102 kHz | 0.72 |

Hammerstad roughness model; ⚠️ it saturates at 2× and the Huray model is harsher,
so the rough rows are optimistic.

**Once the plasma lights, finish stops mattering entirely.** 🔢 Wall loss is
Q_loaded/Q_wall = 165/46,433 = **0.36% of drive power**, about 3.6 W at 1 kW.
Surface finish only ever affects the pre-ignition field, where E ∝ √Q.

> **The trade against sensing latency resolves against roughness.** A rough wall
> doubles the linewidth (54 → 102 kHz), easing a tracking requirement that was
> never tight — at 2 K/s warm-up you exit resonance in 0.66 s vs 1.21 s, both
> needing ~10 Hz loop bandwidth against the kHz a solid-state amplifier manages.
> Acquisition is easier still: machining places f₀ within ±2.3 MHz, so a ±5 MHz
> sweep at 46 kHz steps is 217 points, milliseconds. Meanwhile roughness costs
> **28% of the ignition field**, against the ≥2× margin the route is gated on.
> Buy the Q.
>
> ⚠️ This is why the MP-AES comparison does not transfer. A magnetron cannot
> track, so a low-Q forgiving cavity is a *requirement* there. Solid-state drive
> with f₀ tracking is exactly what buys the freedom to take the high Q — the same
> argument `coupling-architecture.md` §3 makes for mode-shift ignition being
> possible at all.

### Smooth, not precise — they are different operations

Dimensional tolerance is not binding (±0.005" gives 5–9× margin; ±0.010" also
clears). Surface **smoothness** is what buys Q. These need different processes,
and conflating them buys expensive precision that does nothing.

🔢 The best smoothing processes are subtractive and it does not matter:
electropolishing removes 10–50 µm, shifting TE₀₁₁ by 0.12–0.60 MHz against
~21 MHz of band margin. **Dimensionally free.**

**Machine to ordinary shop tolerance, then electropolish or bright-plate.**
No precision operation anywhere in the process.

### Material — plate the substrate, do not choose it

| material | σ (S/m) | Q | field vs Cu |
|---|---:|---:|---:|
| silver | 6.3e7 | 48,400 | 1.02 |
| copper | 5.8e7 | 46,400 | 1.00 |
| aluminium 6061 | 2.5e7 | 30,500 | 0.81 |

Bare 6061 costs 19% of the ignition field before any surface treatment — alloying
hurts conductivity far more than purity tables suggest.

**But RF only sees the top few skin depths, so the substrate is electrically
irrelevant once plated.** Silver skin depth is 1.28 µm:

| plating | skin depths | field reaching substrate |
|---:|---:|---:|
| 3 µm | 2.3 | 9.6% |
| **5 µm** | **3.9** | **2.0%** |
| 10 µm | 7.8 | 0.04% |

At ≥5 µm the cavity performs as solid silver — **better than copper** — on a
machinable, cheap aluminium substrate.

⚠️ **No nickel underlayer.** Silver-on-aluminium normally goes through nickel,
which is ferromagnetic: R_s = 322 mΩ against silver's 12.4 mΩ, **26× worse**.
Specify zincate → copper strike → silver, or keep silver ≥10 µm so the nickel
sits 8 skin depths down.

⚠️ **No anodize on any RF surface.** Aluminium's skin depth is 1.72 µm; Type II
anodize is 5–25 µm and Type III 25–100 µm — a dielectric layer **3–58× the skin
depth** on the current-carrying surface, porous and hygroscopic, at the frequency
chosen because water absorbs there. TE₀₁₁'s wall E-null (J₁(χ′₀₁) = 0) may limit
the damage, but that is unquantified risk on the gating parameter.

**Copper oxidation is not an RF problem** — native oxide self-limits at 2–50 nm,
0.15–3.7% of one skin depth. A handling concern, not a loss mechanism.

### Optical — reflective inside, baffle in the path

The RF and optical requirements are in direct opposition: RF wants smooth,
conductive and specular; stray-light rejection wants black, absorbing and
diffuse. **Do not make one surface serve both.**

A blackened baffle stack at the window, *outside* the RF volume, rejects
wall-scattered light geometrically at zero Q cost. Strictly better than
blackening the cavity.

⚠️ ML on the spectrometer output can also absorb the artifact, and that is
legitimate — it is deconvolution of a real instrumental term, closer to the
nitrate UV/DOC case `soil-testing/metrics-draft-v2.md` §4 endorses than to v1's surrogacy.
Two caveats keep the baffle preferable:

- **It drifts.** Wall reflectivity changes with oxidation, sample deposition and
  temperature, so it is a moving target rather than a fixed calibration.
- **It is steeply wavelength-dependent.** Copper reflects ~95% in the red but
  falls below ~600 nm and is poor in the UV; silver is flatter to ~350 nm with a
  notch near 320 nm. The analyte lines straddle exactly that transition — K
  766.5 nm where reflection is strong, against Ca 393.4, Mg 279.6, Zn 213.9 and
  P 213.6 nm where it is not.

Do both: baffle at source, ML for what only ML can do.

**Bonus from the reflective interior:** plasma radiation passes through the
quartz torch and mostly reflects rather than being absorbed, so the polished wall
also reduces the radiant heat load it has to shed.

### Thermal — anodize the exterior

🔢 Exterior area 0.120 m², at 80 °C into 25 °C ambient:

| exterior finish | radiative |
|---|---:|
| bare polished aluminium (ε ≈ 0.06) | 3.1 W |
| **anodised, any colour (ε ≈ 0.85)** | **44.1 W** |
| — natural convection, h ≈ 7 | 46.1 W |
| — forced air, h ≈ 25 | 164.8 W |

**Anodising the outside roughly doubles passive dissipation**, matching natural
convection on its own. ⚠️ Dye colour is nearly irrelevant to this: anodised
aluminium runs ε ≈ 0.85 in the thermal IR regardless of black or white, because
the emission is from the Al₂O₃ layer, not the pigment. Colour matters for solar
absorption, which is not a factor indoors. **Black is fine; choose it on any
grounds you like.**

Note the RF wall load is only ~3.6 W at 1 kW — the real thermal load is radiant
and conductive from the torch, which is why the reflective interior helps.

### Differential expansion at the brake

🔢 Over 100 K, a 204 mm copper cavity grows 0.34 mm while the 204 mm quartz
annulus grows 0.011 mm (α = 16.5 vs 0.55 ppm/K); aluminium is worse at 23 ppm/K.
That is 0.32 mm of differential across the diameter against a 3 mm brittle plate.

**The brake needs a compliant mount** — spring or gasket at the OD, never a rigid
clamp.

### Materials spec

| | |
|---|---|
| Substrate | 6061 aluminium, machined to ±0.005" (ordinary shop tolerance) |
| Barrel | **one piece**, bored or spun — no longitudinal seam |
| Finish | electropolish, then bright silver plate **≥5 µm** |
| Plating stack | zincate → copper strike → silver. **No nickel** |
| RF surfaces | **no anodize, ever** |
| Exterior | anodize freely, any colour, for emissivity |
| End-cap joint | bolted; invisible to TE₀₁₁, but needs real RF contact **for ignition** |
| Optical | blackened baffle in the collection path, outside the RF volume |
| Brake | 3 mm fused quartz, compliant mount at OD |

---

## 2026-08-14 — Field margin: the gate, answered

### Absolute field without a driven solve

Palace normalises every mode to the same stored energy (3.4024e-10 J each for
E_elec and E_mag), so absolute field follows from U = Q_L·P_abs/ω. **No driven
solve is needed to answer the gate question.**

⚠️ Palace's Q here is **dielectric loss only** — the walls are PEC. Real Q must be
assembled:

| contribution | Q |
|---|---:|
| silver wall, electropolished (Ra 0.2) | 37,600 |
| brake + torch dielectric (from Palace) | 99,400 |
| **combined Q₀ for TM₀₂₀** | **27,300** |

> ⚠️ **The brake costs 27% of the ignition mode's Q.** TM₀₂₀'s E_z peaks exactly
> where the brake sits — the same mechanism that separates the modes damps the
> one ignition needs. Same physics, opposite sign.

🔢 Optimum coupling is **β = 0.5** (undercoupled), maximising Q_L·P_abs and
beating critical coupling by 18%.

**Bore field: 8.05 kV/cm at 1 kW.** Against the 30 kV/cm threshold of
`ignition-study.md` §4.3 that is **0.27×**. 1× needs 13.9 kW; the gated ≥2×
needs **55.6 kW**.

**Target A fails at atmospheric pressure on the bare mode**, by an order of
magnitude in power — exactly as §2 predicted structurally, and why MICAP still
uses argon and a spark.

### Two feed problems the driven model must solve

**1. No fixed coupler can match both states.** Unloaded Q₀ = 27,300 against
plasma-loaded ≈ 165 — a **165× ratio**. Match for operation and pre-ignition
coupling collapses to 2.4% absorbed, dropping the bore field to **0.13 kV/cm,
230× below threshold**. Match for ignition and only 2.4% of power reaches the
plasma in operation. **The coupler must be switchable or tunable.**

⚠️ This refines `coupling-architecture.md` §9. Its "reflects almost regardless of
tuning" holds only for a coupler fixed at the loaded value; matching the unloaded
cavity is perfectly possible, just not simultaneously.

**2. The two modes are orthogonal at the wall.** TE₀₁₁ presents **H_z**, TM₀₂₀
presents **H_φ**. A loop linking one links none of the other. A single loop
cannot drive both; a **45° tilt in the φ–z plane** drives both at −3 dB each.
Mode-shift ignition with one feed constrains the coupler geometry — it is not a
free consequence of frequency agility.

### Pressure is the lever, and geometry is not

⚠️ Collision-limited scaling, E_eff/p ≈ 30 V/(cm·Torr) for air, with the
effective-field correction. Needs the real N₂ curve — `ignition-study.md` §9 q2.

| p (Torr) | p (atm) | E_break | margin @1 kW | margin @10 kW |
|---:|---:|---:|---:|---:|
| 760 | 1.00 | 22.8 kV/cm | 0.4× | 1.1× |
| 400 | 0.53 | 12.0 | 0.7× | 2.1× |
| 200 | 0.26 | 6.0 | 1.3× | 4.2× |
| **134** | **0.18** | **4.0** | **2.0×** | 6.3× |
| 100 | 0.13 | 3.0 | 2.7× | 8.5× |

🔢 **2× margin at 1 kW CW needs 134 Torr (0.18 atm). 3× needs 89 Torr.** At 10 kW
pulsed, 2× comes at 424 Torr — a gentle vacuum.

**The bore diameter does not enter.** 🔢 Diffusion length Λ = 0.35 cm, so
diffusion only raises the threshold below pΛ ≈ 1 Torr·cm, i.e. **p < 2.9 Torr** —
two orders of magnitude below the operating point. Above that the threshold is
set by pressure alone.

**And the geometry has no freedom left anyway.** a = 102 mm is fixed by putting
TM₀₂₀ in band; L = 85 mm is fixed by putting TE₀₁₁ in band. 🔢 For TM₀ₙ₀,
E ∝ √(Q_L/V_eff) ∝ 1/√(L+a), so a shorter cavity would give more field — but L is
not available. **The ignition field is not a design variable. Pressure is.**

> **So the answer to Target A is not more power, not the ceramic, and not a
> spark. It is a valve and a small pump** — mechanism 3 of `ignition-study.md`
> §5, already priced there at $50–200. A diaphragm pump reaching 100–150 Torr is
> a few hundred dollars and runs only at startup.

🔢 Pumping 760 → 134 Torr shifts f₀ up by ~0.5 MHz, about 6 unloaded linewidths.
Predictable, and the tracking loop absorbs it — but it must be *expected*, since
it is 10× the linewidth.

### What is now the critical unknown

The scheme depends on igniting at ~130 Torr and **ramping to atmospheric while
the microwave sustains the discharge**. That is `ignition-study.md` §9 q3 — how
dense the N₂ plasma must be for sustaining to take over — and it has moved from a
background question to **the** question. §2's structural claim (sustaining
threshold ≪ breakdown threshold) is what the whole approach now rests on, and it
is not yet quantified.

### Next

1. **Triple-point striker** — local enhancement is a field-*shape* ratio, so it
   comes from a cheap eigenmode run, not a driven solve. Worth having even with
   the pressure route: it buys margin at higher pressure.
2. **Switchable coupler** — the driven solve's real job, with the tilted-loop
   mode split.
3. **N₂ breakdown curve** at 2.45 GHz for Λ = 0.35 cm, with an uncertainty band.
   Every margin above inherits its error.
4. **The sustaining threshold and the pressure ramp.** Now the gate.

---

## 2026-08-14 — The striker does not work, and standard torches are fine

### Triple-point striker: dead, for a structural reason

An annular metal ridge on the end cap, rounded top (never a sharp edge, per
`ignition-study.md` §7), cut out of the air so the topological rule tags it PEC
automatically. It must live **outside** the torch: the bore gas is enclosed by
quartz, and metal inside the torch is in the sample path, where erosion becomes
permanent spectral background.

The hope was that TM₀₂₀'s E_z, being *tangential* to the torch wall and therefore
continuous across it, would carry an enhancement raised outside the tube into
the bore.

| case | h, r_tip, r_ring (mm) | ignition f | bore E | bore field |
|---|---|---:|---:|---:|
| none | — | 2.4993 | 5.703% | 1.00× |
| h5r1 | 5, 1, 11 | 2.4809 | 5.613% | 0.99× |
| h5r25 | 5, 2.5, 12.5 | 2.4814 | 5.085% | **0.94×** |
| h8r25 | 8, 2.5, 12.5 | 2.4586 | 5.672% | 1.00× |

**No enhancement reaches the bore in any geometry**, and every ridge drags TM₀₂₀
down 18–41 MHz — a retune for no benefit.

🔢 **The trade never closes.** Enhancement at a rounded feature is a near-field
effect decaying over ~r_tip, with β ≈ 1 + h/r_tip. Buying reach by increasing
r_tip reduces β in exact proportion. The nearest possible metal is r = 10 mm
(torch OD) and the bore is r < 8.5 mm, so the tip-to-gas distance is ≥4 mm
however the ridge is shaped.

⚠️ Metric caveat, checked: bore energy is integrated over the full 85 mm, which
would dilute a very local effect. But a genuine 3× enhancement over 3 mm would
raise it 28%, and 2× over 2 mm would give 7%. Measured −11% to 0%. Nothing is
hiding.

Dielectric enhancement is not a way out either — for E normal to a quartz/gas
interface the gas-side field is capped by ε_r = 3.78, a plug filling half the
bore gives only ~1.6×, and it obstructs the gas path.

> **So no practical field enhancement is available in the bore.** The field is
> fixed at 8.05 kV/cm per kW by a geometry with no remaining freedom (§ above),
> and **pressure is the only lever**, with pulse power secondary. Mechanism 2 of
> `ignition-study.md` §5 — the triple-point striker, listed there as "free
> (geometry)" — is not available in this architecture.

### Standard torches: no modification needed

The model already uses standard Fassel geometry — **20 mm OD, 1.5 mm wall,
17 mm ID** — which is the commodity part. Nothing in the design touches it:

| feature | where it lives |
|---|---|
| brake | cavity end cap, ID 20 mm, clears the torch OD |
| striker (were it used) | r ≥ 10 mm, entirely outside the torch |
| cavity | 85 mm long, passes a standard 120–150 mm torch straight through |

**The cost risk is not the torch.** It is the reduced-pressure fixture: a
standard torch is open at both ends, so pumping to ~134 Torr means sealing the
*exhaust* while plasma runs through it. That is a novel fitting at the torch tip
and it must survive the plasma exit. `ignition-study.md` §5 prices the valve at
$50–200, which should now be treated as optimistic.

🔢 **The axial aperture is free electrically.** A 20 mm bore has a TE₁₁ cutoff of
8.79 GHz, so at 2.45 GHz it is 3.6× below cutoff and attenuates at ~1540 dB/m —
**31 dB per 20 mm of depth**, 60 dB for a 40 mm chimney, with no gasket. It
doubles as the optical path and the exhaust duct.

### Where the model is still unfaithful ⚠️

The torch is modelled as a plain hollow tube. A real Fassel torch has an
intermediate tube and an **injector**, and the injector sits on axis — exactly
where TM₀₂₀'s E_z peaks. It displaces gas from the highest-field region, so it
will change η and the effective breakdown gap.

Also, in a real torch the plasma forms **downstream of the intermediate tube**,
in the last 20–30 mm before the tip, not uniformly along the tube as modelled.
The torch must therefore be positioned with that region at the cavity mid-plane,
where TE₀₁₁'s H_z peaks.

Both should be modelled before any hardware. Neither requires a custom torch.

---

## 2026-08-14 — Real torch: injector and intermediate tube

Standard Fassel assembly added: outer 20/17 mm (unchanged), intermediate
16/14 mm ending 20 mm below mid-plane, injector 5/2 mm ending 25 mm below.

⚠️ **The energy-integration region changed with it.** Attribute 1 is now the
**plasma zone** — the clear bore downstream of the intermediate tube — not the
whole 85 mm tube, because that is where the plasma actually forms. η from here
is not comparable with earlier entries. Consistency check: outer-only gives
3.865% against the old 5.205% scaled by 62.5/85 = 3.83%, agreeing to 1%, so the
drop is the redefinition and not a physics change.

| | outer only | full Fassel | Δ |
|---|---:|---:|---:|
| TE₀₁₁ | 2.4779 | 2.4756 | **−2 MHz** |
| ignition TM₀₂₀ | 2.4233 | 2.4105 | **−13 MHz** |
| split | −55 MHz | −65 MHz | |
| plasma-zone E | 3.865% | 3.557% | **0.959× field** |

**TE₀₁₁ barely notices the inner tubes.** The injector sits on axis, where
TE₀₁₁'s E_φ vanishes — the same null that makes the brake selective and the
axial window free. TM₀₂₀ moves 6× further because its E_z peaks exactly there.

🔢 Field 8.05 → **7.72 kV/cm** at 1 kW, so 2× margin moves 134 → **129 Torr**
and 3× moves 89 → 86 Torr. Immaterial to the architecture.

### But it forces a retune ⚠️

Ignition at 2.4105 leaves only **10.5 MHz** to the 2.400 band edge. Against
±6.4 MHz worst-case tolerance and −4 MHz thermal at 100 K, that is 0.1 MHz of
margin — not viable.

🔢 Using the measured sensitivities (−23 MHz/mm on a for the ignition mode,
−12 MHz/mm on a and −14 MHz/mm on L for TE₀₁₁):

**a: 102 → 101.43 mm, L: 85 → 85.48 mm**, brake 3 mm.

Not yet solved — the correction is arithmetic from the orthogonal handles and
should be confirmed. This is the outstanding action.

### Revised design point (to be confirmed)

| | |
|---|---|
| Cavity | 202.9 mm dia × 85.5 mm |
| Brake | 3 mm fused quartz per cap, 20 mm clear aperture |
| Torch | standard Fassel, no modification |
| Ignition | ~130 Torr for 2× margin at 1 kW |

---

## 2026-08-14 — Design point confirmed with the real torch

Retune solved: **a = 101.43 mm, L = 85.48 mm, brake 3 mm**, full Fassel torch.

### The orthogonal-handle arithmetic predicted it to ~1 MHz

| | predicted | solved | error |
|---|---:|---:|---:|
| ignition TM₀₂₀ | ~2.4235 | **2.4245** | 1.0 MHz |
| TE₀₁₁ | ~2.4756 | **2.4741** | 1.5 MHz |

The correction was computed purely from the measured sensitivities (−23 MHz/mm
on a for the ignition mode, −12 MHz/mm on a and −14 MHz/mm on L for TE₀₁₁) and
landed within a megahertz on both modes. **The design is tunable by arithmetic
rather than by search** — which is the practical payoff of the orthogonality,
and something the ring architecture could not offer.

### The point

| | |
|---|---|
| TE₀₁₁ operating | **2.4741 GHz**, sector CV **0.0091**, clean m=0 |
| TM₀₂₀ ignition | **2.4245 GHz**, plasma-zone E **4.062%** |
| split | **−50 MHz** = 3.4 loaded linewidths |
| band margins | **+25.9 / +24.5 MHz** — balanced at both edges |
| worst case | +22.5 MHz cold, +14.1 MHz hot (100 K) with tolerance |

### Field and pressure, recomputed

🔢 Q assembled for this geometry: silver wall (electropolished) 37,800 in
parallel with dielectric 87,400 → **Q₀ = 26,400**. At β = 0.5:

| drive | bore field |
|---|---:|
| 1 kW CW | **8.13 kV/cm** |
| 10 kW pulsed | 25.7 kV/cm |

| margin | pressure at 1 kW |
|---|---:|
| 1× | 271 Torr |
| **2×** | **136 Torr (0.18 atm)** |
| 3× | 90 Torr |

> **The design is insensitive to the refinements that were supposed to threaten
> it.** Adding the intermediate tube and injector, redefining the integration
> region to the plasma zone, and retuning the cavity moved the 2× pressure
> requirement from 134 to **136 Torr** — 1.5%. The architecture is not balanced
> on a knife edge.

### Still open

1. **Order-2 confirmation** — running.
2. **Finite-conductivity walls.** Every Q here is still assembled by hand from a
   PEC solve plus an analytic wall term.
3. **Switchable coupler.** The 165× Q ratio between unloaded and plasma-loaded
   states admits no fixed match, and TE₀₁₁/TM₀₂₀ present orthogonal H at the
   wall so one loop cannot drive both. This is the driven model's job.
4. **N₂ breakdown curve** at 2.45 GHz, Λ = 0.35 cm, with an uncertainty band.
   Every margin above inherits its error.
5. **The sustaining threshold and the pressure ramp** — the bench question the
   whole scheme now rests on.

---

## 2026-08-14 — The order-1 sweeps are not mesh-converged

**The design point's absolute frequencies are wrong by roughly 20 MHz, and the
cause is mine.**

`geometry.py` sizes the mesh at **8 elements per wavelength**, described in the
harness as "coarse-ish; compensate with high-order FEM in Palace", and
`eigenmode.json` accordingly specifies **Order 2**. Every sweep in this session
defaulted to **Order 1**. The mesh was under-resolved for the solver actually
used.

### Measured

h-refinement at the design point, order 1, identical geometry and solver
settings — only the mesh size changes:

| mesh factor | elements | TE₀₁₁ | ignition | sector CV |
|---:|---|---:|---:|---:|
| 1.0000 | baseline | 2.4741 | 2.4245 | 0.0091 |
| 0.7275 | ~2.6× finer | **2.4939** | **2.4337** | 0.0040 |
| | **shift** | **+19.8 MHz (+0.80%)** | **+9.2 MHz** | |

🔢 Richardson extrapolation from these two points:

| assumed order | f_exact | beyond the fine mesh |
|---|---:|---:|
| h² (nominal for eigenvalues) | 2.5162 GHz | +22 MHz |
| h¹ | 2.5468 GHz | +53 MHz |

⚠️ Two-point Richardson with an assumed order is unreliable — a third mesh
(factor 0.60) is running to fit the order empirically. But both extrapolations
put TE₀₁₁ **outside the ISM band**, which is decisive enough to act on.

### What this invalidates

- **The specific geometry a = 101.43 mm, L = 85.48 mm.** Tuned against a mesh
  whose error (~20 MHz) exceeds the margins being optimised (~25 MHz).
- **The band-margin table and the PASS verdict** in the previous entry.

### What survives

Everything derived from **differences and ratios**, because systematic
discretisation error largely cancels in them:

- **Orthogonality of the handles** (−23 MHz/mm on a, −14 on L, ~0 cross-terms).
  These are derivatives; the mesh error is common-mode.
- **The brake's selectivity** (8:1) and the fact that it lifts the degeneracy.
- **The striker negative result** — a ratio of bore energies, and it measured
  ~1.00× on three geometries.
- **The pressure requirement, ~136 Torr.** η moved only 4.062% → 4.178%
  (+2.9%), so the field changes +1.4%.
- The mode-identification method and the architecture generally.

> **So the method is intact and the numbers are not.** The efficient repair is
> not to re-run everything at order 2 — that route failed to converge three
> times. It is to establish **one converged anchor**, then reuse the cheap
> order-1 sensitivities to retune onto it, and confirm once. That is the
> structure already in place; it was just anchored to an unconverged point.

### Note on the order-2 difficulty

Order 2 on this mesh has now failed to converge three times (N=20 wide,
N=10 targeted, N=6 at Tol 1e-6 reaching nconv=1 of 6 in 31 min). So "just run
order 2" is not available at sweep cadence. The practical anchor is more likely
**order 1 on a converged mesh** than order 2 on the coarse one.

### Resolved — converged design point

Three-mesh convergence study at a = 101.43, L = 85.48, order 1:

| h factor | TE₀₁₁ | Δ | ignition | Δ |
|---:|---:|---:|---:|---:|
| 1.0000 | 2.4741 | — | 2.4245 | — |
| 0.7275 | 2.4939 | +19.8 | 2.4337 | +9.2 |
| 0.6000 | 2.5002 | +6.3 | 2.4368 | +3.1 |

🔢 Fitted convergence order **p = 2.46** (TE₀₁₁) and **2.24** (ignition), both
near the h² theory for order-1 Nedelec eigenvalues — that agreement is the real
check, since a 3-point fit reproduces the third point by construction.

**Extrapolated:** TE₀₁₁ → 2.5106, ignition → 2.4425. So TE₀₁₁ sat **11 MHz
above the band** and only it needed moving; the ignition mode was always fine.

**The h = 0.60 mesh has a stable, measured offset: +10.4 MHz (TE₀₁₁), +5.7 MHz
(ignition).** That is the anchor. Order 1 cannot reach ~2 MHz accuracy at any
affordable mesh — it would need factor ~0.31, about 34× the baseline element
count — so a fine-but-affordable mesh plus a measured offset replaces both
brute force and the order-2 eigensolve that failed to converge three times.

### Retune, and a falsifiable prediction that held

Length is the near-pure handle on TE₀₁₁, so L 85.48 → **87.67 mm**.

Predicted at h = 0.60 **before running**: TE₀₁₁ 2.4696, ignition 2.4390.
Measured: **2.4704, 2.4377** — errors of **0.8 and 1.3 MHz**.

> **That is the load-bearing validation.** It confirms the coarse-mesh
> sensitivities transfer to the fine mesh, because systematic discretisation
> error is common-mode and cancels in derivatives. The cheap-sweep /
> expensive-anchor structure is therefore sound.

### The design point

| | |
|---|---|
| Cavity | **202.9 mm dia × 87.67 mm**, silver-plated 6061, electropolished |
| Brake / window | 3 mm fused quartz per end cap, 20 mm clear aperture |
| Torch | standard Fassel, unmodified |
| **TE₀₁₁ operating** | **2.4808 GHz**, sector CV **0.0021** |
| **TM₀₂₀ ignition** | **2.4434 GHz**, plasma-zone E 4.17% |
| split | **−37 MHz** = 2.5 loaded linewidths |
| band margins | +19.2 / +43.4 MHz; worst case +15.8 cold, +33.0 hot |
| Q₀ (ignition mode) | 26,563 (wall 38,194 ∥ dielectric 87,231) |
| bore field | **8.17 kV/cm at 1 kW** |
| ignition pressure | **136 Torr** for 2× margin, 91 Torr for 3× |

🔢 The pressure requirement is unchanged from the pre-convergence estimate
(136 Torr both times) — η moved only +2.7%, so the field is insensitive to the
discretisation error that displaced the frequencies.

---

## 2026-08-14 — Finite-conductivity solve abandoned; the perturbative Q stands

Two attempts to replace the hand-assembled Q with one Palace computes directly,
both at the converged design point (a = 101.43, L = 87.67, brake 3, h = 0.60):

| run | config | outcome |
|---|---|---|
| sigma_h060 | N=14, Target 2.0, Tol 1e-8 | 26 min, **no eigenvalues converged** |
| sigma_b | N=4, Target 2.46, Tol 1e-5 | 21 min, **no eigenvalues converged** |

Both wrote only an `eig.csv` header. **Finite conductivity makes the
eigenproblem complex / non-Hermitian**, and shift-invert Krylov handles that far
worse than the real-symmetric PEC case.

> **The pattern across this session is consistent and worth recording as a
> property of the setup, not a run of bad luck:**
>
> | formulation | outcome |
> |---|---|
> | order 1, PEC, real-symmetric | converges in ~5 min, every time |
> | order 2, PEC | failed 3× (N=20 wide, N=10 targeted, N=6 at Tol 1e-6 → nconv 1 of 6 in 31 min) |
> | order 1, finite conductivity | failed 2× |
>
> Keep the analysis on **order-1 PEC solves with perturbative corrections.**
> Reaching for the heavier formulation has cost roughly three hours this session
> and produced nothing.

### This is not a gap in the result

**Perturbative loss is the standard method for high-Q cavities**, not a
fallback: solve the lossless problem, then Q = ωU/P_loss with
P_loss = (R_s/2)∮|H_tan|²dS. It is accurate when R_s ≪ η, which holds
comfortably at Q ~ 26,000. The closed-form wall-Q expressions used here are the
textbook results for TE₀ₙₚ and TM₀ₙ₀ in a right circular cylinder.

So **Q₀ = 26,563 for the ignition mode stands** (wall 38,194 ∥ dielectric
87,231), and with it the 8.17 kV/cm bore field and the 136 Torr ignition
pressure.

⚠️ What remains unverified is the *arithmetic* of that assembly against an
independent solver — not the method. A cheaper future check would be Palace's
boundary postprocessing to obtain ∮|H|²dS from the existing PEC solve, which
needs no complex eigenproblem.

### Predictions left on the record, unfalsified

Stated before the runs, for whoever attempts this next:

| mode | wall Q | dielectric Q | combined |
|---|---:|---:|---:|
| TE₀₁₁ | 49,182 | 1,768,472 | **47,851** |
| TM₀₂₀ | 38,958 | 87,231 | **26,931** |

(The 26,931 differs from 26,563 only because it uses the 2.4434 GHz converged
frequency rather than the h=0.60 value — a 1.4% difference, immaterial.)

---

## 2026-08-14 — The coupler: orthogonality solves the Q mismatch

Two constraints looked like they compounded. They cancel.

1. **Q mismatch.** Unloaded 26,563 vs plasma-loaded ~165 — **161×**. Matching
   either leaves the other ~98% reflected. Accepting the mismatch gives
   0.13 kV/cm, which needs ~3900× more power to recover: dead.
2. **Mode orthogonality.** At the side wall TE₀₁₁ presents **H_z**, TM₀₂₀
   presents **H_φ**. One loop cannot link both.

> **Resolution: stop fighting constraint 2 and use it.** Two ports, each
> oriented and sized for its own mode. Because the modes are orthogonal, each
> port is automatically blind to the other — the ignition loop cannot spoil the
> operating Q, and the operating loop cannot waste power into TM₀₂₀. The 161×
> ratio is absorbed by making the ignition loop *small*, not by making any loop
> adjustable. **No switch, no tuner, no moving parts.**

### Loop sizing

🔢 Small-loop coupling, Q_ext = 2Z₀U/(ωμ₀²H²A²), with the analytic mode fields
normalised to U = 1 J:

| | TE₀₁₁ | TM₀₂₀ |
|---|---:|---:|
| field at wall | \|H_z\| = 24,317 A/m | \|H_φ\| = 22,301 A/m |
| target Q_ext | 165 | 26,563 |
| loop area | 204.1 mm² | 17.7 mm² |
| **single-loop dia** | **16.1 mm** | **4.7 mm** |
| **per loop, 4-fold feed** | **8.1 mm** | — |
| plane | r–φ (links axial H) | r–z (links azimuthal H) |

With the §4 four-fold symmetric feed, coupling adds coherently so each loop
takes area A_total/N — hence 8.1 mm rather than 16.1 mm.

🔢 Small-loop approximation valid: 16 mm against λ = 121 mm.

**The ignition loop's axial position is free.** TM₀₂₀ has p = 0, so H_φ is
uniform in z. The TE₀₁₁ loop by contrast must sit at mid-plane, where
H_z ∝ sin(πz/L) peaks.

### Caveats before building

- ⚠️ **Factor-of-2 conventions.** Q_ext formulas differ by 2–4× between texts
  depending on how port power is defined. Treat these as sizing estimates to be
  confirmed by a driven solve, not as final dimensions.
- ⚠️ **Ignition port symmetry is a choice.** TM₀₂₀ is m=0, so a symmetric feed
  avoids exciting m≠0. A single loop is simpler, and `ignition-study.md` notes
  breakdown does not need symmetry — but an asymmetric drive puts field
  elsewhere in the cavity too, and the cavity gas is at 1 atm while the bore is
  at 136 Torr, so parasitic breakdown outside the torch is unlikely but not
  impossible. Worth settling deliberately.
- ⚠️ Loop conductors must be sized for power separately, per
  `coupling-architecture.md` §0 — the DRA literature gives geometry at
  milliwatts, not kilowatts.

### Next: the driven solve

Verify Q_ext by driven analysis with a lumped port, sweeping S11 around each
mode. **This should converge where the eigensolves did not** — driven analysis
is a linear solve per frequency, not an eigenproblem, so it avoids the
shift-invert Krylov weakness that cost three hours this session.

The expensive part is resolving a 53 kHz linewidth; that is what adaptive
frequency sweeping exists for.

---

## OPEN RISK — the pressure ramp is not addressed by any of this

Recorded prominently because the entire reduced-pressure ignition route rests
on it and **no simulation in this programme can settle it.**

The scheme ignites at ~136 Torr and ramps to atmospheric while the microwave
sustains the discharge. Everything computed here is linear, time-harmonic and
plasma-free. The ramp is nonlinear and self-consistent — conductivity, density
and plasma shape all change with pressure and feed back on the fields.
`ignition-study.md` §3 already classes this as step 6, **"❌ Poorly"** simulable:
*"Nonlinear, needs validation data we don't have."*

The load-bearing assumption is §2's claim that the **sustaining threshold sits
far below the breakdown threshold**. Directionally certain — it is why MICAP can
light in argon and swap to nitrogen — but **unquantified for N₂**, and listed as
§9 q3.

**The plausible failure mode is tractable, though, and is not plasma physics.**
As pressure rises the discharge contracts and the cavity impedance swings. If it
swings faster than the amplifier can track, power delivery collapses and the
plasma dies. That is `ignition-study.md` §4.4 — reduced-order RLC, plasma as a
variable conductance, amplifier with a tracking loop — called there "the
highest-value simulation after eigenmode, and it needs no plasma physics."
**Not done.**

| ignition chain | status |
|---|---|
| high-E mode exists, m=0, in band | ✅ |
| field vs drive power | ✅ 8.17 kV/cm at 1 kW |
| breakdown threshold at 136 Torr | ⚠️ literature scaling; needs the N₂ curve |
| coupler delivers it | 🔄 in progress |
| **plasma survives 136 → 760 Torr** | ❌ **not addressed, not simulable** |
| amplifier tracks the impedance swing | ❌ tractable via §4.4, not done |

---

## 2026-08-14 — Driven model works, and the bare loop cannot match

### The driven solver converges where every eigensolve failed

**Sweep 2.40–2.55 GHz, adaptive ROM, complete in under 5 minutes.** The greedy
sampler converged 5.1e-1 → 9e-3 in five iterations. As predicted: driven
analysis is a linear solve per frequency, not an eigenproblem, so it avoids the
shift-invert weakness that cost ~3 hours today across five failed attempts.

**This is now the tool of choice for anything that can be posed as a driven
problem.**

### Three port-construction bugs, all silent or misleading

Recorded because none announced itself usefully:

1. **Face embedded parallel to the wire.** The gap is in a crossbar running
   along y, so the port must bridge along y. A face built in the z=0 plane lies
   parallel to the wire and bridges nothing. **No error** — S11 came back
   varying 0.036 dB over the whole sweep with no resonance.
2. **Face normal to the direction.** Correcting (1) by making a disc *normal*
   to +Y aborts: Palace requires `Direction` to lie **in** the port surface —
   the direction across the gap between conductors, not the surface normal.
3. **`embed()` refuses a face that touches anything.** But the face must touch
   both conductor ends to drive the loop. Fix: pass it as a **tool in
   `fragment()`** so it shares edges conformally instead.

Also: the resonance is narrower than the sweep step, so the first zoom-less run
reported a dip depth that was a **sampling artifact**. The ROM can be evaluated
at any resolution — re-sweep narrow rather than trusting a dip resolved by one
point.

### First measurement

Loop 12 × 17 mm (204 mm²), wire r = 1 mm, gap 0.3 mm, in the z=0 plane at the
wall linking H_z.

| | |
|---|---:|
| f₀ | 2.450980 GHz |
| \|S11\|min | −0.290 dB |
| Q_L | 14,320 (171 kHz linewidth) |
| β | 60 — overcoupled |
| **Q_ext measured** | **14,559** |
| Q_ext predicted (§ coupler entry) | 165 |

The loop pulls TE₀₁₁ down ~19 MHz from 2.4704 — a metal object in the cavity,
as expected.

### Why the analytic estimate was 88× optimistic

🔢 It omitted the **loop's own self-inductance**:

| | |
|---|---:|
| L (12×17 mm, r=1 mm) | 21.5 nH |
| reactance at 2.451 GHz | **332 Ω** |
| port impedance | 50 Ω |
| power factor \|Z₀/(Z₀+jX_L)\|² | 0.0222 |
| Q_ext inflation | **45×** |

165 × 45 = 7,427 against 14,559 measured — a residual 2.0×, which is the
convention ambiguity already flagged.

> **The loop is inductance-limited, not flux-limited.** At 2.45 GHz its own
> reactance is 6.6× the port impedance, so making it bigger raises flux *and*
> inductance and the gain is far less than A². **A bare loop cannot reach
> Q_ext = 165.** It needs series capacitance to tune out the inductance — a
> matching network, exactly as every ICP has.
>
> This does not break the two-port architecture. It adds a component to each
> port that was going to be needed anyway, and it is the reason real plasma
> sources have matching networks rather than bare loops.

### Next

1. **Add series capacitance** to the port model (Palace `LumpedPort` takes
   `C` alongside `R`) and re-measure Q_ext. This is the direct test.
2. Re-derive the loop sizing *with* the reactance term, replacing the
   flux-only estimate in the coupler entry above.
3. The ignition port (Q_ext = 26,563, weak coupling) is far less affected —
   its 4.7 mm loop has much lower inductance, and it wants weak coupling anyway.

### Measurement methodology — Re(Z) is ill-conditioned, use the linewidth

⚠️ **A correction to the previous entry's proposed criterion.** Extracting
Z = Z₀(1+Γ)/(1−Γ) at resonance is numerically unstable when |Γ| → 1, which is
exactly the regime of a lightly-loaded high-Q cavity (|Γ| ≈ 0.97 here). The
same 204 mm² loop returned:

| run | sampling | Re(Z) peak |
|---|---|---:|
| zoom | 10 kHz over 6 MHz | **16.7 Ω** |
| sweep | 20 kHz over 100 MHz | **3171 Ω** |

A 190× spread from sampling alone. **Re(Z) cannot carry a design decision here.**

**Q_L from the |S11| linewidth is robust** — it depends on the shape of the
resonance, not on inverting a near-unity reflection coefficient:

🔢 Q_L = 14,320 (171 kHz linewidth), and with Q₀ = 1.77 × 10⁶ from the
eigenmode solve, 1/Q_L = 1/Q₀ + 1/Q_ext gives **Q_ext = 14,437** for the
204 mm² loop. Against the target of 165, that is **87× too weak**, consistent
with the self-inductance analysis above.

⚠️ **Sweep windows must widen with loop size.** The loop is a substantial
perturbation: 816 mm² moved the resonance −6 MHz, and 1800 mm² pushed it below
the 2.40 GHz window edge entirely — that row reported f₀ = 2.40000, the window
boundary, and is invalid rather than informative.

### Where the coupler stands

- Driven model **works** and is the right tool.
- One loop measured properly: **Q_ext = 14,437 at 204 mm²**.
- The gap to Q_ext = 165 is real and is dominated by **loop self-reactance
  (332 Ω vs a 50 Ω port)**, not by insufficient area.
- **Series capacitance is therefore not optional.** Sizing the loop alone
  cannot close 87× while its own reactance grows with it.

**Next, in order:**
1. Re-run the loop-size sweep tracking **Q_L from linewidth**, with the window
   widened per size, to get the empirical Q_ext(A) scaling *including* the
   inductance penalty.
2. Add series C at the port and confirm Q_ext drops as predicted.
3. Only then re-derive loop dimensions.

### Loop-size sweep fails — and the failure is the finding

Four loop areas, two-stage sweep (coarse locate, then zoom), Q_ext from
linewidth:

| d × 2w (mm) | area | f₀ found | Q_ext |
|---|---:|---:|---:|
| 12 × 17 | 204 | 2.45098 | 14,442 |
| 20 × 28 | 560 | 2.37942 | 12,674 |
| 28 × 40 | 1120 | 2.42177 | 12,840 |
| 36 × 52 | 1872 | 2.31682 | 153,378 |

**f₀ is non-monotonic in loop area** (2.451, 2.379, 2.422, 2.317), which is the
tell: the coarse scan is locking onto *different features*, not tracking one
mode. Re-extracting with TE₀₁₁ identified by bore magnetic energy instead of
argmin|S11| did not rescue it — the bore-H peak and the |S11| dip disagree by
300 kHz, and bore-H falls to 0.7% at the largest loop against ~3.4% for a clean
TE₀₁₁.

> **The failure is informative. A loop large enough to matter stops being a
> perturbation and restructures the cavity.** At 1872 mm² the resonance has
> moved 134 MHz and the mode no longer looks like TE₀₁₁. So "grow the loop
> until Q_ext = 165" is **ill-posed** — the target mode does not survive the
> coupler needed to reach it.
>
> This strengthens rather than weakens the architecture: use a **small,
> non-perturbing loop plus a matching network**, which is how real plasma
> couplers are built, rather than a large loop sized for direct match.

Note also Q_ext barely moves from 204 → 1120 mm² (14,442 → 12,674 → 12,840)
against the 5.5× reduction flux-only scaling would predict — consistent with
the loop being reactance-limited rather than flux-limited.

### The decisive test, and why it is a circuit question

🔢 With the reactance cancelled, Q_ext should fall by 1 + (X_L/Z₀)² =
1 + (332/50)² = **45×**, giving 14,442 → **~320**. Target is 165, so the
residual ~2× is a modest loop enlargement or transformer — well inside the
non-perturbing regime.

Palace's schema does not state whether `LumpedPort` R/L/C combine in series or
parallel, and it matters: parallel C across 50 Ω would barely move anything.
🔢 C = 1/(ω²L) = **0.196 pF**. **Series predicts 45×, parallel predicts ~1×** —
one run decides it.

### Palace's LumpedPort R/L/C are PARALLEL — series matching is not modellable there

Test: 204 mm² loop, C = 0.196 pF added at the port.

| | without C | with C | ratio |
|---|---:|---:|---:|
| Q_ext | 14,442 | 16,860 | **0.9×** |

Series would have given 45×. **Parallel gives ~1×, which is what we see** —
331 Ω across a 50 Ω port changes almost nothing. The schema does not state the
combination; this run establishes it.

⚠️ **So `LumpedPort` C cannot represent a series matching capacitor.** In the
circuit the port sees, the loop inductance is in series with
(R_port ∥ C_gap) — the port surface spans the gap, so the port and the gap
capacitance are in *parallel* with each other. A series element needs a
**second gap in the loop, without a port** — a geometric capacitor.

**The analytic result stands regardless.** Cancelling 332 Ω of series reactance
against a 50 Ω port raises loop current ~6.6× and coupled power ~45×; that is
Ohm's law, not a modelling artefact. Simulation would confirm arithmetic we are
already confident in, and the second-order questions it *could* settle (does
flux linkage change with the series C — it should not, being geometric) do not
gate the design.

### Coupler design, as far as simulation takes it

| | |
|---|---|
| Loop | **12 × 17 mm** (204 mm²), wire r = 1 mm, in the r–φ plane at mid-plane |
| Measured Q_ext, bare | **14,442** |
| Loop inductance | 21.5 nH → **332 Ω** at 2.45 GHz |
| Series C to cancel | **0.196 pF** — realise as a second gap in the loop, ~0.14 mm at r = 1 mm |
| Q_ext after cancellation | **~320** |
| Residual to target 165 | ~2×, i.e. loop area × 1.41 → ~288 mm² (14 × 20.5 mm), or a transformer |

**The loop stays small and non-perturbing throughout** — 288 mm² is well inside
the regime where TE₀₁₁ survives, unlike the 1872 mm² loop that moved the
resonance 134 MHz and destroyed the mode.

⚠️ The residual 2× is the same convention ambiguity flagged before any of these
runs; it has never been resolved and sits between the analytic Q_ext formula and
Palace's port definition. It does not change the design — a 1.41× area factor is
within adjustment range — but it should be pinned down before dimensions go to a
machinist.

**The ignition port is easier and needs no matching**: it wants Q_ext = 26,563,
i.e. *weak* coupling, which a bare 4.7 mm loop overshoots in the helpful
direction. Its inductance is far lower and its reactance penalty correspondingly
smaller.

---

## 2026-08-14 — Ring field measured, and both incumbents ignite on argon

### The ring/AMIP comparison is now measured, not inferred

Same energy-normalisation method applied to the ring's order-2 verified
geometry (`experiments/ignition/postpro/cand_o2`, D=80 mm enclosure, ring scale
0.94):

| | alumina ring | AMIP |
|---|---:|---:|
| ignition mode | TM₀₁₀-like, 2.4563 GHz | TM₀₂₀, 2.4434 GHz |
| bore E fraction | **11.63%** | 4.17% |
| Q wall ∥ dielectric | 26,847 ∥ 44,655 = **16,767** | 38,194 ∥ 87,231 = **26,563** |
| **bore field at 1 kW** | **7.88 kV/cm** | **8.17 kV/cm** |
| 2× margin pressure | **131 Torr** | 136 Torr |
| margin at 1 atm | 0.35× | 0.36× |

🔢 **Ratio 0.965 — within 3.5%.** The ring concentrates field far better (11.6%
vs 4.2% of E in the bore) but carries lower Q (16,767 vs 26,563), and the two
cancel. This is the same cancellation as Q × η, now confirmed on the quantity
that actually matters for ignition rather than a proxy.

**Reduced-pressure ignition is architecture-independent.** It was inferred in
`coupling-architecture.md` §0; it is now measured.

### Neither incumbent ignites nitrogen electronically ✅

🔢 The calculation says both architectures sit at **~0.35× of the atmospheric
breakdown threshold at 1 kW**, and would need **~8 kW** for bare parity. That is
a falsifiable prediction about the commercial art. It holds:

| instrument | ignition |
|---|---|
| **MICAP** (Radom) | 8 s of argon **plus a spark**, then transition to N₂ |
| **MP-AES** (Agilent 4100/4200/4210) | **argon for ignition only** — onboard bottle or external supply, welding grade 99.0%, 1.5 L/min — then automatic switch to N₂ |

⚠️ Whether MP-AES also uses a spark is not established; the sources confirm the
argon flow and the automatic changeover, not the initiating mechanism.

> **Both commercial nitrogen microwave plasmas carry an argon cylinder purely to
> start.** Neither achieves all-electronic N₂ breakdown at atmospheric pressure —
> exactly as the field calculation predicts, and for the reason
> `ignition-study.md` §2 gives: N₂ is molecular, so vibrational and rotational
> channels drain electron energy before ionisation, and the sustaining threshold
> sits far below the breakdown threshold.

**This is the strongest external check the ignition analysis has received.** An
independent prediction — that ~8 kW would be needed at 1 atm — is corroborated by
two vendors independently choosing to ship an argon bottle instead.

**And it raises the value of the reduced-pressure route.** If ignition at
~131–136 Torr works, it deletes the argon cylinder from *both* incumbent
designs, not just from MICAP. `patent-landscape.md` §4 already noted ignition is
"not a solved problem in the commercial art — which makes it open ground rather
than a constraint." That now reads as an understatement.

⚠️ The pressure ramp remains unquantified (see the standing risk above). The
incumbents' argon route sidesteps it entirely by never leaving atmospheric —
which is a real advantage of theirs that the reduced-pressure route must beat,
not merely match.

---

## 2026-08-14 — Silver-wall Q measured at last, via driven + conductivity

**The finite-conductivity measurement abandoned earlier was never impossible —
it was attempted with the wrong solver.** The *eigen*solve is complex and
non-Hermitian and never converged (2 attempts, 26 and 21 min, zero eigenvalues).
**Driven analysis takes the same Conductivity boundary and converges fine**,
because it is a linear solve per frequency. That tool had been working for hours
before this was retried.

### Method — energy balance, not S-parameters

Q₀ = ωU / P_abs, with U from `domain-E.csv` and P_abs = P_inc(1 − |Γ|²).
**No β, no over/undercoupled branch, no convention factor** — which matters,
because every Q_ext figure in this file carries an unresolved ~2× ambiguity.

⚠️ First attempt used P = ½Re(V·I*) from the port files and was **wrong** —
Palace's V/I conventions are not simply total-into-load. Caught only by the
cross-check below.

✅ **Cross-check:** the PEC run returns **2.00 × 10⁶** against the eigenmode's
dielectric-only **1.77 × 10⁶** — 13%. The method is sound.

### Result

| walls | \|Γ\| at f₀ | U | P_abs | **Q₀** |
|---|---:|---:|---:|---:|
| PEC | 0.9676 | 4.14e-6 J | 0.032 W | 2,000,931 |
| **silver, 6.3e7 S/m** | **0.4641** | 2.30e-6 J | 0.392 W | **90,323** |

Note the match improves dramatically once the walls absorb: |S11| goes
−0.289 → **−6.667 dB**.

⚠️ **90,323 is 1.9× the perturbative estimate of 47,851**, and the discrepancy
is **unexplained**. Implied wall Q ~95,000 against the closed-form 49,182.
Candidates: the closed-form assumes an empty right cylinder, while this geometry
carries the brake, torch and loop. Not resolved.

### What it would mean, if it carries to the ignition mode

🔢 Field ∝ √Q, so 1.9× in Q is **1.37× in field**: bore field 8.17 → ~11.2 kV/cm
at 1 kW, and 2× ignition margin moves **136 → ~190 Torr**. A materially gentler
vacuum.

⚠️ **Not established.** This is TE₀₁₁; the ignition mode is TM₀₂₀, a different
field distribution against the same walls. The correction may or may not
transfer, and the perturbative TM₀₂₀ number (Q₀ = 26,563) should be re-measured
the same way before any pressure figure is revised.

**Until then the 136 Torr requirement stands** — it is the conservative number.

### Radial viewport is nearly free — a claim of mine, falsified

I had argued AMIP was constrained to axial viewing because TE₀₁₁'s side-wall
current is azimuthal, so a round viewport would "cut it, radiate, and spoil Q".
**Measured with driven + conductivity:**

| viewport | cutoff | Q₀ | ΔQ | Δf |
|---|---:|---:|---:|---:|
| none | — | 90,323 | — | — |
| 15 mm | 11.7 GHz | 90,264 | −0.1% | +0.7 MHz |
| 25 mm | 7.0 GHz | 89,518 | **−0.9%** | +1.9 MHz |
| 35 mm | 5.0 GHz | 88,091 | −2.5% | −0.4 MHz |

Wrong twice: a 25 mm bore is **2.9× below cutoff** so it does not radiate, and a
round hole is not a circumferential slot — local current detour, not a blocked
path. **"Cuts current" and "spoils Q" are not the same claim.**

**Consequence:** radial viewing is available, so the brake need not double as the
viewport. That keeps the window out of the exhaust stream and gives the more
matrix-robust geometry.

⚠️ Measured on TE₀₁₁. **TM₀₂₀ carries axial wall current**, which a round hole
interrupts differently — the viewport's effect on the ignition mode is not
measured.

⚠️ **Fourth selection bug of the session.** The first analysis compared stored
energy against Q in a tuple index (`U > best[1]` where `best[1]` was Q), so it
returned the first sample and reported a 75% Q penalty. Caught because both
"resonances" landed exactly on their sweep's lower edge. The recurring failure is
not arithmetic — it is **selection criteria that are subtly wrong and produce
plausible numbers.**

---

## RECHECK QUEUE — opened by the driven solver working

The driven + conductivity + energy-balance method (§14) is better than what
several earlier results were established with. It converges where eigensolves
fail, and **Q₀ = ωU/P_abs carries no β, no coupling branch and no convention
factor** — the ~2× ambiguity that has qualified every Q_ext figure in this file.

Ordered by how much the answer would move.

| # | recheck | why it matters | status |
|---|---|---|---|
| ~~R1~~ 🔴 | ~~TM₀₂₀ Q via driven + conductivity~~ **DONE — 46,339, 180 Torr** | Perturbative Q₀ = 26,563 sets the **8.17 kV/cm** field and the **136 Torr** requirement. TE₀₁₁'s perturbative value proved **1.9× low**. If TM₀₂₀ is similarly off, field ×1.37 and pressure relaxes to **~190 Torr** | ✅ **closed — 127 Torr** |
| ~~R2~~ 🔴 | **Diagnose the 1.9×** between closed-form wall Q (49,182) and measured (~95,000) | Every perturbative Q in this file inherits it. Candidates: closed form assumes an empty right cylinder; ours has brake, torch and loop | 🔴 **closed, verdict INVERTED (R5)** |
| ~~R3~~ ✅ | **Order-2 via driven** | Order-2 *eigen*solves failed 3×. Driven is a linear solve — it may converge, finally settling discretisation instead of relying on the +10.4 MHz extrapolation | ✅ **closed** |
| ~~R4~~ 🔴 | **Q_ext by energy balance** | Would pin the 2× convention factor that qualifies the whole coupler section | 🔴 **closed, Q_ext 16,361 (R5)** |
| ~~R5~~ ✅ | **Ring Q and field re-measured** | 7.88 kV/cm is perturbative, same closed-form family. Ratio to AMIP may survive even if both move | ✅ **closed — found the 2× bug** |
| ~~R6~~ ✅ | **Viewport effect on TM₀₂₀** | Measured on TE₀₁₁ only. TM₀₂₀ carries *axial* wall current, which a round hole interrupts differently | ✅ **closed** |

**R1 needs a port that couples to TM₀₂₀**, and the TE₀₁₁ loop cannot — they are
orthogonal at the wall. A **45° tilted loop couples to both at −3 dB each**, so
one geometry and one sweep spanning 2.42–2.49 GHz yields both resonances and
both Q values by energy balance. That is the efficient route and it also serves
R4 and R6.

⚠️ **Until R1 lands, 136 Torr stands.** It is the conservative figure.

---

## 2026-08-14 — R1 answered: ignition pressure relaxes to 180 Torr

A **45° tilted loop** couples to both modes at −3 dB each, so one driven +
conductivity sweep (2.40–2.50 GHz, 20 kHz) yields both resonances and both Q
values by energy balance.

### Cross-check first

| TE₀₁₁ Q₀ | geometry |
|---:|---|
| 90,323 | planar loop, Direction +Y |
| 91,281 | 45° tilted loop, Direction [0, 0.707, 0.707] |

🔢 **1.1% apart** on different geometries with different port orientation. The
method is reproducible, which is what licenses the rest of this.

### R1 — TM₀₂₀

| | perturbative | **measured** | ratio |
|---|---:|---:|---:|
| Q₀ | 26,563 | **46,339** | **1.74×** |
| bore field @1 kW | 8.17 kV/cm | **10.79 kV/cm** | 1.32× |

| margin | pressure at 1 kW | was |
|---|---:|---:|
| 1× | 360 Torr | 272 |
| **2×** | **180 Torr (0.24 atm)** | **136** |
| 3× | 120 Torr | 91 |

**The design figure moves 136 → 180 Torr.** A third more pressure, i.e. a
correspondingly easier vacuum system.

⚠️ The measured Q includes the loop, whose surface is silver and therefore lossy
in this model. So 46,339 **understates** the bare-cavity Q — the correction is
conservative.

### Atmospheric, revisited

| drive | field | margin at 1 atm |
|---|---:|---:|
| 1 kW | 10.8 kV/cm | 0.47× |
| 5 kW | 24.1 | 1.06× |
| **10 kW pulsed** | **34.1** | **1.50×** |
| 20 kW | 48.3 | 2.12× |

🔢 2× margin at atmospheric now needs **18 kW**, down from 56. Still not sane
power — the reduced-pressure route stands — but **the gap is no longer an order
of magnitude**, and a pulse-overdrive-only path is no longer absurd.

### R2 — partly answered

The perturbative underestimate is **1.89× on TE₀₁₁ and 1.74× on TM₀₂₀** —
similar magnitude, two modes, different field distributions.

> **So the error is in the closed-form wall-Q expressions themselves, not in the
> geometry or a particular mode.** Every perturbative Q in this file inherits it,
> including the ring's 7.88 kV/cm (R5). The driven measurement supersedes them
> where it exists.

⚠️ The root cause is still not identified — only localised to the formula family
rather than the model. Do not use the closed forms for anything load-bearing.

### R4 answered — Q_ext without the convention factor

Q₀ from energy balance is convention-free; Q_L from linewidth; then
1/Q_L = 1/Q₀ + 1/Q_ext.

| | value |
|---|---:|
| Q₀ (energy balance) | 90,323 |
| Q_L (linewidth) | 12,010 |
| **Q_ext** | **13,852** |
| previously, via PEC run + assumed Q₀ | 14,442 (4% apart) |
| analytic, self-inductance corrected | 7,427 |
| **residual** | **1.87×** |

🔢 **The residual is the same magnitude as the wall-Q errors** — 1.89× on
TE₀₁₁, 1.74× on TM₀₂₀, 1.87× here. Three different closed-form expressions,
all low by ~1.8×.

⚠️ A shared cause, not three coincidences — but **not identified**. It is not a
field-normalisation error: the closed-form Q expressions are ratios in which any
normalisation cancels. Treat all closed forms as indicative only; the driven
measurement supersedes them wherever it exists.

---

## 2026-08-14 — R2 and R6 answered; R3 mis-sampled

### R2 ✅ — the fault is in my closed forms, not the model

Palace's Conductivity BC tested by scaling σ ×4. Theory: Q_wall ∝ √σ, so it
should double.

| σ | Q₀ | implied Q_wall | ratio |
|---|---:|---:|---:|
| 6.3e7 (silver) | 90,323 | 95,184 | — |
| 2.52e8 (4×) | 172,906 | 191,644 | **2.01×** |

🔢 **2.01× against a theoretical 2.00×.** The boundary condition is exactly
right. **So the ~1.8× discrepancy is definitively in my closed-form
expressions**, not in Palace, not in the mesh, not in σ.

> **All three closed forms — TE₀₁₁ wall Q, TM₀₂₀ wall Q, and small-loop Q_ext —
> are low by 1.74–1.89×. The model is sound; the hand analysis is not.** Do not
> use the closed forms for anything load-bearing. Measure instead: driven +
> conductivity + energy balance costs ~100 s.

⚠️ The root cause within the formulas is still unidentified. It is not
normalisation (Q expressions are ratios in which normalisation cancels) and not
the BC (this test). Most likely an error in how I evaluated them.

### R6 ✅ — the viewport is free for the ignition mode too

25 mm radial viewport, measured on the tilted-loop geometry that drives both:

| mode | f₀ | Q₀ | ΔQ | Δf |
|---|---:|---:|---:|---:|
| TM₀₂₀ | 2.41644 | 45,946 | **−0.8%** | −7.2 MHz |
| TE₀₁₁ | 2.44768 | 90,088 | **−1.3%** | −1.5 MHz |

**Radial viewing costs ~1% of Q on both modes.** The earlier result was TE₀₁₁
only; TM₀₂₀ carries *axial* wall current and might have behaved differently. It
does not. ⚠️ The −7.2 MHz shift on TM₀₂₀ is retunable but must be designed in.

### R3 ⚠️ — order-2 driven converged, but I sampled the wrong band

The solve **completed in 1532 s** — order 2 *is* reachable by driven analysis,
where eigensolves failed 3×. But it found no resonance: |S11| flat at −0.01 dB
across 2.44–2.47, stored energy varying only 3×, maximum on the **upper window
edge**.

**Order 2 is more accurate than order 1 on the same mesh, and refinement raises
the frequency** — the same direction the h-study showed. The window was centred
on the order-1 answer, so the mode moved out the top. Re-running at 2.46–2.54.

⚠️ **The extractor reported a peak anyway.** `dq.peaks()` now requires
max(U)/min(U) ≥ 10 — a real resonance raises stored energy by orders of
magnitude, so low contrast means no resonance in band and any "peak" is noise or
a window edge. Fifth selection-criterion failure of this project; the guard is
now in the shared module rather than in one caller.

### R3 ✅ — order 2 reached by driven, and it validates the extrapolation

Re-run at 2.46–2.54 GHz found the mode immediately:

| | f₀ | Q₀ |
|---|---:|---:|
| order 1 | 2.45095 | 90,323 |
| **order 2** | **2.48168** | **90,845** |
| Δ | **+30.7 MHz** | **+0.6%** |

**Two answers, and the second was not the question asked.**

**1. Driven analysis reaches order 2.** Two runs, 1532 s and this one, against
**five failed eigensolves**. ✅ The rule generalises: *pose the question as a
linear solve wherever possible.* Eigenproblems fail on this geometry; driven
solves do not.

**2. 🔑 It independently confirms the discretisation treatment.** +30.7 MHz
looks at first to contradict the **+10.4 MHz** design offset — but that offset
belongs to the **h = 0.60** mesh, and the driven runs use the baseline mesh
(`ls12x17.msh` 16.0 MB vs `h060.msh` 62.8 MB, 3.9× coarser). The Richardson fit
already predicts the baseline error:

| h | order-1 f | error vs extrapolated 2.5106 |
|---:|---:|---:|
| 1.00 (baseline) | 2.4741 | **+36.5 MHz** |
| 0.7275 | 2.4939 | +16.7 |
| 0.60 (design anchor) | 2.5002 | **+10.4 MHz** |

🔢 **Richardson extrapolation over three order-1 meshes predicts 36.5 MHz of
error at the baseline mesh. A single direct order-2 solve measures 30.7 MHz —
84% of it**, the remainder being that order 2 is not itself exact at 8
elements/wavelength.

> ✅ **Two methods that share no assumptions agree.** Richardson assumes a
> convergence power law and fits it; the order-2 solve assumes nothing and just
> resolves the field better. **The +10.4 MHz offset the design point rests on is
> corroborated, and the design point stands.** This was the last structural
> doubt left by §9.

**3. ⚠️ The result nobody asked for, and the most useful one: Q is nearly
order-independent.** Frequency moved 30.7 MHz — 12,000 ppm — while **Q₀ moved
0.6%**. Q is a ratio of energies over the same field; systematic discretisation
error is common-mode and largely cancels, exactly as it does in the sensitivity
derivatives §9 relied on.

> **So every order-1 Q in this file was never at risk from the §9 mesh error,
> even while every order-1 frequency was.** The ignition margin, the Q × η
> figure of merit, and the 180 Torr result inherit no error from it. Frequencies
> needed the offset; Q never did.

⚠️ Untested whether this extends to the *loaded* Q with a plasma present.

**Loop perturbation, for the record:** the 204 mm² loop appears to raise f₀ by
~+6.7 MHz (mesh-scaled estimate, ⚠️ not directly measured — a no-loop solve on
`ls12x17` would settle it). Direction is right by Slater's theorem: the loop
sits where H is large. Too small to affect the conclusions above.

| 17 | **R3 answered — the design point is corroborated** | Order 2 via driven: f +30.7 MHz (Richardson predicted 36.5), **Q +0.6%**. Two independent methods agree; **Q is order-independent, so no order-1 Q was ever at risk** |

---

## 2026-08-14 — 🔴 R5 found a factor-of-2 error in every measured Q

**R5 set out to measure the ring's Q. It found a bug in the instrument instead.**
The validation run — the one added only to check the method on a geometry whose
answer is already known — returned **22,161 against a known 11,084. Exactly
1.999×.** A factor of exactly 2 is a convention error, not physics.

### Established three independent ways, none of them `dq.py`

| route | Q_dielectric |
|---|---:|
| Palace's own eigenmode (imaginary part of the eigenvalue) | 11,054 |
| Analytic: 1/(p_e·tanδ), p_e = 0.888 + 0.014 | 11,083 |
| **Linewidth + Γ, using no energy at all**: Q_L(1+β), β=(1+\|Γ\|)/(1−\|Γ\|)=4.106 | **11,085** |
| `dq.py` energy balance | ⚠️ **22,161** |

🔢 The third route is the decisive one: **Q_L = 2,171 from linewidth and
β = 4.106 from the reflection coefficient give 2,171 × 5.106 = 11,085 using only
frequencies and a ratio** — no energy, no power, no convention. Three agree;
`dq.py` is alone and high by 2.00×.

### The cause

Palace reports `E_elec` = ½∫ε|E|²dV, which is **twice** the time-averaged
electric energy — and likewise `E_mag`. At resonance the two are equal (measured
ratio 1.0001), so **`E_elec + E_mag` double-counts the stored energy**.

`P_inc` was never the problem: V_inc/I_inc = **50.000 Ω exactly** against a 50 Ω
port, P_inc = 0.5 W. Textbook peak-amplitude convention, correct as written.

**Fix:** `U = (E_elec + E_mag)/2`. Recomputed, the ring returns **11,081**
against the known 11,084 — 0.03%.

### ⚠️ What this overturns

**Every driven-derived absolute Q in this file was 2× too high.**

| | was | **corrected** |
|---|---:|---:|
| TE₀₁₁ Q₀ (sigdrv) | 90,323 | **45,162** |
| TE₀₁₁ Q₀ (order 2) | 90,845 | **45,422** |
| TM₀₂₀ Q₀ (tilt45) | 46,339 | **23,170** |
| TE₀₁₁ Q_wall implied | 95,184 | **47,592** |
| R2 4×σ Q₀ | 172,906 | 86,453 |
| Q_ext (Q_L is linewidth-derived, unaffected) | 13,852 | **16,361** |

**🔴 R2's headline verdict is INVERTED. The closed forms were right.**

| | closed form | corrected measurement | ratio |
|---|---:|---:|---:|
| TE₀₁₁ wall Q | 49,182 | 47,592 | **1.03×** |
| TM₀₂₀ wall Q | 26,563 | 23,170 | **1.15×** |

> R2 recorded *"all three closed forms are low by 1.74–1.89×; the model is sound,
> the hand analysis is not."* **That is exactly backwards.** The closed forms
> agree to 3% and 15%. The fault was in `dq.py` all along. ⚠️ Strike the
> instruction not to use them.
>
> **R2's own test was still valid and is untouched** — σ×4 gave a Q_wall ratio of
> 2.01× against a theoretical 2.00×. It was a *ratio* test, and ratios are immune
> to a constant factor. It correctly proved Palace's BC exact. What was wrong was
> the *inference* that the residual discrepancy therefore lay in the closed
> forms. It lay in the tool doing the comparing, which the test could not see.

### 🔴 The ignition margin gets worse

Field scales as √Q, so a 2× Q error is a 1.41× field error.

| | was | **corrected** |
|---|---:|---:|
| TM₀₂₀ bore field @1 kW | 10.79 kV/cm | **7.63 kV/cm** |
| 1× margin | 360 Torr | 254 Torr |
| **2× margin — the design figure** | **180 Torr** | **🔴 127 Torr** |
| 3× margin | 120 Torr | 85 Torr |

**The design figure moves 180 → 127 Torr — worse than the 136 Torr it started
at.** The vacuum system is harder than currently documented, not easier. R1's
"a third more pressure, i.e. a correspondingly easier vacuum system" is
withdrawn.

### R5's actual answer, and it is not what was recorded either

| ring | was (closed form) | **measured** |
|---|---:|---:|
| Q_wall | 26,847 | **103,586** (3.86× higher) |
| Q_dielectric | 44,655 | **11,081** (4.03× lower) |
| **Q₀ total** | **16,767** | **10,011** |
| bore field @1 kW | 7.88 kV/cm | **6.09 kV/cm** |

🔢 Closure check: 103,586 ∥ 11,081 = 10,010 against 10,011 measured — **1.000×**.

⚠️ **Both halves of the old 16,767 were wrong, in opposite directions, and
partially cancelled.** The wall closed form was 3.9× low because a dielectric
resonator confines its field near the ring, so the enclosure wall sees weak
fields — a plain-cavity formula badly overestimates wall loss. The dielectric
closed form was 4× high. Two large errors cancelling to a plausible-looking
number is the hardest kind to catch, and only an independent measurement did.

⚠️ The ring's Q is dominated by its dielectric loss, and **alumina tanδ = 1×10⁻⁴
is a PLACEHOLDER** (`ignition-study.md` §9 q1). The ring's Q₀ and field are
hostage to it; AMIP's are not, being wall-dominated.

### ✅ The comparative claim survives

**AMIP 7.63 kV/cm vs ring 6.09 = 1.25×** (was 10.79/7.88 = 1.37×). Both figures
fell, AMIP's by more, and AMIP still leads. **The architecture argument does not
depend on the bug.** Only the absolute ignition pressure does — and that got
worse.

### 🔑 What this says about method

**The 2× was already suspected, and the check meant to settle it inherited it.**
§12 records *"the ~2× ambiguity that has qualified every Q_ext figure in this
file"*, and R4 was scoped as *"Q_ext by energy balance — would pin the 2×
convention factor."* R4 ran through `dq.py` and confirmed the wrong branch. ⚠️ **A
measurement cannot audit a bug it is built on.** R4's answer is now
16,361, not 13,852.

> **What actually caught it was validating against a geometry whose answer was
> already known independently.** That run was optional — the wall number was the
> deliverable — and it was the only thing standing between this error and the
> design record. Sixth selection/convention failure in this project. ✅ **Every
> future measurement harness gets a known-answer case before its results are
> believed.**

⚠️ The three-way agreement was available from the start: the ring's Q was in the
eigenmode record all along. Nothing new had to be computed to catch this — only
compared.

| 18 | 🔴 **R5 — factor-of-2 in every measured Q** | `dq.py` summed E_elec+E_mag, double-counting. **All driven Q halve.** Closed forms were RIGHT (1.03×, 1.15×) — R2 inverted. **Ignition 180 → 127 Torr.** Ring Q₀ 10,011, field 6.09. AMIP still leads 1.25× |

---

## 2026-08-14 — audit of everything downstream of `dq.py`

### 1. Code — the bug was confined to one file

`E_elec`/`E_mag` are read by nine scripts. **Only `dq.py` used them as an
absolute stored energy.** Everywhere else they are *ratios*, in which the factor
of 2 cancels identically:

| file | use | affected? |
|---|---|---|
| `reextract.py`, `sweep-encl.py`, `sweep2d.py`, `analyse.py` (both) | bore E/H for mode ID | ❌ ratio |
| `brake-sweep.py`, `tune-sweep.py`, `confirm.py` | per-sector CV (σ/mean) | ❌ ratio |
| `queue.py`, `r5.py` | import `dq` | ✅ fixed at source |
| `reextract-loop.py` | Q_ext from linewidth, Q₀ hardcoded | ⚠️ 0.6%, immaterial |

✅ **No second copy of the arithmetic exists.** Consolidating extraction into one
module — done for convenience — is why one edit fixed everything.

### 2. 🔑 Independent validation across every driven run

Q₀ re-derived by a route sharing **nothing** with energy balance: Q_L from the
FWHM of the stored-energy Lorentzian (frequencies only) and β from |Γ|.

| run | mode | Q₀ energy | Q₀ convention-free | branch | agree |
|---|---|---:|---:|---|---:|
| drv_zoom | TE₀₁₁ | 1,000,465 | 1,001,653 | over | 1.00 |
| sigdrv | TE₀₁₁ | 45,161 | 45,244 | over | 1.00 |
| sig4x | TE₀₁₁ | 86,453 | 86,559 | over | 1.00 |
| tilt45 | **TM₀₂₀** | 23,169 | 22,525 | **under** | 0.97 |
| tilt45 | TE₀₁₁ | 45,640 | 46,685 | over | 1.02 |
| tiltvp | **TM₀₂₀** | 22,973 | 22,571 | **under** | 0.98 |
| o2drv2 | TE₀₁₁ | 45,422 | 45,404 | over | 1.00 |
| vp15/25/35 | TE₀₁₁ | 45,132/44,759/44,045 | 45,296/44,873/44,125 | over | 1.00 |

🔢 **12 modes. Mean 1.000×, worst 0.972×.** The corrected extractor is confirmed
against an independent method on every driven result in the project.

⚠️ **A coupling-branch trap surfaced doing this.** |Γ| alone cannot tell
over- from under-coupling — β is either (1+|Γ|)/(1−|Γ|) or its reciprocal, and
the two differ by up to 1.8× here. **TM₀₂₀ is undercoupled, TE₀₁₁ overcoupled**,
which is physical: the loop is oriented for TE₀₁₁. Forcing one branch on
everything produced two spurious 1.5–1.8× disagreements.

> The two methods are **complementary, not redundant**: energy balance had a
> convention risk and no branch ambiguity; linewidth+Γ has a branch ambiguity and
> no convention risk. Neither alone is trustworthy. Together they are decisive.

### 3. 🔴 The ORIGINAL PEC validation was a false positive

§14 recorded: *"the PEC run returns 2.00 × 10⁶ against the eigenmode's
dielectric-only 1.77 × 10⁶ — 13%. The method is sound."* **It was not sound, and
that check could never have shown it.**

🔢 At Q ≈ 10⁶ the linewidth is **2.45 kHz against a 10–20 kHz sweep step** — the
resonance is 4–8× narrower than the sample spacing. The PEC run is
fundamentally under-resolved and is not a valid absolute reference in either
version. The old 13% agreement was **two errors landing near each other**: a 2×
inflation against a mismatched reference.

| Q | linewidth | samples across FWHM |
|---:|---:|---|
| 1,000,000 | 2.45 kHz | ⚠️ **0.1–0.2 — unresolvable** |
| 45,162 | 54 kHz | 3–5, marginal |
| 23,170 | 106 kHz | 5–10 |
| **10,011 (ring)** | **245 kHz** | ✅ **12–24, well resolved** |

> **The ring was the best-conditioned case available, and that is why it caught
> what the PEC run could not.** |S11| = −4.32 dB there gives 1−|Γ|² = 0.63; the
> PEC run's −0.29 dB gives 0.064, amplifying any S11 error **50× more**. ✅ Choose
> the validation case for conditioning, not convenience — a known answer measured
> in an ill-conditioned regime proves nothing.

### 4. What changed, what did not

**Changed:** Q_ext (R4) **13,852 → ~16,500** (Q_L measured 12,122, unaffected;
Q₀ halved). ⚠️ The coupler conclusion is untouched — still ~100× from the
Q_ext = 165 target, so *"growing the loop is ill-posed"* stands.

**Unaffected, verified rather than assumed:**
- ✅ All **eigenmode** Q (Palace's own eigenvalue) — never went through `dq.py`.
- ✅ **Sector CV 0.0021**, all mode identifications, the brake sweep, the tuning
  sensitivities — ratios throughout.
- ✅ **Viewport ΔQ** (−0.1/−0.9/−2.5%) and **order-2 ΔQ** (+0.6%) — ratios.
- ✅ **R2's σ-scaling 2.01×** — a ratio, and still correct.
- ✅ **Loop-size study** — Q_ext ≈ Q_L since Q₀ ≫ Q_L; 0.6% shift.
- ✅ **The +30.7 MHz order-2 result and the design point** — frequencies, not Q.

### 5. ✅ Q × η survives, and is now measured on both sides

The central claim of `axisymmetric-feed.md` §6 drew on an eigenmode Q for the
ring and a closed form for the cavity — **neither from `dq.py`, so the bug never
touched it.** Both sides can now be replaced with measurements:

| | Q | η (bore) | Q × η |
|---|---:|---:|---:|
| Ring, as recorded (eigenmode) | 11,054 | 0.43% | 47.5 |
| Cavity, as recorded (closed form) | 53,060 | 0.092% | 48.8 |
| **Ring, measured (R5)** | **10,011** | 0.43% | **43.0** |
| **Cavity, measured** | **45,162** | 0.092% | **41.5** |

🔢 **Within 3.5% measured, against 3% as recorded.** *"The ceramic buys
compactness, not coupling"* holds — and now rests on two driven measurements
rather than an eigenmode paired with a closed form.
| 19 | ✅ **Audit of everything downstream of `dq.py`** | Bug confined to one file; all other energy uses are ratios. **12 modes validated 1.000× by a convention-free method.** Original PEC check was a false positive — unresolvable at Q~1e6. Q×η survives at 43.0 vs 41.5 |

---

## 2026-08-14 — RECHECK QUEUE, second round (what R5 reopened)

R1–R6 are closed. R5's factor-of-2 propagated further than the Q values
themselves; these are what it disturbed.

### Closed on inspection — checked, not assumed

| | verdict |
|---|---|
| **Q_ext = 165 target** | ✅ **Untouched.** 165 is the *plasma-loaded* Q (2450/15, bandwidth-derived), **not** a coupling target derived from Q₀. "Growing the loop is ill-posed" stands exactly as written |
| **Thermal / machining tolerance** (§7) | ✅ **Untouched.** Used Q ≈ 46,200 (from f/Q = 53 kHz), within **2.4%** of the corrected measured 45,162. It never went through `dq.py` |
| **Sector CV, mode IDs, brake sweep, tuning sensitivities** | ✅ ratios throughout |
| **Design point, +30.7 MHz, split −37 MHz** | ✅ frequencies, not Q |

### 🔴 Corrected in place — the numbers were wrong, the conclusions survived

**Unlit resonance widths DOUBLE** (Q halved ⇒ linewidth doubled), so the
amplifier requirement is **half as severe** as `architecture-comparison.md` §2c
first stated:

| | was | corrected |
|---|---:|---:|
| TE₀₁₁ unlit width @ critical coupling | 54.2 kHz | **108.5 kHz** |
| TM₀₂₀ unlit width | 105.7 kHz | **211.5 kHz** |
| delivered power, 0.5 MHz off, into TM₀₂₀ | 1.1% | **4.3%** |

⚠️ **A magnetron still cannot ignite this cavity** — ±10–20 MHz of pushing
against a 211 kHz resonance. The conclusion holds with room to spare; only its
sharpness was overstated.

**Atmospheric-parity claims — two documents disagreed, and neither was right:**

| source | claimed | from |
|---|---|---|
| `architecture-comparison.md` | 0.47×, ~18 kW for 2× | the **inflated** field |
| `coupling-architecture.md` | 0.35×, ~8 kW for parity | the **perturbative** field |
| ✅ **corrected, both** | **0.335×, ~8.9 kW parity, ~35.7 kW for 2×** | measured 7.63 kV/cm |

> ⚠️ **That the two documents disagreed and neither was flagged is its own
> finding.** The same physical quantity was quoted from two different
> provenances in two places, and the inconsistency survived because nobody
> compared them. Cross-document consistency is not checked by anything here.

### Genuinely open — new queue

| # | question | why it matters | status |
|---|---|---|---|
| ~~R7~~ ✅ | **Re-derive the ignition pressure ramp on 127 Torr**, not 136 or 180 | `ignition-study.md` §4 and the vacuum-system sizing were written against 136 Torr; the design figure is now **127**. Lower pressure = harder pump, longer ramp, and the ramp is already the **top unquantified risk** | ✅ **closed** |
| ~~R8~~ ✅ | **Why is the TM₀₂₀ closed form 1.15× high when TE₀₁₁'s is 1.03×?** | With the 2× removed, the closed forms are good — but not equally. TE₀₁₁ agrees to 3%, TM₀₂₀ to 15%. ⚠️ TM₀₂₀ is the **ignition** mode, so its 15% is the one that propagates into the pressure figure | ✅ **closed** |
| ~~R9~~ ✅ | ~~Ring Q sensitivity to alumina tanδ~~ → **BOTH architectures' tanδ exposure** | 🔴 **Scope widened by R8.** The ring's Q₀ is dielectric-dominated *and so is 27% of AMIP's ignition mode* — the claim that AMIP is "not exposed" was wrong. AMIP's half is now quantified (95–137 Torr); **the ring's alumina half is not**. Q × η = 43.0 vs 41.5 still rests on a placeholder | ✅ **closed** |
| ~~R10~~ ✅ | **Does the order-independence of Q hold with a plasma load?** | R3 found Q moves 0.6% between order 1 and 2 unloaded. ⚠️ Untested loaded, and a lossy plasma is exactly where discretisation of a *loss* term might not be common-mode | open |

⚠️ **R9 is the cheapest and most load-bearing** — two solves of ~110 s each, and
it bounds how much of the architecture comparison rests on a placeholder.
| 20 | 🔴 **Second-round queue — R7–R10 opened** | Widths doubled (amplifier bar *halved*); two docs disagreed on parity and neither was right (now 0.335×/8.9 kW). Q_ext=165 and the tolerance study verified untouched |

---

## 2026-08-14 — R8 ✅ the comparison was mis-framed, and the ignition mode is not wall-dominated

**The 1.15× was never a closed-form error. It was another unlike-footing
comparison** — the third in this sequence. **The closed forms predict Q_wall.
They were being compared against Q_total**, which also contains dielectric loss.

Decomposed on the tilt45 geometry, which drives both modes in one solve:

| mode | Q_wall measured | closed form | ratio | Q_diel | Q_total | closure |
|---|---:|---:|---:|---:|---:|---:|
| TE₀₁₁ | 47,690 | 49,182 | **1.03×** | 992,991 | 45,640 | 1.003 |
| TM₀₂₀ | 31,677 | 26,563 | **0.84×** | 86,954 | 23,169 | 0.998 |

🔢 **The direction flips.** Against Q_total the TM₀₂₀ closed form looked 15%
*high*; against Q_wall — the quantity it actually predicts — it is **16% low**.
Closure holds to 0.2% on both modes.

**So the closed forms genuinely are mode-dependent in accuracy**: TE₀₁₁ to 3%,
TM₀₂₀ to 16%. ⚠️ The mechanism is the one predicted, with a sign I got wrong. The
quartz does *two* things to TM₀₂₀, which carries **3.978%** of its E-field in the
bore against TE₀₁₁'s **0.054%**:

1. **adds loss** — lowering Q_total, and
2. **redistributes field away from the walls** — *raising* the true Q_wall above
   bare-cavity theory.

I predicted only the first. Both are large for TM₀₂₀ and negligible for TE₀₁₁,
which is why one mode's closed form is fine and the other's is not.

### ✅ 127 Torr stands — R7 is unblocked

The field and pressure were computed from **measured Q_total (23,169)**, never
from the closed form. R8 does not move them. R7 may proceed on 127 Torr.

### 🔴 But R8 found something worse than what it was looking for

| mode | Q_total | = Q_wall ∥ Q_diel | **dielectric share of loss** |
|---|---:|---|---:|
| TE₀₁₁ operating | 45,640 | 47,690 ∥ 992,991 | 4.6% |
| **TM₀₂₀ ignition** | **23,169** | **31,677 ∥ 86,954** | **⚠️ 26.6%** |

> ⚠️ **CORRECTION.** The second-round queue asserted *"AMIP's is wall-dominated
> and **not** exposed"* to placeholder dielectric loss, in contrast to the ring.
> **That is true of the operating mode and false of the ignition mode.** More
> than a quarter of TM₀₂₀'s loss budget is quartz, so the ignition margin — the
> single number gating the vacuum system — depends directly on a material
> constant nobody has verified.

🔢 Ignition pressure vs quartz tanδ, Q_wall held at its measured 31,677:

| quartz tanδ | Q_total | bore field | **2× margin** |
|---:|---:|---:|---:|
| 5×10⁻⁵ (high-purity fused silica) | 26,796 | 8.21 kV/cm | **137 Torr** |
| **1×10⁻⁴ (assumed)** | **23,219** | **7.64 kV/cm** | **127 Torr** |
| 2×10⁻⁴ | 18,325 | 6.79 kV/cm | **113 Torr** |
| 4×10⁻⁴ (lower grade) | 12,892 | 5.69 kV/cm | **95 Torr** |

> 🔑 **The torch and brake quartz grade is now an ignition design parameter, not
> an incidental material choice.** Across the plausible fused-silica range the
> requirement moves **95 → 137 Torr** — a 1.4× span in the vacuum requirement,
> from one number in a datasheet. **Specify high-purity fused silica and verify
> tanδ at 2.45 GHz before sizing the pump.**

⚠️ This is a *stronger* result than R8 was asked for, and it lands on the
critical path. It also means R9's placeholder-tanδ concern applies to **both**
architectures, not only the ring.
| 21 | ✅ **R8 — mis-framed comparison; ignition mode is 27% dielectric** | Closed form predicts Q_wall, was compared to Q_total. Correctly: TE₀₁₁ 1.03×, TM₀₂₀ **0.84×**. **127 Torr stands, R7 unblocked.** 🔴 But quartz grade moves ignition 95–137 Torr |

---

## 2026-08-14 — R7 ✅ ramp re-derived on 127 Torr; the pump spec is what moves

Re-derived on the **measured** field 7.63 kV/cm at 1 kW (§"Pressure is the lever"
used the perturbative 8.05–8.17).

| p (Torr) | p (atm) | E_break | margin @1 kW | margin @10 kW |
|---:|---:|---:|---:|---:|
| 760 | 1.00 | 22.8 kV/cm | 0.3× | 1.1× |
| 400 | 0.53 | 12.0 | 0.6× | 2.0× |
| 254 | 0.33 | 7.6 | **1.0×** | 3.2× |
| **127** | **0.17** | **3.8** | **2.0×** | 6.3× |
| 100 | 0.13 | 3.0 | 2.5× | 8.0× |
| 85 | 0.11 | 2.5 | **3.0×** | 9.5× |

🔢 **2× margin at 1 kW CW needs 127 Torr** (was 134/136 perturbative, then 180
under the factor-of-2 error). 3× needs 85 Torr. At 10 kW pulsed, 2× comes at
**402 Torr**.

### Unchanged, and checked rather than assumed

- ✅ **The bore diameter still does not enter.** Λ = 0.35 cm puts the diffusion
  correction below **2.9 Torr**, still ~36× under the operating point.
- ✅ **The f₀ shift from evacuating is unchanged and still absorbable.** 760 →
  127 Torr moves f₀ **+549 kHz ≈ 5.2 unloaded linewidths** (Q₀ = 23,169). It was
  ~0.5 MHz before; the linewidth grew with the Q correction, so the shift in
  *linewidths* barely moved. Predictable, and the tracking loop takes it — but it
  must be expected.
- ✅ **The ignition field is still not a design variable.** a and L are both
  pinned by band placement. Pressure remains the only lever.

### 🔑 What actually changed: the pump is no longer comfortably specified

The old text called for *"a diaphragm pump reaching 100–150 Torr, a few hundred
dollars"*. At 127 Torr that still holds — **but only at the assumed quartz
tanδ.** Folding in R8's band:

| quartz tanδ | 2× margin | pump class |
|---:|---:|---|
| 5×10⁻⁵ | 137 Torr | ✅ single-stage diaphragm, comfortable |
| **1×10⁻⁴ (assumed)** | **127 Torr** | ✅ single-stage, adequate |
| 2×10⁻⁴ | 113 Torr | ⚠️ at the edge of single-stage |
| 4×10⁻⁴ | 95 Torr | 🔴 **below single-stage floor — needs two-stage** |

> **So R8 and R7 combine into one procurement decision.** Single-stage diaphragm
> pumps bottom out near 100 Torr; two-stage reach ~15 Torr but cost several times
> more. **Either specify high-purity fused silica and buy the cheap pump, or
> accept unverified quartz and buy the expensive one.** ⚠️ The cost table's
> "pump $0.3–0.8k" should read **$0.3–2k** until the quartz is specified.

⚠️ Or drop to 3× margin deliberately and size for 85 Torr, which needs the
two-stage pump regardless — worth considering if the ramp turns out to want
headroom.

### Unchanged: the actual critical unknown

**Igniting at ~127 Torr and ramping to atmospheric while the microwave sustains**
is still the top unquantified risk, exactly as before. Nothing in R5–R8 touched
it, because it is not a Q question. ⚠️ 127 vs 136 Torr does not change the
*character* of that risk — the ramp spans 6× in pressure either way.
| 22 | ✅ **R7 — ramp re-derived on 127 Torr** | 2× at **127**, 3× at 85, 10 kW pulsed at 402. Diffusion and f₀-shift arguments verified unchanged. 🔑 **R7+R8 combine: quartz grade decides single- vs two-stage pump**, cost $0.3–2k |

---

## 2026-08-14 — 🔴 R9: the ring-vs-AMIP comparison cannot currently be made

The analytic dielectric model was validated first, as R5's lesson demands:
1/Q_diel = Σ p_elec,i · tanδ_i, predicting Q_total at 0.5× and 2× alumina tanδ.

| k | tanδ alumina | Q_total predicted | measured | agree |
|---:|---:|---:|---:|---:|
| 0.5 | 5×10⁻⁵ | 18,023 | 18,022 | **1.000** |
| 2.0 | 2×10⁻⁴ | 5,300 | 5,299 | **1.000** |

✅ **Exact.** So the curve can be trusted without further solves — and this is
the cheap way to have run R5 in the first place.

### 🔴 The result: Q × η = 43 vs 41.5 was an artifact of one assumed number

| alumina tanδ | ring Q_total | ring Q × η | vs AMIP's 41.5 |
|---:|---:|---:|---:|
| 5×10⁻⁵ | 18,023 | **77.5** | **1.87×** |
| **1×10⁻⁴ (assumed)** | **10,012** | **43.1** | **1.04×** |
| 2×10⁻⁴ | 5,300 | 22.8 | 0.55× |
| 5×10⁻⁴ | 2,197 | 9.4 | 0.23× |

> 🔴 **"The ceramic buys compactness, not coupling" is true at tanδ = 1×10⁻⁴ and
> false everywhere else.** Across plausible alumina grades the ring's Q × η spans
> **8×**, and the comparison runs from the ring being 1.87× *better* to 4.3×
> worse. The celebrated "within 3%" agreement is a coincidence of the placeholder,
> not a physical result. ⚠️ **This is `axisymmetric-feed.md` §6's central claim,
> and it does not currently hold.**

### Both architectures now, across both unverified loss tangents

| | field @1 kW | 2× margin |
|---|---|---|
| Ring, alumina 5×10⁻⁵ … 5×10⁻⁴ | **2.85 – 8.17 kV/cm** | 48 – 136 Torr |
| AMIP, quartz 5×10⁻⁵ … 4×10⁻⁴ | **5.69 – 8.20 kV/cm** | 95 – 137 Torr |

🔢 **The ranges overlap. AMIP/ring spans 0.70× to 2.87×** — it cannot be said
which architecture couples better without measuring two loss tangents nobody has
measured. ⚠️ The 1.25× recorded earlier today is one point inside that band.

### ✅ But there IS a real AMIP advantage here, and it is not the one claimed

| | dielectric share of loss | field spread across its placeholder |
|---|---:|---:|
| Ring (operating) | **90.3%** | **2.9×** |
| AMIP TM₀₂₀ (ignition) | 26.6% | 1.44× |
| AMIP TE₀₁₁ (operating) | **4.6%** | ~1.02× |

> **AMIP is not demonstrably better-coupled. It is demonstrably more
> *predictable*.** Its operating mode is 95% wall-loss, and wall loss is set by a
> conductivity known to three digits, not by a ceramic datasheet. The ring's Q is
> 90% hostage to a number that varies 10× across grades of the same material.
>
> That is a weaker claim than the one it replaces, and a more defensible one: **a
> design whose performance is set by geometry and conductivity can be predicted
> before it is built. One set by a ceramic loss tangent cannot.**

⚠️ **What would settle it:** the alumina tanδ Radom actually uses, and the fused
silica grade for the torch. Both are datasheet lookups against a specified part,
not simulations. Until then, quote the *bands*, never the point values.
| 23 | 🔴 **R9 — the ring/AMIP coupling comparison is not currently supportable** | Analytic model exact (1.000×). Ring Q×η spans **8×** over plausible alumina; the "within 3%" was a placeholder artifact. Field ranges **overlap**. ✅ Real AMIP edge is *predictability* (4.6% dielectric vs 90.3%), not coupling |

---

## 2026-08-14 — R10 part 1: the plasma-loaded cavity, and a guard that overcorrected

⚠️ **Crude plasma model**: uniform conductivity filling the whole bore column, no
self-consistency, no thermal or chemical model, and the real discharge is a torus
in part of that volume. It cannot predict plasma behaviour. It can answer the
numerical question, and it replaces two things §2c was **assuming**.

### 🔴 First: the contrast guard added this morning caused a false negative

σ = 10 and 30 returned "no resonance". **They were real resonances.** All three
peaks sit *interior* with U falling both sides — they are simply **broad**,
because Q collapses to 138–321 under load.

> **Contrast cannot separate the two failures**: the `o2drv` non-resonance scored
> **3.1×**, a genuine loaded resonance **2.5×**. The guard rejected the good data
> and would have passed the bad on a slightly different sweep.
>
> ✅ **The real discriminator is where the GLOBAL maximum sits.** `o2drv`'s
> resonance was outside the window, so U climbed monotonically to the window
> *edge*. A loaded resonance peaks in the interior. Guard replaced with an
> edge-position test plus a flat-data floor of 1.5×, and regression-tested: it
> still rejects `o2drv` and still passes `sigdrv` unchanged.

**Seventh selection-criterion failure — and the first caused by fixing one.** ⚠️
A guard written against a single observed failure encodes that failure's
incidental features. This one confused "narrow and real" with "real".

### The measurements

| σ (S/m) | skin depth | δ/r_bore | f loaded | shift | Q₀ | linewidth | shift/LW |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 10 | 3.22 mm | 0.38 | 2.46570 | **+16.5 MHz** | 138 | 17.9 MHz | 0.9 |
| 30 | 1.86 mm | 0.22 | 2.47026 | **+21.1 MHz** | 192 | 12.9 MHz | 1.6 |
| 100 | 1.02 mm | 0.12 | 2.47340 | **+24.2 MHz** | 321 | 7.7 MHz | 3.1 |

### ✅ TE₀₁₁ loads strongly — a real doubt closed

Q falls **45,640 → 138–321**. The plasma takes **99.3–99.7%** of all loss.

> ⚠️ This was genuinely in doubt: TE₀₁₁ carries only **0.054%** of its stored
> *electric* energy in the bore. **That fraction is the wrong figure of merit.**
> Dissipation is ∫σ|E|²dV, which is large when σ is large regardless of how
> little energy is *stored* there. A mode can be a poor electric-energy
> concentrator and an excellent plasma coupler simultaneously.

✅ **§2c's "≳95–99% of power reaches the plasma" is confirmed by direct
measurement** rather than the assumed Q_plasma it rested on. 🔢 And Q_plasma
measures **138–321**, so §2c's assumed 200 was about right and its 500 too high.

### 🔑 New requirement §2c did not have: the ignition frequency step

**f₀ jumps +16.5 to +24.2 MHz the instant the plasma lights** — **0.9 to 3.1
loaded linewidths.** The amplifier must retune by more than a linewidth *during*
the ignition transient, not merely track slow drift. ⚠️ That is a control-loop
bandwidth requirement, and nothing in this project has specified one.

### ✅ And the coupling is self-limiting

🔢 Absorption peaks where skin depth ≈ bore radius, at **σ ≈ 1.4 S/m**. Every
case here is far past it, so **a denser plasma absorbs *less*** — Q rises with σ.

> **That is negative feedback on the discharge.** Runaway heating reduces its own
> coupling. ⚠️ Not a stability proof, but the sign is favourable, and it is the
> opposite of what a naive "more plasma = more absorption" picture predicts.

⚠️ TM₀₂₀ was not found under load. It is the **ignition** mode and operates
*before* a plasma exists, so its loaded behaviour matters far less — but it means
the mode-shift ignition sequence has not been modelled through the transient.
| 24 | ✅ **R10 pt 1 — plasma-loaded cavity** | Q 45,640→**138–321**, plasma takes 99.3–99.7%. ✅ TE₀₁₁ loads strongly despite 0.054% bore E. 🔑 **f₀ steps +16–24 MHz on ignition (0.9–3.1 linewidths)**. Coupling self-limits past σ≈1.4 S/m. 🔴 Contrast guard overcorrected — replaced |

### R10 order-2, first attempt — the R3 mistake, repeated

`pl30o2` (window 2.44–2.50) returned no resonance. ✅ **Correctly** this time:
argmax at **exactly 2.50000**, the upper edge, index 1200 of 1201, with U rising
monotonically to it. The freshly-replaced edge-position guard caught a genuine
out-of-window case within an hour of being written — which is the regression test
that matters.

🔴 **But the window was mine to get right, and R3 had already published the
number.** Order 2 raises f by **+30.7 MHz** on this mesh family. Order-1 loaded
f₀ = 2.47026, so the order-2 answer sits near **2.501** — and I set the boundary
at 2.500.

> **A measured offset recorded in this file three entries ago was not applied
> when choosing the next window.** The cost is one ~40-minute solve. ✅ **Rule:
> when moving from order 1 to order 2 on this mesh family, centre the window on
> f₁ + 31 MHz, not on f₁.**

Re-running at 2.48–2.56.

---

## 2026-08-14 — 🔴 R11: the design point was tuned COLD, and the plasma shift eats the band margin

Prompted by a question about the coupling loop, which turned up something larger.

### The loop question, first — it is fine

204 mm² is **12 × 17 mm rectangular**, not a 16.1 mm circle. It spans
**r = 89.4 → 101.4 mm**, |y| ≤ 8.5 mm, in the z = 0 plane. The torch outer wall
is at r = 10 mm, so there is **79.4 mm of clearance** and no interaction.

> ⚠️ Worth stating plainly because the intuition it violates is a reasonable one:
> **the loop does not encircle the torch.** It is not an ICP work coil. It is a
> small pickup loop at the cavity wall whose only job is to feed the cavity; the
> **TE₀₁₁ mode's own E_φ drives the plasma**. That separation is the architecture.

### 🔴 The real finding: the operating mode leaves the ISM band when lit

| | |
|---|---|
| Design TE₀₁₁, **cold** | 2.4808 GHz |
| ISM band top | 2.5000 GHz → **+19.2 MHz margin** |
| Plasma shift, **measured** (R10) | **+16.5 to +24.2 MHz** |

| σ (S/m) | loaded TE₀₁₁ | verdict |
|---:|---:|---|
| 10 | 2.4973 | in band, 2.7 MHz to spare |
| 30 | 2.5019 | 🔴 **out by 1.9 MHz** |
| 100 | 2.5050 | 🔴 **out by 5.0 MHz** |

> 🔴 **The whole design point was optimised against the COLD cavity.** Band
> placement, the −37 MHz split, the brake thickness, the sector CV — every
> criterion was evaluated with no plasma present. **But the operating condition
> is lit**, and the shift that condition produces is the same size as the margin
> that was designed in.
>
> ⚠️ Even taking the crude plasma model's *smallest* shift, the margin drops from
> 19.2 MHz to 2.7 MHz. **A design cannot be called closed when the untested
> effect is as large as the tolerance.**

⚠️ The shift magnitude is model-dependent — uniform bore conductivity overstates
the plasma's volume, and a real torus would shift less. **The direction is not in
doubt** (field expulsion shrinks the effective volume, raising f), and the
magnitude is comparable to the margin under any plausible filling factor.

### ✅ What survives

🔢 The **−37 MHz split still works**, and now on a measured basis: against the
plasma-loaded linewidth it is **2.1 / 2.9 / 4.8 linewidths** at σ = 10/30/100,
bracketing the 2.5 it was designed for (which used an *assumed* loaded Q of 165).

### The retune is not a simple shift

🔢 dTE₀₁₁/dL = **−13.6 MHz/mm**, TM₀₂₀ essentially flat. Landing the *loaded*
TE₀₁₁ mid-band at 2.470 needs cold TE₀₁₁ at 2.449, i.e. **L 87.67 → 90.0 mm**.

⚠️ **But TM₀₂₀ does not follow, so the cold split collapses 37.4 → 5.6 MHz.**
That is still 53–103 *cold unloaded* linewidths, so mode-shift ignition — which
happens cold — is unaffected. The interaction must be checked, not assumed: the
brake thickness was chosen to set that split, and it is now solving a different
problem.

| # | question | status |
|---|---|---|
| **R11** | **Retune the design point so the LIT cavity is in band.** L ≈ 90 mm to first order; re-verify split, CV, brake thickness and band margins **with the bore conductivity present** | 🔴 open — **blocks calling the design closed** |
| ~~R12~~ ✅ | **How much does the shift depend on plasma filling factor?** Uniform-bore σ is an upper bound on volume. Re-run with an annular conducting shell of realistic thickness | open |
| 25 | 🔴 **R11 — design point tuned cold; plasma shift exceeds band margin** | Loaded TE₀₁₁ reaches **2.502–2.505 GHz**, outside ISM, against a +19.2 MHz cold margin. Retune L 87.67 → ~90 mm, but the cold split collapses 37 → 5.6 MHz. ✅ Loop geometry fine (rectangular, 79 mm from torch) |

---

## 2026-08-14 — 🔴 R7's pump conclusion was wrong, in both directions at once

Pricing and grade research, prompted by R7/R8. **R7 said the quartz grade decides
single- vs two-stage pump. That framing is wrong twice.**

### 1. The depth requirement is trivial — a two-stage pump is ~15× overkill

| our target | in pump units |
|---:|---:|
| 137 Torr | 183 mbar |
| **127 Torr** | **169 mbar** |
| 95 Torr (worst-case quartz) | 127 mbar |

✅ Two-stage diaphragm pumps reach **6–9 Torr (8–12 mbar)** and start around
**$2,470** (VACUUBRAND MZ series). Single-stage reach ~100–250 mbar. **Our whole
range sits at 127–183 mbar**, so even the worst-case quartz does not demand a
two-stage pump on *depth*. ⚠️ **Withdraw the R7 claim that 95 Torr forces a
two-stage pump**; it was reasoning from a half-remembered floor, not a spec.

### 2. 🔑 But depth is the wrong spec entirely — the torch is flowing

**Ultimate pressure is a zero-flow number. The torch flows nitrogen continuously**,
so the pump must hold the pressure against that input. Throughput required at
127 Torr:

| N₂ in (slm) | actual volume at 127 Torr | throughput | pump class |
|---:|---:|---:|---|
| 20 (full running flow) | 120 L/min | **7.2 m³/h** | VARIO 30–40 m³/h class |
| 10 | 60 L/min | 3.6 m³/h | mid-size |
| 5 | 30 L/min | 1.8 m³/h | MZ 2C NT (2.3 m³/h) |
| 2 | 12 L/min | 0.7 m³/h | small |

> 🔴 **The pump is sized by ignition gas flow, not by vacuum depth — and the
> ignition flow is a design decision nobody has made.** It spans an order of
> magnitude in pump capacity and roughly $0.3k to $5k+.
>
> ⚠️ Note the MZ 2C NT, the "popular chemistry two-stage" at $2.5k, is only
> **2.3 m³/h** — it is *deep* but *slow*, and would not hold 127 Torr against
> full torch flow at all. **Buying on ultimate pressure would buy the wrong
> pump.**

✅ **The mitigation is free and obvious once stated: ignite at reduced flow**,
then ramp pressure and flow together. Nothing requires full analytical flow
before there is a plasma. That collapses the requirement to <1 m³/h. ⚠️ But it
adds a second coupled ramp to a sequence whose *single* ramp is already the top
unquantified risk.

### 3. Quartz grades — the assumed tanδ is optimistic, and mostly not ours to pick

✅ Literature: fused silica tanδ ≈ **2×10⁻⁴** typical at microwave; high-purity
measures 2.3×10⁻⁴ at 9.33 GHz and 0.9×10⁻⁴ at 22.7 GHz. Microwave-transparency
specs quote "<0.001, preferably <0.0005". Values **below 5×10⁻⁵ need special
measurement technique**, so they are not casually available.

> ⚠️ **Our assumed 1×10⁻⁴ sits at the optimistic end of the plausible band, not
> the middle.** 2×10⁻⁴ is the more defensible default, which puts ignition at
> **113 Torr**, not 127.

🔴 **And the constraint R7 missed: the torch is a standard Fassel part.** Its
quartz grade is whatever the vendor uses — Glass Expansion, Meinhard, Agilent —
and is **not a design variable** without abandoning the standard-torch decision
that was made on cost grounds. Only the **brake** is a custom part whose grade we
choose. `dsplit` is running to find which of the two carries the loss; if it is
the torch, the grade lever does not exist.

| # | question | status |
|---|---|---|
| **R13** | **Choose the ignition gas flow.** It sizes the pump across an order of magnitude and is currently unspecified | 🔴 open |
| **R14** | **Get the actual tanδ of a standard ICP torch's quartz** at 2.45 GHz, from a vendor datasheet | open |
| 26 | 🔴 **Pump/quartz research — R7 conclusion withdrawn** | Two-stage is **15× overkill on depth** ($2.5k, 6–9 Torr vs our 127–183 mbar). 🔑 **Pump is sized by ignition FLOW, not depth** — 0.7 to 7.2 m³/h, unspecified. Assumed quartz tanδ 1e-4 is optimistic; 2e-4 → 113 Torr. Torch grade is **not ours to choose** |

---

## 2026-08-14 — R10 ✅ answered: Q is NOT order-independent under load. The shift is.

| | order 1 | order 2 | Δ |
|---|---:|---:|---:|
| f₀ (σ=30 plasma) | 2.47026 | 2.50235 | **+32.1 MHz** |
| Q₀ | 192 | 271 | **+41.1%** |

🔢 The frequency offset **+32.1 MHz** matches R3's unloaded **+30.7 MHz** — the
discretisation behaves as established. **But Q moved 41%, against 0.6% unloaded.**

> ✅ **R10's hypothesis was right.** Unloaded, Q is a ratio of energies over the
> same field and discretisation error cancels. **Loaded, the loss is a volume
> integral ∫σ|E|²dV concentrated in a skin layer**, and that does not cancel —
> it is a property of how well the mesh resolves one thin region.

### Why, quantitatively

| | |
|---|---|
| Skin depth at σ = 30 | **1.86 mm** |
| Bore mesh, median edge | **1.41 mm** |
| Elements per skin depth | **≈1.3** |
| Wanted for an exponential decay | 3–4, i.e. ≤0.62 mm |

🔴 **So the plasma-loaded Q is not converged at EITHER order.** Order 2 is better,
not right. The 41% jump is the signature of an unresolved skin layer, and there
is no reason to think order 2 has arrived. **Quote plasma-loaded Q as a lower
bound (≳270 at σ=30), never as a measurement.**

⚠️ Consequence for §2c: Q_plasma is **not** 138–321 as recorded this evening.
That was order 1. The order-2 value at σ = 30 is **273**, and the true value is
higher still. Ironically this moves it back toward §2c's original *assumed*
200–500 band.

### ✅ What survives, and it is the part that matters

**The plasma-induced frequency shift is order-robust: +21.1 MHz at order 1 vs
+22.5 MHz at order 2 — 6%.** Frequency is a global property of the mode; it does
not depend on resolving the loss layer.

> ✅ **R11 therefore stands.** The band-margin finding — that the lit cavity
> leaves the ISM band — rests on the *shift*, not on Q, and the shift is the
> robust quantity. ⚠️ The order-2 shift currently uses an *estimated* unloaded
> reference (order-1 tilt45 + R3's offset); `t45o2` is running to replace that
> estimate with a measurement, because R11 blocks calling the design closed and
> should not rest on a transferred constant.

### The power-to-plasma conclusion is unaffected

🔢 At order 2, Q_plasma = 272.6 against Q_unloaded 45,640 → the plasma still
takes **99.4%** of all loss (order 1 said 99.6%). ✅ That conclusion was never
sensitive to the convergence problem, because it is a *ratio* of two Q values
that move together.

| # | question | status |
|---|---|---|
| **R15** | **Refine the bore mesh to ≤0.6 mm and re-measure plasma-loaded Q** | open — needed before any *quantitative* plasma-loading claim. ⚠️ Not needed for R11 |
| 27 | ✅ **R10 — Q is NOT order-independent under load** | Q +41% order 1→2 (unloaded: +0.6%). Skin depth 1.86 mm vs 1.41 mm mesh = **1.3 elem/skin depth — unconverged at both orders**. ✅ **Frequency shift IS robust (6%), so R11 stands.** Power-to-plasma 99.4% unaffected |

---

## 2026-08-14 — 🔴 dsplit: the quartz lever is in the part we do NOT choose

Per-dielectric electric-energy fractions, so each contribution is separable
(analytic model validated to 1.000× in R9):

| mode | torch p_elec | Q_diel | brake p_elec | Q_diel | **torch share of dielectric loss** |
|---|---:|---:|---:|---:|---:|
| **TM₀₂₀ ignition** | **8.523%** | 117,325 | 2.947% | 339,362 | 🔴 **74.3%** |
| TE₀₁₁ operating | 0.232% | 4,317,214 | 0.706% | 1,416,045 | 24.7% |

> 🔴 **For the ignition mode the torch carries three-quarters of the dielectric
> loss — and the torch is a standard Fassel part whose quartz grade we inherit.**
> Only the brake is ours to specify, and it carries 26%.

🔢 What specifying the brake actually buys:

| torch tanδ | brake tanδ | Q_total | 2× margin | |
|---:|---:|---:|---:|---|
| 1×10⁻⁴ | 1×10⁻⁴ | 23,235 | 127 Torr | both as assumed |
| 2×10⁻⁴ | 2×10⁻⁴ | 18,346 | 113 Torr | both realistic |
| 2×10⁻⁴ | **5×10⁻⁵** | 19,965 | **118 Torr** | brake upgraded |
| 5×10⁻⁵ | 1×10⁻⁴ | 25,788 | **134 Torr** | good torch |
| 4×10⁻⁴ | 1×10⁻⁴ | 14,576 | **101 Torr** | poor torch |

> ⚠️ **Upgrading the brake to the best available grade buys 5 Torr.** The torch
> grade alone swings the requirement **101 → 134 Torr**. **R8's recommendation —
> "specify high-purity fused silica and verify tanδ before sizing the pump" — is
> therefore 74% unactionable as written.** Withdraw the recommendation; keep the
> *sensitivity*.

### 🔑 What this does to the queue

**R14 becomes the important one, and its character changes.** The torch's tanδ is
now the dominant unverified quantity in the ignition margin, and it is something
to **discover, not choose**. A vendor datasheet decides a build parameter.

### ✅ A way to restore the lever, if it is worth restoring

⚠️ **Demountable ICP torches are standard products** — Agilent, Glass Expansion
and Meinhard all sell them, and the outer tube is a *separate replaceable part*.
That means the outer tube's grade could be specified **without abandoning
standard-torch economics**, which was the decision the whole constraint rests on.

🔢 It would be worth ~16 Torr (101 → 118 at a realistic brake), i.e. the
difference between a comfortable single-stage pump and a marginal one. ⚠️ Not
obviously worth it — but it is a real option and it was invisible while "standard
torch" was treated as one indivisible choice.

| # | question | status |
|---|---|---|
| **R14** | ⬆️ **PROMOTED — get the torch quartz tanδ at 2.45 GHz.** Now the dominant unverified term in the ignition margin, and inherited rather than chosen | open |
| **R16** | **Is a demountable torch's outer tube specifiable by grade?** Would restore a ~16 Torr lever. Vendor question, not a simulation | open |
| 28 | 🔴 **dsplit — the quartz lever is in the torch, not the brake** | Torch carries **74.3%** of TM₀₂₀ dielectric loss. Upgrading the brake buys **5 Torr**; torch grade swings **101–134 Torr**. R8 recommendation withdrawn. ✅ Demountable torches may restore the lever (R16) |

### R11 confirmed — the plasma shift is order-independent to 3 significant figures

The estimated reference is replaced by a measured one:

| | order 1 | order 2 |
|---|---:|---:|
| TE₀₁₁ unloaded (tilt45) | 2.44920 | **2.48125** |
| TE₀₁₁ loaded (σ=30) | 2.47026 | 2.50235 |
| **plasma shift** | **+21.11 MHz** | **+21.10 MHz** |

🔢 **Identical.** Far tighter than the 6% the transferred-offset estimate
suggested — and worth the solve, because the transferred offset was itself off by
1.35 MHz (predicted 2.47990, measured 2.48125). ✅ **R11 no longer rests on a
constant carried between meshes.**

✅ Two side confirmations fell out:
- **Q unloaded moved +0.08%** order 1 → 2 (45,640 → 45,678), even tighter than
  R3's +0.6%. The contrast with the **+41%** loaded is now stark and unambiguous.
- **Order-2 unloaded 2.48125 lands 0.45 MHz from the design point's 2.4808**, an
  independent corroboration on a different mesh and order.

**The band verdict, now measured at both ends:**

| σ | loaded TE₀₁₁ | vs 2.5000 ISM ceiling |
|---:|---:|---|
| 10 | 2.4973 | 2.7 MHz to spare |
| **30** | **2.5019** | 🔴 **out by 1.9 MHz** |
| 100 | 2.5050 | 🔴 out by 5.0 MHz |

**R11 stands on measurement. The design point must be retuned for the lit
cavity.**
| 29 | ✅ **R11 confirmed by measurement** | Plasma shift **+21.11 (o1) vs +21.10 MHz (o2)** — order-independent to 3 s.f. Unloaded Q moved +0.08% vs **+41% loaded**. Order-2 unloaded lands 0.45 MHz from the design point |

---

## 2026-08-14 — R16 ✅ the lever exists, and it comes with a bigger question attached

### R16: yes, the outer tube is a separately specifiable part

✅ **Confirmed as a standard product line.** Agilent sells *"Outer Tube Sets for
Semi/Fully Demountable Torches"*; Glass Expansion's **D-Torch** is built so the
analyst *"replaces only the outer tube, rather than the entire torch"*, and it is
offered in **high-purity quartz OR Sialon ceramic**.

> ✅ **The ~16 Torr lever dsplit said we did not have is real after all.** The
> outer tube — the part carrying 74% of TM₀₂₀'s dielectric loss — is a catalogue
> item available in more than one material, and using it does not abandon the
> standard-torch decision. It replaces "buy a standard torch" with "buy a
> standard *demountable* torch", which is the same class of purchase.

### 🔑 And the finding nobody asked for: Sialon exists *because* of our matrix

⚠️ Glass Expansion offers the ceramic outer tube specifically because *"the
Sialon material does not devitrify"*, of *"particular benefit for the analysis of
high-TDS sample matrices"*.

🔢 **Our matrix is ~2% TDS Mehlich-3** — the exact case it is sold for.
`architecture-comparison.md` §2b listed torch devitrification as
**architecture-independent** and therefore not a differentiator. **It is
architecture-independent for ICP. It may not be for AMIP.**

| | ε | tanδ @2.45 GHz | devitrification in 2% TDS |
|---|---:|---:|---|
| High-purity quartz | 3.78 | ~1×10⁻⁴ ⚠️ assumed | ⚠️ the known failure mode |
| **Sialon** | ⚠️ **~7–8** | ⚠️ **unknown** | ✅ **does not devitrify** |

> 🔴 **This is a coupled decision that does not exist for an ICP.** At 27–40 MHz
> the torch material's microwave loss is irrelevant. **At 2.45 GHz the outer tube
> carries three-quarters of the ignition mode's dielectric loss**, so a material
> swap changes the ignition margin *and* the mode frequencies — ε roughly doubles,
> which is a retune, not a substitution.
>
> ⚠️ Sialon is described in the literature as a **wave-transparent ceramic used
> for microwave windows**, which is encouraging but not a number.

### R14: partial — the grade is probably favourable, still unquantified

✅ **GE 214** (Momentive, the classic quartz tubing grade) is *"high purity, low
hydroxyl (OH) content"*. **Low OH is the favourable direction** — OH is a
principal microwave loss mechanism in fused silica — so a torch in this class
plausibly sits at or below our assumed 1×10⁻⁴.

⚠️ **No datasheet number at 2.45 GHz was found.** Momentive quotes only "loss
factor <10⁻³ at millimetre wavelengths". **R14 stays open**; it needs a vendor
request or a bench measurement, and it remains the dominant unverified term.

| # | question | status |
|---|---|---|
| ~~R16~~ ✅ | Outer tube is separately specifiable | **closed — lever confirmed** |
| **R14** | Torch quartz tanδ at 2.45 GHz | open — vendor request, likely favourable |
| **R17** | **Sialon outer tube: ε and tanδ at 2.45 GHz, and the retune it forces** | 🔴 open — trades our top fouling risk against the ignition margin |
| 30 | ✅ **R16 — demountable outer tube is a catalogue part** | Lever confirmed: Agilent/Glass Expansion sell replaceable outer tubes in quartz **or Sialon**. 🔑 Sialon is sold *for high-TDS matrices because it does not devitrify* — our exact case. But ε~7–8 vs 3.78 forces a retune (R17). R14 partial: GE 214 is low-OH, favourable, unquantified |

### R11 first attempt — the silent no-drive failure, again

The retune solve returned a completely flat sweep: **contrast 1.06×, |S11|
constant to 0.000 dB, stored energy 4×10⁻¹²** against ~2×10⁻⁶ for a working run.
Not an out-of-window resonance — **the port was driving nothing**, the failure
§12 records as raising no error.

**Cause: I omitted `--sectors 1` when generating the mesh.** The working meshes
are all built with it. Without it the geometry builds multiple air sectors, which
**split the port face in two** (attributes 141+201 against the working mesh's
single 52 — *identical total area, 0.5400 mm², which is why an area check would
not have caught it*) and left Palace warning of **8,277 boundary faces with no
associated boundary element**.

| | broken | correct |
|---|---|---|
| flags | no `--sectors 1` | `--sectors 1` |
| port faces | **141, 201** | **52** |
| port area | 0.5400 mm² | 0.5400 mm² |
| PEC surfaces | 48 | 23 |

> ⚠️ **Three diagnostics agreed the port area was fine and the mesh was valid.**
> What identified it was comparing the *face count* against a mesh known to work.
> ✅ **Generate meshes through the same helper that generated the working ones**
> — `queue.py`'s `mesh()` carries `--sectors 1`, `--order 2` and the size-factor
> fallback, and I hand-rolled the command line instead of reusing it.

⚠️ Note `driven-tilt45.json` already carries the tilt-rotated port Direction
[0, 0.707, 0.707]. Reusing that config was right; rebuilding the mesh by hand was
not.

---

## 2026-08-14 — 🔴 R11 PAUSED: wrong handle, and premature anyway

**Two objections, both correct, and the second is the more important.**

### 1. The brake is the worst available tuning handle

🔢 Tolerance needed to hold a mode within ±5 MHz:

| handle | sensitivity | tolerance | as a fraction | part |
|---|---:|---:|---:|---|
| **brake t** | 30.7 MHz/mm | ±0.16 mm | **4.3%** | 🔴 ground **quartz** plate, brittle, **non-stock thickness** |
| radius a | 23.0 MHz/mm | ±0.22 mm | 0.21% | ✅ machined aluminium |
| length L | 14.0 MHz/mm | ±0.36 mm | 0.40% | ✅ machined aluminium |

> 🔴 **The brake is simultaneously the most sensitive handle, the hardest
> material to hold a dimension in, and — at 3.82 mm — not a stock plate.**
> Using it as a tuning element converts a catalogue part into a ground-to-order
> one, and puts the tightest fractional tolerance in the design on the component
> least able to hold it. **That is backwards.**

✅ **The same targets are reachable on the two machined handles alone**, brake
held at a stock 3.00 mm:

| | current | reallocated |
|---|---:|---:|
| radius a | 101.43 | **102.49 mm** |
| length L | 87.67 | **88.61 mm** |
| brake | 3.00 | **3.00 mm — unchanged, stops being a tuning element** |

🔢 System condition det = −334, well posed. Both tolerances are routine metal
machining. **The brake goes back to being a degeneracy brake, which is its job.**

### 2. 🔑 But the retune should not happen yet at all

**The retune target is set by the plasma frequency shift, and that shift is not
yet trustworthy enough to cut metal against.**

| unknown | does it move the retune target? |
|---|---|
| **R12 — plasma filling factor** | 🔴 **YES, directly.** The +21.1 MHz shift comes from a *uniform conductivity filling the whole bore*, an upper bound on plasma volume. A realistic torus shifts less, by an unknown amount. **The entire retune is sized by this number.** |
| **R17 — Sialon outer tube** | 🔴 **YES.** ε 3.78 → ~7–8 on the part carrying 74% of TM₀₂₀'s dielectric energy is a different cavity, not a perturbation |
| R14 — torch tanδ | ❌ moves Q and ignition pressure, not the frequencies |
| R15 — bore mesh convergence | ❌ R10 showed the *shift* is order-robust (+21.11 vs +21.10) even where Q is not |

> ✅ **Sequence: resolve R12 and R17, then optimise once.** Retuning now means
> retuning again after each — and the earlier tuning study already cost a
> 3-mesh convergence programme to establish the offsets it rests on.
>
> ⚠️ **What R11 has already delivered stands and is not wasted:** the design
> point *is* out of band when lit, the retune *is* reachable, and the sensitivity
> method reproduced TE₀₁₁ to **0.04 MHz**. The brake sensitivity was also
> corrected, −26 → **−30.7 MHz/mm** over 3→4 mm, an 18% nonlinearity that was
> not previously measured.

| # | status |
|---|---|
| **R11** | 🟡 **PAUSED pending R12 and R17.** Target and handles both settled; do not cut metal |
| **R12** | ⬆️ **PROMOTED — now blocks the design point.** Annular conducting shell vs uniform bore |
| **R17** | ⬆️ **PROMOTED — Sialon changes ε on the dominant dielectric** |
| 31 | 🟡 **R11 paused — wrong handle, and premature** | Brake is the worst handle (4.3% tolerance, brittle, non-stock). ✅ Reallocated to **a 102.49 / L 88.61, brake stays stock 3.00**. 🔑 But retune target depends on **R12 (filling factor)** and **R17 (Sialon ε)** — resolve those, then optimise once |

### The 3.82 mm run, and why it argues for pausing rather than against it

| | r11 (brake 3.97) | r11b (brake 3.82) |
|---|---|---|
| size-factor | **1.00** | **0.96** ⚠️ |
| TE₀₁₁ | 2.42336 | 2.42656 (**+3.1** vs predicted +0.12) |
| TM₀₂₀ | 2.39568 | 2.39968 (−0.6 vs prediction ✅) |

✅ TM₀₂₀ confirms the corrected **−30.7 MHz/mm** brake sensitivity.

🔴 **TE₀₁₁'s +3.1 MHz is the mesh, not the brake.** The size-factor fallback —
added to survive the order-2 curving SIGABRT — silently dropped 1.00 → 0.96 when
the first attempt failed. From the h-study, that alone raises TE₀₁₁ by
🔢 **+3.5 MHz** (error 36.5 → 33.0 at p = 2.46). **The two runs were never
comparable.**

> ⚠️ **The fallback is a correctness hazard, not just a convenience.** It changes
> the single variable every frequency comparison depends on, and it does so
> *because a mesh failed* — i.e. exactly when attention is elsewhere. ✅ **Record
> the size-factor with every result, and refuse to difference two runs that do
> not share it.**

### 🔑 The scale check that settles the sequencing argument

| quantity | magnitude |
|---|---:|
| retune we are attempting | ~25 MHz |
| **R12 filling-factor unknown** | **~10+ MHz** (the shift is an upper bound) |
| **mesh-density noise, silent** | **~3 MHz** |
| brake sensitivity correction just measured | 4.7 MHz |

> **We are optimising a ~25 MHz adjustment with a ~10 MHz unknown in the target
> and ~3 MHz of uncontrolled noise in the measurement.** The error budget is
> dominated by things not yet resolved. ✅ **Pausing R11 to close R12 and R17
> first is the correct order, and this run demonstrates it rather than
> contradicting it.**
| 32 | 🔴 **Size-factor fallback silently broke comparability** | r11 at 1.00 vs r11b at 0.96 — TE₀₁₁'s +3.1 MHz was **mesh, not brake** (+3.5 predicted from the h-study). ✅ Brake sensitivity −30.7 MHz/mm confirmed on TM₀₂₀. **Record size-factor with every result; never difference across it** |

---

## 2026-08-15 — R12 ✅ the shift is field-weighted, not volume-weighted

Every shift below is a difference between **two solves on the identical mesh** —
a zero-conductivity reference was solved on each case's own mesh, because the
carved geometries meshed at size-factor 1.00 where the plain one needs 0.96.

| case | vol % | shift | shift % | what it isolates |
|---|---:|---:|---:|---|
| full | 100% | +21.1 MHz | 100% | the current model |
| **annular** | **73%** | **+21.2 MHz** | **100%** | 🔑 core removed → **no effect** |
| short | 47% | +16.1 MHz | 76% | axial truncation → real effect |
| **toroid** | **34%** | **+16.3 MHz** | **77%** | the realistic shape |

### 🔑 The two filling factors behave completely differently

> ✅ **Radial filling factor is irrelevant.** Removing the central 4.5 mm — 27%
> of the plasma volume, and precisely the cool sample channel a real discharge
> has — leaves the shift **unchanged**. E_φ ∝ r inside the bore, so the core sits
> where there is nothing to couple to. **A plasma model that omits the central
> channel is not an approximation here; it is exact.**
>
> ⚠️ **Axial extent is what matters, and sub-linearly**: 34% of the volume still
> delivers 77% of the shift.

### 🔴 This softens R11's verdict — the design point is marginal, not out of band

🔢 Scaling by the measured 0.77:

| σ | realistic shift | loaded TE₀₁₁ | margin to 2.5000 |
|---:|---:|---:|---:|
| 10 | 12.7 MHz | 2.4935 | +6.5 MHz |
| 30 | **16.3 MHz** | **2.4971** | **+2.9 MHz** |
| 100 | 18.7 MHz | 2.4995 | +0.5 MHz |

> ✅ **CORRECTION to R11.** It reported the lit cavity as *"out of band by
> 1.9 MHz"* at σ=30. With a realistic plasma shape it is **in band by 2.9 MHz**.
> ⚠️ But thermal drift is ~4 MHz over 100 K, so **0.5–6.5 MHz of margin is
> marginal, not safe.** The retune is still warranted — it is now a **~17 MHz**
> adjustment rather than ~25, and it fixes a thin margin rather than a violation.

### ✅ Measuring the reference beat estimating it

⚠️ I was about to correct the raw numbers by **−3.5 MHz** from the h-study.
The measured per-mesh references moved them by **−1.8, −0.1 and −0.3 MHz**.
A blanket analytic correction would have **overshot by up to 3.4 MHz on a
quantity whose whole answer spans 5 MHz**, and would have made the toroid look
volume-weighted when it is not.

### The error budget R11 was paused for

| term | before R12 | after |
|---|---:|---:|
| filling-factor unknown | ~10 MHz | **~2 MHz** (residual: axial extent, 20–30 mm) |
| mesh-density noise | ~3 MHz, silent | controlled by matched references |
| **retune size** | ~25 MHz | **~17 MHz** |

✅ **The dominant unknown in the retune target is closed.** R17 (Sialon ε)
remains before R11 reopens.
| 33 | ✅ **R12 — shift is FIELD-weighted, not volume-weighted** | Removing the cool core (27% of volume) changes the shift **not at all**; axial truncation does. Realistic toroid **+16.3 MHz = 77%**. 🔴 **Corrects R11: design point is in band by 2.9 MHz, marginal not violated.** Retune now ~17 MHz |

---

## 2026-08-15 — 🔴 R17: Sialon looks disqualifying on loss, not on permittivity

I opened R17 worried about **ε** (3.78 → ~7–8 forcing a retune). ⚠️ **The
permittivity is the lesser problem. The loss tangent may rule it out.**

✅ Published SiAlON/h-BN composite: **ε 3.51–3.69, tanδ 0.9–3.1 × 10⁻³** at
7–18 GHz (Hakki-Coleman post-resonator). **That is 9–31× the loss tangent of
fused silica**, on the part carrying **74%** of the ignition mode's dielectric
loss.

🔢 Consequence, via the analytic model R9 validated to 1.000×:

| outer tube | tanδ | Q_diel | Q_total | field | **2× margin** |
|---|---:|---:|---:|---:|---:|
| fused silica, assumed | 1.0×10⁻⁴ | 87,184 | 23,235 | 7.63 kV/cm | **127 Torr** |
| fused silica, realistic | 2.0×10⁻⁴ | 50,018 | 19,394 | 6.97 | 116 Torr |
| **SiAlON, best quoted** | 0.9×10⁻³ | 12,554 | 8,991 | 4.75 | 🔴 **79 Torr** |
| **SiAlON, worst quoted** | 3.1×10⁻³ | 3,743 | 3,348 | 2.90 | 🔴 **48 Torr** |

> 🔴 **A Sialon outer tube costs 48–79 Torr against 127.** That pushes the
> ignition requirement below the single-stage diaphragm floor and into
> two-stage territory — the very conclusion R7 withdrew — and it does so for a
> *fouling* benefit. ⚠️ **And this is before** bulk Sialon's higher ε (~7–8 vs
> the composite's 3.6) pulls more field into the tube and raises p_elec further.

### ⚠️ Three caveats, and they matter

1. **The quoted material is a SiAlON/h-BN composite, not the torch ceramic.**
   Glass Expansion does not publish dielectric data for their Sialon. h-BN is
   added for machinability and is not necessarily present in a torch tube.
2. **Measured at 7–18 GHz, not 2.45.** Dielectric loss in ceramics generally
   *falls* with frequency in this range, so 2.45 GHz could be worse, not better.
3. **ε 3.51–3.69 for the composite is quartz-like**, which contradicts the ~7–8
   expected for bulk β-SiAlON — further evidence the quoted material is not what
   a torch is made of.

> ⚠️ **So this is a red flag, not a verdict.** But it inverts the question: R16
> framed Sialon as *"a way to restore the lever"*. **It is more likely a way to
> destroy the ignition margin**, and the burden of proof is now on Sialon.

### 🔑 What this means for the architecture

> **This is a genuine AMIP-specific disadvantage, and the first one found.**
> At an ICP's 27–40 MHz a lossy torch ceramic costs nothing — the coupling is
> inductive and the material is electrically invisible. **At 2.45 GHz the outer
> tube is 74% of the ignition mode's dielectric loss**, so the standard
> high-TDS remedy may simply be unavailable to a microwave plasma.
>
> ⚠️ `architecture-comparison.md` §2b lists torch devitrification as
> architecture-independent. **It is worse than architecture-dependent: AMIP may
> be barred from the standard fix.** MP-AES shares this exposure; MICAP does too.

| # | question | status |
|---|---|---|
| **R17** | ⚠️ **Sialon: red flag on tanδ.** Need the *actual* torch ceramic's loss at 2.45 GHz before it can be considered. ε sweep running separately | open — **burden now on Sialon** |
| **R18** | **Does devitrification actually matter at AMIP's power/flow?** If the quartz survives, the Sialon question is moot. Cheaper to answer than R17 | open |
| 34 | 🔴 **R17 — Sialon is a loss problem, not an ε problem** | Published SiAlON tanδ **0.9–3.1e-3 = 9–31× fused silica**, on the part carrying 74% of ignition dielectric loss → **48–79 Torr vs 127**. ⚠️ Composite data, not torch ceramic. 🔑 **First genuine AMIP-specific disadvantage: the standard high-TDS fix may be barred at 2.45 GHz** |

### R17 permittivity — and a mode-identifier that was breaking its own rule

⚠️ **`sialon6` was aborted** by a foreground timeout ("Abort is in progress").
Its −126.3 MHz was **truncated-postpro garbage**; the directory is deleted so it
cannot be mistaken for data. `sialon8` ran to completion.

🔴 **`dq.identify` was violating the rule this file states twice.** It returned
`"TE011" if pm > pe else "TM020"` — a *ratio* of two quantities that can both be
small. In this sweep it labelled peaks with **boreH 0.05% and boreE 0.004%** as
TE₀₁₁, when the real modes carry **2.2%** and **4.0%**. That is precisely the
error that cost a full brake sweep in §8.

> ✅ Replaced with **absolute thresholds** (boreH ≥ 1.0% → TE₀₁₁, boreE ≥ 2.0% →
> TM₀₂₀, otherwise **OTHER**). Regression-tested: sigdrv, tilt45, tiltvp and
> o2drv2 all unchanged; sialon8 now correctly reports two real modes and two
> OTHERs. **The rule was written down and the code still broke it** — writing a
> rule in a findings file does not enforce it.

### 🔑 The result: torch permittivity is a TM₀₂₀-only handle

| | ε 3.78 | ε 8.00 | Δ |
|---|---:|---:|---:|
| TM₀₂₀ (8.523% of E in torch) | 2.42368 | 2.31065 | **−106.6 MHz** |
| TE₀₁₁ (0.232% of E in torch) | 2.44920 | 2.44605 | **−3.1 MHz** |

🔢 **A 34× ratio in response against a 37× ratio in stored energy fraction** —
the two agree, which is the check that licenses the result.

> 🔴 **At ε = 8 the ignition mode falls to a converged 2.3304 GHz — 70 MHz below
> the ISM band.** Recovering it needs a ≈ 98.4 mm (−3.0 mm) plus L compensation:
> **a different cavity, not a substitution.**
>
> ✅ **But this is also a design lever worth having.** Torch material moves
> TM₀₂₀ 34× more than TE₀₁₁, so the mode *split* — the thing the brake exists to
> set — is partly a materials choice. ⚠️ And a vulnerability: any change of torch
> supplier or grade that moves ε shifts the ignition mode and not the operating
> one.

### ⚠️ The honest verdict on R17

**The two published figures for "SiAlON" disagree with each other**: the h-BN
composite measures **ε 3.51–3.69** (quartz-like, harmless) while bulk β-SiAlON is
expected at **~7–8** (70 MHz out of band). Combined with the tanδ spread, the
plausible range for a Sialon outer tube runs from **"drop-in replacement"** to
**"different instrument"**.

> ⚠️ **R17 cannot be closed from literature.** It needs the actual ceramic's ε
> and tanδ at 2.45 GHz from Glass Expansion. ✅ **R18 is the cheaper question and
> should come first** — if quartz survives the matrix, none of this is needed.
| 35 | 🔴 **R17 ε sweep — torch material is a TM₀₂₀-only handle** | ε 3.78→8 moves **TM₀₂₀ −106.6 MHz, TE₀₁₁ −3.1** (34× vs 37× energy ratio ✓). At ε=8 ignition falls **70 MHz out of band**. 🔴 **dq.identify was using a ratio — fixed to absolute thresholds.** sialon6 aborted, data deleted |

---

## 2026-08-15 — 🔑 Arc ignition reconsidered: it may delete the whole pressure programme

Raised as a strategy question: the Torr figure keeps moving, and **even a solid
Torr leaves the TM₀₂₀ → TE₀₁₁ transition unresolved.** Both halves are right.

### ⚠️ First: the settled "striker" entry does NOT close this off

§6 marks the striker **"negative — do not retry"**, and that could easily be read
as ruling out ignition aids generally. **It does not.** The striker was a
*passive* metal ridge shaping the existing 2.45 GHz field; it failed because
near-field enhancement decays over ~r_tip and the quartz keeps metal ≥4 mm away.

🔢 An **active** Tesla-coil igniter supplies its own 10–30 kV. Across that same
4 mm standoff that is **25–75 kV/cm against air's ~30 kV/cm** — it flashes over.
✅ **This is standard ICP practice and has been for sixty years:** the coil is
touched to the *outside* of the torch. **The wall that kills passive enhancement
is not a barrier to 20 kV.** Different mechanism, different verdict.

### 🔢 What arc ignition would delete

| deleted | what it was costing |
|---|---|
| Vacuum pump + valve | $0.3–5k, sized by an unchosen gas flow (R13) |
| Exhaust seal on an open torch | novel, unbuilt, no cost basis |
| **The 760 → 127 Torr ramp** | 🔴 **the top unquantified risk in the project** |
| The whole Torr uncertainty chain | quartz grade 101–134 Torr; Sialon 48–79; R14, R17 |
| **TM₀₂₀ as a required in-band mode** | the band packing R11 is fighting |

> 🔑 **And it addresses the transition objection directly.** The mode-shift scheme
> exists *because* TM₀₂₀ concentrates bore E for breakdown. **A spark supplies
> breakdown, so one could ignite directly on TE₀₁₁ and never transition at all.**
> That removes the mode-shift sequence, TM₀₂₀'s band placement, and the
> amplifier's 16–24 MHz transient retune in one move.
>
> ✅ It also relaxes the brake: its thickness would set **mode purity only**,
> not TM₀₂₀'s frequency — which answers the tolerance objection that paused R11,
> since the 30.7 MHz/mm handle stops being load-bearing.

### The crux moves, and it moves onto ground we already stand on

**The ignition margins in this file are BREAKDOWN thresholds.** A spark supplies
seed electrons, so the bar becomes **sustaining**, which is far lower — and
`ignition-study.md` §2's structural claim (sustaining ≪ breakdown) is *already*
what the pressure-ramp route depends on.

> ⚠️ **So arc ignition does not add an unknown; it removes one.** Both routes need
> "can it sustain at atmospheric". Only the pressure route *additionally* needs
> "can it survive a 6× pressure ramp while sustaining".

✅ **The evidence on sustaining is the comparison we already made**: Q × η =
**41.5 (AMIP) vs 43.0 (ring)**, and MICAP demonstrably sustains N₂ at
atmospheric. Same figure of merit, within 3.5%.

### ⚠️ The honest cost

**MICAP uses argon *and* a spark** — 8 s of argon plus a spark, then changeover.
If AMIP needs argon too, the "no argon cylinder" differentiator is lost. ⚠️ But
it is lost anyway if the pressure ramp fails, and the ramp is the thing nobody
can currently defend. **Arc ignition trades a novel unquantified risk for a
proven one with a known cost (a cylinder).**

✅ Patent position: spark ignition of plasma torches is ancient prior art, and
`patent-landscape.md` §5 records MICAP's own sequence as published. Nothing here
suggests a claim to work around.

| # | question | status |
|---|---|---|
| **R19** | **Cost the arc-ignition architecture against reduced-pressure**, and decide. Deletes the top risk; may re-add an argon cylinder | 🔑 **open — architecture-level decision** |
| **R20** | **Can TE₀₁₁ alone sustain a spark-seeded N₂ plasma at atmospheric?** If yes, TM₀₂₀ and the whole mode-shift scheme become optional | open |
| 36 | 🔑 **Arc ignition may delete the pressure programme** | ⚠️ The settled striker entry does NOT rule it out — passive field-shaping vs active 20 kV, which flashes 4 mm easily. Deletes vacuum system, **the ramp (top risk)**, the Torr chain, and possibly **TM₀₂₀ and the mode transition**. Crux moves from breakdown to sustaining, which both routes already need |

---

## 2026-08-15 — Capacitive external electrode: assessment

Proposal: a conductive band around the outside of the quartz torch, fired with a
10 kV+ HF pulse, capacitively seeding electrons through the wall.

### ✅ What is right, and one part is the strongest argument yet

🔢 **The breakdown physics works with room to spare.** 10 kV across the 1.5 mm
torch wall is 67 kV/cm in the quartz; displacement continuity (D continuous, so
E_gas = ε_q/ε_gas × E_quartz) puts **~252 kV/cm in the gas against ~30 kV/cm
needed.** Not marginal.

✅ **The fouling argument is correct and is the best reason to prefer this over a
manual Tesla coil.** §6 already established that metal cannot go inside the
torch — erosion in the sample path becomes permanent spectral background. An
external electrode never meets the Mehlich-3 aerosol, the acid fumes, or the
salts. **It answers a constraint we had already proved binding**, and it is an
integrated instrument feature rather than a bench procedure.

### 🔴 The problem: a closed band is a shorted turn to TE₀₁₁

**TE₀₁₁'s electric field is azimuthal.** A conducting ring coaxial with the axis
lies *along* E_φ, and tangential E must vanish on a conductor. **A full band
short-circuits the very field that drives the plasma.**

🔢 E_φ ∝ J₁(χ′₀₁r/a)·sin(πz/L), as a fraction of peak at the torch OD:

| position | fraction of peak E_φ |
|---|---:|
| mid-plane (the "active microwave zone") | 🔴 **31.9%** |
| 10 mm from the end cap | 11.2% |
| **5 mm from the end cap** | ✅ **5.7%** |

> ✅ **"Just below the active microwave zone" is the right instinct — it needs to
> go further.** Placement should be *at the axial E-null*, within ~5 mm of an end
> cap, where sin(πz/L) → 0.
>
> 🔑 **Better still: recess the electrode into the end cap itself.** The end cap
> is already grounded metal sitting exactly at the E₀ null. An insulated ring
> around the torch bore, set into it, is at the null **by construction** and
> mechanically integrated rather than added.
>
> ✅ **And put it at the UPSTREAM end.** Gas flows from z₀ upward into the plasma
> zone, so seed electrons are *carried* into the active region. Seeding 24 mm
> below the zone costs nothing when the flow does the transport.

⚠️ A *split* ring avoids the short but becomes a split-ring resonator with its
own resonance and parasitic coupling — likely worse than a closed ring correctly
placed.

### ⚠️ Two engineering costs the proposal does not price

1. **RF isolation.** A 10 kV feed entering a 1 kW 2.45 GHz cavity makes the
   electrode an antenna: microwave power will couple *out* into the pulse
   generator. Needs a low-pass choke rated for kV standoff at 2.45 GHz. Standard,
   but not free, and it is the part most likely to fail in service.
2. 🔴 **"copper or a carbon brush" — copper only.** Carbon is a *microwave
   absorber*; a carbon electrode inside the cavity would heat and dump power.

### Verdict

**Sound, and preferable to the pressure route** — it deletes the ramp, the vacuum
system and the Torr chain, and it is fouling-immune by construction. ⚠️ **The
band position is not a detail; it is the difference between working and killing
Q.** This is directly simulable with the tooling used for the viewport study
(R6): add the band as PEC, sweep axial position, measure ΔQ and Δf on TE₀₁₁.

| # | question | status |
|---|---|---|
| **R21** | **Simulate the capacitive electrode: ΔQ and Δf on TE₀₁₁ vs axial position.** Same method as R6's viewport sweep. Decides band vs end-cap-recessed | open — cheap, directly answers the design |
| 37 | ✅ **Capacitive external electrode assessed** | Breakdown ample (**252 kV/cm in gas vs 30 needed**); fouling-immune ✓. 🔴 But a closed band is a **shorted turn to TE₀₁₁'s azimuthal E** — 31.9% of peak at mid-plane, 5.7% near the end cap. **Recess it into the upstream end cap** (E-null by construction, flow carries electrons in). Copper not carbon |

---

## 2026-08-15 — 🔴 R22 refutes the topology objection I raised

I argued that TM₀₂₀ ignites a central column while TE₀₁₁ needs an annulus, so the
mode-shift handoff might not close. **Measured, that is wrong.**

| | core-only (r<4.5mm) | full bore | annular |
|---|---:|---:|---:|
| frequency shift | **+3.45 MHz** | +21.1 MHz | +21.2 MHz |
| Q₀ | **399** | 192 | — |
| **power to plasma** | ✅ **99.1%** | 99.6% | — |

🔢 **TE₀₁₁ delivers 99.1% of its power to a plasma sitting entirely inside its own
null region.** Q collapses 44,985 → 399.

> 🔴 **The error was mine, and it is the project's recurring one.** R12 showed the
> core contributes **0% of the frequency shift**, and I extrapolated that to
> *power coupling*. They are different integrals:
> - **shift** is reactive — stored energy, weighted by volume
> - **Q** is dissipative — ∫σ|E|²dV over the conductor, skin-limited
>
> **A region can be reactively negligible and dissipatively dominant**, and the
> core is exactly that. Inferring one from a measurement of the other is the same
> mistake as comparing Q_wall to Q_total (R8) and closed forms to the wrong
> quantity (R2/R5).

✅ **So the mode-shift transition is not broken by topology.** TM₀₂₀ can ignite a
column and TE₀₁₁ can pick it up at 99% coupling. ⚠️ The plasma still has to
redistribute toward the annulus, and nothing here models that transient — but the
handoff has a mechanism, which is what I claimed it lacked.

### 🔑 R20 reframed: the real question was never breakdown

Arc ignition and reduced pressure both address **breakdown**. Neither addresses
the step that actually costs eight seconds on a shipping instrument:

| | limited by | does a spark help? |
|---|---|---|
| **A. Breakdown** — 1 electron → conductive gas | field threshold | ✅ deletes it |
| **B. Thermal bootstrap** — weakly-ionised → LTE ~5000 K | **power balance** | ❌ no |

🔢 N₂ carries sinks argon does not: **dissociation 9.8 eV** plus a vibrational
ladder, on top of 15.6 eV ionisation. Argon has **no dissociation channel at
all**.

> ✅ **The published MICAP sequence is "8 s of argon PLUS a spark."** If breakdown
> were the only problem, the spark alone would suffice and the argon would be
> unnecessary. **The argon is there for (B), and it runs for eight seconds.**
>
> ⚠️ **So arc ignition probably does not delete the argon cylinder** — and neither
> does reduced pressure. (B) is common to both routes and unaddressed by either.

**What arc ignition still wins, with argon retained:** the 760→127 Torr ramp (the
top unquantified risk), the pump and novel exhaust seal ($0.3–5k), the whole Torr
uncertainty chain (R14, R17, quartz grade), and TM₀₂₀'s in-band requirement.

> **That is still a strong case — but it is a case for simplification, not for
> the "all-electronic, no cylinder" differentiator.** ⚠️ That differentiator was
> the architectural argument in `coupling-architecture.md` §0, and (B) puts it in
> doubt regardless of which ignition route is chosen.

| # | status |
|---|---|
| ~~R22~~ ✅ | **closed — topology objection refuted.** TE₀₁₁ couples 99.1% to a core plasma |
| **R20** | 🔑 **reframed: the binding question is the N₂ thermal bootstrap, not breakdown.** Both routes need it; nothing in AMIP addresses it |
| **R23** | **Can the argon step be deleted at all?** If not, "all-electronic ignition" leaves the architecture case and only cost/simplicity remain | open |
| 38 | 🔴 **R22 — my topology objection was wrong** | TE₀₁₁ delivers **99.1%** of power to a core-only plasma (Q 44,985→399) despite +3.45 MHz shift. Extrapolated reactive→dissipative; **different integrals**. ✅ Mode handoff has a mechanism. 🔑 **R20 reframed: breakdown was never the binding step — N₂ thermal bootstrap is, and neither route addresses it** |

---

## 2026-08-15 — 🔑 Pulsed energy store for the thermal bootstrap

Prompted by an analogy to the banned Formula E twin-MGU + flywheel: **a store
decouples a peak demand from a continuous supply.** The N₂ thermal bootstrap (R20
step B) is exactly that mismatch, and it is the step neither arc ignition nor
reduced pressure addresses.

### 🔢 The bootstrap is much smaller than it sounds

Energy to bring N₂ from 300 K to LTE ≈ 5000 K: sensible 6,110 J/g plus
dissociation (9.79 eV/molecule; **30% dissociated** assumed) 10,119 J/g =
**16,229 J/g**.

| zone | volume | mass | **energy** |
|---|---:|---:|---:|
| realistic toroid (R12) | 4,935 mm³ | 5.6 mg | **91 J** |
| full plasma zone | 14,438 mm³ | 16.4 mg | **267 J** |

🔢 **90–270 joules.** For scale, 2.7 mF at 450 V is 273 J — a capacitor bank, not
an engineering programme.

### 🔑 And the deadline is set by gas flow, which is ours to choose

The hot gas must be made faster than the flow replaces it:

| ignition flow | residence | power needed for the toroid |
|---:|---:|---:|
| 20 slm (full analytical) | 20 ms | 4.5 kW |
| 10 slm | 41 ms | 2.2 kW |
| **5 slm** | **82 ms** | ✅ **1.1 kW** |
| 2 slm | 204 ms | 0.4 kW |

> ✅ **At reduced ignition flow the bootstrap needs ~1 kW — which the amplifier
> already has.** No store, no pulse, no argon. **There is no reason to ignite at
> full analytical flow**, and R13 already wanted a reduced ignition flow to size
> the pump. **The same choice serves both.**

### ⚠️ But energy is necessary, not sufficient — and this is why argon exists

**The bottleneck is kinetic, not energetic.** Electron energy in N₂ goes
preferentially into the **vibrational ladder**, which relaxes to heat slowly
(V-T relaxation). Argon has **no vibrational modes and no dissociation channel**,
so electron energy goes straight to ionisation and the plasma reaches LTE fast.

> ⚠️ **That is the real reason MICAP runs 8 s of argon**, and the energy budget
> above cannot see it. A path can be energetically open and kinetically shut.
>
> ✅ **This is where the flywheel idea genuinely earns its place**: a *pulse*
> delivers energy faster than V-T relaxation can bleed it away. The argument for
> a store is not "we lack the joules" — at 5 slm we do not — it is **"we must
> beat a slow loss channel"**. That is precisely what a peak-power store buys.

🔢 A 270 J store into 20 ms is 13 kW — 13× the CW rating, from a capacitor bank.
At 10 kW the bore field is √10 = 3.16× higher, which per §"pressure is the lever"
also reaches **1× breakdown margin at atmospheric**, so the same pulse could
cover step (A) as well and delete the spark too.

| # | question | status |
|---|---|---|
| **R24** | **Bench: does a pulsed 5–15 kW burst bootstrap N₂ without argon?** Energy budget says yes at reduced flow; V-T kinetics say maybe not. **Not simulable here** — needs the bench | 🔑 open — would delete argon, vacuum AND spark |
| **R25** | **Set the ignition gas flow at 2–5 slm** and re-derive both the pump (R13) and bootstrap power from it. One decision closes two open items | open — cheap |
| 39 | 🔑 **Pulsed store for the thermal bootstrap** | Bootstrap is only **91–267 J**. ✅ At **5 slm ignition flow it needs 1.1 kW — the amplifier already has it.** ⚠️ But the bottleneck is **kinetic** (N₂ vibrational ladder), which is why argon exists — and that is exactly what a peak-power pulse beats. A 270 J/20 ms burst = 13 kW, also enough for breakdown at atmospheric |

---

## 2026-08-15 — 🔑 The pulse that beats the kinetics also steepens the ramp

The MGU frequency-ramp analogy points at something we have already measured.
**As the plasma builds, the cavity resonance ramps +16 to +24 MHz** (R10, R12).
That ramp is the control problem, and its steepness is set by how fast we force
the bootstrap.

| bootstrap duration | ramp rate | one 13 MHz linewidth every |
|---:|---:|---:|
| 20 ms (20 slm, or a forced pulse) | **1.05 MHz/ms** | 12 ms |
| 50 ms | 0.42 MHz/ms | 31 ms |
| **82 ms (5 slm)** | ✅ **0.26 MHz/ms** | 51 ms |

### The control loop has a comfortable window, but it must be designed

| bound | timescale | constraint |
|---|---:|---|
| cavity fill | 2.9 µs | loop slower than **345 kHz** |
| plasma thermal | 20 ms | loop faster than **50 Hz** |

✅ **1–10 kHz sits comfortably between.** ⚠️ But power and frequency are
*coupled* — more power → more plasma → f₀ shifts → mismatch → less power. A badly
tuned loop can limit-cycle on exactly that path.

### 🔢 And the droop is not free

If a bank feeds the amplifier rail at 13 kW for 20 ms (0.578 C at 450 V):

| bank | stored | droop | RF power falls to |
|---|---:|---:|---:|
| 2.7 mF (sized for energy alone) | 273 J | **48%** | 28% |
| 12.8 mF (sized for 10% droop) | **1,296 J** | 10% | 81% |

⚠️ **Sizing for energy is not sizing for a flat pulse.** Holding the rail within
10% costs **4.7× the stored energy**. The droop profile does roughly match the
demand profile — most power is wanted while the gas is cold — so the ramp may be
a feature, but it is a *second* ramp coupled to the frequency one.

### 🔑 The tension worth naming

> **A fast pulse beats the V-T kinetics. A fast pulse also steepens the frequency
> ramp, deepens the droop, and tightens the loop.** The two requirements pull
> against each other.
>
> ✅ **And the slow route needs no bank at all**: at 5 slm the bootstrap wants
> 1.1 kW over 82 ms — within the CW amplifier — with a 0.26 MHz/ms ramp a modest
> loop tracks easily. **The flywheel is the fallback for if the kinetics refuse
> the slow route, not the primary plan.**

⚠️ Which route is available is a *kinetics* question (R24) that this harness
cannot answer. **But the ordering is now clear: try slow-and-cheap first, and
hold the bank in reserve.**

| # | question | status |
|---|---|---|
| **R26** | **Control-loop design for the ignition transient**: track 0.26–1.05 MHz/ms through a coupled power/frequency plant without limit-cycling | open — the amplifier spec R10 said did not exist |
| 40 | 🔑 **Fast pulse beats kinetics but steepens the ramp** | f₀ ramps **+16–24 MHz** as plasma builds: **1.05 MHz/ms at 20 ms, 0.26 at 82 ms**. Loop window 50 Hz–345 kHz. ⚠️ Flat-pulse bank costs **4.7× the energy** of an energy-sized one (1,296 J vs 273). ✅ **Slow route needs no bank — 1.1 kW CW at 5 slm.** Bank is the kinetics fallback |

---

## 2026-08-15 — R21 ✅ the electrode is nearly free at the end cap and catastrophic at mid-plane

| case | position | predicted E_φ | size-f | Δf | **ΔQ** |
|---|---|---:|---:|---:|---:|
| elnone | — | — | 0.96 | — | — |
| **el05** | **5 mm from end cap** | 5.7% | 1.06 | −0.2 MHz | ✅ **−0.7%** |
| el10 | 10 mm | 11.2% | 1.00 | +1.9 MHz | −2.9% |
| el20 | 20 mm | 21% | 0.96 | +10.2 MHz | −7.8% |
| **elmid** | **mid-plane** | 31.9% | 1.00 | 🔴 **−85.9 MHz** | 🔴 **−60.6%** |

🔢 **A factor of 87 in Q penalty between best and worst placement.** ΔQ tracks the
predicted E_φ exposure monotonically, so **the shorted-turn analysis was right and
placement is the whole answer.**

⚠️ **The mid-plane case is not a perturbation at all.** −85.9 MHz and −60.6% mean
the band has *restructured* the mode, not loaded it — a shorted turn at the E_φ
maximum forces a node where the mode had none. Between 5 and 20 mm the response
is perturbative and roughly linear in exposure; at mid-plane it stops being a
perturbation. **The trend cannot be extrapolated across that boundary.**

> ✅ **Design conclusion: recess the electrode into the end cap, or place it
> within ~5 mm of one.** There it costs **under 1% of Q** — cheaper than the
> 25 mm radial viewport (0.9%) that is already accepted in the design. ⚠️ At the
> "just below the active zone" position the proposal originally suggested
> (~20 mm), it costs 7.8%, and anywhere near mid-plane it destroys the mode.

⚠️ `el05` meshed at size-factor 1.06 against the baseline's 0.96, so its −0.7% is
approximate; a matched 0.96 re-run is going. **The conclusion does not depend on
it** — 0.7% vs 60.6% is not a margin call — but the headline number should be a
clean difference. ⚠️ *The size-factor fallback silently broke comparability for a
third time. It is recorded per-result, which is how this was caught, but the
helper still does not **enforce** a common factor across a sweep.*

### What this unlocks

With the electrode nearly free at the end cap, the assembled architecture holds:

| step | mechanism | cost |
|---|---|---|
| Breakdown | capacitive electrode, ~2 nF at 10 kV, 0.09 J | a few dollars, <1% of Q |
| Bootstrap | 1 kW CW at 5 slm ignition flow, 82 ms | already in the amplifier |
| Operation | TE₀₁₁, tracked | unchanged |

✅ **No vacuum. No mode transition. No TM₀₂₀ band requirement.** ⚠️ Argon retained
until R24 settles the V-T kinetics, and the flywheel held in reserve for that.

| # | status |
|---|---|
| ~~R21~~ ✅ | **closed — recess into the end cap, <1% of Q** |
| **R27** | **Make the mesh helper enforce one size-factor across a sweep**, not merely record it. Third recurrence | open — tooling |
| 41 | ✅ **R21 — electrode placement is the whole answer** | **−0.7% at 5 mm from the end cap, −60.6% at mid-plane** (Δf −85.9 MHz — mode restructured, not perturbed). Factor of **87**. ✅ Cheaper than the accepted 25 mm viewport. Recess into the end cap. 🔴 Size-factor fallback broke comparability a **third** time (R27) |

---

## 2026-08-15 — R11 re-scoped: the electrode architecture dissolves the band-packing problem

**R11 was hard because three constraints were competing for 100 MHz.** Igniting
directly on TE₀₁₁ removes one of them entirely.

| | constraints |
|---|---|
| **Old** | TM₀₂₀ in band **and** TE₀₁₁ cold in band **and** split ≥ 2.5 loaded linewidths |
| **New** | **LIT** TE₀₁₁ in band with margin. TM₀₂₀ only has to stay out of the way. |

> 🔑 **That third constraint is what forced the brake into service as a tuning
> handle** — and the brake is the worst handle available (4.3% tolerance on a
> ground quartz plate). Removing the constraint returns the brake to a stock
> 3 mm part whose only job is breaking degeneracy.

### Proposed retune, on the two machined handles only

Using R12's realistic **+16.3 MHz** plasma shift:

| | current | **re-scoped** |
|---|---:|---:|
| radius a | 101.43 mm | **102.72 mm** (+1.29) |
| length L | 87.67 mm | **88.86 mm** (+1.19) |
| brake | 3.00 mm | ✅ **3.00 mm — stock, not a tuning element** |

**Band layout:**

| | frequency | margin |
|---|---:|---|
| TM₀₂₀ cold | 2.4150 | 15.0 MHz above band bottom |
| TE₀₁₁ cold | 2.4487 | — |
| **TE₀₁₁ LIT** | **2.4650** | **35.0 MHz below band top** |
| cold split | 33.7 MHz | |

⚠️ **TM₀₂₀ is kept in band deliberately.** It costs nothing under the new
constraint set, and it preserves mode-shift ignition as a fallback if the
electrode disappoints. **Do not push it out of band until the electrode is
demonstrated** — that would foreclose the alternative for no gain.

### Not run yet, and deliberately

R11 remains paused per the standing decision to close unknowns before
optimising. ⚠️ The only *frequency-relevant* unknown left is **R17 (torch ε, if
Sialon)** — R14's tanδ moves Q, not frequency, and R24's kinetics move neither.
**And R18 is the prior question**: if quartz survives the matrix, Sialon never
arises and R11 can be run immediately.

| # | status |
|---|---|
| **R11** | 🟡 paused — **but the target and handles are now settled and simpler.** Blocked only on R18 → R17 |
| ~~R27~~ ✅ | `meshsweep.py`: enforces ONE size-factor across a sweep, or fails loudly. Never returns a mixed-density set |
| 42 | 🔑 **R11 re-scoped by the electrode architecture** | Dropping TM₀₂₀ as a required in-band mode removes the third constraint — the one that forced the brake into tuning service. New target **a 102.72 / L 88.86 / brake stock 3.00**, lit TE₀₁₁ at 2.4650 with 35 MHz top margin. TM₀₂₀ kept in band to preserve the fallback |
| 43 | ✅ **R27 — meshsweep.py enforces a common size-factor** | Finds the one factor that meshes every case in a sweep, or fails loudly. Ends the three-time recurrence of silently mixed mesh densities |

---

## 2026-08-15 — 🔑 R18 ✅ forces ceramic; R17 flips ✅ because MP-AES already ships it

### R18: devitrification is decisive for this matrix

✅ Quartz devitrifies above its 573 °C transition in the presence of valence<4
elements — **Na, K, Ca, Li explicitly named** — at a threshold of
**>1000 mg/L** of group I/II.

🔢 Our matrix is Mehlich-3, ~2% TDS = **20,000 mg/L**, **Ca-dominated**, and the
extractant exists *precisely to extract Ca, K and Mg*. Even at 10% group I/II we
are **2× over threshold**, and realistically far more.

| | published lifetime |
|---|---:|
| quartz, significant devitrification | **24 h** |
| quartz at 10% NaCl, badly degraded | 6 h |
| **ceramic outer tube** | ✅ **>900 h, "years"** |

> 🔴 **Quartz is not viable for continuous operation on this matrix.** R18
> answered: devitrification matters, and it forces a ceramic outer tube.
> ⚠️ `architecture-comparison.md` §2b listed devitrification as
> architecture-independent and therefore not a differentiator. It is not a
> differentiator — but it is not *ignorable* either, and it drives a material
> choice with large electromagnetic consequences.

### 🔑 R17 flips: Sialon is already used in a 2.45 GHz microwave plasma

✅ **Glass Expansion's D-Torch with a Sialon ceramic outer tube is sold for
MP-AES** — which is a 2.45 GHz microwave plasma, the same regime as AMIP. The
vendor states the ceramic tube **"produces a hotter, more robust plasma"** and
lasts *years* where quartz lasts hours. Agilent likewise offers an inert torch
for high-TDS work on the 4210.

> ✅ **That is the empirical answer R17 could not get from literature.** My
> concern rested on a **SiAlON/h-BN composite** measuring tanδ 0.9–3.1×10⁻³ — a
> different material, and the composite's ε of 3.5–3.7 (quartz-like, contradicting
> bulk β-SiAlON's ~7–8) was already a hint it was not torch ceramic. **A shipping
> product in the same frequency band settles it: ceramic is compatible.**

🔢 **And our own ε sweep supports the vendor's "hotter plasma" claim:**

| ε | mode | boreE % | **boreH %** | Q₀ |
|---:|---|---:|---:|---:|
| 3.78 | TE₀₁₁ | 0.062 | 2.198 | 45,640 |
| **8.00** | TE₀₁₁ | 0.063 | ✅ **2.620** | 44,966 |

**Bore magnetic fraction rises 19.2% for 1.5% of Q** — and for an inductively
coupled plasma the bore H is the driving quantity. ⚠️ At quartz tanδ; Sialon's
true loss is still unmeasured, but the sign of the ε effect is favourable, not
adverse as R17 assumed.

### 🔑 The design implication

> **Design the cavity around a ceramic outer tube from the start.** ε 3.78 → 8
> moves TM₀₂₀ **−106.6 MHz** — that is a different cavity, not a retrofit. Tuning
> for quartz and then substituting ceramic would put the ignition mode 70 MHz out
> of band.
>
> ⚠️ **This changes R11's target.** The re-scoped retune (a 102.72 / L 88.86)
> assumed quartz. It must be re-solved for the ceramic's ε once that value is
> known — which is now the single blocking unknown.

| # | status |
|---|---|
| ~~R18~~ ✅ | **closed — quartz not viable, ceramic forced** |
| **R17** | ✅ **compatibility settled by a shipping product.** Reduced to: *what are the actual ε and tanδ of the torch Sialon?* Vendor datasheet |
| **R11** | 🟡 paused — target must be re-solved for ceramic ε, not quartz |
| 44 | 🔑 **R18 forces ceramic; R17 flips favourably** | Quartz devitrifies in **24 h** on a Ca-dominated 2% TDS matrix (threshold 1000 mg/L, we are ≥2× over); ceramic lasts **>900 h**. ✅ **Sialon outer tubes already ship for MP-AES at 2.45 GHz** — compatibility settled empirically. Our ε sweep agrees: bore **H +19.2%** for 1.5% of Q. 🔑 **Design the cavity for ceramic from the start** — ε 3.78→8 moves TM₀₂₀ −106.6 MHz |

---

## 2026-08-15 — 🔴 The brute-force RF pulse is dead, but for a reason nobody had identified

An external analysis argued against dumping 8 kW of RF into the unlit cavity.
**Its conclusion is right and two of its three arguments are wrong.** The real
objection is one neither it nor this file had checked.

### ❌ "Impedance void — the unlit gas is an insulator, so ~100% reflects"

**Measured, the unlit cavity absorbs 78–91% of incident power at resonance:**

| run | mode | \|S11\| | absorbed |
|---|---|---:|---:|
| sigdrv | TE₀₁₁ | −6.67 dB | **78%** |
| tilt45 | TM₀₂₀ | −10.56 dB | **91%** |
| tilt45 | TE₀₁₁ | −10.68 dB | **91%** |

⚠️ **A resonator's walls are the load.** Q₀ = 23,170 unlit means the silver
dissipates the power; the gas is irrelevant to the match. Reflection approaches
100% only *off* resonance — which is a **tracking** problem on a 211 kHz
linewidth, not an impedance void.

### ❌ "TE₀₁₁ will break down the quartz walls before igniting the gas"

🔢 E_φ ∝ J₁(χ′₀₁r/a) peaks at **r = 48.7 mm, in open air**:

| location | fraction of peak |
|---|---:|
| bore edge (8.5 mm) | 27.2% |
| torch outer wall (10 mm) | 31.9% |
| **cavity maximum (48.7 mm)** | **100%** |

**The field at the torch wall is 3.1× *lower* than the cavity maximum.** The
failure mode is real but mislocated — nothing shatters the torch first.

### 🔴 The actual objection: the cavity arcs at ~3.2 kW

🔢 From measured Q₀ = 45,162 and U = QP/ω, the **peak field in the unlit cavity
is 16.9 kV/cm at 1 kW** — already **56% of air's ~30 kV/cm** — located in open
air at mid-radius.

> 🔴 **The cavity self-arcs at ~3.16 kW unlit.** An 8 kW pulse would demand
> **48 kV/cm, 1.6× over air breakdown.** The discharge happens at r = 48.7 mm in
> the cavity, not in the torch — damaging the silver plating and shorting the
> mode.
>
> ✅ Cross-checked: 27.2% of 16.9 = 4.59 kV/cm at the bore edge; volume-averaged
> over the bore this gives ~1.7 kV/cm against `dq`'s measured 1.68. Consistent.

⚠️ **This is a new constraint on the whole design, not just on brute force.** It
applies to any high-power *unlit* operation. Once lit, Q collapses 45,162 → ~200
and the field falls 15× to ~1.1 kV/cm, so **normal operation is safe** — the
danger window is precisely the unlit ignition transient.

> ✅ **And it independently validates the electrode.** The electrode ignites at
> 1 kW where the cavity sits at 56% of arcing, and it puts its 252 kV/cm exactly
> where it is wanted — inside the torch — rather than raising the field
> everywhere including the places that must not break down.

### On the laser-seeding proposal

⚠️ Technically sound — multiphoton ionisation genuinely seeds plasmas. But it is
offered to avoid *"physical electrodes to foul up in your high-TDS extracts"*,
and **our electrode is external and never contacts the sample** (R21: recessed at
the end cap, <1% of Q). A Q-switched Nd:YAG is ~$5–20k plus optical access,
alignment and laser safety, against ~$50 for a capacitor and a copper ring.
**It solves a problem the design does not have, at 100–400× the cost.**

| # | question | status |
|---|---|---|
| **R28** | **Cavity arcing margin**: peak unlit field is 56% of air breakdown at 1 kW. Does the design need a dry/pressurised/evacuated cavity fill, or a power ceiling during the unlit transient? | 🔴 open — new, affects the whole design |
| 45 | 🔴 **Cavity self-arcs at ~3.2 kW unlit — brute-force RF is dead** | Peak unlit field **16.9 kV/cm at 1 kW**, at r=48.7 mm in OPEN AIR, = **56% of air breakdown**. 8 kW would need 48 kV/cm. ❌ Refutes 'impedance void' (cavity absorbs **78–91%** unlit) and 'breaks the quartz' (torch wall is 3.1× BELOW the peak). ✅ Validates the electrode; laser seeding solves a problem we do not have at 100–400× cost |

---

## 2026-08-15 — R28 ✅ yes, and nitrogen purge is the answer

### 🔴 First, correcting my own threshold

I quoted **30 kV/cm**, which is the DC/low-frequency figure. At 2.45 GHz the
collision-limited value is the same one this file already uses for the bore:
**30 V/(cm·Torr) × 760 = 22.8 kV/cm.**

| threshold | margin at 1 kW | cavity arcs at |
|---|---:|---:|
| 30 kV/cm (DC — wrong here) | 56% | 3.16 kW |
| **22.8 kV/cm (2.45 GHz — correct)** | 🔴 **74%** | 🔴 **1.82 kW** |

**So the margin is thinner than reported: 26% at 1 kW, not 44%.**

### 🔑 And the structural result: TE₀₁₁ can never strike the bore by field alone

| mode | peak location | bore E @1 kW | cavity peak | ratio |
|---|---|---:|---:|---:|
| **TE₀₁₁** | r = 48.7 mm, **open air** | 1.68 kV/cm | 16.9 kV/cm | 🔴 **10.1×** |
| **TM₀₂₀** | **on axis, in the bore** | 7.63 kV/cm | 7.63 kV/cm | ✅ **1.0×** |

> 🔑 **TE₀₁₁'s field maximum is outside the torch and 10× the bore field.**
> Raising power to reach bore breakdown arcs the cavity **ten times over** first.
> **No power level fixes this — it is geometry.** Any TE₀₁₁ ignition scheme must
> supply its own seed; the mode cannot do it alone.
>
> ✅ **TM₀₂₀'s maximum is on axis, inside the torch — ratio 1.0.** That is a far
> stronger justification for it as the ignition mode than "higher bore E
> fraction", and it is why the mode-shift architecture was sound in the first
> place.

### ✅ The mitigation: nitrogen purge, using gas we already have

| fill | E_break | margin at 1 kW | arcs at |
|---|---:|---:|---:|
| air, as-is | 22.8 kV/cm | 🔴 74% | 1.82 kW |
| **N₂, 1.3 atm** | 29.6 | 57% | 3.08 kW |
| **N₂, 2 atm** | 45.6 | ✅ **37%** | **7.28 kW** |

🔢 **Structurally free**: hoop stress at 2 atm on the 203 mm cavity with a 5 mm
wall is **2.03 MPa against 6061's ~275 MPa yield — a 135× margin.** It needs
*seals*, not a redesign, and the cavity wants RF sealing regardless.

**Three benefits for one change:**
1. ✅ **Raises the breakdown threshold** — pressure directly, plus removing
   humidity, which lowers it.
2. ✅ **Prevents silver tarnish.** Silver sulphides in ambient air; a sealed dry
   N₂ atmosphere preserves the plating, and the plating is what sets Q₀ = 45,162.
3. ✅ Excludes dust and contamination from the high-field region.

⚠️ **It moves the resonance and that must be designed in**: 2 atm shifts f₀ by
**−0.67 MHz ≈ 12 unloaded linewidths.** Static and predictable if the pressure is
regulated — unlike the thermal drift it sits alongside.

⚠️ Field enhancement at edges (loop wire, electrode ring, machining burrs) can
locally multiply the field several-fold, so the 26% air margin is likely
optimistic in practice. **That, not the nominal number, is the argument for the
purge.**

| # | status |
|---|---|
| ~~R28~~ ✅ | **closed — N₂ purge at 1.3–2 atm.** Structurally free, uses existing gas, protects the plating |
| 46 | ✅ **R28 — N₂ purge at 1.3–2 atm** | Threshold corrected 30→**22.8 kV/cm** (2.45 GHz, not DC): cavity arcs at **1.82 kW**, 74% at 1 kW. 🔑 **TE₀₁₁ can NEVER strike the bore by field alone** — its peak is in open air at **10.1×** the bore field; TM₀₂₀'s is on axis at 1.0×. Purge is structurally free (135× stress margin), also stops silver tarnish. Costs −0.67 MHz |

---

## 2026-08-15 — R26 ✅ the tracking spec, and the over-coupling that already helps

⚠️ **Two figures in circulation are stale** (mine, corrected one message later):
the cavity arcs at **1.82 kW not 3.16**, and 1 kW unlit sits at **74% of
breakdown not 56%**, because 30 kV/cm is the DC value and 2.45 GHz gives
22.8 kV/cm. **1 kW unlit is not "safely at 56%"** — 26% of headroom before any
edge enhancement is exactly why R28 makes the N₂ purge necessary rather than
optional.

### 🔑 The resonance is 3.8× wider than the unloaded figure, because we are over-coupled

| | |
|---|---:|
| TE₀₁₁ unloaded Q₀ | 45,162 → **55 kHz** |
| Q_ext (R4, measured) | 16,361 |
| **loaded Q_L** | **12,010 → 207 kHz** |

🔢 β = Q₀/Q_ext = **2.76**, so 4β/(1+β)² = **78% of power coupled** — which is
exactly the measured |S11| = −6.67 dB. ✅ **The design is already over-coupled,
and it bought 3.8× of capture range for 22% of power.** That trade was made
(perhaps unintentionally) and it is the right one for ignition.

### The strike gets easier as it proceeds

| | linewidth |
|---|---:|
| unlit, as coupled | 0.21 MHz |
| lit, Q ≈ 200 | **12.40 MHz** |

> ✅ **Capture range grows 60× while f₀ moves 16.3 MHz.** The resonance broadens
> faster than it runs away, so tracking becomes progressively easier once the
> plasma starts. **The risk is concentrated in the first instant**, when f₀ has
> begun moving but the linewidth has not yet opened.

🔢 **Worst moment**: f₀ moving 0.20 MHz/ms across a 207 kHz linewidth crosses one
linewidth in **1.04 ms**.

> ✅ **R26 answered: the loop needs ≳1 kHz bandwidth**, bounded above by the
> 2.9 µs cavity fill (345 kHz). **1–10 kHz is the design window**, and the
> binding constraint is the first millisecond of the strike, not the steady
> state.

### Pre-strike is a drift problem, not a tracking problem

🔢 Thermal drift is 0.76 unloaded linewidths/K = **42 kHz/K**, i.e. **4.9 K per
loaded linewidth**. Holding a 207 kHz resonance against warm-up is slow work —
tens of linewidths over a warm-up, but at thermal rates. ⚠️ It needs a loop that
*exists*, not a fast one.

### ⚠️ An unused knob worth recording

Coupling is a design variable, not a constant. β can be raised to trade power for
capture range:

| β | power coupled | linewidth |
|---:|---:|---:|
| 1 (critical) | 100% | 110 kHz |
| **2.76 (as built)** | **78%** | **207 kHz** |
| 5 | 56% | 330 kHz |

⚠️ If the first-millisecond tracking proves hard on the bench, **more
over-coupling buys margin without any moving part** — at a known cost in
efficiency. Worth keeping in reserve.

| # | status |
|---|---|
| ~~R26~~ ✅ | **closed — 1–10 kHz loop, set by the first ms of the strike.** Over-coupling already provides 3.8× capture range |
| 47 | ✅ **R26 — tracking spec is 1–10 kHz** | Already **over-coupled (β=2.76)**: loaded linewidth **207 kHz**, 3.8× the unloaded 55, for 22% of power — matches measured −6.67 dB. Capture range grows **60×** during the strike, so risk is the first millisecond (1.04 ms per linewidth). Pre-strike is drift (4.9 K/linewidth), not tracking. Knob in reserve: more β = more range |

---

## 2026-08-15 — 🔑 R11 unblocked: torch ε barely touches the operating mode

R11 was held on "we need the ceramic's ε". **Measured, that dependency is almost
entirely on the mode we no longer need to place.**

🔢 Over ε 3.78 → 8.00:

| mode | shift | **per unit ε** |
|---|---:|---:|
| TM₀₂₀ | −113.0 MHz | 🔴 **−26.8 MHz** |
| TE₀₁₁ | −3.1 MHz | ✅ **−0.75 MHz** |

**A 36× difference.** Under the electrode architecture only TE₀₁₁ needs placing,
and ±1 in ε moves it 0.75 MHz — **correctable by 0.05 mm of L.**

### The two options, and why one of them cannot be designed yet

With a ceramic outer tube the fallback is *already* gone before any retune:
TM₀₂₀ lands at **2.3304 — 70 MHz below the band.**

| | a | L | brake | TM₀₂₀ |
|---|---:|---:|---:|---|
| **A — TE₀₁₁ only** | 101.43 (unchanged) | **89.80** | 3.00 stock | out of band |
| B — keep the fallback | **97.97** | **92.71** | 3.00 stock | 2.4150 |

> 🔑 **Option B cannot be designed on current knowledge.** Placing TM₀₂₀ inside a
> 100 MHz band at 26.8 MHz per unit ε requires the ceramic's permittivity to
> ≈±0.2. **We do not have it to ±2.** Designing for a mode whose position is
> uncertain by ±27 MHz is designing for nothing.
>
> ✅ **Option A is robust to the same ignorance**, because TE₀₁₁ moves 36× less.
> **Take Option A: L 87.67 → 89.80 mm, radius and brake unchanged.**

⚠️ The cost is explicit: **the mode-shift fallback is surrendered.** If the
electrode disappoints, recovering it means a materially different cavity (196 mm
dia vs 203) *and* a measured ε. That is a real bet, but the alternative is
betting on a number we do not have.

### Also settled: which quartz part actually matters

🔢 Splitting TM₀₂₀'s quartz loss by volume × J₀(χ₀₂r/a)²:

| part | volume | weight |
|---|---:|---:|
| **outer tube** | 7,642 mm³ | ✅ **83.0%** |
| intermediate | 1,125 mm³ | 13.1% |
| injector | 311 mm³ | 3.9% |

⚠️ **The outer tube dominates**, so swapping it to ceramic changes most of the
dielectric loss — and **R14 (residual quartz tanδ) matters far less than dsplit's
74.3% implied**, since 83% of that 74.3% is the part being replaced.

| # | status |
|---|---|
| **R11** | 🟢 **UNBLOCKED — Option A, L = 89.80 mm.** Verification solve running |
| **R14** | ⬇️ **demoted** — applies only to the intermediate tube and injector, ~17% of the quartz loss |
| **R17** | ⬇️ **demoted** — ε needed only to recover the fallback, not to build Option A |
| 48 | 🔑 **R11 unblocked — torch ε moves TM₀₂₀ 36× more than TE₀₁₁** | −26.8 vs **−0.75 MHz per unit ε**. Option A (**L 89.80**, a and brake unchanged) is robust to ε ignorance; Option B (keep fallback) needs ε to ±0.2 and **cannot be designed**. Fallback surrendered deliberately. R14/R17 demoted — outer tube is **83%** of the quartz loss and is being replaced |

---

## 2026-08-15 — 🔴 The L sensitivity does not transfer either

Option A verification, ε = 8, matched size-factor 0.96 via `meshsweep`:

| | predicted | measured | error |
|---|---:|---:|---:|
| c_ref (L 87.67) | 2.44610 | 2.44604 | ✅ **−0.06 MHz** |
| c_new (L 89.80) | 2.41710 | 2.42472 | 🔴 **+7.62 MHz** |

> ✅ **c_ref is exact, which localises the error precisely**: the ε = 8 starting
> point is right, so the fault is entirely in the **L sensitivity**.

🔢 | | dTE₀₁₁/dL |
|---|---:|
| assumed (L 85.48→87.67, quartz, **no loop**) | −13.6 MHz/mm |
| **measured (L 87.67→89.80, ε=8, tilted loop)** | 🔴 **−10.0 MHz/mm** |

**74% of the assumed value.** The 1/L³ nonlinearity explains only ~7%; the rest
is configuration — the loop is present and ε has doubled.

> 🔴 **Third sensitivity today that failed to transfer between configurations**,
> after the brake's −26 → −30.7 MHz/mm and the transferred +30.7 MHz mesh offset
> that was off by 1.35 MHz. ✅ **Sensitivities are local. Measure them in the
> configuration you intend to use, or budget for one correction iteration.**
> ⚠️ The method still works — it is self-correcting, and c_ref proves the
> *absolute* prediction is sound. It is the *derivative* that must be re-measured.

🔢 **Corrected: L = 90.56 mm** (not 89.80), from the directly measured
−10.0 MHz/mm. Verification running.
| 49 | 🔴 **L sensitivity does not transfer: −13.6 → −10.0 MHz/mm** | c_ref exact (**0.06 MHz**) so the ε=8 baseline is right; the error is entirely in the derivative. Configuration (loop + ε) not nonlinearity (~7%). **Third non-transferring sensitivity today.** Corrected **L = 90.56 mm** |

### R21 headline number, now a matched difference

`meshsweep` rejected 1.00 (baseline failed) and 0.96 (electrode failed) and built
both at a **common 1.06**:

| | f | Q₀ |
|---|---:|---:|
| no electrode | 2.44660 | 45,568 |
| **electrode, 5 mm from end cap** | 2.44900 | 45,379 |
| **Δ** | **+2.40 MHz** | ✅ **−0.41%** |

🔢 **0.41%, not the 0.7% estimated from mismatched meshes** — and **less than half
the 0.9% of the 25 mm radial viewport the design already accepts.**

> ✅ **The capacitive ignition electrode is the cheapest feature in the cavity.**
> Recessed at the end cap it costs under half a percent of Q and shifts f₀ by
> 2.4 MHz — a static, designed-in offset, not a tracking problem.
>
> ✅ And the tooling worked on its first real use: two of the three candidate
> factors failed, for *different* cases, and it converged on one rather than
> returning a mixed-density pair. That is exactly the failure it was written to
> prevent.
| 50 | ✅ **Electrode costs 0.41% of Q — matched** | meshsweep found a common factor 1.06 after 1.00 and 0.96 each failed for a different case. Electrode at 5 mm: **Δf +2.40 MHz, ΔQ −0.41%** — under half the accepted viewport&#39;s 0.9%. Cheapest feature in the cavity |

### ⚠️ And I misused the tool I had just written

The corrected L = 90.56 run came back at **−6.08 MHz** from target — but it
meshed at size-factor **1.00** while c_ref and c_new were at **0.96**. I passed
`meshsweep.sweep()` a **single case**, so it enforced a common factor across
nothing, and the result is not comparable to the earlier pair.

> ⚠️ **The helper guarantees consistency WITHIN a sweep. It cannot know about
> earlier calls.** Every case being compared has to be in the *same* sweep. A
> tool that prevents a class of error still has a usage contract, and I broke it
> on the second use.
>
> ✅ `meshsweep.sweep()` now warns explicitly when called with fewer than two
> cases. Re-running all three lengths — 87.67, 89.80, 90.56 — in one sweep, which
> also yields the L sensitivity from three points instead of two.

---

## 2026-08-15 — R11 ✅ CLOSED: a = 101.43, L = 90.4 mm, brake 3.00 stock

Three lengths at a **common size-factor 0.96**, ε = 8 on the torch:

| L (mm) | order-1 | converged | **lit (+16.3)** |
|---:|---:|---:|---:|
| 87.67 | 2.44604 | 2.4776 | 2.4939 |
| 89.80 | 2.42472 | 2.4563 | 2.4726 |
| 90.56 | 2.41528 | 2.4469 | 2.4632 |

🔢 **dTE₀₁₁/dL = −10.0 to −10.6 MHz/mm, consistent across the range.** The
assumed −13.6 was simply a different configuration (quartz, no loop). ✅ Measured
over three matched points, this one is trustworthy.

**Final: L = 90.39 ≈ 90.4 mm.** (⚠️ An intermediate line said 90.73 — I divided
the error by the sensitivity without negating it and moved the cavity the wrong
way. Needing +1.8 MHz on a −10.6 MHz/mm handle means a *shorter* cavity.)

| | value |
|---|---|
| radius a | **101.43 mm** — unchanged |
| length L | **90.4 mm** (was 87.67) |
| brake | ✅ **3.00 mm, stock** — no longer a tuning element |
| outer tube | **ceramic** (R18) |
| TE₀₁₁ lit | **≈2.465 GHz**, 35 MHz below the ISM ceiling |

### Uncertainty budget, and why it does not matter

| source | ~MHz |
|---|---:|
| +31.6 MHz offset assumed to transfer from the quartz geometry | 2 |
| ε = 8 assumed (±1 → 0.75 MHz) | 1 |
| R12 lit shift +16.3 MHz (toroid model) | 2 |
| **total** | **~3** |

> ✅ **~3 MHz of uncertainty against 35 MHz of band margin.** And the amplifier
> **tracks** the resonance, so absolute frequency precision was never the
> requirement — **landing inside the band with margin is.** It does, comfortably.
>
> ⚠️ The offset transfer should still be checked with one order-2 solve before
> metal is cut, since it is the largest single term and it is assumed rather than
> measured at ε = 8.

| # | status |
|---|---|
| ~~R11~~ ✅ | **CLOSED — a 101.43, L 90.4, brake 3.00 stock.** The retune that started as a three-constraint packing problem ends as one length change |
| 51 | ✅ **R11 CLOSED — L = 90.4 mm** | Three matched lengths at 0.96: dTE₀₁₁/dL = **−10.0 to −10.6 MHz/mm** (assumed −13.6 was a different configuration). **a unchanged at 101.43, brake stays stock 3.00.** Lit TE₀₁₁ ≈2.465, **35 MHz of band margin against ~3 MHz of uncertainty** |

---

## 2026-08-15 — Standing inventory: what is actually still open

The electromagnetic design is essentially closed. **What remains divides into
three kinds, and the third is the one that has had no attention at all.**

### 1. Physics that only a bench can settle

| | risk |
|---|---|
| 🔴 **N₂ thermal bootstrap without argon** (R20/R23/R24) | **The top unquantified risk.** Energy budget says 91 J at 5 slm is within the amplifier; V-T kinetics say maybe not. If it fails, argon returns — survivable, but it costs the differentiator |
| ⚠️ Does the discharge sustain at all in this geometry | Q×η = 41.5 vs the ring's 43.0 is the only evidence, and R9 showed that comparison rests on a placeholder |

### 2. Quantified but not designed

| | state |
|---|---|
| Pressure-sealed cavity (R28) | Spec known (1.3–2 atm N₂). **No mechanical design** |
| Control loop (R26) | Spec known (1–10 kHz). **Not designed** |
| Ignition gas flow (R13/R25) | **Unspecified**, and it sets bootstrap power and pump size |
| Offset transfer at ε = 8 | One order-2 solve, owed before metal is cut |
| Sialon ε and tanδ (R17) | Vendor datasheet. Blocks the fallback, not the build |

### 3. 🔴 Never examined

**a. The unlit cavity is a 780 W heater.**
🔢 Lit, 99.4% goes to the plasma and the walls see ~6 W. **Unlit, 78% couples
into the silver — 780 W.** On ~1.7 kg of 6061 that is **0.53 K/s**. The loop
tracks the resulting drift easily (9 s per linewidth), but **a minute of failed
ignition attempts is a 32 K rise.** ⚠️ There is no retry limit and no cooling
design.

**b. The torch exit hole is asked to do four incompatible jobs.**

| job | status |
|---|---|
| RF boundary | below-cutoff analysed for the 25 mm viewport **only** |
| **pressure boundary** | 🔴 **new from R28** — cavity at 1.3–2 atm |
| thermal boundary | a 5000 K plume passes through it |
| optical path | if viewing axially through the brake |

⚠️ **These conflict.** A pressure seal wants continuity; an RF choke wants
particular dimensions; a 5000 K plume wants clearance and cooling. **Nothing has
been designed here**, and R28's purge made it harder by adding the pressure role.

**c. RF leakage has six penetrations and one analysis.**
Viewport, torch entry, torch exit, electrode feedthrough, loop feedthrough,
pressure port. ⚠️ Only the viewport has a cutoff calculation. **Leakage is a
regulatory and safety gate, not an optimisation.**

**d. The optical collection train** — lens, fibre, window purge — is assumed to
exist. The spectrometer dominates the budget and nothing about coupling to it has
been specified.

> ⚠️ **The pattern worth noting: every item in category 3 sits at a boundary
> between subsystems.** The cavity is solved, the torch is standard, the
> spectrometer is bought — and every unexamined problem lives in the interfaces
> between them. That is the usual place for a design to fail, and it is where no
> simulation so far has looked.

---

## 2026-08-15 — 🔑 ARCHITECTURE DECISION: reduced-pressure ignition is dropped

**Decision:** ignition is by **capacitive electrode**, with **argon as the
fallback**. Reduced-pressure ignition is removed from the design.

### Why — and it was never the number

| stage | figure | |
|---|---:|---|
| perturbative Q | 136 Torr | original |
| factor-of-2 bug | 180 Torr | inflated |
| bug corrected | 127 Torr | R5 |
| quartz tanδ band | 95–137 Torr | R8 |
| **ceramic forced** | **moot** | R18 |

**The figure moving was never the objection.** What accumulated was structural
cost:

- the pump is sized by **ignition flow, not vacuum depth** — 0.7–7.2 m³/h, and
  the flow was never chosen (R13)
- sealing an **open torch exhaust** — novel, no cost basis
- that exhaust is *also* the 5000 K plume path *and* the optical path
- 🔴 **R28 now wants the cavity at 1.3–2 atm — the opposite direction to the bore**

### 🔴 The collision that settles it

🔢 Cavity at 2 atm against a bore at 0.167 atm is a **12× differential across the
torch outer tube** — a *consumable*, replaced routinely, passing through both end
caps, at 5000 K inside.

⚠️ **The tube itself survives easily**: buckling limit 626 atm against 1.8
needed, a 341× margin. **The tube is not the problem. The seals are.** Two
pressure boundaries in opposite directions on a hot consumable, one of which is
simultaneously the exhaust and the optical path.

> **A design should not ask its most frequently replaced part to be two pressure
> boundaries at once.** That is the objection, and no amount of refining the Torr
> figure touches it.

### What the decision buys

| deleted | |
|---|---|
| vacuum pump, valve, exhaust seal | $0.3–5k and a novel mechanism |
| the 760 → 127 Torr ramp | the former top unquantified risk |
| R7, R13 entirely | pressure ramp and pump sizing |
| the bore-pressure role of the torch exit | 🔑 **one of its four conflicting jobs** — leaving RF, thermal and optical |

✅ **R28's cavity purge is unaffected** — that is the cavity, not the bore, and
it now has no counter-pressure to fight.

### What must still be substantiated

⚠️ **The electrode is substantiated as a BREAKDOWN mechanism, not as a complete
ignition solution:**

| | status |
|---|---|
| breakdown field | ✅ 252 kV/cm in the gas vs ~30 needed |
| cost to the cavity | ✅ **−0.41% of Q**, matched (R21) |
| placement | ✅ recessed at the end cap |
| **N₂ thermal bootstrap** | 🔴 **UNPROVEN — R24** |

**Argon is the fallback precisely because it addresses the unproven step.**
Argon has no dissociation channel and no vibrational ladder, which is why MICAP
runs it for 8 s. **The fallback is not "give up and use argon" — it is targeted
at the one step the electrode cannot help with.**

| # | status |
|---|---|
| ~~R7~~ ❌ | **withdrawn — pressure route dropped** |
| ~~R13~~ ❌ | **withdrawn — no pump** |
| **R24** | 🔴 **now THE gating question.** N₂ bootstrap at reduced flow, electrode-seeded, no argon. Bench |
| **R25** | ⬆️ still live — ignition flow now sets bootstrap power only, not pump size |
| 52 | 🔑 **DECISION: reduced-pressure ignition dropped** | Electrode primary, argon fallback. **The Torr figure was never the objection** — structural cost was: pump sized by unspecified flow, novel exhaust seal, and R28 wanting the **cavity at 2 atm against a bore at 0.167 — a 12× differential across a hot consumable**. Tube survives (341× margin); the seals do not justify themselves. R7/R13 withdrawn; **R24 is now the gating question** |

---

## 2026-08-15 — 🔑 The end-cap aperture: three roles that stop conflicting once it is a tube

After dropping bore-pressure (vacuum gone) and optical (axial viewing gone), the
aperture still has three jobs — **RF boundary, thermal, and cavity pressure**
(2 atm against ambient, from R28's purge). Those looked like a conflict. They are
not, once the aperture is sized for the *first* one properly.

🔢 The torch is 20 mm OD, so the aperture is ≥21 mm. Below-cutoff attenuation at
2.45 GHz:

| D | TE₁₁ cutoff | attenuation | 60 dB needs | 100 dB needs |
|---:|---:|---:|---:|---:|
| **21 mm** | 8.37 GHz (3.4×) | **1.46 dB/mm** | **41 mm** | 69 mm |
| 25 mm | 7.03 GHz (2.9×) | 1.20 dB/mm | 50 mm | 83 mm |
| 30 mm | 5.86 GHz (2.4×) | 0.97 dB/mm | 62 mm | 103 mm |

> 🔑 **The aperture is not a hole in a plate. It is a chimney 40–70 mm long.**
> And the same chimney serves the other two roles:
>
> - **thermal** — 40–70 mm of metal surrounding the plume is a heat sink and
>   radiation shield, sited exactly where the 5000 K gas exits
> - **pressure** — a long annular gap around the torch is a far easier seal path
>   than a knife-edge at a plate, and the differential is now only 1 atm
>
> ✅ **The three roles were only in conflict while the aperture was imagined as a
> hole.** Sized for RF leakage it becomes the right part for all three.

⚠️ Design consequences not yet worked: the chimney adds 40–70 mm to the
instrument height at each end, it must not perturb the mode (it is a
below-cutoff stub on an end cap, at the TE₀₁₁ E-null, so it should be benign —
**but that is an assumption, not a measurement**), and the torch must be
removable through it.

| # | question | status |
|---|---|---|
| **R29** | **Does a 21 × 41 mm below-cutoff chimney perturb TE₀₁₁?** It sits at the E-null so it ought to be free, like the electrode — but the viewport was also "obviously fine" until measured | open — cheap, same method as R6/R21 |
| 53 | 🔑 **End-cap aperture is a chimney, not a hole** | Below-cutoff at 21 mm gives **1.46 dB/mm → 41 mm for 60 dB**. The same tube serves thermal (heat sink around the plume) and pressure (long annular seal path, now only 1 atm). ✅ **Three roles stop conflicting once it is sized for RF.** R29 opened to check it does not perturb TE₀₁₁ |

---

## 2026-08-15 — 🔑 What the torch contributes to degeneracy breaking: nothing

Hypothesis: with a ceramic outer tube at ε ≈ 8 the torch is roughly twice the
dielectric perturbation it was, so perhaps **it could break the TE₀₁₁/TM₁₁₁
degeneracy and make the brake deletable.** Tested on 4 sectors at a common
size-factor, identifying modes by **sector CV** (axisymmetry) and bore magnetic
fraction — never by a ratio.

| configuration | TE₀₁₁ | **sector CV** | nearest m≠0 |
|---|---:|---:|---:|
| **brake + quartz torch** | 2.3883 | ✅ **0.0075** | **+59 MHz** |
| quartz torch, **no brake** | 2.4018 | ⚠️ 0.0498 | **+0.8 MHz** |
| **ceramic torch, no brake** | 2.3891 | 🔴 **0.0861** | **−1.3 MHz** |

> 🔴 **The ceramic torch does not substitute for the brake — it is slightly
> worse than quartz.** Without the brake, TE₀₁₁ is *sandwiched* between m≠0 modes
> 1–3 MHz away and its axisymmetry degrades **6.6× (quartz) to 11× (ceramic)**.
> At ε = 8 the mode at 2.3891 no longer classifies as axisymmetric at all — it is
> **hybridised**, carrying TE₀₁₁'s bore-H signature (4.0%) with a CV of 0.086.
>
> ✅ **The brake is not deletable. It is doing essentially all of the work.**

### Why — and it is a useful rule

**Splitting two modes requires a perturbation placed where they DIFFER.**

- The **brake** sits at the end caps. TE₀₁₁ has an **E-null** there
  (sin(πz/L) → 0); TM₁₁₁ does not. **Maximum differential** → large splitting.
- The **torch** sits on axis. TM₁₁₁'s E_z ∝ J₁(χ₁₁r/a) is **zero on axis**, and
  TE₀₁₁'s E_φ ∝ J₁(χ′₀₁r/a) is also small there. **Both weak, similarly
  perturbed** → frequencies move together, no splitting.

> 🔑 **A bigger dielectric in the wrong place does nothing.** Doubling ε at the
> axis moved both modes ~100 MHz and split them by ~0. That is why the brake was
> put at the end cap rather than made thicker or moved inward, and it retroactively
> justifies a choice that had been made on selectivity grounds alone.

⚠️ The two `--no-torch` cases failed to mesh (rc=1), so *brake-alone* was not
measured. The conclusion does not need it — the comparison that matters is
brake-present vs brake-absent, and both of those ran.

⚠️ **Consequence for the design:** the brake stays, at stock 3 mm, and its
justification is now measured rather than inherited. It is the only dielectric in
the cavity and it is load-bearing for the axisymmetry claim that the whole
architecture rests on.
| 54 | 🔑 **The torch contributes nothing to degeneracy breaking** | Sector CV **0.0075 with brake**, 0.0498 without (quartz), **0.0861 without (ceramic)** — ceramic is WORSE. Nearest m≠0 goes **59 MHz → ~1 MHz**; at ε=8 TE₀₁₁ is hybridised. ✅ **Brake is not deletable.** Rule: splitting needs a perturbation where the modes DIFFER — end cap yes, axis no |

---

## 2026-08-15 — 🔴 Devitrification's third danger, and the collision it creates

### The three dangers, in order of how they actually bite

**1. Mechanical — and it fails cold, between runs.**
✅ Cristobalite inverts β→α at **200–275 °C with a ~0.8% volume change**, and the
devitrified layer has a different expansion coefficient from the parent glass. Every
thermal cycle drives micro-cracks along grain boundaries; the literature is explicit
that the tube becomes *"highly vulnerable to thermal shock … catastrophic
failure."* ⚠️ **The torch does not degrade gracefully — it shatters on cooldown.**

**2. Autocatalytic fouling.** Devitrification roughens the surface, the rough
surface holds more salt, and more salt nucleates more devitrification.

**3. 🔴 Optical, and this is the one that bites first.** Devitrified quartz goes
milky and scatters the emission we are trying to measure. **The torch degrades
optically long before it fails mechanically** — so the real lifetime is set by
signal loss, not by breakage.

### 🔴 And the fix breaks the optics outright

✅ Published: *"when the inner tube and outer tube are made of a ceramic they are
understood to be **opaque**."*

> 🔴 **In AMIP the plasma is inside the torch, inside the cavity.** A radial
> viewport in the cavity wall looks: viewport (r=101) → cavity gas → **torch wall
> (r=8.5–10)** → plasma. **An opaque outer tube makes radial viewing
> impossible.**
>
> ⚠️ **ICP-OES escapes this and we cannot.** Its plasma extends *above* the torch
> tip into open air, and that plume is what is viewed — the ceramic tube is never
> in the optical path. **AMIP encloses the plasma for the full cavity length. The
> geometries are not equivalent, and I adopted the ceramic without checking it.**

### Viewing the exiting plume does not rescue it

🔢 RF leakage budget: **1 mW/cm² at 5 cm → 157 mW → −38 dB**; at 1.46 dB/mm that
is a **26 mm chimney** (34 mm for 50 dB).

⚠️ But the plasma centre sits at the cavity mid-plane, so the plume emerges
**71–79 mm downstream** — against ICP's analytical viewing zone of **5–15 mm above
the coil**. 🔢 It spends 18–23 ms inside the chimney first. **That is a cooled,
recombined plume: the wrong place to look.**

### The trade, stated honestly

| | radial viewing | torch life | consumable cost |
|---|---|---|---|
| **Quartz outer tube** | ✅ works | 🔴 ~24 h at 2% TDS | ⚠️ ~$8k/yr at 8 h/day, $100/tube |
| **Ceramic outer tube** | 🔴 **impossible** | ✅ years | ✅ negligible |

> ⚠️ **This is a genuine architectural problem and it was not visible until the
> ceramic decision met the optical path.** Quartz at ~$8k/yr in consumables is
> *survivable* — it is not obviously worse than the alternatives — but it must be
> a deliberate choice, not an accident.

| # | question | status |
|---|---|---|
| **R30** | 🔴 **Resolve the optical path against the outer-tube material.** Options: (a) quartz + radial + frequent replacement, (b) ceramic + relocate the coupling region toward the exit, (c) composite tube, (d) short chimney with RF absorber instead of below-cutoff length | 🔴 **open — architectural** |
| 55 | 🔴 **Ceramic outer tube is OPAQUE — it breaks radial viewing** | Devitrification dangers: shatters on **cooldown** (cristobalite β→α, 0.8% at 200–275 °C), autocatalytic fouling, and **optical scattering that bites first**. 🔴 But AMIP encloses the plasma, so the torch wall is in the optical path — unlike ICP, whose plume is viewed in open air. Plume exits **71–79 mm downstream** vs ICP&#39;s 5–15 mm zone. **R30 opened** |

---

## 2026-08-15 — 🔑 R30: sapphire rescues radial viewing, and beats quartz on loss

### The material, for the record

✅ The ceramic outer tube is **Sialon / silicon nitride** (vendors describe it
both ways — "a durable ceramic material derived from silicon nitride" and "the
Sialon material"). Sourcing for a datasheet:

| | |
|---|---|
| Glass Expansion | D-Torch ceramic outer tube |
| Precision Glassblowing | **31-808-2815** |
| Thermo Fisher | **842312052205** (iCAP series) |
| bulk ceramic makers | International Syalons, CeramTec, Kyocera — **more likely to publish tanδ than the torch vendors, who treat it as a consumable** |

### 🔑 Option 1: sapphire — transparent AND lower loss than quartz

| material | tanδ @2.45 GHz | transparent | devitrifies |
|---|---:|---|---|
| fused silica | 1–2×10⁻⁴ | ✅ yes | 🔴 **yes, 24 h** |
| Sialon / Si₃N₄ | ⚠️ unknown | 🔴 **no** | ✅ no |
| **sapphire** | ✅ **3.5×10⁻⁵** | ✅ **yes** | ✅ **no — already crystalline** |

> ✅ **Sapphire's loss tangent is measured at 2.45 GHz, 300 K: 3.5×10⁻⁵** —
> **3–6× LOWER than fused silica**, not higher. The literature calls sapphire
> *"one of the lowest dielectric losses of any material."* It cannot devitrify
> because it is already a single crystal.
>
> 🔑 **It solves the problem the ceramic was adopted for, without the opacity
> that broke the optics.**

🔢 **The Q gain is negligible and that is fine.** For TE₀₁₁ the torch is 25% of a
dielectric loss that is itself 4.6% of the total, so sapphire moves Q₀ 45,640 →
~45,985. **The win is optical and lifetime, not Q.**

🔢 ε ≈ 9.4 (∥c) to 11.6 (⊥c). At ε = 10, TE₀₁₁ shifts **−4.7 MHz → L adjusts
+0.44 mm.** TM₀₂₀ shifts −167 MHz, already surrendered. **Compatible with the
Option A design at a sub-millimetre correction.**

⚠️ **The caveat that must be checked before committing: thermal shock.**
Sapphire's CTE is ~5–8×10⁻⁶/K against fused silica's 0.55×10⁻⁶ — roughly **10×
more shock-sensitive than quartz**. A torch cycled daily may object. Sapphire is
routinely used for high-temperature windows, but not, as far as I can find, for
ICP torch outer tubes — **so this would be a custom part with no service
precedent.**

### Option 2: truncate the ceramic tube inside the cavity

Transplant the ICP geometry inward — end the opaque tube at z ≈ +20 mm, let the
plume extend above it *inside* the cavity, and view radially at z ≈ +25–30 mm
with no tube in the optical path.

⚠️ Costs: plume gas enters the cavity proper, analyte deposits on the cavity
walls **and the viewport**, and the chimney sees hotter gas. It trades a material
problem for a fouling problem — and fouling of the *cavity* was previously
AMIP's strongest advantage over MICAP.

| # | status |
|---|---|
| **R30** | 🟡 **two live options.** Sapphire is preferred on every axis except thermal shock and precedent. **Needs: sapphire tube CTE/shock data, and a price** |
| 56 | 🔑 **Sapphire rescues radial viewing** | tanδ **3.5e-5 measured at 2.45 GHz** — 3–6× LOWER than fused silica — transparent, and cannot devitrify (already crystalline). ε~10 costs **+0.44 mm of L**. ⚠️ CTE ~10× quartz, so thermal shock needs checking, and no ICP-torch precedent. Material is **Sialon/Si₃N₄**; try International Syalons for tanδ |

---

## 2026-08-15 — ✅ R17 CLOSED by measured data: SiAlON's ε and tanδ at 2.45 GHz

Source: **Kim et al., "Dielectric properties of SiAlON ceramics"** (KAIST +
Agency for Defense Development), `refs/Dielectric_Properties_of_SiAlON_Ceramics.pdf`.
✅ **Hakki-Coleman post-resonator, measured at exactly 2.45 GHz** — our frequency,
not extrapolated.

| cation | r (Å) | phase | **ε′** | **tan δ** |
|---|---:|---|---:|---:|
| Yb | 1.008 | α | 8.618 | 1.53×10⁻³ |
| **Y** | 1.040 | α | **8.681** | ✅ **1.06×10⁻³** (best) |
| Sm | 1.098 | α | 8.938 | 1.68×10⁻³ |
| Nd | 1.123 | β + 2nd phase | 9.355 | ⚠️ 9.03×10⁻³ |
| La | 1.172 | β + 2nd phase | 10.263 | ⚠️ 5.59×10⁻³ |

**Single-phase α (Yb/Y/Sm): ε ≈ 8.6–8.9, tanδ = 1.06–1.68×10⁻³.** Two-phase
material (La, Nd) is 3–8× worse — **phase purity matters more than cation
choice**, and ε rises with cation radius.

### Scoring my earlier guesses

| | guessed | measured | verdict |
|---|---|---|---|
| ε | 8 (bulk β-SiAlON estimate) | **8.6–8.9** | ✅ close — R11's L is right to ~0.1 mm |
| tanδ | "unknown; h-BN composite says 0.9–3.1×10⁻³" | **1.06–1.68×10⁻³** | ⚠️ **the composite figure was coincidentally in range** — right answer, wrong material |

### 🔢 What it costs

| outer tube | tanδ | Q_diel | **Q₀** | vs quartz |
|---|---:|---:|---:|---:|
| quartz (assumed) | 1.0×10⁻⁴ | 1,066,098 | 45,648 | — |
| **sapphire** | 3.5×10⁻⁵ | 1,270,325 | **45,964** | ✅ **+0.7%** |
| SiAlON, Y-doped | 1.06×10⁻³ | 315,936 | 41,435 | ⚠️ **−9.2%** |
| SiAlON, Sm-doped | 1.68×10⁻³ | 217,221 | 39,105 | ⚠️ **−14.3%** |

> ✅ **SiAlON is usable — 9–14% of Q₀ is a real cost but not disqualifying**,
> which is a much better answer than R17's original red flag suggested. The
> earlier fear of 48–79 Torr came from applying that loss to **TM₀₂₀**, where the
> torch carried 74% of the dielectric loss. **On TE₀₁₁ the torch carries only
> 25% of a loss that is 4.6% of the total**, so the same material costs ~10×
> less. **Dropping the mode-shift architecture is what made SiAlON affordable.**

⚠️ **Two caveats, and the first is significant:**
1. **This is room-temperature data.** The paper's Fig. 1 shows ε rising with
   temperature to 1200 °C, and dielectric loss in ceramics generally rises with
   it too. **A torch outer tube runs hot.** The in-service tanδ is likely worse
   than 1.06×10⁻³, and the paper does not give loss-vs-temperature.
2. **SiAlON remains opaque** (R30). The loss question is now answered; **the
   optical question is not.**

### 🔑 The comparison this settles

**Sapphire is 30–48× lower loss than SiAlON, transparent, and non-devitrifying.**
The only things against it are thermal shock (CTE ~10× quartz) and no ICP-torch
precedent. ⚠️ **On dielectric grounds sapphire is now clearly the better part —
the remaining question is purely mechanical.**

| # | status |
|---|---|
| ~~R17~~ ✅ | **CLOSED — ε 8.6–8.9, tanδ 1.06–1.68×10⁻³ at 2.45 GHz, measured** |
| **R30** | 🟡 sapphire vs SiAlON now turns on **thermal shock and price**, not dielectrics |
| **R31** | **SiAlON tanδ at operating temperature** — room-temperature data only. Matters if sapphire fails on shock | open |
| 57 | ✅ **R17 CLOSED — SiAlON measured at 2.45 GHz** | Kim et al.: single-phase α gives **ε 8.6–8.9, tanδ 1.06–1.68e-3**. My ε=8 guess was close; the h-BN composite tanδ was coincidentally right. Costs **9–14% of Q₀** on TE₀₁₁ — usable, because dropping TM₀₂₀ cut the torch from 74% to 25% of dielectric loss. ⚠️ Room-temperature data only. **Sapphire still 30–48× lower loss and transparent** |

---

## 2026-08-15 — Sapphire: manufacturing is real, two objections are not

An external analysis of sapphire's practical cost. ✅ **The manufacturing points
are correct and worth having.** ⚠️ Three claims are contradicted by things
already measured or decided here.

### ✅ Correct, and it is the real constraint

Sapphire **cannot be flame-worked or fused** — it must be EFG-grown or
core-drilled from a boule, then diamond-machined and polished. Hence
**$1,500–3,000+ per tube against $50–150 for quartz.** That is the genuine
objection and it stands.

### ⚠️ "You must design a specialised manifold to hold it"

🔑 **We already specified a demountable torch (R16/R18)** — forced by the ceramic
decision, before sapphire arose. **And SiAlON cannot be flame-worked either**, so
the D-Torch base *already* holds a straight, unfused ceramic tube on O-rings and
introduces the swirl gases mechanically. **That manifold is a catalogue item.**

> ✅ Sapphire is a **materials substitution into an existing base**, not a
> mechanical redesign — provided the tube dimensions match a stock D-Torch. The
> objection would be decisive against a *monolithic Fassel* torch, which is
> exactly what we already abandoned.

### ⚠️ "It will pull the TE₀₁₁ resonance down significantly"

🔢 Measured here: **dTE₀₁₁/dε = −0.75 MHz per unit ε** — 36× less than TM₀₂₀,
because TE₀₁₁ carries only **0.232%** of its electric energy in the torch.

| ε | TE₀₁₁ shift | L correction |
|---:|---:|---:|
| 8.7 (SiAlON) | −3.7 MHz | +0.35 mm |
| 10.0 | −4.7 MHz | +0.44 mm |
| 11.5 (sapphire ⊥c) | −5.8 MHz | +0.55 mm |

⚠️ **Real but sub-millimetre.** The claim is true of TM₀₂₀ (−167 MHz) and that
mode was surrendered.

### ⚠️ "Ensure the field still targets the centre axis for spark ignition"

Two misreadings of the architecture:
- **The electrode is external**, capacitively coupled through the wall at an end
  cap. It does not use the cavity field to strike (R21).
- **TE₀₁₁'s E is zero on axis by construction** — J₁(0) = 0. That is inherent to
  the mode, not a property to be preserved. Indeed **no** TE₀₁₁ field
  distribution can strike the bore (R28: the cavity arcs 10× first), which is
  precisely why the electrode exists.

### 🔢 The economics, which the analysis frames correctly

| | cost | |
|---|---:|---|
| quartz at 24 h life, 8 h/day | **$8,333/yr** | 83 tubes at $100 |
| sapphire at $1,500 | **payback 2.2 months** | |
| sapphire at $3,000 | **payback 4.3 months** | |

> ✅ **"Turning the torch from a consumable into a permanent hardware component"
> is the right framing, and the payback is months, not years.** ⚠️ Conditional
> entirely on surviving thermal cycling — CTE ~10× quartz, no ICP precedent
> (R30). **That, not price, is what to check next.**
| 58 | ✅ **Sapphire: manufacturing objection real, two others not** | Cannot be flame-worked → **$1.5–3k/tube**, correct. ⚠️ But the manifold already exists — **SiAlON cannot be flame-worked either, so the D-Torch base already takes a straight unfused tube**. And ε pulls TE₀₁₁ only **−3.7 to −5.8 MHz = 0.35–0.55 mm of L**, not &quot;significantly&quot;. Payback vs quartz: **2–4 months** |

---

## 2026-08-15 — 🔑 Sapphire thermal management: the c-axis constraint is electromagnetic too

### The two thermal-shock figures of merit disagree, and that resolves the worry

| | **R (instantaneous quench)** | **R′ = k·R (steady flux)** |
|---|---:|---:|
| sapphire | 157 K | **5,486 W/m** |
| fused silica | **1,048 K** | 1,467 W/m |
| | 🔴 quartz **6.7× better** | ✅ sapphire **3.7× better** |

🔢 **Sapphire's conductivity (35 W/m·K vs quartz's 1.4 — 25×) more than offsets
its 10× CTE once heat is flowing.** Steady radial ΔT across a 1.5 mm wall at
~2.9 W/cm²:

| | ΔT |
|---|---:|
| sapphire | **1.3 K** |
| fused silica | 31.4 K |

> ✅ **In steady state sapphire barely develops a gradient at all. It is only the
> sudden onset that hurts it** — so the soft-start strategy protects precisely
> the one regime where sapphire is weak, and after that it is the better material
> thermally as well as optically.

### ✅ And the mitigations are already in the design for other reasons

| proposed | status here |
|---|---|
| **Soft start / power ramp** | ✅ Already wanted: R26 needs the loop to track f₀ across 16.3 MHz, and a **slower ramp makes that easier**. Two requirements, one measure |
| **Staged gas flow** | ✅ Already specified: ignition at **5 slm** rather than 20, chosen for the thermal bootstrap (91 J over 82 ms). **The same choice protects the crystal** |
| **Thin wall** | ⚠️ Free structurally — buckling margin was **341×** at the pressures now in play |

> 🔑 **Three independent requirements — plasma bootstrap, frequency tracking, and
> crystal survival — all want the same thing: ramp power and flow together from a
> low start.** That convergence is worth more than any one of them.

### 🔑 The c-axis constraint is stricter for AMIP than the analysis states

⚠️ It is presented as mechanical. **For us it is electromagnetic first.**

🔢 Sapphire's permittivity is anisotropic: **ε = 9.4 (∥c) vs 11.6 (⊥c) — 23%.**
TE₀₁₁'s field is **azimuthal**.

- **c-axis longitudinal** → E_φ is everywhere ⊥ c → **ε = 11.6 uniformly around
  the circumference.** ✅ Axisymmetric.
- **c-axis transverse** → ε swings 9.4 ↔ 11.6 with azimuth — **a 23% m=2
  perturbation**, which would split the very modes the brake exists to keep clean
  and destroy the axisymmetry the whole architecture rests on.

> 🔴 **c-axis longitudinal is mandatory, and not merely to avoid warping.** A
> mis-oriented boule would not just risk fracture — it would electromagnetically
> ruin the cavity. **This must be on the purchase order as an EM requirement, not
> a mechanical preference.**

🔢 With c longitudinal, TE₀₁₁ sees **ε = 11.6**: shift **−5.9 MHz → L correction
+0.55 mm.** That supersedes the ε = 10 estimate; **the design length becomes
L ≈ 90.9 mm if sapphire is chosen.**

| # | status |
|---|---|
| **R30** | 🟡 sapphire viable on thermals **given a soft start**, which is already required twice over. **Specify c-axis longitudinal as an EM requirement** |
| 59 | 🔑 **Sapphire thermals resolve; c-axis is an EM constraint** | Quartz **6.7× better on quench**, sapphire **3.7× better on steady flux** (k=35 vs 1.4 beats CTE 10×); steady ΔT **1.3 K vs 31 K**. Soft start + staged flow were **already required** for bootstrap and tracking — three needs, one measure. 🔴 **c-axis must be longitudinal or ε swings 9.4↔11.6 azimuthally — a 23% m=2 perturbation.** TE₀₁₁ sees ε=11.6 → **L ≈ 90.9 mm** |

---

## 2026-08-15 — Sapphire pre-commitment sims: three answers and one invalid test

One mesh (L = 90.4, 4 sectors, brake 3 mm), **material varied only** — so no
mesh-comparability risk.

### 🔴 Q1: the ε extrapolation does NOT hold

| ε step | Δf | per unit ε |
|---|---:|---:|
| 3.78 → 8.00 | −10.3 MHz | **−2.44** |
| 8.00 → 11.60 | −23.6 MHz | **−6.56** |
| **3.78 → 11.60** | **−33.9 MHz** | |

⚠️ I extrapolated **−0.75 MHz/unit** from the tilt45 geometry, predicting −5.9 MHz.
**Measured: −33.9 MHz — off by 6×, and strongly nonlinear.**

> 🔴 **Fourth non-transferring sensitivity today**, after the brake's −26 → −30.7,
> the mesh offset's 1.35 MHz, and L's −13.6 → −10.0. **The sapphire geometry must
> be re-solved from scratch, not corrected.** The +0.55 mm figure quoted earlier
> is withdrawn.

### ✅ Q2: the brake still works, and sapphire is the cleanest of the three

| ε | sector CV | nearest m≠0 |
|---:|---:|---:|
| 3.78 | 0.0075 | +59 MHz |
| 8.00 | 0.0078 | +75 MHz |
| **11.60** | ✅ **0.0054** | +58 MHz |

### ✅ Q3: sapphire nearly doubles the bore coupling

| ε | boreH | vs quartz |
|---:|---:|---:|
| 3.78 | 3.444% | — |
| 8.00 | 4.144% | +20% |
| **11.60** | **6.384%** | ✅ **+85%** |

> 🔑 **This is a performance argument, not just a maintenance one.** For an
> inductively coupled plasma the bore magnetic fraction is the driving quantity,
> and sapphire nearly doubles it — consistent with the vendor claim that a
> higher-ε tube gives "a hotter, more robust plasma", but far larger than SiAlON
> delivers.

### 🔴 Q4: my anisotropy test was invalid

✅ **c-longitudinal reproduces isotropic ε = 11.6 exactly** (2.3544 GHz, boreH
6.378 vs 6.384). **That part of the reasoning holds**: E_φ sees ε_⊥ when c lies
along z.

🔴 **But c-transverse showed CV 0.0052 — no penalty — and that is an artifact of
my own metric.** A transverse c-axis makes ε ∝ cos²φ, an **m = 2 perturbation of
period 180°**. 🔢 The integral of cos²φ over *each* 90° sector is **π/4 for all
four**:

> **Four equal sectors are mathematically blind to m = 2.** The CV metric cannot
> see the very perturbation the test was designed to detect. With 8 sectors the
> same integral gives 0.643 vs 0.143 — a **127% swing**, plainly visible.

⚠️ The orientation *does* matter — f differs by **9.4 MHz** and boreH by **14%**
between orientations — so it is not benign. **But the symmetry penalty remains
unmeasured**, and my earlier "23% m=2 perturbation, mandatory" claim is
unsupported until re-run at 8 sectors.

> ⚠️ **A metric chosen for one purpose silently failed at another.** Sector CV was
> built to catch loop-induced m=1 asymmetry, where 4 sectors are ample. Reused
> against m=2 it returns a confident, meaningless number.

| # | status |
|---|---|
| **R32** | **Re-run the anisotropy comparison at 8 sectors** — 4 cannot resolve m=2 | open — cheap |
| **R33** | **Re-solve the design point for ε = 11.6 from scratch.** Extrapolation is 6× wrong and nonlinear | open — blocks committing to sapphire |
| 60 | 🔴 **Sapphire sims: extrapolation 6× wrong, anisotropy test invalid** | ε 3.78→11.6 moves TE₀₁₁ **−33.9 MHz**, not the −5.9 extrapolated; nonlinear (−2.44→−6.56/unit). ✅ Brake still separates (58–75 MHz), **boreH +85%** — a performance gain. 🔴 **4 sectors are mathematically blind to m=2** (∫cos²φ = π/4 in every 90° sector), so the c-axis test measured nothing. R32/R33 opened |

---

## 2026-08-15 — 🔴 R32 first attempt: a tag collision, and why 5 sectors beat 8

`--sectors 8` failed at every size-factor with **"Physical volume 8 already
exists."** 🔢 `TAG_AIR0 = 3`, so 8 sectors occupy attributes **3–10**, and
**`TAG_BRAKE = 8`**. **Five sectors is the hard maximum** in the current tag
scheme.

> ✅ **The error-surfacing fix earned its keep.** Before it, `meshsweep` would
> have reported only "MESH FAIL at every size factor" and sent me looking for a
> curving problem. It printed the actual exception instead, and the cause was
> obvious in one line.

### And five is not a compromise — it is the better choice

🔢 CV sensitivity of an N-sector metric to a cos²φ (m=2) perturbation:

| N | CV | |
|---:|---:|---|
| **4** | **0.000** | 🔴 **exactly blind** |
| **5** | **0.535** | ✅ usable, fits under the tag collision |
| 6 | 0.585 | ⚠️ collides with TAG_BRAKE |
| 8 | 0.637 | ⚠️ collides |

**N = 4 is not merely insensitive to m=2, it is exactly blind** — the integral of
cos²φ over every 90° sector is identically π/4. ⚠️ **Sector CV has been the
axisymmetry metric for this entire project, and it cannot see even-order
azimuthal perturbations at all.** It was built for the loop's m=1 asymmetry,
where 4 sectors are ample.

> 🔑 **Every "CV = 0.002, axisymmetric" claim in this file means
> *no m=1 asymmetry*, not *axisymmetric*.** Nothing measured so far would have
> detected an m=2 defect — including machining ovality, which is exactly an m=2
> perturbation.

⚠️ **That is a broader gap than the sapphire question that exposed it.** Cavity
ovality from machining, a two-point clamping distortion, or any elliptical
tolerance would all be invisible to the metric used to validate the design.

| # | question | status |
|---|---|---|
| ~~R34~~ ✅ RETRACTED | ~~Re-check the design's axisymmetry claim at 5 sectors**, including a deliberate ovality perturbation. The CV = 0.0021 headline was measured with a metric blind to m=2 | 🔴 open — affects a load-bearing claim |
| 61 | 🔴 **Sector CV is blind to m=2 — 8 sectors impossible (tag collision)** | `--sectors 8` hits **TAG_BRAKE=8**; five is the max. 🔑 **N=4 CV is EXACTLY zero for cos²φ** — so every &quot;axisymmetric&quot; claim in this file means *no m=1*, not *axisymmetric*. **Machining ovality is m=2 and would have been invisible.** R34 opened |

---

## 2026-08-15 — R32 ✅ and R33 ✅: sapphire is buildable, and my sourcing claim was wrong

### 🔴 R32: the c-axis constraint is NOT mandatory

Five sectors (CV response **0.535** to a full cos²φ, so the metric can now see m=2):

| case | f (GHz) | CV | boreH % |
|---|---:|---:|---:|
| isotropic ε = 11.6 | 2.4053 | 0.0053 | 3.085 |
| **c LONGITUDINAL** | 2.4053 | 0.0053 | 3.085 |
| **c TRANSVERSE** | 2.4064 | 0.0059 | 2.930 |

✅ **c-longitudinal reproduces isotropic ε = 11.6 exactly** — confirming E_φ sees
ε_⊥ when c lies along the axis. That half of the reasoning holds.

🔴 **But transverse costs almost nothing**: f +1.1 MHz, CV +11%, boreH −5%. 🔢 The
CV change is **0.0006 against 0.535 for a full m=2 — 0.11% of it.**

> 🔴 **I told you to put "c-axis longitudinal, mandatory" on the purchase order.
> That was wrong and I withdraw it.** The torch holds too little of the field for
> a 23% anisotropy to matter: a large perturbation in a place that carries almost
> no energy is still a small perturbation. **Preferred, not required** — and
> relaxing it should help both price and lead time.

⚠️ Ironically this is the same lesson as the brake/torch result: *a big
dielectric effect in the wrong place does nothing.* I derived that rule this
morning and then failed to apply it to my own anisotropy claim.

### ✅ R33: sapphire design point, with one point discarded

| L (mm) | f | Q₀ | boreE % | boreH % | |
|---:|---:|---:|---:|---:|---|
| 87.0 | 2.37320 | 18,594 | 0.532 | 1.700 | 🔴 **hybrid — discard** |
| 88.5 | 2.43304 | 44,596 | 0.073 | 3.089 | ✅ |
| 90.0 | 2.41280 | 45,714 | 0.072 | 3.090 | ✅ |

⚠️ **L = 87.0 is a hybridised mode**, not TE₀₁₁: boreE 7× higher, boreH 45% lower,
Q 2.4× lower. **It passed `identify()` because boreH = 1.70% clears the 1.0%
threshold** — but a clean TE₀₁₁ here is 3.09%.

> ✅ **Better rule, and it generalises**: in a *sweep*, the mode signature must
> vary **smoothly**. A point whose boreH/boreE jumps is a misidentification
> whatever its absolute value. Absolute thresholds fixed the ratio problem but
> still admit hybrids. **This is the third distinct mode-identification failure
> in this project** — ratio, then absolute-threshold-too-loose, now hybrid-passes.

🔢 The two clean points give **dTE₀₁₁/dL = −13.49 MHz/mm** (it was −10.6 at ε = 8,
−13.6 at ε = 3.78 on another geometry — **local, as always**), and both
independently solve to the same answer:

> ✅ **SAPPHIRE DESIGN POINT: L = 89.68 mm** at a = 101.43, brake 3.00 stock,
> ε = 11.6. ⚠️ The contaminated three-point fit said 89.31 — **discarding the bad
> point moved the answer 0.37 mm, about 5 MHz.**

### Where sapphire now stands

| | |
|---|---|
| optical access | ✅ transparent — rescues radial viewing |
| devitrification | ✅ cannot (single crystal) |
| tanδ @2.45 GHz | ✅ 3.5×10⁻⁵ — 30–48× better than SiAlON |
| bore coupling | ✅ **+85% boreH vs quartz** |
| degeneracy | ✅ brake still separates, CV improves |
| c-axis orientation | ✅ **preferred, not mandatory** (R32) |
| geometry | ✅ **L = 89.68 mm**, solved not extrapolated (R33) |
| **thermal shock** | ⚠️ **the only open question** — quench R 6.7× worse than quartz |
| **price** | ⚠️ $1.5–3k/tube, payback 2–4 months |
| 62 | ✅ **R32/R33 — sapphire buildable; my sourcing claim withdrawn** | 🔴 **c-axis is NOT mandatory**: transverse costs f +1.1 MHz, CV +11%, boreH −5% — **0.11% of a full m=2**. Same lesson as the brake: a big effect in a low-energy place is small. ✅ **L = 89.68 mm** from two clean points; L=87.0 was a **hybrid that passed identify()** at boreH 1.70% vs a clean 3.09%. Only thermal shock remains |

---

## 2026-08-15 — ✅ RETRACTION: the m=2 blindness was mine, not the project's

I claimed sector CV had been blind to m=2 throughout, and that *"every
'axisymmetric' claim in this file means no m=1, not axisymmetric."* **That is
wrong and I withdraw it.**

🔢 Verified from the meshes themselves:

| mesh | sector attributes | N |
|---|---|---:|
| `final_o2.msh` (**the design point**) | 3,4,5,6,7 | ✅ **5** |
| `retune_h060.msh` | 3,4,5,6,7 | ✅ **5** |
| `d_both.msh` (**my run today**) | 3,4,5,6 | 🔴 **4** |

✅ `geometry.py` defaults to **`sectors=5`**, and its help text reads *"azimuthal
energy sectors (**5 resolves m=1..4**)"*. `brake-sweep.py` and `tune-sweep.py`
both default to 5. **Whoever wrote that chose it deliberately and documented
why.**

> ✅ **The CV = 0.0021 headline was measured at 5 sectors and does resolve m=2.
> It stands.** The blindness was introduced by *me*, today, by passing
> `--sectors 4` to the degeneracy and sapphire runs — which is also why R32's
> first attempt found nothing.
>
> ⚠️ **I generalised a fault in my own run into a fault in the project's
> record.** The check that would have caught it — reading the default before
> asserting the metric was inadequate — took one grep.

### What survives: ovality has still never been simulated

The exposure analysis is unaffected by the retraction. **A 5-sector metric could
see ovality; nobody has ever put ovality into a mesh.**

| feature | order | status |
|---|---|---|
| coupling loop, viewport | m=1 | ✅ visible, and measured |
| brake, electrode ring | m=0 | ✅ axisymmetric by construction |
| sapphire c-axis transverse | m=2 | ✅ measured at 5 sectors (R32): negligible |
| **cavity ovality** | **m=2** | 🔴 **never simulated** |
| **two-point clamping distortion** | **m=2** | 🔴 **never simulated** |

🔢 For a bore machined to a(φ) = a(1 + δ·cos2φ):

| roundness | δ | Δf ≈ δ·f | mixing if 50 MHz separation |
|---:|---:|---:|---:|
| ±0.20 mm | 2.0×10⁻³ | 4.8 MHz | 9.7% |
| ±0.10 mm | 9.9×10⁻⁴ | 2.4 MHz | 4.8% |
| **±0.05 mm** | 4.9×10⁻⁴ | 1.2 MHz | **2.4%** |
| ±0.02 mm | 2.0×10⁻⁴ | 0.5 MHz | 1.0% |

⚠️ A bored aluminium cavity holds ±0.02–0.05 mm routinely, giving **1–2% mixing**
— likely fine. **But "likely fine" is an estimate, and it is the kind of estimate
this project has repeatedly found to be wrong.**

| # | question | status |
|---|---|---|
| ~~R34~~ | ~~re-check the CV headline~~ | ✅ **retracted — headline is sound at 5 sectors** |
| **R36** | **Simulate a deliberately oval cavity** (δ = 0.05, 0.1, 0.2 mm) and measure TE₀₁₁ mixing. Sets the roundness tolerance on the drawing | open — the real gap |
| 63 | ✅ **RETRACTION — the m=2 blindness was mine** | `geometry.py` defaults to **sectors=5** (&quot;5 resolves m=1..4&quot;), and the design-point mesh has 5. **The CV=0.0021 headline stands.** I introduced 4 sectors today and then generalised my own fault into a project-wide one. ✅ Real gap remains: **ovality has never been simulated** — ±0.05 mm gives ~2.4% mixing (R36) |

---

## 2026-08-15 — ✅ Dual-material design point: 0.74 mm apart

**Quartz (ε = 3.78), driven, three lengths at a common size-factor 1.00:**

| L (mm) | f | converged | Q₀ | boreH % |
|---:|---:|---:|---:|---:|
| 91.5 | 2.40456 | 2.4362 | 46,913 | 2.252 |
| 92.5 | 2.39184 | 2.4234 | 47,580 | 2.275 |
| 93.5 | 2.38124 | 2.4128 | 48,153 | 2.281 |

✅ **Signature smooth across all three** (the new consistency rule), and the three
independent solves agree: **L = 90.42 / 90.33 / 90.42.** dTE₀₁₁/dL = −11.66 MHz/mm.

| material | ε | **L** |
|---|---:|---:|
| **quartz — development** | 3.78 | **90.4 mm** |
| **sapphire — production** | 11.6 | **89.68 mm** |

> 🔑 **They differ by 0.74 mm.** A **shim between the cavity body and one end cap
> swaps between them** — build the body at the sapphire length and add a 0.74 mm
> spacer for quartz development. **You can break $150 parts while commissioning
> and fit the $3k part only when the sequence is proven.**

### ⚠️ Two measurement routes disagree, and it matters for a claim I made

🔢 Normalised to L = 90.0, the **driven** runs put quartz→sapphire at
**9.25 MHz**. The **eigenmode** ε sweep put ε 3.78→11.6 at **−33.9 MHz** — a
**3.7× discrepancy**.

The driven runs define the design point and are internally consistent: three
lengths, smooth signatures, three L_targets within 0.09 mm. The eigenmode sweep
used a different mesh, **no loop, and 4 sectors**, and its boreH nearly doubled at
ε = 11.6 (3.44 → 6.38%) where the driven runs give **2.27 → 3.09%, +36%**.

> ⚠️ **My "+85% bore coupling" headline for sapphire came from the eigenmode
> sweep. The driven runs say +36%.** Still a real gain — but **less than half what
> I claimed, and I should quote +36% until the discrepancy is understood.**
>
> 🔴 **Two routes to the same quantity differing by 3.7× is exactly the pattern
> that preceded the factor-of-2 Q bug (R5).** It should not be left unresolved.

| # | question | status |
|---|---|---|
| **R37** | **Why do eigenmode and driven disagree 3.7× on the ε sensitivity?** Candidates: loop present/absent, 4 vs 5 sectors, mode hybridisation at high ε in the eigensolve | 🔴 open — an unresolved 3.7× has burned this project before |
| 64 | ✅ **Dual-material: quartz L=90.4, sapphire L=89.68 — 0.74 mm apart** | A **shim** swaps them: commission on $150 quartz, fit the $3k sapphire when proven. ⚠️ **Eigenmode and driven disagree 3.7× on ε sensitivity** (9.25 vs 33.9 MHz); driven is self-consistent and defines the design. 🔴 **My +85% boreH headline becomes +36%.** R37 opened — an unresolved 3.7× preceded the R5 bug |

---

## 2026-08-15 — 🔑 STANDING POLICY: eigenmode-derived values are suspect

**R37 resolved: the eigensolve and the driven solve were looking at different
modes.**

| | f | boreH | boreE |
|---|---:|---:|---:|
| **driven TE₀₁₁** | 2.41280 | **3.089%** | **0.072%** |
| eigen 2.3544 (what my picker took) | 2.3544 | 6.384% | 0.137% |
| eigen 2.7050 | 2.7050 | 2.620% | ⚠️ 9.757% |

🔢 A **58 MHz gap for a 0.4 mm length difference** (≈5 MHz expected) settles it —
**no mode in the eigenmode spectrum matches the driven TE₀₁₁ signature.**

### 🔑 Why driven is structurally more trustworthy, not just better-measured

An **eigensolve returns every mode near the target**, including ones the
instrument will never excite. Picking the right one is a *classification*
problem — and classification has now failed **three times**:

1. `pm > pe` **ratio** picked the wrong mode across an entire brake sweep (§8)
2. **absolute threshold** boreH > 1% admitted a hybrid at L = 87.0 (R33)
3. **"highest boreH"** picked a non-TE₀₁₁ mode at ε = 11.6 (R37)

> ✅ **A driven solve has a physical filter: only modes the port couples to
> appear at all.** The loop links H_z, so it shows TE₀₁₁ and little else — and
> **that filter is the same one the real instrument has.** The driven result is
> not merely better measured; it is asking the question the instrument asks.
>
> 🔑 **POLICY: prefer driven wherever both are possible. Treat every
> eigenmode-derived number as provisional until a driven solve confirms it.**

### What this puts at risk, listed honestly

| eigenmode-derived | exposure |
|---|---|
| **+31.6 MHz order-1 → converged offset** | 🔴 **load-bearing** — every "converged" frequency uses it. ⚠️ *Partly corroborated*: R3's order-2 **driven** solve gave +30.7 MHz against Richardson's 36.5 |
| Sector CV 0.0021 | ⚠️ the axisymmetry headline |
| Tuning sensitivities (−12, −23, −14, +1, −0.8, −26) | ✅ mostly superseded by driven re-measurement |
| Brake / TM₁₁₁ splitting, degeneracy tests | ⚠️ including today's "brake is essential" result |
| Ring Q = 11,054 and Q × η = 47.5 | ⚠️ but the ring's Q was independently confirmed 3 ways in R5 |

⚠️ **Not everything eigenmode is wrong** — R5 confirmed the ring's Q by three
independent routes including a convention-free one. **The rule is that eigenmode
results need corroboration, not that they are false.**

| # | status |
|---|---|
| ~~R37~~ ✅ | **closed — different modes, not a solver discrepancy.** Policy adopted |
| **R38** | **Re-confirm the +31.6 MHz offset by driven order-2 at the current geometry.** It is the most load-bearing eigenmode-derived number left | 🔴 open |
| **R39** | **Re-do the brake-essential test (m=2 capable, driven if possible).** Today's result used 4 sectors and an eigensolve — both now suspect | open |
| 65 | 🔑 **POLICY: eigenmode values are provisional** | R37 closed — eigensolve and driven were on **different modes** (58 MHz gap for 0.4 mm). Eigensolves return everything; picking is classification, which has failed **3×**. **Driven has a physical filter matching the instrument.** 🔴 R38: re-confirm the +31.6 MHz offset. R39: re-do the brake test |

---

## 2026-08-15 — 🔑 Mehlich-3 contains fluoride, and that strengthens the sapphire case

🔢 Standard Mehlich-3: 0.2 M CH₃COOH, 0.25 M NH₄NO₃, **0.015 M NH₄F**, 0.013 M
HNO₃, 0.001 M EDTA.

> 🔴 **Ammonium fluoride plus acid generates HF in situ, and HF attacks SiO₂
> vigorously.** This has never been noted in the fouling analysis, which treated
> the matrix only as high-TDS.
>
> ✅ **Al₂O₃ is the standard HF-resistant torch material** — Agilent ships an
> *alumina injector* specifically for HF work, and Inorganic Ventures sells an
> "HF-resistant introduction system" for ICP-OES. **Sapphire is single-crystal
> Al₂O₃.**
>
> 🔑 **The same matrix that forces us off quartz for devitrification also attacks
> it chemically, and sapphire answers both with one part.** That is a second,
> independent argument for sapphire that has nothing to do with optics.

⚠️ **This also weakens the quartz-for-development fallback**: a quartz tube on
Mehlich-3 faces devitrification *and* HF etching. Fine for commissioning on clean
standards; **not fine for extended running on real extracts.**

### Sapphire properties still unknown — the supplier question list

**🔴 Blocking**

| property | why it matters | what to ask |
|---|---|---|
| **Thermal shock / cycling limit** | The only open blocker. Quench resistance is 6.7× worse than quartz | Max ΔT and cycles-to-failure for a 20 mm OD × 1.5 mm wall tube, cycled daily |

**⚠️ Important**

| property | why | note |
|---|---|---|
| **tanδ at operating temperature** | We have 3.5×10⁻⁵ at **300 K**; the tube runs hot, and sapphire's loss *rises* with temperature | The cited source shows loss falling toward 4.2 K, i.e. rising the other way. Ask for 500–800 °C |
| **HF resistance at temperature** | Mehlich-3 generates HF; sapphire should be excellent but confirm at plasma-adjacent temperature | |
| **Thermal conductivity vs temperature** | My 1.3 K ΔT used k = 35 W/m·K (room temp). k drops with temperature — at ~10 W/m·K it becomes 4.4 K, still fine, but the margin shrinks | |

**Practical**

| | |
|---|---|
| Availability at **20 mm OD × 17 mm ID × ~150 mm** | EFG-grown standard sizes? |
| Price at that size | we assumed $1.5–3k |
| **c-axis orientation premium** | R32 made it *preferred, not mandatory* — so ask whether it is cheap, and decline it if not |
| Inner/outer surface finish | radial viewing looks **through** the wall; scattering matters where devitrified quartz failed |

⚠️ **What we do NOT need**, thanks to R32: a tight c-axis specification. Transverse
orientation costs f +1.1 MHz, CV +11%, boreH −5%. **If longitudinal carries a
price or lead-time premium, decline it.**
| 66 | 🔑 **Mehlich-3 contains NH₄F — HF attacks quartz** | 0.015 M ammonium fluoride + acid generates HF in situ. **Al₂O₃ is the standard HF-resistant torch material; sapphire is single-crystal Al₂O₃.** A second independent argument for sapphire, unrelated to optics — and it weakens the quartz-development fallback for real extracts |

---

## 2026-08-15 — 🔑 Sapphire materials data: shock settled, and the blocker moves

### ✅ Thermal shock is SETTLED, confirmed twice independently

🔢 My R = σ_f(1−ν)/(Eα) = **157 K**. Their quoted ΔT_c = **150–200 K.** Two
independent routes agree, and brittle single crystals do not fatigue — the tube
survives unlimited cycles provided the transient stays under rupture. **With the
soft-start and 5 slm staging already required for three other reasons, it does.**

⚠️ Thermal conductivity falls hard with temperature (40 → 25 → 12.5 → 5–8 W/m·K
from 20 to 800 °C), but even at k = 5 the steady ΔT is ~9 K — **15× under the
limit. The margin shrinks and remains ample.**

> ✅ **R30's blocking question is closed. Sapphire will not fracture.**

### ⚠️ The tanδ claim is internally inconsistent

They quote sapphire at 800 °C as **"10⁻⁴ to low 10⁻³"** and then say it *"remains
orders of magnitude below SiAlON."* 🔢 SiAlON measures **1.06–1.68×10⁻³ at room
temperature** (KAIST), so **at low-10⁻³ sapphire equals cold SiAlON** — not orders
below.

| sapphire tanδ | Q_diel | **Q₀** | vs 3.5×10⁻⁵ |
|---|---:|---:|---:|
| 3.5×10⁻⁵ (300 K, measured) | 1,270,325 | 45,964 | — |
| 1×10⁻⁴ (~400 °C) | 1,066,098 | 45,648 | −0.7% |
| 1×10⁻³ (800 °C, their upper) | 330,469 | **41,676** | ⚠️ **−9.3%** |

⚠️ Fair reading: **both materials rise with temperature**, so sapphire probably
keeps its ~30× advantage in *relative* terms. But **the absolute hot value is
what sets Q**, and at their upper bound we lose 9.3% — exactly what SiAlON costs
cold.

### 🔑 The genuinely new finding: sapphire is NOT permanent

> **HF etch pits frost the inner diameter over "thousands of runs". Optical
> degradation, not fracture, sets the life** — the *same failure mode as
> devitrified quartz*, just far slower.

⚠️ **That retires the "permanent hardware component" framing**, mine and theirs.
And it changes the economics decisively, because the life is unquantified:

| sapphire life | tubes/yr @8 h/day | at $1,500 | at $3,000 |
|---:|---:|---:|---:|
| 83 h (1,000 × 5 min) | 24.1 | 🔴 **$36,145** | $72,289 |
| 250 h | 8.0 | ⚠️ $12,000 | $24,000 |
| 900 h | 2.2 | ✅ **$3,333** | $6,667 |
| *quartz reference* | | **$8,333** | |

🔴 **At ~83 h sapphire costs 4× more than quartz. At 250 h it is roughly
break-even. It only clearly wins above several hundred hours.**

### 🔑 And the price driver is the ID polish, which only optics needs

| | |
|---|---:|
| as-drawn EFG tube | **$200–400** |
| + optical ID/OD polish | **$1,500+** |

⚠️ **The 4–7× premium buys exactly one thing: seeing through the wall.** Worth
asking whether a *polished strip* along the viewing line costs less than a full
17 mm × 150 mm ID polish.

> 🔑 **THE BLOCKING UNKNOWN HAS MOVED.** It was thermal shock; that is now settled
> twice over. **It is now: how fast does HF frost the ID?** That single number
> decides whether sapphire is a bargain or a mistake, and nothing in the design
> can answer it — it needs a vendor with fluoride service history, or a coupon
> test.

| # | status |
|---|---|
| **R30** | ✅ thermal shock closed; 🔴 **reopened on ID etch rate** |
| **R40** | **HF etch rate on sapphire at plasma-adjacent temperature** — sets tube life and therefore the entire economic case | 🔴 **now the deciding question** |
| 67 | 🔑 **Sapphire: shock settled, HF etch becomes the blocker** | ✅ ΔT_c **150–200 K vs my independent 157 K** — will not fracture. ⚠️ Their tanδ &quot;10⁻⁴ to low 10⁻³&quot; contradicts &quot;orders below SiAlON&quot;; at 1e-3 we lose **9.3% of Q**. 🔑 **HF frosts the ID — sapphire is NOT permanent.** At 83 h life it costs **4× quartz**; only wins above several hundred hours. Price driver is the **ID polish ($200–400 → $1,500+)**, which only optics needs |

---

## 2026-08-15 — R40: the fluoride mechanism, and a correction to my break-even

### ✅ The mechanism is correct and well-established

🔢 **SiF₄ boils at −86 °C** — quartz attacked by fluorine radicals *volatilises*,
exposing fresh SiO₂ continuously. **AlF₃ sublimes at ~1276 °C** — alumina forms a
**solid passivation layer** instead. ✅ This is exactly why semiconductor plasma
etch chambers use alumina and sapphire liners, and the quoted **10–100× slower
etch rate than fused silica** is consistent with that industry's practice.

> ✅ **It also explains the 24 h quartz figure better than devitrification alone
> did.** Quartz suffers *both* mechanisms at once — thermal devitrification *and*
> SiF₄ volatilisation — and they compound: vaporising the surface exposes fresh
> silica, which devitrifies, which roughens, which holds more salt.

### 🔴 But I had the break-even wrong, and it changes the verdict

⚠️ I said 250 h. **The correct figures:**

| | break-even life |
|---|---:|
| at $1,500/tube | **360 h** |
| at $3,000/tube | **720 h** |

| sapphire life | @$1,500 | @$3,000 | vs quartz $8,333/yr |
|---:|---:|---:|---|
| **240 h (their worst case)** | 🔴 **$12,500** | $25,000 | **loses** |
| 960 h (their probable) | ✅ $3,125 | $6,250 | wins / ties |

🔴 **At their own worst case sapphire loses on consumable cost.** The projection
spans break-even to 2.7× better, and the price point matters as much as the life.

### 🔑 But consumable cost is the wrong metric

🔢 Quartz at 24 h needs **83 torch changes a year**. At ~0.5 h each for swap,
realignment and recalibration that is **42 h/yr of lost analysis time** — against
**1 h/yr** for sapphire.

> 🔑 **On an instrument whose premise is unattended throughput, a daily torch
> change with recalibration is the real cost, not the $100 tube.** That is the
> argument for sapphire, and it holds even at the pessimistic 240 h life where
> the consumable arithmetic does not.

### ⚠️ Two things the mechanism implies that were not stated

**1. Passivation and "10× slower etch" are different models.** A *self-limiting*
layer means life is set by something else entirely (handling, thermal, mechanical);
a *linear* 10–100× etch means life scales from quartz's 24 h. **The answer uses
both framings, and they predict very different lifetimes.** ⚠️ Reality is probably
quasi-steady — the AlF₃ layer forms, erodes under gas flow, re-forms — but which
dominates is unmeasured.

**2. 🔴 The passivation depends on the wall staying below ~1276 °C.** The coolant
flow is what holds it at 500–800 °C. **So a coolant-flow interruption is no longer
merely a thermal event — it strips the passivation layer by sublimation and
exposes bare crystal to fluorine radicals.**

> ⚠️ **Coolant failure becomes a torch-destroying event.** That belongs in the
> interlock list, which does not yet exist.

| # | status |
|---|---|
| **R40** | ⚠️ **mechanism understood, lifetime still a projection** (240–960 h). Break-even is **360 h @$1,500**, so the worst case loses on cost but wins on downtime |
| **R41** | **Interlock: coolant-flow loss must cut RF within one thermal time constant.** Passivation sublimes above 1276 °C and the tube is then unprotected | 🔴 open — new |
| 68 | ⚠️ **Fluoride mechanism sound; break-even corrected to 360 h** | ✅ SiF₄ boils at −86 °C (quartz volatilises); **AlF₃ solid to 1276 °C (sapphire passivates)** — semiconductor-liner practice. 🔴 I said break-even 250 h; it is **360 h @$1,500 / 720 h @$3,000**, so their 240 h worst case **loses on cost**. 🔑 But quartz costs **42 h/yr of downtime** vs 1 h — that is the real argument. 🔴 **Coolant loss now strips passivation → R41 interlock** |

---

## 2026-08-15 — 🔑 R40 resolved: sapphire wins, and Sialon is NOT its equivalent

### 🔴 The "ceramic D-Torch is sintered alumina" claim is wrong, and the error matters

Our own sources: Glass Expansion says **"the SiAlON material"**; Thermo says
*"ceramic material derived from **silicon nitride**"*; the KAIST paper defines
SiAlON as a solid solution of **Si₃N₄**.

> 🔴 **SiAlON contains silicon.** Under fluorine attack it forms **both**:
> - Al + F → **AlF₃**, solid to 1276 °C — passivating ✅
> - Si + F → **SiF₄**, boils at −86 °C — volatile 🔴
>
> So a Sialon tube should etch by partial volatilisation of its silicon fraction —
> **the same mechanism that destroys quartz, merely diluted.** ⚠️ **The "alumina
> lasts years in HF" evidence does not transfer to Sialon.**
>
> ✅ **Sapphire is pure α-Al₂O₃: no silicon, no volatile fluoride path.** This
> argument therefore favours sapphire **over** Sialon, not alongside it — and
> Agilent's HF option being an *alumina* injector rather than a Sialon one is
> consistent with exactly that.

🔑 **Net effect: the fluoride in Mehlich-3 has now eliminated two of the three
candidate materials.** Quartz volatilises; Sialon partially volatilises; only
pure alumina passivates cleanly.

### ✅ Revised economics — quartz at 6–24 h, and I was optimistic at 24

| quartz life | tubes/yr | cost/yr | **changes/yr** | **downtime** |
|---:|---:|---:|---:|---:|
| **6 h** (10% NaCl, documented) | 333 | $33,333 | 333 | 🔴 **167 h** |
| 12 h | 167 | $16,667 | 167 | 83 h |
| 24 h (my earlier figure) | 83 | $8,333 | 83 | 42 h |

| sapphire | tubes/yr | cost/yr | downtime |
|---|---:|---:|---:|
| 1-year life | 1.00 | $1,500 | 0.5 h |
| 3-year life | 0.33 | $500 | 0.2 h |

⚠️ **At 6 h quartz life the comparison is no longer close** — 333 torch changes
a year is more than one per working day, and **167 h of downtime is 8% of
capacity** on an instrument built for unattended throughput.

### ✅ Re-lapping is the best idea in the exchange

🔢 Wall budget on a 1.5 mm sapphire tube:

| removed per lap | laps before the wall halves |
|---:|---:|
| 10 µm | **75** |
| 25 µm | 30 |
| 50 µm | 15 |

✅ And **0.147% ID change per lap is electromagnetically invisible** — the torch
holds ~0.2% of TE₀₁₁'s electric energy, so a 25 µm bore change is far below
anything the design resolves.

> 🔑 **That converts sapphire from a consumable into a refurbishable asset.**
> Re-lapping an existing bore avoids crystal growth and core-drilling — the two
> expensive steps — so it should cost a fraction of a new tube. **It also means
> the "how fast does it frost?" unknown stops being a cliff and becomes a service
> interval.**

| # | status |
|---|---|
| ~~R40~~ ✅ | **closed — sapphire, with re-lapping as the service strategy** |
| **R42** | **Confirm the D-Torch ceramic composition** (Sialon vs alumina) with the vendor. If some outer tubes are pure alumina they would be an opaque-but-cheap fallback with the same fluoride resistance | open |
| 69 | 🔑 **R40 closed — sapphire wins; Sialon is NOT equivalent** | 🔴 The D-Torch ceramic is **SiAlON, which contains silicon** → forms volatile SiF₄ as well as passivating AlF₃. The &quot;alumina lasts years in HF&quot; data does **not** transfer. ✅ **Sapphire is pure Al₂O₃ — no volatile path.** Fluoride has now eliminated 2 of 3 materials. Quartz at 6 h = **167 h/yr downtime**. ✅ **Re-lapping: 30–75 laps available, 0.147% ID change is EM-invisible** |

---

## 2026-08-15 — 🔴 The 15-hour etch estimate is an upper bound, and it contradicts itself

A stoichiometric mass-transport estimate put the optical life at **~3.3 h of
active aerosol, ≈13–15 h of instrument time.** ✅ **Every arithmetic step
reproduces** — 0.015 M NH₄F, 1.5 mL/min uptake, 5% aerosol efficiency, 2% wall
collision, 6 F per Al₂O₃ → **5.4 nm/h average**, ×2–3 for pit localisation →
50 nm in ~3.3 h.

### 🔴 But it assumes every F reaching the wall consumes Al₂O₃

**That is the *unpassivated* rate, and it contradicts the AlF₃ mechanism the same
argument rests on.** Passivation *means* the reaction self-limits: once the
surface is AlF₃ there is nothing left to fluorinate. **The steady rate is then set
by how fast AlF₃ is removed, not how fast F arrives** — and at 500–800 °C it does
not sublime (needs 1276 °C).

### 🔑 The empirical refutation: semiconductor practice

🔢 A plasma etch chamber runs ~100 sccm CF₄ = **1.79×10⁻² mol F/min**. Our torch
delivers **1.13×10⁻⁶**. **The semiconductor tool has ~15,900× more fluorine.**

> 🔴 **If the arrival-limited model were right, an alumina liner in that chamber
> would lose its optical surface in 0.75 seconds.** Liners last **months**.
> **Passivation therefore dominates by three to four orders of magnitude**, and
> the 5.4 nm/h figure is an upper bound with the protective mechanism switched
> off.

### 🔑 And AlF₃ is an anti-reflection coating, not a scatterer

⚠️ The estimate notes AlF₃'s n ≈ 1.36 against sapphire's 1.77 and then treats the
layer as damage. **AlF₃ — like MgF₂ — is a standard deep-UV AR coating material.**
A *smooth* AlF₃ film on sapphire improves transmission. **Only a rough or patchy
layer scatters**, so the optical failure mode depends entirely on film morphology,
which the model does not address.

> ✅ **Verdict: 13–15 h is a floor, not an estimate.** The true life is bounded
> below by that number and above by semiconductor liner experience (months at
> 15,900× the flux). ⚠️ **The honest statement is that we do not know it to better
> than two orders of magnitude, and no desk calculation will close that** — the
> controlling variable is AlF₃ film morphology and adhesion under a
> high-velocity N₂ sheath.

⚠️ **If it really were 15 h, sapphire would be pointless** — worse than quartz
after polishing costs. The disagreement matters, and it is resolvable only by a
coupon test: a polished sapphire witness sample in the plasma zone, pulled and
measured for Ra and deep-UV transmission at intervals.

| # | question | status |
|---|---|---|
| **R43** | 🔴 **Sapphire coupon test under real Mehlich-3 aerosol.** Ra and 213 nm transmission vs exposure hours. **The only way to settle a 2-order-of-magnitude spread** | 🔴 **the deciding experiment** |
| 70 | 🔴 **The 15 h etch estimate is an upper bound and self-contradictory** | Arithmetic reproduces exactly (5.4 nm/h), but it assumes **every arriving F consumes Al₂O₃ — i.e. no passivation**, contradicting its own mechanism. 🔑 **Semiconductor chambers run 15,900× the F flux; that model predicts liner failure in 0.75 s, and liners last months.** AlF₃ is also a **standard deep-UV AR coating**, not inherently a scatterer. **R43 coupon test is the only resolution** |

---

## 2026-08-15 — 🔴 R38 found something worse than an offset error: the retune crossed TE₀₁₁ through TM₀₂₀

R38 was meant to re-confirm the +31.6 MHz offset. **The order-2 solve returned a
hybrid, and chasing that exposed a design fault.**

| | f | Q₀ | boreE | boreH |
|---|---:|---:|---:|---:|
| order 1, TE₀₁₁ | 2.41405 | 46,835 | 0.063% | 2.225% |
| order 1, TM₀₂₀ | 2.42090 | 23,506 | 3.876% | 0.098% |
| **order 2, single peak** | 2.44605 | 38,506 | 🔴 **1.065%** | 1.729% |

⚠️ The order-2 peak's boreE (1.065%) sits **between** TE₀₁₁'s 0.063% and TM₀₂₀'s
3.876% — it is a **hybrid**, and Q moved −18% where R3 found order-independence
to 0.6%. ✅ **The signature-consistency rule caught it.**

### 🔴 TE₀₁₁ and TM₀₂₀ have crossed

🔢 TE₀₁₁ falls at −11.7 MHz/mm; TM₀₂₀ is nearly flat in L:

| L (mm) | TE₀₁₁ | TM₀₂₀ | **TE − TM** |
|---:|---:|---:|---:|
| 87.67 *(original design)* | 2.4808 | 2.4434 | **+37 MHz** |
| **90.4 (the retune)** | 2.41405 | 2.42090 | 🔴 **−6.85 MHz** |
| 91.5 | 2.40456 | 2.42350 | −18.9 |
| 92.5 | 2.39184 | 2.42328 | −31.4 |
| 93.5 | 2.38124 | 2.42360 | −42.4 |

> 🔴 **Lengthening the cavity dragged TE₀₁₁ down through TM₀₂₀, and the chosen
> design point sits 6.85 MHz from the crossing** — where the two hybridise at
> order 2.
>
> ⚠️ **Nothing flagged this.** R11, R33 and R35 all tracked TE₀₁₁ alone and it
> looked clean at order 1. The crossing is only visible when both modes are
> listed, or at order 2 where they merge. **The brake protects TE₀₁₁ from TM₁₁₁,
> not from TM₀₂₀ — different mode, different mechanism, no protection.**

### Why it matters

Both are m = 0, so **axisymmetry survives** — this does not break the
architecture's central claim. But at 6.85 MHz separation with a *plasma-loaded*
linewidth of ~13 MHz, **the two modes overlap completely once lit**: power
splits between them, the field becomes a mixture of azimuthal-E and axial-E, and
the tracking loop has two overlapping resonances to disambiguate.

⚠️ **And it is not fixable by moving L**, because L is what sets TE₀₁₁'s position
in the first place. **The brake is the TM₀₂₀ handle** (−30.7 MHz/mm) — a *thinner*
brake pushes TM₀₂₀ up and away, but thinner also weakens the TE₀₁₁/TM₁₁₁ splitting
the brake exists for. ⚠️ **The two brake jobs now pull in opposite directions.**

| # | question | status |
|---|---|---|
| 🔴 **R44** | **Resolve the TE₀₁₁/TM₀₂₀ crossing at the design point.** Candidates: (a) accept it — both are m=0; (b) thin the brake to push TM₀₂₀ up, and re-check TM₁₁₁; (c) change radius a, which moves TM₀₂₀ at −23 MHz/mm against TE₀₁₁'s −12 | 🔴 **blocks the design point** |
| **R38** | ⚠️ **inconclusive** — the order-2 comparison is contaminated by the hybrid. Re-run at a length clear of the crossing |
| 71 | 🔴 **R38 — the retune crossed TE₀₁₁ through TM₀₂₀** | Order-2 returned a **hybrid** (boreE 1.065% between TE₀₁₁&#39;s 0.063 and TM₀₂₀&#39;s 3.876; Q −18% vs R3&#39;s +0.6%). Cause: TE₀₁₁ falls −11.7 MHz/mm, TM₀₂₀ flat — **+37 MHz at L=87.67 became −6.85 MHz at L=90.4.** R11/R33/R35 tracked TE₀₁₁ alone and never saw it. **The brake guards TM₁₁₁, not TM₀₂₀.** R44 blocks the design point |

---

## 2026-08-15 — ✅ R43 closed by literature: sapphire's fluoride passivation is self-limiting AND smoothing

Empirical data from CF₄ plasma ALE / XPS work on Al₂O₃, which supersedes both my
upper-bound estimate and the 15-hour projection.

| finding | value |
|---|---|
| Fluorination depth | ✅ **self-limiting at 3–5 nm** — dense AlF₃ blocks further F diffusion |
| Spallation | ✅ **does not occur** — at 5 nm the film accommodates lattice strain elastically; bulk Pilling-Bedworth mechanics do not apply |
| Surface roughness | ✅ **RMS 2.6 nm → <1.0 nm** (AFM) — F preferentially attacks asperities before passivating valleys |

### 🔢 Why the roughness number decides everything

Transmission scatter at the Zn/P **213.8 nm** line, TIS ≈ (2πσΔn/λ)²:

| RMS | TIS | |
|---:|---:|---|
| **<1.0 nm (measured post-plasma)** | **0.011%** | ✅ negligible |
| 2.6 nm (as-deposited) | 0.076% | ✅ negligible |
| 10 nm | 1.12% | 🔴 destructive |
| 50 nm (the earlier assumption) | **27.98%** | 🔴 fatal |

> ✅ **The entire disagreement was one number.** At 50 nm roughness the optics die
> in hours; at <1 nm they never degrade. **The empirical value is the good one,
> and it is measured rather than modelled.**

⚠️ **One correction to the conclusion.** An ideal AR layer needs n = √(n₁n₂) =
1.33, and AlF₃ at 1.36 is nearly perfect — **but a quarter-wave at 213.8 nm is
39.3 nm thick and the layer is 3–5 nm.** At **0.13 of a quarter-wave it is not an
AR coating**; it is simply too thin to do anything. ✅ **Optically inert, not
beneficial** — which is the ideal outcome, but should be stated correctly.

### Status

> ✅ **No 15-hour optical cliff. No continuous spallation. Sapphire is a
> multi-year capital asset**, and the $1,500 optical polish is justified because
> it is amortised over years rather than hours.

⚠️ **R43 downgraded, not deleted.** The pALE data is low-pressure CF₄ on ALD
alumina; ours is atmospheric N₂ plasma, dilute HF from an aerosol, single-crystal
sapphire at 500–800 °C. **Close enough to remove it as a go/no-go, different
enough to keep a coupon as confirmation before committing to a production tube.**

| # | status |
|---|---|
| ~~R43~~ ✅ | **closed as a blocker** — self-limiting passivation, smoothing, <1 nm RMS |
| **R43b** | Coupon confirmation under *our* conditions before buying a production tube | open — low priority |
| 72 | ✅ **R43 closed — sapphire passivation is self-limiting and SMOOTHING** | CF₄ pALE/XPS: fluorination stops at **3–5 nm**, no spallation, and RMS goes **2.6 → &lt;1.0 nm**. At &lt;1 nm the 213.8 nm scatter is **0.011%** vs **28%** at the assumed 50 nm — the whole disagreement was one number. ⚠️ At 3–5 nm the AlF₃ is **0.13 of a quarter-wave — optically inert, not an AR coating**. **Sapphire is a multi-year asset** |

---

## 2026-08-15 — ✅ R44 CLOSED: design point re-solved on both handles, both modes tracked

| | predicted | measured | error |
|---|---:|---:|---:|
| v_ref TE₀₁₁ | 2.4234 | 2.4234 | **0.0 MHz** |
| v_ref TM₀₂₀ | 2.4430 | 2.4430 | **0.0 MHz** |
| v_new TE₀₁₁ | 2.4487 | 2.4526 | +3.9 MHz |
| v_new TM₀₂₀ | 2.3900 | 2.3943 | +4.3 MHz |

✅ Reference exact; candidate within **4 MHz on a simultaneous +2.07 mm radius and
−4.50 mm length move.** The 2×2 sensitivity model holds.

### 🔑 THE DESIGN POINT

| | |
|---|---|
| **radius a** | **103.50 mm** (207.0 mm diameter) |
| **length L** | **88.3 mm** (88.00 solved, +0.33 trim) |
| brake | 3.00 mm stock fused quartz |
| outer tube | sapphire, ε ≈ 11.6 *(quartz L = 90.4 for development — see below)* |
| **TE₀₁₁ cold** | **2.4487** |
| **TE₀₁₁ lit** | **2.4650** — 35 MHz below the ISM ceiling |
| **TM₀₂₀** | **2.3943** — 🔑 **5.7 MHz BELOW the band floor** |
| separation | **58.3 MHz**, TE₀₁₁ above TM₀₂₀ |

> 🔑 **TM₀₂₀ is out of band. The amplifier operates 2.400–2.500 GHz and cannot
> reach it at all** — an unconditional guarantee that does not depend on how the
> mode shifts when the plasma lights, which we never measured.
>
> ✅ **The original ordering is restored** (TE₀₁₁ above TM₀₂₀), and the crossing
> that R38 exposed is gone.

✅ **Signatures clean and consistent across both geometries** — TE₀₁₁ boreH
2.08–2.28% / boreE 0.049–0.052%; TM₀₂₀ boreE 3.81–3.88%. **No hybridisation.**

⚠️ **The optional trim exploits the exact result**: TE₀₁₁ is +3.9 MHz high, and
L +0.33 mm corrects it **without moving TM₀₂₀ at all**, because dTM₀₂₀/dL = 0
identically. **That is the p = 0 property being used as a design tool rather than
tripping over it.**

### What this supersedes

| superseded | by |
|---|---|
| a 101.43, L 87.67 (original) | crossed TE₀₁₁ through TM₀₂₀ when retuned |
| a 101.43, L 90.4 (R11/R35) | **sat 6.85 MHz from the crossing** |
| a 101.43, L 89.68 (R33 sapphire) | same defect, tracked TE₀₁₁ only |

⚠️ **All three earlier design points tracked TE₀₁₁ alone.** The fault was never in
the arithmetic — it was in watching one mode while moving a handle that only
moves one mode.

| # | status |
|---|---|
| ~~R44~~ ✅ | **CLOSED — a = 103.50, L = 88.3, both modes verified** |
| **R46** | **Re-solve the quartz development length at a = 103.50** (was 90.4 at a = 101.43) so the shim swap still works | open — small |
| 73 | ✅ **R44 CLOSED — design point a=103.50, L=88.3** | Two-handle re-solve, **both modes tracked**: predictions within **4 MHz** on a +2.07/−4.50 mm move. **TE₀₁₁ lit 2.4650 (35 MHz margin); TM₀₂₀ 2.3943 — OUT OF BAND**, unreachable by the amplifier. Separation 58.3 MHz, ordering restored, no hybridisation. Supersedes all three earlier design points, which tracked TE₀₁₁ alone |

---

## 2026-08-15 — ✅ Sensitivity matrix measured by driven solve; design point refined

| | **DRIVEN** | analytic | eigenmode | driven vs analytic |
|---|---:|---:|---:|---:|
| dTE₀₁₁/da | **−12.86** | −13.20 | −12 | 2.6% |
| dTM₀₂₀/da | **−21.99** | −25.60 | −23 | ⚠️ 14.1% |
| dTE₀₁₁/dL | **−11.66** | −11.70 | −14 | ✅ **0.3%** |
| dTM₀₂₀/dL | **+0.05** | **0 exactly** | +1 | both ≈ 0 |

✅ **dTE₀₁₁/dL agrees with theory to 0.3%**, and dTM₀₂₀/dL is zero by both routes —
the p = 0 result confirmed empirically.

⚠️ **dTM₀₂₀/da is 14% off the analytic** because the closed form assumes an *empty*
cavity. The brake and torch load TM₀₂₀ by **154 MHz** (2.597 → 2.443 GHz), which
changes its radius response. **Use the driven values.**

🔢 Determinant **−257** — well posed, so a and L give genuine independent control.

### 🔑 REFINED DESIGN POINT

Correcting from the *measured* v_new point rather than re-solving from the
reference:

| | |
|---|---|
| **radius a** | **103.70 mm** (207.4 mm diameter) |
| **length L** | **88.12 mm** |
| **TE₀₁₁ cold / lit** | **2.4487 / 2.4650** |
| **TM₀₂₀** | **2.3900** — 10 MHz below the band floor |

### ⚠️ And the radius is now the critical dimension

🔢 dTM₀₂₀/da = −22 MHz/mm, and TM₀₂₀ must stay below 2.400:

| radius tolerance | TM₀₂₀ movement | |
|---|---:|---|
| ±0.10 mm | ±2.2 MHz | ✅ |
| ±0.25 mm | ±5.5 MHz | ✅ at a = 103.70 |
| ±0.45 mm | ±10 MHz | ⚠️ the limit |

> 🔑 **The refinement is not cosmetic — it buys the machining tolerance.** At
> a = 103.50 (TM₀₂₀ = 2.3943) a **+0.25 mm** radius error puts TM₀₂₀ back *into*
> the band. At a = 103.70 there is 10 MHz of headroom, i.e. **±0.45 mm** — a
> routine bore tolerance instead of a tight one.
>
> ⚠️ **Thermal drift helps here**: heating expands the cavity, lowering TM₀₂₀
> *further* below the floor. The tolerance is one-sided in our favour.

**Put on the drawing: bore radius 103.70 mm ±0.2 mm, roundness per R36.**
| 74 | ✅ **Sensitivities measured driven; design point refined to a=103.70, L=88.12** | Driven matrix **−12.86 / −21.99 / −11.66 / +0.05**; dTE₀₁₁/dL matches theory to **0.3%**, dTM₀₂₀/dL is zero both ways. Analytic dTM₀₂₀/da is 14% off (empty-cavity assumption; loading shifts TM₀₂₀ by 154 MHz). 🔑 **Radius is now the critical dimension** — ±0.45 mm before TM₀₂₀ re-enters the band, and the refinement is what buys that tolerance |

---

## 2026-08-15 — R46 CLOSED: quartz development length, 0.41 mm shim

Three lengths at a = 103.70, common size-factor 0.96, quartz (eps 3.78):

| L (mm) | TE011 conv | TM020 conv | boreH |
|---:|---:|---:|---:|
| 88.5 | 2.4488 | 2.3921 | 2.09% |
| 89.0 | 2.4431 | 2.3930 | 2.10% |
| 89.5 | 2.4375 | 2.3929 | 2.11% |

Signature check kept 3 of 3. dTE011/dL = -13.06 MHz/mm, and the three
independent solves agree: L_target = 88.50 / 88.57 / 88.50.

| material | eps | L |
|---|---:|---:|
| **sapphire (production)** | 11.6 | **88.12 mm** |
| **quartz (development)** | 3.78 | **88.53 mm** |
| | | **shim 0.41 mm** |

**Build the cavity body at the sapphire length and add a 0.41 mm spacer for
quartz commissioning.** Break $150 tubes while proving the ignition sequence;
fit the sapphire when it works.

Note TM020 stays at 2.392-2.393 across all three lengths — dTM020/dL = 0
holding to within 1 MHz over a 1 mm span, and comfortably below the 2.400
band floor in both configurations.
| 75 | **R46 CLOSED — quartz L = 88.53, shim 0.41 mm** | Three lengths, signature check 3/3, L_target agreeing to 0.07 mm. Sapphire 88.12 / quartz 88.53. TM020 stays 2.392-2.393 across the sweep, confirming dTM020/dL = 0 and staying below the band floor in both builds |

---

## 2026-08-16 — ✅ R36 CLOSED: ovality is SECOND ORDER, and roundness is nearly free

R36 was the last "the real gap" item: every non-axisymmetric feature ever put
into this model — loop, viewport — is m=1. **Machining ovality is m=2 and had
never been simulated at all.** The roundness figure on the drawing rested on a
two-level estimate in this file predicting 2.4–9.7% mixing over ±0.05–0.20 mm.

`geometry.py` gained `--ovality MM` (peak radial deviation): the cavity wall is
anisotropically dilated to semi-axes a±ov **before** the torch bore is punched,
so the cavity goes oval while torch, brake ID and loop stay round — which is
what a bored-and-clamped aluminium body actually does. `--ovality 0` is a no-op.

### ✅ The baseline validates against R46 independently

Raw driven TE₀₁₁ at a = 103.70: **2.41692** at L = 88.53 (this work) against
R46's **2.41716** at L = 88.5. With dTE₀₁₁/dL = −13.06 MHz/mm that is agreement
to **0.15 MHz** — the geometry edit is a genuine no-op at δ = 0.

> ⚠️ R46's headline 2.4488 is the order-1 raw value **plus the measured
> extrapolation offset**, ≈ +31.6 MHz. Comparing a raw number to a corrected one
> reads as a 32 MHz discrepancy that is not there. Every number in this entry is
> RAW order-1 unless it says otherwise.

### 🔴 The round case is the WRONG control

First pass, differenced against a perfectly round bore:

| δ (mm) | TE₀₁₁ | Δf | TM₀₂₀ | Δf |
|---:|---:|---:|---:|---:|
| 0 (round) | 2.41692 | — | 2.37546 | — |
| 0.05 | 2.41484 | −2.08 | 2.37650 | +1.04 |
| 0.10 | 2.41520 | −1.72 | 2.37408 | −1.38 |
| 0.20 | 2.41474 | −2.18 | 2.37334 | −2.12 |

TE₀₁₁ sits ~2 MHz below round at **every** δ. Flat in δ is not physics: a real
perturbation of an m=0 mode must vanish as δ → 0, and a second-order one grows
16× from 0.05 to 0.20 mm. Element counts are within **0.3%**, so it is not mesh
density — it is the **surface representation**. A round bore is an analytic OCC
cylinder; any ovalised bore is a GTransform'd surface, and the curved order-2
elements on it discretise differently. Constant offset at any nonzero δ.

> 🔑 **Use a SHAM OVAL as the reference, not a round cavity.** δ = 0.01 mm is
> round to 1e-4 of the radius but carries the identical BSpline representation.
> Differences against it are physics.

### The sham control (δ = 0.01 vs 0.20 vs 0.40 mm)

| δ (mm) | TE₀₁₁ | Δf vs sham | TM₀₂₀ | Δf vs sham |
|---:|---:|---:|---:|---:|
| 0.01 sham | 2.41334 | — | 2.37554 | — |
| 0.20 | 2.41474 | +1.40 | 2.37334 | −2.20 |
| 0.40 | 2.41334 | **+0.00** | 2.37184 | −3.70 |

TE₀₁₁ at **twice** the tolerance lands exactly on the sham. TM₀₂₀ looked like a
monotone −3.7 MHz trend — **and the ladder below shows that was scatter of the
wrong sign.**

⚠️ `c020` and `ov020` returned **bit-identical** frequencies from separate
sweeps. Meshing is deterministic, so that is not independent confirmation: the
scatter is not run-to-run noise but **systematic discretisation error that
varies with geometry**. Repeats cannot average it away. Only amplification
separates it from physics.

### 🔑 The amplification ladder — δ = 0.01 / 1 / 2 mm, common size-factor 0.96

Driven far past any machine tolerance to get the effect above the ~1 MHz floor,
then read the **exponent**, which is what licenses extrapolating back down.

| δ (mm) | % of radius | TE₀₁₁ Δf | TM₀₂₀ Δf | TE₀₁₁ Q₀ | ΔQ |
|---:|---:|---:|---:|---:|---:|
| 0.01 sham | 0.01% | — | — | 45,776 | — |
| 1.0 | 0.96% | +2.76 | +2.54 | 45,905 | +0.28% |
| 2.0 | 1.93% | +3.18 | +9.34 | 45,735 | −0.09% |

🔢 **Ratio test, Δf(2mm)/Δf(1mm):**

| mode | ratio | verdict |
|---|---:|---|
| **TM₀₂₀** | **3.68** | ✅ **quadratic** — the m=0 cancellation holds exactly as predicted |
| **TE₀₁₁** | 1.15 | no trend — flat scatter, no measurable effect even at **10×** the tolerance |

✅ **The pre-registered prediction was right.** For an m=0 mode the first-order
shift is ∫cos2φ·|field|²dφ, and |field|² has no φ dependence, so the +δ lobe
pays for the −δ lobe **exactly**. Both operating modes are m=0. Only δ² survives.

🔢 TM₀₂₀ extrapolated on the measured δ² law:

| roundness | TM₀₂₀ shift |
|---:|---:|
| ±0.40 mm | 0.37 MHz |
| ±0.20 mm | **0.09 MHz** |
| ±0.10 mm | 0.02 MHz |
| ±0.05 mm | 0.006 MHz |

> ⚠️ **CORRECTION to the sham-control reading.** I reported TM₀₂₀ moving *down*
> with ovality (−2.2, −3.7 MHz) and called that favourable, since down is away
> from the 2.400 band floor. **The sign is wrong.** The real effect is +0.09 MHz
> **upward** at ±0.20 mm; the −3.7 MHz was discretisation scatter forty times
> larger than the physics it was hiding. The direction is unfavourable and the
> magnitude is irrelevant — but it was reported the wrong way round, and a
> directional safety claim is exactly the kind that gets built on.

### 🔴 ±4 mm destroys the mode — corroboration only, size-factor 1.00

Not size-factor-matched to the ladder, so **not differenced** and excluded from
the fit. The qualitative change is far beyond any discretisation effect:

| mode found | f | Q₀ | boreE | boreH |
|---|---:|---:|---:|---:|
| hybrid | 2.31510 | 19,678 | 0.754% | 1.156% |
| hybrid | 2.37034 | 19,447 | 0.784% | 1.257% |
| TM₀₂₀-like | 2.40418 | 23,465 | 3.211% | 0.084% |

**No peak carries TE₀₁₁'s signature any more.** Its boreH of 2.08% has split
into two modes at 1.16% and 1.26%, and Q collapses from 45,776 to ~19,500. The
partner is identifiable: a weak resonance at **2.3499 GHz** (boreE 0.77%, boreH
1.21%) is present in every δ = 0–0.20 run at ~10% of peak energy, stationary to
0.6 MHz with no δ trend. At ±4 mm the m=2 perturbation has mixed TE₀₁₁ into it
completely. TM₀₂₀-like also lands at **2.40418 — above the 2.400 band floor.**

### 🔑 What goes on the drawing

> **Roundness is not a critical dimension. Mean radius is.**
>
> | error, 0.2 mm | TM₀₂₀ moves |
> |---|---:|
> | **mean radius** (dTM₀₂₀/da = −22 MHz/mm) | **4.4 MHz** |
> | **ovality** (δ², measured) | **0.09 MHz** |
>
> 🔢 **~50× apart at the same magnitude.** Keep bore radius 103.70 ±0.2 mm as
> the binding callout (R44 / the sensitivity matrix). Roundness needs only a
> **±0.5 mm** note — 4× inside where anything begins and ~1000× inside where the
> mode is destroyed. A bored aluminium cavity holds ±0.02–0.05 mm without
> trying, so this is free.

✅ **A hand-finished bore is viable.** At ±1 mm — roughly a skilled operator
with a Dremel and a guide — TE₀₁₁ is unmoved within scatter and Q is within
0.3%. The prototype body does not need a boring mill. The cliff is between
±2 mm (fine) and ±4 mm (mode destroyed), not anywhere near a machined part.

### Limitations, stated

- A driven sweep only sees what the loop couples to. A weakly-coupled split
  doublet would not appear. Peak-finding was re-run down to **1% of maximum
  stored energy** and found only the 2.3499 GHz mode; the window's lower edge is
  flat at 5e-5 of peak, so nothing strongly coupled is pressing in from below.
- All runs are `--sectors 1`, so there is **no sector-CV measurement here** —
  the loop sits at φ = 0, exactly on a 5-sector plane, and splitting it kills
  the port. The m=2 question was answered by frequency and Q instead. A CV
  measurement would need `--loop-phi` at 36°, which does not exist as a flag.
- δ = 4 mm is one solve at a different size-factor. It is read for sign and
  scale only.

| # | question | status |
|---|---|---|
| ~~R36~~ ✅ | **CLOSED — ovality is δ², 0.09 MHz at ±0.20 mm. Roundness ±0.5 mm, non-binding** |
| **R47** | Measure the **sector-CV** signature of ovality directly (needs a `--loop-phi` flag so the loop clears the sector planes at 5 sectors) | open — low priority, the frequency answer is already conclusive |
| 76 | ✅ **R36 CLOSED — ovality is second order and the tolerance is nearly free** | `--ovality` added; baseline reproduces R46 to **0.15 MHz**. 🔑 The round bore is the WRONG control — a GTransform'd surface carries a constant ~2 MHz representation offset; use a **sham oval** (δ=0.01). Ladder at 1/2 mm gives **ratio 3.68 = quadratic**, confirming the pre-registered m=0 cancellation ∫cos2φ dφ = 0. **TM₀₂₀ shifts 0.09 MHz at ±0.20 mm — 50× less than the same error in MEAN radius.** TE₀₁₁ shows no trend at 10× the tolerance. ⚠️ Corrects my sham-control claim that TM₀₂₀ moved *down*: sign was scatter. 🔴 At **±4 mm** TE₀₁₁ hybridises with the 2.3499 GHz mode, Q halves, TM₀₂₀-like rises above the band floor — but ±1 mm (hand-finished) is fine |

---

## 2026-08-16 — ✅ R39 CLOSED: the brake survives a driven re-test, and 3 mm is not stock thickness

The standing "brake is essential" result was measured with an **eigensolve on 4
sectors** — provisional under the R37 policy, and blind to m=2 besides. Re-asked
driven at a = 103.70 / L = 88.53, quartz, one common size-factor 0.96, with a
half-thickness case the original never ran.

| brake | TE₀₁₁ raw | Q₀ | boreH | nearest ANY resonance | TM₀₂₀ raw | TM₀₂₀ conv |
|---:|---:|---:|---:|---:|---:|---:|
| **3.0 mm** | 2.41692 | 45,727 | 2.079% | **−41.5 MHz** (TM₀₂₀) | 2.37546 | **2.3952 ✅ below floor** |
| 1.5 mm | 2.41838 | 47,518 | 2.093% | 🔴 **−8.2 MHz** (TM₀₂₀) | 2.41018 | **2.4299 🔴 IN BAND** |
| 0 mm | 2.41746 | 48,457 | 2.082% | 🔴 **+3.2 MHz** (m≠0, boreH 1.25%) | 2.44366 | **2.4634 🔴 IN BAND** |

### 🔑 The result stands, but the MECHANISM in the record was wrong

✅ **TE₀₁₁ itself is robust.** It keeps a clean signature in all three cases —
boreH 2.08–2.09%, Q 45.7–48.5k, one peak. **It does not hybridise when the brake
is deleted**, contrary to what "the brake is doing essentially all of the work"
implied. At this geometry TE₀₁₁ stands on its own.

🔴 **What the brake actually buys is the TM₀₂₀ position.** Delete it and the
ignition mode climbs from 2.3952 (10 MHz below the band floor, unreachable by
the amplifier) to **2.4634 — squarely in band**. That is the decisive objection,
and it is a different argument from the axisymmetry one the file has been making.

🔴 **And it clears TE₀₁₁'s neighbourhood.** Without the brake a mode sits **+3.2
MHz** away carrying boreH 1.25% at 15% of peak energy. Driven and eigenmode
agree here — the original found "1–3 MHz" by a completely different method, so
that number is now corroborated rather than provisional.

> ⚠️ 3.2 MHz is **65 loaded linewidths** at Q ≈ 48,000, so the two are
> spectrally resolved and the amplifier would not confuse them today. The
> objection is not present-tense: it is that nothing keeps them apart under
> drift, plasma loading or a radius tolerance, and the whole point of the brake
> is to not have to think about that.

### ✅ NEW — 1.5 mm is not enough, so 3 mm is a real number

The original never tested a thinner brake, and "3 mm stock thickness — not a
tuning element" appears on the drawing. **Halving it puts TM₀₂₀ at 2.4299, in
band, and only 8.2 MHz from TE₀₁₁** — worse than no brake in the separation
sense, because at half thickness TM₀₂₀ lands *between* where it sits at 0 and at
3 mm, right on top of the operating mode.

🔢 **What the brake costs:** Q falls 48,457 → 45,727 as it goes 0 → 3 mm, i.e.
**−5.6% of Q**, all of it the brake's own dielectric loss.

> 🔑 **The trade is 5.6% of Q for 53 MHz of separation and an ignition mode below
> the band floor.** Keep 3 mm. Do not thin it to recover Q.

### 🔴 A detector bug in my own harness, recorded

The script flagged **all three** cases as "TE₀₁₁ hybridised", including the
known-good design point. The cut was boreH ≥ 1.0%, and a **resident mode family
at boreH ≈ 1.21% exists in every run** — the same 2.3499 GHz mode R36 identified.
The signature under test is TE₀₁₁'s own 2.08% *splitting*, so the threshold has
to sit **above** the resident family, not below it. Corrected to 1.8% in
`r39.py`; the numbers above are the corrected read.

⚠️ **A detector calibrated only on the failure case will fire on the healthy
one.** R36 calibrated this signature on ±4 mm ovality, where TE₀₁₁ genuinely
split into 1.16% + 1.26% — and 1.0% separated those two fine. It was never
checked against a *passing* case, which is where the resident family lives.

### Limitations

- `--sectors 1`, so no sector-CV number; this replaces that metric rather than
  reproducing it (see R47).
- The +31.6 / +19.7 MHz order-1 → converged offsets are measured **with** the
  brake (R46). Applying them to the 0 and 1.5 mm cases is an extrapolation; the
  raw column is the measurement, the conv column is indicative. It does not
  change the verdict — TM₀₂₀ raw alone moves 68 MHz between 3 mm and 0.

| # | question | status |
|---|---|---|
| ~~R39~~ ✅ | **CLOSED — brake confirmed driven; 3 mm required; mechanism corrected to TM₀₂₀ position, not TE₀₁₁ hybridisation** |
| 77 | ✅ **R39 CLOSED — the brake stays, for a different reason than the file said** | Driven, 3 cases at common 0.96. ✅ **TE₀₁₁ does NOT hybridise without the brake** — clean 2.08% boreH and Q *rises* to 48,457. 🔴 What the brake buys is **TM₀₂₀ out of band**: 2.3952 → **2.4634** if deleted, and a neighbour at **+3.2 MHz** (corroborating the eigenmode "1–3 MHz" by an independent method). ✅ **NEW: 1.5 mm is worse than useless** — TM₀₂₀ lands at 2.4299, in band, 8.2 MHz from TE₀₁₁. Trade is **−5.6% of Q for 53 MHz of separation**. 🔴 Harness bug recorded: a 1.0% bore-H cut flagged the known-good case as hybridised, because a resident mode family sits at 1.21% |

---

## 2026-08-16 — ✅ R29 CLOSED: the chimney is free for TE₀₁₁ and costs TM₀₂₀ 1.3 MHz of margin

Entry 53 sized the end-cap aperture as a **chimney** — 21 mm bore, 41 mm long,
below cutoff — doing RF isolation, thermal and pressure duty at once. R29 asked
whether it perturbs TE₀₁₁, because the radial viewport was also "obviously fine"
until it was measured and cost 0.9% of Q.

`geometry.py` gained `--chimney D,LEN`: air continuing past the +z end cap,
terminated PEC, same treatment as the viewport stub. Three cases, driven, common
size-factor.

| case | TE₀₁₁ Δf | TE₀₁₁ ΔQ | TM₀₂₀ Δf | TM₀₂₀ ΔQ |
|---|---:|---:|---:|---:|
| no chimney | — | — | — | — |
| **21 × 41 mm** | **−0.06 MHz** | +0.19% | **+1.26 MHz** | +0.56% |
| 25 × 41 mm | +0.20 MHz | −0.45% | +2.56 MHz | +0.42% |

### ✅ The prediction held, and the contrast is what makes it believable

An aperture couples through the **tangential H** and the **normal E** on the wall
it pierces. At a TE₀₁₁ end cap both vanish — E is azimuthal ∝ sin(πz/L) → 0, and
H_r ∝ sin(πz/L) → 0, leaving only H_z, which is normal and does not drive
aperture coupling. TM₀₂₀'s E_z is normal to that cap and maximum on axis, exactly
where the hole is.

> 🔑 **TM₀₂₀ is the positive control for TE₀₁₁'s null.** R36 established that
> separately built meshes carry 1–3 MHz of systematic scatter, which could hide a
> small real effect. But scatter does not know which mode is which. **In the same
> meshes, TM₀₂₀ moves 2.56 MHz monotonically with hole diameter while TE₀₁₁ moves
> 0.20 MHz with no consistent sign — a 13× contrast.** The null is physical, not
> under-resolved.

✅ **The chimney is free for the operating mode.** Q within ±0.45%, bore-H
2.079 → 2.083%, and the aperture can be opened from 21 to 25 mm with no change.
Compare the viewport's −0.9%: this one really is free, and for a reason that was
stated in advance.

### 🔴 But it is NOT free for TM₀₂₀, and that spends design margin

🔢 TM₀₂₀ rises **+1.26 MHz** at 21 mm and **+2.56 MHz** at 25 mm — very nearly
linear in aperture area, and **upward**, toward the 2.400 band floor it must stay
below.

| | headroom below 2.400 | radius tolerance at −22 MHz/mm |
|---|---:|---:|
| design point as recorded | 10.0 MHz | ±0.45 mm |
| **with the 21 mm chimney** | **8.7 MHz** | **±0.40 mm** |
| with a 25 mm chimney | 7.4 MHz | ±0.34 mm |

> 🔑 **The exhaust aperture and the bore tolerance are the same budget.** Opening
> the chimney to 25 mm to help the plume costs 0.11 mm of machining tolerance.
> Neither number is alarming — ±0.40 mm is still routine — but they trade, and
> nothing in the file said so before.

### ⚠️ My predicted SIGN was wrong again

I predicted TM₀₂₀ would move **down**, reasoning that the chimney adds volume for
E_z to store energy in (Slater: adding volume where E dominates lowers f). It
moved **up**, +2.56 MHz at 25 mm. The likely reason is that a below-cutoff tube
closed by PEC is not "added volume" at all — it is a **shorted evanescent stub**,
which loads the aperture inductively. **That explanation is post-hoc and is not
tested here.** It predicts the shift is insensitive to chimney *length* once
several decay constants long, which is a cheap check (R48).

⚠️ **Second sign error of the night on TM₀₂₀** — the first was in R36's sham
control. The magnitudes have been right and the signs have not. TM₀₂₀ responses
should be taken from a solve, never from my reasoning about which way a
perturbation pushes.

| # | question | status |
|---|---|---|
| ~~R29~~ ✅ | **CLOSED — chimney free for TE₀₁₁ (<0.2 MHz, <0.5% Q); costs TM₀₂₀ 1.26 MHz** |
| **R48** | **Is the TM₀₂₀ shift independent of chimney LENGTH?** Tests the shorted-evanescent-stub explanation and bounds whether the 41 mm can be shortened for packaging | open — cheap, one sweep of 2 |
| 78 | ✅ **R29 CLOSED — chimney free for TE₀₁₁, 1.3 MHz off TM₀₂₀'s margin** | `--chimney` added. TE₀₁₁ **−0.06 MHz / +0.19% Q** at 21 × 41, unchanged out to a 25 mm hole — the pre-registered aperture argument (E and tangential H both vanish at a TE₀₁₁ cap) holds. 🔑 **TM₀₂₀ is the positive control**: it moves **+2.56 MHz monotonically** with diameter in the same meshes, a **13× contrast**, so TE₀₁₁'s null is physical not under-resolved. 🔴 TM₀₂₀ rises toward the band floor: headroom **10.0 → 8.7 MHz**, radius tolerance **±0.45 → ±0.40 mm** — the exhaust aperture and the bore tolerance are one budget. ⚠️ My predicted sign was wrong again (second time tonight on TM₀₂₀) |

---

## 2026-08-16 — 🔴 R38 CLOSED: the +31.6 MHz offset is WRONG. Measured +24.54, and order 2 is converged

The most load-bearing eigenmode-derived number in the project, re-measured
driven at the current design point. **Only `Solver.Order` varies** — same mesh,
same band, same everything — because R36 showed separately built meshes carry
1–3 MHz of scatter, which is 10% of the quantity being measured.

| mode | order 1 | order 2 | **OFFSET** | recorded |
|---|---:|---:|---:|---:|
| **TE₀₁₁** | 2.41692 | 2.44146 | **+24.54** | 🔴 +31.6 — **7.06 MHz wrong** |
| **TM₀₂₀** | 2.37546 | 2.39552 | **+20.06** | ✅ +19.7 assumed — right to 0.4 MHz |

The order-2 driven solve ran clean in 67 min: two distinct modes, boreH 2.084%,
boreE 4.106%, none of the hybridisation that derailed the first R38 attempt.

### ✅ And order 2 is genuinely converged — the check the original never had

An offset only means anything if the thing it extrapolates *to* is fixed. r38's
probe would not build at 0.85; retried at 0.90 it did, and the answer is
emphatic:

| mode | order 2 @ 0.96 | order 2 @ 0.90 | drift |
|---|---:|---:|---:|
| TE₀₁₁ | 2.44146 | 2.44144 | **−0.02 MHz** |
| TM₀₂₀ | 2.39552 | 2.39552 | **+0.00 MHz** |

> ✅ **Order 2 is resolved.** +24.54 is a correction to a fixed target and
> supersedes +31.6. ⚠️ **The original +31.6 was never held to this standard** —
> it was applied for the life of the project without anyone checking that order 2
> had converged.

### 🔑 What this changes, and what it does not

| | recorded | **corrected** |
|---|---:|---:|
| TE₀₁₁ cold | 2.4487 | **2.4416** |
| TE₀₁₁ lit (+16.3 MHz plasma) | 2.4650 | **2.4579** |
| margin to the 2.500 band top | 35 MHz | ✅ **42 MHz** |
| TM₀₂₀ | 2.3900 | **2.3900 — unchanged** |
| TE₀₁₁ − TM₀₂₀ separation | 58.7 MHz | 51.6 MHz |

✅ **Both binding constraints still hold and one improves.** TM₀₂₀ stays 10 MHz
below the band floor (its offset was right, so R39's and R29's margins stand
untouched), and TE₀₁₁ lit has *more* room to the band top, not less. **The design
does not need a retune.**

🔧 **Recorded as a lever, not an action:** if more TE₀₁₁/TM₀₂₀ separation is ever
wanted, shortening L by **0.62 mm** at −11.66 MHz/mm buys back the 7 MHz at zero
cost to TM₀₂₀, whose dL sensitivity is zero.

### 🔑 Q is order-independent; frequency is not

🔢 TE₀₁₁ Q₀ **45,728 → 45,835** from order 1 to order 2 — **+0.23%**.

> ✅ **Every Q result in this file is safe at order 1**: the viewport's −0.9%,
> the electrode's −0.41%, tonight's brake −5.6%. So is every **Δf between two
> cases**, since the offset is systematic and cancels in a difference.
> 🔴 **What is wrong is absolute placement in the band**, which is exactly what
> the design point is.

⚠️ **The offset is geometry-dependent** — it is a discretisation error, and
+31.6 was measured at a = 101.43 / L = 87.67, two design points ago. It was then
carried across a radius change of 2.3 mm and a length change of 0.5 mm without
re-measurement. **Re-measure it whenever the geometry moves materially.**

⚠️ **It is also mode-dependent**: 24.54 vs 20.06, a 4.5 MHz spread. A single
offset applied to both modes would corrupt the *separation*, which is the number
the whole degeneracy argument rests on.

### What to do with the earlier record

**Every converged TE₀₁₁ frequency in this file that was derived with +31.6 is
7.06 MHz high.** Subtract it. Q values, ΔQ values and Δf comparisons are
unaffected. TM₀₂₀ converged values are unaffected.

| # | question | status |
|---|---|---|
| ~~R38~~ ✅ | **CLOSED — offset is +24.54 (TE₀₁₁) / +20.06 (TM₀₂₀); order 2 verified converged** |
| 79 | 🔴 **R38 CLOSED — the +31.6 MHz offset was 7.06 MHz wrong** | Measured driven, same mesh, order 1 vs 2: **TE₀₁₁ +24.54**, TM₀₂₀ **+20.06** (the assumed 19.7 was right). ✅ **Order 2 verified converged** — 0.02 MHz drift from 0.96 to 0.90, a check the original offset never faced. 🔑 TE₀₁₁ cold **2.4487 → 2.4416**, lit 2.4650 → **2.4579**, band margin 35 → **42 MHz**; TM₀₂₀ and both binding constraints unchanged, **no retune needed**. ✅ **Q is order-independent (+0.23%)** so every Q and every Δf in the file survives; only absolute band placement was wrong. ⚠️ The offset is geometry- AND mode-dependent, and +31.6 had been carried across two design points without re-measurement |

---

## 2026-08-16 — ⚠️ CORRECTION to R29's reasoning: tangential H does NOT vanish at a TE₀₁₁ end cap

R29's entry justified the chimney's null with *"E is azimuthal ∝ sin(πz/L) → 0,
and H_r ∝ sin(πz/L) → 0, leaving only H_z"*. **The H claim is wrong**, and it was
repeated in `r29.py`'s pre-registration.

🔢 For TE₀₁₁ with E_φ ∝ J₁(χ′₀₁r/a)·sin(πz/L):

| at the end cap | | |
|---|---|---|
| E_φ | ∝ sin(πz/L) | ✅ **zero** |
| E_z | TE modes have none | ✅ **zero, identically** |
| **H_r** (tangential) | ∝ **cos**(πz/L) | 🔴 **MAXIMUM, not zero** |
| H_z (normal) | ∝ sin(πz/L) | zero |

**The caps carry azimuthal surface current K = H_r φ̂, and they dissipate.**
Getting this backwards would have implied the end caps are lossless, which the
solver's own Q numbers contradict.

### ✅ What survives

The measurement is untouched — TE₀₁₁ −0.06 MHz, +0.19% Q — and so is the
contrast argument, but the correct statement of it is:

> **TE₀₁₁ has no normal E on the cap at all** (exactly zero, by mode structure),
> so there is no electric-dipole coupling. Magnetic coupling through H_r exists
> but is weak here for two compounding reasons: **H_r ∝ J₁(r) vanishes on axis**,
> so at r ≤ 10.5 mm it is only ~⅓ of its own peak, and small-hole coupling scales
> as **(d/λ)³ ≈ 0.005** for 21 mm at 122 mm.
>
> **TM₀₂₀'s E_z is normal to the cap and at its ABSOLUTE MAXIMUM on axis** —
> J₀(0) = 1, exactly where the hole is. An exact zero against an absolute maximum
> is still what produces the measured 13× contrast.

### 🔴 What does NOT survive: the generalisation

The old phrasing implies **any** aperture in a TE₀₁₁ cap is free. It is not.

🔢 Cap current ∝ J₁(χ′₀₁r/a) peaks at **r = 49.8 mm**. A hole at mid-radius sits
in maximum tangential H and would couple to TE₀₁₁ strongly — the opposite of the
chimney's result.

> 🔑 **Cap apertures are free only NEAR THE AXIS.** The chimney and the feed
> feedthrough qualify (r ≤ 10.5 mm, J₁ → 0). Anything at mid-radius — a
> thermocouple port, a pressure tap, a bolt circle penetrating the cap — does
> not, and must be simulated rather than assumed free by analogy.

⚠️ **This is why the caps are not PEC in the model and must not be.** Their loss
is real and is part of every Q in this file.

| 80 | ⚠️ **CORRECTION — tangential H is MAXIMAL at a TE₀₁₁ cap, not zero** | R29's stated reason was wrong: H_r ∝ **cos**(πz/L). ✅ The measurement and the 13× contrast stand — the real asymmetry is TE₀₁₁'s **exactly zero normal E** against TM₀₂₀'s **absolute-maximum E_z on axis**, plus J₁→0 on axis and (d/λ)³ ≈ 0.005. 🔴 **The generalisation dies**: cap current peaks at **r = 49.8 mm**, so cap apertures are free only near the axis. A mid-radius port would couple strongly and must be simulated, not assumed free |

---

## 2026-08-16 — 🔴 HARNESS TRAP: `queue.py` shadowed the stdlib, and an `import` ran 43 minutes of Palace

A one-line Bessel-function calculation, run from `experiments/waveguide/`,
silently launched three Palace solves and consumed **~43 minutes of 4-rank CPU**
(17:41–18:24) concurrently with the R38 order-2 run.

**Mechanism, and it is entirely mundane:**

1. The command imported `scipy.special`.
2. Something in scipy's import chain does `import queue` — a **standard library
   module**.
3. Python puts the **current working directory first on `sys.path`** for
   `python -c`, so `import queue` resolved to **`./queue.py`**, this project's
   R2/R6/R3 recheck driver.
4. `queue.py` was **top-level code with no `if __name__ == "__main__"` guard**,
   so *importing* it ran the whole sweep: meshing, three solves, the lot.

🔢 Verified without executing anything, via `importlib.util.find_spec`:

| | resolves to |
|---|---|
| before | `…/experiments/waveguide/queue.py` |
| after the rename | `/usr/lib/python3.12/queue.py` ✅ |

### What it cost, and what it did not

✅ **No result is corrupted.** The sweep wrote `sig4x`, `tiltvp` and `o2drv`
outputs, none of which any current work reads, and its meshes are built at the
**old** a = 101.43 / L = 87.67 geometry. R38's numbers are unaffected — the solve
is deterministic, it was only slowed by the contention.

⚠️ **It did overlap an active run while `geometry.py` was being edited**, which
is the one condition [the background-job rules] say never to create. It happened
to be harmless because the stale-geometry meshes are unused, but the collision
was real and was not visible at the time.

### Fixed

`queue.py` → **`recheck_queue.py`**. Checked every other `*.py` here against
`sys.stdlib_module_names`: **no other filename shadows a standard module.**

> 🔑 **Never name a script in a working directory after a stdlib module**, and
> give any script with top-level side effects a `__main__` guard. The failure is
> silent, it is triggered by code that has nothing to do with the script, and
> here the side effect was a 43-minute solve rather than an error message.

⚠️ **This one was found by accident** — the stray output appeared in a task log
that was being read for an unrelated reason. Had the Bessel command not been the
thing that timed out, the CPU would simply have gone missing.

| 81 | 🔴 **`queue.py` shadowed the stdlib `queue`; an import ran 43 min of Palace** | `import scipy.special` → chain imports `queue` → CWD is first on `sys.path` → resolved to this project's R2/R6/R3 driver, which has **no `__main__` guard**, so importing it SOLVED. ✅ No result corrupted (stale-geometry tags, unread) but it contended with the R38 order-2 run and overlapped live `geometry.py` edits. **Renamed to `recheck_queue.py`**; verified no other filename here shadows a stdlib module |

---

## 2026-08-16 — ✅ R15 CLOSED: loaded Q converges at 320, and the number in use was 55% low

R10 had already shown the plasma-induced *frequency shift* is order-robust. What
was never checked is the loaded **Q**, which is what any quantitative
impedance-collapse or matching claim rests on — and Q is exactly the quantity
that depends on resolving the field INSIDE the conductor.

🔢 The length to resolve is the RF skin depth: δ = √(2/ωμσ) = **1.86 mm** at
σ = 30 S/m. The R12 sub-region was being meshed at 1.5 mm near the quartz wall
growing to 15 mm inland — under one element per skin depth.

| plasma mesh | tets in region | elements per δ | Q₀ | loaded f |
|---:|---:|---:|---:|---:|
| 1.2 mm | 15,544 | 1.5 | 311 | 2.43115 |
| 0.8 mm | 49,231 | 2.3 | 319 | 2.42735 |
| **0.6 mm** | **115,605** | **3.1** | **320** | 2.43240 |

✅ **Converged: 0.3% across the finest two, over a 7.4× refinement of the
region.** Loaded Q at σ = 30 S/m is **320**, against the ~144 previously in use —
**the old figure was 55% low.**

🔧 Consequences: loaded linewidth is **7.6 MHz**, not 16.9. The collapse from
unloaded 45,728 is **143×**, and against the β = 2.76 coupled linewidth of
~199 kHz the capture range grows ~38×, not the 60× in entry 47. **The conclusion
of entry 47 is unchanged** — the strike is easy and pre-strike drift is the hard
part — but the figure should be recomputed at Q = 320.

⚠️ **Loaded FREQUENCY is not converged and this run cannot settle it.** The three
values span 5 MHz on a resonance whose linewidth is 7.6 MHz; that is peak-location
noise on a broad flat maximum, not physics. Q is well determined because it comes
from an energy integral; the peak *position* is not. R10's +21.11 vs +21.10 MHz
agreement was measured across solver orders on ONE mesh, which cancels this — it
is not evidence that the loaded frequency is reproducible across meshes.

### 🔴 TWO silent no-ops found on the way, either of which would have faked the answer

| # | what was asked | what happened |
|---|---|---|
| 1 | plasma size via `set_pts` | **ignored** — `Mesh.MeshSizeExtendFromBoundary = 0`, so a size prescribed at boundary POINTS never reaches a volume interior. Mesh changed by 795 tets where ~29,000 were expected |
| 2 | plasma size via a Cylinder FIELD | **clamped** — `Mesh.MeshSizeMin` was h_qtz×0.8 = 1.2 mm, and gmsh clamps every requested size to that floor. The 1.0 and 0.6 mm cases came back as the SAME mesh: 14,703 vs 14,586 tets |

🔴 **The second one produced a verdict.** The run reported *"39.5% apart, NOT
CONVERGED"* while comparing a mesh against itself. Had it reported convergence
instead, R15 would have been closed on a number that was never computed.

> 🔑 **Both failures are silent no-ops, not wrong answers.** Neither raises an
> error; both yield confident output from a mesh that never changed. **The check
> that catches both is a postcondition on element count** — "the region's tet
> count must change by ≥N% between densities" — which no script here has.
> Caught only by counting elements by hand afterwards.

### 🔑 Under-resolved, this quantity is unstable — not merely inaccurate

🔢 The two clamped meshes differed by **0.8% in element count** and returned
**Q = 149 and Q = 208**, a 40% swing. Refined properly, three meshes spanning
7.4× in density agree to 0.3%.

> ✅ **Instability is the signature of the under-resolved regime here**, and
> convergence is sharp once δ is resolved at ~2 elements. A Q difference of tens
> of percent between coarse plasma meshes means nothing at all.

⚠️ **σ-specific.** δ ∝ 1/√σ, so a denser plasma needs a finer mesh than this.
At σ = 100 S/m, δ = 1.02 mm and 0.6 mm would be back to ~1.7 elements per δ.
⚠️ Built at common size-factor **0.93**, not the usual 0.96 — the fine meshes
would not curve at 0.96 — so these are comparable to each other and **not**
directly differenceable against the day's other runs.

| # | question | status |
|---|---|---|
| ~~R15~~ ✅ | **CLOSED — loaded Q = 320 at σ=30, converged 0.3% over a 7.4× refinement** |
| **R50** | **Add postconditions to the harness**: assert that a requested refinement changed the mesh, and that a sweep's achieved size-factor is recorded, not just its requested one | open — this is the testing-infrastructure work, and it has two confirmed failures behind it |
| 82 | ✅ **R15 CLOSED — loaded Q is 320, not 144** | Converged to **0.3%** across 1.2/0.8/0.6 mm (15.5k → 115.6k tets in the region, 3.1 elements per skin depth). **The figure in use was 55% low.** Loaded linewidth **7.6 MHz**, collapse 143×, capture range ~38× not 60× — entry 47's conclusion survives, its number does not. ⚠️ Loaded *frequency* is NOT converged: 5 MHz spread on a 7.6 MHz-wide peak, peak-location noise. 🔴 **Two silent no-ops found** (`set_pts` vs ExtendFromBoundary=0; Cylinder field vs MeshSizeMin floor) — the second reported a verdict from a mesh compared against itself. R50 opened for postconditions |

---

## 2026-08-16 — ✅ R49 CLOSED: the unmodelled feed aperture costs 2× what the modelled one does

The torch penetrates the −z cap to reach its plumbing. `geometry.py` ended the
tube flush against solid metal, so **that aperture had never existed in any
simulation** — every number on this design was taken on a cavity with one hole
when the real object has two. `--feed D,LEN` and `--torch-ext MM` add it, with
the outer tube continuing through, which is what makes it dielectric-loaded
rather than an air hole.

| case | TE₀₁₁ Δf | TE₀₁₁ ΔQ | TM₀₂₀ Δf |
|---|---:|---:|---:|
| no feed | — | — | — |
| 21 × 10 mm | +0.00 | −0.79% | **+2.70** |
| 21 × 20 mm | −0.04 | −1.10% | **+2.70** |
| **21 × 41 mm** | **−0.24** | **−1.18%** | **+2.58** |

### 🔴 The aperture costs more than twice the chimney, and they add

🔢 TM₀₂₀ rises **+2.70 MHz**, against the exhaust chimney's +1.26 for the same
21 mm diameter. Both are near-axis cap apertures and TM₀₂₀ has p = 0 — equal
field at both caps — so to first order they are additive:

| | TM₀₂₀ headroom below 2.400 | bore tolerance at −22 MHz/mm |
|---|---:|---:|
| design point as recorded | 10.0 MHz | ±0.45 mm |
| with the chimney (R29) | 8.7 MHz | ±0.40 mm |
| **with BOTH apertures** | **6.0 MHz** | **±0.27 mm** |

> ⚠️ **The drawing callout of ±0.2 mm still passes** — but the cushion between
> callout and budget has gone from 2.25× to **1.35×**. That is the whole margin
> on the binding machining dimension, spent by a feature that was never in the
> model.

⚠️ **My prediction was wrong by 2.1×.** I pre-registered "roughly the chimney's
+1.26 MHz" on the grounds of equal diameter and cap symmetry. The feed aperture
does more, plausibly because the on-axis gas column *continues* through it —
TM₀₂₀'s E_z is maximal on axis, and extending that region gives the field
somewhere to go, where the chimney's dielectric-free step does not. ✅ I declined
to predict the *sign* given two competing effects; it is **up**.

### ✅ TE₀₁₁ is untouched; the cost there is Q, and it is length-dependent

🔢 TE₀₁₁ moves **−0.24 MHz** at 41 mm — nothing, as expected for a near-axis cap
aperture. But Q falls monotonically with feed length: **−0.79 / −1.10 / −1.18%**
at 10 / 20 / 41 mm. That is not leakage; it is the quartz tanδ and the added wall
area of a longer tube. **Budget 1.2% of Q for the feedthrough**, against the
chimney's +0.19% — the difference is that the chimney is empty and this one has
the torch in it.

### ⚠️ The isolation test did not discriminate, and the control is why

The plan was length-independence: if the tube is below cutoff, f and Q stop
moving once it is a few decay constants long, with **10 mm as a positive
control** that should still be short enough to move.

🔴 **It didn't move.** TM₀₂₀ is +2.70 at both 10 and 20 mm. So the run cannot
distinguish "properly isolated" from "test too blunt to see anything", and the
script says so rather than claiming a null.

🔢 On reflection the control was mis-sized, not the method: at an estimated
~1.0–1.2 dB/mm the decay length is **3–4 mm**, so 10 mm is already ~3 decay
lengths. What the data does support is bounded and still useful:

> ✅ **Beyond 10 mm there is no detectable length dependence** — 20 → 41 mm moves
> TM₀₂₀ by −0.12 MHz against a +2.70 MHz aperture effect, i.e. any far-end
> contribution is **under 5%**, with ~0.2 MHz of resolution in this mesh family.
> **41 mm is ample and 20 mm would do.** What is NOT established is the decay
> length itself, which needs 2/4/6 mm cases.

⚠️ The frequency resolution *within this family* is ~0.2 MHz — far better than
the 1.5 MHz mesh-to-mesh scatter of R36 — because these four meshes differ only
by the feed geometry. Do not generalise 0.2 MHz to comparisons across sweeps.

| # | question | status |
|---|---|---|
| ~~R49~~ ✅ | **CLOSED — feed aperture costs TM₀₂₀ +2.70 MHz and 1.2% of Q; 41 mm is ample** |
| **R51** | **Measure the evanescent decay length** with 2/4/6 mm feed tubes. Only needed if the feed is to be shortened for packaging, or to check the sapphire (ε = 11.6) case where the cutoff falls further | open — low |
| 83 | ✅ **R49 CLOSED — the aperture nobody had modelled costs 2× the one we did** | `--feed`/`--torch-ext` added; regression-checked that the feature off reproduces the old mesh exactly. 🔴 **TM₀₂₀ +2.70 MHz** vs the chimney's +1.26; additive, so headroom **10.0 → 6.0 MHz** and bore tolerance **±0.45 → ±0.27 mm**. The ±0.2 mm callout still passes but the cushion drops 2.25× → 1.35×. ✅ TE₀₁₁ unmoved (−0.24 MHz) but **Q −1.2%**, rising with length — quartz tanδ, not leakage. ⚠️ The 10 mm positive control did not move, so isolation is bounded (<5% far-end contribution beyond 10 mm) rather than measured; decay length ~3–4 mm estimated, R51 opened. ⚠️ My +1.26 prediction was 2.1× low |

---

## 2026-08-16 — The brake's shape, measured; a mounting constraint; and a deferred optimization

Characterised off `choff.msh` rather than from source, so this is what is being
solved.

| | |
|---|---|
| form | two flat annular discs, one flush against each end cap |
| outer radius | **103.70 mm** (OD 207.4) — wall to wall |
| inner radius | **10.0 mm** — clearance on the torch OD; it touches the tube |
| thickness | **3.0 mm**, at z = −44.27…−41.27 and +41.27…+44.27 |
| material | fused quartz, ε 3.78, tanδ 1e−4 |
| volume | 100.4 cm³ each — **200.8 cm³, 442 g total** |

A 69:1 diameter-to-thickness washer. The shape follows from where the mode
families differ: at a cap TE₀₁₁'s E is identically zero (∝ sin πz/L) and every
TM_mn1's E_z is maximal, so a dielectric there is maximum differential. Being a
FULL annulus it is rotationally symmetric and introduces no azimuthal mixing —
which matters more than it looks, given R36.

### 🔧 ACT NOW — the brake cannot be rim-clamped

🔢 Fused quartz CTE **0.55e−6/K** against aluminium's **23e−6/K**. Over 207.4 mm
and a 100 K rise the cap grows **0.47 mm** more than the disc — **0.23 mm
radially**.

> **The mount needs deliberate radial clearance, or the disc cracks.** At 442 g
> across a 207 mm span, support and retention are not trivial either. This is a
> constraint on the design as it stands, not a consequence of any change.

⚠️ Also: the drawing row was corrected after R39 to say 3 mm is required rather
than stock. **The expensive dimension is the DIAMETER** — a 207.4 mm × 3 mm fused
quartz annulus with a 20 mm bore is a custom optical-scale part, twice over, and
it is still described as though it were catalogue.

### ⏸️ DEFERRED — the disc may be much larger than it needs to be

🔢 TM₀₂₀'s E_z ∝ J₀(5.5201 r/a) crosses zero at **r = 45.2 mm** and only reaches
|J₀| = 0.40 again at r = 72 mm. Weighting |E_z|² by area, the region from 10 to
45 mm carries **roughly half** the perturbation on **~22%** of the disc's area.
If that carries to the TE₀₁₁/TM₁₁₁ splitting the brake actually exists for, a
**~100 mm OD annulus could do most of the job with a fifth of the quartz** —
cheaper, lighter, far easier to mount.

⚠️ **Estimate only, on the EMPTY-cavity profile.** The brake and torch together
shift TM₀₂₀ by 154 MHz (entry 74), so the loaded radial profile differs. Do not
act on this without a solve.

> ⏸️ **Deferred deliberately: this is an optimization, and it comes after the
> harness refactor and the falsification pass.** Optimizing a shape before the
> harness can regress it means being unable to tell a better brake from a worse
> solve. The estimate is recorded here so it need not be re-derived.

| # | question | status |
|---|---|---|
| **R52** | **Narrow the brake annulus** — sweep outer radius 103.7 → ~50 mm, watching **TE₀₁₁/TM₁₁₁ separation**, not TM₀₂₀. Needs a `--brake-ro` parameter, which does not exist | ⏸️ **deferred — optimization, after R50 and falsification** |
| **R53** | **Radial clearance and retention scheme for a 207 mm × 3 mm quartz annulus** under 0.23 mm of differential expansion | open — mechanical, applies to the design as it stands |
| 84 | 🔧 **Brake characterised: 207.4 × 3 mm quartz annulus, 442 g the pair** | Full-annulus shape is what makes it azimuthally clean. 🔧 **CTE mismatch 0.23 mm radial over 100 K — it cannot be rim-clamped** (R53, applies now). ⚠️ The costly dimension is the diameter, still described as catalogue. ⏸️ **R52 deferred**: |E_z|²-by-area says the inner 45 mm carries ~half the effect on ~22% of the area, so a ~100 mm OD annulus may suffice — estimate on the empty-cavity profile, recorded so it is not re-derived, to be tested AFTER the refactor |

---

## 2026-08-16 — TERMINOLOGY: the "dielectric brake" is a MODE FILTER

**Adopted: the quartz annulus at each end cap is a MODE FILTER.** "Dielectric
brake" was this project's own coinage. It maps onto no RF literature and no
vendor vocabulary, which has been silently costing us both searchability and the
ability to describe the part to anyone outside this file.

✅ **The name is right on mechanism, not just convention.** R39's data shows it
discriminates on both axes:

| | no filter | 3 mm | |
|---|---:|---:|---|
| **TM₀₂₀ Q₀** | 27,251 | 23,448 | **−14.0%** |
| TE₀₁₁ Q₀ | 48,457 | 45,727 | −5.6% |

🔢 It dissipates TM **2.5× more** than TE — genuine filter action — on top of the
**68 MHz** of frequency separation that is its dominant effect.

> ⚠️ **State the mechanism when using the term.** "Mode filter" in RF usually
> implies discrimination by LOSS. This one is primarily a frequency separator
> that also damps, so a reader who assumes a lossy suppressor will misread how it
> works — and, more practically, will look for the wrong kind of part.

### Scope of the rename, deliberately limited

| | |
|---|---|
| **prose from now on** | ✅ "mode filter" — README, design docs, new entries |
| **146 historical mentions of "brake" here** | ✅ left alone. This file is append-only and the trail is the asset; they mean the same part |
| **code identifiers** — `--brake`, `brake_t`, `brake_eps`, `TAG_BRAKE`, `name="brake"` | ⏸️ **unchanged, deferred to R50.** 29 uses in `geometry.py` and ~27 scripts reference the flag; renaming now would break a sweep that is running as this is written, and would invalidate every provenance string in `baselines.json` |

> 🔑 **A rename is a refactor.** Doing it piecemeal produces a codebase where both
> names are live and neither is searchable — the exact failure the rename is meant
> to fix. It goes in with R50, atomically, with the regression baselines in place
> to prove nothing moved.

| 85 | 📝 **TERMINOLOGY — "dielectric brake" is a MODE FILTER** | Adopted in prose; the coinage mapped onto no literature or vendor vocabulary. ✅ Justified on mechanism: R39 shows **TM₀₂₀ Q −14.0% vs TE₀₁₁ −5.6%**, a 2.5× loss discrimination, on top of 68 MHz of separation — though it is primarily a frequency separator, which must be said when using a term that usually implies loss. ⏸️ **Code identifiers unchanged, deferred to R50** — 29 uses in geometry.py plus ~27 scripts; a half-done rename leaves both names live and neither searchable |

---

## 2026-08-16 — Mode filter: two corrections to the standard account, and a cheaper alternative

Following the terminology adoption in entry 85. The standard RF framing —
**dielectric loading for mode separation**, the part being a **dielectric mode
suppressor / mode filter** — is correct and adopted. Two things need sharpening
against what this project has actually measured.

### ⚠️ 1. TM₁₁₁ has never been positively identified here

The textbook justification is TE₀₁₁/TM₁₁₁ degeneracy, and it is structural: this
file's own constants record **χ′₀₁ = χ₁₁ = 3.8317** exactly, which is why the two
families collide at all.

🔢 But every number we have on the filter's effect is measured on **TM₀₂₀**:
68.2 MHz of shift when the 3 mm annulus is removed (2.44366 → 2.37546 raw, R39).
The only TM₁₁₁-shaped evidence is the mode appearing **+3.2 MHz from TE₀₁₁** with
the filter deleted, carrying boreH 1.25% — consistent with an m = 1 partner and
**never identified**, because `--sectors 1` carries no azimuthal information.

> ⚠️ **The part's headline justification rests on a degeneracy we have only seen
> indirectly.** This raises the value of **R47** considerably: it is the only
> route to positively identifying the m = 1 modes, and it was filed as low
> priority when its only purpose was corroborating R36.

### 🔴 2. Grooves are NOT the same mechanism — they discriminate by LOSS

A common account has metal grooves in the end plates achieving "the same mode
separation". They do not: they achieve the same *outcome* by a different route.

| | mechanism | cost to TE₀₁₁ |
|---|---|---|
| **quartz annulus** (ours) | **detunes** TM by dielectric loading at the E_z maximum | **5.6% of Q**, 442 g of custom quartz |
| **groove / choke joint** | **damps** TM by interrupting its radial wall current | ~nothing — TE₀₁₁ has no current there to interrupt |

🔑 The enabling property is the one corrected in entry 80: **TE₀₁₁'s surface
current is purely azimuthal on the barrel AND on the caps, so nothing crosses the
cap-to-wall seam.** TM₁₁₁'s current is radial and must cross it. That is why
precision TE₀₁₁ cavities are routinely built with non-contacting end plates.

⚠️ **And the usual "grooves avoid complex CNC" framing is backwards for us.** A
circumferential groove is turning work on a part already being turned. Two
**207.4 mm × 3 mm fused quartz annuli with 20 mm bores** are custom optical
parts. **The quartz is the expensive route, not the cheap one.**

⚠️ Constraint we have that the textbook case does not: the cavity is **N₂-purged
at 1.3–2 atm** (R28), so a genuinely open non-contacting cap leaks. It would have
to be a blind groove or a λ/4 choke, and whether that gives enough discrimination
is unknown without a solve.

| # | question | status |
|---|---|---|
| **R54** | **Groove / λ/4 choke as the mode filter instead of the quartz annulus.** Damps TM₁₁₁ rather than detuning it; potentially recovers the 5.6% Q and deletes a 442 g custom part. Must respect the 1.3–2 atm purge, so blind groove or choke, not an open gap | ⏸️ **deferred — optimization, after R50 and falsification** |
| **R47** | *(re-prioritised)* Sector-resolved azimuthal identification — **now the only route to confirming TM₁₁₁ exists where the theory says**, not merely corroborating R36 | open — **raised from low** |
| 86 | ⚠️ **The mode filter's justification rests on a mode we have never identified** | Every measured number is **TM₀₂₀** (68.2 MHz on removal); **TM₁₁₁ has never been positively identified** — the +3.2 MHz neighbour at zero thickness is consistent but unresolved at `--sectors 1`. **R47 re-prioritised.** 🔴 Also: grooves are NOT the same mechanism — they **damp** TM by cutting its radial cap current (TE₀₁₁'s is purely azimuthal, entry 80) rather than **detuning** it. ⚠️ The "grooves avoid complex CNC" framing is backwards here: turning a groove is cheaper than two custom 207 mm quartz annuli. **R54** opened, deferred |

---

## 2026-08-16 — Mode filter retention: the rim is a field null, and that resolves R53

Extends R53. The question was whether the quartz annulus can be attached to the
end plates without creating an arcing site.

✅ **The quartz-to-metal interface is not the risk.** Partial discharge at a
dielectric/metal gap needs E **normal** to the interface — a void then sees ε_r
times the field in the solid. At a TE₀₁₁ cap the field is E_φ, **tangential** and
vanishing. The mode that would drive it is the TM family, whose E_z is normal and
maximal there (which is why the filter works), and TM₀₂₀ is below the band floor
and unreachable by the amplifier.

🔴 **The risk is retention hardware standing proud of the disc.** At 3 mm above
the cap, E_φ has recovered to **sin(3π/88.53) = 10.6% of peak**:

| | at the disc's outer face |
|---|---:|
| peak unlit field @ 1 kW (R28: 16.9 kV/cm) | 1.8 kV/cm |
| peak unlit field @ 8 kW (√P scaling → 47.8) | **5.1 kV/cm** |
| air breakdown | 30 kV/cm |

🔢 **A factor of 5.9 in hand at full power** — which a sharp clip edge consumes,
since 10× edge enhancement is routine. Same rule the striker was designed around.

### 🔑 The outer rim is an exact field null

E_φ ∝ J₁(χ′₀₁·r/a), and **J₁(χ′₀₁) = 0 by the boundary condition itself**, so
E_φ = 0 at r = a for every z. **Retention at the rim is electrically free.**

> 🔑 **This resolves R53's apparent conflict.** The rim is simultaneously the
> electrically ideal place to retain the disc and the place 0.23 mm of
> differential expansion has to go. Both constraints point at one answer:
> **compliant rim retention** — a retaining ring or spring clips at r = a,
> rounded, flush or recessed, with deliberate radial float.

🔴 **No adhesive.** An organic bond line outgasses, adds RF loss, and carbonises
under heat — and carbon is conductive, which is the OD-fouling failure mode
arriving by another route.

| 87 | ✅ **Mode filter retention resolved in principle — compliant rim clips** | Interface arcing is a non-issue: TE₀₁₁'s field at the cap is **tangential and zero**, and gap enhancement needs NORMAL E, which only the unexcited TM family has. 🔴 Real risk is hardware standing proud — at 3 mm height E_φ is **10.6% of peak**, giving **5.1 kV/cm at 8 kW** against 30 kV/cm breakdown, only **5.9×** before edge enhancement. 🔑 **The rim is an exact field null (J₁(χ′₀₁) = 0)**, and it is also where the 0.23 mm CTE differential must go — so rim retention, rounded, flush, with radial float. **No adhesive** |

---

## 2026-08-16 — ✅ R48 CLOSED: the shift saturates by 6 mm, and my "shorted stub" story was overstated

R29 left the chimney's **upward** TM₀₂₀ shift explained only by a post-hoc guess:
that a PEC-terminated below-cutoff tube acts as a shorted evanescent stub loading
the aperture inductively. R48 tests the checkable part — the shift must saturate
with length, and must vanish as L → 0, where the tube is only a dimple in the cap.

Four cases at common size-factor 0.96, 21 mm bore:

| chimney | TM₀₂₀ Δf | % of saturation | evanescent model (TE₁₁) | TE₀₁₁ Δf |
|---:|---:|---:|---:|---:|
| none | — | — | — | — |
| **2 mm** | **+0.92** | **74.2%** | 48.9% | +0.02 |
| 6 mm | +1.22 | 98.4% | 86.6% | +0.06 |
| 41 mm | +1.24 | 100% | 100% | −0.06 |

✅ **The control moved.** Unlike R49, where the 10 mm "control" was already three
decay lengths long and proved nothing, 2 mm is short enough to be partial. The
method has demonstrated sensitivity, so the saturation at 41 mm is a real null.

✅ **Cross-sweep agreement: +1.24 MHz here against R29's +1.26.** Two independent
sweeps, 0.02 MHz apart. That is a direct confirmation of the baselines claim that
**Δf measured WITHIN a sweep is reliable** even though absolute f carries 1–3 MHz
of mesh-to-mesh scatter.

### 🔴 The onset is twice as fast as the TE₁₁ estimate

🔢 Fitting 1 − exp(−2αL) to both loaded points gives **α = 0.34 Np/mm, decay
length 2.9 mm** — consistently from both, against the **5.96 mm** predicted from
the TE₁₁ cutoff of 8.37 GHz.

> 🔑 **TE₁₁ is the lowest-cutoff mode, so it decays SLOWEST — but only matters if
> it is excited.** The aperture is on-axis and TM₀₂₀ drives it with axial E, which
> excites TM-type evanescent modes, and those have higher cutoffs and decay
> faster. Sizing the tube from TE₁₁ is therefore **conservative for perturbation**.
>
> ⚠️ **It remains the right basis for LEAKAGE**, because leakage is a worst-case
> question: whatever excites TE₁₁ still gets the slow 1.46 dB/mm decay. Do not use
> the 2.9 mm figure to shorten the chimney.

### ⚠️ Partial retraction of my own explanation

**74% of the shift is already present at 2 mm**, where the termination is 2 mm
away. So the effect is dominated by the **aperture opening itself**, with a ~26%
evanescent tail that saturates by ~6 mm. My "shorted stub loading it inductively"
framing implied the termination did most of the work. **It does not.** The stub
picture survives only as the small tail, not as the mechanism.

⚠️ **Prediction scorecard:** monotone ✅, no sign change ✅, saturating ✅, control
moved ✅ — rate wrong ❌ (74% vs 49% at 2 mm).

⚠️ Q is unaffected throughout: TE₀₁₁ +0.24/+0.09/+0.11%, TM₀₂₀ +0.32/+0.95/+0.61%,
all inside scatter.

| # | question | status |
|---|---|---|
| ~~R48~~ ✅ | **CLOSED — saturates by 6 mm; decay length 2.9 mm measured; 41 mm ample for perturbation, and NOT a licence to shorten** |
| 88 | ✅ **R48 CLOSED — chimney shift saturates by 6 mm, decay length 2.9 mm** | 2 mm gives **74%** of the +1.24 MHz saturated shift, 6 mm gives 98%. ✅ Control moved, so the null at 41 mm is real. ✅ **+1.24 vs R29's +1.26 across independent sweeps** — Δf within a sweep is trustworthy. 🔴 Measured decay is **2.9 mm, half the 5.96 mm TE₁₁ estimate**, because an on-axis aperture driven by axial E excites higher-cutoff TM modes; TE₁₁ stays the right basis for **leakage** as the worst case. ⚠️ **Partial retraction**: 74% of the effect exists at 2 mm, so it is the APERTURE, not the shorted-stub termination I invented in R29 |

---

## 2026-08-16 — 🔑 R47 CLOSED: TM₁₁₁ POSITIVELY IDENTIFIED, and R39's "TE₀₁₁ is robust" was under-resolved

R47 was low priority until entry 86 pointed out that **the mode filter's entire
justification is a degeneracy nobody here had ever observed.** Every number was
TM₀₂₀. With `--loop-phi 36` clearing the sector planes at `--sectors 5`, the
azimuthal content is now measurable — by DFT over the five sector energies, not
by the CV scalar, which says "not axisymmetric" without saying how.

🔢 A mode of index m has energy ∝ cos²(mφ), i.e. spatial frequency **2m**:
**bin 2 → m = 1**, **bin 1 → m = 2** (aliased at N = 5).

### ✅ TM₁₁₁ exists, is m = 1, and the filter moves it 45 MHz

| | TE₀₁₁ | **TM₁₁₁** | separation |
|---|---:|---:|---:|
| **filter 3 mm** | 2.41524 | **2.35094** (bin2 **57.7×** floor) | **64.3 MHz** |
| no filter | 2.41974 | **2.40022** (bin2 **63.6×**) | **19.5 MHz** |

**The mode that has appeared in every run since R36 at boreH ≈ 1.2% — which I
could only call "the resident family" — is TM₁₁₁.** Measured on the mode the
filter was designed against, not inferred from TM₀₂₀.

### 🔴 CORRECTION to entry 77: TE₀₁₁ *does* lose azimuthal purity without the filter

R39 concluded, at `--sectors 1`, that *"TE₀₁₁ does NOT hybridise when the brake is
deleted"* because its bore-H signature stayed clean at 2.08%.

🔢 With azimuthal resolution, unfiltered TE₀₁₁ shows **bin 1 at 23× the floor** —
genuine m = 2 content, ~11% sector-to-sector variation, on a mode whose linewidth
(53 kHz) is 49× smaller than its distance to the nearest neighbour, so this is not
spectral overlap.

> 🔑 **The bore-H signature was intact while the azimuthal purity was not.**
> R39's mechanism conclusion stands — the filter's decisive job is keeping TM₀₂₀
> out of band — but "TE₀₁₁ is robust on its own" was a statement the instrument
> could not make. **Symmetry from boundary conditions is AMIP's whole thesis, so
> azimuthal purity is the more load-bearing measure of the two.**

✅ R39's "+3.2 MHz neighbour" also resolves: it is the mode at **2.42236**,
carrying **both** m = 1 (52.6×) and m = 2 (25.3×) — a genuine hybrid.

⚠️ **Method limit:** at N = 5, bin 1 means m = 2 **or** m = 3, bin 2 means m = 1
**or** m = 4. It separates what matters here; it is not a unique assignment.

### 🔴 `dq.identify` threshold — THIRD occurrence

The calibration block printed twice because `dq.identify` labels the 1.2% TM₁₁₁
family as TE₀₁₁ (`te_h = 0.010`). Same defect that made R39's detector fire on the
known-good case, and that R36 had to work around. **The floor ended up anchored on
the real TE₀₁₁ only by ordering luck.**

> 🔑 **Raise `te_h` to 0.018 in `dq.py` — but as part of R50, not now.** It is
> shared by every script and changing it silently re-labels historical runs. It
> belongs in the atomic refactor, with the baselines in place to prove what moved.

| # | question | status |
|---|---|---|
| ~~R47~~ ✅ | **CLOSED — TM₁₁₁ identified (m=1); filter buys 64.3 vs 19.5 MHz; TE₀₁₁ purity depends on it** |
| **R54** | *(now well-posed)* Geometric mode filter — **target is TM₁₁₁ at m = 1**, metric is **TE₀₁₁–TM₁₁₁ separation AND TE₀₁₁ bin-1/bin-2 purity**, both now measurable | ready to run |
| **R50** | +requirement: `dq.identify` te_h 0.010 → 0.018; derive port `Direction` from loop φ/tilt rather than hardcoding | open |
| 89 | 🔑 **R47 CLOSED — TM₁₁₁ SEEN, first time in this project** | `--loop-phi 36` clears the sector planes at 5 sectors (single port face verified); m from a **DFT of sector energies**, bin2 → m=1, bin1 → m=2. ✅ **TM₁₁₁ at 2.35094 with the filter (64.3 MHz below TE₀₁₁) and 2.40022 without (19.5 MHz)** — the filter buys **45 MHz**, measured on the right mode at last. 🔴 **Corrects entry 77**: unfiltered TE₀₁₁ carries m=2 at **23× the floor**; bore-H looked clean because `--sectors 1` cannot see azimuthal content. R39's "+3.2 MHz neighbour" is a genuine m=1/m=2 hybrid at 2.42236. 🔴 `dq.identify`'s 1% threshold mislabelled TM₁₁₁ as TE₀₁₁ — third occurrence, fix deferred to R50 |

---

## 2026-08-17 — 🔴 The torch no longer fits: 129.5 mm of span against a 120–150 mm catalogue tube

Line 717 records *"cavity 85 mm long, passes a standard 120–150 mm torch straight
through"*. That was written when the cavity was **85 mm** and the model had **no
feed feedthrough at all**. Neither is true now, and nobody recomputed it.

| | mm |
|---|---:|
| cavity length (quartz build) | 88.53 |
| feed feedthrough, as modelled in R49 | 41 |
| **span inside the assembly** | **129.5** |
| catalogue outer tube | **120–150** |

🔴 **At 120 mm it does not fit. At 150 mm, 20.5 mm remains for the base fitting**,
against the 20–30 mm a demountable torch base typically engages.

> ⚠️ **R16's lever is what is at risk** — "the demountable outer tube is a
> catalogue part" (entry 30). If the stack forces a custom length, that lever is
> gone, and it is gone for the SAPPHIRE tube too, where length drives cost.

### The λ/4 groove's role is narrower than it looks, but real

The groove sits at r ≈ 100–104 mm and does not lie in the torch's path. What it
does is force the **cap to be ≥ 33 mm thick** (30.6 mm of groove plus backing),
and the torch passes through that cap.

> 🔑 **So a λ/4 groove and a short feed passage are mutually exclusive — if the
> groove is a pocket in the CAP.** That kills the lever R49 identified when it
> found 20 mm of feed was enough.

✅ **The escape is a fabrication choice, not an electromagnetic one.** Cut the
groove as a **counterbore in the BARREL end** instead of a pocket in the cap.
Electromagnetically it is the identical annular slot at the identical corner —
the solver cannot tell which side of the joint the metal belongs to — but the cap
can then be thin, the feed passage short, and the groove depth lives at large
radius where nothing competes for it.

### 🔴 An unstated trade: leakage wants the feed long, the torch wants it short

R49's "41 mm is ample" was about **perturbation saturation**, with leakage
explicitly left open. 🔢 At the estimated ~0.76 dB/mm for a dielectric-loaded
aperture, **41 mm gives only ~31 dB, not 60** — so leakage may want it LONGER,
while the torch wants it SHORTER. Those pull opposite ways.

⚠️ **Do not shorten the feed on R49's evidence alone.** That would repeat exactly
the error flagged in R48: near-field saturation is not leakage.

| # | question | status |
|---|---|---|
| **R55** | **Axial stack budget**: cavity + feed passage + base engagement against a catalogue tube. Decide groove-in-barrel vs groove-in-cap, and settle the feed length against BOTH leakage and torch reach | 🔴 **open — blocks committing to a cap design** |
| 90 | 🔴 **The torch does not fit any more** | **129.5 mm of span** (88.53 cavity + 41 feed) against a **120–150 mm** catalogue tube — at 150 that leaves **20.5 mm** for a base needing 20–30. The "passes straight through" claim dates from an 85 mm cavity with no feedthrough modelled. ⚠️ Puts **R16's catalogue-part lever** at risk. 🔑 λ/4 grooves force a **≥33 mm cap**, which excludes the short feed R49 showed was sufficient — unless the groove is cut as a **counterbore in the barrel**, which is electromagnetically identical. 🔴 New trade: **leakage wants the feed longer (31 dB at 41 mm, not 60), the torch wants it shorter.** R55 opened |

---

## 2026-08-17 — ⚠️ CORRECTION to entry 90: the groove does NOT constrain the feed length

Entry 90 claimed a λ/4 groove forces a ≥33 mm cap, and therefore excludes the
short feed passage R49 showed was sufficient. **That is wrong.** The cap needs
33 mm of metal only **at the groove radius** (r ≈ 100–104 mm). The middle can be
relieved, and doing so is machining cost, not a constraint.

🔢 Structurally there is ample room. Clamped circular plate, σ = 3pR²/4t², at
R = 103.7 mm and 1 atm differential (conservative — the purge differential is
0.3–1.0 atm):

| target stress | required t |
|---|---:|
| 90 MPa (⅓ of 6061-T6 yield) | **3.0 mm** |

An 8–10 mm web is already a ~7× margin.

### ⚠️ But the relief must be ANNULAR, leaving a central boss

🔑 **The feed's below-cutoff length is the metal surrounding the BORE, not the
cap's nominal thickness.** Hog a pocket that surrounds the feedthrough and the
isolation length collapses to the web — 🔢 **8 mm at ~0.76 dB/mm is ~6 dB**,
which is nothing.

> **Shape: thick rim carrying the groove, thin annular web, central boss carrying
> the feedthrough bore.** One billet, three diameters, all turning work. The same
> applies at the +z cap, where the chimney is already conceived as a tube standing
> proud of the cap rather than a bore through it.

✅ **Net effect on entry 90:** the groove/feed conflict dissolves. What survives
unchanged is the real trade — **leakage wants the feed long, torch reach wants it
short** — and the 129.5 mm span against a 120–150 mm catalogue tube. R55 stands,
with one option removed from it: groove-in-cap vs groove-in-barrel no longer
decides the feed length either way.

| 91 | ⚠️ **CORRECTION to 90 — relief is machining cost, not a constraint** | The cap needs 33 mm only **at the groove radius**; a relieved middle is fine, and structurally 3.0 mm carries 1 atm at ⅓ yield so an 8–10 mm web is 7× margin. ⚠️ **The relief must be ANNULAR with a central boss** — the feed's isolation length is the metal around the BORE, and a pocket surrounding it would cut isolation to ~6 dB. ✅ The groove/feed conflict in entry 90 is withdrawn; the leakage-vs-torch-reach trade and the 129.5 mm span stand |

---

## 2026-08-17 — 🔴 R56 OPENED: what matches the LIT cavity? With fixed coupling and no tuner, nothing does

Raised while questioning whether a circulator is required. The circulator turns
out to be the smaller question.

🔢 From tonight's numbers and entry 47:

| | |
|---|---:|
| Q₀ unlit | 45,728 |
| β unlit | 2.76 → **Q_ext = 16,568** |
| Q₀ lit at σ = 30 S/m (R15) | **320** |
| **β lit** = Q₀/Q_ext | **0.019** |
| **\|Γ\|² lit** | **≈ 0.93** |

Q_ext is set by loop geometry and cannot follow the plasma. The cavity goes from
**over-coupled (β = 2.76)** unlit to **badly under-coupled (β = 0.019)** lit, and
reflects ~93% of forward power. Sizing the loop for the lit state instead gives
β = 143 unlit and ~97% reflection. **One state is always badly mismatched.**

✅ Inputs cross-check: Q_L = Q₀/(1+β) = 12,162 → 199 kHz linewidth, against the
207 kHz entry 47 records. The arithmetic is consistent with the file.

> 🔑 **This is not a protection question.** A circulator protects an amplifier
> from a transient; it does not turn a 93%-reflecting system into an instrument.
> And **"no tuner, no moving parts" is an explicit design commitment** — there is
> no matching network to retune between states, which is exactly what
> conventional ICP/MIP systems use to bridge this.

### 🔑 The consequence: this probably sets the SAMPLE FEED RATE

Plasma conductivity depends on what is in the plasma. Aerosol loading — solvent
uptake and dissolved solids — changes electron density and the energy balance, so
**σ is a function of sample feed rate**. With fixed coupling, only a window of σ
gives an acceptable match.

> 🔑 **The tolerable match window therefore sets a tolerable loading window, which
> sets an uptake rate and a dissolved-solids ceiling.** That is an
> analytical-method constraint derived from an RF one, and it lands on the actual
> product: **Mehlich-3 is a salty extractant** (NH₄NO₃, NH₄F, HNO₃, EDTA, acetic
> acid), which is the high-TDS case.

### What would settle it

Sweep σ over a plausible range on R15's converged recipe, giving Q₀(σ) → β(σ) →
|Γ|²(σ), and read off the window where reflection is acceptable.

⚠️ **Mesh caveat, from R15:** δ ∝ 1/√σ, and the 0.6 mm plasma mesh gives 3.1
elements per skin depth only at σ = 30. At σ = 300, δ = 0.59 mm and that mesh is
down to **one element per skin depth** — under-resolved, which R15 showed makes
loaded Q unstable at the ±40% level. **High-σ cases need a finer mesh than the
one that closed R15.**

⚠️ Two things could soften the result and neither is settleable from here: σ = 30
is a model value, and R22's "99.1% of power delivered to the plasma" is a
different quantity — where ABSORBED power goes, not how much is absorbed — so it
does not contradict this.

| # | question | status |
|---|---|---|
| **R56** | 🔴 **What matches the lit cavity?** Fixed Q_ext = 16,568 against Q₀ collapsing to ~320 gives \|Γ\|² ≈ 0.93. Map Q₀(σ) → β(σ) → \|Γ\|²(σ) and find the acceptable window; **that window probably sets the sample uptake rate and a dissolved-solids ceiling** | 🔴 **open — larger than anything currently on the list, and adjacent to R26's missing amplifier bandwidth spec** |
| 92 | 🔴 **R56 OPENED — the lit cavity may reflect 93%, and it likely constrains sample feed rate** | β goes **2.76 → 0.019** as Q₀ collapses **45,728 → 320** against a fixed Q_ext = 16,568. Sizing for the lit state instead gives β = 143 unlit. **One state is always badly mismatched**, and "no tuner" is a design commitment. 🔑 σ depends on aerosol loading, so **the match window sets an uptake rate and TDS ceiling — an analytical constraint from an RF one**, and Mehlich-3 is the high-TDS case. ⚠️ Settling it needs a σ sweep with a mesh finer than R15's at high σ (δ ∝ 1/√σ). The circulator question is downstream of this and much smaller |

---

## 2026-08-17 — 🔑 The far cavity wall is in the optical path, and that decides the surface material

The viewport looks radially inward past a thin on-axis plasma column, so **the
far wall is the background — necessarily, not conditionally.**

### 🔴 The wall is a concave mirror with the plasma at its centre of curvature

Every point of the cylindrical wall is at r = 103.7 mm with its normal pointing
at the axis. **A specular surface retro-reflects emission straight back through
the plasma.** That is a deliberate double-pass in some instruments; here it
**enhances self-absorption on exactly the strong resonance lines** — Ca 393.4,
Mg 279.6, Na 589, K 766.5 — the major cations a soil panel reports at high
concentration, where linearity and dynamic range matter most.

### 🔴 Three independent arguments against silver, none of them about Q

| | |
|---|---|
| **UV reflectance** | Silver collapses at its ~320 nm plasmon and stays poor below. Aluminium holds ~90% to 200 nm. **P 213.6, Zn 213.9, B 249.7, Mn 257.6, Cu 324.8** are all in silver's bad region — and Cu sits in the dip |
| **Drift** | Ag₂S growth is not self-limiting and darkens progressively, so the background *changes* over months. A constant offset calibrates out; a drifting one does not |
| **Self-absorption** | Specular + centre-of-curvature = retroreflection through the plasma, above |

⚠️ And the RF case for silver is weak: **wall loss is 0.7% of dissipation once
lit**, and unlit, Q shifts ignition and arcing power *together* without changing
the margin between them. **This is an optics decision, not an RF one.**

### ✅ The fix: put the absorber OUTSIDE, behind a small below-cutoff aperture

🔴 **Blackening the far wall from inside is a trap.** Black anodise is 5–25 µm of
lossy alumina against a **1.28 µm skin depth**; optical texturing needs
sub-micron features, also comparable to skin depth. And the far wall at mid-plane
is exactly where TE₀₁₁'s wall current PEAKS, so anything lossy there is expensive.

✅ Instead: a small aperture diametrically opposite the viewport with a light trap
behind it. 🔢 Aperture coupling scales as d³, and the 25 mm viewport costs 0.9% of
Q, so a **10 mm** trap costs **(10/25)³ × 0.9% ≈ 0.06%** — effectively free, and
it converts the worst optical surface in the cavity into a controlled dark
background that cannot drift.

### ⚠️ Azimuthal allocation: the current default makes this impossible

🔢 `view_phi = π` with the loop at φ = 0 puts the trap at **φ = 0 — on the loop**.
At 5 sectors, 0° is also a sector **plane**, which is what split the port face and
killed R47's first run. Two conflicts at once.

> ✅ **Solution — three features at three sector centres:**
>
> | feature | φ |
> |---|---:|
> | loop | **36°** |
> | viewport | **108°** |
> | light trap | **288°** (= 108 + 180) |
>
> All are sector centres at N = 5, none straddles a plane, and viewport/trap are
> exactly opposed as the optics require.

| # | question | status |
|---|---|---|
| **R57** | **Light-trap aperture opposite the viewport** — simulate the Q cost of a ~10 mm below-cutoff hole at mid-plane (estimated 0.06%), and adopt the 36/108/288 azimuthal allocation | open — cheap, uses the viewport tooling |
| **R58** | **Re-decide the cavity surface on OPTICAL grounds.** Silver was chosen for Q; Q is 0.7% of lit dissipation. Bare electropolished aluminium wins on UV, on drift, and on self-absorption. ⚠️ **Do NOT anodise** — 5–25 µm of lossy oxide against a 1.28 µm skin depth | open — reverses a fixed drawing parameter |
| 93 | 🔑 **The far wall is in the optical path, and silver is the wrong surface** | The viewport looks past a thin axial plasma at the far wall, which is a **concave mirror with the plasma at its centre of curvature** — specular = retroreflection through the plasma, **enhancing self-absorption on Ca/Mg/Na/K**. Plus silver is poor in the UV where **P, Zn, B, Mn, Cu** sit, and Ag₂S darkens progressively so the background DRIFTS. ⚠️ RF cost of changing is ~nil (wall loss 0.7% when lit). ✅ Fix: **10 mm below-cutoff aperture + external trap, ~0.06% of Q** by d³ scaling — absorber must be OUTSIDE, since anodise/texture features rival the 1.28 µm skin depth and mid-plane is the wall-current peak. ⚠️ Current `view_phi = π` puts the trap on the loop AND on a sector plane; **use loop 36 / viewport 108 / trap 288** |

---

## 2026-08-17 — 🔑 R54 CLOSED: the geometric mode filter WORKS, and the mechanism is DETUNING

The quartz annulus can be replaced by a circumferential groove at the cap/barrel
corner. Four cases at `--sectors 5`, common size-factor 0.96, plus a wide-band
follow-up to locate the modes that left the window.

| | quartz 3 mm | bare | groove 15 mm | **groove λ/4** |
|---|---:|---:|---:|---:|
| TE₀₁₁ f | 2.41524 | 2.41974 | 2.41876 | 2.42012 |
| TE₀₁₁ Q₀ | 45,913 | 45,421 | **48,656** | **48,155** |
| TE₀₁₁ bin1 (purity) | 0.0046 | 🔴 0.1061 | 0.0088 | ✅ **0.0027** |

✅ **Better than the quartz on every TE₀₁₁ measure.** Q **+6.0%** — which matches
R39's independently measured **5.6%** cost of the quartz, so the groove gives back
exactly what the dielectric was taking. Purity at λ/4 is **0.58× the quartz
case's**, i.e. cleaner than the incumbent. And it barely moves TE₀₁₁'s frequency
(0.4 MHz from bare, against the quartz's 4.5 MHz pull).

### ✅ DETUNING, confirmed by finding the modes rather than assuming

R54 reported TM₁₁₁ and TM₀₂₀ "absent". That was overclaiming — absent from a
160 MHz window is not absent. Re-swept 2.10–2.60 GHz (`--sectors 1`, since
locating a mode needs its bore-energy signature, not azimuthal content):

| | TM₁₁₁ vs TE₀₁₁ | TM₀₂₀ vs TE₀₁₁ | TE₀₁₁ Q₀ |
|---|---:|---:|---:|
| no groove | −15.8 MHz | +26.2 | 48,556 |
| groove 15 mm | **−87 / −100** | −29.1 | 48,509 |
| groove λ/4 | **+136.2** | **+79.5** | 48,581 |

🔑 **They moved. They did not die.** The mechanism is detuning, with some damping
alongside (TM₀₂₀'s Q roughly halves).

✅ **TE₀₁₁ is untouched at every depth: Q spread 0.15%, frequency spread 2.6 MHz
across depths from zero to λ/4.** That is the H_φ argument confirmed — the
groove's slot mode is driven by azimuthal H, TM modes have it, and a TE₀ₙₚ mode
has none at all.

### 🔴 There is a SIGN FLIP, and λ/4 is a pole

At 15 mm the TM modes move **down**; at λ/4 they move **up**. That is a shorted
stub crossing its pole, so **the effective quarter-wave depth is LESS than the
geometric 30.6 mm** — implying a fringing extension of roughly 8 mm where the
slot mouth opens into the cavity. The real pole sits near **20–23 mm** geometric.

> 🔴 **λ/4 is therefore a bad production dimension.** On a pole the response is
> hypersensitive to depth tolerance, temperature and the fringing extension —
> which is inferred here, not measured. Choose a depth well clear of it.

### ⚠️ Open: TM₀₂₀'s placement, which is the binding criterion

R39 established that keeping TM₀₂₀ out of band is the decisive job. With the
groove it depends on depth: at 15 mm TM₀₂₀ lands near **2.411 converged — in
band**; at λ/4 near **2.520 — above the band top**. A depth clearing the band on
the high side may exist, but it sits near the pole. ⚠️ Offsets are extrapolated
from R38's geometry; treat as indicative.

⚠️ These runs use a **45°-tilted loop**, a diagnostic choice that couples to both
mode families. The operational coupler is at 0° tilt and links H_z only, so
TM₀₂₀ would be weakly driven — but "out of band, unreachable" would have to be
restated as "in band, weakly coupled", which is a materially weaker claim.

### 🔴 My verdict block was wrong three ways — the raw table is what stands

| | |
|---|---|
| criterion 1 | one-sided: flagged **+6% Q as a failure**. A gain is a pass |
| criteria 3–4 | read `nan` when TM₁₁₁ was not found, and treated not-found as failure when it was the goal |
| bare reference | `pick()` chose by highest Q among bore-H candidates and grabbed the **hybrid at 2.42236**, not TM₁₁₁ — so the "−2.6 MHz bare separation" is spurious; the real figure is +19.5 |

⚠️ Also noted: `--sectors 1` and `--sectors 5` meshes of the same geometry give
TE₀₁₁ Q differing by **6.9%** (48,556 vs 45,421). Larger than the ~2% mesh
scatter already recorded. **Never compare Q across sector counts.**

| # | question | status |
|---|---|---|
| ~~R54~~ ✅ | **CLOSED — groove works, mechanism is DETUNING, TE₀₁₁ untouched, +6% Q vs quartz** |
| **R59** | **Groove geometry optimization** — depth and width. First job is to **locate the pole** (~20–23 mm geometric) and measure the fringing extension rather than infer it. Differentiator depths **7 / 17 / 23 mm**, chosen for indivisibility against λ/1, λ/2, λ/4, λ/8 — the mirror of R36's 1/2/4 amplification ladder. Binding criterion is **TM₀₂₀ out of band**, not TM₁₁₁ separation | ⏸️ **deferred — optimization, after R50** |
| 94 | 🔑 **R54 CLOSED — the geometric mode filter works and it DETUNES** | Groove beats the quartz on every TE₀₁₁ measure: **Q +6.0%** (matching R39's 5.6% quartz cost exactly), purity **0.58×** the quartz floor, frequency pulled 0.4 MHz vs 4.5. ✅ Mechanism settled by a **2.10–2.60 GHz** re-sweep: TM₁₁₁ and TM₀₂₀ **moved** (−100 MHz at 15 mm, **+136 MHz** at λ/4), they did not die. ✅ **TE₀₁₁ untouched at every depth — 0.15% in Q** — confirming the H_φ argument. 🔴 **Sign flip means λ/4 is a POLE**: effective quarter-wave depth is below the geometric 30.6, implying ~8 mm of fringing, so the real pole is ~20–23 mm and λ/4 is a hypersensitive production dimension. ⚠️ TM₀₂₀ placement is the open binding criterion. 🔴 My verdict block was wrong three ways; the raw table stands |

---

## 2026-08-17 — R60: TM₀₂₀ is 18 dB down at the operational tilt — and TM₁₁₁ goes the WRONG WAY

Every driven run in this project uses a **45° loop tilt**, which `geometry.py`
documents as a diagnostic: 0° links H_z and shows TE₀₁₁, 90° links H_φ and shows
TM₀₂₀, 45° couples to both so one sweep yields both. **The instrument's coupler
is at 0°.** Since every TM mode has H_z = 0 identically, an untilted loop should
be orthogonal to all of them — which would make TM₀₂₀'s frequency a non-issue and
the 2.400 floor a vestige of the surrendered mode-shift scheme.

| loop tilt | TM₀₂₀ / TE₀₁₁ energy | TM₁₁₁ / TE₀₁₁ energy |
|---|---:|---:|
| 45° diagnostic | 52.70% | 9.62% |
| **0° instrument** | **0.77%** | 🔴 **28.63%** |

### ⚠️ Half-right, and I am correcting my own speculation

✅ **TM₀₂₀ is suppressed 18.3 dB** at the operational tilt. The orthogonality
argument holds in direction.

🔴 **But 18.3 dB is not "unreachable", and I said it might be.** A finite loop
with radial legs is not an ideal filament and the residual coupling is real.

> 🔑 **The 2.400 floor is a SECOND LAYER, not a redundant one.** TM₀₂₀ is
> protected twice — 18 dB down, and tens of linewidths from any frequency the
> amplifier can reach. **The aperture budget is therefore NOT simply recoverable**
> (chimney 1.26 MHz, feed 2.70 MHz, bore tolerance ±0.45 → ±0.27 mm), though it
> is less critical than it has been treated.

### 🔴 The anomaly: TM₁₁₁ couples MORE to the untilted loop

TM₁₁₁'s relative amplitude **tripled** going from 45° to 0°. Both it and TM₀₂₀
have H_z = 0, so the same argument predicts both suppressed — one was, by 18 dB;
the other got stronger.

🔢 Correcting for TE₀₁₁'s own coupling (H_z linkage ∝ cos θ, so energy ∝ cos²θ,
i.e. 2× stronger at 0°), TM₁₁₁'s **absolute** excitation rose ~**6×**. ⚠️ That
correction assumes equal drive and cos² scaling; it is an inference, not a
measurement.

> 🔴 **This matters more than the TM₀₂₀ result. EVERY TM₁₁₁ measurement in this
> project was taken at 45°** — R47's identification, R54's assessment of the
> geometric mode filter, R39's brake test. If the operational coupler drives
> TM₁₁₁ harder than the diagnostic one, all of them **understate the hazard the
> mode filter exists to address.**

⚠️ I have no mechanism. Candidates: the loop's radial legs and finite wire radius
couple to m = 1 by something other than H_z flux; or the normalisation misleads.
**Flagged rather than explained away** — it inverts an assumption several
conclusions rest on.

⚠️ Note the shape of this error. The 45° tilt is a **measurement convenience
mistaken for the operating configuration** — the same class as the +31.6 MHz
offset carried across two design points, and the torch-length claim that outlived
an 85 mm cavity.

| # | question | status |
|---|---|---|
| ~~R60~~ ✅ | **CLOSED — TM₀₂₀ 18.3 dB down at 0° tilt; floor is a second layer, budget not recoverable** |
| **R61** | 🔴 **Why does TM₁₁₁ couple MORE to the untilted loop?** And re-take the load-bearing TM₁₁₁ results at 0° tilt: R47's identification, R54's groove assessment, R39's filter test | 🔴 **open — mechanism question about the instrument as built; ahead of R59** |
| 95 | ⚠️ **R60 — TM₀₂₀ 18 dB down at the real tilt, TM₁₁₁ 3× UP** | Orthogonality holds for TM₀₂₀ (**52.7% → 0.77%**) but 18.3 dB is not unreachable, so **the 2.400 floor is a second layer and the aperture budget is NOT recoverable** — correcting my own speculation. 🔴 **TM₁₁₁ went the wrong way**, tripling in relative amplitude (~6× absolute after correcting for TE₀₁₁'s stronger coupling), despite also having H_z = 0. **Every TM₁₁₁ result in this file was measured at the 45° DIAGNOSTIC tilt, not the instrument's 0°**, so they may understate the hazard. R61 opened, ahead of the groove optimization |

---

## 2026-08-17 — ✅ R61: the m=1 identification SURVIVES the operational tilt; the amplitude anomaly does not resolve

R60 found TM₁₁₁'s excitation rising at 0° tilt while TM₀₂₀'s fell 18 dB, which
threatened every TM₁₁₁ result in this file — all measured at the **45° diagnostic
tilt**, not the instrument's 0°. R47 repeated exactly, one variable changed.

### ✅ Q1 — the identification is untouched, and that is the load-bearing half

| | bin2 at 45° | bin2 at 0° | reads |
|---|---:|---:|---|
| filtered TM₁₁₁ | 0.2034 | **0.2034** | m=1 at **57×** floor |
| unfiltered TM₁₁₁ | 0.2244 | **0.2253** | m=1 at **39×** floor |

**Identical to four decimals.** As it should be — a mode's own azimuthal structure
does not care how it is excited. ✅ **R47 stands, and the mode filter's
justification with it.**

✅ The DFT was also given a known-answer check it never had: synthetic uniform →
(0, 0), cos²(φ) → bin2 0.5, cos²(2φ) → bin1 0.5.

### 🔴 Q2 — the anomaly goes BOTH ways, so I have no mechanism

Comparing within matched sector counts, picking TM₁₁₁ by **highest bin2** (the
discriminator that separates it from the hybrid), not highest energy:

| | 45° | 0° | |
|---|---:|---:|---|
| **filtered** TM₁₁₁ / TE₀₁₁ | 0.1039 | 0.2723 | **2.6× enhanced** |
| **unfiltered** TM₁₁₁ / TE₀₁₁ | 0.3392 | 0.0634 | **5.4× suppressed** |

🔴 **Opposite directions.** This kills the electric-dipole explanation I proposed
mid-run — that the port gap is an azimuthal dipole driving TM₁₁₁'s E_φ while
being blind to TM₀₂₀ (which has no E_φ at all, since E_φ ∝ m). That story
predicts enhancement in **both** configurations. **Stated as unresolved rather
than patched a second time.**

### ✅ But the practical news is the opposite of R60's implication

🔢 The hazard case is the **unfiltered** one — modes 18 MHz apart, hybridising —
and there TM₁₁₁ is **5.4× LESS** driven at the operational tilt. The 2.6×
enhancement occurs only in the filtered case, where TM₁₁₁ sits 65 MHz away and
the filter is working.

> ✅ **The 45° measurements were CONSERVATIVE, not optimistic.** R60's warning that
> every TM₁₁₁ result understates the hazard is **withdrawn**.

🔢 TE₀₁₁'s m=2 contamination follows the same pattern: bin1 **0.0347** at 0°
against 0.1061 at 45°, so R47's "23× the floor" is **8.5×** for the real coupler.
Real, but less severe than recorded.

### 🔴 Two errors of mine in this run

| | |
|---|---|
| **cross-sector-count comparison** | The script's Q2 differenced `--sectors 5` runs against reference values taken from `--sectors 1` runs — after I had recorded the **6.9% Q discrepancy across sector counts** specifically as a warning. Both sides of the printed ratio were invalid |
| **picker grabbed the hybrid** | Chose 2.42278 (the m=1/m=2 hybrid) instead of TM₁₁₁ at 2.40256, by taking highest energy among bore-H candidates. **Third occurrence tonight** — same defect as R54's `pick()` and R47's `dq.identify` misfire |

> 🔑 **The fix is a discriminator, not a threshold**: select TM₁₁₁ by **maximum
> bin2**, which is the property that defines it. Add to R50 alongside the
> `dq.identify` te_h change.

| # | question | status |
|---|---|---|
| ~~R61a~~ ✅ | **CLOSED — identification survives at 0°; R47 stands; R60's hazard warning withdrawn** |
| **R61b** | 🔴 **Why does the tilt change TM₁₁₁'s coupling in OPPOSITE directions with and without the filter?** Electric-dipole story falsified | open — mechanism, no design decision blocked on it |
| 96 | ✅ **R61 — identification survives the real tilt; my anomaly explanation is dead** | bin2 **0.2034 → 0.2034** filtered, 0.2244 → 0.2253 unfiltered: **TM₁₁₁ still reads m=1 at 57× / 39× the floor**, so R47 and the mode filter's justification stand. DFT given a known-answer check at last. 🔴 The amplitude anomaly goes **both ways** — 2.6× enhanced filtered, **5.4× suppressed unfiltered** — which **falsifies the azimuthal-electric-dipole story I proposed**, and I am leaving it unresolved rather than patching it. ✅ **R60's warning is WITHDRAWN**: in the hazard case the 45° runs were conservative. TE₀₁₁ m=2 contamination is **8.5×** the floor at the real tilt, not 23×. 🔴 Two errors of mine: a cross-sector-count comparison I had myself warned against, and a **third** wrong-mode pick — fix is to select by max bin2 |

---

## 2026-08-17 — 🔴 ARCHITECTURAL: the cavity may be too large to MATCH a plasma, and two independent lines now say so

Raised by the user against R56's first point. Assessed honestly, including where
the premise needs correcting.

### ⚠️ First, a correction: 207 mm is NOT legacy cruft

The diameter is **forced by physics, not inherited from a withdrawn argument**.
An air-filled TE₀₁₁ at 2.45 GHz requires a = 103.7 mm; that is the "electrical
size" problem `coupling-architecture.md` opens with, and paying it in size is the
explicit price of the AMIP thesis (**no dielectric resonator**). The genuinely
legacy items — TM₀₂₀'s band floor, the quartz filter, silver plating — set the
*tolerance*, the *length* and the *materials*. **None of them set the diameter.**

### 🔴 But the substantive worry is right, by a mechanism the file half-recorded

🔢 **Q_ext = ωU/P_ext.** A 3-litre cavity stores enormous energy for a given
field, so a small loop yields a **huge** Q_ext — measured at **16,568**. Matching
a loaded cavity requires Q_ext ≈ Q₀_lit:

| state | Q₀ | β = Q₀/Q_ext |
|---|---:|---:|
| unlit | 45,728 | 2.76 |
| lit, σ = 0.3 (R56) | 1,389 | 0.084 |
| lit, σ = 30 (R15) | 320 | 0.019 |

> 🔑 **The coupler would need Q_ext ≈ 320, a 52× reduction.** And this file already
> found that route closed: *"Growing the loop to reach Q_ext = 165 is ill-posed —
> a loop that large restructures the cavity. At 1872 mm² the resonance moved
> **134 MHz** and bore-H fell to **0.7%**"* (§12, in the README's do-not-re-attempt
> list). **Two independent lines converge**: R56 measures the match we need, §12
> shows the coupler cannot deliver it.

### 🔢 Why size is the root cause, stated physically

**Small resonators match plasmas easily; large ones cannot.** Q_ext scales with
stored energy, so the same physical coupler gives a far lower Q_ext in a small
cavity — naturally landing in the hundreds, exactly where a loaded plasma sits.

| | bore | mechanism |
|---|---:|---|
| MICAP (Radom) | **25 mm** | dielectric resonator shrinks λ |
| MP-AES (Hammer) | **72 mm** | waveguide, not a free-space-λ cavity |
| Beenakker TM₀₁₀ | ~94 mm | classic MIP cavity, a = 2.405c/2πf = 46.8 mm |
| **AMIP TE₀₁₁** | **207 mm** | air-filled, full free-space λ |

🔢 The filling factor follows: cavity **2,991 cm³** against a plasma zone of
**6.8 cm³ — 0.23% by volume**, and TE₀₁₁ puts only **2.08%** of its magnetic
energy in the bore. The mode barely knows the plasma is there, which is precisely
why Q₀ stays high enough that β never approaches 1.

### ⚠️ What this does and does not imply

✅ **The cavity is a fine resonator and absorbs well once driven** — R22's 99.1%
of dissipated power reaching the plasma stands. The failure is **getting power in
past the mismatch**, not what happens after.

🔴 **It is a COUPLING problem, and the obvious fixes are excluded**: a bigger loop
is ill-posed (§12); a matching network violates *"no tuner, no moving parts"*.
What remains is an aperture/iris feed, a waveguide feed, or a smaller resonator —
and the first two are what the incumbents this project set out to avoid.

⚠️ **TM₀₁₀ at 94 mm is worth naming**: also m = 0, so the axisymmetry thesis
survives at **1/10 the volume** and with E_z maximal on axis where the plasma is.
But its field is axial, driving a capacitive discharge rather than the toroidal
inductive one AMIP argues for — **not a drop-in**, a different machine.

⏸️ R56's remaining four σ points are still solving. This assessment does not
depend on them; they set *where* β=1 falls, not whether the coupler can reach it.

| # | question | status |
|---|---|---|
| **R62** | 🔴 **Can THIS cavity be matched to a lit plasma by ANY coupler that does not restructure the mode?** Aperture/iris, waveguide feed, or over-sized loop with the §12 failure re-examined. **If no, the architecture does not close and cavity size is back on the table** | 🔴 **open — the largest question in the programme; first item of the falsification pass** |
| 97 | 🔴 **The cavity may be unmatchable to a plasma, and it is a size problem** | ⚠️ Correcting the premise: **207 mm is forced by air-filled TE₀₁₁ at 2.45 GHz**, not inherited from TM ignition or the filter. 🔴 But matching needs **Q_ext ≈ 320 against a measured 16,568**, and §12 already recorded that growing the loop even to 165 **restructures the cavity** (134 MHz shift, bore-H 0.7%). Two independent lines converge. 🔢 Root cause is **filling factor: plasma is 0.23% of cavity volume, 2.08% of mode energy**; MICAP 25 mm, MP-AES 72 mm, Beenakker TM₀₁₀ 94 mm, AMIP 207 mm. ✅ Absorption is fine once driven (R22); **the failure is getting power in.** R62 opened as the first falsification item |

---

## 2026-08-17 — ⚠️ CORRECTION to entry 97, and the size question is settled: TE₀₁₁ cannot be shrunk

Entry 97 said 207 mm is "forced by physics". **Too strong.** The radius is forced
only *given* L = 88.53 mm; a and L trade along
a = χ′₀₁/√(k² − (π/L)²).

| L (mm) | a (mm) | diameter | **volume (cm³)** |
|---:|---:|---:|---:|
| 80 | 115.8 | 231.6 | 3,371 |
| **88.53 (current)** | 103.2 | 206.5 | **2,965** |
| **105 — volume minimum** | **91.8** | **183.6** | **2,781** |
| 140 | 83.0 | 165.9 | 3,027 |
| ∞ | **74.6** | **149.2** | ∞ |

✅ **The diameter floor is 149 mm, not 207** — the current 207 comes from choosing
a short cavity.

### 🔴 But it does not help, and that settles R62's size half

🔢 **Volume is bounded below at ~2,781 cm³, and the current design is already
within 6% of it.** Diameter and volume minimise at *different* L: shrinking the
bore to 165 mm makes the cavity **longer and larger**.

> 🔑 **No air-filled TE₀₁₁ geometry at 2.45 GHz is meaningfully smaller than what
> we have.** Matching needs Q_ext down 52×; the available volume reduction is 6%.
> **Within this mode, at this frequency, in air, the coupling problem cannot be
> solved by resizing.** It needs a different mode, dielectric loading, or a
> different feed.

⚠️ For contrast, **TM₀₁₀ has no z-dependence at all**, so its length is free and
set by mechanics rather than resonance: a = 46.8 mm with L = 40 mm gives
**275 cm³ — 10× smaller**. That is why Beenakker cavities are small. It remains a
different machine (axial E, capacitive discharge) and is not proposed here, only
recorded as the scale that a plasma-matchable resonator actually has.

⚠️ **Guard against a misreading**: λ/2 = 61.2 mm is *not* the TE₀₁₁ radius. The
cutoff radius is χ′₀₁λ/2π = **74.6 mm**, and any finite cavity is larger.

| 98 | ⚠️ **CORRECTION to 97 — and TE₀₁₁ cannot be shrunk out of the problem** | a and L trade: the diameter floor is **149 mm**, not 207, so "forced by physics" was too strong. 🔴 But **volume bottoms out at 2,781 cm³ and we are within 6% of it** — diameter and volume minimise at different L, so a narrower bore means a *bigger* cavity. Matching needs **52×** less Q_ext against **6%** of available shrink. **Resizing cannot solve R62.** For scale: TM₀₁₀ has free length and reaches **275 cm³, 10× smaller** — a different machine, recorded as the size a matchable resonator has |

---

## 2026-08-17 — 🔴 R56 CLOSED: the lit cavity absorbs at most 31%, and the root cause is the COUPLER, not size

Five σ points at the operational 0° tilt, each meshed at ≥3 elements per skin
depth (R15's converged criterion), |Γ| read directly off S11 rather than derived.

| σ (S/m) | Q₀ | β | **\|Γ\|² measured** | \|Γ\|² from β | **absorbed** |
|---:|---:|---:|---:|---:|---:|
| 0.3 | 1,389 | 0.084 | **0.695** | 0.714 | **30.5%** |
| 1.0 | 461 | 0.028 | 0.888 | 0.895 | 11.2% |
| 3.0 | 208 | 0.013 | 0.937 | 0.951 | 6.3% |
| 10.0 | 199 | 0.012 | 0.951 | 0.953 | 4.9% |
| 30.0 | — | — | — | — | no usable peak |

✅ **Measured and β-derived \|Γ\|² agree to ≤1.5 points throughout**, so Q_ext is
constant under load and the β model this project's coupling numbers rest on
**survives**. That was the more dangerous alternative.

🔴 **No σ absorbs even 50%.** Best is 31% at σ = 0.3, which is barely a plasma.
Across the physically plausible range (σ ≈ 3–30) the cavity absorbs **5–6%**.

⚠️ σ = 30 returned no usable peak — the resonance is too broad and low-contrast
for the peak-finder at that loading. R15 measured Q₀ = 320 there by a converged
mesh study, consistent with the trend.

### 🔑 CORRECTION to entries 97 and 98: I mis-attributed the root cause to SIZE

🔢 **β = Q₀/Q_ext = P_ext/P_plasma — the stored energy cancels.** β = 0.019 means
the plasma absorbs **52× more than the port delivers at the same field**. That is
not a volume problem and not a filling-factor problem:

> 🔑 **It is a COUPLER-STRENGTH problem.** The loop is a weak coupler; the plasma
> is a strong absorber. **Shrinking the cavity would not fix it** — Q₀ and Q_ext
> both scale with stored energy and their ratio does not move.

⚠️ Size still matters *indirectly*: a larger cavity needs a larger loop for the
same coupling, and §12 recorded that a loop that large restructures the mode
(1872 mm² → 134 MHz shift, bore-H 0.7%). **Size makes the fix harder; it is not
the cause.** Entries 97 and 98 stand on their arithmetic — the 149 mm floor, the
2,781 cm³ volume minimum — but their emphasis is corrected here.

🔢 Dielectric loading does not close it either: full quartz fill gives Q_ext
8,522, sapphire 4,865, against ~320 needed. **ε ≈ 2,700 would be required.**

### 🔑 What R62 actually needs to answer

**A feed that couples ~52× more strongly without perturbing TE₀₁₁** — an iris or
waveguide feed, which is what MP-AES uses and what AMIP set out to avoid.

⏸️ **R54's "delete the quartz" verdict is now PROVISIONAL, not settled.** If the
feed architecture changes, the mode-filter question is re-asked in a different
geometry and the groove-vs-quartz comparison may not transfer. **Do not remove the
quartz annulus from the drawing until R62 resolves.**

| # | question | status |
|---|---|---|
| ~~R56~~ ✅ | **CLOSED — 31% absorbed at best, 5–6% at plausible σ; β model validated; cause is coupler strength** |
| ~~R54~~ ⏸️ | **verdict PROVISIONAL pending R62** — groove beats quartz *in this architecture* |
| **R62** | 🔴 **A feed with ~52× the coupling that does not restructure TE₀₁₁.** Iris, waveguide, or over-coupled aperture. **The programme's central open question** | 🔴 open |
| 99 | 🔴 **R56 CLOSED — the lit cavity absorbs 5–6%, and the coupler is why** | Five σ points, \|Γ\| measured not derived: **30.5% absorbed at σ=0.3, 4.9% at σ=10**, none above 50%. ✅ **Measured vs β-derived \|Γ\|² agree within 1.5 points — the β model survives**, which was the dangerous alternative. 🔑 **Corrects entries 97/98**: β = P_ext/P_plasma, stored energy cancels, so this is **coupler strength, not size or filling factor** — shrinking the cavity would not help, and dielectric loading would need ε ≈ 2,700. ⏸️ **R54's delete-the-quartz verdict is provisional** until the feed architecture is settled |

---

## 2026-08-17 — 📋 PROVENANCE AUDIT: the measurements hold, the justifications do not

Every fixed parameter checked against the finding that set it. Full table in
[`AUDIT.md`](AUDIT.md) — a regenerated working artifact, not part of this
append-only record.

🔑 **The single clearest pattern: almost every ✅ is a MEASURED quantity and
almost every 🔶 is a CHOSEN one.** The measurement layer is in good shape. The
justification layer is where the rot is.

### Three findings

🔴 **The design point's frequency target never existed.** `cav.length_sapphire`
and `cav.length_quartz` were chosen to place TE₀₁₁ at 2.4487 GHz using the
**+31.6 MHz** offset. R38 measured **+24.54**. The lengths are not wrong — entry
79 showed both binding constraints still hold — but they were **selected against
a target 7.06 MHz from where it was believed to be**, so they are unjustified at
their stated precision.

⚠️ **34 of 57 entries are contingent on R62.** If the feed architecture changes,
the design point moves and every geometric parameter re-opens.

🔶 **The tightest number on the drawing rests on a downgraded argument.**
`cav.radius`'s ±0.2 mm tolerance is set by TM₀₂₀ headroom, and R60 measured that
mode 18.3 dB down at the operational tilt. The tolerance may be several times
tighter than it needs to be.

### Nothing is fully orphaned, but the mode filter comes close

`brake.thickness` went on the drawing to keep TM₀₂₀ out of band (R39's stated
decisive job). With the floor downgraded **and** a groove that outperforms it
(R54), its surviving justification is the **TE₀₁₁/TM₁₁₁ separation** from R47 —
a different argument from the one that put it there. **Restate it, do not delete
it.**

### 🔑 What it means for the refactor

> **Build the regression suite from the ✅ set only.** Pinning a contingent value
> makes it look authoritative, which is precisely the failure this audit exists
> to prevent.

⚠️ **`offset.*` must be first-class and re-measurable, never a constant** — it is
geometry-dependent, it was wrong for the life of the project, and it is the most
load-bearing number in the file.

⚠️ **Dead-code check before porting**: mode-shift is surrendered, so `--striker`
and possibly `--electrode` may be unreachable paths.

| 100 | 📋 **PROVENANCE AUDIT — measurements hold, justifications do not** | All 57 baselines checked against their source findings ([`AUDIT.md`](AUDIT.md)). 🔑 **Almost every ✅ is MEASURED, almost every 🔶 is CHOSEN.** 🔴 The design lengths were picked against a TE₀₁₁ target computed with the **wrong +31.6 offset** — not wrong, but unjustified at their precision. ⚠️ **34 of 57 entries contingent on R62.** 🔶 `cav.radius` ±0.2 mm defends a constraint R60 downgraded, so it may be far tighter than needed. `brake.thickness` needs its justification **restated** as TE₀₁₁/TM₁₁₁ separation. Refactor rule: **regression suite from the ✅ set only**, and `offset.*` becomes re-measurable rather than constant |

---

## 2026-08-17 — ✅ R50 phase 1: the harness has a regression net, and the migration is proven

The audit's rule applied to the refactor itself — **do not change code you cannot
regress** — so the net was built before anything moved.

### Two tiers, both passing

| tier | what it covers | cost | status |
|---|---|---|---|
| **1** `regress.py` | analysis layer, replayed from stored `postpro/` CSVs | **seconds** | ✅ **34/34** |
| **2** `regress_tier2.py` | solve path — env, config assembly, port direction, attributes | ~30 min | ✅ **18.27 dB vs 18.3 recorded** |

✅ **The new stack reproduces the old physics.** Tier 2 re-solved R60's tilt pair
through geometry → sidecar → `solveconf` → `solver` and returned the recorded
suppression. TE₀₁₁ came back at **2.41692** on a mesh rebuilt hours later by
changed code — identical to `choff` to five decimals.

### 🔑 The mesh now describes itself

`geometry.py` writes `<mesh>.meta.json` at mesh time, and configs are derived
from it. Three failure classes become structurally impossible rather than merely
avoided:

| | before | now |
|---|---|---|
| port `Direction` | one constant copied between 8 scripts; **R47 died in 7 s** when the loop moved to 36° | derived per mesh — tier 2 shows (0,.707,.707) and (0,1,0) from the two meshes |
| materials on absent attributes | `--brake 0` left a material bound to attribute 8 | dropped, **with the reason printed** |
| achieved vs requested size-factor | only the mesher knew | recorded in the sidecar; `solver.sweep` **refuses a mixed set** |

### 🔑 What the net caught on its first run

`plasma.q_loaded` failed: a loaded resonance carries **0.43% bore-H** against an
unloaded TE₀₁₁'s 2.08%, so the unloaded discriminator correctly refused it. Added
`modes.loaded()`, which returns **no mode label** — loaded, identity comes from
the run's configuration, not from a signature the plasma has redistributed.

### Scope decisions, deliberately narrow

⚠️ **Only the 9 pinned meshes were rebuilt**, not all 154 (~2.9 GB). The rest are
one-offs from closed questions, never re-solved, and their *results* are read
directly from `postpro/` by tier 1.

⚠️ **Closed drivers were NOT edited.** They are the evidence trail. The migration
is proven by re-expressing one case on the new stack and checking the physics
survives — a stronger test than rewriting fifteen files nobody will run again.

⚠️ **Only ✅-VALID baselines are pinned.** AUDIT.md's 34 R62-contingent entries
are excluded and listed: a passing test on a contingent value would endorse a
choice that is still open.

### Remaining in R50

mesh no-op postconditions (sidecar element counts make this mechanical) ·
`offset.*` promoted to re-measurable · dead-code check on `--striker` /
`--electrode` · **renames last** (brake → mode filter, sectors → azimuthal_bins),
since they touch the most and verify the least.

| 101 | ✅ **R50 phase 1 — regression net live, migration proven** | Tier 1 **34/34** in seconds over stored CSVs; tier 2 re-solves through the new stack and returns **18.27 dB vs 18.3 recorded**. 🔑 **The mesh now describes itself** via a sidecar, so port `Direction`, attribute binding and achieved size-factor are DERIVED — the R47 crash class is structurally impossible now. 🔑 Net caught a real gap on first run: unloaded discriminators refuse a loaded resonance (0.43% vs 2.08% bore-H), so `modes.loaded()` returns **no label**. Scope kept narrow on purpose: 9 pinned meshes not 154, closed drivers untouched as evidence, only ✅-VALID baselines pinned |

---

## 2026-08-17 — ✅ R50 phase 2 COMPLETE: postconditions, geometry-bound offsets, renames

### Mesh postconditions — the two silent no-ops can no longer pass

`meshcheck.py`, enforced by `solver.sweep` **before any solve**, so a bad sweep
fails in milliseconds rather than after four hours.

🔑 **The distinction that makes it useful rather than noisy:** a **sizing**
parameter (`plasma_h`) exists to change the element count, so if it differs and
the count does not, it did not take effect. A **shape** parameter need not —
ovality moved the mesh 0.4% and was applied perfectly. A blanket "meshes must
differ" rule would have cried wolf on every geometry sweep tonight.

Pinned against **replays of the real failures**, not invented ones:

| replay | |
|---|---|
| R15's clamped pair (1.0 and 0.6 mm → same 1.2 mm mesh) | ✅ caught, by two independent routes |
| R15's fixed sweep (1.2/0.8/0.6) | ✅ passes |
| ovality, 0.4% element change | ✅ no false positive |

`geometry.py` now records the *effective* `MeshSizeMin` in the sidecar, so a
clamp is visible rather than inferred.

### 🔑 `offset.*` is measured and BOUND TO ITS GEOMETRY

The audit called it the most load-bearing number in the file, and it was **wrong
by 7.06 MHz for the life of the project**. The failure was not arithmetic: an
offset measured at a = 101.43 / L = 87.67 was carried across two design points
and applied as a constant. It is a discretisation error — geometry-, mesh- AND
mode-dependent.

`offsets.py` stores each offset beside its mesh with a **fingerprint** of the
geometry it was measured on:

| | |
|---|---|
| derives +24.54 / +20.06 from the stored R38 runs | ✅ |
| applying it reproduces `te011.f_converged` 2.44146 | ✅ |
| **a foreign-geometry offset is REFUSED** | ✅ the +31.6 failure mode |
| an unmeasured geometry raises rather than borrowing | ✅ |
| refuses to substitute one mode's offset for another | ✅ (they differ 4.5 MHz; using one for both corrupts the SEPARATION) |

### Renames, with aliases

`--mode-filter` and `--azimuthal-bins` are the names; `--brake` and `--sectors`
remain as deprecated aliases so the ~18 closed drivers that are **the evidence
trail** stay runnable. Verified: both spellings build byte-identical meshes
(103,293 tets), and the old spelling prints a note naming its replacement.

⚠️ **Internal identifiers are deliberately NOT renamed** — `TAG_BRAKE`, the
`"brake"` physical-group name, the sidecar key. Changing them would invalidate
all 154 existing meshes and the 9 sidecars just built, for a cosmetic gain. They
move when meshes are next rebuilt wholesale.

🔑 `--sectors` was renamed because it misled **the project's own author** into
reading sectors=4 as a 4-port feed. Bins are a MEASUREMENT construct: fictitious
internal partitions that exist so Palace reports energy per wedge. They are not
boundaries — tagging their planes PEC would make N wedge resonators out of one
cavity.

| 102 | ✅ **R50 phase 2 — postconditions, bound offsets, renames** | `meshcheck` enforced in `solver.sweep` before any solve, pinned against **replays of both real no-ops**, with a sizing-vs-shape distinction so it does not cry wolf on geometry sweeps. 🔑 **`offsets.py` binds each offset to a geometry FINGERPRINT and refuses a foreign one** — the +31.6 failure is now structurally impossible, not merely corrected. Renames landed as `--mode-filter`/`--azimuthal-bins` with the old flags aliased so the evidence-trail drivers still run; internal tags deliberately untouched to avoid invalidating 154 meshes. **Net at 42 checks.** |

---

## 2026-08-17 — 🔑 R62: R56 measured the BARE loop. The design's coupler has a series capacitor.

R56 concluded the lit cavity absorbs 5–6% and the feed is **52× too weak**, and
entry 99 called that a coupler-strength problem. Chasing the fix led straight
back into this file's own coupler section, which already contains the answer.

| | |
|---|---:|
| bare loop, measured | Q_ext **14,442** (204 mm²) |
| loop inductance | 21.5 nH → **332 Ω** at 2.45 GHz |
| series C to cancel it | **0.196 pF** |
| current ×6.6, coupled power **×45** | Ohm's law |
| **Q_ext after cancellation** | **~320** |
| **Q_ext R56 says matching needs** | **~320** |

🔑 **Those are the same number.** The "52× deficit" is the deficit of an
**untuned** loop. R56 used Q_ext = 16,568, derived from the design table's
β = 2.76 — and that β describes the **bare** loop, not the coupler the design
specifies (README: "small non-perturbing loop **+ series C**").

> ⚠️ **The file carries two inconsistent coupler descriptions and I used the
> stale one.** β = 2.76 / Q_ext = 16,568 (bare) sits in the design table;
> Q_ext ≈ 320 (with series C) sits in the coupler section. They cannot both
> describe the same part.

### 🔴 But the series C has NEVER been correctly simulated

**Palace's lumped-port R and C are in PARALLEL.** Setting `C` on the port does
not create a series element. A true series capacitor is **a second gap in the
loop, without a port** — a geometric capacitor, which `geometry.py` cannot build.

`driven-capC.json` (C = 1.96e-13) was run 08-14 and returns **Q₀ = 986,444** with
|S11| = −0.33 dB — not a physical cavity Q, consistent with the port not being
the intended element. The record's own follow-up actions — *"add series C at the
port and confirm Q_ext drops as predicted"* — were closed with *"simulation would
confirm arithmetic we are already confident in"*, and never done.

### What this does and does not change

✅ **R56's measurements stand** — |Γ|² read from S11, five σ points, β model
validated. What changes is the **denominator**: they describe a cavity fed by an
untuned loop.

⏸️ **Entry 99's conclusion is SUSPENDED, not withdrawn.** The architecture may
close after all. It cannot be confirmed until the series C is in a model.

⚠️ **The unresolved 2× convention ambiguity** between the analytic Q_ext formula
and Palace's port definition is flagged in the coupler section and still open. It
sits directly between "matched" and "6 dB off".

| # | question | status |
|---|---|---|
| **R62** | **Build the series capacitor as a SECOND GAP in the loop** (geometry.py cannot yet), measure Q_ext, and re-run R56's σ sweep against it. Confirms or kills the architecture | 🔴 **open — now well-posed and simulable** |
| ~~R62-size~~ ✅ | closed by entry 98: resizing cannot fix coupling; and entry 99's coupler-strength framing is what led here |
| 103 | 🔑 **R62 — R56 measured the bare loop; the design's coupler has a series C** | The coupler section already records: bare Q_ext **14,442**, loop reactance **332 Ω**, **0.196 pF** cancels it, power **×45**, **Q_ext ≈ 320** — which is exactly what R56 says matching needs. **The 52× deficit is an UNTUNED loop's deficit.** ⚠️ The file carries two coupler descriptions (β=2.76 bare in the design table, Q_ext≈320 tuned in the coupler section) and R56 used the stale one. 🔴 **The series C has never been correctly simulated** — Palace's port R and C are PARALLEL, so a true series element needs a second gap in the loop, which geometry.py cannot build. ⏸️ **Entry 99 suspended, not withdrawn** |

---

## 2026-08-17 — 🔴 R62 first attempt: the series capacitor was INVISIBLE to the solver

`geometry.py` gained `--loop-gap2`, a second gap in a radial leg — a real series
capacitor, in series with the loop, with the port gap left alone in the crossbar.
Q_ext from the LINEWIDTH (1/Q_L = 1/Q₀ + 1/Q_ext), since |Γ| alone cannot
separate over- from under-coupling and §12 already recorded Re(Z) as
ill-conditioned when |Γ| → 1.

| gap (mm) | Q₀ | Q_L | **Q_ext** |
|---:|---:|---:|---:|
| 0.00 (none) | 45,723 | 9,299 | **11,674** |
| 0.60 | 45,799 | 9,300 | **11,669** |
| 0.30 | 45,794 | 9,300 | **11,670** |
| 0.15 | 45,794 | 9,300 | **11,670** |

🔴 **Identical to four significant figures, including against no gap at all.**

✅ **The run predicted this failure in advance and said what it would mean**, so
it is a diagnosis rather than a surprise: the gap is 0.15–0.6 mm against a
~1.2 mm `MeshSizeMin`. Two test builds at 0.15 and 0.30 mm returned **identical
element counts with different checksums** — the geometry differed, the
discretisation did not, and a void smaller than its surrounding elements
contributes nothing the field equations can see.

> 🔑 **A sub-mesh-scale feature is not "present but small". It is absent.** Same
> lesson as R15's plasma refinement, in a different guise: geometry that is not
> resolved is geometry that is not there.

### Fixed by local refinement, and the first attempt at that was too generous

A Ball field at the gap with elements at gap/3, plus lowering the `MeshSizeMin`
floor that would otherwise clamp it (R15's fix, reused).

| ball radius | tets | |
|---|---:|---|
| 4 × wire radius | **1,358,279** | 13× baseline — hours per solve at order 2 |
| **1.5 × wire radius** | **143,097** | +39% over baseline, ~20 min |

The capacitance lives within roughly one wire radius of the gap, so the tight
ball is not a compromise — the wide one was simply wasteful.

⚠️ **A lumped-element alternative exists and may be better**: a second
non-excited `LumpedPort` carrying C, on an embedded face in the gap, reusing the
port-face machinery. That models a lumped element AS a lumped element instead of
resolving a 0.15 mm void volumetrically. Worth comparing against the geometric
result rather than assuming either.

| 104 | 🔴 **R62 attempt 1 — the series capacitor was below the mesh floor and invisible** | Q_ext came back **11,670 ± 5 across gaps of 0, 0.15, 0.30 and 0.60 mm** — no response whatsoever. Two builds at different gaps had **identical element counts, different checksums**: geometry differed, discretisation did not. ✅ The run **pre-registered this failure mode** and named the remedy, so it diagnoses rather than surprises. 🔑 **Sub-mesh-scale geometry is absent, not small** — R15's lesson in new clothing. Fixed with a Ball refinement at gap/3 plus a lowered floor; first ball was 4× wire radius and cost **1.36M tets**, tightened to 1.5× for **143k**. ⚠️ A second non-excited LumpedPort carrying C may model this better than resolving the void |

---

## 2026-08-17 — ⚠️ CORRECTION to entry 104, and a method lesson worth more than the result

### 🔴 First, correcting entry 104: attempt 2's null was MY BUG, not resolution

Entry 104 diagnosed attempt 1 correctly — the gap was below the mesh floor — and
the Ball refinement fixed that: meshes went **103k → 114k → 143k → 358k** as the
gap narrowed, so the feature was genuinely resolved. Attempt 2 then returned the
**same flat Q_ext**, and I read it as "still unresolved" and re-ran the same
diagnosis.

🔢 It was a sign error. The leg runs from `xo = 105.7` **inward** to
`xi = 91.7`, so x DECREASES along it, and my two segments were laid out as if it
increased. Result: the pieces **overlapped by 14 mm** instead of separating by
0.15. **The conductor was never broken.**

> ✅ **The check that caught it was structural and cost seconds**: PEC surface
> count, **23 before and 23 after**. Breaking a conductor must create new faces.
> With the direction fixed: **26**.
>
> 🔑 **This belongs in `meshcheck`** — if a flag is meant to break a conductor,
> the exterior-surface count must change. Same family as the two mesh no-op
> guards, and it would have caught this in seconds instead of after two sweeps.

⚠️ **My error of reasoning**: the element counts told me the refinement HAD
worked. I should have asked why a resolved feature still did nothing, instead of
repeating the previous diagnosis.

### ✅ The small test — 52 seconds to settle what four hours had not

The whole geometric route rests on one recorded claim: **Palace's lumped-port R
and C are in PARALLEL**, so port C cannot stand in for a series capacitor. That
claim had never been tested.

🔑 **It needed no new geometry and no resonance** — only an existing mesh, a
one-point band, and two hypotheses whose predictions differ by an order of
magnitude:

| | Z at 0.196 pF, 2.45 GHz | predicted \|Γ\| |
|---|---|---:|
| parallel | 48.9 − 7.3j | 0.074 |
| series | 50 − 336j | **0.958** |
| **measured change in \|Γ\|** | | **0.029** |

✅ **PARALLEL confirmed.** The record is right, the geometric gap is required,
and the two spent sweeps were on the correct route — defeated by resolution and
then by my sign error, not by a wrong premise.

> 🔑 **THE METHOD LESSON, which outlives this result: build the smallest test
> that DISCRIMINATES.** Four hours of full-cavity sweeps rested on an untested
> assumption that a 52-second run settled. The test needed no resonance, no new
> mesh and no convergence — only two hypotheses far enough apart that the
> structure's own contribution could not flip the verdict.

| 105 | ⚠️ **CORRECTION to 104 — attempt 2's null was a SIGN ERROR, and a 52 s test settled the premise** | 🔴 The leg runs with x DECREASING; my segments assumed increasing, so the pieces **overlapped by 14 mm** and the conductor was never broken. **PEC surface count 23 → 23** was the tell; fixed it is **26**. ⚠️ I misread a resolved-but-broken case as still-unresolved and repeated the diagnosis. 🔑 **`meshcheck` should assert that a conductor-breaking flag changes the surface count.** ✅ Separately, the load-bearing claim that Palace's port C is PARALLEL was tested directly for the first time — one mesh, one frequency, **52 s**: predicted \|Γ\| 0.074 parallel vs 0.958 series, **measured change 0.029 → PARALLEL**. 🔑 **Build the smallest test that discriminates** — four hours of sweeps rested on an assumption a minute could check |

---

## 2026-08-17 — 🔴 R62 ANSWERED: the series capacitor does NOT work, and the coupler's 45× rests on a model that does not apply

The design specifies "loop + series C", and the coupler section computes that
0.196 pF cancels the loop's 332 Ω self-reactance, raising coupled power **45×**
and taking Q_ext from 14,442 to **~320** — exactly what R56 measured as the
requirement for matching a lit plasma. That arithmetic was accepted in August
without simulation: *"simulation would confirm arithmetic we are already
confident in"*.

**It does not.**

| flange r (mm) | Q_ext | \|Γ\| | absorbed |
|---:|---:|---:|---:|
| **none (bare loop)** | **9,785** | **0.567** | **67.9%** |
| 1.0 | 1,312 | 0.939 | 11.9% |
| 1.5 | 1,675 | 0.923 | 14.8% |
| **1.9 — predicted cancellation** | 2,024 | 0.909 | 17.3% |
| 2.5 | 3,474 | 0.851 | 27.7% |

🔴 **No minimum. Monotonic. And every flanged case is WORSE than the bare loop**,
recovering toward it as capacitance rises — the signature of a series capacitor
with **no inductive reactance to cancel**. As C → ∞, Z_c → 0 and |Γ| → the bare
0.567. The trend goes exactly that way.

> 🔑 **The loop is not a lumped inductor.** Its perimeter is ~58 mm against
> λ = 122 mm — about **λ/2** — so it is a distributed structure near its own
> self-resonance, attached to the wall at both ends. The 21.5 nH → 332 Ω came
> from a lumped formula that does not describe it. **The 45× was wrong at its
> foundation, not in its arithmetic.**

### ✅ How this was established, in four cheap steps rather than one expensive one

| | cost | result |
|---|---|---|
| is Palace's port C series or parallel? | **52 s** | PARALLEL — geometric gap required |
| does a bare gap couple at all? | 2 solves | yes: \|Γ\| 0.568 → 0.904, but the WRONG way |
| is C too small? area, not gap width | analysis | 0.196 pF at 0.5 mm needs r ≈ 1.9 mm |
| **does it cancel?** | 5 solves | 🔴 **monotonic — no** |

⚠️ Two failed attempts preceded these, both self-inflicted: a gap below the mesh
floor, then a **sign error** that made the two leg pieces overlap by 14 mm
instead of separating. Both are now caught by postconditions (`plasma_clamped`,
and PEC surface count for conductor-breaking flags).

### 🔑 Consequences

🔴 **Entry 99 is UN-SUSPENDED.** R56 stands as measured: the lit cavity absorbs
5–6%, and the coupling deficit is real. The design's own coupler cannot close it.

🔴 **`te011.q_ext` needs restating.** Three values now exist — 16,568 (from
β = 2.76), 11,674 and 9,785 (measured directly here). All ~10⁴; none near the
~320 required. The ~320 figure was analytic and is now falsified.

✅ **The bare loop absorbs 68% unlit** — better than β = 2.76 implies. The loop is
fine as an unlit coupler. It is the LIT state it cannot follow.

| # | question | status |
|---|---|---|
| ~~R62-seriesC~~ 🔴 | **ANSWERED: the series capacitor does not cancel. Lumped model falsified** |
| **R63** | **A feed that couples ~30× more strongly than the bare loop without restructuring TE₀₁₁.** Loop route now doubly closed — bigger loop restructures the mode (§12), series C does not work (R62). What remains is an **iris or waveguide feed**, i.e. what MP-AES uses and AMIP set out to avoid | 🔴 **open — the programme's central question** |
| 106 | 🔴 **R62 ANSWERED — the series C does not work; the coupler's 45× is founded on a model that does not apply** | Flange sweep at a 0.5 mm gap: **monotonic, no minimum**, and every flanged case worse than the bare loop (Q_ext 9,785 → 1,312–3,474). The signature of a capacitor with **nothing inductive to cancel**. 🔑 **The loop is ~λ/2 in perimeter** — distributed, not lumped — so the 21.5 nH → 332 Ω → 45× chain fails at its first step. ✅ Established in four cheap steps after two self-inflicted failures now caught by postconditions. 🔴 **Entry 99 un-suspended: R56 stands, the deficit is real.** ✅ The bare loop absorbs **68% unlit** — it is the LIT state it cannot follow. **R63 opened: iris or waveguide feed** |

---

## 2026-08-17 — ✅ THE 2× AMBIGUITY IS CLOSED: it is a Palace output convention, and dq.py was already right

Open since August, flagged in the coupler section as sitting *"between the
analytic Q_ext formula and Palace's port definition"*, and never resolved. It
gates everything: it is the difference between "matched" and "6 dB off".

Closed by asking Palace for the **wall power directly** —
`Boundaries.Postprocessing.SurfaceFlux` with `Type: Power` on the PEC attribute —
and checking whether energy balances. One 23-second solve on an existing mesh.

| at resonance 2.41692 | W |
|---|---:|
| **P_wall (surface flux)** | **0.9095** |
| **P_abs (from S-parameters)** | **0.4764** |
| ratio | **1.909** |

🔴 A cavity fed 0.5 W cannot dissipate 0.909 W. **Energy did not balance**, by
almost exactly 2.

### ✅ And the answer was already written in `dq.py`

Its docstring records that *"Palace reports E_elec = (1/2)∫ε|E|², which is TWICE
the time-averaged electric energy… Q comes out exactly 2× too high"* — caught
years-of-work ago by the ring, whose Q was known three independent ways. **The
surface flux uses the same convention.** Correcting it:

| | W |
|---|---:|
| P_wall / 2 | 0.4547 |
| P_abs from S-parameters | 0.4764 |
| **residual** | **0.0217 = 4.6%** |

✅ **The residual is dielectric loss**, and it is the right size: the mode filter
alone costs 5.6% of Q (R39), plus the torch. **The balance closes.**

> 🔑 **VERDICT: Palace's energy and flux outputs are 2× time-averaged, applied
> CONSISTENTLY. `dq.py`'s existing /2 correction is correct, and every Q₀ in this
> project stands.** The S-parameter route gives true time-averaged power. There
> was never a discrepancy between two methods — there was one convention, and
> only half of it had been discovered.

⚠️ **Consequence for anything reading Palace surface flux in future: divide by
2**, exactly as `dq.py` does for stored energy. This is now the second place the
convention has bitten; it should be handled in one helper, not per-script.

### What this does for R63

✅ The Q chain is validated: the loss model, the extraction and the port
convention are mutually consistent to 4.6%, with the residual physically
accounted for. **A Q_ext measured on an iris feed can be believed** — which is
what the R63 validation ladder was for, and it was test 3 that settled it.

⚠️ Still unvalidated: the **waveguide port** itself (test 2) and the **aperture
scaling exponent** (test 4). Neither is needed to trust existing results; both
are needed before trusting a new feed geometry.

| 107 | ✅ **The 2× ambiguity is CLOSED — a Palace output convention, consistently applied** | Asked Palace for wall power directly (`SurfaceFlux`, `Type: Power`): **P_wall 0.9095 W against P_abs 0.4764 W, ratio 1.909** — energy apparently violated on a cavity fed 0.5 W. 🔑 **Palace's flux is 2× time-averaged, the same convention `dq.py` already corrects for stored energy.** Halved, the balance closes to **4.6%**, and that residual is dielectric loss of exactly the right size (mode filter 5.6% of Q). ✅ **Every Q₀ in this project stands**; there was one convention, half-discovered. ⚠️ Divide Palace surface flux by 2 — second time this has bitten, belongs in one helper. ✅ **A Q_ext on an iris feed can now be believed** (R63 test 3 of 4) |

---

## 2026-08-18 — ✅ R63 validation ladder: 2 of 4 passed, test 4 BLOCKED on solver convergence

Before building an iris feed whose entire output would be a Q_ext with no
independent check, four validations were planned. Two passed; one is blocked and
the block is itself informative.

| | test | result |
|---|---|---|
| **3** | energy balance / the 2× convention | ✅ **closed** — entry 107 |
| **2** | WavePort vs WR-340 dispersion | ✅ **0.0° phase error at 3 frequencies** |
| **4** | iris scaling exponent d⁻⁶ | 🔴 **blocked — see below** |
| **1** | analytic cavity Q | ⏸️ rides on test 4's rig |

### ✅ Test 2 — the port type R63 depends on is sound

Straight WR-340 section, 4,498 tets, **18 s**:

| f (GHz) | \|S11\| dB | \|S21\| dB | arg S21 | −βL theory | error |
|---:|---:|---:|---:|---:|---:|
| 2.20 | −112.5 | −0.000 | 165.2° | 165.2° | **0.0°** |
| 2.45 | −107.2 | −0.000 | 110.8° | 110.8° | **0.0°** |
| 2.70 | −103.2 | −0.000 | 62.0° | 62.0° | **0.0°** |

🔑 The phase advance FALLS from 165° to 62° as frequency rises — the dispersion
curve, not a straight line. A port launching a free-space plane wave would give
the latter. **Palace's WavePort launches the correct TE₁₀ mode.**

### 🔴 Test 4 — the rig is right, the solver will not converge

Rig: empty TE₀₁₁ cavity at design dimensions, fed through a circular iris in the
barrel at mid-plane from a WR-340 section ending in a WavePort. Builds cleanly at
34,605 tets.

⚠️ **Two self-inflicted problems first**, both now fixed and documented:
1. Running the whole driver under `micromamba run` breaks once Python spawns
   Palace → mpirun: gmsh dies with *"Interrupted system call"* AFTER writing the
   mesh, so the symptom appears far from the cause. Every working driver here
   uses plain `python3` and shells out to micromamba only for meshing.
2. A 60 MHz band across an **empty** cavity's 49 kHz linewidth — **1,227
   linewidths** — which the adaptive ROM cannot resolve. Narrowed to 6 MHz
   centred on the analytic 2.44438 GHz.

🔴 **It still does not converge.** 37,041 ND unknowns, four ranks at **99.9% CPU
for 50 minutes**, log frozen after "Operator assembly level: Partial". Computing,
not deadlocked, and not finishing.

> 🔑 **Leading hypothesis: WavePort + a very high-Q resonance.** `rig_wg.py`
> proved WavePort works on a NON-RESONANT structure in 18 s. Every previous
> cavity solve here used a **LumpedPort**. An empty cavity is Q ≈ 50,000 and
> driven at resonance the operator is nearly singular — the combination is what
> is new.
>
> ⚠️ **The empty cavity was chosen to be "clean" for validation. Clean means high
> Q, and high Q is what broke it.** The analytic anchor and the tractability
> pulled in opposite directions and I did not anticipate that.

### What this means for R63

✅ Nothing measured so far is in doubt: tests 2 and 3 passed, and test 3 was the
only one that could have invalidated existing results retroactively.

🔴 **An iris feed cannot yet be evaluated.** Options, cheapest first: add
realistic loss (torch + mode filter) so Q drops to ~45,000 and the operator
conditions better — at the cost of the analytic anchor; relax `Linear.Tol` from
1e-8; try a different `SolverType` for the wave-port boundary mode; or drive
off-resonance and infer Q_ext from the linewidth rather than the peak.

| # | question | status |
|---|---|---|
| **R64** | **Make WavePort converge on a high-Q cavity.** Blocks R63 entirely — an iris feed cannot be evaluated until a wave-port-fed resonator solves | 🔴 open |
| 108 | ✅ **R63 ladder: WavePort validated exactly, iris rig blocked on convergence** | Test 2: WR-340 phase matches **−βL to 0.0°** at three frequencies with dispersion curvature — the port launches the right mode. Test 4: rig builds at 34,605 tets but **4 ranks × 99.9% CPU × 50 min** without converging, 37k unknowns. 🔑 Hypothesis: **WavePort + Q ≈ 50,000 resonance**; WavePort is proven on a non-resonant guide, and every prior cavity solve used a LumpedPort. ⚠️ **The empty cavity was chosen for a clean analytic anchor, and that is exactly what made it intractable.** Two self-inflicted issues fixed en route: micromamba-wrapped driver breaking signal handling, and a 1,227-linewidth band. **R64 opened; it blocks R63** |

---

## 2026-08-18 — ✅ The wide-band ROM results hold, but |S11| null depth does not

Challenged directly: given how much broke tonight, are the existing results in
doubt at all? Nearly every sweep here ran a **140–220 MHz band across a ~54 kHz
linewidth** — 2,600–4,000 linewidths, the same regime that just defeated the
wave-port rig. Tested rather than argued, on `choff.msh`, two narrow bands
against the original:

| band | f | Q₀ | \|S11\| |
|---|---:|---:|---:|
| **±70 MHz (original)** | 2.41692 | **45,728** | −13.27 dB |
| ±1 MHz | 2.41692 | 45,863 | −13.27 dB |
| ±0.2 MHz | 2.41693 | 45,782 | **−14.81 dB** |

✅ **Frequency reproduces to 10 kHz and Q₀ to 0.3% across a 350× change in band
width.** The wide-band ROM did resolve the resonance. Existing f and Q stand, and
the ~2% Q scatter is meshing, not sampling.

🔴 **But \|S11\| at the bottom of a sharp null moves 1.5 dB — a 16% shift in
\|Γ\|.** The depth of a deep null is the hardest thing for a ROM to resolve, and
it is the one quantity a matching analysis rests on.

> 🔑 **Read Q and f from any band; read \|Γ\| only from a narrow one.** R56's
> match figures are less exposed than they look — its resonances were broad
> (Q ≈ 200–1400), which is the easy case — but the rule stands.

### 🔑 Every solve now carries a CEILING, not just a floor

Two runs burned hours without being noticed: **3h51m** on a band 1,227 linewidths
wide, and **50 min at 99.9% CPU on 37k unknowns** that never converged. The
harness already refused solves returning too FAST (under 30 s = did not run).
It had nothing for the opposite.

`solver.solve` now takes `timeout_s`, defaulting to 3600, and on expiry says what
the failure actually is: *"Not a slow solve — a non-converging one. A frozen log
with ranks at 100% CPU means the linear solve is not converging, not that it
needs longer."*

⚠️ **Working rule, from the user: bound at ~3× what you expect.** Seconds → a
2-minute ceiling; 20 minutes → an hour. A hang then self-terminates instead of
being discovered hours later by someone asking why it is taking so long.

| 109 | ✅ **Wide-band ROM validated; \|S11\| null depth is the exception; solves now have a ceiling** | Challenged on whether existing results survive the night's failures. Tested: **f to 10 kHz and Q₀ to 0.3% across a 350× band-width change** — the ROM did resolve it, existing values stand, 2% scatter is meshing. 🔴 **\|S11\| null depth moves 1.5 dB (16% in \|Γ\|)** — read \|Γ\| from a narrow band only. 🔑 `solver.solve` gained `timeout_s` (default 3600) after runs of **3h51m** and **50 min at 99.9% CPU** went unnoticed; the harness could detect solves that were too fast but not ones that never finished. Bound at ~3× expectation |

---

## 2026-08-18 — 🔑 Q_ext from linewidth was BIASED; β = 2.76 is wrong; the coupling model works

Challenged on whether anything measured survives the night's failures — "something
is going wrong that isn't detectable, like a divide by zero that doesn't throw".
It was a fair challenge and it found something.

### 🔴 The undetectable error: coarse sampling biases Q_L in ONE direction

Q_L is taken from the half-power width of the stored-energy peak. The linewidth
here is ~130 kHz; the wide-band sweeps stepped at **20 kHz**. Taking "the first
sample below half maximum" **overshoots** the true half-power point, which widens
the measured Δf and lowers Q_L — systematically, silently, with a perfectly
plausible result.

🔢 Same mesh, same port, only the frequency step differs:

| band | Q_ext at R = 50 Ω |
|---|---:|
| ±70 MHz, 20 kHz step | **9,785 – 16,568** |
| ±1.5 MHz, 2 kHz step | **31,304** |

⚠️ **Every linewidth-derived Q_ext in this project came from a wide band**,
including R62's 11,670 — the number used to declare the series capacitor a
failure — and the 9,785 fed into R63's premise.

✅ **f and Q₀ are NOT affected**: across a 350× band-width change they reproduce
to 10 kHz and 0.3%. Q₀ comes from an energy integral, not a width. **The ~2%
Q₀ scatter really is meshing.**

### ✅ POSITIVE CONTROL: the coupling model is not broken

Sweeping the lumped-port impedance on `choff.msh`, narrow band throughout:

| R (Ω) | Q_ext | β | \|S11\| | absorbed |
|---:|---:|---:|---:|---:|
| 5 | 199,979 | 0.22 | −3.85 | 58.8% |
| **50** | **31,304** | **1.46** | **−14.81** | **96.7%** |
| 500 | 95,745 | 0.48 | −8.09 | 84.5% |
| 2,000 | 329,041 | 0.14 | −1.94 | 36.0% |
| 8,000 | 716,389 | 0.06 | −0.48 | 10.5% |

🔑 **A clean minimum at R ≈ 50, β crossing 1 on both sides. Matching IS reachable
and the model produces it.** Two independent observables agree: β = 1.46 predicts
−14.6 dB, measured −14.81. β = 2.76 would predict −6.6 dB.

> 🔴 **The recorded β = 2.76 / Q_ext = 16,568 is WRONG.** True unlit values at
> R = 50 are **β = 1.46, Q_ext = 31,304**. `baselines.json` needs restating.

### 🔴 And R56's conclusion SURVIVES, on a better footing

🔢 The **minimum** Q_ext, optimised over three decades of port impedance, is
**31,304**. The lit cavity needs Q_ext in the **hundreds** (320 for β=1;
55–1,880 for ≥50% absorbed). Port impedance cannot touch it — Q_ext is a property
of the coupling structure, not the termination.

**Deficit ≈ 98×**, and it now rests on a validated instrument with a positive
control rather than on a single walked value. R56 measured 5–6% absorbed
directly; this route independently gives 4.0%.

### 🔴 THE OPEN CONTRADICTION — this is the real gap

| | Q_ext vs loop area |
|---|---|
| geometry (Q_ext ∝ V/ωA²) | slope **−2** |
| §12 measurement (204→1120 mm²) | slope **−0.07**, essentially FLAT |

The explanation offered for the flatness — loop self-reactance, 332 Ω against a
50 Ω port — was **falsified by R62**. So a scaling law and a measurement disagree
completely and nothing survives to explain it.

🔑 **This cannot be resolved by more point-sampling**: both slopes produce
plausible individual readings. §12 grew d and 2w **together** (aspect ratio ~1.4
throughout) — one diagonal through the space. A flat sweep along a degenerate
direction and a genuinely flat surface are indistinguishable from the surface.

⏳ **IN FLIGHT: `scatter.py`** — 12 random (depth, half-width, wire radius) points
with area ≤ 1,100 mm², two stages each (starved locate, then narrow measure).
Tests whether the flatness is a degenerate direction. Affordable only because
narrow-band solves are ~29 s instead of 850.

### 🔧 New harness: `watchjob.py`

Wakes on completion OR a deadline and **diagnoses**: log growing = progressing;
log frozen at ~100% CPU = **not converging, waiting will not help**; frozen at
~0% = deadlocked. Those look identical from "still running" and need opposite
responses. Two jobs burned 3h51m and 50 min unnoticed before this existed.

⚠️ Deadlines must be computed from measured solve times, not guessed: a 600 s
guess for `scatter.py` was **18× low** against a measured 3.1 h.

| 110 | 🔑 **Linewidth Q_ext was biased ~2× low; β=2.76 wrong; coupling model validated** | 🔴 Coarse sampling (20 kHz on a 130 kHz linewidth) overshoots the half-power point and **systematically lowers Q_L** — silent, one-directional, plausible. **Q_ext at R=50 is 31,304, not 9,785–16,568.** ✅ f and Q₀ unaffected (10 kHz, 0.3% across a 350× band change). ✅ **POSITIVE CONTROL PASSED**: port-impedance sweep gives a clean \|S11\| minimum at R≈50 with β crossing 1 both sides — matching is reachable, two observables agree, **β=2.76 is wrong (true 1.46)**. 🔴 **R56 survives on a better footing**: min Q_ext 31,304 against a required few hundred, **98× deficit**, and port impedance cannot fix it. 🔴 **OPEN: geometry says Q_ext ∝ A⁻², §12 measured A⁻⁰·⁰⁷, and R62 killed the explanation.** `scatter.py` in flight to test whether §12's diagonal was degenerate |

## 2026-08-18 — 🔑 R65 OPENED: the analytic Q_ext = 165 was never valid, and the electrically-small regime has never been sampled

Prompted by the observation that *"at some point we had a coupling and lost it —
but that was analytical, and we haven't been able to re-derive it by simulation,
with any architecture."* That is exactly right, and tracing it exposes a
domain-of-validity error rather than an arithmetic one.

### The coupling was never simulated at any step

| step | claim | source | status |
|---|---|---|---|
| target | Q_ext = **165** | small-loop formula 2Z₀U/(ωμ₀²H²A²) | never reproduced |
| measured | Q_ext = 14,442 | simulation (§12) | → **31,304** after entry 110 |
| patch | **45×** from loop self-inductance | lumped L = 21.5 nH | 🔴 falsified by R62 |

Line 1334 recorded the moment the analytic result was exempted from simulation:
*"The analytic result stands regardless… Simulation would confirm arithmetic we
are already confident in."* R62 then falsified the **patch**. Nobody asked
whether it also falsified the **original**.

### It does, for the same reason

🔢 The small-loop formula assumes **uniform current around the loop**. R62's
finding was that the loop perimeter is ~λ/2. A λ/2 loop has a **current null and
a sign reversal**: its two halves link flux with opposite sign and partially
cancel. The formula that produced 165 is invalid in precisely the regime where
it was applied — and so is the 21.5 nH lumped inductance that was supposed to
explain the shortfall. Both rest on the same assumption.

### 🔴 Every loop ever simulated is electrically large

λ = 122.4 mm at 2.45 GHz; `--loop d,w` gives perimeter ≈ 2(d + 2w).

| loop | perimeter | in λ |
|---|---:|---:|
| 12 × 17 mm — **smallest ever tested** (§12) | 58 mm | **0.47 λ** |
| 28 × 40 mm | 136 mm | 1.11 λ |
| 36 × 52 mm | 176 mm | 1.44 λ |
| `scatter.py` bounds d∈[8,30], w∈[5,20] | 36–140 mm | **0.29–1.14 λ** |

"Electrically small" is ≲ 0.1 λ, i.e. ~12 mm perimeter — about a 3 × 3 mm loop
of **9 mm²**, some 23× smaller in area than the smallest point ever sampled.
**The regime the analytic coupling was derived in has never been simulated**,
and neither §12, R62, nor the running scatter can reach it by construction.

### Three loose ends collapse into one cause

- **§12's A⁻⁰·⁰⁷** — growing the loop adds flux *and* electrical length, so the
  phase reversal eats the gain. Not a degenerate sweep direction; a ceiling.
- **R62's monotonic flange sweep** — no lumped inductance to cancel, because at
  λ/2 there isn't one.
- **the 98× deficit** — a formula quoted outside its domain.

⚠️ **This weakens R62's generality.** R62 tested series-capacitor cancellation on
a λ/2 structure where the lumped model was already void, so its null is
plausibly **regime-specific, not general**. At λ/20 the loop *is* an inductor and
the cancellation could exist — the one place it was never tried, and how real
couplers are actually built.

🔢 The honest counter-argument, to be tested rather than assumed: flux ∝ A, so
coupled power ∝ A², and a 9 mm² loop starts ~500× worse than a 204 mm² one
*before* matching. R65 is therefore not "small loops couple better" — they do
not. It is **"does the cancellation that failed at λ/2 work at λ/20?"** If it
never works at any perimeter, the analytic 165 dies for good and the loop route
closes on evidence rather than on a single falsified patch.

### R65 — the test

Sweep loop **perimeter** from ~λ/20 to ~λ/2 with and without the R62 gap+flange,
and measure whether the gap changes Q_ext by 1 + (X_L/Z₀)². Known-answer in
form: the ratio must **rise as perimeter falls** if the lumped picture is ever
valid. Flat across the whole range falsifies it everywhere.

| 111 | 🔑 **R65 OPENED — the analytic Q_ext=165 was invalid where it was applied; λ/20 never sampled** | Prompted by "we had a coupling and lost it, but that was analytical." 🔑 **The coupling was never simulated at any step**: target 165 analytic, the 88× shortfall explained by an analytic 45× patch, patch falsified by R62 — but **the same λ/2 finding invalidates the original**, since the small-loop formula assumes uniform loop current and a λ/2 loop has a current null and sign reversal. 🔴 **Every loop ever simulated is electrically large**: smallest ever tested is **0.47 λ**, `scatter.py` spans 0.29–1.14 λ, electrically small is ≲0.1 λ ≈ 9 mm² — **23× below the sampled floor**. ✅ Unifies §12's A⁻⁰·⁰⁷, R62's monotonic flange, and the 98× deficit as one domain error. ⚠️ **R62 weakened to regime-specific**: it tested cancellation where there was no inductance to cancel. R65 asks whether cancellation works at λ/20, not whether small loops couple better (they do not, ~500× worse in flux) |

## 2026-08-18 — 🔑 R66 OPENED: the coupler has the wrong topology, not the wrong size — TE₀₁₁ wall current is purely azimuthal

The user's reframing, and it is literal rather than metaphorical: *"We designed
the plasma to be a torus, after all. We're trying to view the lit torus at its
center, which does not exist."*

### The field topology, which settles the loop question

🔢 TE₀₁₁ has E = E_φ only and H poloidal (H_r, H_z). The surface current
`J_s = n̂ × H` is therefore **purely azimuthal on the barrel AND on both end
caps**. This is the mode's defining property — it is why TE₀₁₁ has exceptional Q
and why it tolerates a non-contacting end cap: no current crosses the joint.
The plasma ring is that same current continued in gas rather than in metal, so
the cavity is a **one-turn transformer with a toroidal secondary**.

🔴 A small loop at the barrel therefore links H_z over a few degrees of azimuth
out of 360 — a **magnetic point probe on a distributed ring**. Enlarging it to
link more azimuth makes it electrically long (R65) before it links much. This is
not a size problem that a better (d, w) can solve.

> **§12's A⁻⁰·⁰⁷ is what a parameter surface looks like when the answer is "not
> here" everywhere on it.** Flat because the family is wrong, not because the
> sweep direction was degenerate.

### The orientation rule, and why it is also a mode filter

| feature | cuts azimuthal J_φ | couples TE₀₁₁ |
|---|---|---|
| circumferential slot/gap | no — runs parallel | ❌ this is the classic TE₀₁₁ **choke** |
| **axial slot in the barrel** | **yes, broadside** | ✅ |
| radial slot in an end cap | yes | ✅ |
| circular iris (R63) | partially, and topologically a point | weak — Bethe d⁻⁶ |

🔢 Two consequences that make this more than a substitution:

- **Resonant-length scaling, not d⁶.** A λ/2 slot is ~61 mm and couples as an
  antenna, not as a small-hole perturbation. R63's circular iris was
  topologically a point, which is why it had to be enormous to do anything.
- **🔑 Mode selectivity for free.** TM₀₂₀ — the degenerate competitor the mode
  filter exists to suppress — has H_φ only, so its barrel wall current is
  **axial**. An axial slot runs *parallel* to TM₀₂₀'s current and *cuts*
  TE₀₁₁'s. The feature that couples the wanted mode is close to blind to the
  fought one. Coupling and discrimination from one geometric choice.

⚠️ To verify rather than assume: the sign/orientation work above is analytic and
must be confirmed numerically — this whole line of enquiry began with an analytic
result exempted from simulation (entry 111). The slot must also be backed by a
WR-340 section whose own broad-wall current it cuts; that part is ordinary
slotted-waveguide practice.

### Consequence for work in flight

`scatter.py` changes role: it is no longer searching for a good loop, it is the
**negative control**. Twelve random points flat across 0.29–1.14 λ is the
evidence that licenses abandoning the loop *family* rather than optimising
within it. R65 (small-loop regime) drops below R66 in priority — it settles
whether the analytic 165 was ever valid, which is bookkeeping, where R66 could
deliver the coupling.

| 112 | 🔑 **R66 OPENED — the coupler has the wrong TOPOLOGY; TE₀₁₁ wall current is purely azimuthal, so the fix is an axial slot** | User's reframing, literal not metaphorical: the plasma is a torus and we were hunting a coupling at its non-existent centre. 🔢 **TE₀₁₁ wall current is φ-directed on the barrel and both caps** — the mode's defining property, and why it tolerates a non-contacting cap. A small loop is a **magnetic point probe on a distributed ring**; enlarging it hits R65's λ/2 limit before it links meaningful azimuth. 🔑 **§12's A⁻⁰·⁰⁷ is a wrong-family signature, not a degenerate sweep direction.** ✅ Orientation rule: an **axial slot cuts J_φ broadside** and scales as a resonant length (λ/2 ≈ 61 mm), not as Bethe d⁻⁶ — R63's circular iris was topologically a point. 🔑 **Bonus: TM₀₂₀ barrel current is AXIAL**, so an axial slot is near-blind to the degenerate competitor — coupling and mode discrimination from one feature. ⚠️ Analytic; must be confirmed numerically. `scatter.py` re-purposed as the negative control |

⚠️ **Caveat logged live, at 3 of 12 scatter points:** the surface is NOT flat
off-diagonal — Q_ext 17,521 / 37,528 / 151,715 across areas 320 / 531 / 435 mm²,
an **8.7× spread** where §12's diagonal moved 12%. So §12 was indeed a degenerate
direction, and the "flat everywhere" negative control above is **not** what is
being observed. Note the sign, though: the **smallest area couples best**, which
is backwards for any flux argument and is what the electrical-length picture
(R65) predicts. It does not rescue the family — 17,521 is still ~50× short and is
the best of three. R66's topology argument stands on the field geometry, not on
the flatness. Await all 12 before fitting.

## 2026-08-18 — 🔴 R67 OPENED: Q_lit = 320 is a converged answer to an assumed question, and the 98× coupling deficit is σ in disguise

The user: *"Q = 320 is an artifact of measuring the center of a torus, with an
error. It's actually 0."* Substantially right, and the mechanism is nameable.

### The provenance

`r12.py:26` is `SIGMA = 30.0` — a bare literal, no derivation, no citation.
`baselines.json` carries `plasma.sigma` with **`error: null`**, the schema's own
marker for UNMEASURED. `plasma.q_loaded = 320 ± 10` then reports *mesh*
convergence across a 7.4× refinement. **We converged onto a restatement of a
guess**, and the tightness of that convergence (0.3%) made it read as solid.

### 🔑 The deficit is not a coupler property

🔢 Q_lit ∝ 1/σ in the volumetric regime, so

        coupling_deficit = Q_ext / Q_lit  ∝  σ
        31,304 / 320 = 97.8

**The 98× "coupling deficit" is the σ = 30 assumption in different units.** It
is a linear readout of line 26, not a measurement of any coupler. Every
architecture "failed" against a target that moves 1:1 with an unvalidated input.

### σ checked against plasma physics rather than against itself

🔢 σ = n_e e²/(m_e ν_m), with ν_m ≈ 10¹¹–10¹² s⁻¹ for atmospheric argon:

| σ (S/m) | n_e @ν=10¹¹ | n_e @ν=10¹² | Q_lit | deficit vs Q_ext = 31,304 |
|---:|---:|---:|---:|---:|
| 30 | 1.1e14 cm⁻³ | 1.1e15 cm⁻³ | 320 | **98×** |
| 3 | 1.1e13 | 1.1e14 | ~3,200 | ~10× |
| 0.3 | 1.1e12 | 1.1e13 | ~32,000 | **~1 — already matched** |

MP-AES-class 2.45 GHz atmospheric plasmas run ~10¹³–10¹⁴ cm⁻³; **σ = 30 sits at
the ICP end of the plausible range.** ✅ At σ ≈ 0.3 S/m the *bare measured loop*
is critically coupled. The coupling crisis may be entirely manufactured.

⚠️ Where this stops short of the user's "actually 0": Q₀ = ωU/P_abs is a
well-defined energy ratio at any σ, so 320 is not nonsense — it is the correct
answer for a plasma nobody has shown exists. What is fictitious is its **status
as a design target**.

### 🔑 The torus centre, named

σ, Q and P_abs are **mutually determined**: σ sets absorption, absorption sets
the power sustaining ionisation, ionisation sets σ. We broke the loop by pinning
σ and solving once, then walked the coupler surface hunting a fixed point we had
already assumed away. There may be one fixed point, several, or none at the
available power. **Nothing about the lit state is established until that is
solved.**

⚠️ Corroboration previously filed as harmless: the lit peak scatters **5 MHz
across meshes on a 7.6 MHz linewidth** — 66% of its own width. The energy-integral
defence of Q is fair, but it means the lit resonance **cannot be located to
better than two-thirds of its width**, so "tune the cavity to the lit state" is
not presently possible either.

### Re-scoping

🔴 **R56's 98× and every lit-state conclusion are suspended**, not refuted.
R63/R65/R66 (iris, small loop, axial slot) were all chasing a target set by line
26. **R67 now precedes them**: sweep σ over 0.03–30 S/m, extract Q_lit(σ), and
intersect it with an independent power-balance estimate of what σ a given
absorbed power density sustains. The design point is that intersection.

| 113 | 🔴 **R67 OPENED — Q_lit=320 is a converged answer to an ASSUMED σ; the 98× deficit is σ in disguise** | `r12.py:26` is a bare `SIGMA = 30.0`; `plasma.sigma` carries **`error: null`** (UNMEASURED) while `plasma.q_loaded = 320 ± 10` reports only *mesh* convergence — 0.3% tightness onto a restatement of a guess. 🔑 **Q_lit ∝ 1/σ, so deficit = Q_ext/Q_lit ∝ σ, and 31,304/320 = 97.8**: the "coupling deficit" is a linear readout of line 26, not a property of any coupler. 🔢 σ=30 ⟹ n_e ~1e14–1e15 cm⁻³, the **ICP end** of the plausible range; MP-AES-class is 1e13–1e14. ✅ **At σ ≈ 0.3 S/m the already-measured bare loop is critically coupled** — the crisis may be manufactured. 🔑 **The torus centre named: σ, Q and P_abs are mutually determined and the fixed point was never solved for.** ⚠️ Lit peak scatters 5 MHz on a 7.6 MHz linewidth, so the lit resonance cannot be located to tune to. 🔴 **R56 and all lit-state conclusions suspended; R67 precedes R63/R65/R66** |

## 2026-08-18 — 🔑 R68 OPENED: simulate MP-AES and MICAP as POSITIVE CONTROLS; R67's "manufactured crisis" branch weakened

The user: *"we have two examples to compare to: MP-AES and MICAP, both
demonstrably working. Since they are known to work, we should be able to
simulate them. If we can't, our model is wrong, and if we can, we can tell
whether or not the circular waveguide can work or not."* This is the
falsification the coupling work has lacked — **every AMIP result to date is
self-referential**, measured against targets AMIP itself generated.

### What the two devices actually are

| | MP-AES (Agilent 4100/4200/4210) | MICAP (Radom) |
|---|---|---|
| resonator | **Hammer cavity**, a waveguide structure | **alumina dielectric resonator ring** |
| feed | **capacitive/resonant iris in the waveguide** | magnetron into the DR |
| coupling | **from the MAGNETIC field**, explicitly unlike earlier E-coupled MIPs | polarisation currents in the ring → axial H, *"analogous to the electrical current within a traditional ICP load coil"* |
| gas / power | N₂ or air, ~1 kW | N₂, ~1.5 kW, 19.4 L/min |
| plasma | toroidal, aerosol into the core | toroidal |

✅ **Both couple magnetically, and neither uses a loop.** MP-AES's commercial
answer to "how do you couple a microwave plasma" is **an iris in a waveguide** —
independent corroboration of R66's topology argument from a device on the market
since 2012. 🔑 **MICAP is AMIP with a different resonator**: azimuthal E driving
a toroidal secondary at 2.45 GHz, same physics, smaller structure.

### ⚠️ R67 partially walked back

R67 speculated σ = 30 S/m might be 10–100× too high. Checked against these
devices it is **defensible**: MICAP claims ICP-approaching performance, argon
ICPs run n_e ≈ 1–3e15 cm⁻³, and σ = 30 corresponds to 1e14–1e15 cm⁻³.
🔴 **The "crisis is manufactured" branch weakens; the 98× deficit is probably
real.** R67's core survives — σ is unvalidated and the deficit scales linearly
with it — but the resolution is not "the target was fake".

### 🔑 The question inverts: what does MICAP's resonator have that TE₀₁₁ lacks?

🔢 Candidate: **scale**. TE₀₁₁ at 2.45 GHz forces a = 103.70 mm. The plasma at
r = 4.5–8.5 mm sits where E_φ is 27% of peak (J₁(0.314)/J₁ₘₐₓ). A dielectric
resonator shrinks by √ε_r — 3.1× for alumina (ε_r ≈ 9.8), ~30× in volume; more
for a high-ε DR ceramic. MICAP wraps a **small** resonator tightly around the
plasma; AMIP puts a small plasma **and** a small coupler inside a large cavity,
the loop occupying ~1e-4 of the mode volume.

> **Q_ext is hard to make small when the coupler is 10⁻⁴ of the cavity.** That is
> a SCALE mismatch, not a shape problem, and it would explain why loop, iris and
> slot all look weak at once.

### The test that does not need paywalled geometry

Exact Agilent/Radom drawings are not needed and the RSC/Elsevier sources are
paywalled. The project's discipline is exponents and ratios, not absolute
values, so the control is: **build a Hammer-type structure — shorted WR-340
section, capacitive iris, torch on axis — and ask whether our model says it
matches.** A model that reports the commercial device as 98× undercoupled is
falsified, and the AMIP verdict then means nothing. A model that reports it
matched can be believed when it judges TE₀₁₁.

| 114 | 🔑 **R68 OPENED — MP-AES and MICAP as positive controls; MP-AES uses an IRIS, corroborating R66; R67 partly walked back** | User: two demonstrably working devices exist, so a model that cannot reproduce them is wrong. **Every AMIP result to date is self-referential.** ✅ **MP-AES = Hammer cavity + capacitive IRIS in a waveguide, coupling from the MAGNETIC field** — the commercial answer is an iris, not a loop, corroborating R66 from a 2012 product. ✅ **MICAP = alumina dielectric resonator ring**, polarisation currents → axial H *"analogous to an ICP load coil"*, toroidal N₂ plasma at 2.45 GHz — **AMIP's physics with a smaller resonator**. ⚠️ **R67 weakened**: σ=30 ⟹ n_e 1e14–1e15 cm⁻³, defensible against ICP-class devices, so **the 98× deficit is probably REAL** and the target was not fake. 🔑 **Question inverts — what does MICAP have that TE₀₁₁ lacks? Candidate: SCALE.** DR shrinks by √ε_r (~30× volume for alumina); AMIP's loop is ~1e-4 of mode volume. ✅ Test needs no paywalled geometry: build a Hammer-type shorted-WR-340 + iris and see if our model calls it matched |

## 2026-08-18 — 🔑 R69 OPENED: the TE₀₁₁ magnetic torus has coordinates, and loop POSITION has never been varied

The user: *"A magnetic field is a literal torus. Instead, we should try to
characterize the torus ID and OD, and try to measure coupling somewhere
in-between."* Doing that exposes a constraint neither of us had stated.

### The torus, analytically (a = 103.70 mm, L = 88.53 mm)

🔢 E_φ ∝ J₁(k_c r)·sin(πz/L), H_z ∝ J₀(k_c r)·sin(πz/L),
H_r ∝ −J₁(k_c r)·cos(πz/L), with k_c = χ′₀₁/a.

| feature | radius | what it is |
|---|---:|---|
| **E_φ max ring** | **49.83 mm** (0.4805 a) | the plasma current ring — the designed torus |
| **H null circle (O-point)** | **65.08 mm** (0.6276 a) | the MAGNETIC torus core; H_z reverses sign here |
| barrel wall | 103.70 mm | E_φ = 0 |

🔢 Net flux linked by a COAXIAL mid-plane loop of radius R, ∝ R·J₁(k_c R):

| R (mm) | 20 | 40 | 49.83 | **65.08** | 80 | 103.70 |
|---|---:|---:|---:|---:|---:|---:|
| flux (norm.) | 0.204 | 0.657 | 0.858 | **1.000** | 0.841 | **0.000** |

✅ **Maximised exactly at the H-null radius and identically ZERO at the wall.**
The user's ID/OD framing lands on 65.08 mm analytically.

### 🔑 The unstated constraint: metal may only sit where E_φ = 0

In the barrel that is **only the wall**, which is why every loop in this project
has been mounted at r = 103.70 mm — never a design choice, the only legal
position. 🔑 But **both END CAPS are also E_φ nulls** (E_φ ∝ sin πz/L), an
entire unswept surface, and H_r peaks there at r = 49.83 mm.

So "somewhere in between" is buildable: a coupler on the **end cap at
r ≈ 50–65 mm**, not on the barrel at 103.70 mm.

### ⚠️ The honest arithmetic — position alone does NOT close the deficit

🔢 |H_z|peak/|H_r|peak = k_c/((π/L)·J₁ₘₐₓ) = 1.789; |H_z| at the wall is
J₀(χ′₀₁) = 0.4028 of the axial peak, i.e. 0.721 of |H_r|peak. Moving a coupler
from the barrel wall to the cap at r = 49.83 mm therefore gains

        1.39x in H  →  1.93x in coupled power.   NOT 98x.

What the cap gives instead is **room**: a full annulus rather than a strip jammed
against the barrel — which is the axis R65 says is needed. ⚠️ Note also that
**every loop ever simulated sat entirely in r > 65.08 mm**, the reversed-H_z
outer region where |H_z| is only 0.2–0.40 of the axial peak.

### 🔴 A third never-sampled dimension

- R65: loop **perimeter** never taken below 0.29 λ.
- R69: loop **position** never varied at all — barrel wall, mid-plane, every run.

⚠️ Everything above is Bessel algebra, which is precisely what entries 111 and
113 are about. **Next step is to MEASURE the torus, not to trust it**: dump H and
E from a solved case, locate the null circle and flux maximum numerically, and
check against 65.08 and 49.83 mm. Post-processing, not a new solve, and it gates
the position sweep.

| 115 | 🔑 **R69 OPENED — the magnetic torus has coordinates (core 65.08 mm, plasma ring 49.83 mm) and loop POSITION was never varied** | User: characterise the torus ID/OD and couple in between. 🔢 **H-null circle at r = 65.08 mm (0.6276a)** is the magnetic torus core where H_z reverses; **E_φ max ring at 49.83 mm (0.4805a)**. Coaxial mid-plane flux ∝ R·J₁(k_c R) is **maximised exactly at 65.08 mm and ZERO at the wall** — the ID/OD framing lands on a number. 🔑 **Unstated constraint found: metal may only sit where E_φ = 0**, which in the barrel is ONLY the wall — every loop's position was forced, not chosen. **Both END CAPS are also E_φ nulls**, an entirely unswept surface, with H_r peaking there at 49.83 mm. ⚠️ **Honest arithmetic: wall → cap gains only 1.39× in H, 1.93× in power — NOT 98×**; what the cap buys is ROOM. ⚠️ Every loop ever simulated sat in r > 65.08, the reversed-H_z region at 0.2–0.40 of axial peak. 🔴 **Third unsampled dimension** (after R65's perimeter). Measure the torus before trusting the algebra |

### ✅ The (ID+OD)/2 midpoint rule is ROBUST — it finds the H_r maximum unaided

User's refinement: place the coupler at **(ID + OD)/2**. Applied to every
defensible bounding pair:

| ID → OD | (ID+OD)/2 | \|H_r\| there | % of max |
|---|---:|---:|---:|
| torch OD (10.5) → wall | **57.10 mm** | 0.5672 | 97.5% |
| axis → wall | **51.85 mm** | 0.5807 | **99.8%** |
| E_φ ring → H-null core | **57.46 mm** | 0.5658 | 97.2% |
| E_φ ring → wall | 76.76 mm | 0.3975 | 68% |
| H-null core → wall | 84.39 mm | 0.2938 | 50% |

🔑 **Every definition that bounds the torus by its true extent clusters at
52–57 mm and lands on 97–100% of the transverse-field maximum** (|H_r| peak
0.5819 at r = 49.83 mm). The rule finds the optimum without being told it. The
two outliers use an *interior* feature as the inner bound, which does not
describe the torus's extent.

✅ **Actionable answer: couple on the END CAP at r ≈ 52–57 mm** — a legal
position for metal, and 1.39× in H / 1.93× in coupled power over the barrel wall
used in every run to date.

⚠️ The optimum radius depends on coupler SIZE, which is why a sweep must follow
the formula rather than replace it:

| coupler | best radius |
|---|---|
| small loop linking H_z | r → 0 — **occupied by the torch** |
| small loop linking H_r | **49.83 mm** |
| large coaxial loop (flux R·J₁) | **65.08 mm** |

Our loops sit between those limits, so the true optimum is 50–65 mm — the band
the midpoint rule brackets. **R69's test: sweep cap radius 15 → 95 mm.** First
time r has been a variable.

## 2026-08-18 — ✅ R70: SCATTER ANSWERED. Q_ext = 1,084 measured (29× better than the believed floor), but NO geometric parameter predicts it

12 random loop geometries, seed 20260818, area ≤ 1,100 mm², two-stage
locate-then-measure. All 12 usable, EXIT=0.

### ✅ The measurements are trustworthy — validated against a second observable

Q_ext from the linewidth vs |Γ| measured directly at the peak, using
β = Q₀/Q_ext and |Γ| = |1−β|/(1+β):

**12/12 agree within 0.12 in |Γ| across a 140× Q_ext range.** The best-coupled
case predicts |Γ| = 0.941 and measures 0.941. Every case is a clean single peak
with bore-H 0.0192–0.0209, well above the 0.018 TE₀₁₁ threshold and tightly
clustered — **no mode contamination**, so the scatter is physics, not
misidentification.

### 🔑 Q_ext = 1,084 — the believed floor was 29× too high

| d | 2w | area | perim/λ | Δf | Q₀ | **Q_ext** | β unlit |
|---:|---:|---:|---:|---:|---:|---:|---:|
| **25.8** | **38.8** | **1001 mm²** | 1.06 | **17.2 MHz** | 35,773 | **1,084** | 33.0 |
| 13.1 | 16.4 | 215 | 0.48 | 3.4 | 45,465 | 13,817 | 3.3 |
| 15.3 | 28.4 | 435 | 0.71 | 1.0 | 44,737 | 151,715 | 0.29 |

🔑 **The lit-state deficit falls from 98× to 3.4×** (Q_ext 1,084 against the
σ-dependent target ~320). The previously recorded minimum was 31,304.
⚠️ The cost is real: Q₀ drops 21% and the resonance moves 17.2 MHz, so this loop
perturbs the mode — and at β = 33 it is badly OVERcoupled unlit, which is R56's
"one state is always mismatched" showing up again.

### 🔴 But NO geometric parameter predicts Q_ext

Log-log regression of Q_ext on every loop variable, 12 points:

| predictor | exponent | r² |
|---|---:|---:|
| area | −0.52 | **0.043** |
| perimeter | −0.63 | **0.018** |
| aspect | −0.61 | 0.036 |
| depth d | −2.29 | 0.162 |
| half-width w | −0.12 | 0.001 |
| wire radius rw | +0.97 | 0.055 |
| Δf (mode pull) | −0.36 | 0.171 |
| Q₀ | +13.45 | 0.495 |

Best two-variable fit reaches only r² = 0.376, and needs exponents of −11.9 and
+21.8 — i.e. it is fitting noise.

> 🔑 **Q_ext varies 140× with no power-law dependence on any loop dimension.**
> The only decent single predictor is Q₀, which is an OUTCOME, not a design
> variable, and its absurd +13.45 exponent means both are driven by a common
> hidden variable — mode perturbation.
>
> **The loop response is not a smooth function of loop geometry.** It cannot be
> designed, and it cannot be optimised by point-sampling: neighbouring points
> carry no information about each other. This is the torus-walking failure
> measured rather than argued, and it is a far stronger result than §12's
> "flat" — which is now explained as a diagonal that happened to stay in one
> regime.

### 🔴 Unresolved: sc06 contradicts §12 by 12× at nearly identical geometry

| source | d × 2w | area | f | Q_ext |
|---|---|---:|---:|---:|
| §12 | 28 × 40 | 1120 mm² | 2.42177 | 12,840 |
| R70 sc06 | 25.8 × 38.8 | 1001 mm² | **2.40227** | **1,084** |

Nearly the same loop, **12× apart in Q_ext and 19.5 MHz apart in frequency**.
Entry 110's step bias cannot explain it — that bias makes Q_ext read LOW, so
§12's true value would be even higher. Candidate cause: §12 predates the mode
filter and probably ran without `--mode-filter 3`, making these different
cavities. ⚠️ **Must be checked before either number is used**; one of them is
describing a configuration nobody intends to build.

| 116 | ✅ **R70 — scatter answered: Q_ext = 1,084 (29× below the believed floor), but NO loop parameter predicts Q_ext** | 12 random geometries, all usable. ✅ **Validated against a second observable: 12/12 agree within 0.12 in \|Γ\| across a 140× range**, best case predicting 0.941 and measuring 0.941; every peak clean at bore-H 0.019–0.021, so the scatter is physics not misidentification. 🔑 **Best point Q_ext = 1,084 at 1001 mm² — deficit 98× → 3.4×**, against a previous floor of 31,304. ⚠️ Cost: Q₀ −21%, resonance moved 17.2 MHz, β = 33 badly overcoupled unlit. 🔴 **Regression finds NOTHING**: area r²=0.043, perimeter r²=0.018, w r²=0.001, best 2-var r²=0.376 with nonsense exponents. Only Q₀ correlates (r²=0.495, exponent +13.45) and it is an OUTCOME — both driven by mode perturbation. **The loop response is not a smooth function of loop geometry; it cannot be designed or optimised by point-sampling.** §12's "flat" was a diagonal inside one regime. 🔴 **OPEN: sc06 contradicts §12 by 12× and 19.5 MHz at nearly identical loop size** — likely the mode filter, must be resolved before either is used |

## 2026-08-18 — 🔑 R71 OPENED: the "divide by zero with no error", named and given a quantitative test

The user: *"The magnetic field is a torus and we're trying to derive coupling in
the center. This obviously can't work, methodologically. That's the divide by 0
with no error."* R70 caught it in the act.

### What the error-free divide-by-zero actually is

🔴 R70 regressed Q_ext against every loop variable over a **140× range** and
found **nothing**: area r² = 0.043, perimeter 0.018, half-width **0.001**. The
regression still returns exponents — −0.52, −0.63, −2.29 — and **never signals
that they are meaningless**. §12 reported a slope of −0.07 and never reported its
r². That is the divide-by-zero: a machine that always yields a number, applied to
a function that has no gradient in the space being swept.

> Every loop sweep since §12 has been computing a derivative that does not exist.

### 🔑 The candidate mechanism, and its quantitative criterion

χ′₀₁ = χ₁₁ **exactly**, so TE₀₁₁ and TM₁₁₁ are degenerate by construction.
Perturbation theory for "how does the loop change the mode" divides by the
inter-mode frequency difference — **literally zero at exact degeneracy**. The
response is then not analytic: it is set by which superposition inside the
degenerate subspace the perturbation selects, and that rotates discontinuously
with geometry. The signature would be exactly what R70 measured, including Q₀
being the only correlate (r² = 0.495) at an absurd exponent of **+13.45** —
coupling and mode identity moving together.

🔢 The criterion is **mode separation vs coupler frequency pull**:

| | TE₀₁₁–TM₁₁₁ separation | loop pull (R70 max) | margin |
|---|---:|---:|---:|
| no mode filter | 19.5 MHz | 17.2 MHz | **1.1×** — fully degenerate |
| 3 mm mode filter | 64.3 MHz | 17.2 MHz | **3.7×** — marginal |

⚠️ **This does NOT confirm the mechanism.** R70 ran WITH the 3 mm filter, at a
3.7× margin, and still scattered 140×. Thin, but not obviously thin enough. The
degeneracy is a candidate, not a finding.

### 🔑 The trap it implies

The loops that couple best are the ones that pull hardest — sc06 gave the best
Q_ext (1,084) with the largest pull (17.2 MHz) and the largest Q₀ drop (−21%).
**Coupling strength and mode integrity are the same variable in this cavity.**
Any coupler large enough to couple is large enough to restructure the mode it
couples to, which is why the surface has no usable gradient.

### R71 — the test

Repeat a handful of R70's points with a THICKER mode filter and compare the
**spread**, not the values. Two clean outcomes:

  scatter collapses to a smooth law  ✅ degeneracy confirmed; separation is the
     lever, and loop coupling becomes designable for the first time
  scatter persists                   🔴 the non-smoothness is something else and
     the mode filter is not the lever — stop sweeping loops entirely

⚠️ Either way, **no further loop-geometry optimisation until R71 answers**, and
any past exponent fitted over loop geometry (§12's −0.07 included) must carry an
r² before it is quoted again.

| 117 | 🔑 **R71 OPENED — the error-free divide-by-zero named: sweeps have been computing a derivative that does not exist** | User's diagnosis, confirmed by R70's regression: **Q_ext varies 140× with r² = 0.043 (area) / 0.018 (perimeter) / 0.001 (half-width)**, yet the fit still returns exponents and never flags them as meaningless — **§12's −0.07 was quoted without an r²**. 🔑 **Candidate mechanism: the exact χ′₀₁ = χ₁₁ degeneracy**, where perturbation theory divides by an inter-mode gap of exactly zero, so the response is set by which degenerate superposition the loop selects and rotates discontinuously. Signature matches: Q₀ the only correlate (r²=0.495) at exponent **+13.45**. 🔢 Criterion = separation vs pull: **no filter 19.5 vs 17.2 MHz = 1.1× (degenerate); 3 mm filter 64.3 vs 17.2 = 3.7× (marginal)**. ⚠️ **NOT confirmed — R70 ran WITH the filter and still scattered.** 🔑 **Trap: the best-coupling loop is also the hardest-pulling** (sc06: best Q_ext, largest pull, largest Q₀ drop) — coupling and mode integrity are one variable. **R71: repeat points at a thicker filter, compare SPREAD not values. No loop optimisation until it answers** |

## 2026-08-18 — ✅ R72: STOPPED MEASURING THE CENTRE. The field map says the target is reachable, and names the coupler

The user: *"Stop measuring the center. It's not there. We have to measure from
somewhere else."* Correct, and `rig_cap.py` as written was the same mistake on a
different surface — another coupler sweep.

### The move: measure the FIELD, not the response

The centre that does not exist is *"the coupling coefficient of a loop in this
cavity."* Every attempt to measure it inserts a coupler, and R71 showed the
insertion destroys the measurement: the coupler perturbs a degenerate mode, so
what returns is its own back-reaction. **The mode is a coupler-independent
object and cannot be perturbed by a probe that is not there.** Flux available to
any footprint is then an integral over it — smooth by construction, no
degeneracy anywhere in it.

🔑 **ADMISSIBILITY RULE, from R71**: a coupler whose frequency pull exceeds ~1/10
of the mode separation is measuring its own back-reaction. With the 3 mm filter
that is **6.4 MHz**. sc06 pulled **17.2 MHz** — 2.7× outside, which is why the
best-coupling point is also the least trustworthy.

### The map (analytic TE₀₁₁, normalised by sqrt of stored energy)

**A) Barrel at mid-plane** — normal ẑ, links H_z, radial depth d:

| d mm | 5 | 20 | 38.6 | 50 |
|---|---:|---:|---:|---:|
| flux/area vs best cap | 0.72 | 0.65 | 0.47 | 0.32 |

🔑 **A barrel loop gets WORSE per unit area the deeper it goes**, averaging over
falling H_z toward the null at 65.08 mm; past it the flux cancels. Growing a
barrel loop radially buys area and loses flux density.

**B) End cap** — normal r̂, links H_r, radius FREE:

| r mm | 15 | 30 | 45 | 49.8 | 57 | 65 | 80 | 95 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| flux/area | 0.46 | 0.81 | 0.99 | **1.00** | 0.98 | 0.89 | 0.61 | 0.23 |

✅ Flat-topped across 45–57 mm, so cap position tolerance is generous. Numerical
peak lands at **49.82 mm** against the predicted 49.83.

### 🔑 The ceiling, and how much headroom is left

🔢 Max flux a single turn can link = the poloidal flux through a mid-plane disc
out to the H-null (past it H_z reverses and cancels) = **7.844** in these units.

| coupler | area | % of ceiling | × to ceiling |
|---|---:|---:|---:|
| typical barrel 12 × 17 | 204 mm² | 1.38% | 72× |
| **sc06 barrel 25.8 × 38.8** (best measured) | 1001 mm² | **5.93%** | 16.9× |
| **cap patch r = 50, same size** | 1001 mm² | **9.74%** | 10.3× |

> 🔑 **sc06 — the best coupler in the project's history — captures 5.9% of the
> available flux.** The ceiling is 285× away in Q_ext; the floor for a perfect
> single turn is Q_ext ≈ 4. **The remaining 3.4× deficit is nowhere near a
> physical limit.**

🔢 Q_ext ∝ 1/flux², so 1,084 → 320 needs only **1.84× more flux**, i.e. 5.9% →
10.9% of the ceiling. **A cap patch of the SAME SIZE at r = 50 mm already gives
9.74% — 1.64× more flux — landing at Q_ext ≈ 400 against a target of ~320.**
Same coupler, moved from barrel to cap, is within **1.25×** of matched.

⚠️ Held against it, in order: (1) weak-coupling estimate with **no
back-reaction**, and 1001 mm² is exactly the size that violates admissibility;
(2) assumes the loop is not reactance-limited (R65); (3) analytic, so it needs
the numerical field check.

### The validation changes shape: validate the MAP, not the coupler

Measure Q_ext at three positions with a probe small enough to stay admissible
(pull ≪ 6.4 MHz), and test whether the **ratios** match the map's flux ratios. A
ratio test is immune to the absolute-scale errors that wrecked every previous
estimate. `rig_cap.py` must be rewritten to this — small probe, low port
impedance to keep Q_ext measurable, ratios not values.

| 118 | ✅ **R72 — stopped measuring the centre; the FIELD MAP says the target is reachable and names the coupler** | User: stop measuring the centre, measure from somewhere else. ✅ **Measure the field, not the response**: the mode is coupler-independent, so flux available to any footprint is an integral — smooth, no degeneracy. 🔑 **Admissibility rule: pull > 1/10 of mode separation = measuring your own back-reaction**; 6.4 MHz allowed, sc06 pulled 17.2. 🔑 **A barrel loop gets WORSE per unit area with depth** (0.72 → 0.32) — radial growth buys area, loses flux density. ✅ Cap flat-topped 45–57 mm, numerical peak **49.82 vs 49.83 predicted**. 🔑 **CEILING: sc06, the best coupler ever measured here, captures only 5.93% of linkable flux** — 285× from the Q_ext floor of ~4, so **3.4× is nowhere near a limit**. 🔑 **A cap patch of the SAME SIZE at r=50 gives 9.74%, 1.64× the flux → Q_ext ≈ 400 vs target ~320 — within 1.25×, from repositioning alone.** ⚠️ No back-reaction, not reactance-checked, analytic. **Validate the MAP by ratios with an admissible probe, not the coupler** |

## 2026-08-18 — 🔑 R73: STOPPED MEASURING Q. The observable is returned power, which has no denominator

The user, a third time: *"trying to characterize Q at the center of a magnetic
field is like staring into the abyss. It doesn't work."* Correct, and
`rig_cap.py` — written in this same session as the fix for the previous two
corrections — was still doing it. It swept cap radius and read **Q_ext**. Killed
mid-run.

### Why Q was always the wrong observable

🔑 **Q is a GLOBAL scalar**, ω·U/P integrated over the whole cavity. It has no
position. Every rig since §12 has swept a coordinate and read a whole-cavity Q,
attributing a global quantity to a local one, then trying to invert that back
into "what the coupler at r contributes" — which requires exactly the
perturbation assumption R71 showed fails.

🔑 **And Q has a denominator**: 1/Q_ext = 1/Q_L − 1/Q₀, a difference of
reciprocals, ill-conditioned the moment Q_L approaches Q₀, and **undefined
without a resonance to measure**. The lit cavity barely has one — its peak
scatters 5 MHz on a 7.6 MHz linewidth, 66% of its own width (entry 82, filed at
the time as harmless). That is the divide-by-zero structurally, and no sampling
discipline repairs a quantity that is not defined where the design needs it.

### The replacement

🔢     **η_total = 1 − |Γ|²**

"Of the power I sent in, what fraction did not come back." One measured number,
no model in it. **No resonance, no linewidth, no mode identification, no offset,
no 2× convention, no peak-finding** — the maximum of η over a band is well
defined even when the band holds a broad flat maximum rather than a resonance,
which is exactly the lit case. It is also the real design figure of merit:
"Q_ext must be 320" was only ever a proxy for "most of the power must reach the
plasma".

🔑 **The R71/R72 admissibility gate does not apply to η.** That gate existed
because Q-based coupling coefficients are linearisations that break when the
coupler perturbs the mode. η measures the outcome, so a coupler that
restructures the mode is fine provided it delivers power. **This frees the test
to use the size we would actually build** — sc06's 1001 mm² — rather than a
probe small enough to be theoretically clean and practically useless.

### R73 — the run

sc06's loop, plasma-loaded, mounted on the barrel and on the cap at r = 30/50/70.
Direct question: does moving the SAME coupler to the cap deliver more power? R72
predicts 1.64× more linked flux at r = 50; in η that is DIRECTIONAL rather than a
square law, because η saturates at 1. Decomposition into plasma/wall/dielectric
via SurfaceFlux is a cross-check, not the headline — if the split does not close,
only η_total gets quoted.

⚠️ η depends on σ = 30 S/m, still the bare literal at `r12.py:26` (R67). **Read
the ratios between cases, not the absolute percentages.**

### ⚠️ Harness bug found and fixed en route

`watchjob.py` reported **"✅ COMPLETED after 60s"** for a 50-minute job that had
not started its first solve. The driver prints its own docstring at startup, the
docstring documents its `VERDICTS:`, and the watcher was armed with
`--sentinel 'VERDICT|EXIT='`. **A detector whose pattern can match the job's own
self-description is not a detector.** Two rules now enforced: the process is
authoritative — a sentinel only ends a watch when no matching process is alive —
and sentinels must be anchored to something only the end can produce (`^EXIT=`).

| 119 | 🔑 **R73 — stopped measuring Q entirely; the observable is η = 1 − \|Γ\|², which has no denominator** | User's third correction; `rig_cap.py`, written this session as the fix for the previous two, was still sweeping position and reading **Q_ext**. Killed mid-run. 🔑 **Q is a GLOBAL scalar with no position** — every rig since §12 attributed a whole-cavity quantity to a local coordinate, then inverted it using the perturbation assumption R71 falsified. 🔑 **Q has a denominator**: 1/Q_ext = 1/Q_L − 1/Q₀, ill-conditioned as Q_L → Q₀ and **undefined without a resonance** — and the lit peak scatters 66% of its own linewidth. ✅ **η = 1 − \|Γ\|² has no resonance, no linewidth, no mode ID, no offset, no 2× convention, no peak-finding in it**, and IS the design figure of merit. 🔑 **The admissibility gate does not apply to η**, freeing the test to use the real 1001 mm² coupler. ⚠️ **Harness bug fixed: watchjob reported COMPLETED at 60 s on a 50-min job** because its sentinel matched the driver's own docstring — process is now authoritative, sentinels anchored |

## 2026-08-18 — ✅ R73 ANSWERED: 78.8% of input power reaches the plasma. The coupling crisis was an artefact of Q

Four cases, sc06's loop geometry, plasma-loaded at σ = 30 S/m, all meshed at a
COMMON size-factor 1.06 after the harness retried two failures. Order 1.

### The measurement

| case | f @ max η | η_total | η_wall | **η_plasma** | vs barrel |
|---|---:|---:|---:|---:|---:|
| **barrel** | 2.41020 | 79.3% | 0.5% | **78.8%** | 1.00× |
| cap r=70 | 2.40880 | 69.1% | 0.5% | 68.6% | 0.87× |
| cap r=50 | 2.41540 | 41.4% | 0.3% | 41.1% | 0.52× |
| cap r=30 | 2.42280 | 13.7% | 0.1% | 13.6% | 0.17× |

✅ The decomposition closes in all four. **Wall loss is 0.6–1.0% of absorbed
power** — the cavity is efficient; essentially everything absorbed reaches the
plasma rather than the silver.

### 🔴 THE FIELD MAP (R72) IS FALSIFIED, and I made the error it was built to avoid

R72 predicted the cap at r = 50 would beat the barrel by 1.64× in linked flux.
**Measured: the barrel wins, and η rises MONOTONICALLY with radius.**

The map computes linked flux with no coupler present — the coupling term. It
omits the **shorting term**: what the conductor does to the mode it is coupling
to. That is back-reaction, precisely what R71 warned of, and here it dominates.
I built a map to escape back-reaction and then used it to predict the behaviour
of a real, inserted coupler.

🔑 **Mechanism, visible in the geometry.** A cap loop's crossbar is an ARC OF
CONDUCTOR AT CONSTANT RADIUS — a partial **shorted turn to E_φ**, the one thing
TE₀₁₁ cannot tolerate. At radius r a half-width of 19.4 mm subtends:

| r | angular arc | η_plasma |
|---:|---:|---:|
| 30 | ±40.0° | 13.6% |
| 50 | ±22.6° | 41.1% |
| 70 | ±16.1° | 68.6% |
| barrel | ~0° | **78.8%** |

Smaller radius → wider arc → worse short. ✅ **The barrel loop's legs are RADIAL,
crossing E_φ rather than following it, and its crossbar sits at the wall where
E_φ = 0.** It was in the right place all along, for a reason nobody had stated.
R69's "the position was forced, not chosen" was right about the constraint and
wrong to read it as a limitation.

### 🔑 THE HEADLINE: Q made a modest penalty look like a catastrophe

🔢 η = 4β/(1+β)², which is FLAT near β = 1:

| framing | β | delivered power |
|---|---:|---:|
| "98× deficit" (Q_ext = 31,304) | 0.0102 | **4.0%** |
| "3.4× deficit" (Q_ext = 1,084) | 0.295 | **70.4%** |
| critical coupling | 1.00 | 100% |
| **measured directly** | (0.37 implied) | **78.8%** |

> **The 3.4× shortfall that drove six rounds of work is worth 21 percentage
> points of delivered power.** Q_ext is a reciprocal-difference quantity, so it
> amplifies precisely the region where the physics is least sensitive. R56's
> "one state is always badly mismatched" is true in β and nearly irrelevant in
> watts — β = 33 unlit still delivers 11%, and β = 3 delivers 75%.

### ⚠️ What this does NOT establish

- **σ = 30 S/m is still the bare literal** at `r12.py:26`, error null (R67). η
  scales with it. The RATIOS between cases are safe; 78.8% is not.
- **No mode identification was done** — deliberately, since η needs none. But
  f@max ranges 2.4088–2.4228 across cases, so they may not all sit on the same
  resonance. Irrelevant to watts delivered; **relevant to whether the plasma is
  heated in the intended TE₀₁₁ geometry**, which is an analytical-performance
  question, not a power one.
- Order 1, one mesh density. No convergence study on η.

| 120 | ✅ **R73 ANSWERED — 78.8% of input power reaches the plasma; the coupling crisis was an artefact of Q** | Four cases, sc06 loop, plasma-loaded, common size-factor. **η_plasma: barrel 78.8%, cap70 68.6%, cap50 41.1%, cap30 13.6%** — decomposition closes, **wall loss only 0.6–1.0% of absorbed**. 🔴 **R72's field map FALSIFIED**: it predicted cap r=50 beats barrel by 1.64×; measured, η rises MONOTONICALLY with radius and the barrel wins. **The map has the coupling term but not the SHORTING term** — I built it to escape back-reaction then used it to predict an inserted coupler. 🔑 **Mechanism: a cap crossbar is an arc at constant radius = a partial SHORTED TURN to E_φ**, arc ±40° at r=30 vs ~0° at the barrel. **The barrel loop's radial legs cross E_φ and its crossbar sits where E_φ = 0 — it was right all along.** 🔑 **HEADLINE: η = 4β/(1+β)² is flat near β=1, so the "3.4× deficit" is worth 21 POINTS of power** (4.0% → 70% → 78.8%). Q_ext is a reciprocal difference and amplifies where the physics is least sensitive. ⚠️ σ still a literal; no mode ID; order 1 |

## 2026-08-18 — ✅ R74 ANSWERED: η(σ) is U-SHAPED with a floor of 60.5%. The design survives a 1000× error in the one unmeasured literal

R73 closed with its own warning: *σ = 30 S/m is still the bare literal at
`r12.py:26`, error null (R67). η depends on it.* R67 could not be tested while
the observable was Q. With η it is one sweep.

**Method: ONE mesh, hash-pinned.** Every case is the same `wbarrel.msh` that
produced R73's 78.8% (md5 `ca8ca503`, 126,012 tets, size-factor 1.06). Nothing is
remeshed, so the two silent no-ops that have faked results here cannot occur —
not because they were checked but because nothing was rebuilt. Only the material
conductivity moves. ✅ **σ = 30 is a known-answer case inside the sweep and
reproduced R73 exactly** — η = 79.3% at f = 2.4102 on a wider band (2.38–2.48 vs
2.40–2.46).

### The measurement

| σ S/m | 0.3 | 1 | 3 | 10 | **30** | 100 | 300 |
|---|---:|---:|---:|---:|---:|---:|---:|
| f @ max η | 2.3972 | 2.3972 | 2.3996 | 2.4068 | **2.4102** | 2.4124 | 2.4136 |
| **η_total** | **99.5%** | 85.3% | **60.5%** | 61.2% | **79.3%** | 93.8% | **99.9%** |
| η_wall | 2.4% | 0.8% | 0.3% | 0.3% | 0.5% | 0.9% | 1.7% |
| η_plasma | 96.3% | 84.3% | 60.1% | 60.8% | 78.6% | 92.5% | 97.5% |
| **Q₀** (direct) | 1144 | 426 | **203** | **193** | 300 | 473 | 839 |
| bore-H | 0.01003 | 0.00984 | 0.00869 | 0.00566 | 0.00433 | 0.00388 | 0.00369 |

✅ Decomposition closes within **0.8 points everywhere**, and η_plasma is computed
independently from plasma-region field energy — (σ/ε₀)·E_elec[90]/P_inc — not by
subtracting the wall from the total. That is what makes closure a test.

### 🔑 THE FLOOR: 60.5% over a 1000× range of σ

> **Across three orders of magnitude in the one quantity nobody has measured,
> delivered power never falls below 60.5%.** There is no value of σ in the
> plausible range that produces a coupling crisis.

🔴 **My driver's own verdict was WRONG and is fixed.** It reported "FLANK, peak at
σ = 300" because its plateau-detector assumed a single maximum. **η(σ) is
U-SHAPED** — high at both ends, minimum at σ ≈ 3–10. A unimodal detector on a
bimodal curve is the same class of error as R71's regression returning exponents
for a relationship that does not exist.

### 🔑 η IS A PURE MATCH CURVE. The plasma is never the problem.

🔢 **η_plasma / η_total ≥ 96.8% at EVERY σ**, and wall loss never exceeds 2.4%.
**Whatever enters the cavity reaches the plasma.** η is therefore not measuring
absorption at all — it is measuring how much power gets *in*, i.e. the match.

That is confirmed directly by Q₀ = ωU/P_abs, which needs no reciprocal difference
and no resonance model: **Q₀ has a MINIMUM of 193 at σ = 10**, rising to 1144 at
σ = 0.3 and 839 at σ = 300. Internal loss peaks exactly where η is worst.

### 🔑 THE BRANCH IS SETTLED: the cavity is UNDERCOUPLED everywhere

η = 4β/(1+β)² is symmetric in β ↔ 1/β, so η alone cannot say which side. **Q_ext =
Q₀/β does**, because it must be a property of the coupler and not of the load:

| branch | Q_ext across σ = 0.3 → 300 | verdict |
|---|---|---|
| β < 1 (undercoupled) | **1318, 955, 890, 828, 800, 787, 904** | ✅ constant to ±15% over 1000× in σ |
| β > 1 (overcoupled) | 993, 190, 46, 45, 112, 284, 778 | 🔴 swings 22× — not a coupler property |

✅ **And ~850 agrees with R70's independently measured Q_ext = 1,084 for this
exact sc06 loop.** Two unrelated routes to the same number.

🔑 **β = 0.87 → 0.45 → 0.23 → 0.23 → 0.38 → 0.60 → 0.93.** The cavity is
undercoupled at every plausible σ, **worst matched precisely where the plasma
absorbs best.** More coupling is still wanted — but the reason has changed. The
deficit was never that the plasma is hard to reach.

✅ **R67's own low-σ arithmetic is corroborated**: it predicted that at σ ≈ 0.3 the
already-measured loop is critically coupled. Measured β = 0.87, η = 99.5%.

### What R74 does to R67

- 🔽 **DEMOTED as a gate on the design.** "Does this coupler work?" no longer
  depends on σ: the answer is yes across 1000×, floor 60.5%.
- 🔼 **STILL BINDING on any quoted number.** 78.8% is one point on a 60–100%
  curve. **Quote the floor, not the point**, until σ is pinned (audit A5).
- ⚠️ **The worst case is in the MIDDLE of the plausible range, not at an
  extreme** — σ = 3–10, between MP-AES class and ICP class. It cannot be
  dismissed as an unphysical limit.

### ✅ Mechanism for the frequency drift, and a coherence check

f @ max η rises monotonically **2.3972 → 2.4136, 16.4 MHz**, while bore-H falls
**2.7×** (0.01003 → 0.00369). Both are the same effect: with `Permittivity = 1.0`
the plasma adds loss and no reactance, so at low σ it barely moves the frequency;
as σ rises the skin depth collapses and field is excluded from the plasma volume,
which is electrically like removing dielectric — the frequency rises and the bore
empties. Two independent observables telling one story.

### ⚠️ What this does NOT establish

- One geometry (sc06 on the barrel), **one mesh density, order 1**. No convergence
  study on η.
- The plasma **region SHAPE** (`baselines plasma.region`, the R12 toroid) is as
  assumed as its conductivity was. This sweep moved σ and nothing else.
- Q_ext drifts 1318 → 787 across the sweep. Expected — the mode structure genuinely
  changes (bore-H moves 2.7×) — but it is drift, not a constant.
- σ = 0.3 is **not** the transparent limit: at 2.4 GHz, σ/(ωε₀) = 2.25 there, still
  a loss tangent above 1. The true σ → 0 overcoupled collapse is below the sweep.

### ✅ Settled en route, from data already on disk: R73's mode-identity caveat

R73 warned its four cases might not share a resonance (f@max spanned 2.4088–2.4228).
Comparing the η-maximum against the **stored-energy** maximum:

| case | f@η-max | f@U-max | Δ | bore-H | U (nJ) |
|---|---:|---:|---:|---:|---:|
| barrel | 2.4102 | 2.4100 | 0.2 MHz | 0.00433 | 7.87 |
| cap70 | 2.4088 | 2.4086 | 0.2 MHz | 0.00401 | 7.17 |
| cap50 | 2.4154 | 2.4152 | 0.2 MHz | 0.00404 | 4.46 |
| **cap30** | 2.4228 | 2.4178 | **5.0 MHz** | 0.00535 | **1.62** |

✅ Barrel/cap70/cap50 agree to **one sample** and their bore-H agrees within 8% —
same mode, and the η maximum *is* the resonance. **R73's ratios among those three
are safe.** 🔴 **cap30 is the sole exception**, its η-max 5 MHz off its own
resonance with 4.9× less stored energy — consistent with the shorted-turn
mechanism, since it barely has a resonance to sit on. It is also the case whose
number matters least. ⚠️ Do not compare these to R70's *unlit* discriminator
(0.019–0.021); lit values run ~5× lower because the plasma screens the bore.

| 121 | ✅ **R74 ANSWERED — η(σ) is U-SHAPED with a FLOOR of 60.5%; the design survives a 1000× error in σ** | One hash-pinned mesh (`wbarrel.msh`, md5 ca8ca503), only conductivity moved; **σ=30 reproduced R73 exactly (79.3% @ 2.4102) as a known-answer case inside the sweep**. 🔑 **η = 99.5 / 85.3 / 60.5 / 61.2 / 79.3 / 93.8 / 99.9% at σ = 0.3→300 — U-shaped, minimum at σ≈3–10, FLOOR 60.5% over 1000×.** No σ in the plausible range produces a coupling crisis. 🔴 **My driver's own verdict was wrong** ("FLANK, peak at 300"): a unimodal plateau-detector on a bimodal curve, same class as R71's regression. 🔑 **η is a pure MATCH curve — η_plasma/η_total ≥ 96.8% everywhere, wall ≤ 2.4%: whatever enters reaches the plasma.** Confirmed by **Q₀ (direct, no denominator) bottoming at 193 @ σ=10** — loss peaks where η is worst. 🔑 **BRANCH SETTLED: undercoupled everywhere.** Q_ext = Q₀/β is **constant to ±15% (787–1318) on the β<1 branch but swings 22× on β>1**, and ~850 matches R70's independent 1,084 for this same loop. **β = 0.87→0.23→0.93: worst matched exactly where the plasma absorbs best.** ✅ R67's own low-σ prediction corroborated (β=0.87 at σ=0.3). **R67 DEMOTED as a design gate, still binding on any quoted number — quote the floor, not the point.** ⚠️ Worst case sits in the MIDDLE of the plausible range (σ=3–10), not at an extreme. ✅ Also settled from disk: R73's mode caveat — barrel/cap70/cap50 share a mode to one sample, **cap30 alone is off-resonance by 5 MHz** |

## 2026-08-18 — 🔴 HARNESS TRAP: the watcher matched its own wrapper, because I made the regex text identical to the argv text

R74's job finished cleanly with `EXIT=0`. **The watcher kept running anyway**, and
would have sat until its 7,800 s ceiling before reporting a spurious OVERRUN on a
job that had already succeeded.

**Mechanism, and it is the self-match trap wearing a new face.** The standing rule
is that a `pgrep`-style pattern must not appear unbracketed in the same command
block, because the harness wrapper shell carries the whole block in its argv.
`watchjob.py` brackets the first character itself, so the caller obfuscates the
token instead. I passed:

```
'rig_si"gma.py"'          # ← the single quotes are the bug
```

The single quotes stopped the shell from removing the inner double quotes, so the
child received the literal pattern `rig_si"gma.py"` — which never matches a real
process — **and the wrapper's own argv contained that same text**, which the
derived regex `[r]ig_si"gma.py"` matches perfectly. The watcher therefore saw
exactly one "live process": itself. Dropping the single quotes is the whole fix —
`rig_si"gma.py"` unquoted reaches argv as the clean `rig_sigma.py` while the
wrapper's text keeps the quotes and no longer matches.

🔑 **The generalisation, which the existing rule does not cover:** bracketing only
defeats self-match when the *regex text* and the *argv text* differ. Obfuscating
the token in a way that survives into the pattern itself re-synchronises them and
restores the bug at full strength. **A detector must not be spelled the same way
as the thing it is looking through.**

⚠️ Note what did *not* save this: the job's real completion signal (`^EXIT=` in the
log, process gone) was present and correct the whole time. The sentinel logic is
gated on "no matching process", and the process check was the part that lied. The
R73 fix made the process authoritative over the sentinel; **this shows the
authority has to be earned by a pattern that cannot match the watcher.**

✅ Killed by exact-argv selection, per the standing rule — dry run listed one
candidate (`python3 -u watchjob.py …`), killed by PID, calling shell survived.

## 2026-08-18 — ✅ R75: THE TUNER QUESTION IS THE σ QUESTION AGAIN. ~23 MHz of settable range, and essentially zero dynamic range

Asked directly by the user off the back of R74's 16.4 MHz drift. Answered from
the seven η(f) curves R74 already left on disk — **no new solve** — because the
question is about the shape of those curves, not about a new configuration.

### 🔑 "16.4 MHz" is not an answer. Two things have to be added before it means anything

1. **MHz is meaningless without the linewidth.** Lit, Q_L = 156–612 and the
   linewidth is **3.9–15.4 MHz**, so 16.4 MHz of drift is ≈ 1 linewidth. Unlit,
   Q_L ≈ 18,000 and the linewidth is **0.13 MHz** — the same drift is 120
   linewidths. **The identical number is trivial in one state and hopeless in the
   other.**
2. **The design question is not "how many MHz" but "what does not tuning cost".**
   Park the source at one fixed frequency, take the worst σ, read the delivered
   power. That is acceptable or it is not. A range in MHz is neither.

### The measurement: minimax over a fixed frequency

For each admitted σ window, the single frequency maximising the **worst-case** η
across that window, against perfect per-σ tracking:

| admitted σ | drift | in linewidths | tuned | best fixed f | **cost of not tuning** |
|---|---:|---:|---:|---:|---:|
| 1000× (0.3–300) | 16.4 MHz | 4.2 | 60.5% | 2.4040 | 🔴 **52.0 pts** |
| 100× (1–100) | 15.2 | 1.9 | 60.5% | 2.4046 | 40.9 pts |
| 30× (3–100) | 12.8 | 1.6 | 60.5% | 2.4068 | 28.6 pts |
| 10× (10–100) | 5.6 | 0.7 | 61.2% | 2.4092 | 5.4 pts |
| **~3× (10–30)** | 3.4 | 0.3 | 61.2% | 2.4072 | ✅ **0.2 pts** |

> 🔑 **The cost of having no tuner falls from 52 points to 0.2 points as σ is
> pinned from 1000× to 3×. You do not need a tuner; you need to KNOW σ.** Same
> conclusion R74 reached from the other direction, and the same audit item (A5).

### ✅ Band placement, with the offset applied

⚠️ Everything above is **order-1 raw**, where Δf is valid and absolute placement
is not. A band-placement claim is an absolute claim, so it gets `offset.te011`:

🔢 raw **2.3972–2.4136** → corrected **2.4217–2.4381 GHz**. ✅ **Inside ISM
2.400–2.500 with 22 MHz below and 62 MHz above** — the amplifier has **6× more
range than the plasma uncertainty needs**. ⚠️ The offset was measured on the
design geometry, not on `wbarrel` with sc06's loop, and R38 flags it
geometry-dependent; treat placement as ~5 MHz accurate, which does not move the
verdict.

### 🔑 Three different specs were hiding inside the word "range"

| | what it needs | verdict |
|---|---|---|
| **1. One fixed frequency for all units**, no calibration | to cover the full σ bracket | 🔴 **52-point loss.** Not viable while σ is unpinned |
| **2. Set once at commissioning**, per instrument | **~23 MHz of settable range** (16.4 σ + 5.1 machining + 1.5 model), **no dynamic tracking** | ✅ **This is what the design needs.** Peak-find once, lock, done |
| **3. Track σ during operation** (sample aspiration loads the plasma) | sized by RUNTIME VARIATION, not a-priori uncertainty | ✅ 0.2 pts at a 3× swing, 5.4 pts at 10× |

> ✅ **The "no tuner, no moving parts" constraint SURVIVES.** A mechanical tuner
> was never the thing at issue — a frequency-agile solid-state source already
> covers 23 MHz inside a 100 MHz band. **Build-time uncertainty is not a tuner;
> it is a calibration step.**

### ⚠️ σ is not the whole budget, and machining is not small

| MHz | contributor | kind |
|---:|---|---|
| 16.4 | plasma σ, 1000× bracket (R74, measured) | lit |
| 3.4 | plasma σ pinned to ~3× (R74, measured) | lit |
| **5.1** | machining, `cav.radius` ±0.2 mm × −12.86 MHz/mm | **both** |
| 1.5 | mesh-to-mesh scatter — a MODEL error, not a real one | model |
| 24.0 | cold → lit ignition step (R10, **different geometry**) | transient |

🔑 **Machining contributes 5.1 MHz — larger than the σ drift over any realistic
window.** It is a fixed offset per unit, absorbed at build time by cutting the
cavity to length, which is what `cav.shim` already does.

### 🔴 The transient, not the drift, is the unsolved problem

Unlit Q_L ≈ 18,000 (linewidth **0.13 MHz**); lit Q_L ≈ 219 (**11 MHz**) — **85×
wider**. The amplifier must *find* a 0.13 MHz target to deposit ignition power,
then follow a resonance that moves tens of MHz and broadens 85× within the
ignition timescale. **That is an ACQUISITION and BANDWIDTH spec, not a range
spec**, and it is README open risk 5, untouched by this analysis.

⚠️ **Not measured here: the cold resonance of THIS geometry.** It needs a
different sweep — R74's 0.2 MHz step walks straight over a 0.13 MHz linewidth,
which is exactly `reproducibility.linewidth_step_bias`. Coarse-locate then
fine-resolve, or the answer will be confidently wrong.

| 122 | ✅ **R75 — the tuner question is the σ question again: ~23 MHz of SETTABLE range, essentially ZERO dynamic range** | Answered from R74's seven η(f) curves, **no new solve**. 🔑 **"16.4 MHz" is not an answer**: lit linewidth is 3.9–15.4 MHz so the drift is ≈1 linewidth, unlit it is 0.13 MHz so the same drift is 120 — and the real question is what NOT tuning costs, not how many MHz. **Minimax over a fixed frequency: cost of no tuner = 52.0 pts over a 1000× σ bracket, 5.4 pts at 10×, and 0.2 pts at 3×.** 🔑 **You do not need a tuner; you need to know σ** (AUDIT A5) — R74's conclusion from the other side. ✅ **Band placement with `offset.te011` applied: 2.4217–2.4381 GHz, inside ISM with 22/62 MHz margin — 6× more range than needed.** 🔑 **Three specs were hiding in the word "range"**: one-fixed-frequency-for-all 🔴 loses 52 pts; **set-once-at-commissioning needs ~23 MHz and no tracking ✅ (this is the design)**; runtime tracking costs ≤5 pts. ✅ **"No tuner, no moving parts" SURVIVES — build-time uncertainty is a calibration step, not a tuner.** ⚠️ **Machining is 5.1 MHz, larger than the σ drift over any realistic window** — but a fixed per-unit offset, absorbed by `cav.shim`. 🔴 **The TRANSIENT is the unsolved problem**: unlit linewidth 0.13 MHz vs lit 11 MHz, **85× broadening** — an acquisition/bandwidth spec, not a range spec |

## 2026-08-18 — ✅ HARNESS: `watchjob.py --uid` removes the self-match bug class instead of respelling it

The user's fix for the watcher trap logged above: *"just use a unique arg. Add
`--uid`, give it a random value on start, then locate in ps."* Right, and it is
strictly better than every previous attempt, for a reason worth recording.

**Every earlier fix was a way of SPELLING the job's name so the watcher could not
read its own command line**, and each failed differently:

| pattern | failure |
|---|---|
| `scatter.py` | matches the watcher's own argv → never exits |
| `[s]catter.py` | works until the plain token appears anywhere else in the block |
| `rig_si"gma.py"` | wrapped in single quotes, so the shell did **not** strip them: the child got a pattern matching no real process, **and the wrapper's argv held that same literal text** → matched itself, and reported a finished job as running |

🔑 **The failures are all one failure: bracketing only defeats self-match when the
REGEX text and the ARGV text differ.** Every fix is one careless quote away from
re-synchronising them. That is a bug class, not a bug.

**`--uid` removes the class.** Two properties, and the second is the one that
matters:

1. the token is **random**, so it cannot collide with anything incidental;
2. 🔑 the watcher **excludes its own process ancestry** — itself, its wrapper
   shell, and that shell's parents, walked via `/proc/<pid>/stat`. That is
   exactly the set of processes carrying the watcher's command text, so
   **self-match becomes structurally impossible rather than carefully avoided.**

The job's own wrapper shell also carries the token, deliberately: it is alive for
as long as the job is, so detection survives the job re-execing or shelling out
to `mpiexec`.

```
WJ=$(python3 watchjob.py --newuid)
python3 -u sweep.py --uid $WJ > job.log 2>&1; echo "EXIT=$?" >> job.log
python3 -u watchjob.py job.log 2600 --uid $WJ --sentinel '^EXIT='
```

✅ **Verified by the falsification test, not by it working once.** The decisive
case is the *negative* one, because "it found the job" does not prove it was not
also finding itself:

- **Test A — no job running at all.** The watcher's own argv contains the token.
  It reported `EXITED, no matching process` in 6 s. **Self-blindness proven.**
- **Test B — a real 25 s job carrying the token.** Stayed alive, then reported
  `COMPLETED after 24s (sentinel matched, no process alive)`.

Passing both `--uid` and a `PROC_PATTERN` is now a hard error: two detectors
disagreeing is worse than one.

## 2026-08-18 — ✅ R76: THE COLD RESONANCE, MEASURED. 2.39745 GHz raw, and a strongly-coupled INTERLOPER sits 33 MHz above it

R75 flagged this as the missing number: every lit result sits on `wbarrel.msh`,
but the unlit resonance of that same geometry had never been measured, so the
cold → lit excursion was unknown for the thing actually simulated. R10's
+16–24 MHz is a different geometry.

Same hash-pinned mesh, same config builder, **one key different from the lit
runs** — the plasma attribute gets air instead of a conductor, i.e. literally the
lit material with `Conductivity` removed, asserted at config-write time. So the
cold–lit difference cannot be a configuration difference.

### 🔴 FIRST ATTEMPT PICKED THE WRONG MODE, and the rule it broke is this project's own

The driver selected the peak by **`argmax(stored energy)`**. That chose a
resonance at **2.4304** — and reported its β (0.17) and a cold → lit excursion of
the **wrong sign** (−20.2 MHz). Every number in that first run was for a mode
nobody wanted.

🔑 **`argmax(U)` is not a mode identifier. It selects the mode the LOOP COUPLES
BEST TO**, because stored energy at fixed drive is set by coupling. That is
exactly the standing rule — *identify a mode by where its energy is, never by a
ratio or a global scalar that can be large for the wrong reason* — broken in a
new spelling. **`argmin|S11|` and `argmax(U)` are the same error.** Selection is
now by **bore magnetic fraction**, and the driver prints every candidate so a
mis-pick is visible instead of silent.

⚠️ Also fixed: FWHM and step are in GHz, and the report printed `1e3×` labelled
**kHz**. The first output read "FWHM 0.2 kHz" for 0.166 MHz and "step 0.05 kHz"
for 0.05 MHz. The solves were correct; only the labels lied — which is worse,
because a label is what gets quoted later.

### The band, and what is in it

| f raw | U/U_max | bore-H | bore-E | η | Q₀ | identification |
|---|---:|---:|---:|---:|---:|---|
| 2.3695 | 0.17 | 0.0006 | **0.0239** | 5.5% | 23,186 | **TM₀₂₀** — bore-E dominant; +`offset.tm020` → 2.3896 vs baseline 2.3955 |
| **2.3975** | 0.51 | **0.0101** | 0.0003 | 11.1% | **35,961** | ✅ **TE₀₁₁** — bore-H dominant, Q₀ matches the expected ~36,000 (45,728 × R70's −21%) |
| 2.4304 | **1.00** | 0.0040 | 0.0016 | **46.5%** | 17,097 | 🔴 **UNIDENTIFIED.** Not TM₁₁₁ (`tm111.f_filtered` = 2.3509) and not TM₀₂₀ |

### ✅ The measurement, coarse then fine, with no step bias

| stage | f GHz | FWHM | Q_L | Q₀ | β | pts/FWHM |
|---|---:|---:|---:|---:|---:|---:|
| coarse (50 kHz) | 2.397450 | 2.339 MHz | 1,025 | 35,961 | 34.09 | 46.8 |
| fine (93.6 kHz) | 2.397450 | 2.341 MHz | 1,024 | 35,961 | 34.11 | 25.0 |

✅ **Q_L agrees to 0.1% and Q₀ to 5 figures.** The coarse step already resolved
this resonance, so there is no step bias to correct — the opposite of the
narrow-band case that cost this project a Q measurement, and the reason for
running both rather than assuming either.

🔑 **Q_ext = Q₀/β = 35,961/34.11 = 1,054, against R70's independently measured
1,084 — 2.8%.** Two unrelated routes, and it settles the branch: **cold β = 34.1,
badly OVERCOUPLED**, confirming R70's "β = 33 unlit".

### ✅ R73's deferred caveat is now CLOSED BY MEASUREMENT, not waived

R73 declined mode identification because η needs none, leaving open *whether the
plasma is heated in the intended TE₀₁₁ geometry*. Enumerating every lit resonance
the same way answers it:

| σ | η-max f | bore-H | vs cold TE₀₁₁ |
|---|---:|---:|---:|
| cold | 2.3975 | 0.01006 | — |
| 0.3 | 2.3974 | 0.01004 | −0.1 MHz |
| 3 | 2.3996 | 0.00869 | +2.1 |
| 30 | **2.4100** | 0.00433 | **+12.5** |
| 300 | 2.4136 | 0.00369 | +16.1 |

✅ **η-max tracked TE₀₁₁ in every lit case** — same bore-H signature, monotonic in
σ, and the interloper collapses from η 46.5% cold to 16.3% at σ = 30 because the
plasma damps it while TE₀₁₁ becomes the absorber. **R73/R74's 78.8% and 60.5%
floor are TE₀₁₁ numbers.** The bore-H fall 0.0101 → 0.0037 is the plasma screening
the bore, as R74 read it.

### 🔴 THE INTERLOPER IS AN IGNITION HAZARD

**Cold — which IS the ignition state — the cavity's strongest response is not
TE₀₁₁.** The unidentified mode at 2.4304 takes **46.5%** of input power against
TE₀₁₁'s **11.1%**, a 4.2× advantage, 33 MHz away.

> 🔑 **An amplifier that cold-starts by peak-finding on reflected power will lock
> onto the wrong mode**, deposit four times more power into a resonance that does
> not drive the plasma torus, and never light. **Ignition frequency must be
> commanded from the design value, not searched for.**

⚠️ Held against that: the interloper has **4.7× more bore-E** than TE₀₁₁ (0.00158
vs 0.00034), and bore E-field is what breaks gas down. It may be an ignition
*opportunity* rather than purely a hazard. **Not resolved here** — the design's
ignition mechanism is a capacitive electrode, not mode E-field. Identifying this
mode is now the open question.

### 🔑 The number R75 asked for

🔢 **cold 2.39745 → lit 2.41020 (σ=30) = +12.8 MHz, monotonic, = 5.4 COLD
linewidths and 1.2 lit linewidths.** Full range to σ=300 is +16.2 MHz.

**With `offset.te011` applied: cold floor 2.42199, lit ceiling 2.43814 GHz** —
22.0 MHz above the 2.400 LDMOS/ISM floor, 61.9 MHz below 2.500.

⚠️ **R75's "0.13 MHz cold linewidth" was for the DESIGN coupler (β = 1.46) and is
wrong for this geometry.** sc06's β = 34 broadens the cold resonance to
**2.34 MHz** — 18× easier to acquire. **The acquisition worry was real but
attached to the wrong coupler.** The trade is now explicit: sc06 gives an easy
2.34 MHz cold target at only **11.1%** cold power transfer; the design coupler
gives ~98% into a 0.13 MHz needle. **Overcoupling buys ignition ACQUISITION at
the price of ignition POWER** — whether 11% of the amplifier is enough to light
is an ignition-study question, not an EM one.

| 123 | ✅ **R76 — cold resonance measured: TE₀₁₁ at 2.39745 GHz raw, +12.8 MHz to lit; and a strongly-coupled INTERLOPER 33 MHz above it** | Same frozen mesh, lit config with `Conductivity` removed and asserted absent. 🔴 **First attempt picked the WRONG MODE**: `argmax(stored energy)` chose the best-COUPLED resonance (η 46.5%) over TE₀₁₁ (η 11.1%) and reported an excursion of the **wrong sign** — the project's own rule broken in a new spelling, since **argmax(U) and argmin\|S11\| are the same error**. Selection now by bore-H, all candidates printed. ⚠️ Units bug: GHz printed as kHz, so "FWHM 0.2 kHz" meant 0.166 MHz. ✅ **Three modes found: TM₀₂₀ 2.3695 (bore-E), TE₀₁₁ 2.3975 (bore-H, Q₀ 35,961 as predicted), and an UNIDENTIFIED one at 2.4304** — not TM₁₁₁, not TM₀₂₀. ✅ **Coarse and fine agree: Q_L 1,025 vs 1,024, Q₀ identical, NO step bias**; **β = 34.1 ⟹ Q_ext = 1,054 vs R70's independent 1,084 (2.8%)**. ✅ **R73's mode caveat CLOSED BY MEASUREMENT: η-max tracked TE₀₁₁ at every σ** — the interloper collapses 46.5% → 16.3% when lit. 🔴 **IGNITION HAZARD: cold, the interloper beats TE₀₁₁ 4.2× on absorbed power — a peak-finding cold start locks onto the wrong mode. Command the ignition frequency, do not search for it.** ⚠️ But it has 4.7× more bore-E, so it may be an ignition opportunity — unresolved. 🔑 **cold floor 2.42199, lit ceiling 2.43814 GHz (offset applied): 22.0 MHz above 2.400, 61.9 below 2.500.** ⚠️ **R75's 0.13 MHz cold linewidth was the DESIGN coupler; sc06 gives 2.34 MHz** — overcoupling buys acquisition (18× easier) at the price of cold power transfer (11.1%) |

## 2026-08-18 — 🔴 R77 RETRACTED, and R78/R79: the groove depth decides whether TE₀₁₁ exists as a pure mode

### 🔴 First, the retraction

R77 identified the 2.4382 interloper as TM₁₁₁ by elimination: fingerprint p = 1,
χ_eff 3.846 = χ′₀₁ = χ₁₁ to 0.4%, which at p = 1 admits only TE₀₁₁ and TM₁₁₁, and
TE₀₁₁ was separately identified. **The elimination was invalid.** I ruled TM₁₁₁ out
using `tm111.f_filtered` = 2.35094 — a baseline measured on a *different geometry*
— instead of measuring it, and then chose a band (2.360–2.440) that excluded the
place that baseline pointed at.

✅ **R77b looked there. TM₁₁₁ is at 2.3431 GHz**, DFT bin2 = 0.1774 = **38.6× the
m=0 floor** against R47's 57.7×, 52.8 MHz below TE₀₁₁. So TM₁₁₁ and TE₀₁₁ are both
accounted for and **the 2.4382 mode remains unidentified.**

🔑 **The lesson is not "check your bands."** It is that an elimination argument
imports the reliability of whatever it eliminated *with*. I used a measured number
from another geometry as though it were a fact about this one — the same error as
quoting `Q_ext = 165` outside its domain, and the same error as simulating a mode
filter the design had dropped.

### R78: the interloper is attached to the FILTER, not to the cavity

Same mesh, quartz annuli in and out, one meshsweep call:

| mode | quartz 3 mm | bare | shift | η cold |
|---|---:|---:|---:|---:|
| TE₀₁₁ | 2.3960 | 2.3979 | **+2.0** | 14.6% → 9.3% |
| TM₁₁₁ | 2.3430 | 2.4247 | +81.6 | 26.6% → 99.5% |
| TM₀₂₀ | 2.3742 | 2.4448 | +70.5 | 3.0% → 9.3% |
| interloper | 2.4383 | 2.3034 | **−134.9** | 7.0% → 22.5% |

🔑 **The interloper moves 135 MHz where TE₀₁₁ moves 2.0** — 67×. Its frequency is
set by the annuli. ✅ And the table is the mode filter's whole job in one view: it
detunes every TM mode by 70–135 MHz and leaves TE₀₁₁ alone, because the annuli sit
where TM modes have E_z and TE₀₁₁ has E_φ = 0.

⚠️ **Bare is a control, not an option** — the user's correction. A circular cavity
with no filtering reverts to the χ′₀₁ = χ₁₁ degeneracy, and bare TE₀₁₁ duly shows
azimuthal bin1 = 0.2443 = **53× the m=0 floor** (R47 measured 23× independently).
The choice is quartz *or* groove; "bare is worse" decides nothing.

### 🔑 R79: at 15 mm the groove puts TM₁₁₁ ON TOP OF TE₀₁₁

Three filters, one meshsweep call, size-factor 1.00, band 2.35–2.49:

| | f raw | pm/pe | Q₀ | η | bin1 | bin2 |
|---|---:|---:|---:|---:|---:|---:|
| **quartz 3 mm** | 2.3960 | **27.5** | 37,059 | 14.6% | 0.026 | 0.029 |
| | 2.4383 | 2.8 | 17,235 | 7.0% | 0.037 | 0.050 |
| | 2.3742 (TM₀₂₀) | 0.0 | 23,378 | 3.0% | 0.004 | 0.009 |
| **groove 15 mm** | 2.4046 | 9.3 | 18,027 | **38.0%** | **0.125** | **0.148** |
| | 2.4081 | 5.7 | 13,384 | **67.3%** | **0.120** | **0.154** |
| | 2.3901 (TM₀₂₀) | 0.1 | 13,409 | **0.7%** | 0.021 | 0.026 |
| **groove λ/4** | 2.4086 | **58.4** | 31,879 | 15.2% | 0.079 | 0.065 |
| | 2.3969 | 2.2 | 7,006 | 5.1% | 0.076 | 0.140 |

🔴 **At 15 mm there is no pure TE₀₁₁.** Two modes 3.5 MHz apart with nearly
identical azimuthal content (bin1 0.120/0.125, bin2 0.148/0.154 — **26–33× the m=0
floor**), intermediate pm/pe, and Q₀ down 45% from bare. That is an **avoided
crossing**: the groove has swept TM₁₁₁ onto TE₀₁₁ and they have hybridised. **67.3%
of cold power goes into a mixed, m=1-contaminated state.**

> 🔑 AMIP's entire thesis is that symmetry comes from the boundary conditions, so
> there is no loop to have a phase gradient around. **A hybridised operating mode
> at 30× the m=0 floor is not that.** Depth is not a Q optimisation; it decides
> whether the operating mode exists.

✅ **λ/4 gives the PUREST TE₀₁₁ of all three — pm/pe 58.4 against the quartz's
27.5**, Q₀ 31,879, and it wins its band 15.2% vs 5.1%. Consistent with R54's
independently measured purity gain.

🔑 **Generalisation, and it supersedes my own framing of R59's constraints.** As
depth sweeps, the TM modes traverse continuously from below TE₀₁₁ to above it — so
they *pass through it*. R79 has now located that crossing near **15 mm**. The
usable region is on the far side, and R54's estimated pole at 20–23 mm sits
between the crossing and the clean case. **A depth ladder must bracket the
crossing, not just the pole.**

### 🔑 THE TM-IGNITION QUESTION, RE-ASKED WITH THE RIGHT INSTRUMENT

The user's history: TM ignition was attempted, judged impossible, and the
capacitive electrode was introduced to compensate; later TE operation was judged
impossible, iris and waveguide architectures were explored, and **that** verdict
turned out to be an artefact of measuring Q. The parallel demanded a re-check.

✅ **First, the premise was configuration-dependent, and the configuration
changed.** `TM₀₂₀ is 10 MHz below the band floor and unreachable` is true of the
**quartz** cavity and only of it:

| filter | TM₀₂₀ corrected | vs the 2.400 floor |
|---|---:|---:|
| quartz 3 mm | 2.3943 | −5.7 MHz — unreachable |
| bare | 2.4649 | +64.9 — in band |
| **groove 15 mm** | **2.4102** | **+11.0 — in band** |
| groove λ/4 | 2.5200 | +120 — above the top |

🔴 **But in band does NOT mean drivable. Measured in η: TM₀₂₀ takes 0.7%.**
Consistent with R60's independently measured 18.3 dB suppression at the
operational tilt. **The re-examination confirms the original verdict rather than
overturning it** — this time in delivered power, with no denominator in it.

⚠️ Scope of that: it says TM ignition is unavailable **with a loop oriented for
TE₀₁₁**, which was always the trade. R60 showed a 45° tilt couples to both
families. It does not say TM ignition is impossible with a different coupler.

### ⚠️ Two harness bugs, opposite in sign, both mine

- `rel > 0.02` (R77) **could only silently drop** — it discarded TM₀₂₀ from a case
  and the matcher then paired it with the wrong mode, reporting df/dL = +49.6
  MHz/mm for a p = 0 mode.
- `meta.get("groove")` (R79) **could only fire** — the sidecar keeps geometry under
  `geometry_mm`, so it returned None for every case including the quartz one that
  never asked for a groove, and it killed a correct run after 18 minutes of good
  solve. **A check that cannot pass is not a safety net; it is a second way to lose
  the answer.** Verify an assertion against known-good data before trusting it.

| 124 | 🔴 **R77 RETRACTED; R78/R79 — the groove DEPTH decides whether TE₀₁₁ exists as a pure mode** | 🔴 **R77's elimination was invalid**: it ruled out TM₁₁₁ using a baseline from a DIFFERENT geometry, then chose a band excluding where that baseline pointed. ✅ **R77b found TM₁₁₁ at 2.3431 (bin2 38.6× floor), 52.8 MHz below TE₀₁₁** — so the 2.4382 mode is still unidentified. 🔑 **An elimination argument imports the reliability of what it eliminated with.** ✅ **R78: the interloper shifts 135 MHz when the quartz comes out against TE₀₁₁'s 2.0** — it is filter-attached; and the same table is the filter's whole job, detuning every TM mode 70–135 MHz while leaving TE₀₁₁ alone. 🔴 **R79: at a 15 mm groove there is NO pure TE₀₁₁** — two modes 3.5 MHz apart, azimuthal content 26–33× the m=0 floor, Q₀ −45%: **TM₁₁₁ has been swept onto TE₀₁₁ and hybridised, taking 67.3% of cold power into an m=1-contaminated state.** ✅ **λ/4 gives the purest TE₀₁₁ of all three (pm/pe 58.4 vs quartz 27.5)** and wins its band 15.2% vs 5.1%. 🔑 **The TM modes CROSS TE₀₁₁ as depth sweeps; the crossing is near 15 mm and R59 must bracket it, not just the pole.** ✅ **TM ignition re-asked in η: TM₀₂₀ IS in band with a 15 mm groove (2.4102) — its unreachability was the quartz's doing — but it takes only 0.7% of input power**, so the original verdict stands, now measured in watts rather than Q. ⚠️ Two harness bugs, opposite in sign: a threshold that could only drop silently, an assertion that could only fire |

## 2026-08-18 — 🔑 R59: the groove is a RESONATOR, not a detuner. 21 mm leaves TE₀₁₁ alone in the band, and no depth fixes azimuthal purity

Six depths at 3 mm width, one meshsweep, size-factor 1.00, band 2.34–2.54 GHz at
50 kHz. ✅ **Both tie points reproduce R79 to every digit** — 15.0 mm (pm/pe 9.3,
Q₀ 18,027, η 38.0%, bin1 0.1250) and 30.6 mm (pm/pe 58.4, Q₀ 31,879, η 15.2%,
bin1 0.0788). The ladder is trustworthy; two of its columns were not.

| depth | TE₀₁₁ f | pm/pe | Q₀ | η | bin1 | bin2 |
|---|---:|---:|---:|---:|---:|---:|
| 10.0 | 2.4072 | 9.6 | 35,083 | 18.3% | 0.0627 | 0.0026 |
| 15.0 | 2.4046 | 9.3 | **18,027** | 38.0% | 0.1250 | 0.1476 |
| **21.0** | 2.4050 | 49.0 | 33,424 | 11.6% | 0.0572 | 0.0279 |
| 26.0 | 2.4130 | 49.7 | **8,089** | 97.0% | 0.0383 | 0.1712 |
| 30.6 | 2.4086 | 58.4 | 31,879 | 15.2% | 0.0788 | 0.0646 |
| 36.0 | 2.4039 | 58.1 | 25,171 | 14.9% | 0.0902 | 0.0503 |
| *quartz 3 mm* | *2.3960* | *27.5* | *37,059* | *14.6%* | *0.0263* | *0.0287* |

### 🔴 Two bugs in my own driver, and correcting them changes the answer

🔴 **C5/C6 are VOID.** The TM₁₁₁ tracker took "the m=1 mode with the most stored
energy", which is a **different mode at each depth** — at 21 mm it grabbed 2.5297
(125 MHz above TE₀₁₁, near the top of the sweep), at 36 mm 2.5112. The separation
series −35.8 / +3.5 / +124.8 / −29.0 / −11.6 / +107.3 is mode-hopping, not
physics. **The three reported "crossings" and the whole tolerance table are
withdrawn.** A tracker that re-identifies its target every step measures nothing.

🔴 **C4 did not apply reachability** — the single idea the driver was built on. The
sweep runs to 2.565 corrected, 65 MHz past the LDMOS top, so modes the amplifier
cannot reach were scored as rivals. Recomputed against 2.400–2.500 corrected:

| depth | TE₀₁₁ η | in-band rivals | best rival | C4 |
|---|---:|---:|---:|---|
| 10 | 18.3% | 2 | 43.2% | 🔴 |
| 15 | 38.0% | 2 | 67.3% | 🔴 |
| **21** | 11.6% | **0** | **none** | ✅ |
| 26 | 97.0% | 3 | 41.2% | ✅ |
| 30.6 | 15.2% | 3 | 5.1% | ✅ |
| 36 | 14.9% | 4 | 58.8% | 🔴 |

### 🔑 THE MECHANISM: the groove adds its own lossy resonances

The ladder's real finding is not where TM₁₁₁ went. It is that **the slot resonates
on its own account and its modes sweep through the band with depth**:

| depth | the groove's own modes (f raw, Q₀) | where |
|---|---|---|
| 21.0 | 2.4994 (5,717) · 2.5205 (3,340) · 2.5297 (3,188) | ✅ above the band |
| 26.0 | 2.3840 (5,264) · 2.3971 (3,988) · **2.4130 (8,089)** · 2.4202 (5,558) | 🔴 **on TE₀₁₁** |
| 36.0 | 2.4469 (2,650) · 2.4505 (2,680) | 🔴 in the band |

🔑 **At 26 mm one of them lands on TE₀₁₁ and collapses it to Q₀ = 8,089** — and
*every* mode at that depth is lossy. That is not detuning; it is the slot eating
the cavity. R54's model of the groove as a shorted stub that pushes TM modes
around is incomplete: it is also a lossy resonator that must be parked somewhere.

✅ **21 mm parks them above the amplifier band** and leaves **TE₀₁₁ alone in
2.400–2.500 with no rival at all** — pm/pe 49.0 (1.8× quartz), Q₀ 33,424 (90% of
quartz). That is the best depth found, and my own verdict block missed it because
of the two bugs above.

⚠️ At 21 mm **TM₁₁₁ is unlocated**, not absent — it is not in the swept
2.34–2.54. Below 2.365 corrected it is unreachable and harmless, but "absent from
a window is not absent" has now cost this project three times (R54, R77, here).

### 🔴 C1 AND C3 FAIL AT EVERY DEPTH, and that is the durable result

**C1 azimuthal purity:** bin1 never gets below **0.0572** among viable depths,
against quartz's 0.0263. **C3 Q₀:** no depth reaches quartz's 37,059; the best is
35,083. Both are robust — TE₀₁₁ is tracked consistently by pm/pe throughout.

> 🔑 **The filter cannot fix azimuthal purity; the coupler owns it.** Quartz's own
> bin1 of 0.0263 is already **5.7× R54's design-loop floor of 0.0046**, and every
> groove depth is worse. R54 measured the groove beating quartz by +6.0% in Q with
> the design loop; scaled by sc06's −21% (R70) that predicts 38,438 against a
> measured 33,424. **The quartz's Q number transfers to sc06 and the groove's does
> not** — the groove is the more coupler-sensitive of the two.

| # | question | status |
|---|---|---|
| **R59** | groove DEPTH at 3 mm width | ✅ **CLOSED — 21 mm, TE₀₁₁ alone in band; C1/C3 unfixable by depth** |
| **R80** | groove WIDTH at 21 mm depth — does Z₀ ∝ w park the parasitic family further above the band, or drag it in? | open — running |

| 125 | 🔑 **R59 — the groove is a RESONATOR not a detuner; 21 mm leaves TE₀₁₁ alone in the band; no depth fixes azimuthal purity** | Six depths, one meshsweep, **both tie points reproduce R79 exactly**. 🔴 **Two bugs in my own driver**: the TM₁₁₁ tracker re-identified its target at every depth (the +125/−29/+107 separation series is mode-hopping — **C5, C6 and the three "crossings" are WITHDRAWN**), and **C4 never applied reachability** despite that being the driver's whole framing. 🔑 **THE MECHANISM: the slot resonates on its own account** — a family of Q₀ 2,650–5,717 modes that sweeps through the band with depth; **at 26 mm one lands on TE₀₁₁ and collapses it to Q₀ 8,089** with every mode at that depth lossy. R54's shorted-stub picture is incomplete. ✅ **21 mm parks the parasitic family above the band and leaves TE₀₁₁ ALONE in 2.400–2.500** — pm/pe 49.0, Q₀ 33,424 (90% of quartz) — the best depth found, which the buggy verdict block missed. 🔴 **C1 and C3 fail at EVERY depth**: bin1 ≥ 0.0572 vs quartz 0.0263, Q₀ ≤ 35,083 vs 37,059. **The filter cannot fix azimuthal purity — the coupler owns it**, and quartz's own bin1 is already 5.7× R54's design-loop floor. ⚠️ TM₁₁₁ at 21 mm is UNLOCATED, not absent |

## 2026-08-19 — ✅ R81: the slot modes IDENTIFIED BY MEASUREMENT, the 26 mm collapse is hybridisation, and 15 mm was never a measurement

Two inferences had already failed on this question — R77 called the interloper
TM₁₁₁ by an elimination that imported a baseline from another geometry, R78
proposed a dielectric resonance that its own control killed. R81 stops inferring:
the groove gets its own mesh attribute (`--tag-groove`, TAG 13) and Energy index
80, and every mode reports **what fraction of its energy is inside the slot**.

⚠️ `groove_frac` = `p_elec[80] + p_mag[80]`, each a fraction of its own total, so
the scale is 0–2. Halve it for the share of total energy.

| depth | TE₀₁₁-like | in slot | the other modes |
|---|---|---:|---|
| 15 mm | pm/pe 25.8, Q₀ 31,238 | **0.6%** | 5%, 6% |
| 21 mm | pm/pe 47.8, Q₀ 32,662 | **0.6%** | 17, 52, 44, 44, 31, 35% |
| 26 mm | pm/pe 50.2, Q₀ **7,572** | **15.7%** | 31, 37, 22, 29, 52, 42, 24, 24% |

🔑 **TE₀₁₁ is a cavity mode the groove perturbs from OUTSIDE** — 0.6% of its
energy in the slot at both good depths. 🔑 **The family at 17–52% are modes of the
SLOT**, not of the cavity. That is measured, not inferred, and it is the first
thing said about these modes that rests on where their energy is rather than on
what they are not.

### ✅ The 26 mm collapse is HYBRIDISATION — the question R81 was built to settle

At 26 mm the TE₀₁₁-like mode carries **15.7% of its energy in the groove, 26× its
value at 21 mm**, while keeping pm/pe 50.2. Both partners carry substantial slot
energy and substantial bore-H. **TE₀₁₁ partially moves INTO the slot** — it is not
a separate slot mode swamping it. Those were the two candidate failures and they
have different fixes; this one says the groove and the operating mode become the
same object at that depth.

### 🔴 15 mm WAS NEVER A MEASUREMENT — and R59's reading of it is withdrawn

Tagging changes the mesh by **0.16%** (143,395 → 143,623 tets) and nothing else —
same geometry, same air material, bookkeeping only. Used as a sensitivity probe:

| depth | pm/pe | Q₀ | verdict |
|---|---|---|---|
| 21 mm | 49.0 → 47.8 (**3%**) | 33,424 → 32,662 (**2%**) | ✅ solid |
| 15 mm | 9.3 → **25.8 (178%)** | 18,027 → **31,238 (73%)** | 🔴 unmeasurable |

🔑 **A 0.16% mesh change swings the answer by 178% at 15 mm and 3% at 21 mm.**
That is R71's signature: at a degeneracy the quantity is not a property of the
design, it is a property of the discretisation. R59's 15 mm row and R81's are
both "right" and neither means anything.

> 🔴 **R59 reported 15 mm as a catastrophe (TE₀₁₁ hybridised, Q₀ 18,027). The
> correct statement is that 15 mm is a point where nothing can be measured.**
> Those are different claims: one is a property of the groove, the other is a
> warning that no simulation at that depth is admissible. ✅ And it retroactively
> explains why R59 and R80 disagreed there while reproducing exactly at 21 mm.

### 🔑 C1 WAS A CATEGORY ERROR, and it invalidates the framing of R59 and R80

C1 — "TE₀₁₁ azimuthal purity ≤ quartz" — rejected ten geometries across depth and
width. It treats azimuthal purity as a property of the RESONATOR. **It is a
property of the DRIVE.**

A filter changes which modes exist and where they sit in frequency. It cannot
change what the source excites. The floor is set by the coupler: **0.0046 with
the design loop, 0.0263 with sc06 on the same nominal cavity — 5.7×** — and no
groove geometry reached below 0.0372.

> 🔑 **C1 asked the filter to remove contamination the coupler injects, then
> reported ten filter geometries as failures for not doing it.** The criterion was
> unachievable by construction. That is the tell: not a hard problem, a
> mis-assigned one.

⚠️ Three further mis-categorisations in the same criterion, any one of which
would also disqualify it as stated:

- **cold measurement, lit consequence** — the outcome it proxies is plasma
  symmetry, and R74 measured the plasma taking ≥96.8% of absorbed power, so the
  lit field is set by the load, not by the cold mode structure;
- **wrong region** — the bins are air attributes 3..7, the WHOLE cavity; what
  matters is deposition symmetry in the plasma torus;
- **wrong quantity** — stored energy, where the physics is ∫σ|E|²dφ.

✅ **What survives R59/R80 is narrower than reported**: the κ identity (TE modes
are blind at the cap/barrel corner because J′ₘ(χ′ₘₙ) = 0 — closed form,
sampling-independent), the harness tie-points, and the qualitative fact that a
slot-mode family exists and moves with depth. **The (w, d) verdicts do not
survive**, both because C1 was mis-assigned and because the sampling interval was
unknowable without the identification R81 has only now supplied.

| 126 | ✅ **R81 — slot modes IDENTIFIED BY MEASUREMENT; the 26 mm collapse is hybridisation; 15 mm was never a measurement; C1 was a category error** | Groove given its own attribute (TAG 13, Energy index 80) after two failed inferences (R77's TM₁₁₁, R78's dielectric resonance). 🔑 **TE₀₁₁ carries 0.6% of its energy in the slot; the family at 17–52% ARE slot modes** — measured, not inferred. ✅ **At 26 mm TE₀₁₁ carries 15.7%, 26× its 21 mm value, at pm/pe 50.2: the Q₀ collapse is HYBRIDISATION**, TE₀₁₁ moving into the slot, not a slot mode swamping it. 🔴 **Tagging is a 0.16% mesh change and swings 15 mm by 178% in pm/pe and 73% in Q₀, against 3%/2% at 21 mm** — R71's signature. **15 mm is not a catastrophe, it is a point where nothing is measurable**, and R59's reading of it is withdrawn; it also explains why R59 and R80 disagreed there and matched exactly at 21 mm. 🔑 **C1 was a CATEGORY ERROR: azimuthal purity is a property of the DRIVE, not the resonator.** The floor is the coupler's (0.0046 design loop vs 0.0263 sc06, 5.7×) and no groove reached 0.0372 — the criterion was unachievable by construction, and ten geometries were reported as failures for it. ⚠️ Also cold-for-lit, whole-cavity-for-plasma-region, and stored-energy-for-deposited-power. **R59/R80's (w,d) verdicts do not survive; the κ identity and the tie-points do** |

## 2026-08-19 — 🔑 STANDING POLICY: the design is DIMENSIONLESS with two hard anchors, and millimetres were hiding its structure

The user's reframing, and it generalises three separate errors already recorded.
**Maxwell's equations are scale-invariant** — scale every length by k and the
wavelength by k and the solution is identical — so the cavity electromagnetics is
determined entirely by RATIOS. Millimetres are a presentation choice, and this
project has been sweeping them and matching absolute values from one
configuration onto another.

### The two anchors, and everything else reduces

| | |
|---|---|
| ① **f₀ = 2.45 GHz, band ±2.04% fractional** | A **regulatory** anchor — ISM allocation and LDMOS availability — not a physical one. Fixes λ = 122.36 mm |
| ② **N₂ at 0–2 atm** | The only place scale-invariance genuinely fails: Paschen is *p·d*, Townsend is *E/N*, the vibrational bootstrap is absolute. Produces σ, which re-enters the EM **only** as δ/t |

✅ Two that look like hard units and are not: **wall conductivity** →
δ_wall/λ = 1.05e-5, a fixed dimensionless number; **thermal drift** →
Δf/f = −α·ΔT = **−23.6 ppm/K**, scale-free. Only the absolute temperature *rise*
needs units, and that is a cooling question, not an EM one.

### 🔑 What millimetres were hiding

| depth | in λ | |
|---|---|---|
| 15 mm | **0.1226 = λ/8** | the crossing — R81 showed it unmeasurable |
| 21 mm | **0.1716 = λ/6** | the surviving candidate |
| 26 mm | 0.2125 | 🔴 the hybridisation catastrophe — **not a simple fraction** |
| 30.6 mm | **0.2501 = λ/4** | the classic quarter-wave choke |

🔑 **The trouble lies between λ/5 and λ/4, and the ladder never sampled it** —
0.172 → 0.213 → 0.250 leaves both gaps empty. In millimetres, 21/26/30.6 looked
like even steps. In λ they are λ/6, nothing, λ/4, with the catastrophe sitting in
the first gap. **A ladder in λ would have sampled λ/5 = 24.5 mm and λ/4.5 =
27.2 mm** — which is where the mechanism actually changes.

✅ Also visible only in λ: `chimney.diameter`, `feed.diameter` and `torch.od` all
cluster at **λ/6**, and both aperture lengths at **λ/3**.

### Why this is the same error as three already recorded

| | absolute framing | ratio framing |
|---|---|---|
| R73 | Q_ext = 31,304 → "98× deficit" | η, delivered power → 21 points |
| R74 | σ = 30 S/m | **δ/t** — and the η minimum sits at δ/t ≈ 1, which is the physics |
| entry 126 | C1: bin1 ≤ 0.0263, quartz's own number carried onto grooves | fraction of the *bare* contamination removed — 63–85% vs quartz's 89%, **assignable to the filter** |

> 🔑 **The ratio framing and the assignability fix are the same fix.** Scoring
> within a configuration makes the criterion attributable to the component being
> varied; scoring against another configuration's absolute does not.

### ⚠️ Implementation, and the trap avoided

`dimensionless.py` **derives** the view from `baselines.json`; it does not store
it. `baselines.json` stays in millimetres because that is what `geometry.py`
consumes. A hand-maintained second copy in λ would become the next thing to drift
— which is exactly how a dropped mode filter kept being simulated for a day.

🔴 **One trap the derived view exposed:** `baselines.json` mixes order-1 RAW and
offset-corrected frequencies without marking which is which, and the offsets are
**mode-dependent** (+24.54 MHz TE₀₁₁ = +1.00% of f₀, +20.06 TM₀₂₀). An
in-band/out-of-band call read straight off a fractional-detuning table can be
wrong by ~1% — a quarter of the whole band. The tool now says so on every run.

| 127 | 🔑 **STANDING POLICY — the design is DIMENSIONLESS; two hard anchors; millimetres were hiding the structure** | Maxwell is scale-invariant, so the EM design is pure ratios. ① **f₀ = 2.45 GHz ±2.04%**, a REGULATORY anchor, fixing λ = 122.36 mm; ② **N₂ at 0–2 atm**, the only place scale-invariance fails (Paschen *pd*, Townsend *E/N*), producing σ which re-enters only as **δ/t**. ✅ Wall conductivity (δ/λ = 1.05e-5) and thermal drift (−23.6 ppm/K) look like hard units and are not. 🔑 **In λ the groove ladder reads λ/8 (crossing, unmeasurable), λ/6 (candidate), 0.2125 (catastrophe, NOT a simple fraction), λ/4 (choke) — and the trouble lies in the unsampled gaps between λ/5 and λ/4.** In mm, 21/26/30.6 looked like even steps. ✅ chimney/feed/torch all cluster at λ/6, aperture lengths at λ/3. 🔑 **Same error as R73 (Q_ext→η), R74 (σ→δ/t) and C1 (absolute→fraction-of-bare-removed): the ratio framing and the assignability fix are the same fix.** ⚠️ `dimensionless.py` DERIVES from baselines rather than storing a second copy. 🔴 It exposed that baselines mixes raw and offset-corrected frequencies unmarked, with mode-dependent offsets worth ~1% of f₀ — a quarter of the band |

## 2026-08-19 — ⚠️ CORRECTION: band-placement claims that borrowed TE₀₁₁'s offset, and the `frame` field that now prevents it

Acting on entry 127's finding, every GHz/MHz entry in `baselines.json` now carries
a mandatory **`frame`**: `raw-order1` (offset NOT applied) · `converged` (applied
or order-2 verified) · `delta` (a difference, order-independent) · `offset` (the
constant itself). 25 entries: 6 raw, 4 converged, 13 delta, 2 offset.

✅ **The framing immediately validated itself.** `te011.f_raw_order1` + 24.54 MHz
= **2.4415** against `te011.f_converged` = **2.44146**; TM₀₂₀ likewise agrees to
four decimals. Raw + offset must equal converged, and now a guard checks it —
`dimensionless.check()` fails on any unframed entry or any broken identity.

### ⚠️ What I got wrong

**I applied `offset.te011` (+24.54 MHz) to modes that are not TE₀₁₁ and whose
offsets have never been measured**, then quoted the result as a known frequency:

| claim | raw | using the two MEASURED offsets | I quoted | verdict |
|---|---:|---|---:|---|
| the interloper is in band | 2.4383 | 2.4584 – 2.4628 | 2.4628 | ✅ IN either way |
| TM₁₁₁ is out of band (R76) | 2.3430 | 2.3631 – 2.3675 | 2.3675 | ✅ OUT either way |

✅ **Both conclusions survive** — the 4.5 MHz spread between the two known offsets
does not cross a band edge in either case. 🔴 **But the precision was
unjustified**, and R38 records the offsets as geometry-dependent as well as
mode-dependent, so the real spread for an unidentified mode is wider than 4.5 MHz.
`dimensionless.py` now **refuses** to make a placement claim for a mode whose
offset is unmeasured, rather than silently borrowing TE₀₁₁'s.

🔑 The general form, and it is the third instance today: **a constant measured for
one object was carried onto another without checking it transfers.** The others
were `tm111.f_filtered` used to eliminate TM₁₁₁ in R77, and quartz's bin1 used as
C1's threshold for grooves. Same error, three costumes.

| 128 | ⚠️ **CORRECTION — placement claims borrowed TE₀₁₁'s offset for modes whose offset is unmeasured; `frame` added to baselines** | All 25 GHz/MHz entries now carry a mandatory frame (6 raw-order1, 4 converged, 13 delta, 2 offset), and `dimensionless.check()` guards it. ✅ **Self-validating: raw + offset = converged to four decimals for both measured modes.** 🔴 **I quoted the interloper at 2.4628 and TM₁₁₁ at 2.3675 using TE₀₁₁'s offset on modes that are not TE₀₁₁** — the two measured offsets span 4.5 MHz, so **both conclusions survive (IN / OUT either way) but the precision was unjustified**, and R38 makes the offsets geometry-dependent too. The tool now refuses a placement claim for a mode with no measured offset. 🔑 **Third instance today of a constant measured for one object being carried onto another**: also R77's use of `tm111.f_filtered` from another geometry, and C1's use of quartz's bin1 as a threshold for grooves |

## 2026-08-19 — 🔑 D/L IS A LIVE AXIS, not a settled one — and it is the dominant lever on mode crowding

Following entry 127's dimensionless policy. The cavity's mode landscape is a
function of **D/L alone** — a pure ratio, computable analytically at zero cost —
and it was never chosen for it.

| D/L | nearest non-TM₁₁₁ mode | |
|---|---:|---|
| 1.40 | **7.33%** | widest clearance available |
| 2.00 | 3.65% | |
| **2.343** | **3.34%** (TM₂₁₀) | ✅ the current design |
| **2.50** | **0.61%** (TM₀₂₀) | 🔴 inside the ±2.04% band |
| 3.00 | 3.95% | |

⚠️ TM₁₁₁ is excluded because χ′₀₁ = χ₁₁ **exactly, at every aspect ratio** — it is
immovable by shape and remains the filter's job whatever D/L is chosen. Shape
moves everything else.

### 🔴 The design sits 0.16 in D/L from a collapse it never knew about

At D/L = 2.50 TM₀₂₀ lands **0.61%** from TE₀₁₁ — reachable by the amplifier.
Machining tolerance is ±0.0045 in D/L, nowhere near it, so this is not a present
risk. **But the margin was inherited, not designed**, and it must be recorded so
that "round the cavity to 210 mm" is never a free-looking change.

### ✅ The torch length constraint does NOT bind the production design

Entry 90 recorded 129.5 mm of span against a 120–150 mm catalogue tube and warned
that a custom length would spend R16's catalogue-part lever. ✅ **That lever was
already spent.** Entry 30's finding is that *quartz or Sialon* outer tubes are
catalogue; the design's tube is **SAPPHIRE**, a made-to-order part at ~$1,500 with
its own payback analysis. Entry 90's own wording — *"length drives cost"* — is a
gradient, not a wall.

> 🔑 **The 120–150 mm limit binds the QUARTZ DEVELOPMENT BUILD, not the sapphire
> production design. Outer tube length is a specification line, so D/L is
> purchasable.**

🔢 Cost of D/L = 1.4 at f₀ = 2.45: cavity **123 mm** against 88.5, D **172 mm**
against 207.4. With entry 90's own escape — the groove cut as a **counterbore in
the barrel** rather than a pocket in the cap, electromagnetically identical — the
cap stays thin and the feed short, so span goes ~130 → ~143 mm plus base. Roughly
**+15–25 mm of sapphire (~+15–20% on the tube), and the loss of the cheap
catalogue-quartz development path.**

### ⚠️ Do not spend it yet — 3.34% is probably adequate

🔢 The entire settable range — σ drift, machining, thermal, offset uncertainty —
is **23 MHz = 0.94% of f₀**, against **3.34%** to the nearest non-TM₁₁₁ mode.
**3.5× margin, and nothing non-TM₁₁₁ is in band today.** D/L ≈ 1.4 buys margin
that is not currently short.

✅ What the analysis is worth is that it converts *"the aspect ratio is fixed"*
into *"the aspect ratio is a purchasable 2.2× on clearance"* — the right shape for
a decision — and it names where the room is if the slot modes force us to want it.

🔑 **How D/L came to be frozen, which is the general lesson:** entry 98 settled
that TE₀₁₁ **cannot be shrunk**, which is a statement about SIZE. The SHAPE
silently inherited that verdict and was never posed as a variable. **Anchoring to
absolutes early froze the ratio that mattered most** — exactly the failure entry
127 describes.

| # | question | status |
|---|---|---|
| **R84** | **Aspect ratio D/L as a design variable.** Analytic mode chart done: 3.34% now, 7.33% available at D/L ≈ 1.4, catastrophe at 2.50. Needs the empty-cavity chart re-done WITH torch, apertures and filter before any commitment, plus the sapphire length/cost gradient | open — not urgent while 3.5× margin holds |

| 129 | 🔑 **D/L is a LIVE axis and the dominant lever on mode crowding; the torch constraint does not bind the sapphire design** | Mode landscape is a function of D/L alone — analytic, free. **Current 2.343 gives 3.34% to the nearest non-TM₁₁₁ mode; D/L ≈ 1.4 gives 7.33%; D/L = 2.50 gives 0.61% — inside the band.** ⚠️ TM₁₁₁ excluded: χ′₀₁ = χ₁₁ at EVERY aspect ratio, so shape can never move it and the filter is always needed. 🔴 **The design sits 0.16 in D/L from a collapse it never knew about** — not a present risk (tolerance is ±0.0045) but an inherited margin, recorded so a "round it to 210 mm" change is never free-looking. ✅ **Entry 90's torch limit binds the QUARTZ DEVELOPMENT build only** — entry 30's catalogue lever covers quartz/Sialon, and the design's sapphire tube is already made-to-order at ~$1,500, so **length is a spec line and D/L is purchasable** (~+15–25 mm of sapphire for D/L 1.4, plus loss of the catalogue-quartz dev path). ⚠️ **Do not spend it yet: the whole settable range is 0.94% of f₀ against 3.34% clearance — 3.5× margin.** 🔑 **D/L froze because entry 98's "TE₀₁₁ cannot be shrunk" is about SIZE and the SHAPE silently inherited it** — anchoring to absolutes early froze the ratio that mattered most |

## 2026-08-19 — ✅ R83: C1's REFERENT IS REAL. Cold contamination tracks lit deposition uniformity — and my category-error claim was too strong

C1 was withdrawn in entry 126 as a category error. R83 measures the outcome it
was a proxy for: the plasma toroid split into azimuthal sectors
(`--plasma-sectors`, attributes 20–24, one Energy index each), lit, with deposited
power per sector = (σ/ε₀)·E_elec — the relation R74 validated when its
decomposition closed to 0.22 points. Scored as a **within-configuration ratio**,
(P_max − P_min)/P_mean.

| config | δ/t | cold bin1 | per-sector deposition | non-unif |
|---|---:|---:|---|---:|
| bare | 2.55 | 0.2443 | 46.4 / 21.8 / 5.3 / 5.2 / 21.3% | **2.057** |
| bare | 0.25 | 0.2443 | 15.8 / 11.3 / 30.8 / 30.7 / 11.4% | **0.978** |
| quartz 3 mm | 2.55 | 0.0263 | 16.3 / 17.2 / 25.6 / 24.6 / 16.3% | **0.468** |
| quartz 3 mm | 0.25 | 0.0263 | 25.0 / 21.0 / 15.8 / 16.2 / 21.9% | **0.459** |

🔑 **A 9.3× reduction in cold bin1 buys 4.4× better deposition uniformity in the
transparent regime and 2.1× in the opaque one. The proxy was real.**

✅ **The plasma partially symmetrises and does not rescue.** Bare improves 2.057 →
0.978 as it goes opaque — screening helps — but stays **2.1× worse than quartz**.
My prediction that the plasma might symmetrise regardless (it takes ≥96.8% of
absorbed power) was half right and nowhere near enough.

✅ **Regime matters only when contamination is large.** Bare swings 2.057 → 0.978
across δ/t; quartz is 0.468 → 0.459, **identical**. Once contamination is low, δ/t
stops mattering — a useful robustness statement, and it means the criterion does
NOT have to be quoted with δ/t for a good design.

⚠️ **Even the best case is 46% non-uniform** — sectors 15.8 to 25.6% against a
uniform 20. Whether that is acceptable is an analytical-chemistry spec, not an EM
one, and remains unanswered.

### 🔴 WALKING BACK part of entry 126

Entry 126 said azimuthal purity is a property of the DRIVE and not the resonator,
so C1 was mis-assigned. **R83 shows the filter has real leverage — 2.1 to 4.4×.**
The accurate statement is narrower:

> 🔑 **The filter controls contamination from DEGENERATE modes; it cannot control
> what the coupler injects.** Bare is not a filter variant — it is the cavity with
> the χ′₀₁ = χ₁₁ degeneracy unbroken. Quartz removes that. What remains — quartz's
> 0.0263 cold, 0.46 deposition — is the coupler's floor, and **C1's threshold was
> set below it.**

So C1 conflated two contributions, one assignable to the filter and one not, then
put its bar under the un-assignable part. That still invalidates rejecting ten
geometries on it. But "wholly mis-assigned" was too strong, and entry 126 is
corrected accordingly.

### ✅ The replacement criterion, now defined

**C1′ — azimuthal non-uniformity of deposited power in the plasma torus, lit,
scored as (P_max − P_min)/P_mean.** An outcome, in the right region, in the right
state, as a within-configuration ratio. Reference values: **bare 0.98–2.06,
quartz 0.46.** ⚠️ Measured at 5 sectors, so an m=5 deposition pattern would read
as uniform (R82 unresolved).

### ⚠️ A tag collision, caught only by reading the log

The first attempt wrote four solves into two directories.
`str(100.0).replace('.','p').rstrip('p0')` → `'1'` — **rstrip takes a CHARACTER
SET, not a suffix**, so σ = 1 and σ = 100 both became `_s1` and the second
overwrote the first. The run completed and printed plausible numbers. R32's tag
collision in a new spelling. Fixed with `f"{sig:g}"`, and the driver now **proves
the tag mapping is injective before solving anything**, because a collision is
undetectable afterwards.

| # | question | status |
|---|---|---|
| **R85** | **Groove 21 mm under C1′.** It sits between quartz (0.0263) and bare (0.2443) on cold bin1 at 0.0572 — does it reach quartz-like deposition uniformity? One solve pair | open — now well-posed |

| 130 | ✅ **R83 — C1's referent is REAL: cold contamination tracks lit deposition uniformity; entry 126's category-error claim narrowed** | Plasma split into azimuthal sectors, lit, deposited power per sector as a within-configuration ratio. **9.3× less cold bin1 buys 4.4× better deposition uniformity transparent, 2.1× opaque.** ✅ **The plasma partially symmetrises and does not rescue** — bare goes 2.057 → 0.978 opaque but stays 2.1× worse than quartz. ✅ **Regime matters only when contamination is high**: quartz is 0.468 vs 0.459 across a 10× range in δ/t, identical. ⚠️ **Even quartz is 46% non-uniform** — acceptability is an analytical-chemistry spec, still unanswered. 🔴 **Entry 126 WALKED BACK**: the filter does have leverage, so C1 was not wholly mis-assigned — **the filter controls DEGENERATE-mode contamination, the coupler sets the floor, and C1 conflated them and set its bar below the un-assignable part.** ✅ **C1′ defined**: deposition non-uniformity, lit, in the torus, as a ratio — bare 0.98–2.06, quartz 0.46. ⚠️ **Tag collision caught by reading the log**: `rstrip('p0')` takes a character set, so σ=1 and σ=100 wrote the same directory and the run printed plausible numbers; tags now proven injective before solving |

## 2026-08-19 — 🔴 R85: the groove DELIVERS MORE POWER AND SPREADS IT WORSE. On present evidence the quartz filter is the safer choice.

The 21 mm groove scored under C1′, against the two references. ⚠️ Its mesh was
built in a **separate** call at a forced `--size-factor 1.00` and checked (144,393
/ 160,634 / 145,524 tets, all 1.00) rather than guaranteed by one sweep — weaker
than R27's rule, and recorded as such.

| config | cold bin1 | η transparent | η opaque | **non-unif tr** | **non-unif op** |
|---|---:|---:|---:|---:|---:|
| bare | 0.2443 | 66.6% | 83.2% | 2.057 | 0.978 |
| **quartz 3 mm** | 0.0263 | 71.4% | 84.8% | **0.468** | **0.459** |
| **groove 21 mm** | 0.0572 | **96.2%** | **98.2%** | 1.107 | 0.643 |

🔑 **The groove delivers far more power — 96–98% against 71–85% — and distributes
it 2.4× (transparent) / 1.4× (opaque) less evenly.** Both are outcomes; neither
dominates on physics alone.

### ✅ The cold proxy predicts the lit outcome, in rank

quartz < groove < bare on **both** cold bin1 (1.0 / 2.2 / 9.3×) and lit
non-uniformity (1.0 / 2.4 / 4.4× transparent). ✅ **The cheap cold measurement is
a valid ranking instrument for the expensive lit one** — which retrospectively
justifies having used it, even though its threshold and its assignment were both
wrong.

### The deposition is one-sided, and the pattern is not simply "hot at the loop"

| config | per-sector % | hot | |
|---|---|---|---|
| bare | 46.4 / 21.8 / 5.3 / 5.2 / 21.3 | sector 1 | **at** the loop (φ = 36°) |
| quartz | 16.3 / 17.2 / 25.6 / 24.6 / 16.3 | sector 3 | **opposite** the loop |
| groove | 29.8 / 11.7 / 7.8 / 20.7 / 30.0 | sectors 5+1 | spanning the loop |

All three are essentially m = 1 — one hot side, one cold side — but the phase
differs. ⚠️ At 5 sectors an m = 5 component would read as uniform (R82).

### ⚠️ The η comparison sits on two favourable points

δ/t = 2.55 and 0.25 were chosen to span transparent and opaque. **Neither is the
η minimum**, which R74 puts at δ/t ≈ 1 (σ ≈ 3–10). So the groove's 96–98% is
measured on both high flanks and may not hold at the worst case. ⚠️ 96–98% is also
near saturation, where R74 warned that ratios between cases understate
differences.

### 🔴 What this does to the filter decision

> **On present evidence the quartz annulus is the safer choice, and that reverses
> the working decision to drop it for a groove.**

The reasoning, and it turns on which unknown is which:

- **Power is not short.** R74 measured a floor of 60.5% delivered across a 1000×
  range in σ *with the quartz*. The groove's power advantage buys margin in a
  quantity already shown to have plenty.
- **Uniformity's acceptable value is unknown.** Nobody has stated what deposition
  asymmetry the instrument tolerates, and the groove is 2.4× worse on it.
- 🔑 **Prefer the option that is better on the criterion whose limit you do not
  know, when the other criterion already has margin.**

⚠️ Held against that: R80 measured the groove's Q advantage evaporating with sc06
(33,424 vs quartz's 37,059), so the groove's original justification — +6% Q, no
dielectric loss — is already weakened. And the quartz brings back
`brake.thickness`'s mounting/CTE problem (R53) and its 5.6% Q cost.

| # | question | status |
|---|---|---|
| **R86** | **Score both filters at the η MINIMUM (δ/t ≈ 1, σ ≈ 3–10).** R83/R85 sampled only the favourable flanks; the groove's power advantage is unverified where it matters most | open — one solve pair each |
| **R87** | **State the deposition-uniformity spec.** What azimuthal asymmetry does OES precision tolerate? Analytical chemistry, not EM. **It decides the filter choice** | open — external |

| 131 | 🔴 **R85 — the groove delivers MORE power (96–98% vs 71–85%) and spreads it WORSE (2.4× / 1.4×); quartz is the safer choice on present evidence** | 21 mm groove scored under C1′ against bare and quartz. ✅ **The cold proxy predicts the lit outcome in RANK** — quartz < groove < bare on both cold bin1 and lit non-uniformity — which retrospectively justifies using it as a ranking instrument even though its threshold and assignment were wrong. **Deposition is one-sided (m≈1) in all three, but the phase differs: bare hot AT the loop, quartz hot OPPOSITE it, groove spanning it.** ⚠️ η measured at δ/t = 2.55 and 0.25, **both favourable flanks — neither is the η minimum at δ/t ≈ 1**, and 96–98% is near saturation where ratios understate. 🔴 **REVERSES the working decision to drop the quartz**: power already has a 60.5% floor across 1000× in σ, while uniformity's acceptable value is unknown — **prefer the option better on the criterion whose limit you do not know, when the other has margin.** ⚠️ Against: R80 showed the groove's Q advantage evaporates with sc06, and quartz reinstates the CTE/mounting problem (R53). R86 (score at the η minimum) and R87 (state the uniformity spec) opened |

## 2026-08-19 — ✅ R88 stage 2: the ten torch parameters exposed, validated, and recorded — plus a correction about what was already modelled

### 🔴 First, a correction I made and had to withdraw within the hour

I scoped a "dimensionless torch" claiming the **three-tube Fassel geometry was
not modelled**. It is, and has been. `geometry.py` builds outer, intermediate and
injector tubes, and its own comment records that the single-tube model was
already found insufficient and fixed:

> *"Modelling only the outer tube was wrong in two ways. The intermediate tube
> and injector displace gas — and the injector sits ON AXIS, exactly where
> TM₀₂₀'s E_z peaks. And the plasma forms DOWNSTREAM of the intermediate tube."*

✅ **R83 and R85's deposition results therefore already include the full torch
and stand.** 🔑 **How I got it wrong: I inferred capability from the fragment
inputs and the parameter defaults without reading the construction thirty lines
below.** Same shape as reading `"Type": "Linear"` and concluding brute force when
the log said `PROM construction`. **Inferring capability from a config surface
instead of the code that consumes it** — twice in one day, now a standing hazard.

### ✅ What was actually missing: every dimension was unreachable

Ten parameters — `torch_od`, `torch_wall`, `torch_eps`, `torch_tand`,
`inter_od/wall/end`, `inj_od/id/end` — lived in the dict with **no CLI flag**.
Exposed as four grouped comma flags, matching `--groove` / `--plasma` / `--loop`:

```
--torch-tube od,wall            default 20,1.5
--intermediate od,wall,end      default 16,1.0,-20   (od=0 disables)
--injector od,id,end            default 5,2,-25      (od=0 disables)
--torch-material eps,tand       default 3.78,1e-4    (sapphire 9.4,3.5e-5)
```

### ✅ Validated, not trusted — four guards, all verified firing

Three concentric tubes that overlap, or a wall thicker than its own radius,
produce a mesh that is geometric nonsense **and solves happily**:

| guard | test | result |
|---|---|---|
| wall < od/2 | `--torch-tube 20,12` | ✅ refused |
| intermediate inside outer bore | `--intermediate 20,1,-20` | ✅ refused (10.00 vs 8.50 mm) |
| injector inside intermediate bore | `--injector 16,2,-25` | ✅ refused (8.00 vs 7.00 mm) |
| arity | `--intermediate 25.6,1.6` | ✅ refused, "needs 3, got 2" |

### ✅ And the sidecar now records the torch — a silent-drift gap closed

`geometry_mm` carried radius, length, brake, chimney, feed, groove and loop, but
**nothing about the torch**. A mesh built with a different torch was
indistinguishable from the default in its own metadata — precisely the failure
that let a dropped mode filter be simulated for a day. Now records `torch`,
`intermediate`, `injector` and `torch_material`.

### ✅ Regression and demonstration

**Default path byte-identical: 158,929 tets**, matching `gq3`/`idref`/`fltr3`. A
1.6× torch (`--torch-tube 32,2.4 --intermediate 25.6,1.6,-20 --injector 8,3.2,-25`
with `--plasma 7.2,13.6,-20,10`) builds cleanly and takes **bore/a from 0.0820 to
0.1311, ρ from 0.063 to 0.100** — the first rung of the R88 stage-3 ladder, now
constructible.

⚠️ **ρ is not independently settable**: the plasma is bounded by the outer tube
bore, so all three tubes scale together. The 2.5× deposition estimate for ρ = 0.10
assumed only the plasma moved and must be re-derived from a solve.

| 132 | ✅ **R88 stage 2 — ten torch parameters exposed as four grouped flags, four validation guards, sidecar recording; and a correction about what was already modelled** | 🔴 **I claimed the three-tube Fassel geometry was not modelled. It is, and the code comment shows that gap was already found and closed** — R83/R85 already include the full torch and stand. **I inferred capability from the fragment inputs and parameter defaults without reading the construction below them** — same error as reading `"Type": "Linear"` and missing the PROM in the log. ✅ The real gap was that all ten dimensions were unreachable from the CLI; now `--torch-tube`, `--intermediate`, `--injector`, `--torch-material`. ✅ **Four guards verified firing** — overlapping concentric tubes are geometric nonsense that solves happily. ✅ **Sidecar now records the torch**, closing a silent-drift gap: a non-default torch was previously invisible in its own metadata. ✅ **Default path byte-identical at 158,929 tets**; a 1.6× torch builds and takes ρ from 0.063 to 0.100. ⚠️ ρ is not independently settable — all three tubes scale together, so the 2.5× deposition estimate must be re-derived from a solve |

## 2026-08-19 — 🔑 STANDING POLICY: every criterion must state its path to DETECTION LIMIT. Three of six used this session cannot.

The user's framing: any performance parameter is downstream of **plasma spectrum
visibility**. This instrument's terminal objective is a detection limit,

🔢     **LOD ≈ 3·σ_background / sensitivity**

and a criterion that cannot name its path down to it may not reject a design.

| level 1 — sets LOD directly | level 2 — what we optimise |
|---|---|
| **background** — continuum, N₂ bands, **wall reflectance**, stray light | surface material · light trap |
| **sensitivity** — excitation × collection × residence | η → power → temperature; viewport solid angle |
| **noise / RSD** — plasma flicker | deposition uniformity · frequency stability |
| **self-absorption** on Ca/Mg/Na/K | wall retroreflection · plasma chord length |

### 🔴 Retroactive audit — three of six criteria cannot justify themselves

| criterion | path | verdict |
|---|---|---|
| **η** = 1−\|Γ\|² | power → temperature → excitation → sensitivity | ✅ |
| **C4** TE₀₁₁ ≥ 2× best reachable rival | is TE₀₁₁ driven at all → a plasma exists | ✅ |
| **C1′** deposition non-uniformity | plasma symmetry → RSD → noise | ✅ path valid, **threshold unknown (R87)** |
| **C1** bin1 ≤ 0.0263 | 🔴 none — a cold field statistic | 🔴 **rejected ten geometries** |
| **C3** Q₀ ≥ 37,059 | Q₀ → η → sensitivity, but η has a 60.5% floor | 🔴 real quantity, **deficit does not propagate** |
| **C5** separation ≥ 10 linewidths | 🔴 threshold invented | 🔴 |

🔑 **C1 and C5 were inventions; C3 measures something real that already has
margin.** That is the C1 error generalised, and it is why the gate exists rather
than a one-off correction.

### 🔴 Two consequences that reorder the work

**R57 and R58 are the only open items that move BACKGROUND**, which sits in the
LOD *numerator* — silver collapses below its 320 nm plasmon where P 213.6,
Zn 213.9, B 249.7, Mn 257.6 and Cu 324.8 live, Ag₂S drifts it over months, and the
light trap removes the retroreflection that enhances self-absorption on the
majors. Cost ~0.06–0.9% of Q against Q being 0.7% of lit dissipation. **Nearly
free, first-order, and open since 2026-08-17 while six registers of coupling work
went past them.**

🔴 **The viewport is `view_d = 0` in every mesh run this session.** The optical
path — the thing the terminal objective is *about* — has never been modelled here.

### ⚠️ And ρ changes sign

R88 scoped torch radius as pure coupling gain. A larger torus is also a **longer
chord through the plasma**, and self-absorption scales with optical depth on
exactly the strong lines a soil panel reports at high concentration. **ρ buys
signal and costs linearity**, and its net sign on LOD is unknown. The
coupling-only framing had no way to see the second half.

| 133 | 🔑 **STANDING POLICY — every criterion must state its path to DETECTION LIMIT; three of six used this session cannot** | Terminal objective is **LOD ≈ 3σ_background/sensitivity**; a criterion that cannot name its path down to it may not reject a design. ✅ η and C4 pass; C1′ passes with an unknown threshold (R87). 🔴 **C1 (rejected ten geometries) and C5 were inventions with no path; C3 measures something real whose deficit does not propagate because η already has a 60.5% floor.** 🔴 **R57/R58 are the ONLY open items that move BACKGROUND** — the LOD numerator — and have sat open since 2026-08-17 behind six registers of coupling work; silver fails in the UV where P/Zn/B/Mn/Cu live and Ag₂S drifts. 🔴 **The viewport is view_d = 0 in every mesh run this session** — the optical path has never been modelled. ⚠️ **ρ changes sign**: a bigger torus is a longer chord, so it buys signal and costs linearity on Ca/Mg/Na/K |

## 2026-08-19 — 🔴 R89: THE NULL CONTROL FAILS. "TE₀₁₁ wins in band" is not established, and the azimuth story was doubly wrong.

### First: azimuth was never a variable

Both meshes have `view_d = 0`, `chim_d = 0`, `feed_d = 0` — **the loop is the only
azimuthal feature**. The cavity is otherwise axisymmetric, so rotating the loop
rotates the whole solution and changes no observable. 🔴 **I attributed an effect
to azimuth twice, then retracted it as "confounded". It was worse than confounded
— it was inert.** Checking whether a parameter *can* matter costs less than
measuring it or retracting it.

The two runs actually differed in **sector count (1 vs 5)** and **size-factor
(1.06 vs 1.00)**, and the modes compared sat 7.9 MHz apart.

### 🔴 The null control, which must return zero

`az5b` is `az5a` with the loop at 108° instead of 36° — another sector centre, so
an **exact symmetry of a 5-fold mesh**. It must reproduce az5a identically.

| | Δf | Δη | ΔQ₀ |
|---|---:|---:|---:|
| worst across four modes | **1.55 MHz** | **5.0 points** | **2.5%** |

🔑 **That is the numerical noise floor**, measured rather than assumed.

### 🔴 The competition margins are the same size as the noise

| mesh | TE₀₁₁ η | best in-band rival | margin | verdict |
|---|---:|---:|---:|---|
| gq3 — 5 sectors, sf 1.00 | 14.6% | 7.0% | **+7.6** | TE₀₁₁ wins |
| **az5a** — 5 sectors, sf 0.96 | 10.6% | 15.5% | **−4.9** | 🔴 rival wins |
| **az5b** — 5 sectors, sf 0.96 | 12.1% | 16.8% | **−4.7** | 🔴 rival wins |
| az1 — 1 sector, sf 0.96 | 9.3% | 1.8% | **+7.5** | TE₀₁₁ wins |

> 🔴 **Margins of +7.6, −4.9, −4.7, +7.5 against a 5.0-point noise floor. Sector
> count flips the verdict. Mesh density flips the verdict. An operation that
> changes nothing moves it by 5 points. THE COMPETITION RANKING IS NOT RESOLVED
> BY THESE MESHES.**

This is R71's error in a new place: differencing two quantities whose separation
is below the resolution, and reading a sign off it.

### What this retracts, and what survives

🔴 **RETRACTED — "TE₀₁₁ wins in band"**, from the catch-and-hold summary and from
R78/R79's readings. Neither "quartz gives TE₀₁₁ a 2:1 margin" nor "the groove
leaves TE₀₁₁ alone" is established; both sit inside mesh noise.

✅ **SURVIVES — everything about TE₀₁₁ itself**, because it is identified by
bore-H, not by winning a contest:

| | across all four meshes |
|---|---|
| TE₀₁₁ corrected f | 2.4250 – 2.4262 GHz, **spread 1.2 MHz** |
| Q₀ | 34,472 – 36,263, **spread 5%** |
| band margin | 22 MHz below, 62 above — unaffected |
| cold→lit excursion, linewidth, settable range | unaffected |

So **catch and hold in FREQUENCY stands. Which mode takes the power at cold start
does not.**

⚠️ Also: `rig_r89` applies `offset.te011` to every mode, the error entry 128
corrected elsewhere. The bore-E mode it marked in-band at 2.4020 is at **2.3976
with TM₀₂₀'s own offset — out of band, but by only 2.4 MHz against a 1.55 MHz
frequency noise floor.** The verdict above is unchanged either way.

| # | question | status |
|---|---|---|
| **R90** | **Is the in-band competition resolvable at all?** Needs either a mesh-convergence study on η (expensive) or an observable less fragile than peak-picking η on modes separated by less than the mesh noise. **Until then, no design may be selected on mode competition** | open — blocks C4 |

| 134 | 🔴 **R89 — the null control FAILS; "TE₀₁₁ wins in band" is not established; azimuth was inert, not confounded** | Both meshes have viewport, chimney and feed diameters of ZERO, so **the loop is the only azimuthal feature and rotating it changes no observable** — I attributed an effect to azimuth twice and called the retraction "confounded" when it was inert. 🔴 **Null control: φ 36°→108° is an EXACT symmetry of a 5-fold mesh and moves η by 5.0 points, f by 1.55 MHz, Q₀ by 2.5%.** 🔴 **Competition margins are +7.6 / −4.9 / −4.7 / +7.5 points against that 5.0-point floor — sector count flips the verdict, mesh density flips the verdict.** **RETRACTS "TE₀₁₁ wins in band"** from the catch-and-hold summary, R78 and R79. ✅ **TE₀₁₁ itself survives**: f spread 1.2 MHz, Q₀ spread 5%, band margins and excursion unaffected — because it is identified by bore-H, not by winning a contest. **Catch and hold in FREQUENCY stands; which mode takes the power at cold start does not.** R90 opened: no design may be selected on mode competition until it is resolvable |

## 2026-08-19 — ✅ R57 and R58 CLOSED analytically, and a pre-existing bug found: the viewport has never been buildable with azimuthal sectors

Both were the only open registers on the terminal axis (entry 133). Neither needed
a solve — and R89's noise floor is why.

### 🔑 R57: the trap is CALCULABLE, not measurable

| | |
|---|---|
| predicted Q cost, 10 mm trap | **0.06%** (d³ from the 25 mm viewport's 0.9%) |
| 🔴 R89 mesh-to-mesh Q₀ noise floor | **2.5%** |

**The trap is 42× below the noise floor and the viewport 2.8× below it. Neither is
measurable by differencing meshes, and the analytic estimate is strictly better
than anything this harness can produce.** ✅ Below-cutoff margin is ample: a 10 mm
circular aperture has TE₁₁ cutoff at **17.6 GHz, 7.2× above f₀**, giving
~5.4 dB/mm — **~108 dB over a 20 mm depth.**

### ✅ R58: aluminium wins on THREE axes, not two

🔢 Q ∝ √σ, so Ag 6.3e7 → Al 3.5e7 drops Q₀ **25%**. Where that goes:

| | |
|---|---|
| lit, σ=30 | η_wall 0.5% → 0.67%, so η_plasma falls **0.17 points** |
| lit, worst case | η_wall 2.4% → 3.22%, **0.82 points** |
| **cold** | β 34 → 25.3, so cold coupling η **11.1% → 14.6%** |

🔑 **The 25% Q loss is worth a fifth of a point of delivered power, and it
IMPROVES cold coupling by 31%** — because the cavity is heavily *overcoupled*
unlit, so lowering Q₀ moves β toward critical. That helps ignition, which is the
one place power is actually short. Together with entry 93's optical case (UV
reflectance where P/Zn/B/Mn/Cu live, Ag₂S drift, retroreflection into
self-absorption), aluminium wins on optics, on ignition, and costs 0.17 points.

### 🔴 The bug: radial stubs were fused into EVERY wedge

Building R57's azimuthal allocation exposed it. `--viewport 25` works at
`--sectors 1` and **fails at `--sectors 5`** with "volume classification failed":

> A **CUT** of a disjoint tool leaves the wedge unchanged — harmless. A **FUSE**
> of a disjoint tool returns BOTH solids, so the wedge count grows and
> classification breaks. Four sites do this: viewport, the new trap, **the R29
> chimney and the R49 feed feedthrough.**

🔴 **So no mesh in this project has ever combined azimuthal sectoring with a
viewport, chimney or feed.** Every azimuthally-resolved result — R32, R36, R47,
R54, R61 and everything this session — ran on a bare cavity with only the loop and
torch. Entry 93's 36/108/288 allocation was not buildable when it was written.

✅ Fixed for the radial stubs with `fuse_radial()`, which targets the single wedge
containing the stub's azimuth and **refuses if the stub straddles a sector
plane**. ⚠️ **The chimney and feed remain broken at ns > 1** — recorded, not
fixed, since both are currently disabled.

✅ **Regression: no apertures → 158,929 tets, byte-identical.** R57 geometry
builds: **159,677 tets, loop 36 / viewport 108 / trap 288, all sector centres.**

| # | question | status |
|---|---|---|
| ~~R57~~ | ✅ **CLOSED** — trap costs 0.06% of Q (analytic, 42× below measurable), ~108 dB below cutoff, geometry builds at the 36/108/288 allocation | closed |
| ~~R58~~ | ✅ **CLOSED — adopt bare electropolished aluminium.** 0.17 points of delivered power, +31% cold coupling, and the whole optical case | closed |
| **R91** | **Chimney and feed feedthrough are broken at `--sectors > 1`** — same fuse-into-every-wedge bug. Blocks any azimuthal study that includes them | open |

| 135 | ✅ **R57/R58 CLOSED analytically; and radial stubs were never buildable with azimuthal sectors** | 🔑 **R57 is calculable, not measurable**: the trap's 0.06% Q cost is **42× below R89's 2.5% mesh noise floor**, so the analytic d³ estimate beats any simulation here; below-cutoff margin ~108 dB over 20 mm. ✅ **R58 — ADOPT ALUMINIUM.** Q drops 25% but that is **0.17 points** of delivered power, and it **improves cold coupling 11.1% → 14.6%** because the cavity is overcoupled unlit — helping ignition, where power IS short. 🔴 **Pre-existing bug found: radial stubs were FUSED into every wedge**, which is correct at ns=1 and breaks classification at ns>1 — so **no mesh here has ever combined sectoring with a viewport, chimney or feed**, and entry 93's 36/108/288 allocation was unbuildable when written. Fixed for viewport and trap via `fuse_radial()` (targets one wedge, refuses if it straddles a sector plane); **chimney and feed remain broken — R91**. ✅ Regression byte-identical at 158,929; R57 geometry builds at 159,677 |

## 2026-08-19 — 🔑 The viewport was never sized optically. Étendue says 10 mm, and the trap must match it. R91 withdrawn.

### 🔴 Where 25 mm came from

Entry 14b: *"Radial viewport nearly free — **0.9% of Q at 25 mm**"*. It was a **test
size chosen to demonstrate the viewport is cheap in Q**, and it became "the
accepted 25 mm viewport" by repetition. There is no étendue argument for it
anywhere in the record.

### ✅ Sized properly, from the spectrometer

The viewport only needs to pass the cone the spectrometer can accept. At the
103.7 mm plasma-to-wall path:

| spectrometer | viewport = trap |
|---|---:|
| **Echelle f/15** — the usual ICP-OES choice | **~10 mm** |
| Echelle f/12 | ~12 mm |
| Czerny-Turner f/10 | ~13 mm |
| CT f/8 | ~16 mm |
| very fast f/6 | ~20 mm |

🔑 **The trap must MATCH the viewport**, because its job is to absorb exactly the
cone the viewport can see — the user's point, and it is the durable part. The
number follows from F; the matching does not.

🔴 **So R57's original 10 mm was right and my "25 mm, not 10" was wrong.** I argued
the trap was undersized *relative to a 25 mm viewport that was itself never
justified* — sizing one unexamined number to another.

✅ RF is irrelevant at every one of these: below-cutoff needs d < 71.7 mm, and Q
costs 0.06% at 10 mm — thousandths of a point of delivered power (R58).

### ⚠️ Defaults changed: viewport and trap are now ON at 10 mm

`view_d` 0 → **10 mm**, `trap_d` 0 → **10 mm**, `view_phi` 180° → **108°**,
`trap_phi` → **288°** — the entry-93 allocation, all sector centres at N=5 with
the loop at 36°.

> 🔴 **THIS CHANGES EVERY MESH BUILT FROM NOW ON.** Every result file written
> before today was built with `view_d = 0` and no trap. **Do not difference across
> that boundary.** The sidecar records both, so it is detectable — which is why
> the sidecar recording had to come first.

✅ Verified building at sectors 1 and 5 and across the size-factor ladder
(147,454 / 164,544 / 126,616 / 193,425 at sf 1.00/0.96/1.06/0.90; 159,838 at
sectors 5).

### 🔴 R91 WITHDRAWN — the chimney and feed are NOT broken at ns > 1

I claimed both were broken from pattern-matching the fuse-into-every-wedge loop.
Tested:

| | ns=1 | ns=5 |
|---|---|---|
| chimney | 90,162 tets | ✅ 92,198 tets |
| feed | 90,623 tets | ✅ builds (slow, ~2 min) |

And the duplication hypothesis fails on its own evidence: **the chimney adds 1,453
tets at ns=5 against 2,087 at ns=1 — fewer, not the five overlapping copies the
theory predicts.** The later `fragment` evidently resolves what the repeated fuse
creates. ⚠️ The viewport failure was real and is fixed; the generalisation to
chimney and feed was not tested before it was asserted.

### 🔑 The pattern this makes four of

An inherited number used outside the context that produced it:

| | measured as | reused as |
|---|---|---|
| `offset.te011` +24.54 | TE₀₁₁'s order-1 correction | every mode's correction |
| quartz bin1 0.0263 | one filter's contamination | C1's threshold for grooves |
| `tm111.f_filtered` 2.35094 | TM₁₁₁ in another geometry | grounds to eliminate TM₁₁₁ here |
| **viewport 25 mm** | **a Q test size** | **an accepted design dimension** |

**Each entered as a measurement in one context and left as a specification in
another.** The check is one question — *what produced this number, and does that
context still hold?*

| # | question | status |
|---|---|---|
| **R92** | **What is the spectrometer's f-number?** It sets both apertures, and nothing else does. Instrument spec, not EM | open — external, blocks the final aperture sizing |
| ~~R91~~ | 🔴 **WITHDRAWN** — chimney and feed build correctly at ns > 1; the claim was untested | withdrawn |

| 136 | 🔑 **The viewport was never sized optically — étendue says 10 mm, the trap must match, and R91 is withdrawn** | 🔴 **25 mm came from entry 14b as a Q TEST SIZE and became a spec by repetition** — no étendue argument exists. ✅ Sized from the spectrometer at the 103.7 mm path: **f/15 Echelle → ~10 mm**, f/10 → 13, f/6 → 20. 🔑 **The trap must MATCH the viewport** — it absorbs exactly the cone the viewport sees. 🔴 **So R57's 10 mm was right and my "25 mm not 10" was wrong** — I sized one unexamined number to another. ⚠️ **Defaults changed: viewport and trap now ON at 10 mm, at 108°/288°. THIS CHANGES EVERY MESH FROM NOW ON** — pre-today result files have no viewport and no trap; do not difference across it. 🔴 **R91 WITHDRAWN**: chimney and feed build fine at ns>1, and the chimney adds FEWER tets at ns=5 than ns=1, refuting the duplication theory — I asserted it from pattern-matching without testing. 🔑 **Fourth instance of an inherited number reused outside its context** (offset, bin1, tm111.f_filtered, and now 25 mm) |

## 2026-08-19 — ✅ R90 ANSWERED: the competition question was MIS-POSED. Rivals take <0.5% at the drive frequency, and "out of band" is the wrong criterion.

R89 left the in-band competition unresolvable — margins of ±5–8 points against a
5.0-point noise floor. The resolution is not a better measurement. **The question
compares peak η values at frequencies the amplifier never visits simultaneously.**

### 🔑 The amplifier drives at ONE frequency

A rival's contribution there is its own Lorentzian tail, not its peak. Computed in
the **worst case** — every rival assigned the overcoupled branch of
η = 4β/(1+β)², making its line as wide as its measured η permits, which maximises
the tail:

| mesh | rivals present | **total rival power at TE₀₁₁'s drive frequency** |
|---|---|---:|
| az5a | 3 | **0.085%** |
| az5b | 3 | **0.086%** |
| az1 | 3 | **0.438%** |

Against TE₀₁₁'s 10–15%. 🔑 **Once parked on TE₀₁₁, every rival combined takes
under half a percent.**

✅ **And this is robust exactly where R89 was not.** It depends on **separations**
(23–60 MHz, stable to 1.55 MHz) and **linewidths** (from Q₀, stable to 2.5%) — the
two quantities R89 showed hold. It never touches η-at-peak, the one that moved
5 points. The noisy observable was load-bearing only for a question that did not
need answering.

> 🔴 **"TE₀₁₁ wins in band" was both unresolvable AND irrelevant.** R89's
> retraction stands — the claim was not supported — but the design conclusion it
> appeared to threaten is unaffected.

### 🔑 "OUT OF BAND" IS THE WRONG CRITERION

R39 gave the filter its defining job — *keep TM₀₂₀ out of the 2.400–2.500 band* —
and that is what sized the 3 mm quartz annulus. My C5 (separation ≥ 23.4 MHz) was
the same idea reinvented with an arbitrary threshold.

Band membership is not what matters. **Distance from the DRIVE FREQUENCY in units
of the rival's own linewidth is.** TM₀₂₀ sits 2.4 MHz below the band floor —
marginal against 1.55 MHz of mesh noise — yet contributes **0.04%** at the drive
frequency, and would still contribute 0.04% if it crept inside.

🔢 **Derivable replacement.** For a rival to take under 1% of TE₀₁₁'s power it
needs roughly **11 half-linewidths** of separation — about **17 MHz for a 3 MHz
mode**. Everything present is 23–60 MHz away, so all pass with margin.

✅ This is a criterion that satisfies the entry-133 gate: its path to LOD is
*power diverted from TE₀₁₁ → plasma temperature → excitation → sensitivity*, and
its threshold is derived rather than invented.

### ⚠️ What it does not cover

- 🔴 **Acquisition.** If the amplifier SWEEPS to find a resonance at cold start it
  passes through every rival. **R76's "command the ignition frequency, do not
  search for it" is now the only thing preventing a lock onto the wrong mode** —
  essential rather than advisory.
- ⚠️ **Near-degenerate cases.** The Lorentzian-superposition argument assumes
  isolated modes. At the 15 mm groove they hybridise, and R81 already showed that
  depth is unmeasurable.
- ⚠️ Rival frequencies come from meshes whose η was noisy; only the stable inputs
  are used, but they are the same solves.

| # | question | status |
|---|---|---|
| ~~R90~~ | ✅ **ANSWERED — mis-posed.** Rivals take <0.5% at the drive frequency, worst case, across all meshes | closed |
| ~~C5~~ | 🔴 **WITHDRAWN**, replaced by the drive-frequency criterion below | withdrawn |
| **R93** | **Acquisition sequence.** Commanded frequency, not a sweep — specify the cold-start procedure and what happens if the commanded value is wrong by more than a cold linewidth (2.34 MHz) | open |

| 137 | ✅ **R90 ANSWERED — the competition question was MIS-POSED; rivals take <0.5% at the drive frequency; "out of band" is the wrong criterion** | The amplifier drives at ONE frequency, so a rival contributes its Lorentzian TAIL, not its peak. **Worst case — every rival given the overcoupled branch to maximise its width — total rival power at TE₀₁₁'s drive frequency is 0.085 / 0.086 / 0.438% across the three R89 meshes**, against TE₀₁₁'s 10–15%. ✅ **Robust where R89 was not**: it uses separations (stable to 1.55 MHz) and Q₀ (stable to 2.5%), never η-at-peak (which moved 5 points). 🔑 **"Out of band" is the WRONG criterion** — R39's defining job for the filter, which sized the 3 mm quartz, and my C5 reinvented it. **What matters is distance from the DRIVE frequency in units of the rival's own linewidth**: TM₀₂₀ is 2.4 MHz below the band floor yet contributes 0.04%, and would still contribute 0.04% inside it. 🔢 **Derivable threshold: ~11 half-linewidths, ≈17 MHz for a 3 MHz mode** — everything present is 23–60 MHz away. ⚠️ Does NOT cover acquisition: a SWEEPING amplifier passes through every rival, making R76's "command, do not search" essential. R93 opened |

## 2026-08-19 — 🔑 R93: the full operating sequence mapped. Two states were never in the frequency budget, and the control-loop bandwidth is now derivable.

The user's decomposition: **(cold | hot start) → N₂ holding → sample start →
sample holding → N₂ holding**, plus flush and purge. "Acquisition" was one state
of six.

| state | f GHz | vs cold | in cold LW | in lit LW | basis |
|---|---:|---:|---:|---:|---|
| **cold start, 20 °C** | 2.4220 | — | — | — | ✅ MEASURED (R76) |
| hot start, +25 K | 2.4206 | −1.4 | **−0.6** | −0.1 | CTE 23.6e-6/K |
| hot start, +50 K | 2.4191 | −2.9 | **−1.2** | −0.3 | |
| hot start, +100 K | 2.4163 | −5.7 | **−2.4** | −0.5 | |
| **lit, N₂ holding** | 2.4347 | +12.8 | +5.4 | +1.2 | ✅ MEASURED (R74) |
| lit, σ×3 (sample proxy) | 2.4369 | +14.9 | +6.4 | +1.4 | R74 σ=100 |
| lit, σ÷3 | 2.4313 | +9.3 | +4.0 | +0.8 | R74 σ=10 |

### 🔴 Two states R75's budget never had

**HOT START.** A warm cavity's cold resonance sits **0.6–2.4 cold linewidths**
below the room-temperature one. 🔴 **A single commanded cold-start frequency
MISSES above ~50 K.** R75 concluded "settable once at commissioning, essentially
zero dynamic range" — true for σ, false across a duty cycle. The commanded value
must be temperature-compensated or re-acquired per start.

**EXTINCTION.** If the plasma goes out, f drops 12.8 MHz instantly and the
amplifier is **5.5 cold linewidths** off a 2.34 MHz resonance. 🔴 **It cannot
re-ignite without re-acquiring** — and if the cavity is now hot, at a third
frequency again.

### ✅ Sample on/off is a non-issue

~2–3 MHz = **0.23 lit linewidths**. Inside one linewidth, so no tracking is
needed and R75's "zero dynamic range" survives *for the sample cycle*. ⚠️ The σ
change on aspiration is a proxy from R74's σ sweep, not a measurement of solvent
loading.

### 🔑 Control-loop bandwidth, derived

README open risk 5 says *"the control loop needs a bandwidth spec, which does not
exist yet."* From the recorded bootstrap times:

| ignition flow | bootstrap | slew | 1 cold LW in | **BW needed** |
|---|---:|---:|---:|---:|
| 20 slm | 20 ms | 640 MHz/s | 3.7 ms | **274 Hz** |
| 10 slm | 41 ms | 312 MHz/s | 7.5 ms | 133 Hz |
| 5 slm | 82 ms | 156 MHz/s | 15.0 ms | 67 Hz |

🔑 **~1 kHz with margin.** ✅ And the requirement RELAXES through the transient,
because **the resonance broadens as it moves** — 2.34 → 11 MHz. The tightest
moment is the first instant, when the mode is still narrow. Slewing is trivial for
a DDS or PLL; the real constraint is how fast reflected power can be measured and
acted on.

### ✅ Purge and flush: EM-negligible, chemistry-critical

Air ε_r 1.00058 vs N₂ 1.00060 — no measurable EM effect. But O₂ must be purged
before ignition or the electrode and torch oxidise, and the N₂ kinetics that the
bootstrap depends on are not the kinetics of air.

### The sequence, as requirements

| transition | requirement |
|---|---|
| purge → cold start | N₂ established; f from a **temperature-compensated** table, not a constant |
| cold start → lit | track **+12.8 MHz in 20–82 ms**, ~1 kHz loop; gets easier as the line broadens |
| N₂ holding ↔ sample | ±2–3 MHz, inside one lit linewidth — **no action needed** |
| any → extinction | **detect, then re-acquire** at the now-hot cold frequency |

⚠️ **Total span, hot start to densest lit: 20.7 MHz** — close to R75's 23 MHz
settable range, so the number survives, but **the reason has changed**: it is
thermal offset plus the ignition transient, not σ uncertainty.

| # | question | status |
|---|---|---|
| **R94** | **How hot does the cavity actually get?** It sets the hot-start offset (−57 kHz/K) and nothing else does. Wall loss is 3–24 W at 1 kW plus radiant load through the torch. Thermal, not EM | open — external, gates the commanded-frequency table |
| **R95** | **Extinction detection.** What signature, how fast, and what re-acquisition sequence | open |

| 138 | 🔑 **R93 — the full operating sequence mapped; hot start and extinction were never in the frequency budget; control-loop bandwidth derived** | Sequence is (cold\|hot start) → N₂ holding → sample start → sample holding → N₂ holding, plus flush/purge. 🔴 **HOT START sits 0.6–2.4 cold linewidths below the room-temperature resonance — a single commanded frequency MISSES above ~50 K**, so R75's "settable once, zero dynamic" is false across a duty cycle. 🔴 **EXTINCTION drops f by 12.8 MHz = 5.5 cold linewidths, so re-ignition REQUIRES re-acquisition** — at a third frequency if the cavity is hot. ✅ **Sample on/off is 0.23 lit linewidths — no tracking needed.** 🔑 **Control-loop bandwidth DERIVED (README open risk 5): 67–274 Hz from the recorded 20–82 ms bootstrap, so ~1 kHz with margin** — and the requirement RELAXES as the resonance broadens 2.34 → 11 MHz. ✅ Purge/flush are EM-negligible but chemistry-critical. ⚠️ Total span 20.7 MHz — R75's 23 MHz survives but for thermal + transient reasons, not σ. R94 (cavity temperature rise) and R95 (extinction detection) opened |

## 2026-08-19 — 🔑 R96: all-sapphire torch is RF-free; only the outer tube is in the optical path; R18 PROMOTED to tier 1

### ✅ All three tubes in sapphire costs essentially nothing in RF

Perturbation goes as ∫(ε−1)|E_φ|²dV with E_φ ∝ J₁(χ′₀₁ r/a), so a tube near the
axis is nearly invisible:

| tube | r mm | share of the torch's RF effect | share of material | share of lapped area |
|---|---|---:|---:|---:|
| **outer** | 8.5–10 | **73.2%** | 73.2% | 67.1% |
| intermediate | 7–8 | 26.3% | 18.3% | 25.1% |
| **injector** | 1–2.5 | **0.5%** | 8.5% | 7.8% |

| | |
|---|---|
| retune, inner two in sapphire | **≈0.15 mm shorter** cavity (1.8 MHz) |
| retune, full sapphire torch | ≈0.56 mm, against the **0.41 mm shim R46 already sized** |
| loss | tanδ 1.0e-4 → 3.5e-5, so **Q slightly IMPROVES** (−0.8% of total loss) |
| CTE | all-sapphire is a **matched** assembly; quartz-in-sapphire is a 10× mismatch (0.55 vs 5.30 e-6/K), and R53 already records a CTE failure with the quartz brake |

🔑 **The retune mechanism already exists.** R46 sized the shim so one cavity takes
either material; all-sapphire just changes its value. ⚠️ **Sign correction: I first
said sapphire needs a LONGER cavity. It needs a SHORTER one** — higher ε loads
more, f drops, compensate by shrinking — and the record says so directly (88.12
sapphire vs 88.53 quartz). My +0.31 mm came from scaling R33's L = 89.68, measured
at a different radius and not comparable.

### 🔑 Only the outer tube is in the OPTICAL path

The viewport looks radially at mid-plane; the plasma sits at r 4.5–8.5 **inside**
an outer tube of ID 8.5. **Emission passes through the outer tube wall to reach
the viewport — it is the first optical element.** The intermediate ends at
z = −20 and the injector at z = −25, both well below the viewing zone.

✅ So **diamond-lapping is needed only on the outer tube.** Lapping scales with
area, and the inner two are **33% of it** — as-grown or fire-polished suffices for
both, since nothing looks through them. At the user's ~10× quartz for
diamond-lapped sapphire tubing, that is a real saving on the parts that do not
need the finish.

### 🔴 R18 PROMOTED — devitrification is an OPTICAL failure, and it is CHEMICAL as well as thermal

R18 has sat open since 2026-08-15 as a consumables-cost question. Two reasons it
is tier 1 under the entry-133 LOD gate:

🔑 **Cristobalite scatters.** A clouded outer tube **raises background AND cuts
signal** — both terms of LOD = 3σ_B/sensitivity. Quartz does not fail by cracking,
it fails by clouding: gradual, drifting, and it would present as calibration drift
rather than a broken part.

🔑 **And the driver is chemistry at least as much as power.** Alkali metals are
classic nucleating agents for cristobalite, and Mehlich-3 delivers a **2% TDS,
Ca-dominated matrix with Na and K** — which is exactly why Sialon is *sold* for
high-TDS matrices (entry 30). **So "does it survive at AMIP's power" is the wrong
question**: it must be "does it survive AMIP's power *with a Mehlich-3 matrix*",
and the chemistry term may dominate. A power-only test would pass and the
instrument would still cloud.

### The economics, with the user's price point

At ~10× quartz, an all-sapphire set is ~$2,000. Payback is set by the replacement
interval, not the multiple:

| devitrification interval | quartz $/month | payback |
|---|---:|---|
| 6 h (record low) | $5,867 | **0.3 months** |
| 24 h (record high) | $1,467 | 1.4 months |
| 200 h | $176 | 11 months |
| survives | $18 | never |

🔑 **10× is irrelevant against a 100× service life — but if quartz survives,
sapphire never pays back. R18 IS the decision**, and it now gates a ~$2,000 part
choice, an optical-path spec, and a materials decision for all three tubes.

⚠️ `torch_eps`/`torch_tand` apply to all three tubes as ONE fused region, so
per-tube materials are not expressible and none of this is solvable in the current
harness — it is field-weighted estimation.

| # | question | status |
|---|---|---|
| **R18** | ⬆️ **PROMOTED TO TIER 1 and RESTATED**: does quartz survive AMIP's power **with a Mehlich-3 matrix** (2% TDS, Ca-dominated, Na/K present)? Chemistry may dominate thermal. Devitrification is an OPTICAL failure — cristobalite scatters, hitting both LOD terms. Gates ~$2,000 of parts and the optical-path spec | open — external, **tier 1** |
| **R97** | Per-tube materials in `geometry.py` — all three share one `TAG_QUARTZ` region | open — small, blocks solving any mixed-material torch |

| 139 | 🔑 **R96 — all-sapphire torch is RF-free; only the outer tube is in the optical path; R18 promoted and restated** | ✅ **Inner two tubes in sapphire cost ~0.15 mm of shim and Q slightly IMPROVES** (tanδ 2.9× lower); full sapphire ≈0.56 mm against the 0.41 mm shim R46 already sized for exactly this. ✅ **All-sapphire is CTE-matched**; quartz-in-sapphire is a 10× mismatch, and R53 records a CTE failure already. ⚠️ **Sign correction — sapphire needs a SHORTER cavity, not longer** (record: 88.12 vs 88.53); my +0.31 mm scaled R33's L=89.68 from a different radius. 🔑 **Only the outer tube is in the OPTICAL path** — the viewport looks through its wall at mid-plane, while the intermediate (z=−20) and injector (z=−25) sit below the viewing zone — so **diamond-lapping is needed on one tube, and the inner two are 33% of the lapped area**. 🔴 **R18 PROMOTED to tier 1 and RESTATED**: cristobalite SCATTERS, so devitrification hits background AND signal — both LOD terms — and **the driver is CHEMICAL (alkali nucleation, 2% TDS Ca-dominated Mehlich-3) as much as thermal, so a power-only test would pass and the instrument would still cloud.** At 10× quartz, payback is 0.3–1.4 months at the recorded 6–24 h interval and never if quartz survives — **R18 is the decision** |

---

## 2026-08-19 — 🔴 R98: quartz was ALREADY abandoned on 2026-08-15. Entry 139 re-opened a closed question, and R18 is withdrawn as moot

### 🔴 The correction, first

Yesterday I promoted **R18** to tier 1 — *"does quartz survive AMIP's power with a
Mehlich-3 matrix"* — and wrote **"R18 IS the decision"**, gating ~$2,000 of parts
on a devitrification test.

**That question was already dead.** On **2026-08-15**, four days earlier, quartz
was eliminated on a *separate and stronger* ground:

| entry | what it settled |
|---|---|
| 66 | 🔑 **Mehlich-3 contains 0.015 M NH₄F.** Ammonium fluoride + acid generates **HF in situ** |
| 68 | ✅ **SiF₄ boils at −86 °C** — quartz *volatilises*. **AlF₃ is solid to 1276 °C** — sapphire *passivates* |
| 69 | ✅ Fluoride eliminated **two of three** materials: quartz volatilises, **Sialon partially volatilises** (it contains Si), only pure α-Al₂O₃ passivates |
| 72 (R43) | ✅ Passivation is **self-limiting at 3–5 nm**, no spallation, and **SMOOTHING** (RMS 2.6 → <1.0 nm). Scatter at 213.8 nm is **0.011%**. **Sapphire is a multi-year capital asset** |

> 🔴 **Devitrification was never the binding constraint.** Even a quartz tube that
> never clouded would still be etched by the fluoride in the extractant. R18 asks
> whether an already-eliminated material survives a *second, weaker* mechanism.
> **R18 is WITHDRAWN as moot** — not answered, not deferred.

⚠️ **This is the meandering-FINDINGS failure the user named, in its purest form.**
574 KB of append-only record; I re-derived a materials argument four days
downstream without reading the closure, and promoted the result to tier 1. The
tier-1 list was 4; **it is now 3** (R87, R92, R94). Nothing was measured to make
that change — only read.

### ✅ So: yes, abandon quartz. That is the 2026-08-15 decision, restated

The user's proposal and `torch.material_plan` already agree. Two refinements are
genuinely new, and one of them costs money:

| | |
|---|---|
| **raw EFG, inner two tubes** | ✅ consistent. Sapphire **cannot be flame-worked** (entry, 2026-08-15) so EFG is forced regardless; nothing looks through the inner two (R96), and **fluoride SMOOTHS rather than roughens** (R43), so as-grown is the right finish, not a compromise |
| **lap the outer tube in+out, only down to below the viewing window** | ✅ new, and it cuts the lapped area again. **Both surfaces are correctly in the path** — emission crosses ID 8.5 and OD 10 to reach the viewport |

🔴 **But the lap-zone LENGTH is not free to choose: it is the collection field of
view, which is R92.** The zone must span the plasma image plus alignment
tolerance, and that footprint is set by the spectrometer f-number. **R92 now sets
three things, not one** — viewport aperture, trap aperture, and the axial extent
of the most expensive surface finish in the build.

### 🔢 The number entry 139 glossed: the shim is 0.15 mm SHORT

`cav.length_sapphire = 88.12` is labelled *sapphire* but its description says
**"a sapphire OUTER tube"** — inner two still quartz. All-sapphire adds the inner
two's 0.15 mm:

| build | L | |
|---|---:|---|
| all quartz (development) | 88.53 | |
| **sapphire outer only** | **88.12** | ← what `cav.length_sapphire` means |
| **all sapphire (the proposal)** | **≈87.97** | 🔴 **new** |

🔴 **`cav.shim = 0.41 mm` spans quartz → sapphire-outer. The all-sapphire swing is
0.56 mm, so the shim R46 sized is 0.15 mm short of the build we are now choosing.**
Entry 139 said 0.56 mm was "absorbed by the 0.41 mm shim"; 0.56 > 0.41 and it is
not. Re-size the shim to **0.56 mm** — a stock-thickness change, no redesign.

🔑 Same class as every other correction in this record: **an inherited number
reused outside the context of its own description.**

### 🔴 A live trap in `geometry.py`

`--torch-material` help reads `9.4,3.5e-5 sapphire`. **9.4 is ε∥c. The design uses
ε = 11.6**, because with c longitudinal E_φ lies ⊥ c (R32 measured this: c-longitudinal
reproduces isotropic 11.6 exactly). Anyone typing the hint gets **ε 23% low** and a
cavity several mm wrong. Hint corrected to `11.6,3.5e-5`.

⚠️ For the purchase order: **c-axis longitudinal is PREFERRED, NOT MANDATORY** —
R32 withdrew the mandatory claim, because transverse costs +1.1 MHz and 0.11% of a
full m=2 perturbation. Relaxing it helps price and lead time on EFG stock.

### 🔑 The architectural rule: the torch is SEPARABLE from the cavity, and here is the criterion

The user asked to keep torch design separate from resonance-cavity design. That is
not merely a working preference — **it is true, it is measured, and it has a
stated limit.**

✅ **The tubes enter the cavity through exactly two scalars:**

| coupling | magnitude | absorbed by |
|---|---|---|
| ∫(ε−1)\|E_φ\|²dV → **resonant length** | 0.56 mm on 88.53 = **0.63%** | the shim (re-sized above) |
| tanδ → **Q** | −0.8% of total loss (**improves**) | nothing needed |

🔑 **The separation holds BECAUSE the perturbation is sub-1%** — it is a small
parameter, not an assumption. This is the same fact R32 and the brake result both
turn on: *a large dielectric effect where the field is weak is still a small
effect.* If a future tube change pushed the length swing past a few percent, the
separation would stop being valid and would have to be re-earned.

🔴 **THE LIMIT, stated so it is not lost: the PLASMA is not separable.** The torch
sets where the plasma sits (r 4.5–8.5, z −20…10) and the plasma **is the load** —
σ, position and volume determine η. So:

> ✅ tube **materials and walls** → separable, two scalars, one shim
> 🔴 torch-defined **plasma geometry** → NOT separable; it is the coupling problem itself

In the harness that line falls between `--torch-tube`/`--intermediate`/`--injector`/
`--torch-material` (separable) and `--plasma` (not).

### ✅ R97 closes as moot

R97 was *"per-tube materials in geometry.py — all three tubes share one TAG_QUARTZ
region."* All-sapphire means **one material is now CORRECT**, not a limitation. The
region name is wrong, but the physics is right. ⚠️ Note this also removes the
caveat entry 139 ended on — the field-weighted per-tube estimate is no longer
needed for a decision, because there is no longer a mixed build to decide about.

### What is actually still open on the torch

| # | question | status |
|---|---|---|
| **R41** | 🔴 **Coolant-flow interlock: AlF₃ passivation sublimes above 1276 °C.** Loss of coolant strips the protective layer and the tube is then unprotected. RF must cut within one thermal time constant | 🔴 **open — the real tier-1 torch item, and it is a safety interlock, not a material question** |
| **R43b** | Sapphire coupon under *our* conditions (atmospheric N₂, dilute HF aerosol, 500–800 °C) before committing to a production tube. R43's data is low-pressure CF₄ on ALD alumina — close enough to remove the go/no-go, different enough to confirm | open — low |
| **R92** | Spectrometer f-number — now also sets the **lap-zone length** | open — **tier 1** |
| ~~R18~~ | ⛔ **WITHDRAWN as moot** — quartz eliminated 2026-08-15 on fluoride, independently of devitrification | closed |
| ~~R97~~ | ✅ **moot** — one material is correct for an all-sapphire torch | closed |
| ~~R42~~ | ✅ **moot** — Sialon eliminated by entry 69; no need to confirm the D-Torch ceramic | closed |

| # | headline | detail |
|---|---|---|
| 140 | 🔴 **R98 — quartz was already abandoned four days ago; R18 withdrawn as moot; the torch/cavity separation given a criterion** | 🔴 **Entry 139 re-opened a closed question**: quartz died on 2026-08-15 on **fluoride** (Mehlich-3 carries 0.015 M NH₄F → HF in situ; SiF₄ volatilises, AlF₃ passivates self-limitingly at 3–5 nm and SMOOTHS to <1 nm RMS). Devitrification was never binding. **Tier 1 goes 4 → 3 with nothing measured, only read.** ✅ User's proposal = the standing plan; **raw EFG is forced anyway** (sapphire cannot be flame-worked) and fluoride smooths, so as-grown is right for the inner two. 🔴 **Partial lap zone length = collection FOV = R92**, so R92 now sets viewport, trap AND the most expensive finish in the build. 🔴 **`cav.length_sapphire`=88.12 means sapphire OUTER ONLY; all-sapphire is ≈87.97 and the 0.41 mm shim is 0.15 mm short** — re-size to 0.56. 🔴 **`geometry.py` hinted ε=9.4 (∥c) where the design uses 11.6 (⊥c)** — a 23% trap, corrected. 🔑 **Separability is MEASURED, not assumed**: two scalars, 0.63% length and −0.8% loss — but **the plasma is NOT separable**, it is the load. ✅ **R97 and R42 close as moot; R41 coolant interlock is the real open torch item** |

---

## 2026-08-19 — 🔑 R99: the torch is PERMANENT, so the shim is deleted and the development build stops being a proxy

The user: *"less concerned now about supporting two materials, since it's now
basically a permanent feature rather than a swappable part."* Three consequences,
one of them a correction to the whole simulation record.

### ✅ Delete the shim — and it was never RF-neutral

`cav.shim` exists only to convert one cavity body between two torch materials. No
dual-material support → **no shim**. The cavity is machined to
`cav.length_all_sapphire` **87.97 mm** directly.

🔑 **This is better than a part count.** A shim is a seam in the cavity wall, and
seams are mode-selective:

| mode | current across a cap/barrel seam | shim is |
|---|---|---|
| **TE₀₁₁** | **none** — J′₀(χ′₀₁) = 0, no current crosses the corner | invisible |
| TM₀₂₀, TM₁₁₁ | **yes** — TM modes carry current across it | a loss path and an arc site |

✅ So the shim was **invisible to the operating mode and a leak for its rivals** —
the worst possible sign. Deleting it removes a TM loss path, an arcing site, and a
tolerance stack, and costs the operating mode nothing. ⚠️ It also removes the
"commission on a $150 quartz tube, fit sapphire when proven" path as a *mechanical*
option; quartz remains reachable in simulation and on the bench, just detuned.

### 🔴 Every mesh in the record is the QUARTZ development build

| | |
|---|---|
| all meshes to date | `torch_eps = 3.78`, L = 88.53 — **quartz** |
| R44 design point | *"outer tube: sapphire, ε ≈ 11.6"* — **sapphire** |

The gap was legitimate while the shim made the two builds one cavity. **Permanence
removes that justification.** The development build is now a *different resonator*
from the product, and the difference is not uniform across modes:

> 🔑 **The torch sits ON AXIS, where TM modes have E_z and TE₀₁₁ has almost
> nothing.** E_φ ∝ J₁(χ′₀₁r/a) → 0 at the axis, so the torch is nearly invisible to
> TE₀₁₁ (driven ε sensitivity **9.25 MHz**, entry 64) — but TM₀₂₀ and TM₁₁₁ have
> their field maximum exactly where the tubes are. **Torch permittivity is a
> DIFFERENTIAL mode-mover: it changes mode SEPARATIONS, not just f(TE₀₁₁).**

🔴 **And the margin it moves is the tight one.** R44 records **TM₀₂₀ at 5.7 MHz
below the 2.400 band floor** — the guarantee that the amplifier cannot reach it at
all. That 5.7 MHz was computed for the sapphire design point, but **no mesh has
been solved there**, and every mode-landscape result since (interloper ID, groove
trades, TM₁₁₁ at 2.3431) belongs to the quartz cavity.

⚠️ **Do not carry the mode landscape across this boundary.** The TM shift for
ε 3.78 → 11.6 at a = 103.70 is **unmeasured**. Quoting entry 60's −33.9 MHz here
would repeat the standing error: that is the **eigenmode** number, and entry 64
recorded eigenmode and driven disagreeing **3.7×** (33.9 vs 9.25) with **driven
defining the design**.

### ✅ `geometry.py` default flipped to sapphire

`torch_eps` 3.78 → **11.6**, `torch_tand` 1.0e-4 → **3.5e-5**. Simulating quartz by
default would model a cavity we are not building. Quartz stays reachable as
`--torch-material 3.78,1e-4`.

⚠️ **THIS IS A MESH BOUNDARY — the second in two days.** Every mesh before now is
quartz; every mesh after is sapphire. **Do not difference across it.** The sidecar
records `torch_material`, and mesh time now **prints the material by name**,
because a silent default is exactly how the viewport/trap boundary was crossed
unnoticed this morning. The physical group is also renamed `quartz` → `torch` in
the printout (`TAG_QUARTZ` unchanged, so old sidecars still parse).

### 🔑 Permanence converts a CONSUMABLE risk into a SERVICEABILITY risk

The inner wall of the outer tube is **simultaneously the optical surface and the
deposition surface** (C1′ measured 0.46 deposition non-uniformity). A swappable
quartz tube made fouling a consumables problem; a permanent sapphire tube makes it
a **maintenance** problem:

| | |
|---|---|
| material budget | ✅ **30–75 re-laps** available, ID change 0.147% — **EM-invisible** (R40) |
| what is now required | the mount must allow the tube out and back **without disturbing cavity alignment**, against a **±0.2 mm** radius callout |
| what is unknown | the **cleaning interval** — deposition rate on the optical surface has never been estimated |

🔴 **R100 opened**: what is the service interval on the outer tube's inner surface,
and can it be removed and refitted inside the radius tolerance? This is the risk
the permanence decision takes on, and it is the honest cost of deleting the shim.

### Register

| # | question | status |
|---|---|---|
| **R99** | 🔴 **Re-take the mode landscape at the SAPPHIRE point** (ε = 11.6, L = 87.97, a = 103.70). Specifically: does TM₀₂₀ keep its 5.7 MHz clearance below the 2.400 floor? TM modes see the on-axis torch; TE₀₁₁ does not | 🔴 open — **now gates R61, R82 and R86**, which would otherwise characterise the wrong cavity |
| **R100** | Outer-tube service interval and refit repeatability inside ±0.2 mm | open — the cost of permanence |
| ~~cav.shim~~ | ⛔ **deleted as a part** — machine to 87.97 | closed |

| # | headline | detail |
|---|---|---|
| 141 | 🔑 **R99 — the torch is permanent: shim deleted, and the whole mesh record is the wrong material** | ✅ **Shim deleted**, cavity machined to **87.97** — and it was never neutral: **TE₀₁₁ carries no current across a cap/barrel seam (J′₀ = 0) but TM modes do**, so the shim was invisible to the operating mode and a **loss path plus arc site for its rivals**. 🔴 **Every mesh in the record is `torch_eps = 3.78` quartz while the R44 design point is sapphire** — legitimate only while the shim made them one cavity. 🔑 **The torch is ON AXIS, so it is a DIFFERENTIAL mode-mover**: E_φ ∝ J₁ → 0 at the axis makes it nearly invisible to TE₀₁₁ (driven 9.25 MHz) while TM₀₂₀/TM₁₁₁ peak exactly there — it moves mode SEPARATIONS. 🔴 **TM₀₂₀'s clearance is only 5.7 MHz below the band floor and has never been solved at the sapphire point** → **R99 gates R61/R82/R86**. ⚠️ Do not quote entry 60's −33.9 MHz: that is eigenmode, and entry 64 recorded a **3.7× eigenmode/driven disagreement** with driven defining the design. ✅ **Default flipped to sapphire; MESH BOUNDARY, second in two days** — material now printed at mesh time. 🔴 **R100**: permanence turns fouling from a consumables cost into a service problem on the surface that is both optical and deposition-facing |

---

## 2026-08-19 — 🔴 R101: `--torch-material` never reached the solver. R99 was two hours from reporting "sapphire changes nothing"

### What was wrong

`geometry.py --torch-material eps,tand` fed **two** things: the mesh SIZING
(`h_qtz = min(mesh_size(torch_eps, ...), torch_wall)`) and the sidecar label. It
fed **nothing to Palace.** `solveconf.driven` bound attribute 2 from the template:

```
w890.json:  {"Attributes": [2], "Permittivity": 3.78, "LossTan": 0.0001}
```

So a sapphire mesh **solved as quartz**.

🔴 **And nothing downstream could have noticed**, because the sizing is clamped by
the wall thickness in both cases, so the two meshes came out **byte-identical**:

```
md5sum s99qz.msh s99sa.msh  ->  1 unique hash
```

Identical mesh, identical material, different label. The run would have measured
**Δf = 0 for every mode** and reported that torch permittivity does not matter —
a false negative on the exact question R99 exists to answer.

⚠️ **The null control would have passed.** B vs C must agree on TM₀₂₀ because
dTM₀₂₀/dL = 0; with the material silently identical they would have agreed *for
the wrong reason*. **A control that passes trivially is not a control**, and this
one was designed this morning specifically to catch a bad measurement.

### 🔑 The class, and it is R50's own

`solveconf.py` exists because of exactly this. Its docstring:

> *"Everything here is derived from `<mesh>.meta.json` … The config cannot
> disagree with the mesh because it is not told anything the mesh did not say."*

R88 added `torch_material` to the sidecar. **Nothing was ever added to the
consumer.** So the sidecar recorded the truth, the config ignored it, and the
provenance chain *looked* complete — `results.py` faithfully reported
`torch_material: [11.6, 3.5e-05]` for a solve that used 3.78.

> 🔑 **Adding a field to a provenance record is not the same as binding it to the
> thing that consumes it.** A sidecar entry nobody reads is a claim, not a fact.

### ✅ Bounded: nothing in the record is affected

The historical sapphire work did **not** use this path — it used hand-written
configs, and they are still on disk:

| ε at attribute 2 | configs | |
|---:|---:|---|
| 3.78 | 251 | quartz |
| **11.6** | **7** | `s_116`, `b5_lon`, `s_ani` — R32/R33/R44 |
| 9.4 | 2 | `b5_tra`, `s_tra` — R32's transverse c-axis case |
| 8.0 / 6.0 | 10 | Sialon (R17) |

✅ So `cav.length_sapphire`, the **9.25 MHz driven ε-sensitivity**, and R32's
anisotropy result all stand. **`--torch-material` was added in R88 as a geometry
parameter and no driven rig had ever passed it** — `rig_r99.py`, written today,
was the first. The bug was latent from birth and had no victims.

### How it was caught, which is the uncomfortable part

Not by a test, not by the guard, not by review. By noticing in an `ls` that two
mesh files had **the same byte count**, and being suspicious enough to `md5sum`
them. Ninety seconds earlier the run had printed
`✅ all 3 cases at a COMMON size-factor 0.96` — a green line, correctly reported,
on a sweep that was measuring nothing.

⚠️ **The pre-run criteria (declared this morning, in the driver docstring) did not
help either.** They constrained how the ANSWER would be judged; none of them asked
whether the CASES DIFFER. That is the gap: a criterion about the result cannot
catch a run where the independent variable was never applied.

### The fixes

1. ✅ **`solveconf` now binds the torch material from the sidecar** — and if a
   mesh has none (pre-R88), it says so loudly and names the template value it fell
   back to, rather than substituting silently.
2. ✅ **A guard in the rig that CAN pass**: assert the written config's attribute-2
   permittivity equals the mesh's. ⚠️ Deliberately not the earlier `meta["groove"]`
   mistake — *"a check that cannot pass is not a safety net; it is a second way to
   lose the answer."* This one was verified to pass on all three cases before
   relaunching.
3. ✅ Verified end to end: `s99qz` → 3.78/1e-4, `s99sa`/`s99pr` → 11.6/3.5e-5.

### ✅ One thing the bug leaves behind is genuinely useful

Because the mesh sizing is wall-clamped, **A and C are byte-identical meshes**. So
the material comparison now has **ZERO mesh confound** — not a common size factor,
not a matched element count, the *same file*. That is the cleanest control this
harness has ever had for a material question, and it exists by accident.

| # | headline | detail |
|---|---|---|
| 142 | 🔴 **R101 — `--torch-material` never reached the solver; R99 was two hours from a false negative** | 🔴 The flag fed **mesh sizing and the sidecar label only**; `solveconf` bound attribute 2 from the template's **3.78/1e-4**, so a sapphire mesh **solved as quartz**. Sizing is wall-clamped, so the meshes were **BYTE-IDENTICAL** — the run would have reported **Δf = 0 for every mode** and concluded torch permittivity does not matter. ⚠️ **The null control would have PASSED, for the wrong reason** — B and C agree on TM₀₂₀ trivially when the material is secretly the same. 🔑 **R50's own class**: `solveconf` exists so the config cannot disagree with the mesh, but **R88 added `torch_material` to the sidecar and never added it to the consumer** — *adding a field to a provenance record is not the same as binding it*. ✅ **Bounded — no victims**: historical sapphire used hand-written ε=11.6 configs (7 on disk), and **no rig had ever passed the flag before today**. ⚠️ **Caught by two mesh files having the same byte count**, not by any check; the pre-declared criteria judged the ANSWER and never asked whether the CASES DIFFER. ✅ Now bound from the sidecar, with a loud fallback for pre-R88 meshes and a rig-side assert **verified to pass** before relaunch. ✅ Silver lining: A vs C is now a material change on the **same mesh file** — zero confound |

---

## 2026-08-19 — ✅ R99/R99b CLOSED: TM020 falls 190.9 MHz at the sapphire point. It stops being a design constraint, and it stops binding the radius tolerance

Six driven solves on three meshes (two windows), all criteria declared before the
run in `rig_r99.py`, all labels produced by a re-runnable `evaluate.r99()`.

### The measurement

| | quartz ε 3.78 | sapphire ε 11.6 | Δ |
|---|---:|---:|---:|
| **TM₀₂₀** (bore-E 2.36 → 2.27%) | 2.37330 | **2.18240** | 🔑 **−190.9 MHz** |
| **TE₀₁₁** (bore-E 0.042 → 0.034%) | 2.39945 | 2.39365 | **−5.8 MHz** |
| bore-H mode at 2.34 | 2.34195 | 2.32700 | −15.0 MHz |
| bore-H mode at 2.43 | 2.43080 | 2.42215 | −8.7 MHz |
| TE₀₁₁ **Q₀** | 34,585 | **34,682** | ✅ +0.3% |

🔑 **TM₀₂₀ moves 33× further than TE₀₁₁.** The differential-mode-mover prediction
is confirmed emphatically: E_z ∝ J₀ is maximum on axis where the torch is, E_φ ∝ J₁
vanishes there, and the ratio of the shifts is the ratio of the field at the tube.
Q₀ rising confirms the tanδ prediction (1.0e-4 → 3.5e-5) in the right direction.

⚠️ **All three cases share a byte-identical mesh family** (s99qz/s99sa are the SAME
FILE — R101), so the material comparison has zero mesh confound.

### ✅ The criteria, as declared

| | | |
|---|---|---|
| **CONTROL** | quartz in the low window shows max bore-E **0.119%**, no TM₀₂₀ | ✅ the low window reads correctly; the absence in sapphire was real, not a windowing artefact |
| **NULL CONTROL** | dTM₀₂₀/dL = 0 → L 88.53 vs 87.97 agree to **0.40 MHz** (2 grid steps) while TE₀₁₁ moves **5.85 MHz** for the same ΔL | ✅ **15× discrimination** — the control now passes for the RIGHT reason, unlike R99's first attempt where it would have passed trivially |
| **PRIMARY** | clearance below 2.400: **195.4 MHz** against a **4.4 MHz** threshold | ✅ **passes by 44×** |
| **FRAME** | differential against `tm020.f_converged`, never raw vs 2.400 | ✅ f_conv(sapphire) = **2.20462 GHz** |

### 🔑 The consequence nobody asked for: the radius tolerance was TM₀₂₀'s

`cav.radius`'s **±0.2 mm** callout is the tightest machining requirement in the
design, and its own provenance says why:

> *"set by dTM₀₂₀/da = −22 MHz/mm against TM₀₂₀'s headroom below the 2.400 band
> floor … the tolerance BUDGET is ±0.27 mm"* (R49)

🔢 At the sapphire point, the radius error needed to lift TM₀₂₀ to 2.400 GHz is
**195.4 / 22 = 8.88 mm** — **44× the drawing callout**, and 8.6% of the radius.

> ✅ **TM₀₂₀ no longer binds the radius tolerance.** The constraint that set the
> hardest number on the drawing is gone, because the torch we are now building
> loads the mode we were afraid of. Sapphire was chosen for fluoride resistance
> and optical survival; **the RF benefit is incidental and larger than either.**

🔴 **But do NOT relax the callout yet.** R49's budget was TM₀₂₀-driven; with TM₀₂₀
removed, the next binding constraint on radius is **unidentified**. "No longer
bound by X" is not "unbound". → **R102**.

### What did NOT go as predicted

🔴 **The 2.342 mode moved 15.0 MHz — 2.6× further than TE₀₁₁ — and I predicted it
would be nearly unmoved.** If it is TM₁₁₁, its E_z ∝ J₁(χ₁₁ r/a) and TE₀₁₁'s
E_φ ∝ J₁(χ′₀₁ r/a) share **the same χ = 3.8317**, so they should see the torch
alike. They do not, by a factor of 2.6. Either the identification is wrong or the
mechanism is not the one I gave. **Unexplained, and recorded as unexplained.**

⚠️ **dTE₀₁₁/dL measures −10.4 MHz/mm here against the recorded −13.06** (5.85 MHz
over 0.56 mm). This mesh family carries the viewport and trap that the R46 family
lacked, so some difference is expected — but 20% on the coefficient the entire
tuning budget rests on is more than a mesh-family note. → **R103**.

### Register

| # | question | status |
|---|---|---|
| ~~R99~~ | ✅ **CLOSED** — TM₀₂₀ −190.9 MHz, clearance 195.4 MHz, all criteria pass. **R61/R82/R86 are unblocked and must run on the sapphire meshes** | closed |
| **R102** | With TM₀₂₀ gone, **what now binds the ±0.2 mm radius tolerance?** The tightest number on the drawing has lost its justification | 🔴 open — new, and it is a COST question as much as an EM one |
| **R103** | dTE₀₁₁/dL is **−10.4 MHz/mm** in the viewport+trap family vs **−13.06** recorded. Re-derive, because `tune.settable_range` and the machining budget both use it | 🔴 open — new |
| **R104** | The 2.342 bore-H mode moves 2.6× more than TE₀₁₁ despite sharing χ = 3.8317. Identify it (R82's N=24 DFT is the instrument) | open |

| # | headline | detail |
|---|---|---|
| 143 | ✅ **R99 CLOSED — TM₀₂₀ falls 190.9 MHz at the sapphire point and stops constraining the design** | 🔑 **TM₀₂₀ −190.9 MHz vs TE₀₁₁ −5.8 MHz: a 33× differential**, exactly as the on-axis field argument predicts (E_z ∝ J₀ max on axis, E_φ ∝ J₁ zero there). ✅ **Clearance below the 2.400 floor = 195.4 MHz against a 4.4 MHz threshold — passes by 44×**, computed differentially against `tm020.f_converged` and never raw-vs-absolute. ✅ **Null control passes for the RIGHT reason**: 0.40 MHz across a ΔL that moves TE₀₁₁ by 5.85 MHz, a 15× discrimination — where R99's first attempt would have passed it trivially on byte-identical materials (R101). ✅ Q₀ **rises** 34,585 → 34,682, confirming tanδ 1.0e-4 → 3.5e-5. 🔑 **THE RADIUS TOLERANCE WAS TM₀₂₀'s**: ±0.2 mm was set by dTM₀₂₀/da = −22 MHz/mm against its headroom, and reaching 2.400 now needs an **8.88 mm** radius error — 44× the callout. **Sapphire was chosen for fluoride and optics; the RF benefit is incidental and larger than both.** 🔴 But "no longer bound by X" is not "unbound" → **R102**. 🔴 **Two things did not go as predicted**: the 2.342 mode moved 2.6× more than TE₀₁₁ despite sharing χ = 3.8317 (**unexplained**, R104), and **dTE₀₁₁/dL measures −10.4 vs −13.06 recorded** (R103) — the coefficient the whole tuning budget uses |

---

## 2026-08-19 — ✅ R103 CLOSED: there was never a discrepancy. A 2-point slope has no error bar, and mine was ±4.9 MHz/mm

Eight driven solves, two ladders, criteria declared in `rig_r103.py` before the
run. The result dissolves the question that prompted it — and convicts the
measurement that raised it.

### The ladders

| ladder | | slope | per-point σ |
|---|---|---:|---:|
| **A** | sapphire, viewport+trap **ON** (the product), 5 lengths over 2 mm | **−11.89 ± 1.21 MHz/mm** | 1.92 MHz |
| **B** | sapphire, viewport+trap **OFF**, 3 lengths, same span | −12.19 ± 2.16 MHz/mm | 3.05 MHz |
| R46 | quartz, no optics, 3 lengths | −13.06 | (0.9 MHz implied) |
| R99 | **2 points over 0.56 mm** | −10.40 | — |

### 🔑 Everything agrees. The disagreement was an artefact of not having an error bar

| comparison | | |
|---|---:|---|
| A vs R46's −13.06 | **0.97σ** | ✅ consistent |
| A vs B (does the viewport+trap matter?) | **0.12σ** | ✅ consistent — the optical features change nothing |
| A vs R99's −10.40 | 1.23σ | ✅ consistent |

🔢 **And R99's own uncertainty, computed properly**: per-point σ = 1.92 MHz over a
**0.56 mm** baseline gives **σ_slope = 1.92·√2 / 0.56 = ±4.9 MHz/mm**. So R99
measured **−10.4 ± 4.9**, which is consistent with −13.06, with −11.89, and with
almost anything else. **It never had the power to resolve the coefficient**, and I
reported it to two significant figures and opened a register item about the gap.

> 🔑 **A two-point slope cannot detect its own failure** — no residual, no σ, no
> way to separate an outlier from a trend. That was in R103's docstring as the
> justification for re-taking it. It turned out to be the entire finding.

⚠️ **R99's specific pair re-measures at −10.45 here**, reproducing the 2-point
value exactly on new meshes — so it was not a fluke, it was a **locally biased
baseline**: two adjacent points whose independent mesh errors happened to lean the
same way. Reproducibility is not accuracy.

### 🔴 And the gate I declared this morning could not pass

I set a **0.5 MHz** linearity gate, reasoning from R46's three L_target values
agreeing to 0.07 mm. But **per-mesh discretisation scatter here is σ = 1.9–3.1 MHz**
— every ladder point is a *separate mesh* carrying independent error. A gate below
the noise floor **fails regardless of the physics**, and the evaluator duly printed
🔴 *"NOT linear; a single coefficient is wrong"* — which is false.

> ⚠️ **Same lesson as the `meta["groove"]` assert: a check that cannot pass is not
> a check.** I recorded that lesson on 2026-08-19 and re-made the mistake the same
> day, in the layer specifically built because it keeps being wrong.

✅ Residual signs are `+ + − − +` — **scatter, not curvature.** There is no evidence
of nonlinearity. `evaluate.r103()` now detects a sub-noise gate and says so instead
of returning a verdict, and `_fit` returns σ_point and σ_slope so no slope from
this harness is ever again quoted bare.

### ✅ Design impact: none

`tune.settable_range` = 23 MHz = 16.4 lit drift + 5.1 machining. The machining term
scales with this coefficient: 11.89/13.06 = **0.91**, so 5.1 → **4.6 MHz** and the
total goes **23 → 22.5 MHz**. Inside the rounding already in the spec. 🔑 **Nothing
downstream moves**, and R103's alarm — that a 20% error was propagating into the
tuning budget and the machining tolerance — was itself the error.

### What this costs and what it buys

⚠️ **The coefficient cannot be pinned much better by this method.** σ_slope =
σ/√Sxx, so with ~2 MHz of per-mesh noise a 2 mm ladder buys ±1.2 MHz/mm and a 10 mm
ladder would buy ±0.24 — but over 10 mm the neighbouring mode (25–30 MHz above,
tracked cleanly here at every length) would be crossed and nonlinearity would
become real. **±1.2 MHz/mm is close to the practical floor for separate meshes.**

✅ **Mode identity was clean throughout** — TE₀₁₁ held bore-H 1.35–1.38% and bore-E
0.032–0.035% at all five lengths, with the rival 25–30 MHz above and moving the
same way. No hop, no crossing; the identity gate never had to fire.

| # | question | status |
|---|---|---|
| ~~R103~~ | ✅ **CLOSED — no discrepancy.** dTE₀₁₁/dL = **−11.89 ± 1.21 MHz/mm**, consistent with R46 at 0.97σ. Viewport+trap change nothing (0.12σ). No design impact | closed |
| **R105** | 🔑 **Per-mesh discretisation noise is σ ≈ 2 MHz and has never been characterised.** It sets the floor on every frequency difference this harness reports, and several closed results are differences of that order | 🔴 open — **methodological, and it bounds the whole record** |

| # | headline | detail |
|---|---|---|
| 144 | ✅ **R103 CLOSED — the 20% discrepancy never existed; a 2-point slope with no error bar invented it** | 🔑 **dTE₀₁₁/dL = −11.89 ± 1.21 MHz/mm** (5 lengths, 2 mm span), **consistent with R46's −13.06 at 0.97σ**. ✅ **Viewport+trap change nothing** — ladders A and B differ by 0.12σ, so the attribution question had no gap to attribute. 🔢 **R99's 2-point value was −10.4 ± 4.9** once per-point σ = 1.92 MHz is propagated over its 0.56 mm baseline — it never had the power to resolve the coefficient, and I quoted it to two figures and opened a register item. ⚠️ Its pair **re-measures at −10.45 on fresh meshes**, so it was reproducible and still wrong: two adjacent points whose mesh errors leaned the same way. 🔴 **My declared 0.5 MHz linearity gate sat BELOW the 1.9–3.1 MHz per-mesh noise floor and could not pass** — the evaluator printed "NOT linear", which is false; residual signs `+ + − − +` are scatter, not curvature. **Same "a check that cannot pass is not a check" lesson recorded earlier the same day.** ✅ Design impact **nil**: the machining term moves 5.1 → 4.6 MHz, total 23 → 22.5. 🔴 **R105 opened — per-mesh noise σ ≈ 2 MHz is uncharacterised and bounds every frequency difference in this record** |

---

## 2026-08-19 — ⚠️ R105 PARTIALLY CHARACTERISED: σ = 1.3–3.3 MHz, the two routes disagree, and the cross-check I declared says that means we do not know

Nine driven solves, two ladders, criteria declared in `rig_r105.py`. The primary
number came out; **the cross-check that was supposed to validate it failed**, and
the declared consequence of that is that σ is bounded, not measured.

### ✅ The gate that ran before any solve

Ladder N perturbs L by ±7.5 µm against ~1.5 mm elements, so it might have produced
identical meshes and reported σ = 0 — flattering and false.

| | |
|---|---|
| distinct md5 | **5/5** |
| distinct tet counts | **5/5** (164,216 → 165,295, a 0.65% spread) |

✅ The meshes genuinely differ. This is the R101 lesson wired in as a gate rather
than remembered, and it cost nothing because it ran before the hour of solving.

### 🔑 The solver contributes ZERO. All of it is meshing

`r105c0p96` and `r105n88p53` are the **same geometry at the same size factor**, so
gmsh produced a byte-identical mesh (md5 `7b1236e2ce`) — and they were solved as
two independent cases:

| | |
|---|---|
| f, both | **2.393650 GHz**, difference **+0.0000 MHz** |

✅ **Same mesh → same answer, exactly.** So there is no solver noise to separate
out: 100% of the scatter below is mesh *generation*. That was an accident of tag
naming and it is the cleanest control in the run.

### LADDER N — realisation noise, geometry effectively fixed

| L (mm) | tets | f | detrended |
|---:|---:|---:|---:|
| 88.5225 | 164,942 | 2.39440 | −0.96 |
| 88.5262 | 164,848 | 2.39560 | +0.29 |
| 88.5300 | 164,700 | 2.39365 | −1.62 |
| 88.5338 | 165,295 | 2.39700 | +1.78 |
| 88.5375 | 164,216 | 2.39570 | +0.52 |

🔑 **σ_realisation = 1.33 MHz.** Peak-to-peak **3.40 MHz** against a true
geometric change of **0.18 MHz** — the mesher moves the answer **19× further than
the physics does** across this span.

### LADDER C — convergence, and it is not a clean noise estimator

| sf | tets | f | resid |
|---:|---:|---:|---:|
| 1.20 | 93,571 | 2.37325 | −1.12 |
| 1.06 | 126,712 | 2.39125 | +3.30 |
| 0.96 | 164,700 | 2.39365 | −2.97 |
| 0.90 | 193,650 | 2.40220 | +0.79 |

✅ Monotonic with refinement — coarse sits low, as predicted. σ_C = **3.29 MHz**.

⚠️ **sf = 1.00 and 0.85 failed to mesh at all** ("Failed to reach critical value
… ScaledJac"), so *mesh constructibility is itself size-factor dependent* — 2 of 6
candidates were lost, which is why `meshsweep` tries a list.

### 🔴 The cross-check failed, and I am not going to overrule it

> σ_N = 1.33, σ_C = 3.29, **ratio 2.48× against a declared 2× gate.**

The declared consequence was: *"if they disagree by more than 2×, neither is
characterised and the result is that we do not know."* **That is the result.**

I can say *why* they differ, and the asymmetry is real — ladder C has **4 points
and 2 parameters, so 2 degrees of freedom**, and its residuals also absorb any
error in my assumed h² convergence law, whereas ladder N has 5 points about a mean
with a known 0.18 MHz trend and 4 dof. So **σ_N is the better-conditioned estimate
and σ_C is an upper bound**. But "the estimator I prefer is better conditioned" is
an argument, not a measurement, and this record has been burned by exactly that
move. **σ is bounded at 1.3–3.3 MHz until a wider convergence ladder settles it.**

### 🔴 The consequence, and one result of mine takes damage

| claim | | at σ_N | at σ_C |
|---|---:|---:|---:|
| R99 TM₀₂₀ quartz→sapphire | 190.9 MHz | 143.8σ | 58.1σ ✅ |
| R104 the 2.342-mode gap | 9.2 MHz | 6.9σ | 2.8σ ✅ |
| **R99 TE₀₁₁ quartz→sapphire** | **5.8 MHz** | 4.4σ | **1.8σ** 🔴 |
| R99b null control B vs C | 0.40 MHz | — | 0.1σ ✅ passes |

🔴 **R99's TE₀₁₁ shift is not resolved at the conservative σ.** I reported
"TE₀₁₁ barely moves, −5.8 MHz" as a confirmed prediction; at σ_C it is a **1.8σ
observation**, which is not a measurement of anything. The *direction* survives
because ladder C's monotonicity is independent, but the **magnitude should not be
quoted without its error bar.** TM₀₂₀'s 190.9 MHz and R99's overall conclusion are
untouched — 58σ at the most pessimistic estimate.

⚠️ **And a labelling bug I introduced and fixed**: the first version of the
consequence printer flagged R99b's null control **🔴 UNRESOLVED** for landing at
0.1σ. **A null control passes by being INSIDE the noise** — a claimed difference
and a claimed agreement have opposite pass conditions. Same class as R103's
sub-noise gate: the criterion was wrong, not the data. Now handled explicitly.

### 🔴 R106 — the recorded convergence offset may be badly low

Extrapolating ladder C to h → 0 gives **f∞ = 2.43619 GHz**, i.e. **+42.5 MHz above
the sf = 0.96 solve**. The record's `offset.te011` is **+24.54 MHz**.

⚠️ **This is a 4-point extrapolation on an assumed h² law with 2 dof, in a
different mesh family (sapphire, viewport+trap) from the one the offset was
measured in.** It is not evidence that 24.54 is wrong. It *is* enough to say the
offset has never been validated in the family we now build, and every "converged"
frequency in the record passes through it.

| # | question | status |
|---|---|---|
| **R105** | ⚠️ **PARTIALLY CLOSED** — σ = **1.3–3.3 MHz**, solver contributes zero, cross-check failed. Needs a wider convergence ladder (≥6 factors) to settle σ_C and test the h² law | open — reduced from "uncharacterised" to "bounded" |
| **R106** | 🔴 **Is `offset.te011 = +24.54` right for the sapphire/viewport family?** Ladder C extrapolates +42.5. Every converged frequency in the record passes through this constant | 🔴 open — new |

| # | headline | detail |
|---|---|---|
| 145 | ⚠️ **R105 — mesh scatter is σ = 1.3–3.3 MHz; the solver contributes exactly zero; the cross-check failed and I let it fail** | ✅ **Cases-differ gate passed before solving**: 5/5 distinct md5, tets spanning 0.65%. 🔑 **Solver is deterministic** — a duplicated mesh (same md5, two tags) gave **+0.0000 MHz**, so all scatter is mesh GENERATION. 🔑 **σ_N = 1.33 MHz** from a 15 µm ladder whose true frequency change is 0.18 MHz — **the mesher moves the answer 19× further than the physics**. ⚠️ **σ_C = 3.29 MHz**, but from 4 points / 2 dof and contaminated by the assumed h² law. 🔴 **Cross-check 2.48× against a declared 2× gate → σ is BOUNDED, not measured**; σ_N is better-conditioned but "the estimator I prefer" is an argument, not a measurement. 🔴 **R99's TE₀₁₁ −5.8 MHz is 1.8σ at the conservative σ** and should not have been quoted bare; TM₀₂₀'s 190.9 MHz survives at **58σ**. ⚠️ **2 of 6 size factors would not mesh at all** — constructibility is itself variable. ⚠️ Fixed a labelling bug that called a null control "UNRESOLVED" for passing: **agreements pass by being inside the noise, differences by exceeding it.** 🔴 **R106 opened — `offset.te011 = +24.54` extrapolates to +42.5 here** and has never been validated in the family we now build |

---

## 2026-08-19 — 🔴 R106 STOPPED mid-run, and a course correction: three registers in a row were self-generated

**Killed the order-2 run.** R106 cannot change a decision. `offset.te011` is used
for band placement; converged TE₀₁₁ is 2.44146 against an ISM ceiling of 2.500 —
**58 MHz of margin**, and the largest error my own weak extrapolation suggested was
**18 MHz**. An offset error would have to exceed ~40 MHz to flip anything, and the
same is true of mode separations now that TM₀₂₀ has 195 MHz of clearance. Measuring
it more precisely buys nothing.

### 🔑 The pattern, named

| register | opened by | outcome |
|---|---|---|
| **R103** | R99's 2-point slope, quoted bare | **no discrepancy existed** — all values agreed within noise |
| **R105** | R103's residual | σ bounded 1.3–3.3, cross-check failed |
| **R106** | R105's weak extrapolation | **premise withdrawn on reading** — two different limits compared |

> 🔴 **R103 and R106 both closed by dissolving their own premise.** That means the
> premises were artefacts of my own imprecision — a slope reported without an
> error bar, then a limit compared against a different limit — not real problems.
> **I generated the questions I then spent hours answering.**

⚠️ This is not the same as R101, which was a live bug that would have produced a
false result and had to be fixed. The distinction worth keeping: **fix errors that
corrupt results; do not go metrology-hunting.** R105's σ = 1.3–3.3 MHz is worth
having — it retroactively qualified R99's TE₀₁₁ claim — and that is where the chain
should have stopped.

### ✅ And the one question that could have justified more EM work is dead on reading

With TM₀₂₀ 195 MHz clear (R99), does the mode filter still earn its ~5.6% of Q?

🔴 **No — it was never TM₀₂₀'s.** `match.filter_vs_coupler_split`: *"filter controls
degeneracy, coupler sets the floor."* The filter exists for **TM₁₁₁**, the exact
χ′₀₁ = χ₁₁ = 3.8317 degeneracy:

| | |
|---|---|
| TM₁₁₁ **unfiltered** | **2.40022** — sitting ON the 2.400 ISM floor, i.e. reachable |
| TM₁₁₁ filtered | 2.35094 — the filter moves it **49.3 MHz** |
| does sapphire help? | **No.** TM₁₁₁'s E_z ∝ J₁ vanishes on axis, so the torch barely touches it — R99 measured 15.0 MHz against TM₀₂₀'s 190.9 |

✅ **The filter stays.** Answered by reading the record in two minutes, not by a run
— which is the point.

| # | headline | detail |
|---|---|---|
| 146 | 🔴 **R106 stopped; the R103→R105→R106 chain was self-generated** | **Killed mid-run**: `offset.te011` feeds band placement, which has **58 MHz of margin** against a possible **18 MHz** error — it cannot flip a decision. 🔑 **R103 and R106 both closed by dissolving their own premise**, so the premises were artefacts of my own imprecision (a bare 2-point slope; then two different limits compared), not real problems. ⚠️ Distinct from **R101**, a live bug that would have produced a false result — **fix what corrupts results, do not go metrology-hunting**. R105's σ = 1.3–3.3 MHz was the worthwhile output and the chain should have ended there. ✅ **Mode filter question closed by reading**: it was never TM₀₂₀'s — `filter controls degeneracy`, and **TM₁₁₁ unfiltered sits at 2.40022, ON the ISM floor**; the filter moves it 49.3 MHz and **sapphire does not help** (E_z ∝ J₁ = 0 on axis). **The filter stays.** |

---

## 2026-08-20 — ✅ METHODOLOGY.md added; the same-mesh rule promoted; R104 dropped

The user: *"sometimes it feels like we're overfitting to gmsh or palace instead of
answering physics questions, and it's hard to tell which is which."* Three actions.

### ✅ `METHODOLOGY.md` — tool lessons, gathered from 146 entries

A fourth working artifact (regenerated, not appended). Environment; determinism
and the noise floor; the same-mesh rule; gmsh (size factors, constructibility,
clamps, sidecar-is-not-a-binding); Palace (orders, offsets, frames, the 2×
conventions, eigenmode-vs-driven, band and step); where nothing is measurable;
failure modes that look like results.

### 🔑 The same-mesh rule, promoted to a standing principle

Because the solver is deterministic and **all** error is mesh generation, a
difference taken on ONE mesh is good to 0.02 MHz while any cross-mesh difference
carries 1.3–3.3 MHz. Material, solver order, excitation and boundary conditions
can be same-mesh; **geometry cannot.** R99 is the strongest result in the record
because its two meshes were byte-identical; R103 failed because a length ladder
forces a new mesh per point.

⚠️ **And R105 partly re-measured what was already on disk.**
`reproducibility.mesh_to_mesh_scatter` (1.5 MHz) and `reproducibility.same_mesh`
(0.02 MHz) predate it. R105's genuinely new contributions were the *h*-ladder, the
**exact** 0.0000 MHz determinism proof, `mesh.constructibility`, and the design
implication above. **The same failure as R98's**: re-deriving instead of reading.
🔑 That is now the argument for `METHODOLOGY.md` existing at all — a 619 KB
append-only trail cannot be read before every run, so the reusable parts must be
lifted out into something that can.

### ⛔ R104 dropped

The 2.342 mode moving 2.6× more than TE₀₁₁: **no closed-form reason** (it shares
χ = 3.8317 with TE₀₁₁ and should behave alike), **cross-mesh**, and **2.8σ**
against the R105 floor. That is the artifact profile, not a finding. Dropped
rather than chased — and the ordering rule that produced this call is now
recorded: **a result needs a closed-form reason before it earns a run.**

| # | headline | detail |
|---|---|---|
| 147 | ✅ **METHODOLOGY.md added; same-mesh rule promoted; R104 dropped** | 🔑 **Same-mesh differences are good to 0.02 MHz; cross-mesh differences carry 1.3–3.3 MHz** — material/order/excitation/BC can be same-mesh, **geometry cannot**. R99 was accidentally byte-identical and is the record's strongest result; R103's length ladder could not be and drowned. ⛔ **R104 dropped**: no analytic reason + cross-mesh + 2.8σ = artifact profile. ⚠️ **R105 partly re-measured `reproducibility.mesh_to_mesh_scatter` and `same_mesh`, which already existed** — same re-derivation failure as R98, and the reason a 619 KB trail needs a lifted-out reference |

---

## 2026-08-20 — 🔑 R107: the unfiltered cavity has NO TE₀₁₁ — it has two hybrids. The filter's job is preventing mixing, not shifting frequency. And a sapphire filter is WORSE.

Three filter materials on **one mesh** (`s99sa.msh`, attribute 8), so mesh error is
common-mode and the solver is deterministic — these differences are exact.

| case | ε | tanδ | TE₀₁₁ | Q₀ | bore-E |
|---|---:|---:|---:|---:|---:|
| **quartz** | 3.78 | 1.0e-4 | 2.39365 | **34,682** | **0.034%** |
| **none** | 1.0 | 0 | 2.38935 | 27,412 | 0.103% |
| **sapphire** | 11.6 | 3.5e-5 | 2.38085 | 31,500 | 0.031% |

### 🔑 The unfiltered cavity does not contain a TE₀₁₁ mode

Filtered, the two bore-H modes are cleanly separated and cleanly *typed*:

| | f | bore-E | Q₀ |
|---|---:|---:|---:|
| TM₁₁₁ | 2.32700 | 0.247% | 19,692 |
| TE₀₁₁ | 2.39365 | 0.034% | 34,682 |

Unfiltered, they are 18.6 MHz apart and **both are mixtures**:

| | pure TE₀₁₁ | pure TM₁₁₁ | **mean** | hybrid A | hybrid B | **mean** |
|---|---:|---:|---:|---:|---:|---:|
| bore-E | 0.034% | 0.247% | **0.141%** | 0.103% | 0.179% | **0.141%** |
| Q₀ | 34,682 | 19,692 | 27,187 | 27,412 | 28,294 | 27,853 |

> 🔑 **The hybrids' bore-E averages to 0.141% — exactly the mean of the two pure
> modes.** Character is conserved and split, which is the textbook signature of a
> two-mode avoided crossing. Q behaves the same way. **Without the filter there is
> no TE₀₁₁ to operate; there are two half-TE₀₁₁/half-TM₁₁₁ modes.**

✅ **So the filter's value is NOT a frequency shift and NOT a loss trade — it is
preventing hybridisation.** Removing it costs **21% of TE₀₁₁'s Q**, and none of
that is dielectric loss: it is the mode becoming half TM₁₁₁, whose Q is 19,692.

🔴 **The recorded "quartz filter costs 5.6% of Q" (R39) is not reproduced.**
Same-mesh, removing the filter *lowers* Q by 21% — opposite sign, 4× the size.
R39 must have compared against something else (most likely the groove, not bare).
⚠️ The 5.6% and the groove's 6.0% gain both sit under the 6.9% cross-mesh Q floor
anyway, which is why this was worth re-taking.

### 🔴 A sapphire filter is WORSE than quartz — keep quartz

| | |
|---|---|
| TE₀₁₁ Q₀ | 34,682 → 31,500, **−9.2%** |
| TE₀₁₁ f | −12.8 MHz (more loading, as expected) |
| mode purity | bore-E 0.031% vs 0.034% — both clean, so the comparison is valid |

🔑 **ε = 11.6 pulls more field into the annulus than the 3× lower tanδ recovers.**
I predicted sapphire would be strictly better on both axes; it is worse on Q. The
prediction was wrong because I reasoned from tanδ alone and ignored that the field
concentration scales with ε too.

✅ **And the extra separation it buys has no value**: TM₁₁₁ is already 66.7 MHz
away with quartz, and R90 measured rivals taking <0.5% at the drive frequency.
**Sapphire buys margin we do not need and costs 9.2% of Q. The filter stays fused
quartz** — the one part of the assembly that should NOT follow the torch.

⚠️ **No separation number for sapphire**: TM₁₁₁ left the 2.30–2.46 window entirely
(only two modes returned). Predictable in hindsight — 3× the ε pushes it 3× further
— and it is *"absent from a window is not absent"* for the fourth time. **No claim
is made about sapphire's separation.**

### 🔴 My degeneracy guard was mis-specified — again a criterion, not the data

I declared a guard at **7 MHz of separation**. The unfiltered case landed at
**18.6 MHz**, so the guard did not fire — yet the modes were plainly hybridised.

> 🔑 **Separation is the wrong indicator. Mode CHARACTER is the right one.**
> Hybridisation shows up as bore-E moving toward the mean of the two parents, and
> it did so unmistakably (0.034 → 0.103). A frequency threshold cannot see that,
> because how close is "too close" depends on the coupling strength, not on a
> fixed number of MHz.

⚠️ Third mis-specified criterion this session — R103's sub-noise gate, R105's
null-control labelling, now this. **All three were the criterion, not the data**,
and all three were caught because the measurements were reported separately from
the verdicts. That separation is doing its job.

| # | headline | detail |
|---|---|---|
| 148 | 🔑 **R107 — the unfiltered cavity has no TE₀₁₁, only hybrids; the filter prevents mixing; a sapphire filter is worse** | Three materials on ONE mesh, so differences are exact. 🔑 **Unfiltered, TE₀₁₁ and TM₁₁₁ hybridise**: bore-E 0.034% and 0.247% become 0.103% and 0.179%, **averaging to 0.141% — exactly the mean of the parents**, the textbook avoided-crossing signature; Q does the same. **There is no TE₀₁₁ to operate without the filter.** ✅ So the filter's value is **preventing hybridisation**, not shifting frequency — removing it costs **21% of Q, none of it dielectric loss**. 🔴 **R39's "5.6% Q cost" is not reproduced** — same-mesh gives −21%, opposite sign; and both it and the groove's 6.0% sat under the 6.9% cross-mesh Q floor. 🔴 **A SAPPHIRE FILTER IS 9.2% WORSE ON Q**: ε = 11.6 pulls in more field than 3× lower tanδ recovers — my "strictly better" prediction was wrong because it reasoned from tanδ alone. Extra separation is worthless (TM₁₁₁ already 66.7 MHz off, rivals <0.5%). **The filter stays fused quartz.** ⚠️ Sapphire's TM₁₁₁ left the window — no separation claim. 🔴 **My 7 MHz degeneracy guard was mis-specified**: it fired on separation, but the modes hybridised at 18.6 MHz. **Character, not frequency, is the indicator** |

---

## 2026-08-20 — ✅ R111: the misleading names are GONE, not annotated. Rename, rebuild, re-run

The user, overruling my first instinct:

> *"The code is documentation, and wrong code is wrong documentation. There are
> no names we cannot change. I would rather re-run the relevant solves than leave
> them, even if they produce the same result. I can just imagine closing this
> session and having to work through the misunderstandings yet again."*

🔑 **That is the right cost model and mine was wrong.** A misleading name does not
cost a stale comment — it costs **every future session re-deriving the same
misunderstanding.** This session alone lost time twice to exactly that:
`cav.length_sapphire` (which meant *sapphire outer tube only*) and `TAG_QUARTZ`
(which holds a sapphire torch). A rebuild costs an hour once; a wrong name costs
an hour every time it is read.

### What was renamed

| old | new | why the old one lied |
|---|---|---|
| `TAG_PEC` | **`TAG_WALL`** | nothing here was ever a perfect conductor — attribute 90 carries a finite `Conductivity` boundary |
| `TAG_QUARTZ` | **`TAG_TORCH`** | the torch has been **sapphire** since R99 |
| `TAG_BRAKE`, `brake_t/eps/v` | **`TAG_FILTER`, `filter_*`** | it is the **mode filter**; "brake" is a role it stopped having |
| sidecar `pec`/`quartz`/`brake` | **`wall`/`torch`/`filter`** | same, and these are what code actually reads |
| local `quartz`, `quartz_in` | `torch_v`, `torch_in` | |
| `cav.length_sapphire` | **`cav.length_torch_sapphire_outer`** | did not say WHICH parts were sapphire — cost a correction mid-session |
| `cav.length_quartz` / `_all_sapphire` | `cav.length_torch_all_quartz` / `_all_sapphire` | |
| `cav.shim` / `cav.shim_all_sapphire` | `cav.shim_quartz_to_sapphire_outer` / `_to_all_sapphire` | a shim between *what and what* |
| `filter.q_cost_r39_superseded` | `filter.q_cost_vs_bare` | named its own history, not its content |

✅ **Attribute NUMBERS are unchanged (2, 8, 90), so no physics moves.** The rename
is purely nominal — which is exactly why re-running to pick it up is cheap.

### 🔑 The rule, generalised

**Name by ROLE, never by material, value, or idealisation.** Every name in this
project that encoded a material or an idealisation has become wrong; every name
that encoded a role (`bore`, `plasma`, `port`, `groove`, `upstream`) is still
correct. Materials get swapped and idealisations get replaced; the role does not.

### ✅ Failing loudly beats falling back

`solveconf.load_meta` now **REFUSES** a pre-rename sidecar:

> *"…predates the R111 rename (has ['brake', 'pec', 'quartz']). Rebuild the mesh
> with the current geometry.py — attribute NUMBERS are unchanged, only the names,
> so nothing about the physics moves."*

⚠️ A compatibility alias was the tempting option and would have been the wrong
one: **silently falling back to an old name is how a wrong name becomes a wrong
result** — which is precisely the R101 failure (`torch_material` recorded and
never read) in another costume. `--brake` survives only as a loud deprecated CLI
alias so the ~18 closed evidence-trail drivers still run.

⚠️ I also re-made the argparse `%` bug from earlier today — `"9.2% WORSE"` in a
help string is `%W` and crashes `--help`. **Second time in one session**; it is in
the memory and I still did it.

### What has to be re-run, and why it is mostly not the rename

🔑 The rename changes no numbers. **The wall metal does.** Every solve in this
record used SILVER (6.3e7) while the design has been aluminium (3.5e7) since R58,
so every absolute Q is ~33% high. The re-run list is driven by that:

| | |
|---|---|
| **R110** (running) | already carries the fix — gives the wall-loss law *and* the filter ladder at aluminium |
| **s99\* mesh family** | rebuild for the new sidecar keys |
| **R99 / R99b** | re-solve at aluminium on rebuilt meshes. ⚠️ Frequencies are barely wall-sensitive, so TM₀₂₀'s 190.9 MHz and the 195.4 MHz clearance are expected to stand — but they will be *measured* at the right metal, not assumed |
| **R107** | superseded by R110's ladder, which runs at aluminium |
| **R109** | queued; will build on renamed meshes |

| # | headline | detail |
|---|---|---|
| 149 | ✅ **R111 — misleading names removed, not annotated; rebuild and re-run accepted as the price** | 🔑 **`TAG_PEC`→`TAG_WALL`** (nothing was ever a perfect conductor), **`TAG_QUARTZ`→`TAG_TORCH`** (sapphire since R99), **`TAG_BRAKE`→`TAG_FILTER`** (it is the mode filter), sidecar keys with them, and **`cav.length_sapphire`→`cav.length_torch_sapphire_outer`** (it never said *which parts*). **Attribute numbers unchanged, so no physics moves.** 🔑 Rule: **name by ROLE, never by material, value or idealisation** — every material/idealisation name in this project has gone wrong; every role name is still right. ✅ **`load_meta` REFUSES a pre-rename sidecar** rather than aliasing: silently falling back is how a wrong name becomes a wrong result, which is R101 in another costume. 🔴 **The re-runs are driven by the WALL METAL, not the rename** — every solve in the record used silver while the design has been aluminium since R58, so every absolute Q is ~33% high |

---

## 2026-08-20 — 🔴 WITHDRAWN: R107's explanation for the sapphire filter. It is quantitatively impossible

⚠️ **The MEASUREMENT stands. The MECHANISM I attached to it does not.**

R107 measured TE₀₁₁ Q₀ falling **34,682 → 31,500 (−9.2%)** when the mode filter
goes quartz → sapphire, same mesh. I wrote:

> *"ε = 11.6 pulls more field into the annulus than the 3× lower tanδ recovers."*

🔴 **That cannot produce the observed number.** TE₀₁₁'s E is azimuthal and lies
*parallel* to the flat annulus face, so E is continuous across it and the
dielectric loss density goes as **ε·tanδ**:

| | |
|---|---:|
| ε·tanδ, quartz | 3.780e-4 |
| ε·tanδ, sapphire | 4.060e-4 → **+7.4%** |
| measured rise in TOTAL loss | **+10.1%** |
| dielectric share of total loss required | **1.36** |

**A component cannot be 136% of the whole.** Even if the filter were the *only*
loss in the cavity, a 7.4% rise in it gives 7.4%, not 10.1%. The explanation is
withdrawn.

### What could actually do it — stated as candidates, not as an answer

| | | distinguishing signature |
|---|---|---|
| **field redistribution** | higher ε concentrates ∫\|E\|²dV in the annulus beyond the simple ε·tanδ ratio | Q₀(ε) smooth, monotonic |
| **partial hybridisation** | at ε = 11.6 a neighbour sits **13.2 MHz** from TE₀₁₁ (2.38085 vs 2.39400) — close, though bore-E stayed clean at 0.031% | Q₀(ε) dips locally near that approach |
| **artifact** | | Q₀(ε) erratic |

✅ **R110's ε ladder was already designed to separate these** — nine permittivities
on one mesh. The curve shape decides it.

🔑 **THE GENERAL FAULT, which the user named**: *"you tend to accept results
gormlessly. Everything that diverges from the prediction needs to be
characterised."* I predicted sapphire would be strictly better, measured worse,
attached a plausible-sounding mechanism, and wrote it into the record without
checking whether the arithmetic could carry it. **Thirty seconds of division
would have caught it.** A mechanism that is not quantitatively checked is a story,
and a story in FINDINGS is worse than an open question.

### 🔴 And two older instances of the same fault are still open

| | |
|---|---|
| **R37** | eigenmode and driven disagree **3.7×** on ε sensitivity (9.25 vs 33.9 MHz). Open since 2026-08-15. We resolved it by CHOOSING — *"driven is self-consistent and defines the design"* — which is a policy, not a diagnosis. **Two solvers disagreeing 3.7× on the same physics is the signature of a bug** |
| **R2** | closed-form wall Q 49,182 vs measured ~95,000, closed as *"closed forms are the fault, not the model"* because ours is not an empty right cylinder. A legitimate explanation — **but it means the pipeline has never been checked against a case where the closed form is EXACT.** The escape hatch was used and never removed |

| # | headline | detail |
|---|---|---|
| 150 | 🔴 **WITHDRAWN — R107's sapphire mechanism is arithmetically impossible; the measurement stands** | TE₀₁₁'s E is parallel to the annulus face so loss goes as **ε·tanδ: quartz 3.78e-4 → sapphire 4.06e-4, +7.4%**. Measured total loss rose **10.1%**, which would need the dielectric to be **136% of total loss**. Withdrawn. Candidates now stated with distinguishing signatures — field redistribution (smooth Q₀(ε)), partial hybridisation (local dip near the 13.2 MHz neighbour), artifact (erratic) — and **R110's nine-point ε ladder separates them.** 🔑 The general fault, as the user put it: a plausible mechanism written into the record without checking the arithmetic. **Two older instances remain open: R37's unexplained 3.7× eigenmode-vs-driven disagreement, and R2's closed-form escape hatch that was used and never removed** |
