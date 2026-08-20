# Experiment register — 2026-08-20 (rev 13, METHODOLOGY.md added)

**What this is:** the parameter space, what is settled on each axis, what is open,
and what each open axis is blocked on. It exists because the last several runs
were designed reactively — each one scoped from the previous one's surprise — and
that produced three retractions in a day.

**This is a working artifact, not a findings entry.** It is regenerated, not
appended to, like `AUDIT.md`. `FINDINGS.md` remains the append-only evidence
trail; where they disagree, FINDINGS wins.

---

## 0. The design is DIMENSIONLESS. Two hard anchors; sweep in λ, not millimetres.

Maxwell is scale-invariant, so the cavity electromagnetics is pure ratios.
`dimensionless.py` derives this view from `baselines.json` — it is never stored,
because a hand-maintained second copy is the next thing that drifts.

| | anchor |
|---|---|
| ① | **f₀ = 2.45 GHz, band ±2.04% fractional.** REGULATORY (ISM + LDMOS), not physical. λ = 122.36 mm |
| ② | **N₂ at 0–2 atm.** The only place scale-invariance fails — Paschen *p·d*, Townsend *E/N*, the vibrational bootstrap. Produces σ, which re-enters the EM only as **δ/t** |

Everything else reduces: geometry /λ · D/L = 2.343 · ε_r, tanδ · wall δ/λ =
1.05e-5 · thermal Δf/f = −23.6 ppm/K · tolerance ±0.0016λ.

🔑 **Sweep in λ.** The groove ladder in millimetres looked like even steps; in λ
it reads **λ/8** (crossing, unmeasurable), **λ/6** (candidate), **0.2125** (the
hybridisation catastrophe — not a simple fraction), **λ/4** (choke). The trouble
sits in the gaps between λ/5 and λ/4 that were never sampled. The next ladder is
λ/5 = 24.5 mm and λ/4.5 = 27.2 mm, not another set of round millimetres.

⚠️ **Score within a configuration, never against another's absolute.** That is
the same fix as assignability (§1): a ratio taken inside one run is attributable
to the component being varied; an absolute imported from a different
configuration is not.

🔴 **`baselines.json` mixes order-1 raw and offset-corrected frequencies without
marking which**, and the offsets are mode-dependent (+24.54 MHz TE₀₁₁ = 1.00% of
f₀, +20.06 TM₀₂₀). Any in-band call read off a fractional table can be wrong by a
quarter of the band. Check provenance before quoting placement.

---

## 0.5 THE GATE — every criterion must state its path to detection limit

🔑 **This instrument's terminal objective is a detection limit per element:**

```
        LOD  ≈  3 · sigma_background / sensitivity
```

Everything else is upstream of that. A criterion that cannot name its path down
to it may not reject a design.

| level 1 — sets LOD directly | level 2 — the EM parameters we work on |
|---|---|
| **background** — continuum, N₂ bands, **wall reflectance**, stray light | surface material · light trap |
| **sensitivity** — excitation × collection × residence | η → power → temperature; viewport solid angle |
| **noise / RSD** — plasma flicker | deposition uniformity · frequency stability |
| **self-absorption** on Ca/Mg/Na/K — linearity, dynamic range | wall retroreflection · plasma chord length |

### Retroactive audit of the criteria actually used

| criterion | stated path to LOD | verdict |
|---|---|---|
| **η** = 1−\|Γ\|² | power → temperature → excitation → sensitivity | ✅ passes |
| **C4** TE₀₁₁ ≥ 2× best reachable rival | is TE₀₁₁ the mode being driven at all → plasma exists | ✅ passes |
| **C1′** deposition non-uniformity | plasma symmetry → RSD → noise | ✅ path valid; **threshold unknown (R87)** |
| **C1** bin1 ≤ quartz's 0.0263 | 🔴 **none stated** — a cold field statistic | 🔴 fails; rejected ten geometries |
| **C3** Q₀ ≥ quartz's 37,059 | Q₀ → η → sensitivity, but **η already has a 60.5% floor** | 🔴 fails on relevance — the deficit does not propagate |
| **C5** TM₁₁₁ separation ≥ 10 linewidths | 🔴 **threshold invented**, no path | 🔴 fails |

