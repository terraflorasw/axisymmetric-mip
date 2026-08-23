# METHODOLOGY — using gmsh and Palace without fooling yourself

**Working artifact, rev 4 (2026-08-20). REGENERATED, not appended** — like
`EXPERIMENTS.md` and `AUDIT.md`.

⚠️ **UPDATED 2026-08-23.** `FINDINGS.md` was removed from the working tree (it
had grown to 5,300 lines across three invalidated eras). **`KNOWN.md` is now the
authority on what is established**; where this file disagrees with KNOWN.md,
KNOWN.md wins. FINDINGS is retrievable for citations:
`git -C axisymmetric-mip show ba740d6:experiments/resonance/FINDINGS.md`
⚠️ `EXPERIMENTS.md` and `AUDIT.md` are also absent from this directory.

**What this is.** Tool-specific lessons, each paid for with at least one wrong
answer. It is not a tutorial and not general epistemics — the reasoning hazards
live in `EXPERIMENTS.md` §5. This is what these two programs do that is
surprising, silent, or both.

> 🔑 **THE ONE RULE.** *The solver is deterministic; the mesher is not stable
> under geometry change.* Every number below follows from that. A quantity
> computed on **one mesh** is trustworthy to 0.02 MHz. A quantity computed
> **across two meshes** carries 1.3–3.3 MHz of fog that no amount of care
> removes.

---

## 0. Environment

| | |
|---|---|
| Python + gmsh | `~/.local/share/mamba/envs/emsim/bin/python3` (3.12.13, gmsh 4.15.2) |
| system python | has **no** gmsh; `pip install --user` is blocked by PEP 668 |
| Palace | `~/.local/opt/palace/bin/palace`, run `-np 4` |

⚠️ **Palace dies in 0 s without the emsim env on PATH.** It is a wrapper that
shells out to `mpiexec`; the failure is `Could not locate MPI launcher`, rc=1,
instantly. Pass `PATH=~/.local/share/mamba/envs/emsim/bin:$PATH` (this is what
`solver.ENV` is for). 🔴 **Treat any solve returning in under 30 s as a failure**
and print the log's last line — a driver reporting "no peaks" makes a solver that
never ran look exactly like a cavity with no resonance.

⚠️ Container PID 1 does not reap, so `ps -C` and `pgrep` match `<defunct>`
entries and make finished runs look alive. Filter on state.

---

## 1. Determinism, and the noise floor it implies

| measurement | value | |
|---|---:|---|
| same mesh, two independent solves | **0.0000 MHz** | R105 — exact |
| same mesh, across a solver change | 0.02 MHz | `reproducibility.same_mesh` |
| **separately built meshes, same geometry, same size factor** | **1.5 MHz** | `reproducibility.mesh_to_mesh_scatter` |
| **geometry perturbed 7.5 µm at fixed size factor** | **σ = 1.33 MHz** | R105 ladder N |
| residual about a convergence trend | 3.29 MHz | R105 ladder C — an **upper bound** (2 dof) |

🔑 **The solver contributes nothing. All of it is mesh generation.** Perturbing a
length by 7.5 µm — a true frequency change of 0.18 MHz — moved the answer by
3.40 MHz peak-to-peak, **19× further than the physics did**.

⚠️ **It is not random, so repeats cannot average it away.** Meshing is
deterministic: the same inputs give a byte-identical mesh. Two *different*
geometries give two different meshes and two different errors, and re-running
reproduces both exactly. R99's 2-point slope re-measured to −10.45 on fresh
meshes and was still wrong. **Reproducibility is not accuracy.**

> 🔴 **Quote frequency differences against 3.3 MHz when being careful.** Anything
> under ~6.6 MHz (2σ) is not resolved by this harness.

---

## 2. 🔑 THE SAME-MESH RULE — the most useful thing in this document

Because all error is mesh generation, **a difference taken on one mesh is immune
to the dominant error source.** Design experiments to exploit this.

