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