⚠️ **Three of six criteria used this session cannot justify themselves.** C1 and
C5 were inventions; C3 measures something real that has margin. That is the C1
error generalised — and the gate is the fix.

### Re-ranked open registers

| tier | | why |
|---|---|---|
| **1 — EM, unblocked** | **R61** TM₁₁₁ at 0° tilt · **R82** aliasing at N=24 · **R86** filters at δ/t ≈ 1 | ✅ **R99 closed**, so these run on the **sapphire** meshes (s99sa/s99pr), not the quartz development build. R82's N=24 DFT would also settle R104 if it is ever worth revisiting |
| **1 — methodological, and it bounds everything** | ⚠️ **R105 BOUNDED at σ = 1.3–3.3 MHz** (cross-check failed at 2.48× vs a declared 2×) · ⛔ **R106 STOPPED** — premise withdrawn (two different limits compared) and not decision-relevant: 58 MHz of band margin against an 18 MHz possible error | ✅ **The solver contributes ZERO** — a duplicated mesh gave +0.0000 MHz, so all scatter is mesh GENERATION. 🔑 A 15 µm length ladder moved f **19× further than the physics did**. 🔴 **Quote differences against 3.3 MHz when being careful**: R99's TE₀₁₁ −5.8 MHz is only 1.8σ there. **R105 needs a ≥6-factor convergence ladder** to settle σ_C and test the h² law — and that same ladder answers R106, where an extrapolation gives +42.5 against the recorded +24.54 |
| **1 — open from R99** | **R102** what now binds the ±0.2 mm radius tolerance | **R102 is a cost question** — the tightest number on the drawing lost its justification when TM₀₂₀ fell 190.9 MHz. ⛔ **R104 DROPPED** — no closed-form reason, cross-mesh, and 2.8σ against the R105 floor. That is the artifact profile, not a finding |
| **1 — external** | **R92** spectrometer f-number · **R87** uniformity spec · **R94** cavity temperature rise | R92 sets viewport aperture, trap aperture **and** the axial extent of the diamond-lapped zone |
| **1 — torch safety** | **R41** coolant-flow interlock | AlF₃ passivation sublimes above 1276 °C; losing coolant strips it and RF must cut within one thermal time constant |
| **3 — margin, or no path** | **R84** D/L · **R88** torch ρ · **R43b** sapphire coupon · **R100** outer-tube service interval · groove geometry | D/L has 3.5× margin. **R100 is the cost of permanence**: the outer tube's inner wall is both the optical and the deposition surface |

**Closed 2026-08-19** — ✅ **R99** TM₀₂₀ falls 190.9 MHz at the sapphire point, clearance 195.4 MHz vs a 4.4 MHz threshold. ✅ **R103** dTE₀₁₁/dL = −11.89 ± 1.21 MHz/mm, consistent with R46 at 0.97σ — the 20% gap was a 2-point slope with no error bar. ⛔ **R18 withdrawn as moot** (quartz died on fluoride 2026-08-15). ✅ **R97/R42 moot**, **R57/R58/R89/R90** closed.

✅ **Superseded 2026-08-19**: the viewport and light trap are now ON BY DEFAULT at
10 mm (`optics.aperture_rule`), and R103 measured that they change dTE₀₁₁/dL by
0.12σ — i.e. not at all. ⚠️ **That default flip is a MESH BOUNDARY**, as is the
quartz→sapphire torch default (R99). Every mesh before 2026-08-19 has neither;
do not difference across either one. The sidecar records both.

---

## 1. The blocker: C1 was a CATEGORY ERROR, and it has to be replaced before anything is swept

🔴 **C1 — "TE₀₁₁ azimuthal purity ≤ quartz" — rejected ten geometries across depth
and width. It treats azimuthal purity as a property of the RESONATOR. It is a
property of the DRIVE.**

