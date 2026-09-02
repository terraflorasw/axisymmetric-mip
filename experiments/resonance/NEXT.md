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

## 🔴 LIVE STATE — written 2026-08-27T15:26Z, refresh or delete when stale

**RUNNING:** `h3-ehratio-01` (stamp `d6043449`) on a NEW host — 4 cases
`ld = 5, 8, 11, 14`, lw 8, barrel, gap2 0.5, grooved, cold. **8 eigen solves**
(2 port BCs per case). `h3_loopq` has REAL resume keyed on the config stamp, so
a reclamation costs only the case in flight.

    ops/watch.sh h3-ehratio-01        # mirror: h3-ehratio-01.watch.log

**What it answers:** rho = |E|/(c|B|) at the loop. `series_gap` reads 9.30
where TE011's own value at that radius is 0.218 (`h3-field-01`) — but a series
capacitor has a voltage across it BY CONSTRUCTION, so that alone decides
nothing. The NEW `leg_intact` / `leg_broken` probes are where it decides: legs
are current maxima, so a flux-linking loop must be H-dominated there.
F1/F2/F3 are declared in the config, before the run.

**🔴 CORRECTION TO THAT CONFIG'S OWN RECORD — read before quoting it.** Its
`slice_note` says "no torch". **Wrong: the torch is SAPPHIRE, eps = 9.39** —
`GEO_DESIGN` carries the design torch by default and the log confirms it. So
this run IS on `h3-field-01`'s slice (the comparison that matters) but is NOT
on `h3-lambda4-02`'s, which was DRIVEN with a VACUUM torch. Same four ld
values; the torch moves f0 by ~10.4 MHz, i.e. ~0.42 % in L/(lambda/4).
⚠️ **The config was NOT edited to fix this, deliberately:** `stamp()` is
sha256 of the config file and every artefact name carries it, so an edit
mid-run would orphan the solves and silently empty the resume set. The
correction belongs in the write-up.

**LANDED SINCE:** `h3-lambda4-02` finished — `KNOWN.md` § MEASURED, Q_ext has an
interior minimum near lambda/4. ⚠️ Its heading first read "lambda/4 CONFIRMED"
and was downgraded: **surviving a falsifier is not confirmation** (user). One
thing IS falsified — the monotonic-area prediction.

**NOT LANDED, ON PURPOSE:** the E-vs-H results. User: *"I don't think we should
be updating KNOWN without going through the full process."* `ehratio.py` is the
evaluation layer; the numbers are in the session and the result files only.

**🔑 THE WATCHER IS STANDARDIZED — see CONVENTIONS §7bq.** It had failed FOUR
times, never the same way twice, and CONVENTIONS had nothing on it. `ops/watch.sh
<slug>` is now the only watch command to type; every line is mirrored to disk so
a buffering caller cannot hide a live watch; `ops/status.sh` is a SNAPSHOT and
`ops/remote.sh` no longer calls it a watch.

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

## 🔴 THE RE-DERIVE LIST — what is now known to be unsupported

**Opened 2026-08-25.** Each of these was believed, is now marked TENTATIVE or
open, and **must not be quoted until re-derived.**

| # | what | why it is not supportable now | cost |
|---|---|---|---|
| ~~R1~~ | ✅ **RESOLVED 2026-08-25 — ε_⊥c = 9.39, MEASURED** | Krupka, Huang & Tung, *Meas. Sci. Technol.* **16** (2005) 1014, fig 10: *"perpendicular to the anisotropy axis … **9.39 ± 0.5 %** for sapphire"*, by **TE0np modes in a cylindrical sample — our own mode family**. So **11.6 is ε_∥c** and `geometry.py` had the axes inverted. Canonical value updated; **the constant is NOT flipped yet** — that moves every stored f₀ and belongs with the restoration | — |
| ~~R2~~ | ✅ **CLOSED 2026-08-25 — torch shift = −10.40 MHz** | `e3-torch-01`, matched pair (B_sap ε=9.39 vs B_vac ε=1.0, wall-loss only). **Not the cancellation I predicted** — the R-era slope was 4.4× too large; the real sensitivity is **1.50 MHz per unit ε**. ⚠️ The old −13.87 was wrong twice: wrong ε *and* cross-geometry. 🔴 **~10.4 MHz is 6.5× the anchor band — the restoration KEEPS its urgency** | — |
| ~~R3~~ | ✅ **RESOLVED 2026-08-25 — NO SOLVE NEEDED** | Decimating the anchor's own sweep gives Q_L error vs samples-across-linewidth: 30 → −0.8 %, **16 → −7.0 %**. The cold case had **14 samples** and read **−7.1 %** against eigen. **The driven/eigen "disagreement" was SAMPLING, quantitatively.** ✅ Cold Q_ext = **9,117** (eigen) stands; the driven 8,462 is the artefact | — |
| **R4** | 🔴 **E3's closure (F1)** | ⚠️ **REDIAGNOSED 2026-08-25.** Not sapphire+plasma — `h3_qext`'s anchor case **timed out with a VACUUM torch** (159 PCG failures, 0 iterations) at ε = −1.46. **ε-near-zero conditioning, the prediction recorded before the run.** η_plasma stays unquotable | 🔴 **the PRECONDITIONER, and it does NOT depend on R1** |
| ~~R5~~ | 🔴 **FALSIFIED 2026-08-26 — the correction goes the OTHER WAY.** The design cavity MEASURES Q₀ = **43,259** (barrel) / 43,253 (cap), i.e. **−0.61 %** against the stored 43,523, not +1.46 %. ⚠️ **44,160 was `e3` B_sap = WALL LOSS ONLY**, excluding sapphire's tan δ = 3.5e-5. A partial-loss Q compared against a total-loss Q — §7c's η trap again. ✅ E3's channels recombine (1/44,160 + 1/1,911,259 → 43,163) to within **0.22 %** of the measurement, so both are corroborated. **Not promoted**: the stored value is CAP-mount and the design mount is item 7's open question. See KNOWN.md § THE TORCH RESTORATION | ✅ **done** |
| ~~R5-old~~ | ⚠️ ~~`eta.reference` = 43,523 — CONFIRMED, correction now sized~~ | ✅ Independently reproduced by `e3-torch-01` B_vac (43,522.8) from a rig that built its own mesh. 🔑 The design-torch value is **+1.46 %** higher (44,160.1), not the +2.0 % estimated at the wrong ε | re-measure with the restoration |

✅ **R1 WAS THE ROOT OF FOUR OF THE FIVE, AND IT IS NOW CLOSED BY A CITATION.** R2 collapses to *"probably ~0, verify"*; R5's 2 % η correction largely evaporates with it; **R4 was never dependent on it** — that is ε-near-zero conditioning and still needs the preconditioner. 🔑 **The remaining physics is R4 plus item 7.**

### ✅ ANSWERED 2026-08-25 — and my first answer was WRONG

⚠️ **I first landed "≳30 samples across the 3 dB width for <1 % in Q_L", derived
from ONE density. Testing it on three killed it:** 1e20 showed **0.0 % error at
TEN samples** while cold showed **−12.5 % at eight.** Sample count does not
determine the error.

🔑 **THE ERROR IS EDGE QUANTISATION.** Q_L comes from the 3 dB width, and the
edges were snapped to the nearest GRID POINT. Each edge can be off by up to one
step, so the bound is **|ΔQ_L/Q_L| ≲ 2/N** — and where it lands inside that
bound depends on whether the width happens to be commensurate with the step.
**1e20's 16.00 MHz width is exactly 80 × 200 kHz, so decimation moved nothing.
That is luck, not accuracy.**

✅ **THE FIX IS INTERPOLATION, NOT MORE SAMPLES** — linearly interpolate the
|S11| crossing, as for the vertex:

| density | N | grid edges | **interpolated edges** |
|---|---:|---:|---:|
| cold | 13 | −6.4 % | **+0.0 %** |
| cold | 6.5 | −18.1 % | **−0.8 %** |
| anchor | 14.8 | −7.3 % | **−0.3 %** |
| 1e20 | 9.9 | −1.1 % | **−0.1 %** |

> ✅ **SPEC: interpolate both the vertex AND the 3 dB crossings. Then ~10 samples
> across the width suffices for ≲1 %.** Without interpolation, no achievable
> sample count is reliable — only commensurate ones are accurate, and you cannot
> know in advance which those are.

### ~~CHEAP AND UNCLAIMED: the sweep step a target Q accuracy requires~~

**From the conjugate-pair framing (KNOWN.md).** Driven Q error tracks samples
across the linewidth: **14 → −7.1 %**, **80 → −3.3 %**. Two points, not a law.
**Nothing in this programme specifies a step for a target Q accuracy** — every
`COARSE_STEP`/`FINE_STEP` was chosen by feel.
✅ **One mesh we already have, three step sizes, Q vs samples.** It would size
every future driven sweep and retire R3 (cold Q_ext, sidelined as
under-resolved) at the same time.

## 🔴 THE GEO RE-RUN LIST — opened 2026-08-25, after the GEO fix

**User: *"We can't leave bugs in place just because they might invalidate
results. We have to fix, and then add a new queue item to verify or re-run."***
✅ The bugs are fixed. This is the verification debt they created.

### What was wrong

**`GEO` carried `A_MM, L_MM = 103.70, 88.53` — D/L = 2.343, the cavity H1
REJECTED.** H1's answer is D/L = 1.525 (a 88.0045, L 115.4158), stated plainly
in `KNOWN.md`. The literal sat as GEO's **default**, so any rig that did not
append its own `--radius/--length` meshed a cavity nobody is building.

✅ **The H3 design record is PROVEN unaffected — by artefact, not by argument
(§7bm).** Every H3 mesh SIDECAR records `radius 88.004517 / length 115.41576`,
which is H1's cavity. That is the consumer's own record of what it actually
meshed, so it discharges the burden. `h3-bore-01`, `h3-loop-barrel-01` and the
e3/h3_qext meshes all carry it. **Nothing measured this week moves.**

### What was fixed

| | |
|---|---|
| `cavity.d_over_l` = 1.525, `source.f0.ghz` = 2.45 | **declared** — the shape now has one home |
| `physics.design_point(d_over_l, f_ghz)` | the ONE derivation. `A_MM/L_MM` now DERIVED, so GEO cannot disagree with H1 again |
| `DL` in `e0k2_anchor` + `h2_groove` | were **two** copies of the same literal → bound |
| the frozen groove `(5.0, 10.0)` | was in **SEVEN** files → `cavity.groove.mm`, 7 consumers |
| the design loop `11.0, 8.0` | was in **NINE** files → `loop.size.mm`, 9 consumers |
| `CAP_R_FRAC`, `LOOP_RW`, `LOOP_GAP`, `LOOP_PHI` | bound; the last two are **TENTATIVE** and now say so at the call site |
| `e0q_wallloss` `AL = 3.5e7` | bound; `AG` = silver kept as an explicit COMPARATOR |
| `preflight` geometry pattern | geometry was **invisible** to the linter — that is why none of the above was ever flagged |