| comparison | same-mesh? | trustworthy to |
|---|---|---|
| solver order 1 vs 2 | ✅ | 0.02 MHz |
| **material change** (ε, tanδ) | ✅ *if sizing does not change* | 0.02 MHz |
| excitation, port, boundary condition | ✅ | 0.02 MHz |
| **any geometry change** | 🔴 impossible | 1.3–3.3 MHz |

✅ **This is why R99 is the strongest result in the record.** `s99qz.msh` and
`s99sa.msh` came out **byte-identical** (`md5sum` → one hash), because the torch
mesh sizing is clamped by wall thickness in both materials. Quartz→sapphire was
therefore a pure material change with **zero** mesh confound, and TM₀₂₀'s
−190.9 MHz stands at 58σ even against the pessimistic floor.

🔴 **And it is why R103 failed.** dTE₀₁₁/dL *requires* changing L, which forces a
new mesh, so every ladder point carried independent error. The result — ±1.21
MHz/mm — is dominated by meshing, not physics. **A length or radius derivative
cannot be measured better than this by ladders alone.**

**Practical:** `md5sum` the meshes in any comparison set. Identical hashes are a
feature for a material sweep and a **red flag** for a geometry sweep — R101 was
caught exactly that way.

---

## 2b. 🔑 ORTHOGONAL QUESTIONS ON ONE MESH

The same-mesh rule is usually read as *"prefer same-mesh when you can."* Stronger:
**design the experiment so the mesh never has to change.** Put every feature into
one mesh as a separately tagged volume, then switch features by MATERIAL rather
than by geometry.

🔑 **A dielectric region with ε = 1.0 and tanδ = 0 IS AIR, exactly.** So "part
present" vs "part absent" is a material state, not a geometry, for anything that
is a *dielectric volume*. No remeshing, no confound, and the solver's determinism
makes the difference exact.

**What is switchable on a fixed mesh:**

| | how |
|---|---|
| torch tubes (attr 2), mode filter (8), upstream gas (11), plasma (12), groove (13 when tagged) | set ε → 1.0, tanδ → 0 |
| wall material — Al / Ag / Cu | boundary `Conductivity`, attr 90 |
| solver order, port direction, excitation | config only |
| **cavity length and radius; the loop; viewport and trap PRESENCE** | 🔴 **not switchable.** Geometry, and voids — a hole cannot be filled by a dielectric. Filling a viewport with glass asks a *different* question (a window), which is fine but is not "absent" |

⚠️ **The two error-cancellations compound.** A ratio of two same-mesh answers has
the mesh error cancel twice — once as common mode, once because a dimensionless
quantity cannot depend on the mesh's absolute scale. The project's
"design is dimensionless" rule therefore doubles as an artifact filter.

🔴 **THIS MATTERS MOST FOR Q, NOT FREQUENCY.** Frequency's cross-mesh floor is
1.3–3.3 MHz and most claims clear it. **Q's is 6.9%** across sector counts on the
same geometry, and **40%** when the skin depth is under-resolved — and the filter's
quoted Q cost is **5.6%**, the groove's gain over it **6.0%**. *Both sit under the
noise they were measured against.* Any Q comparison worth quoting should be
same-mesh or it is not a comparison.

⚠️ **One mesh changes what the cases-differ gate must check.** `md5sum` polices a
geometry sweep; it cannot police a material sweep on one mesh, because the mesh is
*supposed* to be identical. There the CONFIG is the independent variable, so
assert the written config carries distinct values before solving (R101, R107).

**Consequence for tagging:** tag regions you may ever want to switch, even when
the build will never use them separately. R97 (per-tube torch materials) was
closed as moot once the torch went all-sapphire — but as an *instrument* it would
let each tube be switched to ε = 1 in turn, measuring its RF share exactly on one
mesh, where R96's 73.2 / 26.3 / 0.5% split is field-weighted estimation.

---

## 2c. GEOMETRY SWEEPS — validating and invalidating questions

§2b removes the mesh error wherever a question can be asked on one mesh. **This
section is for the questions that cannot be** — cavity length, radius, loop, and
anything else that is genuinely a shape. Those are the fine-tuning sweeps, and
they are the ones with an irreducible floor. The protocol below makes the floor
*measured per sweep* rather than assumed.

