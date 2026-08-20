# Phase 1 — findings

Chat replies are being truncated, so results land here.

## 1. The fundamental ring mode, tracked correctly

Earlier table was broken: the extractor picked `max(alumina fraction)`
independently per diameter and flipped between two different physical modes.
Re-extracted from saved CSVs (no re-solving) reporting *all* m=0 ring-like
modes, the fundamental TE mode is clean and monotonic:

| D (mm) | f (GHz) | Q | bore E/H | % in Al₂O₃ |
|---:|---:|---:|---:|---:|
| 90 | **2.2515** | 11242 | 0.019 | 56.2 |
| 95 | 2.2234 | 11401 | 0.019 | 55.6 |
| 100 | 2.1992 | 11566 | 0.018 | 54.9 |
| 110 | 2.1593 | 11927 | 0.018 | 53.5 |
| 120 | 2.1264 | 12336 | 0.017 | 52.0 |
| 140 | 2.0714 | 13343 | 0.016 | 48.6 |
| 160 | 2.0239 | 14750 | 0.015 | 44.4 |

Textbook behaviour: f rises as the wall closes in, energy concentrates in the
ceramic, Q falls as more field sees the lossy dielectric. E/H ≈ 0.02 confirms
strongly H-dominated in the bore — the ICP-analogue mode.

**Order-1 error is 0.17%** (160 mm: order 1 = 2.0239 vs order 2 = 2.0204), so
none of this is discretisation.

## 2. The model will not reach 2.45 GHz — sensitivity study

| parameter | range tested | effect on ring f₀ |
|---|---|---:|
| enclosure diameter | 160 → 90 mm | **+11.2%** |
| enclosure length | 300 → 60 mm | +2.4% (converged above 120 mm) |
| quartz torch | present → removed | ~+1.4% (holds only 3.7% of energy) |
| **all three, best case** | | **≈ 2.28 GHz** |

Target is 2.45 GHz. **Still ~7% short with every parameter pushed to its limit.**

Length is fully converged beyond 120 mm, so the PEC end caps are not the
problem — Radom's open waveguide vs our closed cavity does not explain it.
The torch is negligible. Diameter is the only real lever and it runs out of
room at 90 mm, where the wall is already 20 mm from a 50.8 mm ring.

### What that means

The model is converged, self-consistent, and disagrees with the patent's
"approximately 2.45 GHz" by ~8–10% in a direction no available parameter
closes. Candidate explanations, none yet tested:

- The patent's 2.45 GHz is the **source** frequency, not the ring's unloaded
  resonance. In a real device the ring is coupled to a waveguide and loaded by
  plasma; the system resonates at 2.45, the bare ring need not.
- Real ε_r differs from the stated 9.8. Closing 8% would need ε_r ≈ 8.3, which
  is below any high-purity alumina — unlikely but cheap to bound.
- The stated dimensions are illustrative rather than as-built. JAAS 2016
  confirms the *material* is >99.9% Al₂O₃; it does not confirm the dimensions.

## 3. Consequence — stop copying, start designing

We are not obliged to reproduce Radom's dimensions. The requirement is a ring
that resonates at 2.45 GHz **in our enclosure, with our torch**. That is a
straightforward inverse problem.

Rough scaling (f ∝ 1/size) from 2.20 GHz at D=100 mm needs the ring ~10%
smaller:

| | patent | scaled target |
|---|---:|---:|
| OD | 50.8 mm | ~45.7 mm |
| ID | 25.4 mm | ~22.9 mm |
| length | 19.05 mm | ~17.1 mm |

A 22.9 mm bore still clears a 20 mm torch. So the design closes.

**Next: inverse-design sweep on ring scale factor at fixed enclosure, to land
the TE mode on 2.45 GHz.** Then re-check TM₀₁₀ placement for ignition against
the final geometry.

## 4. TM₀₁₀ — clean and calibrated

Rises as 1/D, consistently pulled below the empty-cavity value by ring loading:

| D (mm) | TM₀₁₀ | empty cavity | pull-down |
|---:|---:|---:|---:|
| 90 | 2.2080 | 2.550 | −13.4% |
| 100 | 2.0246 | 2.295 | −11.8% |
| 120 | 1.7344 | 1.912 | −9.3% |
| 140 | 1.5169 | 1.639 | −7.4% |
| 160 | 1.3473 | 1.434 | −6.1% |