🔑 **Every bound site was asserted IDENTICAL to the literal it replaced before
the edit was kept.** 16 duplicates collapsed to 2 canonical names, no number
moved.

### 🔴 THE DEBT — rigs that meshed the LEGACY cavity

These used `GEO`/`GEO_DESIGN` **without** overriding, so they ran D/L = 2.343.
🔴 **UNDER §7bm THEY ARE INVALID UNTIL A RE-RUN SAYS OTHERWISE.** I first wrote
that their conclusions were "mostly self-consistent, because closed form was
evaluated at the same a/L they meshed". **That is an argument, not a
measurement, and it does not discharge the burden.** They are E0 instrument
rigs rather than design rigs, which affects PRIORITY, not validity.

⚠️ **Do not cite any number below until its rig is re-run.**

| rig | what it claims | action |
|---|---|---|
| `e0b_offset` | mesh offset invariance | re-run on H1's cavity |
| `e0f_geomorder` / `e0f2_geomorder` | geometric order | re-run |
| `e0j_frontier` | cost frontier | re-run — **sizing advice descends from this** |
| `e0kp_meshfloor` | mesh floor | re-run |
| `e0k_driven_vs_eigen` | driven vs eigen | re-run |
| `e0m_meshthreads` | thread scaling | re-run (cost only; low value) |
| `azimuthal`, `meshdiff`, `meshstage`, `cachetest` | utilities | no claim — no re-run |

⚠️ **`e0l_scaling`, `facetcount`, `resplit` keep the legacy literal ON PURPOSE**
— they ANALYSE meshes built at those dimensions, so binding them to H1 would
silently break the comparison. Each is now marked `# LEGACY` in place. **Nothing
in them is a design number.**

### 🔴 AND THE THIRD DEBT — 30 RESULT FILES CARRY NO STAMP

**User, 2026-08-25: *"result.json is not a valid filename."*** Correct, and
chasing it found a hole bigger than the name.

🔴 **`slug.check_stamps()` was KNOWN-SLUG-DRIVEN, so it was nearly blind.** It
only inspected slugs that already have a `baseline-*.json`. Every artefact whose
slug never got a config was invisible: **30 of 32 `*.result.json` files carry no
stamp and the check reported ONE.** ⚠️ *An audit that can only see what is
already registered is not an audit* (§7d) — and this is the second instance
today, after the linter that could not see geometry.

✅ **Fixed both ways:**
- `check_stamps()` now sweeps **what is on disk**, not what is registered.
- `outfile()` **refuses** a suffix that is a path, a config name, or one already
  carrying a stamp — so a double-stamped or unqualified artefact cannot be
  produced by the normal route.
- `slug.unstamped_artefacts()` makes the burn-down countable.

**The 30, by family:**

| family | files | status |
|---|---:|---|
| `e0b` `e0f` `e0f2` `e0j` `e0k` `e0kp` `e0m` | 7 | **already queued above** — same rigs, same re-run |
| `e3` | 7 | E3 closure; F1 still open anyway |
| `e0k2` | 6 | instrument anchors — several already superseded |
| `e0v` | 3 | — |
| `e0c` `e0d` `e0e` `e0q` `h1` `h3` `h4` | 7 | one each |

🔴 **UNDER §7bm THESE ARE NOT CITABLE AS CURRENT RESULTS WITHOUT A RE-RUN.**
Their inputs cannot be verified — that is precisely what the stamp exists to
prove. ⚠️ **This does NOT mean they are wrong**; it means the record cannot show
what produced them. The two that DO carry stamps (`h3-bore-01`,
`h3-loop-barrel-01`) are the only fully provenanced results in the tree.

🔑 **Priority: LOW, and deliberately so.** Most are E0 instrument rigs already
queued for the GEO re-run, which will re-produce them stamped as a side effect.
**Do not re-run them for the stamp alone** — re-run them when their claim is
needed, and take the stamp then.

### 🔴 THE FOURTH DEBT — THE MESH SIDECAR DOES NOT RECORD THE LOOP SIZE

**Opened 2026-08-27, by `h3-lambda4-02`.** `geometry_mm` records `loop_cap_r`,
`loop_mount`, `loop_gap2`, `loop_flange_r`, and `loop_phi_deg`/`loop_tilt_deg`
sit alongside it — **but not `[ld, lw]`, the loop's actual size.**

🔴 **This is the artefact the programme relies on to discharge §7bm.** The GEO
debt was closed "by artefact, not by argument" because every mesh sidecar
recorded `geometry_mm.radius/length`. For a loop sweep the equivalent record
does not exist, so when `h3_driven`'s tags collided there was **nothing in the
sidecar to bind a point to its ld** — it took a re-mesh (`verify_ld_tets.py`)
to do by measurement what the sidecar should have carried for free.

✅ **THE FIX IS ONE FIELD:** `geometry_mm.loop = [ld, lw, rw, gap]` in
`geometry.py`, alongside `groove`. Then assert it at the consumer, the way
`cavity.groove.mm` is asserted (`mesh-is-what-you-ordered`).
⚠️ It changes no mesh — sidecar content only — but it touches `geometry.py`,
which owns `GEO`/`GEO_DESIGN` and the groove. **Verify the tet count is
unchanged on one mesh before and after.**

### 🔴 THE OTHER DEBT — values still literal

The widened linter surfaced residue that was invisible before. It is
grandfathered so it cannot grow, and **the list may only shrink**:

- `h3_loaded.Q_BARE_WITH_LOOP = 29,854` and `Q_BARE_EMPTY = 44,384` — **both are
  RETRACTED η references** (§7c). These should be **DELETED, not bound.**
- `h3_step3.H3COLD_PICK_GHZ = 2.440003` — from a retracted `h3_cold` result.
- `h3_margin.NE = 1e20` — the superseded density (§7ab), in a rig still using it.
- `h3_qext.LOOPQ_EIGEN_NO_TORCH = 9,231` — has a canonical home
  (`cavity.Q_ext`, no_torch context); bind it.

**Verification for the whole item:** re-running any one E0 rig on H1's cavity
must reproduce its CONCLUSION (the instrument claim) while changing its
NUMBERS. If a conclusion flips, that rig's claim depended on the cavity and was
never an instrument result.

## 🔴 THE MATERIALS QUEUE — opened 2026-08-27

**User: *"We should also try to get rid of all PEC that would also be a real part
in a real build. I'd guess aluminum for the cavity, copper otherwise."***

⚠️ **The premise needed one correction and the conclusion survives it.** Almost
nothing is spuriously PEC: `geometry.py:990` tags the wall TOPOLOGICALLY — every
face with a single adjacent volume — and the loop wire is cut OUT of the vacuum,
so its surface has one adjacent volume and is swept into attribute 90 with the
cavity wall. Confirmed from the resolved config Palace actually ran:
`Conductivity {Attributes:[90], 3.5e7}` and `PEC {Attributes:[91]}`, where 91 is
only the port face in the shorted control.

🔴 **So the loop is not PEC — it is ALUMINIUM, and indistinguishable from the
wall.** Two defects, one cause.

| A | **the loop is the wrong metal** | it should be copper 5.8e7, not the wall's 3.5e7 |
| B | **its loss cannot be separated from the wall's** | one attribute, one Conductivity entry, one number out |

⚠️ **B invalidates a claim I made today.** "The coupler eats 45.3 % of cold
dissipation at λ/4" is NOT supportable: the solve cannot tell wire loss from wall
loss. **What is measured is that the loop's PRESENCE raises dissipation on the
conducting surfaces by 83 % (Q₀ 44,414 → 24,292), location unknown.**

### The order, and why

| | do | why here |
|---|---|---|
| **A1** | **give the loop its own attribute + copper** | 🔴 **FIRST.** It moves every Q₀ and every loss number downstream. Re-running anything before it burns solves on numbers that will change (§7bp) |
| ~~A6~~ | ✅ **DONE** — the surface/volume rule has ONE definition | 🔴 **21 SITES ACROSS 18 FILES**, not the "nine" I first reported — I had capped the grep with `\| head`, and **undercounting a duplication is how you fix most of it and leave the rest to fail later**. All bound to `volume_attrs(meta)`, proven identical to the expression it replaced on a pre-loop sidecar. `e0k2_anchor.shared_energy_list` now takes `meta` instead of `attrs` (an attrs dict CANNOT say which entries are surfaces; only the sidecar can) and its five callers are updated. Zero new lint warnings, diffed against HEAD |
| A2 | re-run the three missing `h3-ehratio-01` cases | needs a SETTINGS decision (645 / 1,402 NLEPS without convergence is conditioning, not impatience) **and** A1 |
| ~~A3~~ | ✅ **DONE** — `h3_loopq`'s V1 anchor is configuration-aware | It matched the anchor case on `(ld, lw)` + `grooved` only, so every barrel+capacitor run was compared against a **cap loop with no capacitor**. Now SUPPRESSES with the reason instead of firing. `check_v1()` is a pure function of the points; all five paths exercised, two on real landed data |
| ~~A4~~ | ✅ **DONE** — item 7 step 4 **RETIRED**, not restated | Stronger than expected: **area is bounded by length**, area_max = (L + gaps)²/8, and the design sits at **97.5 %** of its own bound. The surviving axis is **aspect ratio at fixed L** — the radial/azimuthal split of the conductor |
| ~~A5~~ | ✅ **DONE** — item 7 step 3 reframed, and a probe added | The **port gap is the tighter break** (0.3 vs 0.5 mm) and carries the drive, yet had no probe while the series gap had one. `port_gap` added to `h3_loopq`; `fieldcheck` maps it to a limit. ⚠️ `values.get` REFUSED its width as TENTATIVE — correct, it has no owner |

### A1 — what it must prove, not just do

`loop.conductivity.s_per_m` = 5.8e7 is declared in `baselines.json` and consumed
by **NOTHING** — zero hits across every rig. This is its first consumer, so the
declared-but-unused pattern is exactly the risk.

- ✅ **V** tet count UNCHANGED (a boundary retag is not a geometry change);
  the wall attribute's face count drops by exactly the loop's faces; the new
  attribute contains only wire faces.
- 🔴 **F** if Q₀ on a known case does not move AT ALL, the new attribute is not
  being consumed and the change is cosmetic. Copper is less lossy than
  aluminium, so **Q₀ must RISE** — a fall means the assignment is inverted.
- 🔑 The payoff is the PARTITION: wall loss and loop loss as separate numbers,
  which is what the 83 % question actually needs.

### A3 — the V1 anchor fires on the wrong comparison

`h3_loopq` compares every run against `h3_step3`'s **cap loop with no series
capacitor** (Q_ext 9,117, β 4.8) and printed *"THE ANCHOR DOES NOT REPRODUCE —
treat every other row as SUSPECT"* over a run whose own declared control passed
at 0.6–1.9 %. **A guard that fires when it should not trains you to ignore it.**
It should suppress on a non-cap config the way `eta` already does.

## THE QUEUE