A filter changes which modes exist and where they sit in frequency. It cannot
change what the source excites. The floor is the coupler's:

| coupler | TE₀₁₁ bin1 | |
|---|---:|---|
| design loop (R47) | 0.0046 | the recorded "m=0 floor" |
| **sc06**, same nominal cavity | **0.0263** | **5.7× higher** |
| best of ten groove geometries | 0.0372 | never reached the quartz value |

> 🔑 **C1 asked the filter to remove contamination the coupler injects, then
> reported ten filter geometries as failures for not doing it.** Unachievable by
> construction — which is the tell that it is a mis-assigned problem rather than
> a hard one.

⚠️ **Three further mis-categorisations in the same criterion**, any one of which
would disqualify it as stated:

| | C1 measures | the design cares about |
|---|---|---|
| state | **cold** cavity | the **lit** plasma — and R74 measured the plasma taking ≥96.8% of absorbed power, so the lit field is set by the load |
| region | air attributes 3..7, the **whole cavity** | deposition symmetry in the **plasma torus** |
| quantity | **stored energy** | **∫σ\|E\|²dφ**, power deposited per unit azimuth |

### The replacement, and why it is first in the queue

This is the third time a proxy has driven the programme:

| proxy | said | the outcome said |
|---|---|---|
| Q_ext | "98× coupling deficit" | 21 percentage points of power (R73) |
| Q_lit | "the cavity cannot be matched" | η = 78.8%, floor 60.5% over 1000× in σ (R74) |
| **bin1** | **"no filter geometry is acceptable"** | **never measured** |

✅ The one figure of merit that is an outcome is **η = 1 − |Γ|²**. The open
question is its azimuthal analogue: **does azimuthal contamination at the levels
measured change anything about the plasma?** That is a lit-state question about
deposition uniformity in the torus, and it decides whether the filter and coupler
programmes matter at all. **If the answer is "nothing measurable", the groove work
was unnecessary and sc06 is already adequate.**

## 2. The axes

### ✅ Settled — do not sweep

| axis | value | authority |
|---|---|---|
| `cav.radius` / `cav.length` | 103.70 / 88.53 mm | R44/R46. TE₀₁₁ cannot be resized (entry 98). D/L = 2.343, clear of the TM₀₁₂ crossing at 1.096 |
| loop mount | **barrel**, not cap | R73 — a cap crossbar is a partial shorted turn to E_φ; η 78.8% barrel vs 13.6% at cap r=30 |
| loop tilt | 0° operational | R60 |
| filter present | **required** | bare reverts to the χ′₀₁ = χ₁₁ degeneracy; TE₀₁₁ bin1 = 0.2443, 53× the m=0 floor |

### 🔴 Proven unsweepable

| axis | why |
|---|---|
| coupler size / shape | R70, 12 geometries: Q_ext vs area **r² = 0.043**, vs perimeter 0.018, best two-variable 0.376 with nonsense exponents. *"The loop response is not a smooth function of loop geometry; it cannot be designed or optimised by point-sampling."* A grid on this axis returns noise however much compute is thrown at it |

### ⏸️ Open, blocked

| axis | blocked on | why |
|---|---|---|
| groove (w, d) | **the C1 replacement** | ✅ R81 identified the modes by measurement — TE₀₁₁ carries 0.6% of its energy in the slot, the family at 17–52% ARE slot modes. So a dispersion relation is now buildable. 🔴 But the (w,d) verdicts of R59/R80 do not survive C1's mis-assignment, so there is nothing to sweep *for* until the criterion is replaced. ⚠️ **15 mm and any near-degenerate depth is unmeasurable** — a 0.16% mesh change swings pm/pe 178% there against 3% at 21 mm |
| feed multiplicity N | **R82** | An N-fold feed drives m ≡ 0 (mod N) and nulls the rest — so a 4-fold feed drives m=4 *harder*. N=5 binning cannot distinguish m=4 from m=1. **Choosing N without knowing m can make the parasite worse** |
| surface material + light trap | nothing | R57/R58 — analysis complete, decision never landed. This is a decision, not a sweep |
| plasma σ | external | Not a design axis but an uncertainty. Swept 0.3–300 (R74), floor 60.5%. AUDIT A5 to pin it |