Monotone and smooth. Extrapolating the ~13% pull-down, TM₀₁₀ reaches 2.45 GHz
near **D ≈ 80–85 mm**. Encouraging for mode-shift ignition, but it must be
re-evaluated once the ring is re-scaled, since both move together.

## 5. Infrastructure notes

- GPU is **not available** — no `/dev/nvidia*`, no `libcuda`, no `nvcc`. The
  container lacks device passthrough. Would need relaunching with `--gpus all`.
- Not worth pursuing regardless: order-1 points take 2–5 min, the whole 7-point
  sweep ran in under an hour, and every hour actually lost was to a modelling
  error or an extraction bug. **We are not compute-bound.**
- `pgrep` repeatedly matched *defunct* processes (container PID 1 does not reap
  zombies), which twice made finished runs look like running ones. Check
  `ps -o stat` and exclude `Z` before believing any progress check.

---

# Append log

Convention from here: **append only**, newest section at the bottom.

## 2026-08-13 — Inverse design: ring scale sweep

Stopped copying the patent dimensions and asked instead what ring resonates at
2.45 GHz in *our* enclosure. Uniform scale factor on OD/ID/length, enclosure
fixed at D=100 mm, order 1.

| scale | OD (mm) | ID (mm) | TE ring (GHz) | TM₀₁₀ (GHz) | TE−TM split |
|---:|---:|---:|---:|---:|---:|
| 1.00 | 50.8 | 25.4 | 2.1992 | 2.0246 | −7.9% |
| 0.95 | 48.3 | 24.1 | 2.2898 | 2.0383 | −11.0% |
| 0.92 | 46.7 | 23.4 | 2.3489 | 2.0462 | −12.9% |
| 0.90 | 45.7 | 22.9 | 2.3903 | 2.0513 | −14.2% |
| **0.88** | **44.7** | **22.4** | **2.4331** | 2.0572 | −15.5% |
| 0.85 | 43.2 | 21.6 | 2.5009 | 2.0643 | −17.5% |

**Scale 0.88 lands the TE mode at 2.4331 GHz — inside the ISM band.**
Interpolating, 2.450 GHz falls at scale ≈ 0.874, i.e. **OD 44.4 mm, ID 22.2 mm,
length 16.6 mm**. A 22.2 mm bore still clears a 20 mm torch.

So the design closes. The inverse problem is well behaved and nearly linear:
f scales as 1/size to within a percent over this range, exactly as expected for
a dielectric resonator.

### The catch — TM₀₁₀ barely moves

TM₀₁₀ is set by the *enclosure*, not the ring, so shrinking the ring changes it
only through reduced loading: 2.0246 → 2.0643 GHz across the whole sweep.
Meanwhile TE climbs 2.20 → 2.50.

**They diverge.** The split widens from −7.9% to −17.5% as the ring shrinks.
Tuning the ring onto 2.45 GHz pushes the ignition mode *further away*, which is
the opposite of what mode-shift ignition needs.

### Consequence: the two modes need independent handles

They are set by different things, so they can be tuned independently:

- **ring scale** → sets TE (operating) mode
- **enclosure diameter** → sets TM₀₁₀ (ignition) mode

From the earlier sweep, TM₀₁₀ ≈ 2.45 GHz needs D ≈ 80–85 mm. So the candidate
geometry is roughly **ring at scale ~0.87 inside a ~82 mm enclosure** — but
shrinking the enclosure also raises TE (+11% from 160→90 mm), so the two must
be solved *together*, not sequentially.

**Next: 2-D sweep over (ring scale, enclosure diameter).** Find the pair that
puts TE on 2.45 GHz with TM₀₁₀ as close beneath it as possible. Grid is small —
5 scales x 5 diameters at order 1 is ~25 runs, under two hours.

Open question that may make the whole thing easier: the ignition mode does not
have to be TM₀₁₀. Any cavity mode with high E in the bore will break down gas.
The 2-D sweep should record *all* E-dominated modes, not just the lowest, so a
higher-order cavity mode sitting just above TE is not missed.