| # | item | status |
|---|---|---|
| 1 | Matching network required | ✅ answered — tuner spec in `../control-loop/` |
| 2 | **Anchor n_e** | ✅ **7.3–8.6e18**, from MICAP's measured 5220–5270 K |
| **7** | 🔴 **DESIGN the loop — barrel mount, then the SERIES CAPACITOR** | **THE BIGGEST LEVER LEFT.** ~45× in Q_ext is calculated and never simulated; and I ∝ √VSWR, so it is the only thing that touches the tuner's thermal wall |
| 3 | Test the coupler class | 🔴 **REOPENED — and it is the biggest lever left.** ❌ Aperture is out (patented; the cavity IS the waveguide). 🔴 **But the LOOP was never designed** — forced into existence so driven solves would have a port; `h3_loopq` swept AREA only. **Q_ext = 9,231 floors ONE arbitrary family.** VSWR 85→20 needs 4.2×, β=1 needs 84×. See CONVENTIONS §7al |
| 4 | **H3's HOT leg** | ✅ **DONE — H3 IS COMPLETE** |
| **5** | **PLAN E3 — the energy-balance closure** | ⚠️ **RAN (EXIT=0), 3 of 5 landed.** ✅ **B, D, E.** ✅ **F2 resolved by a bound** (η_diel ≤ 2.27%; PLAN's ~2% CONFIRMED). ✅ **E gave an eigen↔driven cross-check — 70 kHz and 3.42% — which RESTORES V1's anchor.** 🔴 **A, C failed on the sapphire+plasma ε-contrast, already documented in `h3_driven` lines 10–11 BEFORE E3 was written** (§7an). 🔴 **F1 untested; η_plasma unquotable** |
| 6 | H4 ignition | ⏸️ parked |
| ~~8~~ | ✅ **H3 AT THE ANCHORED DENSITY — DONE** | `h3-driven-anchor-01`, 9 points. **f₀ 2.458529, Q₀ 105, η 0.9976, VSWR 75–82, slew +7.04 MHz, margin 41.5 MHz.** ⚠️ vacuum torch (R1/R2) |

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

### 7e. ✅ ITEM 7's MEASUREMENT PHASE IS CLOSED — and the objective changed

**User, 2026-08-25: *"We have enough information for optimization at this
point."*** ✅ Agreed. **9 Q_ext values across 4 design families**, spanning
8,716 → 322, with every control reproducing exactly.

| step | question | answer |
|---|---|---|
| 1 | barrel vs cap mount | ✅ barrel is **5.6 % better**, and free. My 1.93× prediction was falsified; the 1.39× field ratio behind it was a **legacy-cavity** number |
| 2 | does a series capacitor work? | ✅ **7.6×** at the bare-wire gap. Falsifier needed ≥4× |
| 2b | which way does the gap move it? | ✅ **wider** — 12.1× at 0.75 mm |
| 2c | where is the optimum? | 🔴 **not bracketed** — 27.0× at 2.25 mm, still falling |
| — | **is minimising Q_ext even right?** | 🔴 **NO** — see KNOWN.md § CORRECTION |

🔴 **THE OBJECTIVE IS NO LONGER "MINIMISE Q_ext".** Q_ext serves cold AND
loaded, whose Q₀ differ 265×, so the sweeps were sliding along a **trade**:
loaded VSWR 83 → 3.1 bought cold ignition power 556 W → 45 W. **The minimax
fixed loop is Q_ext ≈ 1,700 (VSWR ~16 in both states) — roughly where the gap
sweep STARTED.**

### ✅ MEASURED — THE AZIMUTHAL LOOP COUPLES ~10x LESS (2026-08-30)

**FIRST azimuthal Q_ext ever measured.** Reference geometry, h = 3 mm,
L(arc) = 12.24 mm, 1 mm wire, grooved, unwound 17.94 mm, clearance 2.00 mm.
Slug `h3-azim-01`, stamp `9e60089f`.

    pec     Q0    = 43,744   f0 = 2.439429   P>=1.0000  spread 0.0000
    lumped  Q_L   =  9,154   Q_ext = 11,576  beta = 3.779   OVERCOUPLED

⚠️ **PROVENANCE IS THE WATCH-LOG MIRROR, not the artefact.** The host was
reclaimed mid-grid; `h3-azim-01.9e60089f.result.json` is on the EBS volume and
has never been fetched. Numbers above are from `h3-azim-01.watch.log`. Re-fetch
and reconcile before this is cited anywhere.

**Against the rectangular barrel loop (13x6, `h3-aspect-02`): beta 36.8 -> 3.78.**
User: *"Already at that VSWR, it's workable."*

⚠️ **THE COMPARISON CROSSES RUNS.** The rectangular figure is from a DIFFERENT
aspect-ratio cavity, and the `-01`/`-02` offset is still unresolved and parked.
The ~10x gap is far larger than that offset so the DIRECTION holds, but the
ratio is not a measurement until both are on one cavity. See
[epoch comparisons are not measurements].

🔑 **The null hypothesis below is REFUTED.** It argued a topology could only move
VSWR through Q_ext, and predicted no benefit. Q_ext is exactly where it moved:
1,097 -> 11,576. The reasoning was right; the prediction of "no benefit" was
wrong, because it assumed the two topologies reach comparable loop areas at
comparable coupling. They do not — the azimuthal loop sits where it barely
perturbs the mode (P >= 1.0000, spread 0.0000, Q0 cost 0.75% vs 6-12%), so it
extracts far less energy for the same conductor length.

### ✅ MEASURED — beta ∝ AREA^4, and critical coupling is BRACKETED (2026-08-30)

Azimuthal wire loops, slug `h3-azim-01` stamp `9e60089f`, all P >= 0.9999.
Area = L x h. Q0 is flat at 43,744-43,937 across all four, so the loop barely
perturbs the mode and every difference is in Q_ext.

    h   L(arc)  A/mm^2   Q_ext     beta     VSWR
    2   10.2      21    112,004   0.392     2.55   undercoupled
    2   12.24     25     62,800   0.699     1.43   undercoupled
    2   14.2      29     31,111   1.410     1.41   OVERCOUPLED
    3   12.24     37     11,576   3.779     3.78   OVERCOUPLED

🔴 **SUPERSEDED — "area governs" HOLDS ONLY FOR h <= 3 mm.** See the
h=4 swap test below. Area^4 fits 6 points to <10% and then fails by 29%.

🔴🔴 **RETRACTED 2026-08-30 — THE SATURATION WAS THE WRONG VARIABLE.**
*User: "I also worry that h is mis-characterized. The distance to wall should be
the dominant term, so a thicker wire or strip has the same wall distance. h
should just be the height of the stud that the strip/wire sits on."*

`h` was the conductor CENTRELINE height; wall clearance was `h - t/2`, so it
moved with conductor thickness. Re-fitting the SAME wire data at L = 10.2
against CLEARANCE instead:

    vs centreline h (what was fitted) : 3.89 then 2.99   -> 23% apart
    vs CLEARANCE (the stud height)    : 2.27 then 2.12   ->  7% apart

**There is no saturation.** Centreline height and wall distance differ by a
fixed offset, so a power law in one cannot be a power law in the other — the
"saturation" is the residual of fitting the wrong variable. ⚠️ This also
retracts what was built on it: **"buy coupling with L, not h" is withdrawn.**
Both are live levers; L simply has the steeper exponent (3.87 vs ~2.2).

🔴 **AND WIRE-vs-STRIP WAS NEVER AT MATCHED WALL DISTANCE.** clearance = h-t/2,
so at every h the 5x1 strip sat 0.5 mm FURTHER out than the 1 mm wire —
systematically. The 3.0-4.0x ratio is confounded with that offset and must not
be quoted as a cross-section effect until re-measured at matched clearance.

⚠️ SUPERSEDED, kept for the record — the original claim:
🔑 **beta ∝ L^3.88 x f(h), and f SATURATES above h = 3 mm:**

    L-exponent at h=2 .......... 3.87     rock steady
    L-exponent at h=3 .......... 3.89
    h-exponent, L=10.2, 2->3 ... 3.89
    h-exponent, L=10.2, 3->4 ... 2.99     <-- saturates

✅ **THE h=4 SWAP TEST IS WHAT CAUGHT IT.** h=4/L=10.2 (A=42) vs h=3/L=14.2
(A=43): near-identical area, beta 4.486 vs 6.872 — 1.53x apart. Area alone
cannot produce that. Area^4 predicted 6.29, MEASURED 4.486, 29% low, against
residuals of 4-9% on every earlier point.

🔑 **Why A^4 looked so good first:** while both exponents sit near 3.9,
L^3.9 h^3.9 = (Lh)^3.9 ~ A^4. Area was NEVER the governing variable — it was a
coincidence of the two exponents matching inside h = 2-3, and it dies as soon
as height leaves that band. [epoch comparisons are not measurements] applies to
laws too: a fit that works over a narrow span is not a mechanism.

⚠️ Physical reading, UNVERIFIED: the loop stops gaining flux once it reaches
out of the strong near-wall H field. That is a ceiling on HEIGHT but not on
azimuthal run. **Buy coupling with L, not h.**

✅ The beta = 1 design point (h=2, L~13.4 mm) is INSIDE the validated band and
is unaffected — both exponents are ~3.88 there.


✅ **THE CONTROL DECIDED IT, OUT OF SAMPLE.** h=2/L=14.2 (unwound 17.90 mm) and
h=3/L=12.24 (unwound 17.94 mm) are the SAME conductor length split differently.
Unwound length predicted beta = 3.78; area^4 predicted 1.42. **MEASURED 1.410.**
Area governs; unwound length does not. This is why L and h were made
independent — the two hypotheses were 2.7x apart and one case separated them.

🔴 **I GOT THIS WRONG TWICE FIRST, and both are worth keeping:**
1. Predicted beta ∝ A² (textbook magnetic loop, flux ∝ area, beta ∝ flux²) —
   predicted 1.2 for the 21 mm² case, MEASURED 0.392.
2. Then fit L-only and h-only exponents from 2-point pairs (3.2 and 4.2),
   concluded "not a function of area at all, beta ∝ L^3.2 h^4.2". **REFUTED by
   the control**, which lands on the single-variable area^4 curve. Those pair
   exponents were local curvature in 2-point fits, not real anisotropy.
⚠️ A^4 is DOUBLE the textbook exponent and is so far EMPIRICAL ONLY — no
mechanism. Do not extrapolate outside 21-37 mm² on it.

🔑 **DESIGN POINT: beta = 1 at A ~ 26.8 mm^2** — at h=2, L ~ 13.38 mm;
at h=3, L ~ 8.92 mm. VSWR = 1. Interpolated on the A^4 fit, NOT measured;
the bracket around it IS measured (0.699 at 25, 1.410 at 29).

**Rectangular barrel 13x6 on `h3-aspect-02` was beta 36.8 / VSWR ~37.**
User on the first azimuthal point: *"Already at that VSWR, it's workable."*

### ⏳ OPEN — h=4 row, and the 9 strip cases

### ⏳ OPEN — does beta reach 1, and what sets it

18-case grid launched, 1 complete, host reclaimed at case 2 of 18.
Grid: L in {10.2, 12.24, 14.2} mm x h in {2,3,4} mm x {1 mm wire, 5x1 strip}.
L and h are INDEPENDENT (unwound = L + 2h - gap), so the L+2h = 18.24 diagonal
is an internal control on whether unwound length alone predicts Q_ext.

🔎 **PREDICTION, UNTESTED:** if beta scales as loop area squared, h=2/L=10.2 at
21 mm² against this 37 mm² gives beta ~ 3.78 x (21/37)² ~ 1.2, i.e. near
critical. That case was solving when the host died. It is a sharp, falsifiable
number — record what it actually returns, do not quietly drop it.

⚠️ **A dead spot on a SATURDAY is a first** — every prior reclamation was a
weekday. Do not assume weekend capacity is safe.

---

### 🔎 QUEUED — THE AZIMUTHAL LOOP, and the question is VSWR (2026-08-28)

**User: *"the other loop option: one that runs azimuthally along the wall at the
cavity equator ... My main interest in the other loop shape is if/how it manages
VSWR."*** ⚠️ Framed on VSWR deliberately — my first analysis emphasised mode
perturbation, which is not the question.

✅ **PRIOR ART: NONE.** No azimuthal / wall-following / equatorial loop appears in
`KNOWN`, `PLAN`, `NEXT`, `CONVENTIONS`, `HYPOTHESES` or `OPTIMIZER`. Only two
mounts have ever been meshed — cap and barrel.

### 🔴 THE NULL HYPOTHESIS IS "NO VSWR BENEFIT", AND IT IS STRONG

VSWR is set by β = Q₀/Q_ext. **Q_ext is cold and geometric; Q₀ swings ~400×
cold→loaded.** So a topology can only move VSWR through Q_ext.

🔑 **Both topologies are the SAME optimisation** — a rectangle *closed through the
wall*, conductor on three sides, the wall closing the fourth for free:

| conductor 38 mm | max area | at |
|---|---:|---|
| radial (current) | 180.5 mm² | ld = 9.5 |
| azimuthal | **191.4 mm²** | h = 9.5 |

**6 %**, all of it the outer arc being longer than the inner. And the area sits
over the same J₀ range (r/a 0.875–1.0 vs 0.892–1.0). Same flux, same Q_ext, same
VSWR. **Against Q_ext moving 5.6× across the ld sweep, 6 % is nothing.**

### 🔑 THE ONE MECHANISM THAT COULD BREAK THE NULL — image loading

A conductor running **parallel and close to** the wall is image-loaded: its image
current largely cancels its own, cutting self-inductance and changing its
effective electrical length. A radial leg poking into the volume is not.
**Since λ/4 governs Q_ext (KNOWN.md § MEASURED), moving the effective length
moves the resonance — and Q_ext with it.**

> **The measurement:** Q_ext vs conductor length for the azimuthal loop, plotted
> against the radial curve already measured — **1,325 / 359 / 1,135 / 2,024 at
> L/(λ/4) = 0.82 / 1.02 / 1.22 / 1.41.**
>
> 🔴 **F1 — if azimuthal Q_ext falls on the SAME curve vs conductor length,**
> image loading is negligible, the topology is a MECHANICAL choice and not an
> electrical one, **VSWR is unchanged, and the decision goes to buildability.**
> 🔴 **F2 — if it falls on a DIFFERENT curve,** the λ/4 point has moved and there
> is a new axis: the same Q_ext at a different physical size, which is exactly
> what the tolerance problem wants (d ln Q_ext / d ln L ≈ 4–6.5 means ±0.37 mm
> is ±5 % in Q_ext).

⚠️ **What NOT to spend the run on.** Whether it perturbs TE011 less — the arc
runs *along* the wall current (K = H_z φ̂) the way the groove does, while radial
legs cross it — is a real and testable side-effect, but it is NOT the question.
Record Q₀ and purity because they come free; do not size the sweep for them.

### What it costs to build

A third branch in `geometry.py` beside cap and barrel. The arc is free —
`occ.addTorus` takes an angular extent — plus two radial legs and the existing
fuse/cut/port machinery. By analogy with the current design: **port gap in the
ARC** (the side parallel to the wall, as the crossbar is now), **series gap in a
radial leg**.
✅ **The 2026-08-27 loop-surface machinery carries over unchanged**: an arc at
z = 0 with circular cross-section still has z-extent exactly 2·lrw with centroid
at z = 0, so the copper attribute, the partition assertion and the leg probes all
work as-is.
🔴 **`geometry.py` is where this session's regression came from.** Same
discipline: `--dump-faces` first, tet-count A/B with the branch disabled, and the
partition assertion must pass before any solve.

### What item 7 still owes, in order

| | | blocked on |
|---|---|---|
| **1** | **Choose the target: minimax, β = 1 loaded, or TWO LOOPS** | 🔴 **`../ignition-options/`** — the choice is theirs, not this programme's. 🔑 **Two loops (user, 2026-08-25) gives β = 1 in BOTH states** and makes the choice moot; its cost is a second port in `geometry.py`, a switch, and an unmeasured mode perturbation |
| ~~2~~ | ✅ **DONE 2026-08-27 — series-gap E-field measured.** `fieldcheck`: **1.334 MV/m at 1 kW cold, limit 5.44, margin 4.08×** (ld 11, gap2 0.5). The precondition on gap widening is discharged | — |
| **3** | 🔑 **REFRAMED (A5) — the PORT gap is the tighter break and was NEVER probed.** 0.3 mm against the series gap's 0.5, and it carries the **drive**; the series gap had a probe and a margin, this had neither. ✅ `port_gap` probe added to `h3_loopq`, and `fieldcheck` now maps it to a limit. ⚠️ Its width is **TENTATIVE with no owner** — `values.get` REFUSED it until the call site said `allow_tentative`, so the margin is only as good as a number nobody chose. 🔑 It is also a **length trim**: 0.3 → 1.0 mm is −1.9 % in L ≈ **8–12 % in Q_ext** | nothing |
| ~~4~~ | 🔴 **RETIRED AS WRITTEN (A4) — "re-sweep AREA" cannot do what it says.** Area is **bounded by length**: with S = (L + gaps)/2, area ≤ S²/2, i.e. **area_max = (L + gaps)²/8**. The design's 176 mm² is **97.5 %** of the 180.5 mm² available at its own conductor length, so *"increase area"* and *"increase length"* are the same instruction and the length sweep already ran it. ✅ **The real independent axis is ASPECT RATIO at fixed L** — ld + lw constant changes the **radial/azimuthal split of the conductor** (how much links H_z), which is an orientation question, not an area one. Area along that line only spans 96–180 mm² and needs ld=16/lw=3 to move at all | nothing |
| 5 | Feed transition, support, material, cooling (7d.B) | **hardware design, not EM sweeps** |

⚠️ **Do not run another gap sweep before 1 and 2.** Widening further optimises
an objective that may be wrong, along an axis whose failure mode is unmeasured.

### 7d. 🔴 A BUILDABLE LOOP IS NOT THE SAME AS A LOW Q_ext — opened 2026-08-25

**User: *"I think we have more design to do on a buildable loop, beyond the VSWR
problem."*** ✅ Correct, and the gap is wider than it looks. Steps 1–2c have been
optimising **one number**. The loop as a physical object is barely specified.

#### A. Dimensions with NO provenance — and everything measured sits on them

| | value | status |
|---|---|---|
| `loop.wire_r.mm` | 1.0 | 🔴 **TENTATIVE** — a `geometry.py` default, never chosen |
| `loop.gap.mm` (PORT gap) | 0.3 | 🔴 **TENTATIVE** — same |
| `loop.size.mm` | 11 × 8 = 176 mm² | ⚠️ swept on the **CAP** at N=1; item 7 already records that it **does not transfer** to the barrel |

🔑 The store refuses these without `allow_tentative=True`, and `e0k2_anchor` has
to say so at the call site — so the lack of provenance is visible, not hidden.
**But Q_ext = 720 was measured on top of all three.**

#### B. Not in the model at all

- 🔴 **THE COAX TRANSITION DOES NOT EXIST.** `geometry.py` puts a **lumped port
  on an internal face** — its own comment says *"no coax transition needed"*,
  which is true of the SOLVER and false of the hardware. There is no connector,
  no dielectric bead, no wall penetration. A real feed adds reactance and its
  own discontinuity, and **Q_ext is measured at that face.**
- 🔴 **MECHANICAL SUPPORT.** A 0.3 mm port gap and a 0.75 mm series gap must be
  held rigid in a cantilevered 1 mm wire, 13 mm long. Nothing holds them. A
  dielectric bead in either gap **changes its capacitance**, which is the whole
  mechanism.
- 🔴 **LOOP MATERIAL IS UNSTATED.** The walls are declared (aluminium 6061,
  `wall.conductivity.s_per_m`). The loop is not — and at β = 52 it carries the
  coupled current.

#### C. Failure modes never checked

- 🔴 **ARCING.** The series gap is a deliberate E-field concentrator at kW
  levels, and the **PORT gap at 0.3 mm is the tighter feature**. Neither has
  been checked against a breakdown limit. ✅ Answerable from solves already on
  disk — peak |E| in each gap.
- 🔴 **I²R heating** in a 1 mm conductor, and how it is removed.

#### D. 🔴 THE CAVITY'S OWN GAS ENVIRONMENT IS NOWHERE IN THE RECORD

Searched: no statement anywhere of whether the cavity volume is **air at
atmosphere, N₂-purged, sealed, or evacuated.** ⚠️ **This single unstated fact
DECIDES the arcing question** — Paschen breakdown over a sub-millimetre gap
differs by orders of magnitude between atmospheric air and vacuum, and vacuum
would raise multipactor instead. It is also the §7ab pattern again: a value
nobody chose, now load-bearing.

#### ✅ What is already answerable, and one answer

**Machining tolerance, DERIVED from the measured gap sweep** (Q_ext ∝ gap^−1.14
locally, 0.5 → 0.75 mm):

| gap tolerance | Q_ext | VSWR band |
|---|---:|---|
| ±0.02 mm | ±3.0 % | 6.7 – 7.1 |
| **±0.05 mm** | **±7.6 %** | **6.4 – 7.4** |
| ±0.10 mm | ±15.2 % | 5.9 – 7.9 |

✅ **The series gap is FORGIVING** — ±0.05 mm is routine machining and costs
nothing at VSWR 6.9. ⚠️ **The port gap is 0.3 mm and has never been swept**, so
its sensitivity is unknown and it is the tighter feature.

#### Sequencing

1. **Finish 2c** — bracket the Q_ext optimum (running).
2. **Arcing check** — peak |E| in both gaps from existing solves. No new solve.
   🔴 Blocked on D: state the cavity atmosphere first, or the limit is undefined.
3. **Port-gap sweep** — the untested tentative value, and the tighter feature.
4. **Step 3 (already queued)** — re-sweep AREA on the barrel; 176 mm² was a cap
   result and does not transfer.
5. Feed transition, support, material, cooling — **hardware design, not EM
   sweeps**, and the point at which this stops being a `resonance` question.

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

🔑 **AND IT IS THE ONLY LEVER ON THE TUNER'S THERMAL WALL.** Load current goes
as **√VSWR**, so VSWR 79 → 20 takes **39.7 A → 20.0 A** — from 4.4× short of the
best microwave PIN die to **2.2×**. A phase detector removes the β↔1/β ambiguity
but **removes no current** (`../control-loop/SOURCE.md` § DOES THE DETECTOR
RETIRE THE TUNER). **Item 7 is upstream of the whole magnitude-tuning problem.**

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

### 🔧 AFTER THE AZIMUTHAL GRID — two resume inefficiencies (2026-08-30)

Both seen recovering `h3-azim-01` from the Saturday reclamation. Neither is
wrong, both waste time on every resume:

1. **Resume is per-CASE, not per-solve.** Case 2's `pec` had completed (it was
   the newest entry in postpro) but its `lumped` had not, so the whole case
   re-ran and a ~10 min pec was recomputed. Key the resume on the solve, not
   the case.