### Declare both sets, before the run

| | |
|---|---|
| **VALIDATING** — what MUST move | the swept quantity, with its **sign and rough magnitude from closed form**, plus monotonicity. If you cannot say which way it goes before solving, the run is exploratory and its result is a hypothesis, not a measurement |
| **INVALIDATING** — what must NOT move | a quantity with **analytically zero** sensitivity to the swept parameter, measured on the same meshes, in the same solves |

🔑 **THE INVARIANT'S OBSERVED DRIFT IS THE ERROR BAR.** Not a fitted residual —
a residual conflates real nonlinearity with mesh noise and cannot separate them.
An invariant's drift is noise *by construction*, because its true value did not
change. It is measured in situ, on the same meshes as the signal, in the same run,
for free.

> 🔴 **R103 is the worked example of getting this wrong.** Its band was 2.36–2.44,
> which excluded TM₀₂₀ at 2.182 — so there was no invariant, σ had to come from
> the fit residual, and a declared 0.5 MHz linearity gate then failed for reasons
> that had nothing to do with linearity. **Had the band reached TM₀₂₀, the error
> bar would have come free and correct.**

### Invariants, by sweep axis

| swept | invalidating question | basis |
|---|---|---|
| **length L** | f(TM₀₂₀) must not move at all | p = 0, **dTM₀₂₀/dL = 0 identically** — measured 0.40 MHz across a ΔL that moved TE₀₁₁ by 5.85 |
| **radius a** | 🔴 **none from dispersion** — every mode depends on a | use replicates, below |
| any | m = 1 azimuthal amplitude of TE₀₁₁ stays at the floor | TE₀₁₁ is m = 0; a symmetric cavity cannot produce it |
| any | η_total = η_plasma + η_wall + η_dielectric to a few % | conservation; already in `rig_power.py` |
| any | a **pure-bookkeeping** change — tag a region, renumber an index — must not move f | if it does, the point is unmeasurable (§5) |
| any | 🔑 **mode CHARACTER, not frequency separation** | R107: two modes 18.6 MHz apart were fully hybridised while a declared 7 MHz separation guard sat quiet. Hybridisation shows as **bore-E moving toward the mean of the two parents** (0.034 / 0.247 → 0.103 / 0.179, mean 0.141 both ways). How close is "too close" depends on coupling strength, not on a fixed number of MHz — **guard on the signature** |

### When no invariant exists: replicate with a sub-noise jitter

For a radius sweep there is no dispersion invariant. Manufacture one: at one or
two points, build a **second mesh with a geometric jitter far below the noise** —
R105 used ±7.5 µm of length, a true change of 0.18 MHz against a 1.3 MHz floor.
The spread of those replicates **is** σ for that sweep. Cost: two extra solves,
no extra meshing logic. This is R105's ladder N promoted from a one-off to a
standard tool.

### Planning the span — the expected error, before running

σ_slope = σ / √Sxx, and for n points evenly spread over a span W, Sxx ≈ nW²/12:

> **W ≈ σ · √(12 / n) / σ_slope,target**

| target on dTE₀₁₁/dL | n | span needed |
|---|---:|---:|
| ±1.2 MHz/mm | 5 | **2.0 mm** ← what R103 actually did |
| ±0.5 MHz/mm | 5 | **4.6 mm** |
| ±0.25 MHz/mm | 5 | 9.3 mm |

⚠️ **But span is limited by physics, not budget.** Over ~10 mm the neighbouring
mode 25–30 MHz above TE₀₁₁ is crossed, and near that crossing nothing is
measurable at all (§5). **±0.5 MHz/mm is about the practical limit for a length
derivative in this cavity**, and that ceiling should be checked against what the
tolerance actually needs before any such sweep is run.

### Reporting rule