## 2026-08-13 — 2-D sweep, and the candidate verified at order 2

The sweep ran (25 points, order 1, ~18 min) and the winning point was re-solved
at order 2 with fields saved.

**The design closes. TE and an E-dominated bore mode land 39 MHz apart, both
inside the ISM band.** The pessimism closing the previous section does not
survive the joint solve: the two modes diverge under a *sequential* tune, but
not under a joint one.

### The grid

Ring scale × enclosure diameter. Torch fixed, enclosure length fixed at 120 mm
(converged). Clearance floor 8 mm — no point was skipped.

TE operating mode (GHz):

| D \ scale | 0.82 | 0.85 | 0.88 | 0.91 | 0.94 |
|---:|---:|---:|---:|---:|---:|
| **80** | 2.6866 | 2.6145 | 2.5473 | 2.4852 | **2.4279** |
| 85 | 2.6534 | 2.5804 | 2.5124 | 2.4493 | 2.3904 |
| 90 | 2.6240 | 2.5509 | 2.4828 | 2.4189 | 2.3593 |
| 95 | 2.5979 | 2.5249 | 2.4564 | 2.3926 | 2.3326 |
| 100 | 2.5733 | 2.5009 | 2.4331 | 2.3690 | 2.3091 |

Nearest E-dominated bore mode (GHz):

| D \ scale | 0.82 | 0.85 | 0.88 | 0.91 | 0.94 |
|---:|---:|---:|---:|---:|---:|
| **80** | 2.4926 | 2.4827 | 2.4724 | 2.4615 | **2.4505** |
| 85 | 2.7970 | 2.7943 | 2.3540 | 2.3440 | 2.3341 |
| 90 | 2.6882 | 2.6858 | 2.6833 | 2.2365 | 2.2276 |
| 95 | 2.5900 | 2.5882 | 2.5858 | 2.5831 | 2.1303 |
| 100 | 2.5017 | 2.4997 | 2.4978 | 2.4955 | 2.4926 |

TE is smooth and near-exactly bilinear in both variables — which is why the
inverse problem was easy. **The ignition surface is not smooth**: every row
except D=80 has a discontinuity where *nearest* jumps between two different mode
branches (§ below). Do not interpolate it.

### Candidates — TE within ±1.5% of 2.45 GHz

| D (mm) | scale | TE | ignition | gap |
|---:|---:|---:|---:|---:|
| **80** | **0.94** | 2.4279 | 2.4505 | **23 MHz** |
| 80 | 0.91 | 2.4852 | 2.4615 | 24 MHz |
| 100 | 0.88 | 2.4331 | 2.4978 | 65 MHz |
| 85 | 0.91 | 2.4493 | 2.3440 | 105 MHz |
| 95 | 0.88 | 2.4564 | 2.5858 | 129 MHz |
| 90 | 0.91 | 2.4189 | 2.2365 | 182 MHz |
| 90 | 0.88 | 2.4828 | 2.6833 | 201 MHz |

Every nearest-ignition mode came back m=0. No higher-order azimuthal mode beat
the axisymmetric ones anywhere on the grid.

### Order-2 verification — D = 80 mm, scale 0.94

Geometry as actually meshed in `cand.msh`:

| | mm |
|---|---:|
| ring OD / ID / length | 47.75 / 23.88 / 17.91 |
| enclosure dia / length | 80 / 120 |
| torch OD / ID | 20 / 17 |
| ring-to-wall clearance | 16.1 |
| **ring bore to torch OD** | **1.94 radial** |

| | order 1 | **order 2** | shift |
|---|---:|---:|---:|
| TE | 2.4279 | **2.4170** | −0.45% |
| ignition | 2.4505 | **2.4563** | +0.24% |
| gap | 23 MHz | **39 MHz (+1.63%)** | +70% |

⚠️ **Order-1 error here is 0.45%, not the 0.17% established at D=160** — and the
two modes move in *opposite* directions, so the error on the gap is worse than
the error on either frequency. The 0.17% bound was measured on a larger
enclosure with an unscaled ring and does not transfer.

**Operational rule: sweep at order 1, but never quote a gap from order 1.** Any
point that matters gets re-solved at order 2.

Full order-2 mode picture at the candidate, energy fractions by domain:

| f (GHz) | Q | bore E/H | % of E in bore | % of H in bore | % in Al₂O₃ | role |
|---:|---:|---:|---:|---:|---:|---|
| **2.4170** | 11054 | 0.023 | 0.43 | 19.2 | 56.7 | **operating** — H-dominated bore |
| **2.4563** | 44655 | 41.4 | 11.6 | 0.28 | 8.1 | **ignition** — E-dominated bore |
| 2.8997 | 56453 | 29.7 | — | — | 0.6 | E-dom, too far |
| 3.0668 (×2) | 33595 | 0.81 | — | — | 24.6 | mixed, degenerate |

The contrast is the entire design: two modes 39 MHz apart whose bore fields are
**inverted** — 19.2% of the magnetic energy in the bore for one, 11.6% of the
electric energy in the bore for the other, each with the complementary component
near zero. Ignite on the upper, run on the lower.

The ignition mode is TM₀₁₀, pulled down **14.4%** from the 2.8686 GHz empty-cavity
value at D=80 — consistent with the −13.4% at D=90 in §4.

Q on the ignition mode is 44655, four times the operating mode's. 🔢 Field
enhancement goes as √Q, so the ignition mode is worth **~2× the field** of the
operating mode at equal drive — the overdrive scheme is landing on the right
mode. Build-up time τ = Q/ω = 44655/1.543e10 = **2.9 µs**, so §4.2's 10 µs pulse
is now ~3.5 time constants rather than 30. Still adequate, but no longer
generous — check this against the pulse plan.

### The second branch is TM₀₁₁, not a second TM₀₁₀ ⚠️

The previous section asked whether a higher-order E-dominated mode could land
nearer TE than TM₀₁₀. **A second branch does exist**, and for D ≥ 85 it is the
nearer one — it is the branch that makes the ignition surface discontinuous.

It cannot be TM₀₁₀: it sits *above* the empty-cavity TM₀₁₀ frequency, and
dielectric loading can only pull down.

| D (mm) | observed | vs empty TM₀₁₀ | vs empty TM₀₁₁ |
|---:|---:|---:|---:|
| 85 | 2.7970 | **+3.6%** ✗ | −6.0% |
| 90 | 2.6882 | **+5.4%** ✗ | −5.3% |
| 95 | 2.5900 | **+7.2%** ✗ | −4.8% |
| 100 | 2.5017 | **+9.0%** ✗ | −4.3% |

Against TM₀₁₁ the pull-down is small, smooth and monotone — exactly right for a
mode with an E_z null at the ring plane, which barely feels the ring. Two further
consistency checks: the branch is nearly **scale-independent** (2.5017 → 2.4926
across the whole scale range at D=100, vs TM₀₁₀'s 12–14% loading), and its
pull-down grows as the wall closes in, as loading should.

🔢 Identification is arithmetic, not a demonstrated result. **The clean
discriminator is enclosure length** — TM₀₁₁ moves with L, TM₀₁₀ does not.
`len-sweep.sh` already does this; three points at fixed (D=100, scale 0.82)
settles it in minutes.

⚠️ Worth remembering: **D=100 / scale 0.85 has a 1 MHz gap** (TE 2.5009 vs
2.4997) against this branch — very nearly degenerate. It was rejected only
because TE is 2.1% high and 2.50 GHz sits at the ISM edge. Since plasma loading
pulls f₀ *down*, a design deliberately placed high is not obviously wrong, and
this point should be revisited once the loaded shift from §4.4 has a number.

### Next

1. **Length sweep** to confirm the TM₀₁₁ identification. Minutes, harness exists.
2. **Tolerance study on the candidate.** 39 MHz is 1.6% — how far does the gap
   move under ±1 mm on ring OD/ID and enclosure D, and under ε_r 9.8 ± 0.2? This
   decides whether the thing is buildable as-machined or needs a tuner, and it is
   the highest-value run left in Phase 1.
3. **Phase 2 (driven)** on the candidate: |E|max in the bore at 2.4563 GHz vs
   drive power, against §4.3's N₂ threshold. The saved `cand_o2` fields can be
   sampled with pyvista for the eigenmode field shape before any driven run.
4. Re-examine the 10 µs pulse against τ = 2.9 µs.