2. **The mesh-retry ladder is not memoised.** Case 2 needed size-factor 1.42
   and 7 chords. The winning mesh is cached, but the rig re-walks the ladder
   from the default and FAILED attempts are not cached, so it repeats the
   failures before reaching the cached winner. Record the winning
   `(size_factor, chords)` per case in the result and try it FIRST on resume.

⚠️ Not done during the run: the rig shells out to `geometry.py` per case and
editing it mid-run is what cost 6 of 16 grid points. See [frozen is not removed].

### ⚠️ EIGEN CANNOT ANSWER THE IMPEDANCE QUESTION (2026-08-30)

**User: *"Can we even test impedance with PEC?"*** — the loop is NOT PEC (the
A-queue removed it): wall attr 90 = 3.5e7 aluminium, loop attr 92 = 5.8e7
copper, port attr 91 = 50 ohm LumpedPort. Conductor loss IS modelled.

🔴 **But the limit is the SOLVER, not the material.** An eigen solve with a
lumped port returns Q_ext — a coupling MAGNITUDE. There is no complex Z in that
output. R + jX against 50 ohm, and whether the loop's reactance cancels or adds,
has no representation in it.

- ✅ the 6 strip cases CAN answer: does cross-section change coupling strength,
  and does it shift the prefactor of the beta ∝ L^3.88 law