1. Quote σ_insitu from the invariant, not from the fit residual.
2. Report the slope **with** σ_slope; never bare (R99's −10.4 was really −10.4 ± 4.9).
3. Refuse the result if the signal does not exceed **2 σ_insitu**.
4. State the invariant's measured drift in the output, whether it passed or not —
   a null control that is not reported is not a control.

---

## 2d. NAMES ARE TECH DEBT

Every name in this project that encoded a **material, a value, or an
idealisation** has since become wrong. Every name that encoded a **role** is
still correct. That is not luck — materials get swapped, values get superseded,
idealisations get replaced, and the name stays.

| name | says | actually holds | |
|---|---|---|---|
| `cav.length_sapphire` | a sapphire cavity | sapphire **outer tube only**; all-sapphire is 87.97 | 🔴 |
| `TAG_QUARTZ` | quartz | the torch, now **sapphire** | 🔴 |
| `TAG_PEC` | perfect conductor | **finite conductivity**, always did | 🔴 |
| `brake` / `brake_eps` | a dielectric brake | the **mode filter** | 🔴 |
| `TAG_BORE`, `TAG_AIR0`, `TAG_PLASMA`, `TAG_PORT`, `TAG_GROOVE`, `TAG_UPSTREAM` | a role | that role | ✅ |

> 🔑 **NAME BY ROLE, NEVER BY MATERIAL, VALUE, OR IDEALISATION.** `TAG_TORCH`, not
> `TAG_QUARTZ`. `cav.length_with_sapphire_outer`, or better a role name plus a
> `material` field. The role outlives every value the slot will ever hold.

⚠️ **And the debt compounds silently**, because a wrong name reads as
documentation. `wall.conductivity` said aluminium while the template said silver
for a full day of solves, and `torch_material` sat in the sidecar unread for
weeks — in both cases the name told everyone the right thing was happening.

**Paying it down — and NOT by annotating.** My first instinct was to leave the
names and fix the comments, on the grounds that renaming a mesh attribute
invalidates existing meshes. 🔴 **That was wrong, and the user overruled it:**

> *"The code is documentation, and wrong code is wrong documentation. There are no
> names we cannot change. I would rather re-run the relevant solves than leave
> them, even if they produce the same result."*

The cost of a wrong name is not a stale comment — it is **every future session
re-deriving the same misunderstanding**, which has already happened repeatedly
here (`cav.length_sapphire` and `TAG_QUARTZ` both cost a mid-session correction).
A rebuild costs an hour once; a misleading name costs an hour every time someone
reads it.

✅ **So: rename, and rebuild.** R111 renamed `TAG_PEC`→`TAG_WALL`,
`TAG_QUARTZ`→`TAG_TORCH`, `TAG_BRAKE`→`TAG_FILTER`, the sidecar keys with them,
and the ambiguous baselines (`cav.length_sapphire` → `cav.length_torch_sapphire_outer`,
which now says *which parts*). **Attribute NUMBERS are unchanged, so no physics
moves** — and `solveconf.load_meta` REFUSES a pre-rename sidecar with an
instruction to rebuild, rather than half-reading it. Failing loudly costs one
rebuild; falling back silently is how a wrong name becomes a wrong result.

---

## 3. gmsh

**Size factor.** `Mesh.MeshSizeFactor`; element count scales roughly as sf⁻³.
Design point is **0.96** (~165k tets).

🔴 **Not every size factor produces a valid curved mesh.** 2 of 6 candidates
failed at the design geometry with `Failed to reach critical value in pass 1 for
measure(s): ScaledJac` (`mesh.constructibility`: 1.20/1.06/0.96/0.90 work; 1.00
and 0.85 do not). **This is why `meshsweep.FACTORS` is a candidate list tried in
order.** Any sweep that sets the size factor itself must tolerate failures rather
than abort — and must not silently drop them.

⚠️ Negative Jacobians *during* high-order optimisation are normal and usually
resolve; `worst distortion = −0.13 … N elements with jac. < 0` in the log is not
by itself a failure. The fatal line is the `Failed to reach critical value` one.

⚠️ **Mesh order (2, curved) is not solver order.** Both are called "order".

🔴 **Every comparison set must share one size factor** (`meshsweep.sweep`
enforces it) — and only *within* one call. Passing a single case enforces
commonality across nothing.

🔴 **Never compare Q across sector counts**: `--sectors 1` vs `--sectors 5` on the
same geometry differ by **6.9%** in TE₀₁₁ Q. Sectors are a *measurement*
construct, but they change the mesh.

⚠️ **Representation matters independently of dimensions**: an analytic OCC
cylinder and an anisotropically dilated BSpline one differ by a constant **2.0
MHz**, regardless of the amount of dilation.

⚠️ **Mesh sizing can be clamped and silently ignore you.** `set_pts` was ignored
because `Mesh.MeshSizeExtendFromBoundary = 0`; a size field was clamped by
`Mesh.MeshSizeMin`. Both produced confident verdicts from meshes never modified.
**Check element counts or file sizes differ across a sweep before reading any
result** — neither raises an error.

**The sidecar is the contract.** `geometry.py` writes `<mesh>.meta.json`;
`solveconf.py` derives the config *from it* so the config cannot disagree with
the mesh. 🔴 **But a field in the sidecar is not a binding** — R88 added
`torch_material` to the sidecar and nothing to the consumer, so Palace kept using
the template's ε=3.78 while `results.py` faithfully reported 11.6. **An entry
nobody reads is a claim, not a fact.**

---

## 4. Palace

**Driven, order 1, with adaptive PROM.** Postprocessing dominates: 437 s of a
~470 s solve at 165k tets. **Runtime scales with the number of frequency samples,
not with the physics** — so a band twice as wide costs twice as much for nothing
if the mode is not in the extra half.

**Solver order and the offset.**

| | |
|---|---|
| `offset.te011` | **+24.54 MHz** — order 1 → order 2 **on the same mesh** |
| `offset.tm020` | **+20.06 MHz** — 🔴 **mode-specific; applying one to both corrupts the separation** |

⚠️ These are **same-mesh** differences, so §2 applies: they are the most
trustworthy numbers in the harness. But they are **geometry-dependent** and have
not been re-measured for the sapphire + viewport + trap family.

🔑 **Frames are mandatory.** Every frequency in `baselines.json` carries
`frame: raw-order1 | converged | delta | offset`, and `dimensionless.check()`
refuses an unframed one. 🔴 **Never compare a raw order-1 number to an absolute
band edge** — it sits ~20–25 MHz low. Convert differentially where possible:
`f_conv(new) = f_conv(ref) + [f_raw(new) − f_raw(ref)]` cancels the offset to
first order and dodges the whole question.

**Conventions with a factor of 2.** Palace reports `E_elec = ½∫ε|E|²dV`, which is
**twice** the time-averaged energy; `SurfaceFlux` type `Power` carries the same
convention. `dq.py` corrects for it. 🔴 An unresolved 2× preceded the R5 bug —
if a derived quantity is off by ~2, check the convention before the physics.

**Eigenmode vs driven disagree.** By **3.7×** on ε sensitivity (9.25 vs
33.9 MHz). 🔑 **Driven is self-consistent and defines the design.** Never quote an
eigenmode sensitivity in a driven context — that mistake was made again in R99
and caught in review.

**Energy indices** (`solveconf.py`): 1 = bore, 2..N+1 = air sectors, 20+k = plasma
sectors, 80 = groove, 90 = plasma. Chosen not to collide.

**Band and step.**

- 🔴 **"Absent from a window is not absent."** Three retractions: R54's
  TM₁₁₁/TM₀₂₀, R77's excluded 2.3431, R59's unlocated TM₁₁₁. If a mode is missing,
  **widen the band before concluding anything** — R99b found TM₀₂₀ 190 MHz below
  where R99 looked.
- ⚠️ **A coarse step depresses a linewidth-derived Q by up to 2×**, one-directional
  and silent (`reproducibility.linewidth_step_bias`). A locate-only sweep may use
  a coarse step; **a linewidth may not be quoted from one.**
- ⚠️ A peak-relative threshold silently dropped TM₀₂₀ once, and the matcher then
  paired the survivor with an interloper and accepted it.

---

## 5. Where nothing is measurable

🔴 **Near a degeneracy, stop.** A **0.16% mesh change** — 143,395 → 143,623 tets,
from *tagging a region*, same geometry and same materials — swung TE₀₁₁'s pm/pe by
**178%** (`reproducibility.degeneracy_sensitivity`). TE₀₁₁ and TM₁₁₁ are exactly
degenerate (χ′₀₁ = χ₁₁ = 3.8317, immovable by aspect ratio), so anything sitting
on that crossing is unmeasurable in this harness. **§1's noise floor does not
apply there — it is a floor for well-separated modes only.**

🔴 **Under-resolved skin depth swings Q by 40%** between meshes of effectively
identical density. Any loaded-Q claim must clear that first. δ ∝ 1/√σ, so a high-σ
plasma needs a finer mesh than the cold cavity does.

🔑 **The test for an unmeasurable point**: make a change that is *pure
bookkeeping* — tag a region, renumber an index — and re-solve. If the answer
moves, the point is unmeasurable and no amount of sweeping will fix it.

---

## 6. Failure modes that look like results

| | |
|---|---|
| solve returns in seconds | MPI launcher missing → "no resonance" |
| mesh silently unchanged | size clamp → confident verdict from a stale mesh |
| **cases silently identical** | R101 — verify the independent variable was **applied**, not just declared. `md5sum` |
| mode missing from window | 🔴 not absent — **widen** |
| Q looks low | coarse step, or under-resolved skin depth, before physics |
| derived quantity off by ~2 | the time-averaged convention |
| `grep` on command output | swallowed a traceback; a stale mesh then fed a 2 h solve. **Check exit codes; never diagnose through a filter** |
| harness says "exit 0" | 🔴 `cmd > log; echo "EXIT=$?"` exits with the *echo*'s status. **The sentinel on disk is authoritative, not the notification** |

---

## 7. Running jobs

`run_in_background: true` with the command **directly** — no `nohup`, no `&`
(either alone is a distinct failure). Always leave `; echo "EXIT=$?" >> log`.
Never `pkill -f` — the wrapper shell carries the whole command block in its argv.
Never edit a file a running job shells out to. Full recipe in the
`background-job-recipe` memory; `watchjob.py --uid` for diagnosis (log growing /
frozen at high CPU / frozen at low CPU are three different problems).

---

### ⚠️ Coordinate magnitude is NOT a precision problem — correction

I argued that translating far from the origin would degrade geometric predicates,
because double spacing grows with magnitude. **That was wrong by nine orders of
magnitude.**

| coordinate | ulp | vs OCC's ~1e-7 m tolerance |
|---:|---:|---:|
| 0.1 m | 1.4e-17 m | 1.4e-10 |
| **0.356 m** (a +256 mm offset) | **5.6e-17 m** | **5.6e-10** |
| 100 m | 1.4e-14 m | 1.4e-7 |
| **2^31 m** | **4.8e-7 m** | **≈ 5 — parity at last** |

✅ **A +256 mm offset costs a factor of 4 in ulp and remains 9 orders below the
geometric tolerance.** Precision only becomes the binding constraint above ~2^31.

🔑 **What actually makes the origin special is EXACT COINCIDENCE, not precision.**
At x = y = 0 the cavity axis lies exactly on the coordinate axis, so geometric
predicates evaluate to exact zeros — and exact zeros are where degenerate
tie-breaking lives in CAD and meshing algorithms. Offsetting breaks the
coincidence at **no** precision cost. That is the reason to do it, and it means
the offset should be an awkward number rather than a power of two.

---

## 8. What this document cannot fix

⚠️ Q depends on resolution in ways that do not cancel in a ratio. η depends on
σ = 30 S/m, still a bare literal. Geometry derivatives are floored at ~1.2 MHz/mm
by §2. These are **limits to state**, not problems to solve with more discipline.

🔑 **And the ordering rule that would have saved the most time here: a result
needs a closed-form reason before it earns a run.** TM₀₂₀'s 33× shift was
predicted from J₀ peaking on axis and J₁ vanishing there, *then* measured. R104
had no analytic reason, was cross-mesh, and sat at 2.8σ — the artifact profile —
and was dropped rather than chased.