### ⏸️ Open, unblocked, not a sweep

| | |
|---|---|
| **R61** | Every load-bearing TM₁₁₁ result was taken at the 45° *diagnostic* tilt, not the instrument's 0°. R60 found TM₁₁₁ goes the wrong way at 0°. Re-take them |
| **the interloper** | Still unidentified. p = 1, χ_eff ≈ 3.85, filter-attached (135 MHz vs TE₀₁₁'s 2.0), in band at 2.4628, absorbing 7–46.5% |

---

## 3. The queue

1. ✅ **DONE — R83. C1's referent is real and C1′ is defined.** Azimuthal
   non-uniformity of deposited power in the lit torus, as a within-configuration
   ratio: **bare 0.98–2.06, quartz 0.46**. A 9.3× cut in cold bin1 buys 4.4×
   (transparent) / 2.1× (opaque). Regime-independent once contamination is low.
   ⚠️ Even quartz is 46% non-uniform and the acceptable value is an
   analytical-chemistry spec, still unanswered.
   → **R85: score the 21 mm groove under C1′** (cold bin1 0.0572, between quartz
   and bare). One solve pair, now well-posed.
2. **R82 — break the azimuthal aliasing.** N = 5 resolves nothing above m = 1:
   m0=m5, m1=m4=m6, m2=m3=m7. N = 24 is the minimum for m ≤ 6, and 2πa = 5.3λ so
   orders 5–6 are exactly what a ring structure produces. ⚠️ Identification
   instrument ONLY — sector count moves Q by 6.9% (R54b), and `--loop-phi` must
   move to a sector centre for the new N (37.5° at N = 24, not 36°).
   ⚠️ Also worth testing: the mesh itself has 5-fold structure (air is built as 5
   wedges, the groove as 5 fused arcs), so an m=5 *numerical* artefact would be
   invisible to an N=5 DFT by construction.
3. **R61 — re-take the TM₁₁₁ results at 0° tilt.** Every load-bearing one was
   measured at the 45° diagnostic tilt, and R60 found TM₁₁₁ behaves oppositely at
   0°.
4. **Then, and only then, the (w, d) plane** — as predict-then-verify against the
   slot-mode dispersion R81 makes possible, roughly 20 confirmatory points rather
   than a grid.

## 4. What would justify renting compute

🔴 **Not yet, and not for cost reasons.** A 96-core instance is ~$4/hr; a hundred
hours is $400. The constraint is that more runs without a design produce more
retractions — three today, and faster hardware would only have produced them
faster.

⚠️ **And fix the read resolution first.** Palace's timing report on a typical run:

```
offline phase (14 full solves, all the physics)     109 s
postprocessing (4001 output points)                1278 s   ← 91%
```

The adaptive ROM was already running in every solve this session. The cost is not
solving — it is *evaluating the answer* at 4001 points, at 0.32 s each. Dropping
to ~400 points is **6× for free**, and the ROM can be re-read at any resolution
for another 109 s. Renting before fixing this buys 6× more machine than needed.

✅ **After the C1 replacement and R82** the (w, d) plane becomes
predict-then-verify — roughly 20 confirmatory points against an analytic model,
not a grid. *That* is a workload worth renting for, and it is small enough that
the two laptops may cover it.

🔑 **The bottleneck is methodological, not computational.** Of the last four
substantial runs, three produced retractions — R77's identification, R59's
C5/C6 and its 15 mm row, R80's downgrade — and every one came from a
mis-specified measurement rather than from insufficient compute. Faster hardware
would have produced them faster.

---

## 5. Standing hazards for any future sweep

Each cost this project at least one wrong answer.

| | |
|---|---|
| **Verify the CASES DIFFER, not just the answer** | 🔴 R101: `--torch-material` fed mesh sizing and the sidecar but never the solver, so sapphire and quartz were **byte-identical meshes with identical materials**. Δf would have been 0 everywhere and the null control would have PASSED for the wrong reason. Pre-declared criteria judge the ANSWER; **none asks whether the independent variable was applied.** `md5sum` the meshes |
| **A field in the sidecar is not a binding** | R88 added `torch_material` to the provenance record and nothing to the consumer, so `results.py` reported `[11.6, 3.5e-05]` for a solve that used 3.78. **An entry nobody reads is a claim, not a fact** |
| **Quote a slope with σ, never bare** | R103: a 2-point dTE₀₁₁/dL was **−10.4 ± 4.9 MHz/mm** once per-mesh scatter was propagated, and it opened a register item about a gap that did not exist. **A 2-point slope has no residual and cannot detect its own failure** |
| **A gate below the noise floor is not a gate** | R103: a declared 0.5 MHz linearity gate sat under a 1.9–3.1 MHz per-mesh floor, so it failed regardless of physics and the evaluator printed a false "NOT linear". Same class as the `meta.get("groove")` assert that could only fire |
| 🔑 **Prefer a SAME-MESH comparison** | The solver is deterministic (0.0000 MHz on a duplicated mesh) and **all** error is mesh generation, so a difference taken on ONE mesh is good to 0.02 MHz while any cross-mesh difference carries 1.3–3.3 MHz. Material, solver order, excitation and boundary conditions can be same-mesh; **geometry cannot**. R99 is the record's strongest result because its two meshes were byte-identical; R103 failed because a length ladder forces a new mesh per point. `md5sum` the set — identical hashes are a feature for a material sweep and a red flag for a geometry sweep. See `METHODOLOGY.md` §2 |
| 🔑 **A result needs a closed-form reason before it earns a run** | TM₀₂₀'s 33× shift was predicted from J₀ peaking on axis and J₁ vanishing there, then measured. **R104 had no analytic reason, was cross-mesh, and sat at 2.8σ — the artifact profile — and was DROPPED.** Absent a reason, a marginal cross-mesh difference is more likely to be the mesher than the physics |
| **Record the window** | "Absent from a window is not absent" — three retractions: R54's TM₁₁₁/TM₀₂₀, R77's excluded 2.3431, R59's unlocated TM₁₁₁ |
| **Never track a mode by "largest of its type"** | R59's tracker re-identified its target at every depth; the +125/−29/+107 series was mode-hopping |
| **Apply reachability before ranking** | R59 failed depths on rivals 65 MHz above the LDMOS top |
| **Verify an assertion against known-good data before trusting it** | one threshold could only drop silently (`rel > 0.02`), one assertion could only fire (`meta.get("groove")`) — opposite failures, same cause |
| **N = 5 azimuthal binning is a contamination meter, not a mode identifier** | valid for comparing two geometries measured identically; invalid for labelling m |
| **Never compare Q across sector counts** | 6.9% (R54b). Nor across tagged/untagged meshes — 0.08% |
| **Criteria before the run, evaluation after and separate** | the verdict block has been wrong four times across two authors while the tables survived every time |
| **argmax(U) and argmin\|S11\| are not mode identifiers** | both select the best-COUPLED mode, not the intended one |
| **Near a degeneracy, nothing is measurable** | a 0.16% mesh change swings pm/pe by 178% at 15 mm and 3% at 21 mm. Before reporting a value, perturb the mesh and see whether it survives |
| **Check the criterion is assignable to the component being varied** | C1 asked a filter to fix what a coupler injects, and rejected ten geometries for it |
| **Ask what produced a number before reusing it** | Four instances in one day: `offset.te011` applied to other modes · quartz's bin1 as C1's threshold · `tm111.f_filtered` from another geometry · the 25 mm viewport, which was a Q test size. **Each entered as a measurement in one context and left as a specification in another** |
| **Test a generalisation before asserting it** | The viewport's fuse bug was real; extending it to the chimney and feed was pattern-matching, and both build correctly (R91 withdrawn) |