- 🔴 they CANNOT answer: does a 5x1 strip MATCH 50 ohm better than a 1 mm wire

Same point from the other side: KNOWN records that **|S11| cannot distinguish
beta from 1/beta**, resolved by `e0k2_anchor.branch_from_phase`. Magnitude is
not enough; PHASE carries the impedance information.

### 🔴 REFUTED-AND-REPLACED — a strip changes the EXPONENT, not a prefactor (2026-08-30)

Azimuthal, h = 2, grooved, slug `h3-azim-01` stamp `71364f1e`. Same h, same
arc, same enclosed area to the conductor centreline — only the cross-section
differs (1 mm round wire vs 5x1 mm strip, wide face parallel to the wall):

    L        wire beta   strip beta   ratio
    10.2      0.392       0.129       3.04
    12.24     0.699       0.229       3.05

Predicted the second from the first at a constant 3.04x: 191,000 vs MEASURED
Q_ext 190,750 — **0.1%**. So the cross-section factor is SEPARABLE from the
geometry: it moves the PREFACTOR and leaves the L^3.88 exponent untouched.

🔴🔴 **THE THIRD POINT REFUTED ALL OF THAT, ONE CASE LATER.**

    L        wire beta   strip beta   ratio
    10.2      0.392       0.129       3.04
    12.24     0.699       0.229       3.05
    14.2      1.410       0.370       3.81   <-- predicted 0.464, 20% off

**The ratio is NOT constant in L.** The two conductors have DIFFERENT
EXPONENTS, measured over the same 10.2 -> 14.2 span at h = 2:

    1 mm round wire ... beta ∝ L^3.87
    5x1 mm strip ...... beta ∝ L^3.19

Cross-section changes the SHAPE of the law, not a multiplier on it. The 0.1%
"confirmation" at L=12.24 was two points agreeing on a line, which any two
points do.

🔑 **THE SAME ERROR TWICE, ONE LEVEL APART.** The user objected that one WIDTH
cannot establish a width response. It then turned out two LENGTHS could not
establish the L response either — a constant extrapolated from the minimum
number of points that can produce one. [epoch comparisons are not measurements]
has a sibling: **a fit through N points does not survive point N+1 unless N was
chosen to test it, not to produce it.**

🔴 **SCOPE — ONE WIDTH, AND NOW NOT EVEN A CLEAN RATIO.** *User: "Independent at 5mm width. We would
have to try different widths to ascertain 'the strip divides beta by 3.04 at
every size'."* I called this a "3x knob on coupling", which claims a RESPONSE
CURVE from a single sampled point. Two conductors give ONE ratio.

    ✅ established: a 5x1 strip couples WEAKER than a 1 mm wire at every
       (h, L) measured — 3.0x to 3.8x — and the mode stays clean (P >= 0.9999)
    ✅ established: the two cross-sections obey DIFFERENT L-exponents,
       3.87 (wire) vs 3.19 (strip), over 10.2-14.2 mm at h = 2
    🔴 NOT established: any constant ratio; how either exponent varies with
       WIDTH; that the strip exponent is stable outside this span; that a
       thicker ROUND wire moves coupling the other way at all

➡️ To earn the knob, sweep WIDTH at fixed h and L — e.g. 2x1, 3x1, 5x1, 8x1
against the 1 mm wire, one geometry, one variable. Cheap: h=2 cases solve fast
and the arcs {10.2, 12.24, 14.2} are known to mesh.

### 🔴 CORRECTION — THE MINIMAX IS NOT THE TARGET (2026-08-30)

**User: *"The minimax loop is not an accepted solution, so it's not appropriate
to make claims like 'we need more coupling to reach Q_ext ~ 2,100'. We've found
Beta = 1 unloaded, we're looking for Beta = 1 loaded."***

🔑 I quoted the minimax as the objective. It is not one — and KNOWN marks that
very line **"Design implication, NOT a decision ... Do not adopt a leg depth
from this line."** I adopted a target from a line that says not to. The minimax
is what a SINGLE fixed coupler is reduced to (VSWR ~20 in both states); the
DUAL-LOOP plan exists precisely so that compromise is not needed.

**The objective is beta = 1 in EACH state, with a coupler for each:**

    beta = 1 COLD   ✅ bracketed — h=2, L ~ 13.4 mm (Q_ext ~ Q0cold ~ 43,700)
    beta = 1 LOADED ⏳ OPEN — needs Q_ext ~ Q0loaded, and Q0loaded is UNMEASURED

⚠️ **The scale of the loaded ask is not small.** If Q0loaded is order 100-200,
beta = 1 loaded wants Q_ext of the same order — **30-60x below the smallest
Q_ext this programme has measured (6,362)**. Running beta ∝ L^3.88 backwards
puts that near L ~ 37 mm at h=3, area ~111 mm², far outside the validated
10.2-14.2 band and into the range where **F2** asks whether purity degrades with
loop area. Whether an azimuthal loop can get there without hybridising TE011 is
GENUINELY OPEN. Do not assume the extrapolation holds — it already broke once,
at h=4.

🔑 **Measure Q0loaded FIRST.** Every number above is conditional on it.

➡️ **Carry the impedance question into the DRIVEN rig**, which is needed for
loaded work anyway (PRIOR ART: eigen with sapphire + plasma does not converge).

### ✅ RE-MEASURED WITH A CORRECT PORT — the strip sweep (2026-08-31)

Slug `h3-azimwidth-01` stamp `c1dffc3d`. ALL at **standoff 2.0 mm** (the WALL
GAP, held fixed) and a port face of **0.9 x the conductor's HALF-EXTENT** — the
same face-to-conductor ratio for every conductor, which is what the earlier data
did not have.

    conductor      10.2    12.24    14.2      L-exponent
    wire (ref)    1.897    3.779   6.872       3.89
    2x1           1.262    2.215   3.654       3.21
    3x1             -      2.260   3.798          -
    5x1           1.180    2.156   3.840       3.57
    8x1           1.119    2.205   3.911       3.78
    5x0.5         1.170    1.948   2.965       2.81
    5x0.25        1.662      -       -            -

🔑 **WIRE vs STRIP: 1.6-1.8x, not 7-8x.** At matched wall gap AND matched port
ratio the round wire couples 1.61x (arc 10.2) to 1.79x (arc 14.2) more than a
5x1 strip. Every larger figure this programme reported — 3.04, 4.13, 7.19, 7.89,
8.54 — was the port face, not the conductor.

🔑 **CROSS-SECTION ROTATES THE CURVE, IT DOES NOT SHIFT IT.** The L-exponent
rises monotonically with conductor size in BOTH dimensions:

    width  2 -> 5 -> 8 mm  :  3.21 -> 3.57 -> 3.78
    thick  0.5 -> 1.0 mm   :  2.81 -> 3.57

At any single arc the widths differ by only ~5%, which is near the mesh-to-mesh
reproducibility, and the ordering even flips between arcs — because the curves
CROSS near arc 12. ⚠️ A single-arc comparison cannot see this. Fit exponents.

🔴 **THE 5x0.25 SERIES IS UNUSABLE — 1 of 3 points.** arc 12.24 TIMED OUT at
7200 s; arc 14.2's pec continuation BROKE. The one point that landed (1.662)
also breaks the thickness trend, sitting ABOVE both thicker strips rather than
below. ⚠️ Its port face is ~0.225 mm across a ~0.12 mm gap element — two
elements — which is the regime `e0k2_anchor` records a face floating in. **Do
not quote 5x0.25.** If thin strips matter, refine the gap mesh first.

⚠️ Also lost: 3x1 arc 10.2, pec continuation BROKE (nearest converged mode
+147.5 MHz, the 2.598-2.607 GHz cluster). 15 of 18 cases returned results; all
three failures were REFUSALS, not mislabelled modes.

🔑 **THE SOLVER STRUGGLES NEAREST beta = 1** — the L=13.0/13.4 wire cases, and
both 5x0.25 failures. That is the most design-relevant point on the curve, and
it is an argument for the DRIVEN solver on any near-critical geometry.

### 🔴🔴 SUPERSEDED — THE PORT FACE DOMINATES Q_ext (2026-08-30)

Strip 5x1, standoff 2.0, arc 12.24 — IDENTICAL geometry, identical mesh
settings, identical solver settings. ONLY the port-face half-width changed:

    pw    face      Q_L      implied Q_ext   implied beta
    0.9   1.80 mm   29,465      ~90,000         0.49
    0.45  0.90 mm   13,826      ~20,200         2.17

🔴 **HALVING THE FACE CHANGES beta BY 4.5x.** A well-posed lumped port is
INSENSITIVE to this. Q_ext is therefore set by an arbitrary modelling choice,
not by the loop.

**WHAT THIS INVALIDATES — every azimuthal COUPLING number:**
  - beta ∝ A^4.07 and the "critical coupling at A ~ 26.7 mm^2" bracket
  - the L-exponents (wire 3.87-3.89, strip 3.19-3.37)
  - every wire-vs-strip ratio (3.0x, 4.1x, 7.2-8.5x matched-standoff)
  - the 18-case `h3-azimwidth-01` sweep, and the 9 strip cases of `71364f1e`
  - "VSWR 1.09 at h=3 L=12.24 strip", "beta = 1 bracketed"

⚠️ **AND THE TWO FAMILIES SIT AT DIFFERENT POINTS ON THIS CURVE.** `_rc_p` is
the wire's RADIUS but the strip's FULL thickness, so at the same factor the
wire's face is INSET (0.9x its half-extent) and every strip's OVERSHOOTS
(1.8x). Wire-vs-strip is thus not merely uncertain — it is a comparison across
a steep artefact.

✅ **WHAT SURVIVES — everything from the `pec` solves**, where the gap is
SHORTED and the face plays no part: Q0 (43,378-44,083 across the whole grid),
mode purity (P >= 0.9999 throughout), f0, the 0.75% Q0 cost of an azimuthal
loop vs 6-12% for the rectangular one, and the groove behaviour. The MODE work
is intact. The COUPLING work is not.

🔑 **THE FIX IS PHYSICAL, NOT NUMERICAL.** The face represents where a feed
actually attaches, so its size is a DESIGN INPUT. It must come from the real
connector cross-section, be declared in `baselines.json` like any other
canonical value, and be held CONSTANT across every conductor — then all
comparisons sit at one feed. `0.9 * _rc_p` is a factor times the conductor,
which is why it silently differed between families.

⚠️ Also open, and NOT the same question: the face is a flat rectangle in the
**z = 0 plane** (radial x tangential). The conductor's cross-section at the gap
is (radial x AXIAL). For a 5 mm-tall strip the face spans none of the axial
extent. Whether that is right depends on how Palace integrates the lumped
element and is NOT resolvable by argument — measure it.

### 🔴 SUPERSEDED — the original suspicion, kept because it was right for the wrong reason

Found 2026-08-30 while checking probe readings. In `geometry.py`:

    _rc_p = (_strip[1] if _strip else lrw)
    _pw   = 0.9 * _rc_p

🔴 **THE TWO BRANCHES DO NOT MEAN THE SAME THING.** `lrw` is a wire RADIUS (a
half-extent), so a wire gets a face inset to 90% of its conductor — the intent.
`_strip[1]` is a strip's FULL radial thickness, so a 5x1 strip gets a face of
+-0.9 mm against a conductor of +-0.5 mm: it OVERSHOOTS by 0.4 mm per side.

⚠️ Separately, the face is a flat rectangle in the **z = 0 plane** spanning
radial x tangential. That was validated on a ROUND WIRE. A 5 mm-tall strip
extends +-2.5 mm in z and the face does not.

**Consequence: every strip beta may carry a systematic port error** — the nine
cases of `h3-azim-01` stamp `71364f1e` (beta 0.129-1.664) and the 18 of
`h3-azimwidth-01`. They are SELF-CONSISTENT and the mode is clean
(P >= 0.9999), which is why nothing flagged it.

✅ **DECISIVE TEST, and it is cheap.** `AMIP_PORT_PW` is already a hashed
parameter. **A correct port gives Q_ext INSENSITIVE to reasonable changes in
face width.** Sweep it on ONE strip case — e.g. 0.4 / 0.6 / 0.9 — at fixed
geometry:
  - Q_ext flat  -> the face is fine, strip results stand
  - Q_ext moves -> the strip betas need re-deriving, and the wire/strip ratio
    is an instrument artefact rather than a cross-section effect

🔑 Do this BEFORE quoting any wire-vs-strip ratio, including the
matched-standoff series A now running — which was specifically built to make
that ratio meaningful.

### 🔴 LOADED, FIRST ATTEMPT — Q0loaded STILL UNMEASURED (2026-08-31)

Slug `h3-azimload-01` stamp `b593113a`, driven, azimuthal wire loop at standoff
2.0 / arc 12.24 (the reference coupler). ne = 0 then 7.9e18.

✅ **WHAT LANDED, and it does not depend on the coupling model:**

    cold    f0 = 2.450325 GHz   dip -16.29 dB   (selected by CONTINUATION)
    loaded  f0 = 2.455755 GHz   dip  -4.13 dB
    LOADED PULL = +5.43 MHz

⚠️ Compare the DISCARDED groove-free value of +31.6 MHz — this is 6x smaller.
Continuation also correctly rejected a DEEPER feature at 2.6048 GHz (-22.10 dB)
as not-the-mode, which is exactly the trap `h3_sapphire` fell into.

🔴 **THE COLD CROSS-CHECK FAILED — and it was there to catch this.**

    driven cold, dip -16.29 dB -> beta = 0.734 (under) or 1.362 (over)
    eigen  cold, SAME mesh     -> beta = 3.779
    eigen's beta would give a -4.71 dB dip; driven measured -16.29 dB

🔴🔴 **CORRECTED — THE TWO RUNS ARE DIFFERENT CAVITIES, and the solvers are
not in disagreement at all.** From the mesh sidecars:

    eigen  (h3_loopq azim grid) : torch_material = [9.39, 3.5e-05]  SAPPHIRE
    driven (h3_azimload cold)   : torch_material = [1.0,  3.5e-05]  VACUUM

That is the whole 11 MHz f0 offset (2.4394 vs 2.4503) and a different field at
the loop, hence a different beta. Each rig is right for its own purpose — the
driven rig meshes a VACUUM torch for its cold reference BY DESIGN — but the two
numbers were never comparable. ⚠️ I wrote "same geometry, same mesh, same port
face" here without checking the sidecars, and then built a port-face hypothesis
on top of it. [epoch comparisons are not measurements], again, and this time I
had the artefacts on disk that would have shown it in one command.

✅ The loop itself was built correctly in BOTH: loop_mount azim, standoff 2.0,
centreline 3.0, port_face 1.80 mm. (The driven mesh tag says `ld11` — that is
unused radial-loop defaults leaking into the NAME, not the geometry.)

🔴 **AND SO THE OBVIOUS SHORTCUT IS ALSO VOID.** Q0loaded = beta x Q_ext (with
Q_ext taken as cold and geometric) gives ~2,700 — but it inherits beta from the
method that just failed validation, and Q_ext from the port face that is not
physically anchored. Do NOT quote 2,700.

🔴 **THE PORT-FACE HYPOTHESIS WAS WRONG HERE** (it is still a real effect on
Q_ext — 4.5x across the overshoot boundary — but both runs used the SAME face,
so it cannot produce a difference BETWEEN them).

⚠️ **AND THE PRESCRIPTION IT CAME WITH WAS WRONG TOO.** "Pin the face to the
real connector cross-section and declare it in baselines.json" treats a
MODELLING artefact as a design parameter. A lumped port is a surface impedance
Z_s = R*W/L over the face; what matters is how much of the conductor's actual
current it intercepts. In a real build the coupling is set by the loop's FLUX
LINKAGE, not by the connector aperture. ➡️ The face should BE the conductor's
cross-section at the gap, and the right check is CONVERGENCE toward that — not
a connector dimension.

➡️ **The real next step:** run the eigen azimuthal case on a VACUUM-torch
cavity so eigen and driven can be compared like with like. Until then there is
no evidence the two solvers disagree.

⚠️ Why the width failed, for whoever retries: the loaded dip is only 4.13 dB
deep, so the 3 dB points sit ~1.1 dB above a nearly flat baseline, and the
high-side walk turned at 2.4652 GHz on competing structure. A shallow dip on a
sloping baseline cannot give a linewidth. Isolate the mode with a band centred
on it, or drive harder toward beta = 1 so the dip deepens.

✅ FIXED: `_report` KeyError'd on a fit with no `linewidth_mhz`, killing the
summary of a run whose result file held BOTH located dips. It now prints what
exists and dashes what does not.

### 🔴 THE FEED TOPOLOGY WAS NEVER CHOSEN (2026-08-31)

**User: *"Doesn't picking the adapter type seem premature at this point, when we
haven't established anything else about how the coupler enters the cavity, or
how it's connected to the cavity on the far side from the inlet?"*** — yes, and
asking for SMA/N-type was doubly wrong, because the same message called the
port face a modelling convenience. Both cannot be true.

**WHAT THE MODEL ACTUALLY BUILDS** (geometry.py, azimuthal mount):

    wall --leg--  quarter-arc --GAP--  quarter-arc  --leg-- wall
                                ^ port face, mid-arc at phi = 0

Both legs are galvanically joined to the wall; a 0.3 mm gap is cut at the
CENTRE of the arc and the port bridges it. Verified against the mesh: for the
2x1 strip at standoff 2.0 the port spans r 85.0545-85.9546 inside a conductor
at 85.0045-86.0045, 2 mm inside the wall at 88.0045.

🔴 **NOBODY CHOSE THIS.** It was inherited from the radial loop, where the gap
sits mid-crossbar for its own reasons. A coax-fed loop normally grounds the
outer conductor AT THE WALL PENETRATION, with the inner conductor forming the
loop — so the driven gap is at the ENTRY, not mid-arc.

🔴 **DOWNGRADED 2026-09-01 — I OVERSTATED THIS.** *User: "Why can't the coupler
simply enter through a hole? As opposed to specifying every detail about the
adapter."* Right: it is ONE geometric decision, not a shopping list.

✅ **THE MINIMAL REALISTIC FEED, and it needs no connector model:**
    coax OUTER grounds at a HOLE in the wall; INNER passes through and becomes
    one leg; the loop runs round; the FAR leg grounds to the wall. A lumped
    port across the hole still terminates in 50 ohm. Coax dimensions matter
    only if you later want the connector's own reactance.

🔑 **AND IT IS THE SAME CIRCUIT CLASS AS WHAT IS ALREADY BUILT** — a series-fed
loop returning through the wall. The only difference is WHERE around the loop
the source sits, and that is small:

    unwound loop = 17.94 mm = 0.147 lambda = lambda/6.8
    phase around the loop            = 53 deg
    mid-arc vs entry feed shifts it  = ~26 deg

**So the existing Q_ext numbers are NOT invalidated by this** — 26 deg is a
perturbation, not a different circuit. It was wrong to call this a blocker or
to rank it above the port face.

➡️ **Worth doing anyway, and cheap:** put the hole in, drive at the entry, and
compare Q_ext against the mid-arc model. That also puts the port REFERENCE
PLANE at the wall, which is where VSWR would actually be measured — a real gain
for the design deliverable, independent of how much the number moves.

### ✅ COLD ANCHORED / 🔴 EIGEN STALLS ON PLASMA — closed-ring azimuthal loop (2026-08-31)

**User: *"We're not trying to hit Beta = 1 loaded yet, so I don't think the
0.3mm gap should be there at this point."*** ✅ Right, and it dissolves the port
face, the feed topology and the coupling branch in one move. `port_bc="pec"`
SHORTS the gap, so the loop is electrically a CLOSED RING — a conductor the
mode must coexist with, nothing more. No new mesh needed: the driven run's own
meshes were reused.

✅ **COLD, closed ring, VACUUM torch, standoff 2.0 / arc 12.24 wire:**

    f = 2.381453  Q = 13,094
    f = 2.381793  Q = 13,107
    f = 2.450751  Q = 43,875   <- TE011
    f = 2.604939  Q = 20,994
    f = 2.607576  Q = 20,577

🔑 **AND IT VALIDATES DRIVEN AGAINST EIGEN AT LAST.** The driven sweep put its
cold dip at 2.450325 GHz on THIS SAME MESH — **0.43 MHz apart, 0.017%**. The
earlier apparent 3x disagreement was entirely the sapphire-vs-vacuum torch
mismatch. The two solvers agree on this cavity. The 2.6049/2.6076 pair is the
same competitor cluster driven saw at 2.6048.

🔴 **LOADED: EIGEN DOES NOT CONVERGE.** ne = 7.9e18, plasma attr 12 at
eps = -1.456, sigma = 2.1746 (the driven rig's own Drude values):

    PCG solver did NOT converge in 1000 iterations (avg. reduction 9.987e-01)
    Linear solver did not converge, norm(Ax-b)/norm(b) = 1.117e+00
    nconv = 0

⚠️ **THIS EXTENDS THE PRIOR ART, IT DOES NOT MERELY CONFIRM IT.** `h3_driven`
records sapphire + plasma stalling and says *"neither ingredient alone fails"*.
Here the torch is VACUUM (eps 1.0) and it stalls anyway, in the same
PCG-stagnation mode `h3_eigenprobe` found. **The negative permittivity alone is
sufficient.** Update the PRIOR ART line accordingly.

🔴 **AND A TRAP THAT ALMOST PASSED SILENTLY.** The first loaded attempt returned
eigenvalues IDENTICAL to cold to 6 figures — because `eigen_cfg` builds
materials from the MESH SIDECAR, which does NOT carry the plasma's Drude
permittivity (the RIG computes it from n_e). Every volume came out eps = 1.0,
so the "loaded" solve was a COLD solve. This is R101's exact failure, and the
guard that catches it lives in the RIG — bypassed by hand-rolling the solve.
✅ The re-run carries an explicit fail-closed check: refuse if ne > 0 and the
plasma attribute has eps = 1.0.

➡️ **THE PATH LEFT FOR Q0 LOADED.** Eigen stalls; driven cannot fit a linewidth
because the loaded dip is only 4.13 dB deep on a sloping baseline; and with the
ring SHORTED there is no port to drive at all. The remaining route is ENERGY
BALANCE from a driven solve: Q0 = omega * W_stored / P_dissipated, both of which
Palace can report per domain (`Domains.Postprocessing.Energy` is already wired
in h3_driven). That needs no linewidth and no port model.

### 🔑 Q_L BY ENERGY BALANCE — and TE011 IS EXTINGUISHED AT THE ANCHOR DENSITY (2026-09-01)

Computed from artefacts ALREADY on the volume — no new solve. Steady state on
resonance: the port delivers exactly what the materials dissipate, so

    Q_L = omega * W_stored / P_delivered      W = E_elec + E_mag (domain-E.csv)
                                              P = 0.5*Re{V I*}  (port-V/I.csv)

⚠️ This is Q_L, NOT Q0 — it includes the port. I mislabelled it first time.

✅ **COLD, and it closes the coupling question without any |S11| branch:**

    Q_L (driven, energy balance, port LIVE)   = 10,602   @ 2.450450
    Q0  (eigen, ring SHORTED, same mesh)      = 43,875   @ 2.450751
    ->  beta = Q0/Q_L - 1 = 3.14        Q_ext = Q0/beta = 13,977

🔑 beta from TWO INDEPENDENT SOLVES, not from a dip depth — so the branch
ambiguity that has dogged every driven number simply does not arise.
⚠️ The two use different port BCs (shorted vs 50 ohm) and their f0 differs by
300 kHz, so this beta is good to ~10%, not better.
🔴 Note the dip-depth method gave 0.734 or 1.362 for the same case. NEITHER is
3.14. **Dip depth is unreliable here; energy balance is not.**

🔴🔴 **LOADED AT ne = 7.9e18: TE011 IS GONE.** Every local maximum of stored
energy across 2.30-2.65 GHz:

    f=2.45760  W=2.620e-10 J  (0.149% of peak)  |S11| -4.13 dB   <- TE011
    f=2.60500  W=1.075e-07 J  ( 61%)            |S11| -21.67 dB
    f=2.60600  W=1.761e-07 J  (100%)            |S11| -3.01 dB

TE011's stored energy is **3,250x below its cold value** and its Q_L is **~3.6**.
|S11| sits near -4 dB across the WHOLE band: ~60% of the drive is absorbed at
every frequency. That is broadband absorption, not a resonance. The rig's
"-4.13 dB dip" is the top of a featureless hump.

🔑 **WHY, AND IT IS NOT A SOLVER ARTEFACT:**

🔴 **CORRECTED 2026-09-01 — I QUOTED THE WRONG THRESHOLD.** First written as
"106x over-dense" using the COLLISIONLESS critical density. That is a formula
outside its domain (cf. the Q_ext = 165 error). With nu = 6.5*omega this plasma
is COLLISION-DOMINATED and nu^2 beats omega^2 by 42x, so eps = 1 -
wp^2/(omega^2 + nu^2) stays near 1 far above n_c:

    collisionless n_c (wp = omega)   = 7.446e16 m^-3   <- NOT the threshold here
    COLLISIONAL threshold (eps = 0)  = 3.217e18 m^-3   <- the real one
    the programme's anchor           = 7.900e18 m^-3   = 2.5x over, NOT 106x

✅ The anchor IS over-dense — eps = -1.456 is negative and the mode really is
extinguished. Only the FACTOR was wrong, and it matters because it moves the
interesting density range by two orders.

    eps across density:  1e16 +0.997   3e17 +0.907   3e18 +0.067
                         7.4e16 +0.977  1e18 +0.689   7.9e18 -1.456

At 2.5x the collisional threshold the plasma is a lossy MIRROR: the field
reaches ~1.9 mm into 6.5 mm of plasma, the bore is excluded, and TE011 — whose
E_phi lives in the bore — cannot exist.

➡️ **CONSEQUENCE: "Q0 loaded for TE011" is ill-posed at this density.** There is
no mode to have a Q. The design question is not "how do I couple to a loaded
TE011" but "at what density does TE011 still exist", which is exactly what
`h3_loaded` was built to map: *"what plasma does TE011 sustain? A 2-D map, not
a point."*

➡️ **NEXT: sweep ne through 1e18-1e19**, where eps actually crosses zero.
⚠️ NOT 1e16-1e17 — that was the mis-derived range, and the sweep launched on
2026-09-01 (`h3-azimne-01`, stamp 4b8c220c) is mis-centred because of it: four
of its nine points sit below 1.5e17 where eps > 0.95 and nothing happens, and
those are the EXPENSIVE ones because driven cost scales with Q. It still
brackets the transition with 1e18 / 3e18 / 7.9e18.
Energy balance works on driven artefacts, needs no linewidth, no port branch
and no eigen convergence, so it runs where both other methods failed.


## 📋 PLAN FOR THE NEXT SESSION (written 2026-09-01, no instance up)

The 2026-09-01 spot died ~04:00 local, mid-sweep. `h3-azimne-01` never reached
its end-of-run fetch, so ITS RESULTS ARE ON THE EBS VOLUME AND NOT LOCAL.

### 1. RECOVER FIRST — before launching anything (~10 min)

    ops/env.sh -> new address
    NOSYNC=1 ops/go ops/mount.sh
    ops/go ops/fetch.sh
    cd /opt/amip/repo/experiments/resonance && python3 /tmp/parse.py ...   # or:
    grep -aE "^  --- ne|selected .* GHz" h3-azimne-01.log

Cold + ne = 1e16 / 3e16 / 7.4e16 had completed before it died; more may have.
**Extract Q_L for each completed density** with
`ops/oneoff/qL_energy_balance.py <postpro_dir> <f0_ghz>`. The number to watch
is stored energy as a FRACTION OF THE BAND PEAK: at 7.9e18 TE011 was 0.149%
(gone); a surviving mode should be tens of percent.

### 2. THEN the re-centred sweep — this is the real measurement

eps crosses zero at 3.22e18, so the transition is 1e18-1e19, NOT 1e16-1e17:

    ne=1.00e+18  eps=+0.6891
    ne=1.80e+18  eps=+0.4404
    ne=2.50e+18  eps=+0.2228
    ne=3.20e+18  eps=+0.0051
    ne=4.00e+18  eps=-0.2436
    ne=5.50e+18  eps=-0.7099
    ne=7.90e+18  eps=-1.4561
    ne=1.20e+19  eps=-2.7307

Eight points, all in the interesting band, and all CHEAPER than the ones the
mis-centred sweep spent its time on (driven cost scales with Q; these have low
Q). Reuse `baseline-h3-azimne-01.json` — change only `ne_grid`, and amend
provenance so the stamp moves.
⚠️ Cold (ne=0) MUST stay first and is mandatory: it is the continuation seed
and the rig hard-exits without it. It is also the expensive point, so a
reclamation during it loses the run.

### 3. WHAT THE ANSWER LOOKS LIKE

The density where TE011's stored-energy fraction collapses IS the design
constraint — it says what plasma this cavity can actually run. That is
`h3_loaded`'s original question ("what plasma does TE011 sustain? A 2-D map,
not a point"), and the 7.9e18 anchor silently assumed it away.

### 🔧 WORTH DOING, NOT BLOCKING — feed through a hole

The model drives a mid-arc gap with both legs grounded (inherited from the
radial loop). The buildable version is a HOLE in the wall: coax outer grounds
there, inner becomes one leg, far leg grounds. Same circuit class — a series-fed
loop returning through the wall — with the source moved ~26 deg around a
lambda/6.8 loop. ⚠️ I first called this a blocker upstream of all coupling work;
that was wrong. It is a modest perturbation, worth measuring by building both
and comparing Q_ext, and it usefully puts the port reference plane at the wall
where VSWR is actually measured.

### ✅ INSTRUMENT STATUS, so nobody re-derives it

    eigen  + plasma        🔴 STALLS (PCG stagnation, nconv=0) even at eps_torch=1
    driven + 3 dB width    🔴 loaded dip 4.13 dB on a sloping baseline: unfittable
    driven + dip depth     🔴 gave beta 0.734/1.362 where the truth was 3.14
    driven + ENERGY BALANCE ✅ WORKS — Q_L = omega*W/P from artefacts it already writes
    eigen  port_bc=pec     ✅ WORKS for Q0 (loop shorted = closed ring), COLD only

### ✅✅ THE DENSITY SWEEP — TE011 HAS AN OPERATING POINT, AT ~3e16 NOT 7.9e18 (2026-09-01)

`h3-azimne-01` stamp `4b8c220c` completed ALL 9 densities before the 04:00 spot
death (it exited 1 on the V1/report step, but every postpro dir is on the
volume). Azimuthal wire loop, standoff 2.0 / arc 12.24, vacuum torch.
Q_L by ENERGY BALANCE — `ops/oneoff/qL_energy_balance.py`.

     n_e (m^-3)   eps      f0 (GHz)   W/W_peak     Q_L     |S11|
      0.00e+00  +1.000   2.450450   100.00%    10602   -4.29
      1.00e+16  +0.997   2.450400   100.00%     9678   -8.71
      3.00e+16  +0.991   2.450400   100.00%     6182   -8.47
      7.40e+16  +0.977   2.450400   100.00%     2964   -7.47
      1.50e+17  +0.953   2.450600    49.33%     1107   -4.65
      3.00e+17  +0.907   2.450600    18.62%      441   -4.88
      1.00e+18  +0.689   2.450800     2.41%       57   -4.41
      3.00e+18  +0.067   2.452200     0.39%        9   -4.17
      7.90e+18  -1.456   2.457600     0.15%        4   -4.13

🔴 **THE MECHANISM IS ABSORPTION, NOT CUTOFF — my "over-dense mirror" was
wrong.** Q_L is already down 3.6x at 7.4e16 and down to 57 at 1e18, where
eps = +0.689 and the plasma is comfortably UNDER-dense. sigma rises linearly
with n_e (0.0028 -> 2.175 S/m) and that is what kills the mode. Cutoff
(eps < 0) only arrives at 7.9e18, long after TE011 has gone.

🔑 **THE DESIGN NUMBER** — using the cold Q_ext = 13,977 as load-independent
(Q0 = 43,875 from eigen with the ring SHORTED, Q_L = 10,602 from driven energy
balance, same mesh):

     n_e       Q0_loaded  beta    P_in->cav  eta_plasma  OVERALL to plasma
     1.0e16      31465  2.2512      85.2%      28.3%       24.1%
     3.0e16      11085  0.7931      98.7%      74.8%       73.8%  <- OPTIMUM
     7.4e16       3762  0.2691      66.8%      91.4%       61.1%
     1.5e17       1202  0.0860      29.2%      97.3%       28.4%
     3.0e17        455  0.0326      12.2%      99.0%       12.1%
     7.9e18          4  0.0003       0.1%     100.0%        0.1%  <- THE ANCHOR

✅ **At n_e ~ 3e16 this loop puts 73.8% of INCIDENT power into the plasma at
VSWR 1.3.** At the programme's assumed anchor it puts in 0.1% — a factor of 700.

🔑 It is a genuine OPTIMUM, not a monotone: below it the plasma absorbs too
little of what enters (eta 28% at 1e16); above it the cavity reflects nearly
everything (12% enters at 3e17) because Q0 has collapsed far below Q_ext. The
peak sits where beta passes through 1.

⚠️ **THREE CAVEATS, none small:**
  1. Q_ext assumed LOAD-INDEPENDENT (geometric). The whole beta column rests on it.
  2. The plasma is a STATIC UNIFORM Drude annulus at r = 2-8.5 mm. This says
     what the CAVITY wants, not what a real discharge will do — that is
     `h3_loaded`'s map.
  3. The optimum is a property of THIS loop's Q_ext = 13,977. A stronger
     coupler moves it to higher density: matching at 3e17 needs Q_ext ~ 455,
     about 30x stronger than anything the azimuthal family has reached (the
     corrected sweep spanned Q_ext ~ 11,000-39,000).

➡️ **THE FORK.** Either operate near 3e16 with the coupler we have, or build a
~30x stronger coupler to reach 3e17. beta ∝ L^3.88 says that is L ~ 30 mm at
h = 2 — a 2.4x extrapolation beyond the validated 10.2-14.2 mm band, and larger
loops perturb the mode more. **Which fork depends on what density the plasma
must run at, which is a PLASMA question, not a cavity one.**


### 🔧 COAX FEED THROUGH A HOLE — BUILT AND VERIFIED IN GEOMETRY, NOT YET SOLVED (2026-09-02)

*User: "Why can't the coupler simply enter through a hole?"* — implemented.
`--loop-hole r_mm,stub_mm`. Default None reproduces every earlier run byte for
byte (control checked: loop area 121.8 mm^2, unchanged).

✅ **VERIFIED AGAINST THE MESH, not the sidecar:**

    physical groups: (2,90) wall  (2,91) PORT  (2,92) loop
    attr 91 : 210 nodes  r 96.0045..96.0321  z -2.2993..+2.2975
    port_face_mm (outer,inner dia) = [4.6, 2.0]   tets 75,724

The annulus sits at the stub mouth (r = a + 8 = 96.004 mm), outer 4.6 mm /
inner 2.0 mm dia — the coax cross-section. The feed leg runs through to
r = 96.01 (attr 92), and the stub's outer surface is at r = 96.03 (attr 90).

🔑 **TWO NUMBERS THE PHYSICS CHOSE, NOT A CATALOGUE:**
  - **hole radius 2.3 mm**, because Z0 = 59.96*ln(2.3/1.0) = **49.9 ohm** against
    a 1 mm inner conductor in air. That is the whole "what connector" question.
  - **the leg MUST pass through.** An empty 2.3 mm hole has a TE11 cutoff of
    29.3 GHz — ~5 e-foldings of decay over an 8 mm stub, i.e. a dead end. With
    the inner conductor it is a COAX, and TEM has no cutoff.

✅ **THE HOLE IS ELECTRICALLY BENIGN.** Eigen with the face shorted:
TE011 Q0 = 43,900 at 2.439396 vs ~43,800 without a hole — 0.2%. And MFEM loaded
it, so the per-sector fuse is manifold (the chimney/feed hazard, 7bn).

🔴 **A LUMPED PORT CANNOT DESCRIBE IT — from Palace's source, not a guess.**
`configfile.cpp ParseStringAsDirection`: a string Direction "r" maps to
CYLINDRICAL, but about the GLOBAL z axis. This coax enters through the BARREL,
so its inner->outer field lies in the theta-z plane. Also
`ParseElementData`: "Cannot specify CoordinateSystem with string Direction" —
CoordinateSystem is only legal beside an ARRAY Direction.
✅ Palace supports **WavePort** (mode_idx, d_offset, excitation, attributes),
which solves the port's own modal field and needs no direction.
⚠️ DRIVEN ONLY — wave ports are frequency-dependent. Q0 keeps coming from eigen
with the face shorted (port_bc="pec"), which needs no port model at all.
`solveconf.driven()` now emits a WavePort when the sidecar carries
`loop_hole_mm`, and a LumpedPort otherwise.

🔴 **NOT YET DONE: the end-to-end driven solve.** The spot died mid-test and it
lived in /tmp, so nothing of it survives. **Next session: rebuild the coax mesh
and run one driven sweep** — the open question is simply whether Palace accepts
a WavePort on this annulus, and what Q_L it gives with the reference plane AT
THE WALL, against the mid-arc-fed Q_ext = 13,977.

### 🔴 A BUG CLASS THAT BIT THREE TIMES THIS SESSION — metadata asserting what the artefact lacks

  1. `surface_attributes` was the literal `["wall","port","loop"]` regardless of
     what was built, so the first coax mesh — which really had only groups 90
     and 92 — still advertised a port. `volume_attrs()` TRUSTS that list to
     tell surfaces from volumes, so a config could reference attribute 91 into
     thin air. ✅ Now derived from whether a port face exists.
  2. `loop_azim`'s first element silently changed meaning (centreline ->
     standoff) while configs kept the old value.
  3. `eigen_cfg` gave the plasma eps = 1.0 because the Drude values live in the
     RIG, not the mesh — so a "loaded" solve was a COLD solve, identical to 6
     figures.

🔑 **All three were caught only because something downstream happened to look
wrong.** Verify metadata against the ARTEFACT (`ops/oneoff/mesh_attr_extents.py`
reads the mesh's real physical groups), never against what the writer intended.


### 🔧 COAX WAVE PORT — FIVE FAULTS FIXED, THE SOLVE STILL UNTESTED (2026-09-02)

The geometry is right and every guard passes; what has never run is Palace
accepting the wave port. Two spots died mid-test, both times with the run in
/tmp. **One driven sweep is all that is outstanding.**

✅ **VERIFIED:** `COAX MOUTH: exterior face 288, 13.48 mm^2 (annulus wants
13.48)` — the mouth is found by area to 4 significant figures.

**The five faults, in the order they surfaced** (each hid the next):

  1. **Silent rsync.** The sync carrying the WavePort code ran while the spot
     was being reclaimed; output went to /dev/null so it "succeeded". The next
     box came up with the OLD code and the mesh cache served OLD meshes. The
     symptom — a sidecar field reading None for an unconditional parameter —
     looked exactly like a code bug in code that was already correct.
     ➡️ CONVENTIONS: never `rsync.sh >/dev/null`; assert on the far side.
  2. **`driven()` returns a tuple**, not a dict — my test harness assumed dict.
  3. **Inserted the port face.** A LUMPED port is an INTERIOR face you insert;
     a WAVE port is an EXTERIOR boundary you IDENTIFY. Inserting a coincident
     annulus was wrong — though this was NOT the cause of the Palace error, and
     I rebuilt it on that wrong theory because I had truncated the message.
     ➡️ CONVENTIONS: read the whole error before grepping it.
  4. **The mouth was in BOTH `wall` and `port`.** Every exterior face lands in
     `wall` unless excluded, so tagging it `port` too put two boundary elements
     on one face: *"A non-periodic face (288) cannot have multiple boundary
     elements! Attributes: 91 90"* — the message named the face AND both
     attributes, i.e. the entire diagnosis, in the clause I had cut off.
  5. **The area partition check.** wall+loop no longer covered the exterior,
     because a coax port is a THIRD exterior class. ✅ This guard fired
     immediately and exactly — the discrepancy was 13.477 mm^2, the mouth. It
     now counts an exterior port.

🔑 **THE ASYMMETRY WORTH KEEPING:** the three GEOMETRY guards (loop area,
standoff/centreline, area partition) each caught their fault precisely and at
once. The METADATA that asserted what the artefact contained caught nothing and
caused three separate wrong turns. Guard on measurements of the artefact, not
on declarations about it.

➡️ **NEXT SESSION, first thing:** rebuild the coax mesh and run one driven
sweep. `/tmp/wpt2.sh` is the recipe (kept as ops/oneoff/). The open question is
only whether Palace accepts a WavePort on this annulus, and what Q_L it gives
with the reference plane AT THE WALL, against the mid-arc-fed Q_ext = 13,977.
